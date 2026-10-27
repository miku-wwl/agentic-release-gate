"""Record the exact, credential-free Docker build candidate subset."""

import argparse
import hashlib
import json
import re
from pathlib import Path


def build(root, sha, output):
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("An immutable source commit is required")
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("Linked candidate files are prohibited")
        name = path.relative_to(root).as_posix()
        if any(
            part in {".git", ".venv", ".artifacts", "__pycache__"} or part.startswith(".env")
            for part in path.relative_to(root).parts
        ):
            raise ValueError("Private or generated candidate path")
        if path.is_file():
            raw = path.read_bytes()
            files[name] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    if sum(item["bytes"] for item in files.values()) > 16 * 1024 * 1024 or len(files) > 200:
        raise ValueError("Candidate exceeds its build bounds")
    value = {
        "schema_version": 1,
        "candidate_sha": sha,
        "scope": "TRUSTED_PACKAGED_VERIFICATION_SUBSET",
        "files": files,
    }
    output.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", "utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.root, args.sha, args.output)
