# Implementation plan

## Phase 0 — established locally

1. Read/preserve AGENTS.md and inspect the fresh repository/remotes.
2. Research the six official event/platform sources and the documented v1 flow
   specification, CI artifacts, manual jobs, tools, prerequisites and sessions.
3. Verify the initial shared release tag and inspect pinned metadata/reference.
   The historical v0.1.0 licensing concern is superseded by Phase 1.1 below.
4. Choose a Python 3.12 CLI with real pytest/Bandit evidence and no release execution.
5. Record onboarding as incomplete following the user's confirmation.

## Phase 1 — local vertical slice

- Pure policy with ALLOW/DENY reasons and explicit next gate. No execution framework.
- Trusted collector commands for actual tests and Bandit; raw and normalized JSON
  artifacts, source identity, exact SHA and pipeline-context consistency checks.
- Positive and negative policy tests, parser corruption tests, persisted tampering
  tests, CLI fail-closed checks and basic YAML structure checks.
- Six CI stages, artifacts on failure and default-branch blocking manual review.
- One read-only Duo risk-review flow prepared for AI Catalog import. Platform schema
  acceptance and execution are NOT VERIFIED; local YAML checks do not establish them.
- Isolated local ALLOW/DENY demonstrations using actual commands. No unsafe fixture
  function executes, no cloud resources and no simulated Duo result.
- MIT license, README and factual handoff with command evidence.

## Phase 1.1 — compatibility qualification (2026-10-14)

- Verify annotated v0.2.0 and immutable commit
  `7261fdd2f47d2b15fabe8faac527eeee37338eb1`, MIT terms and Python 3.13 metadata.
- Inspect the pinned handoff, adapter guide, consumer example and dependency
  template; record the template's stale v0.1.0 reference inside the release tag.
- Validate a separate non-editable Python 3.13 installation, source provenance,
  installed public API and dependencies. Confirm normal rejection on Python 3.12.
- Keep application dependencies, lockfile, 3.12 CI and execution policy unchanged.
  Correct only the release command's obsolete informational Runtime status.
- Rerun existing local validation and document results in `phase1.1-handoff.md`.

## Phase 2A — controlled GitLab import and genuine CI verification

1. Phase 1.2 added the provisioned project's separate GitLab remote. Its handoff was
   published to GitHub as `ba1690d787312d642e8bee2680f46d5d9f4a572c`. Preserve
   GitHub origin and `main -> origin/main`; refresh GitLab main before importing.
2. Verify authenticated identity, membership, branch/MR rights and runners. Current
   anonymous identity request returned HTTP 401; local authentication is BLOCKED.
   Complete independent local preparation while this external dependency is missing.
3. Policy v2 adds a reviewed, source-bound mandatory-test identity manifest and
   denies all skips. Qualify existing behavior and regression cases with real pytest,
   Bandit, ALLOW/DENY demos, frozen dependencies, static and package checks. Normally
   publish the reviewed preparation to GitHub and record its immutable source SHA.
4. Create `import/releasegate-phase2a` in an isolated worktree based on GitLab main.
   Transfer only tracked files from that GitHub SHA, archive the official initial
   README and add its workspace/welcome links to the product README. Validate the
   combined tree, commit locally, then push that branch and open an MR only after
   authenticated permissions are verified. Never merge unrelated histories or
   overwrite GitLab main; leave the MR open.
5. Use the project's documented `POST /projects/87602765/ci/lint` with the YAML
   `content` and `include_jobs: true`; after the branch exists, use `dry_run: true`
   and its `ref` to inspect pipeline creation. Lint/simulation is not job execution.
   [CI Lint API](https://docs.gitlab.com/api/lint/).
6. Observe actual validate/tests/security/release_policy/evidence_bundle jobs, their
   URLs, statuses, SHA, raw artifacts and decisions. Confirm runner context and
   artifact availability rather than inferring success from local checks.
7. Use isolated, safe negative branches for failing tests, mandatory omissions/skips,
   high findings and evidence/SHA mismatches. Preserve expected denial job failures
   separately from baseline defects. The existing tests and local demo prepare these
   checks; they do not prove hosted execution.
8. MR pipelines cannot demonstrate the protected-default-branch manual review rule.
   Inspect branch protection and server lint/job inclusion; defer actual protected
   main manual-job observation until a human authorizes/merges the MR. Do not weaken
   the rule, merge automatically, grant approval or perform production deployment.

## Phase 2B — genuine GitLab Duo release-risk workflow

1. After real MR/pipeline context exists, inspect existing feature entitlement,
   credits, custom-flow enablement and Maintainer/Owner permissions. Authentication
   currently blocks inspection; no paid resource activation is authorized.
2. Import and enable the prepared flow. Run Mention or Assign reviewer on a real MR.
   Resolve observed schema/tool differences using official documentation. Store the
   actual session URL, flow version, input SHA, tool calls and output without secrets.
3. Add Passed/Failed pipeline triggers only after validating their payloads. Keep
   deterministic CI policy independent of AI risk text. Do not invent a Duo API job.
4. Demonstrate one real passing candidate and one real blocked candidate, with AI
   session, pipeline/job URLs and raw artifacts. Runtime execution is not required
   to qualify these eligibility and human-review boundaries.

## Future milestone — persistent release execution after platform verification

1. Select an actual, explicitly authorized release effect and human-identity adapter.
   Decide whether the future execution composition and its CI should use Python 3.13
   together or a separately scoped 3.13 environment. Update metadata and the lock
   explicitly at that milestone; the new Runtime's MIT license is already verified.
2. Add only the immutable v0.2.0 dependency, verify the exact installed commit again,
   and compose one narrow release executor via
   the core reference pattern. Add the core-required acceptance cases: unregistered
   tool; target/binding/scope mismatch; no authorization; stale approval; duplicate
   effect and payload conflict; ambiguous outcome/no blind retry; persisted receipt.
3. Build a trusted GitLab human-approval identity adapter and independently scoped
   authorization. Only then consider a protected-environment production workflow.
   No mock deployment may be reported as production.
4. Retain the default five-second budget unless a measured use case needs an extended
   profile. Extended profiles need fresh binding/scope/ledger, approval and independent
   authorization; include profile/non-escalation/deadline/recovery acceptance tests.
5. Record a video showing real MR context, autonomous risk assessment, CI tests and
   scanning, DENY reasons, human gate and auditable outcome. Submit only on request.

The critical path is genuine GitLab integration, not frontend or infrastructure.
The next milestone is platform verification. Installation and licensing are qualified,
but trusted approval identity, authorization, executor and receipt verification still
need implementation before any production execution can be shown.
