import json

from releasegate.cli import main


def test_release_remains_closed_without_runtime(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["release"]) == 3
    result = json.loads(capsys.readouterr().out)
    assert result["execution_authorized"] is False
    assert result["reasons"] == ["EXECUTION_NOT_CONFIGURED"]
    assert list(tmp_path.iterdir()) == []


def test_missing_reports_emit_durable_deny(tmp_path, monkeypatch, sha, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "example.py").write_text("value = 1\n")
    assert main(["evaluate", "--sha", sha, "--target", "staging"]) == 1
    result = json.loads((tmp_path / "evidence" / "decision.json").read_text())
    assert result["decision"] == "DENY"
    assert "MISSING_SECURITY_EVIDENCE" in result["reasons"]
    assert json.loads(capsys.readouterr().out) == result
