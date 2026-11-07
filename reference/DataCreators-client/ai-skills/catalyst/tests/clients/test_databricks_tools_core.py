"""Vendored databricks_tools_core package integrity tests.

These tests are intentionally *narrow*: they apply only to the vendored
``skills/clients/databricks_tools_core`` package and do not generalise
to other skills.

Three concerns:
  1. Import smoke — all top-level public submodules must import cleanly.
  2. Dropped-subdir check — the 9 subdirectories removed in the OQ-7 wipe
     scope must not exist in the vendored package.
  3. (Placeholder) sqlfluff shim regression — ensure the package does not
     crash when sqlfluff is not installed.

Offline only — no LLM calls, no network I/O.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

# Ensure the repo root is on sys.path so vendored package imports work.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_PACKAGE_PATH = REPO_ROOT / "skills" / "clients" / "databricks_tools_core"

# The 9 subdirectories removed in the OQ-7 wipe scope.
_DROPPED_SUBDIRS = [
    "agent_bricks",
    "aibi_dashboards",
    "apps",
    "lakebase",
    "lakebase_autoscale",
    "pdf",
    "serving",
    "spark_declarative_pipelines",
    "vector_search",
]

# Top-level public submodules that must import cleanly.
_EXPECTED_SUBMODULES = [
    "auth",
    "client",
    "sql",
    "jobs",
    "unity_catalog",
    "compute",
    "dabs",
    "file",
]


# ---------------------------------------------------------------------------
# Guards — skip cleanly if the package is not present on this branch
# ---------------------------------------------------------------------------

_PACKAGE_PRESENT = _PACKAGE_PATH.is_dir()
_SKIP_REASON = (
    "skills/clients/databricks_tools_core is not present on this branch "
    "(it ships on feat/databricks-build-skills)"
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not _PACKAGE_PRESENT, reason=_SKIP_REASON)
@pytest.mark.parametrize("submodule", _EXPECTED_SUBMODULES)
def test_submodule_imports(submodule: str) -> None:
    """Each public submodule must import without raising."""
    import importlib  # noqa: PLC0415

    mod = importlib.import_module(f"skills.clients.databricks_tools_core.{submodule}")
    assert mod is not None


@pytest.mark.skipif(not _PACKAGE_PRESENT, reason=_SKIP_REASON)
@pytest.mark.parametrize("subdir", _DROPPED_SUBDIRS)
def test_dropped_subdir_absent(subdir: str) -> None:
    """OQ-7 wipe scope: these subdirs must not exist in the vendored package."""
    assert not (_PACKAGE_PATH / subdir).exists(), (
        f"{subdir} should have been dropped from the vendored package "
        f"but still exists at {_PACKAGE_PATH / subdir}"
    )


@pytest.mark.skipif(not _PACKAGE_PRESENT, reason=_SKIP_REASON)
def test_package_has_init(self=None) -> None:
    """The vendored package must have an __init__.py."""
    assert (_PACKAGE_PATH / "__init__.py").is_file(), (
        f"databricks_tools_core/__init__.py not found at {_PACKAGE_PATH}"
    )
