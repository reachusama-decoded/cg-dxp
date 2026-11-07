"""DBX-WASTE-002: autoscale floor dwell exceeds threshold."""

from __future__ import annotations

from typing import Any, Optional

from .common import (
    AUTOSCALE_FLOOR_DWELL_THRESHOLD,
    Finding,
    _bundle_file_for_job,
    _job_cluster_path,
    _job_cluster_spec,
    _safe_int,
)


def evaluate_dbx_waste_002(
    runs: dict[str, Any], dbt_config: dict[str, Any]
) -> Optional[Finding]:
    """Autoscale floor dwell - cluster spends most of each run at min_workers.

    Computes the duration-weighted floor-dwell ratio by integrating the
    forward-filled worker-count timeline (from RESIZING / UPSIZE_COMPLETED
    ``current_num_workers``) against event timestamps. Same shape as
    WASTE-008's cluster_count integration.

    Remediation lowers `autoscale.min_workers` to `max(1, current - 2)` per
    catalog; it does NOT delete the autoscale block (a fixed-size cluster
    is a different decision the engineer should make explicitly).
    """
    cluster = _job_cluster_spec(runs)
    autoscale = cluster.get("autoscale") or {}
    min_workers = _safe_int(autoscale.get("min_workers"))
    max_workers = _safe_int(autoscale.get("max_workers"))
    if min_workers <= 1 or max_workers <= min_workers:
        # Per catalog: skip silently when nothing to cut.
        return None

    # Build a (timestamp_ms, worker_count) sample list across all cluster
    # event streams. Only RESIZING / UPSIZE_COMPLETED carry the realized
    # current_num_workers; AUTOSCALING_STATS_REPORT.target_num_workers is
    # intent, not state (see WASTE-001 fix).
    PEAK_EVENT_TYPES = {"RESIZING", "UPSIZE_COMPLETED"}
    samples: list[tuple[int, int]] = []
    for events in (runs.get("cluster_events") or {}).values():
        for ev in events or []:
            et = (ev.get("type") or ev.get("event_type") or "").upper()
            if et not in PEAK_EVENT_TYPES:
                continue
            ts = _safe_int(ev.get("timestamp") or ev.get("event_time_ms"))
            details = ev.get("details") or {}
            wc = _safe_int(details.get("current_num_workers"), -1)
            if ts <= 0 or wc < 0:
                continue
            samples.append((ts, wc))
    if len(samples) < 2:
        return None
    samples.sort()

    # Duration-weighted floor share: between sample i and i+1 the count
    # is samples[i][1] (forward-fill). Floor seconds are the dt-share
    # where the held value equals min_workers.
    floor_dt = 0
    total_dt = 0
    for (ts0, wc0), (ts1, _wc1) in zip(samples, samples[1:]):
        dt = max(0, ts1 - ts0)
        total_dt += dt
        if wc0 == min_workers:
            floor_dt += dt
    if total_dt == 0:
        return None
    dwell = floor_dt / total_dt
    if dwell < AUTOSCALE_FLOOR_DWELL_THRESHOLD:
        return None

    proposed_min = max(1, min_workers - 2)
    # The label needs to reflect *total-time* savings, not per-floor-second:
    # the cluster only sits at the floor for `dwell` of total time, so the
    # honest total-time saving is the worker-share reduction multiplied by
    # the dwell. Without this scaling, the label overstates by up to ~30%.
    proposed_min_workers_share = 1 - proposed_min / min_workers
    dwell_weighted_saving_share = proposed_min_workers_share * dwell
    return Finding(
        rule_id="DBX-WASTE-002",
        severity="warning",
        title="Autoscale floor dwell exceeds threshold",
        evidence={
            "min_workers": min_workers,
            "max_workers": max_workers,
            "floor_dwell_ratio": round(dwell, 3),
            "proposed_min_workers_share": round(proposed_min_workers_share, 3),
            "dwell_weighted_saving_share": round(dwell_weighted_saving_share, 3),
            "threshold": AUTOSCALE_FLOOR_DWELL_THRESHOLD,
            "samples_evaluated": len(samples),
            "total_dt_ms": total_dt,
            "floor_dt_ms": floor_dt,
            "derivation": (
                "Duration-weighted: integrated current_num_workers from "
                "RESIZING / UPSIZE_COMPLETED events against event "
                "timestamps; share = sum(dt where count == min_workers) "
                "/ sum(dt total)."
            ),
        },
        remediation={
            "summary": (
                f"Cluster sits at autoscale.min_workers={min_workers} for "
                f"{round(dwell * 100, 1)}% of active time. Lower "
                f"`autoscale.min_workers` to {proposed_min} so the cluster "
                "can scale down when idle; keep the autoscale block intact "
                "so upper-tier bursts still work."
            ),
            "config_delta": {
                _job_cluster_path(runs, "autoscale.min_workers"): {
                    "current": min_workers,
                    "proposed": proposed_min,
                },
            },
            "affected_files": [_bundle_file_for_job(runs)],
        },
        # Cluster-wide change - suggestion-only.
        apply_mode_supported=False,
        confidence="medium",
        estimated_impact=(
            f"~{int(dwell_weighted_saving_share * 100)}% idle-time "
            "floor-worker reduction (dwell-weighted)"
        ),
    )
