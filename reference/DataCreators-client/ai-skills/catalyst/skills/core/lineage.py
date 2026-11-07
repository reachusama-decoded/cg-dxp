"""Core function: SQL column-level lineage tracer.

Pure function — no external calls, no I/O.
Ported from edo-ai-skills column_lineage.py.
"""

from __future__ import annotations

import re
from collections import OrderedDict


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AGG_FUNCTIONS = {
    "COUNT", "SUM", "AVG", "MIN", "MAX", "MEDIAN", "STDDEV", "VARIANCE",
    "LISTAGG", "STRING_AGG", "ARRAY_AGG", "GROUP_CONCAT",
    "APPROX_COUNT_DISTINCT", "HLL", "PERCENTILE_CONT", "PERCENTILE_DISC",
    "ANY_VALUE", "BOOL_OR", "BOOL_AND", "BIT_OR", "BIT_AND",
}

WINDOW_FUNCTIONS = {
    "ROW_NUMBER", "RANK", "DENSE_RANK", "NTILE", "PERCENT_RANK", "CUME_DIST",
    "LAG", "LEAD", "FIRST_VALUE", "LAST_VALUE", "NTH_VALUE",
}

_SQL_KEYWORDS = {
    "FROM", "WHERE", "JOIN", "ON", "AND", "OR", "NOT", "IN", "AS",
    "GROUP", "ORDER", "HAVING", "LIMIT", "UNION", "EXCEPT", "INTERSECT",
    "INNER", "LEFT", "RIGHT", "FULL", "OUTER", "CROSS", "NATURAL",
    "CASE", "WHEN", "THEN", "ELSE", "END", "BETWEEN", "LIKE", "IS",
    "NULL", "TRUE", "FALSE", "OVER", "PARTITION", "BY", "ASC", "DESC",
    "DISTINCT", "ALL", "EXISTS", "ANY", "SOME",
}

_TRANSFORM_PATTERNS = [
    (re.compile(r"\bCASE\b", re.I), "CONDITIONAL"),
    (re.compile(r"\bCOALESCE\b", re.I), "CONDITIONAL"),
    (re.compile(r"\bIFF?\b", re.I), "CONDITIONAL"),
    (re.compile(r"\bNVL\b", re.I), "CONDITIONAL"),
    (re.compile(r"\|\|"), "CONCAT"),
    (re.compile(r"\bCONCAT\b", re.I), "CONCAT"),
    (re.compile(r"[+\-*/]"), "ARITHMETIC"),
    (re.compile(r"\bCAST\b", re.I), "CAST"),
    (re.compile(r"::"), "CAST"),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def trace_lineage(sql: str) -> dict:
    """Parse SQL and extract column-level lineage.

    Handles CTEs, JOINs, aggregations, window functions, aliases, and
    table-qualified column references.

    Args:
        sql: A single SQL statement (SELECT or WITH...SELECT).

    Returns:
        dict with keys:
          ctes (list[str]): Names of CTEs defined in WITH clause.
          from_tables (list[dict]): Source tables/aliases from FROM/JOIN clauses.
            Each dict: {table: str, alias: str}.
          column_lineage (list[dict]): Per-output-column lineage entries.
            Each dict: {output_column, expression, transform, sources}.
            sources is a list of {table, column, resolved_table?, is_cte?}.
    """
    clean = _strip_comments(sql).strip()

    ctes = _extract_ctes(clean)

    # Find the final SELECT (past the WITH block)
    final_sql = _get_final_select(clean, ctes)

    columns = _extract_select_columns(final_sql)
    from_tables = _extract_from_tables(final_sql)

    lineage = []
    for col_expr in columns:
        parsed = _parse_column_expr(col_expr)

        # Resolve table aliases
        for src in parsed["sources"]:
            if src["table"]:
                for t in from_tables:
                    if t["alias"] == src["table"]:
                        src["resolved_table"] = t["table"]
                        break
                else:
                    src["resolved_table"] = src["table"]

                cte_name = src["table"]
                resolved = src.get("resolved_table", "")
                if cte_name in ctes or resolved.lower() in ctes:
                    src["is_cte"] = True

        lineage.append(parsed)

    return {
        "ctes": list(ctes.keys()),
        "from_tables": from_tables,
        "column_lineage": lineage,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _strip_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    sql = re.sub(r"--[^\n]*", "", sql)
    return sql


def _strip_strings(sql: str) -> str:
    return re.sub(r"'[^']*'", "'__STR__'", sql)


def _extract_ctes(sql: str) -> OrderedDict:
    """Extract CTE names and their SQL bodies from a WITH clause."""
    ctes: OrderedDict = OrderedDict()
    clean = sql.strip()

    if not re.match(r"\s*WITH\b\s+", clean, re.I):
        return ctes

    rest = re.sub(r"^\s*WITH\b\s+", "", clean, count=1, flags=re.I)

    while rest:
        m = re.match(r"\s*(\w+)\s+AS\s*\(", rest, re.I)
        if not m:
            break
        cte_name = m.group(1)
        depth = 1
        pos = m.end()
        while pos < len(rest) and depth > 0:
            if rest[pos] == "(":
                depth += 1
            elif rest[pos] == ")":
                depth -= 1
            pos += 1
        cte_body = rest[m.end() : pos - 1]
        ctes[cte_name.lower()] = cte_body.strip()
        rest = rest[pos:].lstrip()
        if rest.startswith(","):
            rest = rest[1:]

    return ctes


def _get_final_select(sql: str, ctes: OrderedDict) -> str:
    """Return the final SELECT statement, stripped of the WITH...CTEs preamble."""
    if not ctes:
        return sql

    depth = 0
    in_with = False
    for i, char in enumerate(sql):
        if sql[i : i + 4].upper() == "WITH" and (i == 0 or not sql[i - 1].isalnum()):
            in_with = True
            continue
        if in_with:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    rest = sql[i + 1 :].lstrip()
                    if rest and rest[0] == ",":
                        continue
                    return rest
    return sql


def _extract_select_columns(sql: str) -> list[str]:
    """Extract column expressions from the SELECT clause."""
    clean = _strip_comments(sql).strip()

    select_match = re.match(
        r"\s*SELECT\s+(?:DISTINCT\s+|ALL\s+)?(.*?)\bFROM\b",
        clean,
        re.I | re.DOTALL,
    )
    if not select_match:
        select_match = re.match(
            r"\s*SELECT\s+(?:DISTINCT\s+|ALL\s+)?(.*)",
            clean,
            re.I | re.DOTALL,
        )
        if not select_match:
            return []

    select_body = select_match.group(1).strip()

    columns: list[str] = []
    depth = 0
    current: list[str] = []
    for char in select_body:
        if char == "(":
            depth += 1
            current.append(char)
        elif char == ")":
            depth -= 1
            current.append(char)
        elif char == "," and depth == 0:
            columns.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        remaining = "".join(current).strip()
        if remaining:
            columns.append(remaining)

    return columns


def _parse_column_expr(expr: str) -> dict:
    """Parse a single SELECT column expression into source references and alias."""
    expr = expr.strip()

    alias_match = re.match(
        r"(.+?)\s+AS\s+[`\"]?(\w+)[`\"]?\s*$", expr, re.I | re.DOTALL
    )
    if not alias_match:
        alias_match = re.match(r"(.+?)\s+([a-zA-Z_]\w*)\s*$", expr, re.I | re.DOTALL)
        if alias_match:
            alias_cand = alias_match.group(2).upper()
            if alias_cand in _SQL_KEYWORDS:
                alias_match = None

    if alias_match:
        expression = alias_match.group(1).strip()
        alias = alias_match.group(2).strip().strip('"').strip("`")
    else:
        expression = expr
        if re.match(r"^(\w+\.)?(\w+)$", expr):
            alias = expr.split(".")[-1]
        else:
            alias = expr

    # Extract column references
    sources: list[dict] = []
    clean_expr = _strip_strings(expression)

    for m in re.finditer(r"\b(\w+)\.(\w+)\b", clean_expr):
        table_ref = m.group(1).lower()
        col_ref = m.group(2).lower()
        if table_ref.upper() in AGG_FUNCTIONS or table_ref.upper() in WINDOW_FUNCTIONS:
            continue
        sources.append({"table": table_ref, "column": col_ref})

    if not sources:
        bare = re.sub(
            r"\b(?:" + "|".join(AGG_FUNCTIONS | WINDOW_FUNCTIONS) + r")\s*\(",
            "(",
            clean_expr,
            flags=re.I,
        )
        bare = re.sub(
            r"\b(?:CASE|WHEN|THEN|ELSE|END|AND|OR|NOT|IS|NULL|AS|OVER|PARTITION|BY"
            r"|ORDER|ASC|DESC|ROWS|RANGE|BETWEEN|UNBOUNDED|PRECEDING|FOLLOWING"
            r"|CURRENT|ROW)\b",
            "",
            bare,
            flags=re.I,
        )
        bare = re.sub(r"'__STR__'", "", bare)
        bare = re.sub(r"\b\d+\b", "", bare)
        for m in re.finditer(r"\b([a-zA-Z_]\w*)\b", bare):
            col = m.group(1).lower()
            if len(col) > 1:
                sources.append({"table": None, "column": col})

    transform = _detect_transform(expression, sources)
    if transform == "PASS-THROUGH" and sources and alias.lower() != sources[0]["column"]:
        transform = "RENAME"

    return {
        "output_column": alias,
        "expression": expression,
        "transform": transform,
        "sources": sources,
    }


def _detect_transform(expression: str, sources: list[dict]) -> str:
    """Classify the transformation type of a column expression."""
    # SELECT *
    if expression.strip() == "*" or re.match(r"^\w+\.\*$", expression.strip()):
        return "STAR"

    # Literal/constant
    if re.match(
        r"^(?:'[^']*'|\d+(?:\.\d+)?|NULL|TRUE|FALSE"
        r"|CURRENT_TIMESTAMP\(\)|CURRENT_DATE\(\)|GETDATE\(\))$",
        expression.strip(),
        re.I,
    ):
        return "CONSTANT"

    expr_upper = expression.upper()

    for func in AGG_FUNCTIONS:
        if re.search(rf"\b{func}\s*\(", expr_upper):
            return "AGGREGATION"

    for func in WINDOW_FUNCTIONS:
        if re.search(rf"\b{func}\s*\(", expr_upper):
            return "WINDOW"

    if len(sources) > 1 or not re.match(r"^(\w+\.)?(\w+)$", expression.strip()):
        for pattern, trans_type in _TRANSFORM_PATTERNS:
            if pattern.search(expression):
                return trans_type
        if re.search(r"\w+\s*\(", expression):
            return "FUNCTION"

    return "PASS-THROUGH"


def _extract_from_tables(sql: str) -> list[dict]:
    """Extract source table references from FROM/JOIN clauses."""
    clean = _strip_comments(sql).strip()
    tables: list[dict] = []

    for m in re.finditer(r"\bFROM\s+(\w+(?:\.\w+)*)\s*(?:AS\s+)?(\w+)?", clean, re.I):
        alias = m.group(2) or m.group(1).split(".")[-1]
        tables.append({"table": m.group(1), "alias": alias.lower()})

    for m in re.finditer(r"\bJOIN\s+(\w+(?:\.\w+)*)\s*(?:AS\s+)?(\w+)?", clean, re.I):
        alias = m.group(2) or m.group(1).split(".")[-1]
        tables.append({"table": m.group(1), "alias": alias.lower()})

    return tables
