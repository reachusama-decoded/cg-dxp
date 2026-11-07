# Compute model

Three compute shapes appear in the real DABs:

| Shape | What | When |
|---|---|---|
| `existing_cluster_id` (persistent) | Long-lived shared cluster, identified by ID via `${var.cluster_id}` | Default for dbt-run tasks. Reduces cold-start latency, shares state across dataset jobs. |
| `job_cluster` (ephemeral) | Cluster spun up at job start, torn down at end. Keyed by `job_cluster_key` referencing a complex var (e.g. `${var.dqf_cluster}`) | DQ verification (Deequ). One job's failure won't poison a shared cluster. |
| `environment_key: default_python` (serverless) | Serverless Python compute, deps via `environments[]` | **Not used today.** DBX-DAB-006 (renamed from RFD 0012 DBX-COMPUTE-007) wants this for pipeline tasks. Deferred — see `rfd-0012-citations.md`. |

## Persistent shared cluster — `${var.cluster_id}`

The default for dbt run/test tasks. The cluster itself isn't owned by
the bundle; it's pre-provisioned per env and its ID lands in the
`databricks.yml#targets.<env>.variables:` block (mirrored in
`variables_<env>.yml`). The job references it by var name only
(DBX-DAB-005).

```yaml
tasks:
  - task_key: dbt_run
    spark_python_task: { ... }
    existing_cluster_id: ${var.cluster_id}
```

When to use:

- The task is short (< a few minutes) and benefits from a warm cluster.
- The task is one of many similar jobs that can share the cluster.
- The team wants predictable resource budgeting per env (one cluster vs
  N ephemeral ones).

Tradeoffs:

- Cluster contention when many jobs run at once.
- A poisoned cluster (rare — usually a dependency conflict) affects all
  jobs until restart.

## Ephemeral `job_cluster` — `${var.dqf_cluster}` / `${var.small_cluster}`

For workloads that need isolation: DQ verification, one-off backfills,
spike load. The cluster shape comes from `clusters.yml` as a complex var.

```yaml
job_clusters:
  - job_cluster_key: job_cluster
    new_cluster: ${var.dqf_cluster}

tasks:
  - task_key: deequ_verify_task
    notebook_task: { ... }
    job_cluster_key: job_cluster
```

The `new_cluster:` body **must** reference a complex var; never inline
`node_type_id` / `autoscale` etc. in a `*.job.yml` (per DBX-BUNDLE-004
spirit, even though the var itself currently inlines those fields).

When to use:

- The task is long (tens of minutes+) — cold-start overhead is amortized.
- The task has unusual config (single-node, jar libraries, specific
  Spark conf) that doesn't belong on a shared cluster.
- Isolation matters (DQ jobs shouldn't share state with dbt jobs).

## Serverless Python (deferred)

DBX-DAB-006 calls for serverless Python compute for pipeline tasks.
Shape:

```yaml
tasks:
  - task_key: dbt_run
    spark_python_task: { ... }
    environment_key: default_python

environments:
  - environment_key: default_python
    spec:
      client: "1"
      dependencies:
        # cgrepo Nexus proxy required — DBX-DAB-008
        - "--index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/"
        - "dbt-databricks>=1.8,<2.0"
```

Why deferred:

1. The real repo's dbt run depends on `init_scripts` (installing custom
   requirements + DQF libs) that serverless doesn't support yet.
2. Custom JARs (Deequ) live on the cluster, not in `environments[].spec`.
3. The `dbt_wrapper.py` flow has been validated against
   `existing_cluster_id` — switching compute is a separate validation.

Migration path:

1. Get the team's `init_scripts` working as `environments[].spec.dependencies`
   (or move installation into the wrapper itself).
2. Confirm Deequ works in serverless (libraries block on the task).
3. Add a skill mode flag `compute=serverless` that emits the serverless
   shape; default stays `existing_cluster` until the team flips.

## Anti-patterns

- **Don't** mix `existing_cluster_id` and `job_clusters` in the same job.
  Pick one.
- **Don't** put a `new_cluster:` literal in a `*.job.yml`. Reference a
  complex var.
- **Don't** put long-lived cluster sizing in the bundle. Those live in
  the compute-DAB / Terraform / infra layer — the pipeline DAB references
  them by ID only (DBX-DAB-005).
