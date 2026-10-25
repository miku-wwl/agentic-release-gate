# ReleaseGate

Official competition workspace: [GitLab Showcase](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase).
The [welcome issue](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/work_items/1)
contains onboarding and community resources. The original workspace README is
preserved in [gitlab-initial-README.md](docs/gitlab-initial-README.md) as historical
content; its template push instructions do not govern this import.

The original GitLab import used GitHub commit
`98d81957f19afa8d7de8843236b7497d5baac2b3`, based on the GitLab initialization
commit. The GitHub and GitLab histories remain independent.

Documentation updated from reviewed GitHub commit
`7a692fbba0139fd4805fc9c2bce95eda35d5eebf`; code corrections are recorded in the Phase 2 handoff.

Commit-bound release evidence and deterministic policy for GitLab Transcend
**Life After Code**, Path A / Best Assisted Agent. GitLab Duo advises; real pytest
and Bandit evidence qualify a candidate; ReleaseGate presents an inspectable
ALLOW/DENY for human review.

**Status (2026-10-24):** Phase 4.1 merged [GitLab MR !3](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/3)
and [GitHub PR #1](https://github.com/miku-wwl/agentic-release-gate/pull/1).
Their 67 tracked files matched exactly. The Phase 4.1 main pipeline passed six
automatic jobs and 139 tests; its overall status is manual at the unexecuted human
candidate-review gate. Phase 4.2 refreshed research against the committed source
digest: 42/42 correct, with zero false ALLOW/DENY. See
[post-merge qualification](docs/phase4/15-post-merge-qualification.md) for the evidence
timeline and the final main CI/artifact authority. Final Phase 4.2 merge identities
and cross-platform hashes are recorded in the external delivery report and ZIP
manifest, avoiding self-referential commits. The project is public and MIT licensed.

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

The **[Live Verification Console](docs/live-verification.md)** runs actual pytest,
Bandit, evidence validation and policy evaluation from browser controls:

```powershell
uv sync --frozen --extra dev
uv run --no-sync python -m releasegate.live --port 8776
```

Open <http://127.0.0.1:8776/>. Every run uses a new isolated snapshot of committed
HEAD and new artifacts. The controlled rejection adds a scan-only fixture; it
never executes that fixture. Human approval remains required and unexecuted.
This local application is separate from the public static showcase and GitLab Duo.
See the guide for cancellation, evidence inspection and reproducible browser QA.

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

MIT licensed. AGENTS.md is preserved. Phase 4.2 uses normal reviewed MR/PR merges; production execution remains disabled.

## Human review and reproducible evaluation

The new [read-only Decision Console](frontend/README.md) is a separate static
frontend with Overview, Positive/Negative DEMO FIXTURE navigation, Evidence Chain,
bounded Research and original Audit Trail sources. It preserves Policy and all
139 mandatory identities. [Phase 4.3 architecture and handoff](docs/phase4.3/console-handoff.md)
and [local visual QA](docs/phase4.3/qa-report.md) explain its reference-data scope.
The reviewed static showcase is published separately on
[GitHub Pages](https://miku-wwl.github.io/agentic-release-gate/). It displays static
reference evidence, not live localhost execution. Changes to the public payload
require separate explicit publication authorization. The GitLab Pages include
remains gated by its approved-source rule; this local application does not enable it.

```powershell
uv run --no-sync python frontend/build_console.py --output-dir dist/console
uv run --no-sync python -m http.server 8767 --bind 127.0.0.1 --directory dist/console
```

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
- [Historical Phase 4 results](docs/phase4/02-experimental-results.md)
- [Phase 4.2 refreshed qualification](docs/phase4/15-post-merge-qualification.md)
- [Threat model and limits](docs/phase4/03-threat-model-and-validity.md)
- [Review report](docs/phase4/06-human-review-experience.md)
- [Lifecycle coverage](docs/phase4/07-devsecops-lifecycle-matrix.md)
- [New video storyboard](docs/phase4/09-video-storyboard.md) — materials only; recording pending

Phase 4.2 uses a GitLab-main-based feature branch and normal MR, then a separate
GitHub-history-based mirror PR. GitLab initialization history, MR !2, all policy
gates and the Python 3.12 lock are preserved. Phase 5 recording, visual acceptance,
publication and competition submission remain pending.
