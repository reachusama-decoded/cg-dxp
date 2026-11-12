"""Structural tests for the price sheet DAG: static, offline.

Cheap text checks that the DAG file has the expected shape, with no Airflow and no warehouse: the files
parse, the chain is wired, the callbacks and the SLA are attached at their scopes, and no file holds a
secret. Run with: pytest demos/airflow_local/dags/price_sheet/tests -q
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

DAGS_DIR = Path(__file__).resolve().parents[1] / "dags"
PRIMARY_DAG = DAGS_DIR / "price_sheet_daily.py"


def test_expected_dag_files_parse() -> None:
    """The DAG and its helper modules are present and are valid Python."""
    for path in (PRIMARY_DAG, DAGS_DIR / "callbacks.py", DAGS_DIR / "notifications.py"):
        assert path.exists(), f"missing file: {path.name}"
        ast.parse(path.read_text(encoding="utf-8"))


def test_chain_is_wired() -> None:
    """The one line the learners write: the five tasks in order."""
    text = PRIMARY_DAG.read_text(encoding="utf-8")
    assert re.search(
        r"^\s*start\s*>>\s*source_freshness_check\s*>>\s*dbt_pipeline\s*>>\s*publish_to_catalog\s*>>\s*end",
        text, re.MULTILINE,
    ), "the chain start >> source_freshness_check >> dbt_pipeline >> publish_to_catalog >> end is not wired"


def test_callbacks_and_sla_wired() -> None:
    """The tiered callbacks and the 90-minute SLA are attached at their scopes."""
    text = PRIMARY_DAG.read_text(encoding="utf-8")
    assert '"on_failure_callback": on_failure_callback' in text    # default_args: every task
    assert '"on_retry_callback": on_retry_callback' in text        # default_args: every task
    assert "sla_miss_callback=on_sla_miss_callback" in text        # on the DAG
    assert "on_success_callback=on_success_callback" in text       # on the last working task only
    assert re.search(r"sla\s*=\s*timedelta\(minutes=90\)", text), "publish_to_catalog must carry sla=timedelta(minutes=90)"


def test_no_secret_literals_in_dag_files() -> None:
    """No DAG file may hold a Databricks token or a workspace host."""
    leak = re.compile(r"dapi[0-9a-f]{16,}|cloud\.databricks\.com|adb-\d+\.\d+\.")
    for py in DAGS_DIR.glob("*.py"):
        assert not leak.search(py.read_text(encoding="utf-8")), f"possible secret in {py.name}"
