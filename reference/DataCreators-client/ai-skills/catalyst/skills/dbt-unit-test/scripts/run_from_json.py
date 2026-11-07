#!/usr/bin/env python3
"""
dbt-unit-test skill helper — execute a pre-generated test cases JSON through the
full dbt-unit-test pipeline (seed fixing, script generation, test execution, report).

Self-contained: uses the ``engine/`` package bundled alongside this script.
The agent IS the LLM; this script handles only the deterministic execution steps.

Usage:
    python run_from_json.py \\
        --json dbt-unit-test/generated/int_currency_v4/int_currency_v4_test_cases.json \\
        --executor pandas \\
        --project-root /path/to/dbt/project
"""

from __future__ import annotations

import argparse
import json as _json_lib
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Make the bundled engine package importable — adds scripts/ to sys.path
# so that ``from engine.*`` works regardless of where this script is run from.
# ---------------------------------------------------------------------------
_SCRIPTS_DIR = Path(__file__).resolve().parent

if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# ---------------------------------------------------------------------------
# Load .env so that JIRA_API_TOKEN and other credentials placed there by the
# user (per SKILL.md Step 0) are available via os.environ.  Shell / CI env
# vars always win because load_dotenv() only sets vars that are not already
# set.  Catalyst convention: stdlib-only parser (see skills/source-aligned/
# scripts/run_curation_dbt.py and databricks_local_ingest.py for the same
# pattern) — no external dependency required.
# ---------------------------------------------------------------------------
def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger("dbt-unit-test-skill")


def _ensure_conftest(output_dir: Path) -> None:
    """
    Copy the bundled conftest.py into the model's output directory so that
    pytest can discover the --dbt-unit-test-executor option and dbt_unit_test_config fixture.
    The conftest also adds scripts/ to sys.path inside the pytest subprocess.
    """
    src = _SCRIPTS_DIR / "engine" / "generated" / "conftest.py"
    # Place conftest one level above the model dir so it covers all model subdirs.
    generated_dir = output_dir.parent
    dest = generated_dir / "conftest.py"
    if not dest.exists() and src.exists():
        shutil.copy2(src, dest)
        logger.info("conftest.py installed at %s", dest)


def _analyzer_cache_path(output_dir: Path, model_name: str) -> Path:
    return output_dir / f".{model_name}_analyzer.cache.json"


def _model_sql_mtimes(project_root: Path, model_name: str) -> list[float]:
    """Return the mtimes of all SQL files in the model's staging/int/prepared chain."""
    patterns = [
        f"models/**/{model_name}.sql",
        f"models/**/int_{model_name}.sql",
        f"models/**/stage_{model_name}.sql",
        f"models/**/stage_{model_name}_*.sql",
    ]
    mtimes = []
    for pat in patterns:
        for p in project_root.glob(pat):
            mtimes.append(p.stat().st_mtime)
    return mtimes


def _load_analyzer_cache(cache_path: Path, project_root: Path, model_name: str) -> dict | None:
    """Return cached analyzer data if all model SQL files are older than the cache."""
    if not cache_path.exists():
        return None
    cache_mtime = cache_path.stat().st_mtime
    sql_mtimes = _model_sql_mtimes(project_root, model_name)
    if not sql_mtimes:
        return None  # can't validate cache without knowing SQL files
    if any(m > cache_mtime for m in sql_mtimes):
        logger.debug("Model SQL changed; invalidating analyzer cache for %s", model_name)
        return None
    try:
        data = _json_lib.loads(cache_path.read_text(encoding="utf-8"))
    except _json_lib.JSONDecodeError:
        logger.warning("Analyzer cache corrupt for %s; regenerating.", model_name)
        return None
    logger.info(
        "  ✓  Analyzer cache hit — %d output columns | %d refs | %d sources",
        data.get("column_count", 0),
        data.get("ref_count", 0),
        data.get("source_count", 0),
    )
    return data


def _save_analyzer_cache(cache_path: Path, ctx) -> None:
    """Persist lightweight analyzer output so re-runs skip the analysis step."""
    data = {
        "raw_sql": ctx.raw_sql if ctx else "",
        "column_count": len(ctx.schema_columns) if ctx else 0,
        "ref_count": len(ctx.refs) if ctx else 0,
        "source_count": len(ctx.sources) if ctx else 0,
    }
    cache_path.write_text(_json_lib.dumps(data), encoding="utf-8")


def _run_pipeline(json_path: Path, executor: str, project_root: Path) -> int:
    """
    Run the full engine pipeline using the bundled engine package directly.

    Steps:
      1. Load + seed-fix test cases from JSON
      2. Render Jinja2 pytest script
      3. Execute pytest (with PYTHONPATH pointing to scripts/)
      4. Generate Markdown report
    """
    try:
        from engine.analysis.model_analyzer import DBTModelAnalyzer
        from engine.execution.script_generator import TestScriptGenerator
        from engine.reporting.report_generator import MarkdownReportGenerator
    except ImportError as exc:
        logger.error(
            "engine package not found: %s\n"
            "Ensure this script is run from skills/dbt-unit-test/scripts/ "
            "or that the engine/ folder is on PYTHONPATH.",
            exc,
        )
        return 1

    model_name = json_path.stem.replace("_test_cases", "")
    output_dir = json_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Ensure conftest.py is present so pytest discovers the --dbt-unit-test-executor option
    _ensure_conftest(output_dir)

    # ── Step 1: Load + seed-fix test cases ───────────────────────────────
    logger.info("Step 1: Loading test cases from %s", json_path)
    script_gen = TestScriptGenerator(output_dir=output_dir)
    test_cases = script_gen.load_test_cases_json(str(json_path))

    # Attempt schema context for seed-fixing (non-fatal if model SQL missing)
    raw_sql = ""
    try:
        cache_path = _analyzer_cache_path(output_dir, model_name)
        cached = _load_analyzer_cache(cache_path, project_root, model_name)
        if cached:
            raw_sql = cached.get("raw_sql", "")
            ctx = None
        else:
            analyzer = DBTModelAnalyzer(project_root=str(project_root))
            ctx = analyzer.analyze(model_name)
            raw_sql = ctx.raw_sql if ctx else ""
            logger.info(
                "  ✓  %d output columns | %d refs | %d sources",
                len(ctx.schema_columns),
                len(ctx.refs),
                len(ctx.sources),
            )
            _save_analyzer_cache(cache_path, ctx)
    except FileNotFoundError:
        logger.warning("Model SQL not found in project root; seed-fixing without schema context.")
        ctx = None

    from engine.generation.seed_fixer import fix_seed_column_gaps
    test_cases = fix_seed_column_gaps(test_cases, raw_sql)
    logger.info("  ✓  %d test cases loaded", len(test_cases))

    # ── Step 2: Render pytest script ─────────────────────────────────────
    logger.info("Step 2: Rendering pytest script …")
    script_path = script_gen.generate_pytest_script(model_name, test_cases)
    json_out = script_gen.save_test_cases_json(model_name, test_cases)
    logger.info("  ✓  Script : %s", script_path)
    logger.info("  ✓  JSON   : %s", json_out)

    # ── Step 3: Execute pytest ────────────────────────────────────────────
    logger.info("Step 3: Running pytest …")
    report_xml = output_dir / f"{model_name}_results.xml"
    report_md = output_dir / f"{model_name}_report.md"

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(script_path),
        "--tb=short",
        "-v",
        "-s",
        f"--junitxml={report_xml}",
        "--override-ini=addopts=",
        "-p",
        "no:cacheprovider",
        f"--dbt-unit-test-executor={executor}",
    ]
    try:
        import pytest_html  # type: ignore  # noqa: F401

        report_html = output_dir / f"{model_name}_report.html"
        cmd += [f"--html={report_html}", "--self-contained-html"]
    except ImportError:
        pass

    try:
        import xdist  # type: ignore  # noqa: F401

        cmd += ["-n", "auto"]
        logger.info("pytest-xdist detected — running tests in parallel")
    except ImportError:
        pass

    # Ensure the engine package is findable by pytest sub-process
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(_SCRIPTS_DIR) + os.pathsep + existing if existing else str(_SCRIPTS_DIR)
    run = subprocess.run(cmd, cwd=str(project_root), env=env)

    # ── Step 4: Markdown report ───────────────────────────────────────────
    try:
        MarkdownReportGenerator(
            xml_path=report_xml,
            json_path=json_out,
            model_name=model_name,
            output_path=report_md,
        ).generate()
        logger.info("  ✓  Report : %s", report_md)
    except Exception as exc:
        logger.warning("Could not generate Markdown report: %s", exc)

    if run.returncode == 0:
        print("\n  ✅  ALL TESTS PASSED")
    else:
        print("\n  ❌  SOME TESTS FAILED")

    return run.returncode


def main() -> int:
    p = argparse.ArgumentParser(description="dbt-unit-test skill: run from agent-generated JSON")
    p.add_argument("--json", required=True, help="Path to agent-generated test cases JSON")
    p.add_argument(
        "--executor",
        default="pandas",
        choices=["pyspark", "pandas"],
        help="SQL execution engine (default: pandas)",
    )
    p.add_argument(
        "--project-root",
        default=None,
        help="DBT project root (default: current working directory)",
    )
    args = p.parse_args()

    # Load .env so credentials in it (e.g. JIRA_API_TOKEN) reach os.environ.
    # Shell/CI env vars always win — load_dotenv() never overwrites existing values.
    _env_root = Path(args.project_root).resolve() if args.project_root else Path.cwd()
    load_dotenv(_env_root / ".env")

    json_path = Path(args.json).resolve()
    if not json_path.exists():
        print(f"[dbt-unit-test-skill] ERROR: JSON file not found: {json_path}", file=sys.stderr)
        return 1

    project_root = Path(args.project_root).resolve() if args.project_root else Path.cwd()

    return _run_pipeline(json_path, args.executor, project_root)


if __name__ == "__main__":
    sys.exit(main())
