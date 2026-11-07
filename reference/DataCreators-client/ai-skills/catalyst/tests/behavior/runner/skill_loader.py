# tests/behavior/runner/skill_loader.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import re
import yaml

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


@dataclass
class LoadedSkill:
    path: Path
    name: str
    description: str
    argument_hint: str
    allowed_tools: list[str]
    body: str  # with $ARGUMENTS already substituted
    frontmatter: dict = field(default_factory=dict)


def load_skill(path: Path, arguments: str) -> LoadedSkill:
    # If path is a directory, look for SKILL.md inside it
    if path.is_dir():
        path = path / "SKILL.md"
    text = path.read_text()
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"{path}: missing or malformed YAML frontmatter")
    fm_raw, body = m.group(1), m.group(2)
    fm = yaml.safe_load(fm_raw) or {}
    allowed_tools_raw = fm.get("allowed-tools", "")
    if isinstance(allowed_tools_raw, str):
        allowed_tools = allowed_tools_raw.split()
    else:
        allowed_tools = list(allowed_tools_raw)
    body = body.replace("$ARGUMENTS", arguments)
    return LoadedSkill(
        path=path,
        name=fm.get("name", path.stem),
        description=fm.get("description", ""),
        argument_hint=fm.get("argument-hint", ""),
        allowed_tools=allowed_tools,
        body=body,
        frontmatter=fm,
    )
