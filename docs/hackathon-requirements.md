# Life After Code — requirement and evidence map

Researched on 2026-10-13 against **GitLab Transcend Life After Code**, not an earlier
GitLab event. Deadline: **2026-10-27 13:00 UTC / 2026-10-28 02:00 Pacific/Auckland**.
Selected category: **Path A / Supervised**; secondary objective: Most Stages Covered.
[Official event](https://gitlab-transcend.devpost.com/).

The official rules require a new Path A project created on or after October 5, 2026,
using GitLab Duo Agent Platform. The target autonomy delegates workflow steps while
a human reviews the outcome. Our new consumer app follows that direction; final
Supervised eligibility still needs a real automated Duo workflow and demonstration.
Dependency reuse is distinguished from copying a previous application, but the
shared Runtime's license must first be resolved. [Official rules](https://gitlab-transcend.devpost.com/rules).

| Submission requirement | ReleaseGate evidence / remaining work |
|---|---|
| New app and pipeline, post-code automation | New Python package, tests, CI and Duo flow |
| Genuine Duo Agent Platform use | Mandatory; NOT VERIFIED until actual session |
| Public GitLab project with full source/instructions | BLOCKED: onboarding incomplete; GitHub origin alone is insufficient |
| MIT license visible in GitLab About | Root LICENSE added; GitLab visibility NOT VERIFIED |
| Visible CI execution history | NOT RUN on GitLab; local pytest is not a substitute |
| Text description of problem, product and GitLab use | README / architecture foundation; final submission pending |
| Public YouTube demo under 3 minutes | NOT CREATED; show real automated ALLOW and DENY |
| Google Cloud deployment | Optional for Path A; NOT RUN; no bonus claimed |

The public project, visible pipeline history, MIT license and short public demo are
specified by the event submission checklist. Production hosting is optional for
Path A; there is no need to provision infrastructure in Phase 1.
[Submission requirements](https://gitlab-transcend.devpost.com/).

Contributor approval provisions a group, subgroup, project and welcome issue.
Onboarding typically takes about 24 business hours. The user is completing it;
do not infer permissions or credits until the provisioned project can be inspected.
[Official onboarding resources](https://gitlab-transcend.devpost.com/resources).

## Phase 1 acceptance

| Requirement | Status |
|---|---|
| Failed tests deny | Implemented; tested locally |
| HIGH/CRITICAL findings deny | Implemented; real Bandit HIGH demo plus policy CRITICAL tests |
| Missing/malformed evidence denies | Implemented; tested locally |
| Wrong commit denies | Implemented; tested locally |
| Missing final production approval denies | Implemented; tested locally |
| Passing evidence reaches next configured gate | ALLOW to HUMAN_APPROVAL; no execution authority |
| LLM recommendation is not authorization | No model input to policy or CLI approval; tested |
| Persisted JSON evidence bundle | Raw JUnit/Bandit, per-check envelopes, decisions, demo transcript |
| Real successful and blocked GitLab workflows | NOT RUN; local counterparts are explicitly labeled |
| Runtime integration without core modifications | BLOCKED by missing licensing and Python compatibility |

## Platform validation required after onboarding

Verify project membership (Maintainer for Catalog/trigger setup), Duo/Core/Agent
Platform enablement, custom-flow enablement, available credits, runner availability,
and protected-branch settings. These are independent prerequisites; public docs do
not prove a participant project's configuration. [Agent Platform prerequisites](https://docs.gitlab.com/user/duo_agent_platform/).

Supported read-only tools are selected explicitly in the prepared flow. Artifact
retrieval through the generic REST GET tool needs a real test; failure must become
`NOT_VERIFIED`, not invented clean evidence. [Agent tools](https://docs.gitlab.com/user/duo_agent_platform/agents/tools/).

Capture actual MR and head SHA, pipeline/job/artifact URLs, enabled flow version,
trigger identity and the AI session link/logs. Sessions provide execution visibility
through **AI > Sessions**. [Sessions](https://docs.gitlab.com/user/duo_agent_platform/sessions/).
