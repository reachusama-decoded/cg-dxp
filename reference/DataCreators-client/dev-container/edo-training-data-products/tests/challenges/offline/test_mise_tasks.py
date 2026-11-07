import subprocess
import shutil
import pytest
from tests.challenges.conftest import repo_root


def _mise_tasks() -> str:
    if shutil.which("mise") is None:
        pytest.skip("mise not installed; skipping tests that require mise")
    return subprocess.run(["mise", "tasks", "--no-header"], cwd=repo_root(),
                          capture_output=True, text=True, check=True).stdout


def test_challenge_tasks_register() -> None:
    out = _mise_tasks()
    for task in ("challenge:verify", "challenge:verify-all", "challenge:dbt", "challenge:reset"):
        assert task in out, f"{task} must be registered in .mise.toml"


def test_challenge_toml_uses_nn_glob() -> None:
    toml = (repo_root() / ".mise.toml").read_text()
    assert 'challenges/v1/${usage_challenge' in toml or 'challenges/v1/$usage_challenge' in toml
