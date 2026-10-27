"""Add the constrained public verification interface to the preserved static design."""
# ruff: noqa: E501

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ("public.css", "public.js")


def panel():
    return """<section class="panel live-console" aria-labelledby="live-heading">
<div class="section-heading"><div><p class="eyebrow">TRUSTED PACKAGED SOURCE / REAL SERVER EXECUTION</p><h2 id="live-heading">Fresh verification. Inspectable evidence.</h2></div><span id="live-status" class="pill neutral" role="status">CONNECTING</span></div>
<div class="live-scenarios" aria-label="Fixed verification scenarios"><button class="live-scenario" type="button" data-scenario="POSITIVE_CANDIDATE" aria-pressed="true"><strong>Positive Candidate</strong><span>Real mandatory tests + Bandit</span><small>Expected ALLOW if evidence qualifies</small></button><button class="live-scenario" type="button" data-scenario="SECURITY_HIGH" aria-pressed="false"><strong>Security High</strong><span>Real scan of a controlled unsafe fixture</span><small>Expected DENY · fixture is never executed</small></button></div>
<div class="live-actions"><button type="button" class="live-primary" id="run-verification" disabled>Run Live Verification</button><button type="button" class="live-secondary" id="view-cached" hidden>View latest completed result</button></div>
<p id="live-notice" class="source-note" role="status" aria-live="polite">Connecting to the verification service. No result is assumed.</p>
<p class="live-boundary"><strong>Production disabled</strong> · Human Gate unexecuted · <code>execution_authorized=false</code></p>
<div id="live-result" hidden><div class="live-result-top"><div><p class="label" id="result-origin">ACTUAL SERVER EXECUTION</p><p class="live-decision" id="live-decision">—</p><p id="live-reasons"></p></div><div class="live-gate"><span class="label">NEXT GATE</span><strong id="live-next-gate">—</strong><span>Production execution stays disabled.</span></div></div>
<div class="live-metrics"><article><span class="label">ACTUAL TESTS</span><strong id="live-tests">—</strong></article><article><span class="label">SECURITY HIGH / CRITICAL</span><strong id="live-security">—</strong></article><article><span class="label">DURATION</span><strong id="live-duration">—</strong></article></div>
<dl class="binding-list live-identities"><div><dt>Scenario</dt><dd id="live-scenario-id"></dd></div><div><dt>Candidate</dt><dd><code id="live-candidate"></code></dd></div><div><dt>Run ID</dt><dd><code id="live-run-id"></code></dd></div><div><dt>Started UTC</dt><dd id="live-time"></dd></div><div><dt>Evidence SHA256</dt><dd><code id="live-digest"></code></dd></div></dl>
<ol class="live-chain" id="live-chain" aria-label="Actual evidence chain"></ol>
<button type="button" class="text-link live-evidence-button" id="inspect-evidence" disabled>Inspect sanitized evidence and logs →</button><pre id="live-evidence" class="live-evidence" tabindex="0" hidden></pre></div>
<p class="source-note">Fixed DEMO scenarios run on the server. History and quota counters are ephemeral and may reset after scale-to-zero. No production execution authority. Historical GitLab CI and Duo records below remain historical.</p></section>"""


def history():
    return """<section class="panel live-history"><div class="section-heading"><div><p class="eyebrow">ACTUAL INSTANCE HISTORY</p><h2>Recent verification runs</h2></div><button type="button" class="text-link" id="refresh-history">Refresh</button></div><p class="source-note">Public sanitized demo evidence only. Up to 10 runs, retained for at most one hour in instance memory; restarts can remove this history.</p><div id="live-history" class="live-history-list" aria-live="polite">Loading actual history…</div></section>"""


def build(output, root=ROOT):
    spec = importlib.util.spec_from_file_location(
        "recorded_console", root / "frontend/build_console.py"
    )
    recorded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recorded)
    recorded.build(output, root)
    directory = root / "frontend/public"
    if directory.is_symlink() or {p.name for p in directory.iterdir()} != set(ASSETS):
        raise ValueError("Unknown public frontend asset")
    for name in ASSETS:
        path = directory / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("Public assets must be regular files")
        (output / "assets" / name).write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
    titles = {
        "index.html": "Run the checks. Review the decision.",
        "decision-explorer.html": "Same policy. Fresh evidence.",
        "evidence-chain.html": "Follow an actual verification run.",
        "audit-trail.html": "Every run leaves inspectable evidence.",
    }
    for name in recorded.PAGES:
        path = output / name
        page = path.read_text("utf-8")
        page = page.replace("connect-src &#x27;none&#x27;", "connect-src &#x27;self&#x27;")
        page = page.replace("Read-only by design", "Safe live verification")
        page = page.replace(
            "No approval or execution controls", "No production execution authority"
        )
        page = page.replace("REFERENCE SNAPSHOT", '<span id="public-mode">CONNECTING</span>')
        page = page.replace(
            "</head>",
            '<link rel="stylesheet" href="assets/public.css"><script src="assets/public.js" defer></script></head>',
        )
        page = page.replace(
            "ReleaseGate read-only DevSecOps Decision Console.",
            "ReleaseGate constrained public verification console.",
        )
        if name != "research.html":
            match = re.search(r'(<main id="main-content" tabindex="-1">)(.*?)(</main>)', page, re.S)
            old = re.sub(
                r'<header class="page-heading">.*?</header>', "", match[2], count=1, flags=re.S
            )
            heading = recorded.heading(
                "PUBLIC VERIFICATION / FIXED SCENARIOS",
                titles[name],
                "Execute trusted packaged checks, inspect the evidence, and preserve independent human authority.",
            )
            new = heading + panel() + (history() if name == "audit-trail.html" else "")
            new += (
                '<details class="recorded-reference"><summary>Historical reference evidence · recorded CI, fixtures and Duo reviews</summary>'
                + old
                + "</details>"
            )
            page = page[: match.start()] + match[1] + new + match[3] + page[match.end() :]
        path.write_bytes(page.encode())
    manifest = {
        "schema_version": 1,
        "product": "ReleaseGate public fixed-scenario verification console",
        "production_execution": "DISABLED",
        "execution_authorized": False,
        "files": {
            p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*"))
            if p.is_file() and p.name != "build-manifest.json"
        },
    }
    (output / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", "utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    build(args.output_dir)
