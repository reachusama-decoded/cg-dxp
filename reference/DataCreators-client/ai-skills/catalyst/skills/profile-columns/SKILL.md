---
name: profile-columns
description: >
  Compute column-level statistics from table data. Trigger phrases:
  "profile this table", "what's the data quality",
  "show column stats", "assess data fitness".
allowed-tools: Read Bash
metadata:
  tier: capability
  lifecycle-phase: none
  dependencies: []
  consumes: []
  shared-components:
    core: [profile_table]
    platforms: [databricks]
---

# Profile Columns

Compute column-level quality statistics for the tables listed in $ARGUMENTS
and produce a structured profiling report.

## Instructions

1. Read the profiling checklist at
   `skills/profile-columns/references/profiling-checklist.md`
   for the quality dimensions and SQL templates to apply.

2. Parse $ARGUMENTS into a list of fully-qualified table names
   (`catalog.schema.table`). Ask the user for catalog, schema, and table
   if only a bare table name is given.

3. For each table, call `profile_table()` from `skills/core/profile.py`:

   ```python
   from skills.clients.databricks import DatabricksClient
   from skills.core.profile import profile_table

   client = DatabricksClient(
       host=DATABRICKS_HOST,
       token=DATABRICKS_TOKEN,
       warehouse_id=WAREHOUSE_ID,
   )
   result = profile_table(client, catalog=catalog, schema=schema, table=table)
   ```

   The function runs a single batched SQL pass -- one `DESCRIBE` plus one
   aggregation `SELECT` -- so it is safe to call on large tables.

4. Interpret the results:
   - `null_rate > 0.20` on a key column is a quality concern -- flag it.
   - `distinct_count == row_count` on a column that should be a key
     confirms uniqueness.
   - `date_range` tells you the historical coverage of the table.

5. Format findings using the output format below.

## Output Format

```markdown
## Column Profile -- <catalog.schema.table>

**Rows:** 82,000,000 | **Columns:** 14 | **Date range:** 2019-01-01 to 2024-12-31

### Column Quality

| Column | Type | Null Rate | Distinct Count | Min | Max | Notes |
|:-------|:-----|----------:|--------------:|:----|:----|:------|
| txn_id | bigint | 0.00% | 82,000,000 | 1 | 82000000 | Unique key confirmed |
| client_id | bigint | 0.02% | 4,195,000 | 100 | 9999999 | Acceptable |
| amount | decimal | 0.00% | 12,400,000 | 0.01 | 999999.99 | |
| status | string | 0.15% | 8 | | | Low cardinality |

### Summary

- **Overall quality:** ACCEPTABLE -- no blocking issues found.
- **Concerns:** `status` has 0.15% nulls -- confirm whether nulls are valid.
- **Recommendation:** Suitable as a primary source for the data product.
```

Profile each requested table as a separate section. End with a
fitness-for-purpose summary.

## Error Handling

- **Databricks not configured** -- tell the user to configure `.env`
  with Databricks credentials. Offer best-effort profile from sample data.
- **Table not found** -- suggest running `query-catalog` to verify.
- **Query timeout** -- suggest profiling fewer columns or a date filter.

## Standalone Usage

```
/profile-columns cspn_dev1.payments.fct_transactions
```

## Composition

Used by: `execution/data-profiling`, `orchestrators/dplc-discovery`.

## Dependencies

- `skills/core/profile.py` -- `profile_table()`
- `skills/clients/databricks.py` -- `DatabricksClient`
- Environment: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `WAREHOUSE_ID`
