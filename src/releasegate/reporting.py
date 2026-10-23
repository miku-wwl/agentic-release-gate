"""Present a revalidated Policy v2 decision without granting any authority."""

import html
import json
import re
from pathlib import Path

from releasegate.advisory import advisory_summary, confined, load_advisory, no_secrets
from releasegate.evidence import (
    RAW_FILES,
    EvidenceError,
    load_evidence,
    load_required_tests,
    write_json,
)
from releasegate.policy import Decision, evaluate

LIMITATIONS = [
    "Hashes establish local integrity, not runner attestation or artifact authenticity.",
    "CI context in a file is not independently verified hosted execution.",
    "Duo references are offline evidence; ingestion does not authenticate a GitLab session.",
    "No authenticated human approval adapter or release executor is configured.",
]


def build_report(
    *,
    root: Path,
    directory: Path,
    sha: str,
    target: str,
    gate: str = "eligibility",
    advisory_path: Path | None = None,
) -> dict:
    directory = confined(root, directory)
    for name in (*RAW_FILES.values(), "tests.json", "security.json"):
        confined(root, directory / name)
    advisory = load_advisory(advisory_path, root=root) if advisory_path else None
    checks, required = {}, frozenset()
    usable = False
    try:
        evidence = load_evidence(directory, root=root)
        required = load_required_tests(root)
        decision = evaluate(
            evidence, expected_commit=sha, target=target, gate=gate, required_test_ids=required
        )
        checks = evidence["checks"]
        usable = True
    except (EvidenceError, OSError, ValueError, TypeError, KeyError) as exc:
        reason = str(exc) if isinstance(exc, EvidenceError) else type(exc).__name__
        decision = Decision("DENY", ("EVIDENCE_UNUSABLE", reason), sha, target, gate, None, None)
    tests = checks.get("tests", {}).get("summary")
    security = checks.get("security", {}).get("summary")
    case_ids = set(tests["case_ids"]) if tests else set()
    contexts = {kind: check["context"] for kind, check in checks.items()}
    pipeline_refs = []
    for context in contexts.values():
        if context["origin"] == "gitlab-ci" and context["project_id"] == "87602765":
            ref = (
                "https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/"
                f"43343080/showcase/-/pipelines/{context['pipeline_id']}"
            )
            if ref not in pipeline_refs:
                pipeline_refs.append(ref)
    report = {
        "schema_version": 1,
        "report_type": "releasegate-human-review-v1",
        "decision": decision.to_dict(),
        "evidence_status": (
            "LOCAL_TESTED"
            if len(checks) == 2
            and usable
            and all(c["origin"] == "local-working-tree" for c in contexts.values())
            else "NOT_VERIFIED"
        ),
        "evidence_revalidated": usable,
        "tests": tests,
        "mandatory_tests": {
            "required": len(required),
            "present": len(required & case_ids),
            "missing": sorted(required - case_ids),
            "complete": bool(required) and required <= case_ids,
        },
        "security": security,
        "provenance": {
            kind: {
                key: check[key]
                for key in (
                    "commit_sha",
                    "context",
                    "tool",
                    "tool_version",
                    "exit_code",
                    "raw_file",
                    "raw_sha256",
                )
            }
            for kind, check in checks.items()
        },
        "pipeline_references": pipeline_refs,
        "hosted_verification": "NOT_VERIFIED",
        "duo": advisory_summary(advisory, candidate_sha=sha),
        "required_next_action": (
            "Obtain exact human review; execution still requires separate authorization."
            if decision.decision == "ALLOW"
            else "Resolve every denial reason and collect fresh evidence."
        ),
        "human_authorization_boundary": (
            "ALLOW is eligibility only. Final production approval is required. "
            "execution_authorized=false. release remains DENY / exit 3."
        ),
        "limitations": LIMITATIONS,
    }
    no_secrets(report)
    return report


def _md(value) -> str:
    value = html.escape(str(value), quote=True).replace("\n", " ").replace("\r", " ")
    return re.sub(r"([\\`*{}\[\]()|#!])", r"\\\1", value)


def render_markdown(report: dict) -> str:
    d = report["decision"]
    tests = report["tests"]
    mandatory = report["mandatory_tests"]
    lines = [
        "# ReleaseGate human review",
        "",
        f"**{d['decision']}** — {_md(report['evidence_status'])}",
        "",
        f"Candidate: `{_md(d['commit_sha'])}`  ",
        f"Target: {_md(d['target'])}; gate: {_md(d['gate'])}  ",
        f"Policy: {_md(d['policy_version'])}  ",
        f"Next gate: {_md(d['next_gate'])}  ",
        f"Evidence digest: {_md(d['evidence_digest'])}",
        "",
        "## Policy reasons",
        "",
        *[f"- {_md(r)}" for r in d["reasons"]],
        "",
        "## Tests and security",
        "",
        (
            f"Tests: {tests['passed']}/{tests['total']} passed; {tests['failed']} failed; "
            f"{tests['errors']} errors; {tests['skipped']} skipped."
            if tests
            else "Tests: NOT_VERIFIED."
        ),
        f"Mandatory identities: {mandatory['present']}/{mandatory['required']}; "
        f"complete={str(mandatory['complete']).lower()}.",
        f"Missing identities: {_md(', '.join(mandatory['missing']) or 'none')}",
        "Security: NOT_VERIFIED."
        if report["security"] is None
        else f"Security: {report['security']['scanned_files']} scanned files; "
        f"{len(report['security']['findings'])} findings.",
        "",
    ]
    for finding in (report["security"] or {}).get("findings", []):
        lines.append(f"- {_md(finding)}")
    lines += ["", "## Evidence provenance", ""]
    for kind, provenance in report["provenance"].items():
        lines += [f"- {_md(kind)}: {_md(json.dumps(provenance, sort_keys=True))}"]
    lines += [f"Hosted verification: {_md(report['hosted_verification'])}"]
    lines += [f"Pipeline reference: {_md(ref)}" for ref in report["pipeline_references"]]
    lines += ["", "## Duo advisory", "", f"Status: {_md(report['duo']['status'])}"]
    review = report["duo"]["review"]
    if review:
        lines += [
            f"Reviewed revision: `{review['reviewed_sha']}`; "
            f"matches candidate={str(report['duo']['reviewed_candidate']).lower()}.",
            f"Session: {_md(review['session_url'])}",
            f"Finding: {_md(review['finding'])}",
            f"Finding reference: {_md(review['finding_url'])}",
            f"Recommendation: {_md(review['recommendation'])}",
            f"Review timestamp: {_md(review['review_timestamp'])}",
            f"Correction actor: {_md(review['correction']['actor'])}; "
            f"reference: {_md(review['correction']['reference'])}",
            *[f"- {_md(item)}" for item in review["limitations"]],
        ]
    else:
        lines += ["No advisory supplied. No successful review is inferred."]
    lines += [
        "",
        "## Required next action",
        "",
        _md(report["required_next_action"]),
        "",
        _md(report["human_authorization_boundary"]),
        "",
        "## Limitations",
        "",
        *[f"- {_md(item)}" for item in report["limitations"]],
        "",
    ]
    return "\n".join(lines)


def render_html(report: dict) -> str:
    d = report["decision"]
    esc = html.escape
    tests = report["tests"]
    mandatory = report["mandatory_tests"]
    security = report["security"]
    test_count = f"{tests['passed']}/{tests['total']}" if tests else "NOT_VERIFIED"
    finding_count = str(len(security["findings"])) if security else "NOT_VERIFIED"
    cards = (
        f'<div class="card">Tests passed<strong>{test_count}</strong></div>'
        f'<div class="card">Mandatory identities<strong>{mandatory["present"]}/'
        f"{mandatory['required']}</strong></div>"
        f'<div class="card">Security findings<strong>{finding_count}</strong></div>'
    )
    reasons = "".join(f"<li><code>{esc(r)}</code></li>" for r in d["reasons"])
    review = report["duo"]["review"]
    advice = "<p>No advisory supplied. No successful review is inferred.</p>"
    if review:
        advice = (
            f"<p><strong>{esc(report['duo']['status'])}</strong> · OFFLINE_REFERENCE_ONLY</p>"
            f"<p>Reviewed SHA: <code>{review['reviewed_sha']}</code><br>"
            f"Matches candidate: {str(report['duo']['reviewed_candidate']).lower()}</p>"
            f"<p><b>Finding:</b> {esc(review['finding'])}</p>"
            f"<p><b>Recommendation:</b> {esc(review['recommendation'])}</p>"
            f"<p>Session: {esc(review['session_url'])}<br>"
            f"Finding: {esc(review['finding_url'])}<br>Time: {esc(review['review_timestamp'])}</p>"
            f"<p>Subsequent correction by <strong>{esc(review['correction']['actor'])}</strong>"
            f"<br>{esc(review['correction']['reference'])}</p>"
            + "".join(f"<p>{esc(item)}</p>" for item in review["limitations"])
        )
    provenance = "".join(
        f"<tr><td>{esc(kind)}</td><td>{esc(p['tool'])} {esc(p['tool_version'])}</td>"
        f"<td>{esc(p['context']['origin'])}</td><td>{p['exit_code']}</td></tr>"
        for kind, p in report["provenance"].items()
    )
    test_detail = (
        f"Passed {tests['passed']}; failed {tests['failed']}; errors {tests['errors']}; "
        f"skipped {tests['skipped']}."
        if tests
        else "Tests: NOT_VERIFIED."
    )
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta http-equiv="Content-Security-Policy" '
        "content=\"default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'\">"
        "<title>ReleaseGate candidate review</title><style>"
        "body{margin:0;background:#101828;color:#e4e7ec;font:16px/1.6 system-ui}"
        "main{max-width:1050px;margin:32px auto;padding:24px}"
        "section{margin:24px 0;padding:24px;background:#1d2939;border:1px solid #344054;"
        "border-radius:12px;overflow-wrap:anywhere}h2{font-size:21px}"
        ".cards{display:flex;gap:16px;flex-wrap:wrap}.card{flex:1;min-width:170px;"
        "padding:20px;background:#26364c;border-radius:8px}"
        ".card strong{display:block;font-size:27px}"
        "table{width:100%;text-align:left;border-collapse:collapse}td,th{padding:10px;"
        "border-bottom:1px solid #344054}.boundary{border-left:5px solid #efb95b}"
        "h1{margin:0;font-size:32px}p{color:#b9c5d6}.badge{font-size:28px;font-weight:700;"
        "display:inline-block;padding:4px 24px;border-radius:8px;background:"
        + ("#075e47" if d["decision"] == "ALLOW" else "#922b3b")
        + "}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.8 ui-monospace,monospace}"
        "</style><main><h1>ReleaseGate</h1><p>Evidence → eligibility → human review</p>"
        f'<div class="badge">{html.escape(d["decision"])}</div>'
        "<p>Execution authorization: false · Production execution disabled</p>"
        f"<section><strong>Candidate</strong><p><code>{esc(d['commit_sha'])}</code></p>"
        f"<p>Target: {esc(d['target'])} · Gate: {esc(d['gate'])} · "
        f'Policy: {esc(d["policy_version"])}</p></section><div class="cards">{cards}</div>'
        f"<section><h2>Exact policy reasons</h2><ul>{reasons}</ul>"
        f"<p>Next gate: {esc(str(d['next_gate']))}</p>"
        f"<p>{esc(report['required_next_action'])}</p></section>"
        '<section class="boundary"><h2>Human authorization boundary</h2>'
        f"<p>{esc(report['human_authorization_boundary'])}</p></section>"
        f"<section><h2>Test and security detail</h2><p>{test_detail}</p>"
        f"<p>Missing identities: {esc(str(mandatory['missing']))}</p>"
        f"<pre>{esc(json.dumps(security, indent=2))}</pre></section>"
        "<section><h2>Evidence provenance</h2><table><tr><th>Check</th><th>Tool</th>"
        f"<th>Origin</th><th>Exit</th></tr>{provenance}</table>"
        f"<p>Hosted verification: {esc(report['hosted_verification'])}</p>"
        + "".join(f"<p>Pipeline reference: {esc(ref)}</p>" for ref in report["pipeline_references"])
        + "<details><summary>Digests and source context</summary>"
        f"<pre>{esc(json.dumps(report['provenance'], indent=2, sort_keys=True))}</pre>"
        f"</details></section><section><h2>Duo advisory</h2>{advice}</section>"
        "<section><h2>Known limitations</h2><ul>"
        + "".join(f"<li>{esc(item)}</li>" for item in report["limitations"])
        + "</ul></section></main></html>\n"
    )


def write_report(directory: Path, report: dict) -> None:
    write_json(directory / "report.json", report)
    (directory / "report.md").write_text(render_markdown(report), encoding="utf-8")
    (directory / "report.html").write_text(render_html(report), encoding="utf-8")
