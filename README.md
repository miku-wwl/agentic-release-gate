# ReleaseGate

Commit-bound release evidence and deterministic policy for GitLab Transcend
**Life After Code**, Path A / Supervised. Phase 1 evaluates actual pytest and Bandit
reports, blocks unsafe candidates, and produces JSON evidence for human review.

**Status (2026-10-15):** GitLab import, real MR CI (96 tests) and a genuine Duo
Code Review Flow are VERIFIED. [MR !1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/1)
remains open. Phase 2 is PARTIAL: custom risk-flow registration and its final risk
JSON contract remain unverified. See the [actual CI/Duo evidence and handoff](docs/phase2-unified-handoff.md).
Production execution is disabled. ALLOW means eligible for the next gate, never execution authorization. The pinned shared
Runtime v0.2.0 is MIT licensed and verified separately on Python 3.13. Its execution
integration belongs to a separately authorized persistent-execution milestone; see
[feasibility](docs/runtime-feasibility.md).

## Run locally

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/). Commands work in PowerShell:

```powershell
uv sync --frozen --extra dev
uv run --no-sync ruff check .
uv run --no-sync pytest -q
$sha = git rev-parse HEAD
uv run --no-sync python -m releasegate run-check tests --sha $sha
uv run --no-sync python -m releasegate run-check security --sha $sha
uv run --no-sync python -m releasegate evaluate --sha $sha --target staging
```

Artifacts: `evidence/tests.junit.xml`, `security.bandit.json`, per-check JSON
envelopes and `decision.json`. The local working-tree digest includes uncommitted
source; local results are not proof of a committed GitLab pipeline.

```powershell
# Real commands in isolated snapshots; creates a scanned-only unsafe fixture for DENY.
uv run --no-sync python scripts/demo.py
# Missing verified production approval => DENY / exit 1.
uv run --no-sync python -m releasegate evaluate --sha $sha --target production --gate final
# Executor unavailable => DENY / exit 3; creates no release effect.
uv run --no-sync python -m releasegate release
```

DENY exits 1; unusable check collection exits 2. Security collection records Bandit's
actual exit, and applies the HIGH threshold to its own command exit; LOW/MEDIUM
findings remain in evidence. Checks cannot be waived by LLM recommendations.

Policy v2 requires every test identity in the reviewed `tests/required-tests.json`
manifest and denies any skipped test. There are no skip exceptions. Missing or
duplicate identities, substituted extra tests and absent/malformed policy fail closed.
Manifest changes require human review, like changes to tests or policy code; the
collector includes the manifest in its source digest. The demo also runs actual
isolated pytest suites with 1 pass/83 skips and 83 passes/1 missing mandatory case;
both must produce DENY. The MR's `release_boundary_demo` also runs these derived
snapshots on a genuine GitLab runner, including failed-test, missing-evidence and
wrong-SHA cases. Their inner reports retain `local-working-tree` provenance;
the baseline test/security jobs record actual `gitlab-ci` context.

## GitLab setup

The `.gitlab-ci.yml` runs validation, tests, security, policy, evidence
generation and a blocking manual candidate review on the protected default branch.
It does not deploy. The existing foundational Duo Code Review Flow produced a real
MR recommendation that was reviewed, fixed and verified by CI. The prepared
`.gitlab/duo/flows/release-risk.yaml` still needs Maintainer/Owner registration
through AI Catalog; the file alone does not install a flow. See [Duo setup and limitations](docs/duo-integration.md).

- [Architecture and trust boundaries](docs/architecture.md)
- [Hackathon requirements](docs/hackathon-requirements.md)
- [Implementation and Phase 2 plan](docs/implementation-plan.md)
- [Phase 1 handoff and actual verification](docs/phase1-handoff.md)
- [Phase 1.1 Runtime compatibility update](docs/phase1.1-handoff.md)

MIT licensed. AGENTS.md is preserved. GitHub publication and a GitLab import branch
are authorized for this milestone; deployment and automatic MR merge are excluded.
