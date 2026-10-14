# GitLab Duo release-risk flow — prepared, NOT VERIFIED

File: `.gitlab/duo/flows/release-risk.yaml`. This is a documented custom-flow body
for the AI Catalog editor, not a promised automatic repository integration.

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

## Exact setup after authenticated access is available

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

## Phase 2 access and qualification (2026-10-14)

Onboarding is complete and the official workspace is publicly readable. Local
GitLab authentication returned HTTP 401 and no controllable browser was connected.
Registration, project schema acceptance, trigger configuration, model execution and
sessions are **NOT VERIFIED**, blocked by authentication. No Codex output substitutes
for Duo evidence. Roles and existing credits/entitlements must be inspected after
login; do not purchase credits or change paid/security settings to unblock a run.
The current custom-flow schema chooses its model through group/instance settings;
our YAML deliberately has no `model` override. Platform documentation describes
credit consumption, but does not establish this hackathon project's entitlement.
[Platform prerequisites](https://docs.gitlab.com/user/duo_agent_platform/).

The reviewer must inspect mandatory-test coverage and unapproved skips in addition
to counts, findings and SHA. Its JSON remains advisory text even if valid: it cannot
produce `ApprovalFacts`, grant execution authorization or override a DENY. Record a
real session only after an MR and genuine pipeline context exist.
