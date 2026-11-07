"""Tests for skills/_lib/optimize.py shared optimize utilities."""
from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
_MODULE_PATH = REPO_ROOT / "skills" / "_lib" / "optimize.py"


def _load():
    spec = importlib.util.spec_from_file_location("catalyst_lib_optimize", _MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


optimize = _load()
Finding = optimize.Finding


def _make_finding(**overrides):
    base = dict(
        rule_id="R001",
        severity="warning",
        target="path/to/file.sql",
        message="msg",
        suggestion="do x",
        before=None,
        after=None,
    )
    base.update(overrides)
    return Finding(**base)


def test_finding_dict_roundtrip():
    f = _make_finding(before="a", after="b")
    d = asdict(f)
    assert d["rule_id"] == "R001"
    assert d["severity"] == "warning"
    assert d["before"] == "a"
    assert d["after"] == "b"
    assert d["applied"] is False
    # roundtrip
    f2 = Finding(**d)
    assert f2 == f


def test_format_text_covers_all_findings():
    findings = [
        _make_finding(rule_id="R001", message="first"),
        _make_finding(rule_id="R002", message="second"),
    ]
    out = optimize.format_text(findings)
    assert isinstance(out, str) and out
    assert "R001" in out and "R002" in out
    assert "first" in out and "second" in out


def test_format_json_is_parseable_list():
    findings = [_make_finding(rule_id="R001"), _make_finding(rule_id="R002")]
    raw = optimize.format_json(findings)
    parsed = json.loads(raw)
    assert isinstance(parsed, list)
    assert len(parsed) == 2
    assert parsed[0]["rule_id"] == "R001"


def test_apply_finding_rewrites_file_when_before_present(tmp_path):
    target = tmp_path / "model.sql"
    target.write_text("select * from foo")
    f = _make_finding(target=str(target), before="foo", after="bar")
    assert optimize.apply_finding(f) is True
    assert target.read_text() == "select * from bar"


def test_apply_finding_returns_false_when_before_missing(tmp_path):
    target = tmp_path / "model.sql"
    target.write_text("select * from foo")
    f = _make_finding(target=str(target), before="zzz", after="qqq")
    assert optimize.apply_finding(f) is False
    assert target.read_text() == "select * from foo"
    assert f.applied is False


def test_apply_finding_dry_run_does_not_modify(tmp_path):
    target = tmp_path / "model.sql"
    target.write_text("select * from foo")
    f = _make_finding(target=str(target), before="foo", after="bar")
    assert optimize.apply_finding(f, dry_run=True) is True
    assert target.read_text() == "select * from foo"
    assert f.applied is False


def test_apply_finding_sets_applied_on_real_write(tmp_path):
    target = tmp_path / "model.sql"
    target.write_text("hello world")
    f = _make_finding(target=str(target), before="world", after="there")
    assert optimize.apply_finding(f) is True
    assert f.applied is True


def test_redact_tokens_scrubs_bearer():
    out = optimize.redact_tokens("Authorization: Bearer abc.def-123_XYZ")
    assert "abc.def-123_XYZ" not in out
    assert "Bearer" not in out or "***" in out


def test_redact_tokens_scrubs_dapi_and_dsapi():
    out = optimize.redact_tokens("token=dapi0123456789abcdef0123 other=dsapiabcdef0123456789ab")
    assert "dapi0123456789abcdef0123" not in out
    assert "dsapiabcdef0123456789ab" not in out


def test_redact_tokens_preserves_git_sha():
    sha = "a" * 40
    out = optimize.redact_tokens(f"commit {sha}")
    assert sha in out


def test_parse_mode_report():
    assert optimize.parse_mode("report") == (False, False)


def test_parse_mode_apply():
    assert optimize.parse_mode("apply") == (True, False)


def test_parse_mode_dry_run():
    assert optimize.parse_mode("dry-run") == (False, True)


def test_parse_mode_unknown_raises():
    with pytest.raises(ValueError):
        optimize.parse_mode("bogus")
