# Job Task Times Out on Cold Start — Full Fix

## Symptoms to grep for

```
Cluster startup time
CLUSTER_REQUEST_LIMIT_EXCEEDED
cluster not ready
timeout waiting for cluster
Task timed out after
```

## Root cause

When a DAB job uses an on-demand job cluster (specified via `job_cluster_key`
in `databricks.yml`), every run provisions a fresh cluster. Cluster cold-start
typically takes 3–8 minutes. If the first task has a tight `timeout_seconds`,
it will expire before the cluster is ready.

## Diagnostic steps

1. In `databricks.yml`, check the task spec for the affected job:
   - `job_cluster_key` — on-demand cluster, subject to cold-start.
   - `existing_cluster_id` — attached to an existing all-purpose cluster,
     faster if cluster is already running.
   - `environment_key` with `client: "1"` — serverless Python compute,
     no cold-start.
2. Check `timeout_seconds` on the first task — if < 600, it may race against
   startup.

## Fix options (in order of preference)

### Option A — Switch to serverless Python compute (no cold-start)

```yaml
tasks:
  - task_key: dbt_run
    python_wheel_task:
      package_name: dbt_wrapper
      entry_point: main
    environment_key: serverless_env
environments:
  - environment_key: serverless_env
    spec:
      client: "1"
      dependencies:
        - dbt-databricks==1.8.7
```

### Option B — Add a low-cost pre-warm task

```yaml
tasks:
  - task_key: pre_warm
    spark_python_task:
      python_file: scripts/noop.py
    job_cluster_key: dbt_cluster
    timeout_seconds: 600

  - task_key: dbt_run
    depends_on:
      - task_key: pre_warm
    python_wheel_task:
      package_name: dbt_wrapper
      entry_point: main
    job_cluster_key: dbt_cluster
    timeout_seconds: 3600
```

### Option C — Raise timeout_seconds

Raise `timeout_seconds` on the first task to accommodate cluster startup
(minimum 900 seconds when using on-demand clusters).

See `/databricks-jobs` for cluster spec configuration details.
See `/databricks-docs` to fetch the official Databricks Jobs API reference.
See `/databricks-execution-compute` for compute type trade-offs.
