import argparse
import json
from pathlib import Path

from releasegate.evidence import (
    EvidenceError,
    load_evidence,
    load_required_tests,
    run_check,
    write_json,
)
from releasegate.policy import Decision, evaluate
from releasegate.reporting import build_report, write_report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="ReleaseGate: evidence policy, no deployment")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("run-check", help="Run actual tests or static security checks")
    check.add_argument("kind", choices=("tests", "security"))
    check.add_argument("--sha", required=True)
    check.add_argument("--evidence-dir", type=Path, default=Path("evidence"))
    assess = commands.add_parser("evaluate", help="ALLOW means eligible for the next gate")
    assess.add_argument("--sha", required=True)
    assess.add_argument("--target", choices=("staging", "production"), required=True)
    assess.add_argument("--gate", choices=("eligibility", "final"), default="eligibility")
    assess.add_argument("--evidence-dir", type=Path, default=Path("evidence"))
    assess.add_argument("--output", type=Path, default=Path("evidence/decision.json"))
    report = commands.add_parser("report", help="Revalidate evidence and present human review")
    report.add_argument("--sha", required=True)
    report.add_argument("--target", choices=("staging", "production"), required=True)
    report.add_argument("--gate", choices=("eligibility", "final"), default="eligibility")
    report.add_argument("--evidence-dir", type=Path, default=Path("evidence"))
    report.add_argument("--advisory", type=Path)
    report.add_argument("--output-dir", type=Path, default=Path("evidence/review"))
    commands.add_parser("release", help="Fail closed: release executor is not configured")
    args = parser.parse_args(argv)
    if args.command == "release":
        print(
            json.dumps(
                {
                    "decision": "DENY",
                    "reasons": ["EXECUTION_NOT_CONFIGURED"],
                    "execution_authorized": False,
                    "runtime": "NOT_INTEGRATED",
                }
            )
        )
        return 3
    if args.command == "report":
        try:
            value = build_report(
                root=Path.cwd(),
                directory=args.evidence_dir,
                sha=args.sha,
                target=args.target,
                gate=args.gate,
                advisory_path=args.advisory,
            )
            write_report(args.output_dir, value)
        except (EvidenceError, OSError, ValueError, TypeError, KeyError):
            print(json.dumps({"decision": "DENY", "reasons": ["REPORT_INPUT_UNUSABLE"]}))
            return 2
        print(json.dumps(value["decision"], sort_keys=True))
        return 0 if value["decision"]["decision"] == "ALLOW" else 1
    try:
        if args.command == "run-check":
            result = run_check(
                args.kind,
                root=Path.cwd(),
                directory=args.evidence_dir.resolve(),
                commit_sha=args.sha,
            )
            print(
                json.dumps(
                    {
                        "kind": args.kind,
                        "exit_code": result["exit_code"],
                        "summary": result["summary"],
                    },
                    sort_keys=True,
                )
            )
            if args.kind == "security":
                findings = result["summary"]["findings"]
                if result["exit_code"] != (1 if findings else 0):
                    return 2
                return int(any(f["severity"] in {"HIGH", "CRITICAL"} for f in findings))
            return result["exit_code"] if result["exit_code"] in range(0, 6) else 2
        evidence = load_evidence(args.evidence_dir.resolve(), root=Path.cwd())
        # No JSON/env/LLM approval input. Production final gate requires a future trusted adapter.
        result = evaluate(
            evidence,
            expected_commit=args.sha,
            target=args.target,
            gate=args.gate,
            required_test_ids=load_required_tests(Path.cwd()),
        )
    except (EvidenceError, OSError, ValueError, TypeError, KeyError) as exc:
        if args.command == "run-check":
            print(
                json.dumps(
                    {
                        "decision": "DENY",
                        "reasons": ["CHECK_UNUSABLE"],
                        "error_type": type(exc).__name__,
                    }
                )
            )
            return 2
        reasons = (
            ("EVIDENCE_UNUSABLE", str(exc))
            if isinstance(exc, EvidenceError)
            else ("EVIDENCE_UNUSABLE", type(exc).__name__)
        )
        result = Decision("DENY", reasons, args.sha, args.target, args.gate, None, None)
    write_json(args.output, result.to_dict())
    print(json.dumps(result.to_dict(), sort_keys=True))
    return 0 if result.decision == "ALLOW" else 1
