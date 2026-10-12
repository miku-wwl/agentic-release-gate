# Implementation plan

## Phase 0 — established locally

1. Read/preserve AGENTS.md and inspect the fresh repository/remotes.
2. Research the six official event/platform sources and the documented v1 flow
   specification, CI artifacts, manual jobs, tools, prerequisites and sessions.
3. Verify the shared release tag and inspect pinned package metadata and consumer
   reference. Record missing license and the Python 3.13 requirement.
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

## Phase 2 — after onboarding and explicit delivery authorization

1. Obtain the official provisioned project URL and inspect roles, settings, runner,
   credits and available AI tools. Add the GitLab remote only when delivery is agreed.
2. Validate `.gitlab-ci.yml` with that project's GitLab CI Lint, publish the scoped
   changes when authorized, and preserve real passing/blocked pipeline histories.
3. Import and enable the prepared flow. Run Mention or Assign reviewer on a real MR.
   Resolve observed schema/tool differences using official documentation. Store the
   actual session URL, flow version, input SHA, tool calls and output without secrets.
4. Add Passed/Failed pipeline triggers only after validating their payloads. Keep
   deterministic CI policy independent of AI risk text. Do not invent a Duo API job.
5. Resolve the shared Runtime license explicitly for the pinned code. Use Python
   3.13 if that exact release remains required; do not bypass package metadata.
6. Install the immutable Git pin in an isolated environment; verify `direct_url.json`
   and inspect the installed public API. Compose one narrow release executor via
   the core reference pattern. Add the core-required acceptance cases: unregistered
   tool; target/binding/scope mismatch; no authorization; stale approval; duplicate
   effect and payload conflict; ambiguous outcome/no blind retry; persisted receipt.
7. Build a trusted GitLab human-approval identity adapter and independently scoped
   authorization. Only then consider a protected-environment production workflow.
   No mock deployment may be reported as production.
8. Record a video showing real MR context, autonomous risk assessment, CI tests and
   scanning, DENY reasons, human gate and auditable outcome. Submit only on request.

The critical path is genuine GitLab integration, not frontend or infrastructure.
Until the Runtime blockers are resolved, the authentic demo can show the eligibility
and human-review boundary, with production execution transparently unavailable.
