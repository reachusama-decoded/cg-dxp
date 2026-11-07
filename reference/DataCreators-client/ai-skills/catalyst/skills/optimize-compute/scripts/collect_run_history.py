#!/usr/bin/env python3
"""collect_run_history: Databricks run-history collector for optimize-compute.

Pure data collector. Calls the Databricks read APIs documented in the
optimize-compute architect brief and emits a normalized JSON document that
the evaluator (``evaluate_findings.py``) reads. No rule logic lives here.

Endpoints called:
    GET  /api/2.1/jobs/get
    GET  /api/2.1/jobs/runs/list           (RUN_HISTORY_DAYS window, capped at RUN_HISTORY_MAX_RUNS)
    GET  /api/2.1/jobs/runs/get             (escalation only - when normalize_run
                                              cannot find a required field on the
                                              list payload)
    POST /api/2.0/clusters/events           (RESIZING / UPSIZE_COMPLETED / AUTOSCALING_STATS_REPORT)
    GET  /api/2.0/sql/warehouses/{id}       (when --warehouse-id is set)
    POST /api/2.0/sql/warehouses/{id}/events (for DBX-WASTE-008 cluster_count timeline)
    GET  /api/2.0/sql/history/queries       (WAREHOUSE_QUERY_HISTORY_DAYS window)

Also (when a Databricks Asset Bundle root is supplied via --bundle-dir):
    Scans ``databricks.yml`` for ``include:`` globs, walks the matching
    resource YAML files, and records the actual on-disk path of the file
    that declares each job/warehouse. This path lands in the snapshot as
    ``job.source_path`` / ``warehouse.source_path`` so apply mode edits the
    real bundle file rather than synthesising a name from a display string.

Auth follows the pattern set by ``connect-databricks``: it prefers the
vendored ``databricks_tools_core.client.DatabricksClient`` (which honours
``DATABRICKS_HOST`` / OAuth M2M / PAT in order). If that client cannot be
imported, the script falls back to raw ``requests`` calls using
``DATABRICKS_HOST`` + ``DATABRICKS_TOKEN``.

CLI:
    python collect_run_history.py --job-id 1234 [--warehouse-id 5678] [--bundle-dir .] --output runs.json
    python collect_run_history.py --warehouse-id 5678 --output runs.json

Exit codes:
    0  success
    2  bad CLI args / missing required env
    3  Databricks API error (HTTP non-2xx or auth failure)
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
from typing import Any, Iterable

try:
    import yaml  # PyYAML - optional; only needed for --bundle-dir scanning
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Repo-root bootstrap so `from skills.core...` resolves when this script is
# invoked as `python scripts/collect_run_history.py` from a bundle root that
# is not itself the repo root. Walk up from this file looking for a parent
# that contains a `skills/` directory; if found, prepend it to sys.path.
# ---------------------------------------------------------------------------
for _candidate in Path(__file__).resolve().parents:
    if (_candidate / "skills").is_dir():
        candidate_str = str(_candidate)
        if candidate_str not in sys.path:
            sys.path.insert(0, candidate_str)
        break

from skills.core.databricks_raw_client import (  # noqa: E402
    AuthNotConfigured as _SharedAuthNotConfigured,
    RETRY_AFTER_MAX_SECONDS as _SHARED_RETRY_AFTER_MAX_SECONDS,
    RETRY_BACKOFF_SECONDS as _SHARED_RETRY_BACKOFF_SECONDS,
    RETRY_MAX_ATTEMPTS as _SHARED_RETRY_MAX_ATTEMPTS,
    RawRequestsClient as _SharedRawRequestsClient,
    should_retry_databricks as _shared_should_retry_databricks,
)

# ---------------------------------------------------------------------------
# Constants - must match references/findings-catalog.md and run-history-signals.md
# ---------------------------------------------------------------------------

RUN_HISTORY_DAYS: int = 30
RUN_HISTORY_MAX_RUNS: int = 200
WAREHOUSE_QUERY_HISTORY_DAYS: int = 14

# Pagination caps. The Databricks /clusters/events endpoint returns a
# `next_page` token; we cap total events per cluster to bound both the
# API spend and the size of the snapshot the evaluator has to process.
# 2000 events per cluster covers >30 days of typical autoscale chatter
# for daily-frequency jobs (Worker B's calibration in
# `references/run-history-signals.md`).
CLUSTER_EVENTS_MAX_PER_CLUSTER: int = 2000
# Warehouse events cap. The /sql/warehouses/{id}/events endpoint returns
# lifecycle and scale events; the volume per warehouse is much lower than
# /clusters/events (a few scale events per day, not per minute), so 2000
# events covers >30 days of typical activity with margin.
WAREHOUSE_EVENTS_MAX: int = 2000
# /sql/history/queries cap: MIN(2000, 14d * estimated_qps). We use a
# flat 2000 here -- estimated_qps requires telemetry we don't have at
# collect time, and 2000 queries over 14 days is ~6 qps sustained,
# generous for the EDO warehouses Catalyst tracks.
WAREHOUSE_QUERY_HISTORY_MAX: int = 2000

RELEVANT_CLUSTER_EVENT_TYPES: tuple[str, ...] = (
    "RESIZING",
    "UPSIZE_COMPLETED",
    "AUTOSCALING_STATS_REPORT",
)

# Warehouse events we care about for DBX-WASTE-008. The catalog points at
# /api/2.0/sql/warehouses/{id}/events for the cluster_count timeline; the
# valid event types for that endpoint are STARTING / RUNNING / STOPPING and
# the scale events SCALED_UP / SCALED_DOWN, each of which carries a
# `cluster_count` field in `details`. CLUSTER_CREATED / CLUSTER_TERMINATED
# are NOT valid event types here (they belong to /api/2.0/clusters/events,
# the all-purpose/job cluster endpoint). The evaluator integrates the
# cluster_count deltas implied by SCALED_UP / SCALED_DOWN against the event
# timestamps to compute the duration-weighted avg_cluster_count_share.
RELEVANT_WAREHOUSE_EVENT_TYPES: tuple[str, ...] = (
    "STARTING",
    "RUNNING",
    "STOPPING",
    "SCALED_UP",
    "SCALED_DOWN",
)

# ---------------------------------------------------------------------------
# Databricks API client (vendored if available, else raw requests)
# ---------------------------------------------------------------------------
#
# The 429 retry policy, the raw-requests fallback client, and the auth
# exception class all live in skills/core/databricks_raw_client.py so other
# Databricks-touching skills can reuse them. The names below are kept as
# module-local aliases (underscored) for backward compatibility with any
# external caller that previously imported them from this module.


# Retry policy for 429 Too Many Requests. Exponential backoff capped per
# attempt; honors a Retry-After header when present (either delta-seconds
# or HTTP-date per RFC 7231 §7.1.3).
_RETRY_MAX_ATTEMPTS: int = _SHARED_RETRY_MAX_ATTEMPTS
_RETRY_BACKOFF_SECONDS: tuple[float, ...] = _SHARED_RETRY_BACKOFF_SECONDS
_RETRY_AFTER_MAX_SECONDS: float = _SHARED_RETRY_AFTER_MAX_SECONDS

# Backward-compat alias for the retry predicate.
_should_retry = _shared_should_retry_databricks

# Backward-compat alias for the raw-requests fallback client.
_RawRequestsClient = _SharedRawRequestsClient


def _build_client() -> Any:
    """Return an object exposing ``get`` and ``post`` for the Databricks REST API."""
    try:
        from skills.clients.databricks_tools_core.client import (
            DatabricksClient,  # type: ignore[import-not-found]
        )

        try:
            return DatabricksClient()
        except ValueError as exc:
            # The vendored Databricks SDK raises ValueError during
            # construction when its default-auth chain can't resolve
            # credentials. Translate to _AuthNotConfigured so the CLI
            # surfaces an actionable hint; any other ValueError shape
            # propagates as-is.
            msg = str(exc).lower()
            if any(marker.lower() in msg for marker in _VENDORED_AUTH_ERROR_MARKERS):
                raise _AuthNotConfigured(_AUTH_HINT) from exc
            raise
    except (ImportError, ModuleNotFoundError):
        # Vendored client isn't on sys.path in this install -- expected
        # fallback path, not a failure.
        pass

    host = os.environ.get("DATABRICKS_HOST", "")
    token = os.environ.get("DATABRICKS_TOKEN", "")
    return _RawRequestsClient(host, token)


# Backward-compat alias for the auth exception class.
_AuthNotConfigured = _SharedAuthNotConfigured


_AUTH_HINT = (
    "Databricks auth not configured. Run /connect-databricks first, "
    "or set DATABRICKS_HOST + DATABRICKS_TOKEN."
)


_VENDORED_AUTH_ERROR_MARKERS: tuple[str, ...] = (
    "default auth",
    "cannot configure default credentials",
    "default credentials",
    "no auth configured",
    "DATABRICKS_HOST",
    "DATABRICKS_TOKEN",
)


def _auth_preflight(client: Any) -> None:
    """Cheap probe to confirm the client has working credentials.

    Calls ``GET /api/2.0/preview/scim/v2/Me`` (or the vendored client's
    idiomatic equivalent). Translates missing-env, 401/403 outcomes,
    and the vendored SDK's "default auth: cannot configure default
    credentials" path into ``_AuthNotConfigured`` so the CLI can emit
    an actionable hint; other errors propagate so the normal API-error
    handling kicks in.
    """
    if not os.environ.get("DATABRICKS_HOST") and not getattr(client, "host", None):
        raise _AuthNotConfigured(_AUTH_HINT)
    try:
        client.get("/api/2.0/preview/scim/v2/Me")
    except _AuthNotConfigured:
        raise
    except Exception as exc:
        status = getattr(getattr(exc, "response", None), "status_code", None)
        if status in (401, 403):
            raise _AuthNotConfigured(_AUTH_HINT) from exc
        # Vendored Databricks SDK auth resolution failure: the SDK raises
        # a generic error (no HTTP response) when default auth chain
        # can't find credentials. Detect by message-text markers since the
        # SDK doesn't expose a stable exception type for this case.
        msg = str(exc).lower()
        if any(marker.lower() in msg for marker in _VENDORED_AUTH_ERROR_MARKERS):
            raise _AuthNotConfigured(_AUTH_HINT) from exc
        raise


# ---------------------------------------------------------------------------
# Collection helpers
# ---------------------------------------------------------------------------


@dataclass
class CollectionContext:
    client: Any
    window_start: datetime
    window_end: datetime


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def fetch_job_spec(ctx: CollectionContext, job_id: int) -> dict[str, Any]:
    """GET /api/2.1/jobs/get."""
    return ctx.client.get("/api/2.1/jobs/get", params={"job_id": job_id})


def fetch_runs_list(
    ctx: CollectionContext, job_id: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """GET /api/2.1/jobs/runs/list, paginated, capped at RUN_HISTORY_MAX_RUNS.

    Uses ``expand_tasks=true`` so we get task-level start/end times on the
    list response. We do NOT then call /runs/get per run (the previous
    implementation's N+1 pattern); the list payload already carries the
    fields the evaluator needs. ``fetch_run_detail`` only runs when
    ``normalize_run`` reports a missing field for a specific run.
    """
    runs: list[dict[str, Any]] = []
    page_token: str | None = None
    total_available: int | None = None
    start_ms = _ms(ctx.window_start)
    end_ms = _ms(ctx.window_end)

    while len(runs) < RUN_HISTORY_MAX_RUNS:
        params: dict[str, Any] = {
            "job_id": job_id,
            "expand_tasks": "true",
            "start_time_from": start_ms,
            "start_time_to": end_ms,
            "limit": min(25, RUN_HISTORY_MAX_RUNS - len(runs)),
        }
        if page_token:
            params["page_token"] = page_token
        resp = ctx.client.get("/api/2.1/jobs/runs/list", params=params)
        raw_total = resp.get("total_count")
        if isinstance(raw_total, int):
            total_available = raw_total
        page_runs = resp.get("runs", []) or []
        runs.extend(page_runs)
        page_token = resp.get("next_page_token")
        if not page_token or not page_runs:
            break

    visible_runs = runs[:RUN_HISTORY_MAX_RUNS]
    truncated = bool(page_token) or (
        isinstance(total_available, int) and total_available > RUN_HISTORY_MAX_RUNS
    )
    if total_available is None:
        # Lower bound when the API doesn't return total_count.
        total_available = len(visible_runs)
        if truncated:
            total_available += 1

    return visible_runs, {
        "truncated": truncated,
        "total_available": total_available,
        "cap": RUN_HISTORY_MAX_RUNS,
    }


def fetch_run_detail(ctx: CollectionContext, run_id: int) -> dict[str, Any]:
    """GET /api/2.1/jobs/runs/get - escalation only.

    The list response with ``expand_tasks=true`` carries the fields the
    evaluator needs. This call is reserved for the rare case where a
    specific run's payload is missing a required field on the list response
    (e.g. older API versions, partial responses). Callers should pass
    ``reason`` for diagnostic traceability.
    """
    detail = ctx.client.get(
        "/api/2.1/jobs/runs/get",
        params={"run_id": run_id, "include_history": "true"},
    )
    return detail


_RUN_REQUIRED_FIELDS = ("run_id", "start_time", "end_time")


def normalize_run(run: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    """Strip a run record to the fields the evaluator needs.

    Returns ``(normalized, missing_field)``. ``missing_field`` is non-None
    when one of ``_RUN_REQUIRED_FIELDS`` is absent, signalling to the caller
    that a /runs/get escalation is worthwhile for this single run.
    """
    cluster_instance = run.get("cluster_instance") or {}
    tasks = []
    for task in run.get("tasks", []) or []:
        tasks.append(
            {
                "task_key": task.get("task_key"),
                "state": (task.get("state") or {}).get("life_cycle_state"),
                "result_state": (task.get("state") or {}).get("result_state"),
                "start_time": task.get("start_time"),
                "end_time": task.get("end_time"),
                "execution_duration_ms": task.get("execution_duration"),
                "setup_duration_ms": task.get("setup_duration"),
                "cleanup_duration_ms": task.get("cleanup_duration"),
                "cluster_instance_id": (task.get("cluster_instance") or {}).get(
                    "cluster_id"
                ),
            }
        )
    normalized = {
        "run_id": run.get("run_id"),
        "state": (run.get("state") or {}).get("life_cycle_state"),
        "result_state": (run.get("state") or {}).get("result_state"),
        "start_time": run.get("start_time"),
        "end_time": run.get("end_time"),
        "duration_ms": run.get("execution_duration"),
        "setup_duration_ms": run.get("setup_duration"),
        "cleanup_duration_ms": run.get("cleanup_duration"),
        "cluster_instance_id": cluster_instance.get("cluster_id"),
        "tasks": tasks,
    }
    missing = next(
        (k for k in _RUN_REQUIRED_FIELDS if normalized.get(k) in (None, 0)),
        None,
    )
    # end_time == 0 for in-flight runs is legitimate (we filter those later);
    # don't escalate for that case.
    if missing == "end_time" and normalized.get("state") == "RUNNING":
        missing = None
    return normalized, missing


def fetch_cluster_events(
    ctx: CollectionContext, cluster_id: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """POST /api/2.0/clusters/events, paginated, filtered to relevant event types.

    /clusters/events is a POST endpoint that takes a JSON body and returns
    a ``next_page`` token when more events are available. We paginate
    forward and cap total events per cluster at
    ``CLUSTER_EVENTS_MAX_PER_CLUSTER`` to bound API spend. Each page
    requests up to 500 events; pagination tokens are passed in the body
    on subsequent requests per the Databricks API contract.

    Returns ``(events, meta)`` where meta is ``{"truncated", "count", "cap"}``.
    Truncation matters here because the endpoint returns events in DESC
    order; if we hit the cap, we have dropped the OLDEST events, which
    breaks DBX-WASTE-008's duration-weighted integration unless the
    evaluator knows to mark the result partial.
    """
    events: list[dict[str, Any]] = []
    next_page: dict[str, Any] | None = None
    base_body: dict[str, Any] = {
        "cluster_id": cluster_id,
        "event_types": list(RELEVANT_CLUSTER_EVENT_TYPES),
        "start_time": _ms(ctx.window_start),
        "end_time": _ms(ctx.window_end),
        "order": "DESC",
        "limit": 500,
    }
    while len(events) < CLUSTER_EVENTS_MAX_PER_CLUSTER:
        body = dict(base_body)
        if next_page:
            # The Databricks API echoes the pagination context back as a
            # `next_page` object that the caller forwards verbatim.
            body["next_page"] = next_page
        resp = ctx.client.post("/api/2.0/clusters/events", json=body)
        page_events = resp.get("events", []) or []
        if not page_events:
            break
        events.extend(page_events)
        next_page = resp.get("next_page")
        if not next_page:
            break
    truncated = bool(next_page) or len(events) > CLUSTER_EVENTS_MAX_PER_CLUSTER
    visible = events[:CLUSTER_EVENTS_MAX_PER_CLUSTER]
    meta = {
        "truncated": truncated,
        "count": len(visible),
        "cap": CLUSTER_EVENTS_MAX_PER_CLUSTER,
    }
    return visible, meta


def fetch_warehouse_spec(ctx: CollectionContext, warehouse_id: str) -> dict[str, Any]:
    return ctx.client.get(f"/api/2.0/sql/warehouses/{warehouse_id}")


def fetch_warehouse_events(
    ctx: CollectionContext, warehouse_id: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """POST /api/2.0/sql/warehouses/{id}/events for cluster_count timeline.

    Drives DBX-WASTE-008 (scale-out sub-case). Filters to the warehouse
    lifecycle event types (STARTING / RUNNING / STOPPING) plus the scale
    deltas (SCALED_UP / SCALED_DOWN). Each event payload includes
    `details.cluster_count`, which the evaluator integrates against the
    event timestamps to derive a duration-weighted concurrent cluster
    count.

    Paginates via ``next_page_token`` -- matching the other warehouse
    cursored endpoints -- and caps total events at ``WAREHOUSE_EVENTS_MAX``.
    Returns ``(events, meta)`` where meta is ``{"truncated", "count", "cap"}``.
    On API failure (e.g. workspaces that 404 this endpoint), returns the
    single ``_fetch_error`` sentinel event with ``truncated=False``.
    """
    base_body: dict[str, Any] = {
        "warehouse_id": warehouse_id,
        "event_types": list(RELEVANT_WAREHOUSE_EVENT_TYPES),
        "start_time": _ms(ctx.window_start),
        "end_time": _ms(ctx.window_end),
        "limit": 1000,
    }
    events: list[dict[str, Any]] = []
    page_token: str | None = None
    try:
        while len(events) < WAREHOUSE_EVENTS_MAX:
            body = dict(base_body)
            if page_token:
                body["page_token"] = page_token
            resp = ctx.client.post(
                f"/api/2.0/sql/warehouses/{warehouse_id}/events", json=body
            )
            page_events = resp.get("events", []) or []
            if not page_events:
                break
            events.extend(page_events)
            page_token = resp.get("next_page_token")
            if not page_token:
                break
    except Exception as exc:  # pragma: no cover - best-effort; some workspaces 404 this
        err_events = [{"_fetch_error": f"{type(exc).__name__}: {exc}"}]
        return err_events, {
            "truncated": False,
            "count": len(err_events),
            "cap": WAREHOUSE_EVENTS_MAX,
        }
    truncated = bool(page_token) or len(events) > WAREHOUSE_EVENTS_MAX
    visible = events[:WAREHOUSE_EVENTS_MAX]
    meta = {
        "truncated": truncated,
        "count": len(visible),
        "cap": WAREHOUSE_EVENTS_MAX,
    }
    return visible, meta


# PII redaction for SQL text persisted in the snapshot.
#
# Trust boundary: the snapshot JSON is written to the user's repo (on disk,
# checked into source control by some users). /sql/history/queries can return
# raw user query text that embeds customer identifiers (e.g. WHERE clauses
# with account numbers), date filters, or other PII as string/numeric
# literals. We redact at the source -- before the query dict is appended to
# the returned list -- so the on-disk artifact never carries the raw text.
#
# Constraint: the evaluator's `_query_mentions_model` walks the redacted
# text looking for fully-qualified table names (schema.table). Therefore the
# redaction must preserve SQL *structure* and *identifiers*: keywords,
# operators, dotted FQNs, and quoted identifiers like "schema"."table" must
# survive intact. Only literal values (string and numeric literals) are
# replaced with placeholders.

# Match single-quoted string literals (with doubled '' as an escape).
_SQL_SINGLE_QUOTED_RE = re.compile(r"'(?:''|[^'])*'")
# Match double-quoted content that contains whitespace. This deliberately
# leaves quoted identifiers like "my_table" intact (no whitespace), so the
# default-mode interpretation as a string literal is only triggered when the
# token can't be an identifier. Matches the existing evaluator heuristic.
_SQL_DOUBLE_QUOTED_STRING_RE = re.compile(r'"[^"]*\s[^"]*"')
# Bare numeric literals. Word-boundary anchored so we don't gobble digits
# inside identifiers like `t1` or `col_2024`.
_SQL_NUMERIC_LITERAL_RE = re.compile(r"\b\d+(?:\.\d+)?\b")


def _redact_query_text(text: str) -> str:
    """Replace literal values in SQL text with placeholders.

    Preserves: keywords, operators, identifiers (including schema-qualified
    FQNs like ``analytics.fct_orders`` and ``"a"."b"``), comments.

    Redacts:
        - ``'foo'`` (single-quoted string literal) -> ``'<str>'``
        - ``"foo bar"`` (double-quoted, whitespace inside -> treated as
          string literal per default ANSI mode heuristic) -> ``"<str>"``
        - ``42`` / ``3.14`` (bare numeric literals) -> ``<num>``
    """
    if not isinstance(text, str) or not text:
        return text
    redacted = _SQL_SINGLE_QUOTED_RE.sub("'<str>'", text)
    redacted = _SQL_DOUBLE_QUOTED_STRING_RE.sub('"<str>"', redacted)
    redacted = _SQL_NUMERIC_LITERAL_RE.sub("<num>", redacted)
    return redacted


def fetch_warehouse_query_history(
    ctx: CollectionContext, warehouse_id: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """GET /api/2.0/sql/history/queries, paginated, for the 14d window.

    Paginates via the ``next_page_token`` returned alongside ``res``. Caps
    total queries at ``WAREHOUSE_QUERY_HISTORY_MAX`` to bound API spend
    and snapshot size (see the constant's docstring for the qps math).

    Returns ``(queries, meta)`` where meta is ``{"truncated", "count", "cap"}``.
    ``query_text`` (and ``statement`` if present) are redacted via
    ``_redact_query_text`` BEFORE the query dict is added to the result so the
    on-disk snapshot never carries raw user SQL literals.
    """
    window_start_ms = _ms(_now_utc() - timedelta(days=WAREHOUSE_QUERY_HISTORY_DAYS))
    window_end_ms = _ms(_now_utc())
    queries: list[dict[str, Any]] = []
    page_token: str | None = None
    truncated = False
    while len(queries) < WAREHOUSE_QUERY_HISTORY_MAX:
        params: dict[str, Any] = {
            "filter_by.warehouse_ids": warehouse_id,
            "filter_by.query_start_time_range.start_time_ms": window_start_ms,
            "filter_by.query_start_time_range.end_time_ms": window_end_ms,
            "max_results": 1000,
        }
        if page_token:
            params["page_token"] = page_token
        resp = ctx.client.get("/api/2.0/sql/history/queries", params=params)
        page_queries = resp.get("res", []) or []
        if not page_queries:
            break
        # Redact PII at the source before persisting -- see
        # `_redact_query_text` for the trust-boundary rationale.
        for q in page_queries:
            if not isinstance(q, dict):
                continue
            if isinstance(q.get("query_text"), str):
                q["query_text"] = _redact_query_text(q["query_text"])
            if isinstance(q.get("statement"), str):
                q["statement"] = _redact_query_text(q["statement"])
        queries.extend(page_queries)
        page_token = resp.get("next_page_token")
        if not page_token:
            break
    if len(queries) >= WAREHOUSE_QUERY_HISTORY_MAX and page_token:
        truncated = True
    visible = queries[:WAREHOUSE_QUERY_HISTORY_MAX]
    if len(queries) > WAREHOUSE_QUERY_HISTORY_MAX:
        truncated = True
    meta = {
        "truncated": truncated,
        "count": len(visible),
        "cap": WAREHOUSE_QUERY_HISTORY_MAX,
    }
    return visible, meta


# ---------------------------------------------------------------------------
# Databricks Asset Bundle source-path resolver
# ---------------------------------------------------------------------------


def _load_yaml_safe(path: Path) -> Any:
    if yaml is None:
        return None
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _bundle_include_globs(bundle_dir: Path) -> list[str]:
    root_path = bundle_dir / "databricks.yml"
    if not root_path.exists():
        return []
    doc = _load_yaml_safe(root_path) or {}
    raw = doc.get("include") or []
    if not isinstance(raw, list):
        return []
    return [g for g in raw if isinstance(g, str)]


def resolve_bundle_source_paths(
    bundle_dir: Path,
) -> dict[str, dict[str, str]]:
    """Walk databricks.yml include globs and index job/warehouse declarations.

    Returns ``{"jobs": {job_key_or_name: relpath}, "warehouses": {key: relpath}}``.
    Indexed by both the bundle resource key and by display name so the
    evaluator can match either way without requiring the caller to know
    which one the API surfaces.
    """
    out: dict[str, dict[str, str]] = {"jobs": {}, "warehouses": {}}
    if yaml is None or not bundle_dir.is_dir():
        return out

    for pattern in _bundle_include_globs(bundle_dir):
        # Globs in databricks.yml are relative to the bundle root.
        for match in glob.glob(str(bundle_dir / pattern), recursive=True):
            file_path = Path(match)
            if not file_path.is_file():
                continue
            doc = _load_yaml_safe(file_path)
            if not isinstance(doc, dict):
                continue
            resources = doc.get("resources") or {}
            if not isinstance(resources, dict):
                continue
            rel = str(file_path.relative_to(bundle_dir))

            jobs = resources.get("jobs") or {}
            if isinstance(jobs, dict):
                for key, body in jobs.items():
                    out["jobs"][key] = rel
                    if isinstance(body, dict):
                        name = body.get("name")
                        if isinstance(name, str) and name:
                            out["jobs"][name] = rel

            warehouses = resources.get("sql_warehouses") or resources.get("warehouses") or {}
            if isinstance(warehouses, dict):
                for key, body in warehouses.items():
                    out["warehouses"][key] = rel
                    if isinstance(body, dict):
                        name = body.get("name")
                        if isinstance(name, str) and name:
                            out["warehouses"][name] = rel
    return out


def _match_source_path(
    index: dict[str, str], *candidates: Any
) -> str | None:
    for c in candidates:
        if isinstance(c, str) and c and c in index:
            return index[c]
    return None


# ---------------------------------------------------------------------------
# Top-level collect
# ---------------------------------------------------------------------------


def collect(
    job_id: int | None,
    warehouse_id: str | None,
    bundle_dir: Path | None = None,
) -> dict[str, Any]:
    """Drive the full collection. Returns the normalized JSON document."""
    if job_id is None and warehouse_id is None:
        raise ValueError("Either --job-id or --warehouse-id must be supplied")

    end = _now_utc()
    start = end - timedelta(days=RUN_HISTORY_DAYS)
    try:
        client = _build_client()
    except RuntimeError as exc:
        # _RawRequestsClient raises RuntimeError when DATABRICKS_HOST /
        # DATABRICKS_TOKEN are absent; surface the actionable hint.
        raise _AuthNotConfigured(_AUTH_HINT) from exc
    _auth_preflight(client)
    ctx = CollectionContext(client=client, window_start=start, window_end=end)
    bundle_index = (
        resolve_bundle_source_paths(bundle_dir) if bundle_dir is not None else {"jobs": {}, "warehouses": {}}
    )

    # Capture the workspace host the client is bound to so the evaluator can
    # populate target.workspace_host. Prefer the client's .host attribute
    # (set on both the vendored DatabricksClient and the raw-requests
    # fallback); fall back to the DATABRICKS_HOST env var. Returns an
    # empty string if neither is available -- the evaluator drops the key
    # entirely when this is falsy.
    workspace_host = getattr(client, "host", None) or os.environ.get(
        "DATABRICKS_HOST", ""
    )
    workspace_host = (workspace_host or "").rstrip("/") or None

    snapshot: dict[str, Any] = {
        "schema_version": "1.0.0",
        "collected_at": end.isoformat(),
        "window": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "days": RUN_HISTORY_DAYS,
        },
        "bundle_dir": str(bundle_dir) if bundle_dir else None,
        "workspace_host": workspace_host,
        "job": None,
        "runs": [],
        "cluster_events": {},
        "cluster_events_meta": {},
        "warehouse": None,
        "warehouse_events": [],
        "warehouse_events_meta": {},
        "warehouse_query_history": [],
        "warehouse_query_history_meta": {},
    }

    if job_id is not None:
        job_spec = fetch_job_spec(ctx, job_id)
        settings = (job_spec.get("settings") or job_spec) or {}
        job_source_path = _match_source_path(
            bundle_index["jobs"],
            settings.get("name"),
            str(job_id),
        )
        snapshot["job"] = {
            "job_id": job_id,
            "spec": job_spec,
            "source_path": job_source_path,
        }

        raw_runs, runs_meta = fetch_runs_list(ctx, job_id)
        snapshot["runs_metadata"] = runs_meta
        normalized: list[dict[str, Any]] = []
        seen_cluster_ids: set[str] = set()
        escalation_notes: list[dict[str, Any]] = []
        for raw in raw_runs:
            run_id = raw.get("run_id")
            if run_id is None:
                continue
            norm, missing = normalize_run(raw)
            # Escalate ONLY for the specific run that lacks a required field,
            # not for every run. The list response already has expand_tasks.
            if missing:
                try:
                    detail = fetch_run_detail(ctx, run_id)
                    norm, _ = normalize_run(detail)
                    escalation_notes.append(
                        {"run_id": run_id, "missing": missing, "outcome": "recovered"}
                    )
                except Exception as exc:  # pragma: no cover - best-effort
                    escalation_notes.append(
                        {
                            "run_id": run_id,
                            "missing": missing,
                            "outcome": f"failed: {type(exc).__name__}",
                        }
                    )
            normalized.append(norm)
            cid = norm.get("cluster_instance_id")
            if cid:
                seen_cluster_ids.add(cid)
            for task in norm["tasks"]:
                tcid = task.get("cluster_instance_id")
                if tcid:
                    seen_cluster_ids.add(tcid)
        snapshot["runs"] = normalized
        if escalation_notes:
            snapshot["_run_detail_escalations"] = escalation_notes

        cluster_events: dict[str, list[dict[str, Any]]] = {}
        cluster_events_meta: dict[str, dict[str, Any]] = {}
        for cid in seen_cluster_ids:
            try:
                ev, meta = fetch_cluster_events(ctx, cid)
                cluster_events[cid] = ev
                cluster_events_meta[cid] = meta
            except Exception as exc:  # pragma: no cover - best-effort
                cluster_events[cid] = [
                    {"_fetch_error": f"{type(exc).__name__}: {exc}"}
                ]
                cluster_events_meta[cid] = {
                    "truncated": False,
                    "count": 1,
                    "cap": CLUSTER_EVENTS_MAX_PER_CLUSTER,
                }
        snapshot["cluster_events"] = cluster_events
        snapshot["cluster_events_meta"] = cluster_events_meta

    if warehouse_id is not None:
        wh_spec = fetch_warehouse_spec(ctx, warehouse_id)
        wh_source_path = _match_source_path(
            bundle_index["warehouses"],
            wh_spec.get("name"),
            warehouse_id,
        )
        snapshot["warehouse"] = {
            "warehouse_id": warehouse_id,
            "spec": wh_spec,
            "source_path": wh_source_path,
        }
        wh_events, wh_events_meta = fetch_warehouse_events(ctx, warehouse_id)
        snapshot["warehouse_events"] = wh_events
        snapshot["warehouse_events_meta"] = wh_events_meta
        wh_queries, wh_queries_meta = fetch_warehouse_query_history(
            ctx, warehouse_id
        )
        snapshot["warehouse_query_history"] = wh_queries
        snapshot["warehouse_query_history_meta"] = wh_queries_meta

    return snapshot


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="collect_run_history",
        description=__doc__.splitlines()[0] if __doc__ else "",
    )
    p.add_argument("--job-id", type=int, default=None, help="Databricks job ID to collect")
    p.add_argument(
        "--warehouse-id",
        type=str,
        default=None,
        help="Databricks SQL warehouse ID to collect",
    )
    p.add_argument(
        "--bundle-dir",
        type=str,
        default=None,
        help=(
            "Path to the Databricks Asset Bundle root (contains databricks.yml). "
            "When supplied, the collector scans include: globs to record the "
            "actual bundle file path for each job/warehouse so apply mode can "
            "edit the real file."
        ),
    )
    p.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to write the normalized JSON snapshot",
    )
    return p


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_parser().parse_args(list(argv) if argv is not None else None)
    if args.job_id is None and args.warehouse_id is None:
        print(
            "error: at least one of --job-id or --warehouse-id is required",
            file=sys.stderr,
        )
        return 2

    bundle_dir = Path(args.bundle_dir).expanduser().resolve() if args.bundle_dir else None
    if bundle_dir is not None and not bundle_dir.is_dir():
        print(f"error: --bundle-dir not found: {bundle_dir}", file=sys.stderr)
        return 2

    try:
        snapshot = collect(
            job_id=args.job_id,
            warehouse_id=args.warehouse_id,
            bundle_dir=bundle_dir,
        )
    except _AuthNotConfigured as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(
            f"error: Databricks API call failed: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 3

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True))
    print(
        f"wrote {len(snapshot.get('runs', []))} runs to {out_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
