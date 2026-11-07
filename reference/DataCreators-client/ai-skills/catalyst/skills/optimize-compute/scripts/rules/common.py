"""Shared constants, dataclass, and helpers for the optimize-compute rules.

Everything that more than one rule (or the top-level orchestrator) needs goes
here. Rule modules import from ``.common``; the orchestrator and gates import
from here too. This module has no rule-specific logic and no cross-imports
between rule files, which keeps the package free of circular imports.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Thresholds - MUST match references/findings-catalog.md (Worker B owns the
# authoritative version). If a threshold here disagrees with the catalog,
# leave the value here unchanged and surface the disagreement in the report.
# ---------------------------------------------------------------------------

# DBX-WASTE-001 / -002 / -003 require either >=10 runs OR >=7 calendar days
# of evidence, whichever is satisfied first. A weekly job with 10 runs is
# 10 weeks of data which is overkill; a daily job hits 7 days in 7 runs and
# still gives a usable peak/floor signal. The gate is min(10, 7d).
MIN_RUNS_REQUIRED: int = 10
MIN_DAYS_REQUIRED: int = 7

PEAK_WORKER_UTILIZATION_THRESHOLD: float = 0.6   # DBX-WASTE-001
AUTOSCALE_FLOOR_DWELL_THRESHOLD: float = 0.7     # DBX-WASTE-002
INTER_TASK_GAP_THRESHOLD: float = 0.2            # DBX-WASTE-003
WAREHOUSE_CLUSTER_UTILIZATION_THRESHOLD: float = 0.5  # DBX-WASTE-008
WAREHOUSE_QUEUE_RATIO_THRESHOLD: float = 0.1     # DBX-WASTE-009
WAREHOUSE_QUEUE_ABS_P95_MIN_MS: int = 2000       # DBX-WASTE-009 absolute gate

# DBX-WASTE-004 sub-case thresholds (from catalog).
DBT_THREADS_OVER_PROVISION_MULT: float = 1.5
DBT_THREADS_OVER_PROVISION_FLOOR: int = 8
DBT_THREADS_OVERSUBSCRIBE_MULT: int = 2
DBT_THREADS_BIG_CLUSTER_CORES: int = 16
DBT_THREADS_BIG_CLUSTER_MIN: int = 4

RUN_HISTORY_DAYS: int = 30
RUN_HISTORY_MAX_RUNS: int = 200
WAREHOUSE_QUERY_HISTORY_DAYS: int = 14

SCHEMA_VERSION = "1.0.0"

# Rules that depend on runtime evidence (run history). Skipped when the
# MIN_RUNS_REQUIRED / MIN_DAYS_REQUIRED gate fails. dbt-config-only rules
# (e.g. DBX-WASTE-010) are still evaluated.
RUNTIME_RULE_IDS: tuple[str, ...] = (
    "DBX-WASTE-001",
    "DBX-WASTE-002",
    "DBX-WASTE-003",
    "DBX-WASTE-008",
    "DBX-WASTE-009",
)

# Rules that require the dbt-config snapshot. When --dbt-config is omitted
# (warehouse-only audits), these are skipped and surfaced in
# insufficient_data.skipped_rules with the "no dbt config provided" reason.
DBT_CONFIG_RULE_IDS: tuple[str, ...] = (
    "DBX-WASTE-004",
    "DBX-WASTE-005",
    "DBX-WASTE-010",
)

# Rules that require a stable warehouse query-history sample for their
# percentile / volume math. The catalog mandates >= 200 queries over the
# 14-day window; below that, percentiles are too noisy to trust.
# WASTE-008 is intentionally NOT here: it reads /sql/warehouses/{id}/events
# (lifecycle + SCALED_UP/DOWN), not /sql/history/queries, so the query-history
# floor does not apply. A low-traffic over-provisioned warehouse is exactly
# the scenario WASTE-008 is designed to catch.
WAREHOUSE_QUERY_RULE_IDS: tuple[str, ...] = (
    "DBX-WASTE-009",
)
MIN_WAREHOUSE_QUERIES_REQUIRED: int = 200

# Apply-mode allowlist. WASTE-007 is the only rule the skill may auto-apply,
# and only when the caller opts in per-key via `--apply DBX-WASTE-007
# --config-key <specific-key>` (enforced at the apply-mode layer, not here).
# Everything else is suggestion-only because the fix is cluster-wide,
# structural, or judgment-dependent.
APPLY_MODE_ALLOWLIST: frozenset[str] = frozenset({"DBX-WASTE-007"})

# DBX-WASTE-007 watched Spark keys. Each finding emits one key. Photon
# clusters skip a subset (driver-side keys behave differently on Photon).
SPARK_WATCHED_KEYS: tuple[str, ...] = (
    "spark.sql.shuffle.partitions",
    "spark.executor.memory",
    "spark.sql.adaptive.enabled",
    "spark.sql.adaptive.coalescePartitions.enabled",
    "spark.sql.adaptive.skewJoin.enabled",
    "spark.sql.adaptive.advisoryPartitionSizeInBytes",
    "spark.driver.memory",
    "spark.driver.cores",
    "spark.driver.maxResultSize",
)
SPARK_WATCHED_KEYS_SKIP_ON_PHOTON: frozenset[str] = frozenset({
    # Photon manages executor memory itself; flagging an override here
    # frequently misfires.
    "spark.executor.memory",
    # Photon's driver shape is fixed by the runtime image; manual driver
    # tuning is usually inert.
    "spark.driver.memory",
    "spark.driver.cores",
})

# Databricks-runtime documented defaults for watched Spark keys. Per catalog
# edge case: an override that matches the documented default is noise, not
# waste -- skip emitting a finding for that key. Keys whose default depends
# on the DBR / node-type (executor memory, driver memory/cores, maxResultSize)
# are intentionally absent; those still fire on any presence, with an
# evidence note explaining the documented-default check doesn't apply.
SPARK_KEY_DEFAULTS: dict[str, Any] = {
    "spark.sql.adaptive.enabled": True,
    "spark.sql.adaptive.coalescePartitions.enabled": True,
    "spark.sql.adaptive.skewJoin.enabled": True,
    "spark.sql.shuffle.partitions": 200,
    "spark.sql.adaptive.advisoryPartitionSizeInBytes": 67_108_864,  # 64MB
}


def _normalize_spark_value(value: Any) -> Any:
    """Normalize a spark_conf value for default-comparison.

    Spark conf values come in as strings (the API serializes everything to
    text), but documented defaults are commonly published as their typed
    forms (True / 200 / 64MB). Normalize both sides to a canonical shape
    so ``"true" == True``, ``"200" == 200``, ``"64MB" == 67108864``.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int):  # bool already returned above
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else value
    if isinstance(value, str):
        s = value.strip()
        low = s.lower()
        if low in {"true", "false"}:
            return low == "true"
        # Size suffixes Databricks/Spark accept (all 1024-based):
        # k/kb/kib, m/mb/mib, g/gb/gib, t/tb/tib, case-insensitive. Spark
        # docs frequently publish defaults with the IEC form (`64MiB`), so
        # both binary-prefix and short variants must compare equal.
        m = re.match(r"^(\d+(?:\.\d+)?)\s*([kmgt])(?:i?b)?$", low)
        if m:
            mag = float(m.group(1))
            unit = m.group(2)
            mult = {"k": 1024, "m": 1024**2, "g": 1024**3, "t": 1024**4}[unit]
            return int(mag * mult)
        # Bare-bytes notation: `67108864b`.
        m = re.match(r"^(\d+)\s*b$", low)
        if m:
            return int(m.group(1))
        try:
            if "." in s:
                f = float(s)
                return int(f) if f.is_integer() else f
            return int(s)
        except ValueError:
            return s
    return value


def _spark_value_matches_default(key: str, value: Any) -> bool:
    """True when ``value`` equals the documented Databricks default for ``key``."""
    if key not in SPARK_KEY_DEFAULTS:
        return False
    return _normalize_spark_value(value) == _normalize_spark_value(
        SPARK_KEY_DEFAULTS[key]
    )

# DBX-WASTE-007 won't fire on pre-13 DBR (catalog rationale: AQE defaults
# less aggressive there).
DBR_MIN_FOR_WASTE_007: int = 13

# DBX-WASTE-010: any target not named like "dev" is "scheduled-ish".
DEV_TARGET_NAMES: frozenset[str] = frozenset({"dev", "developer", "local"})

# DBX-WASTE-004: cores-per-node lookup. Calibrated against the common AWS
# i/r/m families plus Azure DS / D / E. Used to translate the cluster's
# `node_type_id` (already in runs.json from /jobs/get's job_clusters[].
# new_cluster.node_type_id) into a cores-per-worker integer. Falls back to
# `DEFAULT_CORES_PER_WORKER` only for truly unknown types; the finding's
# evidence records `cores_assumed: true` whenever we hit the fallback so
# downstream consumers can flag the imprecision.
NODE_TYPE_CORES: dict[str, int] = {
    # AWS - storage-optimized i3 family
    "i3.xlarge": 4,
    "i3.2xlarge": 8,
    "i3.4xlarge": 16,
    "i3.8xlarge": 32,
    "i3.16xlarge": 64,
    # AWS - memory-optimized r5d family
    "r5d.xlarge": 4,
    "r5d.2xlarge": 8,
    "r5d.4xlarge": 16,
    "r5d.8xlarge": 32,
    # AWS - general-purpose m5 family
    "m5.xlarge": 4,
    "m5.2xlarge": 8,
    "m5.4xlarge": 16,
    # AWS Graviton (m7gd / i7gd)
    "m7gd.large": 2,
    "m7gd.xlarge": 4,
    "m7gd.2xlarge": 8,
    "m7gd.4xlarge": 16,
    "i7gd.large": 2,
    "i7gd.xlarge": 4,
    "i7gd.2xlarge": 8,
    "i7gd.4xlarge": 16,
    # Azure - DS v2 (legacy but still common)
    "Standard_DS3_v2": 4,
    "Standard_DS4_v2": 8,
    "Standard_DS5_v2": 16,
    # Azure - D v3 (general-purpose) / E v3 (memory-optimized)
    "Standard_D8s_v3": 8,
    "Standard_D16s_v3": 16,
    "Standard_E8s_v3": 8,
    "Standard_E16s_v3": 16,
}
DEFAULT_CORES_PER_WORKER: int = 4  # used only when node_type is truly unknown

# Severity / confidence rankings for top_findings ordering.
_SEVERITY_RANK = {"error": 0, "warning": 1, "info": 2}
_CONFIDENCE_RANK = {"high": 0, "medium": 1, "low": 2}
TOP_FINDINGS_LIMIT = 5


# ---------------------------------------------------------------------------
# Finding dataclass
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    rule_id: str
    severity: str  # info | warning | error
    title: str
    evidence: dict[str, Any]
    remediation: dict[str, Any]
    apply_mode_supported: bool
    confidence: str  # high | medium | low
    estimated_impact: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if d.get("estimated_impact") is None:
            d.pop("estimated_impact", None)
        return d


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _percentile(values: list[float], pct: float) -> float:
    """Linear-interpolation percentile, no numpy dependency."""
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * pct
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    if lo == hi:
        return s[lo]
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def _job_cluster_spec(runs: dict[str, Any]) -> dict[str, Any]:
    """Return the first job_cluster's new_cluster dict, or {}."""
    spec = (runs.get("job") or {}).get("spec") or {}
    settings = spec.get("settings") or spec
    job_clusters = settings.get("job_clusters") or []
    if not job_clusters:
        return {}
    first = job_clusters[0] or {}
    return first.get("new_cluster") or {}


def _job_cluster_path(runs: dict[str, Any], suffix: str) -> str:
    """Build the dotted config-delta path for a key inside the first job cluster."""
    return f"job_clusters[0].new_cluster.{suffix}"


def _bundle_file_for_job(runs: dict[str, Any]) -> str:
    """Resolve the bundle YAML path that declares the job.

    Prefers the collector-recorded ``job.source_path`` (the file scanned out
    of ``databricks.yml#include``). Falls back to a clearly-marked placeholder
    when the collector wasn't given ``--bundle-dir`` so the report shows
    "unknown" rather than a synthesised name that doesn't exist on disk.
    """
    job = runs.get("job") or {}
    sp = job.get("source_path")
    if isinstance(sp, str) and sp:
        return sp
    return "<bundle path unknown - re-run collector with --bundle-dir>"


def _bundle_file_for_warehouse(runs: dict[str, Any]) -> str:
    wh = runs.get("warehouse") or {}
    sp = wh.get("source_path")
    if isinstance(sp, str) and sp:
        return sp
    return "<bundle path unknown - re-run collector with --bundle-dir>"


def _dbr_major(spark_version: str | None) -> int | None:
    if not spark_version:
        return None
    m = re.match(r"^(\d+)", spark_version)
    return int(m.group(1)) if m else None


def _is_photon(spark_version: str | None) -> bool:
    return bool(spark_version) and "photon" in spark_version.lower()


def _classify_http_path(http_path: str | None) -> dict[str, Any]:
    """Light-weight resolver for the http_path string.

    Full resolver lives in dbt-config-audit.md; this version handles the two
    string shapes we can classify without an API call. Cluster-path
    classification requires a /clusters/get lookup the collector doesn't do
    today, so we return ``kind = "cluster"`` here and defer the all_purpose
    vs job_cluster decision to DBX-WASTE-010, which reads
    ``resolved_compute[cluster_id].kind`` and emits a warning when that
    kind is ``cluster_unknown``.
    """
    if not http_path:
        return {"kind": "unresolved", "id": None, "reason": "empty"}
    s = http_path.strip()
    if "{{" in s or "${" in s:
        return {"kind": "unresolved", "id": None, "reason": "templated"}
    m = re.match(r"^/sql/1\.0/warehouses/([\w-]+)$", s)
    if m:
        return {"kind": "warehouse", "id": m.group(1), "reason": None}
    m = re.match(r"^/sql/protocolv1/o/\d+/([\w-]+)$", s)
    if m:
        return {"kind": "cluster", "id": m.group(1), "reason": None}
    return {"kind": "unresolved", "id": None, "reason": "unrecognized shape"}


def _resolved_cluster_kind(dbt_config: dict[str, Any], cluster_id: str) -> str | None:
    """Look up cluster classification recorded by audit_dbt_config (if any).

    Returns the recorded ``kind`` string, or None when not resolved. The
    audit script doesn't fetch /clusters/get today, so cluster-path targets
    are typically tagged ``cluster_unknown``; higher-fidelity callers may
    override with ``all_purpose_cluster`` or ``job_cluster`` in their own
    snapshot. DBX-WASTE-010 treats only those two confirmed kinds as
    decision-quality; anything else falls into the warning branch.
    """
    rc = (dbt_config or {}).get("resolved_compute") or {}
    info = rc.get(cluster_id)
    if isinstance(info, dict):
        return info.get("kind")
    return None


def _resolved_worker_count(cluster_id: str, dbt_config: dict[str, Any]) -> int:
    """Return worker_count recorded under resolved_compute, or 0 when absent.

    Mirrors ``_resolved_cluster_kind``: callers that can't recover
    ``num_workers`` / ``max_workers`` from the job_cluster spec (e.g. an
    existing-cluster job referenced via ``resolved_compute``) can plant the
    worker count under ``resolved_compute[<cluster_id>].worker_count`` and
    have it picked up as a second source.
    """
    if not cluster_id:
        return 0
    rc = (dbt_config or {}).get("resolved_compute") or {}
    info = rc.get(cluster_id)
    if isinstance(info, dict):
        return _safe_int(info.get("worker_count"), 0)
    return 0


def _runs_span_days(runs_list: list[dict[str, Any]]) -> float:
    """Approximate calendar-day span of the run list."""
    starts = [
        s
        for s in (_safe_int(r.get("start_time"), 0) for r in runs_list)
        if s > 0
    ]
    if len(starts) < 2:
        return 0.0
    return (max(starts) - min(starts)) / (1000 * 60 * 60 * 24)


def _truncated_cluster_events(runs: dict[str, Any]) -> list[dict[str, Any]]:
    """Return per-cluster truncation entries for cluster_events_meta.

    Each entry is ``{"cluster_id": <id>, "count": int, "cap": int}`` for
    every cluster whose event window the collector reports truncated. The
    field is optional - older runs.json snapshots predate it; callers
    that get back an empty list should treat truncation as unknown
    (i.e. don't gate).
    """
    meta = runs.get("cluster_events_meta") or {}
    out: list[dict[str, Any]] = []
    if not isinstance(meta, dict):
        return out
    for cluster_id, entry in meta.items():
        if not isinstance(entry, dict):
            continue
        if not entry.get("truncated"):
            continue
        out.append(
            {
                "cluster_id": cluster_id,
                "count": _safe_int(entry.get("count"), 0),
                "cap": _safe_int(entry.get("cap"), 0),
            }
        )
    return out


def _truncated_envelope(runs: dict[str, Any], key: str) -> dict[str, Any] | None:
    """Return the truncation envelope for a top-level *_meta key when truncated.

    Returns ``{"count": int, "cap": int}`` when the envelope is present and
    has ``truncated == True``; otherwise None. Used for the singleton
    envelopes (``warehouse_events_meta``, ``warehouse_query_history_meta``).
    Tolerant of older snapshots that lack the field.
    """
    meta = runs.get(key) or {}
    if not isinstance(meta, dict) or not meta.get("truncated"):
        return None
    return {
        "count": _safe_int(meta.get("count"), 0),
        "cap": _safe_int(meta.get("cap"), 0),
    }


def _runs_sampling_meta(runs: dict[str, Any]) -> dict[str, Any]:
    """Collector-reported run-list cap/truncation metadata (if available)."""
    meta = runs.get("runs_metadata") or {}
    truncated = bool(meta.get("truncated", False))
    total_available = _safe_int(meta.get("total_available"), 0)
    cap = _safe_int(meta.get("cap"), RUN_HISTORY_MAX_RUNS)
    return {
        "runs_truncated": truncated,
        "runs_total_available": total_available,
        "runs_cap": cap,
    }


def _selected_target_cluster_id(dbt_config: dict[str, Any]) -> str | None:
    """Best-effort selected dbt cluster id from target config."""
    target_cfg = (dbt_config or {}).get("selected_target_config") or {}
    explicit = target_cfg.get("cluster_id")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    resolved = _classify_http_path(target_cfg.get("http_path"))
    if resolved.get("kind") == "cluster":
        cid = resolved.get("id")
        if isinstance(cid, str) and cid:
            return cid
    return None


def _job_existing_cluster_id(runs: dict[str, Any]) -> str | None:
    """Return job.spec existing_cluster_id when this is an existing-cluster job."""
    job = runs.get("job") or {}
    spec = job.get("spec") or {}
    settings = spec.get("settings") or {}
    cid = settings.get("existing_cluster_id") or spec.get("existing_cluster_id")
    if isinstance(cid, str) and cid:
        return cid
    return None


def _waste_004_skip_reason(runs: dict[str, Any], dbt_config: dict[str, Any]) -> str | None:
    """Return skip reason when WASTE-004 would compare against the wrong cluster.

    Also catches the no-compute-info case: a serverless job (no
    ``job_clusters``, no ``existing_cluster_id``) with neither a
    ``resolved_compute`` worker_count nor a ``cores_per_worker``
    override. Without that signal the evaluator would previously fall
    through to a 4-core default and over-fire on any ``threads >= 9``;
    we now surface the gap explicitly in ``skipped_rules`` so the user
    can wire up ``resolved_compute`` rather than seeing a silent miss.
    """
    target_cluster_id = _selected_target_cluster_id(dbt_config)
    job_existing_cluster_id = _job_existing_cluster_id(runs)

    job = runs.get("job") or {}
    spec = job.get("spec") or {}
    settings = spec.get("settings") or {}
    has_job_clusters = bool((settings.get("job_clusters") or spec.get("job_clusters") or []))

    target_cfg = (dbt_config or {}).get("selected_target_config") or {}
    threads = _safe_int(target_cfg.get("threads"), 0)
    http_path = target_cfg.get("http_path")
    resolved_http = _classify_http_path(http_path)
    # WASTE-004 only ever evaluates against cluster targets with a threads
    # setting; for warehouse / unresolved targets the rule short-circuits
    # before we'd need any compute info, so don't emit a skip reason.
    rule_in_scope = threads > 1 and resolved_http.get("kind") == "cluster"

    if rule_in_scope:
        resolved_compute = (dbt_config or {}).get("resolved_compute") or {}
        resolved_target = (
            resolved_compute.get(target_cluster_id)
            if target_cluster_id else None
        )
        override_cores = (
            _safe_int(resolved_target.get("cores_per_worker"), 0)
            if isinstance(resolved_target, dict) else 0
        )
        rc_worker_count = _resolved_worker_count(target_cluster_id, dbt_config)
        if (
            not has_job_clusters
            and not job_existing_cluster_id
            and override_cores <= 0
            and rc_worker_count <= 0
        ):
            return (
                "no compute spec available for WASTE-004: job has no "
                "job_clusters and no existing_cluster_id (serverless or "
                "compute-on-demand), and dbt_config.resolved_compute does "
                "not carry cores_per_worker / worker_count for the target. "
                "Plant resolved_compute.<cluster_id>.{cores_per_worker, "
                "worker_count} to enable the comparison."
            )

    if not target_cluster_id:
        return None

    if job_existing_cluster_id and job_existing_cluster_id != target_cluster_id:
        return (
            f"selected dbt target cluster_id={target_cluster_id} differs from "
            f"job existing_cluster_id={job_existing_cluster_id}; target cluster "
            "spec is not available in runs snapshot."
        )

    if not has_job_clusters:
        return None

    resolved_compute = (dbt_config or {}).get("resolved_compute") or {}
    resolved_target = resolved_compute.get(target_cluster_id)
    if isinstance(resolved_target, dict):
        if _safe_int(resolved_target.get("cores_per_worker"), 0) > 0:
            return None

    return (
        f"selected dbt target cluster_id={target_cluster_id} is not the job-cluster "
        "spec carried in runs snapshot; provide resolved_compute.<cluster_id>.cores_per_worker "
        "or collect target cluster spec before evaluating DBX-WASTE-004."
    )
