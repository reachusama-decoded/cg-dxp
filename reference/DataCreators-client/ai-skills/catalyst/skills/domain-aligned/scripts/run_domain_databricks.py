"""Execute domain-aligned dbt models against Databricks SQL warehouse.

Runs the generated dbt project, validates results, and produces a Databricks report.

Usage:
    python run_domain_databricks.py \
        --model-name <model> \
        --dbt-dir <path/to/dbt/> \
        [--select <dbt_selector>] \
        [--full-refresh]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent

# Add shared scripts to path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "shared"))

try:
    from config import load_env
except ImportError:
    def load_env(env_path=None, override=False):
        """Fallback env loader."""
        env_file = Path(env_path) if env_path else REPO_ROOT / ".env"
        if not env_file.exists():
            return
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if not override and key in os.environ:
                    continue
                os.environ[key] = value


def _copy_macro_overrides(dbt_dir: Path) -> None:
    """Copy macro templates into the dbt project."""
    templates = Path(__file__).resolve().parent.parent / "templates" / "dbt_project" / "macros"
    if not templates.exists():
        return
    macros_dir = dbt_dir / "macros"
    macros_dir.mkdir(parents=True, exist_ok=True)
    for macro_file in templates.glob("*.sql"):
        dest = macros_dir / macro_file.name
        if not dest.exists():
            shutil.copy2(macro_file, dest)
            print(f"  copied macro: {macro_file.name}")


def _run_dbt(dbt_dir: Path, command: list[str]) -> subprocess.CompletedProcess:
    """Run a dbt command in the project directory."""
    env = os.environ.copy()
    # Ensure profiles dir is set to the dbt project directory
    env["DBT_PROFILES_DIR"] = str(dbt_dir)

    cmd = ["dbt"] + command + ["--project-dir", str(dbt_dir)]
    print(f"  running: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(dbt_dir),
        timeout=600,
    )

    if result.stdout:
        print(result.stdout)
    if result.returncode != 0 and result.stderr:
        print(result.stderr, file=sys.stderr)

    return result


def _get_row_counts(dbt_dir: Path) -> dict[str, int | str]:
    """Extract row counts from run_results.json if available."""
    results_path = dbt_dir / "target" / "run_results.json"
    if not results_path.exists():
        return {}

    with open(results_path, encoding="utf-8") as f:
        results = json.load(f)

    counts = {}
    for result in results.get("results", []):
        node_id = result.get("unique_id", "")
        model_name = node_id.split(".")[-1] if "." in node_id else node_id
        rows = result.get("adapter_response", {}).get("rows_affected", "N/A")
        counts[model_name] = rows

    return counts


def _generate_report(
    model_name: str,
    dbt_dir: Path,
    run_success: bool,
    test_success: bool,
    row_counts: dict,
) -> str:
    """Generate a markdown Databricks report."""
    status = "SUCCESS" if (run_success and test_success) else "FAILED"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    rows_table = "
".join(
        f"| {name} | {count} |" for name, count in row_counts.items()
    )
    if not rows_table:
        rows_table = "| (no results) | - |"

    return dedent(f"""\
        # Databricks Report: {model_name}

        **Generated:** {timestamp}

        ## Execution Summary

        - **Status:** {status}
        - **dbt run:** {"PASS" if run_success else "FAIL"}
        - **dbt test:** {"PASS" if test_success else "FAIL"}
        - **Project:** {dbt_dir}

        ## Row Counts

        | Model | Rows |
        |-------|------|
        {rows_table}

        ## Next Steps

        {"- Review the data in Databricks" if run_success else "- Fix errors and re-run"}
        - Iterate on the model if needed
        - Hand off to Hourglass for production deployment
    """)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run domain-aligned dbt on Databricks")
    parser.add_argument("--model-name", required=True, help="Canonical model name")
    parser.add_argument("--dbt-dir", required=True, help="Path to generated dbt project")
    parser.add_argument("--select", default=None, help="dbt model selector (default: +<model_name>)")
    parser.add_argument("--full-refresh", action="store_true", help="Run with --full-refresh")
    parser.add_argument("--env-file", default=None, help="Path to .env file")
    args = parser.parse_args()

    # Load environment
    load_env(args.env_file)

    # Validate required env vars
    required_vars = ["DATABRICKS_HOST", "DATABRICKS_TOKEN"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        print(f"error: Missing env vars: {missing}", file=sys.stderr)
        print("Set these in .env or export them.", file=sys.stderr)
        sys.exit(1)

    dbt_dir = Path(args.dbt_dir).resolve()
    if not (dbt_dir / "dbt_project.yml").exists():
        print(f"error: No dbt_project.yml found in {dbt_dir}", file=sys.stderr)
        sys.exit(1)

    model_name = args.model_name
    selector = args.select or f"+{model_name}"

    print(f"Running domain-aligned Databricks execution for: {model_name}")
    print(f"  dbt project: {dbt_dir}")
    print(f"  selector: {selector}")

    # Copy macros
    _copy_macro_overrides(dbt_dir)

    # Check for packages.yml
    if (dbt_dir / "packages.yml").exists():
        print("
Installing dbt packages...")
        _run_dbt(dbt_dir, ["deps"])

    # Run models
    print("
Running dbt models...")
    run_cmd = ["run", "--select", selector]
    if args.full_refresh:
        run_cmd.append("--full-refresh")
    run_result = _run_dbt(dbt_dir, run_cmd)
    run_success = run_result.returncode == 0

    # Run tests
    print("
Running dbt tests...")
    test_result = _run_dbt(dbt_dir, ["test", "--select", selector])
    test_success = test_result.returncode == 0

    # Get row counts
    row_counts = _get_row_counts(dbt_dir)

    # Generate report
    report = _generate_report(
        model_name=model_name,
        dbt_dir=dbt_dir,
        run_success=run_success,
        test_success=test_success,
        row_counts=row_counts,
    )

    # Write report
    databricks_dir = dbt_dir.parent / "databricks"
    databricks_dir.mkdir(parents=True, exist_ok=True)
    report_path = databricks_dir / "databricks_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"
Databricks report: {report_path}")

    # Copy run_results
    run_results_src = dbt_dir / "target" / "run_results.json"
    if run_results_src.exists():
        shutil.copy2(run_results_src, databricks_dir / "run_results.json")

    if not run_success:
        print("
Databricks execution FAILED — check errors above.", file=sys.stderr)
        sys.exit(1)

    print("
Databricks execution completed successfully.")


if __name__ == "__main__":
    main()
