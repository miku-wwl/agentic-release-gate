"""Fail-closed per-instance admission before opening the HTTP listener."""

import hashlib
import json
import os
import secrets
import signal
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from releasegate.evidence import parse_junit, read_json
from releasegate.public_security import enable_subreaper, entry_guard, reap_group


def main():
    identity = entry_guard()
    enable_subreaper()
    mode = os.environ.get("PUBLIC_EXECUTION_MODE", "STAGING")
    if mode not in {"STAGING", "PUBLIC"}:
        raise RuntimeError("INVALID_TRUSTED_EXECUTION_MODE")
    control = Path(tempfile.mkdtemp(prefix="releasegate-control-"))
    os.chmod(control, 0o700)
    os.environ["RELEASEGATE_CONTROL_DIR"] = str(control)
    descriptor = os.open(
        "/tmp/releasegate-control.path",
        os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW,
        0o600,
    )
    with os.fdopen(descriptor, "w") as locator:
        if os.fstat(locator.fileno()).st_uid != 43343:
            raise RuntimeError("CONTROL_LOCATOR_OWNER_INVALID")
        locator.write(str(control))
    if mode == "STAGING":
        descriptor = os.open(control / "operator.key", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w") as stream:
            stream.write(secrets.token_urlsafe(48))
    temporary = control / "tmp"
    temporary.mkdir(mode=0o700)
    env = {
        "PATH": str(Path(sys.executable).parent),
        "PYTHONPATH": "/app/candidate/src",
        "TMPDIR": str(temporary),
        "HOME": "/nonexistent",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
    }
    junit = control / "admission.junit.xml"
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "-s",
        "frontend/tests/test_public.py",
        "-p",
        "no:cacheprovider",
        "-k",
        "linux_network_filter_is_inherited_by_child or actual_total_timeout_kills_owned_descendant",
        f"--junitxml={junit}",
    ]
    process = None
    with (control / "admission.log").open("wb") as log:
        try:
            process = subprocess.Popen(
                command,
                cwd="/app/candidate",
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=log,
                start_new_session=True,
            )
            code = process.wait(timeout=30)
        finally:
            if process is not None and process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
                reap_group(process.pid)
    raw = (control / "admission.log").read_bytes()
    summary = parse_junit(junit.read_bytes())
    if (
        code != 0
        or summary["passed"] != 2
        or any(summary[k] for k in ("failed", "errors", "skipped"))
    ):
        raise RuntimeError("INSTANCE_SECURITY_ADMISSION_FAILED")
    events = []
    for line in raw.decode("utf-8", "replace").splitlines():
        try:
            event = json.loads(line[line.index("{") :])
            if event.get("test") in {"inherited_network_denial", "owned_group_timeout"}:
                events.append(event)
        except (ValueError, TypeError):
            pass
    if (
        len(events) != 2
        or not events[0].get("child_alive_confirmed")
        or not events[1].get("child_absent")
    ):
        raise RuntimeError("INSTANCE_SECURITY_EVIDENCE_INCOMPLETE")
    report = {
        "status": "PASS",
        "at": datetime.now(UTC).isoformat(),
        "identity": identity,
        "candidate_sha": read_json(Path("/app/source-manifest.json"))["candidate_sha"],
        "tests": summary,
        "events": events,
        "log_sha256": hashlib.sha256(raw).hexdigest(),
        "production_execution": "DISABLED",
        "execution_authorized": False,
    }
    (control / "admission.json").write_text(json.dumps(report, indent=2), "utf-8")
    executable = str(Path(sys.executable).parent / "gunicorn")
    os.execv(
        executable,
        [
            executable,
            "--config",
            "/app/gunicorn.conf.py",
            "releasegate.public_verification:create_app()",
        ],
    )


if __name__ == "__main__":
    main()
