# Phase 1.1 handoff — 2026-10-14

**Compatibility qualification: PASS. Runtime execution integration: NOT IMPLEMENTED.**
Use GitLab Duo/CI verification as the next competition milestone; integrate the
shared Runtime afterward for persistent approval, authorization, Action and receipt
execution. The existing eligibility pipeline does not need it yet.

## Independently verified v0.2.0

| Check | Actual result |
|---|---|
| Live annotated tag | `v0.2.0`, tag object `b193d38a4804725d44ca536a3bd9778679cc7b4c` |
| Peeled release commit | `7261fdd2f47d2b15fabe8faac527eeee37338eb1` |
| Pinned license and metadata | MIT, version 0.2.0, Python `>=3.13,<3.14` |
| Separate Git-pin installation | PASS, CPython 3.13.9, non-editable installed package |
| Installed source identity | `direct_url.json` commit and requested revision both equal the full pin |
| Installed imports | Public Runtime API imported with `python -I` from the private environment's `site-packages` |
| Package integrity | All 57 RECORD hashes passed; module/license text matches pinned source after LF/CRLF normalization |
| Pure budget helper | Default 5 preserves binding; 15 yields `.exec-15s`; 9 invalid inputs rejected |
| Runtime/approval/authorization/Action execution | NOT RUN; no runtime opened, no credentials or capability provisioned |

Read the pinned handoff, adapter guide and consumer example. The dependency template
inside the tag still references v0.1.0; the corrected guide is at the independently
confirmed documentation commit `65767556f6de78e3fb7c2e6141a3769d20c76a99`. This
does not change the Runtime dependency pin. Details, actual signatures, immutable
reference links and installation commands are in [feasibility](runtime-feasibility.md).

Verified metadata/imports establish compatibility, not consumer acceptance. Documented
scope remains one trusted single-step `SIDE_EFFECT` tool, strict Plan identity, exact
human approval, separate authorization, durable claim and receipt, CAS/idempotent
commands and terminal Unknown/no blind retry. It does not supply a generic multi-tool
engine, production human authentication or universal remote exactly-once effects.

The documented default adapter budget is five seconds, with trusted opt-in up to
fifteen. Extended profiles need reviewed fresh binding/scope/ledger and fresh approval
and authorization; old Actions cannot gain authority. A caller deadline only shortens
the configured budget. The bundled HTTP parent deadline is ten seconds, so a full
fifteen-second allowance requires a suitable consumer request envelope. These lifecycle
properties were inspected, not re-executed in this compatibility-only phase.

## Python findings and dependency decision

- ReleaseGate already permits `>=3.12,<3.14`; no application requirement was changed.
- An actual pinned Runtime install under 3.12.13 failed with exit 1 because it requires
  `>=3.13,<3.14`; the fresh 3.12 probe environment remained empty. No bypass was used.
- The normal ReleaseGate environment and CI remain Python 3.12.13 with the original
  dependencies and `uv.lock`. The Runtime is not added to that environment or pipeline.
- The built ReleaseGate wheel and all existing tests also worked under 3.13.9 in
  the separate environment alongside Runtime 0.2.0. This supports a future explicit
  3.13 adoption, but is not hosted Linux CI evidence or an execution adapter.
- When execution becomes a real requirement, explicitly choose the 3.13 composition,
  add the immutable dependency, review the application lock and retain MIT notices.

## Updated files

| File | Change |
|---|---|
| `AGENTS.md` | Record independent v0.2.0 verification, immutable references and ReleaseGate-specific milestone/safety boundaries |
| `docs/runtime-feasibility.md` | Replace the obsolete license/install blocker with actual installation/API/Python evidence |
| `docs/architecture.md` | Assign Duo/CI/policy responsibilities and defer execution Runtime until after platform verification |
| `docs/implementation-plan.md` | Split real GitLab verification from future persistent release execution |
| `README.md`, `docs/hackathon-requirements.md` | Correct current compatibility status and link this handoff |
| `src/releasegate/cli.py` | One informational field: `runtime=NOT_INTEGRATED` instead of the outdated license/install label |
| `docs/phase1.1-handoff.md` | This evidence-backed handoff |

The release command still returns DENY, `EXECUTION_NOT_CONFIGURED`,
`execution_authorized=false` and exit 3. No executor, gate bypass, new approval path,
runtime import or database was added. Policy, evidence collector, tests, demo script,
CI, project metadata, lockfile and the historical Phase 1 handoff were preserved.

## Complete existing local validation

| Actual command / validation | Result |
|---|---|
| `uv sync --frozen --extra dev` | PASS; 15-package 3.12 environment |
| `uv lock --check --offline` | PASS; lock unchanged |
| `uv run --no-sync ruff check .` | `All checks passed!` |
| `uv run --no-sync ruff format --check .` | `11 files already formatted` |
| 3.12 `pytest -q --junitxml=.../pytest-py312.xml` | **84 passed in 0.59s**, no failures |
| Installed 3.13 `python -I -m pytest -q tests --junitxml=.../pytest-py313.xml` | **84 passed in 0.74s**, no failures |
| `scripts/demo.py` using actual local pytest/Bandit | PASS: ALLOW / scanner-backed DENY; each snapshot also passed 84 tests |
| `uv build` | PASS; source archive and wheel |
| Fresh 3.12 wheel installation/import | PASS; release command stayed DENY/exit 3 |
| 3.13 wheel installation/import beside Runtime | PASS; both packages imported from `site-packages`; release stayed DENY/exit 3 |
| `uv pip check` | PASS in normal 3.12, Runtime-only 3.13, combined 3.13 and fresh wheel 3.12 environments |
| Final scope, whitespace, local Markdown links and bounded secret-pattern checks | PASS; no secret-pattern matches; protected Phase 1 files and index unchanged |

The actual demo scans retain the two original LOW B404/B603 findings in five product
files. Bandit's own exit is 1; the collector's LOW-only policy exit is 0. The isolated
DENY snapshot adds one scanned-only fixture: Bandit reports B602 HIGH and the policy
returns `SECURITY_HIGH`/exit 1. No unsafe fixture code executes. Final production
assessment without verified approval still denies with `PRODUCTION_APPROVAL_REQUIRED`.
Every decision remains `execution_authorized=false`.

Evidence directory: `.artifacts/phase1.1-20261014/` (ignored by Git), including
installation logs, `runtime-api.json`, the API probe, test stdout/JUnit, build output,
and `demo/4eae6fe5-3081-4dc4-804c-f122ff81e6c4/verification.json` with the actual raw
artifacts and command stdout/stderr/exits. `scope-verification.json` records the
final file/link/secret checks and unchanged, clean shared core checkout. Demo SHA references unchanged HEAD
`be6c49f1518c16b0de6e607fa67db1e228220c31` plus the uncommitted source digest;
these are local results, not committed GitLab pipelines.

## Remaining work and order

1. **GitLab Duo first:** obtain the provisioned project URL and verify access/runner/
   credits; perform server CI Lint and actual pipelines, enable the prepared Catalog
   flow and supported trigger, and preserve a genuine AI session and ALLOW/DENY
   pipeline evidence. Duo is NOT VERIFIED; GitLab CI is NOT RUN in this phase.
2. **Runtime afterward:** implement trusted human identity, exact approval binding,
   separate authorization, one concrete release executor and verified durable receipts.
   Add consumer acceptance tests for mismatched identities, stale approval, missing
   authorization, duplicate/conflicting/concurrent effects, restart and ambiguity.
3. Production deployment and real external effects remain NOT RUN. The old v0.1.0
   licensing blocker is resolved for the new v0.2.0 pin; the 3.12 incompatibility is
   explicit and isolated, while the substantive execution integration is still pending.

No shared Runtime checkout changes, staging, commit, push or deployment were made.
