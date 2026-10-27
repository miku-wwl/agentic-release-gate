"""Fixed packaged verification, invoked only by the dedicated public service."""

import ctypes
import errno
import hashlib
import json
import os
import platform
import socket
import sys
import time
from pathlib import Path

from releasegate.evidence import (
    load_evidence,
    load_required_tests,
    read_json,
    run_check,
    write_json,
)
from releasegate.policy import evaluate

SCENARIOS = ("POSITIVE_CANDIDATE", "SECURITY_HIGH")
FIXTURE = (
    b"import subprocess\n\ndef unsafe_example(value):\n"
    b'    return subprocess.run("echo " + value, shell=True, check=True)\n'
)


def verify_bundle(root, manifest, *, negative=False):
    """Only regular manifest-bound files may enter a verification snapshot."""
    actual = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("LINKED_SOURCE")
        if path.is_file():
            raw = path.read_bytes()
            actual[path.relative_to(root).as_posix()] = {
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
    expected = dict(manifest["files"])
    if negative:
        expected["src/scan_only_security_fixture.py"] = {
            "bytes": len(FIXTURE),
            "sha256": hashlib.sha256(FIXTURE).hexdigest(),
        }
    if actual != expected:
        raise ValueError("PACKAGED_SOURCE_MISMATCH")


def isolate_worker():
    """Fail closed unless Linux/amd64 kernel network filtering is installed."""
    if sys.platform != "linux" or platform.machine() != "x86_64":
        raise RuntimeError("LINUX_AMD64_ISOLATION_REQUIRED")
    import resource

    for kind, limit in (
        (resource.RLIMIT_CPU, 55),
        (resource.RLIMIT_AS, 600 * 1024 * 1024),
        (resource.RLIMIT_FSIZE, 2 * 1024 * 1024),
        (resource.RLIMIT_NOFILE, 64),
        (resource.RLIMIT_NPROC, 32),
        (resource.RLIMIT_CORE, 0),
    ):
        resource.setrlimit(kind, (limit, limit))

    class Filter(ctypes.Structure):
        _fields_ = [
            ("code", ctypes.c_ushort),
            ("jt", ctypes.c_ubyte),
            ("jf", ctypes.c_ubyte),
            ("k", ctypes.c_uint),
        ]

    class Program(ctypes.Structure):
        _fields_ = [("length", ctypes.c_ushort), ("filter", ctypes.POINTER(Filter))]

    # Validate the syscall architecture, reject x32, then deny network and escape
    # mechanisms. This narrows trusted test processes; it is not an untrusted-code sandbox.
    instructions = [
        (0x20, 0, 0, 4),
        (0x15, 1, 0, 0xC000003E),
        (0x06, 0, 0, 0x80000000),
        (0x20, 0, 0, 0),
        (0x35, 0, 1, 0x40000000),
        (0x06, 0, 0, 0x80000000),
    ]
    denied = (*range(41, 56), 101, 165, 272, 288, 299, 304, 307, 308, 311, 321, 425)
    for number in denied:
        instructions += [(0x15, 0, 1, number), (0x06, 0, 0, 0x00050000 | errno.EPERM)]
    instructions.append((0x06, 0, 0, 0x7FFF0000))
    filters = (Filter * len(instructions))(*(Filter(*item) for item in instructions))
    program = Program(len(instructions), filters)
    libc = ctypes.CDLL(None, use_errno=True)
    libc.prctl.argtypes = [ctypes.c_int, *([ctypes.c_ulong] * 4)]
    for option, argument in ((38, 1), (22, ctypes.addressof(program))):
        # PR_SET_SECCOMP takes SECCOMP_MODE_FILTER as its second argument.
        result = (
            libc.prctl(option, argument, 0, 0, 0)
            if option == 38
            else libc.prctl(option, 2, argument, 0, 0)
        )
        if result != 0:
            raise OSError(ctypes.get_errno(), "WORKER_ISOLATION_UNAVAILABLE")
    try:
        socket.socket()
    except PermissionError:
        return "LINUX_SECCOMP_NETWORK_DENIED"
    raise RuntimeError("NETWORK_DENIAL_NOT_CONFIRMED")


def artifact(path):
    raw = path.read_bytes()
    return {
        "original_bytes": len(raw),
        "original_sha256": hashlib.sha256(raw).hexdigest(),
        "text": raw[: 64 * 1024].decode("utf-8", errors="replace"),
        "truncated": len(raw) > 64 * 1024,
    }


def execute(directory):
    value = read_json(directory / "input.json")
    scenario = value["scenario"]
    if scenario not in SCENARIOS:
        raise ValueError("UNSUPPORTED_SCENARIO")
    root = directory / "snapshot"
    manifest = read_json(directory / "source-manifest.json")
    verify_bundle(root, manifest, negative=scenario == "SECURITY_HIGH")
    isolation = isolate_worker()
    os.chdir(root)
    evidence_dir = root / "evidence"
    steps = []
    for kind in ("tests", "security"):
        write_json(directory / "progress.json", {"stage": kind.upper()})
        started = time.monotonic()
        check = run_check(
            kind, root=root, directory=evidence_dir, commit_sha=value["candidate_sha"]
        )
        steps.append(
            {
                "tool": check["tool"],
                "version": check["tool_version"],
                "exit_code": check["exit_code"],
                "duration_ms": round((time.monotonic() - started) * 1000),
                "raw_sha256": check["raw_sha256"],
            }
        )
    write_json(directory / "progress.json", {"stage": "EVIDENCE_AND_POLICY"})
    evidence = load_evidence(evidence_dir, root=root)
    required = load_required_tests(root)
    decision = evaluate(
        evidence,
        expected_commit=value["candidate_sha"],
        target="staging",
        required_test_ids=required,
    ).to_dict()
    events = [json.loads(line) for line in (directory / "guard.jsonl").read_text().splitlines()]
    entered = [item["module"] for item in events if item["event"] == "run_module"]
    if entered.count("pytest") != 1 or entered.count("bandit") != 1:
        raise ValueError("GENUINE_CHECK_EXECUTION_UNCONFIRMED")
    if any(item["event"] == "fixture_execution_blocked" for item in events):
        raise ValueError("SCAN_ONLY_EXECUTION_ATTEMPT_BLOCKED")
    security = evidence["checks"]["security"]["summary"]
    expected = (
        decision["decision"] == "ALLOW" and decision["next_gate"] == "HUMAN_APPROVAL"
        if scenario == "POSITIVE_CANDIDATE"
        else decision["decision"] == "DENY"
        and "SECURITY_HIGH" in decision["reasons"]
        and any(f["severity"] == "HIGH" for f in security["findings"])
    )
    result = {
        "policy": decision,
        "expected_outcome_matched": expected,
        "test_summary": evidence["checks"]["tests"]["summary"],
        "security_summary": security,
        "mandatory_required": len(required),
        "mandatory_present": len(
            required & set(evidence["checks"]["tests"]["summary"]["case_ids"])
        ),
        "source_digest": evidence["checks"]["tests"]["context"]["source_digest"],
        "source_manifest_sha256": hashlib.sha256(
            (directory / "source-manifest.json").read_bytes()
        ).hexdigest(),
        "evidence_digest": decision["evidence_digest"],
        "execution_origin": "PUBLIC_CONTAINER_EXECUTION",
        "policy_context_origin": "local-working-tree",
        "network_isolation": isolation,
        "scan_only_fixture_executed": False,
        "actual_steps": steps,
        "execution_events": events,
        "artifacts": {
            name: artifact(evidence_dir / name)
            for name in ("tests.junit.xml", "security.bandit.json", "tests.json", "security.json")
        },
    }
    if scenario == "SECURITY_HIGH":
        result["scan_only_fixture_sha256"] = hashlib.sha256(FIXTURE).hexdigest()
    write_json(directory / "result.json", result)


if __name__ == "__main__":
    execute(Path(sys.argv[1]).resolve())
