"""Single source of truth for "what counts as invoking a sub-skill".

Two forms count as routing through a sub-skill in this harness:
  1. Explicit `Skill` tool call (Claude Code's native sub-skill mechanism).
  2. Reading `skills/<name>/SKILL.md` directly — orchestrators in this
     setup often "route" by reading the sub-skill's SKILL.md and following
     the instructions inline, because Catalyst skills aren't registered in
     Claude Code's skill registry. This is a workaround. When skills land
     in the registry, drop case (2).

Orchestrator self-invocation is the AICAT-127 / AICAT-74 anti-pattern:
the orchestrator's own SKILL.md announces the slash command and the
model interprets that as "call Skill with my own name first." The
detection helpers exclude self-invocation from the sub-skill list
(it isn't routing anywhere) AND surface a separate count so the
harness can name the anti-pattern in failure messages instead of
just reporting absence of expected sub-skills.

Used live by claude_agent.py while messages stream and again by cache.py
when re-judging old transcripts after the rule changes.
"""
from __future__ import annotations
import re
from typing import Optional

from tests.behavior.runner.base import ToolCall

_SKILL_MD_RE = re.compile(r"(?:^|/)skills/([^/]+)/SKILL\.md$")


def _skill_tool_target(tool_args: dict) -> Optional[str]:
    """Extract the bare skill name from a `Skill` tool's args.

    The Anthropic / Claude Code SDKs use different keys (`skill`, `name`,
    `command`) depending on version. Try each in order.
    """
    args = tool_args or {}
    sub = args.get("skill") or args.get("name") or args.get("command")
    return str(sub) if sub else None


def detect_sub_skill(
    tool_name: str,
    tool_args: dict,
    skill_under_test: Optional[str] = None,
) -> Optional[str]:
    """Return the sub-skill name if this tool call counts as routing, else None.

    skill_under_test: bare skill name (e.g. "dplc-design"). When provided,
    BOTH of these are excluded — they are not routing anywhere:

      - `Read(skills/<self>/SKILL.md)` — orchestrator loading its own
        instructions at startup (AICAT-122).
      - `Skill({skill: <self>})` — orchestrator self-invocation; the
        AICAT-127 / AICAT-74 anti-pattern. Use `is_self_invocation`
        (or `count_self_invocations`) to surface this separately so
        failure messages can name the cause.
    """
    args = tool_args or {}
    if tool_name == "Skill":
        sub = _skill_tool_target(args)
        if not sub:
            return None
        if skill_under_test and sub == skill_under_test:
            return None
        return sub
    if tool_name == "Read":
        m = _SKILL_MD_RE.search(str(args.get("file_path") or ""))
        if m:
            name = m.group(1)
            if skill_under_test and name == skill_under_test:
                return None
            return name
    return None


def is_self_invocation(
    tool_name: str,
    tool_args: dict,
    skill_under_test: Optional[str],
) -> bool:
    """True if this tool call is the orchestrator calling itself.

    Only the explicit `Skill({skill: <self>})` form counts here — a
    self-`Read` is the harmless "load my own instructions" pattern
    (already excluded by `detect_sub_skill`), not the delegation
    anti-pattern. Returns False when `skill_under_test` is None
    (the harness can't tell what "self" means without it).
    """
    if not skill_under_test:
        return False
    if tool_name != "Skill":
        return False
    sub = _skill_tool_target(tool_args)
    return sub == skill_under_test


def collect_sub_skills(
    tool_calls: list[ToolCall],
    skill_under_test: Optional[str] = None,
) -> list[str]:
    """Apply detect_sub_skill across every captured tool call. Used to
    re-derive sub_skills from cached transcripts under current rules."""
    out: list[str] = []
    for tc in tool_calls:
        sub = detect_sub_skill(tc.name, tc.args, skill_under_test=skill_under_test)
        if sub:
            out.append(sub)
    return out


def count_self_invocations(
    tool_calls: list[ToolCall],
    skill_under_test: Optional[str],
) -> int:
    """Count orchestrator self-invocations in a tool-call list.

    Used by the cache wrapper to re-derive `self_invocations` from a
    cached transcript when the detection rules have evolved. Returns 0
    when `skill_under_test` is None or no self-calls are found.
    """
    if not skill_under_test:
        return 0
    return sum(
        1 for tc in tool_calls
        if is_self_invocation(tc.name, tc.args, skill_under_test)
    )
