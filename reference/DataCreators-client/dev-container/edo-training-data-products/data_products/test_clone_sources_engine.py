"""Unit tests for the clone-sources engine."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / ".devcontainer"
    / "clone_tools"
    / "clone_sources_engine.py"
)


def _load_clone_engine_module():
    spec = importlib.util.spec_from_file_location("clone_sources_engine", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import module from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


clone_engine = _load_clone_engine_module()


class FakeCursor:
    def __init__(self):
        self.executed_sql: list[str] = []

    def execute(self, sql: str):
        self.executed_sql.append(sql)

    def fetchone(self):
        return None

    def fetchall(self):
        return []


class FakeConnection:
    def __init__(self):
        self.cursors: list[FakeCursor] = []

    def cursor(self):
        cursor = FakeCursor()
        self.cursors.append(cursor)
        return cursor


class FakeConnectionContext:
    def __init__(self, conn: FakeConnection):
        self.conn = conn

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeCursorWithResult(FakeCursor):
    """FakeCursor whose fetchone/fetchall return caller-supplied data."""

    def __init__(self, fetchone_result=None, fetchall_result=None):
        super().__init__()
        self._fetchone_result = fetchone_result
        self._fetchall_result = fetchall_result or []

    def fetchone(self):
        return self._fetchone_result

    def fetchall(self):
        return self._fetchall_result


class FakeConnectionWithResult(FakeConnection):
    """FakeConnection that seeds every cursor with the provided return values."""

    def __init__(self, fetchone_result=None, fetchall_result=None):
        super().__init__()
        self._fetchone_result = fetchone_result
        self._fetchall_result = fetchall_result or []

    def cursor(self):
        cursor = FakeCursorWithResult(self._fetchone_result, self._fetchall_result)
        self.cursors.append(cursor)
        return cursor


def test_get_http_path_raises_when_explicit_profile_missing(tmp_path, monkeypatch):
    """Ensure requesting a missing Databricks profile raises an explicit error."""
    cfg_path = tmp_path / ".databrickscfg"
    cfg_path.write_text("[DEFAULT]\nhttp_path = /sql/1.0/warehouses/default\n", encoding="utf-8")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("DATABRICKS_HTTP_PATH", raising=False)

    with pytest.raises(EnvironmentError, match="requested but not found"):
        clone_engine._get_http_path("MISSING")


def test_clone_table_materializes_view_as_table(monkeypatch):
    """Verify a source VIEW is cloned into a materialized target TABLE."""
    conn = FakeConnection()

    monkeypatch.setattr(clone_engine, "table_exists", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(clone_engine, "get_table_type", lambda *_args, **_kwargs: "VIEW")
    monkeypatch.setattr(clone_engine, "is_delta_table", lambda *_args, **_kwargs: False)

    ok = clone_engine.clone_table(
        conn,
        source_catalog="src_cat",
        source_schema="src_schema",
        source_table="src_view",
        target_catalog="tgt_cat",
        target_schema="tgt_schema",
    )

    assert ok is True
    sql = conn.cursors[-1].executed_sql[-1]
    assert "CREATE OR REPLACE TABLE" in sql
    assert " AS SELECT * FROM " in sql
    assert "CREATE OR REPLACE VIEW" not in sql


def test_clone_product_sources_continues_after_source_failure(monkeypatch):
    """Confirm cloning continues and counts successes when one source clone fails."""
    conn = FakeConnection()

    monkeypatch.setattr(
        clone_engine,
        "discover_sources",
        lambda _product_dir: [
            {"database": "cat", "schema": "sch", "name": "bad_table"},
            {"database": "cat", "schema": "sch", "name": "good_table"},
        ],
    )
    monkeypatch.setattr(clone_engine, "create_schema_if_not_exists", lambda *_args, **_kwargs: None)

    def fake_clone_table(_conn, _sc, _ss, table, _tc, _ts):
        if table == "bad_table":
            raise RuntimeError("clone failed")
        return True

    monkeypatch.setattr(clone_engine, "clone_table", fake_clone_table)

    success_count = clone_engine.clone_product_sources(conn, Path("/tmp/product"), "namespace", "target_cat")
    assert success_count == 1


def test_cleanup_only_targets_expected_schemas(monkeypatch):
    """Check cleanup drops only namespace-prefixed schemas discovered from sources."""
    conn = FakeConnection()

    monkeypatch.setattr(clone_engine, "discover_data_products", lambda: [Path("/tmp/product")])
    monkeypatch.setattr(
        clone_engine,
        "discover_sources",
        lambda _product_dir: [
            {"database": "catalog_a", "schema": "schema_one", "name": "table1"},
            {"database": "catalog_b", "schema": "schema_two", "name": "table2"},
        ],
    )
    monkeypatch.setattr(clone_engine, "get_databricks_connection", lambda _profile=None: FakeConnectionContext(conn))
    monkeypatch.setattr(clone_engine, "resolve_clone_namespace", lambda _conn: "user_ns")
    monkeypatch.setattr(clone_engine, "resolve_workspace_default_catalog", lambda _conn: "target_catalog")
    monkeypatch.setattr(clone_engine, "schema_exists", lambda *_args, **_kwargs: True)

    clone_engine.cleanup()

    all_sql = [sql for cursor in conn.cursors for sql in cursor.executed_sql]
    drop_sql = [sql for sql in all_sql if sql.startswith("DROP SCHEMA IF EXISTS")]

    assert len(drop_sql) == 2
    assert any("`target_catalog`.`user_ns__schema_one`" in sql for sql in drop_sql)
    assert any("`target_catalog`.`user_ns__schema_two`" in sql for sql in drop_sql)


def test_get_http_path_uses_explicit_profile_when_present(tmp_path, monkeypatch):
    """Ensure HTTP path is read from the explicitly requested Databricks profile."""
    cfg_path = tmp_path / ".databrickscfg"
    cfg_path.write_text(
        "[DEFAULT]\nhttp_path = /sql/1.0/warehouses/default\n"
        "[MY_PROFILE]\nhttp_path = /sql/1.0/warehouses/profile\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("DATABRICKS_HTTP_PATH", raising=False)

    assert clone_engine._get_http_path("MY_PROFILE") == "/sql/1.0/warehouses/profile"


# ---------------------------------------------------------------------------
# configure_logging
# ---------------------------------------------------------------------------

def test_configure_logging_sets_debug_when_verbose():
    """configure_logging(True) switches the module logger to DEBUG level."""
    import logging
    clone_engine.configure_logging(verbose=True)
    assert clone_engine.logger.level == logging.DEBUG
    clone_engine.configure_logging(verbose=False)  # restore to INFO


def test_configure_logging_sets_info_when_not_verbose():
    """configure_logging(False) sets the module logger to INFO level."""
    import logging
    clone_engine.configure_logging(verbose=False)
    assert clone_engine.logger.level == logging.INFO


# ---------------------------------------------------------------------------
# SQL helpers
# ---------------------------------------------------------------------------

def test_sql_string_literal_wraps_and_escapes_quotes():
    """sql_string_literal wraps a value in single quotes and doubles embedded quotes."""
    assert clone_engine.sql_string_literal("hello") == "'hello'"
    assert clone_engine.sql_string_literal("it's") == "'it''s'"


def test_sql_string_literal_rejects_null_byte():
    """sql_string_literal raises ValueError when the value contains a null byte."""
    with pytest.raises(ValueError, match="null byte"):
        clone_engine.sql_string_literal("bad\x00string")


def test_sanitize_branch_name_raises_on_degenerate_input():
    """sanitize_branch_name raises ValueError when the result sanitizes to an empty string."""
    with pytest.raises(ValueError, match="sanitizes to empty string"):
        clone_engine.sanitize_branch_name("---")


def test_build_clone_source_schema_combines_namespace_and_schema():
    """build_clone_source_schema joins namespace and schema with a double-underscore."""
    result = clone_engine.build_clone_source_schema("alice", "raw_orders")
    assert result == "alice__raw_orders"


# ---------------------------------------------------------------------------
# _tail_lines
# ---------------------------------------------------------------------------

def test_tail_lines_returns_last_n_lines(tmp_path):
    """_tail_lines returns the last max_lines lines from an existing file."""
    log = tmp_path / "dbt.log"
    log.write_text("\n".join(str(i) for i in range(50)), encoding="utf-8")
    tail = clone_engine._tail_lines(log, max_lines=5)
    lines = tail.splitlines()
    assert lines[-1] == "49"
    assert len(lines) == 5


def test_tail_lines_returns_empty_for_missing_file(tmp_path):
    """_tail_lines returns an empty string when the target file does not exist."""
    assert clone_engine._tail_lines(tmp_path / "nonexistent.log") == ""


# ---------------------------------------------------------------------------
# _extract_dbt_failure_summary
# ---------------------------------------------------------------------------

def test_extract_dbt_failure_summary_identifies_missing_env_var():
    """_extract_dbt_failure_summary highlights missing required env vars from dbt output."""
    stderr = "Env var required but not provided: 'DBT_WAREHOUSE'"
    result = clone_engine._extract_dbt_failure_summary(stderr=stderr, stdout="")
    assert "DBT_WAREHOUSE" in result


def test_extract_dbt_failure_summary_falls_back_to_last_line():
    """_extract_dbt_failure_summary returns the last non-empty line for generic errors."""
    result = clone_engine._extract_dbt_failure_summary(stderr="", stdout="line1\nline2\nfinal error")
    assert result == "final error"


def test_extract_dbt_failure_summary_handles_empty_output():
    """_extract_dbt_failure_summary returns a safe message when dbt produces no output."""
    result = clone_engine._extract_dbt_failure_summary(stderr="", stdout="")
    assert "No dbt" in result


# ---------------------------------------------------------------------------
# _load_manifest_sources
# ---------------------------------------------------------------------------

def test_load_manifest_sources_returns_empty_when_no_manifest(tmp_path):
    """_load_manifest_sources returns an empty dict when manifest.json is absent."""
    assert clone_engine._load_manifest_sources(tmp_path) == {}


def test_load_manifest_sources_parses_source_nodes(tmp_path):
    """_load_manifest_sources extracts database, schema, and identifier from manifest sources."""
    import json

    target = tmp_path / "target"
    target.mkdir()
    manifest = {
        "sources": {
            "source.proj.mysrc.tbl": {
                "database": "my_catalog",
                "schema": "my_schema",
                "name": "tbl",
                "identifier": "tbl_physical",
            }
        }
    }
    (target / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    result = clone_engine._load_manifest_sources(tmp_path)
    assert result["source.proj.mysrc.tbl"]["database"] == "my_catalog"
    assert result["source.proj.mysrc.tbl"]["identifier"] == "tbl_physical"


# ---------------------------------------------------------------------------
# Databricks SQL operations (fully in-process with fakes)
# ---------------------------------------------------------------------------

def test_table_exists_returns_true_when_info_schema_returns_truthy():
    """table_exists returns True when the information_schema query yields a truthy result."""
    conn = FakeConnectionWithResult(fetchone_result=(True,))
    assert clone_engine.table_exists(conn, "cat", "sch", "tbl") is True


def test_table_exists_returns_false_when_no_row():
    """table_exists returns False when fetchone returns None."""
    conn = FakeConnectionWithResult(fetchone_result=None)
    assert clone_engine.table_exists(conn, "cat", "sch", "tbl") is False


def test_get_table_type_returns_uppercased_type():
    """get_table_type uppercases the table_type column returned by information_schema."""
    conn = FakeConnectionWithResult(fetchone_result=("base table",))
    assert clone_engine.get_table_type(conn, "cat", "sch", "tbl") == "BASE TABLE"


def test_get_table_type_returns_unknown_on_empty_row():
    """get_table_type returns 'UNKNOWN' when information_schema returns no row."""
    conn = FakeConnectionWithResult(fetchone_result=None)
    assert clone_engine.get_table_type(conn, "cat", "sch", "tbl") == "UNKNOWN"


def test_is_delta_table_returns_true_when_provider_is_delta():
    """is_delta_table returns True when DESCRIBE TABLE EXTENDED shows Provider=delta."""
    conn = FakeConnectionWithResult(fetchall_result=[("Provider", "delta", ""), ("Format", "parquet", "")])
    assert clone_engine.is_delta_table(conn, "cat", "sch", "tbl") is True


def test_is_delta_table_returns_false_when_no_provider_row():
    """is_delta_table returns False when DESCRIBE TABLE EXTENDED has no Provider row."""
    conn = FakeConnectionWithResult(fetchall_result=[("Format", "parquet", "")])
    assert clone_engine.is_delta_table(conn, "cat", "sch", "tbl") is False


def test_create_schema_if_not_exists_executes_correct_sql():
    """create_schema_if_not_exists runs a quoted CREATE SCHEMA IF NOT EXISTS statement."""
    conn = FakeConnection()
    clone_engine.create_schema_if_not_exists(conn, "cat", "my_schema")
    sql = conn.cursors[0].executed_sql[0]
    assert "CREATE SCHEMA IF NOT EXISTS" in sql
    assert "`cat`" in sql
    assert "`my_schema`" in sql


def test_schema_exists_returns_true_when_found():
    """schema_exists returns True when the schemata query returns a truthy row."""
    conn = FakeConnectionWithResult(fetchone_result=(True,))
    assert clone_engine.schema_exists(conn, "cat", "sch") is True


def test_schema_exists_returns_false_when_not_found():
    """schema_exists returns False when the schemata query returns None."""
    conn = FakeConnectionWithResult(fetchone_result=None)
    assert clone_engine.schema_exists(conn, "cat", "sch") is False


def test_get_current_databricks_principal_returns_principal():
    """get_current_databricks_principal returns the trimmed current_user() value."""
    conn = FakeConnectionWithResult(fetchone_result=("alice@example.com",))
    assert clone_engine.get_current_databricks_principal(conn) == "alice@example.com"


def test_get_current_databricks_principal_raises_when_empty():
    """get_current_databricks_principal raises RuntimeError when current_user() is blank."""
    conn = FakeConnectionWithResult(fetchone_result=(None,))
    with pytest.raises(RuntimeError, match="Could not resolve"):
        clone_engine.get_current_databricks_principal(conn)


def test_resolve_workspace_default_catalog_returns_catalog():
    """resolve_workspace_default_catalog returns current_catalog() when it is a UC catalog."""
    conn = FakeConnectionWithResult(fetchone_result=("main_dev",))
    assert clone_engine.resolve_workspace_default_catalog(conn) == "main_dev"


def test_resolve_workspace_default_catalog_raises_when_empty():
    """resolve_workspace_default_catalog raises when current_catalog() is empty."""
    conn = FakeConnectionWithResult(fetchone_result=(None,))
    with pytest.raises(RuntimeError, match="default catalog"):
        clone_engine.resolve_workspace_default_catalog(conn)


def test_resolve_workspace_default_catalog_raises_for_hive_metastore():
    """resolve_workspace_default_catalog raises for hive_metastore default target."""
    conn = FakeConnectionWithResult(fetchone_result=("hive_metastore",))
    with pytest.raises(RuntimeError, match="hive_metastore"):
        clone_engine.resolve_workspace_default_catalog(conn)


# ---------------------------------------------------------------------------
# clone_product_sources edge cases
# ---------------------------------------------------------------------------

def test_clone_product_sources_returns_zero_when_no_sources(monkeypatch):
    """clone_product_sources returns 0 without errors when dbt ls returns no source nodes."""
    conn = FakeConnection()
    monkeypatch.setattr(clone_engine, "discover_sources", lambda _: [])
    assert clone_engine.clone_product_sources(conn, Path("/tmp/product"), "ns", "target_cat") == 0


def test_clone_product_sources_returns_zero_on_dbt_ls_failure(monkeypatch):
    """clone_product_sources returns 0 and logs an error when dbt ls raises RuntimeError."""
    conn = FakeConnection()

    def _raise(_dir):
        raise RuntimeError("dbt ls failed")

    monkeypatch.setattr(clone_engine, "discover_sources", _raise)
    assert clone_engine.clone_product_sources(conn, Path("/tmp/product"), "ns", "target_cat") == 0


def test_clone_product_sources_skips_sources_with_missing_fields(monkeypatch):
    """clone_product_sources skips and doesn't count sources that lack database/schema/name."""
    conn = FakeConnection()
    monkeypatch.setattr(clone_engine, "discover_sources", lambda _: [{"name": "tbl"}])
    monkeypatch.setattr(clone_engine, "create_schema_if_not_exists", lambda *_a, **_k: None)
    monkeypatch.setattr(clone_engine, "clone_table", lambda *_a, **_k: True)
    assert clone_engine.clone_product_sources(conn, Path("/tmp/product"), "ns", "target_cat") == 0


def test_clone_product_sources_uses_provided_target_catalog(monkeypatch):
    """clone_product_sources should always target the explicitly resolved catalog."""
    conn = FakeConnection()
    monkeypatch.setattr(
        clone_engine,
        "discover_sources",
        lambda _: [{"database": "source_catalog", "schema": "src_schema", "name": "tbl"}],
    )

    observed = {}

    def fake_create_schema_if_not_exists(_conn, catalog, schema):
        observed["catalog"] = catalog
        observed["schema"] = schema

    def fake_clone_table(_conn, source_catalog, source_schema, source_table, target_catalog, target_schema):
        observed["source_catalog"] = source_catalog
        observed["target_catalog"] = target_catalog
        observed["target_schema"] = target_schema
        return True

    monkeypatch.setattr(clone_engine, "create_schema_if_not_exists", fake_create_schema_if_not_exists)
    monkeypatch.setattr(clone_engine, "clone_table", fake_clone_table)

    success = clone_engine.clone_product_sources(conn, Path("/tmp/product"), "ns", "workspace_default")

    assert success == 1
    assert observed["source_catalog"] == "source_catalog"
    assert observed["catalog"] == "workspace_default"
    assert observed["target_catalog"] == "workspace_default"


# ---------------------------------------------------------------------------
# main() additional branches
# ---------------------------------------------------------------------------

def test_main_cleanup_path_calls_cleanup_and_returns_zero(monkeypatch):
    """main calls cleanup() when --cleanup is set and returns exit code 0."""
    called = {}
    monkeypatch.setattr(
        clone_engine.argparse.ArgumentParser,
        "parse_args",
        lambda _self: type("Args", (), {"cleanup": True, "databricks_profile": None, "verbose": False})(),
    )
    monkeypatch.setattr(clone_engine, "configure_logging", lambda _v: None)
    monkeypatch.setattr(clone_engine, "cleanup", lambda profile=None: called.__setitem__("done", True))
    assert clone_engine.main() == 0
    assert called.get("done") is True


def test_main_returns_one_on_environment_error(monkeypatch):
    """main returns exit code 1 when clone_all raises an EnvironmentError."""
    monkeypatch.setattr(
        clone_engine.argparse.ArgumentParser,
        "parse_args",
        lambda _self: type("Args", (), {"cleanup": False, "databricks_profile": None, "verbose": False})(),
    )
    monkeypatch.setattr(clone_engine, "configure_logging", lambda _v: None)

    def _raise_env_error(_profile=None):
        raise EnvironmentError("auth failed")

    monkeypatch.setattr(clone_engine, "clone_all", _raise_env_error)
    assert clone_engine.main() == 1


def test_main_returns_one_on_import_error(monkeypatch):
    """main returns exit code 1 when a missing Databricks library causes ImportError."""
    monkeypatch.setattr(
        clone_engine.argparse.ArgumentParser,
        "parse_args",
        lambda _self: type("Args", (), {"cleanup": False, "databricks_profile": None, "verbose": False})(),
    )
    monkeypatch.setattr(clone_engine, "configure_logging", lambda _v: None)

    def _raise_import_error(_profile=None):
        err = ImportError("No module named 'databricks'")
        err.name = "databricks"
        raise err

    monkeypatch.setattr(clone_engine, "clone_all", _raise_import_error)
    assert clone_engine.main() == 1


def test_clone_table_returns_false_when_source_is_missing(monkeypatch):
    """Ensure clone_table returns False and executes no SQL when source is absent."""
    conn = FakeConnection()

    monkeypatch.setattr(clone_engine, "table_exists", lambda *_args, **_kwargs: False)

    ok = clone_engine.clone_table(
        conn,
        source_catalog="src_cat",
        source_schema="src_schema",
        source_table="missing_table",
        target_catalog="tgt_cat",
        target_schema="tgt_schema",
    )

    assert ok is False
    assert conn.cursors == []


def test_clone_table_uses_shallow_clone_for_delta_tables(monkeypatch):
    """Verify clone_table uses SHALLOW CLONE when source table provider is Delta."""
    conn = FakeConnection()

    monkeypatch.setattr(clone_engine, "table_exists", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(clone_engine, "get_table_type", lambda *_args, **_kwargs: "BASE TABLE")
    monkeypatch.setattr(clone_engine, "is_delta_table", lambda *_args, **_kwargs: True)

    ok = clone_engine.clone_table(
        conn,
        source_catalog="src_cat",
        source_schema="src_schema",
        source_table="src_delta",
        target_catalog="tgt_cat",
        target_schema="tgt_schema",
    )

    assert ok is True
    sql = conn.cursors[-1].executed_sql[-1]
    assert "SHALLOW CLONE" in sql


def test_namespace_helpers_sanitize_and_extract_principal_prefix():
    """Check branch/principal normalization into safe schema namespace segments."""
    assert clone_engine.sanitize_branch_name("feature/my-branch.v1") == "feature_my_branch_v1"
    assert clone_engine.extract_clone_namespace_from_principal("alice.smith@example.com") == "alice_smith"


def test_quote_identifier_part_escapes_backticks_and_rejects_empty():
    """Validate SQL identifier quoting and rejection of blank identifier parts."""
    assert clone_engine._quote_identifier_part("a`b") == "`a``b`"
    with pytest.raises(ValueError, match="cannot be empty"):
        clone_engine._quote_identifier_part("   ")


def test_main_returns_zero_for_clone_flow(monkeypatch):
    """Ensure main returns 0 and forwards profile in the non-cleanup clone path."""
    seen = {"profile": None, "verbose": None}

    monkeypatch.setattr(
        clone_engine.argparse.ArgumentParser,
        "parse_args",
        lambda _self: type(
            "Args",
            (),
            {"cleanup": False, "databricks_profile": "MY_PROFILE", "verbose": True},
        )(),
    )
    monkeypatch.setattr(
        clone_engine,
        "configure_logging",
        lambda verbose: seen.__setitem__("verbose", verbose),
    )
    monkeypatch.setattr(
        clone_engine,
        "clone_all",
        lambda profile=None: seen.__setitem__("profile", profile) or 1,
    )

    assert clone_engine.main() == 0
    assert seen["profile"] == "MY_PROFILE"
    assert seen["verbose"] is True


def test_main_returns_one_on_called_process_error(monkeypatch):
    """Ensure main maps subprocess command failures to a non-zero exit code."""
    monkeypatch.setattr(
        clone_engine.argparse.ArgumentParser,
        "parse_args",
        lambda _self: type(
            "Args",
            (),
            {"cleanup": False, "databricks_profile": None, "verbose": False},
        )(),
    )
    monkeypatch.setattr(clone_engine, "configure_logging", lambda _verbose: None)

    def _raise_called_process_error(_profile=None):
        raise subprocess.CalledProcessError(2, ["dbt", "ls"], stderr="boom")

    monkeypatch.setattr(clone_engine, "clone_all", _raise_called_process_error)

    assert clone_engine.main() == 1
