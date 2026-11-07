"""Core function: parse SQL identifiers for boundary-checked FQN matching.

Pure string layer — no I/O, no platform clients. Used by skills that need
to ask "does this SQL text reference object ``schema.alias``?" without
spinning up a full SQL parser.

Two operations are exposed:

- :func:`strip_sql_noise` — drop comments, single-quoted literals, and
  whitespace-containing double-quoted literals, while preserving
  identifier-shaped double-quoted tokens (ANSI quoting). The result is
  safe to feed into a regex-based identifier matcher without the
  matcher accidentally hitting a name embedded in a comment or string
  literal.

- :func:`query_mentions_object` — boundary-checked FQN match with
  backtick / double-quote identifier wrapper tolerance. Returns
  ``True`` iff the query text contains a reference to ``schema.alias``
  (or, when ``schema`` is empty, a conservative ``FROM/JOIN`` / DML
  occurrence of ``alias``).

The pair is deliberately not a full SQL parser. They exist for cheap
heuristics — read-count diagnostics, model-usage scans — where a parser
dependency would be heavy-handed and the false-positive cost is low.
"""

from __future__ import annotations

import re

__all__ = [
    "strip_sql_noise",
    "query_mentions_object",
]


# ---------------------------------------------------------------------------
# strip_sql_noise
# ---------------------------------------------------------------------------

# Block comments: /* ... */  (non-greedy, multiline)
_SQL_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", flags=re.DOTALL)
# Line comments: -- through end of line
_SQL_LINE_COMMENT_RE = re.compile(r"--[^\n]*")
# Single-quoted string literals (with doubled '' as an escape)
_SQL_SINGLE_QUOTED_RE = re.compile(r"'(?:[^']|'')*'")
# Any double-quoted run (with doubled "" as an escape). Whether to strip
# depends on whether the content looks like an identifier or a string
# literal; the decision is made in the substitution callback below.
_SQL_DOUBLE_QUOTED_RE = re.compile(r'"(?:[^"]|"")*"')


def strip_sql_noise(text: str) -> str:
    """Strip comments and string literals from SQL text.

    Removed:
        - ``/* block comments */`` (multiline)
        - ``-- line comments`` (through end of line)
        - ``'single-quoted string literals'`` (with ``''`` escapes)
        - ``"double-quoted string literals"`` *only when* the content
          contains whitespace — under default ANSI mode a double-quoted
          run is a string literal, but identifier-shaped tokens
          (``"my_table"``) are left intact so callers doing
          ``"schema"."table"`` matching still see them.

    Preserved: keywords, operators, identifiers (including
    schema-qualified FQNs such as ``analytics.fct_orders`` and
    ``"a"."b"``), numeric tokens.

    Returns the noise-stripped text. Whitespace from removed regions is
    collapsed to a single space so identifier-boundary regexes still
    see word breaks.
    """
    if not isinstance(text, str) or not text:
        return text
    text = _SQL_BLOCK_COMMENT_RE.sub(" ", text)
    text = _SQL_LINE_COMMENT_RE.sub(" ", text)
    text = _SQL_SINGLE_QUOTED_RE.sub(" ", text)

    def _maybe_strip_double_quoted(m: re.Match) -> str:
        content = m.group(0)[1:-1]
        if not content or re.search(r"\s", content):
            return " "
        return m.group(0)

    text = _SQL_DOUBLE_QUOTED_RE.sub(_maybe_strip_double_quoted, text)
    return text


# ---------------------------------------------------------------------------
# query_mentions_object
# ---------------------------------------------------------------------------


def query_mentions_object(query_text: str, schema: str, alias: str) -> bool:
    """Return True iff *query_text* references ``schema.alias``.

    Matching is boundary-checked so ``alias=fct_orders`` does NOT match
    ``fct_orders_v2``. Identifier wrappers (backticks, double quotes)
    are tolerated on either component, so all of the following match
    when ``schema="analytics"`` and ``alias="fct_orders"``::

        FROM analytics.fct_orders
        JOIN `analytics`.`fct_orders` AS o
        SELECT * FROM "analytics"."fct_orders"

    When *schema* is empty (or falsy), the function falls back to a
    conservative table-position heuristic: it only counts ``alias`` as
    a reference if it appears immediately after ``FROM``, ``JOIN``,
    ``UPDATE``, ``INTO``, or ``TABLE``. This avoids broad alias
    collisions in SELECT lists, CTE definitions, and comment text.

    Args:
        query_text: SQL text to scan. Callers typically pass the output
            of :func:`strip_sql_noise` so comments and string literals
            don't trigger false positives.
        schema: Schema (database) component of the FQN. Pass ``""`` if
            you don't know the schema and want the conservative
            FROM/JOIN fallback.
        alias: Table / view / model name. Required (returns ``False``
            for empty alias).

    Returns:
        ``True`` if a boundary-checked reference exists, ``False``
        otherwise.
    """
    if not alias:
        return False
    alias_re = re.escape(alias)
    quoted_alias = rf'(?:[`\"]?{alias_re}[`\"]?)'
    if schema:
        schema_re = re.escape(schema)
        quoted_schema = rf'(?:[`\"]?{schema_re}[`\"]?)'
        fqn_pat = rf'(?<![\w]){quoted_schema}\s*\.\s*{quoted_alias}(?![\w])'
        return re.search(fqn_pat, query_text) is not None

    # Schema is missing: only count conservative table-position refs.
    from_join_pat = rf'\b(from|join|update|into|table)\s+{quoted_alias}(?![\w])'
    return re.search(from_join_pat, query_text) is not None
