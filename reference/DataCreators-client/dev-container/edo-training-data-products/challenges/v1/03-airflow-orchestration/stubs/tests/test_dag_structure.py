"""Structural tests for the portfolio-analytics DAGs — static, offline.

Cheap ast/text checks that the DAG files parse into the expected shape without a
DagBag or a Databricks connection: both DAGs parse, the primary DAG wires the
tiered callbacks and the 90-minute SLA at their correct scopes, and no DAG file
embeds a Databricks token or workspace-host literal. Airflow itself lives in the
astro containers, so these stay import-free (static) and run with a plain
`pytest`. The freshness -> pipeline -> publish *chain* is the learner deliverable
and is checked separately by `mise run challenge:verify 03`.

Run with: `pytest data_products/portfolio_analytics/tests/ -q`
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

DAGS_DIR = Path(__file__).resolve().parents[1] / "dags"
PRIMARY_DAG = DAGS_DIR / "portfolio_analytics_daily.py"
SUBMIT_DAG = DAGS_DIR / "databricks_submit_run_dag.py"


def test_expected_dag_files_parse() -> None:
    """Both DAGs and the callbacks module are present and parse as valid Python."""
    for path in (PRIMARY_DAG, SUBMIT_DAG, DAGS_DIR / "callbacks.py"):
        assert path.exists(), f"missing DAG file: {path.name}"
        ast.parse(path.read_text(encoding="utf-8"))


def test_primary_dag_callbacks_and_sla_wired() -> None:
    """The tiered callbacks and the 90-minute SLA are attached at their scopes."""
    text = PRIMARY_DAG.read_text(encoding="utf-8")
    assert "on_failure_callback" in text                       # default_args: every task
    assert "on_retry_callback" in text                         # default_args: every task
    assert "sla_miss_callback=on_sla_miss_callback" in text    # DAG-level
    assert "on_success_callback=on_success_callback" in text   # final task only
    assert re.search(r"sla\s*=\s*timedelta\(minutes=90\)", text), (
        "publish_to_catalog must carry sla=timedelta(minutes=90)"
    )


def test_no_secret_literals_in_dag_files() -> None:
    """No DAG file may embed a Databricks token or workspace-host literal."""
    leak = re.compile(r"dapi[0-9a-f]{16,}|cloud\.databricks\.com|adb-\d+\.\d+\.")
    for py in DAGS_DIR.glob("*.py"):
        text = py.read_text(encoding="utf-8")
        assert not leak.search(text), f"possible secret literal in {py.name}"
