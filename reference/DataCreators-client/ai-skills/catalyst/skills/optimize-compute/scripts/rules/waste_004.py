"""DBX-WASTE-004: dbt threads mismatch vs cluster cores."""

from __future__ import annotations

from typing import Any, Optional

from .common import (
    DBT_THREADS_BIG_CLUSTER_CORES,
    DBT_THREADS_BIG_CLUSTER_MIN,
    DBT_THREADS_OVER_PROVISION_FLOOR,
    DBT_THREADS_OVER_PROVISION_MULT,
    DBT_THREADS_OVERSUBSCRIBE_MULT,
    DEFAULT_CORES_PER_WORKER,
    Finding,
    NODE_TYPE_CORES,
    _classify_http_path,
    _job_cluster_spec,
    _resolved_worker_count,
    _safe_int,
    _selected_target_cluster_id,
)


def evaluate_dbx_waste_004(
    runs: dict[str, Any], dbt_config: dict[str, Any]
) -> Optional[Finding]:
    """dbt threads vs cluster cores mismatch.

    Three sub-cases per catalog (over-provisioned inside dbt,
    over-subscribing cluster, under-utilising big cluster). Triggered on
    either over- or under-provisioning. Cluster cores come from the
    /clusters/get info that the collector records under
    ``cluster_events`` (we read it back from runs.json - the collector
    keeps the cluster spec on the job spec when the cluster is a job
    cluster).
    """
    target_cfg = (dbt_config or {}).get("selected_target_config") or {}
    threads = _safe_int(target_cfg.get("threads"), 0)
    if threads <= 0:
        return None

    # Only applies to cluster targets; warehouse targets show up as
    # DBX-WASTE-009 (queueing) instead.
    http_path = target_cfg.get("http_path")
    resolved = _classify_http_path(http_path)
    if resolved.get("kind") == "warehouse":
        return None
    if resolved.get("kind") == "unresolved":
        return None  # can't compare without knowing the cluster

    # threads == 1 is usually intentional per catalog edge case.
    if threads == 1:
        return None

    # Compute cluster cores from the job-cluster spec on the snapshot. The
    # collector doesn't fetch /clusters/get for the dbt target, so this is
    # a best-effort: use the first job_cluster's node_type cores * peak
    # workers observed, falling back to the configured num_workers/max.
    cluster = _job_cluster_spec(runs)
    autoscale = cluster.get("autoscale") or {}
    # Use peak observed (only `current_num_workers` from RESIZING /
    # UPSIZE_COMPLETED, matching WASTE-001); fall back to max_workers.
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
    # worker_count resolution order: peak observed -> autoscale.max_workers ->
    # job_cluster num_workers -> resolved_compute fallback. The
    # resolved_compute fallback is the escape hatch for existing-cluster
    # jobs (no job_cluster spec on /jobs/get) where the caller plants
    # `resolved_compute[<cluster_id>].worker_count` in the dbt snapshot.
    target_cluster_id = _selected_target_cluster_id(dbt_config)
    resolved_compute = (dbt_config or {}).get("resolved_compute") or {}
    target_entry = resolved_compute.get(target_cluster_id) if target_cluster_id else None
    override_cores = _safe_int(
        (target_entry or {}).get("cores_per_worker") if isinstance(target_entry, dict) else 0,
        0,
    )
    node_type_id = cluster.get("node_type_id") or ""

    job_cluster_worker_count = peak_workers or _safe_int(
        autoscale.get("max_workers")
    ) or _safe_int(cluster.get("num_workers"), 0)
    if job_cluster_worker_count > 0:
        worker_count = job_cluster_worker_count
        worker_count_source = "job_cluster"
    else:
        rc_worker_count = _resolved_worker_count(target_cluster_id, dbt_config)
        if rc_worker_count > 0:
            worker_count = rc_worker_count
            worker_count_source = "resolved_compute"
        else:
            worker_count = 0
            worker_count_source = "override" if override_cores > 0 else "unknown"

    # Catalog promises override_cores is the escape hatch. Only skip when
    # we have neither signal at all (no worker_count AND no override_cores).
    if worker_count <= 0 and override_cores <= 0:
        return None
    if not node_type_id and override_cores <= 0:
        return None
    # No worker_count but override_cores supplied: treat as a single-node
    # equivalent so the cores comparison still runs against override_cores.
    if worker_count <= 0:
        worker_count = 1
    cores_assumed = False
    if override_cores > 0:
        cores_per_node = override_cores
        cores_source = "resolved_compute.cores_per_worker override"
    elif node_type_id in NODE_TYPE_CORES:
        cores_per_node = NODE_TYPE_CORES[node_type_id]
        cores_source = f"NODE_TYPE_CORES[{node_type_id}]"
    else:
        cores_per_node = DEFAULT_CORES_PER_WORKER
        cores_assumed = True
        cores_source = (
            f"DEFAULT_CORES_PER_WORKER ({DEFAULT_CORES_PER_WORKER}); "
            f"node_type_id={node_type_id or '<unset>'} not in catalog"
        )
    cluster_cores = max(worker_count * cores_per_node, cores_per_node)

    sub_cases: list[str] = []
    if (
        threads > _safe_int(target_cfg.get("observed_concurrent_tasks_peak"), threads)
        * DBT_THREADS_OVER_PROVISION_MULT
        and threads >= DBT_THREADS_OVER_PROVISION_FLOOR
    ):
        sub_cases.append("over_provisioned_inside_dbt")
    if threads > cluster_cores * DBT_THREADS_OVERSUBSCRIBE_MULT:
        sub_cases.append("over_subscribing_cluster")
    if (
        cluster_cores >= DBT_THREADS_BIG_CLUSTER_CORES
        and threads < DBT_THREADS_BIG_CLUSTER_MIN
    ):
        sub_cases.append("under_utilizing_big_cluster")

    if not sub_cases:
        return None

    # avg_query_cost is a workspace-level tuning hint, not per-cluster: read
    # it from the per-cluster entry first (matches the resolved_compute key
    # shape), then fall back to a top-level slot for callers that prefer to
    # set it once across all targets.
    avg_query_cost = (
        _safe_int((target_entry or {}).get("avg_query_cost") if isinstance(target_entry, dict) else 0, 0)
        or _safe_int(resolved_compute.get("avg_query_cost"), 0)
        or 2
    )
    suggested = max(
        DBT_THREADS_BIG_CLUSTER_MIN,
        min(cluster_cores * DBT_THREADS_OVERSUBSCRIBE_MULT, cluster_cores // avg_query_cost),
    )

    return Finding(
        rule_id="DBX-WASTE-004",
        severity="warning",
        title="dbt threads mismatch vs cluster cores",
        evidence={
            "threads": threads,
            "cluster_cores_estimated": cluster_cores,
            "worker_count_used": worker_count,
            "worker_count_source": worker_count_source,
            "node_type_id": node_type_id or None,
            "cores_per_worker": cores_per_node,
            "cores_assumed": cores_assumed,
            "cores_source": cores_source,
            "sub_cases": sub_cases,
            "suggested_threads": suggested,
        },
        remediation={
            "summary": (
                f"profiles.yml declares {threads} threads against an estimated "
                f"{cluster_cores}-core cluster. Sub-case(s): {', '.join(sub_cases)}. "
                f"Suggested threads: {suggested}."
            ),
            "config_delta": {
                "threads": {"current": threads, "proposed": suggested},
            },
            "affected_files": [(dbt_config or {}).get("profiles_file", "profiles.yml")],
        },
        apply_mode_supported=False,  # profiles.yml is environment-specific
        confidence="medium",
    )
