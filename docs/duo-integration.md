# GitLab Duo integration — genuine foundational review, custom flow pending

Updated: 2026-10-15. Authentication is VERIFIED in the actual glab execution
environment as `weilai-wang`, Developer (30). The project has enabled foundational
and remote flows and an available Duo workflow runner. The existing Code Review
Catalog consumer `12590001` (item `1796`, executed version `2514`) was invoked once
on real MR !1 through the supported Flows API, after a real pipeline existed.
[Flows API](https://docs.gitlab.com/api/duo_agent_platform_flows/).

- [Session 9451709](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/automate/agent-sessions/9451709): `code_review/v1`, **finished**.
- [Duo pipeline 2946840620](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2946840620): genuine `duo_workflow`, **success**, reviewed SHA `4182deb55678382c0a99f7b1fd8e2232d17a0611`.
- [Actual Duo recommendation](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/1#note_4012466889): `git` is absent in the slim CI image; use CI commit identity for the demo. The failed job log independently confirms this defect.
- Reviewed correction `d05e8bb205a0411c5f7b5bc5c6fc68b0b367a7cf` uses validated `CI_COMMIT_SHA` only in GitLab CI, retaining local Git lookup. [Corrected MR CI 2946878007](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2946878007) passed all six jobs.

The actual trace includes structured model prescan JSON (`project_structure`,
`custom_instructions_summary`, `related_files`, `key_patterns`, `recommendations`),
MR context/file reads and `post_duo_code_review`. Its final advice is in MR comments.
This is real Agent Platform execution, not Codex output. It does **not** qualify the
prepared custom release-risk JSON contract or prove that Duo read CI artifacts.
The invocation supplied the actual failed pipeline as additional context; observed
tools prove MR/diff/file reads, not retrieval or interpretation of that pipeline.

The Catalog resolved `environment=web` with approved privileges
`read_write_gitlab`, `run_commands`, `use_git`, `read_only_files`, despite the
request's ambient/read-only selection. Only context/file reads and MR review posts
were observed; a hard read-only restriction is **NOT VERIFIED**. The trace also
records access denial for `.gitlab/duo/mr-review-instructions.yaml` because
`.gitlab/duo` matches Duo Context Exclusion. That file is not present in this
repository; no group exclusion or security setting was changed. Do not claim the
prepared YAML or AGENTS.md governed this foundational review.
[Code Review Flow behavior](https://docs.gitlab.com/user/duo_agent_platform/flows/foundational_flows/code_review/).

File: `.gitlab/duo/flows/release-risk.yaml`. This is a documented custom-flow body
for the AI Catalog editor; registration and execution remain **NOT VERIFIED**.
Creating/enabling it is **BLOCKED** by the current Developer role: the supported
setup requires Maintainer/Owner. Existing foundational execution did not register
this file. [Custom-flow permissions](https://docs.gitlab.com/user/duo_agent_platform/flows/custom/).

## Purpose and boundaries

Given a real MR, the flow reads its SHA, diff, CI configuration, pipeline/jobs and
available policy evidence. It returns advisory JSON with concrete risks, evidence
URLs, remediation and limitations. Its allowlist contains only supported read tools:
`get_merge_request`, `list_merge_request_diffs`, `get_repository_file`,
`get_job_logs`, `gitlab_api_get`. It has no commit, merge, approve, deploy or shell
tool. [Official tool list](https://docs.gitlab.com/user/duo_agent_platform/agents/tools/).

No custom-agent API or unsupported `response_schema_id` is assumed. The selected
flow uses one AgentComponent, an inline prompt, a final-answer log event and `end`
routing. JSON is requested in the prompt; Phase 1 never trusts this text as policy
input. [Custom-flow schema](https://docs.gitlab.com/user/duo_agent_platform/flows/custom_flows_schema/).

## Remaining custom-flow setup by a Maintainer/Owner

1. Open the provisioned project and welcome issue. Verify runner access and Duo
   enablement/credits; note the actual roles and supported features.
2. As Maintainer/Owner, open **AI > Flows > New flow**. Enter display name
   `ReleaseGate risk reviewer`, a short description, and initially Private visibility.
   Under Configuration choose Flow and paste the contents of our YAML. Save the
   server's validation outcome. A saved file alone is insufficient.
3. Enable the flow for the project. Record the Catalog item/version and the service
   account provided by GitLab. The managing project uses its current Catalog version;
   preserve a configuration hash with the session evidence.
4. Create a trigger under **AI > Triggers > New flow trigger**. Select Mention or
   Assign reviewer, the actual service account, and **AI Catalog** configuration
   source. Do not guess a service-account username or require the flag-gated
   Configuration path option.
5. For Mention, add a real MR comment using the shown service-account mention and
   ask it to assess the MR and its current pipeline. For Assign reviewer, assign that
   account as reviewer; the flow receives MR IID through `context:goal`.
6. In **AI > Sessions**, preserve the actual session link, input context, read tool
   calls, retrieved SHA/pipeline and final response. Confirm each cited source exists.
7. Repeat against a blocked MR/pipeline. Validate that missing reports remain
   insufficient evidence and old pipeline success never authorizes the new SHA.

Catalog registration and enablement are the supported UI path for custom flows.
[Create/enable a flow](https://docs.gitlab.com/user/duo_agent_platform/flows/custom/).
Trigger events, service account and configuration source are separate project
settings. [Trigger setup](https://docs.gitlab.com/user/duo_agent_platform/triggers/).

## Evidence to preserve

Store MR URL/IID and head SHA, pipeline/job URLs and raw artifact digests, flow
configuration/version, trigger account/event, actual AI session URL/logs and advisory
JSON. Preserve limitations if the read-only REST tool cannot retrieve JSON artifacts.
Use job logs as observed context without claiming an artifact was retrieved.
Do not save tokens or full sensitive job logs to the public repository.

After successful initial runs, consider pipeline Passed/Failed triggers with a
separate prompt handling the documented webhook payload. No generic MR-updated
trigger is assumed. The current trigger documentation also lists selected MR
actions, such as Created and Marked ready; verify the actual project's supported
actions before selecting one. Mention/Assign reviewer remains the minimal first run.

## Remaining qualification

Onboarding and authentication are complete. Foundational execution, its session,
pipeline and model recommendation are VERIFIED. Custom registration, server schema
acceptance, event trigger, strict read-tool allowlist and final risk JSON remain
NOT VERIFIED. No paid feature or model purchase was made; credit balance and the
specific model identifier are not established by the captured session.
The current custom-flow schema chooses its model through group/instance settings;
our YAML deliberately has no `model` override. Platform documentation describes
credit consumption, but does not establish this hackathon project's entitlement.
[Platform prerequisites](https://docs.gitlab.com/user/duo_agent_platform/).

The reviewer must inspect mandatory-test coverage and unapproved skips in addition
to counts, findings and SHA. Its JSON remains advisory text even if valid: it cannot
produce `ApprovalFacts`, grant execution authorization or override a DENY. Record a
real session only after an MR and genuine pipeline context exist.
