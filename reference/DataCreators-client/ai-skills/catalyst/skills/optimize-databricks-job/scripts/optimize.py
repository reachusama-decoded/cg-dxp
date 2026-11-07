#!/usr/bin/env python3
"""Optimize a Databricks Asset Bundle for performance (capability skill).

Scans a rendered DAB tree's `resources/*.yml` for DBX-PERF-* findings
and optionally applies safe defaults. Binds DBX-PERF-* (with light
overlap with DBX-BUNDLE-*).

Exit codes:
    0  report or successful apply
    2  input error (no databricks.yml at bundle path)
    5  apply failure (at least one apply-able finding could not be written)
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
_OPTIMIZE_LIB = REPO_ROOT / "skills" / "_lib" / "optimize.py"


def _load_optimize_lib():
    spec = importlib.util.spec_from_file_location(
        "catalyst_lib_optimize", _OPTIMIZE_LIB
    )
    assert spec and spec.loader, f"could not load optimize lib at {_OPTIMIZE_LIB}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_lib = _load_optimize_lib()
Finding = _lib.Finding


def _dbr_major(spark_version: str) -> int | None:
    m = re.match(r"^(\d+)\.", spark_version or "")
    return int(m.group(1)) if m else None


def _job_anchor(job_name: str, raw_text: str) -> tuple[str, str] | None:
    """Find the indented `name: <job_name>` line and return (line, indent)."""
    m = re.search(
        rf"^([ \t]+)name:\s*{re.escape(job_name)}\s*$",
        raw_text,
        flags=re.MULTILINE,
    )
    if not m:
        return None
    indent = m.group(1)
    return (f"{indent}name: {job_name}\n", indent)


def _scan_job(
    job_name: str, job: dict, file_path: Path, raw_text: str
) -> list:
    findings: list = []
    anchor = _job_anchor(job_name, raw_text)

    if "max_concurrent_runs" not in job:
        before = after = None
        if anchor is not None:
            line, indent = anchor
            before = line
            after = f"{line}{indent}max_concurrent_runs: 1\n"
        findings.append(
            Finding(
                rule_id="DBX-PERF-001",
                severity="warning",
                target=str(file_path),
                message=f"job {job_name!r} has no max_concurrent_runs set",
                suggestion="set max_concurrent_runs: 1 to prevent overlapping runs",
                before=before,
                after=after,
            )
        )

    if "timeout_seconds" not in job:
        before = after = None
        if anchor is not None:
            line, indent = anchor
            before = line
            after = f"{line}{indent}timeout_seconds: 3600\n"
        findings.append(
            Finding(
                rule_id="DBX-PERF-004",
                severity="warning",
                target=str(file_path),
                message=f"job {job_name!r} has no timeout_seconds set",
                suggestion="set timeout_seconds: 3600 as a safe default",
                before=before,
                after=after,
            )
        )

    for task in job.get("tasks", []) or []:
        cluster = task.get("new_cluster") or task.get("job_cluster") or {}
        if not isinstance(cluster, dict):
            continue
        task_key = task.get("task_key", "<unknown>")

        autoscale = cluster.get("autoscale") or {}
        if isinstance(autoscale, dict):
            mn = autoscale.get("min_workers")
            mx = autoscale.get("max_workers")
            if mn is not None and mx is not None and mn == mx:
                findings.append(
                    Finding(
                        rule_id="DBX-PERF-002",
                        severity="info",
                        target=str(file_path),
                        message=(
                            f"task {task_key!r} in job {job_name!r} has "
                            f"min_workers == max_workers ({mn}); no autoscaling"
                        ),
                        suggestion="widen the autoscale range to enable scaling",
                    )
                )

        spark_version = cluster.get("spark_version") or ""
        major = _dbr_major(spark_version)
        if major is not None and major < 14:
            findings.append(
                Finding(
                    rule_id="DBX-PERF-003",
                    severity="warning",
                    target=str(file_path),
                    message=(
                        f"task {task_key!r} in job {job_name!r} uses "
                        f"spark_version {spark_version!r} (older than DBR 14.x)"
                    ),
                    suggestion="upgrade to DBR 14.x or newer LTS runtime",
                )
            )

        engine = (cluster.get("runtime_engine") or "").upper()
        if engine and engine != "PHOTON":
            findings.append(
                Finding(
                    rule_id="DBX-PERF-005",
                    severity="info",
                    target=str(file_path),
                    message=(
                        f"task {task_key!r} in job {job_name!r} has Photon "
                        f"disabled (runtime_engine={engine})"
                    ),
                    suggestion="enable Photon by setting runtime_engine: PHOTON",
                )
            )

    return findings


def _scan_resource_file(file_path: Path) -> list:
    try:
        raw = file_path.read_text()
        doc = yaml.safe_load(raw) or {}
    except (OSError, yaml.YAMLError):
        return []
    if not isinstance(doc, dict):
        return []
    jobs = ((doc.get("resources") or {}).get("jobs")) or {}
    if not isinstance(jobs, dict):
        return []
    out: list = []
    for job_name, job in jobs.items():
        if isinstance(job, dict):
            out.extend(_scan_job(job_name, job, file_path, raw))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Optimize a Databricks Asset Bundle for performance."
    )
    parser.add_argument("--bundle-path", required=True, dest="bundle_path")
    parser.add_argument(
        "--mode",
        choices=["report", "apply", "dry-run"],
        default="report",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", dest="fmt"
    )
    args = parser.parse_args(argv)

    bundle = Path(args.bundle_path).resolve()
    databricks_yml = bundle / "databricks.yml"
    if not databricks_yml.exists():
        print(
            f"optimize-databricks-job: missing {databricks_yml}",
            file=sys.stderr,
        )
        return 2

    resources_dir = bundle / "resources"
    findings: list = []
    if resources_dir.is_dir():
        for yml in sorted(resources_dir.glob("*.yml")):
            findings.extend(_scan_resource_file(yml))

    apply, dry_run = _lib.parse_mode(args.mode)
    apply_failed = False
    if apply or dry_run:
        for f in findings:
            if f.before is None or f.after is None:
                continue
            ok = _lib.apply_finding(f, dry_run=dry_run)
            if not ok and apply:
                apply_failed = True

    if args.fmt == "json":
        out = _lib.format_json(findings)
    else:
        out = _lib.format_text(findings)
    print(_lib.redact_tokens(out))

    if apply and apply_failed:
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
