---
name: databricks-jobs
description: |
  Use this skill proactively for ANY Databricks Jobs task - creating, listing, running, updating,
  or deleting jobs. Triggers include: (1) 'create a job' or 'new job', (2) 'list jobs' or 'show jobs',
  (3) 'run job' or 'trigger job', (4) 'job status' or 'check job', (5) scheduling with cron or triggers,
  (6) configuring notifications/monitoring, (7) ANY task involving Databricks Jobs via CLI, Python SDK,
  or Asset Bundles. ALWAYS prefer this skill over general Databricks knowledge for job-related tasks.
  Catalyst trigger phrases: "configure a Databricks job", "set up job.yml", "wire up Databricks scheduling".
allowed-tools: Read Bash Write Edit
metadata:
  tier: capability
  lifecycle-phase: cross-cutting
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
  standards:
    - DBX-WORKFLOW-001
    - DBX-WORKFLOW-002
    - DBX-WORKFLOW-005
  upstream-source: databricks-solutions/ai-dev-kit/databricks-skills/databricks-jobs
  upstream-commit: 8cb4456543d6413e8a12923d4d4b5394fea89b25
  upstream-license: Databricks (custom — see third-party/LICENSE-databricks.md)
  catalyst-modifications: |
    Modified by Capital Group on 2026-05-14:
    - dropped MCP tool references (Catalyst policy)
    - added metadata.standards citations (RFD 0008)
    - added Catalyst trigger phrases in description
---

> _Modified from `databricks-solutions/ai-dev-kit/databricks-skills/databricks-jobs` by Capital Group on 2026-05-14. See `metadata.catalyst-modifications` for the change set._

# Databricks Lakeflow Jobs

## Overview

Databricks Jobs orchestrate data workflows with multi-task DAGs, flexible triggers, and comprehensive monitoring. Jobs support diverse task types and can be managed via Python SDK, CLI, or Asset Bundles.

## Reference Files

| Use Case | Reference File |
|----------|----------------|
| Configure task types (notebook, Python, SQL, dbt, etc.) | [references/task-types.md](references/task-types.md) |
| Set up triggers and schedules | [references/triggers-schedules.md](references/triggers-schedules.md) |
| Configure notifications and health monitoring | [references/notifications-monitoring.md](references/notifications-monitoring.md) |
| Complete working examples | [references/examples.md](references/examples.md) |

## Quick Start

### Python SDK

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import Task, NotebookTask, Source

w = WorkspaceClient()

job = w.jobs.create(
    name="my-etl-job",
    tasks=[
        Task(
            task_key="extract",
            notebook_task=NotebookTask(
                notebook_path="/Workspace/Users/user@example.com/extract",
                source=Source.WORKSPACE
            )
        )
    ]
)
print(f"Created job: {job.job_id}")
```

### CLI

```bash
databricks jobs create --json '{
  "name": "my-etl-job",
  "tasks": [{
    "task_key": "extract",
    "notebook_task": {
      "notebook_path": "/Workspace/Users/user@example.com/extract",
      "source": "WORKSPACE"
    }
  }]
}'
```

### Asset Bundles (DABs)

```yaml
# resources/jobs.yml
resources:
  jobs:
    my_etl_job:
      name: "[${bundle.target}] My ETL Job"
      tasks:
        - task_key: extract
          notebook_task:
            notebook_path: ../src/notebooks/extract.py
```

## Core Concepts

### Multi-Task Workflows

Jobs support DAG-based task dependencies:

```yaml
tasks:
  - task_key: extract
    notebook_task:
      notebook_path: ../src/extract.py

  - task_key: transform
    depends_on:
      - task_key: extract
    notebook_task:
      notebook_path: ../src/transform.py

  - task_key: load
    depends_on:
      - task_key: transform
    run_if: ALL_SUCCESS  # Only run if all dependencies succeed
    notebook_task:
      notebook_path: ../src/load.py
```

**run_if conditions:**
- `ALL_SUCCESS` (default) - Run when all dependencies succeed
- `ALL_DONE` - Run when all dependencies complete (success or failure)
- `AT_LEAST_ONE_SUCCESS` - Run when at least one dependency succeeds
- `NONE_FAILED` - Run when no dependencies failed
- `ALL_FAILED` - Run when all dependencies failed
- `AT_LEAST_ONE_FAILED` - Run when at least one dependency failed

### Task Types Summary

| Task Type | Use Case | Reference |
|-----------|----------|-----------|
| `notebook_task` | Run notebooks | [references/task-types.md#notebook-task](references/task-types.md#notebook-task) |
| `spark_python_task` | Run Python scripts | [references/task-types.md#spark-python-task](references/task-types.md#spark-python-task) |
| `python_wheel_task` | Run Python wheels | [references/task-types.md#python-wheel-task](references/task-types.md#python-wheel-task) |
| `sql_task` | Run SQL queries/files | [references/task-types.md#sql-task](references/task-types.md#sql-task) |
| `dbt_task` | Run dbt projects | [references/task-types.md#dbt-task](references/task-types.md#dbt-task) |
| `pipeline_task` | Trigger DLT/SDP pipelines | [references/task-types.md#pipeline-task](references/task-types.md#pipeline-task) |
| `spark_jar_task` | Run Spark JARs | [references/task-types.md#spark-jar-task](references/task-types.md#spark-jar-task) |
| `run_job_task` | Trigger other jobs | [references/task-types.md#run-job-task](references/task-types.md#run-job-task) |
| `for_each_task` | Loop over inputs | [references/task-types.md#for-each-task](references/task-types.md#for-each-task) |

### Trigger Types Summary

| Trigger Type | Use Case | Reference |
|--------------|----------|-----------|
| `schedule` | Cron-based scheduling | [references/triggers-schedules.md#cron-schedule](references/triggers-schedules.md#cron-schedule) |
| `trigger.periodic` | Interval-based | [references/triggers-schedules.md#periodic-trigger](references/triggers-schedules.md#periodic-trigger) |
| `trigger.file_arrival` | File arrival events | [references/triggers-schedules.md#file-arrival-trigger](references/triggers-schedules.md#file-arrival-trigger) |
| `trigger.table_update` | Table change events | [references/triggers-schedules.md#table-update-trigger](references/triggers-schedules.md#table-update-trigger) |
| `continuous` | Always-running jobs | [references/triggers-schedules.md#continuous-jobs](references/triggers-schedules.md#continuous-jobs) |

## Compute Configuration

### Job Clusters (Recommended)

Define reusable cluster configurations:

```yaml
job_clusters:
  - job_cluster_key: shared_cluster
    new_cluster:
      spark_version: "15.4.x-scala2.12"
      node_type_id: "i3.xlarge"
      num_workers: 2
      spark_conf:
        spark.speculation: "true"

tasks:
  - task_key: my_task
    job_cluster_key: shared_cluster
    notebook_task:
      notebook_path: ../src/notebook.py
```

### Autoscaling Clusters

```yaml
new_cluster:
  spark_version: "15.4.x-scala2.12"
  node_type_id: "i3.xlarge"
  autoscale:
    min_workers: 2
    max_workers: 8
```

### Existing Cluster

```yaml
tasks:
  - task_key: my_task
    existing_cluster_id: "0123-456789-abcdef12"
    notebook_task:
      notebook_path: ../src/notebook.py
```

### Serverless Compute

For notebook and Python tasks, omit cluster configuration to use serverless:

```yaml
tasks:
  - task_key: serverless_task
    notebook_task:
      notebook_path: ../src/notebook.py
    # No cluster config = serverless
```

## Job Parameters

### Define Parameters

```yaml
parameters:
  - name: env
    default: "dev"
  - name: date
    default: "{{start_date}}"  # Dynamic value reference
```

### Access in Notebook

```python
# In notebook
dbutils.widgets.get("env")
dbutils.widgets.get("date")
```

### Pass to Tasks

```yaml
tasks:
  - task_key: my_task
    notebook_task:
      notebook_path: ../src/notebook.py
      base_parameters:
        env: "{{job.parameters.env}}"
        custom_param: "value"
```

## Common Operations

### Python SDK Operations

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# List jobs
jobs = w.jobs.list()

# Get job details
job = w.jobs.get(job_id=12345)

# Run job now
run = w.jobs.run_now(job_id=12345)

# Run with parameters
run = w.jobs.run_now(
    job_id=12345,
    job_parameters={"env": "prod", "date": "2024-01-15"}
)

# Cancel run
w.jobs.cancel_run(run_id=run.run_id)

# Delete job
w.jobs.delete(job_id=12345)
```

### CLI Operations

```bash
# List jobs
databricks jobs list

# Get job details
databricks jobs get 12345

# Run job
databricks jobs run-now 12345

# Run with parameters
databricks jobs run-now 12345 --job-params '{"env": "prod"}'

# Cancel run
databricks jobs cancel-run 67890

# Delete job
databricks jobs delete 12345
```

### Asset Bundle Operations

```bash
# Validate configuration
databricks bundle validate

# Deploy job
databricks bundle deploy

# Run job
databricks bundle run my_job_resource_key

# Deploy to specific target
databricks bundle deploy -t prod

# Destroy resources
databricks bundle destroy
```

## Permissions (DABs)

```yaml
resources:
  jobs:
    my_job:
      name: "My Job"
      permissions:
        - level: CAN_VIEW
          group_name: "data-analysts"
        - level: CAN_MANAGE_RUN
          group_name: "data-engineers"
        - level: CAN_MANAGE
          user_name: "admin@example.com"
```

**Permission levels:**
- `CAN_VIEW` - View job and run history
- `CAN_MANAGE_RUN` - View, trigger, and cancel runs
- `CAN_MANAGE` - Full control including edit and delete

## Common Issues

| Issue | Solution |
|-------|----------|
| Job cluster startup slow | Use job clusters with `job_cluster_key` for reuse across tasks |
| Task dependencies not working | Verify `task_key` references match exactly in `depends_on` |
| Schedule not triggering | Check `pause_status: UNPAUSED` and valid timezone |
| File arrival not detecting | Ensure path has proper permissions and uses cloud storage URL |
| Table update trigger missing events | Verify Unity Catalog table and proper grants |
| Parameter not accessible | Use `dbutils.widgets.get()` in notebooks |
| "admins" group error | Cannot modify admins permissions on jobs |
| Serverless task fails | Ensure task type supports serverless (notebook, Python) |

## Related Skills

- **[databricks-bundles](../databricks-bundles/SKILL.md)** - Deploy jobs via Databricks Asset Bundles
- **[databricks-spark-declarative-pipelines](../databricks-spark-declarative-pipelines/SKILL.md)** - Configure pipelines triggered by jobs

## Resources

- [Jobs API Reference](https://docs.databricks.com/api/workspace/jobs)
- [Jobs Documentation](https://docs.databricks.com/en/jobs/index.html)
- [DABs Job Task Types](https://docs.databricks.com/en/dev-tools/bundles/job-task-types.html)
- [Bundle Examples Repository](https://github.com/databricks/bundle-examples)
