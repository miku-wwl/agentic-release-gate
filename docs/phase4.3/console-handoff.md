# Phase 4.3 Console architecture and handoff

The Decision Console is an independent static presentation product. Python's
standard library reads existing public JSON, validates its identity and boundaries,
escapes all dynamic HTML and emits five HTML pages plus local CSS/JS/SVG. No app
dependency or Runtime integration is added. Existing Policy, report generator,
production-disabled release command and the 139-identity mandatory manifest remain
unchanged. The frontend tests run separately from those mandatory application tests.

## Views and provenance

- Overview: immutable Phase 4.2 reference candidate bc5e410f, its actual six
  automatic successes and manual pipeline status, 139 required tests and no
  HIGH/CRITICAL findings. All values are a dated checkpoint, not live telemetry.
- Decision Explorer: the two existing generated local JSON examples at 81aadcf6.
  Both are DEMO FIXTURE; the negative contains the actual recorded B602 HIGH
  scanner finding in a scanned-only unsafe fixture. Neither authorizes production.
- Evidence Chain: commit → tests → security → eligibility → human approval, with
  a separate authority boundary and execution_authorized=false.
- Research: the original measured Phase 4.2 14×3 sample, all 42 expected decisions,
  zero false ALLOW/DENY, original commit/source/script identities and synthetic
  POLICY_ONLY disclosure. This is not 100% production reliability.
- Audit Trail: the real pipeline, unexecuted gate, original Duo note/session,
  Codex correction and GitLab/GitHub Phase 4.2 merge records. No live agent animation
  or custom-Flow execution claim is made.

The build verifies the original public artifact hashes and mandatory identities.
Its manifest covers every emitted file and all evidence/source inputs, excluding
the manifest itself. Research and demo source JSON are copied without changing
their measured values, using canonical Git LF bytes. CI YAML additions change the
current source digest; the reference research is deliberately not relabelled as
a measurement of this frontend branch. Fresh branch qualification is recorded
separately in the external Phase 4.3 report and hosted MR pipeline.

## Read-only security design

All external strings use HTML escaping. Link destinations must be HTTPS and inside
the exact reviewed GitLab/GitHub project prefixes; credentials, hostile schemes
and deceptive hosts are rejected. JSON rejects duplicate keys, non-finite numbers
and oversized inputs. The CSP permits only same-origin static script/style/images,
with connect-src and form-action set to none. No inline scripts, dynamic HTML
injection, storage, network client, forms, approval buttons or deployment controls.
Native fragment links remain usable without JavaScript. JavaScript enhances case
selection/history and the mobile menu only.

System fonts, an original SVG mark and restrained CSS replace external assets.
Layout uses emerald for ALLOW, rose for DENY and amber for required human approval;
text labels accompany colors. Skip link, landmarks, table captions, current-page
state, focus outlines, live case announcements and reduced-motion rules provide
basic accessibility. This is not a full assistive-technology certification.

## Pages: prepared, not deployed

`.gitlab/ci/console-validate.yml` is included for testing/building only. It uploads
no Console build artifacts or demo payloads. `.gitlab/pages.console.yml` is a
separate **unincluded** template, so pushing this feature branch cannot publish it.
The template uses the current nested `pages.publish` syntax described in the
[GitLab Pages documentation](https://docs.gitlab.com/user/project/pages/introduction/).
Pages publishing itself uploads site artifacts; none is authorized in this phase.

After explicit authorization for an exact reviewed source/build manifest, payload
and intended audience, a maintainer can review/enable that template through normal
MR controls. Its rule requires protected default main, a manual job and an
operation-specific RELEASEGATE_PAGES_APPROVED_SHA equal to CI_COMMIT_SHA. That
variable is only an operational fence, not proof of human identity or production
authorization. Do not change Pages visibility, domain or access-control settings
without separate permission. No deployed URL or HTTPS accessibility is claimed.

## Phase 5 continuation

Phase 5 recording is NOT_STARTED for this Console. After separately authorized
merge and Pages publication, obtain the actual returned HTTPS URL and let Work
independently decide whether it is accessible. Re-run visual QA there before
recording; local browser QA does not prove hosted access. The old file-protocol
rejection remains historical and is not bypassed by this new product.

Use the current IAB Browser Video Skill, genuine browser actions, real event logs
and trace-grounded cursor/click rendering with source review and strict calibration.
Show DEMO FIXTURE labels, ALLOW → human review, SECURITY_HIGH DENY, bounded research,
historical Duo/Codex attribution, and the untouched human gate. Target 155–170
seconds with English narration materials and 1080p/30fps export. Actual source
resolution/fps, encoding and visual acceptance must be measured then. No video,
voiceover, upload, YouTube publication or Devpost submission is performed here.
