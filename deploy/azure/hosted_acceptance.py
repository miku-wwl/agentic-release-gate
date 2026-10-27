"""Authenticated exec-only acceptance. No secret is printed or sent outside the container."""

import errno
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from releasegate.evidence import parse_junit, read_json
from releasegate.public_security import enable_subreaper, entry_guard, reap_group, snapshot

CONTROL = Path(Path("/tmp/releasegate-control.path").read_text().strip())
BASE = "http://127.0.0.1:8080"
ORIGIN = os.environ["PUBLIC_ORIGIN"]
KEY = (
    (CONTROL / "operator.key").read_text()
    if os.environ.get("PUBLIC_EXECUTION_MODE") == "STAGING"
    else None
)


def request(path, body=None, *, expected=200, authorized=True):
    headers = {"Origin": ORIGIN, "Content-Type": "application/json"}
    if KEY and authorized:
        headers["Authorization"] = "Bearer " + KEY
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urlopen(Request(BASE + path, data=data, headers=headers), timeout=15) as reply:
            code, raw = reply.status, reply.read()
    except HTTPError as exc:
        code, raw = exc.code, exc.read()
    if code != expected:
        raise RuntimeError(f"HTTP_ACCEPTANCE_FAILED:{path}:{code}:{expected}")
    return json.loads(raw) if raw[:1] in (b"{", b"[") else None


def security():
    identity = entry_guard()
    enable_subreaper()
    admission = read_json(CONTROL / "admission.json")
    assert admission["status"] == "PASS"
    server_identity = snapshot(admission["identity"]["Pid"])
    assert all(int(server_identity[field], 16) == 0 for field in ("CapEff", "CapPrm", "CapInh"))
    assert server_identity["NoNewPrivs"] == "1"
    for name in ("/app/candidate/.write-probe", "/opt/venv/.write-probe"):
        try:
            descriptor = os.open(name, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except OSError as exc:
            assert exc.errno in {errno.EACCES, errno.EPERM, errno.EROFS}
        else:
            os.close(descriptor)
            Path(name).unlink()
            raise RuntimeError("TRUSTED_SOURCE_WRITABLE")
    if KEY:
        request("/api/demo/scenarios", expected=403, authorized=False)
        request(
            "/api/demo/verifications",
            {"scenario": "POSITIVE_CANDIDATE"},
            expected=403,
            authorized=False,
        )
    for bad in (
        {"scenario": "UNKNOWN"},
        {"scenario": "SECURITY_HIGH", "command": "id"},
        {"scenario": "../../etc/passwd"},
        {"scenario": "https://example.com/code.py"},
    ):
        request("/api/demo/verifications", bad, expected=400)
    for path in (
        "/.env",
        "/.git/config",
        "/api/deploy",
        "/api/approve",
        "/api/runs",
        "/api/demo/verifications/../../etc/passwd",
    ):
        request(path, expected=404)
    metadata = request("/api/demo/scenarios")
    assert (
        metadata["execution_authorized"] is False and metadata["production_execution"] == "DISABLED"
    )
    assert metadata["limits"]["active_runs"] == 1 and metadata["limits"]["timeout_seconds"] == 60
    log_path = CONTROL / "hosted-tests.log"
    junit = CONTROL / "hosted-tests.xml"
    environment = {
        "PATH": str(Path(sys.executable).parent),
        "PYTHONPATH": "/app/candidate/src",
        "TMPDIR": str(CONTROL / "tmp"),
        "HOME": "/nonexistent",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
    }
    process = None
    with log_path.open("wb") as log:
        try:
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    "-s",
                    "frontend/tests/test_public.py",
                    "-p",
                    "no:cacheprovider",
                    f"--junitxml={junit}",
                ],
                cwd="/app/candidate",
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=log,
                start_new_session=True,
            )
            code = process.wait(timeout=60)
        finally:
            if process is not None and process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
                reap_group(process.pid)
    summary = parse_junit(junit.read_bytes())
    assert (
        code == 0
        and summary["passed"] >= 35
        and not any(summary[k] for k in ("failed", "errors", "skipped"))
    )
    events = []
    for line in log_path.read_text().splitlines():
        try:
            value = json.loads(line[line.index("{") :])
            if value.get("test"):
                events.append(value)
        except ValueError:
            pass
    assert len(events) == 2 and events[0]["child_alive_confirmed"] and events[1]["child_absent"]
    result = {
        "status": "PASS",
        "at": datetime.now(UTC).isoformat(),
        "revision": os.environ.get("CONTAINER_APP_REVISION", "LOCAL"),
        "source_sha": metadata["candidate_sha"],
        "identity": identity,
        "server_identity": server_identity,
        "boot_admission": admission,
        "tests": summary,
        "hosted_events": events,
        "protected_unauthenticated_api": bool(KEY),
        "source_write_denied": True,
        "log_sha256": hashlib.sha256(log_path.read_bytes()).hexdigest(),
    }
    (CONTROL / "hosted-security.json").write_text(json.dumps(result, indent=2), "utf-8")
    print(json.dumps(result), flush=True)


def business():
    assert read_json(CONTROL / "hosted-security.json")["status"] == "PASS"
    records = []
    for scenario in ("POSITIVE_CANDIDATE", "SECURITY_HIGH"):
        while (meta := request("/api/demo/scenarios"))["cooldown_remaining"]:
            time.sleep(min(meta["cooldown_remaining"], 5))
        run = request("/api/demo/verifications", {"scenario": scenario}, expected=202)
        print(json.dumps({"started": run["run_id"], "scenario": scenario}), flush=True)
        request("/api/demo/verifications", {"scenario": scenario}, expected=409)
        deadline = time.monotonic() + 70
        while time.monotonic() < deadline:
            run = request("/api/demo/verifications/" + run["run_id"])
            if run["status"] in {"COMPLETED", "FAILED", "TIMED_OUT"}:
                break
            time.sleep(1)
        assert run["status"] == "COMPLETED", run
        assert (
            run["test_summary"]["passed"]
            == run["mandatory_present"]
            == run["mandatory_required"]
            == 139
        )
        assert run["execution_authorized"] is False and run["human_gate_executed"] is False
        assert run["policy_decision"] == ("ALLOW" if scenario == "POSITIVE_CANDIDATE" else "DENY")
        assert run["next_gate"] == ("HUMAN_APPROVAL" if scenario == "POSITIVE_CANDIDATE" else None)
        if scenario == "SECURITY_HIGH":
            assert "SECURITY_HIGH" in run["denial_reasons"]
        evidence = request(run["evidence"])
        worker = evidence["worker_security"]
        assert all(int(worker[name], 16) == 0 for name in ("CapEff", "CapPrm", "CapInh"))
        assert worker["NoNewPrivs"] == "1" and worker["Seccomp"] == "2"
        assert set(worker["Uid"].split()) == {"43343"} and set(worker["Gid"].split()) == {"43343"}
        assert worker["limits"]["RLIMIT_NPROC"] == [32, 32]
        assert evidence["scan_only_fixture_executed"] is False
        assert evidence["evidence_digest"] == run["evidence_digest"]
        assert [step["tool"] for step in evidence["actual_steps"]] == ["pytest", "bandit"]
        for item in evidence["artifacts"].values():
            assert (
                hashlib.sha256(item["text"].encode()).hexdigest() == item["sanitized_view_sha256"]
            )
        if request("/api/demo/scenarios")["cooldown_remaining"]:
            request("/api/demo/verifications", {"scenario": scenario}, expected=429)
        records.append({"run": run, "evidence": evidence})
        print(
            json.dumps(
                {
                    "completed": run["run_id"],
                    "decision": run["policy_decision"],
                    "duration_ms": run["duration_ms"],
                }
            ),
            flush=True,
        )
    assert records[0]["run"]["run_id"] != records[1]["run"]["run_id"]
    result = {
        "status": "PASS",
        "source_sha": records[0]["run"]["candidate_sha"],
        "records": records,
    }
    (CONTROL / "hosted-business.json").write_text(json.dumps(result, indent=2), "utf-8")
    summary = {
        "status": "PASS",
        "source_sha": result["source_sha"],
        "records": [
            {
                "run_id": item["run"]["run_id"],
                "scenario": item["run"]["scenario"],
                "started_at": item["run"]["started_at"],
                "decision": item["run"]["policy_decision"],
                "evidence_digest": item["run"]["evidence_digest"],
                "worker_security": item["evidence"]["worker_security"],
            }
            for item in records
        ],
    }
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    {"security": security, "business": business}[sys.argv[1]]()
