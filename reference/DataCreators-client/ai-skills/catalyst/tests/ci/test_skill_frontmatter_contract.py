"""Repo-wide SKILL.md frontmatter contract tests (RFD 0006).

Every skill directory in skills/ that contains a SKILL.md is subject to these
checks — not just a specific phase's worth.  Non-compliant pre-RFD-0006 skills
are marked xfail so failures are tracked without blocking CI.

Offline only — no LLM calls, no network I/O.
"""
from __future__ import annotations

import pathlib
from typing import Any

import pytest
import yaml

# ---------------------------------------------------------------------------
# Repo-wide skill discovery
# ---------------------------------------------------------------------------
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_EXCLUDED = {"clients", "core", "tests"}

SKILL_DIRS = sorted(
    [
        d
        for d in (REPO_ROOT / "skills").iterdir()
        if d.is_dir() and (d / "SKILL.md").exists() and d.name not in _EXCLUDED
    ]
)

# Valid tier values per RFD 0006 (all observed in the repo)
VALID_TIERS = {"orchestrator", "workflow", "capability", "document"}

# Any non-empty lifecycle-phase string is acceptable; we just enforce presence.
# Skills with metadata.tier=capability often use "none" which is fine.


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_frontmatter(skill_dir: pathlib.Path) -> tuple[dict[str, Any], str]:
    """Return (frontmatter_dict, body) for SKILL.md in *skill_dir*."""
    content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{skill_dir / 'SKILL.md'}: missing frontmatter delimiters")
    return yaml.safe_load(parts[1]) or {}, parts[2]


# Skills that pre-date RFD 0006 and are not yet fully compliant.
# Add a skill here with a comment when an xfail is introduced.
_PRE_RFD0006_NO_METADATA_TIER = {
    "catalyst-feedback",   # utility/feedback skill, predates RFD 0006 metadata block
    "dplc-validate",       # orchestrator predates RFD 0006 metadata block
}

_PRE_RFD0006_NO_ALLOWED_TOOLS = {
    "catalyst-feedback",   # predates allowed-tools field
    "consumer-aligned",    # workflow skill, allowed-tools not yet set
    "domain-aligned",      # workflow skill, allowed-tools not yet set
    "source-aligned",      # workflow skill, allowed-tools not yet set
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda d: d.name)
def test_skill_md_exists(skill_dir: pathlib.Path) -> None:
    """SKILL.md must exist (discovery guarantees this, belt-and-suspenders)."""
    assert (skill_dir / "SKILL.md").is_file()


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda d: d.name)
def test_name_matches_directory(skill_dir: pathlib.Path) -> None:
    """frontmatter.name must equal the directory name."""
    fm, _ = _parse_frontmatter(skill_dir)
    assert fm.get("name") == skill_dir.name, (
        f"frontmatter name={fm.get('name')!r} does not match directory {skill_dir.name!r}"
    )


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda d: d.name)
def test_description_non_empty(skill_dir: pathlib.Path) -> None:
    """frontmatter.description must be a non-empty string."""
    fm, _ = _parse_frontmatter(skill_dir)
    desc = fm.get("description", "")
    assert desc and str(desc).strip(), "description is empty or missing"


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda d: d.name)
def test_metadata_tier_valid(skill_dir: pathlib.Path) -> None:
    """metadata.tier must be one of the recognised tier values."""
    fm, _ = _parse_frontmatter(skill_dir)
    tier = fm.get("metadata", {}).get("tier")

    if skill_dir.name in _PRE_RFD0006_NO_METADATA_TIER:
        pytest.xfail(reason=f"{skill_dir.name} predates RFD 0006 metadata.tier enforcement")

    assert tier in VALID_TIERS, (
        f"metadata.tier={tier!r} is not one of {VALID_TIERS}"
    )


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda d: d.name)
def test_metadata_lifecycle_phase_present(skill_dir: pathlib.Path) -> None:
    """metadata.lifecycle-phase must be present (any non-None value is OK)."""
    fm, _ = _parse_frontmatter(skill_dir)
    phase = fm.get("metadata", {}).get("lifecycle-phase")

    if skill_dir.name in _PRE_RFD0006_NO_METADATA_TIER:
        pytest.xfail(reason=f"{skill_dir.name} predates RFD 0006 metadata block")

    assert phase is not None, "metadata.lifecycle-phase is missing"


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda d: d.name)
def test_allowed_tools_present_and_string(skill_dir: pathlib.Path) -> None:
    """allowed-tools must be present and a non-empty string (RFD 0006 requirement)."""
    fm, _ = _parse_frontmatter(skill_dir)
    allowed = fm.get("allowed-tools")

    if skill_dir.name in _PRE_RFD0006_NO_ALLOWED_TOOLS:
        pytest.xfail(reason=f"{skill_dir.name} predates allowed-tools enforcement")

    assert allowed is not None, "allowed-tools is missing from frontmatter"
    assert isinstance(allowed, str), f"allowed-tools should be str, got {type(allowed).__name__}"
    assert allowed.strip(), "allowed-tools is an empty string"
