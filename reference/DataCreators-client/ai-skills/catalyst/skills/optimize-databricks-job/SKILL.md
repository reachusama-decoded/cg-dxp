---
name: optimize-databricks-job
description: |
  Performance optimizer for Databricks Asset Bundle (DAB) jobs. Scans
  a rendered bundle's `resources/*.yml` and emits DBX-PERF-* findings
  (with light overlap with DBX-BUNDLE-*) covering concurrency, timeouts,
  cluster sizing, runtime version, and Photon. Three modes: report
  (default), apply (writes safe defaults for max_concurrent_runs and
  timeout_seconds), dry-run (shows what apply would change without
  writing). Trigger phrases: "optimize databricks job",
  "tune dab performance", "dbx-perf check".
allowed-tools: Read Bash Write
metadata:
  tier: capability
  lifecycle-phase: phase-7-operate
  dependencies:
    - setup-databricks-asset-bundle
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    - DBX-PERF-*
---

# optimize-databricks-job

Performance-side counterpart to `validate-dab`. Where validate-dab
covers correctness/security (DBX-BUNDLE-*), this skill surfaces
performance hygiene issues against the DBX-PERF-* category and can
apply safe defaults in place.

## When to use

- After `write-dab-resource` and before `deploy-dab`, to catch
  performance regressions in hand-edited bundle files.
- Invoked automatically by `validate-dab` in report mode (forward
  reference; validate-dab skips silently when this script is absent).
- Ad-hoc optimization pass on an existing bundle.

## Inputs

CLI flags:

- `--bundle-path` (required) -- path to a rendered DAB tree (the
  directory containing `databricks.yml`).
- `--mode` (default `report`) -- one of `report`, `apply`, `dry-run`.
- `--format` (default `text`) -- `text` or `json`.

## Outputs

A list of findings, each with:

- `rule_id` -- e.g. `DBX-PERF-001`.
- `severity` -- `info`, `warning`, or `error`.
- `target` -- resource file path.
- `message` -- human-readable explanation.
- `suggestion` -- fix recommendation.
- `before` / `after` / `applied` -- populated when the finding is
  apply-able (currently DBX-PERF-001 and DBX-PERF-004).

Token-shaped substrings (`Bearer ...`, `dapi*`, `dsapi*`) in the
rendered output are scrubbed via the shared `redact_tokens` helper.

Exit code:

- `0` -- report completed, or apply succeeded.
- `2` -- input error (no `databricks.yml` at `--bundle-path`).
- `5` -- apply mode: at least one apply-able finding could not be
  written (anchor not found in source file).

## Rules implemented

- `DBX-PERF-001` (warning, apply) -- job has no `max_concurrent_runs`
  set. Apply writes `max_concurrent_runs: 1`.
- `DBX-PERF-002` (info) -- job task with `min_workers == max_workers`
  (no autoscaling).
- `DBX-PERF-003` (warning) -- cluster `spark_version` is older than
  DBR 14.x.
- `DBX-PERF-004` (warning, apply) -- job has no `timeout_seconds`.
  Apply writes `timeout_seconds: 3600`.
- `DBX-PERF-005` (info) -- Photon disabled on a job cluster
  (`runtime_engine` is set but not `PHOTON`).

## Composes with

- Loaded by `validate-dab` -- the optimizer is invoked in report mode
  during validate, and its findings are appended (forward reference is
  now resolved).

## Procedure

1. Resolve `--bundle-path`; exit 2 if `databricks.yml` is missing.
2. Walk `resources/*.yml`, parse each as YAML, iterate
   `resources.jobs.*`.
3. For each job, run the DBX-PERF-* checks above and accumulate
   findings.
4. If `--mode apply` (or `dry-run`), call `apply_finding` from
   `skills/_lib/optimize.py` on each apply-able finding. Apply-mode
   write failures produce exit code 5.
5. Render via `format_text` or `format_json` from the shared lib,
   running output through `redact_tokens` before printing.

## Failure modes

- Malformed YAML in a `resources/*.yml` file -- that file is skipped
  silently; other files continue to scan.
- Apply mode cannot locate the job's `name:` anchor line -- finding
  is reported but not applied; exit 5.
- Bundle path missing `databricks.yml` -- exit 2 with a clear stderr
  message; no scan performed.
