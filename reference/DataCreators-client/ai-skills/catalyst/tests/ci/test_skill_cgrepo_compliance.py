"""Repo-wide cgrepo (Nexus) install compliance.

Capital Group's corporate network blocks public PyPI.  Any skill that contains
a ``pip install`` (or ``%pip install`` / ``uv pip install``) command in a
*code block* must either:
  - include ``--index-url`` on the same line, OR
  - have ``cgrepo`` appear within ±10 lines of the install command.

Prose-only mentions (outside fenced code blocks) are informational and exempt.

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
# Patterns
# ---------------------------------------------------------------------------
_FENCED_BLOCK_RE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
_PIP_INSTALL_RE = re.compile(r"(?:(?:uv\s+)?pip|%pip)\s+install\b", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _collect_text(skill_dir: pathlib.Path) -> str:
    """Return SKILL.md body + references/* text concatenated."""
    content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    parts = content.split("---", 2)
    body = parts[2] if len(parts) >= 3 else content

    chunks = [body]
    refs_dir = skill_dir / "references"
    if refs_dir.is_dir():
        for p in sorted(refs_dir.rglob("*")):
            if p.is_file():
                try:
                    chunks.append(p.read_text(encoding="utf-8", errors="replace"))
                except OSError:
                    pass
    return "\n".join(chunks)


def _unguarded_pip_installs(text: str) -> list[str]:
    """Return pip install lines in code blocks that lack cgrepo routing."""
    problems: list[str] = []
    for block in _FENCED_BLOCK_RE.findall(text):
        lines = block.splitlines()
        for i, line in enumerate(lines):
            if not _PIP_INSTALL_RE.search(line):
                continue
            # Already guarded on the same line?
            if "--index-url" in line or "cgrepo" in line:
                continue
            # Scan ±10-line window within the block
            window_start = max(0, i - 10)
            window_end = min(len(lines), i + 11)
            window = "\n".join(lines[window_start:window_end])
            if "cgrepo" in window:
                continue
            problems.append(line.strip())
    return problems


def _explicit_pypi_url(text: str) -> list[str]:
    """Return pip install lines that reference pypi.org directly."""
    return re.findall(
        r"pip\s+install[^\n]*https?://pypi\.org[^\n]*",
        text,
        re.IGNORECASE,
    )


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda d: d.name)
def test_no_bare_pypi_org_url(skill_dir: pathlib.Path) -> None:
    """pip install commands must not reference pypi.org directly."""
    text = _collect_text(skill_dir)
    bad = _explicit_pypi_url(text)
    assert not bad, (
        f"{skill_dir.name}: pip install pointing at pypi.org: {bad!r}"
    )


@pytest.mark.parametrize("skill_dir", SKILL_DIRS, ids=lambda d: d.name)
def test_pip_installs_guarded_by_cgrepo(skill_dir: pathlib.Path) -> None:
    """pip install in code blocks must use --index-url or have cgrepo nearby."""
    text = _collect_text(skill_dir)
    problems = _unguarded_pip_installs(text)
    assert not problems, (
        f"{skill_dir.name}: unguarded pip install(s) in code block: {problems!r}"
    )
