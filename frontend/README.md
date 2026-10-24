# ReleaseGate Decision Console

A separate, read-only static product. Build-time Python renders five accessible
HTML pages; local CSS and a small JavaScript file provide navigation. No framework,
backend, credentials, external fonts, analytics, fetch requests or execution API.
The existing Policy/report generator remains unchanged.

```powershell
uv sync --locked --extra dev
uv run --no-sync python frontend/build_console.py --output-dir dist/console
uv run --no-sync python -m http.server 8767 --bind 127.0.0.1 --directory dist/console
```

Open `http://127.0.0.1:8767/`. This is a newly built application served only from
its output directory, not a proxy to old local HTML reports or arbitrary files.
Every build requires a new output directory and refuses to overwrite an existing
build. Outputs have relative links and work under a Pages project subpath.

The checked-in source fixtures are the existing public generated JSON reports.
Both Explorer cases visibly say **DEMO FIXTURE**. Overview/Audit use the explicitly
historical Phase 4.2 checkpoint; Research preserves its evaluated commit/digest.
The Console never treats historical data as a live feed or as authenticated consent.
Unknown/mismatched source hashes, unsafe execution claims, malformed JSON and
unreviewed URLs fail the build. It does not rerun or reimplement Policy.

```powershell
uv run --no-sync pytest -q tests frontend/tests
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
node --check frontend/assets/console.js
uv run --no-project --with tinycss2==1.4.0 python frontend/check_static.py
```

CSS parsing uses a pinned isolated QA tool, leaving application dependencies and
uv.lock unchanged. Node is used only for JavaScript syntax validation; no npm
installation is required to build or serve. The tinycss2 parser checks syntax,
not full property semantics; browser layout/interaction checks supplement it.

See [architecture and publication boundary](../docs/phase4.3/console-handoff.md)
and [QA evidence](../docs/phase4.3/qa-report.md) for the historical frontend checkpoint.

Pages configuration is included but omitted from pipelines unless protected default
main matches `RELEASEGATE_PAGES_APPROVED_SHA` exactly. A matching publication job is
manual and waits for all eight applicable automatic checks without downloading their
artifacts. It rebuilds only `dist/console` from committed source. The validation job
prints the non-secret GitLab-provided `CI_PAGES_URL` for publication review.

Before setting the SHA fence or starting a publication pipeline, obtain explicit
user authorization for the exact main SHA, complete generated file manifest and
intended audience. Reconfirm if source or payload changes. Never infer publication
consent from a code merge or silently change Pages visibility. This operational
fence grants no Human Approval or production execution authority. The archived
Phase 4.3 documents describe the earlier, unincluded-template state.
