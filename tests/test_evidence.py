import hashlib
import json

import pytest

from releasegate.evidence import (
    EvidenceError,
    context_for,
    load_evidence,
    parse_bandit,
    parse_junit,
    read_json,
    verify_scan_scope,
    write_json,
)


def junit(cases='<testcase name="example"/>', *, tests=1, failures=0, errors=0, skipped=0):
    return (
        f'<testsuites><testsuite tests="{tests}" failures="{failures}" '
        f'errors="{errors}" skipped="{skipped}">{cases}</testsuite></testsuites>'
    ).encode()


def bandit():
    metrics = {
        "loc": 5,
        "SEVERITY.LOW": 0,
        "SEVERITY.MEDIUM": 0,
        "SEVERITY.HIGH": 0,
        "SEVERITY.UNDEFINED": 0,
    }
    return {
        "errors": [],
        "generated_at": "2026-10-13T00:00:00Z",
        "metrics": {"_totals": metrics.copy(), "src/example.py": metrics.copy()},
        "results": [],
    }


def test_realistic_junit_counts():
    raw = junit(
        "<testcase/><testcase><failure/></testcase><testcase><skipped/></testcase>",
        tests=3,
        failures=1,
        skipped=1,
    )
    assert parse_junit(raw) == {"total": 3, "passed": 1, "failed": 1, "errors": 0, "skipped": 1}


@pytest.mark.parametrize(
    "raw",
    [
        b"not xml",
        b"<unknown/>",
        junit(tests=2),
        junit("<testcase><failure/></testcase>"),
        junit("<testcase><failure/><error/></testcase>", failures=1, errors=1),
        b'<!DOCTYPE x [<!ENTITY x "data">]><testsuites>&x;</testsuites>',
    ],
)
def test_unusable_xml_fails_closed(raw):
    with pytest.raises(EvidenceError):
        parse_junit(raw)


def test_security_metrics_are_verified():
    assert parse_bandit(bandit()) == {"scanned_files": 1, "findings": []}


def test_partial_security_scan_is_unusable(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "example.py").write_text("value = 1\n")
    (tmp_path / "src" / "unscanned.py").write_text("value = 2\n")
    with pytest.raises(EvidenceError, match="SECURITY_SCAN_SCOPE_MISMATCH"):
        verify_scan_scope(bandit(), tmp_path)


def test_inconsistent_line_metrics_are_unusable():
    report = bandit()
    report["metrics"]["_totals"]["loc"] = 100
    with pytest.raises(EvidenceError, match="BANDIT_COUNT_MISMATCH"):
        parse_bandit(report)


@pytest.mark.parametrize(
    "mutation",
    [
        "error",
        "no_metrics",
        "mismatched_totals",
        "zero_loc",
        "no_results",
        "bool_count",
        "bad_file_metric",
    ],
)
def test_unusable_bandit_fails_closed(mutation):
    value = bandit()
    if mutation == "error":
        value["errors"] = [{"filename": "broken.py", "reason": "syntax error"}]
    elif mutation == "no_metrics":
        value["metrics"] = {}
    elif mutation == "mismatched_totals":
        value["metrics"]["_totals"]["SEVERITY.HIGH"] = 1
    elif mutation == "zero_loc":
        value["metrics"]["_totals"]["loc"] = 0
    elif mutation == "no_results":
        del value["results"]
    elif mutation == "bool_count":
        value["metrics"]["_totals"]["SEVERITY.HIGH"] = False
    else:
        value["metrics"]["src/example.py"] = None
    with pytest.raises(EvidenceError):
        parse_bandit(value)


@pytest.mark.parametrize("content", ['{"a":1,"a":2}', '{"a":NaN}', "[]"])
def test_ambiguous_json_rejected(tmp_path, content):
    path = tmp_path / "input.json"
    path.write_text(content)
    with pytest.raises(EvidenceError):
        read_json(path)


def persisted(tmp_path, evidence):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "example.py").write_text("value = 1\n")
    directory = tmp_path / "evidence"
    directory.mkdir()
    for kind, raw in (("tests", junit()), ("security", json.dumps(bandit()).encode())):
        check = evidence["checks"][kind]
        check["context"] = context_for(tmp_path)
        check["summary"] = parse_junit(raw) if kind == "tests" else parse_bandit(bandit())
        check["raw_sha256"] = hashlib.sha256(raw).hexdigest()
        (directory / check["raw_file"]).write_bytes(raw)
        write_json(directory / f"{kind}.json", check)
    return directory


def test_load_verifies_persisted_raw_artifacts(tmp_path, evidence):
    directory = persisted(tmp_path, evidence)
    assert load_evidence(directory, root=tmp_path) == evidence


@pytest.mark.parametrize("tamper", ["raw", "summary", "path", "source", "context"])
def test_tampered_evidence_rejected(tmp_path, evidence, tamper):
    directory = persisted(tmp_path, evidence)
    path = directory / "security.json"
    check = read_json(path)
    if tamper == "raw":
        (directory / "security.bandit.json").write_text("{}")
    elif tamper == "summary":
        check["summary"]["scanned_files"] = 999
    elif tamper == "path":
        check["raw_file"] = "../../secret.json"
    elif tamper == "source":
        (tmp_path / "src" / "example.py").write_text("value = 2\n")
    else:
        check["context"]["pipeline_id"] = "another-pipeline"
    write_json(path, check)
    with pytest.raises(EvidenceError):
        load_evidence(directory, root=tmp_path)
