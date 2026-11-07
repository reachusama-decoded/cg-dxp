"""Shared fixtures for marketplace client tests."""

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture
def valid_token_file(tmp_path, fixtures_dir):
    src = fixtures_dir / "valid_token.json"
    dst = tmp_path / "marketplace.json"
    dst.write_text(src.read_text())
    return dst


@pytest.fixture
def expired_token_file(tmp_path, fixtures_dir):
    src = fixtures_dir / "expired_token.json"
    dst = tmp_path / "marketplace.json"
    dst.write_text(src.read_text())
    return dst


@pytest.fixture
def isolated_config_dir(tmp_path, monkeypatch):
    """Redirect platformdirs config location to a tmp dir for the test.

    Works cross-platform: monkey-patches HOME (Linux/Mac), USERPROFILE/APPDATA
    (Windows), and platformdirs.user_config_dir directly.
    """
    fake_root = tmp_path / "config_root"
    fake_root.mkdir()
    fake_app = fake_root / "catalyst"
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "home"))
    monkeypatch.setenv("APPDATA", str(fake_root))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(fake_root))
    # Patch platformdirs to return the fake root, so token_path() lands inside fake_app
    import platformdirs
    monkeypatch.setattr(
        platformdirs, "user_config_dir",
        lambda *a, **kw: str(fake_app),
    )
    return fake_app
