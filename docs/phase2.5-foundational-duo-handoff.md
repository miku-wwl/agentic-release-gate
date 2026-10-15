# ReleaseGate Phase 2.5 — foundational Duo qualification checkpoint

Updated: **2026-10-15**, Pacific/Auckland. Verdict: **BLOCKED** pending review of
unverified effective execution permissions and branch isolation. Browser login and
the official Fix Pipeline UI entry point are now VERIFIED. The controlled failure
and deterministic DENY are VERIFIED; a new
Fix CI/CD Pipeline Flow, diagnosis, repair and successful repair pipeline are NOT
VERIFIED. This checkpoint is not Phase 2.5 completion. The demonstrated autonomy
claim remains **Assisted**; Supervised is NOT VERIFIED.

Custom Flow registration is not a prerequisite for this milestone. No Custom Flow
was registered and no Runtime dependency or executor was added.

## Recovered state and access

The actual local/tracking/live refs were refreshed before changes:

| Checkout / remote branch | Recovered SHA / status |
|---|---|
| GitHub `main -> origin/main` | `ceac68727df0f00945ef7eedc9c715bb156597c8`, CLEAN |
| GitLab `import/releasegate-phase2a` | `559c47fa7a645795cd6ca46f91825445d29d70a6`, CLEAN |
| GitLab default `main` | `e4239c704040e427ef6ded36a4163113f995cef9`, initialization retained |
| [MR !1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/1) | Open, auto-merge disabled, source SHA unchanged |
| [Baseline pipeline 2946935881](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2946935881) | SUCCESS; previous actual qualification: six jobs, 96 tests, two LOW findings |

Remotes and primary upstream remain unchanged:

- GitHub: `git@github.com:miku-wwl/agentic-release-gate.git`.
- GitLab: `https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase.git`.

The interrupted preflight completed only read-only checks; no demo branch or MR
existed when it was resumed. Existing commits, worktrees and evidence were retained.
No reset, clean, stash, rebase, force push or repeated session was performed.

The existing glab 1.123.0 independently authenticates as `weilai-wang`, Developer
(30), against project `87602765`. CLI/API authentication is VERIFIED. Shared runners
and the Duo workflow runner are available. Actual new jobs ran on shared instance
runner `54907241`. Push-rule inspection returned 403, so service-account push-rule
compatibility is NOT VERIFIED. No push rule or security setting was changed.

Browser work now uses only the **ChatGPT Work built-in browser**, as requested.
The official GitLab login first required email identity verification. A subsequent
browser observation showed the authenticated `weilai-wang` project page; the
intervening verification action was not observed or attributed to an actor. Browser
authentication is now VERIFIED; no further code is needed. The tab is retained.
Credentials and authentication codes are excluded from this report and repository.

## Fix CI/CD Pipeline availability and invocation boundary

The actual configured item is independently verified, beyond a generic enablement flag:

| Observed project Catalog fact | Result |
|---|---|
| Consumer / item | `12590005` / `1800`, **Fix CI/CD Pipeline**, foundational |
| Enabled / current-user execution permission | `true` / `executeAiCatalogItem=true` |
| Pinned and latest version | `2518`, version `1.0.0` |
| Platform-reported reference | `fix_pipeline/v1` — discovered, not invented |
| Visible configuration | Ambient placeholder; no effective session tool/privilege profile supplied |
| Consumer service-account field | `null`; this does not prove that no account will be used at execution |
| Current-user credits query | `gitlabCreditsAvailable=true`; denial reason null; not a project balance or per-run price |

The documented entry point is the GitLab UI's **Fix pipeline with Duo** control.
The dedicated documentation explicitly describes UI-only availability; the generic
workflows API was not used as an invocation substitute. Developer can use the flow;
group enablement, service-account push rules and hosted runners are additional
prerequisites. [Official Fix Pipeline guide](https://docs.gitlab.com/ci/pipelines/fix_pipeline/).

The flow can inspect failed job output and repository context and return inline
suggestions or another review artifact. Its behavior must be observed, not inferred
from that description. Flow execution can consume compute and GitLab Credits;
balance, exact model and run consumption are NOT VERIFIED. No credit purchase,
subscription, paid-setting change or new flow execution occurred.

**Gate 1: PASS for availability.** Configuration, execute permission and the actual
enabled **Fix pipeline with Duo** button on pipeline `2949021100` are VERIFIED.
The GitLab-managed flow detail page confirms it is enabled, v1.0.0, with no event
triggers configured. An event trigger is not needed for this explicit UI action.
The effective execution profile and service-account push-rule compatibility remain
unqualified; a visible button is not proof of successful execution.
Before dispatch, inspect the actual permissions/write scope. Foundational flows are
not assumed read-only. The inspected protected-main rule permits Developer pushes;
branch-local instructions therefore cannot be treated as technical isolation.
If the effective profile can affect unrelated branches/resources, obtain the scope
review required by the user's Phase 2.5 instructions before starting it. The actual
flow detail page exposes no effective tool/privilege list or forced branch limit.
An explicit one-run scope-risk review is pending; the Fix button has not been clicked.

## Controlled failure — Gate 2 PASS

A third isolated worktree was created at
`D:\workshop\oct\agentic-release-gate-phase25-demo`, based on the unchanged GitLab
import SHA. Only the dedicated branch `demo/duo-fix-ci` was normally pushed.

Commit: **`e451c3b74b3bb978d5d644bb8f75203253dc9188`**.

Exactly three demo-only files changed:

- `.gitlab-ci.yml`: add a local include; every existing job remains identical.
- `.gitlab/ci/phase2.5-demo.yml`: validation-stage `duo_fix_ci_demo` intentionally
  invokes absent `releasegate_demo_python --version` in the existing Python image.
- `AGENTS.md`: append a narrow diagnosis/inline-suggestion scope for Duo, preserving
  all existing Runtime and product safety instructions.

The missing command is a deliberately planted, reversible fault. It is not an
application vulnerability or an agent-discovered production incident. The expected
use of the image's Python executable was prepared by Codex, not generated by Duo.
No correction has been applied and the job has not been skipped or allowed to fail.

[Demo MR !2](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/2)
is open, from `demo/duo-fix-ci` to `import/releasegate-phase2a`. This keeps the review
diff small; it does not modify the target branch. Auto-merge is disabled. Neither
MR is merged, closed or approved.

Local prepublication checks passed frozen sync, Ruff check/format and **96 tests
in 0.97s**, no errors/failures/skips. The JUnit identities independently match all
96 mandatory cases. Actual local Bandit covered five source files and retained two
LOW findings, B404/B603. Its raw exit 1 and collector threshold result are retained.
These are local results, not hosted pytest passes on the failed demo pipeline.

Prepublication flattened YAML passed server lint. After publication,
`GET /projects/87602765/ci/lint?content_ref=<immutable-demo-SHA>&include_jobs=true`
verified the actual committed include: valid, no errors/warnings, eight static jobs
including the protected-main manual job. An earlier static POST used default-main
include context and could not find the demo file; the exact-ref GET resolved that
validation-context issue without a code change. [CI Lint API](https://docs.gitlab.com/api/lint/).

| Genuine pipeline | Actual outcome |
|---|---|
| [2949019407, branch push](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2949019407) | FAILED, same deliberate fault |
| [2949021100, MR !2](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2949021100) | FAILED, SHA `e451c3b…`, real hosted execution |
| [Fault job 17188078493](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17188078493) | `releasegate_demo_python: command not found`; **exit 127** |
| [validate 17188078494](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17188078494) | SUCCESS |
| [tests 17188078495](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17188078495) | SKIPPED after validation failure; no hosted 96-pass claim |
| [security 17188078496](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17188078496) | SUCCESS; actual scan, two LOW, commit/project/pipeline bound |
| [release_policy 17188078497](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17188078497) | Expected DENY / `MISSING_TESTS_EVIDENCE`, exit 1 |
| [evidence_bundle 17188078498](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17188078498) | Independently regenerated the same DENY, exit 1 |
| [release_boundary_demo 17188078499](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17188078499) | SUCCESS; derived snapshots remain separate from baseline CI evidence |

Real policy JSON binds the demo SHA and retains `execution_authorized=false`,
`next_gate=null`. Missing required evidence cannot be waived by the scanner or an
AI recommendation. Raw logs/ZIPs were downloaded, path-checked and hash-recorded
under ignored `.artifacts/phase2.5/`. Fault-job trace SHA-256:
`12d6c090004c855455c268242f4d1096f9db9b152693e33d56651958883293a1`.

The observed demo MR UI also displayed optional approval and Ready to merge while
the pipeline was failed. Native MR merge checks are therefore not claimed to enforce
ReleaseGate's DENY. Release eligibility and execution authorization remain separate;
no merge was attempted and no project security setting was changed.

## Actual agent actions, repair and continuation

**Gate 3: BLOCKED / NOT RUN pending scope-risk review.** No new Fix Flow session, workload pipeline/job,
diagnosis, patch, comment, suggestion or agent-authored commit exists from this
milestone. Session `9451709` remains the sole observed session: genuine Phase 2
Code Review, not a Phase 2.5 Fix Pipeline run. No new model output was fabricated.

**Gate 4: NOT RUN.** No repaired commit or successful repair pipeline exists. Do not
substitute baseline pipeline `2946935881`, a local expected fix or hosted boundary
snapshots for qualification of a corrected demo SHA. Production final approval and
the closed release command remain required; no executor or authorization was added.

After the required scope-risk review, use the retained built-in browser to open
[MR !2](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/2),
then **Overview → failed pipeline → Fix pipeline with Duo**, or **Pipelines →
2949021100 → Fix pipeline with Duo**. First inspect availability and permission
scope; stop for review if broader than authorized. Monitor **AI → Sessions** and
retain the actual session, workload job, traces and suggestions. Do not invoke twice
if a session has already been created.

Review the complete output and diff. Any accepted correction may be applied only
to the demo branch, preserving the fault job, all tests/scans/policy and approvals.
Record whether Duo authored a suggestion, Codex/human applied it, or Duo actually
committed code. Then qualify a new real pipeline with the corrected job, 96 mandatory
tests, scan, exact-SHA evidence, deterministic decision and final human boundary.

## Autonomy and lifecycle evidence matrix

| Step | Actor / trigger | Approval boundary / actual evidence |
|---|---|---|
| Prepare intentional fault and narrow MR | Codex, user-authorized manual orchestration | Reviewed locally before normal push; MR !2 |
| Start branch/MR pipelines | GitLab CI, automatic after push/MR | No individual job approval; pipelines above |
| Validate and scan | GitLab CI, automatic jobs | Actual successful jobs; no AI orchestration claim |
| Reject missing required evidence | ReleaseGate in CI, automatic | DENY before any final release approval; policy artifacts above |
| Foundational Code Review in Phase 2 | GitLab Duo, explicitly invoked | [9451709](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/automate/agent-sessions/9451709); genuine advice, no execution authorization |
| Apply Phase 2 recommendation | Codex, manually reviewed and applied | GitHub `3b6b277…`; not autonomous Duo repair |
| Phase 2.5 diagnosis / patch | PLANNED Duo; UI invocation not performed | Login/button verified; effective-profile risk review pending; NOT VERIFIED |
| Apply suggestion / verify repair | PLANNED reviewer/Codex plus automatic CI | No patch or repair pipeline yet; NOT VERIFIED |
| Final approval / execution | Human / future independent authorization | No authenticated approval or production effect; release remains closed |

Assisted is the supported existing demonstration: real Duo advice, separately
reviewed Codex correction and automatic CI. Sequential Codex/API calls and ordinary
CI stages do not prove agent-owned orchestration. Supervised and autonomous repair
remain NOT VERIFIED; no safety gate is relaxed to improve that classification.
[Official autonomy definitions](https://gitlab-transcend.devpost.com/rules).

## Submission readiness and next action

| Requirement | Current evidence / remaining work |
|---|---|
| Public source and instructions | VERIFIED on import/demo branches; default main is still initialization |
| MIT license | LICENSE bytes verified on public import branch; About detection NOT VERIFIED, project API license null |
| Visible CI / real Agent Platform use | VERIFIED failure/baseline history and earlier Code Review; new Fix Flow NOT RUN |
| Path A chronology | Policy first added `5928377bafbf2cf68a2b78fbe78aca495b483834`, 2026-10-13; GitLab project created 2026-10-14, within the event window |
| Autonomy | Assisted supported; Supervised target unproven |
| Stage coverage | Actual review, testing, scanning, policy/evidence; repair pending; no deployment/monitoring claim |
| Reproducibility | Exact fault commit, MR, job error and artifacts retained; passing comparison untouched |
| Outstanding reviews | MR !1 and demo MR !2 open; later merge requires human review, not this run |
| Sub-three-minute demonstration | Earlier Assisted evidence can support a storyboard; Phase 2.5 failure-to-repair recording is not ready |
| Final submission | Public YouTube video and Devpost submission NOT CREATED / NOT SUBMITTED |

Deadline: **2026-10-27 13:00 UTC / 2026-10-28 02:00 Pacific/Auckland**. Public source,
detectable MIT license, visible automation history and a public video under three
minutes still need final submission review. [Official requirements](https://gitlab-transcend.devpost.com/rules).

**Single most valuable next action:** review whether to permit one scoped Fix Flow
invocation despite the unverified effective privilege list and branch isolation.
The concrete target is MR !2 / pipeline `2949021100`, with inline suggestions as the
intended output and no authority to change main/import, MR !1, security settings or
release authorization. No new login/token
setup, custom registration, permission escalation or Runtime implementation is needed
for the already verified preparation.

The GitHub documentation publication SHA is reported in the delivery response to
avoid a self-referential commit. MR !1, the import/default branches, primary upstream,
previous evidence and all existing code/tests/locks remain preserved. Generated
evidence, environments and temporary helpers stay ignored. No deployment occurred.
