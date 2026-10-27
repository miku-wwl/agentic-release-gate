"""Anonymous, fixed-scenario product checks. No approval or deployment authority."""

import atexit
import copy
import hashlib
import hmac
import json
import math
import mimetypes
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from releasegate.advisory import SECRET
from releasegate.evidence import read_json
from releasegate.policy import SHA
from releasegate.public_security import enable_subreaper, entry_guard, reap_group
from releasegate.public_worker import FIXTURE, SCENARIOS, verify_bundle

MAX_OUTPUT = 512 * 1024
TERMINAL = {"COMPLETED", "FAILED", "TIMED_OUT"}
STATIC = (
    "index.html",
    "decision-explorer.html",
    "evidence-chain.html",
    "research.html",
    "audit-trail.html",
    "assets/console.css",
    "assets/console.js",
    "assets/mark.svg",
    "assets/public.css",
    "assets/public.js",
    "evidence/positive-report.json",
    "evidence/negative-report.json",
    "evidence/research-results.json",
    "build-manifest.json",
)
REFERENCE_STATIC = tuple(
    name for name in STATIC if name not in {"assets/public.css", "assets/public.js"}
)


def now():
    return datetime.now(UTC).isoformat()


def sanitize(value, roots=()):
    if isinstance(value, str):
        value = SECRET.sub("[REDACTED]", value)
        value = re.sub(r"https?://[^\s/:]+:[^\s/@]+@", "https://[REDACTED]@", value)
        value = re.sub(
            r"(?i)(\b(?:password|api[_-]?key|access[_-]?token|client[_-]?secret)\s*[:=]\s*)"
            r"(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)",
            r"\1[REDACTED]",
            value,
        )
        for root in sorted((str(p) for p in roots), key=len, reverse=True):
            value = value.replace(root, "<verification>").replace(
                root.replace("\\", "/"), "<verification>"
            )
        return value
    if isinstance(value, dict):
        return {key: sanitize(item, roots) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize(item, roots) for item in value]
    return value


def strict_body(raw):
    def unique(pairs):
        result = dict(pairs)
        if len(result) != len(pairs):
            raise ValueError("DUPLICATE_KEY")
        return result

    def reject(_):
        raise ValueError("NON_FINITE_NUMBER")

    value = json.loads(raw, object_pairs_hook=unique, parse_constant=reject)
    if (
        type(value) is not dict
        or set(value) != {"scenario"}
        or type(value["scenario"]) is not str
        or value["scenario"] not in SCENARIOS
    ):
        raise ValueError("Choose a fixed scenario; no commands, paths, URLs or extra fields")
    return value["scenario"]


def guard_source(forbidden, events):
    return f"""import datetime,json,os,sys
_forbidden = os.path.realpath({str(forbidden)!r})
_events = {str(events)!r}
def record(event, module=None):
    with open(_events, "a", encoding="utf-8") as stream:
        stream.write(json.dumps({{"event":event,"module":module,"pid":os.getpid(),"at":datetime.datetime.now(datetime.timezone.utc).isoformat()}})+"\\n")
def audit(event, args):
    if event == "cpython.run_module" and args[0] in ("pytest", "bandit"):
        record("run_module", args[0])
    if event == "exec" and args:
        name = getattr(args[0], "co_filename", "")
        if name and os.path.realpath(name) == _forbidden:
            record("fixture_execution_blocked")
            raise RuntimeError("Scan-only fixture execution prohibited")
sys.addaudithook(audit)
record("activated")
"""


class Rejected(ValueError):
    def __init__(self, code, message, retry=0):
        self.code, self.retry = code, retry
        super().__init__(message)


class PublicManager:
    """One process, one active job, ephemeral bounded history and global quotas."""

    def __init__(self, candidate, manifest, *, timeout=60, cooldown=30, daily_quota=24):
        self.candidate = Path(candidate).resolve()
        self.manifest = copy.deepcopy(manifest)
        if not SHA.fullmatch(manifest.get("candidate_sha", "")):
            raise ValueError("PINNED_CANDIDATE_REQUIRED")
        verify_bundle(self.candidate, self.manifest)
        enable_subreaper()
        self.timeout, self.cooldown, self.daily_quota = timeout, cooldown, daily_quota
        self.lock = threading.RLock()
        self.runs = {}
        self.active = None
        self.last_start = float("-inf")
        self.day = now()[:10]
        self.starts = 0
        self.requests = deque()
        self.closed = False
        self.process = None
        self.thread = None
        self.session_id = str(uuid4())

    def _prune(self):
        for key, item in list(self.runs.items()):
            if item["status"] in TERMINAL and time.monotonic() - item["_monotonic"] > 3600:
                del self.runs[key]
        if self.day != now()[:10]:
            self.day, self.starts = now()[:10], 0

    def allow_request(self):
        with self.lock:
            stamp = time.monotonic()
            while self.requests and self.requests[0] < stamp - 10:
                self.requests.popleft()
            if len(self.requests) >= 120:
                raise Rejected(429, "Global request rate limit; retry shortly", 10)
            self.requests.append(stamp)

    def metadata(self):
        with self.lock:
            self._prune()
            return {
                "candidate_sha": self.manifest["candidate_sha"],
                "session_id": self.session_id,
                "scenarios": [
                    {"id": SCENARIOS[0], "label": "Positive Candidate", "expected": "ALLOW"},
                    {
                        "id": SCENARIOS[1],
                        "label": "Security High",
                        "expected": "DENY / SECURITY_HIGH",
                    },
                ],
                "active_run_id": self.active,
                "cooldown_remaining": math.ceil(
                    max(0, self.cooldown - (time.monotonic() - self.last_start))
                ),
                "daily_starts_remaining": max(0, self.daily_quota - self.starts),
                "limits": {
                    "timeout_seconds": self.timeout,
                    "cooldown_seconds": self.cooldown,
                    "daily_starts": self.daily_quota,
                    "active_runs": 1,
                    "history": 10,
                },
                "history": [self.get(key) for key in reversed(list(self.runs))],
                "history_scope": "EPHEMERAL_INSTANCE_MEMORY",
                "quota_scope": "EPHEMERAL_INSTANCE_UTC_DAY_NOT_A_SPENDING_CAP",
                "production_execution": "DISABLED",
                "human_gate_executed": False,
                "execution_authorized": False,
            }

    def get(self, run_id, *, evidence=False):
        with self.lock:
            self._prune()
            try:
                if str(UUID(run_id, version=4)) != run_id or UUID(run_id).version != 4:
                    raise ValueError("INVALID_RUN_ID")
                item = self.runs[run_id]
            except (ValueError, TypeError, AttributeError, KeyError):
                raise KeyError("Run missing or expired; history is ephemeral") from None
            value = {k: copy.deepcopy(v) for k, v in item.items() if not k.startswith("_")}
            value["cached"] = item["status"] in TERMINAL
            if evidence:
                if item["status"] not in TERMINAL:
                    raise Rejected(409, "Evidence is available after verification finishes")
                return copy.deepcopy(item.get("_evidence", {"error": "No completed evidence"}))
            if item["status"] not in TERMINAL:
                value["duration_ms"] = round((time.monotonic() - item["_monotonic"]) * 1000)
            return value

    def start(self, scenario):
        if type(scenario) is not str or scenario not in SCENARIOS:
            raise Rejected(400, "Unsupported scenario")
        with self.lock:
            self._prune()
            if self.closed:
                raise Rejected(503, "Verification is unavailable")
            if self.active:
                raise Rejected(409, "One verification is already running")
            retry = self.cooldown - (time.monotonic() - self.last_start)
            if retry > 0:
                raise Rejected(
                    429, "Global start cooldown; inspect a cached completed result", int(retry) + 1
                )
            if self.starts >= self.daily_quota:
                raise Rejected(
                    429, "Instance daily quota reached; cached results remain available", 3600
                )
            while len(self.runs) >= 10:
                self.runs.pop(next(iter(self.runs)))
            run_id = str(uuid4())
            self.last_start = time.monotonic()
            self.starts += 1
            self.runs[run_id] = {
                "run_id": run_id,
                "scenario": scenario,
                "candidate_sha": self.manifest["candidate_sha"],
                "status": "RUNNING",
                "stage": "PREPARING",
                "started_at": now(),
                "completed_at": None,
                "duration_ms": 0,
                "test_summary": None,
                "security_summary": None,
                "policy_decision": "DENY",
                "denial_reasons": ["VERIFICATION_NOT_COMPLETE"],
                "next_gate": None,
                "execution_authorized": False,
                "production_execution": "DISABLED",
                "human_gate_executed": False,
                "evidence": f"/api/demo/verifications/{run_id}/evidence",
                "_monotonic": self.last_start,
            }
            self.active = run_id
            self.thread = threading.Thread(target=self._execute, args=(run_id,), daemon=True)
            self.thread.start()
            return self.get(run_id)

    def _kill(self, process):
        if os.name == "posix":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:
            process.kill()
        process.wait(timeout=5)
        reap_group(process.pid)

    def _execute(self, run_id):
        item = self.runs[run_id]
        directory = None
        process = None
        try:
            with tempfile.TemporaryDirectory(prefix="releasegate-public-") as temporary:
                directory = Path(temporary)
                snapshot = directory / "snapshot"
                verify_bundle(self.candidate, self.manifest)
                shutil.copytree(self.candidate, snapshot)
                if item["scenario"] == "SECURITY_HIGH":
                    (snapshot / "src/scan_only_security_fixture.py").write_bytes(FIXTURE)
                (directory / "source-manifest.json").write_text(json.dumps(self.manifest), "utf-8")
                (directory / "input.json").write_text(
                    json.dumps(
                        {"scenario": item["scenario"], "candidate_sha": item["candidate_sha"]}
                    ),
                    "utf-8",
                )
                guard = directory / "guard"
                guard.mkdir()
                (guard / "sitecustomize.py").write_text(
                    guard_source(
                        snapshot / "src/scan_only_security_fixture.py", directory / "guard.jsonl"
                    ),
                    "utf-8",
                )
                (directory / "home").mkdir()
                env = {
                    "PATH": str(Path(sys.executable).parent),
                    "HOME": str(directory / "home"),
                    "TMPDIR": str(directory),
                    "PYTHONPATH": os.pathsep.join((str(guard), str(snapshot / "src"))),
                    "PYTHONNOUSERSITE": "1",
                    "PYTHONSAFEPATH": "1",
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "PYTHONUTF8": "1",
                    "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
                }
                with (
                    (directory / "stdout.txt").open("wb") as stdout,
                    (directory / "stderr.txt").open("wb") as stderr,
                ):
                    process = subprocess.Popen(
                        [sys.executable, "-m", "releasegate.public_worker", str(directory)],
                        cwd=snapshot,
                        env=env,
                        stdin=subprocess.DEVNULL,
                        stdout=stdout,
                        stderr=stderr,
                        start_new_session=True,
                    )
                    with self.lock:
                        self.process = process
                    while process.poll() is None:
                        elapsed = time.monotonic() - item["_monotonic"]
                        if self.closed or elapsed > self.timeout:
                            self._kill(process)
                            raise TimeoutError("TOTAL_RUN_DEADLINE")
                        if stdout.tell() + stderr.tell() > MAX_OUTPUT:
                            self._kill(process)
                            raise ValueError("OUTPUT_LIMIT")
                        if (directory / "progress.json").exists():
                            try:
                                progress = read_json(directory / "progress.json")["stage"]
                                with self.lock:
                                    item["stage"] = progress
                            except (ValueError, OSError):
                                pass
                        time.sleep(0.05)
                if process.returncode != 0:
                    raise ValueError("VERIFICATION_PROCESS_FAILED")
                if (directory / "stdout.txt").stat().st_size + (
                    directory / "stderr.txt"
                ).stat().st_size > MAX_OUTPUT:
                    raise ValueError("OUTPUT_LIMIT")
                result = read_json(directory / "result.json")
                if result["policy"]["execution_authorized"] is not False:
                    raise ValueError("EXECUTION_BOUNDARY_INVALID")
                # Public views never serve private files. Hashes refer to original bytes;
                # sanitized-view hashes are separate and independently reproducible.
                roots = (directory, self.candidate, Path.home())
                public = sanitize(result, roots)
                for view in public["artifacts"].values():
                    view["sanitized_view_sha256"] = hashlib.sha256(
                        view["text"].encode()
                    ).hexdigest()
                    view["sanitized"] = view["sanitized_view_sha256"] != view["original_sha256"]
                public["logs"] = {
                    name: sanitize(
                        (directory / name).read_bytes()[: 64 * 1024].decode("utf-8", "replace"),
                        roots,
                    )
                    for name in ("stdout.txt", "stderr.txt")
                }
                if len(json.dumps(public).encode()) > 384 * 1024:
                    raise ValueError("PUBLIC_EVIDENCE_LIMIT")
                matched = result["expected_outcome_matched"] is True
                policy = result["policy"]
                with self.lock:
                    item.update(
                        status="COMPLETED" if matched else "FAILED",
                        stage="COMPLETE" if matched else "ERROR",
                        test_summary=public["test_summary"],
                        security_summary=public["security_summary"],
                        policy_decision=policy["decision"] if matched else "DENY",
                        denial_reasons=list(policy["reasons"])
                        if matched
                        else ["SCENARIO_EXPECTATION_FAILED"],
                        next_gate=policy["next_gate"] if matched else None,
                        observed_policy_decision=policy["decision"],
                        evidence_digest=policy["evidence_digest"],
                        source_digest=result["source_digest"],
                        mandatory_required=result["mandatory_required"],
                        mandatory_present=result["mandatory_present"],
                        _evidence=public,
                        completed_at=now(),
                        duration_ms=round((time.monotonic() - item["_monotonic"]) * 1000),
                    )
        except Exception as exc:
            with self.lock:
                item.update(
                    status="TIMED_OUT" if isinstance(exc, TimeoutError) else "FAILED",
                    stage="ERROR",
                    policy_decision="DENY",
                    denial_reasons=[
                        "VERIFICATION_TIMEOUT"
                        if isinstance(exc, TimeoutError)
                        else "VERIFICATION_UNUSABLE"
                    ],
                    next_gate=None,
                    error=type(exc).__name__,
                )
        finally:
            if process is not None and process.poll() is None:
                self._kill(process)
            with self.lock:
                item.update(
                    completed_at=now(),
                    duration_ms=round((time.monotonic() - item["_monotonic"]) * 1000),
                )
                self.active = None
                self.process = None

    def close(self):
        self.closed = True
        if self.process is not None and self.process.poll() is None:
            self._kill(self.process)
        if self.thread is not None:
            self.thread.join(timeout=6)


class PublicApplication:
    def __init__(
        self, manager, site, origin, *, accepted=False, execution_mode="PUBLIC", operator_key=None
    ):
        self.manager = manager
        self.origin = origin.rstrip("/")
        if not re.fullmatch(r"https://[a-z0-9.-]+|http://127\.0\.0\.1:[0-9]+", self.origin):
            raise ValueError("TRUSTED_PUBLIC_ORIGIN_REQUIRED")
        self.accepted = accepted
        if execution_mode not in {"STAGING", "PUBLIC", "LOCKED"}:
            raise ValueError("INVALID_EXECUTION_MODE")
        if execution_mode == "STAGING" and (
            not isinstance(operator_key, str) or len(operator_key) != 64
        ):
            raise ValueError("STAGING_OPERATOR_KEY_REQUIRED")
        self.execution_mode, self.operator_key = execution_mode, operator_key
        self.files = {}
        for name in REFERENCE_STATIC if execution_mode == "STAGING" else STATIC:
            path = Path(site) / name
            if path.is_symlink() or not path.is_file():
                raise ValueError("PUBLIC_STATIC_FILE_UNUSABLE")
            self.files["/" + name] = (
                path.read_bytes(),
                mimetypes.guess_type(name)[0] or "application/octet-stream",
            )
        self.files["/"] = self.files["/index.html"]

    def __call__(self, env, start_response):
        headers = []
        content_type = "application/json; charset=utf-8"
        try:
            path = env.get("PATH_INFO", "")
            method = env.get("REQUEST_METHOD", "")
            if (
                env.get("QUERY_STRING")
                or len(path) > 160
                or "%" in path
                or "\\" in path
                or ".." in path
            ):
                raise Rejected(404, "Unknown route")
            if path == "/healthz" and method in {"GET", "HEAD"}:
                code, value = 200, {"status": "ok", "production_execution": "DISABLED"}
            else:
                self.manager.allow_request()
                if path.startswith("/api/demo/") and self.execution_mode != "PUBLIC":
                    authorization = env.get("HTTP_AUTHORIZATION", "")
                    if self.execution_mode != "STAGING" or not hmac.compare_digest(
                        authorization, "Bearer " + self.operator_key
                    ):
                        raise Rejected(403, "Pre-release API is operator-only")
                if method not in {"GET", "HEAD", "POST"}:
                    raise Rejected(405, "Method unavailable")
                if method == "POST":
                    if path != "/api/demo/verifications":
                        raise Rejected(404, "No approval, release or deployment route exists")
                    if (
                        env.get("HTTP_ORIGIN") != self.origin
                        or env.get("HTTP_SEC_FETCH_SITE", "same-origin") != "same-origin"
                    ):
                        raise Rejected(403, "Use the same-origin console")
                    if env.get("CONTENT_TYPE") != "application/json" or env.get(
                        "HTTP_TRANSFER_ENCODING"
                    ):
                        raise Rejected(400, "A bounded application/json body is required")
                    length = env.get("CONTENT_LENGTH", "")
                    if not length.isdigit() or not 1 <= int(length) <= 128:
                        raise Rejected(413, "Request body exceeds the allowed size")
                    connection = env.get("gunicorn.socket")
                    if connection is not None:
                        connection.settimeout(5)
                    raw = env["wsgi.input"].read(int(length))
                    if len(raw) != int(length):
                        raise Rejected(400, "Incomplete JSON body")
                    code, value = 202, self.manager.start(strict_body(raw))
                elif path in self.files:
                    value, content_type = self.files[path]
                    code = 200
                elif path in {"/api/demo/scenarios", "/api/demo/verifications"}:
                    code, value = 200, self.manager.metadata()
                    value["live_e2e_accepted"] = self.accepted
                    value["mode"] = "LIVE_VERIFICATION" if self.accepted else "VERIFICATION_PREVIEW"
                elif match := re.fullmatch(
                    r"/api/demo/verifications/([a-f0-9-]{36})(/evidence)?", path
                ):
                    code, value = 200, self.manager.get(match[1], evidence=bool(match[2]))
                else:
                    raise Rejected(404, "Run or route missing; history is ephemeral")
        except Rejected as exc:
            code, value = exc.code, {"error": str(exc)}
            if exc.retry:
                headers.append(("Retry-After", str(exc.retry)))
        except (ValueError, TypeError, UnicodeError):
            code, value = 400, {"error": "Invalid fixed-scenario request"}
        except KeyError:
            code, value = 404, {"error": "Run missing or expired; history is ephemeral"}
        except Exception:
            code, value = 503, {"error": "Verification service unavailable"}
        raw = value if isinstance(value, bytes) else json.dumps(value, allow_nan=False).encode()
        if len(raw) > 1024 * 1024:
            code, raw = 503, b'{"error":"Response size limit"}'
        reasons = {
            200: "OK",
            202: "Accepted",
            400: "Bad Request",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            409: "Conflict",
            413: "Content Too Large",
            429: "Too Many Requests",
            503: "Service Unavailable",
        }
        headers += [
            ("Content-Type", content_type),
            ("Content-Length", str(len(raw))),
            ("Cache-Control", "no-store"),
            ("X-Content-Type-Options", "nosniff"),
            ("X-Frame-Options", "DENY"),
            ("Referrer-Policy", "no-referrer"),
            ("Permissions-Policy", "camera=(), microphone=(), geolocation=()"),
            ("Cross-Origin-Resource-Policy", "same-origin"),
            (
                "Content-Security-Policy",
                "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
                "connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; "
                "frame-ancestors 'none'",
            ),
            ("X-ReleaseGate-Mode", "PUBLIC_FIXED_SCENARIO_VERIFICATION"),
        ]
        start_response(f"{code} {reasons[code]}", headers)
        return [b"" if env.get("REQUEST_METHOD") == "HEAD" else raw]


def create_app():
    root = Path("/app")
    manager = PublicManager(root / "candidate", read_json(root / "source-manifest.json"))
    atexit.register(manager.close)
    mode = os.environ.get("PUBLIC_EXECUTION_MODE", "STAGING")
    control = os.environ.get("RELEASEGATE_CONTROL_DIR")
    operator_key = None
    if mode != "LOCKED":
        if not control:
            raise RuntimeError("INSTANCE_ADMISSION_REQUIRED")
        admission = read_json(Path(control) / "admission.json")
        if (
            admission.get("status") != "PASS"
            or admission.get("candidate_sha") != manager.manifest["candidate_sha"]
        ):
            raise RuntimeError("INSTANCE_ADMISSION_IDENTITY_MISMATCH")
        entry_guard()
    if mode == "STAGING":
        if not control:
            raise RuntimeError("STAGING_OPERATOR_CONTROL_UNAVAILABLE")
        operator_key = (Path(control) / "operator.key").read_text("utf-8")
    return PublicApplication(
        manager,
        root / ("reference-site" if mode == "STAGING" else "site"),
        os.environ["PUBLIC_ORIGIN"],
        accepted=os.environ.get("PUBLIC_LIVE_ACCEPTED") == "1",
        execution_mode=mode,
        operator_key=operator_key,
    )
