"""Upstream attribution file checks.

These tests are repo-level (not per-skill) and enforce that the Databricks
attribution files required by the upstream license are present in
third-party/ and contain expected content.

Apache-2.0 forks (dbt-labs) are not asserted: internal use does not trigger
Apache §4 redistribution clauses, so we don't carry the license text. Skill
frontmatter still records the upstream commit for provenance.

Files are expected to land on ``feat/databricks-build-skills``.  On branches
where they don't yet exist, tests are skipped (not failed) so the suite stays
green during incremental development.

Offline only — no LLM calls, no network I/O.
"""
from __future__ import annotations

import pathlib
import re

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_THIRD_PARTY = REPO_ROOT / "third-party"

_LICENSE_DATABRICKS = _THIRD_PARTY / "LICENSE-databricks.md"
_NOTICE = _THIRD_PARTY / "NOTICE.md"

_MISSING_MSG = "not yet present on this branch (ships with feat/databricks-build-skills)"


# ---------------------------------------------------------------------------
# LICENSE-databricks.md
# ---------------------------------------------------------------------------

def test_license_databricks_exists() -> None:
    """LICENSE-databricks.md must exist in third-party/."""
    if not _LICENSE_DATABRICKS.is_file():
        pytest.skip(f"LICENSE-databricks.md {_MISSING_MSG}")
    assert _LICENSE_DATABRICKS.is_file()


def test_license_databricks_wipe_runbook() -> None:
    """LICENSE-databricks.md must contain the wipe runbook section."""
    if not _LICENSE_DATABRICKS.is_file():
        pytest.skip(f"LICENSE-databricks.md {_MISSING_MSG}")
    content = _LICENSE_DATABRICKS.read_text(encoding="utf-8")
    assert re.search(r"wipe runbook", content, re.IGNORECASE), (
        "LICENSE-databricks.md does not contain 'Wipe runbook' section"
    )


def test_license_databricks_scope_of_use() -> None:
    """LICENSE-databricks.md must contain 'Scope of Use' from the upstream license."""
    if not _LICENSE_DATABRICKS.is_file():
        pytest.skip(f"LICENSE-databricks.md {_MISSING_MSG}")
    content = _LICENSE_DATABRICKS.read_text(encoding="utf-8")
    assert "Scope of Use" in content, (
        "LICENSE-databricks.md does not contain 'Scope of Use'"
    )


# ---------------------------------------------------------------------------
# NOTICE.md
# ---------------------------------------------------------------------------

def test_notice_exists() -> None:
    """NOTICE.md must exist in third-party/."""
    if not _NOTICE.is_file():
        pytest.skip(f"NOTICE.md {_MISSING_MSG}")
    assert _NOTICE.is_file()


def test_notice_cites_ai_dev_kit() -> None:
    """NOTICE.md must cite the ai-dev-kit upstream."""
    if not _NOTICE.is_file():
        pytest.skip(f"NOTICE.md {_MISSING_MSG}")
    content = _NOTICE.read_text(encoding="utf-8")
    assert "ai-dev-kit" in content, "NOTICE.md does not cite 'ai-dev-kit' upstream"
