# Compose Contract with /setup-databricks-asset-bundle

Every emitted DAG invokes a Databricks job. The job is deployed by the
Databricks Asset Bundle that `/setup-databricks-asset-bundle` emits. The
DAG's `job_name` must match the bundle's deployed job name exactly.

This reference documents how `/generate-dag` discovers the job name from
bundle artifacts so the two skills compose without manual coordination.

## The contract

`/setup-databricks-asset-bundle` writes, per dataset:

```yaml
# data_products/<product>/datasets/<dataset>/bundle/<dataset>.job.yml
resources:
  jobs:
    <dataset>_job:
      name: "${var.databricks_job_prefix}<dataset>_job"
      tasks:
        - task_key: deps
          spark_python_task:
            python_file: "../python/<pkg>/main.py"
            parameters: ["deps"]
        - task_key: run
          depends_on: [{task_key: deps}]
          spark_python_task: ...
        - task_key: test
          depends_on: [{task_key: run}]
          spark_python_task: ...
```

`/generate-dag` discovers from this file:

| Discovered | Source line | Used as |
|---|---|---|
| Resource key | `<dataset>_job:` | Internal reference |
| Rendered job name | `name: "${var.databricks_job_prefix}<dataset>_job"` | DAG's `job_name:` field |
| Task chain | `tasks: [deps, run, test]` | DAG could split into sub-tasks (optional; default is single-task DatabricksRunNowOperator wrapping the whole job) |

The DAG references the rendered name via Airflow Variable templating:

```yaml
# In the emitted DAG:
job_name: "{{ var.value.databricks_job_prefix }}<dataset>_job"
```

Variable `databricks_job_prefix` is set per environment in
`variables/variables_<env>.yml` (e.g., `dev-`, `qa-`, `prd-`).

## Discovery flow (concrete walk-through)

Given a target `data_products/client_positions/`:

### 1. Read `databricks.yml`

```bash
cat data_products/client_positions/databricks.yml
```

Returns:

```yaml
bundle:
  name: client_positions
variables:
  databricks_job_prefix:
    default: ""
targets:
  dev:
    variables:
      databricks_job_prefix: "dev-positions-"
  prd:
    variables:
      databricks_job_prefix: "prd-positions-"
```

Note: targets dev/prd available with respective prefixes.

### 2. Read per-dataset bundle artifact

For dataset `daily_positions`:

```bash
cat data_products/client_positions/datasets/daily_positions/bundle/daily_positions.job.yml
```

Returns:

```yaml
resources:
  jobs:
    daily_positions_job:
      name: "${var.databricks_job_prefix}daily_positions_job"
      tasks: [...]
```

Resource key: `daily_positions_job`. Rendered name pattern:
`<prefix>daily_positions_job`. In dev: `dev-positions-daily_positions_job`.

### 3. Read per-env variables

```bash
cat data_products/client_positions/variables/variables_dev.yml
cat data_products/client_positions/variables/variables_prd.yml
```

Confirm `databricks_job_prefix` is set in each. If missing or set to `""`,
flag in the emitted DAG with an advisory comment.

### 4. Emit DAG with templated job_name

```yaml
tasks:
  run_databricks_job:
    operator: airflow.providers.databricks.operators.databricks.DatabricksRunNowOperator
    databricks_conn_id: "{{ conn.databricks_default.conn_id }}"
    job_name: "{{ var.value.databricks_job_prefix }}daily_positions_job"
```

At runtime: Airflow substitutes `var.value.databricks_job_prefix` per
the deployed env, producing `dev-positions-daily_positions_job` in dev.

This matches what `databricks bundle deploy --target dev` actually pushed
to Databricks.

## Without a bundle — mode behaviour

If `databricks.yml` is absent or has no entry for the requested dataset:

### `production` mode → STOP

Skill refuses to emit. Report:

> No `databricks.yml` found at `data_products/<product>/`, or the bundle
> has no job for dataset `<dataset>`. Run `/setup-databricks-asset-bundle`
> first, or point me at an existing job in the workspace.

### `prototype` mode → emit with placeholder

```yaml
tasks:
  run_databricks_job:
    job_name: "{{ var.value.databricks_job_prefix }}<dataset>_job  # TODO: confirm job name when bundle is deployed"
```

Advisory comment at the top of the file:

```yaml
# TODO: This DAG was emitted in prototype mode without a deployed bundle.
# Run /setup-databricks-asset-bundle for this dataset before deploying
# this DAG to a runtime environment, then re-run /generate-dag in
# production mode to remove this advisory.
```

### `lift-and-shift` mode → preserve existing

If the team already has a DAG that references a different job name (e.g.,
the bundle convention has drifted), preserve the existing `job_name` and
flag the divergence in a comment:

```yaml
job_name: "<existing-job-name>"  # WARNING: this name does not match the bundle convention; reconcile before promoting
```

## Why composition matters

Without this contract:

- DAG says `job_name: dev_orders_job`; bundle deployed `dev_orders_pipeline_job`. Silent 404 on first run. No validator catches it.
- DAG points at connection name the team doesn't have. Run fails on first deploy.
- DAG hard-codes prefixes that the bundle parametrized. Cannot promote between envs without manual edits.

With this contract:

- Skill reads bundle output and emits matching DAG.
- Fail-fast when no bundle exists in `production` mode.
- Templated variables let the same DAG promote across dev/qa/sqa/prd.
