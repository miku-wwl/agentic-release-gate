import pytest

from releasegate.policy import digest


@pytest.fixture
def sha():
    return "a" * 40


@pytest.fixture
def evidence(sha):
    context = {
        "origin": "local-working-tree",
        "project_id": "",
        "pipeline_id": "",
        "source_digest": digest({"fixture": "unit-test-only"}),
    }
    checks = {}
    for kind, tool, raw in (
        ("tests", "pytest", "tests.junit.xml"),
        ("security", "bandit", "security.bandit.json"),
    ):
        checks[kind] = {
            "kind": kind,
            "commit_sha": sha,
            "context": context.copy(),
            "tool": tool,
            "tool_version": "unit-fixture",
            "command": [tool],
            "exit_code": 0,
            "raw_file": raw,
            "raw_sha256": "b" * 64,
            "summary": (
                {
                    "total": 2,
                    "passed": 2,
                    "failed": 0,
                    "errors": 0,
                    "skipped": 0,
                    "case_ids": ["fixture::required_one", "fixture::required_two"],
                }
                if kind == "tests"
                else {"scanned_files": 1, "findings": []}
            ),
        }
    return {"schema_version": 1, "checks": checks}
