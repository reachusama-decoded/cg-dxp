"""Tests for the register-data-contract capability skill (binds RFD 0009).

Builds / updates an ODCS contract.yaml at
`data-products/{domain}/datasets/{product}/contract/contract.yaml`.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTER_PATH = (
    REPO_ROOT / "skills" / "register-data-contract" / "scripts" / "register.py"
)


def _load_register():
    spec = importlib.util.spec_from_file_location(
        "register_data_contract_register", REGISTER_PATH
    )
    assert spec and spec.loader, "could not build import spec"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def register():
    return _load_register()


def _make_product_path(tmp_path: Path, domain: str = "marketing", product: str = "leads") -> Path:
    p = tmp_path / "data-products" / domain / "datasets" / product
    (p / "contract").mkdir(parents=True)
    (p / "product.yaml").write_text(
        yaml.safe_dump({"domain": domain, "dataset": product})
    )
    return p


def _make_schema_file(tmp_path: Path) -> Path:
    schema_file = tmp_path / "schema.yaml"
    schema_file.write_text(
        yaml.safe_dump(
            {
                "properties": [
                    {"name": "lead_id", "logicalType": "string", "required": True},
                    {"name": "score", "logicalType": "integer", "required": False},
                ]
            }
        )
    )
    return schema_file


def _run_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(REGISTER_PATH), *args],
        capture_output=True,
        text=True,
    )


def test_creates_contract_yaml_with_odcs_structure(tmp_path):
    product_path = _make_product_path(tmp_path)
    schema_file = _make_schema_file(tmp_path)

    result = _run_cli(
        [
            "--product-path",
            str(product_path),
            "--owner-team",
            "marketing-data",
            "--sla-availability",
            "99.5%",
            "--sla-freshness",
            "PT15M",
            "--schema-file",
            str(schema_file),
        ]
    )
    assert result.returncode == 0, result.stderr

    contract_path = product_path / "contract" / "contract.yaml"
    assert contract_path.exists()
    data = yaml.safe_load(contract_path.read_text())

    assert data["version"] == "3.0.0"
    assert data["domain"] == "marketing"
    assert data["dataset"] == "leads"
    assert data["status"] == "draft"
    assert data["contract"]["owner"]["team"] == "marketing-data"
    assert data["contract"]["sla"]["availability"] == "99.5%"
    assert data["contract"]["sla"]["freshness"] == "PT15M"
    props = data["contract"]["schema"]["properties"]
    assert isinstance(props, list) and len(props) == 2
    assert props[0]["name"] == "lead_id"
    assert props[0]["logicalType"] == "string"


def test_rerun_bumps_patch_version(tmp_path):
    product_path = _make_product_path(tmp_path)
    schema_file = _make_schema_file(tmp_path)
    args = [
        "--product-path",
        str(product_path),
        "--owner-team",
        "marketing-data",
        "--sla-availability",
        "99.5%",
        "--sla-freshness",
        "PT15M",
        "--schema-file",
        str(schema_file),
    ]
    assert _run_cli(args).returncode == 0
    assert _run_cli(args).returncode == 0

    data = yaml.safe_load(
        (product_path / "contract" / "contract.yaml").read_text()
    )
    assert data["version"] == "3.0.1"
    assert data["contract"]["owner"]["team"] == "marketing-data"


def test_missing_schema_file_refuses(tmp_path):
    product_path = _make_product_path(tmp_path)
    result = _run_cli(
        [
            "--product-path",
            str(product_path),
            "--owner-team",
            "marketing-data",
            "--sla-availability",
            "99.5%",
            "--sla-freshness",
            "PT15M",
            "--schema-file",
            str(tmp_path / "nonexistent.yaml"),
        ]
    )
    assert result.returncode != 0
    contract_path = product_path / "contract" / "contract.yaml"
    assert not contract_path.exists()


def test_invalid_freshness_raises(register, tmp_path):
    product_path = _make_product_path(tmp_path)
    schema_file = _make_schema_file(tmp_path)
    with pytest.raises(ValueError, match="freshness"):
        register.build_and_validate(
            product_path=product_path,
            owner_team="marketing-data",
            sla_availability="99.5%",
            sla_freshness="15 minutes",
            schema_file=schema_file,
        )


def test_contract_round_trips(tmp_path):
    product_path = _make_product_path(tmp_path, domain="finance", product="ledgers")
    schema_file = _make_schema_file(tmp_path)
    result = _run_cli(
        [
            "--product-path",
            str(product_path),
            "--owner-team",
            "finance-core",
            "--sla-availability",
            "99.9%",
            "--sla-freshness",
            "PT1H",
            "--schema-file",
            str(schema_file),
        ]
    )
    assert result.returncode == 0
    text = (product_path / "contract" / "contract.yaml").read_text()
    data = yaml.safe_load(text)
    assert isinstance(data, dict)
    assert data["domain"] == "finance"
    assert data["dataset"] == "ledgers"
    # ensure JSON-serializable (no funky tags)
    json.dumps(data)
