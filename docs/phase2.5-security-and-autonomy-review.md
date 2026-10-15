# Phase 2.5 V2 — security and autonomy review

Reviewed **2026-10-15**, Pacific/Auckland. The security-probe receipt is timestamped
`2026-10-15T05:41:59Z`. This is an independent read-only continuation of the existing
checkpoint, with documentation publication. No new agent execution was attempted.

**Security Invocation Verdict: BLOCKED.** The current controls do not establish
demo-only writes for the foundational Fix Pipeline flow. Broad authorization cannot
replace technical isolation under the V2 task's mandatory Stage 2 gate.

**Phase 2.5 Overall Verdict: BLOCKED.** Recovery, availability, failure evidence and
security analysis are complete; genuine Fix diagnosis/repair/repair CI are not.
**Autonomy: ASSISTED VERIFIED.** Supervised and Hands-off remain NOT VERIFIED.

Labels describe evidence: VERIFIED = observed platform/source/artifact fact;
NOT VERIFIED = missing or unavailable proof; BLOCKED = cannot safely proceed under
current authorization; PLANNED = proposed future work, not a completed action.

## Recovered repository and authentication

All three existing worktrees were CLEAN. Local, tracking and live refs matched:

| Worktree / branch | Recovery commit |
|---|---|
| `D:\workshop\oct\agentic-release-gate`, `main -> origin/main` | `5241e2c915b52bb3c27f82570e800ab2b8ec0316` |
| `D:\workshop\oct\agentic-release-gate-phase2a`, `import/releasegate-phase2a` | `559c47fa7a645795cd6ca46f91825445d29d70a6` |
| `D:\workshop\oct\agentic-release-gate-phase25-demo`, `demo/duo-fix-ci` | `e451c3b74b3bb978d5d644bb8f75203253dc9188` |
| GitLab default `main` | `e4239c704040e427ef6ded36a4163113f995cef9` |

Configured remotes remain `git@github.com:miku-wwl/agentic-release-gate.git` and
`https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase.git`.
The primary upstream remains `origin/main`. The documentation publication SHA is
reported separately to avoid self-reference; none of the GitLab branches changed.
The GitHub branch API reports `main` unprotected; only the expressly authorized
normal GitHub documentation publication is performed, not a GitLab main push.

VERIFIED: existing glab 1.123.0 authenticates as active `weilai-wang`, id `43343080`,
Developer (30) through group access to project `87602765`. API and the ChatGPT Work
built-in browser both work; the browser shows pipeline `2949021100`, MR !2, demo SHA
and an enabled **Fix pipeline with Duo** button. No Windows/native computer control
was used in this review. No login, token or authentication code is needed.

[MR !1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/1)
and [MR !2](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/2)
remain open, auto-merge disabled. Their source SHAs match the table. MR !2 targets
the import branch, not main. No new visible Agent Session exists: the complete
session query returns only `9451709`, finished `code_review/v1`, with no next page.
Recent pipeline history still ends at `2949021100`; nothing was recreated/retried.

## Availability, identity and permissions

VERIFIED project Catalog consumer `12590005`, item `1800`, foundational reference
`fix_pipeline/v1`, enabled, current-user execution allowed. Pinned Catalog version
`2518` is v1.0.0. Both consumer service-account and parent-consumer fields return
null; this is not proof of execution without a service account. Shared runners,
Duo runner availability and foundational/remote flow flags are true.

The dedicated [Fix Pipeline documentation](https://docs.gitlab.com/ci/pipelines/fix_pipeline/)
requires Developer or higher, enablement, runners and compatible push rules. It
documents UI invocation and suggestions or repair MRs; AGENTS instructions are not
guaranteed. No supported REST invocation for this specific UI-only operation was
established; no generic workflow POST or non-starting session was used to test it.
The intended target remains MR !2 / failed pipeline `2949021100`.

The API reports GitLab `19.5.0-pre`, revision `135fb0218a7`. That prefix resolves in
the public GitLab source repository to
`135fb0218a7aa9cc54a5c2b4033d2f0e7d9b4e0b`. Its
[Fix definition](https://gitlab.com/gitlab-org/gitlab/-/blob/135fb0218a7aa9cc54a5c2b4033d2f0e7d9b4e0b/ee/app/models/ai/catalog/foundational_flow/fix_pipeline/definition.rb)
declares file read/write, GitLab read/write, command and Git privileges, web
execution and flow version 1.0.4, with an experimental feature-dependent resolver.
The [matching base class](https://gitlab.com/gitlab-org/gitlab/-/blob/135fb0218a7aa9cc54a5c2b4033d2f0e7d9b4e0b/ee/app/models/ai/catalog/foundational_flow.rb)
defaults pre-approved privileges to the granted set. This is stronger evidence than
the Catalog's ambient placeholder, but does not resolve deployment flags, the
Workflow Service version, exact tool list or a new session's effective tokens.
Catalog version 1.0.0 must not be reported as the executed flow version.

| Identity / privilege evidence | Finding and limit |
|---|---|
| Human | VERIFIED Developer, `can_push=true` on main, import and demo; not a Maintainer |
| Fix-specific project member | VERIFIED active bot `33073387`, `duo-fix-ci-cd-pipeline-gitlab-ai-hackathon`, directly granted Developer (30) |
| Runtime identity model | Official runner flows combine service account and initiator; access is their intersection, potentially across shared projects |
| Exact future Fix session account/token | NOT VERIFIED; no session exists and consumer association is null. Named bot membership is not a resolved token |
| Fix privilege configuration | VERIFIED in version-matched source: file writes, GitLab writes, commands and Git, default pre-approval; not an observed use of those tools |
| Requested/resolved new privileges | NOT VERIFIED / NOT RUN; no restricted request or claimed read-only profile |
| Previous Code Review requested profile | Ambient, privilege IDs 2/8; comparison only |
| Previous Code Review resolved profile | VERIFIED prior response: web, assigned/pre-approved 3/4/5/8, MCP enabled; not the requested restrictions and not proof of Fix's profile |
| Previous Code Review observed tools | MR context, file discovery/read, review-note posting; no observed code writes, but not evidence of enforced read-only access |

[Composite identity](https://docs.gitlab.com/user/duo_agent_platform/composite_identity/)
limits agents to the intersection of both identities' grants, rather than to the
user's task description. No independent server-enforced demo-ref restriction was
exposed by Catalog configuration or the inspected branch controls. Git capability
is write-capable according to the [privilege specification](https://docs.gitlab.com/development/ai_features/foundational_flows/#agent-privileges).
The failed pipeline/source-branch resolver supplies context; it does not establish
a token restricted to that ref. No test push to main or unrelated branch was made.

## Actual main protection and secret boundaries

VERIFIED `GET protected_branches` returns only `main`, rule `340218024`:

| Control | Actual value |
|---|---|
| Protected | true |
| Allowed to push and merge | Developer + Maintainer, role 30 |
| Allowed to merge | Developer + Maintainer, role 30 |
| Explicit user/group/deploy-key narrowing | None on either grant |
| Force push | false |
| Code Owner approval required | false |
| Inherited | false |
| Import/demo protection | Neither is protected |

These role grants cover a Developer bot as well as the human at the branch-rule
layer. Additional token/tool restrictions might narrow access, but they are NOT
VERIFIED. Main's protected label does not deny direct Developer pushes. Official
[branch permission semantics](https://docs.gitlab.com/user/project/repository/branches/protected/)
confirm that push permission permits direct changes; an MR is not inherently
required. The project also reports `only_allow_merge_if_pipeline_succeeds=false`.
No protection, account grant, merge setting or context exclusion was changed.

VERIFIED metadata-only variable queries: project variables = 0, immediate subgroup
`144731366` variables = 0. Parent `142538134` and root `121124982` return 403;
their contents and ordinary CI inheritance are NOT VERIFIED. Push-rule inspection
also returns 403, so service-account push-rule compatibility remains NOT VERIFIED.
Variable values and names were not printed or saved.

Official [flow-variable filtering](https://docs.gitlab.com/user/duo_agent_platform/flows/execution/execution-variables/)
excludes custom project/group/instance variables, including protected and masked
ones, from flow jobs. Platform-issued Git/API/job credentials still exist. This
documented protection is not proof of the exact future job environment, nor proof
that ordinary CI pipelines the agent could cause have no inherited secrets.
No future Fix job, environment dump, secret read or token disclosure occurred.

The current main tree contains only README: no `.gitlab/duo/agent-config.yml`,
setup script or declared external ID token. The [configuration reference](https://docs.gitlab.com/user/duo_agent_platform/flows/execution/agent-config-yaml/)
reads configuration from the default branch and provides no demo-ref allowlist key;
adding one on demo would not configure the flow. Default sandbox network/filesystem
controls are not GitLab branch authorization. A Fix workload's actual image,
sandbox activation and group policy are NOT VERIFIED. Do not conflate the regular
Python CI image with the separate flow image. [Sandbox limits](https://docs.gitlab.com/user/duo_agent_platform/environment_sandbox/).
The [flow security guide](https://docs.gitlab.com/user/duo_agent_platform/flows/execution/security-considerations/)
also warns that setup scripts run outside SRT with platform credentials; none is
configured on the inspected default branch. A future configuration requires review.

## Demonstration isolation and safety decision

VERIFIED immutable demo diff from `559c47f…` to `e451c3b…`: exactly three files,
29 added lines. Main/import history and MR !1 are untouched. Full root CI, included
demo YAML, invoked ReleaseGate collectors/policy and boundary script were reviewed.

| Reviewed surface | Finding |
|---|---|
| Intentional fault | Separate validation job calls absent `releasegate_demo_python --version`; exact source/log match |
| Root CI and include | Python 3.12.13 slim, frozen dependencies; original validation/tests/scanning/policy/evidence jobs retained |
| Scan and evidence | Actual Bandit source scan, raw artifact binding and exact-SHA policy recomputation; no waiver |
| Boundary job | Isolated derived snapshots; genuine runner execution, no committed-negative-branch claim |
| Final manual job | Protected default-main only; eligibility check, no deploy command or execution authorization |
| Side effects | No production deployment, paid infrastructure provisioning, irreversible API action, runtime executor or real credential literal in the reviewed workflow |
| Agent instructions | Demo-only suggestions requested, but prompts cannot enforce branch privileges |

The failure is isolated **as code**, not proven isolated **as agent authority**.
The broad source-declared capabilities, permissive actual main rule and unprotected
import branch leave unacceptable cross-ref write risk under the user-defined gate.
There is no verified mitigation before dispatch. Therefore **BLOCKED**, not
CONDITIONAL. No broad risk acceptance is requested; no Fix button was clicked.

**PLANNED mitigation for independent Maintainer review:** verify the actual Fix
account/token/tool enforcement; propose server-enforced denial of writes and merge
paths to all preserved refs, with only explicitly reviewed disposable repair refs
permitted. Review overlapping/wildcard rules, because permissive matches can win.
Review the bot's other project memberships and inherited CI secrets; protect
default-branch agent configuration and retain human review. If supported controls
cannot enforce that scope, continue the Assisted fallback. A separately reviewed
isolated project is an alternative proposal, not permission to create one or proof
that a shared service account would be isolated. No settings/account changes or
new project were made. Re-run the safety gate before any later invocation.

## Genuine failure, policy and existing repair evidence

| Evidence | Actual result / actor |
|---|---|
| [Demo MR pipeline 2949021100](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2949021100) | FAILED, MR !2, `e451c3b…`; unchanged |
| [Fault job 17188078493](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17188078493) | Command not found, exit 127; live trace hash matches retained bytes |
| Demo tests / security | Tests SKIPPED after validation fault; actual Bandit scans five source files, two LOW B404/B603 |
| [Policy 17188078497](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17188078497) / [bundle 17188078498](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17188078498) | DENY, `MISSING_TESTS_EVIDENCE`, exact demo SHA; execution false, next gate null |
| Fix session / diagnosis / patch / commit | NOT RUN / NOT VERIFIED; no agent or manual correction of demo |
| Corrected Phase 2.5 pipeline | Does not exist; baseline success is not repair evidence for this fault |
| [Existing baseline 2946935881](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2946935881) | SUCCESS, `559c47f…`, six jobs, 96 mandatory passes, no failures/errors/skips, two LOW findings |
| Baseline policy | ALLOW → HUMAN_APPROVAL, `execution_authorized=false`; no release effect |
| Prior local demo qualification | Frozen sync, Ruff and 96 tests passed; local, not hosted passes on the failing demo |

This review independently rehashed retained baseline artifact ZIPs and reparsed raw
JUnit against the mandatory manifest: all 96 unique identities pass, no skips.
The failure trace SHA-256 remains
`12d6c090004c855455c268242f4d1096f9db9b152693e33d56651958883293a1`.
Baseline/failure scan findings remain visible; LOW is not described as no findings.
No test/scanner/CI execution was repeated for these documentation-only changes.
Production approval tests and the closed release command remain unchanged. Reviewed
documentation passes `git diff --check`; a bounded credential-pattern scan and
relative documentation-link checks pass before exact-path staging/publication.

The **different, existing Phase 2** chain supports the fallback:
[failed pipeline 2946803065](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2946803065)
→ [Code Review session 9451709](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/automate/agent-sessions/9451709)
→ [Duo recommendation](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/1#note_4012466889)
→ Codex-reviewed GitLab correction `d05e8bb205a0411c5f7b5bc5c6fc68b0b367a7cf`
→ [successful pipeline 2946878007](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2946878007)
→ baseline qualification above. Duo identified reliance on missing Git in a slim
image and recommended CI identity. Codex implemented validated `CI_COMMIT_SHA`
handling; Duo did not author that commit. The review session's workload pipeline
[2946840620](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2946840620)
and job `17171276318` succeeded. Its 16-entry trace proves MR/diff/file analysis and
review posting, not direct raw CI artifact/log reads. This is Code Review, not Fix.

## Independent autonomy matrix

| Step | Actor / trigger | Control / platform evidence | Approval / security implication |
|---|---|---|---|
| Prepare fault and MR !2 | Codex, explicit user task | Manually orchestrated; `e451c3b…` | Isolated code diff reviewed; no agent-scope guarantee |
| CI tests/scanning | GitLab CI, push/MR | Automatic jobs, 2946935881 / 2949021100 | Deterministic automation, not agent-owned workflow |
| Code Review analysis | Duo, one explicit Phase 2 invocation | Autonomous internal MR/file/review sequence, session 9451709 | Advisory output; broad resolved profile recorded, no new invocation |
| Prior diagnosis recommendation | Duo | Real MR note; missing Git matches actual job fault | Useful diagnosis, not approval or proof of raw-log retrieval |
| Prior repair | Codex, reviewed task continuation | `d05e8bb…`, manually selected/applied | Not an agent-authored repair or autonomous lifecycle transition |
| Repair/baseline validation | CI after Codex push | 2946878007 / 2946935881 success | No human per-job action; ordinary CI cannot establish Supervised |
| Eligibility decision | ReleaseGate in CI | Exact-SHA ALLOW or DENY artifacts | AI cannot waive missing/failed evidence; execution remains false |
| Phase 2.5 Fix / repair / repair CI | Not executed | BLOCKED; no session, patch or corrected pipeline | No invented actor or outcome |
| Final review / production | Human / future independent gate | No authenticated final approval or deployment | Release command still DENY, exit 3; no production executor |

Under the [official autonomy definitions](https://gitlab-transcend.devpost.com/rules),
the demonstrated product is **ASSISTED VERIFIED**: genuine agent recommendations,
separately reviewed implementation and CI. The internal multi-step review is real,
but there is no verified agent-owned repair-to-validation lifecycle. Sequential
Codex calls and multiple CI jobs do not establish Supervised. Hands-off is not
claimed. No approval evidence is inferred from initiating a review or running CI.

## Submission readiness and prepared Assisted fallback

| Requirement | Current assessment |
|---|---|
| Public GitLab source | VERIFIED public project; complete source exists on import/demo. Unauthenticated import LICENSE/README retrieval succeeded |
| MIT license | VERIFIED import LICENSE matches local bytes; SHA-256 `62a90fe7963937439077512690b05873b5f00997ab8f4161b555a93fb40b97d1` |
| Default branch / About | BLOCKED for submission readiness: main has only README; API license/license_url null. About recognition NOT VERIFIED |
| Setup / reproduction | VERIFIED import README contains frozen setup, tests/scanner commands and demo instructions; no fresh install claimed |
| Visible genuine history | VERIFIED public CI pipelines, Duo review notes; judge access to complete session trace NOT VERIFIED |
| Duo role / autonomy | VERIFIED Code Review and Assisted evidence; custom risk JSON, raw-artifact agent evaluation and Supervised NOT VERIFIED |
| Path A provenance | First policy addition `5928377bafbf2cf68a2b78fbe78aca495b483834`, 2026-10-13T09:59:43+13:00; project created 2026-10-14; consistent with event window, not proof of all entrant eligibility |
| DevSecOps coverage | Genuine review, tests, scanning, deterministic policy and evidence; no deployment/monitoring or agent release execution claim |
| Repeatability | Exact SHAs, original failed/passing CI and ignored raw receipts retained; artifact retention is 14 days, sessions documented as 30 days, so capture approved public demo evidence before expiry |
| Outstanding MRs | !1 integration and !2 deliberate-failure demo remain open, unmerged; human review required |
| Video / submission | PLANNED only; no public video, final project description or submitted Devpost entry verified/created |

Deadline: **2026-10-27 13:00 UTC / 2026-10-28 02:00 Pacific/Auckland**.
The official rules require public functional source, detectable MIT license,
visible CI and a public YouTube demonstration under three minutes. Submission
would accept competition terms; no final submission was performed.
[Submission requirements](https://gitlab-transcend.devpost.com/rules#submission-requirements).
The documented session retention limit comes from the [Sessions guide](https://docs.gitlab.com/user/duo_agent_platform/sessions/#session-retention),
not a promise that a public reviewer can access every trace.

Prepared recording outline, **2m45s**, using existing real evidence:

| Time | Show / narration |
|---|---|
| 0:00–0:20 | Product: Duo advises, CI measures, ReleaseGate decides eligibility; final execution remains closed |
| 0:20–0:55 | Original Phase 2 failure, real Code Review session/note, exact reviewed SHA; no claim Duo read raw logs |
| 0:55–1:20 | Codex-authored correction and actual successful pipeline; explicitly identify manual repair actor |
| 1:20–1:55 | Baseline 96 required tests, two LOW findings and exact-SHA ALLOW → HUMAN_APPROVAL / execution false |
| 1:55–2:25 | Separate planted fault MR !2, actual exit 127, skipped tests and deterministic missing-evidence DENY |
| 2:25–2:45 | Human review boundary, unchanged MRs, blocked Fix scope and honest Assisted classification |

Draft description: “ReleaseGate combines genuine GitLab Duo Code Review with
commit-bound CI evidence and deterministic release eligibility. Duo proposes;
reviewed changes run through tests and scanning. Missing evidence produces DENY;
passing evidence advances to human approval without authorizing execution.”
This is prepared text, not a published submission or recorded video. Prefer this
evidence-backed Assisted story to claiming an unexecuted Fix lifecycle.

Before submission, obtain human review of MR !1 and decide its publication through
the normal MR process; then verify source/setup/license on the default branch and
About recognition. Do not merge MR !2's deliberate fault into the baseline. Record
and review the public video, verify links/visibility, then separately authorize any
submission. Fix Flow is not required for the Assisted fallback; custom registration
and Runtime integration do not resolve this permission gap.

**Single most valuable next action:** a Maintainer independently reviews the
technical isolation proposal above and supplies evidence of enforceable scope.
Until then, retain BLOCKED and prepare the Assisted submission. This is not a request
for blanket permission to run the current broad profile.

## Files, evidence and preservation

Only `README.md`, `docs/phase2.5-foundational-duo-handoff.md` and this report change.
Application, mandatory tests, security checks, policy, Python requirements, lockfile,
AGENTS.md and shared Runtime are unchanged. New read-only metadata/source receipts
are ignored under `.artifacts/phase2.5-v2/`: `preflight.json`,
`recovered-git-state.json`, `security-probe.json`, `flow-identity.json`,
`platform-identities-and-history.json`, `source-permission-review.json` and
`public-readiness.json`. Source-definition hash:
`9519294d560601c76fff4d58747c4556c8c21ee650b08130f26d008e9017c978`.
Existing evidence remains under `.artifacts/phase2/` and `.artifacts/phase2.5/`.
No credentials, private environments, databases, logs or generated outputs are
published. No GitLab push, new pipeline/session, merge, protected-rule change,
account-permission change, deployment, purchase or real release effect occurred.
