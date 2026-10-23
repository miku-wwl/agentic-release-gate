# Duo advisory evidence integration

Implemented: `releasegate.advisory`, consumed only by the report presentation layer.
The [curated historical input](duo-advisory.json) records project/MR, session,
reviewed SHA, paraphrased finding/recommendation, original timestamp, subsequent
correction actor/reference, verification status and limitations.

The existing authenticated REST note/pipeline and GraphQL session reads were used
for the baseline audit; runtime report generation is offline and makes no network
calls. No supported assumption about arbitrary session-message retrieval is needed.
Input status is HISTORICAL_EVIDENCE or NOT_VERIFIED. Ingestion always identifies
itself as OFFLINE_REFERENCE_ONLY; accepting JSON never authenticates a session.

The historical session is bound to reviewed SHA
`4182deb55678382c0a99f7b1fd8e2232d17a0611`, timestamp, finding reference and Codex
correction `d05e8bb205a0411c5f7b5bc5c6fc68b0b367a7cf`. A contradictory identity is
rejected. This catalog is trusted application code requiring review to extend.
Finding prose is untrusted and escaped even for a known session. New unverified
session references may be represented as NOT_VERIFIED, never promoted by JSON.

No advisory fields are passed to Policy v2. Unknown fields (including approval,
verified_human and execution_authorized), malformed JSON, duplicate keys, nonfinite
numbers, oversized inputs, credential-like text and inconsistent URLs are rejected.
Only GitLab HTTPS project/session/note/commit reference shapes are accepted; the
loader never follows URLs or executes embedded commands.

Tests prove that favorable or forged advice cannot waive failed tests or HIGH
findings, missing advice remains NOT_VERIFIED, textual approval does not satisfy
production approval and historical reviewed identity cannot silently become current.
No Flow was registered or invoked; no code was auto-committed or merged by advice.
