"""Functional tests for the write-dbt-model capability skill.

Asserts that running the skill's write_model.py against a product
directory produces a dbt model `.sql` file plus a `.yml` config file
compliant with SQL-DBSQL-* and PY-NAMING-*.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WRITE_MODEL_PATH = (
    REPO_ROOT / "skills" / "write-dbt-model" / "scripts" / "write_model.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "write_dbt_model_write_model", WRITE_MODEL_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def write_model_mod():
    return _load_module()


def _make_product(tmp_path: Path) -> Path:
    product_root = tmp_path / "data-products" / "marketing" / "datasets" / "orders"
    (product_root / "dbt").mkdir(parents=True)
    return product_root


def _run_cli(
    product: Path,
    *,
    model_name: str = "stg_orders",
    layer: str = "staging",
    materialization: str = "view",
    unique_key: str | None = None,
) -> subprocess.CompletedProcess[str]:
    argv = [
        sys.executable,
        str(WRITE_MODEL_PATH),
        "--product",
        str(product),
        "--model-name",
        model_name,
        "--layer",
        layer,
        "--materialization",
        materialization,
    ]
    if unique_key is not None:
        argv.extend(["--unique-key", unique_key])
    return subprocess.run(argv, capture_output=True, text=True)


def test_happy_path_view_writes_sql_and_yml(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(product, materialization="view")
    assert result.returncode == 0, result.stderr

    sql_path = product / "dbt" / "staging" / "stg_orders.sql"
    yml_path = product / "dbt" / "staging" / "_staging__models.yml"
    assert sql_path.is_file()
    assert yml_path.is_file()


def test_snake_case_enforced_rejects_pascal_case(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(product, model_name="StgOrders")
    assert result.returncode == 2
    assert "snake_case" in (result.stderr + result.stdout)


def test_snake_case_enforced_rejects_kebab_case(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(product, model_name="stg-orders")
    assert result.returncode == 2
    assert "snake_case" in (result.stderr + result.stdout)


def test_incremental_requires_unique_key(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(product, materialization="incremental")
    assert result.returncode == 2
    assert "unique-key" in (result.stderr + result.stdout) or "unique_key" in (
        result.stderr + result.stdout
    )


def test_incremental_config_uses_merge_strategy(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(
        product,
        materialization="incremental",
        unique_key="order_id",
        layer="intermediate",
    )
    assert result.returncode == 0, result.stderr

    sql = (product / "dbt" / "intermediate" / "stg_orders.sql").read_text()
    assert "incremental_strategy='merge'" in sql
    assert "unique_key='order_id'" in sql


def test_table_materialization_renders(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(product, materialization="table", layer="marts")
    assert result.returncode == 0, result.stderr

    sql = (product / "dbt" / "marts" / "stg_orders.sql").read_text()
    assert "materialized='table'" in sql


def test_file_format_delta_default(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(product, materialization="table")
    assert result.returncode == 0, result.stderr

    sql = (product / "dbt" / "staging" / "stg_orders.sql").read_text()
    assert "file_format='delta'" in sql


def test_location_root_present_external_table(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(product, materialization="table")
    assert result.returncode == 0, result.stderr

    sql = (product / "dbt" / "staging" / "stg_orders.sql").read_text()
    assert "location_root" in sql


def test_vacuum_hint_in_rendered_sql(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(product, materialization="table")
    assert result.returncode == 0, result.stderr

    sql = (product / "dbt" / "staging" / "stg_orders.sql").read_text()
    assert "168" in sql and "VACUUM" in sql.upper()


def test_layer_choice_rejects_unknown(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(product, layer="bronze")
    assert result.returncode != 0


def test_yml_has_not_null_test_stub(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(product, materialization="view")
    assert result.returncode == 0, result.stderr

    yml_text = (
        product / "dbt" / "staging" / "_staging__models.yml"
    ).read_text()
    data = yaml.safe_load(yml_text)
    models = data["models"]
    assert any(
        any("not_null" in (col.get("tests") or []) for col in m.get("columns", []))
        for m in models
    )


def test_idempotent_rerun(tmp_path):
    product = _make_product(tmp_path)
    r1 = _run_cli(product, materialization="view")
    assert r1.returncode == 0, r1.stderr
    r2 = _run_cli(product, materialization="view")
    assert r2.returncode == 0, r2.stderr

    sql = (product / "dbt" / "staging" / "stg_orders.sql").read_text()
    yml_text = (
        product / "dbt" / "staging" / "_staging__models.yml"
    ).read_text()
    data = yaml.safe_load(yml_text)
    # Model appears exactly once in the yml after re-run.
    names = [m["name"] for m in data["models"]]
    assert names.count("stg_orders") == 1
    assert "stg_orders" in sql
