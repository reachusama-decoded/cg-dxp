from pathlib import Path
import pytest
from tests.challenges.conftest import repo_root, challenge_dirs


def test_challenges_readme_lists_full_path() -> None:
    readme = (repo_root() / "challenges" / "v1" / "README.md").read_text()
    for token in ("00-environment-check", "01-docker-intro", "02-dbt-pipeline",
                  "03-airflow-orchestration", "04-atlas-capstone"):
        assert token in readme, f"challenges/README.md must mention {token}"


def test_five_challenge_dirs_present() -> None:
    names = [p.name for p in challenge_dirs()]
    assert names == ["00-environment-check", "01-docker-intro", "02-dbt-pipeline",
                     "03-airflow-orchestration", "04-atlas-capstone"], names


def test_getting_started_points_to_challenges() -> None:
    gs = (repo_root() / "GETTING_STARTED.md").read_text()
    assert "challenges/README.md" in gs
