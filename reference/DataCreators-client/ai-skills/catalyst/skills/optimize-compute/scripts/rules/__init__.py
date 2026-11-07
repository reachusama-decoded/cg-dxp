"""optimize-compute rules package.

Source of truth for which rules run in which order. The orchestrator
(``evaluate()``) lives here so the CLI entry can stay a thin wrapper.

Public surface (re-exported by ``evaluate_findings.py`` for backwards
compatibility):
    * ``evaluate(runs, dbt_config) -> dict``
    * ``RULES`` registry
    * ``Finding`` dataclass
    * Every ``DBX-WASTE-XYZ`` rule function
    * Schema-validation helpers
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Optional

from .common import (
    APPLY_MODE_ALLOWLIST,
    Finding,
    SCHEMA_VERSION,
    _waste_004_skip_reason,
)
from .gates import (
    _gate_cluster_events,
    _gate_dbt_config,
    _gate_runtime_rules,
    _gate_warehouse_events,
    _gate_warehouse_queries,
)
from .ranking import _impact_or_zero, _rank_top_findings
from .schema_validation import _validate_against_schema, load_schema
from .waste_001 import evaluate_dbx_waste_001
from .waste_002 import evaluate_dbx_waste_002
from .waste_003 import evaluate_dbx_waste_003
from .waste_004 import evaluate_dbx_waste_004
from .waste_005 import evaluate_dbx_waste_005
from .waste_007 import evaluate_dbx_waste_007
from .waste_008 import evaluate_dbx_waste_008
from .waste_009 import evaluate_dbx_waste_009
from .waste_010 import evaluate_dbx_waste_010


# Registry. Some rules return a list (one finding per key / per model).
RULES: list[tuple[str, Callable[[dict[str, Any], dict[str, Any]], Any]]] = [
    ("DBX-WASTE-001", evaluate_dbx_waste_001),
    ("DBX-WASTE-002", evaluate_dbx_waste_002),
    ("DBX-WASTE-003", evaluate_dbx_waste_003),
    ("DBX-WASTE-004", evaluate_dbx_waste_004),
    ("DBX-WASTE-005", evaluate_dbx_waste_005),
    ("DBX-WASTE-007", evaluate_dbx_waste_007),
    ("DBX-WASTE-008", evaluate_dbx_waste_008),
    ("DBX-WASTE-009", evaluate_dbx_waste_009),
    ("DBX-WASTE-010", evaluate_dbx_waste_010),
]


# ---------------------------------------------------------------------------
# Top-level evaluate
# ---------------------------------------------------------------------------


def _enforce_apply_allowlist(finding: Finding) -> Finding:
    """Defensive: zero out apply_mode_supported for any rule not in allowlist."""
    if finding.rule_id not in APPLY_MODE_ALLOWLIST and finding.apply_mode_supported:
        finding.apply_mode_supported = False
    return finding


def evaluate(
    runs: dict[str, Any], dbt_config: dict[str, Any]
) -> dict[str, Any]:
    findings: list[Finding] = []
    runs_observed = len(runs.get("runs", []) or [])
    insufficient = _gate_runtime_rules(runs)

    # Additional skip reasons that aren't tied to the runtime gate. Each
    # entry is {rule_id, reason}. We merge these into insufficient_data
    # below so consumers see a single list.
    extra_skips: list[dict[str, str]] = []
    extra_skips.extend(_gate_warehouse_queries(runs))
    extra_skips.extend(_gate_warehouse_events(runs))
    extra_skips.extend(_gate_cluster_events(runs))
    extra_skips.extend(_gate_dbt_config(dbt_config))
    waste_004_skip = _waste_004_skip_reason(runs, dbt_config)
    if waste_004_skip:
        extra_skips.append({"rule_id": "DBX-WASTE-004", "reason": waste_004_skip})

    runtime_skipped_ids = {
        entry["rule_id"] if isinstance(entry, dict) else entry
        for entry in (insufficient or {}).get("skipped_rules", [])
    }
    extra_skipped_ids = {e["rule_id"] for e in extra_skips}
    all_skipped_ids = runtime_skipped_ids | extra_skipped_ids

    for rule_id, fn in RULES:
        if rule_id in all_skipped_ids:
            continue
        try:
            result = fn(runs, dbt_config)
        except Exception as exc:
            # Graceful degradation: a single rule's exception shouldn't
            # blank the whole report. But surface it as `warning`, not
            # `info`, so it's visible against the noise floor of normal
            # diagnostics, and prefix the title with "evaluator bug:" so
            # it's unambiguously distinguishable from a rule that fired
            # legitimately at info severity.
            findings.append(
                Finding(
                    rule_id=rule_id,
                    severity="warning",
                    title=f"evaluator bug: rule {rule_id} raised an exception",
                    evidence={"error": f"{type(exc).__name__}: {exc}"},
                    remediation={
                        "summary": "Investigate the rule implementation or input data.",
                        "config_delta": {},
                        "affected_files": [],
                    },
                    apply_mode_supported=False,
                    confidence="low",
                )
            )
            continue
        if result is None:
            continue
        if isinstance(result, list):
            for r in result:
                findings.append(_enforce_apply_allowlist(r))
        else:
            findings.append(_enforce_apply_allowlist(result))

    target_block: dict[str, Any] = {"kind": "job", "id": "unknown"}
    if runs.get("job"):
        job = runs.get("job") or {}
        spec = job.get("spec") or {}
        name = (spec.get("settings") or {}).get("name") or spec.get("name")
        target_block = {"kind": "job", "id": str(job.get("job_id"))}
        if isinstance(name, str) and name:
            target_block["name"] = name
    elif runs.get("warehouse"):
        wh = runs.get("warehouse") or {}
        target_block = {"kind": "warehouse", "id": str(wh.get("warehouse_id"))}
        wh_name = (wh.get("spec") or {}).get("name")
        if isinstance(wh_name, str) and wh_name:
            target_block["name"] = wh_name
    # Schema-optional fields: omit when absent rather than emitting None,
    # which would fail validation against `type: string`.
    workspace_host = runs.get("workspace_host")
    if workspace_host:
        target_block["workspace_host"] = workspace_host

    findings_dicts = [f.to_dict() for f in findings]
    counts = {
        "error": sum(1 for f in findings_dicts if f["severity"] == "error"),
        "warning": sum(1 for f in findings_dicts if f["severity"] == "warning"),
        "info": sum(1 for f in findings_dicts if f["severity"] == "info"),
        "total": len(findings_dicts),
    }
    top_findings = _rank_top_findings(findings_dicts)

    # Merge runtime-gate insufficiency with extra skip reasons (warehouse
    # query-history shortfall, missing dbt config). When the runtime gate
    # didn't trip but other rules were skipped, we still emit an
    # insufficient_data block so the report surfaces the skips.
    insufficient_out = insufficient
    if extra_skips:
        if insufficient_out is None:
            insufficient_out = {
                "reason": "Some rules were skipped; see skipped_rules for per-rule reasons.",
                "skipped_rules": list(extra_skips),
            }
        else:
            insufficient_out = dict(insufficient_out)
            insufficient_out["skipped_rules"] = (
                list(insufficient_out.get("skipped_rules") or []) + list(extra_skips)
            )

    window_block: dict[str, Any] = {"runs_analyzed": runs_observed}
    win = runs.get("window") or {}
    if win.get("start") is not None:
        window_block["start"] = win["start"]
    if win.get("end") is not None:
        window_block["end"] = win["end"]

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": target_block,
        "window": window_block,
        "insufficient_data": insufficient_out,
        "counts": counts,
        "top_findings": top_findings,
        "findings": findings_dicts,
    }


__all__ = [
    "RULES",
    "SCHEMA_VERSION",
    "Finding",
    "evaluate",
    "load_schema",
    "evaluate_dbx_waste_001",
    "evaluate_dbx_waste_002",
    "evaluate_dbx_waste_003",
    "evaluate_dbx_waste_004",
    "evaluate_dbx_waste_005",
    "evaluate_dbx_waste_007",
    "evaluate_dbx_waste_008",
    "evaluate_dbx_waste_009",
    "evaluate_dbx_waste_010",
    "_validate_against_schema",
    "_gate_runtime_rules",
    "_gate_warehouse_queries",
    "_gate_warehouse_events",
    "_gate_cluster_events",
    "_gate_dbt_config",
    "_enforce_apply_allowlist",
    "_rank_top_findings",
    "_impact_or_zero",
]
