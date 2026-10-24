"""Frontend safety and integrity checks, separate from the unchanged mandatory 139."""

import hashlib
import importlib.util
import json
import os
import shutil
import stat
from html.parser import HTMLParser
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("console_build", ROOT / "frontend/build_console.py")
console = importlib.util.module_from_spec(spec)
spec.loader.exec_module(console)


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    destination = tmp_path_factory.mktemp("console") / "site"
    console.build(destination)
    return destination


def data():
    return [
        console.load_json(ROOT / name)
        for name in (
            "frontend/data/checkpoint.json",
            "docs/phase4/examples/complete/report.json",
            "docs/phase4/examples/high_security/report.json",
            "docs/phase4/evidence/research-results.json",
            "tests/required-tests.json",
        )
    ]


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.nodes = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))


def test_pages_links_semantics_and_read_only_surface(site):
    for page in console.PAGES:
        text = (site / page).read_text(encoding="utf-8")
        doc = Document(text)
        assert sum(tag == "h1" for tag, _ in doc.nodes) == 1
        assert sum(tag == "main" for tag, _ in doc.nodes) == 1
        ids = [attrs["id"] for _, attrs in doc.nodes if "id" in attrs]
        assert len(ids) == len(set(ids))
        assert not any(
            tag in {"iframe", "form", "input", "object", "embed"} for tag, _ in doc.nodes
        )
        assert not any(key.startswith("on") for _, attrs in doc.nodes for key in attrs)
        assert sum(attrs.get("aria-current") == "page" for _, attrs in doc.nodes) == 1
        assert all("src" in attrs for tag, attrs in doc.nodes if tag == "script")
        assert "execution_authorized=false" in text and "Production disabled" in text
        for _tag, attrs in doc.nodes:
            for key in ("href", "src"):
                value = attrs.get(key, "")
                if value and not value.startswith(("#", "https://")):
                    assert (site / value).is_file(), (page, value)
                if value.startswith("https://"):
                    assert console.safe_url(value) == value
                    assert attrs.get("rel") == "noopener noreferrer"


def test_csp_forbids_connections_forms_and_inline_script(site):
    for page in console.PAGES:
        doc = Document((site / page).read_text(encoding="utf-8"))
        csp = next(
            a["content"]
            for tag, a in doc.nodes
            if tag == "meta" and a.get("http-equiv") == "Content-Security-Policy"
        )
        assert "connect-src 'none'" in csp and "form-action 'none'" in csp
        assert "script-src 'self'" in csp and "unsafe-inline" not in csp


def test_positive_negative_fixtures_cannot_be_confused(site):
    text = (site / "decision-explorer.html").read_text(encoding="utf-8")
    assert text.count("Recorded local experiment") == 2
    assert text.count("DEMO FIXTURE") == 4
    assert "SECURITY_HIGH" in text and "HUMAN_APPROVAL" in text
    assert 'data-case-panel="positive"' in text and 'data-case-panel="negative"' in text
    pos = json.loads((site / "evidence/positive-report.json").read_text())
    neg = json.loads((site / "evidence/negative-report.json").read_text())
    assert pos["decision"]["decision"] == "ALLOW"
    assert neg["decision"]["decision"] == "DENY"
    assert pos["decision"]["execution_authorized"] is False
    assert neg["decision"]["execution_authorized"] is False


def test_xss_strings_are_text_not_nodes_or_attributes():
    cp, pos, neg, research, required = data()
    attack = '<img src=x onerror="alert(1)"><script>alert(2)</script>&'
    pos["decision"]["reasons"] = [attack]
    pos["security"]["findings"][0]["file"] = attack
    pos["required_next_action"] = attack
    # Even fields normally holding numbers must be escaped before rendering.
    pos["tests"]["passed"] = attack
    pos["tests"]["total"] = attack
    pos["security"]["scanned_files"] = attack
    rendered = console.case_panel(pos, "positive")
    assert attack not in rendered and "&lt;script&gt;" in rendered
    assert not any(
        tag in {"script", "img"} or "onerror" in attrs for tag, attrs in Document(rendered).nodes
    )
    assert console.esc('" onclick="attack') == "&quot; onclick=&quot;attack"


@pytest.mark.parametrize(
    "url",
    [
        "javascript:alert(1)",
        "data:text/html,unsafe",
        "http://gitlab.com/a",
        "https://gitlab.com.evil.example/a",
        "https://user:secret@gitlab.com/a",
        console.LAB + '/x" onclick="unsafe',
        console.LAB + "/x\nunsafe",
        "https://github.com/other/project",
        console.LAB + ":443/path",
    ],
)
def test_unreviewed_links_are_rejected(url):
    with pytest.raises(ValueError):
        console.safe_url(url)


@pytest.mark.parametrize("payload", ['{"x":1,"x":2}', '{"x":NaN}', "[]"])
def test_malformed_json_rejected(tmp_path, payload):
    path = tmp_path / "input.json"
    path.write_text(payload, encoding="utf-8")
    with pytest.raises(ValueError):
        console.load_json(path)


@pytest.mark.parametrize(
    "index,field,value",
    [
        (0, "human_gate_executed", True),
        (0, "production_execution", "ENABLED"),
        (0, "pipeline_status", "success"),
    ],
)
def test_unsafe_checkpoint_not_rendered(index, field, value):
    values = data()
    values[index][field] = value
    with pytest.raises(ValueError):
        console.validate_data(*values)


def test_execution_claim_and_research_metric_tampering_rejected():
    values = data()
    values[1]["decision"]["execution_authorized"] = True
    with pytest.raises(ValueError):
        console.validate_data(*values)
    values = data()
    values[3]["metrics"]["false_allow"] = False
    with pytest.raises(ValueError):
        console.validate_data(*values)
    values = data()
    values[3]["results"][0]["trial"] = 2
    with pytest.raises(ValueError):
        console.validate_data(*values)


def test_build_is_reproducible_and_manifest_matches_all_bytes(site, tmp_path):
    second = tmp_path / "second"
    console.build(second)
    assert {p.relative_to(site) for p in site.rglob("*") if p.is_file()} == {
        p.relative_to(second) for p in second.rglob("*") if p.is_file()
    }
    for path in site.rglob("*"):
        if path.is_file():
            assert path.read_bytes() == (second / path.relative_to(site)).read_bytes()
    manifest = json.loads((site / "build-manifest.json").read_text())
    for path, expected in manifest["files"].items():
        assert hashlib.sha256((site / path).read_bytes()).hexdigest() == expected
    with pytest.raises(ValueError):
        console.build(site)


def test_published_research_and_fixture_hashes_are_binding(tmp_path):
    root = tmp_path / "bad-source"
    for name in ("docs", "tests", "frontend"):
        import shutil

        shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns("__pycache__"))
    path = root / "docs/phase4/evidence/research-results.json"
    research = json.loads(path.read_text())
    research["metrics"]["false_allow"] = 9
    path.write_text(json.dumps(research))
    with pytest.raises(ValueError, match="hash mismatch"):
        console.build(tmp_path / "bad-build", root=root)


def test_research_and_audit_are_bounded_and_historical(site):
    research = (site / "research.html").read_text(encoding="utf-8")
    assert research.count('class="row-index"') == 14
    assert "100% production reliability" in research and "not a production guarantee" in research
    audit = (site / "audit-trail.html").read_text(encoding="utf-8")
    assert "not a live agent run" in audit and "Codex implemented" in audit
    assert "Supervised: NOT_VERIFIED" in audit


def test_pages_deployment_config_is_inert_and_validation_has_no_uploads():
    root_ci = yaml.safe_load((ROOT / ".gitlab-ci.yml").read_text())
    assert root_ci["include"] == [{"local": ".gitlab/ci/console-validate.yml"}]
    validate = yaml.safe_load((ROOT / ".gitlab/ci/console-validate.yml").read_text())
    assert all("pages" not in job and "artifacts" not in job for job in validate.values())
    deploy = yaml.safe_load((ROOT / ".gitlab/pages.console.yml").read_text())
    job = deploy["console_pages"]
    assert job["pages"]["publish"] == "dist/console"
    assert job["rules"][0]["when"] == "manual"
    assert "$RELEASEGATE_PAGES_APPROVED_SHA == $CI_COMMIT_SHA" in job["rules"][0]["if"]
    assert job["rules"][-1] == {"when": "never"}


def test_original_mandatory_manifest_is_unchanged():
    # Exact LF blob at bc5e410f; no git binary needed in the slim CI image.
    expected = "43e36e2ec937c00bf8fa66990611a3f9731430f7a2b09ebfb9d55224b6fd27ac"
    assert (
        hashlib.sha256(console.source_bytes(ROOT, "tests/required-tests.json")).hexdigest()
        == expected
    )


def test_client_has_no_execution_or_html_injection_sinks():
    source = (ROOT / "frontend/assets/console.js").read_text(encoding="utf-8")
    for sink in (
        "innerHTML",
        "outerHTML",
        "insertAdjacentHTML",
        "eval(",
        "fetch(",
        "XMLHttpRequest",
        "WebSocket",
        "sendBeacon",
        "document.write",
        "localStorage",
    ):
        assert sink not in source
    assert "textContent" in source


@pytest.fixture
def asset_root(tmp_path):
    root = tmp_path / "source"
    shutil.copytree(ROOT / "frontend/assets", root / "frontend/assets")
    return root


def create_test_symlink(link, target, monkeypatch):
    """Use real links in CI; Windows without privilege tests OS-link metadata."""
    try:
        link.symlink_to(target, target_is_directory=target.is_dir())
    except OSError as exc:
        if os.name != "nt" or getattr(exc, "winerror", None) != 1314:
            raise
        # Do not enable Developer Mode or weaken OS settings to create test links.
        if target.is_dir():
            link.mkdir()
        else:
            link.write_text("not copied", encoding="utf-8")
        original = Path.lstat

        def link_metadata(path, *args, **kwargs):
            result = original(path, *args, **kwargs)
            if path == link:
                fields = list(result)
                fields[stat.ST_MODE] = stat.S_IFLNK | 0o777
                return os.stat_result(fields)
            return result

        monkeypatch.setattr(Path, "lstat", link_metadata)
    assert link.is_symlink()


def test_only_reviewed_assets_are_copied_and_manifested(site):
    expected = {"console.css", "console.js", "mark.svg"}
    assert set(console.STATIC_ASSETS) == expected
    assert {p.name for p in (site / "assets").iterdir()} == expected
    manifest = json.loads((site / "build-manifest.json").read_text())
    assert {p for p in manifest["inputs"] if p.startswith("frontend/assets/")} == {
        "frontend/assets/" + name for name in expected
    }


@pytest.mark.parametrize("name", ["extra.js", "console.css.map", "unreviewed.svg"])
def test_unknown_asset_file_rejects_build_before_output(asset_root, tmp_path, name):
    (asset_root / "frontend/assets" / name).write_text("unreviewed", encoding="utf-8")
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="Unknown static asset"):
        console.build(output, root=asset_root)
    assert not output.exists()


def test_unknown_asset_directory_is_rejected(asset_root, tmp_path):
    (asset_root / "frontend/assets/nested").mkdir()
    with pytest.raises(ValueError, match="Unknown static asset"):
        console.build(tmp_path / "output", root=asset_root)


@pytest.mark.parametrize("name", ["console.css", "console.js", "mark.svg"])
def test_missing_required_asset_is_rejected(asset_root, tmp_path, name):
    (asset_root / "frontend/assets" / name).unlink()
    with pytest.raises(ValueError, match="Required static asset is missing"):
        console.build(tmp_path / "output", root=asset_root)


def test_approved_asset_name_cannot_be_directory(asset_root, tmp_path):
    path = asset_root / "frontend/assets/console.js"
    path.unlink()
    path.mkdir()
    with pytest.raises(ValueError, match="regular file"):
        console.build(tmp_path / "output", root=asset_root)


@pytest.mark.parametrize("name", ["console.css", "console.js", "mark.svg"])
def test_approved_asset_symlink_is_rejected(asset_root, tmp_path, monkeypatch, name):
    external = tmp_path / "external.txt"
    external.write_text("must not enter output", encoding="utf-8")
    path = asset_root / "frontend/assets" / name
    path.unlink()
    create_test_symlink(path, external, monkeypatch)
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="must not be a symlink"):
        console.build(output, root=asset_root)
    assert not output.exists()


def test_asset_directory_symlink_is_rejected(tmp_path, monkeypatch):
    root = tmp_path / "source"
    (root / "frontend").mkdir(parents=True)
    target = tmp_path / "external-assets"
    target.mkdir()
    create_test_symlink(root / "frontend/assets", target, monkeypatch)
    output = tmp_path / "output"
    with pytest.raises(ValueError, match="directory must not be a symlink"):
        console.build(output, root=root)
    assert not output.exists()
