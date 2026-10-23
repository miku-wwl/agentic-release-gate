import copy
import json

import pytest

from releasegate.advisory import advisory_summary, load_advisory, validate_advisory
from releasegate.evidence import EvidenceError

BASE = "https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43343080/showcase"


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema_version", True),
        ("review_source", "invented"),
        ("project_id", 87602765),
        ("project_url", "https://user:secret@gitlab.com/a/b"),
        ("mr_iid", True),
        ("session_url", "https://other.example/9451709"),
        ("reviewed_sha", "main"),
        ("review_timestamp", "2026-10-14"),
        ("finding", ""),
        ("finding_url", BASE + "/-/merge_requests/2#note_4012466889"),
        ("verification_status", "VERIFIED"),
        ("verification_reference", "docs/../secret.md"),
        ("limitations", []),
        ("correction", {"actor": "Codex", "sha": "a" * 40}),
    ],
)
def test_advisory_rejects_unsupported_values(advisory, field, value):
    advisory[field] = value
    with pytest.raises(EvidenceError):
        validate_advisory(advisory)


@pytest.mark.parametrize("field", ["approval", "verified_human", "execution_authorized", "token"])
def test_advisory_cannot_supply_authority(advisory, field):
    advisory[field] = True
    with pytest.raises(EvidenceError, match="UNSUPPORTED_ADVISORY_FIELDS"):
        validate_advisory(advisory)


def test_historical_revision_and_correction_actor_are_preserved(advisory, sha):
    original = copy.deepcopy(advisory)
    result = advisory_summary(advisory, candidate_sha=sha)
    assert result["reviewed_candidate"] is False
    assert result["status"] == "HISTORICAL_EVIDENCE"
    assert result["ingestion"] == "OFFLINE_REFERENCE_ONLY"
    assert result["review"] == original
    assert result["review"]["correction"]["actor"] == "Codex"
    assert advisory_summary(None, candidate_sha=sha) == {
        "status": "NOT_VERIFIED",
        "available": False,
        "review": None,
    }


@pytest.mark.parametrize("raw", [b'{"schema_version":1,"schema_version":1}', b'{"x":NaN}', b"[]"])
def test_advisory_rejects_ambiguous_json(tmp_path, raw):
    path = tmp_path / "advisory.json"
    path.write_bytes(raw)
    with pytest.raises(EvidenceError):
        load_advisory(path, root=tmp_path)


def test_advisory_bounds_and_credentials(tmp_path, advisory):
    path = tmp_path / "advisory.json"
    path.write_bytes(b" " * (64 * 1024 + 1))
    with pytest.raises(EvidenceError, match="TOO_LARGE"):
        load_advisory(path, root=tmp_path)
    advisory["recommendation"] = "Bearer " + "x" * 30
    path.write_text(json.dumps(advisory), encoding="utf-8")
    with pytest.raises(EvidenceError, match="CREDENTIAL_LIKE"):
        load_advisory(path, root=tmp_path)


def test_advisory_input_cannot_escape_workspace(tmp_path):
    with pytest.raises(EvidenceError, match="OUTSIDE_WORKSPACE"):
        load_advisory(tmp_path / "../private.json", root=tmp_path)


@pytest.mark.parametrize(
    "field,value",
    [
        ("reviewed_sha", "a" * 40),
        ("session_id", "99999"),
        ("review_timestamp", "2026-10-24T00:00:00Z"),
    ],
)
def test_historical_session_cannot_be_relabelled(advisory, field, value):
    advisory[field] = value
    if field == "session_id":
        advisory["session_url"] = BASE + "/-/automate/agent-sessions/99999"
    with pytest.raises(EvidenceError, match="HISTORICAL_IDENTITY_MISMATCH"):
        validate_advisory(advisory)
