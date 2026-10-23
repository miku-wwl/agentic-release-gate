"""Measure local evidence integrity with real checks and explicitly labelled policy trials."""

import argparse
import copy
import hashlib
import importlib.metadata
import json
import os
import shutil
import statistics
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from releasegate.evidence import (
    load_evidence,
    load_required_tests,
    read_json,
    source_digest,
    write_json,
)
from releasegate.policy import SHA, ApprovalFacts, digest, evaluate

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = {
    "complete": ("ALLOW", "CHECKS_PASSED"),
    "failed_test": ("DENY", "TESTS_FAILED"),
    "skipped_test": ("DENY", "UNAPPROVED_TEST_SKIPS"),
    "missing_identity": ("DENY", "MISSING_MANDATORY_TESTS"),
    "missing_security": ("DENY", "MISSING_SECURITY_EVIDENCE"),
    "wrong_sha": ("DENY", "TESTS_COMMIT_MISMATCH"),
    "context_mismatch": ("DENY", "EVIDENCE_UNUSABLE"),
    "corrupt_raw": ("DENY", "EVIDENCE_UNUSABLE"),
    "high_security": ("DENY", "SECURITY_HIGH"),
    "missing_approval": ("DENY", "PRODUCTION_APPROVAL_REQUIRED"),
    "stale_approval_sha": ("DENY", "STALE_OR_WRONG_APPROVAL"),
    "wrong_approval_target": ("DENY", "STALE_OR_WRONG_APPROVAL"),
    "wrong_approval_digest": ("DENY", "STALE_OR_WRONG_APPROVAL"),
    "release_unavailable": ("DENY", "EXECUTION_NOT_CONFIGURED"),
}


@contextmanager
def local_snapshot_environment():
    """Parent policy-only loads must share the inner commands' local context too."""
    names = ("GITLAB_CI", "CI_PROJECT_ID", "CI_PIPELINE_ID", "CI_JOB_ID", "CI_COMMIT_SHA")
    saved = {name: os.environ.get(name) for name in names}
    try:
        for name in names:
            os.environ.pop(name, None)
        yield {key: value or "" for key, value in saved.items()}
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def snapshot(destination: Path, *, variant="complete") -> None:
    """Reuse demo.py's isolated snapshot/scanned-only fixture pattern, never edit host tests."""
    destination.mkdir(parents=True)
    for folder in ("src", "tests", "scripts", ".gitlab"):
        shutil.copytree(
            ROOT / folder, destination / folder, ignore=shutil.ignore_patterns("__pycache__")
        )
    for name in ("pyproject.toml", ".gitlab-ci.yml", "uv.lock"):
        shutil.copy2(ROOT / name, destination / name)
    if variant in {"failed_test", "skipped_test", "missing_identity"}:
        # Replace only the isolated suite with three declared fixture identities.
        # This is not a qualification of the application's mandatory manifest.
        for item in (destination / "tests").iterdir():
            if item.is_file():
                item.unlink()
        count = 2 if variant == "missing_identity" else 3
        body = "    assert case >= 0\n"
        if variant == "failed_test":
            body = "    assert case != 0\n"
        elif variant == "skipped_test":
            body = "    if case == 0:\n        pytest.skip('negative fixture')\n" + body
        (destination / "tests/test_required.py").write_text(
            "import pytest\n\n"
            + f"@pytest.mark.parametrize('case', range({count}))\n"
            + "def test_required(case):\n"
            + body,
            encoding="utf-8",
        )
        write_json(
            destination / "tests/required-tests.json",
            {
                "schema_version": 1,
                "required_case_ids": [f"tests.test_required::test_required[{i}]" for i in range(3)],
            },
        )
    if variant == "high_security":
        (destination / "src/unsafe_scanner_fixture.py").write_text(
            "import subprocess\n\ndef unsafe_example(value):\n"
            '    return subprocess.run("echo " + value, shell=True, check=True)\n',
            encoding="utf-8",
        )


def execute(arguments: list[str], *, root: Path, records: list) -> dict:
    env = os.environ.copy()
    for name in ("GITLAB_CI", "CI_PROJECT_ID", "CI_PIPELINE_ID", "CI_COMMIT_SHA"):
        env.pop(name, None)
    env["PYTHONPATH"] = str(root / "src")
    started = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "-m", "releasegate", *arguments],
        cwd=root,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=300,
    )
    record = {
        "command": ["python", "-m", "releasegate", *arguments],
        "exit_code": result.returncode,
        "duration_seconds": time.perf_counter() - started,
    }
    records.append(record)
    # Fixed commands produce bounded output. Keep it out of public reports; its hash
    # detects accidental mismatch without publishing local paths or arbitrary test logs.
    record["output_sha256"] = hashlib.sha256(
        (result.stdout + result.stderr).encode("utf-8")
    ).hexdigest()
    if arguments == ["release"]:
        record["decision"] = json.loads(result.stdout)
    return record


def metrics(rows: list[dict]) -> dict:
    deny = [row for row in rows if row["expected"] == "DENY"]
    latencies = sorted(row["duration_seconds"] for row in rows if row["mode"] == "CLI_EVIDENCE")
    return {
        "total_scenarios": len({row["scenario"] for row in rows}),
        "trials_executed": len(rows),
        "expected_allow": sum(row["expected"] == "ALLOW" for row in rows),
        "expected_deny": len(deny),
        "correct_decisions": sum(row["correct"] for row in rows),
        "false_allow": sum(row["observed"] == "ALLOW" for row in deny),
        "false_deny": sum(row["expected"] == "ALLOW" and row["observed"] == "DENY" for row in rows),
        "fail_closed_detection_rate": (
            sum(row["observed"] == "DENY" for row in deny) / len(deny) if deny else None
        ),
        "cli_latency_seconds": {
            "n": len(latencies),
            "min": min(latencies),
            "median": statistics.median(latencies),
            "max": max(latencies),
            "mean": statistics.mean(latencies),
        }
        if latencies
        else None,
    }


def run(output: Path, *, sha: str, trials: int, host_execution: dict) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    host_digest = source_digest(ROOT)
    rows = []
    for trial in range(1, trials + 1):
        bases = {}
        for variant in (
            "complete",
            "failed_test",
            "skipped_test",
            "missing_identity",
            "high_security",
        ):
            base = output / "snapshots" / str(trial) / variant
            snapshot(base, variant=variant)
            records = []
            test = execute(["run-check", "tests", "--sha", sha], root=base, records=records)
            security = execute(["run-check", "security", "--sha", sha], root=base, records=records)
            if test["exit_code"] != (1 if variant == "failed_test" else 0):
                raise RuntimeError(f"Unexpected pytest collection outcome: {variant}")
            if security["exit_code"] != (1 if variant == "high_security" else 0):
                raise RuntimeError(f"Unexpected scanner outcome: {variant}")
            bases[variant] = (base, records)
        for name, (expected, reason) in SCENARIOS.items():
            base, collected = bases.get(name, bases["complete"])
            records = copy.deepcopy(collected)
            evidence_dir = "evidence"
            mode = (
                "POLICY_ONLY"
                if name in {"stale_approval_sha", "wrong_approval_target", "wrong_approval_digest"}
                else "CLI_EVIDENCE"
            )
            if name in {"missing_security", "context_mismatch", "corrupt_raw"}:
                evidence_dir = f"cases/{name}"
                shutil.copytree(base / "evidence", base / evidence_dir)
                if name == "missing_security":
                    (base / evidence_dir / "security.json").unlink()
                elif name == "context_mismatch":
                    path = base / evidence_dir / "security.json"
                    value = read_json(path)
                    value["context"]["source_digest"] = "0" * 64
                    write_json(path, value)
                else:
                    (base / evidence_dir / "tests.junit.xml").write_bytes(b"corrupt raw artifact")
            expected_sha = ("0" if sha[0] != "0" else "1") * 40 if name == "wrong_sha" else sha
            started = time.perf_counter()
            if mode == "POLICY_ONLY":
                evidence = load_evidence(base / "evidence", root=base)
                facts = ApprovalFacts(
                    commit_sha="0" * 40 if name == "stale_approval_sha" else sha,
                    target="staging" if name == "wrong_approval_target" else "production",
                    evidence_digest="0" * 64
                    if name == "wrong_approval_digest"
                    else digest(evidence),
                    reviewer="synthetic-policy-fixture",
                    verified_human=True,
                    approved=True,
                )
                decision = evaluate(
                    evidence,
                    expected_commit=sha,
                    target="production",
                    gate="final",
                    approval=facts,
                    required_test_ids=load_required_tests(base),
                ).to_dict()
                status = None
                records.append(
                    {
                        "command": None,
                        "api": "releasegate.policy.evaluate",
                        "exit_code": None,
                        "consent": "SYNTHETIC_POLICY_FACTS_ONLY",
                    }
                )
            elif name == "release_unavailable":
                record = execute(["release"], root=base, records=records)
                status = record["exit_code"]
                decision = record["decision"]
            else:
                args = [
                    "evaluate",
                    "--sha",
                    expected_sha,
                    "--target",
                    "production" if name == "missing_approval" else "staging",
                    "--evidence-dir",
                    evidence_dir,
                    "--output",
                    f"cases/{name}-decision.json",
                ]
                if name == "missing_approval":
                    args += ["--gate", "final"]
                record = execute(args, root=base, records=records)
                status = record["exit_code"]
                decision = read_json(base / f"cases/{name}-decision.json")
            duration = time.perf_counter() - started
            provenance = {}
            for kind in ("tests", "security"):
                check_path = base / evidence_dir / f"{kind}.json"
                if check_path.exists():
                    value = read_json(check_path)
                    provenance[kind] = {
                        key: value[key]
                        for key in ("commit_sha", "context", "raw_sha256", "summary")
                    }
            observed = decision["decision"]
            correct = (
                observed == expected
                and reason in decision["reasons"]
                and decision["execution_authorized"] is False
                and (
                    status is None
                    or status
                    == (3 if name == "release_unavailable" else 0 if expected == "ALLOW" else 1)
                )
                and (name != "complete" or decision["next_gate"] == "HUMAN_APPROVAL")
            )
            rows.append(
                {
                    "scenario": name,
                    "trial": trial,
                    "mode": mode,
                    "expected": expected,
                    "required_reason": reason,
                    "observed": observed,
                    "correct": correct,
                    "decision": decision,
                    "exit_code": status,
                    "duration_seconds": duration,
                    "commands": records,
                    "evidence_source": "LOCAL_ISOLATED_SNAPSHOT",
                    "snapshot": base.relative_to(output).as_posix(),
                    "evidence_directory": evidence_dir,
                    "source_digest": source_digest(base),
                    "provenance": provenance,
                }
            )
    if source_digest(ROOT) != host_digest:
        raise RuntimeError("Host source changed during evaluation")
    result = {
        "schema_version": 1,
        "experiment": "releasegate-evidence-integrity-v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "host_commit_sha": sha,
        "host_source_digest": host_digest,
        "trials_per_scenario": trials,
        "host_execution": host_execution,
        "host_context_verification": "ENVIRONMENT_VALUES_ONLY; not independent attestation",
        "tools": {
            "python": sys.version.split()[0],
            **{
                name: importlib.metadata.version(name)
                for name in ("pytest", "bandit", "defusedxml")
            },
        },
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "metrics": metrics(rows),
        "results": rows,
        "limitations": [
            "Small purposive local sample; repeated trials are not independent attack samples.",
            "No statistical significance, production resistance, or authenticated approval claim.",
            "Three-identity negative fixtures do not replace the 96 mandatory baseline identities.",
            "Snapshot digests include changes; commit SHA alone is not snapshot attestation.",
            "CLI latency excludes shared collection; command timings record collection separately.",
        ],
        "reproduce": f"uv run --no-sync python scripts/evaluate_scenarios.py --trials {trials} "
        "--output-dir .artifacts/research-new",
    }
    write_json(output / "results.json", result)
    lines = [
        "# Executed evidence integrity evaluation",
        "",
        "Status: " + ("PASS" if all(row["correct"] for row in rows) else "PARTIAL"),
        "",
        "```json",
        json.dumps(result["metrics"], indent=2),
        "```",
        "",
        "| Scenario | Trial | Mode | Expected | Observed | Exit | Seconds | Reasons |",
        "|---|---:|---|---|---|---:|---:|---|",
        *[
            f"| {r['scenario']} | {r['trial']} | {r['mode']} | {r['expected']} | "
            f"{r['observed']} | {r['exit_code']} | {r['duration_seconds']:.6f} | "
            f"{', '.join(r['decision']['reasons'])} |"
            for r in rows
        ],
        "",
        "## Provenance",
        "",
        f"Host commit: {sha}",
        f"Host source digest: {host_digest}",
        "",
        "Full command exits, versions, per-scenario digests and source paths: results.json.",
        "",
        "## Reproduction",
        "",
        "```text",
        result["reproduce"],
        "```",
        "",
        "## Limitations",
        "",
        *[f"- {item}" for item in result["limitations"]],
        "",
    ]
    (output / "results.md").write_text("\n".join(lines), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".artifacts/research")
    parser.add_argument("--trials", type=int, choices=range(1, 11), default=3)
    args = parser.parse_args()
    sha = (
        os.environ.get("CI_COMMIT_SHA", "")
        if os.environ.get("GITLAB_CI") == "true"
        else (
            subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
                timeout=15,
            ).stdout.strip()
        )
    )
    if not SHA.fullmatch(sha):
        parser.error("A valid host commit identity is required")
    with local_snapshot_environment() as host_execution:
        result = run(
            args.output_dir.resolve(), sha=sha, trials=args.trials, host_execution=host_execution
        )
    print(json.dumps(result["metrics"], sort_keys=True))
    return 0 if all(row["correct"] for row in result["results"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
