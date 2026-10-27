"""Kernel checks for trusted verification processes, independent of Docker flags."""

import ctypes
import os
import sys
import time
from pathlib import Path


def prctl(option, value):
    libc = ctypes.CDLL(None, use_errno=True)
    libc.prctl.argtypes = [ctypes.c_int, *([ctypes.c_ulong] * 4)]
    if libc.prctl(option, value, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), "KERNEL_GUARD_UNAVAILABLE")


def snapshot(pid="self"):
    fields = dict(
        line.split(":", 1)
        for line in Path(f"/proc/{pid}/status").read_text().splitlines()
        if ":" in line
    )
    result = {
        key: fields[key].strip()
        for key in (
            "Pid",
            "PPid",
            "Uid",
            "Gid",
            "Threads",
            "CapInh",
            "CapPrm",
            "CapEff",
            "CapBnd",
            "NoNewPrivs",
            "Seccomp",
        )
    }
    if pid == "self":
        import resource

        result["limits"] = {
            name: list(resource.getrlimit(getattr(resource, name)))
            for name in ("RLIMIT_NPROC", "RLIMIT_CPU", "RLIMIT_AS", "RLIMIT_FSIZE", "RLIMIT_NOFILE")
        }
    return result


def entry_guard():
    if sys.platform != "linux" or any(
        value != 43343
        for value in (
            os.getuid(),
            os.geteuid(),
            os.getgid(),
            os.getegid(),
        )
    ):
        raise RuntimeError("DEDICATED_NONROOT_IDENTITY_REQUIRED")
    current = snapshot()
    if any(int(current[name], 16) for name in ("CapInh", "CapPrm", "CapEff")):
        raise RuntimeError("UNEXPECTED_PROCESS_CAPABILITIES")
    prctl(38, 1)  # PR_SET_NO_NEW_PRIVS: inherited and cannot be unset.
    current = snapshot()
    if current["NoNewPrivs"] != "1":
        raise RuntimeError("NO_NEW_PRIVILEGES_UNCONFIRMED")
    return current


def enable_subreaper():
    if sys.platform == "linux":
        prctl(36, 1)  # Adopt owned orphan descendants, rather than leave zombies.


def reap_group(group, timeout=2):
    if sys.platform != "linux":
        return
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            child, _ = os.waitpid(-group, os.WNOHANG)
            if child:
                continue
        except ChildProcessError:
            try:
                os.killpg(group, 0)
            except ProcessLookupError:
                return
        time.sleep(0.01)
    raise RuntimeError("OWNED_PROCESS_GROUP_NOT_REAPED")
