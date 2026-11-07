"""
DBT Integration Model Analyzer.

Parses the integration SQL file and companion YAML schema for a given DBT model
into a rich DBTModelContext used by the AI test case generator.

Model layout expected by this project:
    models/<domain>/<model_name>_f/integration/int_<model_name>.sql
    models/<domain>/<model_name>_f/<schema_stem>.yml
"""

from __future__ import annotations

import logging
import re
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from engine.analysis.ddl_registry import DDLRegistry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ColumnMapping:
    """A single column as it travels from source to output."""
    output_name: str
    source_expr: str          # raw SQL expression (may include CAST, function, etc.)
    data_type: str = "string"
    description: str = ""
    dbt_tests: list[str] = field(default_factory=list)


@dataclass
class DBTModelContext:
    """All information extracted from a DBT integration model needed for AI test generation."""
    model_name: str           # e.g. "int_currency_v4"
    domain: str               # e.g. "rdm", "ref"
    sql_content: str          # raw SQL (Jinja stripped for analysis use)
    raw_sql: str              # original Jinja2 SQL
    schema_columns: list[ColumnMapping]
    refs: list[str]           # referenced DBT models
    sources: list[tuple[str, str]]  # (schema, table) tuples
    config: dict
    checksum_columns: list[str]   # columns included in the hash expression
    type_casts: list[dict]        # {output_col, cast_type}
    raw_schema: dict
    source_tables: list[str] = field(default_factory=list)  # all source/ref table names extracted from SQL Jinja
    source_table_schemas: dict[str, dict[str, str]] = field(default_factory=dict)  # table_name → {col_name: ddl_type}
    project_root: Path = field(default_factory=Path)  # absolute project root for ref-chain resolution


# ---------------------------------------------------------------------------
# Jinja2 stripping helpers
# ---------------------------------------------------------------------------

_JINJA_BLOCK_RE = re.compile(r"\{\{.*?\}\}", re.DOTALL)
_JINJA_STMT_RE  = re.compile(r"\{%.*?%\}", re.DOTALL)


def _strip_jinja(sql: str) -> str:
    """Remove all Jinja2 blocks so plain SQL can be parsed."""
    sql = _JINJA_STMT_RE.sub("", sql)
    sql = _JINJA_BLOCK_RE.sub("__JINJA_EXPR__", sql)
    return sql


# ---------------------------------------------------------------------------
# Column extraction helpers
# ---------------------------------------------------------------------------


_CONCAT_ARGS_RE = re.compile(r"concat_ws\s*\(\s*'[^']+',\s*(.*?)\)", re.DOTALL | re.IGNORECASE)
_CAST_RE = re.compile(
    r"cast\s*\(\s*([^\s,]+)\s+as\s+([^)]+)\)\s+(?:as\s+)?(\w+)",
    re.IGNORECASE,
)



def _extract_checksum_columns(sql: str) -> list[str]:
    """Extract column names listed inside sha1(concat_ws(...))."""
    match = _CONCAT_ARGS_RE.search(sql)
    if not match:
        return []
    args_str = match.group(1)
    cols = [c.strip().strip('"\"') for c in args_str.split(",")]
    return [c for c in cols if re.match(r"^\w+$", c)]


def _extract_type_casts(sql: str) -> list[dict]:
    """Return list of {src_col, cast_type, output_col} for every CAST expression."""
    results = []
    for m in _CAST_RE.finditer(sql):
        results.append({
            "src_col": m.group(1).strip(),
            "cast_type": m.group(2).strip(),
            "output_col": m.group(3).strip(),
        })
    return results


def _infer_type_from_name(col_name: str) -> str:
    """Heuristic type inference from column naming conventions in this project."""
    name = col_name.lower()
    if any(name.endswith(s) for s in ("_uid", "_id", "_number", "_num")):
        return "bigint"
    if any(name.endswith(s) for s in ("_date", "_from_date", "_to_date")):
        return "date"
    if "_timestamp" in name:
        return "timestamp"
    if any(name.endswith(s) for s in ("_indicator", "_ind")):
        return "varchar(1)"
    if any(name.endswith(s) for s in ("_amount", "_ratio", "_percent", "_price")):
        return "decimal(38,8)"
    if any(name.endswith(s) for s in ("_code", "_cd", "_type_code")):
        return "varchar(50)"
    if any(name.endswith(s) for s in ("_name", "_description")):
        return "varchar(500)"
    return "varchar(255)"


def _find_outermost_select_body(sql: str) -> str | None:
    """
    Return the column-list body of the *last* top-level SELECT statement
    (i.e. the final output SELECT, not a CTE's inner SELECT).

    "Top-level" means at parenthesis depth 0.  CTE bodies live inside
    parentheses so their inner SELECTs are at depth >= 1 and are skipped.
    """
    upper = sql.upper()
    depth = 0
    last_select_end: int | None = None  # index just after the last depth-0 SELECT keyword

    i = 0
    n = len(sql)
    while i < n:
        ch = sql[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif depth == 0 and upper[i:i+6] == "SELECT":
            # Verify word boundary: char before and after must not be alphanumeric
            before_ok = i == 0 or not (sql[i - 1].isalnum() or sql[i - 1] == "_")
            after_ok  = (i + 6 >= n) or not (sql[i + 6].isalnum() or sql[i + 6] == "_")
            if before_ok and after_ok:
                last_select_end = i + 6  # start scanning for matching FROM here
        i += 1

    if last_select_end is None:
        return None

    # Now find the first FROM at depth 0 after last_select_end
    depth = 0
    i = last_select_end
    while i < n:
        ch = sql[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif depth == 0 and upper[i:i+4] == "FROM":
            before_ok = i == last_select_end or not (sql[i - 1].isalnum() or sql[i - 1] == "_")
            after_ok  = (i + 4 >= n) or not (sql[i + 4].isalnum() or sql[i + 4] == "_")
            if before_ok and after_ok:
                return sql[last_select_end:i]
        i += 1

    return None  # no matching FROM found


def _parse_select_columns(stripped_sql: str) -> list[ColumnMapping]:
    """
    Parse SELECT ... FROM block to extract output column → source expression pairs.
    Handles:
      - simple alias:         src_col  output_col
      - AS alias:             src_col AS output_col
      - CAST:                 cast(src_col as decimal) output_col
      - audit/jinja exprs:    skipped (output name contains __)

    Always parses the *last* top-level SELECT (the final output query) so that
    CTE definitions — whose inner SELECTs appear first in the file — are ignored.
    """
    select_body = _find_outermost_select_body(stripped_sql)
    if select_body is None:
        return []
    columns: list[ColumnMapping] = []

    # Split by comma, being careful about nested parentheses
    items = _split_select_items(select_body)
    for item in items:
        item = item.strip()
        if not item:
            continue

        # Strip leading DISTINCT / ALL keywords (e.g. "SELECT DISTINCT col1, col2")
        item = re.sub(r"^(?:distinct|all)\s+", "", item, flags=re.IGNORECASE)
        item = item.strip()
        if not item:
            continue

        # Hash/checksum expressions — add to schema as presence-only column
        if re.match(r"sha1\s*\(", item, re.IGNORECASE):
            alias = _get_trailing_alias(item) or "dl_checksum_value"
            columns.append(ColumnMapping(
                output_name=alias,
                source_expr="sha1(concat_ws(...))",
                data_type="varchar(40)",
            ))
            continue

        # Skip pure Jinja expressions (e.g. audit cols)
        if "__JINJA_EXPR__" in item and re.match(r"^__JINJA_EXPR__", item.strip()):
            continue

        # CAST expression
        cast_m = re.match(
            r"cast\s*\(\s*(.+?)\s+as\s+(.+?)\)\s+(?:as\s+)?(\w+)\s*$",
            item, re.IGNORECASE | re.DOTALL,
        )
        if cast_m:
            columns.append(ColumnMapping(
                output_name=cast_m.group(3).strip(),
                source_expr=f"cast({cast_m.group(1).strip()} as {cast_m.group(2).strip()})",
                data_type=cast_m.group(2).strip(),
            ))
            continue

        # Regular alias (with or without AS)
        alias_m = re.match(
            r"^(\S+(?:\s*\([^)]*\))?)\s+(?:as\s+)?(\w+)\s*$",
            item, re.IGNORECASE,
        )
        if alias_m:
            src = alias_m.group(1).strip()
            out = alias_m.group(2).strip()
            # Skip internal markers
            if "__" in out:
                continue
            columns.append(ColumnMapping(
                output_name=out,
                source_expr=src,
                data_type=_infer_type_from_name(out),
            ))
            continue

        # Plain identifier (no alias) — optionally table-qualified: tbl.col or just col
        plain_m = re.match(r"^(?:\w+\.)?(\w+)\s*$", item)
        if plain_m:
            name = plain_m.group(1)
            columns.append(ColumnMapping(
                output_name=name,
                source_expr=name,
                data_type=_infer_type_from_name(name),
            ))

    return columns


def _split_select_items(select_body: str) -> list[str]:
    """Split a SELECT body by top-level commas (respecting parentheses nesting)."""
    items: list[str] = []
    depth = 0
    current: list[str] = []
    for ch in select_body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            items.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        items.append("".join(current).strip())
    return items


def _get_trailing_alias(expr: str) -> Optional[str]:
    """Extract trailing alias from an expression like `cast(...) AS output_col`."""
    m = re.search(r"\)\s+(?:as\s+)?(\w+)\s*$", expr, re.IGNORECASE)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Ref / Source extraction
# ---------------------------------------------------------------------------

_REF_RE    = re.compile(r"""\bref\s*\(\s*['"](\w+)['"]\s*\)""", re.IGNORECASE)
_SOURCE_RE = re.compile(r"""\bsource\s*\(\s*['"](\w+)['"]\s*,\s*['"](\w+)['"]\s*\)""", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class DBTModelAnalyzer:
    """
    Discovers and parses DBT integration model files for a given model name.

    Supports two usage patterns:
      1. Supply ``model_name`` only — searches the entire ``models/`` directory.
      2. Supply ``sql_path`` + ``schema_path`` directly — useful in tests.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.models_dir = self.project_root / "models"
        self._ddl_registry = DDLRegistry.from_project_root(self.project_root)

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------

    def analyze(self, model_name: str) -> DBTModelContext:
        """
        Full analysis of a DBT integration model.

        ``model_name`` can be supplied with or without the ``int_`` prefix,
        e.g. ``"currency_v4"`` or ``"int_currency_v4"`` both work.
        """
        bare_name = model_name.removeprefix("int_")
        sql_path    = self._find_integration_sql(bare_name)
        schema_path = self._find_schema_yaml(sql_path.parent.parent)
        return self._parse(bare_name, sql_path, schema_path)

    def analyze_from_paths(self, model_name: str, sql_path: Path, schema_path: Path) -> DBTModelContext:
        """Parse from explicit paths (useful for testing)."""
        bare_name = model_name.removeprefix("int_")
        return self._parse(bare_name, sql_path, schema_path)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _parse(self, bare_name: str, sql_path: Path, schema_path: Path) -> DBTModelContext:
        raw_sql     = sql_path.read_text(encoding="utf-8")
        raw_schema  = yaml.safe_load(schema_path.read_text(encoding="utf-8")) or {}
        stripped    = _strip_jinja(raw_sql)

        domain = sql_path.parts[
            list(sql_path.parts).index("models") + 1
        ] if "models" in sql_path.parts else "unknown"

        # Schema columns (from YAML if present, else inferred from SQL)
        schema_col_map = self._extract_schema_columns(raw_schema, f"int_{bare_name}")
        parsed_cols    = _parse_select_columns(stripped)

        # DDL type enrichment — override _infer_type_from_name heuristics with
        # authoritative types from database/dbt_tables/ DDL files.
        # Type priority (highest wins): YAML > DDL > _infer_type_from_name.
        # The YAML merge below runs after this step so YAML always takes precedence.
        from engine.execution.spark_executor import extract_source_tables
        _source_tables = extract_source_tables(raw_sql)
        _plain_col_re  = re.compile(r"^(?:\w+\.)?(\w+)$")
        for col in parsed_cols:
            m_col = _plain_col_re.match(col.source_expr.strip())
            if not m_col:
                continue  # complex expression (CAST, function) — type already accurate
            ddl_type = self._ddl_registry.resolve_column_type(m_col.group(1), _source_tables)
            if ddl_type:
                col.data_type = ddl_type

        # Merge: prefer YAML description/tests when available
        for col in parsed_cols:
            if col.output_name in schema_col_map:
                yml_col = schema_col_map[col.output_name]
                col.description = yml_col.description or col.description
                col.dbt_tests   = yml_col.dbt_tests or col.dbt_tests
                col.data_type   = yml_col.data_type or col.data_type

        model_config = {}
        for m in raw_schema.get("models", []):
            if m.get("name") in (f"int_{bare_name}", bare_name):
                model_config = m.get("meta", {})
                break

        final_cols = parsed_cols if parsed_cols else list(schema_col_map.values())

        # Log analyzed schema columns
        logger.debug(
            "Model '%s' — %d schema column(s) analyzed:",
            f"int_{bare_name}", len(final_cols),
        )
        header = f"  {'#':>3}  {'output_name':<50}  {'data_type':<20}  {'source_expr':<50}  {'dbt_tests'}"
        logger.debug(header)
        logger.debug("  " + "-" * (len(header) - 2))
        for i, col in enumerate(final_cols, start=1):
            logger.debug(
                "  %3d  %-50s  %-20s  %-50s  %s",
                i, col.output_name, col.data_type,
                col.source_expr[:50], ", ".join(col.dbt_tests) or "—",
            )

        # Build DDL schema map for source tables (passed to LLM prompt for seed type guidance)
        source_table_schemas = {
            tbl: schema
            for tbl in _source_tables
            for schema in [self._ddl_registry.get_table_schema(tbl)]
            if schema
        }

        # Enrich with columns from staging SQL files co-located with this model.
        # Ref models ({{ref(...)}}) are DBT models, not raw tables, so the DDL
        # registry often has no entry for them.  Reading the sibling staging/*.sql
        # files gives us the exact SELECT column list the integration model relies on,
        # which the LLM needs to generate correct seed data.
        # Falls back gracefully for models without a staging/ folder (cross-domain
        # refs, models that reference only raw sources, etc.).
        staging_schemas = self._load_staging_ref_schemas(
            sql_path, _REF_RE.findall(raw_sql)
        )
        for ref_name, col_map in staging_schemas.items():
            if ref_name not in source_table_schemas:
                # No DDL entry — use staging SQL columns with generic "string" type
                source_table_schemas[ref_name] = col_map
                logger.info(
                    "Source schema for ref '%s': %d columns from staging SQL "
                    "(no DDL entry found)",
                    ref_name, len(col_map),
                )
            else:
                # DDL exists — supplement with any column the DDL missed
                added = 0
                for col, typ in col_map.items():
                    if col not in source_table_schemas[ref_name]:
                        source_table_schemas[ref_name][col] = typ
                        added += 1
                if added:
                    logger.debug(
                        "Added %d staging-SQL-only columns to DDL schema for '%s'",
                        added, ref_name,
                    )

        return DBTModelContext(
            model_name           = f"int_{bare_name}",
            domain               = domain,
            sql_content          = stripped,
            raw_sql              = raw_sql,
            schema_columns       = final_cols,
            refs                 = _REF_RE.findall(raw_sql),
            sources              = _SOURCE_RE.findall(raw_sql),
            config               = model_config,
            checksum_columns     = _extract_checksum_columns(stripped),
            type_casts           = _extract_type_casts(stripped),
            raw_schema           = raw_schema,
            source_tables        = _source_tables,
            source_table_schemas = source_table_schemas,
            project_root         = Path(self.project_root),
        )

    def _find_integration_sql(self, bare_name: str) -> Path:
        """Search for integration/int_<bare_name>.sql anywhere under models/."""
        candidates = list(self.models_dir.rglob(f"int_{bare_name}.sql"))
        if not candidates:
            # Also accept bare name sql files
            candidates = list(self.models_dir.rglob(f"{bare_name}.sql"))
        if not candidates:
            raise FileNotFoundError(
                f"No integration SQL found for '{bare_name}' under {self.models_dir}\n"
                f"  Hint: run 'dbt-unit-test' from your DBT project root (the folder that contains models/).\n"
                f"  Current working directory: {Path.cwd()}"
            )
        # Prefer files inside an 'integration' folder
        for c in candidates:
            if c.parent.name == "integration":
                return c
        return candidates[0]

    def _find_schema_yaml(self, model_folder: Path) -> Path:
        """Find the schema YAML in the model's folder (parent of 'integration/')."""
        yamls = list(model_folder.glob("*.yml"))
        if not yamls:
            raise FileNotFoundError(f"No YAML schema found in {model_folder}")
        return yamls[0]

    @staticmethod
    def _parse_staging_select_columns(sql_text: str) -> list[str]:
        """Extract column names from a simple staging SQL SELECT list.

        Strips Jinja config/variable blocks, finds the first SELECT...FROM
        block, and returns bare column identifiers (or the alias when AS is
        used).  Returns an empty list when parsing fails or the file uses
        SELECT *.
        """
        # Remove Jinja expression {{ ... }} and statement {% ... %} blocks
        cleaned = re.sub(r"\{\{.*?\}\}", "", sql_text, flags=re.DOTALL)
        cleaned = re.sub(r"\{%.*?%\}", "", cleaned, flags=re.DOTALL)

        m = re.search(r"\bSELECT\b(.*?)\bFROM\b", cleaned, re.IGNORECASE | re.DOTALL)
        if not m:
            return []

        select_body = m.group(1).strip()

        # SELECT * or SELECT DISTINCT * — column names unknowable
        if re.match(r"^DISTINCT\s*\*\s*$|^\*\s*$", select_body, re.IGNORECASE):
            return []

        select_body = re.sub(r"^DISTINCT\s+", "", select_body, flags=re.IGNORECASE)

        cols: list[str] = []
        for part in select_body.split(","):
            # Strip inline SQL comments and surrounding whitespace
            part = re.sub(r"--.*$", "", part, flags=re.MULTILINE).strip()
            if not part:
                continue
            # `expr AS alias` → take alias
            as_m = re.search(r"\bAS\s+(\w+)\s*$", part, re.IGNORECASE)
            if as_m:
                cols.append(as_m.group(1).lower())
            elif re.match(r"^\w+$", part):
                cols.append(part.lower())
            # Complex expressions without an alias are skipped (column name ambiguous)
        return cols

    def _load_staging_ref_schemas(
        self,
        sql_path: Path,
        ref_names: list[str],
    ) -> dict[str, dict[str, str]]:
        """Parse staging SQL files co-located with the integration model.

        Looks in the sibling ``staging/`` directory (next to ``integration/``)
        for a ``.sql`` file matching each ref model name.  Extracts the SELECT
        column list and returns ``{ref_name: {col_name: "string"}}`` for each
        ref model where a staging SQL file is found.

        Fails gracefully — returns an empty dict when there is no staging
        folder or no matching file for a given ref (e.g. cross-domain refs).
        """
        # integration SQL: <model_folder>/integration/int_xxx.sql
        # staging SQLs:    <model_folder>/staging/<ref_name>.sql
        staging_dir = sql_path.parent.parent / "staging"
        if not staging_dir.is_dir():
            logger.debug(
                "No staging/ directory alongside integration model at %s", sql_path
            )
            return {}

        result: dict[str, dict[str, str]] = {}
        for ref_name in ref_names:
            staging_file = staging_dir / f"{ref_name}.sql"
            if not staging_file.exists():
                logger.debug(
                    "No staging SQL for ref '%s' at %s", ref_name, staging_file
                )
                continue
            try:
                cols = self._parse_staging_select_columns(
                    staging_file.read_text(encoding="utf-8")
                )
                if cols:
                    result[ref_name] = {col: "string" for col in cols}
                    logger.debug(
                        "Loaded %d columns from staging SQL for ref '%s'",
                        len(cols), ref_name,
                    )
            except Exception as exc:
                logger.warning(
                    "Failed to parse staging SQL for ref '%s': %s", ref_name, exc
                )
        return result

    @staticmethod
    def _extract_schema_columns(raw_schema: dict, model_name: str) -> dict[str, ColumnMapping]:
        """Build a name → ColumnMapping dict from the YAML models entry."""
        result: dict[str, ColumnMapping] = {}
        for model in raw_schema.get("models", []):
            if model.get("name") == model_name:
                for col in model.get("columns", []):
                    name = col.get("name", "")
                    tests = col.get("tests", [])
                    # Normalise test entries (they can be str or dict)
                    test_names = [
                        t if isinstance(t, str) else list(t.keys())[0]
                        for t in tests
                    ]
                    result[name] = ColumnMapping(
                        output_name = name,
                        source_expr = name,
                        data_type   = col.get("data_type", _infer_type_from_name(name)),
                        description = col.get("description", ""),
                        dbt_tests   = test_names,
                    )
        return result
