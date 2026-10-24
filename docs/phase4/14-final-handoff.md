# Phase 4 final engineering handoff

> This document records the historical Phase 4 handoff and experiment.
> See [Phase 4.2 qualification](15-post-merge-qualification.md) for current provenance and delivery status.

Prepared 24 October 2026, Pacific/Auckland. This file describes engineering evidence,
not a production release or competition submission. Genuine publication qualification
is recorded separately from the local measurements below.

## Local qualification

**PASS:** 139 tests, 0 failures, 0 errors, 0 skips. All 96 original mandatory
identities are retained; 43 new identities are mandatory. Ruff check/format,
frozen dependency sync, lock check and installed dependency compatibility passed.
Policy v2, raw evidence validation, Python pin and dependency lock are unchanged.

**Research PASS:** 14 scenarios × 3 trials = 42 observed decisions; expected ALLOW 3,
DENY 39, correct 42, false ALLOW 0, false DENY 0, fail-closed detection 39/39 (100%).
CLI latency n=33: min 0.294956 s, median 0.343539 s, mean 0.346948 s,
max 0.410587 s, excluding shared collection and policy-only calls. These are small
local purposive fixtures, not statistical significance or production resistance.

**Security PASS at unchanged policy threshold:** real Bandit 1.8.6 scanned 7 files;
2 existing LOW findings (B404/B603), 0 HIGH/CRITICAL. Raw scanner exit 1 records
findings; the security collector CLI correctly exits 0 at the unchanged threshold.
No finding was suppressed. No dependency or external Runtime was added.

Positive report: ALLOW → HUMAN_APPROVAL, execution_authorized=false.
Real failed-test / skipped / missing / HIGH-finding examples: DENY. Production
final without approval: DENY. Release executor remains unavailable: DENY / exit 3.
Existing demo script also executed successfully with all positive/negative checks.

Generated Markdown/JSON/HTML reports and deterministic/escaping/path/schema tests
passed. **Browser visual QA is BLOCKED:** the actual CUA inventory returned no apps
or browsers and `iab` was unavailable. No screenshot or browser interaction is
claimed. This does not block generating or testing the static artifacts; perform
visual/browser verification before the separate video recording milestone.

## Exact reproduction and evidence

```powershell
uv sync --frozen --extra dev
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv lock --check
uv pip check
$sha = git rev-parse HEAD
uv run --no-sync python -m releasegate run-check tests --sha $sha --evidence-dir evidence
uv run --no-sync python -m releasegate run-check security --sha $sha --evidence-dir evidence
uv run --no-sync python -m releasegate evaluate --sha $sha --target staging
uv run --no-sync python -m releasegate report --sha $sha --target staging --advisory docs/phase4/duo-advisory.json --output-dir evidence/review
uv run --no-sync python scripts/evaluate_scenarios.py --trials 3 --output-dir .artifacts/research-new
uv run --no-sync python scripts/demo.py --output-dir .artifacts/demo-new
uv run --no-sync python -m releasegate release
```

All qualification commands above succeeded in their expected sense; the final
release command intentionally exits 3. The local evidence directory used was
`.artifacts/phase4-final-qualification`; full research snapshots are in
`.artifacts/phase4-research-qualified`; legacy demo evidence is in
`.artifacts/phase4-demo/a2bb4082-3975-4703-bdb6-78ef35cc6d31`.

- [Exact executed commands, durations and exits](evidence/validation-commands.json)
- [Observed hosted qualification](evidence/hosted-qualification.json)
- [Local qualification JSON](evidence/local-qualification.json)
- [Executed results and limitations](02-experimental-results.md)
- [Machine-readable research provenance](evidence/research-results.json)
- [Example positive report](examples/complete/report.html)
- [Example negative report](examples/high_security/report.html)
- [Artifact hash manifest](evidence/artifact-manifest.json)
- [Baseline API snapshot](evidence/baseline.json)

Local measurements identify base commit
`81aadcf643f3375046c79c4ff611096923cd93a0` plus uncommitted Phase 4 content through
source digest `3124ed96b8a93d7e56c58164333fe7676e7e909466d4a9f8eec06be9c123df18`
and the explicit script hash. They do not claim to be a pristine run of main.
The final committed candidate and genuine hosted evidence are recorded below.

## Boundaries and remaining work

AUTONOMY_STATUS=ASSISTED_VERIFIED; SUPERVISED_STATUS=NOT_VERIFIED.
Historical Duo Session 9451709 was revalidated, but no new Flow was invoked or
registered. Human production approval is absent; execution stays DISABLED.
No main push, merge, permission/protection change, deployment, release effect,
video creation/publication, restored old video URL or final submission occurred.

The storyboard, English narration, source index and IAB capture instructions are
ready. Record the revised video only after final engineering qualification and
browser visual checks. Potential-impact/user-study and novelty limitations remain
as described in the independent review; no award score/probability is asserted.

## Publication qualification

**Hosted implementation qualification: PASS.** Normal feature push succeeded through
the official glab credential helper (command-scoped; Git configuration unchanged).
The preconfigured Git credential helpers rejected the initial push. No token was
printed, copied or stored in project files.

- Implementation commit: `4a99e9e42c1ef95ec3af91d8f9c8e69c186b35e9`.
- [MR !3](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/3), targeting main, remains unmerged.
- [Branch pipeline 2983196180](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2983196180): success, actual push pipeline.
- [MR pipeline 2983200071](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2983200071): all seven automatic jobs success.
- Actual MR JUnit summary: **139 success, 0 failed, 0 skipped, 0 errors**, tests job `17430569510`.
- Jobs: validate `17430569509`, tests `17430569510`, security `17430569511`, release_policy `17430569512`, evidence_bundle `17430569513`, research_evaluation `17430569514`, release_boundary_demo `17430569515`.
- Research runner job duration: **33.306651 seconds**, including setup/artifact handling; not a per-decision latency measure.

The final evidence-note commit contains this qualification record and a module
comment clarification. Its latest genuine pipeline is linked by MR !3 and reported
in the final response; this document cannot embed its own future commit identity.
No merge or main push is performed. The original main candidate-review job remains
unexecuted. New MR rules contain no deployment or manual release job.

## Acceptance status

Local engineering, deterministic advisory separation, actual research measurements,
report generation, CI integration, mandatory tests, security threshold and all 15
requested documents are delivered. Browser visual QA remains BLOCKED and final
video recording/publication remains PLANNED. The production executor is DISABLED.
The historical artifact download was not established because of TLS timeouts;
fresh MR test-report summary and job statuses were read directly from GitLab.
