"""DBX-WASTE-010: dbt target points at all-purpose cluster for scheduled runs."""

from __future__ import annotations

import re
from typing import Any, Optional

from .common import (
    DEV_TARGET_NAMES,
    Finding,
    _classify_http_path,
    _resolved_cluster_kind,
)


def evaluate_dbx_waste_010(
    runs: dict[str, Any], dbt_config: dict[str, Any]
) -> Optional[Finding]:
    """All-purpose cluster used for a scheduled / CI dbt target.

    Per catalog this is the canonical "error"-severity rule, BUT only when
    we can actually classify the cluster as all-purpose. The collector
    doesn't fetch ``/clusters/get`` for the dbt target's cluster, so the
    classification basis is the literal-default extraction in
    ``audit_dbt_config.extract_jinja_literal_default`` (which surfaces the
    raw http_path) plus any caller-supplied ``resolved_compute`` hints in
    the dbt snapshot. When the cluster kind is genuinely unresolvable -
    no fallback literal, no resolved_compute hint - we drop severity to
    ``warning`` and confidence to ``low`` rather than ship a
    false-positive error that fails CI for every cluster-path dbt target.
    """
    profile_targets = (dbt_config or {}).get("profile_targets") or {}
    if not profile_targets:
        return None

    # Each offender carries the resolution basis so the report can
    # distinguish "we know it's all-purpose" from "we couldn't classify
    # and defaulted conservatively".
    offenders_confirmed: list[dict[str, Any]] = []  # resolved_compute hint says all_purpose_cluster
    offenders_unconfirmed: list[dict[str, Any]] = []  # cluster path but kind unresolved
    unresolved_diagnostics: list[dict[str, Any]] = []
    for target_name, cfg in profile_targets.items():
        if not isinstance(cfg, dict):
            continue
        if isinstance(target_name, str) and target_name.lower() in DEV_TARGET_NAMES:
            continue
        http_path = cfg.get("http_path") or cfg.get("cluster_id")
        # cluster_id directly is shaped like the cluster path's tail.
        if isinstance(http_path, str) and re.match(r"^[\w-]+$", http_path) and "/" not in http_path:
            # Looks like a bare cluster_id; classify as cluster path.
            resolved = {"kind": "cluster", "id": http_path, "reason": None}
        else:
            resolved = _classify_http_path(http_path)

        if resolved["kind"] == "warehouse":
            continue
        if resolved["kind"] == "unresolved":
            unresolved_diagnostics.append(
                {"target": target_name, "http_path": http_path, "reason": resolved.get("reason")}
            )
            continue
        if resolved["kind"] == "cluster":
            cluster_id = resolved["id"]
            cluster_kind = _resolved_cluster_kind(dbt_config, cluster_id)
            if cluster_kind == "all_purpose_cluster":
                offenders_confirmed.append(
                    {
                        "target": target_name,
                        "cluster_id": cluster_id,
                        "basis": "resolved_compute hint",
                    }
                )
            elif cluster_kind == "job_cluster":
                # Caller-supplied hint says this is a job cluster; not waste.
                continue
            else:
                # No resolved_compute hint -- the collector doesn't fetch
                # /clusters/get for dbt targets today. Surface this as a
                # warning rather than a hard error so we don't break CI on
                # every cluster-path target.
                offenders_unconfirmed.append(
                    {
                        "target": target_name,
                        "cluster_id": cluster_id,
                        "basis": "cluster path but cluster_kind unresolved",
                    }
                )

    if (
        not offenders_confirmed
        and not offenders_unconfirmed
        and not unresolved_diagnostics
    ):
        return None

    if offenders_confirmed:
        return Finding(
            rule_id="DBX-WASTE-010",
            severity="error",  # the catalog's only error-severity rule
            title="dbt target points at all-purpose cluster for scheduled runs",
            evidence={
                "offending_targets": offenders_confirmed,
                "unconfirmed_targets": offenders_unconfirmed,
                "unresolved_targets": unresolved_diagnostics,
                "note": (
                    "All-purpose clusters are billed at a higher DBU rate than "
                    "job clusters for the same work. Per DBX-COMPUTE-001 / "
                    "DBX-WASTE-010, scheduled targets must point at a job "
                    "cluster or SQL warehouse."
                ),
            },
            remediation={
                "summary": (
                    "Repoint each offending target's http_path to a SQL warehouse "
                    "(`/sql/1.0/warehouses/<id>`) or a job cluster declared in "
                    "the bundle. Suggestion only - the right replacement "
                    "depends on workload shape."
                ),
                "config_delta": {},
                "affected_files": [
                    (dbt_config or {}).get("profiles_file", "profiles.yml")
                ],
            },
            apply_mode_supported=False,
            confidence="high",
        )

    if offenders_unconfirmed:
        # Cluster path detected but kind unresolvable -- ship as warning,
        # not error, with low confidence and an evidence note explaining
        # the gap.
        return Finding(
            rule_id="DBX-WASTE-010",
            severity="warning",
            title="dbt target uses cluster path; cluster kind unresolved",
            evidence={
                "unconfirmed_targets": offenders_unconfirmed,
                "unresolved_targets": unresolved_diagnostics,
                "note": (
                    "cluster_kind unresolved -- couldn't classify dbt target "
                    "without /clusters/get fetch. Provide the cluster kind via "
                    "the audit snapshot's `resolved_compute` block (keyed by "
                    "cluster_id, value `{\"kind\": \"job_cluster\" | "
                    "\"all_purpose_cluster\"}`) to upgrade this to a hard "
                    "error-severity finding when appropriate."
                ),
            },
            remediation={
                "summary": (
                    "Verify whether the cluster these targets point at is an "
                    "all-purpose or job cluster. All-purpose clusters used for "
                    "scheduled runs are DBU-expensive (DBX-COMPUTE-001 / "
                    "DBX-WASTE-010); repoint to a SQL warehouse or job cluster "
                    "if so."
                ),
                "config_delta": {},
                "affected_files": [
                    (dbt_config or {}).get("profiles_file", "profiles.yml")
                ],
            },
            apply_mode_supported=False,
            confidence="low",
        )

    # Only unresolved targets - emit info-level diagnostic per catalog edge case.
    return Finding(
        rule_id="DBX-WASTE-010",
        severity="info",
        title="dbt target http_path could not be resolved (cannot confirm)",
        evidence={
            "unresolved_targets": unresolved_diagnostics,
            "note": (
                "Could not confirm whether these targets point at an all-purpose "
                "cluster. Re-run with the env vars referenced by http_path so the "
                "resolver can classify them."
            ),
        },
        remediation={
            "summary": "Set the env vars referenced by the templated http_path and re-run.",
            "config_delta": {},
            "affected_files": [
                (dbt_config or {}).get("profiles_file", "profiles.yml")
            ],
        },
        apply_mode_supported=False,
        confidence="low",
    )
