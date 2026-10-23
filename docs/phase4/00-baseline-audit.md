# Phase 4 baseline audit

Observed 24 October 2026, Pacific/Auckland (API capture 23 October 22:08 UTC).
Status: **PASS** for source/platform inspection; **PARTIAL** for platform enforcement.
Selected public API facts are retained in [baseline.json](evidence/baseline.json).

## Repository identities and synchronization

Initial worktree was clean on local/GitHub `main`, SHA
`f0d5f680dd78900f1dd8600534659d2066ea920d`. GitHub branch API independently returned
the same SHA. Configured remotes were preserved:

- origin: `git@github.com:miku-wwl/agentic-release-gate.git`
- gitlab: `https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase.git`

GitHub SSH port 22 timed out; the authenticated GitHub API worked. GitLab HTTPS fetch
and read-only API worked using the existing OS-keyring authentication; no credentials
were extracted. GitLab main is `81aadcf643f3375046c79c4ff611096923cd93a0`.
`git merge-base gitlab/main main` found no common ancestor. Source, dependency,
lock, CI and 96-test policy baseline match; differences are documentation.

The fresh `feat/releasegate-award-readiness` branch starts at GitLab main. Only the
reviewed Phase 2 handoff update and two Phase 2.5 historical reports were restored
from GitHub. GitLab's `docs/gitlab-initial-README.md` remains intact. Neither history
is replaced or force-pushed; GitHub main and other worktrees remain unchanged.

## Live platform checkpoints

| Item | Observation | Status |
|---|---|---|
| [MR !1](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/1) | Merged 16 October; head `63c11ca4d30f021f2808fccae2d480007d440f87`; merge SHA equals main above | PASS |
| [MR !2](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/2) | Open; `demo/duo-fix-ci` → `import/releasegate-phase2a`; SHA `e451c3b74b3bb978d5d644bb8f75203253dc9188`; preserved | PASS |
| [Main pipeline 2953431698](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2953431698) | Five automatic jobs success; candidate review manual and unexecuted; overall API status `manual`, not `success` | PASS |
| [Historical failed pipeline](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2949021100) | Failed at the retained MR !2 revision | PASS |
| [Duo session 9451709](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/automate/agent-sessions/9451709) | GraphQL: finished `code_review/v1`; only session returned, no next page | PASS |
| [Duo pipeline 2946840620](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2946840620) | `duo_workflow`, success, reviewed SHA `4182deb55678382c0a99f7b1fd8e2232d17a0611` | PASS |
| [Finding 4012466889](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/1#note_4012466889) | GitLabDuo authored advice about missing git in slim CI; correction attribution remains Codex | PASS |
| License/publication | Project API public; MIT LICENSE present on GitLab main | PASS |

## Baseline engineering and restrictions

Actual initial commands: `uv run --no-sync pytest -q` → **96 passed**, exit 0;
`uv lock --check` → exit 0; Python **3.12.13**. Inspected all entries in
`tests/required-tests.json`, Policy v2, raw pytest/Bandit parsers, source/context
and raw-digest validation, CLI and CI. The manifest remains additive: original
identities are retained, new Phase 4 tests become mandatory too.

No Runtime dependency exists in the 3.12 environment or application lock. The
existing ignored 3.13 environment was independently reprobed: installed **0.2.0**,
source pin `7261fdd2f47d2b15fabe8faac527eeee37338eb1`, 57 RECORD hashes, public
signatures and five-second default passed. Pinned consumer example, handoff and
adapter guide were reread using `git show`; no Runtime opened or source modified.
This milestone needs no executor/database and does not add this dependency.

The GitHub README's open-MR claim was stale; GitLab's README had a correct Assisted
label but old phase status. Phase 2.5's invocation restriction remains applicable:
the live main branch still allows Developer pushes/merges. No new isolation evidence
justifies a Fix Flow invocation. Custom Flow and Fix Flow execution remain
NOT_VERIFIED; native branch protection is not a demonstrated enforcement of every
application gate. Historical reports are preserved with their original dates.

Read-only reproduction: `git status --short --branch`, `git remote -v`,
`git fetch gitlab main`, `git diff --name-status gitlab/main main`,
`glab api projects/87602765/repository/branches/main`,
`glab api projects/87602765/merge_requests/1`, equivalent `/2`,
`glab api projects/87602765/pipelines/2953431698/jobs`.

The October 15 ZIP was not used as source authority. The removed previous video
is not reused or republished. New Phase 4 CI qualification is recorded separately. A later attempt to download the
historical test artifact did not complete; its job status and artifact metadata were
revalidated, but historical raw test bytes are not claimed as freshly downloaded.
