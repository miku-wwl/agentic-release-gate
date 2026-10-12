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
