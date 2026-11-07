# Run Databricks — Domain-Aligned

Execute the generated dbt models against a Databricks SQL warehouse to validate the canonical model.

## Prerequisites

1. `.env` file with Databricks credentials:
   - `DATABRICKS_HOST`
   - `DATABRICKS_TOKEN`
   - `DATABRICKS_WAREHOUSE_ID` or `DATABRICKS_HTTP_PATH`
   - `DATABRICKS_DEFAULT_CATALOG`
   - `DATABRICKS_DEFAULT_SCHEMA`

2. Generated dbt project at `workspace/generated/domain-aligned/<model>/dbt/`

3. Source tables must be accessible from the configured warehouse

## Execution Steps

1. **Copy macro overrides** from `skills/domain-aligned/templates/dbt_project/macros/` into the generated project's `macros/` directory
2. **Set environment variables** from `.env`
3. **Run `dbt deps`** (only if `packages.yml` exists)
4. **Run `dbt run --select +<model>`** to execute all models in dependency order
5. **Run `dbt test --select +<model>`** to validate data quality
6. **Generate Databricks report** with:
   - Row counts per model
   - Sample rows from canonical model (LIMIT 10)
   - Test results summary
   - Any warnings or errors

## Error Recovery

| Error | Recovery |
|-------|----------|
| Source table not found | Verify catalog/schema in `.env` and source definitions |
| Column type mismatch | Check staging model CASTs match source column types |
| Permission denied | Verify token has access to source catalog and target schema |
| Warehouse not running | Start warehouse or switch to an active one |

## Report Format

```markdown
# Databricks Report: <model_name>

## Execution Summary
- **Status:** SUCCESS / FAILED
- **Models run:** N
- **Tests passed:** N/N

## Row Counts
| Model | Rows |
|-------|------|
| stg_<vendor1>_<entity> | ... |
| stg_<vendor2>_<entity> | ... |
| int_<model>_union | ... |
| <model> | ... |

## Sample Data (canonical model)
<first 10 rows>

## Test Results
<pass/fail summary>
```
