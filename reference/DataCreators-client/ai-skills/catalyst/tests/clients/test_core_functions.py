"""Unit tests for skills/core/ functions.

All tests are fully offline — no live Databricks, Confluence, or marketplace
connections are used.  Platform clients are replaced with MagicMock instances.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch, call

import pytest

from skills.core import (
    discover_tables,
    fetch_confluence_page,
    profile_table,
    search_marketplace,
    trace_lineage,
)


# ===========================================================================
# Helpers
# ===========================================================================


def _make_db_client(rows: list[list] | None = None) -> MagicMock:
    """Return a DatabricksClient mock that returns *rows* for any execute_sql call."""
    client = MagicMock()
    client.execute_sql.return_value = {
        "result": {"data_array": rows or []}
    }
    return client


def _make_confluence_client(page: dict | None = None, children: list | None = None) -> MagicMock:
    """Return a ConfluenceClient mock."""
    client = MagicMock()
    default_page = {
        "id": "123",
        "title": "Test Page",
        "body": {"storage": {"value": "<p>Hello world</p>"}},
        "version": {"number": 1},
        "space": {"key": "TEST", "name": "Test Space"},
        "ancestors": [],
    }
    client.get_page.return_value = page or default_page
    client.get_page_tree.return_value = [page or default_page] + (children or [])
    return client


# ===========================================================================
# discover_tables
# ===========================================================================


class TestDiscoverTables:
    def test_returns_list_of_dicts(self):
        rows = [
            ["my_catalog", "my_schema", "customers", "1000"],
            ["my_catalog", "my_schema", "orders", "5000"],
        ]
        client = _make_db_client(rows)
        result = discover_tables(client, "my_catalog")

        assert isinstance(result, list)
        assert len(result) == 2

    def test_dict_has_required_keys(self):
        rows = [["cat", "sch", "tbl"]]
        client = _make_db_client(rows)
        result = discover_tables(client, "cat")

        row = result[0]
        for key in ("catalog", "schema", "table", "columns", "row_count"):
            assert key in row, f"Missing key: {key}"

    def test_row_count_defaults_to_none(self):
        rows = [["cat", "sch", "tbl"]]
        client = _make_db_client(rows)
        result = discover_tables(client, "cat")
        assert result[0]["row_count"] is None

    def test_empty_catalog_raises(self):
        client = MagicMock()
        with pytest.raises(ValueError, match="catalog"):
            discover_tables(client, "")

    def test_sql_contains_catalog_name(self):
        client = _make_db_client([])
        discover_tables(client, "my_catalog")
        sql_called = client.execute_sql.call_args[0][0]
        assert "my_catalog" in sql_called

    def test_schema_filter_applied(self):
        client = _make_db_client([])
        discover_tables(client, "cat", schema="my_schema")
        sql_called = client.execute_sql.call_args[0][0]
        assert "my_schema" in sql_called

    def test_no_keywords_returns_all_rows(self):
        rows = [
            ["cat", "sch", "alpha"],
            ["cat", "sch", "beta"],
        ]
        client = _make_db_client(rows)
        result = discover_tables(client, "cat")
        assert len(result) == 2

    def test_keyword_filters_by_table_name(self):
        """Tables whose names contain a keyword are returned; others are dropped."""
        table_rows = [["cat", "sch", "customer_dim"]]
        col_rows = [["id", "bigint", ""]]
        col_search_rows = []

        client = MagicMock()
        client.execute_sql.side_effect = [
            {"result": {"data_array": table_rows}},   # table name search
            {"result": {"data_array": col_rows}},      # column fetch for match
            {"result": {"data_array": col_search_rows}}, # column name search
        ]

        result = discover_tables(client, "cat", keywords=["customer"])

        names = [r["table"] for r in result]
        assert "customer_dim" in names
        assert len(result) == 1


# ===========================================================================
# profile_table
# ===========================================================================


class TestProfileTable:
    def _make_describe_rows(self) -> list[list]:
        return [
            ["id", "bigint", ""],
            ["name", "string", ""],
            ["created_at", "date", ""],
        ]

    def _make_batch_rows(self) -> list[list]:
        # ORDER: total_rows, null_id, dist_id, null_name, dist_name,
        #        null_created_at, dist_created_at, min_created_at, max_created_at
        return [["1000", "0", "999", "5", "900", "10", "365", "2020-01-01", "2023-12-31"]]

    def _make_client(self) -> MagicMock:
        client = MagicMock()
        describe_resp = {"result": {"data_array": self._make_describe_rows()}}
        batch_resp = {"result": {"data_array": self._make_batch_rows()}}
        client.execute_sql.side_effect = [describe_resp, batch_resp]
        return client

    def test_returns_required_keys(self):
        client = self._make_client()
        result = profile_table(client, "cat", "sch", "tbl")
        for key in ("row_count", "column_count", "columns", "date_range", "null_rates", "distinct_counts"):
            assert key in result, f"Missing key: {key}"

    def test_row_count(self):
        client = self._make_client()
        result = profile_table(client, "cat", "sch", "tbl")
        assert result["row_count"] == 1000

    def test_column_count(self):
        client = self._make_client()
        result = profile_table(client, "cat", "sch", "tbl")
        assert result["column_count"] == 3

    def test_null_rate_calculation(self):
        """null_rate = null_count / total_rows."""
        client = self._make_client()
        result = profile_table(client, "cat", "sch", "tbl")
        # name has 5 nulls out of 1000
        assert result["null_rates"]["name"] == pytest.approx(0.005, abs=1e-4)

    def test_distinct_counts_in_result(self):
        client = self._make_client()
        result = profile_table(client, "cat", "sch", "tbl")
        assert result["distinct_counts"]["id"] == 999

    def test_date_range_populated_for_date_columns(self):
        client = self._make_client()
        result = profile_table(client, "cat", "sch", "tbl")
        assert result["date_range"] is not None
        assert result["date_range"]["min"] == "2020-01-01"
        assert result["date_range"]["max"] == "2023-12-31"

    def test_empty_table_returns_empty_profile(self):
        """When DESCRIBE returns no rows, return an empty profile."""
        client = MagicMock()
        client.execute_sql.return_value = {"result": {"data_array": []}}
        result = profile_table(client, "cat", "sch", "empty_tbl")
        assert result["row_count"] == 0
        assert result["columns"] == []

    def test_columns_list_has_required_keys(self):
        client = self._make_client()
        result = profile_table(client, "cat", "sch", "tbl")
        for col in result["columns"]:
            for key in ("name", "data_type", "null_count", "null_rate", "distinct_count"):
                assert key in col, f"Column missing key: {key}"


# ===========================================================================
# trace_lineage
# ===========================================================================


class TestTraceLineage:
    def test_simple_select(self):
        sql = "SELECT id, name FROM users"
        result = trace_lineage(sql)
        assert isinstance(result, dict)
        for key in ("ctes", "from_tables", "column_lineage"):
            assert key in result

    def test_from_tables_extracted(self):
        sql = "SELECT u.id FROM users u"
        result = trace_lineage(sql)
        tables = [t["table"] for t in result["from_tables"]]
        assert "users" in tables

    def test_column_lineage_has_required_keys(self):
        sql = "SELECT id FROM users"
        result = trace_lineage(sql)
        for entry in result["column_lineage"]:
            for key in ("output_column", "expression", "transform", "sources"):
                assert key in entry

    def test_alias_resolved(self):
        sql = "SELECT id AS user_id FROM users"
        result = trace_lineage(sql)
        output_cols = [e["output_column"] for e in result["column_lineage"]]
        assert "user_id" in output_cols

    def test_join_tables_extracted(self):
        sql = "SELECT a.id, b.name FROM orders a JOIN customers b ON a.customer_id = b.id"
        result = trace_lineage(sql)
        tables = [t["table"] for t in result["from_tables"]]
        assert "orders" in tables
        assert "customers" in tables

    def test_cte_extracted(self):
        sql = """
        WITH base AS (SELECT id FROM raw_users)
        SELECT id FROM base
        """
        result = trace_lineage(sql)
        assert "base" in result["ctes"]

    def test_aggregation_transform_detected(self):
        sql = "SELECT COUNT(*) AS total FROM orders"
        result = trace_lineage(sql)
        transforms = [e["transform"] for e in result["column_lineage"]]
        assert "AGGREGATION" in transforms

    def test_pass_through_transform(self):
        sql = "SELECT id FROM users"
        result = trace_lineage(sql)
        entry = result["column_lineage"][0]
        assert entry["transform"] in ("PASS-THROUGH", "RENAME")

    def test_rename_transform(self):
        sql = "SELECT user_id AS uid FROM users"
        result = trace_lineage(sql)
        transforms = [e["transform"] for e in result["column_lineage"]]
        assert "RENAME" in transforms

    def test_empty_ctes_when_no_with(self):
        sql = "SELECT id FROM users"
        result = trace_lineage(sql)
        assert result["ctes"] == []


# ===========================================================================
# fetch_confluence_page
# ===========================================================================


class TestFetchConfluencePage:
    def test_calls_get_page_with_correct_id(self):
        client = _make_confluence_client()
        fetch_confluence_page(client, "12345")
        client.get_page.assert_called_once_with("12345")

    def test_returns_string(self):
        client = _make_confluence_client()
        result = fetch_confluence_page(client, "12345")
        assert isinstance(result, str)

    def test_title_appears_in_output(self):
        page = {
            "id": "123",
            "title": "My Important Page",
            "body": {"storage": {"value": "<p>Content here</p>"}},
        }
        client = _make_confluence_client(page=page)
        result = fetch_confluence_page(client, "123")
        assert "My Important Page" in result

    def test_html_content_converted(self):
        page = {
            "id": "123",
            "title": "Page",
            "body": {"storage": {"value": "<p>Hello <strong>world</strong></p>"}},
        }
        client = _make_confluence_client(page=page)
        result = fetch_confluence_page(client, "123")
        # Should contain plain text (tags stripped)
        assert "Hello" in result
        assert "world" in result

    def test_include_children_calls_get_page_tree(self):
        parent_page = {
            "id": "1",
            "title": "Parent",
            "body": {"storage": {"value": "<p>Parent content</p>"}},
        }
        child_page = {
            "id": "2",
            "title": "Child",
            "body": {"storage": {"value": "<p>Child content</p>"}},
        }
        client = _make_confluence_client(page=parent_page, children=[child_page])

        result = fetch_confluence_page(client, "1", include_children=True)

        client.get_page_tree.assert_called_once_with("1")
        assert "Parent" in result
        assert "Child" in result

    def test_include_children_false_does_not_call_get_page_tree(self):
        client = _make_confluence_client()
        fetch_confluence_page(client, "99", include_children=False)
        client.get_page_tree.assert_not_called()

    def test_empty_html_returns_title_only(self):
        page = {
            "id": "1",
            "title": "Empty Page",
            "body": {"storage": {"value": ""}},
        }
        client = _make_confluence_client(page=page)
        result = fetch_confluence_page(client, "1")
        assert "Empty Page" in result

    def test_multiple_pages_separated_by_hr(self):
        """When include_children=True, pages are separated by horizontal rules."""
        pages = [
            {"id": "1", "title": "A", "body": {"storage": {"value": "<p>aaa</p>"}}},
            {"id": "2", "title": "B", "body": {"storage": {"value": "<p>bbb</p>"}}},
        ]
        client = MagicMock()
        client.get_page_tree.return_value = pages
        result = fetch_confluence_page(client, "1", include_children=True)
        assert "---" in result


# ============================================================================
# Marketplace core wrapper (rewritten in Task 14)
# ============================================================================


def test_search_marketplace_returns_search_results_typed(monkeypatch):
    """The core wrapper returns the typed SearchResults, not a list[dict]."""
    from skills.core import marketplace as core_mp
    from skills.clients.marketplace import models, client as client_mod

    fake = models.SearchResults(
        items=[], total_count=0, current_page=1, page_size=25, total_pages=0,
    )

    def fake_init(self, *a, **kw): self._bearer = "x"; self._api_base_url = "y"
    monkeypatch.setattr(client_mod.MarketplaceClient, "__init__", fake_init)
    monkeypatch.setattr(client_mod.MarketplaceClient, "from_cache",
                        classmethod(lambda cls: cls.__new__(cls)))
    monkeypatch.setattr(client_mod.MarketplaceClient, "search",
                        lambda self, **kw: fake)

    result = core_mp.search_marketplace("client risk")
    assert isinstance(result, models.SearchResults)


def test_search_marketplace_no_stub_function():
    """Old _stub_results function MUST be gone."""
    from skills.core import marketplace as core_mp
    assert not hasattr(core_mp, "_stub_results")


def test_search_marketplace_no_fake_v1_search_url():
    """The fake /api/v1/search URL must not appear in the rewritten module."""
    from pathlib import Path
    text = Path("skills/core/marketplace.py").read_text()
    assert "/api/v1/search?" not in text
    assert "_stub_results" not in text
    assert "STUB" not in text


# ===========================================================================
# classify_data_product
# ===========================================================================


