import os, stat
from tests.challenges.conftest import repo_root

CH = repo_root() / "challenges" / "v1" / "00-environment-check"

def test_verify_script_executable() -> None:
    assert (CH / "verify.sh").exists()
    assert os.stat(CH / "verify.sh").st_mode & stat.S_IXUSR

def test_guide_reframed_for_devcontainer() -> None:
    readme = (CH / "README.md").read_text().lower()
    assert "devcontainer" in readme
    assert "byod" not in readme and "laptop" not in readme  # preflight BYOD framing dropped
