# Executed evidence integrity evaluation

> This document records the historical Phase 4 handoff and experiment.
> See [Phase 4.2 qualification](15-post-merge-qualification.md) for current provenance and delivery status.

Status: PASS

```json
{
  "total_scenarios": 14,
  "trials_executed": 42,
  "expected_allow": 3,
  "expected_deny": 39,
  "correct_decisions": 42,
  "false_allow": 0,
  "false_deny": 0,
  "fail_closed_detection_rate": 1.0,
  "cli_latency_seconds": {
    "n": 33,
    "min": 0.29495589999714866,
    "median": 0.3435394000262022,
    "max": 0.4105870999628678,
    "mean": 0.346947830304447
  }
}
```

| Scenario | Trial | Mode | Expected | Observed | Exit | Seconds | Reasons |
|---|---:|---|---|---|---:|---:|---|
| complete | 1 | CLI_EVIDENCE | ALLOW | ALLOW | 0 | 0.340776 | CHECKS_PASSED |
| failed_test | 1 | CLI_EVIDENCE | DENY | DENY | 1 | 0.367806 | TESTS_FAILED |
| skipped_test | 1 | CLI_EVIDENCE | DENY | DENY | 1 | 0.302903 | UNAPPROVED_TEST_SKIPS |
| missing_identity | 1 | CLI_EVIDENCE | DENY | DENY | 1 | 0.345798 | MISSING_MANDATORY_TESTS |
| missing_security | 1 | CLI_EVIDENCE | DENY | DENY | 1 | 0.361473 | MISSING_SECURITY_EVIDENCE |
| wrong_sha | 1 | CLI_EVIDENCE | DENY | DENY | 1 | 0.320894 | TESTS_COMMIT_MISMATCH, SECURITY_COMMIT_MISMATCH |
| context_mismatch | 1 | CLI_EVIDENCE | DENY | DENY | 1 | 0.388581 | EVIDENCE_UNUSABLE, CURRENT_CONTEXT_MISMATCH |
| corrupt_raw | 1 | CLI_EVIDENCE | DENY | DENY | 1 | 0.374759 | EVIDENCE_UNUSABLE, REPORT_DIGEST_MISMATCH |
| high_security | 1 | CLI_EVIDENCE | DENY | DENY | 1 | 0.327578 | SECURITY_HIGH |
| missing_approval | 1 | CLI_EVIDENCE | DENY | DENY | 1 | 0.335655 | PRODUCTION_APPROVAL_REQUIRED |
| stale_approval_sha | 1 | POLICY_ONLY | DENY | DENY | None | 0.019007 | STALE_OR_WRONG_APPROVAL |
| wrong_approval_target | 1 | POLICY_ONLY | DENY | DENY | None | 0.011907 | STALE_OR_WRONG_APPROVAL |
| wrong_approval_digest | 1 | POLICY_ONLY | DENY | DENY | None | 0.012093 | STALE_OR_WRONG_APPROVAL |
| release_unavailable | 1 | CLI_EVIDENCE | DENY | DENY | 3 | 0.307488 | EXECUTION_NOT_CONFIGURED |
| complete | 2 | CLI_EVIDENCE | ALLOW | ALLOW | 0 | 0.338912 | CHECKS_PASSED |
| failed_test | 2 | CLI_EVIDENCE | DENY | DENY | 1 | 0.294956 | TESTS_FAILED |
| skipped_test | 2 | CLI_EVIDENCE | DENY | DENY | 1 | 0.343539 | UNAPPROVED_TEST_SKIPS |
| missing_identity | 2 | CLI_EVIDENCE | DENY | DENY | 1 | 0.328519 | MISSING_MANDATORY_TESTS |
| missing_security | 2 | CLI_EVIDENCE | DENY | DENY | 1 | 0.309238 | MISSING_SECURITY_EVIDENCE |
| wrong_sha | 2 | CLI_EVIDENCE | DENY | DENY | 1 | 0.321744 | TESTS_COMMIT_MISMATCH, SECURITY_COMMIT_MISMATCH |
| context_mismatch | 2 | CLI_EVIDENCE | DENY | DENY | 1 | 0.320185 | EVIDENCE_UNUSABLE, CURRENT_CONTEXT_MISMATCH |
| corrupt_raw | 2 | CLI_EVIDENCE | DENY | DENY | 1 | 0.312811 | EVIDENCE_UNUSABLE, REPORT_DIGEST_MISMATCH |
| high_security | 2 | CLI_EVIDENCE | DENY | DENY | 1 | 0.381047 | SECURITY_HIGH |
| missing_approval | 2 | CLI_EVIDENCE | DENY | DENY | 1 | 0.385024 | PRODUCTION_APPROVAL_REQUIRED |
| stale_approval_sha | 2 | POLICY_ONLY | DENY | DENY | None | 0.016542 | STALE_OR_WRONG_APPROVAL |
| wrong_approval_target | 2 | POLICY_ONLY | DENY | DENY | None | 0.011205 | STALE_OR_WRONG_APPROVAL |
| wrong_approval_digest | 2 | POLICY_ONLY | DENY | DENY | None | 0.012927 | STALE_OR_WRONG_APPROVAL |
| release_unavailable | 2 | CLI_EVIDENCE | DENY | DENY | 3 | 0.320342 | EXECUTION_NOT_CONFIGURED |
| complete | 3 | CLI_EVIDENCE | ALLOW | ALLOW | 0 | 0.337445 | CHECKS_PASSED |
| failed_test | 3 | CLI_EVIDENCE | DENY | DENY | 1 | 0.352259 | TESTS_FAILED |
| skipped_test | 3 | CLI_EVIDENCE | DENY | DENY | 1 | 0.377239 | UNAPPROVED_TEST_SKIPS |
| missing_identity | 3 | CLI_EVIDENCE | DENY | DENY | 1 | 0.304824 | MISSING_MANDATORY_TESTS |
| missing_security | 3 | CLI_EVIDENCE | DENY | DENY | 1 | 0.400294 | MISSING_SECURITY_EVIDENCE |
| wrong_sha | 3 | CLI_EVIDENCE | DENY | DENY | 1 | 0.380472 | TESTS_COMMIT_MISMATCH, SECURITY_COMMIT_MISMATCH |
| context_mismatch | 3 | CLI_EVIDENCE | DENY | DENY | 1 | 0.365693 | EVIDENCE_UNUSABLE, CURRENT_CONTEXT_MISMATCH |
| corrupt_raw | 3 | CLI_EVIDENCE | DENY | DENY | 1 | 0.410587 | EVIDENCE_UNUSABLE, REPORT_DIGEST_MISMATCH |
| high_security | 3 | CLI_EVIDENCE | DENY | DENY | 1 | 0.370285 | SECURITY_HIGH |
| missing_approval | 3 | CLI_EVIDENCE | DENY | DENY | 1 | 0.356180 | PRODUCTION_APPROVAL_REQUIRED |
| stale_approval_sha | 3 | POLICY_ONLY | DENY | DENY | None | 0.017610 | STALE_OR_WRONG_APPROVAL |
| wrong_approval_target | 3 | POLICY_ONLY | DENY | DENY | None | 0.019324 | STALE_OR_WRONG_APPROVAL |
| wrong_approval_digest | 3 | POLICY_ONLY | DENY | DENY | None | 0.020039 | STALE_OR_WRONG_APPROVAL |
| release_unavailable | 3 | CLI_EVIDENCE | DENY | DENY | 3 | 0.363970 | EXECUTION_NOT_CONFIGURED |

## Provenance

Host commit: 81aadcf643f3375046c79c4ff611096923cd93a0
Host source digest: 3124ed96b8a93d7e56c58164333fe7676e7e909466d4a9f8eec06be9c123df18

Full command exits, versions, per-scenario digests and source paths: results.json.

## Reproduction

```text
uv run --no-sync python scripts/evaluate_scenarios.py --trials 3 --output-dir .artifacts/research-new
```

## Limitations

- Small purposive local sample; repeated trials are not independent attack samples.
- No statistical significance, production resistance, or authenticated approval claim.
- Three-identity negative fixtures do not replace the 96 mandatory baseline identities.
- Snapshot digests include changes; commit SHA alone is not snapshot attestation.
- CLI latency excludes shared collection; command timings record collection separately.

## Qualification identity

Executed locally on Python 3.12.13 from GitLab base commit `81aadcf643f3375046c79c4ff611096923cd93a0` plus the Phase 4 working-tree changes. The source digest and script digest in JSON identify those changes. This is **LOCAL_TESTED**, not hosted GitLab evidence. Timing samples include CLI startup.

[Machine-readable results](evidence/research-results.json) include actual command exits, raw digests, versions, scenario provenance and all 42 observations. Full raw snapshots remain in `.artifacts/phase4-research-qualified/snapshots/`; the CI research job preserves equivalent fresh raw artifacts for 14 days.
