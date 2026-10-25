# Live Verification Console

Run real checks, inspect fresh evidence and review the calculated release decision
on your own machine. This is separate from the public static showcase and from
GitLab Duo Agent Platform sessions.

## Operator guide

Use a trusted, clean checkout of the reviewed source branch, Python 3.12, Git and
[uv](https://docs.astral.sh/uv/). From the repository root in PowerShell:

```powershell
uv sync --frozen --extra dev
uv run --no-sync python -m releasegate.live --port 8776
```

Open <http://127.0.0.1:8776/>. Use this exact numeric address; `localhost` is not an
accepted Host alias. The process binds only to IPv4 loopback. No cloud service,
Node installation or frontend build is needed to use the application.

1. **Run Fresh Verification** and **Run ALLOW Verification** perform the same
   real workflow against the current committed HEAD. An eligible source normally
   produces ALLOW, with Human Approval Required; the decision is never prefilled.
2. **Run Security Rejection** adds a controlled, scanner-only file inside a new
   snapshot. Real Bandit findings are submitted to the existing policy. Expect
   DENY with `SECURITY_HIGH`. The fixture is never an import or test target.
3. Watch actual backend stages, then inspect the decision, test counts, findings
   and evidence chain. Expand process details for PIDs, exit codes and durations.
4. Choose an artifact and press **Inspect evidence** to read actual logs, JUnit,
   Bandit JSON, evidence envelopes, source identity or generated reports.
5. **Cancel verification** cancels the active job and terminates its owned
   process tree. Closing the browser does not cancel a job. Press Ctrl+C in the
   server terminal to stop the service and cancel outstanding work.

There is one active job and at most 20 jobs per server session. Restart the server
for a new session; old artifacts remain on disk, but are not replayed as new results.
Uncommitted edits are excluded from verification. Commit reviewed changes locally
before expecting them to appear in a new source snapshot.

## Architecture and evidence

The standard-library HTTP server in `src/releasegate/live.py` accepts only two
fixed operations. Each creates `.artifacts/live-verification/<UUIDv4>/`:

```text
run.json                         real timestamps, stages, result and artifact hashes
source-manifest.json             committed file sizes/SHA256 and derived fixture identity
processes.json                   actual CLI and inner pytest/Bandit PIDs and exit codes
execution-guard.jsonl            interpreter activation and actual check-module entry
logs/{tests,security,policy,report}.{stdout,stderr}.txt
snapshot/evidence/tests.junit.xml
snapshot/evidence/security.bandit.json
snapshot/evidence/{tests,security,decision}.json
snapshot/evidence/review/report.{json,md,html}
```

The server resolves HEAD once per run, exports an isolated Git archive and verifies
every exported file against its committed Git blob. The negative scenario records
its single additional scan-only file separately. Existing historical documentation
in that source archive is never used as live evidence. Preexisting top-level run
evidence is rejected.

The existing CLI performs four real operations: `run-check tests`, `run-check
security`, `evaluate --target staging`, and `report --target staging`. Its existing
collectors create and validate raw artifacts, commit identity, source digest,
mandatory test identities and provenance. The existing policy and report generator
make the decision; this server does not reimplement policy. The verification suite
remains the original `tests/` collection. The broader developer suite additionally
tests the console in `frontend/tests/`, avoiding recursive inner verification.

The browser polls status; its timer schedules requests and never invents stages or
completion. Very short stages can occur between polls; the recorded event sequence
retains all actual transitions. A nonzero Bandit exit may represent findings rather
than an unusable scan. Raw exit codes, findings and the policy outcome are exposed
separately. Missing/unusable evidence fails closed through the existing policy;
service failures are shown as failed verification, not as a successful decision.

For independent freshness verification, compare two runs' distinct UUIDs, UTC
start/end times, JUnit timestamps/hashes, Bandit `generated_at`, separate process
records and execution-guard module entries. Rehash original artifacts and call
`load_evidence` / `evaluate` against each saved snapshot. Byte-identical policy
outcomes alone do not establish a fresh execution.

## Security and limitations

Exact Host and Origin validation, same-origin request metadata, a fixed custom
request header, bounded JSON and a strict operation allowlist protect job creation.
No CORS is enabled. CSP, no framing, no sniffing and no-store headers apply. There
is no arbitrary command, executable, working-directory or filesystem-read input.
Artifacts use fixed aliases and reject traversal, symlinks and junctions.

Children receive a reduced environment without inherited provider credentials,
user-site packages or automatically loaded pytest plugins. Argument arrays use no
shell. Each CLI process has a trusted 120-second timeout and a 2 MiB output limit;
cancellation and shutdown terminate only owned process trees. Source exports are
limited to 64 MiB; browser artifacts to 10 MiB. Session and single-job limits bound
normal use; old artifact cleanup is an explicit operator filesystem operation.

The scanner-only file has an interpreter audit guard that blocks its execution
before its code runs and records attempted violations. This is a defense against
accidental execution, **not an OS sandbox for malicious repository code**. Tests
and Git hooks/configuration belong to a trusted local checkout. Local users can
invoke the API themselves; this is not multi-user authentication. Do not proxy,
tunnel, publish or bind this service to a public interface.

Browser log/report views redact recognized credentials and local paths, and render
only as text. Original private artifacts retain their original bytes; their hashes
are distinct from sanitized-view hashes. Automated redaction is not a guarantee
against every possible secret format. Do not publish these private run directories.

Local provenance is `local-working-tree` for the isolated committed snapshot, never
an attestation of hosted GitLab CI. ALLOW means eligibility for the next gate.
Production execution stays DISABLED, Human Approval REQUIRED / UNEXECUTED, and
`execution_authorized=false`. There is no approval, release or deployment route.
The shared persistent Runtime is neither installed into this baseline nor invoked.

Historical Duo advice remains a separate collapsed reference. The historical
session UI is not anonymously accessible; its original finding is linked publicly.
A local Python run is not a new Duo session. Fresh Code Review Flow execution
requires a permitted MR, supported GitLab initiation and separate authorization
for remote writes and potentially billable GitLab Credits usage.

## Developer checks and independent browser QA

```powershell
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv run --no-sync pytest -q tests frontend/tests
```

For the optional normal-Chrome QA runner, install Node.js and Playwright 1.62.1 in a
private tooling directory (not a product dependency), with Chrome installed:

```powershell
npm install --prefix .artifacts/browser-tools --no-save --package-lock=false playwright@1.62.1
$env:RELEASEGATE_PLAYWRIGHT_MODULE = (Resolve-Path .artifacts/browser-tools/node_modules/playwright/index.mjs).Path
$env:RELEASEGATE_CHROME = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
node scripts/live_browser_qa.mjs
```

Start the service first. The runner uses a fresh, isolated headless Chrome context,
real HTTP requests and real button clicks; it never controls ChatGPT Desktop.
It performs seven complete jobs, a real concurrency rejection and a cancellation,
and saves raw API traces, assertions and exact desktop/mobile screenshots in
`.artifacts/live-browser-qa/`. It does not record video or contact GitLab/GitHub.
The three viewports are 1920×1080, 390×844 and 320×800. No mocked success responses
or altered evidence are used. Successful screenshots supplement functional,
geometry and raw-evidence checks; they are not the sole basis for acceptance.

## Future demonstration handoff

After source review, CI, permitted synchronization and visual acceptance, prepare
a fresh server session. Show the current source SHA, click ALLOW verification,
show real progress, actual test/security results and Human Approval Required.
Then run the controlled security rejection, show the real HIGH finding, DENY and
its original evidence hash. Present genuine Duo evidence separately, with its
actual age, session identity and contributor attribution. A future video can fit
under three minutes using measured execution times; never substitute animation
for backend execution. Recording and submission are separate phases and have
not started.
