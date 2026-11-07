from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_dind_split_files_exist() -> None:
    expected = [
        "tests/local_env/offline/devcontainer/test_dind_runtime_contracts.py",
        "tests/local_env/offline/airflow/test_local_airflow_contracts.py",
        "tests/local_env/offline/auth/test_databricks_auth_contracts.py",
        "tests/local_env/offline/tooling/test_docs_and_build_contracts.py",
    ]
    for rel in expected:
        assert (REPO_ROOT / rel).is_file(), rel
