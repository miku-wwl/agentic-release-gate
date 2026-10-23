"""Offline, reference-only Duo advice; no evaluation or approval path."""

import json
import re
from datetime import datetime
from pathlib import Path

from releasegate.evidence import EvidenceError, read_json
from releasegate.policy import SHA

MAX_ADVISORY_BYTES = 64 * 1024
PROJECT_URL = re.compile(r"https://gitlab\.com/(?:[A-Za-z0-9_-]+/)+[A-Za-z0-9_-]+")
# Reviewed source references, not authentication credentials. Extending this
# curated offline catalog requires code review and independent platform evidence.
HISTORICAL_REVIEW = {
    "project_id": "87602765",
    "project_url": "https://gitlab.com/gitlab-ai-hackathon/"
    "transcend-october-2026/43343080/showcase",
    "mr_iid": 1,
    "session_id": "9451709",
    "reviewed_sha": "4182deb55678382c0a99f7b1fd8e2232d17a0611",
    "review_timestamp": "2026-10-14T12:35:37.799Z",
}
SECRET = re.compile(
    r"glpat-[A-Za-z0-9_-]{10,}|gh[pousr]_[A-Za-z0-9]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|"
    r"Bearer\s+\S+|-----BEGIN [A-Z ]*PRIVATE KEY-----",
    re.IGNORECASE,
)


def confined(root: Path, path: Path) -> Path:
    """Inputs must stay inside the selected workspace, including symlink resolution."""
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise EvidenceError("INPUT_OUTSIDE_WORKSPACE")
    return resolved


def no_secrets(value: dict) -> None:
    if SECRET.search(json.dumps(value, ensure_ascii=False)):
        raise EvidenceError("CREDENTIAL_LIKE_CONTENT_REJECTED")


def _text(value, *, limit=4096) -> bool:
    return (
        type(value) is str
        and 1 <= len(value) <= limit
        and all(ord(c) >= 32 or c in "\n\t" for c in value)
    )


def _timestamp(value) -> bool:
    if not _text(value, limit=64):
        return False
    try:
        return datetime.fromisoformat(value).utcoffset() is not None
    except ValueError:
        return False


def validate_advisory(value: dict) -> dict:
    fields = {
        "schema_version",
        "review_source",
        "project_id",
        "project_url",
        "mr_iid",
        "session_id",
        "session_url",
        "reviewed_sha",
        "finding",
        "recommendation",
        "review_timestamp",
        "finding_url",
        "correction",
        "verification_status",
        "verification_reference",
        "limitations",
    }
    if type(value) is not dict or set(value) != fields:
        raise EvidenceError("UNSUPPORTED_ADVISORY_FIELDS")
    if (
        type(value["schema_version"]) is not int
        or value["schema_version"] != 1
        or value["review_source"] != "gitlab-duo-code-review"
        or not _text(value["project_id"], limit=20)
        or not value["project_id"].isdigit()
        or not _text(value["project_url"], limit=512)
        or not PROJECT_URL.fullmatch(value["project_url"])
        or type(value["mr_iid"]) is not int
        or not 1 <= value["mr_iid"] <= 10**9
        or not _text(value["session_id"], limit=20)
        or not value["session_id"].isdigit()
        or not _text(value["reviewed_sha"], limit=40)
        or not SHA.fullmatch(value["reviewed_sha"])
        or not _timestamp(value["review_timestamp"])
        or value["verification_status"] not in ("HISTORICAL_EVIDENCE", "NOT_VERIFIED")
        or not _text(value["finding"])
        or not _text(value["recommendation"])
        or not _text(value["verification_reference"], limit=512)
        or not re.fullmatch(r"docs/[A-Za-z0-9_./-]+\.md", value["verification_reference"])
        or ".." in value["verification_reference"].split("/")
        or type(value["limitations"]) is not list
        or not 1 <= len(value["limitations"]) <= 16
        or any(not _text(item) for item in value["limitations"])
    ):
        raise EvidenceError("MALFORMED_ADVISORY")
    base = value["project_url"]
    if (
        value["session_url"] != f"{base}/-/automate/agent-sessions/{value['session_id']}"
        or type(value["finding_url"]) is not str
        or not re.fullmatch(
            re.escape(f"{base}/-/merge_requests/{value['mr_iid']}#note_") + r"[0-9]+",
            value["finding_url"],
        )
    ):
        raise EvidenceError("ADVISORY_REFERENCE_MISMATCH")
    correction = value["correction"]
    if (
        type(correction) is not dict
        or set(correction) != {"actor", "sha", "reference"}
        or correction["actor"] not in ("Codex", "human", "GitLab Duo", "NOT_VERIFIED")
        or not _text(correction["sha"], limit=40)
        or not SHA.fullmatch(correction["sha"])
        or correction["reference"] != f"{base}/-/commit/{correction['sha']}"
    ):
        raise EvidenceError("MALFORMED_CORRECTION_ATTRIBUTION")
    known_session = value["session_id"] == HISTORICAL_REVIEW["session_id"]
    if known_session or value["verification_status"] == "HISTORICAL_EVIDENCE":
        if (
            any(value[key] != expected for key, expected in HISTORICAL_REVIEW.items())
            or correction["actor"] != "Codex"
            or correction["sha"] != "d05e8bb205a0411c5f7b5bc5c6fc68b0b367a7cf"
            or value["finding_url"] != f"{base}/-/merge_requests/1#note_4012466889"
        ):
            raise EvidenceError("HISTORICAL_IDENTITY_MISMATCH")
    no_secrets(value)
    # JSON copy prevents callers from subsequently mutating the accepted object in place.
    return json.loads(json.dumps(value))


def load_advisory(path: Path, *, root: Path) -> dict:
    path = confined(root, path)
    if path.stat().st_size > MAX_ADVISORY_BYTES:
        raise EvidenceError("ADVISORY_TOO_LARGE")
    return validate_advisory(read_json(path))


def advisory_summary(value: dict | None, *, candidate_sha: str) -> dict:
    if value is None:
        return {"status": "NOT_VERIFIED", "available": False, "review": None}
    review = validate_advisory(value)
    return {
        "status": review["verification_status"],
        "available": True,
        "ingestion": "OFFLINE_REFERENCE_ONLY",
        "reviewed_candidate": review["reviewed_sha"] == candidate_sha,
        "review": review,
        "authority": "ADVISORY_ONLY; no human identity or execution authorization",
    }
