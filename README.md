# ReleaseGate

Commit-bound release evidence and deterministic policy for GitLab Transcend
**Life After Code**, Path A / Supervised. Phase 1 evaluates actual pytest and Bandit
reports, blocks unsafe candidates, and produces JSON evidence for human review.

**Status:** local implementation runnable; GitLab pipelines NOT RUN; GitLab Duo
NOT VERIFIED (onboarding pending). Production execution is disabled. ALLOW means
eligible for the next gate, never execution authorization. The pinned shared
Runtime v0.2.0 is MIT licensed and verified separately on Python 3.13. Its execution
integration is deferred until after genuine GitLab Duo/CI verification; see
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

## GitLab setup

The initial `.gitlab-ci.yml` runs validation, tests, security, policy, evidence
generation and a blocking manual candidate review on the protected default branch.
It does not deploy. Import `.gitlab/duo/flows/release-risk.yaml` through AI Catalog;
the file alone does not install a flow. See [Duo setup](docs/duo-integration.md).

- [Architecture and trust boundaries](docs/architecture.md)
- [Hackathon requirements](docs/hackathon-requirements.md)
- [Implementation and Phase 2 plan](docs/implementation-plan.md)
- [Phase 1 handoff and actual verification](docs/phase1-handoff.md)
- [Phase 1.1 Runtime compatibility update](docs/phase1.1-handoff.md)

MIT licensed. AGENTS.md is preserved. No commit, push, tag, deployment or submission
is performed by this phase.
