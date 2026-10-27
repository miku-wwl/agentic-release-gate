# Public Live Verification Console

## Threat model and implementation plan

Anonymous clients are untrusted. They may submit malformed JSON, commands, paths,
URLs, duplicate keys, large bodies, forged forwarding headers, concurrent work and
repeated requests. The application accepts exactly one field, `scenario`, whose
value is `POSITIVE_CANDIDATE` or `SECURITY_HIGH`. No user data becomes a command,
path, source file, target, approval or deployment input.

The dedicated public WSGI application is separate from `releasegate.live`, which
remains loopback-only. One Gunicorn process serves a fixed map of generated public
files and a small API. A single owned verification process group runs only trusted
packaged source. The server verifies a build-time SHA256 manifest, copies the
candidate to a private temporary directory, and executes the existing mandatory
pytest suite, Bandit collector, evidence validator and Policy v2. There is no
production executor, Runtime Action, LLM request, external source fetch or human
approval adapter. The Python 3.12 lock and original mandatory manifest remain.

Controls planned before publication: non-root process; no credentials or Docker
socket; reduced child environment; kernel network denial in the Linux worker;
scan-only fixture execution guard; 60-second total deadline; process-group kill;
bounded outputs, memory, requests and retained history; one active run; global
30-second start cooldown and 24 starts per UTC day per process; fixed static and
evidence routes; same-origin browser writes; no CORS; CSP and text-only rendering.
Global controls do not depend on IP or forwarded headers. Cached completed results
can be inspected without starting work. History and counters are ephemeral and
reset with an instance restart or scale-to-zero; they are not a monthly spend cap.

The unsafe fixture is packaged as non-executable text and copied only to the
scanner target. An interpreter audit hook blocks its execution. This service
accepts no untrusted code and is not advertised as a code sandbox. Seccomp reduces
network access; it is not a general malicious-code isolation guarantee.

Required acceptance before Azure change: complete regression, negative API tests,
genuine positive/negative runs inside the resource-limited Linux container, network
denial and process-tree timeout tests, real browser interaction at all three
viewports, and a tested recovery command using the unchanged static image digest.
The public LIVE badge is gated off until public production E2E has passed.

GitLab synchronization needs separate approval after the concrete diff is ready.
GitHub writes and Devpost submission are not part of this authorization.

## Implemented contract

`GET /healthz` is inexpensive readiness. `GET /api/demo/scenarios` returns the
fixed scenarios, source identity, limits, active run and actual ephemeral history.
`POST /api/demo/verifications` accepts only `{"scenario":"POSITIVE_CANDIDATE"}`
or `{"scenario":"SECURITY_HIGH"}` with a same-origin JSON request. Each accepted
POST creates a fresh UUIDv4 run; cached results are never substituted for fresh
work. `GET /api/demo/verifications/{run_id}` returns actual state, and the
`/evidence` suffix returns a bounded sanitized evidence record after completion.
Unknown, expired and pre-restart Run IDs return 404. No cancellation, approval,
release, upload, arbitrary path, source, command or deployment route is exposed.

The candidate is the packaged verification subset of the exact image source
commit, enumerated by size and SHA256 in `/app/source-manifest.json`. The server
checks it on startup and before each copy; the worker checks the derived copy
before execution. The negative copy adds exactly the reviewed scanner-only byte
fixture. Existing `tests/required-tests.json` is unchanged: all 139 identities
must pass with zero skips. Broader frontend/developer tests remain outside the
inner mandatory suite to avoid recursive public verification.

The only normal worker subprocess commands are the existing collector's explicit
arrays: Python `-m pytest tests -q --junitxml=...` and Python `-m bandit -r src
--ignore-nosec -f json -o ...`. There is no shell. After collection, the worker
calls the existing `load_evidence`, `load_required_tests` and `evaluate` functions.
Missing, corrupt or inconsistent raw evidence cannot qualify. Bandit finding
exits remain distinct from scanner failure. An unexpected scenario outcome is a
failed verification and cannot grant eligibility; the original observed Policy
decision is retained separately. An ordinary security DENY has no next approval
gate. ALLOW requires HUMAN_APPROVAL and still has no execution authorization.

Actual test/scanner module-entry events, versions, exits and elapsed times are
recorded. JUnit and Bandit bytes, envelopes and source/evidence hashes are retained
as sanitized views. Original hashes and sanitized-view hashes are distinct;
sanitized copies are not represented as original bytes. Hashes establish byte
integrity, not signed hosted-CI attestation. The outer origin is
`PUBLIC_CONTAINER_EXECUTION`; the existing Policy's filesystem context remains
`local-working-tree`, not `gitlab-ci`. Nothing claims a new CI pipeline or Duo run.
Original logs and temporary workspaces are deleted after a run. Only bounded
public sanitized records remain in instance memory.

## Enforced limits and failure behavior

| Control | Limit |
|---|---|
| Gunicorn | 1 worker, 4 threads, 16 connections, bounded HTTP headers |
| Request body | 128 bytes, exact JSON schema, no chunked body |
| API request rate | 120 requests per rolling 10 seconds, global per instance |
| Concurrent verification | 1; overlapping POST returns 409 |
| Start cooldown | 30 seconds; excess starts return 429 with Retry-After |
| Daily starts | 24 per UTC day per process; excess returns 429 |
| Total run wall time | 60 seconds, including copy and both checks |
| Worker CPU / address space | 55 CPU seconds / 600 MiB |
| Worker file size / open files / processes | 2 MiB / 64 / 32 |
| Worker core dumps | Disabled |
| Combined process output | 512 KiB; excess fails verification |
| Each public raw-artifact/log view | 64 KiB |
| Aggregate public evidence / HTTP response | 384 KiB / 1 MiB |
| Retained history | At most 10 runs, at most one hour |

The global limits do not use client IP, X-Forwarded-For or client-chosen identity.
API fetches, static requests and error routes share the request limiter; the cheap
health check is exempt. A fixed trusted origin restricts browser POSTs, while
scenario, concurrency and cost controls independently apply to every client.
Gunicorn's control socket is disabled. Responses have no CORS, use no-store,
nosniff, no framing, and a CSP with same-origin scripts and connections. Browser
results use text nodes, not HTML injection.

The Linux/amd64 worker fails closed unless no-new-privileges and its seccomp filter
are installed and a socket creation probe is rejected. The filter is inherited
by pytest, Bandit and their descendants. Network syscalls, io_uring, namespace
changes and selected escape mechanisms are denied. The API process can serve
HTTP; verification children cannot create sockets. The timeout watchdog kills
the owned POSIX process group. These controls apply to trusted packaged tests,
not uploaded or arbitrary untrusted code. Process failures, missing evidence,
malformed results, output overflow and timeouts yield FAILED/TIMED_OUT with DENY.

History and quotas are intentionally ephemeral. Restarts or scale-to-zero can
reset both. They are neither durable per-person abuse prevention nor a guaranteed
monthly spending cap. Cached completed runs remain explicitly labelled and can
be inspected without starting another expensive verification.

## Local reproduction and release checks

Use the locked Python 3.12 environment. The additional public extra is pinned
Gunicorn 26.2.0 on Linux; no framework, LLM key or shared Runtime execution adapter
is introduced.

```powershell
uv sync --frozen --extra dev
uv run --no-sync pytest -q tests frontend/tests
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
node --test frontend/tests/live_copy.test.cjs
node --check frontend/public/public.js
uv run --no-project --with tinycss2==1.4.0 python frontend/check_static.py frontend/assets/console.css frontend/public/public.css
```

Build `deploy/azure/Dockerfile.public` from an export of a clean committed tree,
passing that full SHA as `SOURCE_SHA`. The Dockerfile-specific ignore file admits
only the required public source, tests, locked metadata and historical display
inputs. It excludes Git history, private artifacts, credentials and environment
files. The original static Dockerfile and image digest remain available.

```powershell
$sourceSha = git rev-parse HEAD
docker build --platform linux/amd64 -f deploy/azure/Dockerfile.public --build-arg SOURCE_SHA=$sourceSha -t docker.io/minglai/releasegate-demo:$sourceSha .
docker run -d --name releasegate-public-local --cpus 0.5 --memory 1g --pids-limit 64 --read-only --tmpfs /tmp:rw,noexec,nosuid,size=128m --cap-drop ALL --security-opt no-new-privileges -e PUBLIC_ORIGIN=http://127.0.0.1:8778 -p 127.0.0.1:8778:8080 docker.io/minglai/releasegate-demo:$sourceSha
docker exec releasegate-public-local python -m pytest -q frontend/tests/test_public.py -p no:cacheprovider
python deploy/azure/public_smoke.py http://127.0.0.1:8778 --output .artifacts/public-live/container-evidence
$env:RELEASEGATE_BASE_URL = 'http://127.0.0.1:8778'
node scripts/public_browser_qa.mjs
```

Windows skips the two Linux-specific tests; both must pass in the actual Linux
image before publication. Browser QA uses genuine Chrome HTTP, real button clicks
and actual server results at 1920×1080, 390×844 and 320×800. Screenshots supplement
API, raw-evidence and DOM/geometry assertions. No success response is mocked.

## Azure change and rollback

Reuse the existing Consumption app/hostname, 0.5 CPU, 1 GiB, min 0/max 1 and no
logging destination. Set `PUBLIC_ORIGIN` to the verified HTTPS origin. Leave
`PUBLIC_LIVE_ACCEPTED=0` during deployment acceptance: the UI says VERIFICATION
PREVIEW. After genuine public E2E, set it to 1 and recheck the same image/revision
configuration. The visible LIVE label is an operator acceptance flag, not a
replacement for fresh run evidence.

The known-good static fallback is source
`9d4a7618809de126200230f5d6970022c8459c1d`, immutable image
`docker.io/minglai/releasegate-demo@sha256:994d6b794bae2a85fa0aab3ed830106516dc10f672f75ab7b6c7eb7dabc882fd`.
Keep this image and retained Azure revision. Single-revision deployment switches
traffic only after readiness; if acceptance fails, restore this digest using the
existing app and verify the static smoke test. No extra app/environment is needed.

```powershell
az containerapp update --name releasegate-public-demo --resource-group rg-releasegate-hackathon26 --image docker.io/minglai/releasegate-demo@sha256:994d6b794bae2a85fa0aab3ed830106516dc10f672f75ab7b6c7eb7dabc882fd
python deploy/azure/smoke_test.py https://releasegate-public-demo.yellowtree-4e6734d2.australiaeast.azurecontainerapps.io
```

Target incremental cost is USD 0 under unused subscription-shared Consumption
grants and modest traffic. Active checks and requests can consume those grants;
scale-to-zero, quotas and max-one replicas reduce use but do not guarantee zero
charges. No additional Azure service is required. Budget alerts are notifications,
not hard caps. Actual cost remains pending until billing data is available.

## Acceptance and submission state

Implementation and local checks are in progress. No public LIVE acceptance or
GitLab synchronization is claimed by this document until recorded separately.
GitLab remote writes require the user's approval of the completed diff. Preserve
existing CI, manual Human Gate, history, Duo evidence and MIT LICENSE. Do not
merge the independent GitHub and GitLab histories.
