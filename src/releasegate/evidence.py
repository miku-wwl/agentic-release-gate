"""Collect and verify actual pytest/Bandit artifacts. Hashes provide integrity, not attestation."""

import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
from pathlib import Path

from defusedxml import ElementTree

from releasegate.policy import SHA, digest

MAX_REPORT_BYTES = 10 * 1024 * 1024
RAW_FILES = {"tests": "tests.junit.xml", "security": "security.bandit.json"}


class EvidenceError(ValueError):
    pass


def read_bytes(path: Path) -> bytes:
    if path.stat().st_size > MAX_REPORT_BYTES:
        raise EvidenceError("REPORT_TOO_LARGE")
    return path.read_bytes()


def read_json(path: Path) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise EvidenceError("DUPLICATE_JSON_KEY")
            result[key] = value
        return result

    def reject_constant(value):
        raise EvidenceError("NON_FINITE_JSON_NUMBER")

    value = json.loads(read_bytes(path), object_pairs_hook=unique, parse_constant=reject_constant)
    if type(value) is not dict:
        raise EvidenceError("EXPECTED_JSON_OBJECT")
    return value


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", "utf-8")


def parse_junit(raw: bytes) -> dict:
    try:
        root = ElementTree.fromstring(raw)
        if root.tag not in {"testsuites", "testsuite"}:
            raise EvidenceError("INVALID_JUNIT_ROOT")
        suites = list(root.iter("testsuite"))
        if not suites or any(list(s.iter("testsuite"))[1:] for s in suites):
            raise EvidenceError("UNSUPPORTED_JUNIT_STRUCTURE")
        result = dict.fromkeys(("total", "passed", "failed", "errors", "skipped"), 0)
        case_ids = []
        for suite in suites:
            cases = suite.findall("testcase")
            declared = {k: int(suite.attrib[k]) for k in ("tests", "failures", "errors", "skipped")}
            if any(v < 0 for v in declared.values()) or declared["tests"] != len(cases):
                raise EvidenceError("JUNIT_COUNT_MISMATCH")
            actual = {k: 0 for k in ("failures", "errors", "skipped")}
            for case in cases:
                classname, name = case.get("classname"), case.get("name")
                if not classname or not name or len(classname + "::" + name) > 1024:
                    raise EvidenceError("MISSING_JUNIT_TEST_IDENTITY")
                case_ids.append(classname + "::" + name)
                flags = [bool(case.findall(tag)) for tag in ("failure", "error", "skipped")]
                if sum(flags) > 1:
                    raise EvidenceError("AMBIGUOUS_JUNIT_CASE")
                for flag, key in zip(flags, actual, strict=True):
                    actual[key] += int(flag)
            if any(actual[k] != declared[k] for k in actual):
                raise EvidenceError("JUNIT_COUNT_MISMATCH")
            result["total"] += len(cases)
            result["failed"] += actual["failures"]
            result["errors"] += actual["errors"]
            result["skipped"] += actual["skipped"]
        result["passed"] = result["total"] - sum(result[k] for k in ("failed", "errors", "skipped"))
        if len(set(case_ids)) != len(case_ids):
            raise EvidenceError("DUPLICATE_JUNIT_TEST_IDENTITY")
        result["case_ids"] = case_ids
        return result
    except EvidenceError:
        raise
    except Exception as exc:
        raise EvidenceError("UNUSABLE_JUNIT") from exc


def parse_bandit(report: dict) -> dict:
    if (
        type(report.get("errors")) is not list
        or report["errors"]
        or type(report.get("results")) is not list
        or type(report.get("metrics")) is not dict
        or type(report.get("generated_at")) is not str
        or not report["generated_at"]
    ):
        raise EvidenceError("UNUSABLE_BANDIT_REPORT")
    metrics = report["metrics"]
    totals = metrics.get("_totals")
    if type(totals) is not dict:
        raise EvidenceError("MISSING_BANDIT_TOTALS")
    files = {k: v for k, v in metrics.items() if k != "_totals"}
    counts = dict.fromkeys(("LOW", "MEDIUM", "HIGH", "UNDEFINED"), 0)
    findings = []
    for item in report["results"]:
        if (
            type(item) is not dict
            or type(item.get("issue_severity")) is not str
            or item.get("issue_severity") not in counts
            or type(item.get("test_id")) is not str
            or not item["test_id"]
            or type(item.get("filename")) is not str
            or item["filename"] not in files
            or type(item.get("line_number")) is not int
            or item["line_number"] <= 0
        ):
            raise EvidenceError("UNUSABLE_BANDIT_FINDING")
        severity = item["issue_severity"]
        if severity == "UNDEFINED":
            raise EvidenceError("UNDEFINED_BANDIT_SEVERITY")
        counts[severity] += 1
        findings.append(
            {
                "id": item["test_id"],
                "severity": severity,
                "file": item["filename"],
                "line": item["line_number"],
            }
        )
    for severity, count in counts.items():
        key = f"SEVERITY.{severity}"
        if type(totals.get(key)) is not int or totals[key] != count:
            raise EvidenceError("BANDIT_COUNT_MISMATCH")
        if any(
            type(m) is not dict or type(m.get(key)) is not int or m[key] < 0 for m in files.values()
        ):
            raise EvidenceError("UNUSABLE_BANDIT_METRICS")
        if sum(m[key] for m in files.values()) != count:
            raise EvidenceError("BANDIT_COUNT_MISMATCH")
    if not files or type(totals.get("loc")) is not int or totals["loc"] <= 0:
        raise EvidenceError("EMPTY_BANDIT_SCAN")
    if any(type(m.get("loc")) is not int or m["loc"] < 0 for m in files.values()):
        raise EvidenceError("UNUSABLE_BANDIT_METRICS")
    if sum(m["loc"] for m in files.values()) != totals["loc"]:
        raise EvidenceError("BANDIT_COUNT_MISMATCH")
    return {"scanned_files": len(files), "findings": findings}


def verify_scan_scope(report: dict, root: Path) -> None:
    expected = {p.relative_to(root).as_posix() for p in (root / "src").rglob("*.py")}
    actual = {name.replace("\\", "/") for name in report["metrics"] if name != "_totals"}
    if actual != expected:
        raise EvidenceError("SECURITY_SCAN_SCOPE_MISMATCH")


def source_digest(root: Path) -> str:
    paths = sorted(
        [p for folder in ("src", "tests") for p in (root / folder).rglob("*.py")]
        + [
            root / name
            for name in ("pyproject.toml", ".gitlab-ci.yml", "uv.lock", "tests/required-tests.json")
            if (root / name).is_file()
        ]
    )
    if not paths:
        raise EvidenceError("EMPTY_SOURCE_TREE")
    entries = {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths
    }
    return digest(entries)


def load_required_tests(root: Path) -> frozenset[str]:
    """Trusted repository policy; never accept mandatory-test or skip rules from evidence/LLMs."""
    value = read_json(root / "tests" / "required-tests.json")
    if (
        set(value) != {"schema_version", "required_case_ids"}
        or type(value["schema_version"]) is not int
        or value["schema_version"] != 1
        or type(value["required_case_ids"]) is not list
        or not value["required_case_ids"]
        or any(
            type(case_id) is not str or not 1 <= len(case_id) <= 1024
            for case_id in value["required_case_ids"]
        )
        or len(set(value["required_case_ids"])) != len(value["required_case_ids"])
    ):
        raise EvidenceError("UNUSABLE_MANDATORY_TEST_MANIFEST")
    return frozenset(value["required_case_ids"])


def context_for(root: Path) -> dict:
    in_ci = os.environ.get("GITLAB_CI") == "true"
    return {
        "origin": "gitlab-ci" if in_ci else "local-working-tree",
        "project_id": os.environ.get("CI_PROJECT_ID", "") if in_ci else "",
        "pipeline_id": os.environ.get("CI_PIPELINE_ID", "") if in_ci else "",
        "source_digest": source_digest(root),
    }


def run_check(kind: str, *, root: Path, directory: Path, commit_sha: str) -> dict:
    if not SHA.fullmatch(commit_sha):
        raise EvidenceError("INVALID_COMMIT_SHA")
    if os.environ.get("GITLAB_CI") == "true" and os.environ.get("CI_COMMIT_SHA") != commit_sha:
        raise EvidenceError("CI_COMMIT_MISMATCH")
    directory.mkdir(parents=True, exist_ok=True)
    raw_path = directory / RAW_FILES[kind]
    # Do not allow a failed command to reuse a previous successful report.
    raw_path.unlink(missing_ok=True)
    (directory / f"{kind}.json").unlink(missing_ok=True)
    context = context_for(root)
    if kind == "tests":
        command = [sys.executable, "-m", "pytest", "tests", "-q", f"--junitxml={raw_path}"]
        tool = "pytest"
    else:
        command = [
            sys.executable,
            "-m",
            "bandit",
            "-r",
            "src",
            "--ignore-nosec",
            "-f",
            "json",
            "-o",
            str(raw_path),
        ]
        tool = "bandit"
    # Fixed tool commands, shell disabled; never accept commands from model output.
    try:
        completed = subprocess.run(command, cwd=root, check=False, timeout=300)
    except subprocess.TimeoutExpired as exc:
        raise EvidenceError("CHECK_TIMEOUT") from exc
    if context != context_for(root):
        raise EvidenceError("SOURCE_CHANGED_DURING_CHECK")
    raw = read_bytes(raw_path)
    if kind == "tests":
        summary = parse_junit(raw)
    else:
        report = read_json(raw_path)
        summary = parse_bandit(report)
        verify_scan_scope(report, root)
    check = {
        "kind": kind,
        "commit_sha": commit_sha,
        "context": context,
        "tool": tool,
        "tool_version": importlib.metadata.version(tool),
        "command": command,
        "exit_code": completed.returncode,
        "raw_file": raw_path.name,
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "summary": summary,
    }
    write_json(directory / f"{kind}.json", check)
    return check


def load_evidence(directory: Path, *, root: Path) -> dict:
    checks = {}
    current = context_for(root)
    for kind in RAW_FILES:
        envelope = directory / f"{kind}.json"
        if not envelope.exists():
            continue
        check = read_json(envelope)
        if check.get("raw_file") != RAW_FILES[kind]:
            raise EvidenceError("UNTRUSTED_REPORT_PATH")
        raw_path = directory / RAW_FILES[kind]
        if hashlib.sha256(read_bytes(raw_path)).hexdigest() != check.get("raw_sha256"):
            raise EvidenceError("REPORT_DIGEST_MISMATCH")
        if kind == "tests":
            summary = parse_junit(read_bytes(raw_path))
        else:
            report = read_json(raw_path)
            summary = parse_bandit(report)
            verify_scan_scope(report, root)
        if check.get("summary") != summary:
            raise EvidenceError("REPORT_SUMMARY_MISMATCH")
        if check.get("context") != current:
            raise EvidenceError("CURRENT_CONTEXT_MISMATCH")
        checks[kind] = check
    return {"schema_version": 1, "checks": checks}
