from dataclasses import replace

import pytest

from releasegate.policy import ApprovalFacts, digest, evaluate


def assess(evidence, sha, **kwargs):
    kwargs.setdefault(
        "required_test_ids", frozenset({"fixture::required_one", "fixture::required_two"})
    )
    return evaluate(evidence, expected_commit=sha, target=kwargs.pop("target", "staging"), **kwargs)


def test_allow_stops_at_human_gate(evidence, sha):
    result = assess(evidence, sha)
    assert result.decision == "ALLOW"
    assert result.next_gate == "HUMAN_APPROVAL"
    assert result.execution_authorized is False


@pytest.mark.parametrize("kind", ["tests", "security"])
def test_missing_required_evidence(evidence, sha, kind):
    del evidence["checks"][kind]
    assert f"MISSING_{kind.upper()}_EVIDENCE" in assess(evidence, sha).reasons


@pytest.mark.parametrize("kind", ["tests", "security"])
def test_wrong_commit(evidence, sha, kind):
    evidence["checks"][kind]["commit_sha"] = "c" * 40
    assert f"{kind.upper()}_COMMIT_MISMATCH" in assess(evidence, sha).reasons


@pytest.mark.parametrize("field", ["failed", "errors"])
def test_failed_tests(evidence, sha, field):
    evidence["checks"]["tests"]["summary"][field] = 1
    evidence["checks"]["tests"]["summary"]["passed"] = 1
    assert "TESTS_FAILED" in assess(evidence, sha).reasons


@pytest.mark.parametrize("exit_code", [1, 2, 3, 4, 5, -9, True])
def test_test_command_failure_even_when_report_passes(evidence, sha, exit_code):
    evidence["checks"]["tests"]["exit_code"] = exit_code
    assert "TESTS_FAILED" in assess(evidence, sha).reasons


def test_only_skips_do_not_establish_passing_tests(evidence, sha):
    evidence["checks"]["tests"]["summary"].update(passed=0, skipped=2)
    assert "NO_PASSING_TESTS" in assess(evidence, sha).reasons


@pytest.mark.parametrize("value", [-1, True, "2", 1.5])
def test_invalid_test_counts(evidence, sha, value):
    evidence["checks"]["tests"]["summary"]["total"] = value
    assert "MALFORMED_TEST_RESULTS" in assess(evidence, sha).reasons


@pytest.mark.parametrize(
    "severity,expected",
    [
        ("HIGH", "DENY"),
        ("CRITICAL", "DENY"),
        ("LOW", "ALLOW"),
        ("MEDIUM", "ALLOW"),
        ("UNDEFINED", "DENY"),
        ("high", "DENY"),
    ],
)
def test_security_threshold(evidence, sha, severity, expected):
    security = evidence["checks"]["security"]
    security["exit_code"] = 1
    security["summary"]["findings"] = [
        {"id": "B602", "severity": severity, "file": "src/application.py", "line": 1}
    ]
    result = assess(evidence, sha)
    assert result.decision == expected
    assert result.execution_authorized is False


@pytest.mark.parametrize("exit_code", [1, 2, -9, True])
def test_unusable_scanner_exit(evidence, sha, exit_code):
    evidence["checks"]["security"]["exit_code"] = exit_code
    assert "SECURITY_SCANNER_FAILED" in assess(evidence, sha).reasons


def test_empty_scan(evidence, sha):
    evidence["checks"]["security"]["summary"]["scanned_files"] = 0
    assert "EMPTY_SECURITY_SCAN" in assess(evidence, sha).reasons


@pytest.mark.parametrize("field,value", [("pipeline_id", "different"), ("source_digest", "c" * 64)])
def test_cross_run_evidence(evidence, sha, field, value):
    evidence["checks"]["security"]["context"][field] = value
    assert "EVIDENCE_CONTEXT_MISMATCH" in assess(evidence, sha).reasons


def test_missing_production_approval(evidence, sha):
    result = assess(evidence, sha, target="production", gate="final")
    assert result.decision == "DENY"
    assert "PRODUCTION_APPROVAL_REQUIRED" in result.reasons


def test_production_candidate_can_reach_human_gate(evidence, sha):
    assert assess(evidence, sha, target="production").next_gate == "HUMAN_APPROVAL"


def test_llm_recommendation_never_counts_as_approval(evidence, sha):
    result = assess(
        evidence,
        sha,
        target="production",
        gate="final",
        approval={"approved": True, "verified_human": True, "source": "llm"},
    )
    assert "PRODUCTION_APPROVAL_REQUIRED" in result.reasons


def human_facts(evidence, sha):
    return ApprovalFacts(sha, "production", digest(evidence), "test-human", True, True)


def test_approved_policy_still_requires_independent_authorization(evidence, sha):
    result = assess(
        evidence, sha, target="production", gate="final", approval=human_facts(evidence, sha)
    )
    assert result.decision == "ALLOW"
    assert result.next_gate == "EXECUTION_AUTHORIZATION"
    assert result.execution_authorized is False


@pytest.mark.parametrize(
    "change", [{"commit_sha": "c" * 40}, {"target": "staging"}, {"evidence_digest": "c" * 64}]
)
def test_stale_or_wrong_approval(evidence, sha, change):
    approval = replace(human_facts(evidence, sha), **change)
    assert (
        "STALE_OR_WRONG_APPROVAL"
        in assess(evidence, sha, target="production", gate="final", approval=approval).reasons
    )


@pytest.mark.parametrize(
    "change", [{"verified_human": False}, {"approved": False}, {"reviewer": ""}, {"approved": 1}]
)
def test_unverified_or_rejected_approval(evidence, sha, change):
    assert (
        "PRODUCTION_APPROVAL_REQUIRED"
        in assess(
            evidence,
            sha,
            target="production",
            gate="final",
            approval=replace(human_facts(evidence, sha), **change),
        ).reasons
    )


def test_approval_cannot_override_failed_checks(evidence, sha):
    evidence["checks"]["tests"]["exit_code"] = 1
    assert (
        assess(
            evidence, sha, target="production", gate="final", approval=human_facts(evidence, sha)
        ).decision
        == "DENY"
    )


@pytest.mark.parametrize(
    "payload",
    [
        None,
        [],
        {},
        {"schema_version": True, "checks": {}},
        {"schema_version": 99, "checks": {}},
        {"schema_version": 1, "checks": []},
    ],
)
def test_bad_evidence_denied(payload, sha):
    assert assess(payload, sha).decision == "DENY"


@pytest.mark.parametrize("kind", ["tests", "security"])
def test_unknown_tool_is_not_trusted(evidence, sha, kind):
    evidence["checks"][kind]["tool"] = "model_said_it_passed"
    assert assess(evidence, sha).decision == "DENY"


def test_bad_target_gate_and_sha(evidence):
    result = evaluate(evidence, expected_commit="main", target="arbitrary", gate="skip")
    assert {"INVALID_COMMIT_SHA", "UNSUPPORTED_TARGET", "UNSUPPORTED_GATE"} <= set(result.reasons)


def test_evidence_digest_changes_on_new_finding(evidence, sha):
    old = assess(evidence, sha).evidence_digest
    evidence["checks"]["security"]["summary"]["scanned_files"] += 1
    assert assess(evidence, sha).evidence_digest != old


def test_one_pass_and_83_skips_is_denied(evidence, sha):
    ids = [f"fixture::required_{i}" for i in range(84)]
    evidence["checks"]["tests"]["summary"] = {
        "total": 84,
        "passed": 1,
        "failed": 0,
        "errors": 0,
        "skipped": 83,
        "case_ids": ids,
    }
    result = assess(evidence, sha, required_test_ids=frozenset(ids))
    assert result.decision == "DENY"
    assert "UNAPPROVED_TEST_SKIPS" in result.reasons
    assert result.next_gate is None and result.execution_authorized is False


def test_missing_mandatory_test_cannot_be_replaced_by_extra_pass(evidence, sha):
    evidence["checks"]["tests"]["summary"]["case_ids"][1] = "fixture::extra_pass"
    result = assess(evidence, sha)
    assert result.decision == "DENY" and "MISSING_MANDATORY_TESTS" in result.reasons


def test_one_unapproved_skip_denies(evidence, sha):
    evidence["checks"]["tests"]["summary"].update(passed=1, skipped=1)
    assert "UNAPPROVED_TEST_SKIPS" in assess(evidence, sha).reasons


def test_passing_subset_does_not_replace_mandatory_suite(evidence, sha):
    required = frozenset({"fixture::required_one", "fixture::required_two", "fixture::missing"})
    assert "MISSING_MANDATORY_TESTS" in assess(evidence, sha, required_test_ids=required).reasons


def test_mandatory_policy_is_not_optional(evidence, sha):
    result = evaluate(evidence, expected_commit=sha, target="staging")
    assert result.decision == "DENY"
    assert "MANDATORY_TEST_SET_NOT_CONFIGURED" in result.reasons


def test_duplicate_identities_cannot_satisfy_mandatory_suite(evidence, sha):
    evidence["checks"]["tests"]["summary"]["case_ids"] = ["fixture::required_one"] * 2
    assert "UNUSABLE_TEST_IDENTITIES" in assess(evidence, sha).reasons
