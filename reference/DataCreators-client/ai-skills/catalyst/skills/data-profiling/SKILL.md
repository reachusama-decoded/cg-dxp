---
name: data-profiling
description: "Profile source tables for quality, completeness, and fitness. Use during Phase 2 Discovery to assess source data before writing the feasibility report, or Phase 5 Validate to verify built tables."
allowed-tools: Read Grep Bash
metadata:
  tier: workflow
  lifecycle-phase: phase-2-discovery
  dependencies: []
  consumes:
    - discover-data
  shared-components:
    core: [profile_table]
    platforms: [databricks]
---

# Data Profiling

Profile the tables listed in $ARGUMENTS and produce a quality assessment report.

This is a **Phase 2 (Discovery) / Phase 5 (Validate)** execution skill.  During
Discovery it tells you whether source data is fit for purpose before you commit
to building.  During Validate it confirms that built tables meet the quality
thresholds defined in the data contract.

## Lifecycle Context

| Before this skill | This skill | After this skill |
|:------------------|:-----------|:-----------------|
| `discover-data` identified candidate tables | Profiles each table in one batched SQL pass | `feasibility-report` cites quality findings; `data-quality-sign-off` references validate results |

## Instructions

1. Read the profiling checklist at `skills/data-profiling/references/PROFILING_CHECKLIST.md`
   for the quality dimensions and checks to apply.

2. Parse $ARGUMENTS into a list of fully-qualified table names
   (`catalog.schema.table`).  Ask the user for catalog, schema, and table if
   only a bare table name is given.

3. For each table, call `profile_table()` from `skills/core/profile.py`:

   ```python
   from skills.clients.databricks import DatabricksClient
   from skills.core.profile import profile_table

   client = DatabricksClient(host=DATABRICKS_HOST, token=DATABRICKS_TOKEN,
                              warehouse_id=WAREHOUSE_ID)
   result = profile_table(client, catalog=catalog, schema=schema, table=table)
   ```

   The function runs a single batched SQL pass — one `DESCRIBE` plus one
   aggregation `SELECT` — so it is safe to call on large tables.

3. Interpret the results:
   - `null_rate > 0.20` on a key column is a quality concern — flag it.
   - `distinct_count == row_count` on a column that should be a key confirms
     uniqueness.
   - `date_range` tells you the historical coverage of the table.

4. Format findings as the profiling report below.

## Output Format

```markdown
## Data Profiling Report — <table>

**Rows:** 82,000,000 | **Columns:** 14 | **Date range:** 2019-01-01 → 2024-12-31

### Column Quality

| Column | Type | Null Rate | Distinct Count | Notes |
|:-------|:-----|----------:|--------------:|:------|
| txn_id | bigint | 0.00% | 82,000,000 | Unique key confirmed |
| client_id | bigint | 0.02% | 4,195,000 | Acceptable |
| amount | decimal | 0.00% | 12,400,000 | |
| status | string | 0.15% | 8 | Low cardinality |
| load_date | date | 0.00% | 2,190 | Range: 2019-01-01 → 2024-12-31 |

### Summary

- **Overall quality:** ACCEPTABLE — no blocking issues found.
- **Concerns:** `status` has 0.15% nulls — confirm whether nulls are valid.
- **Recommendation:** Suitable as a primary source for the data product.
```

Profile each requested table as a separate section.  End with a one-paragraph
fitness-for-purpose summary.

## When Databricks Is Not Configured

If credentials are not set or the connection fails:

1. Tell the user: "Databricks is not connected — I can't profile live
   tables. To enable profiling, configure your .env with Databricks
   credentials (see .env.example)."
2. If the user can provide sample data or schema descriptions, produce
   a best-effort profile from that information.
3. Note in the output that the profile is based on user-provided data,
   not live queries.

## Dependencies

- `skills/core/profile.py` — `profile_table()`
- `skills/clients/databricks.py` — `DatabricksClient`
- Environment: `DATABRICKS_HOST`, `DATABRICKS_TOKEN` (legacy — see note below), `WAREHOUSE_ID`

> **Auth note (DBX-SEC-002):** the examples above pre-date the OAuth migration. `DATABRICKS_TOKEN` must be a service-principal-scoped credential (OAuth-materialized bearer or SP-PAT), never a user PAT. See `/connect-databricks` for the OAuth-only pattern and detection logic. The legacy `token=` example will move to OAuth client credentials when this skill is donated into PR 95's lifecycle.
