"""
dbt-unit-test DBT Test Runner.

Coordinates model analysis and SQL execution against synthetic seed data.
Supports two execution backends:

  pandas (default)
      Column-rename passthrough: all seed DataFrames are concatenated and
      returned as-is (no SQL transforms applied).  Useful for simple rename
      models or when PySpark is not available.

  pyspark
      A local SparkSession executes the real Jinja-stripped DBT SQL — same
      engine as production.  Requires ``pyspark`` to be installed.

Usage (in generated pytest scripts)
------------------------------------
    from engine.execution.runner import DBTTestRunner
    from engine.execution.synthetic_data import SyntheticDataGenerator

    runner   = DBTTestRunner(model_name="int_currency_v4", project_root=".", executor="pyspark")
    synth    = SyntheticDataGenerator(seed_dir=runner.seed_dir)
    seeds    = synth.write_seeds("TC001", "int_currency_v4", input_data)
    runner.load_seeds(seeds)
    result   = runner.run_and_fetch()   # → pandas DataFrame
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def _fix_join_keys(
    seed_data: dict[str, list[dict]],
    raw_sql: str,
) -> dict[str, list[dict]]:
    """
    Patch seed data so equi-JOIN keys are consistent across seeded tables.

    The LLM sometimes omits JOIN key columns from source tables that don't
    appear in the final output schema (e.g. marketmaturityclassificationsetuniqueidentifier
    used only in an ON condition).  When exactly one side of an equi-join
    has the column, this function copies the value to the other side so the
    INNER JOIN can succeed.

    Only acts when one side is MISSING the column entirely.
    Never overwrites existing values (preserves intentional mismatches).
    """
    known_tables = {t.lower() for t in seed_data}
    if not known_tables:
        return seed_data

    # Build alias → table map from Jinja ref() and bare FROM/JOIN patterns
    alias_to_table: dict[str, str] = {}
    for m in re.finditer(
        r'\{\{\s*ref\s*\(\s*["\']([^"\']+)["\']\s*\)\s*\}\}\s+(?:AS\s+)?(\w+)',
        raw_sql, re.IGNORECASE,
    ):
        tbl, alias = m.group(1).lower(), m.group(2).lower()
        if tbl in known_tables and alias not in known_tables:
            alias_to_table[alias] = tbl

    for m in re.finditer(
        r'\b(?:FROM|JOIN)\s+([a-zA-Z_]\w*)\s+(?:AS\s+)?([a-zA-Z_]\w*)',
        raw_sql, re.IGNORECASE,
    ):
        tbl, alias = m.group(1).lower(), m.group(2).lower()
        if tbl in known_tables and alias not in known_tables:
            alias_to_table[alias] = tbl

    for t in known_tables:
        alias_to_table[t] = t

    # Deep copy to avoid mutating the original
    result: dict[str, list[dict]] = {
        tbl: [dict(row) for row in rows]
        for tbl, rows in seed_data.items()
    }

    def _has_col(rows: list[dict], col: str) -> bool:
        return bool(rows) and any(col in {k.lower() for k in r} for r in rows)

    def _get_val(rows: list[dict], col: str):
        for row in rows:
            for k, v in row.items():
                if k.lower() == col and v is not None:
                    return v
        return None

    # Scan all alias1.col1 = alias2.col2 patterns in ON/WHERE clauses
    on_re = re.compile(
        r'\b([a-zA-Z_]\w*)\s*\.\s*([a-zA-Z_]\w*)\s*=\s*([a-zA-Z_]\w*)\s*\.\s*([a-zA-Z_]\w*)',
        re.IGNORECASE,
    )
    for m in on_re.finditer(raw_sql):
        alias1, col1 = m.group(1).lower(), m.group(2).lower()
        alias2, col2 = m.group(3).lower(), m.group(4).lower()

        tbl1 = alias_to_table.get(alias1)
        tbl2 = alias_to_table.get(alias2)
        if not tbl1 or not tbl2 or tbl1 == tbl2:
            continue

        tbl1_key = next((k for k in result if k.lower() == tbl1), None)
        tbl2_key = next((k for k in result if k.lower() == tbl2), None)
        if not tbl1_key or not tbl2_key:
            continue

        rows1, rows2 = result[tbl1_key], result[tbl2_key]
        if not rows1 or not rows2:
            continue

        has1, has2 = _has_col(rows1, col1), _has_col(rows2, col2)

        if has1 and not has2:
            val = _get_val(rows1, col1)
            if val is not None:
                for row in rows2:
                    row[col2] = val
                logger.debug(
                    "[dbt-unit-test] join-key fix: %s.%s = %r  ←  %s.%s",
                    tbl2_key, col2, val, tbl1_key, col1,
                )
        elif has2 and not has1:
            val = _get_val(rows2, col2)
            if val is not None:
                for row in rows1:
                    row[col1] = val
                logger.debug(
                    "[dbt-unit-test] join-key fix: %s.%s = %r  ←  %s.%s",
                    tbl1_key, col1, val, tbl2_key, col2,
                )

    return result


class DBTTestRunner:
    """
    Runs a DBT model against synthetic seed data using the chosen executor.

    Parameters
    ----------
    model_name   : Full or bare model name (e.g. "int_currency_v4" or "currency_v4").
    project_root : Absolute path to the DBT project root.
    target       : DBT target profile name (informational; not used by local executors).
    db_conn      : SQLAlchemy connection string (reserved for future live-DB executor).
    executor     : "pandas" (default) or "pyspark".
    """

    def __init__(
        self,
        model_name: str,
        project_root: str | Path = ".",
        target: str = "dev",
        db_conn: str | None = None,
        executor: str = "pandas",
    ) -> None:
        self.model_name   = model_name
        self.project_root = Path(project_root).resolve()
        self.target       = target
        self.db_conn      = db_conn
        self.executor     = executor

        # Lazy-loaded on first run_and_fetch() call to avoid slow startup
        # for tests that are skipped before execution.
        self._ctx   = None
        self._seeds: dict[str, list[dict[str, Any]]] | None = None

        # Result cache — keyed by an MD5 of the serialised seed data so that
        # consecutive run_and_fetch() calls with identical seeds return the
        # cached DataFrame without re-executing the model.
        self._result_cache: pd.DataFrame | None = None
        self._cache_key: str | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def seed_dir(self) -> Path:
        """Directory used for optional on-disk seed dumps."""
        return (
            self.project_root
            / "dbt-unit-test"
            / "generated"
            / self.model_name
            / "seeds"
        )

    def load_seeds(self, seeds: dict[str, list[dict[str, Any]]]) -> None:
        """
        Store seed data produced by SyntheticDataGenerator.write_seeds().

        Applies join-key patching so that equi-JOIN columns missing from one
        side of an ON condition are back-filled from the other side.

        Parameters
        ----------
        seeds : Dict mapping source/ref table names → lists of row dicts.
        """
        try:
            raw_sql = self._get_ctx().raw_sql
            seeds = _fix_join_keys(seeds, raw_sql)
        except Exception as exc:
            logger.debug("[dbt-unit-test] join-key fix skipped: %s", exc)
        self._seeds = seeds
        logger.debug(
            "[dbt-unit-test] load_seeds: %d tables loaded for '%s'",
            len(seeds), self.model_name,
        )

    def run_and_fetch(self) -> pd.DataFrame:
        """
        Execute the DBT model against the loaded seed data.

        Returns
        -------
        pandas DataFrame with the model's output columns and rows.

        Raises
        ------
        RuntimeError  if load_seeds() was not called before run_and_fetch().
        """
        if self._seeds is None:
            raise RuntimeError(
                "No seeds loaded. Call load_seeds() before run_and_fetch()."
            )

        # Compute a cache key from the serialised seed payload.
        try:
            _key = hashlib.md5(
                json.dumps(self._seeds, sort_keys=True, default=str).encode()
            ).hexdigest()
        except Exception:
            _key = None

        if _key is not None and _key == self._cache_key and self._result_cache is not None:
            logger.debug("[dbt-unit-test] run_and_fetch: cache hit for '%s'", self.model_name)
            return self._result_cache

        if self.executor == "pyspark":
            result = self._run_pyspark()
        elif self.executor == "pandas":
            result = self._run_pandas()
        else:
            raise ValueError(
                f"Unknown executor '{self.executor}'. Use 'pyspark' or 'pandas'."
            )

        if _key is not None:
            self._cache_key = _key
            self._result_cache = result

        return result

    # ------------------------------------------------------------------
    # Executor backends
    # ------------------------------------------------------------------

    def _get_ctx(self):
        """Lazy-load and cache the DBTModelContext."""
        if self._ctx is None:
            from engine.analysis.model_analyzer import DBTModelAnalyzer
            self._ctx = DBTModelAnalyzer(
                project_root=str(self.project_root)
            ).analyze(self.model_name)
        return self._ctx

    def _run_pyspark(self) -> pd.DataFrame:
        """Execute the model via a local SparkSession (real SQL transforms)."""
        from engine.execution.spark_executor import PySparkExecutor

        ctx = self._get_ctx()
        return PySparkExecutor(ctx).execute(self._seeds)

    def _run_pandas(self) -> pd.DataFrame:
        """
        Column-rename passthrough using pandas.

        Concatenates all seed DataFrames, renames source columns to their
        output aliases using the AS-alias mapping extracted from the SQL,
        then projects down to the declared output schema.  No SQL transforms
        are applied — complex expressions (CAST, COALESCE …) are left
        as-is; only simple identifier renames are applied.
        """
        frames: list[pd.DataFrame] = []
        for table_name, rows in self._seeds.items():
            if rows:
                df = pd.DataFrame(rows)
                frames.append(df)

        if not frames:
            logger.warning(
                "[dbt-unit-test] pandas executor: all seeds are empty for '%s'", self.model_name
            )
            return pd.DataFrame()

        result = pd.concat(frames, ignore_index=True)

        # Apply AS-alias renames and project to output schema when the model
        # context is available.
        try:
            ctx = self._get_ctx()

            # Build source_col → output_name rename map from simple expressions.
            # source_expr may be "col", "t.col", "alias.col" etc.
            # Skip complex expressions (CAST, COALESCE, functions).
            # Skip ambiguous bare names that appear in more than one source column
            # (last-write-wins would silently drop the other table's values).
            bare_counts = Counter(
                col.source_expr.split(".")[-1].strip()
                for col in ctx.schema_columns
                if re.match(r"^\w+$", col.source_expr.split(".")[-1].strip())
            )
            rename_map: dict[str, str] = {}
            for col in ctx.schema_columns:
                bare = col.source_expr.split(".")[-1].strip()
                if re.match(r"^\w+$", bare) and bare != col.output_name and bare_counts[bare] == 1:
                    rename_map[bare] = col.output_name

            if rename_map:
                result = result.rename(columns=rename_map)

            # Project down to expected output columns (best-effort).
            expected_cols = [c.output_name for c in ctx.schema_columns]
            available = [c for c in expected_cols if c in result.columns]
            if available:
                result = result[available]

        except Exception as exc:
            logger.debug(
                "[dbt-unit-test] pandas executor: could not apply rename/projection: %s", exc
            )

        logger.info(
            "[dbt-unit-test] pandas passthrough result: %d rows, %d columns",
            len(result), len(result.columns),
        )
        return result
