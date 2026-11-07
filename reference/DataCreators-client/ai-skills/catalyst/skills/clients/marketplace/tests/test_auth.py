import json
import os
import stat
import sys

import pytest

from skills.clients.marketplace import auth, exceptions as exc


def test_token_path_default():
    """Token path ends at catalyst/marketplace.json regardless of OS."""
    p = auth.token_path()
    assert p.name == "marketplace.json"
    # On Linux/Mac the parent contains "catalyst" under .config or similar.
    # On Windows it's under AppData/Roaming/catalyst.
    assert "catalyst" in p.parts


def test_load_token_missing_returns_none(isolated_config_dir):
    assert auth.load_token() is None


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX file modes don't apply on Windows")
def test_save_token_creates_dir_with_0700(isolated_config_dir):
    auth.save_token(
        bearer="Bearer eyXXX",
        api_base_url="https://example.com",
    )
    assert isolated_config_dir.exists()
    mode = stat.S_IMODE(isolated_config_dir.stat().st_mode)
    assert mode == 0o700, f"expected 0700, got {oct(mode)}"


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX file modes don't apply on Windows")
def test_save_token_writes_file_with_0600(isolated_config_dir):
    auth.save_token(bearer="Bearer eyXXX", api_base_url="https://example.com")
    f = isolated_config_dir / "marketplace.json"
    mode = stat.S_IMODE(f.stat().st_mode)
    assert mode == 0o600, f"expected 0600, got {oct(mode)}"


def test_save_then_load_roundtrip(isolated_config_dir):
    auth.save_token(bearer="Bearer eyXXX", api_base_url="https://example.com")
    tok = auth.load_token()
    assert tok is not None
    assert tok.bearer == "Bearer eyXXX"
    assert tok.api_base_url == "https://example.com"


def test_save_token_overwrites(isolated_config_dir):
    auth.save_token(bearer="Bearer A", api_base_url="https://x")
    auth.save_token(bearer="Bearer B", api_base_url="https://y")
    tok = auth.load_token()
    assert tok.bearer == "Bearer B"
    assert tok.api_base_url == "https://y"


def test_load_token_malformed_file_raises(isolated_config_dir):
    isolated_config_dir.mkdir(parents=True)
    (isolated_config_dir / "marketplace.json").write_text("not-json")
    with pytest.raises(exc.MarketplaceError):
        auth.load_token()


def test_clear_token_removes_file(isolated_config_dir):
    auth.save_token(bearer="Bearer A", api_base_url="https://x")
    auth.clear_token()
    assert auth.load_token() is None


def test_clear_token_when_missing_is_noop(isolated_config_dir):
    auth.clear_token()  # should not raise
    assert auth.load_token() is None


# ===== adversarial token cache state =====

def test_load_token_handles_truncated_json(isolated_config_dir):
    """File exists but JSON is mid-truncated (e.g., crash during write)."""
    isolated_config_dir.mkdir(parents=True)
    (isolated_config_dir / "marketplace.json").write_text('{"bearer": "Bearer eyXX')
    with pytest.raises(exc.MarketplaceError):
        auth.load_token()


def test_load_token_handles_empty_file(isolated_config_dir):
    """Zero-byte file (touched but never written)."""
    isolated_config_dir.mkdir(parents=True)
    (isolated_config_dir / "marketplace.json").write_text("")
    with pytest.raises(exc.MarketplaceError):
        auth.load_token()


def test_load_token_handles_missing_required_field(isolated_config_dir):
    """JSON is valid but doesn't have the bearer field."""
    isolated_config_dir.mkdir(parents=True)
    (isolated_config_dir / "marketplace.json").write_text(
        '{"captured_at": "2026-04-29T17:00:00Z", "api_base_url": "https://x"}'
    )
    with pytest.raises(exc.MarketplaceError):
        auth.load_token()


def test_load_token_handles_extra_fields_gracefully(isolated_config_dir):
    """Forward-compat: extra fields from a newer schema should not break loading."""
    isolated_config_dir.mkdir(parents=True)
    (isolated_config_dir / "marketplace.json").write_text(
        '{"bearer": "Bearer eyXXX", "captured_at": "2026-04-29T17:00:00Z", '
        '"api_base_url": "https://x", "future_field": "something_new"}'
    )
    tok = auth.load_token()
    assert tok is not None
    assert tok.bearer == "Bearer eyXXX"


def test_save_token_handles_existing_directory_at_path(isolated_config_dir):
    """If a DIRECTORY exists where the token FILE should be, error cleanly."""
    p = auth.token_path()
    p.mkdir(parents=True, exist_ok=True)
    with pytest.raises((IsADirectoryError, OSError, PermissionError)):
        auth.save_token(bearer="Bearer eyXXX", api_base_url="https://x")
