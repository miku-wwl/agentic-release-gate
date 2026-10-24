# Phase 4.3 frontend visual QA checkpoint

The actual new static Console was opened in the current IAB through its local
HTTP preview on 127.0.0.1, bound to the generated output directory only. It is
an independent application; no old file HTML was proxied or injected. No public
hosting, payload upload or Pages visibility change occurred.

## Browser observations

The final build received 18 observed view checks: Overview, both Explorer cases,
Evidence Chain, Research and Audit Trail at actual CSS viewports **1920×1080**,
**390×843**, and **320×800**. DOM widths fit their viewport in every final check.
An initial 320px topbar overflow was found and corrected before acceptance.
The wide research table scrolls inside its own container on mobile.

Genuine link clicks selected DENY/SECURITY_HIGH and returned to positive via browser
Back. Only the selected case was visible, and both remained explicitly DEMO FIXTURE.
The mobile navigation button expanded/collapsed with correct aria-expanded state.
The browser exposed one stylesheet, no inline scripts, and no forms/iframes/objects.
Browser warning/error inspection returned no page errors. CSP and semantic checks
supplemented the screenshots. Screenshots of all final views were saved locally
under `dist/phase43/qa/accepted-*`; structured observations are retained externally
in `.artifacts/phase43/browser-final-qa.json` and the final review package.

Desktop Overview, negative Explorer, Evidence Chain, Research and Audit screenshots
were visually inspected. They show legible hierarchies, correct status colors,
source labels and human boundaries. Mobile 390px and corrected 320px examples
were inspected for text wrapping and decision labels. Long pages remain scrollable;
content below the fold is not removed. No screenshot is claimed as proof of hosted
execution or authenticated approval.

## Automated coverage and limits

Frontend tests exercise escaping, unsafe URL rejection, malformed JSON, tampered
metrics/authority, original mandatory-manifest identity, source hash binding,
reproducible builds, relative links, semantic landmarks, CSP/no inline event handlers,
both fixture outcomes, and inert deployment configuration. Node validates JS syntax;
tinycss2 parses CSS rules/declarations in a pinned isolated tool environment.
The original application suite, real Bandit scans, fresh branch research, CLI
boundaries and source integrity are qualified separately and recorded with actual
results in the external final report. No local test is presented as a hosted result.

Keyboard-only and screen-reader certification, forced-colors mode and every
browser engine were not tested. The no-JavaScript fallback is structurally checked;
a separate JS-disabled browser session was not available. Local browser QA does
not establish Pages HTTPS reachability. Formal Phase 5 recording remains pending.

Publication state and exact feature/main commit identities belong to the external
final report, avoiding self-referential commits. MR/PR merge and Pages deployment
require separate user authorization.
