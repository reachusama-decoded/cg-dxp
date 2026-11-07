"""Fork attribution tests.

Any skill whose SKILL.md frontmatter declares ``metadata.upstream-source``
must also carry the full attribution triplet:
  - upstream-commit  (a git SHA or tag)
  - upstream-license (a license identifier, e.g. "Apache-2.0" or "Databricks …")
  - catalyst-modifications (free-text description of changes)

…and the SKILL.md *body* must open with a "Modified from …" attribution notice
in its first 20 lines.

Skills are auto-discovered; the list is not hardcoded.  New forked skills
automatically inherit these assertions.

Offline only — no LLM calls, no network I/O.
"""
from __future__ import annotations

import pathlib
from typing import Any

import pytest
import yaml

# ---------------------------------------------------------------------------
# Repo-wide skill discovery — only skills that declare upstream-source
# ---------------------------------------------------------------------------
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_EXCLUDED = {"clients", "core", "tests"}


def _parse_frontmatter(skill_dir: pathlib.Path) -> tuple[dict[str, Any], str]:
    content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{skill_dir / 'SKILL.md'}: missing frontmatter delimiters")
    return yaml.safe_load(parts[1]) or {}, parts[2]


def _forked_skill_dirs() -> list[pathlib.Path]:
    dirs = []
    for d in (REPO_ROOT / "skills").iterdir():
        if not d.is_dir() or not (d / "SKILL.md").exists():
            continue
        if d.name in _EXCLUDED:
            continue
        try:
            fm, _ = _parse_frontmatter(d)
        except Exception:
            continue
        if fm.get("metadata", {}).get("upstream-source"):
            dirs.append(d)
    return sorted(dirs)


FORKED_SKILL_DIRS = _forked_skill_dirs()

# If no forked skills exist yet, these tests simply have no parametrize cases.

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("skill_dir", FORKED_SKILL_DIRS, ids=lambda d: d.name)
def test_upstream_source_is_url(skill_dir: pathlib.Path) -> None:
    """upstream-source should be a non-empty string (URL or repo path)."""
    fm, _ = _parse_frontmatter(skill_dir)
    source = fm.get("metadata", {}).get("upstream-source", "")
    assert source and str(source).strip(), "upstream-source is empty"


@pytest.mark.parametrize("skill_dir", FORKED_SKILL_DIRS, ids=lambda d: d.name)
def test_upstream_commit_present(skill_dir: pathlib.Path) -> None:
    """upstream-commit (git SHA or tag) must be non-empty."""
    fm, _ = _parse_frontmatter(skill_dir)
    commit = fm.get("metadata", {}).get("upstream-commit")
    assert commit and str(commit).strip(), "upstream-commit is empty or missing"


@pytest.mark.parametrize("skill_dir", FORKED_SKILL_DIRS, ids=lambda d: d.name)
def test_upstream_license_present(skill_dir: pathlib.Path) -> None:
    """upstream-license must be a non-empty string."""
    fm, _ = _parse_frontmatter(skill_dir)
    lic = fm.get("metadata", {}).get("upstream-license")
    assert lic and str(lic).strip(), "upstream-license is empty or missing"


@pytest.mark.parametrize("skill_dir", FORKED_SKILL_DIRS, ids=lambda d: d.name)
def test_catalyst_modifications_present(skill_dir: pathlib.Path) -> None:
    """catalyst-modifications must be a non-empty string."""
    fm, _ = _parse_frontmatter(skill_dir)
    mods = fm.get("metadata", {}).get("catalyst-modifications")
    assert mods and str(mods).strip(), "catalyst-modifications is empty or missing"


@pytest.mark.parametrize("skill_dir", FORKED_SKILL_DIRS, ids=lambda d: d.name)
def test_modification_notice_in_body(skill_dir: pathlib.Path) -> None:
    """First 20 lines of SKILL.md body must contain 'Modified from'."""
    _, body = _parse_frontmatter(skill_dir)
    first_20 = "\n".join(body.strip().splitlines()[:20])
    assert "Modified from" in first_20, (
        "Expected 'Modified from …' attribution notice in first 20 lines of body"
    )
