# Baseline: optimize-dbsql-query vs. unaided agent

**Date:** 2026-05-15
**`optimize-dbsql-query` commit:** `987d382946bdff2c25c7ada6d2cc268c50df7d3e`

## Method

Qualitative comparison of finding coverage between (a) the
`optimize-dbsql-query` capability skill and (b) an unaided agent (no
skills, no scripts) asked to "review this SQL for performance" from a
free-form prompt against the same `.sql` files.

A full LLM-driven run against a prompt suite was not executed in this
PR; the unaided behavior is non-deterministic. The qualitative
comparison below is sufficient to justify the skill against the
SQL-PERF-DBSQL-* bar that its `optimize.py` enforces.

## Finding coverage

| rule_id | Unaided agent (best-effort) | Skill (detected? auto-applies?) |
|---|---|---|
| SQL-PERF-DBSQL-001 (`SELECT *`) | Sometimes flags, phrasing varies | Detected (warning); no auto-apply |
| SQL-PERF-DBSQL-002 (cross join: comma-separated FROM, or JOIN without ON/USING) | May spot comma cross joins; often misses JOIN-without-ON | Detected (error); no auto-apply |
| SQL-PERF-DBSQL-003 (WHERE wraps column in `UPPER`/`LOWER`/`DATE`/`CAST`/`SUBSTR`/`SUBSTRING`/`YEAR`/`MONTH`/`DAY` -> defeats data skipping) | Rarely identifies the data-skipping consequence | Detected (warning); no auto-apply |
| SQL-PERF-DBSQL-004 (ORDER BY inside a parenthesized SELECT subquery without LIMIT) | Not addressed | Detected (info); no auto-apply |
| SQL-PERF-DBSQL-005 (Delta `CREATE TABLE ... USING DELTA` missing `CLUSTER BY`) | Not addressed | Detected (info); no auto-apply |

## Determinism

- **Unaided:** non-deterministic. Same prompt produces different
  findings across runs; no guarantee any individual rule above is
  caught.
- **Skill:** deterministic. Same `.sql` input produces the same
  findings byte-for-byte.

## Apply mode

- **Skill:** has no auto-fix rules today; `--mode apply` and `--mode
  dry-run` are no-ops that succeed (exit 0). The skill is report-only.
- **Unaided:** would have to hand-edit `.sql` files based on free-form
  suggestions, with no idempotency guarantee.

## Out of scope for this baseline

- Quantitative LLM-driven run (tokens, latency, success rate over a
  prompt suite).
