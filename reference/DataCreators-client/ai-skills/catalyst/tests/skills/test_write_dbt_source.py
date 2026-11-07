"""Functional tests for the write-dbt-source capability skill.

Invokes scripts/write_source.py against a synthetic product directory
and asserts that the rendered dbt sources YAML satisfies SQL-DBSQL-005
(external tables only) and PY-NAMING-* (snake_case source names).
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WRITE_SOURCE_PATH = (
    REPO_ROOT / "skills" / "write-dbt-source" / "scripts" / "write_source.py"
)


def _make_product(
    tmp_path: Path,
    *,
    with_yaml: bool = True,
    uc_catalog: str | None = None,
    domain: str = "marketing",
) -> Path:
    product_root = (
        tmp_path / "data-products" / domain / "datasets" / "orders"
    )
    (product_root / "specs").mkdir(parents=True)
    (product_root / "dbt").mkdir()
    if with_yaml:
        body = textwrap.dedent(
            f"""\
            domain: {domain}
            product: orders
            owner: growth_team
            lifecycle: build
            """
        )
        if uc_catalog is not None:
            body += f"meta:\n  uc_catalog: {uc_catalog}\n"
        (product_root / "specs" / "product.yaml").write_text(body)
    return product_root


def _run_cli(
    product: Path,
    *,
    source_name: str = "salesforce",
    layer: str | None = None,
    catalog: str | None = None,
    schema: str | None = "raw_salesforce",
    tables: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    argv = [
        sys.executable,
        str(WRITE_SOURCE_PATH),
        "--product",
        str(product),
        "--source-name",
        source_name,
    ]
    if layer is not None:
        argv += ["--layer", layer]
    if catalog is not None:
        argv += ["--catalog", catalog]
    if schema is not None:
        argv += ["--schema", schema]
    for t in tables or ["accounts", "contacts"]:
        argv += ["--tables", t]
    return subprocess.run(argv, capture_output=True, text=True)


def _read_sources(product: Path, layer: str = "staging") -> dict:
    path = product / "dbt" / layer / f"_{layer}__sources.yml"
    assert path.is_file(), f"missing sources yml: {path}"
    return yaml.safe_load(path.read_text())


def test_happy_path_writes_sources_yml(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(product)
    assert result.returncode == 0, result.stderr
    doc = _read_sources(product)
    assert doc["version"] == 2
    assert len(doc["sources"]) == 1
    assert doc["sources"][0]["name"] == "salesforce"


def test_multiple_tables_flags_accumulate(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(
        product, tables=["accounts", "contacts", "opportunities"]
    )
    assert result.returncode == 0, result.stderr
    doc = _read_sources(product)
    names = [t["name"] for t in doc["sources"][0]["tables"]]
    assert names == ["accounts", "contacts", "opportunities"]


def test_catalog_default_from_meta_uc_catalog(tmp_path):
    product = _make_product(tmp_path, uc_catalog="prod_marketing")
    result = _run_cli(product)
    assert result.returncode == 0, result.stderr
    doc = _read_sources(product)
    assert doc["sources"][0]["catalog"] == "prod_marketing"


def test_catalog_default_from_domain_when_meta_absent(tmp_path):
    product = _make_product(tmp_path, domain="marketing")
    result = _run_cli(product)
    assert result.returncode == 0, result.stderr
    doc = _read_sources(product)
    assert doc["sources"][0]["catalog"] == "marketing"


def test_schema_is_required(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(product, schema=None)
    assert result.returncode != 0
    assert "schema" in (result.stderr + result.stdout).lower()


def test_source_yaml_declares_all_named_tables(tmp_path):
    product = _make_product(tmp_path)
    tables = ["accounts", "contacts", "leads", "opportunities"]
    result = _run_cli(product, tables=tables)
    assert result.returncode == 0, result.stderr
    doc = _read_sources(product)
    rendered_names = [t["name"] for t in doc["sources"][0]["tables"]]
    assert rendered_names == tables


def test_freshness_block_present(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(product)
    assert result.returncode == 0, result.stderr
    doc = _read_sources(product)
    for table in doc["sources"][0]["tables"]:
        assert "loaded_at_field" in table
        assert "freshness" in table
        freshness = table["freshness"]
        assert "warn_after" in freshness
        assert "error_after" in freshness


def test_snake_case_enforcement_on_source_name(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(product, source_name="SalesForce")
    assert result.returncode != 0
    assert "snake_case" in (result.stderr + result.stdout).lower()


def test_idempotent_rerun_overwrites_cleanly(tmp_path):
    product = _make_product(tmp_path)
    first = _run_cli(product, tables=["accounts"])
    assert first.returncode == 0, first.stderr
    second = _run_cli(product, tables=["accounts", "contacts"])
    assert second.returncode == 0, second.stderr
    doc = _read_sources(product)
    names = [t["name"] for t in doc["sources"][0]["tables"]]
    assert names == ["accounts", "contacts"]


def test_layer_flag_changes_output_path(tmp_path):
    product = _make_product(tmp_path)
    result = _run_cli(product, layer="raw")
    assert result.returncode == 0, result.stderr
    path = product / "dbt" / "raw" / "_raw__sources.yml"
    assert path.is_file()


def test_explicit_catalog_overrides_default(tmp_path):
    product = _make_product(tmp_path, uc_catalog="prod_marketing")
    result = _run_cli(product, catalog="override_catalog")
    assert result.returncode == 0, result.stderr
    doc = _read_sources(product)
    assert doc["sources"][0]["catalog"] == "override_catalog"


def test_external_location_marker_present(tmp_path):
    """SQL-DBSQL-005: sources are documented as external."""
    product = _make_product(tmp_path)
    result = _run_cli(product)
    assert result.returncode == 0, result.stderr
    doc = _read_sources(product)
    for table in doc["sources"][0]["tables"]:
        assert "external" in table
