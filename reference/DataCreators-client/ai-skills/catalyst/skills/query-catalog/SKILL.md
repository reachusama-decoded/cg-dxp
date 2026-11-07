---
name: query-catalog
description: >
  Discover catalogs, schemas, tables, and columns in Unity Catalog.
  Trigger phrases: "list tables", "what schemas exist",
  "find tables matching", "discover data", "search catalog".
allowed-tools: Read Bash
metadata:
  tier: capability
  lifecycle-phase: none
  dependencies: []
  consumes: []
  shared-components:
    core: [discover_tables]
    platforms: [databricks]
---

# Query Catalog

Search Unity Catalog for tables matching the criteria in $ARGUMENTS and
return a ranked, structured list of results.

## Instructions

1. Parse $ARGUMENTS: extract `catalog` (required), optional `schema`, and
   any `keywords` that describe the subject matter.

2. Use `discover_tables()` from `skills/core/discover.py`:

   ```python
   from skills.clients.databricks import DatabricksClient
   from skills.core.discover import discover_tables

   client = DatabricksClient(
       host=DATABRICKS_HOST,
       token=DATABRICKS_TOKEN,
       warehouse_id=WAREHOUSE_ID,
   )
   tables = discover_tables(
       client,
       catalog=catalog,
       keywords=keywords,
       schema=schema,
   )
   ```

3. If no keywords are provided, return all tables in the catalog (or
   schema). If keywords are provided, the function filters by table name
   and column names.

4. Rank results by relevance:
   - **HIGH** -- name matches all keywords, or columns align tightly
     with the requested domain.
   - **MEDIUM** -- partial keyword match or related domain.
   - **LOW** -- reference or utility table with tangential relevance.

5. Format results using the output format below.

## Output Format

```markdown
## Catalog Discovery -- <catalog>

Searched: `<catalog>` | Schema filter: `<schema or "all">` | Keywords: `<keywords or "none">`

| Schema | Table | Row Count | Key Columns | Relevance |
|:-------|:------|----------:|:------------|:----------|
| payments | dim_client | 4,200,000 | client_id, client_name | HIGH |
| payments | fct_transactions | 82,000,000 | txn_id, client_id, amount | HIGH |
| reference | ref_currency | 180 | currency_code | LOW |

**Recommended sources:** `payments.dim_client`, `payments.fct_transactions`
```

If no tables are found, say so explicitly and suggest refining keywords
or checking catalog/schema names with the data platform team.

## Error Handling

- **Databricks not configured** -- tell the user: "Databricks is not
  connected. I'll proceed with what you've provided. Configure your
  `.env` with Databricks credentials (see `.env.example`)." Proceed
  using only user-provided context. Do not block or fail.
- **Catalog not found** -- suggest running `SHOW CATALOGS` to list
  available catalogs.
- **Empty results** -- suggest broadening keyword search or checking
  schema spelling.

## Standalone Usage

```
/query-catalog cspn_dev1 client positions
/query-catalog cspn_dev1 --schema payments
```

## Composition

Used by:
- `execution/discover-data` (full discovery workflow)
- `orchestrators/dplc-discovery` (Phase 2 source inventory)

## Dependencies

- `skills/core/discover.py` -- `discover_tables()`
- `skills/clients/databricks.py` -- `DatabricksClient`
- Environment: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `WAREHOUSE_ID`
