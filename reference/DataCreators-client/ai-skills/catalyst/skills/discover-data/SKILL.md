---
name: discover-data
description: "Query Unity Catalog for tables relevant to a data product. Use during Phase 2 Discovery to inventory available sources before writing the feasibility report."
allowed-tools: Read Grep Bash
metadata:
  tier: workflow
  lifecycle-phase: phase-2-discovery
  dependencies: []
  consumes: []
  shared-components:
    core: [discover_tables]
    platforms: [databricks]
  standards: [DBX-SEC-002]
---

# Discover Data

Search Unity Catalog for tables relevant to the data product described in $ARGUMENTS.

This is a **Phase 2 (Discovery)** execution skill.  It feeds raw discovery output
into the `feasibility-report`, `requirements-acceptance-criteria`, and
`data-contract` document skills.  Run it before any artifact generation so your
documents are grounded in the actual available schema — not assumptions.

## Lifecycle Context

| Before this skill | This skill | After this skill |
|:------------------|:-----------|:-----------------|
| `dplc-triage` produced a classification | Inventories real tables in Unity Catalog | `data-profiling` assesses quality; `feasibility-report` documents findings |

## Instructions

1. **Check for Databricks credentials before doing anything else.** Verify
   that `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET`,
   and `DATABRICKS_WAREHOUSE_ID` are all set. If any are missing or the
   connection cannot be established, **stop here and follow the steps in
   [When Databricks Is Not Configured](#when-databricks-is-not-configured)
   below.** Do not proceed to step 2.

2. Parse $ARGUMENTS: extract `catalog` (required), optional `schema`, and
   any `keywords` that describe the subject matter of the data product.

3. Use the `discover_tables()` function from `skills/core/discover.py`:

   ```python
   from skills.clients.databricks import DatabricksClient
   from skills.core.discover import discover_tables

   client = DatabricksClient(host=DATABRICKS_HOST,
                              client_id=DATABRICKS_CLIENT_ID,
                              client_secret=DATABRICKS_CLIENT_SECRET,
                              warehouse_id=WAREHOUSE_ID)
   tables = discover_tables(client, catalog=catalog, keywords=keywords, schema=schema)
   ```

4. If no keywords are provided, return all tables in the catalog (or schema).
   If keywords are provided, the function filters by table name and column names.

5. Format the results as a structured markdown table (see Output Format below).

6. Flag tables that look like strong candidates — name matches all keywords,
   or have columns that align tightly with the product's domain.

## Output Format

Produce a markdown section ready to paste into a feasibility report:

```markdown
## Discovered Tables — <catalog>

Searched: `<catalog>` | Schema filter: `<schema or "all">` | Keywords: `<keywords or "none">`

| Schema | Table | Row Count | Key Columns | Relevance |
|:-------|:------|----------:|:------------|:----------|
| payments | dim_client | 4,200,000 | client_id, client_name, status | HIGH — matches "client" keyword |
| payments | fct_transactions | 82,000,000 | txn_id, client_id, amount, txn_date | HIGH — matches "transactions" keyword |
| reference | ref_currency | 180 | currency_code, currency_name | LOW — reference only |

**Recommended sources:** `payments.dim_client`, `payments.fct_transactions`
```

If no tables are found, say so explicitly and suggest refining the keywords or
checking catalog/schema names with the data platform team.

## When Databricks Is Not Configured

If the environment variables (`DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`,
`DATABRICKS_CLIENT_SECRET`, `DATABRICKS_WAREHOUSE_ID`) are not set, or the
connection fails, **do not silently assume the schema**. Instead:

1. **Inform the user** that the actual schema cannot be pulled live:
   > "Databricks connection is not configured — I cannot verify the source schema.
   > To pull the real schema definitions, set up your Databricks credentials."

2. **Offer to run `connect-databricks`** to establish the connection:
   > "Would you like me to help you configure Databricks credentials now?
   > I'll walk you through setting up your `.env` file."

3. If the user accepts, guide them through the setup:
   - Copy `.env.example` to `.env` (if not already present).
   - Ask the user to open [`.env`](.env) and fill in the required values:
     - `DATABRICKS_HOST` — workspace URL (e.g. `https://your-workspace.cloud.databricks.com`)
     - `DATABRICKS_CLIENT_ID` — OAuth M2M client ID (service principal application ID) per DBX-SEC-002
     - `DATABRICKS_CLIENT_SECRET` — OAuth M2M client secret per DBX-SEC-002
     - `DATABRICKS_WAREHOUSE_ID` — SQL warehouse ID
   - **Do NOT ask the user to paste credentials in chat.** Direct them to
     edit [`.env`](.env) directly or use `databricks configure --profile DEFAULT`.
   - Once the user confirms values are saved, validate via `connect-databricks` (run `SELECT 1`).

4. Once connected, **re-attempt schema discovery** by running:
   ```sql
   DESCRIBE TABLE <fully_qualified_source_table>
   ```
   and return the live column definitions to the calling skill.

5. If the user declines or cannot provide credentials:
   1. Tell the user: "Databricks is not connected — I'll proceed with what
      you've provided. To get richer discovery results, configure your .env
      with Databricks credentials (see .env.example)."
   2. Proceed with the workflow using only information from the user and
      any prior artifacts. Do not block or fail.
   3. Note in the output that results are based on user-provided context,
      not live catalog queries.
   4. Mark all schema-dependent outputs with:
      > **Schema inferred — not verified against live catalog.** Run
      > `connect-databricks` and re-run this skill to produce verified results.

## Dependencies

- `skills/core/discover.py` — `discover_tables()`
- `skills/clients/databricks.py` — `DatabricksClient`
- `skills/connect-databricks` — invoked when credentials need setup
- Environment (required for schema verification): `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET`, `DATABRICKS_WAREHOUSE_ID` (OAuth M2M credentials per DBX-SEC-002)
