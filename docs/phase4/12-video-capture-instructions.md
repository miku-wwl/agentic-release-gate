# ChatGPT Work / IAB production handoff

Status: **PHASE5_VIDEO_STATUS=NOT_RECORDED**. Phase 4.2 supplies handoff materials only.
Use **ChatGPT Desktop Work + the latest installed IAB Browser Video Skill**.
Read `codex-iab-video-recording/SKILL.md` from the currently installed skill before
production; use its current API documentation and helpers, not stale browser IDs.

1. Confirm final engineering qualification in the handoff and reopen its exact
   commit/MR/pipeline. Record no final demo while qualification is unresolved.
2. Inventory current surfaces with the documented browser entry point. Select the
   user's right-side IAB and confirm actual browser/tab IDs. Use no native desktop
   capture, external browser, Selenium, synthetic platform pages or recreated session.
3. Do a genuine 5–8 second read-only preflight using actual page navigation and
   continuous viewport frames. Validate encoding, decoding and representative frames.
4. Capture the storyboard in 20–40 second takes, at most 45 seconds each. Await
   capture and genuine UI actions in the same call. Preserve frame hashes, viewport
   dimensions, monotonic times, interaction-events and capture manifests.
5. Use actual source links from the evidence index. Open/scroll only. Do not invoke
   Duo, push, merge, approve, retry a pipeline or trigger a manual job for footage.
   Stop sensitive capture if authentication is needed; never capture login secrets.
6. Show the generated static report as a real artifact. It must visibly identify
   local versus hosted evidence, historical reviewed SHA, reasons and false execution
   authorization. Negative snapshots are local test fixtures, not production attacks.
7. Preserve original frames. Redact account regions only after inspecting the
   actual image coordinates, leaving key status/SHA/provenance visible. Cursor
   overlays, if used, must derive solely from logged genuine actions and be labelled
   trace-grounded visualization. Never invent pointer trajectories or UI changes.
8. Render using the skill's timestamp-aware `render_iab.py`. Keep actual time gaps
   and aspect ratio. Record source dimensions/fps separately from export 1080p/30fps;
   upscaling does not establish native capture resolution. No copyrighted music.
9. Time actual English narration, then cut to **155–170 seconds** (planned 164).
   Clearly distinguish historical evidence, new artifact viewing and genuine CI.
   Do not imply these were one continuous autonomous run.
10. Verify final MP4 with FFprobe, full `ffmpeg -v error -xerror ... -f null -`
    decoding, key-frame/transition inspection and audible narration review. Record
    hashes, measured duration, capture gaps, export specs and outstanding limitations.

Deliver future MP4 and sanitized QA/verification JSON. Publishing, uploading or
submission is outside this coding phase. Keep the user's existing tabs and artifacts.
If browser/session access is unavailable, mark capture BLOCKED and retain this
handoff; do not generate substitute Agent Session footage.

Phase 5 must use the final pipeline and artifact identities from the Phase 4.2
external report/ZIP manifest, not the older Phase 4 handoff. Show genuine CI,
Historical Duo Advisory (session 9451709), positive ALLOW → HUMAN_APPROVAL,
negative DENY, the untouched manual Human Gate, and Production Execution Disabled.
Use visible pointer and click indicators only from genuine logged IAB inputs.
Inspect source-cursor calibration first; coordinate clicks/drag/scroll can support
trace-grounded visualization. Locator-only clicks do not establish final pointer
coordinates and must remain PARTIAL where required by the current skill. Never
interpolate invented pointer paths. Target 155–170 seconds, English narration,
1920×1080 export at 30fps; record actual source fps/resolution separately.

Recording, final MP4 visual review, publication and Devpost submission belong to
Phase 5. None is completed or authorized by this qualification phase.
