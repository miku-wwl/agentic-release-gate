# ReleaseGate — unified Phase 2 handoff

Date: **2026-10-14**, Pacific/Auckland. Final verdict: **PARTIAL**.

GitHub publication, mandatory-test hardening and the isolated local GitLab import
are VERIFIED. GitLab publication, MR creation, hosted CI and genuine Duo execution
are BLOCKED by unavailable authentication. They are NOT VERIFIED; Phase 2 is not
complete. No model result, approval or platform execution has been fabricated.

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

Public project reads and remote fetch succeeded. Public APIs returned empty current
pipeline and open-MR lists; this does not prove authenticated permissions. Preflight
found no usable process GitLab token, existing glab configuration or Git credential;
noninteractive credential lookup exited 128. `glab` is not installed and the approved
computer-use inventory had no browser surfaces. Anonymous `/api/v4/user` returned
**HTTP 401**. No signed-in account or project role was established.

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
The prepared flow has no unsupported fields. Mention/Assign reviewer is the first
strategy; selected MR or pipeline events need project-specific verification.
[Custom-flow schema](https://docs.gitlab.com/user/duo_agent_platform/flows/custom_flows_schema/),
[triggers](https://docs.gitlab.com/user/duo_agent_platform/triggers/).

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

**Single most valuable next action:** configure usable GitLab authentication locally
or connect a controllable, signed-in GitLab browser; do not paste a token into chat.
Then verify identity/role/runners, refresh GitLab main, normally publish the prepared
branch, open and leave an MR, qualify genuine hosted CI, and register/run the Duo
reviewer against that real context. Record real URLs/statuses and update this handoff.
The public GitLab source/MIT display, pipeline/session evidence, short demo video and
competition submission remain outstanding. Runtime execution is not the next blocker.
