---
name: optimize-dbsql-query
description: |
  Scan SQL files (compiled dbt models or hand-written DBSQL queries)
  for common Databricks SQL performance pitfalls and emit findings
  under the SQL-PERF-DBSQL-* family. Pure static analysis: no
  warehouse connection, no auth. Suggestion-only - findings carry
  remediation text but no automated rewrites. Trigger phrases:
  "optimize dbsql query", "check sql performance", "scan sql for
  perf issues".
allowed-tools: Read Bash
metadata:
  tier: capability
  lifecycle-phase: phase-7-operate
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    - SQL-PERF-DBSQL-001
    - SQL-PERF-DBSQL-002
    - SQL-PERF-DBSQL-003
    - SQL-PERF-DBSQL-004
    - SQL-PERF-DBSQL-005
---

# optimize-dbsql-query

Static analyzer for `.sql` files targeting Databricks SQL. Detects
five classes of performance anti-patterns and reports them as
`Finding` records via the shared `skills/_lib/optimize.py` library.
No SQL is executed; no auto-fix is attempted. All findings are
advisory.

## Rules

- `SQL-PERF-DBSQL-001` (warning): `SELECT *` against a source table.
- `SQL-PERF-DBSQL-002` (error): cross join - two tables joined with
  no `ON` clause (comma join or `JOIN ... ` without `ON`).
- `SQL-PERF-DBSQL-003` (warning): `WHERE` predicate wrapping a
  column in a function (`UPPER(col)`, `DATE(col)`) - defeats
  partition/Z-order pruning.
- `SQL-PERF-DBSQL-004` (info): `ORDER BY` inside a subquery
  without `LIMIT` - sort is discarded by outer scope.
- `SQL-PERF-DBSQL-005` (info): `CREATE TABLE ... USING DELTA`
  without a `CLUSTER BY` clause - misses liquid clustering hint.

## Usage

```
python3 skills/optimize-dbsql-query/scripts/optimize.py \
    --path path/to/file_or_dir \
    --mode report \
    --format text
```

Modes: `report` (default), `apply` (no rules auto-fix today, exits
0), `dry-run` (no writes).

Exit codes: 0 success, 2 input error, 5 apply failure.
