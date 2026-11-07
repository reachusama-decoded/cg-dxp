"""Functional tests for the optimize-dbsql-query capability skill.

Loads optimize.py via importlib (skill dir uses a hyphen). All tests
run against in-memory SQL strings written to tmp files.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "skills" / "optimize-dbsql-query" / "scripts" / "optimize.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("optimize_dbsql_query", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def opt():
    return _load_script()


def _write(tmp_path: Path, name: str, sql: str) -> Path:
    p = tmp_path / name
    p.write_text(sql)
    return p


def test_report_mode_prints_findings(opt, tmp_path, capsys):
    f = _write(tmp_path, "a.sql", "SELECT * FROM big_table;")
    rc = opt.main(["--path", str(f), "--mode", "report"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "SQL-PERF-DBSQL-001" in out


def test_select_star_case_insensitive(opt, tmp_path):
    f = _write(tmp_path, "a.sql", "select   *   from events\n")
    findings = opt.scan_path(f)
    assert any(x.rule_id == "SQL-PERF-DBSQL-001" for x in findings)


def test_select_star_uppercase(opt, tmp_path):
    f = _write(tmp_path, "a.sql", "SELECT * FROM EVENTS\n")
    findings = opt.scan_path(f)
    assert any(x.rule_id == "SQL-PERF-DBSQL-001" for x in findings)


def test_cross_join_comma_detected(opt, tmp_path):
    sql = "SELECT a.id FROM orders a, customers b WHERE a.cid = b.id;"
    f = _write(tmp_path, "cj.sql", sql)
    findings = opt.scan_path(f)
    matches = [x for x in findings if x.rule_id == "SQL-PERF-DBSQL-002"]
    assert matches and matches[0].severity == "error"


def test_join_without_on_detected(opt, tmp_path):
    sql = "SELECT * FROM orders o JOIN customers c WHERE o.cid = c.id;"
    f = _write(tmp_path, "cj.sql", sql)
    findings = opt.scan_path(f)
    assert any(x.rule_id == "SQL-PERF-DBSQL-002" for x in findings)


def test_proper_join_with_on_not_flagged_as_cross(opt, tmp_path):
    sql = "SELECT o.id FROM orders o JOIN customers c ON o.cid = c.id;"
    f = _write(tmp_path, "ok.sql", sql)
    findings = opt.scan_path(f)
    assert not any(x.rule_id == "SQL-PERF-DBSQL-002" for x in findings)


def test_where_upper_flagged(opt, tmp_path):
    sql = "SELECT id FROM users WHERE UPPER(email) = 'X@Y.COM';"
    f = _write(tmp_path, "w.sql", sql)
    findings = opt.scan_path(f)
    matches = [x for x in findings if x.rule_id == "SQL-PERF-DBSQL-003"]
    assert matches
    assert "UPPER" in matches[0].message


def test_where_date_flagged(opt, tmp_path):
    sql = "SELECT id FROM events WHERE DATE(ts) = '2026-01-01';"
    f = _write(tmp_path, "w.sql", sql)
    findings = opt.scan_path(f)
    assert any(x.rule_id == "SQL-PERF-DBSQL-003" for x in findings)


def test_orderby_no_limit_in_subquery(opt, tmp_path):
    sql = "SELECT * FROM (SELECT id FROM events ORDER BY ts) t;"
    f = _write(tmp_path, "o.sql", sql)
    findings = opt.scan_path(f)
    assert any(x.rule_id == "SQL-PERF-DBSQL-004" for x in findings)


def test_orderby_with_limit_in_subquery_ok(opt, tmp_path):
    sql = "SELECT * FROM (SELECT id FROM events ORDER BY ts LIMIT 10) t;"
    f = _write(tmp_path, "o.sql", sql)
    findings = opt.scan_path(f)
    assert not any(x.rule_id == "SQL-PERF-DBSQL-004" for x in findings)


def test_create_delta_missing_cluster_by(opt, tmp_path):
    sql = "CREATE TABLE foo (id BIGINT) USING DELTA;"
    f = _write(tmp_path, "c.sql", sql)
    findings = opt.scan_path(f)
    assert any(x.rule_id == "SQL-PERF-DBSQL-005" for x in findings)


def test_create_delta_with_cluster_by_ok(opt, tmp_path):
    sql = "CREATE TABLE foo (id BIGINT) USING DELTA CLUSTER BY (id);"
    f = _write(tmp_path, "c.sql", sql)
    findings = opt.scan_path(f)
    assert not any(x.rule_id == "SQL-PERF-DBSQL-005" for x in findings)


def test_path_directory_recurses(opt, tmp_path):
    (tmp_path / "sub").mkdir()
    _write(tmp_path / "sub", "a.sql", "SELECT * FROM big;")
    _write(tmp_path, "b.sql", "SELECT * FROM big2;")
    findings = opt.scan_path(tmp_path)
    star = [x for x in findings if x.rule_id == "SQL-PERF-DBSQL-001"]
    assert len(star) == 2


def test_path_file_works(opt, tmp_path, capsys):
    f = _write(tmp_path, "a.sql", "SELECT * FROM t;")
    rc = opt.main(["--path", str(f)])
    assert rc == 0


def test_path_nonexistent_exit_2(opt, tmp_path, capsys):
    rc = opt.main(["--path", str(tmp_path / "missing.sql")])
    assert rc == 2
    err = capsys.readouterr().err
    assert "not found" in err


def test_json_format_valid_list(opt, tmp_path, capsys):
    f = _write(tmp_path, "a.sql", "SELECT * FROM t;")
    rc = opt.main(["--path", str(f), "--format", "json"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    data = json.loads(out)
    assert isinstance(data, list)
    assert any(d["rule_id"] == "SQL-PERF-DBSQL-001" for d in data)


def test_redact_tokens_wrapper_imported(opt):
    # Module re-exports redact_tokens from the shared lib; verify presence
    # and behavior (scrubs Bearer/dapi/dsapi-prefixed tokens).
    assert hasattr(opt, "redact_tokens")
    assert opt.redact_tokens("Authorization: Bearer abc123def456") == "Authorization: ***"
    assert opt.redact_tokens("token=dapi1234567890abcdefXYZ") == "token=***"
    assert opt.redact_tokens("plain text") == "plain text"


def test_dry_run_mode_succeeds(opt, tmp_path):
    f = _write(tmp_path, "a.sql", "SELECT * FROM t;")
    rc = opt.main(["--path", str(f), "--mode", "dry-run"])
    assert rc == 0


def test_apply_mode_succeeds(opt, tmp_path):
    f = _write(tmp_path, "a.sql", "SELECT * FROM t;")
    rc = opt.main(["--path", str(f), "--mode", "apply"])
    assert rc == 0
