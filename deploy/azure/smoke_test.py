"""Functional and security smoke checks for the static container site."""

import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PAGES = (
    "/",
    "/decision-explorer.html",
    "/evidence-chain.html",
    "/research.html",
    "/audit-trail.html",
)
ASSETS = (
    ("/assets/console.css", "text/css"),
    ("/assets/console.js", "javascript"),
    ("/assets/mark.svg", "image/svg+xml"),
)
EVIDENCE = (
    "/evidence/positive-report.json",
    "/evidence/negative-report.json",
    "/evidence/research-results.json",
)
FORBIDDEN = (
    "/.env",
    "/.git/config",
    "/artifacts/",
    "/50x.html",
    "/api/runs",
    "/api/runs/123/cancel",
)
SECURITY_HEADERS = (
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
    "permissions-policy",
    "content-security-policy",
    "cache-control",
    "x-releasegate-mode",
)


def get(base, path, method="GET"):
    request = Request(base + path, method=method)
    try:
        with urlopen(request, timeout=15) as response:
            return response.status, response.headers, response.read()
    except HTTPError as error:
        return error.code, error.headers, error.read()
    except URLError as error:
        raise AssertionError(f"Request failed for {path}: {error.reason}") from error


def check(base):
    for path in PAGES:
        status, headers, body = get(base, path)
        assert status == 200, f"{path}: expected 200, got {status}"
        assert "text/html" in headers.get("Content-Type", ""), path
        text = body.decode("utf-8")
        assert "ReleaseGate" in text, path
        assert headers.get("X-ReleaseGate-Mode") == "READ_ONLY_SHOWCASE", path
        for header in SECURITY_HEADERS:
            assert headers.get(header), f"{path}: missing {header}"

    status, _, explorer = get(base, "/decision-explorer.html")
    text = explorer.decode("utf-8")
    for phrase in ("ALLOW", "DENY", "DEMO FIXTURE", "SECURITY_HIGH"):
        assert phrase in text, f"Decision Explorer missing {phrase}"
    status, _, overview = get(base, "/")
    overview_text = overview.decode("utf-8")
    assert "execution_authorized" in overview_text
    assert "human approval required" in overview_text.casefold()

    for path, content_type in ASSETS:
        status, headers, body = get(base, path)
        assert status == 200 and body, f"asset unavailable: {path}"
        assert content_type in headers.get("Content-Type", ""), path

    for path in EVIDENCE:
        status, headers, body = get(base, path)
        assert status == 200, f"evidence unavailable: {path}"
        assert "application/json" in headers.get("Content-Type", ""), path
        data = json.loads(body)
        assert isinstance(data, dict), path

    positive = json.loads(get(base, EVIDENCE[0])[2])
    negative = json.loads(get(base, EVIDENCE[1])[2])
    research = json.loads(get(base, EVIDENCE[2])[2])
    assert positive["decision"]["decision"] == "ALLOW"
    assert positive["decision"]["execution_authorized"] is False
    assert negative["decision"]["decision"] == "DENY"
    assert negative["decision"]["execution_authorized"] is False
    assert research["metrics"]["total_scenarios"] == 14
    assert research["metrics"]["trials_executed"] == 42
    assert research["metrics"]["correct_decisions"] == 42
    assert research["metrics"]["false_allow"] == 0
    assert research["metrics"]["false_deny"] == 0

    status, headers, body = get(base, "/healthz")
    assert status == 200 and body == b"ok\n"
    assert headers.get("X-ReleaseGate-Mode") == "READ_ONLY_SHOWCASE"

    for path in FORBIDDEN + ("/unknown-releasegate-route",):
        status, _, body = get(base, path)
        assert status == 404, f"{path}: expected 404, got {status}"
        assert b"ReleaseGate" not in body, f"unexpected static fallback for {path}"

    status, _, _ = get(base, "/api/runs", method="POST")
    assert status == 405, f"POST /api/runs: expected 405, got {status}"
    status, _, _ = get(base, "/", method="POST")
    assert status == 405, f"POST /: expected 405, got {status}"
    print("SMOKE_TEST=PASS")
    print(f"PAGES={len(PAGES)} ASSETS={len(ASSETS)} EVIDENCE={len(EVIDENCE)}")
    print("READ_ONLY_SHOWCASE=PASS")
    print("API_AND_SENSITIVE_PATHS=DENIED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", help="Local or public container app origin")
    check(parser.parse_args().base_url.rstrip("/"))
