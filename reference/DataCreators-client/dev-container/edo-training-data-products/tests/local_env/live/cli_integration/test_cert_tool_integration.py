"""Live cert integration checks for databricks, dbt, and astro CLIs.

These tests are opt-in to keep default CI deterministic.
Enable with: CERT_INTEGRATION_TESTS=1
"""

from __future__ import annotations

import configparser
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
DBT_PROJECT_DIR = REPO_ROOT / "data_products" / "atlas_elt"
DBT_PROFILES_DIR = DBT_PROJECT_DIR / "dbt_profiles"


def _enabled() -> bool:
    return os.environ.get("CERT_INTEGRATION_TESTS", "").strip().lower() in {"1", "true", "yes"}


def _run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )


def _has_default_databricks_profile() -> bool:
    cfg_path = Path.home() / ".databrickscfg"
    if not cfg_path.exists():
        return False

    parser = configparser.ConfigParser()
    parser.read(cfg_path)
    if "DEFAULT" not in parser:
        return False

    section = parser["DEFAULT"]
    return bool(section.get("host")) and bool(section.get("token"))


def _has_databricks_auth() -> bool:
    env_ok = bool(os.environ.get("DATABRICKS_HOST") and os.environ.get("DATABRICKS_TOKEN"))
    return env_ok or _has_default_databricks_profile()


def _has_astro_auth() -> bool:
    # Keep this strict to avoid false failures in environments with no Astro login state.
    return bool(os.environ.get("ASTRO_API_TOKEN"))


pytestmark = [pytest.mark.integration]


@pytest.mark.skipif(not _enabled(), reason="Set CERT_INTEGRATION_TESTS=1 to run live cert integration checks")
def test_databricks_cli_tls_handshake() -> None:
    """Validate Databricks CLI can perform a live API call using configured cert chain."""
    if not shutil.which("databricks"):
        pytest.skip("databricks CLI not found in PATH")
    if not _has_databricks_auth():
        pytest.skip("Databricks auth is not configured (env vars or ~/.databrickscfg [DEFAULT])")

    result = _run(["databricks", "current-user", "me"])
    assert result.returncode == 0, (
        "databricks live check failed; this may indicate TLS, network, or auth issues\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


@pytest.mark.skipif(not _enabled(), reason="Set CERT_INTEGRATION_TESTS=1 to run live cert integration checks")
def test_dbt_cli_tls_handshake_via_wrapper() -> None:
    """Validate dbt (through repo wrapper) can establish a live Databricks connection."""
    if not shutil.which("python"):
        pytest.skip("python executable not found in PATH")
    if not _has_databricks_auth():
        pytest.skip("Databricks auth is not configured (env vars or ~/.databrickscfg [DEFAULT])")

    result = _run(
        [
            "python",
            "dbt_wrapper.py",
            "debug",
            "--connection",
            "--project-dir",
            str(DBT_PROJECT_DIR),
            "--profiles-dir",
            str(DBT_PROFILES_DIR),
            "--target",
            "local",
        ],
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, (
        "dbt live check failed; this may indicate TLS, network, profile, or auth issues\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


@pytest.mark.skipif(not _enabled(), reason="Set CERT_INTEGRATION_TESTS=1 to run live cert integration checks")
def test_astro_cli_tls_handshake() -> None:
    """Validate Astro CLI can make a live API call with configured cert chain."""
    if not shutil.which("astro"):
        pytest.skip("astro CLI not found in PATH")
    if not _has_astro_auth():
        pytest.skip("Astro auth not configured (ASTRO_API_TOKEN is required for this test)")

    result = _run(["astro", "workspace", "list"])
    assert result.returncode == 0, (
        "astro live check failed; this may indicate TLS, network, or auth issues\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
