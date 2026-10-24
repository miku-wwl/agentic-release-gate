# Video evidence index

| Shot | Authentic source | Identity / limitation |
|---|---|---|
| Duo session | https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/automate/agent-sessions/9451709 | finished code_review/v1, historical 14 October |
| Duo pipeline | https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2946840620 | reviewed 4182deb55678382c0a99f7b1fd8e2232d17a0611 |
| Actual finding | https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/1#note_4012466889 | GitLabDuo advice, not a Codex-authored substitute |
| Correction | https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/commit/d05e8bb205a0411c5f7b5bc5c6fc68b0b367a7cf | Codex implementation following review |
| Merged baseline | https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/1 | merged into main, not open |
| Historical main CI | https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2953431698 | five automatic successes; overall manual, not full success |
| Original 96 tests | https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17220332232 | historical hosted baseline; Phase 4 expanded suite separate |
| Main review boundary | https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/jobs/17220332236 | remains manual, never play for filming |
| Intentional failure | https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2949021100 | retained MR !2; not changed in Phase 4 |
| Positive / negative reports | [examples](examples/) and original research snapshot artifacts | LOCAL_TESTED, real pytest/Bandit collection, not platform simulation |
| Historical evaluation | [Phase 4 results](02-experimental-results.md), [original JSON](evidence/research-results-phase4-historical.json) | original experiment; not final source qualification |
| Refreshed evaluation | [Phase 4.2 qualification](15-post-merge-qualification.md), [JSON](evidence/research-results.json) | measured local run bound by exact source and script digests |
| Phase 4.2 final CI | External `.artifacts/phase42-final-review.md` and ZIP `MANIFEST-SHA256.json` | use exact final MR/PR/main/pipeline/job identities from the delivered report |
| Phase 4 handoff | [historical handoff](14-final-handoff.md) | historical timeline only |

Before filming, reopen each required platform source using current browser access.
Historical audit proves the earlier read, not future browser availability. Download
hosted artifacts before their 14-day retention expires. Do not publish private raw
logs, browser storage or unredacted identity/credential areas.
