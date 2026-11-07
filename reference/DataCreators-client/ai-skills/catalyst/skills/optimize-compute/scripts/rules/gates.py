"""Gate functions: decide which rules to skip before evaluation.

Each gate inspects a slice of the input (runs / dbt_config / specific
metadata envelopes) and returns either ``None`` / ``[]`` (don't skip
anything) or an insufficient-data block / list of skip entries.

The orchestrator merges these into ``insufficient_data.skipped_rules`` so
the report can explain every rule that did not run.
"""

from __future__ import annotations

from typing import Any, Optional

from .common import (
    DBT_CONFIG_RULE_IDS,
    MIN_DAYS_REQUIRED,
    MIN_RUNS_REQUIRED,
    MIN_WAREHOUSE_QUERIES_REQUIRED,
    WAREHOUSE_QUERY_HISTORY_DAYS,
    WAREHOUSE_QUERY_RULE_IDS,
    _runs_span_days,
    _safe_int,
    _truncated_cluster_events,
    _truncated_envelope,
)


def _gate_runtime_rules(runs: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Decide whether runtime rules should be skipped.

    DISJUNCTION: this gate is OR, not AND. It returns None (i.e. allows
    runtime rules to run) when EITHER ``runs_observed >= MIN_RUNS_REQUIRED``
    OR ``span_days >= MIN_DAYS_REQUIRED``. It returns the insufficient-data
    block only when BOTH arms fail. A weekly job hits the day gate in seven
    runs; a daily job hits the run gate in ten - either is sufficient.
    """
    runs_list = runs.get("runs", []) or []
    runs_observed = len(runs_list)
    if runs.get("job") is None:
        return None  # not a job target - skip the runs gate
    # First arm of the disjunction: run-count threshold.
    if runs_observed >= MIN_RUNS_REQUIRED:
        return None
    # Second arm of the disjunction: calendar-span threshold.
    span_days = _runs_span_days(runs_list)
    if span_days >= MIN_DAYS_REQUIRED and runs_observed > 0:
        return None
    # Both arms failed; gate trips.
    reason = (
        f"Run history insufficient: {runs_observed} runs spanning "
        f"~{span_days:.1f} days. Gate: >= {MIN_RUNS_REQUIRED} runs OR "
        f">= {MIN_DAYS_REQUIRED} calendar days of runs."
    )
    # Inline import to avoid a top-level cycle through ``common`` (the
    # constant lives there too but the tuple lookup keeps this list-comp
    # self-contained).
    from .common import RUNTIME_RULE_IDS

    return {
        "reason": reason,
        "min_runs_required": MIN_RUNS_REQUIRED,
        "min_days_required": MIN_DAYS_REQUIRED,
        "runs_observed": runs_observed,
        "days_observed": round(span_days, 1),
        "skipped_rules": [
            {"rule_id": rid, "reason": reason} for rid in RUNTIME_RULE_IDS
        ],
    }


def _gate_warehouse_queries(runs: dict[str, Any]) -> list[dict[str, str]]:
    """Skip warehouse percentile rules when the query-history sample is small.

    Per the catalog, WASTE-009 needs >= 200 queries over the 14-day window
    for percentile stability. WASTE-008 is *not* gated here — it reads
    /sql/warehouses/{id}/events (lifecycle + SCALED_UP/DOWN), not query
    history, and a low-traffic warehouse is the scenario it's designed to
    catch. Returns a list of skipped-rule entries (each
    ``{"rule_id": ..., "reason": ...}``) - empty when the sample is
    sufficient or when the target isn't a warehouse.

    Also honours the collector's ``warehouse_query_history_meta`` envelope:
    when the query-history fetch was truncated at the collector cap, both
    WASTE-009 (percentile share) and WASTE-005 (per-model read counts)
    would be biased toward whichever slice of the window survived, so we
    skip both with a truncation-specific reason. Older snapshots without
    the meta envelope are not gated on truncation.
    """
    if not runs.get("warehouse"):
        return []

    trunc = _truncated_envelope(runs, "warehouse_query_history_meta")
    if trunc is not None:
        reason = (
            f"warehouse query history truncated at {trunc['cap']}; "
            "percentile and read-count signals would be biased."
        )
        # Truncation affects both the WASTE-009 percentile rule and the
        # WASTE-005 read-count diagnostic that integrates over the same
        # query window. The runtime-only WAREHOUSE_QUERY_RULE_IDS tuple
        # doesn't include WASTE-005, so add it explicitly here.
        return [
            {"rule_id": rid, "reason": reason}
            for rid in (*WAREHOUSE_QUERY_RULE_IDS, "DBX-WASTE-005")
        ]

    queries = runs.get("warehouse_query_history") or []
    if len(queries) >= MIN_WAREHOUSE_QUERIES_REQUIRED:
        return []
    reason = (
        f"warehouse query history below {MIN_WAREHOUSE_QUERIES_REQUIRED} queries "
        f"(observed {len(queries)} over the {WAREHOUSE_QUERY_HISTORY_DAYS}-day window); "
        f"percentile signals are too noisy to trust."
    )
    return [{"rule_id": rid, "reason": reason} for rid in WAREHOUSE_QUERY_RULE_IDS]


def _gate_cluster_events(runs: dict[str, Any]) -> list[dict[str, str]]:
    """Skip cluster-events-dependent rules when the events fetch was truncated.

    The collector now emits ``cluster_events_meta: {<cluster_id>:
    {"truncated": bool, "count": int, "cap": int}, ...}``. WASTE-001
    (peak workers) and WASTE-002 (autoscale floor dwell) both integrate
    across the full cluster_events window; a truncated fetch means
    either calculation starts mid-stream and silently biases the
    realized peak / floor share. When ANY cluster's events are
    truncated, skip both rules with a truncation-specific reason that
    names the cluster_id and the cap.

    The runtime-gate (``_gate_runtime_rules``) covers the orthogonal
    "not enough history at all" axis; this gate covers "history was
    capped after the fact". Older snapshots without the meta envelope
    are not gated.
    """
    truncated = _truncated_cluster_events(runs)
    if not truncated:
        return []
    skips: list[dict[str, str]] = []
    for entry in truncated:
        reason = (
            f"cluster events truncated for cluster {entry['cluster_id']} "
            f"at {entry['cap']}; peak/floor calculations would be biased."
        )
        for rid in ("DBX-WASTE-001", "DBX-WASTE-002"):
            skips.append({"rule_id": rid, "reason": reason})
    return skips


def _gate_warehouse_events(runs: dict[str, Any]) -> list[dict[str, str]]:
    """Skip WASTE-008 when serverless or when fewer than 7 days of events.

    Per catalog edge cases for DBX-WASTE-008:
    - Serverless warehouses don't expose the same scale-out semantics;
      skip with reason. The serverless signal is `enable_serverless_compute`
      (boolean) on the warehouse spec; `warehouse_type` of SERVERLESS /
      PRO_SERVERLESS is the alternate shape some workspaces carry.
    - Brand-new warehouses with <7 days of event data: skip with reason;
      a duration-weighted share over a thin window is too noisy to act on.

    Sibling to ``_gate_warehouse_queries`` so the gate names match their
    data sources (events vs query history).
    """
    if not runs.get("warehouse"):
        return []
    spec = (runs.get("warehouse") or {}).get("spec") or {}
    serverless = bool(spec.get("enable_serverless_compute"))
    wh_type = str(spec.get("warehouse_type") or "").upper()
    if serverless or wh_type in {"SERVERLESS", "PRO_SERVERLESS"}:
        reason = (
            "warehouse is serverless (enable_serverless_compute or "
            "warehouse_type indicates serverless); scale-out semantics "
            "don't apply the same way -- skip DBX-WASTE-008."
        )
        return [{"rule_id": "DBX-WASTE-008", "reason": reason}]

    # Collector-reported truncation: when the events fetch hit the cap,
    # the duration-weighted cluster_count integration starts mid-stream
    # and can't produce a representative share. Skip ahead of the
    # event-count / span / payload pre-checks so the user sees a
    # truncation-specific reason rather than a generic "not enough
    # events" one.
    trunc = _truncated_envelope(runs, "warehouse_events_meta")
    if trunc is not None:
        reason = (
            f"warehouse events truncated at {trunc['cap']}; "
            "partial timeline cannot produce a duration-weighted "
            "cluster_count share."
        )
        return [{"rule_id": "DBX-WASTE-008", "reason": reason}]

    events = runs.get("warehouse_events") or []
    ts_list = [
        _safe_int(ev.get("timestamp") or ev.get("event_time_ms"))
        for ev in events
        if isinstance(ev, dict) and "_fetch_error" not in ev
    ]
    ts_list = [t for t in ts_list if t > 0]
    if len(ts_list) < 2:
        reason = (
            f"warehouse has {len(ts_list)} usable event timestamp(s); "
            "DBX-WASTE-008 requires >= 2 events spanning >= 7 days to "
            "compute a duration-weighted share."
        )
        return [{"rule_id": "DBX-WASTE-008", "reason": reason}]
    span_ms = max(ts_list) - min(ts_list)
    if span_ms < 7 * 86_400_000:
        reason = (
            f"warehouse events span only {span_ms / 86_400_000:.1f} "
            "days; DBX-WASTE-008 requires >= 7 days of event data."
        )
        return [{"rule_id": "DBX-WASTE-008", "reason": reason}]

    # Pre-pass: even with enough events spanning >= 7 days, the rule can't
    # compute a duration-weighted share unless the payloads actually carry
    # `cluster_count` (or its synonym `num_clusters`). Without this check
    # the rule silently returns None and the user sees no finding AND no
    # skip reason. Count events with a usable numeric payload and skip
    # explicitly when fewer than two are present.
    usable_payload = 0
    for ev in events:
        if not isinstance(ev, dict) or "_fetch_error" in ev:
            continue
        details = ev.get("details") or {}
        cc = details.get("cluster_count")
        if cc is None:
            cc = details.get("num_clusters")
        if isinstance(cc, (int, float)) and not isinstance(cc, bool):
            usable_payload += 1
    if usable_payload < 2:
        reason = (
            "warehouse events lack usable cluster_count payload; "
            "DBX-WASTE-008 needs >= 2 events with cluster_count to "
            "compute a duration-weighted share."
        )
        return [{"rule_id": "DBX-WASTE-008", "reason": reason}]
    return []


def _gate_dbt_config(dbt_config: dict[str, Any]) -> list[dict[str, str]]:
    """Skip dbt-config-sensitive rules when no dbt config was supplied.

    Empty / None dbt_config maps to "warehouse-only audit" - the dbt rules
    can't fire, and we surface that explicitly in skipped_rules so the
    report can explain the gap.
    """
    if dbt_config:
        return []
    reason = "no dbt config provided (warehouse-only audit)"
    return [{"rule_id": rid, "reason": reason} for rid in DBT_CONFIG_RULE_IDS]
