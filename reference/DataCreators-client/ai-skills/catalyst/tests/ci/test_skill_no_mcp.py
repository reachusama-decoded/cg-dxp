"""Repo-wide MCP-ban enforcement.

Catalyst policy prohibits MCP servers, tools, and protocols inside this repo.
Every SKILL.md body, references/*, and scripts/* is scanned for MCP patterns.

Offline only — no LLM calls, no network I/O.
"""
from __future__ import annotations

import pathlib
import re

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

# ---------------------------------------------------------------------------
# MCP pattern
# ---------------------------------------------------------------------------
_MCP_PATTERN = re.compile(
    r"mcp tool|\.mcp\.json|MCP server|use the MCP",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _skill_text(skill_dir: pathlib.Path) -> str:
    """Return SKILL.md body + references/* + scripts/* text concatenated."""
    content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    parts = content.split("---", 2)
    body = parts[2] if len(parts) >= 3 else content

    chunks = [body]
    for subdir in ("references", "scripts"):
        subpath = skill_dir / subdir
        if subpath.is_dir():
            for p in sorted(subpath.rglob("*")):
                if p.is_file() and p.suffix in {".md", ".yaml", ".yml", ".txt", ".sh", ".py"}:
                    try:
                        chunks.append(p.read_text(encoding="utf-8", errors="replace"))
                    except OSError:
                        pass
    return "\n".join(chunks)


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda d: d.name)
def test_no_mcp_in_skill(skill_dir: pathlib.Path) -> None:
    """No MCP pattern may appear in SKILL.md body, references/*, or scripts/*."""
    text = _skill_text(skill_dir)
    matches = _MCP_PATTERN.findall(text)
    assert not matches, (
        f"{skill_dir.name}: found banned MCP pattern(s): {matches!r}"
    )
