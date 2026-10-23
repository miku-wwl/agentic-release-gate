from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_ci_preserves_failed_artifacts_and_blocking_review():
    ci = yaml.safe_load((ROOT / ".gitlab-ci.yml").read_text("utf-8"))
    for job in ("tests", "security", "release_policy", "evidence_bundle"):
        assert ci[job]["artifacts"]["when"] == "always"
    assert ci["release_policy"]["when"] == "always"
    rule = ci["review_release_candidate"]["rules"][0]
    assert rule["when"] == "manual" and rule["allow_failure"] is False
    assert "CI_COMMIT_REF_PROTECTED" in rule["if"]
    assert "environment" not in ci["review_release_candidate"]


def test_duo_flow_uses_documented_read_only_configuration():
    flow = yaml.safe_load((ROOT / ".gitlab/duo/flows/release-risk.yaml").read_text("utf-8"))
    assert flow["version"] == "v1" and flow["environment"] == "ambient"
    assert not set(flow) & {"name", "description", "product_group"}
    component = flow["components"][0]
    assert component["type"] == "AgentComponent"
    assert set(component["toolset"]) == {
        "get_merge_request",
        "list_merge_request_diffs",
        "get_repository_file",
        "get_job_logs",
        "gitlab_api_get",
    }
    assert "response_schema_id" not in component
    assert flow["flow"]["entry_point"] == component["name"]
    assert flow["routers"] == [{"from": component["name"], "to": "end"}]
    assert flow["prompts"][0]["prompt_id"] == component["prompt_id"]


def test_research_and_reports_supplement_required_checks():
    ci = yaml.safe_load((ROOT / ".gitlab-ci.yml").read_text("utf-8"))
    research = ci["research_evaluation"]
    assert research["when"] == "always"
    assert research["artifacts"]["when"] == "always"
    assert research["dependencies"] == []
    assert "scripts/evaluate_scenarios.py --trials 3" in research["script"][0]
    assert any("releasegate report" in cmd for cmd in ci["evidence_bundle"]["script"])
    assert "run-check tests" in ci["tests"]["script"][0]
    assert "run-check security" in ci["security"]["script"][0]
    assert all("environment" not in value for value in ci.values() if isinstance(value, dict))
