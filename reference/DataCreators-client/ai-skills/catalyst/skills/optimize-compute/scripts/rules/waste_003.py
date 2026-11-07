"""DBX-WASTE-003: high inter-task gap across runs."""

from __future__ import annotations

from typing import Any, Optional

from .common import (
    Finding,
    INTER_TASK_GAP_THRESHOLD,
    _bundle_file_for_job,
    _safe_int,
)


def evaluate_dbx_waste_003(
    runs: dict[str, Any], dbt_config: dict[str, Any]
) -> Optional[Finding]:
    """Inter-task gap - idle cluster time between tasks within a run."""
    gaps: list[float] = []
    for run in runs.get("runs", []) or []:
        tasks = sorted(
            [t for t in run.get("tasks", []) if t.get("start_time") and t.get("end_time")],
            key=lambda t: _safe_int(t.get("start_time")),
        )
        if len(tasks) < 2:
            continue
        run_duration = _safe_int(run.get("duration_ms"))
        if run_duration <= 0:
            # Fall back to wall-clock from run.start_time/end_time.
            run_duration = _safe_int(run.get("end_time")) - _safe_int(run.get("start_time"))
        if run_duration <= 0:
            continue
        idle_ms = 0
        for prev, cur in zip(tasks, tasks[1:]):
            gap = _safe_int(cur.get("start_time")) - _safe_int(prev.get("end_time"))
            if gap > 0:
                idle_ms += gap
        gaps.append(idle_ms / run_duration)
    if not gaps:
        return None
    avg_gap = sum(gaps) / len(gaps)
    # Catalog: fire only when strictly greater than the threshold. At the
    # boundary (avg_gap == 0.20), do not fire.
    if avg_gap <= INTER_TASK_GAP_THRESHOLD:
        return None

    return Finding(
        rule_id="DBX-WASTE-003",
        # Catalog says info: fix is structural (consolidate, depends_on,
        # shared job cluster) and not mechanical.
        severity="info",
        title="High inter-task gap across runs",
        evidence={
            "avg_inter_task_gap_ratio": round(avg_gap, 3),
            "threshold": INTER_TASK_GAP_THRESHOLD,
            "runs_evaluated": len(gaps),
        },
        remediation={
            "summary": (
                "Cluster is idle for a significant share of each run between "
                "tasks. Consider consolidating tasks, increasing dbt threads, "
                "or moving sequential tasks onto a shared job cluster instead "
                "of separate clusters."
            ),
            "config_delta": {},
            "affected_files": [_bundle_file_for_job(runs)],
        },
        # Structural change, judgement call.
        apply_mode_supported=False,
        confidence="medium",
    )
