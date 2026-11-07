# dbt Project Setup — Domain-Aligned

Generate `dbt_project.yml` and `profiles.yml` for the domain-aligned canonical model project.

## dbt_project.yml

```yaml
name: '<model_name>_domain'
version: '1.0.0'
config-version: 2
profile: 'domain_databricks'

model-paths: ["models"]
macro-paths: ["macros"]

models:
  <model_name>_domain:
    staging:
      +materialized: view
    intermediate:
      +materialized: view
    canonical:
      +materialized: incremental
      +file_format: delta
      +incremental_strategy: merge
```

## profiles.yml

```yaml
domain_databricks:
  target: dev
  outputs:
    dev:
      type: databricks
      catalog: "{{ env_var('DATABRICKS_DEFAULT_CATALOG') }}"
      schema: "{{ env_var('DATABRICKS_DEFAULT_SCHEMA') }}"
      host: "{{ env_var('DATABRICKS_HOST') }}"
      http_path: "{{ env_var('DATABRICKS_HTTP_PATH', '/sql/1.0/warehouses/' + env_var('DATABRICKS_WAREHOUSE_ID', '')) }}"
      auth_type: oauth                                    # SQL-DBSQL-001 + DBX-SEC-002
      client_id: "{{ env_var('DBX_CLIENT_ID') }}"         # service principal
      client_secret: "{{ env_var('DBX_CLIENT_SECRET') }}"
      threads: 4
```

> Note: this example previously used `token: env_var('DATABRICKS_TOKEN')` which conflated user-PAT with SP-PAT. The updated pattern uses OAuth M2M (preferred); see `/setup-dbt-project` for the SP-PAT commented fallback and the user-PAT detection example.

## Rules

1. **Project name:** `<model_name>_domain` (lowercase, underscores)
2. **Profile name:** `domain_databricks`
3. **All credentials via env_var()** — never hardcode
4. **Model materialization defaults:**
   - staging → view
   - intermediate → view
   - canonical → incremental (merge strategy, delta format)
