# ReleaseGate — unified Phase 2 handoff

Updated: **2026-10-15**, Pacific/Auckland. Overall verdict: **PARTIAL**.

GitHub publication, controlled GitLab import/MR, genuine hosted CI and a genuine
GitLab Duo Agent Platform Code Review Flow are **VERIFIED**. The prepared custom
Release Risk Reviewer, its bounded execution profile and final release-risk JSON
contract are **NOT VERIFIED**; registration is **BLOCKED** by the current Developer
role. Production execution remains closed. This is not a claim that the custom
flow or every competition requirement is complete.

## Recovery and authentication

The latest authentication retry resumed clean GitHub `main` at
`72c23e4f86af9cb0426a17cdcca1a0cded606606` and the existing isolated GitLab import
at `6b1b8c04ec9e770cf59e9bbff264e7454b52092b`. The earlier VS Code restart recovery
at `34a2b4f69b0ee3a6192f5a557cfe11dbdafcad70` is preserved in Git history.
Phase 1.2 publication `ba1690d787312d642e8bee2680f46d5d9f4a572c` was already an
ancestor of published main; it was verified and skipped. The original 14 Phase 2A
modified files were retained in the previously published hardening commit. No
completed import, commit or MR was recreated; no reset, clean, stash or rebase ran.

Previous attempts returned HTTP 401 despite Credential Manager entries. A
transient token-info check returned `invalid_token`; expiry/revocation cause was
not established. After the user's secure OAuth refresh, this agent independently
verified the specified glab **1.123.0** executable, `auth status`, `/user` and the
project API in the actual execution environment. Authentication is now **VERIFIED**:
`weilai-wang`, user ID `43343080`, active, group access **Developer (30)**.
No credential values were printed, saved, staged or embedded in URLs. No PAT or
replacement credential was created by the agent.

Authenticated project `87602765` has builds/MRs enabled, shared runners enabled,
Duo remote/foundational flows enabled, and an available Duo workflow runner.
Actual normal branch push and MR creation prove the necessary write operations.
Runner inventory returned **403**; this is an inventory permission limitation,
not unavailable CI: successful jobs independently identify shared instance runner
`54907241`. Protected main settings were inspected and retained unchanged; force
push is disabled. No paid entitlement, credit balance or model identifier is
inferred from these flags.

## Publication and repository identity

| Item | Verified checkpoint |
|---|---|
| Primary checkout | `D:\workshop\oct\agentic-release-gate`, branch `main` |
| GitHub origin, fetch/push | `git@github.com:miku-wwl/agentic-release-gate.git` — unchanged |
| GitHub upstream | `main -> origin/main` — unchanged |
| Phase 1.2 published commit | `ba1690d787312d642e8bee2680f46d5d9f4a572c` |
| Phase 2A mandatory-policy source | `98d81957f19afa8d7de8843236b7497d5baac2b3` |
| Hosted-boundary preparation, GitHub | `5cc2f679bef1160b507cca02b094a876c7448e00` |
| Gitless CI correction, GitHub | `3b6b27765fb0eed36b5f86ac90a6a5dca04d985e` |
| GitLab remote | `https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase.git` — unchanged |
| Isolated worktree | `D:\workshop\oct\agentic-release-gate-phase2a` |
| Integration branch / upstream | `import/releasegate-phase2a -> gitlab/import/releasegate-phase2a` |
| Initial imported snapshot | `6b1b8c04ec9e770cf59e9bbff264e7454b52092b` |
| Hosted-boundary commit reviewed by Duo | `4182deb55678382c0a99f7b1fd8e2232d17a0611` |
| Corrected, CI-qualified GitLab code | `d05e8bb205a0411c5f7b5bc5c6fc68b0b367a7cf` |
| GitLab main | `e4239c704040e427ef6ded36a4163113f995cef9` — initialization retained |
| Merge Request | [!1, opened](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/1), import branch → main; auto-merge disabled |

The existing import was pushed normally, then MR !1 was created once. It preserves
the initialization ancestor, original README bytes in `docs/gitlab-initial-README.md`
and official workspace/welcome links in the product README. The source consists of
reviewed tracked files, not environments, databases, caches or local evidence.
The initial import's 28 unchanged files matched the pinned source after line-ending
normalization. Later CI/script corrections were transferred from exact GitHub
blobs; unrelated histories were never merged. GitHub retains its original history.
Normal HTTPS pushes addressed the intended GitHub repository without changing its
SSH origin or primary upstream. GitLab pushes target only the integration branch.

This report records qualified code SHAs. Subsequent documentation-only publication
SHAs and the final matching local/tracking/live refs are recorded in the delivery
response, avoiding an impossible self-referential report commit.

## Local and genuine hosted CI qualification

`releasegate-policy-v2` uses the reviewed 96-identity `tests/required-tests.json`.
Every mandatory JUnit identity must occur exactly once; extra passing tests cannot
replace missing cases. Any skip denies; no allowlist is justified. The fixed
manifest is included in source identity. Existing failure, HIGH/CRITICAL, tampering,
provenance, stale approval, cross-pipeline and LLM-boundary tests remain covered.

Local frozen sync/lock checks, Ruff check/format and the complete suite passed.
After the gitless CI correction: **96 passed**, no failures/errors/skips; the full
real pytest/Bandit demo passed. Earlier packaging built sdist/wheel and imported
installed `releasegate==0.1.0` from an isolated Python 3.12.13 environment with
`uv pip check` passing. Package requirements, lockfile and the separate Runtime
probe were unchanged. These local results do not substitute for hosted evidence.

Authenticated server CI Lint accepted the actual seven-job YAML with `valid=true`,
no errors/warnings, including `review_release_candidate`. Hosted jobs use
`python:3.12.13-slim`, `uv==0.11.16` and frozen dependencies.

| Actual pipeline | SHA / observed result |
|---|---|
| [2946760514 — initial branch](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2946760514) | `6b1b8c0…`; SUCCESS, five jobs |
| [2946763436 — initial MR](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2946763436) | `6b1b8c0…`; SUCCESS, five jobs |
| [2946803065 — first boundary job](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2946803065) | `4182deb…`; FAILED: demo called unavailable `git`; five other jobs passed |
| [2946878007 — reviewed correction](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2946878007) | `d05e8bb…`; SUCCESS, all six MR jobs |

Pipeline `2946803065` was a real integration defect, not an expected policy DENY.
Its failure log is retained. The reviewed correction uses validated `CI_COMMIT_SHA`
in GitLab CI; local runs still use Git HEAD. No stale job was retried to disguise
the defect. A new commit produced the successful correction pipeline.

| Job in corrected pipeline | Actual status / ID |
|---|---|
| validate | SUCCESS / [17171566655](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17171566655) |
| tests | SUCCESS / [17171566656](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17171566656) |
| security | SUCCESS / [17171566657](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17171566657) |
| release_policy | SUCCESS / [17171566658](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17171566658) |
| evidence_bundle | SUCCESS / [17171566659](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17171566659) |
| release_boundary_demo | SUCCESS / [17171566660](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17171566660) |

Downloaded real logs/ZIPs were hash-recorded and extracted after path checks.
Raw hosted JUnit independently confirms **96 passed, 0 failures/errors/skips**, all
96 mandatory identities. Bandit 1.8.6 scanned all five source Python files, retaining
**B404/B603 LOW**, no MEDIUM/HIGH finding. Its raw exit 1 is recorded, while the
collector applies the existing HIGH threshold. Both envelopes bind `origin=gitlab-ci`,
project `87602765`, pipeline `2946878007`, SHA `d05e8bb…` and matching source digest.
The actual policy and evidence-bundle decisions are **ALLOW**, next gate
**HUMAN_APPROVAL**, always `execution_authorized=false`.

## Actual ALLOW/DENY boundaries

The genuine boundary job executes real commands in isolated derived snapshots.
Its outer `host_execution` records the actual project/pipeline/job IDs and SHA;
its inner reports deliberately remain `local-working-tree` evidence with empty
project/pipeline IDs. These are hosted demonstrations of safe negative fixtures,
not independent committed negative-branch pipelines or fabricated baseline reports.

| Observed case | Actual result |
|---|---|
| Full 96-case suite and normal scan | ALLOW → HUMAN_APPROVAL |
| Scanned-only unsafe fixture, real Bandit HIGH | DENY / SECURITY_HIGH; fixture never imported or executed |
| 83 passes plus one failed mandatory fixture test | DENY / TESTS_FAILED |
| 1 pass and 83 skipped mandatory fixture cases | DENY / UNAPPROVED_TEST_SKIPS, despite pytest exit 0 |
| 83 passes, one mandatory fixture case absent | DENY / MISSING_MANDATORY_TESTS, despite pytest exit 0 |
| Missing security report/envelope | DENY / MISSING_SECURITY_EVIDENCE, exit 1 |
| Both reports from another requested SHA | DENY / TESTS_COMMIT_MISMATCH + SECURITY_COMMIT_MISMATCH, exit 1 |
| Final production gate without verified human approval | DENY / PRODUCTION_APPROVAL_REQUIRED, exit 1 |
| Release command without executor | DENY / EXECUTION_NOT_CONFIGURED, exit 3 |

CRITICAL denial is covered by actual policy tests, not a claimed Bandit CRITICAL
finding. LLM recommendations cannot supply `ApprovalFacts` or override any DENY.
Every decision retains `execution_authorized=false`.

The protected-default-main manual job remains blocking (`allow_failure:false`) and
contains only eligibility evaluation, no deployment. Server lint accepts it, but
its actual protected-main execution is **NOT VERIFIED**: main still contains only
the initialization README and the MR must remain open. No fake human approval,
manual-job run or protected-environment deployment is claimed.

## Genuine Duo Agent Platform execution — VERIFIED

The existing project Code Review Catalog consumer `12590001`, item `1796`, was
invoked once through documented `POST /ai/duo_workflows/workflows`, with real MR !1,
its source branch and the actual failed pipeline `2946803065` as additional context.
No new service account, custom Catalog entry, paid setting or automatic trigger was
created. [Supported Flows API](https://docs.gitlab.com/api/duo_agent_platform_flows/).

| Actual Duo evidence | Observed result |
|---|---|
| [Agent Session 9451709](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/automate/agent-sessions/9451709) | `code_review/v1`, executed Catalog version `2514`, final status **finished** |
| [Duo pipeline 2946840620](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2946840620) | Source `duo_workflow`, **SUCCESS**, SHA `4182deb55678382c0a99f7b1fd8e2232d17a0611` |
| [Duo workload job 17171276318](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17171276318) | SUCCESS; real runner execution log retained |
| Actual trace | 16 entries, MR context/diffs, file discovery/read, structured model prescan and review-post tool |
| [Recommendation note 4012466889](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/1#note_4012466889) | GitLabDuo identified unavailable Git in slim image and recommended CI commit identity |
| [Summary note 4012466832](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/1#note_4012466832) | One concrete recommendation; actual model summary of the import |

The real recommendation agrees with the failed job log. It was reviewed and fixed
in GitHub `3b6b277…` / GitLab `d05e8bb…`; new MR CI independently passed. Duo reviewed
the earlier `4182deb…` commit, **not** the later corrected/documentation head. No
second review or inherited AI approval is claimed. This is genuine agent-assisted
review, not Duo Chat availability, prepared YAML or local Codex simulation.

The model's actual prescan JSON has `project_structure`,
`custom_instructions_summary`, `related_files`, `key_patterns`, `recommendations`.
The final recommendation is a real MR comment. This JSON is **not** the prepared
final release-risk assessment schema. No transformed local record is presented as
model-generated risk JSON. Supplied pipeline context is recorded; observed tools
prove MR/diff/file reads, not that Duo retrieved CI logs/artifacts or evaluated them.

**Resolved execution profile:** the request selected ambient and read-only privilege
IDs 2/8. The Catalog response instead assigned `environment=web`, privileges and
pre-approved privileges 3/4/5/8: `read_write_gitlab`, `run_commands`, `use_git`,
`read_only_files`; `mcp_enabled=true`. Observed tools read context/files and posted
MR review notes. No code mutation or production effect is observed, but hard
read-only enforcement is **NOT VERIFIED**. This profile is not the prepared custom
read-tool allowlist and must not be described as such.

The trace explicitly denied `.gitlab/duo/mr-review-instructions.yaml` because the
`.gitlab/duo` path matches Duo Context Exclusion. That file is absent here; the
prepared flow cannot be assumed to govern the foundational review. AGENTS.md and
docs were not fetched during prescan. No exclusion, protection or security setting
was changed to bypass this. [Code Review Flow](https://docs.gitlab.com/user/duo_agent_platform/flows/foundational_flows/code_review/).

## Changed files, preserved evidence and repository status

This successful-authentication continuation changes only:

- `.gitlab-ci.yml`: genuine MR boundary-demonstration job; no deployment command.
- `scripts/demo.py`: actual failed-test/missing-evidence/SHA demonstrations, outer
  host context and gitless CI identity correction.
- `README.md`, `docs/architecture.md`, `docs/duo-integration.md`,
  `docs/implementation-plan.md`, `docs/hackathon-requirements.md` and this handoff:
  actual platform results and remaining limits.

Earlier policy/source/test changes, AGENTS.md, license, pinned Runtime guidance,
Python requirements, lockfile, commits, initialization history and previous evidence
are retained. No shared Runtime source was modified. Existing root `main` and
integration worktree were clean after code correction publication. Reviewed
report changes are separately committed; final status/ref equality is checked
again and reported with the documentation publication SHAs.

Raw API receipts, traces, logs, actual artifacts and bounded qualification metadata
remain ignored under `.artifacts/phase2/auth-refresh-retry/`. Earlier evidence under
`.artifacts/phase2/` and `resume-20261015/` remains preserved. No generated report,
credential, environment, database, build output or temporary helper is staged.
Public pipeline/job/session/note URLs above provide platform evidence.

Key retained receipts: `preflight.json`, `project-access.json`, `ci-boundaries-lint.json`,
`ci-verification-2946878007.json`, `boundary-ci-verification.json`,
`duo-invocation-request.json`, `duo-invocation-response.json`, `duo-session-current.json`,
`duo-trace-current.jsonl`, `duo-prescan-output.json`, `duo-mr-notes.json` and
`duo-pipeline-verification.json`. Corrected boundary ZIP SHA-256:
`36ae41bfc350c4d4d79d342a8fc40eaf4f41f9441f59e43ecc3191e07777912f`;
its real verification transcript SHA-256:
`50d8d98efcfb3aa015c901c59cbe947ff1a91fbb29152c6e0275c067ce0bf403`.

## Remaining blockers and next action

| Item | Classification / exact remaining work |
|---|---|
| Authentication, import/MR, CI, foundational Duo | VERIFIED; previous 401 blocker resolved |
| Prepared custom Release Risk Reviewer | BLOCKED: Developer (30); create/enable requires Maintainer/Owner |
| Custom final risk JSON, bounded read-tool profile and event trigger | NOT VERIFIED; require actual registration, resolved-profile inspection and a real session |
| Duo reads of raw pipeline artifacts / independent blocked-candidate risk assessment | NOT VERIFIED; do not infer from passing CI or supplied context |
| Protected-main manual job and About license detection | NOT VERIFIED while MR remains open; project API currently reports license null, LICENSE is published on integration branch |
| Authenticated final approval, independent authorization, persistent release effect/receipt | PLANNED future milestone; no production executor exists |
| Public sub-three-minute demo and final competition submission | PLANNED; neither published nor submitted |

**Next action:** have a Maintainer/Owner review and register the bounded custom
Release Risk Reviewer, respecting existing context exclusions. Verify its actual
resolved privileges, real MR/CI artifact reads and final risk JSON on passing and
blocked evidence before claiming the product workflow complete. Creation/enablement
requires that role; no permission escalation was attempted.
[Custom-flow permissions](https://docs.gitlab.com/user/duo_agent_platform/flows/custom/).

The open MR is ready for human review. Do not automatically merge it to exercise
the main gate. The shared Runtime's MIT/install compatibility remains qualified,
but it belongs after platform qualification in an explicitly scoped persistent
Approval/Authorization/Action/Receipt milestone, not in these CI policy jobs.
No force push, protected-rule change, production approval, deployment, paid
provisioning or real release effect occurred.
