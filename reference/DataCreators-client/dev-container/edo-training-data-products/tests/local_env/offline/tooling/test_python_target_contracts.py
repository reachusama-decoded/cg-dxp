from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_python_target_is_313_or_documented_exception() -> None:
    mise = (REPO_ROOT / ".mise.toml").read_text(encoding="utf-8")
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    readme = (REPO_ROOT / ".devcontainer" / "README.md").read_text(encoding="utf-8")

    assert 'python = "3.13' in mise
    assert 'python_version = "3.13"' in pyproject
    assert 'target-version = "py313"' in pyproject
    assert "Python 3.13" in readme
