"""
dbt-unit-test PySpark Executor.

Executes a DBT model's raw Jinja SQL against synthetic DataFrames using a
local PySpark session.  This is the most accurate simulation available without
a live database because it uses the **same SQL engine** (Spark SQL) that runs
in production.

Supported SQL constructs:
  - All Spark SQL functions: REPLACE, CASE WHEN, COALESCE, SHA1, CONCAT_WS
  - GROUP BY / aggregate functions (SUM, COUNT, MIN, MAX)
  - Multi-table JOINs (INNER, LEFT, RIGHT, FULL)
  - UNION ALL / INTERSECT
  - CTEs (WITH ... AS (...))
  - Subqueries
  - Window functions (ROW_NUMBER, RANK, LAG, LEAD)
  - CAST expressions and Spark-specific types

Jinja2 stripping supported:
  - {{ config(...) }} blocks
  - {% set var = "..." %} statements (simple string literal values)
  - {{ schema_var }}.{{ 'table_name' }} → table_name
  - {{ source('schema', 'table') }} → table
  - {{ ref('model') }} → model
  - {{ 'literal_string' }} → literal_string
  - Remaining {{ ... }} blocks stripped

Usage
-----
    from engine.execution.spark_executor import PySparkExecutor
    from engine.analysis.model_analyzer import DBTModelAnalyzer

    ctx = DBTModelAnalyzer(project_root=".").analyze("int_cg_aum_by_country_v4")
    executor = PySparkExecutor(ctx)
    result_df = executor.execute({
        "cgam_position_by_activity_date_v4": [...row dicts...],
        "geography_v4":                      [...row dicts...],
        ...
    })
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import pandas as pd

from engine.analysis.model_analyzer import DBTModelContext

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SQL keyword set — used to filter out keywords when extracting column names
# ---------------------------------------------------------------------------

_SQL_KEYWORDS: frozenset[str] = frozenset(
    {
        "SELECT",
        "FROM",
        "WHERE",
        "JOIN",
        "LEFT",
        "RIGHT",
        "INNER",
        "OUTER",
        "FULL",
        "CROSS",
        "ON",
        "AND",
        "OR",
        "NOT",
        "IN",
        "IS",
        "NULL",
        "AS",
        "CASE",
        "WHEN",
        "THEN",
        "ELSE",
        "END",
        "GROUP",
        "BY",
        "ORDER",
        "HAVING",
        "UNION",
        "ALL",
        "DISTINCT",
        "LIMIT",
        "OFFSET",
        "WITH",
        "CREATE",
        "TABLE",
        "VIEW",
        "DROP",
        "INSERT",
        "UPDATE",
        "SET",
        "DELETE",
        "BETWEEN",
        "LIKE",
        "EXISTS",
        "TOP",
        "CAST",
        "DATE",
        "COALESCE",
        "CONCAT_WS",
        "SHA1",
        "UPPER",
        "LOWER",
        "REPLACE",
        "TRIM",
        "MAX",
        "MIN",
        "SUM",
        "COUNT",
        "AVG",
        "ISNULL",
        "NULLIF",
        "INTERSECT",
        "EXCEPT",
        "VALUES",
        "INTO",
        "OVER",
        "PARTITION",
        "ROWS",
        "RANGE",
        "PRECEDING",
        "FOLLOWING",
        "CURRENT",
        "ROW",
        "UNBOUNDED",
        "INTERVAL",
        "STRING",
        "INT",
        "BIGINT",
        "DOUBLE",
        "FLOAT",
        "BOOLEAN",
        "DECIMAL",
        "TIMESTAMP",
        "YEAR",
        "MONTH",
        "DAY",
        "HOUR",
        "MINUTE",
        "SECOND",
        "TRUE",
        "FALSE",
        "FILTER",
        "WINDOW",
        "QUALIFY",
        "LATERAL",
        "APPLY",
        "PIVOT",
        "UNPIVOT",
        "TABLESAMPLE",
        "IF",
        "IFNULL",
        "NVL",
        "DECODE",
        "GREATEST",
        "LEAST",
        "STRUCT",
        "ARRAY",
        "MAP",
        "EXPLODE",
        "LATERAL",
        "ROW_NUMBER",
        "RANK",
        "DENSE_RANK",
        "LAG",
        "LEAD",
        "FIRST_VALUE",
        "LAST_VALUE",
        "NTILE",
    }
)


def _extract_sql_identifiers(sql: str) -> set[str]:
    """
    Extract all word-like identifiers from stripped SQL, excluding SQL keywords.

    Used to detect column names referenced in the SQL so we can pad seed
    DataFrames with NULL columns for any that are missing — preventing Spark
    UNRESOLVED_COLUMN errors at analysis time.
    """
    words = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", sql)
    # Normalise to lowercase — Spark SQL is case-insensitive, so mixed-case
    # variants (e.g. Position_Date, position_Date) must collapse to a single
    # canonical form to avoid AMBIGUOUS_REFERENCE errors when the same
    # logical column appears under multiple cases after column padding.
    return {w.lower() for w in words if w.upper() not in _SQL_KEYWORDS and len(w) > 1}


def _build_alias_table_col_map(
    stripped_sql: str,
    all_table_names: set[str],
) -> dict[str, set[str]]:
    """
    For each known table, return the set of columns that appear in the SQL as
    ``alias.column`` where that alias maps to the table.

    Algorithm
    ---------
    1.  Scan every ``FROM <table> [AS] <alias>`` and ``JOIN <table> [AS] <alias>``
        occurrence in the stripped SQL to build ``alias → table`` pairs.
    2.  For every resolved (alias, table) pair, collect tokens from
        ``alias.<token>`` patterns.
    3.  Return a mapping ``table_name → set[column_name]``.

    This mapping is used during column-padding so that each stub/seeded view is
    only padded with columns that belong to *that* table's alias space —
    preventing AMBIGUOUS_REFERENCE when the same column name would otherwise be
    added to multiple tables in a multi-table JOIN.
    """
    known_lower = {t.lower() for t in all_table_names}

    from_join_re = re.compile(
        r"\b(?:FROM|JOIN)\s+([a-zA-Z_]\w*)\s+(?:AS\s+)?([a-zA-Z_]\w*)"
        r"|,\s*([a-zA-Z_]\w*)\s+(?:AS\s+)?([a-zA-Z_]\w*)",
        re.IGNORECASE,
    )

    # alias → set of tables (an alias may be reused across CTEs for different tables)
    alias_to_tables: dict[str, set[str]] = {}
    for m in from_join_re.finditer(stripped_sql):
        # group(1)/group(2) = FROM/JOIN match; group(3)/group(4) = comma-join match
        tbl = (m.group(1) or m.group(3) or "").lower()
        alias = (m.group(2) or m.group(4) or "").lower()
        if tbl in known_lower and alias and alias not in known_lower:
            alias_to_tables.setdefault(alias, set()).add(tbl)

    table_to_cols: dict[str, set[str]] = {t: set() for t in known_lower}
    for alias, tbls in alias_to_tables.items():
        cols = {
            col_m.group(1).lower()
            for col_m in re.finditer(
                rf"\b{re.escape(alias)}\s*\.\s*([a-zA-Z_]\w*)",
                stripped_sql,
                re.IGNORECASE,
            )
        }
        for tbl in tbls:
            table_to_cols[tbl] |= cols

    # Handle bare (unaliased) table references where columns are unqualified.
    # e.g.  FROM investment_portfolio_am_membership_v4 WHERE dl_current_indicator = 'Y'
    # Only triggered when FROM <table> is immediately followed by WHERE or ON
    # (proving no alias is present), to avoid capturing unrelated identifiers.
    _KW = {
        "select",
        "from",
        "where",
        "join",
        "inner",
        "left",
        "right",
        "outer",
        "full",
        "on",
        "and",
        "or",
        "not",
        "in",
        "is",
        "null",
        "as",
        "by",
        "group",
        "order",
        "having",
        "limit",
        "union",
        "all",
        "distinct",
        "case",
        "when",
        "then",
        "else",
        "end",
        "between",
        "like",
        "cast",
        "with",
        "set",
        "exists",
        "coalesce",
        "over",
        "partition",
        "count",
        "sum",
        "avg",
        "min",
        "max",
        "true",
        "false",
        "asc",
        "desc",
    }
    for tbl_lower in list(known_lower):
        # FROM tablename WHERE/ON ... (no alias between table and keyword)
        no_alias_re = re.compile(
            rf"\bFROM\s+{re.escape(tbl_lower)}\s+(?:WHERE|ON)\s+(.*?)"
            rf"(?=\bFROM\b|\bJOIN\b|\bSELECT\b|\bWITH\b|\bGROUP\b|\))",
            re.IGNORECASE | re.DOTALL,
        )
        for bm in no_alias_re.finditer(stripped_sql):
            clause = bm.group(1)
            for tok in re.findall(r"\b([a-zA-Z_]\w*)\b", clause):
                tok_lower = tok.lower()
                if tok_lower not in _KW and tok_lower not in known_lower and len(tok_lower) > 1:
                    table_to_cols[tbl_lower].add(tok_lower)

    return table_to_cols


def _register_stub_view(spark, name: str, all_columns: set[str]) -> None:
    """
    Register an empty TempView with a comprehensive set of STRING columns.

    Using a full column set (rather than just a _placeholder) lets Spark resolve
    *any* `alias.column_name` expression against the stub view without raising
    UNRESOLVED_COLUMN errors, even when the underlying table was never seeded.
    """
    try:
        from pyspark.sql.types import StringType, StructField, StructType  # type: ignore

        schema = StructType([StructField(c, StringType(), True) for c in sorted(all_columns)])
        stub_sdf = spark.createDataFrame([], schema=schema)
        stub_sdf.createOrReplaceTempView(name)
        logger.debug("Registered stub '%s' with %d cols (explicit schema)", name, len(all_columns))
    except Exception as exc:
        # Absolute fallback: bare _placeholder schema
        logger.warning("Stub registration failed for '%s': %s — using _placeholder", name, exc)
        try:
            spark.sql(
                f"CREATE OR REPLACE TEMP VIEW {name} "
                f"AS SELECT CAST(NULL AS STRING) AS _placeholder WHERE 1=0"
            )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Singleton SparkSession (reuse across test cases to avoid repeated startup)
# ---------------------------------------------------------------------------

_spark_session = None


def _get_spark():
    """Get or create a local SparkSession, reusing across calls (module-level singleton)."""
    global _spark_session
    if _spark_session is not None:
        return _spark_session

    try:
        from pyspark.sql import SparkSession  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "PySpark is not installed. Run: "
            "pip install --index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/ 'pyspark>=3.4.0'"
        ) from exc

    logger.info("Starting local SparkSession for dbt-unit-test …")
    _spark_session = (
        SparkSession.builder.master("local[*]")
        .appName("dbt-unit-test")
        # Fast for small synthetic datasets
        .config("spark.sql.shuffle.partitions", "1")
        # Disable web UI (not needed in test mode)
        .config("spark.ui.enabled", "false")
        .config("spark.driver.memory", "1g")
        # Handle legacy date/timestamp parsing that DBT/Spark SQL uses
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY")
        # Case-insensitive column lookup (matches Spark SQL production behaviour)
        .config("spark.sql.caseSensitive", "false")
        # Show warnings from Spark (suppresses verbose INFO/DEBUG Java logs)
        .getOrCreate()
    )
    _spark_session.sparkContext.setLogLevel("WARN")
    print("[dbt-unit-test] SparkSession started.", flush=True)
    logger.info("SparkSession ready.")
    return _spark_session


# ---------------------------------------------------------------------------
# Jinja2 → Plain SQL stripper
# ---------------------------------------------------------------------------


def _find_config_block_end(sql: str) -> int:
    """
    Find the end position of the {{ config(...) }} block at the top of a DBT SQL file.

    DBT config blocks may contain nested {{ }} expressions (e.g. in post_hook),
    which means a simple non-greedy regex stops at the wrong }}. This function
    walks character-by-character to count {{ / }} brace pairs and returns the
    index just after the outermost closing }}.

    Returns 0 if no config block is found (file starts differently).
    """
    sql_upper = sql.upper()
    # Config block must start with {{ near the beginning of the file
    start = sql.find("{{")
    if start == -1 or start > 5:
        return 0
    # Check that 'config' appears somewhere before the first SQL keyword
    config_keyword_pos = sql_upper.find("CONFIG", start)
    first_sql_pos = min(
        p
        for p in (
            sql_upper.find("WITH "),
            sql_upper.find("SELECT "),
            len(sql),
        )
        if p >= 0
    )
    if config_keyword_pos == -1 or config_keyword_pos > first_sql_pos:
        return 0

    # Walk forward counting {{ and }} pairs
    depth = 0
    i = start
    n = len(sql)
    while i < n:
        if sql[i : i + 2] == "{{":
            depth += 1
            i += 2
        elif sql[i : i + 2] == "}}":
            depth -= 1
            i += 2
            if depth == 0:
                return i  # character AFTER the closing }}
        else:
            i += 1
    return 0  # no matching }} found


def strip_jinja_for_spark(
    raw_sql: str,
    table_registry: dict[str, str] | None = None,
) -> str:
    """
    Convert a DBT Jinja SQL file into plain SQL that Spark can execute.

    Parameters
    ----------
    raw_sql        : Raw DBT SQL with Jinja2 blocks.
    table_registry : Map from resolved table names used in the SQL to the
                     names they are registered under in Spark as TempViews.
                     Usually identity mapping: {'mytable': 'mytable'}.
                     Pass None to use identity mapping (table names kept as-is).

    Returns
    -------
    Plain SQL string with all Jinja2 syntax removed.
    """
    if table_registry is None:
        table_registry = {}

    sql = raw_sql

    # ── Step 1: Strip {{ config(...) }} multiline block ─────────────────
    # DBT config blocks are always at the top of the file.  They may contain
    # nested {{ expr }} calls (e.g. post_hook = ["{{ macro(this) }}"]) which
    # prevent a simple non-greedy regex from finding the true closing }}.
    # Strategy: find the span from the FIRST {{ to the LAST }} that precedes
    # the first SQL keyword (WITH or SELECT), and remove it entirely.
    _config_end = _find_config_block_end(sql)
    if _config_end > 0:
        sql = sql[_config_end:]

    # ── Step 2: Extract {% set var = "value" %} definitions ─────────────
    # Only handles simple string assignments like:
    #   {% set source_schema = "cspn_fndn2_"|string + target.name %}
    # We extract the variable NAME only; the value is a Jinja expression
    # we cannot evaluate at test time.  We record the var name so we can
    # replace {{ var }}.{{ 'table' }} patterns later.
    set_var_names: set[str] = set()
    for m in re.finditer(
        r"\{%-?\s*set\s+(\w+)\s*=.*?-?%\}",
        sql,
        flags=re.DOTALL | re.IGNORECASE,
    ):
        set_var_names.add(m.group(1))

    # Simple string literal sets (e.g. {% set sep = '|' %})
    simple_set_vars: dict[str, str] = {}
    for m in re.finditer(
        r"\{%-?\s*set\s+(\w+)\s*=\s*['\"]([^'\"]+)['\"]\s*-?%\}",
        sql,
        flags=re.IGNORECASE,
    ):
        simple_set_vars[m.group(1)] = m.group(2)

    # ── Step 2b: Strip Jinja schema prefixes  {{ expr }}.  → ""  ───────────
    # e.g.  {{fndn_source_schema}}.instrument_v4  →  instrument_v4
    # This must run before the general {{ }} stripping so the literal dot that
    # follows the expression is consumed in the same pass, avoiding the stray
    # "FROM .tablename" fragments that Step 9 used to clean up.
    sql = re.sub(r"\{\{[^}]*\}\}\.", "", sql)

    # ── Step 3: Strip all {% ... %} block tags (set, if, for, etc.) ─────
    sql = re.sub(r"\{%-?[\s\S]*?-?%\}", "", sql)

    # ── Step 4: Replace schema_var.{{ 'table_name' }} patterns ──────────
    # Pattern: {{ anything }}.{{ 'tablename' }}  (schema + table pair)
    # The schema part is a Jinja expression we discard; keep only the table.
    def _resolve_schema_table(m: re.Match) -> str:
        table_name = m.group(1)
        return table_registry.get(table_name, table_name)

    sql = re.sub(
        r"\{\{[^}]+\}\}\s*\.\s*\{\{\s*['\"](\w+)['\"]\s*\}\}",
        _resolve_schema_table,
        sql,
    )

    # ── Step 5: Replace {{ source('schema', 'table') }} → table ─────────
    # The schema arg may be a quoted string literal OR a bare Jinja variable
    # identifier (e.g. {{ source(fndn_schema, 'table') }}), so accept both.
    sql = re.sub(
        r"\{\{\s*source\s*\(\s*(?:['\"][^'\"]+['\"]|\w+)\s*,\s*['\"](\w+)['\"]\s*\)\s*\}\}",
        lambda m: table_registry.get(m.group(1), m.group(1)),
        sql,
    )

    # ── Step 6: Replace {{ ref('model') }} → model ──────────────────────
    sql = re.sub(
        r"\{\{\s*ref\s*\(\s*['\"](\w+)['\"]\s*\)\s*\}\}",
        lambda m: table_registry.get(m.group(1), m.group(1)),
        sql,
    )

    # ── Step 7: Replace {{ 'literal_string' }} → literal_string ─────────
    # e.g. {{'cgam_position_by_activity_date_v4'}} → cgam_position_by_activity_date_v4
    sql = re.sub(
        r"\{\{\s*['\"](\w+)['\"]\s*\}\}",
        lambda m: m.group(1),
        sql,
    )

    # ── Step 8: Replace remaining {{ var }} using simple_set_vars ────────
    def _resolve_var(m: re.Match) -> str:
        inner = m.group(1).strip()
        # If it's a known simple var, return its value
        if inner in simple_set_vars:
            return simple_set_vars[inner]
        # Known schema set-vars: strip (they were schema prefixes, table already resolved in step 4)
        if inner in set_var_names:
            return ""
        # Unknown expression: strip it
        return ""

    sql = re.sub(r"\{\{([^}]+)\}\}", _resolve_var, sql)

    # ── Step 9a: Replace CAST(''/"" AS DATE/TIMESTAMP) with valid literals ─
    # Jinja runtime-only parameters such as {{dleffectivedate}} reduce to the
    # empty string after Step 8.  The resulting `CAST("" AS DATE)` /
    # `CAST("" AS TIMESTAMP)` causes CAST_INVALID_INPUT at Spark analysis time
    # because an empty string is not a valid date/timestamp literal.
    # Substitute a safe, clearly-sentinel value so the query can still run.
    def _fix_empty_cast(m: re.Match) -> str:
        type_name = m.group(1).upper()
        if type_name.startswith("DATE"):
            return "CURRENT_DATE()"
        return "CURRENT_TIMESTAMP()"

    sql = re.sub(
        r"""CAST\s*\(\s*(?:""|'')\s+AS\s+(TIMESTAMP\w*|DATE)\s*\)""",
        _fix_empty_cast,
        sql,
        flags=re.IGNORECASE,
    )

    # ── Step 9a-ii: Replace to_date("")/to_timestamp("") with valid literals ─
    # Same root cause as 9a: {{partitiondate}} or similar Jinja vars reduce to ""
    # after Step 8, giving to_date("") which Spark rejects with CAST_INVALID_INPUT.
    # Use current_date()/current_timestamp() so the sentinel is always >= seed
    # effectivefromdate values regardless of when the test is run.
    sql = re.sub(
        r"""to_date\s*\(\s*(?:""|'')\s*\)""",
        "current_date()",
        sql,
        flags=re.IGNORECASE,
    )
    sql = re.sub(
        r"""to_timestamp\s*\(\s*(?:""|'')\s*\)""",
        "current_timestamp()",
        sql,
        flags=re.IGNORECASE,
    )

    # ── Step 9b: Replace CAST with TRY_CAST for tolerant simulation ─────
    # In simulation mode, seed data may contain deliberately invalid values
    # (e.g. 'invalid' for a BIGINT column) to verify that rows with bad data
    # are excluded from output.  Spark's hard CAST throws CAST_INVALID_INPUT
    # and kills the *entire* query; TRY_CAST returns NULL instead, allowing
    # WHERE / JOIN / CASE conditions to filter the row gracefully.
    # Step 9a already fixed CAST("" AS DATE) → CURRENT_DATE(), so those are
    # no longer CAST expressions and won't be affected here.
    sql = re.sub(r"\bCAST\s*\(", "TRY_CAST(", sql, flags=re.IGNORECASE)

    # ── Step 9: Clean up double dots and leading/trailing whitespace ─────
    # After stripping schema prefixes we may get "  .tablename" → "tablename"
    sql = re.sub(r"\.\s*\b(\w+)\b", r".\1", sql)  # remove spaces around dots
    sql = re.sub(r"^\s*\.\s*", "", sql, flags=re.MULTILINE)  # dangling leading dot
    # Also handle bare schema-var references like {{source_schema}}.table_name
    # where the table is NOT wrapped in {{''}} — after stripping the schema var
    # to "" we get "FROM .table_name" (dot not at line-start).  Remove the stray
    # dot when it is not preceded by another word character (i.e. not a.b style).
    sql = re.sub(r"(?<![.\w])\.([a-zA-Z_]\w*)", r"\1", sql)

    # Step 9b (alias.* → bare *) intentionally removed: replacing qualified
    # wildcards causes AMBIGUOUS_REFERENCE when the subquery alias `x` and a
    # JOINed table share a column name (e.g. listing_uid in position_accrual_temp).

    # ── Step 9c: Fix empty FROM in CTE definitions (stripped {{ ref(var) }}) ──
    # When a Jinja {{ ref(variable) }} strips to "" in a CTE pattern like:
    #   table_name AS (SELECT * FROM  )
    # the result is an empty FROM clause that causes INVALID_USAGE_OF_STAR_OR_REGEX
    # in Spark.  Replace with a self-reference to the CTE name so the body
    # resolves to the already-registered TempView of the same name.
    # e.g.: investment_portfolio_position_v4 AS ( SELECT * FROM  )
    #    →  investment_portfolio_position_v4 AS ( SELECT * FROM investment_portfolio_position_v4 )
    sql = re.sub(
        r"\b(\w+)\s+AS\s*\(\s*SELECT\s*\*\s*FROM[ \t]+(?=[),])",
        lambda m: f"{m.group(1)} AS ( SELECT * FROM {m.group(1)}",
        sql,
        flags=re.IGNORECASE,
    )

    return sql.strip()


# ---------------------------------------------------------------------------
# Seed-to-TempView name resolver — handles staging ref() indirection
# ---------------------------------------------------------------------------


def _find_ref_for_source(
    source_table: str,
    sql_table_refs: set[str],
    project_root: Path,
) -> str | None:
    """
    Search the models directory: for each sql_table_ref, try to load its .sql
    file and check if it references source_table via {{ ref() }} or
    {{ source(..., 'source_table') }}.  Return the first match.
    """
    source_lower = source_table.lower()
    models_dir = project_root / "models"
    if not models_dir.exists():
        return None

    for candidate in sql_table_refs:
        matches = list(models_dir.rglob(f"{candidate}.sql"))
        for sql_file in matches:
            try:
                content = sql_file.read_text(encoding="utf-8")
            except OSError:
                continue
            if re.search(
                rf"""['\"]{re.escape(source_lower)}['\"]""",
                content,
                re.IGNORECASE,
            ):
                return candidate
    return None


def _resolve_seed_to_tempview_names(
    input_data: dict[str, list],
    stripped_sql: str,
    project_root: Path,
) -> dict[str, list]:
    """
    Re-key input_data so every key matches a table/view name that actually
    appears in the stripped SQL.

    Handles the common pattern where the agent seeds with a raw source/ingestion
    table name (e.g. workday_associates_demographic_f1_v1_t1) but the integration
    model SQL references it via a staging ref() (e.g. stage_cg_associates_v4).
    Seeds whose key already matches a SQL identifier are kept unchanged.
    Seeds with no match are kept under their original key with a warning.
    """
    from_join_re = re.compile(r"\b(?:FROM|JOIN)\s+([a-zA-Z_]\w*)", re.IGNORECASE)
    sql_table_refs = {m.group(1).lower() for m in from_join_re.finditer(stripped_sql)}

    result: dict[str, list] = {}
    for seed_key, rows in input_data.items():
        seed_lower = seed_key.lower()
        if seed_lower in sql_table_refs:
            # Key already matches a SQL-referenced table — keep as-is
            result[seed_key] = rows
            continue

        matched = _find_ref_for_source(
            source_table=seed_key,
            sql_table_refs=sql_table_refs,
            project_root=project_root,
        )
        if matched:
            logger.debug(
                "[dbt-unit-test] Remapping seed '%s' → '%s' (source found via ref chain)",
                seed_key,
                matched,
            )
            result[matched] = rows
        else:
            logger.warning(
                "[dbt-unit-test] Seed table '%s' not found in SQL refs %s "
                "and no ref chain match found. Output may be empty.",
                seed_key,
                sql_table_refs,
            )
            result[seed_key] = rows

    return result


# ---------------------------------------------------------------------------
# Main executor class
# ---------------------------------------------------------------------------


class PySparkExecutor:
    """
    Execute a DBT model SQL (with Jinja) against synthetic DataFrames using
    a local PySpark session.

    Parameters
    ----------
    model_context : DBTModelContext produced by DBTModelAnalyzer.
    verbose       : If True, log the cleaned SQL before execution.
    """

    def __init__(self, model_context: DBTModelContext, verbose: bool = False):
        self.ctx = model_context
        self.verbose = verbose

    def execute(self, input_data: dict[str, list[dict[str, Any]]]) -> pd.DataFrame:
        """
        Execute the full DBT model SQL against synthetic seed DataFrames.

        Parameters
        ----------
        input_data : dict
            Keys are the source/ref table names as they appear in the SQL after
            Jinja stripping (e.g. 'cgam_position_by_activity_date_v4').
            Values are lists of row dicts (same format as LLM-generated seeds).

        Returns
        -------
        pd.DataFrame with the full SQL result — same column names and
        transformations as the real production run.
        """
        spark = _get_spark()

        # Build table registry, disambiguating tables whose names collide with CTE
        # names.  DBT patterns like "WITH STAGE_TABLE AS (SELECT ... FROM stage_table)"
        # create a name that Spark (case-insensitive) treats as self-referential, so
        # columns inside the CTE become UNRESOLVED.  Rename colliding seed TempViews
        # to <name>_src so the inner FROM resolves to the TempView, not the CTE.
        _cte_names: set[str] = {
            m.lower()
            for m in re.findall(r"\bWITH\s+(\w+)\s+AS\s*\(", self.ctx.raw_sql, re.IGNORECASE)
        } | {m.lower() for m in re.findall(r",\s*(\w+)\s+AS\s*\(", self.ctx.raw_sql, re.IGNORECASE)}
        table_registry: dict[str, str] = {
            t: (t + "_src" if t.lower() in _cte_names else t) for t in input_data
        }
        for _orig, _renamed in table_registry.items():
            if _orig != _renamed:
                logger.debug(
                    "Renamed seed TempView '%s' → '%s' to avoid CTE name collision",
                    _orig,
                    _renamed,
                )

        # Remap seed keys that don't match any SQL-referenced table name.
        # Handles the common pattern where the agent seeds with a raw source table
        # name but the integration model SQL references it via a staging ref().
        input_data = _resolve_seed_to_tempview_names(
            input_data=input_data,
            stripped_sql=strip_jinja_for_spark(self.ctx.raw_sql, table_registry),
            project_root=self.ctx.project_root,
        )
        # Rebuild table_registry after remapping (new keys may or may not be CTE names)
        table_registry = {t: (t + "_src" if t.lower() in _cte_names else t) for t in input_data}

        # -------------------------------------------------------------
        # 1. Register every seed as a Spark TempView
        # -------------------------------------------------------------
        # all_known_tables: original seed names + any _src-renamed counterparts,
        # so section 2's stub registration doesn't overwrite seeded TempViews.
        all_known_tables = set(input_data.keys()) | set(table_registry.values())

        # Pre-compute Jinja-stripped SQL so we can extract all identifiers
        # for the column-padding step below.  Use table_registry so that CTE-
        # colliding table names are already resolved to their _src counterparts.
        _clean_sql_for_pad = strip_jinja_for_spark(self.ctx.raw_sql, table_registry)
        _all_sql_identifiers = _extract_sql_identifiers(_clean_sql_for_pad)

        # Collect every column already present in ANY seeded table.
        # Normalise to lowercase to match the lowercase identifiers produced by
        # _extract_sql_identifiers — prevents mixed-case variants of the same
        # column (e.g. position_date / Position_Date) from surviving set
        # subtraction and being re-added as spurious pad columns.
        _all_seeded_cols: set[str] = set()
        for rows in input_data.values():
            if rows:
                _all_seeded_cols |= {c.lower() for c in pd.DataFrame(rows).columns}

        # Identifiers that are not owned by any seed — these are safe to
        # pad on every table that is missing them.
        _known_lower = {t.lower() for t in all_known_tables}
        # Also extract the left-hand side of every dot expression (e.g. ptlm in
        # ptlm.portfolio_uid) — these are table aliases / CTE names, NOT column
        # names.  Excluding them from _safe_pad_cols prevents Spark from finding
        # a STRING column named "ptlm" when it tries to resolve ptlm.portfolio_uid,
        # which would cause INVALID_EXTRACT_BASE_FIELD_TYPE.
        _dot_aliases: set[str] = {
            m.lower() for m in re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\.", _clean_sql_for_pad)
        }
        _safe_pad_cols = _all_sql_identifiers - _all_seeded_cols - _known_lower - _dot_aliases

        # Build alias-based column map: for each table, the set of columns
        # referenced as alias.column in the SQL.  Used to restrict per-table
        # padding so that a column owned by one table's alias (e.g.
        # l.swap_leg_type_code → listing_v4) is NOT padded onto other tables
        # in the same JOIN, which would otherwise cause AMBIGUOUS_REFERENCE
        # when the column is referenced without a table qualifier in WHERE.
        _all_sql_tables_lower = {t.lower() for t in all_known_tables} | {
            re.sub(r"[^a-zA-Z0-9_]", "_", t).lower()
            for t in _extract_table_names_from_sql(self.ctx.raw_sql) - all_known_tables
        }
        # Also include tables that only appear in the stripped SQL (e.g. CTE names
        # whose FROM came from a Jinja variable ref like {{ ref(accrual_table) }}
        # and were fixed to self-refs by step 9c).
        _plain_from_re_alias = re.compile(
            r"\bFROM\s+([a-zA-Z_]\w*)\b|\bJOIN\s+([a-zA-Z_]\w*)\b", re.IGNORECASE
        )
        for _m in _plain_from_re_alias.finditer(_clean_sql_for_pad):
            _tbl = (_m.group(1) or _m.group(2) or "").lower()
            if _tbl:
                _all_sql_tables_lower.add(_tbl)
        _alias_col_map = _build_alias_table_col_map(_clean_sql_for_pad, _all_sql_tables_lower)
        # Columns claimed by at least one alias → must NOT be freely padded
        _cols_owned_by_alias: set[str] = set().union(*_alias_col_map.values())
        # Columns that appear bare (not dot-qualified) anywhere in the SQL.
        # These may legitimately belong to multiple tables (e.g. shared join-key
        # columns like portfolio_uid in a CTE SELECT list without a table qualifier).
        # Only columns that NEVER appear bare are safe to attribute exclusively to one alias.
        _bare_cols: set[str] = {
            m.group(1).lower()
            for m in re.finditer(r"(?<![.\w])([a-zA-Z_]\w*)\b(?!\s*\()", _clean_sql_for_pad)
            if m.group(1).upper() not in _SQL_KEYWORDS
        }
        _exclusively_qualified_cols: set[str] = _cols_owned_by_alias - _bare_cols
        # Detect output column aliases — names CREATED by the SQL transformation,
        # not read from source tables.  Padding them would cause AMBIGUOUS_REFERENCE
        # when a CTE does SELECT * and the same alias is also created explicitly.
        # E.g. "ins.primaryinstrumenttypecode primaryinstrumenttypecode_src" →
        # "primaryinstrumenttypecode_src" must not be padded onto inse's TempView.
        _SQL_KW = {
            "on",
            "and",
            "or",
            "where",
            "from",
            "join",
            "inner",
            "left",
            "right",
            "outer",
            "full",
            "cross",
            "group",
            "order",
            "having",
            "limit",
            "union",
            "select",
            "with",
            "as",
            "not",
            "in",
            "is",
            "null",
            "by",
            "between",
            "case",
            "when",
            "then",
            "else",
            "end",
            "distinct",
            "all",
            "exists",
            "using",
            "set",
            "insert",
            "into",
            "values",
            "over",
            "partition",
        }
        _col_aliases: set[str] = set()
        # Pattern 1: explicit AS alias_name
        for _m in re.finditer(r"\bAS\s+([a-zA-Z_]\w*)", _clean_sql_for_pad, re.IGNORECASE):
            _w = _m.group(1).lower()
            if _w not in _SQL_KW:
                _col_aliases.add(_w)
        # Pattern 2: implicit alias — "alias.col output_name" (no AS keyword)
        for _m in re.finditer(
            r"[a-zA-Z_]\w*\.[a-zA-Z_]\w*[ \t]+([a-zA-Z_]\w*)", _clean_sql_for_pad
        ):
            _w = _m.group(1).lower()
            if _w not in _SQL_KW:
                _col_aliases.add(_w)
        # Columns in _safe_pad_cols that are NOT claimed by any alias and NOT
        # output aliases: truly unowned identifiers safe to pad onto every view.
        _unowned_safe_cols = _safe_pad_cols - _cols_owned_by_alias - _col_aliases

        for table_name, rows in input_data.items():
            if rows:
                pdf = pd.DataFrame(rows)
                # Deduplicate columns that may have slipped in from CSV
                # parsing (e.g. "position_date", "position_date.1", …).
                pdf = pdf.loc[:, ~pdf.columns.duplicated()]
                # Strip out columns that the LLM seeded into the WRONG table.
                # If a column (e.g. swap_leg_type_code) is claimed exclusively
                # by another table's alias in the SQL, keeping it in this seed
                # DataFrame would cause AMBIGUOUS_REFERENCE in multi-table JOINs.
                # Remove any column from this table's seed that is owned by
                # another table's alias but NOT this table's own alias.
                # Use _exclusively_qualified_cols (not _cols_owned_by_alias) so
                # that columns appearing bare somewhere in the SQL (e.g. shared
                # join keys in CTE SELECT lists) are NEVER stripped — they may
                # legitimately belong to multiple tables.
                _this_alias_cols = _alias_col_map.get(table_name.lower(), set())
                _cols_owned_by_others = _exclusively_qualified_cols - _this_alias_cols
                if _cols_owned_by_others:
                    keep = [c for c in pdf.columns if c.lower() not in _cols_owned_by_others]
                    removed = [c for c in pdf.columns if c.lower() in _cols_owned_by_others]
                    if removed:
                        logger.debug(
                            "Dropped foreign-alias cols from seed '%s': %s",
                            table_name,
                            removed,
                        )
                    pdf = pdf[keep]
                # Pad this seed with:
                #   • columns referenced via this table's own alias in the SQL, AND
                #   • "unowned" safe identifiers (not claimed by any alias), AND
                #   • all explicitly seeded columns (so JOIN keys resolve across
                #     tables).
                # This is narrower than the old _all_sql_identifiers approach but
                # prevents AMBIGUOUS_REFERENCE in multi-table JOINs where the same
                # column name is otherwise padded onto every joined table.
                existing_cols = {c.lower() for c in pdf.columns}
                _per_table_pad_cols = (
                    (_alias_col_map.get(table_name.lower(), set()) | _unowned_safe_cols)
                    - _known_lower
                    - _dot_aliases
                )
                missing_cols = _per_table_pad_cols - existing_cols
                if missing_cols:
                    null_df = pd.DataFrame(
                        None,  # NULL — safe now that createDataFrame uses explicit STRING schema
                        index=pdf.index,
                        columns=sorted(missing_cols),
                    )
                    pdf = pd.concat([pdf, null_df], axis=1)
                    logger.debug("Padded '%s' with NULL cols: %s", table_name, sorted(missing_cols))
                # Also pad with all columns from the staging SQL schema.
                # This handles CTE-chained tables where _build_alias_table_col_map
                # cannot trace the alias path (e.g., stage_X → CTE inst → alias ins).
                _schema_cols = {
                    col.lower() for col in self.ctx.source_table_schemas.get(table_name, {})
                }
                _schema_missing = _schema_cols - {c.lower() for c in pdf.columns}
                if _schema_missing:
                    _null_df = pd.DataFrame(None, index=pdf.index, columns=sorted(_schema_missing))
                    pdf = pd.concat([pdf, _null_df], axis=1)
                    logger.debug(
                        "Padded '%s' with %d staging-schema NULL cols: %s",
                        table_name,
                        len(_schema_missing),
                        sorted(_schema_missing),
                    )
                # Build explicit STRING schema so Spark never infers DOUBLE
                # from float NaN (blank CSV cells) or from padded empty strings.
                # NaN/None values become SQL NULL; Spark casts them as needed.
                try:
                    from pyspark.sql.types import (  # type: ignore
                        StringType,
                        StructField,
                        StructType,
                    )

                    schema = StructType([StructField(c, StringType(), True) for c in pdf.columns])

                    # Serialise each cell to string or None (for blank CSV fields)
                    def _cell(v):
                        if v is None or (isinstance(v, float) and pd.isna(v)):
                            return None
                        return "" if v == "" else str(v)

                    data_rows = [[_cell(v) for v in row] for row in pdf.values.tolist()]
                    sdf = spark.createDataFrame(data_rows, schema=schema)
                    _view_name = table_registry.get(table_name, table_name)
                    sdf.createOrReplaceTempView(_view_name)
                    logger.debug(
                        "Registered TempView '%s' (%d rows, cols: %s)",
                        _view_name,
                        sdf.count(),
                        sdf.columns,
                    )
                except Exception as e:
                    logger.warning(
                        "Could not register TempView '%s': %s — using stub view",
                        table_name,
                        e,
                    )
                    _schema_cols_stub = {
                        col.lower() for col in self.ctx.source_table_schemas.get(table_name, {})
                    }
                    # Pad stubs with EVERY identifier seen in the SQL — narrower
                    # alias-only padding leaves bare-referenced columns unresolved
                    # when the stub is used as a fallback.
                    _tbl_cols = (
                        (_all_sql_identifiers | _schema_cols_stub) - _known_lower - _dot_aliases
                    )
                    _register_stub_view(
                        spark, table_registry.get(table_name, table_name), _tbl_cols
                    )
            else:
                # No rows seeded — register a stub with EVERY identifier seen
                # in the SQL so alias.column AND bare column refs resolve
                # without UNRESOLVED_COLUMN errors.
                _schema_cols_stub = {
                    col.lower() for col in self.ctx.source_table_schemas.get(table_name, {})
                }
                _tbl_cols = (_all_sql_identifiers | _schema_cols_stub) - _known_lower - _dot_aliases
                _register_stub_view(spark, table_registry.get(table_name, table_name), _tbl_cols)
                logger.debug("Registered empty TempView '%s' (no rows)", table_name)

        # -------------------------------------------------------------
        # 2. Also register stub views (with comprehensive schema) for
        #    tables referenced in the SQL that were NOT seeded — this
        #    lets JOINs produce 0 rows rather than crashing with
        #    UNRESOLVED_COLUMN when the SQL accesses alias.column_name.
        # Also include tables from the STRIPPED SQL: strip_jinja_for_spark
        # may introduce new table references (e.g., Step 9c self-referencing
        # CTEs for {{ ref(variable) }} patterns), which won't appear in raw_sql.
        # Use a plain FROM/JOIN extractor for the stripped SQL.
        # -------------------------------------------------------------
        all_sql_tables = _extract_table_names_from_sql(self.ctx.raw_sql)
        # Supplement with plain FROM/JOIN references in the stripped SQL
        _plain_from_re = re.compile(
            r"\bFROM\s+([a-zA-Z_]\w*)\b|\bJOIN\s+([a-zA-Z_]\w*)\b", re.IGNORECASE
        )
        for m in _plain_from_re.finditer(_clean_sql_for_pad):
            tbl = m.group(1) or m.group(2)
            if tbl:
                all_sql_tables.add(tbl)
        for tbl in all_sql_tables - all_known_tables:
            safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", tbl)
            _schema_cols_s2 = {
                col.lower() for col in self.ctx.source_table_schemas.get(safe_name, {})
            }
            # Same rationale as the seeded-table stub paths: pad with EVERY
            # identifier seen in the SQL so unseeded tables can still satisfy
            # bare and alias-qualified column references.
            _stub_cols = (_all_sql_identifiers | _schema_cols_s2) - _known_lower - _dot_aliases
            _register_stub_view(spark, safe_name, _stub_cols)
            logger.debug("Registered stub TempView '%s' for unseeded table", safe_name)

        # -------------------------------------------------------------
        # 3. Strip Jinja2 → Plain Spark SQL (reuse already-computed strip)
        # -------------------------------------------------------------
        clean_sql = _clean_sql_for_pad  # already stripped above for identifier extraction

        if self.verbose or logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "\n%s\nSpark SQL (Jinja stripped) for '%s':\n%s\n%s",
                "=" * 70,
                self.ctx.model_name,
                clean_sql,
                "=" * 70,
            )

        # -------------------------------------------------------------
        # 4. Execute via Spark SQL
        # -------------------------------------------------------------
        print(f"[dbt-unit-test] Running query: '{self.ctx.model_name}' …", flush=True)
        logger.info("Executing '%s' via local Spark SQL …", self.ctx.model_name)
        try:
            result_sdf = spark.sql(clean_sql)
            result_pdf = result_sdf.toPandas()
            # Spark DECIMAL columns become Python decimal.Decimal objects in pandas
            # (stored as object dtype). Convert them to float64 so that pandas_query
            # comparisons like `col == 1100.0` work correctly.
            import decimal as _decimal

            for _col in result_pdf.columns:
                if result_pdf[_col].dtype == object and len(result_pdf) > 0:
                    _sample = result_pdf[_col].dropna()
                    if len(_sample) > 0 and isinstance(_sample.iloc[0], _decimal.Decimal):
                        result_pdf[_col] = result_pdf[_col].apply(
                            lambda v: float(v) if isinstance(v, _decimal.Decimal) else v
                        )
            print(
                f"[dbt-unit-test] Query execution completed — "
                f"{len(result_pdf)} rows, {len(result_pdf.columns)} columns",
                flush=True,
            )
            logger.info(
                "Spark execution successful — %d rows, %d columns for '%s'",
                len(result_pdf),
                len(result_pdf.columns),
                self.ctx.model_name,
            )
            return result_pdf
        except Exception as exc:
            clean_preview = clean_sql[:800]
            print(
                f"[dbt-unit-test] Query FAILED for '{self.ctx.model_name}': {exc}",
                flush=True,
            )
            logger.error(
                "Spark SQL execution failed for '%s':\n%s\n\nSQL (first 800 chars):\n%s",
                self.ctx.model_name,
                exc,
                clean_preview,
            )
            raise RuntimeError(
                f"PySparkExecutor failed for '{self.ctx.model_name}':\n{exc}"
            ) from exc


# ---------------------------------------------------------------------------
# Helper: extract table names referenced in DBT SQL
# ---------------------------------------------------------------------------

# Pattern: {{ schema_var }}.{{ 'table_name' }}
_SCHEMA_TABLE_JINJA_RE = re.compile(
    r"\{\{[^}]+\}\}\s*\.\s*\{\{\s*['\"](\w+)['\"]\s*\}\}",
)
# Pattern: {{schema_var}}.bare_table_name  (table NOT wrapped in {{''}})
_SCHEMA_BARE_TABLE_JINJA_RE = re.compile(
    r"\{\{[^}]+\}\}\s*\.\s*([a-zA-Z_]\w*)",
)
# Pattern: {{ source('schema', 'table') }}
_SOURCE_JINJA_RE = re.compile(
    r"\{\{\s*source\s*\(\s*['\"][^'\"]+['\"]\s*,\s*['\"](\w+)['\"]\s*\)\s*\}\}",
)
# Pattern: {{ ref('model') }}
_REF_JINJA_RE = re.compile(
    r"\{\{\s*ref\s*\(\s*['\"](\w+)['\"]\s*\)\s*\}\}",
)
# Pattern: {{ 'literal_table_name' }}  (standalone)
_LITERAL_TABLE_JINJA_RE = re.compile(
    r"\{\{\s*['\"](\w+)['\"]\s*\}\}",
)


def _extract_table_names_from_sql(raw_sql: str) -> set[str]:
    """
    Extract all source / ref / literal table names referenced in a DBT Jinja SQL.

    Returns a set of plain table names (no schema prefix, no Jinja brackets).
    """
    tables: set[str] = set()
    tables.update(_SCHEMA_TABLE_JINJA_RE.findall(raw_sql))
    tables.update(_SCHEMA_BARE_TABLE_JINJA_RE.findall(raw_sql))
    tables.update(_SOURCE_JINJA_RE.findall(raw_sql))
    tables.update(_REF_JINJA_RE.findall(raw_sql))
    tables.update(_LITERAL_TABLE_JINJA_RE.findall(raw_sql))
    return tables


def extract_source_tables(raw_sql: str) -> list[str]:
    """
    Public helper: return sorted list of all source/ref table names in a DBT SQL.

    Used by model_analyzer to populate DBTModelContext.source_tables and by
    ai_test_case_generator to tell the LLM which seed table names to use.
    """
    return sorted(_extract_table_names_from_sql(raw_sql))
