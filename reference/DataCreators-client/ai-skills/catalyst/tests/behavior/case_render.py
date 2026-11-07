"""Shared rendering helpers for case-evidence sections.

Both the live-report dashboard (`live_report._render_case_doc`) and the
GitHub-issue body builder (`issues._body_pass` / `_body_fail`) need to
render the same building blocks — rubric tables, structural-check lists,
per-criterion grades. Without sharing, the two surfaces drift over time
and a reviewer cross-checking dashboard vs. filed issues sees spurious
differences.

Each helper here takes primitive shapes (lists/dicts) so callers can
adapt their domain types (Pydantic CaseSpec on the dashboard side, raw
YAML dicts on the issues side) into the shared input.
"""
from __future__ import annotations
from typing import Any, Iterable, Optional

from tests.behavior.runner.prompt_render import shorten_criterion_prompt


def render_rubric_table(
    threshold: Optional[float],
    criteria: Iterable[dict[str, Any]],
) -> str:
    """Render the rubric as a markdown table.

    `criteria` items must be dicts with keys `id`, `weight`, `prompt`.
    Long single-quoted skill descriptions in prompts are collapsed via
    the shared shortener so dashboards and issue bodies stay readable.
    """
    rows = []
    for c in criteria:
        prompt = shorten_criterion_prompt(c.get("prompt") or "")
        # Pipe characters break markdown table cells; escape them.
        prompt = prompt.replace("|", "\\|")
        rows.append(f"| `{c.get('id')}` | {c.get('weight')} | {prompt} |")
    if not rows:
        return ""
    header = "| Criterion | Weight | Question |\n|---|---|---|\n"
    threshold_line = f"**Threshold:** {threshold}\n\n" if threshold is not None else ""
    return threshold_line + header + "\n".join(rows)


def render_structural_checks(
    checks: Iterable[Any],
    *,
    expected_template: Optional[str] = None,
    expected_components: Optional[Iterable[str]] = None,
) -> str:
    """Render structural checks (plus synthetic matches_template /
    uses_components entries derived from `expected_*`) as a markdown list.

    `checks` items can be either bare names (str) or dicts/objects with
    `name` and optional `args` — handles both the YAML form (string or
    `{name: args}` dict) and the Pydantic StructuralCheck form (object
    with `.name` / `.args`).
    """
    components = list(expected_components or [])
    items = list(checks or [])
    if not items and not expected_template and not components:
        return "_(none)_"

    lines: list[str] = []
    for c in items:
        if isinstance(c, str):
            lines.append(f"- `{c}`")
        elif isinstance(c, dict):
            # YAML can represent a check as either {"name": "x", "args": {...}}
            # or as a single-item mapping {"name": args}. Handle both.
            if "name" in c:
                args = c.get("args") or {}
                lines.append(f"- `{c['name']}`" + (f" with `{args}`" if args else ""))
            else:
                (k, v), = c.items()
                lines.append(f"- `{k}`: `{v}`")
        else:
            # Pydantic StructuralCheck (or duck-equivalent)
            args = getattr(c, "args", None) or {}
            lines.append(f"- `{c.name}`" + (f" with `{args}`" if args else ""))

    if expected_template:
        lines.append(f"- `matches_template`: `{expected_template}`")
    if components:
        lines.append(f"- `uses_components`: `{components}`")
    return "\n".join(lines)


def render_grade_checklist(grades: Iterable[dict[str, Any]]) -> str:
    """Per-criterion grade lines as a checklist (✅/❌ + text + evidence).

    Empty `grades` (e.g. pre-check failed before judge ran) returns an
    italic placeholder so callers can paste this directly without
    branching.
    """
    items = list(grades or [])
    if not items:
        return "_(no grades — pre-check failed before judge ran)_"
    lines = []
    for g in items:
        mark = "✅" if g.get("passed") else "❌"
        text = (g.get("text") or "").replace("\n", " ")
        ev = (g.get("evidence") or "").replace("\n", " ")
        lines.append(f"- {mark} **{text}** — {ev}")
    return "\n".join(lines)
