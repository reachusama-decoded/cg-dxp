"""
dbt-unit-test Seed Fixer — deterministic post-processing to correct LLM-generated seed gaps.

Module-level functions extracted from AITestCaseGenerator for separation of concerns.
"""
from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def backfill_base_cte_seeds(
    test_cases: list,
    raw_sql: str,
) -> list:
    """
    Guard against LLMs that correctly seed secondary tables (e.g.
    sma_non_discretionary_market_value) but forget to seed the base CTE
    source table (e.g. cgam_position_by_activity_date_v4) that EVERY
    downstream CTE depends on.

    For each TC expecting non-empty output: if the first CTE's source table
    is empty, synthesise a minimal seed row derived from other seeded tables
    (position_date, portfolio_uid, listing_uid) with safe defaults.
    This does NOT override rows the LLM already provided.
    """
    # Find the source table of the first CTE — handles Jinja patterns like:
    #   FROM {{schema}}.{{'table_name'}}
    jinja_table_re = re.compile(
        r"\bFROM\b[^;(]*?\.\{\{['\"]+([\w]+)['\"]",
        re.IGNORECASE | re.DOTALL,
    )
    match = jinja_table_re.search(raw_sql)
    if not match:
        return test_cases  # can't determine base table

    base_table = match.group(1).lower()

    for tc in test_cases:
        # Only backfill TCs that expect non-empty output
        if not tc.expected_output:
            continue

        # Skip if base table already has rows
        if tc.input_data.get(base_table):
            continue

        # Derive values from other seeded tables
        pos_date: str | None = None
        portfolio_uid: Any = None
        listing_uid: Any = 999  # safe non-sentinel default

        for rows in tc.input_data.values():
            if not rows:
                continue
            r = rows[0]
            if pos_date is None and r.get("position_date"):
                pos_date = str(r["position_date"])
            if portfolio_uid is None:
                for col in ("portfolio_uid", "aa_portfolio_uid"):
                    if r.get(col) is not None:
                        portfolio_uid = r[col]
                        break
            if r.get("listing_uid") is not None and r["listing_uid"] != 213242482:
                listing_uid = r["listing_uid"]

        pos_date = pos_date or "2024-01-15"
        portfolio_uid = portfolio_uid if portfolio_uid is not None else 1
        ts = f"{pos_date} 00:00:00" if " " not in str(pos_date) else str(pos_date)

        tc.input_data[base_table] = [{
            "position_date": pos_date,
            "dl_system_start_timestamp": ts,
            "dl_current_indicator": "Y",
            "aa_portfolio_uid": portfolio_uid,
            "listing_uid": listing_uid,
        }]
        logger.info(
            "[dbt-unit-test] Auto-backfilled '%s' seed for %s "
            "(base CTE table was empty, TC expects non-empty output)",
            base_table, tc.test_id,
        )

    return test_cases


def parse_sql_join_structure(raw_sql: str) -> "dict | None":
    """
    Parse Jinja SQL and extract join structure used to drive seed gap fixing.

    Returns a dict with:
      base_table        : str — first FROM source table (no schema prefix)
      inner_join_tables : list[str] — source tables referenced via INNER JOIN
      table_aliases     : dict[str, str] — alias (lower) → table name (lower)
      join_conditions   : list[tuple] — (alias1, col1, alias2, col2) from ON clauses
      coalesce_fallbacks: dict[str, int] — FK col → integer COALESCE fallback value
      between_by_alias  : dict[str, set] — alias → {(start_col, end_col)} pairs
      join_equalities   : dict[str, dict] — alias → {col: literal} from ON/AND =
      join_inequalities : dict[str, dict] — alias → {col: excluded_val} from <> clauses
      unk_country_cols  : dict[str, list] — alias → ordered list of cols that
                          COALESCE to 'UNK' (identifies country-code columns)

    Returns None when no Jinja table references are found in the SQL.
    """
    # Only meaningful for Jinja SQL — detect {{schema}}.{{'table'}} patterns
    _jinja_tbl_re = re.compile(
        r"\{\{[^}]+\}\}\s*\.\s*\{\{\s*['\"](\w+)['\"]\s*\}\}",
        re.IGNORECASE,
    )
    if not _jinja_tbl_re.search(raw_sql):
        return None

    # SQL keywords that must never be captured as a table alias
    _SQL_KW = frozenset({
        "where", "on", "and", "or", "not", "group", "order", "having",
        "limit", "union", "all", "inner", "left", "right", "outer", "cross",
        "join", "from", "select", "with", "as", "by", "set", "into",
        "distinct", "partition", "clustered", "sorted", "case", "when",
        "then", "else", "end", "between", "in", "is", "like", "null",
        "true", "false", "cast", "coalesce",
    })

    result: dict = {
        "base_table"            : None,
        "inner_join_tables"     : [],
        "table_aliases"         : {},
        "join_conditions"       : [],
        "coalesce_fallbacks"    : {},
        "between_by_alias"      : {},
        "range_filter_triplets" : [],   # (lhs_alias, lhs_col, dim_alias, start_col, end_col)
        "join_equalities"       : {},
        "join_inequalities"     : {},
        "unk_country_cols"      : {},
        "cte_names"             : set(),  # CTE names defined in WITH block (not source tables)
        # CASE WHEN col = X THEN val_a ELSE val_b END AS out_col
        # stored as list of (input_col, if_val, then_val, else_val, out_col, valid_set)
        "case_when_int_mappings": [],
        # col_name -> frozenset(reserved_ints) parsed from WHERE col NOT IN (...)
        "not_in_int_cols"       : {},
        # alias -> set(col_names) referenced as alias.col anywhere in the SQL
        "alias_cols"            : {},
    }

    # ── Step 1: Build alias → table_name from FROM / JOIN clauses ──────────
    # Matches:  FROM | INNER JOIN | LEFT [OUTER] JOIN  {{schema}}.{{'table'}} [AS] alias
    join_from_re = re.compile(
        r"(?:FROM|(?:INNER|LEFT(?:\s+OUTER)?|RIGHT(?:\s+OUTER)?|CROSS)"
        r"(?:\s+OUTER)?\s+JOIN)"
        r"\s+\{\{[^}]+\}\}\s*\.\s*\{\{\s*['\"](\w+)['\"]\s*\}\}"
        r"\s*(?:AS\s+)?(\w+)?",
        re.IGNORECASE | re.DOTALL,
    )
    for m in join_from_re.finditer(raw_sql):
        tbl       = m.group(1).lower()
        raw_alias = m.group(2)
        alias     = (
            raw_alias.lower()
            if raw_alias and raw_alias.lower() not in _SQL_KW
            else tbl
        )
        result["table_aliases"][alias] = tbl
        result["table_aliases"][tbl]   = tbl   # identity mapping

    # ── Step 2: Base table — first FROM Jinja reference ────────────────────
    base_re = re.compile(
        r"\bFROM\b\s+\{\{[^}]+\}\}\s*\.\s*\{\{\s*['\"](\w+)['\"]\s*\}\}",
        re.IGNORECASE | re.DOTALL,
    )
    m = base_re.search(raw_sql)
    if m:
        result["base_table"] = m.group(1).lower()

    # ── Step 3: INNER JOIN source tables (deduplicated) ────────────────────
    inner_join_re = re.compile(
        r"\bINNER\s+JOIN\s+\{\{[^}]+\}\}\s*\.\s*\{\{\s*['\"](\w+)['\"]\s*\}\}",
        re.IGNORECASE | re.DOTALL,
    )
    result["inner_join_tables"] = list(
        {m.group(1).lower() for m in inner_join_re.finditer(raw_sql)}
    )

    # ── Step 4: Standard JOIN ON conditions: alias1.col1 = alias2.col2 ──────
    on_cond_re = re.compile(
        r"\bON\b\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)",
        re.IGNORECASE,
    )
    for m in on_cond_re.finditer(raw_sql):
        result["join_conditions"].append((
            m.group(1).lower(), m.group(2).lower(),
            m.group(3).lower(), m.group(4).lower(),
        ))

    # ── Step 4b: COALESCE(alias.col, INT) = alias2.col  (FK with fallback) ─
    coalesce_join_re = re.compile(
        r"COALESCE\s*\(\s*(\w+)\.(\w+)\s*,\s*(\d+)\s*\)\s*=\s*(\w+)\.(\w+)",
        re.IGNORECASE,
    )
    for m in coalesce_join_re.finditer(raw_sql):
        fk_col   = m.group(2).lower()
        fallback = int(m.group(3))
        result["coalesce_fallbacks"][fk_col] = fallback
        result["join_conditions"].append((
            m.group(1).lower(), fk_col,
            m.group(4).lower(), m.group(5).lower(),
        ))

    # ── Step 5: BETWEEN date range pairs (full pattern with LHS) ──────────
    # Captures: lhs_alias.lhs_col BETWEEN dim_alias.start_col AND dim_alias.end_col
    between_re = re.compile(
        r"(\w+)\.(\w+)\s+BETWEEN\s+(\w+)\.([\w]+)"
        r"\s+AND\s+(?:coalesce\s*\(\s*|cast\s*\(\s*)?(\w+)\.([\w]+)",
        re.IGNORECASE | re.DOTALL,
    )
    for m in between_re.finditer(raw_sql):
        lhs_a, lhs_c = m.group(1).lower(), m.group(2).lower()
        a1, c1       = m.group(3).lower(), m.group(4).lower()
        a2, c2       = m.group(5).lower(), m.group(6).lower()
        if a1 == a2:   # start and end belong to the same dim alias
            result["between_by_alias"].setdefault(a1, set()).add((c1, c2))
            result["range_filter_triplets"].append((lhs_a, lhs_c, a1, c1, c2))

    # ── Step 6: Equality constraints from JOIN ON / AND clauses ─────────────
    # e.g.  AND G1.geography_type_code = 'CTRY'
    join_eq_re = re.compile(
        r"(?:ON|AND)\s+(\w+)\.([\w]+)\s*=\s*['\"](\w+)['\"]",
        re.IGNORECASE,
    )
    for m in join_eq_re.finditer(raw_sql):
        a, col, val = m.group(1).lower(), m.group(2).lower(), m.group(3)
        result["join_equalities"].setdefault(a, {})[col] = val

    # ── Step 7: Inequality (<>) constraints from JOIN ON / AND clauses ──────
    # e.g.  AND G1.geography_name <> 'Chinax'
    join_ineq_re = re.compile(
        r"(?:ON|AND)\s+(\w+)\.([\w]+)\s*<>\s*['\"]([^'\"]+)['\"]",
        re.IGNORECASE,
    )
    for m in join_ineq_re.finditer(raw_sql):
        a, col = m.group(1).lower(), m.group(2).lower()
        result["join_inequalities"].setdefault(a, {})[col] = m.group(3)

    # ── Step 8: Columns COALESCE-d to 'UNK' (country-code columns) ──────────
    unk_re = re.compile(
        r"COALESCE\s*\(\s*(\w+)\.([\w]+)\s*,\s*['\"]UNK['\"]\s*\)",
        re.IGNORECASE,
    )
    for m in unk_re.finditer(raw_sql):
        result["unk_country_cols"].setdefault(m.group(1).lower(), []).append(
            m.group(2).lower()
        )

    # ── Step 9: CTE names + CASE WHEN integer-to-integer mappings ──────────
    # Collect CTE names so the post-processor can remove them from input_data.
    _SQL_KW = {
        "select", "from", "where", "join", "on", "and", "or", "not",
        "with", "as", "case", "when", "then", "else", "end", "in",
        "inner", "left", "right", "outer", "cross", "full", "group",
        "by", "order", "having", "limit", "union", "all", "distinct",
        "null", "is", "between", "like", "exists", "table",
    }
    cte_name_re = re.compile(r"\b(\w+)\s+AS\s*\(", re.IGNORECASE)
    for m in cte_name_re.finditer(raw_sql):
        name = m.group(1).lower()
        if name not in _SQL_KW:
            result["cte_names"].add(name)
    # Remove any genuine source tables accidentally detected as CTEs
    source_tables = set(result["table_aliases"].values())
    result["cte_names"] -= source_tables

    # Parse:  CASE WHEN col = INT THEN INT ELSE INT END [AS out_col]
    # and nearby:  WHERE col IN (int_a, int_b) — the valid values set
    case_when_re = re.compile(
        r"CASE\s+WHEN\s+(\w+)\s*=\s*(\d+)\s+THEN\s+(\d+)\s+ELSE\s+(\d+)\s+END"
        r"(?:\s+AS\s+(\w+))?",
        re.IGNORECASE,
    )
    where_in_re = re.compile(
        r"WHERE\s+(\w+)\s+IN\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)",
        re.IGNORECASE,
    )
    valid_values: dict = {}
    for m in where_in_re.finditer(raw_sql):
        col = m.group(1).lower()
        valid_values.setdefault(col, set()).update({int(m.group(2)), int(m.group(3))})

    for m in case_when_re.finditer(raw_sql):
        in_col   = m.group(1).lower()
        if_val   = int(m.group(2))
        then_val = int(m.group(3))
        else_val = int(m.group(4))
        out_col  = m.group(5).lower() if m.group(5) else None
        valid_set = valid_values.get(in_col, {if_val})
        result["case_when_int_mappings"].append(
            (in_col, if_val, then_val, else_val, out_col, valid_set)
        )

    # Parse:  WHERE [alias.]col NOT IN (n1, n2, ...)
    # Captures reserved integer IDs that bypass the main UNION branch.
    not_in_re = re.compile(
        r"WHERE\s+(?:\w+\.)?\s*(\w+)\s+NOT\s+IN\s*\(([\d\s,]+)\)",
        re.IGNORECASE,
    )
    for m in not_in_re.finditer(raw_sql):
        col  = m.group(1).lower()
        vals = frozenset(
            int(v.strip()) for v in m.group(2).split(",") if v.strip().isdigit()
        )
        if vals:
            result["not_in_int_cols"].setdefault(col, set()).update(vals)
    # Freeze to frozenset
    result["not_in_int_cols"] = {
        c: frozenset(v) for c, v in result["not_in_int_cols"].items()
    }

    # ── Step 10: alias.col reference map ────────────────────────────────────
    # Captures every  alias.column_name  reference in the SQL so Fix 9 can
    # detect which columns are expected on each dim-table alias.
    alias_col_re = re.compile(r"\b(\w+)\.(\w+)\b")
    for m in alias_col_re.finditer(raw_sql):
        a, c = m.group(1).lower(), m.group(2).lower()
        if a not in _SQL_KW and c not in _SQL_KW:
            result["alias_cols"].setdefault(a, set()).add(c)

    return result


def fix_seed_column_gaps(
    test_cases: list,
    raw_sql: str = "",
) -> list:
    """
    Deterministic post-processing pass that corrects systematic seed gaps
    that LLMs produce for models with INNER JOIN dimension tables.

    Table and column names are derived entirely from SQL join-structure
    analysis — no hardcoded table or column names.  Falls back to a no-op
    when ``raw_sql`` is absent or the SQL contains no Jinja table references.

    Fixes applied (when applicable):

    Fix 1 — FK column missing from base-table rows.
        The FK used in an INNER JOIN ON condition must be present in every
        base-table seed row or Spark throws AnalysisException.

    Fix 2 — Empty INNER JOIN table.
        An INNER JOIN with an empty TempView always returns 0 rows.
        Synthesises a minimal seed row keyed by the FK value from the base
        table.  The row also includes all BETWEEN date-range columns,
        JOIN equality constraints (e.g. geography_type_code = 'CTRY'),
        and safe placeholder values for JOIN inequality constraints
        (e.g. geography_name <> 'Chinax').

    Fix 3 — PK / FK value mismatch between base and dimension tables.
        Syncs dim-table PK to match the base-table FK so INNER JOIN succeeds.

    Fix 4 — Empty / incomplete COALESCE-joined LEFT JOIN tables.
        Detects tables joined via COALESCE(dim_fk, fallback_int) = geo.pk
        and back-fills them if empty, using the COALESCE fallback integer
        (or the actual FK value from a seeded intermediate dim table).

    Fix 5 — Country-column alignment.
        When the first COALESCE(col, 'UNK') country column in the base table
        is NULL (→ ZZZ), nulls out any other COALESCE('UNK') country columns
        in the same base-table rows so all country-aggregation CTEs resolve
        to the same iso country code.
    """
    if not raw_sql:
        return test_cases

    struct = parse_sql_join_structure(raw_sql)
    if struct is None:
        return test_cases

    base_table         = struct["base_table"]
    inner_join_tables  = set(struct["inner_join_tables"])
    aliases            = struct["table_aliases"]
    join_conditions    = struct["join_conditions"]
    coalesce_fallbacks = struct["coalesce_fallbacks"]
    between_by_alias   = struct["between_by_alias"]
    join_equalities    = struct["join_equalities"]
    join_inequalities  = struct["join_inequalities"]
    unk_country_cols   = struct["unk_country_cols"]

    if not base_table:
        return test_cases

    def _aliases_of(tbl: str) -> list:
        """Return all non-identity aliases mapped to tbl, in insertion order."""
        return [a for a, t in aliases.items() if t == tbl and a != tbl]

    def _fk_pk_for(dim_table: str) -> tuple:
        """
        Return (base_fk_col, dim_pk_col) for the join between the base table
        and dim_table.  Returns (None, None) when unresolvable.
        """
        dim_aliases  = {a for a, t in aliases.items() if t == dim_table}
        base_aliases = {a for a, t in aliases.items() if t == base_table}
        for a1, c1, a2, c2 in join_conditions:
            if a1 in base_aliases and a2 in dim_aliases:
                return c1, c2
            if a2 in base_aliases and a1 in dim_aliases:
                return c2, c1
        return None, None

    def _minimal_row(dim_alias: str, pk_col: str, pk_val) -> dict:
        """
        Build a minimal seed row for a dimension table identified by dim_alias:
          - PK column set to pk_val
          - All BETWEEN date-range start/end columns with safe date defaults
          - JOIN equality constraints (e.g. geography_type_code = 'CTRY')
          - Placeholder values for JOIN inequality constraints
            (any value that is != the excluded literal)
          - dl_current_indicator = 'Y'
        """
        row: dict = {pk_col: pk_val}
        for start_c, end_c in between_by_alias.get(dim_alias, set()):
            row[start_c] = "2018-01-01"
            row[end_c]   = "2099-12-31"
        for col, val in join_equalities.get(dim_alias, {}).items():
            if col not in row:
                row[col] = val
        for col in join_inequalities.get(dim_alias, {}):
            if col not in row:
                row[col] = f"Test_{col[:20]}"  # any value != the excluded literal
        row.setdefault("dl_current_indicator", "Y")
        return row

    # ── Fix 8: Reserved FK substitution ──────────────────────────────────────
    # Some models have `WHERE pk NOT IN (n1, n2)` in a UNION branch, routing
    # those reserved IDs through a separate CTE path that always produces 0
    # with a single seed row (and then gets filtered out by a `SUM <> 0` guard).
    # Replace any reserved IDs found in the base-table FK column with a safe
    # substitute value, and propagate the substitution to all seed tables and
    # to expected_output / pandas_query so assertions stay consistent.
    not_in_int_cols = struct.get("not_in_int_cols", {})
    if not_in_int_cols:
        for tc in test_cases:
            if not tc.expected_output:
                continue
            base_rows = tc.input_data.get(base_table, [])
            if not base_rows:
                continue
            # Build old→safe substitution map for this TC
            substitutions: dict = {}
            for col, reserved_set in not_in_int_cols.items():
                for row in base_rows:
                    val = row.get(col)
                    if val is None:
                        continue
                    try:
                        val = int(val)
                    except (TypeError, ValueError):
                        continue
                    if val in reserved_set and val not in substitutions:
                        safe_val = max(reserved_set) + 1
                        while safe_val in reserved_set:
                            safe_val += 1
                        substitutions[val] = safe_val
            if not substitutions:
                continue

            def _sub_row(row: dict) -> None:
                """Replace reserved int values in *_uid / *portfolio* columns."""
                for k, v in row.items():
                    if v is None:
                        continue
                    try:
                        iv = int(v)
                    except (TypeError, ValueError):
                        continue
                    if iv in substitutions and (
                        "uid" in k.lower() or "portfolio" in k.lower()
                    ):
                        row[k] = substitutions[iv]

            # Apply to all seed tables
            for rows in tc.input_data.values():
                for row in rows:
                    _sub_row(row)

            # Apply to expected_output
            for row in (tc.expected_output or []):
                _sub_row(row)

            # Apply to pandas_query literals (replace bare integers)
            if tc.pandas_query:
                pq = tc.pandas_query
                for old, new in substitutions.items():
                    pq = re.sub(
                        rf"(?<![\d]){old}(?![\d])", str(new), pq
                    )
                if pq != tc.pandas_query:
                    tc.pandas_query = pq

            for old, new in substitutions.items():
                logger.info(
                    "[dbt-unit-test] ReservedFK-fix: replaced %s→%s in all seed "
                    "tables and expected_output for %s",
                    old, new, tc.test_id,
                )

    for tc in test_cases:
        if not tc.expected_output:
            continue

        base_rows = tc.input_data.get(base_table, [])
        if not base_rows:
            continue
        base0 = base_rows[0]

        # ── Derive effective country from base table's primary UNK-country col ──
        eff_country = "ZZZ"
        for ba in _aliases_of(base_table):
            cols = unk_country_cols.get(ba, [])
            if cols:
                raw_v       = base0.get(cols[0])
                eff_country = "ZZZ" if (raw_v is None or raw_v == "UNK") else raw_v
                break

        # ── Fix 1 + 3: FK presence and PK sync for each INNER JOIN table ──────
        for dim_table in inner_join_tables:
            base_fk_col, dim_pk_col = _fk_pk_for(dim_table)
            if not (base_fk_col and dim_pk_col):
                continue

            dim_rows = tc.input_data.get(dim_table, [])

            # Canonical FK value: prefer base row, then dim row, then 1
            fk_val = (
                base0.get(base_fk_col)
                or (dim_rows[0].get(dim_pk_col) if dim_rows else None)
                or 1
            )

            # Fix 1: add FK col to base rows that are missing it
            for row in base_rows:
                if not row.get(base_fk_col):
                    row[base_fk_col] = fk_val
                    logger.info(
                        "[dbt-unit-test] FK-fix: added %s=%s to %s for %s",
                        base_fk_col, fk_val, base_table, tc.test_id,
                    )
                else:
                    fk_val = row[base_fk_col]  # prefer LLM-provided value

            # Fix 2: back-fill empty INNER JOIN tables
            dim_alias = (_aliases_of(dim_table) or [dim_table])[0]
            if not dim_rows:
                minimal = _minimal_row(dim_alias, dim_pk_col, fk_val)
                # Set country-like cols to effective country
                for cc in unk_country_cols.get(dim_alias, []):
                    minimal[cc] = None if eff_country == "ZZZ" else eff_country
                tc.input_data[dim_table] = [minimal]
                dim_rows = tc.input_data[dim_table]
                logger.info(
                    "[dbt-unit-test] Inner-join-fix: backfilled '%s' seed for %s "
                    "(INNER JOIN table was empty)",
                    dim_table, tc.test_id,
                )

            # Fix 3: sync dim PK to match base FK
            for row in dim_rows:
                if row.get(dim_pk_col) != fk_val:
                    logger.info(
                        "[dbt-unit-test] PK-sync: updated %s.%s %s→%s for %s",
                        dim_table, dim_pk_col, row.get(dim_pk_col), fk_val, tc.test_id,
                    )
                    row[dim_pk_col] = fk_val

        # ── Fix 4: Back-fill COALESCE-joined LEFT JOIN tables ────────────────
        # Pattern: COALESCE(intermediate_dim.fk_col, fallback) = geo_table.pk_col
        for fk_col, fallback_val in coalesce_fallbacks.items():
            for a1, c1, a2, c2 in join_conditions:
                if c1 != fk_col:
                    continue
                geo_table  = aliases.get(a2)
                geo_pk_col = c2
                if not geo_table or geo_table == base_table:
                    continue

                # Prefer actual FK from a seeded intermediate dim table
                geo_uid_val = fallback_val
                for dim_table in inner_join_tables:
                    dim_rows = tc.input_data.get(dim_table, [])
                    if dim_rows and dim_rows[0].get(fk_col) is not None:
                        geo_uid_val = dim_rows[0][fk_col]
                        break

                geo_rows  = tc.input_data.get(geo_table, [])
                geo_alias = (_aliases_of(geo_table) or [geo_table])[0]

                if not geo_rows:
                    minimal_geo = _minimal_row(geo_alias, geo_pk_col, geo_uid_val)
                    minimal_geo.setdefault("iso_alpha_three_country_code", eff_country)
                    tc.input_data[geo_table] = [minimal_geo]
                    logger.info(
                        "[dbt-unit-test] Geo-fix: backfilled '%s' (uid=%s, country=%s) for %s",
                        geo_table, geo_uid_val, eff_country, tc.test_id,
                    )
                else:
                    # Ensure the PK uid column is present in existing rows
                    for row in geo_rows:
                        if row.get(geo_pk_col) is None:
                            row[geo_pk_col] = geo_uid_val
                            logger.info(
                                "[dbt-unit-test] Geo-uid-fix: added %s=%s to '%s' for %s",
                                geo_pk_col, geo_uid_val, geo_table, tc.test_id,
                            )

        # ── Fix 5: Country column alignment ─────────────────────────────────
        # When the primary COALESCE('UNK') country col in the base table is
        # NULL (→ ZZZ), null out secondary country cols in the same alias so
        # all country-aggregation CTEs produce the same iso country code.
        for ba in _aliases_of(base_table):
            cols = unk_country_cols.get(ba, [])
            if len(cols) < 2:
                continue
            primary_col    = cols[0]
            secondary_cols = cols[1:]
            raw_primary = base0.get(primary_col)
            if raw_primary is None or raw_primary == "UNK":
                for row in base_rows:
                    for col in secondary_cols:
                        if row.get(col) not in (None, "UNK"):
                            row[col] = None
                            logger.info(
                                "[dbt-unit-test] Country-align: nulled %s.%s for %s "
                                "(primary %s is NULL → all paths must resolve to ZZZ)",
                                base_table, col, tc.test_id, primary_col,
                            )

        # ── Fix 6: Date coverage — ensure every dimension's BETWEEN range
        # covers the base table's date column value.
        # e.g.  pos.position_date BETWEEN pm.investment_account_funded_date AND ...
        # If the LLM seeded funded_date='2018-01-01' but position_date='2016-04-02',
        # the INNER JOIN silently produces 0 rows.
        base_aliases = {a for a, t in aliases.items() if t == base_table}
        for lhs_a, lhs_c, dim_a, start_c, end_c in struct["range_filter_triplets"]:
            if lhs_a not in base_aliases:
                continue
            dim_table = aliases.get(dim_a)
            if not dim_table:
                continue
            dim_rows = tc.input_data.get(dim_table, [])
            if not dim_rows:
                continue
            # Collect the base date values across all base rows
            base_dates = [str(r[lhs_c]) for r in base_rows if r.get(lhs_c)]
            if not base_dates:
                continue
            min_base_date = min(base_dates)
            max_base_date = max(base_dates)
            for row in dim_rows:
                start_val = str(row.get(start_c) or "")
                end_val   = str(row.get(end_c)   or "")
                if start_val and start_val > min_base_date:
                    logger.info(
                        "[dbt-unit-test] Date-coverage-fix: %s.%s %s → %s to cover "
                        "base date %s for %s",
                        dim_table, start_c, start_val, min_base_date,
                        min_base_date, tc.test_id,
                    )
                    row[start_c] = min_base_date
                if end_val and end_val < max_base_date:
                    row[end_c] = "2099-12-31"
                    logger.info(
                        "[dbt-unit-test] Date-coverage-fix: %s.%s extended to 2099-12-31 "
                        "to cover base date %s for %s",
                        dim_table, end_c, max_base_date, tc.test_id,
                    )

    # ── Fix 7a: Remove CTE-derived tables from input_data ────────────────
    # CTEs are defined inside the SQL WITH block; registering them as
    # TempViews is useless because SparkSQL CTE definitions override any
    # TempView with the same name.  Remove them silently so the executor
    # doesn't try to create those spurious views.
    # Track which test cases had CTE seeds removed — their arithmetic
    # expected values can no longer be trusted.
    cte_names = struct.get("cte_names", set())
    _numeric_cmp_re = re.compile(r"==\s*[\d.]+")
    if cte_names:
        for tc in test_cases:
            cte_removed = False
            for cte_name in list(tc.input_data.keys()):
                if cte_name in cte_names:
                    del tc.input_data[cte_name]
                    cte_removed = True
                    logger.info(
                        "[dbt-unit-test] CTE-cleanup: removed '%s' from input_data "
                        "for %s (CTE, not a source table)",
                        cte_name, tc.test_id,
                    )
            # If a CTE seed was removed AND the pandas_query asserts a
            # specific numeric value, clear it — the arithmetic is likely
            # wrong because the CTE contributes to the computed column.
            if cte_removed and tc.pandas_query and \
                    _numeric_cmp_re.search(tc.pandas_query):
                tc.pandas_query = "False"
                logger.info(
                    "[dbt-unit-test] CTE-cleanup: cleared numeric pandas_query for "
                    "%s (arithmetic assertion may be incorrect after CTE removal)",
                    tc.test_id,
                )

    # ── Fix 7b: CASE WHEN integer-to-integer column mapping correction ───
    # The LLM sometimes seeds the *output* value of a CASE WHEN expression
    # for the *input* column (e.g., setting issuer_uid=212278183 when the
    # CASE WHEN would map issuer_uid=212278183 → aa_portfolio_uid=463906,
    # which then fails to join on aa_portfolio_uid=402325).
    # For each mapping, check that every base-table row has an input_col
    # value that actually produces the expected out_col value via the CASE.
    #
    # Additionally: when CASE WHEN integer mappings feed INTO CTE arithmetic
    # (detected by both case_when_int_mappings and cte_names being non-empty),
    # complex derived columns (e.g. adjusted_aum_usd_amount) cannot be
    # reliably asserted by the LLM-generated pandas_query.  Any test case
    # whose pandas_query asserts a specific numeric value on a column that
    # is NOT the direct out_col of the CASE WHEN is invalidated.
    case_when_mappings = struct.get("case_when_int_mappings", [])
    cte_arithmetic_model = bool(cte_names and case_when_mappings)
    if case_when_mappings and base_table:
        direct_case_cols = {m[4] for m in case_when_mappings if m[4]}  # out_col set
        for tc in test_cases:
            base_rows = tc.input_data.get(base_table, [])
            case_when_corrected = False
            for in_col, if_val, then_val, else_val, out_col, valid_set in case_when_mappings:
                if out_col is None:
                    continue
                for row in base_rows:
                    expected_out = row.get(out_col)
                    current_in   = row.get(in_col)
                    if expected_out is None or current_in is None:
                        continue
                    try:
                        expected_out = int(expected_out)
                        current_in   = int(current_in)
                    except (TypeError, ValueError):
                        continue
                    # What would CASE WHEN produce for this input?
                    produced = then_val if current_in == if_val else else_val
                    if produced == expected_out:
                        continue  # already consistent
                    # Pick the correct input value that produces expected_out
                    if expected_out == then_val:
                        correct_in = if_val
                    else:
                        # else_val branch — pick any valid value that != if_val
                        correct_in = next(
                            (v for v in sorted(valid_set) if v != if_val),
                            None,
                        )
                    if correct_in is not None:
                        row[in_col] = correct_in
                        case_when_corrected = True
                        logger.info(
                            "[dbt-unit-test] CaseWhen-fix: %s.%s %s→%s "
                            "(CASE WHEN must produce %s=%s) for %s",
                            base_table, in_col, current_in, correct_in,
                            out_col, expected_out, tc.test_id,
                        )

            # Invalidate numeric pandas_query assertions when:
            # (a) a CASE WHEN correction was made (cascades through formula), OR
            # (b) the model has CTE arithmetic driven by CASE WHEN mappings AND
            #     the assertion targets a column that is NOT the direct out_col
            #     (i.e. it's a downstream derived value the LLM cannot compute).
            if tc.pandas_query and tc.pandas_query.strip().upper() != "FALSE":
                m = _numeric_cmp_re.search(tc.pandas_query)
                if m:
                    # Extract the column being asserted (simple lhs== pattern)
                    asserted_col_m = re.match(
                        r"(\w+)\s*==", tc.pandas_query.strip()
                    )
                    asserted_col = (
                        asserted_col_m.group(1).lower()
                        if asserted_col_m else None
                    )
                    should_invalidate = case_when_corrected or (
                        cte_arithmetic_model
                        and asserted_col is not None
                        and asserted_col not in direct_case_cols
                    )
                    if should_invalidate:
                        tc.pandas_query = "False"
                        logger.info(
                            "[dbt-unit-test] CaseWhen-fix: cleared pandas_query for "
                            "%s (arithmetic assertion on '%s' invalidated by "
                            "CASE WHEN / CTE formula complexity)",
                            tc.test_id,
                            asserted_col or "<unknown>",
                        )

    alias_cols_map = struct.get("alias_cols", {})

    # ── Fix 2b: Back-fill INNER JOIN tables with BETWEEN-only joins ──────
    # The main loop (Fixes 1-3) skips dim tables whose only join to the
    # base table is a BETWEEN date condition (no equality FK), e.g.
    # currency_v4 joined via  position_date BETWEEN ccy.start AND ccy.end.
    # Without a seed row, the Currency CTE produces 0 rows, which cascades
    # to an empty portfolio_currency_dump and zero final output.
    if inner_join_tables and base_table:
        for tc in test_cases:
            if not tc.expected_output:
                continue
            base_rows_2b = tc.input_data.get(base_table, [])
            if not base_rows_2b:
                continue
            # Quick currency harvest for seeding synthesised rows
            _ccy_harvest: dict = {}
            for rows in tc.input_data.values():
                for row in rows:
                    for k, v in row.items():
                        if (
                            v and isinstance(v, str)
                            and "currency_code" in k.lower()
                            and 1 <= len(v) <= 10
                        ):
                            _ccy_harvest[k] = v
            for dim_table in inner_join_tables:
                if dim_table == base_table:
                    continue
                base_fk, dim_pk = _fk_pk_for(dim_table)
                if base_fk and dim_pk:
                    continue  # already handled by Fix 2
                if tc.input_data.get(dim_table):
                    continue  # already seeded
                dim_alias = (_aliases_of(dim_table) or [dim_table])[0]
                between_cols = between_by_alias.get(dim_alias, set())
                if not between_cols:
                    continue  # no join criteria known; skip
                minimal: dict = {}
                for start_c, end_c in between_cols:
                    minimal[start_c] = "2018-01-01"
                    minimal[end_c]   = "2099-12-31"
                # Fill currency-code and currency-name columns
                for col in alias_cols_map.get(dim_alias, set()):
                    if col in minimal:
                        continue
                    if "currency_code" in col:
                        minimal[col] = _ccy_harvest.get(col, "USD")
                    elif "currency_name" in col:
                        minimal[col] = "Default Currency"
                minimal.setdefault("dl_current_indicator", "Y")
                tc.input_data[dim_table] = [minimal]
                logger.info(
                    "[dbt-unit-test] BetweenJoin-fix: backfilled '%s' "
                    "(BETWEEN-only INNER JOIN) for %s",
                    dim_table, tc.test_id,
                )

    # ── Fix 9: Propagate currency codes to INNER JOIN dim-table rows ─────
    # When a position row has a NULL local currency, the only way the row
    # can contribute to the output is via the base-currency path.  For that
    # join to work, the dim table (e.g. cg_aum_portfolio_product_master_v4)
    # must have `base_iso_alpha_three_currency_code` populated — but the
    # LLM often omits it.
    # Strategy: for every INNER JOIN dim table, look up which alias.col
    # patterns appear in the SQL (via struct["alias_cols"]).  If any of
    # those expected cols contain `_currency_code` and are NULL/absent in
    # the seed row, fill them with the best available currency code found
    # in any other seed table for the same TC.
    # Also applied to base table rows (for local currency code columns).
    if alias_cols_map and base_table:
        for tc in test_cases:
            if not tc.expected_output:
                continue
            base_rows = tc.input_data.get(base_table, [])
            if not base_rows:
                continue

            # Harvest all non-null *_currency_code values from seed tables
            available_ccy: dict = {}  # col_name → value
            for rows in tc.input_data.values():
                for row in rows:
                    for k, v in row.items():
                        if (
                            v
                            and isinstance(v, str)
                            and "currency_code" in k.lower()
                            and 1 <= len(v) <= 10
                        ):
                            available_ccy[k] = v

            if not available_ccy:
                continue

            # Any single currency code to use as fallback
            fallback_ccy = next(iter(available_ccy.values()))

            for dim_table in inner_join_tables:
                dim_rows = tc.input_data.get(dim_table, [])
                if not dim_rows:
                    continue
                dim_aliases = {
                    a for a, t in aliases.items() if t == dim_table
                }
                # Columns expected on this alias per the SQL
                expected_cols: set = set()
                for da in dim_aliases:
                    expected_cols.update(alias_cols_map.get(da, set()))
                ccy_cols = {
                    c for c in expected_cols if "currency_code" in c
                }
                if not ccy_cols:
                    continue

                for row in dim_rows:
                    for col in ccy_cols:
                        if row.get(col) is not None:
                            continue  # already populated
                        # Best match: exact same col name, else fallback
                        val = available_ccy.get(col, fallback_ccy)
                        row[col] = val
                        logger.info(
                            "[dbt-unit-test] CurrencyCode-fix: set %s.%s = '%s' "
                            "for %s (missing currency code column)",
                            dim_table, col, val, tc.test_id,
                        )

            # Apply to base table rows too (e.g. local_iso_alpha_three_currency_code)
            base_aliases = {a for a, t in aliases.items() if t == base_table}
            base_ccy_cols: set = set()
            for ba in base_aliases:
                for col in alias_cols_map.get(ba, set()):
                    if "currency_code" in col:
                        base_ccy_cols.add(col)
            for row in base_rows:
                for col in base_ccy_cols:
                    if row.get(col) is not None:
                        continue
                    val = available_ccy.get(col, fallback_ccy)
                    row[col] = val
                    logger.info(
                        "[dbt-unit-test] CurrencyCode-fix: set base %s.%s = '%s' "
                        "for %s (missing base-table currency code column)",
                        base_table, col, val, tc.test_id,
                    )

    # ── Fix 10: Fill missing numeric measure columns in base table rows ──
    # LLMs sometimes generate base-table seed rows with only key/filter
    # columns, omitting measure columns (e.g. total_usd_market_value_amount).
    # With NULL measures, all AUM aggregations sum to 0, and the final
    # WHERE SUM <> 0 filter removes every row, yielding empty output.
    # Detect via alias.col references in the SQL for base-table aliases.
    _measure_suffix_re = re.compile(
        r"(_amount|_value|_qty|_quantity|_count|_price)$", re.IGNORECASE
    )
    if alias_cols_map and base_table:
        for tc in test_cases:
            if not tc.expected_output:
                continue
            base_rows_10 = tc.input_data.get(base_table, [])
            if not base_rows_10:
                continue
            base_aliases_10 = {a for a, t in aliases.items() if t == base_table}
            measure_cols: set = set()
            for ba in base_aliases_10:
                for col in alias_cols_map.get(ba, set()):
                    if _measure_suffix_re.search(col):
                        measure_cols.add(col)
            if not measure_cols:
                continue
            for row in base_rows_10:
                for col in measure_cols:
                    if row.get(col) is None:
                        row[col] = 1000.0
                        logger.info(
                            "[dbt-unit-test] MeasureFill-fix: set %s.%s = 1000.0 "
                            "for %s (missing numeric measure column)",
                            base_table, col, tc.test_id,
                        )

    return test_cases
