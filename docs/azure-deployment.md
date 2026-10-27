# ReleaseGate Azure static showcase

**State: deployed and publicly verified on 27 October 2026.** The public showcase
is running on Azure Container Apps. It is a static, read-only build from source
commit `9d4a7618809de126200230f5d6970022c8459c1d`; it does not contain the local
Live Verification Console or production executor.

| Deployment evidence | Verified value |
|---|---|
| Public URL | <https://releasegate-public-demo.yellowtree-4e6734d2.australiaeast.azurecontainerapps.io> |
| Source revision | `9d4a7618809de126200230f5d6970022c8459c1d` |
| Docker Hub image | `docker.io/minglai/releasegate-demo:9d4a7618809de126200230f5d6970022c8459c1d` |
| Docker Hub manifest digest | `sha256:994d6b794bae2a85fa0aab3ed830106516dc10f672f75ab7b6c7eb7dabc882fd` |
| Resource group | `rg-releasegate-hackathon26` (`australiaeast`) |
| Container Apps environment | `acae-releasegate-hackathon26` |
| Container App | `releasegate-public-demo` |
| Public HTTPS / anonymous read-only checks | PASS |
| Production execution | DISABLED |
| Human Approval Gate | Required and unexecuted |

The deployment branch is local-only. No GitHub or GitLab branches, pipelines,
merge requests, or pull requests were changed as part of Azure deployment.

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

The public image repository is
[`docker.io/minglai/releasegate-demo`](https://hub.docker.com/r/minglai/releasegate-demo).
The public image is tagged with the exact 40-character source commit SHA shown
above. Docker Hub returned the recorded digest, and the tag/digest were verified
through the unauthenticated registry API and an anonymous pull. No `latest` tag is
used for deployment. Docker Personal currently lists unlimited public repositories
with fair-use terms; image pull limits still apply.

The Python 3.12 builder and unprivileged NGINX runtime use pinned linux/amd64
manifest digests in `deploy/azure/Dockerfile`. The build checks the source evidence
hashes through the existing console builder before emitting the site.

## Azure target and cost

The deployed profile is:

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
active usage. The task's `$5` risk budget is not a hard charge ceiling. If a budget
alert is configured, it is notification-only; the CLI returned no subscription
budget for this deployment. Actual cost remains unverified until Cost Management
billing data is available.

The Azure resource group was inspected after deployment and contains exactly the
Container Apps environment and the Container App listed above. The environment
reports only the Consumption workload profile and has no configured log
destination or Log Analytics configuration. The app has no configured environment
variables, Azure secrets, managed identity, or registry credentials. No always-on
replica, dedicated profile, ACR, VM,
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

The deployment used the dedicated resource group, Consumption environment
(`--logs-destination none`) and Container App with the target settings above.
Insecure ingress is false. Azure's HTTPS endpoint returned HTTP 200 with TLS
verification enabled; plain HTTP returned a redirect to HTTPS. The live app
configuration reports external ingress, port 8080, 0.5 CPU, 1.0 GiB, minimum 0 and
maximum 1 replica.

## Public verification and billing

The smoke test was run anonymously against the deployed HTTPS URL and passed all
five pages, three assets, three evidence JSON resources, ALLOW/DENY fixtures,
read-only mode, security headers, and denial of sensitive paths, unknown routes,
and write/API methods. Browser automation passed all five pages at 1920×1080,
390×844 and 320×800, exercised ALLOW→DENY navigation and mobile navigation, and
reported no horizontal overflow or JavaScript page errors. Screenshots are in the
local ignored folder `.artifacts/azure/browser-qa/`.

Scale-to-zero and recovery were verified end to end: after Azure Monitor showed
zero requests across the idle interval, the management-plane replica list returned
an empty list. A subsequent TLS-verified HTTPS `GET /healthz` returned HTTP 200
with `ssl_verify_result=0` in 1.56 seconds, and Azure then reported a new ready
replica created at `2026-10-27T08:15:10Z`. This confirms the configured min-0 app
can wake on an anonymous request and serve after scale-to-zero. It is one observed
cold start, not a latency guarantee.
Report `PUBLIC_SHOWCASE` independently from `LIVE_TEST_EXECUTION_ON_AZURE`, which
remains `NOT_IMPLEMENTED`.

The current billing balance was queried before resource creation, but the Azure CLI
did not return actual `pretaxCost`/currency values for billable usage, and no cost
records were available to validate the deployment charge. **Actual deployment cost
verification is pending billing data.** No subscription budget was returned by the
CLI query. Consumption free grants are shared at subscription scope and are not a
hard spend limit; actual charges depend on total subscription usage and traffic.
No automatic deletion is scheduled.

## Manual retirement after the hackathon

The site is intended to remain available through **18 November 2026 NZDT**. After
that date, review the resource inventory and cost data, then manually delete only
the project-owned resource group if it contains no unrelated resources:

```powershell
$verifiedSubscriptionId = az account show --query id --output tsv
az group delete --name rg-releasegate-hackathon26 --subscription $verifiedSubscriptionId --yes
```

This command is documentation only; no resource cleanup is scheduled or performed.
