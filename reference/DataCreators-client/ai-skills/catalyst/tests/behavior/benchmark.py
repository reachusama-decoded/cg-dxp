"""Emit grading.json + benchmark.json in skill-creator's schemas.

Schema reference:
  ~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/
  skills/skill-creator/references/schemas.md

The skill-creator browser viewer (eval-viewer/generate_review.py) reads field
names EXACTLY. Use 'configuration' not 'config'; nest result fields under
'result'; use eval_id / eval_name / run_number verbatim.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tests.behavior.report import CaseOutcome


@dataclass
class BenchmarkRun:
    eval_id: int
    eval_name: str
    configuration: str                        # "with_skill" | "without_skill"
    run_number: int
    outcome: CaseOutcome
    criterion_grades: list[dict] = field(default_factory=list)  # {text, passed, evidence}
    tool_call_counts: dict[str, int] = field(default_factory=dict)
    transcript_chars: int = 0
    output_chars: int = 0


def _summary(grades: list[dict]) -> dict:
    passed = sum(1 for g in grades if g.get("passed"))
    total = len(grades)
    return {
        "passed": passed,
        "failed": total - passed,
        "total": total,
        "pass_rate": (passed / total) if total else 0.0,
    }


def emit_grading(run: BenchmarkRun, out_dir: Path) -> Path:
    """Write a single run's grading.json into out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "expectations": run.criterion_grades,
        "summary": _summary(run.criterion_grades),
        "execution_metrics": {
            "tool_calls": run.tool_call_counts,
            "total_tool_calls": sum(run.tool_call_counts.values()),
            "total_steps": sum(run.tool_call_counts.values()),
            "errors_encountered": 0 if run.outcome.error_free() else 1,
            "output_chars": run.output_chars,
            "transcript_chars": run.transcript_chars,
        },
        "timing": {
            "total_duration_seconds": run.outcome.duration_s,
            "executor_duration_seconds": run.outcome.duration_s,
        },
        "claims": [],
    }
    grading_path = out_dir / "grading.json"
    grading_path.write_text(json.dumps(payload, indent=2))
    return grading_path


def _stats(values: list[float]) -> dict:
    if not values:
        return {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0}
    n = len(values)
    mean = sum(values) / n
    if n > 1:
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        stddev = math.sqrt(variance)
    else:
        stddev = 0.0
    return {
        "mean": round(mean, 4),
        "stddev": round(stddev, 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
    }


def _delta_str(with_val: float, without_val: float) -> str:
    diff = with_val - without_val
    sign = "+" if diff >= 0 else ""
    return f"{sign}{round(diff, 4)}"


def emit_benchmark(
    runs: list[BenchmarkRun],
    benchmark_dir: Path,
    *,
    skill_name: str,
    executor_model: str = "claude-sonnet-4-6",
) -> Path:
    """Write aggregated benchmark.json into benchmark_dir.

    Splits runs by configuration and computes per-configuration stats plus
    a delta between with_skill and without_skill (if both are present).
    """
    benchmark_dir.mkdir(parents=True, exist_ok=True)
    by_config: dict[str, list[BenchmarkRun]] = {}
    for r in runs:
        by_config.setdefault(r.configuration, []).append(r)

    runs_per_config = max((len(v) for v in by_config.values()), default=0)
    eval_ids = sorted({r.eval_id for r in runs})

    def _run_block(r: BenchmarkRun) -> dict:
        return {
            "eval_id": r.eval_id,
            "eval_name": r.eval_name,
            "configuration": r.configuration,
            "run_number": r.run_number,
            "result": {
                "pass_rate": _summary(r.criterion_grades)["pass_rate"],
                "passed": _summary(r.criterion_grades)["passed"],
                "failed": _summary(r.criterion_grades)["failed"],
                "total": _summary(r.criterion_grades)["total"],
                "time_seconds": r.outcome.duration_s,
                "tokens": r.outcome.input_tokens + r.outcome.output_tokens,
                "tool_calls": sum(r.tool_call_counts.values()),
                "errors": 0 if r.outcome.error_free() else 1,
            },
            "expectations": r.criterion_grades,
            "notes": [],
        }

    run_summary: dict[str, Any] = {}
    for config, config_runs in by_config.items():
        run_summary[config] = {
            "pass_rate": _stats([_summary(r.criterion_grades)["pass_rate"] for r in config_runs]),
            "time_seconds": _stats([r.outcome.duration_s for r in config_runs]),
            "tokens": _stats([r.outcome.input_tokens + r.outcome.output_tokens for r in config_runs]),
        }

    if "with_skill" in run_summary and "without_skill" in run_summary:
        ws = run_summary["with_skill"]
        wos = run_summary["without_skill"]
        run_summary["delta"] = {
            "pass_rate": _delta_str(ws["pass_rate"]["mean"], wos["pass_rate"]["mean"]),
            "time_seconds": _delta_str(ws["time_seconds"]["mean"], wos["time_seconds"]["mean"]),
            "tokens": _delta_str(ws["tokens"]["mean"], wos["tokens"]["mean"]),
        }

    payload = {
        "metadata": {
            "skill_name": skill_name,
            "executor_model": executor_model,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evals_run": eval_ids,
            "runs_per_configuration": runs_per_config,
        },
        "runs": [_run_block(r) for r in runs],
        "run_summary": run_summary,
        "notes": [],
    }
    benchmark_path = benchmark_dir / "benchmark.json"
    benchmark_path.write_text(json.dumps(payload, indent=2))
    return benchmark_path
