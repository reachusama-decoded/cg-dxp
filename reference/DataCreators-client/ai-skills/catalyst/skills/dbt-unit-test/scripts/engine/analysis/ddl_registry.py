"""
dbt-unit-test DDL Registry.

Parses ``CREATE TABLE`` DDL files from ``database/dbt_tables/`` and provides
authoritative column-type lookups for source tables referenced by DBT models.

This eliminates the need to guess column types from naming conventions — instead,
the exact Spark/Hive types declared in the DDL files are used directly.

Usage
-----
    from engine.analysis.ddl_registry import DDLRegistry

    registry = DDLRegistry.from_project_root("/path/to/project")
    registry.get_table_schema("cg_company_v4")  # → {"cg_company_code": "string", ...}
    registry.resolve_column_type("position_date", ["cgam_position_by_activity_date_v4"])  # → "date"
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# DDL parsing
# ---------------------------------------------------------------------------

# Matches: CREATE [EXTERNAL] TABLE [IF NOT EXISTS] [schema_prefix.]table_name(
_CREATE_TABLE_RE = re.compile(
    r"CREATE\s+(?:EXTERNAL\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?"
    r"(?:[^\s(]+\.)?(\w+)\s*\(",
    re.IGNORECASE,
)


def _parse_ddl_file(path: Path) -> tuple[str | None, dict[str, str]]:
    """
    Parse a single ``CREATE TABLE`` DDL file.

    Returns ``(table_name, {column_name: data_type})``.
    Returns ``(None, {})`` when the file cannot be parsed.

    Handles:
      - Optional ``EXTERNAL`` keyword
      - Optional ``IF NOT EXISTS`` clause
      - Schema-prefixed table names: ``cspn_cons2_{env}.instrument_v4``
      - Decimal types with precision: ``decimal(38,8)``
      - Inline SQL comments (``-- ...``)
      - Whitespace variations (leading spaces, trailing commas)
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.debug("Cannot read DDL file %s: %s", path.name, exc)
        return None, {}

    m = _CREATE_TABLE_RE.search(text)
    if not m:
        return None, {}

    table_name = m.group(1).lower()

    # Walk character-by-character from the opening ( to find the matching )
    # so that nested ( ) inside DECIMAL(38,8) are handled correctly.
    col_start = m.end()   # index just after the opening (
    depth = 1
    i = col_start
    n = len(text)
    while i < n and depth > 0:
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
        i += 1
    col_block = text[col_start : i - 1]

    columns: dict[str, str] = {}
    for line in col_block.splitlines():
        line = line.strip().rstrip(",")
        if not line or line.startswith("--"):
            continue
        # Each column line: ``col_name  data_type[(...)]  [-- comment]``
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        col_name = parts[0].strip().lower()
        col_type = re.sub(r"\s*--.*$", "", parts[1]).strip().lower()
        if col_name and col_type:
            columns[col_name] = col_type

    return table_name, columns


# ---------------------------------------------------------------------------
# Public registry class
# ---------------------------------------------------------------------------

class DDLRegistry:
    """
    In-memory registry of table column types parsed from DDL files.

    Parameters
    ----------
    ddl_dir :
        Path to the directory containing DDL ``*.sql`` files.
        Pass ``None`` to create an empty (no-op) registry.
    """

    def __init__(self, ddl_dir: str | Path | None = None) -> None:
        # table_name (lower) → {col_name (lower): data_type}
        self._schemas: dict[str, dict[str, str]] = {}
        if ddl_dir is not None:
            self._load(Path(ddl_dir))

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_project_root(cls, project_root: str | Path) -> "DDLRegistry":
        """
        Create a registry from the standard DDL location relative to the
        project root: ``<project_root>/database/dbt_tables/``.

        Returns an empty (no-op) registry when the directory does not exist.
        """
        ddl_dir = Path(project_root) / "database" / "dbt_tables"
        if ddl_dir.is_dir():
            logger.debug("DDLRegistry: reading DDL files from %s", ddl_dir)
            return cls(ddl_dir)
        logger.debug(
            "DDL directory not found at %s — DDL type enrichment disabled", ddl_dir
        )
        return cls(None)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_table_schema(self, table_name: str) -> dict[str, str]:
        """
        Return ``{column_name: data_type}`` for *table_name*.

        Returns an empty dict when the table is not in the registry.
        """
        return dict(self._schemas.get(table_name.lower(), {}))

    def resolve_column_type(
        self,
        column_name: str,
        candidate_tables: list[str],
    ) -> str | None:
        """
        Search *candidate_tables* (in order) for *column_name* and return
        the DDL data type on the first match.

        Returns ``None`` when the column is not found in any candidate table.
        """
        col_lower = column_name.lower()
        for tbl in candidate_tables:
            schema = self._schemas.get(tbl.lower())
            if schema and col_lower in schema:
                return schema[col_lower]
        return None

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _load(self, ddl_dir: Path) -> None:
        loaded = 0
        for sql_file in ddl_dir.glob("*.sql"):
            table_name, columns = _parse_ddl_file(sql_file)
            if table_name and columns:
                self._schemas[table_name] = columns
                loaded += 1
        logger.debug("DDLRegistry: loaded %d table schemas from %s", loaded, ddl_dir)
