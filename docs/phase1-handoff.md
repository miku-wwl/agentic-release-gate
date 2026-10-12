# Phase 1 handoff — 2026-10-13

**Local vertical slice: PASS. Competition/platform integration: PARTIAL.**
GitLab Duo execution is **NOT VERIFIED**, GitLab CI is **NOT RUN**, and release
execution is deliberately disabled. Onboarding is incomplete, as confirmed by the
user. No simulated session, pipeline or production effect is presented as real.

## Implemented files

| Files | Purpose |
|---|---|
| `src/releasegate/policy.py` | Deterministic ALLOW/DENY, exact commit/target/evidence approval binding |
| `src/releasegate/evidence.py` | Real pytest/Bandit execution, strict parsing, hashes and scan-scope checks |
| `src/releasegate/cli.py`, `__main__.py`, `__init__.py` | Runnable CLI, durable decisions, closed release command |
| `tests/` | 84 policy, parser, artifact-integrity, CLI and configuration tests |
| `.gitlab-ci.yml` | Six stages, failed artifacts retained, blocking manual candidate review |
| `.gitlab/duo/flows/release-risk.yaml` | Documented read-only custom-flow body for Catalog registration |
| `scripts/demo.py` | Isolated actual ALLOW/DENY runs and persisted command transcript |
| `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore` | Installable, locked Python 3.12 foundation |
| `README.md`, `LICENSE`, `docs/` | Usage, MIT terms, requirements, architecture, setup and handoff |

No frontend, database, framework copy, cloud infrastructure or previous hackathon
application code was added. Human identity verification and release authorization
are not implemented. `ApprovalFacts` is the future trusted adapter input contract;
unit tests of that contract are not evidence of a real human approval system.

## Actual local results

Interpreter: **CPython 3.12.13**. uv: **0.11.16**. pytest: **8.4.2**. Bandit: **1.8.6**.
Checks used uncommitted working-tree snapshots referenced to Git HEAD
`ddd1d450a4a987e7d9edbac823c3f4fb44a5473e`; source digests distinguish the two snapshots.
They are local results, not results of a committed or hosted pipeline.

```text
uv sync --frozen --extra dev
Checked 15 packages in 1ms

uv run --no-sync ruff check .
All checks passed!

uv run --no-sync ruff format --check .
11 files already formatted

uv run --no-sync python scripts/demo.py
allow=ALLOW; deny=DENY; gitlab_duo=NOT VERIFIED; deployment=NOT RUN
exit=0
```

The full unmodified stdout/stderr, commands and exits are persisted in:

```text
.artifacts/demo/9e2a6670-0a19-4c13-86b7-a497e37f8f31/verification.json
```

The same directory contains separate `allow/evidence/` and `deny/evidence/` bundles,
including actual raw reports and envelopes. These generated artifacts are ignored
by Git. The intentionally unsafe source exists only in the isolated DENY snapshot;
Bandit scans it but no code imports or calls it.

| Actual demo command | Result | Exit |
|---|---|---|
| `run-check tests --sha <HEAD>` (ALLOW snapshot) | `84 passed in 0.68s`; 0 failed/errors/skipped | 0 |
| `run-check security --sha <HEAD>` (ALLOW snapshot) | 5 scanned files; 2 LOW; no HIGH | 0 |
| `evaluate --sha <HEAD> --target staging` (ALLOW) | ALLOW, `CHECKS_PASSED`, next `HUMAN_APPROVAL` | 0 |
| `run-check tests --sha <HEAD>` (DENY snapshot) | `84 passed in 0.59s`; 0 failed/errors/skipped | 0 |
| `run-check security --sha <HEAD>` (DENY snapshot) | 6 scanned files; actual B602 HIGH in fixture | 1 |
| `evaluate --sha <HEAD> --target staging` (DENY) | DENY, `SECURITY_HIGH`, no next gate | 1 |
| `evaluate --sha <HEAD> --target production --gate final` | DENY, `PRODUCTION_APPROVAL_REQUIRED` | 1 |
| `release` | DENY, `EXECUTION_NOT_CONFIGURED`, no release effect | 3 |

Bandit itself returned **1** in both scans because findings exist. The collector
records that exact exit and applies the product threshold to its own exit. In the
ALLOW snapshot the findings are B404 (subprocess import) and B603 (subprocess call),
both LOW. Fixed command arrays, the trusted interpreter and `shell=False` are used;
findings were retained rather than suppressed. This is not a zero-finding claim.

The ALLOW evidence digest was
`c73c4a6d9b82700a32a55bf9e90be22bc4ba66abb70bde81fe196521249bed23`;
DENY was `13ad669314809d7c6331a08584f796943a22114ba67d8777ddd468da6aab523b`.
Both persisted decisions have `execution_authorized=false`.

Tests cover missing mandatory checks, failing tests/command exits, zero passing
tests, HIGH/CRITICAL and unknown severities, empty/partial scans, wrong SHA,
different source/pipeline context, unknown tool identity, malformed counts/XML/JSON,
raw-report modification, changed source, stale/wrong/false approval, and approval
that cannot override a failure or grant authorization. Basic YAML checks validate
local structure and safety choices; they do not replace GitLab's server validators.

```text
uv build
Successfully built dist\releasegate-0.1.0.tar.gz
Successfully built dist\releasegate-0.1.0-py3-none-any.whl
```

The wheel was installed into a separate Python 3.12 environment with only its one
runtime dependency, `defusedxml==0.7.1`. The installed module was loaded from that
environment's `Lib/site-packages`, not the editable source:

```text
VERSION=0.1.0
MISSING_EVIDENCE_DECISION=DENY
EXECUTION_AUTHORIZED=False
RELEASE_EXIT=3
```

Source secret-pattern scan: **NO MATCHES** for GitLab/GitHub tokens, AWS key IDs,
private-key headers and credential-bearing HTTP URLs. This is a bounded pattern
check, not a comprehensive secret-scanner certification.

## GitLab verification and blockers

| Item | Actual status |
|---|---|
| Current remote | `origin git@github.com:miku-wwl/agentic-release-gate.git` |
| Contributor onboarding | User-confirmed incomplete; user handling web workflow |
| Provisioned GitLab project/roles/runner/credits | NOT VERIFIED; no project URL yet |
| Official requirements and platform docs | Consulted live; linked in architecture and requirements |
| CI image tag / uv registry package | Tag `python:3.12.13-slim` and uv `0.11.16` metadata confirmed |
| GitLab CI server lint / real runner execution | NOT RUN; no GitLab history exists from this work |
| Catalog flow server acceptance / tools / trigger | NOT VERIFIED; prepared configuration only |
| GitLab Duo AI session | NOT VERIFIED; none created |
| Protected environment and approval identity | NOT VERIFIED; no deployment job configured |
| Production deployment | NOT RUN |

The Runtime release tag matches the requested fixed SHA, but the pinned tree has no
established license and requires Python 3.13. A fresh pinned package installation
is **NOT RUN**, in compliance with the task's license restriction. API inspection of
an existing editable installation is **PARTIAL**, not pinned-install acceptance.
Details and the exact deferred dependency are in `runtime-feasibility.md`.

The core acceptance chain (persistent Run, exact Plan approval, independent
authorization, durable Action, executor, verified effect and receipt) is **NOT RUN**.
No replacement implementation or claims about exactly-once effects were introduced.

## Repository preservation

AGENTS.md SHA-256 before and after:

```text
65FD235DE5C15B5DD71DDB52BF151BD1A1B73D45A320DD6347F9228A6D3FFB0B
```

It was already untracked at task start and remains intact. No staging, commit, push,
remote modification, tag, publication, deployment or competition submission occurred.

## Human actions and next step

1. Finish onboarding and provide the official GitLab Project URL, then verify project
   roles/runner/Duo access. No credentials should be pasted into source or chat logs.
2. Authorize delivery to that project when ready. Run server CI Lint and the real
   pipeline; import/enable the flow and create a supported trigger using the actual
   service account. Preserve actual AI session and pipeline URLs.
3. Establish compatible reuse rights for the exact shared Runtime pin and resolve its
   Python 3.13 baseline before adding it as a dependency or enabling execution.

## Proposed competition demonstration

For now, reproduce the local 84-test ALLOW candidate and the scanner-backed DENY
with `scripts/demo.py`. Show raw reports, source digests, reasons and the human gate.
Explain that production execution is unavailable.

After onboarding, repeat these behaviors in real GitLab MRs/pipelines. Show the
Duo flow reading real MR and job context, citing risks and remediation; a passing
candidate reaches human review, while a real HIGH finding prevents continuation.
Show the AI session, pipeline history and artifact bundle in the video. Only show a
production release after a trusted approval adapter and pinned Runtime execution
chain have been implemented and verified. See `implementation-plan.md` for Phase 2.
