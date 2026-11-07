"""DBX-WASTE-001: peak worker utilization below threshold."""

from __future__ import annotations

import math
from typing import Any, Optional

from .common import (
    Finding,
    PEAK_WORKER_UTILIZATION_THRESHOLD,
    _bundle_file_for_job,
    _job_cluster_path,
    _job_cluster_spec,
    _runs_sampling_meta,
    _safe_int,
)


def evaluate_dbx_waste_001(
    runs: dict[str, Any], dbt_config: dict[str, Any]
) -> Optional[Finding]:
    """Peak worker utilization below PEAK_WORKER_UTILIZATION_THRESHOLD.

    Looks at autoscale.max_workers vs the max worker count observed in
    UPSIZE_COMPLETED / AUTOSCALING_STATS_REPORT events.
    """
    cluster = _job_cluster_spec(runs)
    autoscale = cluster.get("autoscale") or {}
    max_workers = _safe_int(autoscale.get("max_workers"))
    if max_workers <= 0:
        return None

    # Peak signal: only `current_num_workers` from RESIZING and
    # UPSIZE_COMPLETED events. AUTOSCALING_STATS_REPORT.details.max_workers
    # is the *configured ceiling* (echoes the cluster spec), not an
    # observation -- including it would always equal max_workers and
    # suppress the rule from firing on oversized clusters. Likewise
    # `target_num_workers` is the autoscaler's *intent* (what it would
    # like to grow to), not a realized count -- exclude that too.
    PEAK_EVENT_TYPES = {"RESIZING", "UPSIZE_COMPLETED"}
    peak_workers = 0
    for events in (runs.get("cluster_events") or {}).values():
        for ev in events or []:
            et = (ev.get("type") or ev.get("event_type") or "").upper()
            if et not in PEAK_EVENT_TYPES:
                continue
            details = ev.get("details") or {}
            v = _safe_int(details.get("current_num_workers"))
            if v > peak_workers:
                peak_workers = v

    if peak_workers <= 0:
        return None
    utilization = peak_workers / max_workers
    # Catalog comparator (findings-catalog.md line ~74):
    #   if observed_peak <= ceil(cluster.autoscale.max_workers * 0.6):
    #       fire DBX-WASTE-001
    # i.e. non-strict inequality against the ceiling of max*0.6, not a
    # ratio comparison against 0.6. The two diverge at small max_workers
    # (e.g. max=7, peak=5: ceil(0.6*7)=5, 5<=5 fires per catalog, but
    # 5/7=0.714 > 0.6 so a ratio gate would skip). Match the catalog.
    fire_threshold_workers = math.ceil(max_workers * PEAK_WORKER_UTILIZATION_THRESHOLD)
    if peak_workers > fire_threshold_workers:
        return None

    proposed = max(peak_workers + 1, _safe_int(autoscale.get("min_workers"), 1) + 1)
    return Finding(
        rule_id="DBX-WASTE-001",
        severity="warning",
        title="Peak worker utilization below threshold",
        evidence={
            "max_workers_configured": max_workers,
            "peak_workers_observed": peak_workers,
            "peak_utilization": round(utilization, 3),
            "threshold": PEAK_WORKER_UTILIZATION_THRESHOLD,
            "runs_evaluated": len(runs.get("runs", []) or []),
            **_runs_sampling_meta(runs),
        },
        remediation={
            "summary": (
                f"Lower autoscale.max_workers from {max_workers} to {proposed}; "
                f"peak workers observed across the window was {peak_workers}."
            ),
            "config_delta": {
                _job_cluster_path(runs, "autoscale.max_workers"): {
                    "current": max_workers,
                    "proposed": proposed,
                },
            },
            "affected_files": [_bundle_file_for_job(runs)],
        },
        # Cluster-wide change - judgement call, suggestion-only per catalog.
        apply_mode_supported=False,
        # Rule only fires when peak_workers > 0, so confidence is always high.
        confidence="high",
        estimated_impact=f"~{int((1 - proposed / max_workers) * 100)}% peak DBU reduction",
    )
