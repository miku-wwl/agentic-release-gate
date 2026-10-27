"""Exercise genuine public scenarios and abuse rejection; never supplies a command."""

import argparse
import hashlib
import json
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def verify(base, output):
    output.mkdir(parents=True, exist_ok=True)

    def request(path, body=None, expected=200):
        raw = json.dumps(body).encode() if body is not None else None
        req = Request(
            base + path, data=raw, headers={"Content-Type": "application/json", "Origin": base}
        )
        try:
            with urlopen(req, timeout=90) as reply:
                code, content = reply.status, reply.read()
                assert reply.headers["X-Content-Type-Options"] == "nosniff"
        except HTTPError as exc:
            code, content = exc.code, exc.read()
        assert code == expected, (path, code, content[:300])
        return json.loads(content)

    for path in (
        "/.env",
        "/.git/config",
        "/api/runs",
        "/api/deploy",
        "/api/approve",
        "/etc/passwd",
    ):
        request(path, expected=404)
    for bad in (
        {"scenario": "UNKNOWN"},
        {"scenario": "SECURITY_HIGH", "command": "id"},
        {"scenario": "../../private"},
    ):
        request("/api/demo/verifications", bad, expected=400)
    runs = []
    for scenario in ("POSITIVE_CANDIDATE", "SECURITY_HIGH"):
        while (metadata := request("/api/demo/scenarios"))["cooldown_remaining"] > 0:
            time.sleep(min(5, metadata["cooldown_remaining"] + 1))
        run = request("/api/demo/verifications", {"scenario": scenario}, expected=202)
        run_id = run["run_id"]
        request("/api/demo/verifications", {"scenario": scenario}, expected=409)
        deadline = time.monotonic() + 75
        while time.monotonic() < deadline:
            run = request("/api/demo/verifications/" + run_id)
            if run["status"] in {"COMPLETED", "FAILED", "TIMED_OUT"}:
                break
            time.sleep(1)
        assert run["status"] == "COMPLETED", run
        assert run["test_summary"]["passed"] == run["test_summary"]["total"] == 139
        assert run["mandatory_present"] == run["mandatory_required"] == 139
        assert run["test_summary"]["skipped"] == 0
        assert run["execution_authorized"] is False and run["human_gate_executed"] is False
        assert run["production_execution"] == "DISABLED"
        assert run["completed_at"] > run["started_at"] and run["duration_ms"] > 0
        if scenario == "POSITIVE_CANDIDATE":
            assert run["policy_decision"] == "ALLOW" and run["next_gate"] == "HUMAN_APPROVAL"
        else:
            assert run["policy_decision"] == "DENY" and "SECURITY_HIGH" in run["denial_reasons"]
            assert run["next_gate"] is None
        evidence = request(run["evidence"])
        assert evidence["evidence_digest"] == run["evidence_digest"]
        assert evidence["network_isolation"] == "LINUX_SECCOMP_NETWORK_DENIED"
        assert evidence["scan_only_fixture_executed"] is False
        assert [step["tool"] for step in evidence["actual_steps"]] == ["pytest", "bandit"]
        assert {
            event["module"]
            for event in evidence["execution_events"]
            if event["event"] == "run_module"
        } == {"pytest", "bandit"}
        for artifact in evidence["artifacts"].values():
            assert (
                hashlib.sha256(artifact["text"].encode()).hexdigest()
                == artifact["sanitized_view_sha256"]
            )
            if not artifact["sanitized"] and not artifact["truncated"]:
                assert artifact["sanitized_view_sha256"] == artifact["original_sha256"]
        if request("/api/demo/scenarios")["cooldown_remaining"] > 0:
            request("/api/demo/verifications", {"scenario": scenario}, expected=429)
        (output / f"{scenario}.json").write_text(
            json.dumps({"run": run, "evidence": evidence}, indent=2) + "\n", "utf-8"
        )
        runs.append(run)
    assert runs[0]["run_id"] != runs[1]["run_id"]
    assert runs[0]["started_at"] < runs[1]["started_at"]
    assert len(request("/api/demo/scenarios")["history"]) >= 2
    print(
        json.dumps(
            {
                "status": "PASS",
                "run_ids": [r["run_id"] for r in runs],
                "decisions": [r["policy_decision"] for r in runs],
                "tests_each": 139,
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    verify(args.base_url.rstrip("/"), args.output)
