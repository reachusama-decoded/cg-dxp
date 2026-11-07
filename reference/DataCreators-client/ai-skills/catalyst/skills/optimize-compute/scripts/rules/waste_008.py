"""DBX-WASTE-008: SQL warehouse scale-out headroom unused."""

from __future__ import annotations

from typing import Any, Optional

from .common import (
    Finding,
    WAREHOUSE_CLUSTER_UTILIZATION_THRESHOLD,
    _bundle_file_for_warehouse,
    _safe_int,
)


def evaluate_dbx_waste_008(
    runs: dict[str, Any], dbt_config: dict[str, Any]
) -> Optional[Finding]:
    """SQL warehouse scale-out headroom unused.

    Driven by /api/2.0/sql/warehouses/{id}/events. The valid event types
    for that endpoint are STARTING / RUNNING / STOPPING / SCALED_UP /
    SCALED_DOWN; each payload carries ``details.cluster_count`` (the
    realized concurrent cluster count immediately after the event). We
    integrate ``cluster_count`` against event timestamps to compute the
    duration-weighted ``avg_cluster_count_share`` and fire when that
    falls below WAREHOUSE_CLUSTER_UTILIZATION_THRESHOLD relative to
    ``max_num_clusters``.
    """
    warehouse = runs.get("warehouse")
    if not warehouse:
        return None
    spec = warehouse.get("spec") or {}
    max_clusters = _safe_int(spec.get("max_num_clusters"))
    if max_clusters <= 1:
        return None

    events = runs.get("warehouse_events") or []
    if not events or any("_fetch_error" in (e or {}) for e in events):
        return None

    # Build a (timestamp_ms, cluster_count) timeline by reading the
    # `cluster_count` field from each event's details. The events are
    # snapshots of realized state, not deltas, so we forward-fill the
    # most recent reported cluster_count between events. SCALED_UP /
    # SCALED_DOWN events carry the new count; STARTING/RUNNING/STOPPING
    # carry the count at that lifecycle transition.
    samples: list[tuple[int, int]] = []
    for ev in events:
        ts = _safe_int(ev.get("timestamp") or ev.get("event_time_ms"))
        et = (ev.get("event_type") or "").upper()
        if et not in {"STARTING", "RUNNING", "STOPPING", "SCALED_UP", "SCALED_DOWN"}:
            continue
        details = ev.get("details") or {}
        # `cluster_count` is the canonical field; some payload shapes use
        # `num_clusters` as a synonym. Treat STOPPING as 0 if missing.
        cc = details.get("cluster_count")
        if cc is None:
            cc = details.get("num_clusters")
        if cc is None and et == "STOPPING":
            cc = 0
        if cc is None:
            continue
        samples.append((ts, _safe_int(cc)))
    if len(samples) < 2:
        return None
    samples.sort()

    # Duration-weighted average: between sample i and i+1, the realized
    # count is samples[i][1] (forward-fill).
    weighted_sum = 0.0
    total_dt = 0
    for (ts0, cc0), (ts1, _cc1) in zip(samples, samples[1:]):
        dt = max(0, ts1 - ts0)
        weighted_sum += cc0 * dt
        total_dt += dt
    avg_cluster_count = weighted_sum / total_dt if total_dt > 0 else 0.0
    utilization = avg_cluster_count / max_clusters

    if utilization >= WAREHOUSE_CLUSTER_UTILIZATION_THRESHOLD:
        return None

    proposed_max = max(2, max_clusters - 1)
    return Finding(
        rule_id="DBX-WASTE-008",
        severity="warning",
        title="SQL warehouse scale-out headroom unused",
        evidence={
            "max_clusters_configured": max_clusters,
            "avg_concurrent_clusters": round(avg_cluster_count, 3),
            "cluster_count_share": round(utilization, 3),
            "threshold": WAREHOUSE_CLUSTER_UTILIZATION_THRESHOLD,
            "events_evaluated": len(samples),
            "endpoint": "/api/2.0/sql/warehouses/{id}/events",
            "event_types_considered": [
                "STARTING",
                "RUNNING",
                "STOPPING",
                "SCALED_UP",
                "SCALED_DOWN",
            ],
        },
        remediation={
            "summary": (
                f"Lower max_num_clusters from {max_clusters} to {proposed_max}; "
                f"the duration-weighted mean concurrent cluster count over the window "
                f"was {avg_cluster_count:.2f}."
            ),
            "config_delta": {
                "max_num_clusters": {
                    "current": max_clusters,
                    "proposed": proposed_max,
                }
            },
            "affected_files": [_bundle_file_for_warehouse(runs)],
        },
        apply_mode_supported=False,  # warehouse-wide change, judgement call
        confidence="low",
    )
