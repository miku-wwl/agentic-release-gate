"""Build an independent, read-only decision console using public recorded evidence."""
# HTML template literals retain long attribute lines; all Python logic is formatted by Ruff.
# ruff: noqa: E501

import argparse
import hashlib
import html
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
STATIC_ASSETS = ("console.css", "console.js", "mark.svg")
LAB = "https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase"
HUB = "https://github.com/miku-wwl/agentic-release-gate"
PAGES = {
    "index.html": ("Overview", "01"),
    "decision-explorer.html": ("Decision Explorer", "02"),
    "evidence-chain.html": ("Evidence Chain", "03"),
    "research.html": ("Research", "04"),
    "audit-trail.html": ("Audit Trail", "05"),
}
CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
    "font-src 'none'; connect-src 'none'; object-src 'none'; base-uri 'none'; "
    "form-action 'none'; frame-src 'none'"
)


def esc(value):
    return html.escape(str(value), quote=True)


def safe_url(value):
    if not isinstance(value, str) or any(c.isspace() for c in value):
        raise ValueError("Invalid reference URL")
    url = urlsplit(value)
    if url.scheme != "https" or url.username or url.password or url.port:
        raise ValueError("Only public HTTPS project references are supported")
    if not any(value == base or value.startswith(base + "/") for base in (LAB, HUB)):
        raise ValueError("Reference outside the reviewed projects")
    if any(c in value for c in ('"', "'", "<", ">", "\\")):
        raise ValueError("Invalid reference characters")
    return value


def link(url, label, cls="text-link"):
    return (
        f'<a class="{cls}" href="{esc(safe_url(url))}" target="_blank" '
        f'rel="noopener noreferrer">{esc(label)} <span aria-hidden="true">↗</span></a>'
    )


def load_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result

    def reject(_):
        raise ValueError("Non-finite JSON")

    if path.stat().st_size > 5 * 1024 * 1024:
        raise ValueError("Evidence exceeds build limit")
    result = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=unique, parse_constant=reject
    )
    if not isinstance(result, dict):
        raise ValueError("Expected JSON object")
    return result


def source_bytes(root, name):
    # Text inputs use canonical Git LF bytes, independent of Windows checkout settings.
    return (root / name).read_bytes().replace(b"\r\n", b"\n")


def validated_static_assets(root):
    directory = root / "frontend/assets"
    if directory.is_symlink():
        raise ValueError("Static asset directory must not be a symlink")
    if not directory.is_dir():
        raise ValueError("Static asset directory is missing")
    entries = tuple(directory.iterdir())
    for entry in entries:
        if entry.is_symlink():
            raise ValueError("Static asset must not be a symlink: " + entry.name)
        if entry.name not in STATIC_ASSETS:
            raise ValueError("Unknown static asset: " + entry.name)
        if not entry.is_file():
            raise ValueError("Static asset must be a regular file: " + entry.name)
    if {entry.name for entry in entries} != set(STATIC_ASSETS):
        raise ValueError("Required static asset is missing")
    return tuple("frontend/assets/" + name for name in STATIC_ASSETS)


def validate_data(checkpoint, positive, negative, research, required):
    identities = required["required_case_ids"]
    if len(identities) != 139 or len(set(identities)) != 139:
        raise ValueError("Original 139 mandatory identities must remain intact")
    for report, expected in ((positive, "ALLOW"), (negative, "DENY")):
        d, tests = report["decision"], report["tests"]
        if d["execution_authorized"] is not False or d["decision"] != expected:
            raise ValueError("Fixture cannot grant execution authority")
        if not re.fullmatch(r"[0-9a-f]{40}", d["commit_sha"]):
            raise ValueError("Invalid fixture identity")
        if set(tests["case_ids"]) != set(identities) or tests["passed"] != 139:
            raise ValueError("Fixture mandatory evidence mismatch")
        if any(type(tests[k]) is not int or tests[k] != 0 for k in ("failed", "errors", "skipped")):
            raise ValueError("Fixture test outcome mismatch")
    if positive["decision"]["next_gate"] != "HUMAN_APPROVAL":
        raise ValueError("Human gate missing")
    if "SECURITY_HIGH" not in negative["decision"]["reasons"] or not any(
        f["severity"] == "HIGH" for f in negative["security"]["findings"]
    ):
        raise ValueError("Genuine recorded HIGH fixture required")
    if (
        checkpoint["production_execution"] != "DISABLED"
        or checkpoint["human_gate_executed"] is not False
    ):
        raise ValueError("Closed execution boundary required")
    if checkpoint["pipeline_status"] != "manual" or checkpoint["automatic_jobs_passed"] != 6:
        raise ValueError("Reference pipeline must retain manual boundary")
    rows = research["results"]
    counts = Counter(row["scenario"] for row in rows)
    if len(rows) != 42 or len(counts) != 14 or set(counts.values()) != {3}:
        raise ValueError("Research sample mismatch")
    if any({r["trial"] for r in rows if r["scenario"] == s} != {1, 2, 3} for s in counts):
        raise ValueError("Duplicate/missing research trial")
    if not all(
        r["correct"] is True
        and r["expected"] == r["observed"]
        and r["decision"]["execution_authorized"] is False
        for r in rows
    ):
        raise ValueError("Research results cannot be relabelled")
    metrics = research["metrics"]
    expected = {
        "total_scenarios": 14,
        "trials_executed": 42,
        "correct_decisions": 42,
        "false_allow": 0,
        "false_deny": 0,
    }
    if any(type(metrics[k]) is not int or metrics[k] != value for k, value in expected.items()):
        raise ValueError("Research metrics mismatch")
    if research["evaluated_source_digest"] != checkpoint["evaluated_source_digest"]:
        raise ValueError("Qualified research source mismatch")
    for url in checkpoint["references"].values():
        safe_url(url)


def pill(text, tone="neutral"):
    return f'<span class="pill {tone}"><span class="status-dot" aria-hidden="true"></span>{esc(text)}</span>'


def metric(label, value, detail, tone=""):
    return (
        f'<article class="metric {tone}"><p class="label">{esc(label)}</p>'
        f'<p class="metric-value">{esc(value)}</p><p class="muted">{esc(detail)}</p></article>'
    )


def heading(kicker, title, description):
    return (
        f'<header class="page-heading"><p class="eyebrow">{esc(kicker)}</p>'
        f'<h1>{esc(title)}</h1><p class="lead">{esc(description)}</p></header>'
    )


def chain():
    steps = [
        ("01", "Commit", "Exact candidate SHA", "Bound", "neutral"),
        ("02", "Tests", "139 mandatory identities", "Verified", "allow"),
        ("03", "Security", "Raw scanner evidence", "Verified", "allow"),
        ("04", "Policy", "Deterministic eligibility", "ALLOW", "allow"),
        ("05", "Human approval", "Independent authority", "Required", "pending"),
    ]
    return (
        '<ol class="chain">'
        + "".join(
            f'<li class="chain-step {tone}"><span class="step-number">{n}</span>'
            f"<h3>{label}</h3><p>{detail}</p>{pill(status, tone)}</li>"
            for n, label, detail, status, tone in steps
        )
        + "</ol>"
    )


def overview(cp):
    return (
        heading(
            "RELEASE READINESS / REFERENCE CHECKPOINT",
            "One candidate. An auditable decision.",
            "Trace the evidence, understand the decision, and keep release authority with people.",
        )
        + f"""
    <div class="hero-grid">
      <section class="panel decision-hero"><div class="panel-top"><span class="label">POLICY OUTCOME</span>{pill("Eligibility only", "allow")}</div>
        <div class="decision-word allow-text">ALLOW<span class="decision-symbol" aria-hidden="true">↗</span></div>
        <p class="hero-summary">Evidence qualifies this candidate<br>for human review.</p>
        <div class="gate-callout"><span class="gate-icon" aria-hidden="true">◇</span><div><strong>Human approval required</strong><p>Next gate: <code>HUMAN_APPROVAL</code></p></div><span class="gate-arrow" aria-hidden="true">→</span></div>
        <div class="code-line"><span>execution_authorized</span><strong>false</strong></div>
      </section>
      <section class="panel candidate-panel"><div class="panel-top"><h2>Qualified candidate</h2>{pill("Recorded CI checkpoint")}</div>
        <p class="label spaced">COMMIT IDENTITY</p><code class="commit">{esc(cp["gitlab_main_sha"])}</code>
        <dl class="facts"><div><dt>Target / gate</dt><dd>staging / eligibility</dd></div><div><dt>Policy</dt><dd>releasegate-policy-v2</dd></div><div><dt>Automatic CI</dt><dd class="allow-text">6 jobs passed</dd></div><div><dt>Pipeline overall</dt><dd class="pending-text">Manual · human gate unexecuted</dd></div></dl>
        {link(cp["references"]["pipeline"], "Inspect source pipeline")}
        <p class="source-note">Recorded checkpoint, not a live feed. This Console grants no approval or execution authority.</p>
      </section>
    </div>
    <div class="metrics-grid">{metric("REQUIRED TESTS", "139 / 139", "0 failed · 0 errors · 0 skipped", "allow")}{metric("HIGH / CRITICAL", "0", "2 existing LOW findings retained", "allow")}{metric("EVIDENCE", "Source-bound", "Commit, context and raw SHA256 checked")}{metric("PRODUCTION", "Disabled", "No release executor configured", "pending")}</div>
    <section class="panel"><div class="section-heading"><div><p class="eyebrow">THE TRUST BOUNDARY</p><h2>Evidence moves forward. Authority stays separate.</h2></div><a class="text-link" href="evidence-chain.html">Explore chain <span aria-hidden="true">→</span></a></div>{chain()}</section>
    <div class="bottom-grid"><a class="feature-link panel" href="decision-explorer.html"><span class="small-symbol" aria-hidden="true">⇄</span><div><h2>See both sides of the decision</h2><p>Inspect recorded ALLOW and SECURITY_HIGH demo fixtures.</p></div><span aria-hidden="true">→</span></a><aside class="panel quiet-panel"><span class="label">AI ADVISES. POLICY DECIDES.</span><p>Historical Duo advice is reference-only. It cannot waive failures or authenticate human approval.</p><a class="text-link" href="audit-trail.html">View original sources →</a></aside></div>"""
    )


def case_panel(report, name):
    d, tests, security = report["decision"], report["tests"], report["security"]
    positive = name == "positive"
    tone = "allow" if positive else "deny"
    title = "Complete evidence" if positive else "High-severity security finding"
    reason = "".join(f"<li><code>{esc(r)}</code></li>" for r in d["reasons"])
    findings = "".join(
        f'<tr><td><span class="severity {"deny" if f["severity"] == "HIGH" else "pending"}">{esc(f["severity"])}</span></td><td><code>{esc(f["id"])}</code></td><td class="file-cell"><code>{esc(f["file"])}</code><span>line {esc(f["line"])}</span></td></tr>'
        for f in security["findings"]
    )
    return f'''<section class="case-panel" id="{name}" data-case-panel="{name}" aria-labelledby="{name}-heading">
      <div class="fixture-banner"><strong>DEMO FIXTURE</strong><span>Recorded local experiment · generated example · no production execution</span></div>
      <div class="hero-grid"><article class="panel case-verdict {tone}"><p class="label">OBSERVED DECISION</p><div class="decision-word {tone}-text">{esc(d["decision"])}</div><h2 id="{name}-heading">{esc(title)}</h2><ul class="reason-list">{reason}</ul><div class="code-line"><span>execution_authorized</span><strong>false</strong></div></article>
      <article class="panel"><h2>What the evidence says</h2><dl class="facts"><div><dt>Tests passed</dt><dd>{esc(tests["passed"])} / {esc(tests["total"])}</dd></div><div><dt>Mandatory identities</dt><dd>139 / 139</dd></div><div><dt>Next gate</dt><dd class="{tone}-text">{esc(d["next_gate"] or "None · resolve denial")}</dd></div><div><dt>Evidence source</dt><dd>LOCAL_TESTED</dd></div></dl><p class="source-note">Fixture candidate (historical, separate from the qualified CI checkpoint)</p><code class="commit">{esc(d["commit_sha"])}</code></article></div>
      <div class="detail-grid"><section class="panel"><h2>Scanner findings</h2><div class="table-wrap"><table><caption>Actual recorded Bandit findings</caption><thead><tr><th scope="col">Severity</th><th scope="col">Rule</th><th scope="col">Source</th></tr></thead><tbody>{findings}</tbody></table></div><p class="source-note">Bandit {esc(report["provenance"]["security"]["tool_version"])} · {esc(security["scanned_files"])} scanned files. Unsafe negative fixture is scanned only; never executed.</p></section><aside class="panel boundary-panel"><span class="boundary-mark" aria-hidden="true">◇</span><h2>{"Eligible is not authorized" if positive else "Fail closed, with a reason"}</h2><p>{esc(report["required_next_action"])}</p><p>AI advice cannot override this deterministic decision. Production execution stays disabled.</p><a class="text-link" href="evidence/{name}-report.json">Inspect recorded JSON →</a></aside></div>
    </section>'''


def explorer(pos, neg):
    return (
        heading(
            "DECISION EXPLORER",
            "Same policy. Different evidence.",
            "Compare two recorded examples. Neither fixture represents a live production release.",
        )
        + """
    <div class="case-navigation" aria-label="Demo case navigation">
      <a class="case-choice" href="#positive" data-case-link="positive"><span class="case-choice-icon allow-text" aria-hidden="true">✓</span><span><strong>Positive case</strong><small>Complete evidence · ALLOW</small></span><span class="pill allow">DEMO FIXTURE</span></a>
      <a class="case-choice" href="#negative" data-case-link="negative"><span class="case-choice-icon deny-text" aria-hidden="true">×</span><span><strong>Negative case</strong><small>SECURITY_HIGH · DENY</small></span><span class="pill deny">DEMO FIXTURE</span></a>
    </div><p class="sr-only" id="case-announcement" role="status" aria-live="polite"></p>"""
        + case_panel(pos, "positive")
        + case_panel(neg, "negative")
    )


def evidence_chain(cp):
    return (
        heading(
            "EVIDENCE CHAIN",
            "From a commit to a human decision.",
            "Automatic validation establishes eligibility. Human approval and execution authorization remain separate gates.",
        )
        + f"""
    <section class="panel chain-feature">{chain()}<div class="boundary-divider"><span>Automatic validation</span><span>Independent human authority</span></div></section>
    <div class="detail-grid"><section class="panel"><h2>Bindings that must agree</h2><dl class="binding-list"><div><dt>Candidate commit</dt><dd><code>{esc(cp["gitlab_main_sha"])}</code></dd></div><div><dt>Evaluated source digest</dt><dd><code>{esc(cp["evaluated_source_digest"])}</code></dd></div><div><dt>Required test identities</dt><dd>All 139 reviewed identities, zero unapproved skips</dd></div><div><dt>Raw artifacts</dt><dd>SHA256 checked before summaries are trusted</dd></div><div><dt>Execution context</dt><dd>Commit, project, pipeline and source must match</dd></div></dl></section>
    <aside class="panel boundary-panel"><span class="boundary-mark" aria-hidden="true">◇</span><p class="eyebrow">THE CHAIN STOPS HERE</p><h2>Human approval required</h2><p>The candidate-review CI job is manual and unexecuted. A passed automated check never supplies authenticated human consent.</p><div class="code-line"><span>execution_authorized</span><strong>false</strong></div><p>Production execution is disabled. The release command remains DENY / exit 3.</p>{link(cp["references"]["human_gate"], "Inspect manual gate")}</aside></div>
    <section class="panel"><h2>What breaks the chain?</h2><div class="rule-grid"><article><span class="deny-text">01 / IDENTITY</span><h3>Wrong commit or context</h3><p>Evidence for another candidate cannot qualify this one.</p></article><article><span class="deny-text">02 / COMPLETENESS</span><h3>Missing or skipped tests</h3><p>Extra passing tests cannot replace mandatory identities.</p></article><article><span class="deny-text">03 / INTEGRITY</span><h3>Corrupt or unsafe evidence</h3><p>Unusable raw reports and HIGH findings produce DENY.</p></article></div></section>"""
    )


def research_page(research):
    rows = research["results"]
    scenarios = list(dict.fromkeys(r["scenario"] for r in rows))
    labels = {
        "complete": "Complete evidence",
        "failed_test": "Failed required test",
        "skipped_test": "Skipped required test",
        "missing_identity": "Missing test identity",
        "missing_security": "Missing security evidence",
        "wrong_sha": "Wrong commit SHA",
        "context_mismatch": "Mismatched source context",
        "corrupt_raw": "Corrupt raw artifact",
        "high_security": "HIGH security finding",
        "missing_approval": "Missing production approval",
        "stale_approval_sha": "Stale approval SHA",
        "wrong_approval_target": "Wrong approval target",
        "wrong_approval_digest": "Wrong approval digest",
        "release_unavailable": "Unavailable release executor",
    }
    scenario_rows = "".join(
        f'<tr><td><span class="row-index">{i + 1:02}</span>{esc(labels.get(s, s))}</td><td><span class="pill {"allow" if s == "complete" else "deny"}">{esc(next(r["expected"] for r in rows if r["scenario"] == s))}</span></td><td>{"POLICY_ONLY" if next(r["mode"] for r in rows if r["scenario"] == s) == "POLICY_ONLY" else "Real CLI + evidence"}</td><td><span class="result-track" aria-hidden="true"><i></i></span><strong>3 / 3</strong></td></tr>'
        for i, s in enumerate(scenarios)
    )
    return (
        heading(
            "RESEARCH / CONTROLLED EVALUATION",
            "Measured decisions. Bounded claims.",
            "14 specified scenarios, repeated three times. Reproducibility within this sample is not universal reliability.",
        )
        + f"""
    <div class="research-metrics">{metric("SCENARIOS", "14", "Purposively selected conditions")}{metric("TRIALS", "42", "3 repetitions per scenario")}{metric("EXPECTED DECISIONS", "42 / 42", "Observed decisions matched", "allow")}{metric("FALSE ALLOW", "0", "Within this controlled sample", "allow")}{metric("FALSE DENY", "0", "Within this controlled sample", "allow")}</div>
    <aside class="research-limit"><span aria-hidden="true">ⓘ</span><p><strong>A controlled evaluation, not a production guarantee.</strong> Repeated trials are correlated. Three approval cases use synthetic POLICY_ONLY facts; they do not authenticate a human. No statistical significance or 100% production reliability is claimed.</p></aside>
    <section class="panel"><div class="section-heading"><div><p class="eyebrow">RECORDED OUTCOMES</p><h2>Every scenario, with its boundary intact.</h2></div><span class="pill neutral">Controlled evaluation</span></div><div class="table-wrap"><table class="scenario-table"><caption>Expected outcomes across three actual recorded trials per scenario</caption><thead><tr><th scope="col">Scenario</th><th scope="col">Expected</th><th scope="col">Method</th><th scope="col">Correct trials</th></tr></thead><tbody>{scenario_rows}</tbody></table></div></section>
    <section class="panel provenance-panel"><h2>Trace the measurement</h2><dl class="binding-list"><div><dt>Evaluated commit</dt><dd><code>{esc(research["evaluated_commit_sha"])}</code></dd></div><div><dt>Source digest</dt><dd><code>{esc(research["evaluated_source_digest"])}</code></dd></div><div><dt>Script SHA256</dt><dd><code>{esc(research["script_sha256"])}</code></dd></div><div><dt>Environment</dt><dd>{esc(research["execution_environment"]["platform"])} · Python {esc(research["tools"]["python"])}</dd></div></dl><p class="source-note">Historical, source-bound research. Later Console edits are not relabelled as this measured commit. Raw hashes, commands, modes and limitations remain in the original data.</p><a class="text-link" href="evidence/research-results.json">Inspect all 42 recorded observations →</a></section>"""
    )


def audit_page(cp, advisory):
    cards = [
        (
            "CI / QUALIFIED CHECKPOINT",
            "Qualified CI checkpoint",
            "Six automatic jobs passed; overall manual. The human review job remains unexecuted.",
            "pipeline",
            "Pipeline #2983447020",
        ),
        (
            "HUMAN BOUNDARY",
            "Manual candidate review",
            "A review boundary, not production authorization. No approval or deployment control exists in this Console.",
            "human_gate",
            "View unexecuted job",
        ),
        (
            "HISTORICAL DUO ADVISORY",
            "An actual code-review finding",
            "Duo identified missing git in the slim CI image. This is historical evidence, not a live agent run.",
            "duo_finding",
            "Read original Duo finding",
        ),
        (
            "CORRECTION / CODEX",
            "Implementation has its own author",
            "Codex implemented the correction following Duo's recommendation. The review and the fix retain separate attribution.",
            "correction",
            "Inspect correction commit",
        ),
    ]
    body = "".join(
        f'<article class="panel audit-card"><p class="eyebrow">{k}</p><h2>{title}</h2><p>{desc}</p>{link(cp["references"][key], label)}</article>'
        for k, title, desc, key, label in cards
    )
    return (
        heading(
            "AUDIT TRAIL / ORIGINAL SOURCES",
            "Nothing here asks you to take our word for it.",
            "Open the original CI, recommendation and merge records. All links are read-only public references.",
        )
        + f"""
    <div class="audit-grid">{body}</div><section class="panel"><div class="section-heading"><div><p class="eyebrow">MERGE RECORDS</p><h2>Two repositories. Preserved histories.</h2></div>{pill("Recorded merge history")}</div><div class="merge-grid"><article><span class="source-logo">GL</span><div><h3>GitLab MR !4 · merged</h3><p>{esc(cp["gitlab_merged_at"])}</p><code class="commit">{esc(cp["gitlab_main_sha"])}</code>{link(cp["references"]["gitlab_mr"], "View GitLab merge")}</div></article><article><span class="source-logo">GH</span><div><h3>GitHub PR #2 · merged</h3><p>{esc(cp["github_merged_at"])}</p><code class="commit">{esc(cp["github_main_sha"])}</code>{link(cp["references"]["github_pr"], "View GitHub merge")}</div></article></div></section>
    <section class="panel advisory-record"><div><p class="eyebrow">HISTORICAL · OFFLINE REFERENCE ONLY</p><h2>Duo advises. It does not authorize.</h2><p>{esc(advisory["finding"])}</p><p>Reviewed SHA <code>{esc(advisory["reviewed_sha"])}</code></p><p>Session 9451709 · {esc(advisory["review_timestamp"])}</p></div><aside><p class="label">AUTONOMY SCOPE</p><strong>Assisted verified</strong><p>Supervised: NOT_VERIFIED<br>Custom Flow execution: NOT_VERIFIED<br>Production execution: DISABLED</p>{link(cp["references"]["duo_session"], "Open historical session")}</aside></section><p class="source-note">Static records cannot attest a live platform state. The build validates the supplied data and preserves its source hashes; it does not authenticate a current human or runner.</p>"""
    )


def shell(name, content):
    title = PAGES[name][0]
    nav = "".join(
        f'<a href="{file}" {'aria-current="page"' if file == name else ""}><span class="nav-number">{number}</span><span>{label}</span><span class="nav-arrow" aria-hidden="true">↗</span></a>'
        for file, (label, number) in PAGES.items()
    )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="dark"><meta name="description" content="ReleaseGate read-only DevSecOps Decision Console. Evidence, eligibility and human authority remain separate."><meta http-equiv="Content-Security-Policy" content="{esc(CSP)}"><meta name="referrer" content="no-referrer"><title>{esc(title)} · ReleaseGate</title><link rel="icon" href="assets/mark.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/console.css"><script src="assets/console.js" defer></script></head>
<body><a class="skip-link" href="#main-content">Skip to content</a><div class="app-shell"><aside class="sidebar" id="console-navigation"><a class="brand" href="index.html" aria-label="ReleaseGate overview"><img src="assets/mark.svg" alt="" width="36" height="36"><span>ReleaseGate<small>DECISION CONSOLE</small></span></a><p class="nav-label">WORKSPACE</p><nav aria-label="Primary navigation">{nav}</nav><div class="sidebar-bottom"><div class="readonly-mark"><span aria-hidden="true">◇</span><div><strong>Read-only by design</strong><p>No approval or execution controls</p></div></div><p class="sidebar-caption">GitLab Transcend 2026<br>Evidence-gated release decisions</p></div></aside><div class="workspace"><header class="topbar"><button class="menu-button" aria-expanded="false" aria-controls="console-navigation" aria-label="Toggle navigation">☰</button><p><span>Console</span><span class="crumb-separator">/</span>{esc(title)}</p><div class="topbar-status"><span class="pill neutral">REFERENCE SNAPSHOT</span><span class="topbar-boundary">Production disabled <span class="status-dot pending" aria-hidden="true"></span></span></div></header><main id="main-content" tabindex="-1">{content}</main><footer class="footer"><p><strong>ReleaseGate</strong> · Evidence → eligibility → human review</p><p>execution_authorized=false · No production executor</p></footer></div></div><noscript><p class="noscript-note">JavaScript is disabled. Both demo cases remain available; all page links and evidence are readable.</p></noscript></body></html>'''


def build(output, root=ROOT):
    output = output.resolve()
    if output.exists():
        raise ValueError("Use a new output directory; existing builds are preserved")
    asset_paths = validated_static_assets(root)
    names = {
        "positive": "docs/phase4/examples/complete/report.json",
        "negative": "docs/phase4/examples/high_security/report.json",
        "research": "docs/phase4/evidence/research-results.json",
        "required": "tests/required-tests.json",
        "advisory": "docs/phase4/duo-advisory.json",
        "checkpoint": "frontend/data/checkpoint.json",
    }
    data = {key: load_json(root / name) for key, name in names.items()}
    public_manifest = load_json(root / "docs/phase4/evidence/artifact-manifest.json")
    for key in ("positive", "negative", "research"):
        relative = names[key].removeprefix("docs/phase4/")
        if (
            hashlib.sha256(source_bytes(root, names[key])).hexdigest()
            != public_manifest["sha256"][relative]
        ):
            raise ValueError("Published evidence hash mismatch: " + key)
    validate_data(
        *(data[k] for k in ("checkpoint", "positive", "negative", "research", "required"))
    )
    contents = {
        "index.html": overview(data["checkpoint"]),
        "decision-explorer.html": explorer(data["positive"], data["negative"]),
        "evidence-chain.html": evidence_chain(data["checkpoint"]),
        "research.html": research_page(data["research"]),
        "audit-trail.html": audit_page(data["checkpoint"], data["advisory"]),
    }
    output.mkdir(parents=True)
    (output / "assets").mkdir()
    (output / "evidence").mkdir()
    for name, content in contents.items():
        (output / name).write_bytes(shell(name, content).encode("utf-8"))
    for name in asset_paths:
        (output / "assets" / Path(name).name).write_bytes(source_bytes(root, name))
    for key, filename in (
        ("positive", "positive-report.json"),
        ("negative", "negative-report.json"),
        ("research", "research-results.json"),
    ):
        (output / "evidence" / filename).write_bytes(source_bytes(root, names[key]))
    manifest = {
        "schema_version": 1,
        "product": "ReleaseGate read-only Decision Console",
        "data_scope": "Historical qualified checkpoint and explicitly labelled demo fixtures",
        "production_execution": "DISABLED",
        "execution_authorized": False,
        "inputs": {
            name: hashlib.sha256(source_bytes(root, name)).hexdigest()
            for name in (
                *names.values(),
                "docs/phase4/evidence/artifact-manifest.json",
                "frontend/build_console.py",
                *asset_paths,
            )
        },
        "files": {
            p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*"))
            if p.is_file()
        },
    }
    (output / "build-manifest.json").write_bytes(
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    )
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist/console")
    args = parser.parse_args()
    result = build(args.output_dir)
    print(
        json.dumps(
            {
                "status": "PASS",
                "output": str(args.output_dir),
                "files": len(result["files"]),
                "production_execution": "DISABLED",
            }
        )
    )
