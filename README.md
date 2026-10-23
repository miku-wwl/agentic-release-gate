# ReleaseGate

Official competition workspace: [GitLab Showcase](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase).
The [welcome issue](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/work_items/1)
contains onboarding and community resources. The original workspace README is
preserved in [gitlab-initial-README.md](docs/gitlab-initial-README.md) as historical
content; its template push instructions do not govern this import.

This branch is a tracked content import from GitHub commit
`98d81957f19afa8d7de8843236b7497d5baac2b3`, based on the GitLab initialization
commit. The GitHub and GitLab histories remain independent.

Documentation updated from reviewed GitHub commit
`7a692fbba0139fd4805fc9c2bce95eda35d5eebf`; code corrections are recorded in the Phase 2 handoff.

Commit-bound release evidence and deterministic policy for GitLab Transcend
**Life After Code**, Path A / Best Assisted Agent. GitLab Duo advises; real pytest
and Bandit evidence qualify a candidate; ReleaseGate presents an inspectable
ALLOW/DENY for human review.

**Status (2026-10-24):** [MR !1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/1)
was merged into GitLab main on October 16. The project is public and MIT licensed.
Historical main CI passed five automatic jobs and the original 96 mandatory tests;
its overall status remains manual at the untouched blocking candidate-review job.
Phase 4 adds reproducible evidence experiments, historical Duo advisory ingestion
and Markdown/JSON/static HTML human reports. Exact current qualification is in the
[Phase 4 handoff](docs/phase4/14-final-handoff.md).

AUTONOMY_STATUS=ASSISTED_VERIFIED. SUPERVISED_STATUS=NOT_VERIFIED.
The genuine historical Code Review session found missing git in the slim CI image.
Duo recommended; Codex implemented the correction. The session reviewed an earlier
revision, not the final merged main or Phase 4 candidate. The prepared custom Flow
was not registered; foundational Fix CI/CD Flow was not executed. The historical
[Phase 2.5 safety restriction](docs/phase2.5-security-and-autonomy-review.md)
remains applicable. No new Flow invocation is part of this milestone.

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

MIT licensed. AGENTS.md is preserved. The Phase 4 feature-branch publication and review MR are authorized; deployment and automatic merge are excluded.

## Human review and reproducible evaluation

```powershell
# After collecting tests/security above:
uv run --no-sync python -m releasegate report --sha $sha --target staging --advisory docs/phase4/duo-advisory.json --output-dir evidence/review
uv run --no-sync python scripts/evaluate_scenarios.py --trials 3 --output-dir .artifacts/research-new
```

The report revalidates raw artifacts using existing Policy v2. Advice cannot waive
failures or supply human approval. Open `evidence/review/report.html`; Markdown and
schema-v1 JSON are adjacent. Historical Duo references and local versus hosted
verification remain visible. Research executes real checks in isolated snapshots,
labels synthetic approval-policy evaluations, and records measured outcomes and
provenance. Its three-identity negative fixtures never replace the original 96
mandatory application identities; Phase 4 adds mandatory coverage for new features.

- [Baseline audit](docs/phase4/00-baseline-audit.md)
- [Method and reproduction](docs/phase4/01-research-methodology.md)
- [Executed results](docs/phase4/02-experimental-results.md)
- [Threat model and limits](docs/phase4/03-threat-model-and-validity.md)
- [Review report](docs/phase4/06-human-review-experience.md)
- [Lifecycle coverage](docs/phase4/07-devsecops-lifecycle-matrix.md)
- [New video storyboard](docs/phase4/09-video-storyboard.md) — materials only; recording pending

Phase 4 uses a normal GitLab-main-based feature branch and review MR. It preserves
GitLab initialization history, MR !2, all existing policy gates and the Python 3.12
lock. No main push, merge, deployment or final video publication is included.
