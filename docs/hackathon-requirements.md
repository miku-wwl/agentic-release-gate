# Life After Code — requirement and evidence map

Researched on 2026-10-13 against **GitLab Transcend Life After Code**, not an earlier
GitLab event. Deadline: **2026-10-27 13:00 UTC / 2026-10-28 02:00 Pacific/Auckland**.
Selected category: **Path A / Supervised**; secondary objective: Most Stages Covered.
[Official event](https://gitlab-transcend.devpost.com/).

The official rules require a new Path A project created on or after October 5, 2026,
using GitLab Duo Agent Platform. The target autonomy delegates workflow steps while
a human reviews the outcome. Our new consumer app follows that direction; final
Supervised submission still needs its public demonstration and final evidence review.
Dependency reuse is distinguished from copying a previous application.
[Official rules](https://gitlab-transcend.devpost.com/rules). Phase 1.1 independently
verified the shared Runtime v0.2.0 MIT license; execution integration remains deferred.

| Submission requirement | ReleaseGate evidence / remaining work |
|---|---|
| New app and pipeline, post-code automation | New Python package, tests, CI and Duo flow |
| Genuine Duo Agent Platform use | VERIFIED: finished Code Review session 9451709, real notes and Duo pipeline; custom risk contract pending |
| Public GitLab project with full source/instructions | VERIFIED on import branch and open MR !1; default main remains initialization |
| MIT license visible in GitLab About | LICENSE exists in published import branch; default-branch detection/About NOT VERIFIED (project API license is null) |
| Visible CI execution history | VERIFIED: hosted MR suite, scanning, policy, artifacts and safe boundary job |
| Text description of problem, product and GitLab use | README / architecture foundation; final submission pending |
| Public YouTube demo under 3 minutes | NOT CREATED; show real automated ALLOW and DENY |
| Google Cloud deployment | Optional for Path A; NOT RUN; no bonus claimed |

The public project, visible pipeline history, MIT license and short public demo are
specified by the event submission checklist. Production hosting is optional for
Path A; there is no need to provision infrastructure in Phase 1.
[Submission requirements](https://gitlab-transcend.devpost.com/).

Contributor approval provisions a group, subgroup, project and welcome issue.
Onboarding typically takes about 24 business hours. The workspace is now provisioned;
public read access does not establish authenticated permissions or credits.
[Official onboarding resources](https://gitlab-transcend.devpost.com/resources).

## Phase 1 acceptance

| Requirement | Status |
|---|---|
| Failed tests deny | Implemented; tested locally |
| Missing mandatory tests / unapproved skips deny | Policy v2; reviewed 96-case manifest; tested locally |
| HIGH/CRITICAL findings deny | Implemented; real Bandit HIGH demo plus policy CRITICAL tests |
| Missing/malformed evidence denies | Implemented; tested locally |
| Wrong commit denies | Implemented; tested locally |
| Missing final production approval denies | Implemented; tested locally |
| Passing evidence reaches next configured gate | ALLOW to HUMAN_APPROVAL; no execution authority |
| LLM recommendation is not authorization | No model input to policy or CLI approval; tested |
| Persisted JSON evidence bundle | Raw JUnit/Bandit, per-check envelopes, decisions, demo transcript |
| Real successful and blocked GitLab workflows | Real MR CI and expected DENY cases VERIFIED; negative fixtures run as derived snapshots inside CI, not separate branch pipelines |
| Runtime integration without core modifications | v0.2.0 MIT/install verified on 3.13; execution deferred until after GitLab verification |

## Current platform qualification and remaining work (2026-10-15)

Actual glab authentication, Developer membership, branch/MR access, hosted shared
runner execution, project Duo enablement and a genuine foundational review are
VERIFIED. Custom Catalog/trigger setup remains BLOCKED by the Developer role;
Maintainer/Owner setup is required. Specific model and credit balance remain
NOT VERIFIED; no paid settings changed. Protected main is unchanged and the MR is
open, so its manual gate and default-branch license detection still await human
review/merge. [Custom-flow prerequisites](https://docs.gitlab.com/user/duo_agent_platform/flows/custom/).

Supported read-only tools are selected explicitly in the prepared flow. Artifact
retrieval through the generic REST GET tool needs a real test; failure must become
`NOT_VERIFIED`, not invented clean evidence. [Agent tools](https://docs.gitlab.com/user/duo_agent_platform/agents/tools/).

Capture actual MR and head SHA, pipeline/job/artifact URLs, enabled flow version,
trigger identity and the AI session link/logs. Sessions provide execution visibility
through **AI > Sessions**. [Sessions](https://docs.gitlab.com/user/duo_agent_platform/sessions/).
