# DQ jobs — Deequ verification

Every dataset gets a companion `<dataset>_dq.job.yml` that runs Deequ
data-quality checks against the dataset's produced tables. Separate
job by design — DQ is a sibling concern to the dbt build, orchestrated
by Airflow rather than chained inline.

## Anatomy

```yaml
resources:
  jobs:
    <dataset>_dq_job:
      name: <dataset>_dq_job
      # No email_notifications block: failure alerting is platform-side (Astronomer Datadog)
      tasks:
        - task_key: deequ_verify_task
          notebook_task:
            notebook_path: ${workspace.root_path}/files/data_products/${var.data_product_name}/datasets/<dataset>/runtime/dq_verify
            base_parameters:
              application_name: caspian-im-foundation
              dataset_name: <ruleset-dataset-name>
              ruleset_name: <ruleset-name>
              rule_group: Daily
              schema: "caspian_${var.env}.curated_ref"
              table: "<dataset>"
              env: ${var.env}
              default_catalog: ${var.default_catalog}
              default_schema: ${var.default_schema}
          libraries:
            - jar: ${var.deequ_jar_path}
          job_cluster_key: job_cluster

      job_clusters:
        - job_cluster_key: job_cluster
          new_cluster: ${var.dqf_cluster}
```

## Pieces

### `notebook_task` over `spark_python_task`

DQ jobs run a notebook (`runtime/dq_verify` under the dataset folder)
because Deequ's API surface is easier to drive interactively when
authors are tuning rules. The notebook reads `base_parameters` at run
time.

### `libraries.jar`

The Deequ JAR ships as a UC Volume artifact, referenced via
`${var.deequ_jar_path}` (declared in `variables.yml`). The default:

```
/Volumes/${var.default_catalog}/${var.default_schema}/dqf_libs/deequ-2.0.16-spark-3.5.jar
```

The JAR's version is pinned to a known-good build; bump it as a paired
change to `variables.yml`.

### `job_cluster_key: job_cluster` + `dqf_cluster`

DQ jobs run on a single-node ephemeral cluster (the `dqf_cluster` complex
var). Why single-node:

- Deequ's verification API doesn't benefit from cluster parallelism for
  most DQ rule sets.
- Isolation matters — a poisoned cluster from DQ shouldn't affect dbt.
- Cost scales with verification frequency, not size.

The `dqf_cluster` complex var (in `clusters.yml`) sets
`spark.master: local[*]` + `spark.databricks.cluster.profile: singleNode`
and a `custom_tags.ResourceClass: SingleNode` tag.

### `base_parameters`

The notebook reads these via dbutils. Required:

| Key | Source / convention |
|---|---|
| `application_name` | Constant per product family (e.g. `caspian-im-foundation`) |
| `dataset_name` | Deequ ruleset's `dataset_name` field. Usually `cspn_<dataset>_v<n>_base` |
| `ruleset_name` | Deequ ruleset identifier. Usually `cspn_dim_<dataset>_v<n>_base` |
| `rule_group` | `Daily` / `Hourly` / `Weekly` — selects a subset of rules from the ruleset |
| `schema` | Target schema, env-templated: `"caspian_${var.env}.curated_ref"` |
| `table` | The dataset table name |
| `env` | `${var.env}` |
| `default_catalog` / `default_schema` | `${var.default_catalog}` / `${var.default_schema}` |

## Notebook existence check at emit time

The DQ job's `notebook_task.notebook_path` resolves to
`${workspace.root_path}/files/data_products/<product>/datasets/<dataset>/runtime/dq_verify`,
which maps back to the local path
`data_products/<product>/datasets/<dataset>/runtime/dq_verify.py` once
the bundle syncs. **The skill checks for that file at emit time**:

- File **exists**: emit `<dataset>_dq.job.yml` normally.
- File **missing**: emit the YAML with a `# TODO: author runtime/dq_verify.py before deploy` marker at the top, and surface a loud warning in the Step 6 handoff list.

Why this check matters: `databricks bundle validate` will parse the job
YAML successfully even when the notebook file is missing —
`notebook_path` is just a string at parse time. The failure only
surfaces at `databricks bundle deploy` (workspace path resolution).
Catching it at emit time means the author sees the gap immediately
instead of after a CI deploy step.

## What this template does *not* own

- The DQ rules themselves — those live in a separate ruleset repository
  / catalog. The notebook just executes them.
- The DQ notebook's source — it lives under the dataset's
  `runtime/dq_verify.py`. The skill emits the job YAML and warns when
  the notebook source is absent, but it doesn't author the notebook
  itself.
- Failure-routing (alerting on DQ failure) — same model as the main job:
  Airflow's DAG-level callback handles human escalation, so pipeline DAB
  jobs intentionally omit `email_notifications.on_failure`.
