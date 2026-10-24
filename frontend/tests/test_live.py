"""Local execution/security regression; inner verification still runs the original tests/."""

import ast
import hashlib
import http.client
import json
import os
import subprocess
import sys
import threading
import time
from html.parser import HTMLParser
from pathlib import Path
from uuid import uuid4

import pytest
from test_console import create_test_symlink

from releasegate.evidence import load_evidence, load_required_tests, parse_bandit, parse_junit
from releasegate.live import (
    ARTIFACTS,
    ASSETS,
    LiveError,
    LiveManager,
    LiveServer,
    Run,
    activated_interpreter,
    guard_source,
    redact,
    safe_path,
    valid_id,
)
from releasegate.policy import evaluate

ROOT = Path(__file__).resolve().parents[2]


def test_recycled_windows_pid_cannot_match_an_earlier_process():
    process = {
        "pid": 123,
        "started_at": "2026-10-25T01:00:04+00:00",
        "finished_at": "2026-10-25T01:00:05+00:00",
    }
    old = {"event": "activated", "pid": 123, "ppid": 100, "at": "2026-10-25T01:00:01+00:00"}
    current = {"event": "activated", "pid": 456, "ppid": 123, "at": "2026-10-25T01:00:04.1+00:00"}
    assert activated_interpreter([old, current], process) == 456
    with pytest.raises(LiveError, match="guard was not confirmed"):
        activated_interpreter([old], process)
    with pytest.raises(LiveError, match="guard was not confirmed"):
        activated_interpreter([current, dict(current, pid=789)], process)


def test_posix_cli_activation_is_distinct_from_its_inner_check():
    process = {
        "pid": 123,
        "started_at": "2026-10-25T01:00:01+00:00",
        "finished_at": "2026-10-25T01:00:05+00:00",
    }
    cli = {"event": "activated", "pid": 123, "ppid": 100, "at": "2026-10-25T01:00:02+00:00"}
    inner = {"event": "activated", "pid": 456, "ppid": 123, "at": "2026-10-25T01:00:03+00:00"}
    assert activated_interpreter([cli, inner], process) == 123


def test_status_redaction_preserves_json_types_and_unmodified_original_state(tmp_path):
    manager = LiveManager(ROOT)
    run = Run(tmp_path / str(uuid4()), "allow")
    credential = "synthetic" + "-credential"
    original = "password=" + credential + '"'
    run.value.update(error=original, nested={"text": [original, {"count": 7}], "boundary": False})
    manager.runs[run.directory.name] = run
    try:
        state = manager.get(run.directory.name)
        encoded = json.dumps(state)
        assert json.loads(encoded) == state
        assert credential not in encoded and "[REDACTED]" in encoded
        assert state["nested"]["text"][1]["count"] == 7
        assert state["nested"]["boundary"] is False
        assert run.value["error"] == original
        assert run.value["nested"]["text"][0] == original
    finally:
        manager.runs.clear()
        manager.close()


def wait_for(manager, run_id, timeout=100):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        run = manager.get(run_id)
        if run["status"] != "running":
            return run
        time.sleep(0.05)
    raise AssertionError("Real verification did not finish")


def test_real_consecutive_allow_and_scan_only_rejection(monkeypatch):
    for name in ("GITLAB_CI", "CI_PROJECT_ID", "CI_PIPELINE_ID", "CI_COMMIT_SHA"):
        monkeypatch.delenv(name, raising=False)
    manager = LiveManager(ROOT)
    values = []
    try:
        for operation in ("allow", "allow", "security_rejection"):
            run_id = manager.start(operation)
            run = wait_for(manager, run_id)
            assert run["status"] == "completed", run["error"]
            directory = manager.storage / run_id
            source = directory / "snapshot"
            expected_sha = manager.head()
            assert run["source_sha"] == expected_sha
            evidence = load_evidence(source / "evidence", root=source)
            decision = evaluate(
                evidence,
                expected_commit=expected_sha,
                target="staging",
                required_test_ids=load_required_tests(source),
            )
            assert json.loads(json.dumps(decision.to_dict())) == json.loads(
                (source / "evidence/decision.json").read_text(encoding="utf-8")
            )
            assert decision.decision == ("DENY" if operation == "security_rejection" else "ALLOW")
            assert decision.execution_authorized is False
            if operation == "security_rejection":
                assert "SECURITY_HIGH" in decision.reasons
                assert run["fixture"]["scope"].startswith("CONTROLLED SCAN-ONLY")
            else:
                assert decision.next_gate == "HUMAN_APPROVAL"
            junit = (source / "evidence/tests.junit.xml").read_bytes()
            required = load_required_tests(source)
            tests = parse_junit(junit)
            assert tests["passed"] == len(required) == 139
            assert set(tests["case_ids"]) == required
            bandit = json.loads((source / "evidence/security.bandit.json").read_text("utf-8"))
            findings = parse_bandit(bandit)["findings"]
            assert any(f["severity"] == "HIGH" for f in findings) == (
                operation == "security_rejection"
            )
            assert run["guard_verified"] is True
            assert len(run["processes"]) == 4
            assert all(p["pid"] and p["python_pid"] for p in run["processes"])
            assert all(p["started_at"] <= p["finished_at"] for p in run["processes"])
            assert all(p["inner_check_pid"] for p in run["processes"][:2])
            assert not any(
                e["event"] == "fixture_execution_blocked" for e in run["inner_processes"]
            )
            for artifact in run["artifacts"]:
                raw = (directory / ARTIFACTS[artifact["key"]]).read_bytes()
                assert len(raw) == artifact["bytes"]
                assert hashlib.sha256(raw).hexdigest() == artifact["sha256"]
            stages = [e["stage"] for e in run["events"]]
            assert stages == [
                "preparing",
                "tests",
                "security",
                "collecting",
                "policy",
                "report",
                "completed",
            ]
            values.append((run, hashlib.sha256(junit).hexdigest(), bandit["generated_at"]))
        first, second = values[:2]
        assert first[0]["run_id"] != second[0]["run_id"]
        assert first[0]["finished_at"] < second[0]["started_at"]
        assert first[1] != second[1]
        assert first[2] != second[2]
    finally:
        manager.close()


def test_concurrency_limit_and_shutdown_cancel(monkeypatch):
    manager = LiveManager(ROOT)
    entered = threading.Event()

    def blocked(run):
        entered.set()
        run.cancel.wait(10)
        manager._finish(run, "cancelled", "Verification cancelled")
        with manager.lock:
            manager.active = None

    monkeypatch.setattr(manager, "_execute", blocked)
    first = manager.start("allow")
    assert entered.wait(3)
    with pytest.raises(LiveError, match="Another verification"):
        manager.start("security_rejection")
    manager.close()
    assert manager.get(first)["status"] == "cancelled"
    with pytest.raises(LiveError, match="shutting down"):
        manager.start("allow")


@pytest.mark.parametrize("mode", ["failure", "timeout", "cancel"])
def test_actual_process_failure_timeout_and_cancel(tmp_path, mode):
    manager = LiveManager(ROOT, process_timeout=0.25 if mode == "timeout" else 10)
    directory = tmp_path / str(uuid4())
    directory.mkdir()
    run = Run(directory, "allow")
    env = {**os.environ, "PYTHONUTF8": "1"}
    script = (
        "import sys; print('actual failure'); sys.stderr.write('failure details\\n');sys.exit(7)"
        if mode == "failure"
        else "import time; print('actual running process',flush=True);time.sleep(8)"
    )
    if mode == "cancel":
        timer = threading.Timer(0.3, run.cancel.set)
        timer.start()
    try:
        result = manager._process(
            run, "tests", [sys.executable, "-c", script], snapshot=ROOT, env=env
        )
        assert result["pid"] and result["finished_at"] and result["duration_seconds"] >= 0
        if mode == "failure":
            assert result["exit_code"] == 7 and result["termination"] is None
            assert "actual failure" in (directory / "logs/tests.stdout.txt").read_text("utf-8")
        else:
            assert result["termination"] == ("timeout" if mode == "timeout" else "cancelled")
            assert result["exit_code"] != 0
    finally:
        if mode == "cancel":
            timer.join()
        manager.close()


def test_fixture_guard_blocks_harmless_code_before_execution(tmp_path):
    """Prove the guard with a harmless marker, never execute the vulnerable demo fixture."""
    fixture = tmp_path / "harmless_guard_probe.py"
    marker = tmp_path / "MUST_NOT_EXIST"
    fixture.write_text(f"from pathlib import Path\nPath({str(marker)!r}).touch()\n", "utf-8")
    guard = tmp_path / "guard"
    guard.mkdir()
    events = tmp_path / "events.jsonl"
    (guard / "sitecustomize.py").write_text(guard_source(fixture, events), "utf-8")
    env = {**os.environ, "PYTHONPATH": str(guard), "PYTHONNOUSERSITE": "1"}
    completed = subprocess.run(
        [sys.executable, str(fixture)], cwd=tmp_path, env=env, capture_output=True, timeout=10
    )
    assert (
        completed.returncode != 0 and b"Scan-only fixture execution prohibited" in completed.stderr
    )
    assert not marker.exists()
    assert any(
        json.loads(line)["event"] == "fixture_execution_blocked"
        for line in events.read_text("utf-8").splitlines()
    )


@pytest.fixture
def server():
    manager = LiveManager(ROOT)
    service = LiveServer(manager, 0)
    thread = threading.Thread(target=service.serve_forever, daemon=True)
    thread.start()
    yield service
    service.shutdown()
    manager.close()
    service.server_close()
    thread.join(3)


def request(server, method, path, body=None, **extra):
    connection = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=8)
    headers = {
        "Origin": server.origin,
        "Content-Type": "application/json",
        "X-ReleaseGate-Request": "live-console",
        **extra,
    }
    connection.request(method, path, body=body, headers=headers)
    response = connection.getresponse()
    data, received = response.read(), dict(response.getheaders())
    status = response.status
    connection.close()
    return status, data, received


def test_loopback_initial_state_and_no_cors(server):
    assert server.server_address[0] == "127.0.0.1"
    status, raw, headers = request(server, "GET", "/api/session")
    value = json.loads(raw)
    assert status == 200 and value["source_sha"] == server.manager.head()
    assert value["active_run_id"] is None
    assert value["production_execution"] == "DISABLED"
    assert value["human_approval"] == "REQUIRED / UNEXECUTED"
    assert "Access-Control-Allow-Origin" not in headers
    assert "connect-src 'self'" in headers["Content-Security-Policy"]
    status, raw, _ = request(server, "GET", "/")
    assert status == 200 and b"No verification has been run in this session." in raw
    assert b"139 / 139" not in raw and b"Phase 5" not in raw


@pytest.mark.parametrize(
    "headers",
    [
        {"Origin": "http://evil.example"},
        {"Origin": "null"},
        {"Origin": ""},
        {"Host": "evil.example"},
        {"X-ReleaseGate-Request": ""},
        {"Sec-Fetch-Site": "cross-site"},
    ],
)
def test_cross_origin_and_rebinding_requests_rejected(server, headers):
    status, _raw, _headers = request(
        server, "POST", "/api/runs", '{"operation":"allow"}', **headers
    )
    assert status == 403 and not server.manager.runs


@pytest.mark.parametrize(
    "body",
    [
        '{"operation":"release"}',
        '{"operation":"allow","command":"anything"}',
        '{"operation":"allow","cwd":"C:/"}',
        '{"operation":"allow","executable":"anything"}',
        '{"operation":"allow","operation":"security_rejection"}',
        '{"operation":[]}',
        '{"operation":true}',
        "[]",
        "{}",
        "not json",
    ],
)
def test_arbitrary_commands_paths_and_malformed_operations_rejected(server, body):
    status, _raw, _headers = request(server, "POST", "/api/runs", body)
    assert status == 400 and not server.manager.runs


@pytest.mark.parametrize(
    "path",
    [
        "/../pyproject.toml",
        "/assets/../live.py",
        "/assets/%2e%2e/live.py",
        "/api/runs/../../pyproject.toml",
        f"/api/runs/{uuid4()}/artifacts/../../pyproject.toml",
        f"/api/runs/{uuid4()}/artifacts/source-code",
        "/api/session?path=pyproject.toml",
    ],
)
def test_arbitrary_file_reads_and_traversal_are_rejected(server, path):
    status, _raw, _headers = request(server, "GET", path)
    assert status == 404


def test_uuid_paths_redaction_and_minimal_process_environment(tmp_path):
    assert valid_id(str(uuid4()))
    assert not valid_id("../anything") and not valid_id("A" * 40)
    with pytest.raises(LiveError):
        safe_path(tmp_path, tmp_path / ".." / "elsewhere")
    token = "glpat-" + "A" * 30
    assert token not in redact(token, root=ROOT)
    sample = "secret" + "123"
    password = redact("password=" + json.dumps(sample), root=ROOT)
    assert sample not in password and "[REDACTED]" in password
    url = redact("https://" + "user" + ":" + "secret" + "@example.test", root=ROOT)
    assert "user:secret@" not in url and "[REDACTED]" in url
    manager = LiveManager(ROOT)
    run = Run(tmp_path, "allow")
    env = manager._environment(run, tmp_path, tmp_path)
    assert "GITLAB_CI" not in env and "CI_COMMIT_SHA" not in env
    assert "GH_TOKEN" not in env and "GITLAB_TOKEN" not in env
    assert env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"
    manager.close()


def test_artifact_aliases_and_symlinks_are_confined(tmp_path, monkeypatch):
    manager = LiveManager(ROOT)
    directory = tmp_path / str(uuid4())
    directory.mkdir()
    run = Run(directory, "allow")
    manager.runs[directory.name] = run
    (directory / "logs").mkdir()
    (directory / "logs/tests.stdout.txt").write_text("safe output", "utf-8")
    assert manager.artifact(directory.name, "test-stdout")["text"] == "safe output"
    with pytest.raises(KeyError):
        manager.artifact(directory.name, "../pyproject.toml")
    external = tmp_path / "outside.txt"
    external.write_text("not for browser", "utf-8")
    link = directory / "logs/tests.stderr.txt"
    create_test_symlink(link, external, monkeypatch)
    with pytest.raises(LiveError):
        manager.artifact(directory.name, "test-stderr")
    manager.runs.clear()
    manager.close()


def test_product_assets_have_no_injection_sinks_or_internal_stage_copy():
    html = (ASSETS / "index.html").read_text("utf-8")
    javascript = (ASSETS / "live.js").read_text("utf-8")
    assert all(
        label in html
        for label in ("Run Fresh Verification", "Run ALLOW Verification", "Run Security Rejection")
    )
    assert "Phase " not in html and "Read-only by design" not in html
    assert "No verification has been run in this session." in html
    assert "Production execution" in html and "UNEXECUTED" in html
    assert not any(
        sink in javascript for sink in ("innerHTML", "insertAdjacentHTML", "eval(", "new Function(")
    )
    assert 'api("/api/runs", {operation})' in javascript
    assert "run.events" in javascript and "run.result" in javascript
    assert "setTimeout(resolve, 500)" in javascript
    assert "simulat" not in html.lower()

    class Document(HTMLParser):
        def __init__(self):
            super().__init__()
            self.nodes = []

        def handle_starttag(self, tag, attrs):
            self.nodes.append((tag, dict(attrs)))

    document = Document()
    document.feed(html)
    assert sum(tag == "h1" for tag, _ in document.nodes) == 1
    assert not any(tag in {"iframe", "form", "object", "embed"} for tag, _ in document.nodes)
    assert not any(key.startswith("on") for _, attrs in document.nodes for key in attrs)
    source = ast.parse((ROOT / "src/releasegate/live.py").read_text("utf-8"))
    for node in ast.walk(source):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in {"Popen", "run"}
        ):
            assert not any(
                k.arg == "shell" and isinstance(k.value, ast.Constant) and k.value.value is True
                for k in node.keywords
            )
