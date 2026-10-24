"""Loopback-only, fixed-operation verification UI. No approval or deployment endpoint."""

import argparse
import copy
import hashlib
import io
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import threading
import time
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit
from uuid import UUID, uuid4

from releasegate.advisory import SECRET
from releasegate.evidence import MAX_REPORT_BYTES, read_json

OPERATIONS = frozenset({"allow", "security_rejection"})
TERMINAL = frozenset({"completed", "failed", "cancelled"})
ASSETS = Path(__file__).parent / "live_assets"
ARTIFACTS = {
    "test-stdout": "logs/tests.stdout.txt",
    "test-stderr": "logs/tests.stderr.txt",
    "security-stdout": "logs/security.stdout.txt",
    "security-stderr": "logs/security.stderr.txt",
    "policy-stdout": "logs/policy.stdout.txt",
    "policy-stderr": "logs/policy.stderr.txt",
    "report-stdout": "logs/report.stdout.txt",
    "report-stderr": "logs/report.stderr.txt",
    "junit": "snapshot/evidence/tests.junit.xml",
    "bandit": "snapshot/evidence/security.bandit.json",
    "tests": "snapshot/evidence/tests.json",
    "security": "snapshot/evidence/security.json",
    "decision": "snapshot/evidence/decision.json",
    "review-json": "snapshot/evidence/review/report.json",
    "review-md": "snapshot/evidence/review/report.md",
    "review-html": "snapshot/evidence/review/report.html",
    "processes": "processes.json",
    "source-manifest": "source-manifest.json",
    "execution-guard": "execution-guard.jsonl",
}
CLI_BOOTSTRAP = (
    "import pathlib,sys,sitecustomize,releasegate; "
    "expected=pathlib.Path('src/releasegate').resolve(); "
    "actual=pathlib.Path(releasegate.__file__).resolve().parent; "
    "sys.exit('Verification import identity rejected') "
    "if actual != expected or not sitecustomize.RELEASEGATE_GUARD_ACTIVE else None; "
    "from releasegate.cli import main; sys.exit(main(sys.argv[1:]))"
)


class LiveError(ValueError):
    pass


def utc_now():
    return datetime.now(UTC).isoformat()


def write_state(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes((json.dumps(value, indent=2, sort_keys=True) + "\n").encode())
    temporary.replace(path)


def safe_path(root, path):
    root = root.resolve()
    if not path.resolve().is_relative_to(root):
        raise LiveError("Artifact outside verification workspace")
    current = path
    while current != root:
        if current.is_symlink() or current.is_junction():
            raise LiveError("Linked verification paths are not allowed")
        current = current.parent
    return path


def valid_id(value):
    try:
        parsed = UUID(value)
        return parsed.version == 4 and str(parsed) == value
    except (ValueError, TypeError, AttributeError):
        return False


def activated_interpreter(events, process):
    # Windows can reuse an exited check's PID for a later CLI launcher in one run.
    activated = [
        event
        for event in events
        if event["event"] == "activated"
        and process["started_at"] <= event["at"] <= process["finished_at"]
        and (event["pid"] == process["pid"] or event["ppid"] == process["pid"])
    ]
    if len(activated) != 1:
        raise LiveError("Verification execution guard was not confirmed")
    return activated[0]["pid"]


def redact(text, *, root):
    text = SECRET.sub("[REDACTED]", str(text))
    text = re.sub(r"https?://[^\s/:]+:[^\s/@]+@", "https://[REDACTED]@", text)
    text = re.sub(
        r"(?i)(\b(?:password|api[_-]?key|access[_-]?token|client[_-]?secret)\s*[:=]\s*)"
        r"(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)",
        r"\1[REDACTED]",
        text,
    )
    for path, label in ((str(root), "<workspace>"), (str(Path.home()), "<home>")):
        text = text.replace(path, label).replace(path.replace("\\", "/"), label)
        text = text.replace(path.replace("\\", "\\\\"), label)
    return text


def guard_source(forbidden, events):
    """A negative fixture cannot be executed, even by an accidental import."""
    return f"""import datetime,json,os,re,sys
RELEASEGATE_GUARD_ACTIVE = True
_forbidden = os.path.normcase(os.path.realpath({str(forbidden)!r}))
_events = {str(events)!r}
def _record(event, module=None):
    with open(_events, "a", encoding="utf-8") as stream:
        value = {{"event": event, "pid": os.getpid(), "ppid": os.getppid(),
                 "at": datetime.datetime.now(datetime.timezone.utc).isoformat()}}
        if module:
            value["module"] = module
        stream.write(json.dumps(value) + "\\n")
def _audit(event, arguments):
    if event == "cpython.run_module" and arguments[0] in ("pytest", "bandit"):
        _record("run_module", arguments[0])
    if event == "subprocess.Popen":
        command = arguments[1]
        if isinstance(command, (list, tuple)) and len(command) > 2:
            if command[1] == "-m" and command[2] in ("pytest", "bandit"):
                _record("spawn_check", command[2])
        elif isinstance(command, str):
            match = re.search(r"(?:^|\\s)-m\\s+(pytest|bandit)(?:\\s|$)", command)
            if match:
                _record("spawn_check", match.group(1))
    if event == "exec" and arguments:
        name = getattr(arguments[0], "co_filename", "")
        if name and os.path.normcase(os.path.realpath(name)) == _forbidden:
            _record("fixture_execution_blocked")
            raise RuntimeError("Scan-only fixture execution prohibited")
sys.addaudithook(_audit)
_record("activated")
"""


class Run:
    def __init__(self, directory, operation):
        self.directory = directory
        self.cancel = threading.Event()
        self.started = time.monotonic()
        self.thread = None
        self.value = {
            "run_id": directory.name,
            "operation": operation,
            "status": "running",
            "stage": "preparing",
            "started_at": utc_now(),
            "finished_at": None,
            "source_sha": None,
            "events": [],
            "processes": [],
            "artifacts": [],
            "result": None,
            "error": None,
            "human_approval": "REQUIRED / UNEXECUTED",
            "production_execution": "DISABLED",
            "execution_authorized": False,
        }


class LiveManager:
    """Product verification jobs only; not an agent Action executor or release gateway."""

    def __init__(self, root, *, process_timeout=120, max_runs=20):
        self.root = Path(root).resolve()
        self.git = shutil.which("git")
        if not self.git or not (self.root / "pyproject.toml").is_file():
            raise LiveError("Start in a ReleaseGate Git checkout with Git installed")
        self.storage = safe_path(self.root, self.root / ".artifacts" / "live-verification")
        self.storage.mkdir(parents=True, exist_ok=True)
        self.process_timeout = process_timeout
        self.max_runs = max_runs
        self.lock = threading.RLock()
        self.runs = {}
        self.active = None
        self.closing = False
        self.session_id = str(uuid4())
        self.session_started_at = utc_now()
        self.head()

    def _git(self, *arguments):
        result = subprocess.run(
            [self.git, "-c", "core.autocrlf=false", "-c", "core.eol=lf", *arguments],
            cwd=self.root,
            capture_output=True,
            check=True,
            timeout=20,
        )
        return result.stdout

    def head(self):
        value = self._git("rev-parse", "--verify", "HEAD^{commit}").decode().strip()
        if not re.fullmatch(r"[a-f0-9]{40}", value):
            raise LiveError("Current repository HEAD is unavailable")
        return value

    def _event(self, run, stage, **values):
        with self.lock:
            run.value.update(values, stage=stage)
            run.value["events"].append({"stage": stage, "at": utc_now()})
            write_state(run.directory / "run.json", run.value)

    def start(self, operation):
        if type(operation) is not str or operation not in OPERATIONS:
            raise LiveError("Unsupported verification operation")
        with self.lock:
            if self.closing:
                raise LiveError("Verification service is shutting down")
            if self.active:
                raise LiveError("Another verification is active; wait or cancel that run")
            if len(self.runs) >= self.max_runs:
                raise LiveError("Session run limit reached; restart the service before more runs")
            directory = safe_path(self.storage, self.storage / str(uuid4()))
            directory.mkdir(exist_ok=False)
            run = Run(directory, operation)
            self.runs[directory.name] = run
            self.active = directory.name
            self._event(run, "preparing")
            run.thread = threading.Thread(target=self._execute, args=(run,), daemon=False)
            run.thread.start()
            return directory.name

    def get(self, run_id):
        with self.lock:
            if not valid_id(run_id) or run_id not in self.runs:
                raise KeyError("Run not found in this service session")
            run = self.runs[run_id]
            value = copy.deepcopy(run.value)
            if value["finished_at"] is None:
                value["duration_seconds"] = round(time.monotonic() - run.started, 3)
            return json.loads(redact(json.dumps(value), root=self.root))

    def cancel(self, run_id):
        with self.lock:
            if run_id not in self.runs or self.runs[run_id].value["status"] in TERMINAL:
                raise LiveError("No active verification to cancel")
            self.runs[run_id].cancel.set()

    def close(self):
        with self.lock:
            self.closing = True
            pending = [r for r in self.runs.values() if r.value["status"] not in TERMINAL]
            for run in pending:
                run.cancel.set()
        for run in pending:
            run.thread.join(timeout=25)
            if run.thread.is_alive():
                raise LiveError("Verification worker did not stop cleanly")

    def _snapshot(self, run):
        sha = self.head()
        snapshot = run.directory / "snapshot"
        snapshot.mkdir()
        entries = {}
        for line in self._git("ls-tree", "-rz", sha).split(b"\0"):
            if not line:
                continue
            identity, name = line.split(b"\t", 1)
            mode, kind, blob = identity.decode().split()
            name = name.decode("utf-8")
            if mode not in {"100644", "100755"} or kind != "blob":
                raise LiveError("Only regular tracked source files can be verified")
            entries[name] = blob
        data = self._git("archive", "--format=tar", sha)
        if len(data) > 64 * 1024 * 1024:
            raise LiveError("Verification snapshot exceeds the source size limit")
        files = {}
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            for item in archive.getmembers():
                name = PurePosixPath(item.name)
                if name.is_absolute() or ".." in name.parts or item.issym() or item.islnk():
                    raise LiveError("Unsafe source archive path")
                if item.isdir():
                    continue
                if not item.isfile() or name.as_posix() not in entries:
                    raise LiveError("Unexpected source archive member")
                raw = archive.extractfile(item).read()
                blob = hashlib.sha1(
                    b"blob " + str(len(raw)).encode() + b"\0" + raw, usedforsecurity=False
                ).hexdigest()
                if blob != entries[name.as_posix()]:
                    raise LiveError("Snapshot bytes do not match the committed source")
                target = safe_path(snapshot, snapshot / str(name))
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
                files[name.as_posix()] = {
                    "bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                }
        if set(files) != set(entries) or (snapshot / "evidence").exists():
            raise LiveError("Source snapshot incomplete or contains old run evidence")
        forbidden = snapshot / "src" / "scan_only_security_fixture.py"
        derived = None
        if run.value["operation"] == "security_rejection":
            if forbidden.exists():
                raise LiveError("Scan-only fixture path already exists in source")
            forbidden.write_bytes(
                b"import subprocess\n\ndef unsafe_example(value):\n"
                b'    return subprocess.run("echo " + value, shell=True, check=True)\n'
            )
            derived = {
                "path": forbidden.relative_to(snapshot).as_posix(),
                "sha256": hashlib.sha256(forbidden.read_bytes()).hexdigest(),
                "scope": "CONTROLLED SCAN-ONLY SCENARIO; never an import or test target",
            }
        guard = run.directory / "guard"
        guard.mkdir()
        (guard / "sitecustomize.py").write_bytes(
            guard_source(forbidden, run.directory / "execution-guard.jsonl").encode()
        )
        write_state(
            run.directory / "source-manifest.json",
            {"commit_sha": sha, "committed_files": files, "derived_scan_only_fixture": derived},
        )
        with self.lock:
            run.value.update(source_sha=sha, source_mode="IMMUTABLE HEAD SNAPSHOT", fixture=derived)
        return snapshot, guard, sha

    def _environment(self, run, snapshot, guard):
        temporary = run.directory / "temp"
        temporary.mkdir(exist_ok=True)
        env = {k: os.environ[k] for k in ("SYSTEMROOT", "WINDIR") if k in os.environ}
        env.update(
            PATH=os.pathsep.join((str(Path(sys.executable).parent), str(Path(self.git).parent))),
            TEMP=str(temporary),
            TMP=str(temporary),
            PYTHONPATH=os.pathsep.join((str(guard), str(snapshot / "src"))),
            PYTHONNOUSERSITE="1",
            PYTHONSAFEPATH="1",
            PYTHONUTF8="1",
            PYTHONIOENCODING="utf-8",
            PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_GLOBAL=os.devnull,
        )
        return env

    def _terminate(self, process):
        if process.poll() is not None:
            return
        if os.name == "nt":
            killer = Path(os.environ["SYSTEMROOT"]) / "System32" / "taskkill.exe"
            result = subprocess.run(
                [str(killer), "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                timeout=10,
                check=False,
            )
            if result.returncode and process.poll() is None:
                self.closing = True
                raise LiveError("Owned process-tree shutdown failed; service disabled")
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        process.wait(timeout=5)

    def _process(self, run, label, command, *, snapshot, env):
        logs = run.directory / "logs"
        logs.mkdir(exist_ok=True)
        record = {"step": label, "command": command, "started_at": utc_now(), "pid": None}
        started = time.monotonic()
        process = None
        with self.lock:
            run.value["processes"].append(record)
        with (logs / f"{label}.stdout.txt").open("xb") as stdout:
            with (logs / f"{label}.stderr.txt").open("xb") as stderr:
                try:
                    if run.cancel.is_set():
                        raise LiveError("Verification cancelled")
                    process = subprocess.Popen(
                        command,
                        cwd=snapshot,
                        env=env,
                        stdin=subprocess.DEVNULL,
                        stdout=stdout,
                        stderr=stderr,
                        start_new_session=os.name != "nt",
                        creationflags=(
                            subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
                        ),
                    )
                    record["pid"] = process.pid
                    record["termination"] = None
                    while process.poll() is None:
                        reason = None
                        if run.cancel.is_set():
                            reason = "cancelled"
                        elif time.monotonic() - started > self.process_timeout:
                            reason = "timeout"
                        elif stdout.tell() + stderr.tell() > 2 * 1024 * 1024:
                            reason = "output_limit"
                        if reason:
                            record["termination"] = reason
                            self._terminate(process)
                            break
                        run.cancel.wait(0.05)
                    record["exit_code"] = process.wait(timeout=5)
                except OSError as exc:
                    record.update(exit_code=None, error=type(exc).__name__)
                    stderr.write((redact(str(exc), root=self.root) + "\n").encode())
                finally:
                    if process is not None and process.poll() is None:
                        self._terminate(process)
                    record.update(
                        finished_at=utc_now(), duration_seconds=round(time.monotonic() - started, 3)
                    )
        write_state(run.directory / "processes.json", run.value["processes"])
        return record

    def _artifact_list(self, run):
        result = []
        for key, name in ARTIFACTS.items():
            path = safe_path(run.directory, run.directory / name)
            if path.is_file():
                raw = path.read_bytes()
                if len(raw) <= MAX_REPORT_BYTES:
                    result.append(
                        {
                            "key": key,
                            "path": name,
                            "bytes": len(raw),
                            "sha256": hashlib.sha256(raw).hexdigest(),
                        }
                    )
        return result

    def _execute(self, run):
        failure = None
        try:
            snapshot, guard, sha = self._snapshot(run)
            env = self._environment(run, snapshot, guard)
            steps = (
                ("tests", ["run-check", "tests", "--sha", sha]),
                ("security", ["run-check", "security", "--sha", sha]),
                ("policy", ["evaluate", "--sha", sha, "--target", "staging"]),
                ("report", ["report", "--sha", sha, "--target", "staging"]),
            )
            for label, arguments in steps:
                if run.cancel.is_set():
                    raise LiveError("Verification cancelled")
                if label == "policy":
                    self._event(run, "collecting")
                self._event(run, label)
                record = self._process(
                    run,
                    label,
                    [sys.executable, "-c", CLI_BOOTSTRAP, *arguments],
                    snapshot=snapshot,
                    env=env,
                )
                if record.get("termination") or record.get("exit_code") not in (0, 1):
                    cause = record.get("termination") or record.get("error") or "process failed"
                    failure = f"{label}: {cause}"
            report = read_json(snapshot / "evidence" / "review" / "report.json")
            decision = report["decision"]
            if decision["execution_authorized"] is not False:
                raise LiveError("Execution boundary validation failed")
            events = [
                json.loads(line)
                for line in (run.directory / "execution-guard.jsonl")
                .read_text("utf-8")
                .splitlines()
            ]
            if any(e["event"] not in {"activated", "run_module", "spawn_check"} for e in events):
                raise LiveError("Scan-only fixture execution was attempted and blocked")
            for process in run.value["processes"]:
                # Windows venv python.exe is a redirector; its child is the real interpreter.
                process["python_pid"] = activated_interpreter(events, process)
                if process["step"] in {"tests", "security"}:
                    module = "pytest" if process["step"] == "tests" else "bandit"
                    spawned = any(
                        e["event"] == "spawn_check"
                        and e["pid"] == process["python_pid"]
                        and e["module"] == module
                        for e in events
                    )
                    entered = [
                        e
                        for e in events
                        if e["event"] == "run_module"
                        and e["module"] == module
                        and process["started_at"] <= e["at"] <= process["finished_at"]
                    ]
                    if not spawned or len(entered) != 1:
                        raise LiveError("Actual inner check process was not confirmed")
                    process["inner_check_pid"] = entered[0]["pid"]
            write_state(run.directory / "processes.json", run.value["processes"])
            if run.value["operation"] == "security_rejection" and (
                decision["decision"] != "DENY" or "SECURITY_HIGH" not in decision["reasons"]
            ):
                failure = "Controlled security rejection did not produce SECURITY_HIGH / DENY"
            with self.lock:
                run.value["result"] = {
                    k: report[k]
                    for k in (
                        "decision",
                        "tests",
                        "security",
                        "mandatory_tests",
                        "provenance",
                        "evidence_status",
                    )
                }
                run.value["guard_verified"] = True
                run.value["inner_processes"] = events
            self._finish(run, "failed" if failure else "completed", failure)
        except Exception as exc:
            error = (
                str(exc)
                if isinstance(exc, LiveError)
                else f"Verification interrupted: {type(exc).__name__}"
            )
            self._finish(run, "cancelled" if run.cancel.is_set() else "failed", error)
        finally:
            with self.lock:
                if self.active == run.directory.name:
                    self.active = None

    def _finish(self, run, status, error):
        with self.lock:
            run.value.update(
                status=status,
                error=error,
                finished_at=utc_now(),
                duration_seconds=round(time.monotonic() - run.started, 3),
                artifacts=self._artifact_list(run),
            )
            self._event(run, status)

    def artifact(self, run_id, key):
        self.get(run_id)
        if key not in ARTIFACTS:
            raise KeyError("Artifact not found")
        run = self.runs[run_id]
        path = safe_path(run.directory, run.directory / ARTIFACTS[key])
        if not path.is_file() or path.stat().st_size > MAX_REPORT_BYTES:
            raise KeyError("Artifact is unavailable")
        raw = path.read_bytes()
        text = redact(raw.decode("utf-8", errors="replace"), root=self.root)
        return {
            "key": key,
            "original_sha256": hashlib.sha256(raw).hexdigest(),
            "original_bytes": len(raw),
            "sanitized_view_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "sanitized": text.encode() != raw,
            "text": text,
        }


class LiveServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, manager, port):
        self.manager = manager
        super().__init__(("127.0.0.1", port), LiveHandler)
        self.origin = f"http://127.0.0.1:{self.server_address[1]}"


class LiveHandler(BaseHTTPRequestHandler):
    server_version = "ReleaseGateLocal"

    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, *_arguments):
        pass

    def _reply(self, code, data, content_type="application/json; charset=utf-8"):
        if not isinstance(data, bytes):
            data = json.dumps(data, allow_nan=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
            "connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
        )
        self.end_headers()
        self.wfile.write(data)

    def _boundary(self, *, mutation=False):
        hosts = self.headers.get_all("Host", [])
        origins = self.headers.get_all("Origin", [])
        if (
            self.client_address[0] != "127.0.0.1"
            or hosts != [self.server.origin.removeprefix("http://")]
            or len(origins) > 1
            or (origins and origins != [self.server.origin])
            or self.headers.get("Sec-Fetch-Site", "none") not in {"none", "same-origin"}
            or (mutation and origins != [self.server.origin])
            or (mutation and self.headers.get("X-ReleaseGate-Request") != "live-console")
        ):
            self._reply(403, {"error": "Use this console on its exact 127.0.0.1 origin"})
            return False
        return True

    def _path(self):
        parts = urlsplit(self.path)
        if parts.query or parts.fragment or "%" in parts.path or len(parts.path) > 200:
            raise KeyError("Unknown route")
        return parts.path

    def do_OPTIONS(self):
        self._reply(405, {"error": "Cross-origin access is not enabled"})

    def do_GET(self):
        if not self._boundary():
            return
        try:
            path = self._path()
            files = {
                "/": (ASSETS / "index.html", "text/html; charset=utf-8"),
                "/assets/live.css": (ASSETS / "live.css", "text/css; charset=utf-8"),
                "/assets/live.js": (ASSETS / "live.js", "text/javascript; charset=utf-8"),
                "/assets/base.css": (
                    self.server.manager.root / "frontend/assets/console.css",
                    "text/css; charset=utf-8",
                ),
                "/assets/mark.svg": (
                    self.server.manager.root / "frontend/assets/mark.svg",
                    "image/svg+xml",
                ),
            }
            if path in files:
                file, content_type = files[path]
                self._reply(200, file.read_bytes(), content_type)
            elif path == "/api/session":
                manager = self.server.manager
                self._reply(
                    200,
                    {
                        "session_id": manager.session_id,
                        "started_at": manager.session_started_at,
                        "source_sha": manager.head(),
                        "active_run_id": manager.active,
                        "operations": sorted(OPERATIONS),
                        "production_execution": "DISABLED",
                        "human_approval": "REQUIRED / UNEXECUTED",
                    },
                )
            elif match := re.fullmatch(r"/api/runs/([a-f0-9-]+)", path):
                self._reply(200, self.server.manager.get(match[1]))
            elif match := re.fullmatch(r"/api/runs/([a-f0-9-]+)/artifacts/([a-z-]+)", path):
                self._reply(200, self.server.manager.artifact(*match.groups()))
            else:
                raise KeyError("Unknown route")
        except (KeyError, ValueError):
            self._reply(404, {"error": "Run, route or artifact not found"})
        except (OSError, subprocess.SubprocessError):
            self._reply(503, {"error": "Local repository or artifact is unavailable"})

    def do_POST(self):
        if not self._boundary(mutation=True):
            return
        try:
            lengths = self.headers.get_all("Content-Length", [])
            if self.headers.get("Transfer-Encoding") or len(lengths) != 1:
                raise ValueError("A bounded JSON request is required")
            length = int(lengths[0])
            if not 1 <= length <= 256 or self.headers.get("Content-Type") != "application/json":
                raise ValueError("A small application/json request is required")

            def unique_object(pairs):
                value = dict(pairs)
                if len(value) != len(pairs):
                    raise ValueError("Duplicate request key")
                return value

            value = json.loads(self.rfile.read(length), object_pairs_hook=unique_object)
            if type(value) is not dict:
                raise ValueError("Expected an operation object")
            path = self._path()
            if path == "/api/runs":
                if (
                    set(value) != {"operation"}
                    or type(value["operation"]) is not str
                    or value["operation"] not in OPERATIONS
                ):
                    raise ValueError("Choose a supported verification operation")
                run_id = self.server.manager.start(value["operation"])
                self._reply(202, {"run_id": run_id})
            elif match := re.fullmatch(r"/api/runs/([a-f0-9-]+)/cancel", path):
                if value or not valid_id(match[1]):
                    raise ValueError("Cancellation accepts only the exact active Run ID")
                self.server.manager.cancel(match[1])
                self._reply(202, {"run_id": match[1], "cancel_requested": True})
            else:
                raise KeyError("Unknown operation route")
        except LiveError as exc:
            self._reply(409, {"error": str(exc)})
        except (ValueError, TypeError, UnicodeError):
            self._reply(
                400, {"error": "Invalid verification request; no commands or paths accepted"}
            )
        except KeyError:
            self._reply(404, {"error": "Unknown operation route"})
        except TimeoutError:
            self._reply(408, {"error": "Verification request body was not received in time"})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8776)
    args = parser.parse_args(argv)
    if not 1024 <= args.port <= 65535:
        parser.error("Choose a local port between 1024 and 65535")
    manager = LiveManager(Path.cwd())
    server = LiveServer(manager, args.port)
    print(f"ReleaseGate Live Verification Console: {server.origin}/", flush=True)
    print(
        "Local verification enabled. Production execution DISABLED. Human Gate UNEXECUTED.",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        manager.close()
        server.server_close()


if __name__ == "__main__":
    main()
