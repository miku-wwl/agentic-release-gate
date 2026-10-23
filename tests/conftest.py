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


BASE = "https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase"


@pytest.fixture
def advisory():
    return {
        "schema_version": 1,
        "review_source": "gitlab-duo-code-review",
        "project_id": "87602765",
        "project_url": BASE,
        "mr_iid": 1,
        "session_id": "9451709",
        "session_url": BASE + "/-/automate/agent-sessions/9451709",
        "reviewed_sha": "4182deb55678382c0a99f7b1fd8e2232d17a0611",
        "finding": "git is unavailable in the slim CI image.",
        "recommendation": "Use validated CI_COMMIT_SHA in CI.",
        "finding_url": BASE + "/-/merge_requests/1#note_4012466889",
        "review_timestamp": "2026-10-14T12:35:37.799Z",
        "correction": {
            "actor": "Codex",
            "sha": "d05e8bb205a0411c5f7b5bc5c6fc68b0b367a7cf",
            "reference": BASE + "/-/commit/d05e8bb205a0411c5f7b5bc5c6fc68b0b367a7cf",
        },
        "verification_status": "HISTORICAL_EVIDENCE",
        "verification_reference": "docs/phase4/00-baseline-audit.md",
        "limitations": ["Historical review; offline reference-only ingestion."],
    }
