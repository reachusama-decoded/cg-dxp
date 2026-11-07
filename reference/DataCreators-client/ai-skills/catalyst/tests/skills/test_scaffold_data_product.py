"""Functional tests for the scaffold-data-product capability skill.

Asserts that running the skill's scaffold.py produces the RFD 0003
data-product subtree (airflow/, bundle/, dbt/, contract/, specs/) with
stub artifacts, and that name validation rejects non-snake-case inputs.

The skill directory uses a hyphen (`scaffold-data-product/`) which is not
a valid Python module name, so we load scaffold.py via importlib.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAFFOLD_PATH = (
    REPO_ROOT / "skills" / "scaffold-data-product" / "scripts" / "scaffold.py"
)


def _load_scaffold():
    spec = importlib.util.spec_from_file_location(
        "scaffold_data_product_scaffold", SCAFFOLD_PATH
    )
    assert spec and spec.loader, "could not build import spec"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def scaffold():
    return _load_scaffold()


def _run_cli(tmp_path: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCAFFOLD_PATH),
            "--domain",
            "marketing",
            "--product",
            "orders",
            "--team",
            "growth_team",
            "--target-dir",
            str(tmp_path),
            *extra,
        ],
        capture_output=True,
        text=True,
    )


def _product_root(tmp_path: Path) -> Path:
    return tmp_path / "data-products" / "marketing" / "datasets" / "orders"


def test_scaffold_creates_five_subdirs(tmp_path):
    result = _run_cli(tmp_path)
    assert result.returncode == 0, result.stderr

    root = _product_root(tmp_path)
    for sub in ("airflow", "bundle", "dbt", "contract", "specs"):
        assert (root / sub).is_dir(), f"missing subdir {sub}"


def test_scaffold_emits_no_gitkeep_markers(tmp_path):
    """The three otherwise-empty subdirs exist on disk but ship no .gitkeep —
    git picks them up when the next skill writes its first artifact there."""
    result = _run_cli(tmp_path)
    assert result.returncode == 0, result.stderr

    root = _product_root(tmp_path)
    leftover = list(root.rglob(".gitkeep"))
    assert leftover == [], f"unexpected .gitkeep markers: {leftover}"


def test_readme_mentions_team_and_product(tmp_path):
    result = _run_cli(tmp_path)
    assert result.returncode == 0, result.stderr

    readme = (_product_root(tmp_path) / "README.md").read_text()
    assert "growth_team" in readme
    assert "orders" in readme
    assert "marketing" in readme


def test_databricks_yml_stub_has_bundle_name(tmp_path):
    result = _run_cli(tmp_path)
    assert result.returncode == 0, result.stderr

    yml = (_product_root(tmp_path) / "bundle" / "databricks.yml").read_text()
    assert "bundle:" in yml
    assert "name: marketing_orders" in yml


def test_dbt_project_yml_stub_has_name_and_profile(tmp_path):
    result = _run_cli(tmp_path)
    assert result.returncode == 0, result.stderr

    yml = (_product_root(tmp_path) / "dbt" / "dbt_project.yml").read_text()
    assert "name: marketing_orders" in yml
    assert "profile: marketing_orders" in yml


def test_rerun_without_force_exits_nonzero(tmp_path):
    first = _run_cli(tmp_path)
    assert first.returncode == 0, first.stderr

    # Tamper with an existing file to verify it is NOT overwritten.
    readme = _product_root(tmp_path) / "README.md"
    readme.write_text("SENTINEL")

    second = _run_cli(tmp_path)
    assert second.returncode != 0
    assert readme.read_text() == "SENTINEL"


def test_force_regenerates(tmp_path):
    first = _run_cli(tmp_path)
    assert first.returncode == 0, first.stderr

    readme = _product_root(tmp_path) / "README.md"
    readme.write_text("SENTINEL")

    second = _run_cli(tmp_path, "--force")
    assert second.returncode == 0, second.stderr
    assert readme.read_text() != "SENTINEL"
    assert "orders" in readme.read_text()


def test_validate_name_rejects_uppercase(scaffold):
    with pytest.raises(ValueError):
        scaffold.validate_name("Marketing", field="domain")


def test_validate_name_rejects_hyphen(scaffold):
    with pytest.raises(ValueError):
        scaffold.validate_name("data-orders", field="product")


def test_validate_name_accepts_snake_case(scaffold):
    scaffold.validate_name("marketing_v2", field="domain")
    scaffold.validate_name("orders", field="product")


def test_cli_rejects_uppercase_domain(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCAFFOLD_PATH),
            "--domain",
            "Marketing",
            "--product",
            "orders",
            "--team",
            "growth_team",
            "--target-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert not (tmp_path / "data-products").exists()
