"""Tests for the shared promotions helper at skills/_lib/promotions.py.

Loads the module via importlib because `skills/_lib/` is not an
installable package on sys.path.
"""

from __future__ import annotations

import importlib.util
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROMOTIONS_PATH = REPO_ROOT / "skills" / "_lib" / "promotions.py"


def _load_promotions():
    spec = importlib.util.spec_from_file_location(
        "catalyst_lib_promotions", PROMOTIONS_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def promotions():
    return _load_promotions()


def _write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "promotions.yml"
    p.write_text(textwrap.dedent(body))
    return p


def test_valid_yaml_returns_correct_id(promotions, tmp_path):
    path = _write(
        tmp_path,
        """\
        astronomer:
          dev:
            deployment_id: "dpl-dev-001"
          qa:
            deployment_id: "dpl-qa-001"
          prod:
            deployment_id: "dpl-prod-001"
        """,
    )
    assert promotions.read_deployment_id(path, "astronomer", "dev") == "dpl-dev-001"
    assert promotions.read_deployment_id(path, "astronomer", "qa") == "dpl-qa-001"
    assert promotions.read_deployment_id(path, "astronomer", "prod") == "dpl-prod-001"


def test_missing_system_raises(promotions, tmp_path):
    path = _write(
        tmp_path,
        """\
        astronomer:
          dev: { deployment_id: "dpl-dev-001" }
        """,
    )
    with pytest.raises((KeyError, ValueError)) as exc:
        promotions.read_deployment_id(path, "databricks", "dev")
    assert "databricks" in str(exc.value)


def test_missing_target_raises(promotions, tmp_path):
    path = _write(
        tmp_path,
        """\
        astronomer:
          dev: { deployment_id: "dpl-dev-001" }
        """,
    )
    with pytest.raises((KeyError, ValueError)) as exc:
        promotions.read_deployment_id(path, "astronomer", "prod")
    assert "prod" in str(exc.value)


def test_malformed_yaml_raises(promotions, tmp_path):
    path = tmp_path / "promotions.yml"
    path.write_text("astronomer:\n  dev: [unbalanced\n")
    with pytest.raises(Exception):
        promotions.read_deployment_id(path, "astronomer", "dev")


def test_missing_deployment_id_field_raises(promotions, tmp_path):
    path = _write(
        tmp_path,
        """\
        astronomer:
          dev: {}
        """,
    )
    with pytest.raises((KeyError, ValueError)):
        promotions.read_deployment_id(path, "astronomer", "dev")


def test_missing_file_raises(promotions, tmp_path):
    with pytest.raises(FileNotFoundError):
        promotions.read_deployment_id(
            tmp_path / "nope.yml", "astronomer", "dev"
        )
