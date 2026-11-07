"""Core function: profile a Unity Catalog table.

Runs batched SQL to collect row counts, null rates, distinct counts, and
date-column ranges in a single query per table.  No side-effects.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Data types that are treated as date/timestamp columns for range profiling
_DATE_TYPES = {"date", "timestamp", "timestamp_ntz"}


def profile_table(
    client: Any,
    catalog: str,
    schema: str,
    table: str,
) -> dict:
    """Profile a table's structure and data quality.

    Executes:
    1. A DESCRIBE TABLE to enumerate columns and types.
    2. A single batch SELECT with COUNT/DISTINCT/NULL aggregations for every
       column, plus MIN/MAX for any date or timestamp columns.

    Args:
        client: DatabricksClient with a configured warehouse_id.
        catalog: Unity Catalog catalog name.
        schema: Schema name.
        table: Table name.

    Returns:
        dict with keys:
          row_count (int): Total rows.
          column_count (int): Number of columns.
          columns (list[dict]): Per-column profile.  Each dict has:
            name (str), data_type (str), null_count (int), null_rate (float),
            distinct_count (int).  Date/timestamp columns also have
            min_value (str) and max_value (str).
          date_range (dict | None): {"min": str, "max": str} for the first
            date/timestamp column found, or None.
          null_rates (dict): {column_name: null_rate_float} shortcut.
          distinct_counts (dict): {column_name: distinct_count_int} shortcut.
    """
    full_name = f"`{catalog}`.`{schema}`.`{table}`"

    # Step 1: Enumerate columns via DESCRIBE
    col_meta = _describe_columns(client, full_name)
    if not col_meta:
        return _empty_profile()

    # Step 2: Build and run the batch profiling query
    batch_sql = _build_batch_sql(full_name, col_meta)
    resp = client.execute_sql(batch_sql)
    raw_rows = resp.get("result", {}).get("data_array", [])

    if not raw_rows:
        return _empty_profile()

    # The batch query returns a single row
    values = raw_rows[0]
    return _parse_batch_result(values, col_meta)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _describe_columns(client: Any, full_name: str) -> list[dict]:
    """Return [{name, data_type}] from DESCRIBE TABLE."""
    resp = client.execute_sql(f"DESCRIBE TABLE {full_name}")
    rows = resp.get("result", {}).get("data_array", [])
    cols = []
    for r in rows:
        col_name = r[0].strip() if r else ""
        data_type = r[1].strip() if len(r) > 1 else ""
        # DESCRIBE TABLE appends partition/comment metadata rows after a blank
        if not col_name or col_name.startswith("#"):
            break
        cols.append({"name": col_name, "data_type": data_type})
    return cols


def _build_batch_sql(full_name: str, col_meta: list[dict]) -> str:
    """Build a single SELECT aggregating all columns in one pass."""
    parts = ["SELECT COUNT(*) AS _total_rows"]
    for col in col_meta:
        n = col["name"]
        dt = col["data_type"].lower().split("(")[0].strip()
        parts.append(f"  , COUNT(*) - COUNT(`{n}`) AS `_null_{n}`")
        parts.append(f"  , APPROX_COUNT_DISTINCT(`{n}`) AS `_dist_{n}`")
        if dt in _DATE_TYPES:
            parts.append(f"  , CAST(MIN(`{n}`) AS STRING) AS `_min_{n}`")
            parts.append(f"  , CAST(MAX(`{n}`) AS STRING) AS `_max_{n}`")
    parts.append(f"FROM {full_name}")
    return "\n".join(parts)


def _parse_batch_result(values: list, col_meta: list[dict]) -> dict:
    """Parse the single-row batch result into the profile structure."""
    # Build a flat index: position -> value
    idx = 0
    total_rows = int(values[idx]) if values[idx] is not None else 0
    idx += 1

    column_profiles: list[dict] = []
    null_rates: dict[str, float] = {}
    distinct_counts: dict[str, int] = {}
    first_date_range: dict | None = None

    for col in col_meta:
        n = col["name"]
        dt = col["data_type"].lower().split("(")[0].strip()

        null_count = int(values[idx]) if idx < len(values) and values[idx] is not None else 0
        idx += 1
        distinct_count = int(values[idx]) if idx < len(values) and values[idx] is not None else 0
        idx += 1

        null_rate = round(null_count / total_rows, 4) if total_rows > 0 else 0.0

        col_profile: dict = {
            "name": n,
            "data_type": col["data_type"],
            "null_count": null_count,
            "null_rate": null_rate,
            "distinct_count": distinct_count,
        }

        if dt in _DATE_TYPES:
            min_val = values[idx] if idx < len(values) else None
            idx += 1
            max_val = values[idx] if idx < len(values) else None
            idx += 1
            col_profile["min_value"] = str(min_val) if min_val is not None else None
            col_profile["max_value"] = str(max_val) if max_val is not None else None
            if first_date_range is None and min_val is not None:
                first_date_range = {"min": str(min_val), "max": str(max_val)}

        column_profiles.append(col_profile)
        null_rates[n] = null_rate
        distinct_counts[n] = distinct_count

    return {
        "row_count": total_rows,
        "column_count": len(col_meta),
        "columns": column_profiles,
        "date_range": first_date_range,
        "null_rates": null_rates,
        "distinct_counts": distinct_counts,
    }


def _empty_profile() -> dict:
    return {
        "row_count": 0,
        "column_count": 0,
        "columns": [],
        "date_range": None,
        "null_rates": {},
        "distinct_counts": {},
    }
