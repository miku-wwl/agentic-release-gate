# Human review report

```powershell
$sha = git rev-parse HEAD
uv run --no-sync python -m releasegate run-check tests --sha $sha
uv run --no-sync python -m releasegate run-check security --sha $sha
uv run --no-sync python -m releasegate report --sha $sha --target staging --advisory docs/phase4/duo-advisory.json --output-dir evidence/review
```

Outputs are `report.md`, `report.json` (schema v1, type
`releasegate-human-review-v1`) and a standalone `report.html` with no dependencies,
scripts or network resources. Exit 0 means eligibility ALLOW; 1 means report with
DENY; 2 means unusable report/advisory input. Output locations are chosen by the
trusted CLI operator. Inputs, including resolved symlink targets, must stay inside
the current workspace. Sizes are bounded by the existing evidence reader and the
64 KiB advisory limit. Common credential strings are rejected rather than printed.

The interface revalidates raw evidence and calls the existing evaluate function.
It never imports a saved decision as authority. The complete resulting Decision is
embedded unchanged in JSON; Markdown and HTML display its exact reasons, candidate,
target, next gate, test totals/completeness, findings, digests, context, pipeline
references and historical Duo attribution. Missing evidence remains visible.
No human-approval facts can be supplied by the report command.

Evidence labels: LOCAL_TESTED means current local check artifacts were revalidated,
not that the candidate is approved. HISTORICAL_EVIDENCE is a reviewed reference to
an earlier event. NOT_VERIFIED marks absent advice or hosted attestation. VERIFIED
is reserved in documentation for directly observed platform facts. BLOCKED denotes
an unavailable/safety-restricted action, and PLANNED denotes unexecuted work.
The generated report never upgrades file-supplied GitLab context to VERIFIED.

[Executed examples](examples/) include positive eligibility and real HIGH finding
DENY; original decisions remain alongside research raw artifacts. Rendering tests
cover hostile markup, historical attribution, wrong SHA, missing evidence, reasons,
schema, deterministic rendering and path confinement. Browser rendering is recorded
in the final handoff separately from unit tests.
