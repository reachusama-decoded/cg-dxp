from __future__ import annotations

from tests.challenges.conftest import repo_root

CH = repo_root() / "challenges" / "v1" / "01-docker-intro"


def test_starter_solution_and_verify_present() -> None:
    assert (CH / "starter" / "Dockerfile").exists()
    assert (CH / "solution" / "Dockerfile").exists()
    assert (CH / "verify.sh").exists()
    assert (CH / "starter" / "app").is_dir()
    assert (CH / "solution" / "app").is_dir()
    assert not (CH / "Dockerfile").exists()
    assert not (CH / "app").exists()

    for filename in ("summarize.py", "holdings.csv"):
        assert (CH / "starter" / "app" / filename).read_bytes() == (
            CH / "solution" / "app" / filename
        ).read_bytes()


def test_starter_is_unsolved_and_solution_is_complete() -> None:
    # 01 builds its own python:3.11-slim image, independent of the devcontainer's 3.13.
    starter = (CH / "starter" / "Dockerfile").read_text()
    solution = (CH / "solution" / "Dockerfile").read_text()

    assert "python:3.11-slim" in starter
    assert starter.count("TODO") == 3
    assert "WORKDIR /app" not in starter
    assert "COPY app/ ./" not in starter
    assert 'CMD ["python", "summarize.py"]' not in starter

    assert "python:3.11-slim" in solution
    assert "WORKDIR /app" in solution
    assert "COPY app/ ./" in solution
    assert 'CMD ["python", "summarize.py"]' in solution


def test_verify_defaults_to_starter_and_supports_solution_override() -> None:
    script = (CH / "verify.sh").read_text()
    assert 'BUILD_CONTEXT="${CHALLENGE_DOCKER_CONTEXT:-starter}"' in script
    assert 'DOCKER_CONTEXT="' not in script
    assert "docker build" in script
    assert '[[ "$OUTPUT" == "$EXPECTED" ]]' in script


def test_readme_uses_starter_workflow() -> None:
    readme = (CH / "README.md").read_text()
    assert "cd challenges/v1/01-docker-intro/starter" in readme
    assert "Open `Dockerfile` in the `starter/` folder" in readme
    assert "mise run challenge:verify 01" in readme
    assert "`solution/Dockerfile`" in readme
