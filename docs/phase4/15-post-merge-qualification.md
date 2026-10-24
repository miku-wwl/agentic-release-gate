# Phase 4.2 post-merge qualification

This record separates historical experiments from the refreshed source qualification.
Final merge identities and final main CI artifacts are recorded externally after
merging, in `.artifacts/phase42-final-review.md` and the delivery ZIP's
`review/PHASE42-FINAL-REPORT.md` and `MANIFEST-SHA256.json`. This avoids asking a
commit to contain its own future merge SHA. The final delivered report is the
authority for Phase 4.2 publication and hosted qualification.

## A. Historical Phase 4 experiment

The original [experiment](02-experimental-results.md) and
[handoff](14-final-handoff.md) retain their timeline and measurements. Their local
host commit was `81aadcf643f3375046c79c4ff611096923cd93a0`; source digest was
`3124ed96b8a93d7e56c58164333fe7676e7e909466d4a9f8eec06be9c123df18`.
They do not qualify the final source. Original research and hosted JSON bytes are
preserved as `evidence/research-results-phase4-historical.json` and
`evidence/hosted-qualification-phase4-historical.json`, with published SHA256 hashes.

## B. Phase 4.1 merged checkpoint

- [GitLab MR !3](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/3): merged, main `a657d0e23cca01035ef50a9cc62ed1e6ae456da4`.
- [GitHub PR #1](https://github.com/miku-wwl/agentic-release-gate/pull/1): merged, main `470817fa1b118c30d7a1843301baaa68cc390044`.
- All 67 tracked files matched byte-for-byte. Independent repository histories were preserved.
- [Main pipeline 2983297230](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/pipelines/2983297230): six automatic jobs passed, 139 tests passed, overall **manual**, human candidate review unexecuted.

These identities were rechecked against the live APIs before Phase 4.2. No unknown
main changes were present. This checkpoint is retained in
[hosted-qualification.json](evidence/hosted-qualification.json), whose final-main
locator explains where to find the subsequent authoritative CI record.

## C. Phase 4.2 refreshed qualification

The clean local run evaluated commit `0d25df7495fb111102bf0a64fc92a55c3b555bfa`.
The [actual results](evidence/research-results.json) record its environment, versions,
commands, measured times, 48 raw artifact hashes and separate script hash.
[Independent verification](evidence/phase42-research-verification.json) checked
all raw hashes, snapshot source digests, scanned paths and mandatory identities.

The evaluated source digest is
`08b334201952e6ca624d2e9edffba42d899c535a111ede4f0e00c70ed5c15cd4`,
matching the exact Git blobs. Its 19-file scope comprises Python src/tests,
mandatory manifest, pyproject, CI YAML and lockfile. Script SHA256 is
`0f419fd83e767229863ddab099bf0b24a799e83b83881c34c72e38811ffca44d`.
Docs are outside this source digest and are covered by final per-file manifests.

Local results: **139 passed, 0 failed/errors/skipped**; all original 139 mandatory
identities retained. Ruff, locked sync, dependency checks, real Bandit, positive
CLI/report, negative production/release commands and provenance checks passed.
Bandit scanned 7 files: 2 existing LOW findings, 0 HIGH/CRITICAL, no suppressions.
Research: **14 scenarios × 3 trials = 42/42 correct**, false ALLOW **0**, false DENY
**0**. The measured latency distribution is in the JSON; no production performance
or statistical significance is claimed. Negative fixtures remain isolated, and
synthetic approval facts remain explicitly POLICY_ONLY.

Reproduce from a clean exact-byte checkout with Python 3.12:

```powershell
uv sync --locked --extra dev
uv run --no-sync pytest -q
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv run --no-sync python scripts/evaluate_scenarios.py --trials 3 --output-dir .artifacts/phase42-research
```

Use a new output directory on every rerun. `--extra dev` installs the locked test
and scanning tools. The local source was normalized to exact Git blob LF bytes to
avoid Windows newline conversion changing the digest. Policy and tests are unchanged.

## D. Final main CI and platform synchronization

Phase 4.2 uses a normal GitLab feature MR, then a normal GitHub-history-based mirror
PR. No direct main push, force push, protection change or approval bypass is used.
After each merge, final main is independently fetched. Every tracked project path,
size, file mode and exact-byte SHA256 is compared, including src/tests/scripts/docs,
README, AGENTS, dependencies, lockfile, CI and Duo configuration. Exceptions must be
explicit; equal counts alone are insufficient.

The final delivery report supplies exact MR/PR merge records, both main SHAs,
pipeline/job URLs, artifact archive hashes, raw checks and source digest comparison.
The final research artifact must identify that main SHA through CI_COMMIT_SHA and
the same source/script digest; it supersedes the local run for final hosted execution.
Six successful automatic jobs plus the unexecuted blocking human gate mean overall
**manual**, never overall success. Downloaded artifacts receive independent CRC,
raw hash, parsed summary, mandatory identity and scan scope checks. An unavailable
artifact must be marked NOT_INDEPENDENTLY_VERIFIED and cannot support a PASS.

## E. Phase 5 remains unrecorded

**PHASE5_VIDEO_STATUS=NOT_RECORDED.** Use ChatGPT Desktop Work and the latest
installed `codex-iab-video-recording` skill; see the
[recording handoff](12-video-capture-instructions.md). Target 155–170 seconds,
English narration, 1080p/30fps export, genuine browser actions and visible pointer
and click indicators grounded only in real events. Record source resolution/fps
separately. No recording, final video visual acceptance, publication or submission
is completed here.

Historical Duo Advisory remains session **9451709**, reviewed commit
`4182deb55678382c0a99f7b1fd8e2232d17a0611`, actual finding
[note 4012466889](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase/-/merge_requests/1#note_4012466889).
Duo recommended; Codex implemented the correction. It is not a new review of the
final source, autonomous execution or a verified custom Flow.

`AUTONOMY_STATUS=ASSISTED_VERIFIED`; `SUPERVISED_STATUS=NOT_VERIFIED`.
ALLOW leads to HUMAN_APPROVAL with `execution_authorized=false`. Unverified human
input cannot authorize production; advisory text cannot override policy. The release
command remains DENY / exit 3. **PRODUCTION_EXECUTION_STATUS=DISABLED**.
