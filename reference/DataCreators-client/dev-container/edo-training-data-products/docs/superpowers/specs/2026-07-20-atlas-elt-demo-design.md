# Atlas ELT Demo Data Product Design

## Objective
Build `data_products/atlas_elt_demo` so it emulates `asset_reference_data` structure and required artifact types while using Atlas entities/data from `dpc-academy` instead of currency/geography content.

## Scope
### In scope
- Mirror product-level structure used by `asset_reference_data` for a full data product shell.
- Create dataset folders named after Atlas entities:
  - `trades`
  - `instruments`
  - `portfolios`
  - `clients`
  - `advisors`
  - `funds`
  - `fund_holdings`
- For each dataset, include the same artifact categories as existing products:
  - `airflow/`
  - `bundle/`
  - `contract/`
  - `dbt/`
  - `runtime/`
  - migration doc pattern (`cspn_migration.md`)
- Keep dbt runnable in the current devcontainer/Databricks flow.

### Out of scope
- Adding currency/geography datasets to `atlas_elt_demo`.
- Reworking platform-wide loaders or existing non-demo data products.

## Target Structure
`atlas_elt_demo` will include the product-level files/directories expected in existing products (for example `databricks.yml`, `variables/`, init/runtime dependencies, and dbt profile/project files), then per-dataset artifact trees for Atlas-named datasets.

This follows the same structural contract as `asset_reference_data`, but replaces dataset domain content with Atlas entities from `dpc-academy`.

## Data and Model Design
- Seed/source data comes from Atlas entities (`trades`, `instruments`, `portfolios`, `clients`, `advisors`, `funds`, `fund_holdings`).
- dbt models use the established layering pattern (bronze/silver/gold) adapted to Atlas entities.
- `datasets/sources.yml` is aligned to Atlas source objects so generated models and contracts are consistent.

## Orchestration and Deployment Artifacts
- A Databricks Asset Bundle definition exists at product level and dataset-level bundle artifacts exist per Atlas dataset, matching existing conventions.
- Airflow DAG definitions exist per dataset using existing naming/layout conventions.
- ODCS contract files exist per dataset and map to Atlas-shaped outputs.

## Error Handling
- Reuse existing repository conventions for failing fast on unresolved paths or bad references.
- Do not add silent fallbacks for missing dataset artifacts.

## Validation Criteria
1. `atlas_elt_demo` contains all required structural artifact categories used by `asset_reference_data`.
2. All seven Atlas dataset folders exist with required sub-artifacts.
3. dbt dependency install and representative dbt execution path complete successfully in devcontainer.
4. No geography/currency dataset content is introduced into `atlas_elt_demo`.

## Implementation Notes
- Favor copying and adapting existing working templates from `asset_reference_data` for structural parity.
- Keep changes localized to `atlas_elt_demo` and associated tests/loader references needed for discoverability.
