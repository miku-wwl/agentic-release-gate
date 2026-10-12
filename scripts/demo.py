"""Run real local checks in isolated snapshots; the unsafe fixture is scanned, never executed."""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from releasegate.evidence import read_json, write_json

ROOT = Path(__file__).resolve().parents[1]


def command(arguments, root, env, records, *, expected):
    env = {**env, "PYTHONPATH": str(root / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "releasegate", *arguments],
        cwd=root,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=300,
    )
    records.append(
        {
            "command": ["python", "-m", "releasegate", *arguments],
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    )
    if result.returncode != expected:
        raise RuntimeError(f"Unexpected exit {result.returncode}: {result.stdout} {result.stderr}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".artifacts" / "demo")
    args = parser.parse_args()
    directory = args.output_dir.resolve() / str(uuid4())
    directory.mkdir(parents=True, exist_ok=False)
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    env = os.environ.copy()
    # These runs are local snapshots, including when demonstrated inside CI.
    for name in ("GITLAB_CI", "CI_PROJECT_ID", "CI_PIPELINE_ID", "CI_COMMIT_SHA"):
        env.pop(name, None)
    results = {}
    records = []
    for scenario in ("allow", "deny"):
        root = directory / scenario
        root.mkdir()
        for folder in ("src", "tests", ".gitlab"):
            shutil.copytree(
                ROOT / folder, root / folder, ignore=shutil.ignore_patterns("__pycache__")
            )
        for name in ("pyproject.toml", ".gitlab-ci.yml", "uv.lock"):
            shutil.copy2(ROOT / name, root / name)
        if scenario == "deny":
            # Scanner fixture only: not imported by the product or tests.
            (root / "src" / "unsafe_scanner_fixture.py").write_text(
                "import subprocess\n\ndef unsafe_example(value):\n"
                '    return subprocess.run("echo " + value, shell=True, check=True)\n',
                encoding="utf-8",
            )
        command(["run-check", "tests", "--sha", sha], root, env, records, expected=0)
        command(
            ["run-check", "security", "--sha", sha],
            root,
            env,
            records,
            expected=0 if scenario == "allow" else 1,
        )
        command(
            ["evaluate", "--sha", sha, "--target", "staging"],
            root,
            env,
            records,
            expected=0 if scenario == "allow" else 1,
        )
        results[scenario] = read_json(root / "evidence" / "decision.json")
    if results["allow"]["next_gate"] != "HUMAN_APPROVAL":
        raise RuntimeError("ALLOW did not stop at human approval")
    if "SECURITY_HIGH" not in results["deny"]["reasons"]:
        raise RuntimeError("Real scanner finding did not produce DENY")
    command(
        [
            "evaluate",
            "--sha",
            sha,
            "--target",
            "production",
            "--gate",
            "final",
            "--output",
            "evidence/production-deny.json",
        ],
        directory / "allow",
        env,
        records,
        expected=1,
    )
    command(["release"], directory / "allow", env, records, expected=3)
    summary = {
        "origin": "local-working-tree",
        "gitlab_duo": "NOT VERIFIED",
        "gitlab_pipeline": "NOT RUN",
        "deployment": "NOT RUN",
        "commit_sha": sha,
        "snapshots_include_uncommitted_changes": True,
        "decisions": results,
        "commands": records,
    }
    write_json(directory / "verification.json", summary)
    print(
        json.dumps(
            {
                "verification": str(directory / "verification.json"),
                "allow": results["allow"]["decision"],
                "deny": results["deny"]["decision"],
                "gitlab_duo": "NOT VERIFIED",
                "deployment": "NOT RUN",
            }
        )
    )


if __name__ == "__main__":
    main()
