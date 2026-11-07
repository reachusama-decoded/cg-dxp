"""plugin.json ↔ skills/ bijection check.

Two directions are enforced:
  1. Every ``skills/<name>/SKILL.md`` that exists on disk must have a
     corresponding ``"skills/<name>"`` entry in ``plugin.json#skills``.
  2. Every ``"skills/<name>"`` entry in ``plugin.json#skills`` must have a
     matching directory on disk that contains a ``SKILL.md``.

Both directions are discovered dynamically, so adding a new skill or removing
an old one will automatically surface a mismatch.

Offline only — no LLM calls, no network I/O.
"""
from __future__ import annotations

import json
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Repo-wide discovery
# ---------------------------------------------------------------------------
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_EXCLUDED = {"clients", "core", "tests"}


def _disk_skills() -> set[str]:
    """Return set of 'skills/<name>' paths for skills on disk."""
    return {
        f"skills/{d.name}"
        for d in (REPO_ROOT / "skills").iterdir()
        if d.is_dir() and (d / "SKILL.md").exists() and d.name not in _EXCLUDED
    }


def _registered_skills() -> set[str]:
    """Return set of entries in plugin.json#skills."""
    plugin_json = REPO_ROOT / "plugin.json"
    if not plugin_json.is_file():
        return set()
    data = json.loads(plugin_json.read_text(encoding="utf-8"))
    return set(data.get("skills", []))


DISK_SKILLS = _disk_skills()
REGISTERED_SKILLS = _registered_skills()

# Parametrize the violation cases (empty lists → no parametrized tests, bijection is clean)
_DISK_NOT_REGISTERED = sorted(DISK_SKILLS - REGISTERED_SKILLS)
_REGISTERED_NOT_ON_DISK = sorted(REGISTERED_SKILLS - DISK_SKILLS)


# ---------------------------------------------------------------------------
# Tests — summary bijection (always runs)
# ---------------------------------------------------------------------------

def test_plugin_json_exists() -> None:
    """plugin.json must exist at the repository root."""
    assert (REPO_ROOT / "plugin.json").is_file(), "plugin.json not found at repo root"


def test_plugin_json_has_skills_key() -> None:
    """plugin.json must contain a 'skills' key with a list value."""
    data = json.loads((REPO_ROOT / "plugin.json").read_text(encoding="utf-8"))
    assert "skills" in data, "plugin.json is missing the 'skills' key"
    assert isinstance(data["skills"], list), "plugin.json#skills must be a list"


def test_all_disk_skills_registered() -> None:
    """Every on-disk SKILL.md must have an entry in plugin.json#skills."""
    missing = sorted(DISK_SKILLS - REGISTERED_SKILLS)
    assert not missing, (
        f"{len(missing)} skill(s) on disk are not in plugin.json#skills:\n"
        + "\n".join(f"  {s}" for s in missing)
    )


def test_all_registered_skills_on_disk() -> None:
    """Every plugin.json entry must correspond to a real skills/<name>/SKILL.md."""
    phantom = sorted(REGISTERED_SKILLS - DISK_SKILLS)
    assert not phantom, (
        f"{len(phantom)} plugin.json entry(ies) have no SKILL.md on disk:\n"
        + "\n".join(f"  {s}" for s in phantom)
    )


# ---------------------------------------------------------------------------
# Parametrized violation drilldowns (only populated when the suite drifts)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("skill_path", _DISK_NOT_REGISTERED, ids=lambda s: s)
def test_disk_skill_registered_in_plugin_json(skill_path: str) -> None:
    """On-disk skill must be registered in plugin.json#skills (drilldown)."""
    assert skill_path in REGISTERED_SKILLS, (
        f"{skill_path!r} exists on disk but is missing from plugin.json#skills"
    )


@pytest.mark.parametrize("skill_path", _REGISTERED_NOT_ON_DISK, ids=lambda s: s)
def test_registered_skill_exists_on_disk(skill_path: str) -> None:
    """plugin.json entry must have a SKILL.md on disk (drilldown)."""
    skill_dir = REPO_ROOT / skill_path
    assert (skill_dir / "SKILL.md").is_file(), (
        f"{skill_path!r} is in plugin.json but SKILL.md not found at {skill_dir}"
    )
