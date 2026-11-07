# Per-dataset jobs

Each dataset under `data_products/<product>/datasets/<dataset>/` gets a
`bundle/` directory holding **two** job YAMLs:

| File | Purpose |
|---|---|
| `<dataset>.job.yml` | Main dbt-run job — invokes `dbt_wrapper.py deps_then_run` against the dataset's selected models |
| `<dataset>_dq.job.yml` | Deequ DQ verification job (see `dq-jobs.md`) |

The `include: datasets/**/bundle/*.yml` glob in `databricks.yml` picks
both up automatically.

## Main job (`<dataset>.job.yml`) — anatomy

```yaml
resources:
  jobs:
    <dataset>_job:
      name: <dataset>_job                              # literal today (see DBX-DAB-001 deferral)
      # No email_notifications block: failure alerting is platform-side (Astronomer Datadog)
      tasks:
        - task_key: dbt_run
          spark_python_task:
            python_file: ${workspace.root_path}/files/dbt_wrapper.py
            parameters: [deps_then_run, --debug, run, --project-dir, ..., --select, +<dataset>+, ...]
          existing_cluster_id: ${var.cluster_id}   # DBX-DAB-005 — by var, not inline
```

Single-task design on purpose. `deps_then_run` is a `dbt_wrapper.py`
mode that runs `dbt deps` and `dbt run` back-to-back in the same Python
process; no need to model them as two Airflow / DAB tasks.

### `--select` pattern

The wrapper passes `--select +<dataset>+` (the `+` on both sides means
"this dataset's models plus everything upstream plus everything
downstream"). For a dataset that should *only* build its own models, use
`--select <dataset>`. For staging/intermediate splits, the `<dataset>+`
or `+<dataset>` half-graphs work.

### Compute

`existing_cluster_id: ${var.cluster_id}` — a long-lived shared
cluster, identified by Airflow / a separate process. The bundle never
owns the cluster lifecycle.

When a dataset needs an isolated job cluster instead, swap to:

```yaml
job_clusters:
  - job_cluster_key: this_job
    new_cluster: ${var.small_cluster}
tasks:
  - task_key: dbt_run
    job_cluster_key: this_job
    spark_python_task: { ... }
```

Reference `${var.small_cluster}` (or another shape from `clusters.yml`)
rather than inlining a `new_cluster:` body.

### Variable-driven dbt vars

The wrapper takes a `--vars` JSON-ish argument. The real repo passes:

```
{
  catalog: '${var.app_catalog}',
  schema: '${var.target_schema}',
  target_schema: '${var.target_schema}',
  http_path: '${var.http_path}',
  checkpoint_table: '${var.checkpoint_table}',
  app_catalog: '${var.app_catalog}',
  caspian_catalog: '${var.caspian_catalog}',
  domain_catalog: '${var.domain_catalog}'
}
```

The skill emits this verbatim with placeholders interpolated at write
time — keeps the same vars regardless of dataset so dbt models can
depend on a stable set.

## DQ companion (`<dataset>_dq.job.yml`)

See `dq-jobs.md` for the full anatomy. Summary: notebook task with
Deequ JAR library, runs on an ephemeral `dqf_cluster` job cluster, takes
ruleset / schema / table params for the dataset.

## Multi-task jobs (when needed)

The default is single-task. If a dataset legitimately needs multiple
tasks (e.g. a pre-process step before dbt, or an explicit `dbt test`
phase), add them under `tasks:` with `depends_on:`. Keep each task
single-purpose; don't pack two dbt operations into one `parameters` list.

## What this template does *not* own

- Cluster sizing — that's `clusters.yml` via complex vars.
- Variable defaults — that's `variables.yml`.
- Schedule / trigger — Airflow owns scheduling (per RFD 0011). The DAB
  job doesn't declare a `trigger:` block; Airflow calls it via
  `DatabricksRunNowOperator`.
- Human-facing alerting — provided platform-side by Astronomer's Datadog
  integration (not a DAG `on_failure_callback`); pipeline DAB jobs intentionally
  omit `email_notifications.on_failure` to avoid duplicate channels.
- Tags / permissions — see DBX-BUNDLE-007 / 008 deferrals in
  `rfd-0012-citations.md`.
