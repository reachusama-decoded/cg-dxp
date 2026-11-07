"""Core function: discover tables in Unity Catalog.

Pure query layer — no side-effects.  Callers own the DatabricksClient lifecycle.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_TABLE_TYPES = "('BASE TABLE', 'EXTERNAL', 'MANAGED', 'VIEW')"


def discover_tables(
    client: Any,
    catalog: str,
    keywords: list[str] | None = None,
    schema: str | None = None,
    search_columns: bool = True,
) -> list[dict]:
    """Query Unity Catalog for tables matching criteria.

    Searches the information_schema for tables in *catalog* (and optionally
    *schema*), filtering by *keywords* against table names in SQL.

    Args:
        client: DatabricksClient instance (must have a warehouse_id configured).
        catalog: Unity Catalog catalog name (e.g. ``cspn_prd``).
        keywords: Optional list of search terms.  A table is included if any
                  keyword appears in the table name.
        schema: Optional schema to restrict the search to.
        search_columns: If True, also searches column names for keywords (default True).
                        Provides richer results but adds a second query.

    Returns:
        List of dicts with keys: catalog, schema, table, columns, row_count.
    """
    if not catalog:
        raise ValueError("catalog must be a non-empty string")

    if keywords:
        return _discover_by_keywords(client, catalog, keywords, schema, search_columns)
    else:
        return _discover_all(client, catalog, schema)


def discover_tables_multi(
    client: Any,
    catalogs: list[str],
    keywords: list[str] | None = None,
    schema: str | None = None,
) -> list[dict]:
    """Search multiple catalogs and combine results.

    Convenience wrapper around discover_tables for searching across catalogs.
    """
    results: list[dict] = []
    for catalog in catalogs:
        try:
            tables = discover_tables(client, catalog, keywords, schema)
            results.extend(tables)
        except Exception:
            logger.warning("Could not search catalog %s, skipping", catalog)
    return results


def _discover_by_keywords(
    client: Any,
    catalog: str,
    keywords: list[str],
    schema: str | None = None,
    search_columns: bool = True,
) -> list[dict]:
    """Search for tables matching keywords in table names.

    First searches table names, then enriches matches with column metadata.
    Column-name searching is opt-in (search_columns=True) because it can
    be very slow on production catalogs with millions of column records.
    """

    kw_conditions = _build_like_conditions("table_name", keywords)
    schema_filter = f"AND table_schema = '{schema}'" if schema else ""

    sql = f"""
    SELECT
        table_catalog,
        table_schema,
        table_name
    FROM {catalog}.information_schema.tables
    WHERE table_type IN {_TABLE_TYPES}
    {schema_filter}
    AND ({kw_conditions})
    ORDER BY table_schema, table_name
    """

    resp = client.execute_sql(sql.strip())
    rows = resp.get("result", {}).get("data_array", [])

    tables: list[dict] = []
    for row in rows:
        tbl = _make_table_dict(catalog, row)
        tbl["columns"] = _fetch_columns(client, tbl["catalog"], tbl["schema"], tbl["table"])
        tables.append(tbl)

    if search_columns:
        col_conditions = _build_like_conditions("column_name", keywords)

        col_sql = f"""
        SELECT DISTINCT table_schema, table_name
        FROM {catalog}.information_schema.columns
        WHERE ({col_conditions})
        {schema_filter}
        """

        try:
            col_resp = client.execute_sql(col_sql.strip())
            col_rows = col_resp.get("result", {}).get("data_array", [])

            existing = {(t["schema"], t["table"]) for t in tables}
            for row in col_rows:
                col_schema = row[0] if len(row) > 0 else ""
                col_table = row[1] if len(row) > 1 else ""
                if (col_schema, col_table) not in existing:
                    tbl = {
                        "catalog": catalog,
                        "schema": col_schema,
                        "table": col_table,
                        "columns": _fetch_columns(client, catalog, col_schema, col_table),
                        "row_count": None,
                    }
                    tables.append(tbl)
        except Exception:
            logger.warning("Column-name search failed for %s, continuing with table-name results", catalog)

    return tables


def _discover_all(
    client: Any,
    catalog: str,
    schema: str | None = None,
) -> list[dict]:
    """Return all tables in a catalog (or schema)."""

    schema_filter = f"AND t.table_schema = '{schema}'" if schema else ""

    sql = f"""
    SELECT
        t.table_catalog,
        t.table_schema,
        t.table_name
    FROM `{catalog}`.information_schema.tables t
    WHERE t.table_type IN {_TABLE_TYPES}
    {schema_filter}
    ORDER BY t.table_schema, t.table_name
    """

    resp = client.execute_sql(sql.strip())
    rows = resp.get("result", {}).get("data_array", [])

    return [_make_table_dict(catalog, row) for row in rows]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_like_conditions(column_expr: str, keywords: list[str]) -> str:
    """Build OR-chained LIKE conditions for SQL WHERE clause."""
    return " OR ".join(
        f"LOWER({column_expr}) LIKE '%{kw.lower()}%'" for kw in keywords
    )


def _make_table_dict(catalog: str, row: list) -> dict:
    """Build a table result dict from an information_schema row."""
    return {
        "catalog": row[0] if len(row) > 0 else catalog,
        "schema": row[1] if len(row) > 1 else "",
        "table": row[2] if len(row) > 2 else "",
        "columns": [],
        "row_count": None,
    }


def _fetch_columns(client: Any, catalog: str, schema: str, table: str) -> list[dict]:
    """Return column metadata for a single table."""
    sql = f"""
    SELECT column_name, data_type, comment
    FROM `{catalog}`.information_schema.columns
    WHERE table_catalog = '{catalog}'
      AND table_schema = '{schema}'
      AND table_name = '{table}'
    ORDER BY ordinal_position
    """
    try:
        resp = client.execute_sql(sql.strip())
        rows = resp.get("result", {}).get("data_array", [])
        return [
            {
                "name": r[0] if len(r) > 0 else "",
                "type": r[1] if len(r) > 1 else "",
                "comment": r[2] if len(r) > 2 else "",
            }
            for r in rows
        ]
    except Exception:
        logger.warning("Could not fetch columns for %s.%s.%s", catalog, schema, table)
        return []
