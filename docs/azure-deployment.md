# ReleaseGate Azure static showcase

**State: prepared locally; not deployed.** The Azure resource group, Container Apps
environment, Container App, public image tag, digest and HTTPS URL are pending.
Do not treat this document as evidence of a live Azure deployment.

## Architecture and trust boundary

The container builds the existing `frontend/build_console.py` Decision Console and
serves its five static pages with an unprivileged NGINX process on port 8080. The
Docker context is an explicit allowlist; the runtime image receives only the
generated static site and NGINX configuration. It contains no `.git`, `.env`, local
`.artifacts`, private run logs, test runner, application API, or production executor.

The public mode is `READ_ONLY_SHOWCASE`. All evidence is historical or labelled
`DEMO FIXTURE`. The local Live Verification Console at `src/releasegate/live.py`
is not part of this image and remains loopback-only. Production execution remains
`DISABLED`; `execution_authorized=false`; Human Approval remains required and
unexecuted. The public site has no write, approval, deployment, test-run or process
execution route.

## Registry and source identity

The intended public image repository is
[`docker.io/minglai/releasegate-demo`](https://hub.docker.com/r/minglai/releasegate-demo).
The Docker Hub Personal plan lists public repositories at no charge; image pull
limits and fair-use rules still apply. The published image tag will be the exact
40-character source commit SHA and its registry digest will be recorded after push.
No `latest` tag is used for deployment.

The Python 3.12 builder and unprivileged NGINX runtime use pinned linux/amd64
manifest digests in `deploy/azure/Dockerfile`. The build checks the source evidence
hashes through the existing console builder before emitting the site.

## Azure target and cost

The requested deployment profile is:

| Setting | Value |
|---|---|
| Plan | Consumption |
| Region | `australiaeast` |
| CPU / memory | `0.5` vCPU / `1.0Gi` |
| Replicas | minimum `0`, maximum `1` |
| Ingress | external, port `8080`, managed HTTPS |
| Environment logs | `none` |

Azure Container Apps publishes a subscription-shared monthly Consumption grant
(180,000 vCPU-seconds, 360,000 GiB-seconds and 2 million requests). Usage beyond
the grant is billed at the subscription's applicable rate. The grant is not a
per-app spend cap; other workloads may consume it, and public traffic can increase
active usage. A `$5` budget alert is notification only, not a hard charge ceiling.
Actual cost remains unverified until Cost Management billing data is available.

The intended architecture has no always-on replica, dedicated profile, ACR, VM,
Log Analytics workspace, database, NAT Gateway, public IP, Front Door or separate
monitoring resource. Docker Hub Public is used instead of a paid Azure registry.

## Reproducible local build and test

From a clean checkout, install the locked development dependencies and run the
existing suite and frontend syntax checks:

```powershell
uv sync --frozen --extra dev
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv run --no-sync pytest -q tests frontend/tests
node --check frontend/assets/console.js
uv run --no-project --with tinycss2==1.4.0 python frontend/check_static.py
```

Build from the repository root. Set `SOURCE_SHA` to the committed source revision;
the build context excludes Git history and local/private evidence:

```powershell
$sourceSha = git rev-parse HEAD
docker build --platform linux/amd64 --file deploy/azure/Dockerfile `
  --build-arg SOURCE_SHA=$sourceSha `
  --tag docker.io/minglai/releasegate-demo:$sourceSha .
docker image inspect docker.io/minglai/releasegate-demo:$sourceSha `
  --format '{{.Config.User}} {{json .Config.Labels}}'
```

Run the image bound to loopback with a read-only root filesystem, no Linux
capabilities and no-new-privileges, then run the functional/security smoke checks:

```powershell
docker run --detach --name releasegate-smoke `
  --publish 127.0.0.1:8768:8080 --read-only --tmpfs /tmp:rw,noexec,nosuid,size=16m `
  --cap-drop ALL --security-opt no-new-privileges --pids-limit 64 `
  docker.io/minglai/releasegate-demo:$sourceSha
python deploy/azure/smoke_test.py http://127.0.0.1:8768
docker stop releasegate-smoke
docker rm releasegate-smoke
```

The smoke test checks all five pages, assets, evidence JSON, ALLOW/DENY fixtures,
security headers, the read-only mode marker, sensitive paths, unknown routes and
write/API methods. It tests responses rather than relying on screenshots.

## Azure CLI deployment

Before creating resources, confirm the active subscription, actual permissions,
the target resource names, the regional support and the current spending-limit and
free-grant conditions. Pin every CLI call to that verified subscription. Never use
`az containerapp up`; it may create registry or monitoring resources implicitly.

After publishing and anonymously pulling the exact SHA-tagged public image, create
only the dedicated resource group, Consumption environment (`--logs-destination
none`) and Container App using the target settings above. Set insecure ingress to
false so Azure's managed HTTPS endpoint redirects or rejects plain HTTP. Record the
actual HTTPS FQDN, source SHA, image digest, resource inventory and TLS/browser test
results here only after they are independently verified.

## Public verification and billing

Use `deploy/azure/smoke_test.py https://<verified-fqdn>` from outside the container.
Separately verify TLS, HTTP-to-HTTPS behavior, cold-start recovery, mobile layout,
response headers, 404 behavior, and that `/.env`, `/.git/config`, `/artifacts/`,
`/api/runs`, and cancellation paths neither expose data nor execute work.
Report `PUBLIC_SHOWCASE` independently from `LIVE_TEST_EXECUTION_ON_AZURE`, which
remains `NOT_IMPLEMENTED`.

In Azure Portal, inspect the subscription's Cost Management cost analysis and
budgets. A budget alert is a notification; it does not stop every charge. Report
actual cost only when the billable usage data has arrived. No automatic deletion is
scheduled.

## Manual retirement after the hackathon

The site is intended to remain available through **18 November 2026 NZDT**. After
that date, review the resource inventory and cost data, then manually delete only
the project-owned resource group if it contains no unrelated resources:

```powershell
$verifiedSubscriptionId = az account show --query id --output tsv
az group delete --name rg-releasegate-hackathon26 --subscription $verifiedSubscriptionId --yes
```

This command is documentation only; no resource cleanup is scheduled or performed.
