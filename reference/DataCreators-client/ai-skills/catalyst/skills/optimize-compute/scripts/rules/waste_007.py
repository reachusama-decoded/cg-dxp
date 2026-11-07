"""DBX-WASTE-007: stale Spark configs (one finding per flagged key)."""

from __future__ import annotations

from typing import Any

from .common import (
    DBR_MIN_FOR_WASTE_007,
    Finding,
    SPARK_KEY_DEFAULTS,
    SPARK_WATCHED_KEYS,
    SPARK_WATCHED_KEYS_SKIP_ON_PHOTON,
    _bundle_file_for_job,
    _dbr_major,
    _is_photon,
    _job_cluster_path,
    _job_cluster_spec,
    _spark_value_matches_default,
)


def evaluate_dbx_waste_007(
    runs: dict[str, Any], dbt_config: dict[str, Any]
) -> list[Finding]:
    """Stale Spark configs - one finding per flagged key.

    Per critic verdict (2): implemented but NOT auto-applicable by default.
    The apply-mode layer must enforce `--apply DBX-WASTE-007 --config-key
    <specific-key>` for any write; this evaluator emits one finding per key
    with apply_mode_supported=False. The apply layer flips that bit only
    when the caller explicitly opts in for that one key.
    """
    cluster = _job_cluster_spec(runs)
    spark_conf = cluster.get("spark_conf") or {}
    spark_version = cluster.get("spark_version")
    dbr = _dbr_major(spark_version)
    if dbr is None or dbr < DBR_MIN_FOR_WASTE_007:
        return []

    photon = _is_photon(spark_version)
    custom_tags = cluster.get("custom_tags") or {}
    if isinstance(custom_tags, dict):
        if custom_tags.get("spark-tuned") in ("true", "True", True):
            return []
        for k in custom_tags.keys():
            if isinstance(k, str) and k.startswith("optimize-compute-ignore-"):
                return []

    findings: list[Finding] = []
    for key in SPARK_WATCHED_KEYS:
        if key not in spark_conf:
            continue
        if photon and key in SPARK_WATCHED_KEYS_SKIP_ON_PHOTON:
            continue
        current = spark_conf.get(key)
        # Catalog edge case: an override that matches Databricks' documented
        # default is noise (not waste); skip emitting a finding for that key.
        # Only applies to keys with a stable cross-DBR default; for keys
        # whose default depends on DBR/node-type we still flag on presence
        # and record that in evidence.
        if _spark_value_matches_default(key, current):
            continue
        has_documented_default = key in SPARK_KEY_DEFAULTS
        evidence: dict[str, Any] = {
            "key": key,
            "current_value": current,
            "observed_value": current,
            "spark_version": spark_version,
            "dbr_major": dbr,
            "photon": photon,
        }
        if has_documented_default:
            evidence["documented_default"] = SPARK_KEY_DEFAULTS[key]
        else:
            evidence["documented_default"] = None
            evidence["documented_default_note"] = (
                "default depends on DBR / node-type; firing on presence."
            )
        findings.append(
            Finding(
                rule_id="DBX-WASTE-007",
                severity="warning",
                title=f"Stale Spark config override: {key}",
                evidence=evidence,
                remediation={
                    "summary": (
                        f"Remove `spark_conf.{key}` from the cluster spec; DBR {dbr}+ "
                        "AQE / runtime defaults handle this case without the override."
                    ),
                    "config_delta": {
                        _job_cluster_path(runs, f"spark_conf.{key}"): {
                            "current": current,
                            "proposed": None,
                            # Structured deletion signal: downstream consumers
                            # should remove the key rather than write `: None`.
                            "delete": True,
                        },
                    },
                    "affected_files": [_bundle_file_for_job(runs)],
                },
                # Apply mode requires explicit per-key opt-in; the engine
                # reports apply_mode_supported=False here. The apply CLI
                # flips this on for exactly one key when invoked as
                # `--apply DBX-WASTE-007 --config-key <key>`.
                apply_mode_supported=False,
                confidence="high",
            )
        )
    return findings
