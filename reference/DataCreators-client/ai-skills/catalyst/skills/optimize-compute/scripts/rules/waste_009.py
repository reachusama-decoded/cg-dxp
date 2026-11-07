"""DBX-WASTE-009: SQL warehouse queueing at p95 (under-provisioned)."""

from __future__ import annotations

from typing import Any, Optional

from .common import (
    Finding,
    WAREHOUSE_QUEUE_ABS_P95_MIN_MS,
    WAREHOUSE_QUEUE_RATIO_THRESHOLD,
    _bundle_file_for_warehouse,
    _percentile,
    _safe_int,
)


def evaluate_dbx_waste_009(
    runs: dict[str, Any], dbt_config: dict[str, Any]
) -> Optional[Finding]:
    """SQL warehouse queueing - p95 queue/exec ratio > threshold.

    Per critic verdict (9): rule is queue-time *overhead*, not queue presence.
    Computes ``p95(queued_overhead_ms / max(execution_time_ms, 1000ms)) > 0.10``.
    Severity is warning. Field name is ``queued_overhead_ms``.
    """
    warehouse = runs.get("warehouse")
    if not warehouse:
        return None
    queries = runs.get("warehouse_query_history") or []
    if not queries:
        return None

    shares: list[float] = []
    abs_queue_ms: list[int] = []
    for q in queries:
        metrics = q.get("metrics") or {}
        # The fallback to (total_time_ms - execution_time_ms) is only
        # appropriate when the canonical field `queued_overhead_ms` is
        # *absent* from the metrics payload. If the field is present but
        # zero, that is a legitimate observation (the query did not queue);
        # falling back here would inflate the share with non-queue overhead
        # (planning, result-fetch, etc.) that lives between total_time and
        # execution_time and can run 50-500ms.
        if "queued_overhead_ms" in metrics:
            queued = _safe_int(metrics.get("queued_overhead_ms"), 0)
        else:
            total = _safe_int(metrics.get("total_time_ms"), 0)
            execm = _safe_int(metrics.get("execution_time_ms"), 0)
            queued = max(total - execm, 0)
        exec_ms = _safe_int(metrics.get("execution_time_ms"), 0)
        # Per catalog edge case: floor denominator at 1000ms so trivially
        # short queries don't blow up the share.
        denom = max(exec_ms, 1000)
        shares.append(queued / denom)
        abs_queue_ms.append(queued)

    if not shares:
        return None
    p95 = _percentile(shares, 0.95)
    abs_p95_queue_ms = _percentile(abs_queue_ms, 0.95)
    if (
        p95 <= WAREHOUSE_QUEUE_RATIO_THRESHOLD
        or abs_p95_queue_ms <= WAREHOUSE_QUEUE_ABS_P95_MIN_MS
    ):
        return None

    spec = warehouse.get("spec") or {}
    current_size = spec.get("cluster_size") or spec.get("size") or "Unknown"
    return Finding(
        rule_id="DBX-WASTE-009",
        # Catalog: warning, not info. Under-provisioning is also waste.
        severity="warning",
        title="SQL warehouse queueing at p95 (under-provisioned)",
        evidence={
            "p95_queue_share": round(p95, 3),
            "p95_queued_ms": int(round(abs_p95_queue_ms)),
            "threshold": WAREHOUSE_QUEUE_RATIO_THRESHOLD,
            "absolute_queue_ms_threshold": WAREHOUSE_QUEUE_ABS_P95_MIN_MS,
            "queries_sampled": len(shares),
            "current_cluster_size": current_size,
            "field": "queued_overhead_ms",  # catalog-correct name
        },
        remediation={
            "summary": (
                "Queries spend >10% of execution time queueing at p95. "
                "Raise max_num_clusters or step warehouse size up one tier."
            ),
            "config_delta": {
                "cluster_size": {
                    "current": current_size,
                    "proposed": "<one step larger - pick from Databricks sizing table>",
                }
            },
            "affected_files": [_bundle_file_for_warehouse(runs)],
        },
        apply_mode_supported=False,
        confidence="medium",
    )
