"""Public API abuse cases; Linux-only controls also run in the actual container."""

import hashlib
import importlib.util
import io
import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

from releasegate.public_verification import (
    PublicApplication,
    PublicManager,
    Rejected,
    guard_source,
    sanitize,
    strict_body,
)
from releasegate.public_worker import FIXTURE, verify_bundle

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def public_site(tmp_path_factory):
    spec = importlib.util.spec_from_file_location(
        "public_builder", ROOT / "frontend/build_public_console.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    site = tmp_path_factory.mktemp("public-site") / "site"
    module.build(site)
    return site


@pytest.fixture
def candidate(tmp_path):
    root = tmp_path / "candidate"
    (root / "src").mkdir(parents=True)
    raw = b"trusted = True\n"
    (root / "src/example.py").write_bytes(raw)
    return root, {
        "candidate_sha": "a" * 40,
        "files": {"src/example.py": {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}},
    }


@pytest.fixture
def manager(candidate):
    value = PublicManager(*candidate, cooldown=30)
    yield value
    value.close()


@pytest.mark.parametrize(
    "raw",
    [
        b"{}",
        b"[]",
        b"null",
        b'{"scenario":"SECURITY_HIGH","command":"id"}',
        b'{"scenario":"../etc/passwd"}',
        b'{"scenario":"https://attacker.example/repo"}',
        b'{"scenario":"POSITIVE_CANDIDATE;id"}',
        b'{"scenario":true}',
        b'{"scenario":"POSITIVE_CANDIDATE","scenario":"SECURITY_HIGH"}',
        b'{"scenario":NaN}',
        b'{"scenario":["POSITIVE_CANDIDATE"]}',
    ],
)
def test_only_exact_fixed_scenario_json_is_accepted(raw):
    with pytest.raises((ValueError, TypeError)):
        strict_body(raw)


def test_manifest_rejects_tampering_unknown_files_and_fixture_substitution(candidate):
    root, manifest = candidate
    verify_bundle(root, manifest)
    fixture = root / "src/scan_only_security_fixture.py"
    fixture.write_bytes(FIXTURE)
    with pytest.raises(ValueError, match="MISMATCH"):
        verify_bundle(root, manifest)
    verify_bundle(root, manifest, negative=True)
    fixture.write_bytes(b"not the reviewed fixture")
    with pytest.raises(ValueError, match="MISMATCH"):
        verify_bundle(root, manifest, negative=True)


def test_linked_source_is_rejected(candidate, monkeypatch):
    root, manifest = candidate
    original = Path.is_symlink
    monkeypatch.setattr(
        Path, "is_symlink", lambda path: path.name == "example.py" or original(path)
    )
    with pytest.raises(ValueError, match="LINKED"):
        verify_bundle(root, manifest)


def test_global_concurrency_cooldown_quota_and_ephemeral_history(manager, monkeypatch):
    entered = threading.Event()
    release = threading.Event()

    def block(run_id):
        entered.set()
        release.wait(2)
        with manager.lock:
            manager.runs[run_id].update(
                status="COMPLETED", completed_at="measured", _evidence={"verified": True}
            )
            manager.active = None

    monkeypatch.setattr(manager, "_execute", block)
    first = manager.start("POSITIVE_CANDIDATE")
    assert entered.wait(1)
    with pytest.raises(Rejected) as error:
        manager.start("SECURITY_HIGH")
    assert error.value.code == 409
    release.set()
    manager.thread.join(2)
    with pytest.raises(Rejected) as error:
        manager.start("SECURITY_HIGH")
    assert error.value.code == 429
    manager.last_start = float("-inf")
    manager.starts = manager.daily_quota
    with pytest.raises(Rejected) as error:
        manager.start("SECURITY_HIGH")
    assert error.value.code == 429
    assert manager.get(first["run_id"], evidence=True) == {"verified": True}
    manager.runs[first["run_id"]]["_monotonic"] -= 3601
    with pytest.raises(KeyError):
        manager.get(first["run_id"])


def test_request_rate_limit_is_global_and_does_not_trust_forwarded_ip(manager):
    for _ in range(120):
        manager.allow_request()
    with pytest.raises(Rejected) as error:
        manager.allow_request()
    assert error.value.code == 429


def call(app, path="/", method="GET", body=b"", **extra):
    env = {
        "PATH_INFO": path,
        "REQUEST_METHOD": method,
        "QUERY_STRING": "",
        "CONTENT_LENGTH": str(len(body)),
        "CONTENT_TYPE": "application/json",
        "HTTP_ORIGIN": "http://127.0.0.1:8778",
        "wsgi.input": io.BytesIO(body),
        **extra,
    }
    captured = {}

    def respond(status, headers):
        captured.update(status=int(status[:3]), headers=dict(headers))

    raw = b"".join(app(env, respond))
    return captured, raw


@pytest.mark.parametrize(
    "path",
    [
        "/.env",
        "/.git/config",
        "/api/runs",
        "/api/approve",
        "/api/deploy",
        "/api/release",
        "/api/demo/verifications/../../etc/passwd",
        "/%2e%2e/.env",
        "/src/releasegate/live.py",
    ],
)
def test_no_file_read_or_production_endpoint(manager, public_site, path):
    app = PublicApplication(manager, public_site, "http://127.0.0.1:8778")
    reply, _ = call(app, path)
    assert reply["status"] == 404
    assert "Access-Control-Allow-Origin" not in reply["headers"]


def test_http_schema_boundaries_and_badge_gate(manager, public_site):
    app = PublicApplication(manager, public_site, "http://127.0.0.1:8778")
    reply, raw = call(app, "/api/demo/scenarios")
    assert reply["status"] == 200
    assert json.loads(raw)["live_e2e_accepted"] is False
    assert "connect-src 'self'" in reply["headers"]["Content-Security-Policy"]
    for extra, expected in [
        ({"HTTP_ORIGIN": "https://evil.example"}, 403),
        ({"CONTENT_LENGTH": "9999999"}, 413),
        ({"HTTP_TRANSFER_ENCODING": "chunked"}, 400),
        ({"CONTENT_TYPE": "text/plain"}, 400),
        ({"HTTP_SEC_FETCH_SITE": "cross-site"}, 403),
    ]:
        reply, _ = call(
            app, "/api/demo/verifications", "POST", b'{"scenario":"POSITIVE_CANDIDATE"}', **extra
        )
        assert reply["status"] == expected
    reply, _ = call(
        app, "/api/demo/verifications", "POST", b'{"scenario":"SECURITY_HIGH","path":"/tmp/x"}'
    )
    assert reply["status"] == 400
    assert manager.starts == 0
    reply, raw = call(app, "/healthz", "HEAD")
    assert reply["status"] == 200 and not raw


def test_public_builder_preserves_historical_evidence_and_safe_rendering(public_site):
    for name in (
        "index.html",
        "decision-explorer.html",
        "evidence-chain.html",
        "audit-trail.html",
        "research.html",
    ):
        html = (public_site / name).read_text("utf-8")
        assert html.count("<h1>") == 1
        assert "Production disabled" in html
        assert "Safe live verification" in html
        assert "connect-src &#x27;self&#x27;" in html
        assert "REFERENCE SNAPSHOT" not in html
    assert "42 / 42" in (public_site / "research.html").read_text("utf-8")
    assert "Historical reference evidence" in (public_site / "audit-trail.html").read_text("utf-8")
    script = (public_site / "assets/public.js").read_text("utf-8")
    assert "innerHTML" not in script and "eval(" not in script
    assert "textContent" in script and "cached" in script


def test_redaction_preserves_types_and_escapes_no_json_syntax():
    token = "glpat-" + "z" * 30
    value = sanitize(
        {"text": token + " password=private /private/run/x", "allowed": False, "count": 139},
        ("/private/run",),
    )
    assert token not in value["text"] and "private /private" not in value["text"]
    assert value["allowed"] is False and value["count"] == 139
    assert json.loads(json.dumps(value)) == value


def test_scan_only_guard_prevents_execution_before_any_effect(tmp_path):
    forbidden = tmp_path / "unsafe.py"
    marker = tmp_path / "would-have-executed"
    guard = tmp_path / "guard"
    guard.mkdir()
    (guard / "sitecustomize.py").write_text(
        guard_source(forbidden, tmp_path / "events.jsonl"), "utf-8"
    )
    forbidden.write_text(f"from pathlib import Path\nPath({str(marker)!r}).touch()\n", "utf-8")
    result = subprocess.run(
        [sys.executable, "-c", "import runpy,sys; runpy.run_path(sys.argv[1])", str(forbidden)],
        env={**os.environ, "PYTHONPATH": str(guard)},
        capture_output=True,
        timeout=10,
        check=False,
    )
    assert result.returncode != 0 and not marker.exists()
    assert "fixture_execution_blocked" in (tmp_path / "events.jsonl").read_text()


@pytest.mark.parametrize("failure", ["missing_evidence", "output_limit", "forged_authorization"])
def test_worker_failures_cannot_become_allow(candidate, monkeypatch, failure):
    manager = PublicManager(*candidate, cooldown=0)
    real_popen = subprocess.Popen
    commands = {
        "missing_evidence": "pass",
        "output_limit": "print('x' * (1024 * 1024))",
        "forged_authorization": (
            "import pathlib,json,sys; "
            "pathlib.Path(sys.argv[1],'result.json').write_text("
            "json.dumps({'policy':{'execution_authorized':True}}))"
        ),
    }

    def launch(command, **kwargs):
        return real_popen([sys.executable, "-c", commands[failure], command[-1]], **kwargs)

    monkeypatch.setattr("releasegate.public_verification.subprocess.Popen", launch)
    run = manager.start("POSITIVE_CANDIDATE")
    manager.thread.join(10)
    result = manager.get(run["run_id"])
    assert result["status"] == "FAILED"
    assert result["policy_decision"] == "DENY" and result["next_gate"] is None
    assert result["execution_authorized"] is False
    manager.close()


@pytest.mark.skipif(
    sys.platform != "linux", reason="Linux seccomp is verified inside the production image"
)
def test_linux_network_filter_is_inherited_by_child():
    code = """from releasegate.public_worker import isolate_worker
import json,os,pathlib,resource,subprocess,sys
assert isolate_worker() == "LINUX_SECCOMP_NETWORK_DENIED"
assert resource.getrlimit(resource.RLIMIT_NPROC) == (32, 32)
probe = '''import json,os,pathlib,resource,socket
status = dict(
    line.split(':', 1)
    for line in pathlib.Path('/proc/self/status').read_text().splitlines() if ':' in line
)
print(json.dumps({
    'pid':os.getpid(),'ppid':os.getppid(),'uid':os.getuid(),
    'nproc':resource.getrlimit(resource.RLIMIT_NPROC),'threads':status['Threads'].strip(),
    'seccomp':status['Seccomp'].strip(),'cap_eff':status['CapEff'].strip()
}),flush=True)
socket.socket()
'''
result = subprocess.run([sys.executable, "-c", probe], capture_output=True)
assert result.returncode != 0 and b"Operation not permitted" in result.stderr
child = json.loads(result.stdout)
assert child['pid'] != os.getpid() and child['ppid'] == os.getpid()
assert child['nproc'] == [32,32] and child['seccomp'] == '2'
assert int(child['cap_eff'],16) == 0
print(json.dumps({'test':'inherited_network_denial','parent_pid':os.getpid(),'child':child,'child_exit':result.returncode,'socket_denied':True}))
"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, timeout=10, check=False
    )
    assert result.returncode == 0, result.stderr.decode()
    print(result.stdout.decode().strip())


@pytest.mark.skipif(
    sys.platform != "linux", reason="Linux process groups are verified inside the production image"
)
def test_actual_total_timeout_kills_owned_descendant(candidate, monkeypatch, tmp_path):
    manager = PublicManager(*candidate, timeout=5, cooldown=0)
    real_popen = subprocess.Popen
    pidfile = tmp_path / "child.pid"
    child_code = (
        "import json,os,pathlib,time; "
        f"marker=pathlib.Path({str(pidfile)!r}); temporary=marker.with_suffix('.ready'); "
        "temporary.write_text(json.dumps("
        "{'pid':os.getpid(),'ppid':os.getppid(),'pgid':os.getpgrp()})); "
        "temporary.replace(marker); time.sleep(60)"
    )
    code = (
        "import subprocess,sys,time; "
        f"child=subprocess.Popen([sys.executable,'-c',{child_code!r}]); time.sleep(60)"
    )

    def launch(_command, **kwargs):
        return real_popen([sys.executable, "-c", code], **kwargs)

    monkeypatch.setattr("releasegate.public_verification.subprocess.Popen", launch)
    try:
        started = time.monotonic()
        run = manager.start("POSITIVE_CANDIDATE")
        # Acknowledgment is written by the actual descendant, not its launcher.
        # Observe it alive before the unchanged watchdog mechanism times out.
        while not pidfile.exists() and time.monotonic() - started < 4:
            time.sleep(0.02)
        assert pidfile.exists(), "Descendant did not acknowledge before the test deadline"
        child = json.loads(pidfile.read_text())
        process = manager.process
        assert process is not None and process.poll() is None
        assert child["ppid"] == process.pid == child["pgid"]
        assert child["pgid"] != os.getpgrp()
        stat = Path(f"/proc/{child['pid']}/stat")
        assert stat.exists() and stat.read_text().split()[2] != "Z"
        os.kill(child["pid"], 0)
        ready_ms = round((time.monotonic() - started) * 1000)
        manager.thread.join(10)
        result = manager.get(run["run_id"])
        assert result["status"] == "TIMED_OUT"
        assert process.returncode == -signal.SIGKILL
        assert not stat.exists() or stat.read_text().split()[2] == "Z"
        assert result["policy_decision"] == "DENY" and result["next_gate"] is None
        assert result["execution_authorized"] is False
        assert 5000 <= result["duration_ms"] < 11000
        print(
            json.dumps(
                {
                    "test": "owned_group_timeout",
                    "parent_pid": process.pid,
                    "child": child,
                    "child_ready_ms": ready_ms,
                    "duration_ms": result["duration_ms"],
                    "parent_exit": process.returncode,
                    "child_not_running": True,
                    "decision": result["policy_decision"],
                }
            )
        )
    finally:
        manager.close()
