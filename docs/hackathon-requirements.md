# Life After Code - current requirement and evidence map

Revalidated **24 October 2026**. Deadline: **27 October 2026, 13:00 UTC /
28 October, 02:00 Pacific/Auckland**. Selected category: **Path A / Best Assisted
Agent**. Supervised and Hands-off are NOT_VERIFIED and are not submission claims.
[Official event](https://gitlab-transcend.devpost.com/),
[official rules](https://gitlab-transcend.devpost.com/rules).

Path A requires new hackathon work using the GitLab Duo Agent Platform, public
GitLab source/instructions with MIT licensing, visible pipeline history, a product
description and a public demo under three minutes. Deployment is optional for this
path; no deployment or bonus is claimed. Shared dependency reuse is distinct from
reusing an existing application. No final terms/submission action is included here.

| Requirement | Current evidence / limit |
|---|---|
| New application and CI | ReleaseGate consumer package, real tests, scan, policy and artifacts |
| Genuine Duo platform use | Historical finished Session 9451709 and actual finding 4012466889; reviewed earlier SHA |
| Public GitLab source | MR !1 merged into main at 81aadcf643f3375046c79c4ff611096923cd93a0; Phase 4 via separate unmerged MR |
| MIT license | LICENSE present on GitLab main; runtime package license verified separately |
| Visible CI | Historical main five automatic successes and untouched manual gate; exact Phase 4 qualification in final handoff |
| Product description | Current README, trust boundaries, lifecycle matrix and innovation statement |
| Revised public video | PLANNED; previous video intentionally removed; production materials ready, no old URL reused |
| Assisted autonomy | ASSISTED_VERIFIED: historical Duo advice, reviewed Codex correction, genuine CI |
| Additional autonomy | SUPERVISED_STATUS=NOT_VERIFIED; no custom Flow or Fix Flow execution |
| Production release | DISABLED; ALLOW is eligibility, execution_authorized=false |

Policy v2 denies failed/skipped/missing required tests, HIGH/CRITICAL findings,
unusable or missing evidence, wrong source/context and absent exact production
approval. Phase 4 retains all 96 original mandatory identities and adds mandatory
feature coverage. Real check trials and policy-only fixtures remain distinct.

See [baseline audit](phase4/00-baseline-audit.md),
[research method](phase4/01-research-methodology.md),
[lifecycle matrix](phase4/07-devsecops-lifecycle-matrix.md) and
[final handoff](phase4/14-final-handoff.md). Dated Phase 1/2/2.5 handoffs and the
GitLab initialization README are historical records, not current qualification.
