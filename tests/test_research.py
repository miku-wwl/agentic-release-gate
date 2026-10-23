import importlib.util
import os
from pathlib import Path

import pytest

from releasegate.evidence import context_for


def test_research_metrics_count_false_decisions_and_detections():
    spec = importlib.util.spec_from_file_location(
        "evaluation", Path(__file__).resolve().parents[1] / "scripts/evaluate_scenarios.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = [
        {
            "scenario": name,
            "expected": expected,
            "observed": observed,
            "correct": expected == observed,
            "mode": mode,
            "duration_seconds": seconds,
        }
        for name, expected, observed, mode, seconds in (
            ("positive", "ALLOW", "ALLOW", "CLI_EVIDENCE", 1),
            ("missed", "DENY", "ALLOW", "CLI_EVIDENCE", 2),
            ("false_deny", "ALLOW", "DENY", "POLICY_ONLY", 3),
            ("closed", "DENY", "DENY", "POLICY_ONLY", 4),
        )
    ]
    metrics = module.metrics(rows)
    assert metrics["total_scenarios"] == 4 and metrics["trials_executed"] == 4
    assert metrics["expected_allow"] == 2 and metrics["expected_deny"] == 2
    assert metrics["correct_decisions"] == 2
    assert metrics["false_allow"] == 1 and metrics["false_deny"] == 1
    assert metrics["fail_closed_detection_rate"] == 0.5
    assert metrics["cli_latency_seconds"] == {
        "n": 2,
        "min": 1,
        "median": 1.5,
        "max": 2,
        "mean": 1.5,
    }


@pytest.mark.parametrize("interrupted", [False, True])
def test_snapshot_policy_loads_use_local_context_and_restore_host(monkeypatch, interrupted):
    spec = importlib.util.spec_from_file_location(
        "evaluation", Path(__file__).resolve().parents[1] / "scripts/evaluate_scenarios.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setenv("GITLAB_CI", "true")
    monkeypatch.setenv("CI_PROJECT_ID", "87602765")
    monkeypatch.setenv("CI_PIPELINE_ID", "123")
    try:
        with module.local_snapshot_environment() as host:
            assert host["GITLAB_CI"] == "true"
            assert (
                context_for(Path(__file__).resolve().parents[1])["origin"] == "local-working-tree"
            )
            if interrupted:
                raise RuntimeError("interruption fixture")
    except RuntimeError:
        assert interrupted
    assert os.environ["GITLAB_CI"] == "true"
    assert os.environ["CI_PIPELINE_ID"] == "123"
