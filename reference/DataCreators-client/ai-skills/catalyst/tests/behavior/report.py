# tests/behavior/report.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from tests.behavior.judge.rubric import Verdict
from tests.behavior.runner.base import RunResult


@dataclass
class CaseOutcome:
    case_id: str
    passed: bool
    reason: str
    weighted_score: Optional[float]
    duration_s: float
    input_tokens: int
    output_tokens: int
    criterion_grades: list[dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    output_text: str = ""                          # full text the runner produced
    tool_call_counts: dict[str, int] = field(default_factory=dict)  # {Bash: 5, Read: 2}
    tool_calls_summary: list[dict[str, Any]] = field(default_factory=list)
    """Per-call summary [{name, args_summary}] used to render a tool-call
    timeline in the per-case report so a reviewer can see *what* the agent
    invoked, not just how many times."""
    component_coverage: list[dict[str, Any]] = field(default_factory=list)
    """Per-expected-component verdict [{component, matched, where}] populated
    when expected_components is set on the case."""
    sub_skills: list[str] = field(default_factory=list)
    """Sub-skills the runner actually invoked, in invocation order. Used by
    the live report to show observed-vs-expected for behavior cases at a
    glance — without this the dashboard couldn't surface 'agent missed
    feasibility-report' until you opened the per-case .md."""

    def error_free(self) -> bool:
        return self.error is None


def write_markdown(path: Path, outcomes: list[CaseOutcome]) -> None:
    lines = ["# Skill behavior test report", ""]
    total = len(outcomes)
    passed = sum(1 for o in outcomes if o.passed)
    total_tokens = sum(o.input_tokens + o.output_tokens for o in outcomes)
    total_seconds = sum(o.duration_s for o in outcomes)
    lines.append(f"**Pass rate:** {passed}/{total}")
    lines.append(f"**Total tokens:** {total_tokens}")
    lines.append(f"**Total duration:** {total_seconds:.1f}s")
    lines.append("")
    lines.append("| Case | Status | Score | Tokens | Duration | Notes |")
    lines.append("|---|---|---|---|---|---|")
    for o in outcomes:
        if o.error and "cache miss" in o.error:
            status = "SKIP"
        elif o.passed:
            status = "PASS"
        else:
            status = "FAIL"
        score = f"{o.weighted_score:.2f}" if o.weighted_score is not None else "n/a"
        lines.append(
            f"| {o.case_id} | {status} | {score} | "
            f"{o.input_tokens + o.output_tokens} | {o.duration_s:.1f}s | {o.reason} |"
        )
    path.write_text("\n".join(lines) + "\n")
