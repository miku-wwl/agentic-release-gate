"""Pure product policy; ALLOW means eligibility for a gate, never execution authority."""

import hashlib
import json
import re
from dataclasses import asdict, dataclass

SHA = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"[0-9a-f]{64}")
SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
TARGETS = {"staging", "production"}


def digest(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


@dataclass(frozen=True)
class ApprovalFacts:
    """Facts from a trusted human-identity adapter, not from model output or arbitrary JSON.

    Phase 1 has no such platform adapter. Tests supply these facts to test policy only.
    This object neither authenticates a human nor grants execution authorization.
    """

    commit_sha: str
    target: str
    evidence_digest: str
    reviewer: str
    verified_human: bool
    approved: bool


@dataclass(frozen=True)
class Decision:
    decision: str
    reasons: tuple[str, ...]
    commit_sha: str
    target: str
    gate: str
    next_gate: str | None
    evidence_digest: str | None
    execution_authorized: bool = False
    policy_version: str = "releasegate-policy-v1"

    def to_dict(self) -> dict:
        return asdict(self)


def _count(value) -> bool:
    return type(value) is int and value >= 0


def evaluate(
    evidence: dict,
    *,
    expected_commit: str,
    target: str,
    gate: str = "eligibility",
    approval: ApprovalFacts | None = None,
) -> Decision:
    """Fail closed. Caller must independently establish artifact provenance and human identity."""
    reasons = []
    evidence_digest = None
    if type(expected_commit) is not str or not SHA.fullmatch(expected_commit):
        reasons.append("INVALID_COMMIT_SHA")
    if type(target) is not str or target not in TARGETS:
        reasons.append("UNSUPPORTED_TARGET")
    if type(gate) is not str or gate not in {"eligibility", "final"}:
        reasons.append("UNSUPPORTED_GATE")
    if type(evidence) is not dict or set(evidence) != {"schema_version", "checks"}:
        reasons.append("MALFORMED_EVIDENCE")
        checks = {}
    elif type(evidence["schema_version"]) is not int or evidence["schema_version"] != 1:
        reasons.append("UNSUPPORTED_EVIDENCE_VERSION")
        checks = {}
    elif type(evidence["checks"]) is not dict:
        reasons.append("MALFORMED_EVIDENCE")
        checks = {}
    else:
        checks = evidence["checks"]
        try:
            evidence_digest = digest(evidence)
        except (TypeError, ValueError):
            reasons.append("MALFORMED_EVIDENCE")

    if set(checks) - {"tests", "security"}:
        reasons.append("UNEXPECTED_EVIDENCE")
    contexts = []
    for kind in ("tests", "security"):
        check = checks.get(kind)
        if check is None:
            reasons.append(f"MISSING_{kind.upper()}_EVIDENCE")
            continue
        required = {
            "kind",
            "commit_sha",
            "context",
            "tool",
            "tool_version",
            "command",
            "exit_code",
            "raw_file",
            "raw_sha256",
            "summary",
        }
        if type(check) is not dict or set(check) != required or check.get("kind") != kind:
            reasons.append(f"MALFORMED_{kind.upper()}_EVIDENCE")
            continue
        if check["commit_sha"] != expected_commit:
            reasons.append(f"{kind.upper()}_COMMIT_MISMATCH")
        context = check["context"]
        if (
            type(context) is not dict
            or set(context) != {"origin", "project_id", "pipeline_id", "source_digest"}
            or any(type(context[k]) is not str for k in context)
            or context["origin"] not in {"local-working-tree", "gitlab-ci"}
            or not DIGEST.fullmatch(context["source_digest"])
            or (
                context["origin"] == "gitlab-ci"
                and (not context["project_id"].isdigit() or not context["pipeline_id"].isdigit())
            )
        ):
            reasons.append(f"MALFORMED_{kind.upper()}_CONTEXT")
        else:
            contexts.append(context)
        expected_tool = "pytest" if kind == "tests" else "bandit"
        if (
            check["tool"] != expected_tool
            or type(check["tool_version"]) is not str
            or not check["tool_version"]
            or type(check["command"]) is not list
            or not check["command"]
            or any(type(arg) is not str for arg in check["command"])
            or type(check["raw_file"]) is not str
            or type(check["raw_sha256"]) is not str
            or not DIGEST.fullmatch(check["raw_sha256"])
        ):
            reasons.append(f"MALFORMED_{kind.upper()}_PROVENANCE")
        summary = check["summary"]
        if kind == "tests":
            if (
                type(summary) is not dict
                or set(summary) != {"total", "passed", "failed", "errors", "skipped"}
                or not all(_count(v) for v in summary.values())
                or summary["total"]
                != sum(summary[k] for k in ("passed", "failed", "errors", "skipped"))
            ):
                reasons.append("MALFORMED_TEST_RESULTS")
            elif (
                check["exit_code"] != 0
                or type(check["exit_code"]) is not int
                or summary["failed"]
                or summary["errors"]
            ):
                reasons.append("TESTS_FAILED")
            elif summary["passed"] == 0:
                reasons.append("NO_PASSING_TESTS")
        else:
            if (
                type(summary) is not dict
                or set(summary) != {"scanned_files", "findings"}
                or not _count(summary["scanned_files"])
                or type(summary["findings"]) is not list
            ):
                reasons.append("MALFORMED_SECURITY_RESULTS")
                continue
            if summary["scanned_files"] == 0:
                reasons.append("EMPTY_SECURITY_SCAN")
            findings = summary["findings"]
            for finding in findings:
                if (
                    type(finding) is not dict
                    or set(finding) != {"id", "severity", "file", "line"}
                    or type(finding["severity"]) is not str
                    or finding["severity"] not in SEVERITIES
                    or type(finding["id"]) is not str
                    or not finding["id"]
                    or type(finding["file"]) is not str
                    or not finding["file"]
                    or not _count(finding["line"])
                    or finding["line"] == 0
                ):
                    reasons.append("UNUSABLE_SECURITY_FINDING")
                elif finding["severity"] in {"HIGH", "CRITICAL"}:
                    reasons.append(f"SECURITY_{finding['severity']}")
            expected_exit = 1 if findings else 0
            if type(check["exit_code"]) is not int or check["exit_code"] != expected_exit:
                reasons.append("SECURITY_SCANNER_FAILED")
    if len(contexts) == 2 and contexts[0] != contexts[1]:
        reasons.append("EVIDENCE_CONTEXT_MISMATCH")

    if gate == "final" and target == "production":
        if (
            type(approval) is not ApprovalFacts
            or approval.verified_human is not True
            or approval.approved is not True
            or type(approval.reviewer) is not str
            or not approval.reviewer.strip()
        ):
            reasons.append("PRODUCTION_APPROVAL_REQUIRED")
        elif (
            approval.commit_sha != expected_commit
            or approval.target != target
            or approval.evidence_digest != evidence_digest
        ):
            reasons.append("STALE_OR_WRONG_APPROVAL")

    return Decision(
        "DENY" if reasons else "ALLOW",
        tuple(dict.fromkeys(reasons)) if reasons else ("CHECKS_PASSED",),
        expected_commit,
        target,
        gate,
        None
        if reasons
        else ("HUMAN_APPROVAL" if gate == "eligibility" else "EXECUTION_AUTHORIZATION"),
        evidence_digest,
    )
