# Evidence integrity evaluation methodology

This is a bounded software experiment against unchanged **releasegate-policy-v2**,
not a production attack study. Hypothesis: authentic passing evidence yields
eligibility, while each specified missing, failed, inconsistent or unusable
condition fails closed. The [executed results](02-experimental-results.md) contain
measurements; this method document makes no measured claims by itself.

## Procedure and sample

```text
uv sync --locked --extra dev
uv run --no-sync python scripts/evaluate_scenarios.py --trials 3 --output-dir .artifacts/research-new
```

Output must be a new directory to prevent reuse of prior successful measurements.
There are **14 scenarios 脳 3 trials = 42 planned observations**. Each trial collects
fresh pytest and Bandit artifacts in five independent snapshots: complete, failed
test, skipped test, missing identity, and high security finding. The complete and
high-security snapshots run the full current application suite. Other test
snapshots use three explicitly declared local fixture identities. Those identities
are not a substitute for the application's 96 original mandatory tests.

Snapshots copy source, tests, scripts, dependency/lock and CI configuration.
The unsafe subprocess example is only scanned; it is never imported or executed.
All check subprocesses have fixed commands, shell disabled and bounded timeouts.
CI identity is cleared for inner snapshots, including on a hosted runner. The
outer CI execution context is recorded separately. No external service is mutated.

| Scenario | Intervention | Observation path |
|---|---|---|
| complete | Full real test and scan evidence | CLI evaluate |
| failed_test | One of three real pytest cases fails | CLI evaluate |
| skipped_test | One required fixture case skipped | CLI evaluate |
| missing_identity | Two real passes against three required identities | CLI evaluate |
| missing_security | Remove security envelope from complete artifacts | CLI evaluate |
| wrong_sha | Evaluate a different full commit SHA | CLI evaluate |
| context_mismatch | Change security context source digest | Raw evidence loader + CLI |
| corrupt_raw | Replace JUnit bytes without changing its envelope digest | Raw evidence loader + CLI |
| high_security | Real Bandit HIGH finding in scanned-only fixture | CLI evaluate |
| missing_approval | Production final gate with no human adapter | CLI evaluate |
| stale_approval_sha | Synthetic approval facts for wrong commit | POLICY_ONLY |
| wrong_approval_target | Synthetic approval facts for wrong target | POLICY_ONLY |
| wrong_approval_digest | Synthetic approval facts for wrong evidence | POLICY_ONLY |
| release_unavailable | Call closed release command | CLI release |

Approval-fact fixtures exercise the pure policy API and never authenticate a human.
They record null command/exit status because no shell command is executed for the
policy decision. Every CLI case records the actual exit; release must return 3.
The complete scenario must return ALLOW with HUMAN_APPROVAL and false execution
authorization. Each negative must return DENY and its specified reason.

## Measurement and provenance

Schema v1 JSON records scenario/trial, expected and observed decisions, exact
reasons, actual exit, command list, tool versions, monotonic durations, snapshot
path and source digest, raw report digest, check summaries, host commit/source
identity, script digest and outer execution context. Raw artifacts remain alongside
the snapshots; public results omit arbitrary test logs and environment contents.
Output hashes cover captured command output without exposing it.

`correct_decisions` requires decision, reason, execution boundary and expected exit
to agree. False ALLOW/DENY counts are based on expected versus observed decisions.
Fail-closed detection rate = observed DENY among expected DENY observations divided
by expected DENY observations. CLI min/median/mean/max exclude pure policy calls and
shared check collection. Per-command durations retain the collection cost.
These timings include interpreter startup and file I/O; they are not isolated
policy-engine microbenchmarks. No latency threshold determines release eligibility.

Repeated trials test reproducibility on one machine/runner. They are correlated,
purposively selected cases, not independent samples from a production population.
No significance, confidence interval, defect reduction or performance gain is claimed.
Rerun with a new output directory after checkout of the recorded candidate; timing
and raw-report hashes may vary, but decisions/reasons should reproduce. Working-tree
digests explicitly identify uncommitted content; commit identity alone cannot do so.

## Phase 4.2 qualification

The refreshed JSON explicitly records `evaluated_commit_sha`,
`evaluated_source_digest`, `execution_environment`, runner/tool versions and
`raw_artifact_hashes`. Compatibility `host_*` fields identify the same run.
The digest covers Python files in src/tests, the mandatory manifest, pyproject,
CI YAML and uv.lock. Script identity is bound separately by `script_sha256`;
documentation is covered by the final cross-repository and ZIP file manifests.
Use exact Git blob bytes when comparing to CI; Windows checkout newline conversion
changes byte digests. No policy, test identity or scenario expectation was relaxed.

The original JSON remains byte-for-byte in `research-results-phase4-historical.json`.
The refreshed local run predates the documentation commit by design. Identical
source and script hashes connect it to the final candidate. Final main CI artifacts
identify the actual merge SHA and pipeline/job URLs; the external delivery report
and manifest record those IDs without generating recursive evidence commits.
