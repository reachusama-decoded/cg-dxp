# Baseline: optimize-databricks-job vs. unaided agent

**Date:** 2026-05-15
**`optimize-databricks-job` commit:** `078efddeb5fe3e877ae12727337c42718c9685ad`

## Method

Qualitative comparison of finding coverage and apply behavior between
(a) the `optimize-databricks-job` capability skill and (b) an unaided
agent (no skills, no scripts) asked to "optimize this Databricks job"
from a free-form prompt against the same rendered DAB tree's
`resources/*.yml`.

A full LLM-driven run against a prompt suite was not executed in this
PR; the unaided behavior is non-deterministic. The qualitative
comparison below is sufficient to justify the skill against the
DBX-PERF-* bar that its `optimize.py` enforces.

## Finding coverage

| rule_id | Unaided agent (best-effort) | Skill (detected? auto-applies?) |
|---|---|---|
| DBX-PERF-001 (job missing `max_concurrent_runs`) | Often overlooked | Detected (warning); auto-applies by inserting `max_concurrent_runs: 1` under the job's `name:` anchor |
| DBX-PERF-002 (task autoscale `min_workers == max_workers`) | Rarely identified as a no-op autoscale | Detected (info); report-only, no auto-apply |
| DBX-PERF-003 (task `spark_version` older than DBR 14.x) | Sometimes suggests an upgrade, version varies | Detected (warning); report-only |
| DBX-PERF-004 (job missing `timeout_seconds`) | Frequently omitted | Detected (warning); auto-applies by inserting `timeout_seconds: 3600` |
| DBX-PERF-005 (task `runtime_engine` set but not `PHOTON`) | Not addressed | Detected (info); report-only |

## Determinism

- **Unaided:** non-deterministic. Same prompt produces different
  rewrites across runs; no guarantee any individual rule above is
  caught.
- **Skill:** deterministic. Same `resources/*.yml` input produces the
  same findings and the same applied edits byte-for-byte.

## Apply mode

- **Skill:** `--mode apply` writes fixes in-place for DBX-PERF-001 and
  DBX-PERF-004 (the rules with `before`/`after` blocks anchored to the
  job's indented `name:` line); idempotent on re-run.
- **Unaided:** would have to hand-edit each `resources/*.yml` based on
  free-form suggestions, with no idempotency guarantee.

## Out of scope for this baseline

- Quantitative LLM-driven run (tokens, latency, success rate over a
  prompt suite).
