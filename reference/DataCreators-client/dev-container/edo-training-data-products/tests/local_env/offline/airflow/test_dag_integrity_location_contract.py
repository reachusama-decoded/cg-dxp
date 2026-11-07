from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_dag_integrity_suite_exists_under_local_env_offline_airflow() -> None:
    assert (REPO_ROOT / "tests/local_env/offline/airflow/test_dag_integrity.py").is_file()
