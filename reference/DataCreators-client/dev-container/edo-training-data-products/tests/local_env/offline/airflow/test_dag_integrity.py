from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
DAGS_ROOT = REPO_ROOT / "data_products"
BLUEPRINTS_ROOT = DAGS_ROOT / ".blueprints"

pytestmark = pytest.mark.airflow


def _dag_py_files() -> list[Path]:
    return sorted(DAGS_ROOT.rglob("*.dag.py"))


def _dag_yaml_files() -> list[Path]:
    return sorted({*DAGS_ROOT.rglob("*.dag.yml"), *DAGS_ROOT.rglob("*.dag.yaml")})


def _blueprint_files() -> list[Path]:
    return sorted(BLUEPRINTS_ROOT.glob("*.py"))


def _retry_values(text: str) -> list[int]:
    values: list[int] = []
    for pattern in (
        re.compile(r"retries\s*=\s*(-?\d+)"),
        re.compile(r"['\"]retries['\"]\s*:\s*(-?\d+)"),
    ):
        values.extend(int(match.group(1)) for match in pattern.finditer(text))
    return values


def _assert_python_dag_files_parse_cleanly() -> None:
    # Why: the offline suite must stay deterministic even when Airflow is not
    # installed, so we validate the DAG declaration files directly.
    for path in _dag_py_files():
        text = path.read_text(encoding="utf-8")
        ast.parse(text, filename=str(path))


def _assert_python_dag_files_have_tags() -> None:
    for path in _dag_py_files():
        text = path.read_text(encoding="utf-8")
        assert "tags=" in text, f"{path} must declare DAG tags"


def _assert_yaml_dag_files_parse_and_have_tags() -> None:
    for path in _dag_yaml_files():
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        assert isinstance(payload, dict), f"{path} must parse to a mapping"
        assert "dag_id" in payload, f"{path} must declare dag_id"
        assert payload.get("tags"), f"{path} must declare tags"


def _assert_retry_contracts_are_non_negative() -> None:
    blueprint_retry_values = {
        path.stem: _retry_values(path.read_text(encoding="utf-8"))
        for path in _blueprint_files()
    }

    for path in _dag_py_files():
        values = _retry_values(path.read_text(encoding="utf-8"))
        if not values:
            continue
        assert all(value >= 0 for value in values), f"{path} must not declare negative retries"

    for path in _dag_yaml_files():
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        step_values = payload.get("steps", {})
        blueprints = [
            step.get("blueprint")
            for step in step_values.values()
            if isinstance(step, dict) and step.get("blueprint")
        ]
        for blueprint_name in blueprints:
            values = blueprint_retry_values.get(str(blueprint_name), [])
            if not values:
                continue
            assert all(value >= 0 for value in values), (
                f"{path} uses blueprint {blueprint_name} with negative retries"
            )


def test_airflow_dags_import_cleanly() -> None:
    _assert_python_dag_files_parse_cleanly()
    _assert_yaml_dag_files_parse_and_have_tags()


def test_airflow_dags_have_tags() -> None:
    _assert_python_dag_files_have_tags()
    _assert_yaml_dag_files_parse_and_have_tags()


def test_airflow_dags_default_to_non_negative_retries() -> None:
    _assert_retry_contracts_are_non_negative()
