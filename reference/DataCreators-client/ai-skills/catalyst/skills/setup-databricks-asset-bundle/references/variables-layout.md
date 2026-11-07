# Variables layout

Files under `data_products/<product>/variables/`:

```
variables/
├── variables.yml             # declarations (with defaults)
├── variables_dev.yml         # scaffold for the dev environment
├── variables_sqa.yml         # scaffold for the sqa environment
├── variables_prd.yml         # scaffold for the prd environment
└── clusters.yml              # complex cluster-shape variables
```

The bundle loads `variables.yml` + `clusters.yml` via the top-level
`include:`. Per-env values that actually feed `databricks bundle deploy`
live inline in `databricks.yml#targets.<env>.variables:`; the
`variables_<env>.yml` files mirror those values as reference scaffolding
for each real environment but are not loaded by the bundle (the DAB
schema rejects per-target `include:` —
`config.Target.additionalProperties: false`).

## `variables.yml` — declarations

Every variable the bundle references **must** be declared here, even if
its value comes from a per-env file. The declaration carries the
`description:` (visible in `databricks bundle validate`) and the default.

The real repo declares ~30 variables. Categories:

| Category | Variables |
|---|---|
| Identity / project | `env`, `project_name`, `project_team`, `atm_id`, `app_name`, `data_product_name` |
| Compute references | `cluster_id`, `sql_warehouse_id`, `instance_pools`, `compute_policy_id` |
| Spark / runtime | `databricks_runtime_spark_version`, `root_path`, `shared_init_scripts_location` |
| dbt + SQL | `http_path`, `default_catalog`, `default_schema`, `target_schema`, `checkpoint_table`, `dbt_state_path` |
| Caspian / domain | `caspian_catalog`, `app_catalog`, `domain_catalog` |
| DQF / Deequ | `dev_test_mode`, `deequ_jar_path` |
| Kafka / data-ready | `zone_bucket`, `data_notify_topic`, `kafka_secret_scope` (deprecated), `kafka_secret_arn`, `rootca_secret_arn`, `bootstrap_brokers`, `schema_registry_url`, `aws_region` |
| Misc | `git_branch` |

Defaults skew "dev" — `app_catalog: caspian_ig_dev`, `checkpoint_table`
pointing at `caspian_ig_dev.…`. Production overrides come from
`databricks.yml#targets.prd.variables:` inline.

**`dbt_state_path` default**: the bundle-wide default is a UC Volume
(`/Volumes/${var.app_catalog}/cspn_sys/dbt_state`) matching the real
repo, so dbt artifacts (partial_parse, run_results, manifest) survive
across runs. The `local` target overrides this to a per-user UC Volume
subpath (`/Volumes/${var.app_catalog}/cspn_sys/dbt_state/zz_${workspace.current_user.short_name}`)
so concurrent local deploys on a shared cluster don't collide. `/tmp`-based
paths don't work on shared clusters — the dir is owned by whichever user
ran first, and `os.makedirs()` fails with `PermissionError`.

### Complex variables

Cluster shapes are declared with `type: complex` so they can hold a full
nested mapping. The bundle references them as `${var.small_cluster}` etc.

```yaml
small_cluster:
  description: "Small autoscaling cluster"
  type: complex
  default:
    spark_version: ...
    node_type_id: ...
    autoscale: { ... }
    init_scripts: [...]
```

This isolates cluster sizing from per-dataset job definitions — every job
that needs the same shape references the same variable.

## Per-target overrides — `databricks.yml#targets.<env>.variables:`

Each target carries a full `variables:` block with env-specific values.
Example (`dev`):

```yaml
targets:
  dev:
    workspace:
      host: "https://{{DEV_WORKSPACE_HOST}}"
      root_path: /Workspace/${var.project_name}/${var.app_name}/.bundle/${bundle.name}/${bundle.target}
    variables:
      env: dev
      sql_warehouse_id: "{{DEV_SQL_WAREHOUSE_ID}}"
      kafka_secret_scope: "{{DEV_KAFKA_SECRET_SCOPE}}"
      app_catalog: "{{DEV_APP_CATALOG}}"
      target_schema: ${workspace.current_user.short_name}
      ...
```

Deploy command:

```
databricks bundle deploy --target dev
```

DR variants override `workspace.host` (different region) and
`app_catalog` / `target_schema` (DR-scoped), repeating their base env's
other values inline.

## `clusters.yml` — cluster shapes

Defines reusable cluster shapes as complex vars. Today the real repo has
two:

| Variable | Purpose | Used by |
|---|---|---|
| `small_cluster` | Standard autoscaling cluster for dbt-style workloads | (Available for jobs that need their own cluster) |
| `dqf_cluster` | Single-node Deequ DQ cluster | `<dataset>_dq.job.yml` `job_clusters` block |

### What's *in* each cluster shape

- `spark_version` — pinned to LTS (`15.4.x-scala2.12`). DBX-BUNDLE-009.
- `spark_env_vars` — `PROJECT_HOME`, `PYTHONPATH` rooted at `${var.root_path}`, dbt env vars, CA bundle paths for HTTPS to internal services.
- `policy_id` — `${var.compute_policy_id}` (per-env).
- `node_type_id` — currently `m7gd.large` inline. DBX-BUNDLE-004 says move to a shared compute.yml org-wide; deferred today.
- `autoscale` / `num_workers` — per shape.
- `data_security_mode` — `SINGLE_USER` for both today.
- `init_scripts` — point at `install_requirements.sh` / `install_dqf_requirements.sh` under the product's `init_scripts/` directory.

### Adding a new cluster shape

1. Declare a new top-level variable in `clusters.yml` with `type: complex`.
2. Reference it from jobs that need it: `new_cluster: ${var.your_shape}`.
3. Avoid one-off per-job cluster definitions — the variable indirection
   is what makes cluster sizing changes a single-file edit.

## Anti-patterns

- **Don't** inline `node_type_id` / `autoscale` in a `*.job.yml`.
  Reference a complex var from `clusters.yml` instead.
- **Don't** declare new variables in `variables_<env>.yml` or
  `targets.<env>.variables:` — those only override. The declaration
  belongs in `variables.yml`.
- **Don't** scatter SQL warehouse IDs across multiple variables. The
  bundle uses `sql_warehouse_id` (with `http_path` as the URL form) for
  the dbt task; downstream skills read those by name.
