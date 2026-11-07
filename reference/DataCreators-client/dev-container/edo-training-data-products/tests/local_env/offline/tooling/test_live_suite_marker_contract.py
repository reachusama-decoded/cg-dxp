from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
LIVE_SUITE = REPO_ROOT / "tests/local_env/live/cli_integration/test_cert_tool_integration.py"


def test_live_suite_file_exists() -> None:
    assert LIVE_SUITE.is_file()


def test_live_suite_is_integration_marked() -> None:
    content = LIVE_SUITE.read_text(encoding="utf-8")
    assert "pytestmark = [pytest.mark.integration]" in content
