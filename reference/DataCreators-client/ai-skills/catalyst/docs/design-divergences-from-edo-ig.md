# Design divergences from `edo-ig-data-products`

Verified against `cg-open-itg/edo-ig-data-products` @ `51708bc` on 2026-05-27.

AI Catalyst skills make four deliberate design choices that differ from the
production exemplar (`edo-ig-data-products`). These are deliberate choices,
not bugs. If you're debugging a Catalyst-emitted artifact that doesn't
look like the same thing in edo-ig, check whether your symptom matches one
of the four divergences below before assuming Catalyst is wrong.

> **Status note (2026-05-29):** the in-flight AICAT-130..143 fix batch
> includes AICAT-137, which converges divergence #1 (wrapper location)
> with edo-ig. When AICAT-137 merges, update this doc — drop the section
> for #1 or reduce it to a historical note. The other three divergences
> remain as choices.

---

## 1. Wrapper location

| Surface | Choice |
|---|---|
| `edo-ig-data-products` | Repo-root `/dbt_wrapper.py`, shared across all products. Synced into each bundle via `sync.paths: ../../dbt_wrapper.py` in `data_products/<product>/databricks.yml`. Reference: `cg-open-itg/edo-ig-data-products/dbt_wrapper.py`; bundle wiring in `data_products/shared_ref/databricks.yml`. |
| AI Catalyst | Product-level under `data_products/<product>/python/<pkg>/` — one wrapper per product. Emitted by `/scaffold-repo-structure` and `/write-dbt-wrapper`. |

**Rationale.** Per-product isolation: a wrapper bug in one product can't
break the others, and product teams can iterate on the wrapper without
coordinating across the whole data-products repo.

**Cost.** Wrapper logic drifts across products over time; fixes (e.g. the
robustness gaps in AICAT-138) have to be applied N times instead of once.

**Downstream consequences.**
- `/setup-databricks-asset-bundle` emits the bundle's `sync.paths` to
  point at the product-local wrapper rather than `../../dbt_wrapper.py`.
- `/write-dbt-wrapper`'s path-resolution logic (`__file__` / `PROJECT_HOME`
  / `os.getcwd()` fallback) has to handle a deeper directory layout.

**When to revisit.** If the same wrapper bug is fixed in three or more
products in a short window, the convergence cost has eclipsed the
isolation benefit. Move to repo-root and sync into every bundle.

---

## 2. dbt phase chaining

| Surface | Choice |
|---|---|
| `edo-ig-data-products` | One Databricks task per product: a `deps_then_run` wrapper verb that runs `dbt deps` and `dbt run` in sequence. `dbt seed` and `dbt test` are not in the production job. Reference: `data_products/shared_ref/datasets/currency/bundle/currency.job.yml`. |
| AI Catalyst | Four separate Databricks tasks per product: `deps`, `seed`, `run`, `test`. Emitted by `/setup-databricks-asset-bundle`. Dispatcher pattern in `/write-dbt-wrapper`. |

**Rationale.** Per-phase retry and timeout granularity. A flaky `dbt test`
can re-run independently of `dbt run`; a `deps` resolution failure
short-circuits before any model compute. Easier to attribute cost and
runtime to a specific dbt phase from the Databricks run UI.

**Cost.** More YAML, four task-transition overheads instead of one, and
each task pays the wrapper's import / cold-start cost.

**Downstream consequences.**
- `/setup-databricks-asset-bundle` emits a four-task job template
  instead of a one-task template.
- `/write-dbt-wrapper`'s dispatcher pattern (`sys.argv[1] in {deps, seed,
  run, test}`) exists because of this.

**When to revisit.** If task-transition overhead becomes a measurable
share of total job runtime (e.g. each task spends >30s on cold start
relative to actual dbt work), collapse to a single `deps_then_run` task
and surface phase boundaries via task logs rather than task records.

---

## 3. Data quality strategy

| Surface | Choice |
|---|---|
| `edo-ig-data-products` | Data quality lives in a separate Databricks job using a Deequ notebook task. Reference: `data_products/shared_ref/datasets/currency/bundle/currency_dq.job.yml`. Owned by the platform DQ lane. |
| AI Catalyst | `dbt test` runs as the fourth task in the same job as `deps/seed/run`. No separate DQ job, no Deequ integration. Owned end-to-end by the dbt project. |

**Rationale.** dbt-native testing keeps data-quality assertions colocated
with the model they verify. The test definitions live next to the model
SQL; a model change and its tests version together. No second compute
context, no second ownership boundary.

**Cost.** dbt's test surface is narrower than Deequ's (column-level
predicates and generic relationship tests, not full distribution
profiling). Platform-side DQ telemetry doesn't see Catalyst-emitted
products without explicit wiring.

**Downstream consequences.**
- `/setup-databricks-asset-bundle` does NOT emit a sibling `*_dq.job.yml`
  the way edo-ig does.
- There is no `/setup-deequ-job` skill in Catalyst.
- DQ findings surface via `dbt test` results in the run page, not via a
  centralized DQ dashboard.

**When to revisit.** If platform-level DQ reporting becomes a hard
requirement (e.g. a regulator wants a single source of truth across all
products), add a Deequ-based DQ job and split ownership.

---

## 4. Default compute

| Surface | Choice |
|---|---|
| `edo-ig-data-products` | Classic compute: `existing_cluster_id` references, or `job_clusters` blocks with `new_cluster`. `cluster_log_conf` is configured at infrastructure layer. |
| AI Catalyst | Serverless Python tasks. No `existing_cluster_id`, no `job_clusters`, no `cluster_log_conf`. Emitted by `/setup-databricks-asset-bundle`. |

**Rationale.** Lower cost-to-start (no warm-up), no cluster lifecycle to
manage, and prototype-mode iteration doesn't need cluster permissions.
Serverless is the platform team's recommended default for new pipeline
jobs.

**Pool.** `spark_python_task` without a cluster spec auto-routes to the
**Lakeflow Jobs Serverless** pool — distinct from *Interactive
Serverless Compute* (notebooks) and *Lakeflow Declarative Pipelines
Serverless* (DLT). Cost-attribution joins against `system.billing.usage`
should filter on `sku_name LIKE '%JOBS_SERVERLESS%'`.

Per-DBU pricing between Lakeflow Jobs Serverless and Lakeflow Jobs
Classic is not apples-to-apples — classic also bills the underlying VM
instance separately (the AWS EC2 line item), which serverless rolls into
its DBU rate. A real cost comparison requires totaling DBU + VM under
classic against DBU-only under serverless for a representative
workload. Don't quote the raw DBU delta as the cost difference.

**Cost (logging shape).** `cluster_log_conf` is not available on
serverless — the cluster can't be configured to ship logs anywhere
because Databricks owns the compute. Application-side log/artifact
capture has to fill the gap (see `/setup-monitoring-and-logging`).

**Downstream consequences.**
- `/setup-databricks-asset-bundle` does not emit `cluster_log_conf` in
  per-job YAML (AICAT-135 fixes the legacy placeholder).
- `/setup-monitoring-and-logging` is wrapper-driven, not infra-driven
  (AICAT-136 covers the rewrite).
- The wrapper has to capture dbt artifacts (`run_results.json`,
  `manifest.json`, `logs/dbt.log`) and upload them to a Unity Catalog
  volume, because they're ephemeral on serverless workers.

**When to revisit.** If Databricks adds serverless cluster-log support
that matches the classic `cluster_log_conf` semantics, drop the
wrapper-driven artifact capture and use the platform feature. Also
revisit if a Catalyst-emitted job is large enough that the per-task
serverless billing exceeds an equivalent classic cluster.

---

## References

- edo-ig wrapper: `cg-open-itg/edo-ig-data-products/dbt_wrapper.py`
- edo-ig job YAMLs: `data_products/shared_ref/datasets/currency/bundle/currency.job.yml`, `currency_dq.job.yml`
- Catalyst skills coupled to these choices: `/scaffold-repo-structure`, `/write-dbt-wrapper`, `/setup-databricks-asset-bundle`, `/setup-monitoring-and-logging`
- Driving tickets: AICAT-135, AICAT-136, AICAT-137, AICAT-138

## Maintenance

This doc is a point-in-time snapshot. Update the header date and commit
hash if you re-verify against a newer `edo-ig-data-products` HEAD; drop
or rewrite a section if Catalyst converges. Don't build automation around
it — the rediscovery cost it prevents is human, not machine.
