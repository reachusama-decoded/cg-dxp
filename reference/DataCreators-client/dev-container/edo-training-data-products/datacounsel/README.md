
# datacounsel

Extends [datacontract-cli](https://github.com/datacontract/datacontract-cli) with custom exporters for Databricks SQL.

This platform helper adds Databricks SQL export support to `datacontract-cli`. Migration commands below require an authorised platform workflow; they are not a prerequisite for [assigned v2 practice](../challenges/v2/README.md).

| Feature  | Argument         | Notes                                        |
| -------- | ---------------- | -------------------------------------------- |
| `export` | `--format dbsql` | Adds external location and partition support |
| `import` | `--format dbsql` | Not implemented                   |
| `import` | `--format uc`    | TBD - Not implemented yet!                   |

**note**: All other commands pass and can be directly referenced by `uv run datacontract`.

---

## Local Developer Workflow

### How it works

Contracts (`.odcs.yaml`) define the table schema. `datacounsel generate-migration` converts them into Flyway-compatible SQL files. `flyway migrate` applies those SQL files to Databricks.

Generated SQL uses Flyway placeholders (`${catalog}`, `${schema}`, `${location}`, `${env_grant_prefix}`) — no environment-specific values are hardcoded. Your `.env` file controls which catalog, schema, location, and grant prefix get used at runtime.

**CI is the canonical generator** — `flyway/migrations/` is owned by CI (Harness bot commits generated SQL on PRs). Locally, SQL is generated into `.local/migrations/` (gitignored) and is throwaway. You only commit the `.odcs.yaml` contract.

### First-time setup

1. Open the repo in VS Code and reopen in the dev container when prompted.

2. Run OAuth-first setup in the dev container:

```bash
mise run setup:databricks
```

This creates `.devcontainer/.env` from template if needed and runs Databricks OAuth login.  
Use PAT only as explicit fallback:

```bash
mise run setup:databricks --pat
```

Required values in `.devcontainer/.env`:

```
DATABRICKS_HOST=https://cg-db-aa00003661-dev-us-east-1.cloud.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/<warehouse-id>
DATABRICKS_CATALOG=training_dev
DATABRICKS_SCHEMA=dev_yourname        # your personal schema, e.g. dev_nick

# Only needed for data products that use external tables (external: true in contract schema)
# The migrate task appends /${DATABRICKS_SCHEMA} automatically, so each developer gets an
# isolated S3 prefix: e.g. s3://.../training_dev/dev_nick/currency_v4
DATABRICKS_LOCATION_ASSET_REFERENCE_DATA=s3://datalake-curated-dev1-us-east-1/training_dev
# DATABRICKS_LOCATION_ORDERS=s3://...
```

3. Run once to create your personal schema and Flyway history table in Databricks:

```bash
mise run contract:init
```

4. **If using external tables** (`external: true` in the contract schema), your account must have `CREATE EXTERNAL TABLE` on the external location in Unity Catalog. This is provisioned by the platform team — contact them if you get a permissions error when running `contract:migrate`.

### Deploying a contract to your personal schema

```bash
mise run contract:migrate data_products/<product>/datasets/<dataset>/contract/<contract>.odcs.yaml
```

> **Note:** Run from the repo root (`/workspaces/edo-training-data-products`).

This will:
- Generate SQL into `.local/migrations/<data_product>/` (gitignored; accumulates across versions for ALTER TABLE diff)
- Apply the migration to `${DATABRICKS_CATALOG}.${DATABRICKS_SCHEMA}` via Flyway
- Substitute `${catalog}` → `DATABRICKS_CATALOG`, `${schema}` → `DATABRICKS_SCHEMA`, `${location}` → `DATABRICKS_LOCATION_<DATA_PRODUCT>/<DATABRICKS_SCHEMA>`

### If a migration fails

Databricks does not support transactional DDL — each DDL statement auto-commits immediately. To minimise the blast radius of failures, **the generator produces one file per atomic DDL change** when a version contains multiple schema changes:

| Changes in version | Files generated |
|--------------------|----------------|
| 1 change | `V20260512143022__table_v1_0_8.sql` |
| 3 changes | `V20260512143022.1__table_v1_0_8.sql`, `V20260512143022.2__table_v1_0_8.sql`, `V20260512143022.3__table_v1_0_8.sql` |

This means at most one statement can be in a partially-applied state if Flyway fails mid-run. Flyway applies sub-versioned files in order, checkpointing after each one.

If a migration does fail, run `flyway repair` via the repair task to clear the failed record from the history table. The repair output shows you exactly which SQL statement may have been partially applied so you know what to undo manually, then retry:

```bash
mise run contract:repair data_products/<product>/datasets/<dataset>/contract/<contract>.odcs.yaml
# Undo any partially-applied statements shown in the repair output (e.g. DROP COLUMN)
mise run contract:migrate data_products/<product>/datasets/<dataset>/contract/<contract>.odcs.yaml
```

Example:
```bash
mise run contract:migrate data_products/asset_reference_data/datasets/currency/contract/currency_v4.odcs.yaml
```

Creates `training_dev.dev_yourname.currency_v4` using the configured personal schema.

### External tables

If a contract's schema object has `external: true`, the generated SQL includes a `LOCATION '${location}/<table_name>'` clause. The `DATABRICKS_LOCATION_<DATA_PRODUCT>` env var must be set or `contract:migrate` will error before running.

If `external: true` is absent, a managed table is created and `DATABRICKS_LOCATION_<DATA_PRODUCT>` is ignored.

### Contract schema conventions

| Field | Purpose | Example |
|-------|---------|---------|
| `format` | Spark table format | `delta` |
| `external: true` | Creates an external table with `LOCATION` | |
| `grants.select` | Users/groups granted `SELECT` | `- nick@capgroup.com` |

There is no `servers:` block — catalog, schema, and location are all injected at migrate time via env vars.

### Refreshing an expired token

OAuth mode (default): rerun `mise run setup:databricks` to refresh login/session if needed.  
PAT fallback mode only: rerun `mise run setup:databricks --pat`.

---

## CI Pipeline

On every PR, Harness:
1. Generates `flyway/migrations/<data_product>/V<version>__<table>.sql` for all contracts
2. Commits the SQL back to the branch (`chore: add generated migration SQL [skip ci]`)
3. Runs `flyway migrate` against the target environment with the pipeline's `FLYWAY_CATALOG`, `FLYWAY_LOCATION`, etc.

Developers never commit SQL directly — only the `.odcs.yaml` contract.

### Pipeline Variables per Environment

These Harness pipeline variables must be set when triggering a run. Values differ per environment:

| Variable | Description | Dev example | SQA/Prod |
|---|---|---|---|
| `DATABRICKS_WORKSPACE_URL` | Databricks workspace host | `https://cg-db-aa00003661-dev-us-east-1.cloud.databricks.com` | SQA/prod workspace URL |
| `FLYWAY_CATALOG` | Unity Catalog name | `training_dev` | `caspian_training_sqa` / `caspian_training_prd` |
| `FLYWAY_WAREHOUSE_ID` | SQL warehouse ID for Flyway | `a0e57263293aee36` | SQA/prod warehouse ID |
| `FLYWAY_TOKEN_SECRET` | Harness secret ID for the Databricks PAT | `..._DATABRICKS_TOKEN_DEV` | `..._DATABRICKS_TOKEN_SQA` / `..._PRD` |
| `FLYWAY_EXTERNAL_TABLE_BASE_PATH` | Base S3 path for external tables (leave empty if none) | `s3://datalake-curated-dev1-us-east-1/training_dev` | SQA/prod equivalent path |
| `FLYWAY_ENV_GRANT_PREFIX` | Environment-specific grant group prefix | `OZ_DEV` | `SNP_ATS` / `CPZ_PROD` |

The generated SQL never changes between environments — `${catalog}`, `${schema}`, `${location}`, and `${env_grant_prefix}` placeholders are substituted at migrate time by Flyway from the values above.

> **Note:** `FLYWAY_EXTERNAL_TABLE_BASE_PATH` is a single value per pipeline run. If different data products need different S3 base paths in the same environment, this will need to become per-data-product (same pattern as the local `DATABRICKS_LOCATION_<DATA_PRODUCT>` vars).

---

## Usage

### Import DDL to Contract

```bash
# Import as datacontract format from SQL DDL
uv run datacounsel import --format sql --source input/caspian_dev1.stnd_cdm_mfi.cdm_party_office_f1_v1_t0.sql --output contracts/stg/cdm_party_office_f1_v1_t0.datacontract.yaml

# Import from Unity Catalog (requires .env setup)
uv run datacounsel import --format unity --unity-table-full-name caspian_dev1.stnd_cdm_mfi.cdm_party_office_f1_v1_t0 --output contracts/stg/cdm_party_office_f1_v1_t0.datacontract.yaml
```

### Export DDL

```bash
# Standard SQL export
uv run datacounsel export --format sql contracts/caspian/stnd_cdm_mfi/cdm_party_office_f1_v1_t0.odcs.yaml

# Databricks SQL (with partition/location support)
uv run datacounsel export --format dbsql contracts/caspian/stnd_cdm_mfi/cdm_party_office_f1_v1_t0.odcs.yaml
```

### Lint Contracts

```bash
uv run datacounsel lint contracts/caspian/stnd_cdm_mfi/cdm_party_office_f1_v1_t0.odcs.yaml
```

### Test Against Databricks

```bash
uv run datacounsel test contracts/caspian/stnd_cdm_mfi/cdm_party_office_f1_v1_t0.odcs.yaml
```

## References

- [DataContract Spec](https://github.com/datacontract/datacontract-specification) | [Docs](https://datacontract.com/)
- [OpenDataContract (ODCS)](https://github.com/bitol-io/open-data-contract-standard) | [Docs](https://bitol-io.github.io/open-data-contract-standard/latest/)

## Notes

- DataContract spec doesn't support partitions ([#7](https://github.com/datacontract/datacontract-specification/issues/7)) or external locations
