# ReleaseGate — unified Phase 2 handoff

Updated: **2026-10-15**, Pacific/Auckland, after VS Code restart.
Final verdict: **PARTIAL**; authenticated remote stages remain **BLOCKED**.

GitHub publication, mandatory-test hardening and the isolated local GitLab import
are VERIFIED. GitLab publication, MR creation, hosted CI and genuine Duo execution
are BLOCKED by unusable authentication. They are NOT VERIFIED; Phase 2 is not
complete. No model result, approval or platform execution has been fabricated.

## Recovered checkpoint and current authentication diagnosis

The resumed primary checkout was clean on `main` at
`34a2b4f69b0ee3a6192f5a557cfe11dbdafcad70`, equal to `origin/main` and the live
GitHub main ref. Phase 1.2 commit `ba1690d787312d642e8bee2680f46d5d9f4a572c`
was verified as an ancestor of published main, so publication was skipped.
No completed import or commit was repeated. The existing isolated worktree remains
on `import/releasegate-phase2a` at `6b1b8c04ec9e770cf59e9bbff264e7454b52092b`.
All 28 unmodified source files still match the validated GitHub snapshot after
line-ending normalization; the initialization README remains preserved. Both
worktrees were clean at recovery, and the remote/upstream configuration is unchanged.
Fresh GitLab fetch/ref checks still show only initialization main at
`e4239c704040e427ef6ded36a4163113f995cef9`. Anonymous open-MR and pipeline lists
are empty; these reads do not establish authenticated permissions.

The specified glab executable is still 1.123.0. The fresh Codex process's explicit
`auth status` and identity request return HTTP 401. Host selection is correctly
`gitlab.com` over HTTPS. The actual Local AppData configuration lacks an account,
OAuth type/expiry metadata and keyring-mode setting. No authentication environment
override was present at process, user or machine level, and no legacy Roaming or
`.config` glab configuration was found.

**Correction to the earlier incomplete credential diagnosis:** targeted native
Windows Credential Manager enumeration succeeded in the current Windows session.
The `glab:gitlab.com:token:` and `glab:gitlab.com:oauth2_refresh_token:` entries
exist with credential blobs. This is not a demonstrated keyring-access denial.
A child-process keyring-mode check still returned 401. A documented Bearer request
using only the stored access token also returned 401; `/oauth/token/info` explicitly
returned `invalid_token`, with description `The access token is invalid`.
Expiration, revocation and the reason for the missing CLI metadata are not proven.
The ChatGPT Work PASS report therefore has not been reproduced in this execution
context, and the authenticated GitLab identity remains NOT VERIFIED.
[CLI authentication/storage](https://docs.gitlab.com/cli/authentication/),
[OAuth token information](https://docs.gitlab.com/api/oauth2/).

Credential values were used only transiently in memory for those GitLab GETs;
none were printed, saved, staged or sent in URLs. No credentials were removed,
rewritten, refreshed or regenerated. No personal access token was created. A secure
interactive login under the current Windows account has been requested, followed
by status/identity verification. Repeating identical failing requests was avoided.
Identity, role, runner, MR/write permissions and Duo entitlement remain unresolved,
so no branch push, MR, CI job or Duo mutation was attempted on this resume.

Fresh independent local qualification passed frozen sync/lock checks and Ruff
check/format checks. The imported full suite passed **96 tests in 0.71s**, with
zero failures/errors/skips and all 96 mandatory identities verified against JUnit.
Real local pytest/Bandit demonstrations again yielded ALLOW for the baseline and
DENY for HIGH findings, 1 pass/83 skips and one missing mandatory case. Production
final approval remained required and the release command remained DENY/exit 3.
The source distribution and wheel rebuilt successfully; a fresh Python 3.12.13
wheel probe imported `releasegate==0.1.0` from its installed site-packages and passed
`uv pip check`. These results are local, not hosted CI or Duo execution.

New sanitized diagnostics and qualification outputs are under
`.artifacts/phase2/resume-20261015/`; the imported JUnit is
`.artifacts/phase2/resume-20261015.junit.xml` in its own worktree. The new local demo
transcript is `demo/8bd53426-fc56-4fc2-87ee-a5bacd9e657d/verification.json` under
the primary resume directory. Earlier evidence was preserved. Only this handoff
changed during recovery; application, tests, CI, flow configuration and Runtime
source remain unchanged. GitHub publication of this new factual report does not
repeat any earlier publication. Server CI/Duo documentation was refreshed; server
qualification and actual project feature access still require successful identity.

## Publication and repository identity

| Item | Actual result |
|---|---|
| Phase 1.2 GitHub publication | `ba1690d787312d642e8bee2680f46d5d9f4a572c` — VERIFIED |
| Validated Phase 2A GitHub source | `98d81957f19afa8d7de8843236b7497d5baac2b3` — VERIFIED on `main` |
| GitHub origin, fetch/push | `git@github.com:miku-wwl/agentic-release-gate.git` — preserved |
| GitHub upstream | `main -> origin/main` — preserved |
| GitLab remote | `https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase.git` |
| GitLab project API ID / visibility | `87602765` / public — VERIFIED by public project API |
| Live GitLab main | `e4239c704040e427ef6ded36a4163113f995cef9` — initialization unchanged |
| Integration branch | `import/releasegate-phase2a` — prepared locally, not pushed |
| Local import commit | `6b1b8c04ec9e770cf59e9bbff264e7454b52092b` |
| Merge Request URL / status | None created; BLOCKED |
| GitLab pipeline URLs / IDs / jobs | None created or observed; NOT VERIFIED |
| Duo registration / session URL / ID | None; NOT VERIFIED |

[Phase 1.2 commit](https://github.com/miku-wwl/agentic-release-gate/commit/ba1690d787312d642e8bee2680f46d5d9f4a572c),
[Phase 2A source commit](https://github.com/miku-wwl/agentic-release-gate/commit/98d81957f19afa8d7de8843236b7497d5baac2b3),
[official GitLab project](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase),
[welcome issue](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/work_items/1).

GitHub pushes were normal HTTPS pushes to the same repository, with no origin URL
or upstream change. Local, tracking and live GitHub source SHAs matched after
publication. This handoff is a subsequent documentation publication; its commit
SHA is reported in the delivery response rather than embedded in its own contents.

The isolated worktree is `D:\workshop\oct\agentic-release-gate-phase2a`.
Its two-commit history preserves the GitLab initialization ancestor. It imports
29 tracked GitHub files, explicitly reconciles README.md with official workspace
and welcome links, and adds `docs/gitlab-initial-README.md` containing the exact
original README bytes. The other 28 files were checked against the source Git blobs.
The archived template's origin/force-push instructions were not executed.
GitHub retains its original, independent history; no unrelated-history merge occurred.
Both worktrees were clean after their respective commits; ignored environments,
evidence, builds and local artifacts remain local. GitLab still has only `main`.

## Policy hardening and local qualification — VERIFIED

`releasegate-policy-v2` uses a reviewed, versioned mandatory-test manifest at
`tests/required-tests.json`. It contains 96 unique JUnit `classname::name` identities,
independently matched to the real full-suite report. Additional passing cases cannot
replace missing mandatory cases. Duplicate, absent or malformed identities/policy
deny. Any skipped test denies; no exception or allowlist is currently justified.
The manifest is included in source identity and read only from the fixed trusted
repository path. Pure-policy callers must explicitly supply the trusted identity
set; omitting it denies. Manifest/test/policy changes still require protected review:
hashes do not defend against someone controlling both the code and its runner.

| Validation | Observed local result |
|---|---|
| Python / uv | 3.12.13 / 0.11.16 |
| Frozen sync and lock check | Passed, unchanged dependency requirements/lockfile |
| Ruff check and format check | Passed |
| Complete suite in primary checkout | **96 passed**, 0 failed/errors/skipped, 0.95s |
| Complete suite in imported tree | **96 passed**, 0 failed/errors/skipped, 1.01s |
| Imported commit's actual collector | **96 passed**; SHA bound to local import commit |
| Packaging | sdist and wheel built; mandatory manifest and MIT license in sdist; MIT license in wheel |
| Isolated wheel installation | `releasegate==0.1.0`, policy v2; imported from probe site-packages; `uv pip check` passed |
| Diff/secret review | Worktree and staged diff checks passed; bounded scan: 29 source / 30 import files, no matched secret or forbidden path patterns |

The previous 84-test behavior remains covered, with 12 additional cases for
mandatory policy, skips, substitutions, duplicates and invalid manifests. Existing
failure, CRITICAL/HIGH severity, provenance, tampering, stale approval, context and
LLM-boundary cases continue to pass. Local YAML tests check structure only, not
GitLab's server acceptance. Secret-pattern review is bounded, not a certification.

| Actual local demonstration | Result / evidence |
|---|---|
| Normal full suite + Bandit | ALLOW, `CHECKS_PASSED`, next gate `HUMAN_APPROVAL` |
| Scanned-only unsafe fixture | DENY, `SECURITY_HIGH`; actual Bandit B602 HIGH |
| Mandatory 84-case suite: 1 pass + 83 skips | DENY, `UNAPPROVED_TEST_SKIPS`, despite pytest exit 0 |
| Mandatory 84-case suite: 83 passes, one absent | DENY, `MISSING_MANDATORY_TESTS`, despite pytest exit 0 |
| Missing security envelope/report | DENY, `MISSING_SECURITY_EVIDENCE`, exit 1 |
| Requested SHA differs from both reports | DENY, `TESTS_COMMIT_MISMATCH` and `SECURITY_COMMIT_MISMATCH`, exit 1 |
| Production final gate without verified human approval | DENY, `PRODUCTION_APPROVAL_REQUIRED`, exit 1 |
| Release command | DENY, `EXECUTION_NOT_CONFIGURED`, exit 3 |

The baseline Bandit 1.8.6 scan covers all five source Python files, retaining
B404 and B603 LOW findings and no MEDIUM/HIGH findings. Its raw exit is 1 because
findings exist; security collection exits 0 under the existing HIGH threshold.
The unsafe demonstration scans six files and records three LOW plus one HIGH;
the fixture is never imported or executed. CRITICAL denial is a policy test, not
a claimed Bandit CRITICAL result. All decisions retain `execution_authorized=false`.

Local evidence is ignored and was not uploaded as generated test output:

- Primary checkout `.artifacts/phase2/qualification.junit.xml`.
- `.artifacts/phase2/demo/af9ed9f1-e521-4a95-8e36-c75b7948f955/verification.json`
  and each scenario's raw JUnit/Bandit, normalized envelopes and decisions.
- `.artifacts/phase2/dist/`, `wheel-probe/`, `artifact-hashes.json`.
- Import worktree `evidence/` and `.artifacts/phase2/import-command-evidence.json`,
  `import-validation.junit.xml`, `additional-denials.json`.

The demo explicitly describes local snapshots with then-uncommitted preparation
changes. The import collector records the committed import SHA. Neither is a
GitLab CI attestation. SHA-256 of the saved demo transcript is
`a41eceb8b6a93485aa744acf5aee9f890c190f66414b41e19ef9877b7c15e888`.

## Hosted CI attempt and remaining access — BLOCKED

At the initial attempt, public project reads and remote fetch succeeded. Public APIs returned empty current
pipeline and open-MR lists; this does not prove authenticated permissions. Preflight
found no usable process GitLab token, existing glab configuration or Git credential;
noninteractive credential lookup exited 128. `glab` was not yet installed and the approved
computer-use inventory had no browser surfaces. Anonymous `/api/v4/user` returned
**HTTP 401**. No signed-in account or project role was established.

**Authentication retry after the user's installation report:** the specified
`C:\Users\weila\AppData\Local\Programs\glab\glab.exe` is VERIFIED as 1.123.0.
It resolves configuration to
`C:\Users\weila\AppData\Local\glab-cli\config.yml`. In the current Windows account,
that host's `token`, `user` and `use_keyring` settings are empty. No process, user
or machine authentication variables were present. Actual glab calls to `user`,
project metadata, project runners, protected branches and open MRs all returned
HTTP 401; repeating identity lookup without environment token overrides did too.
`glab auth status --hostname gitlab.com --output json` reports state `error`.
The user-reported `weilai-wang` login therefore remains NOT VERIFIED in this
agent's context. The controlled-browser inventory is still empty. This is a
persistent-authentication/context blocker, not an inferred lack of project role.
No credential value was logged or requested in chat. Filtered results are saved
in `.artifacts/phase2/authenticated/preflight.json`; the existing source commits,
clean worktrees, remote configuration and local import branch are preserved.
A refreshed noninteractive Git Credential Manager lookup also exited 128 with no
credential available; `.artifacts/phase2/authenticated/git-credential-preflight.json`
records only that outcome. No GitLab write, MR or pipeline was attempted during
this failed authenticated preflight.

The actual anonymous project CI Lint request, using the source YAML and documented
`POST /projects/87602765/ci/lint`, returned **HTTP 403 Forbidden**. Server-supported
configuration acceptance is NOT VERIFIED. No runner job was started. Sanitized
responses are in `.artifacts/phase2/gitlab-access.json`, `gitlab-ci-lint.json` and
`public-project.json`; credentials were neither saved nor printed.
[CI Lint API](https://docs.gitlab.com/api/lint/).

Identity, membership, branch/MR rights, protected-branch settings, available runners
and credits/entitlements remain NOT VERIFIED. A dry-run push was not used to bypass
the identity check. Branch push and MR creation are PLANNED after that check passes.
Hosted tests, scans, policy/artifacts and negative pipelines remain NOT VERIFIED.

The prepared CI has validation, tests, security, policy, evidence and release-review
stages, with raw failure artifacts and no deployment/infrastructure commands.
`review_release_candidate` is manual and blocking only on protected default main.
Its eligibility evaluation is an evidence review, not final human approval or
execution authorization. An unprotected import/MR branch cannot exercise that rule;
inspect lint inclusion/protection and observe the real default-branch gate only
after a human merges. Automatic merge, protection weakening and deployment remain
outside this run. [Manual-job rules](https://docs.gitlab.com/ci/jobs/job_control/).

## Duo mechanism and execution — NOT VERIFIED

Official documentation was refreshed on 2026-10-14. The prepared minimum is one
ambient v1 custom flow, created/enabled through the project's AI Catalog UI, then
triggered with Mention or Assign reviewer on an actual MR. It uses only MR, diff,
repository-file, job-log and REST GET tools. It requests advisory JSON; it has no
merge, approval, deployment or shell tool. Its prompt now calls out mandatory tests
and unapproved skips. [Custom flows](https://docs.gitlab.com/user/duo_agent_platform/flows/custom/),
[read tools](https://docs.gitlab.com/user/duo_agent_platform/agents/tools/).

The current schema supports `context:project_id` and trigger-specific `context:goal`;
it restricts environment to ambient, excludes prompt model overrides and
`response_schema_id`, and lets the configured group/instance provider choose the
model. Actual entitlement/model availability is not established by these docs.
The prepared flow omits these restricted fields. Mention/Assign reviewer is the first
strategy; selected MR or pipeline events need project-specific verification.
[Custom-flow schema](https://docs.gitlab.com/user/duo_agent_platform/flows/custom_flows_schema/),
[triggers](https://docs.gitlab.com/user/duo_agent_platform/triggers/).

An independent anonymous read of GitLab's public GraphQL schema also confirmed
`aiCatalogFlowCreate`, `aiCatalogItemConsumerCreate`, `aiFlowTriggerCreate` and
`aiDuoWorkflowCreate` and their input contracts. Selected schema metadata is saved
locally in `.artifacts/phase2/authenticated/duo-registration-schema.json`.
This supplies a possible API route after identity, project permissions and real
MR/pipeline context are verified; no mutation was attempted. A public schema is
not proof of account entitlement, successful registration or model execution.
[GitLab GraphQL API](https://docs.gitlab.com/api/graphql/).

No registration, service account, trigger, server validation, actual invocation,
agent output or session/log URL exists from this run. Authentication blocks the UI;
missing licensing or runner entitlement is not asserted without inspection.
Code/YAML preparation is PLANNED integration, not real Duo evidence. Do not activate
paid resources or change security settings to make a demonstration pass.

AI advice cannot produce trusted `ApprovalFacts`, waive deterministic DENY or grant
authorization. Final production approval remains separate from execution authority.
No authenticated approval adapter or executor exists; the release command stays
closed. The optional pinned Agentic Intent Gate v0.2.0 remains a future Python 3.13
execution component, after genuine Duo/CI verification. No shared core changes,
Runtime invocation, real release effect or deployment occurred.

## Changed files and next milestone

The GitHub preparation commit changed the following 15 files:

- `src/releasegate/{policy,evidence,cli}.py`: mandatory identities, skip denial,
  source binding, trusted manifest loading and policy version.
- `tests/{conftest,test_cli,test_evidence,test_policy}.py` and
  `tests/required-tests.json`: preserved fixtures and new regression cases/manifest.
- `scripts/demo.py`: real isolated skip and missing-case demonstrations.
- `.gitlab/duo/flows/release-risk.yaml`: advisory mandatory-test risk instructions.
- `README.md`, `docs/{architecture,duo-integration,hackathon-requirements,implementation-plan}.md`:
  policy contract, current onboarding/auth state and correct Phase 2A/2B ordering.

This handoff is an additional GitHub documentation file. The local import includes
the source snapshot plus the preserved initial README and explicit README additions.
`.gitlab-ci.yml`, AGENTS.md, Python requirements and uv.lock were carried unchanged;
no environments, credentials, databases, caches or generated outputs were staged.

**Single most valuable next action:** complete secure interactive login in the
current Windows account using the installed executable, which defaults to native
keyring storage, and verify status before continuing:

```powershell
& 'C:\Users\weila\AppData\Local\Programs\glab\glab.exe' auth login --hostname gitlab.com --web --git-protocol https
& 'C:\Users\weila\AppData\Local\Programs\glab\glab.exe' auth status --hostname gitlab.com
```

Report only PASS/FAIL, not a token or token-bearing output. A controllable,
signed-in GitLab browser remains an alternative. Do not log out or delete existing
credentials as a troubleshooting step.
Then verify identity/role/runners, refresh GitLab main, normally publish the prepared
branch, open and leave an MR, qualify genuine hosted CI, and register/run the Duo
reviewer against that real context. Record real URLs/statuses and update this handoff.
The public GitLab source/MIT display, pipeline/session evidence, short demo video and
competition submission remain outstanding. Runtime execution is not the next blocker.
