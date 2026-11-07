#!/usr/bin/env python3
"""evaluate_findings: deterministic rule engine for optimize-compute.

Takes the two snapshots produced by ``collect_run_history.py`` and
``audit_dbt_config.py`` and emits a JSON findings document matching
``templates/compute-optimization-findings.json``.

No network calls, no shell-outs - pure math over JSON in.

CLI:
    python evaluate_findings.py --runs runs.json --dbt-config dbt-config.json \\
        --output compute-optimization-findings.json

Exit codes:
    0  success, no error-severity findings
    1  one or more error-severity findings (today: only DBX-WASTE-010).
       CI workflows can gate on this.
    2  bad CLI args / missing input files / malformed JSON
    3  evaluator output failed schema validation against
       templates/compute-optimization-findings.json (indicates a bug; the
       findings file is not written)

Implementation note: the rule engine itself lives in the sibling
``rules/`` package - one file per rule, plus ``common.py`` (constants /
helpers / ``Finding`` dataclass), ``gates.py`` (pre-evaluation skip
decisions), ``ranking.py`` (top-findings ordering) and
``schema_validation.py``. This file is the CLI entry: argparse + I/O +
re-exports for backwards compatibility with callers that do
``from evaluate_findings import evaluate, RULES, ...``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

# Make `rules` importable whether this file is run as a script (`python
# evaluate_findings.py`) or imported via `sys.path.insert(0, "scripts")`
# from a test / smoke runner. In script-mode `sys.path[0]` already covers
# us; in import-mode the caller's sys.path insertion does. The explicit
# insertion below makes both code paths robust to a third invocation
# style where this module is imported by absolute path without the
# scripts/ directory on sys.path.
_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

# Re-export the full historical public surface so existing callers that do
# `from evaluate_findings import evaluate, RULES, DBT_CONFIG_RULE_IDS,
# DEV_TARGET_NAMES, _normalize_spark_value, ...` keep working unchanged.
from rules import (  # noqa: E402
    RULES,
    SCHEMA_VERSION,
    Finding,
    _enforce_apply_allowlist,
    _gate_cluster_events,
    _gate_dbt_config,
    _gate_runtime_rules,
    _gate_warehouse_events,
    _gate_warehouse_queries,
    _impact_or_zero,
    _rank_top_findings,
    _validate_against_schema,
    evaluate,
    evaluate_dbx_waste_001,
    evaluate_dbx_waste_002,
    evaluate_dbx_waste_003,
    evaluate_dbx_waste_004,
    evaluate_dbx_waste_005,
    evaluate_dbx_waste_007,
    evaluate_dbx_waste_008,
    evaluate_dbx_waste_009,
    evaluate_dbx_waste_010,
    load_schema,
)
from rules.common import (  # noqa: E402
    APPLY_MODE_ALLOWLIST,
    AUTOSCALE_FLOOR_DWELL_THRESHOLD,
    DBR_MIN_FOR_WASTE_007,
    DBT_CONFIG_RULE_IDS,
    DBT_THREADS_BIG_CLUSTER_CORES,
    DBT_THREADS_BIG_CLUSTER_MIN,
    DBT_THREADS_OVER_PROVISION_FLOOR,
    DBT_THREADS_OVER_PROVISION_MULT,
    DBT_THREADS_OVERSUBSCRIBE_MULT,
    DEFAULT_CORES_PER_WORKER,
    DEV_TARGET_NAMES,
    INTER_TASK_GAP_THRESHOLD,
    MIN_DAYS_REQUIRED,
    MIN_RUNS_REQUIRED,
    MIN_WAREHOUSE_QUERIES_REQUIRED,
    NODE_TYPE_CORES,
    PEAK_WORKER_UTILIZATION_THRESHOLD,
    RUN_HISTORY_DAYS,
    RUN_HISTORY_MAX_RUNS,
    RUNTIME_RULE_IDS,
    SPARK_KEY_DEFAULTS,
    SPARK_WATCHED_KEYS,
    SPARK_WATCHED_KEYS_SKIP_ON_PHOTON,
    TOP_FINDINGS_LIMIT,
    WAREHOUSE_CLUSTER_UTILIZATION_THRESHOLD,
    WAREHOUSE_QUERY_HISTORY_DAYS,
    WAREHOUSE_QUERY_RULE_IDS,
    WAREHOUSE_QUEUE_ABS_P95_MIN_MS,
    WAREHOUSE_QUEUE_RATIO_THRESHOLD,
    _bundle_file_for_job,
    _bundle_file_for_warehouse,
    _classify_http_path,
    _dbr_major,
    _is_photon,
    _job_cluster_path,
    _job_cluster_spec,
    _job_existing_cluster_id,
    _normalize_spark_value,
    _percentile,
    _resolved_cluster_kind,
    _resolved_worker_count,
    _runs_sampling_meta,
    _runs_span_days,
    _safe_float,
    _safe_int,
    _selected_target_cluster_id,
    _spark_value_matches_default,
    _truncated_cluster_events,
    _truncated_envelope,
    _waste_004_skip_reason,
)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="evaluate_findings",
        description=__doc__.splitlines()[0] if __doc__ else "",
    )
    p.add_argument("--runs", required=True, help="Path to runs.json from collect_run_history.py")
    p.add_argument(
        "--dbt-config",
        required=False,
        default=None,
        help=(
            "Path to dbt-config.json from audit_dbt_config.py. Optional - omit "
            "for warehouse-only audits with no dbt project. When omitted, "
            "dbt-config-sensitive rules (DBX-WASTE-004/005/010) are skipped "
            "and surfaced in insufficient_data.skipped_rules."
        ),
    )
    p.add_argument(
        "--output",
        required=True,
        help="Path to write compute-optimization-findings.json",
    )
    return p


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"failed to parse {path}: {exc}") from exc


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        runs = _load_json(Path(args.runs))
        # --dbt-config is optional. When omitted, fall back to an empty dict
        # and let the dbt-config gate emit the appropriate skipped_rules.
        if args.dbt_config:
            dbt_config = _load_json(Path(args.dbt_config))
        else:
            dbt_config = {}
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    # Guard against a silently empty / signal-less runs.json. A hand-edited
    # path that points at the wrong file, or a collection step that
    # truncated, would otherwise produce a clean-looking empty report
    # instead of a clear error. Require at least one of the two top-level
    # signal blocks the evaluator knows how to read.
    if not isinstance(runs, dict) or (
        not runs.get("job") and not runs.get("warehouse")
    ):
        print(
            "error: runs.json must contain a 'job' or 'warehouse' block "
            "(or both); got neither. Re-run collect_run_history.py.",
            file=sys.stderr,
        )
        return 2

    result = evaluate(runs, dbt_config)

    errors = _validate_against_schema(result)
    if errors:
        print(
            "error: evaluator output does not conform to "
            "templates/compute-optimization-findings.json:",
            file=sys.stderr,
        )
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 3

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(
        f"wrote {len(result['findings'])} findings to {out_path}",
        file=sys.stderr,
    )
    # Non-zero exit when any finding is error-severity so CI can gate.
    return 1 if result["counts"]["error"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
