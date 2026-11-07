"""Single source of truth for "did the agent reference this component?"

Two consumers, one rule:

  judge.structural._uses_components   raises StructuralCheckFailure on miss
  dispatch._component_coverage        returns the dashboard's matched/total

Before this module they each maintained their own haystack and matching
logic. The structural check included `tool_call.result` in the haystack —
which meant a `Glob skills/**/*.py` whose result list happened to surface
the path counted as "agent invoked it." That gave us cases where the
dashboard said `0/2 ❌❌` but the structural check passed (e.g.
`fetch-confluence.case-01-happy-path` from the first full run).

The honest rule: "agent referenced X" means the agent typed X — in a
tool argument, or in its own output text. NOT in a tool result, which is
external content the agent didn't choose. Both call sites delegate here.
"""
from __future__ import annotations
from typing import Iterable, Optional, Sequence

from tests.behavior.runner.base import ToolCall


def _build_haystack(tool_calls: Optional[Sequence[ToolCall]], output_text: str) -> str:
    """Concatenate the agent's own output text + each tool call's name and
    args. Excludes tool_call.result by design — see module docstring."""
    parts: list[str] = [output_text or ""]
    for tc in tool_calls or []:
        parts.append(tc.name or "")
        try:
            parts.append(str(tc.args))
        except Exception:
            pass
    return "\n".join(parts)


def component_referenced(
    component: str,
    *,
    tool_calls: Optional[Sequence[ToolCall]] = None,
    output_text: str = "",
) -> bool:
    """True if the agent referenced this component path in its own
    output or a tool argument.

    Accepts both forward-slash form (`skills/core/discover.py`) and
    dotted-import form (`skills.core.discover`) — different tools express
    paths differently, both count.
    """
    haystack = _build_haystack(tool_calls, output_text)
    slash = component
    dotted = component.replace("/", ".").removesuffix(".py")
    return slash in haystack or dotted in haystack


def coverage(
    components: Iterable[str],
    *,
    tool_calls: Optional[Sequence[ToolCall]] = None,
    output_text: str = "",
) -> list[dict]:
    """Per-component verdict in the shape the dashboard consumes:
    `[{"component": ..., "matched": True/False}, ...]`. Order preserved
    so the table reads in declaration order."""
    haystack = _build_haystack(tool_calls, output_text)
    out: list[dict] = []
    for c in components:
        slash = c
        dotted = c.replace("/", ".").removesuffix(".py")
        out.append({
            "component": c,
            "matched": slash in haystack or dotted in haystack,
        })
    return out


def missing_components(
    components: Iterable[str],
    *,
    tool_calls: Optional[Sequence[ToolCall]] = None,
    output_text: str = "",
) -> list[str]:
    """Components NOT referenced — used by the structural check to build
    its failure message."""
    return [c for c in components
            if not component_referenced(c, tool_calls=tool_calls, output_text=output_text)]
