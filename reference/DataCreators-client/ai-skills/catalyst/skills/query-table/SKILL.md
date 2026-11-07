---
name: query-table
description: >
  Run SQL against a connected Databricks workspace. Trigger phrases:
  "run this query", "query this table", "show me the schema",
  "describe table", "execute SQL".
allowed-tools: Read Bash
metadata:
  tier: capability
  lifecycle-phase: none
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
  standards: [DBX-SEC-002]
---

# Query Table

Execute a SQL statement or table inspection query against Databricks and
return structured results.

## Instructions

1. Parse $ARGUMENTS to determine the query type:
   - **Fully-qualified table name** (e.g. `catalog.schema.table`) --
     run `DESCRIBE TABLE EXTENDED catalog.schema.table`.
   - **Bare SQL** (starts with `SELECT`, `DESCRIBE`, `SHOW`, or `WITH`) --
     run the statement as-is.
   - **Short table name** (no catalog/schema) -- ask the user for the
     fully-qualified name before proceeding.

2. Establish a connection using `skills/clients/databricks.py`:

   ```python
   from skills.clients.databricks import DatabricksClient

   client = DatabricksClient(
       host=DATABRICKS_HOST,
       client_id=DATABRICKS_CLIENT_ID,
       client_secret=DATABRICKS_CLIENT_SECRET,
       warehouse_id=WAREHOUSE_ID,
   )
   ```

3. Execute the query. Handle these scenarios:
   - **Large result sets** -- limit output to 1,000 rows by default.
     Append `LIMIT 1000` if the user's SQL does not already include a
     limit. Inform the user the results are truncated.
   - **Timeouts** -- if the query does not return within 120 seconds,
     cancel it and suggest the user add filters or run on a larger
     warehouse.
   - **Errors** -- surface the Databricks error message verbatim and
     suggest corrections (typo in table name, missing catalog, etc.).

4. Format the results as a markdown table. For wide result sets (more
   than 8 columns), use a condensed format or offer to return raw CSV.

## Output Format

```markdown
## Query Results

**SQL:** `SELECT client_id, amount FROM catalog.schema.table LIMIT 5`
**Rows returned:** 5 (of ~82,000,000)

| client_id | amount |
|----------:|-------:|
| 101 | 4500.00 |
| 102 | 1200.50 |
| 103 | 8700.00 |
| 104 | 330.25 |
| 105 | 6100.75 |
```

For `DESCRIBE` output, format the column list with types and comments.

## Error Handling

- **Connection not established** -- prompt the user to run
  `connect-databricks` first, or attempt auto-connection.
- **Permission denied** -- report the table/catalog and suggest the user
  check their Unity Catalog grants.
- **Table not found** -- suggest running `query-catalog` to discover
  available tables.

## Standalone Usage

```
/query-table catalog.schema.table
/query-table SELECT COUNT(*) FROM catalog.schema.fct_transactions
```

## Composition

Used by:
- `execution/data-profiling` (via batched SQL pass)
- `execution/discover-data` (schema inspection)
- `execution/data-modeling` (source exploration)

## Dependencies

- `skills/clients/databricks.py` -- `DatabricksClient`
- Environment: `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET`, `WAREHOUSE_ID` (OAuth M2M credentials per DBX-SEC-002)
