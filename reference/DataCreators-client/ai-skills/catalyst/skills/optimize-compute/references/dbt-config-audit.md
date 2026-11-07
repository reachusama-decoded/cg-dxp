# dbt Config Audit

What `optimize-compute` looks at inside `profiles.yml`,
`dbt_project.yml`, and the dbt artifacts (`manifest.json`,
`run_results.json`) when evaluating the dbt-side rules
(DBX-WASTE-004, -005, -006, -010).

This document is self-contained: anyone arriving from a SKILL.md
link should be able to understand what config keys we read, what
healthy values look like, and how we classify the cluster a target
points at.

## `profiles.yml` keys

### `threads`

- **What we read.** The integer at
  `<profile_name>.outputs.<target>.threads` for every target the
  skill is asked to audit. Default behavior: audit every target
  whose name does not start with `dev` (developer-local).
- **Healthy range.** Roughly `cluster_cores / avg_query_cost`, clamped
  to `[4, cluster_cores * 2]`. For a 48-core cluster running typical
  analytic queries (`avg_query_cost ~ 2`), threads in the 16-24 range
  is healthy.
- **What triggers a finding.** DBX-WASTE-004 fires on:
  - `threads > observed_concurrent_tasks_peak * 1.5` AND `threads >= 8`;
  - `threads > cluster_cores * 2`; or
  - `cluster_cores >= 16 AND threads < 4`.

Good:

```yaml
# profiles.yml - cluster has 48 cores; threads in healthy band
my_project:
  target: prod
  outputs:
    prod:
      type: databricks
      threads: 16
      http_path: /sql/1.0/warehouses/abcd1234
```

Bad:

```yaml
my_project:
  outputs:
    prod:
      type: databricks
      threads: 64                  # > cluster_cores * 2 if cluster is 48
      http_path: /sql/1.0/warehouses/abcd1234
```

### `http_path`

- **What we read.** The string at `outputs.<target>.http_path` for
  every target.
- **How we resolve it.** See "Resolving `http_path`" below.
- **What triggers a finding.** DBX-WASTE-010 (`error`) when a
  non-`dev` target resolves to an all-purpose cluster.

Good (scheduled target on a warehouse):

```yaml
prod:
  http_path: /sql/1.0/warehouses/abcd1234
```

Good (scheduled target on a DAB job cluster, referenced via
templated env var that we can resolve):

```yaml
prod:
  http_path: "{{ env_var('DBT_PROD_HTTP_PATH') }}"   # resolves to /sql/protocolv1/o/.../0125-jobs-xyz
```

Bad (scheduled target on an all-purpose cluster):

```yaml
prod:
  http_path: /sql/protocolv1/o/123/0125-allp-abcd99
```

### `cluster_id`

- **What we read.** The string at `outputs.<target>.cluster_id` if
  present. This is the legacy dbt-databricks profile shape; modern
  configs use `http_path` exclusively.
- **What triggers a finding.** Same as `http_path` - we feed
  `cluster_id` directly into the resolver. Additionally, if both
  `cluster_id` and `http_path` are set we emit a diagnostic ("dbt
  will use http_path; cluster_id is ignored").

## `dbt_project.yml` keys

### `models.<project>.+materialized`

- **What we read.** Effective materialization per model, from
  `manifest.json` (which already resolves project-level vs.
  model-header overrides).
- **What triggers a finding.** DBX-WASTE-005 - table for low-read,
  view for high-read.

### `models.<project>.+on_schema_change`

- **What we read.** Per-model effective value.
- **Healthy values.** `append_new_columns` or `sync_all_columns` for
  incremental models in lake / silver layers. `ignore` is the dbt
  default and silently masks upstream changes.
- **What triggers a finding.** No direct DBX-WASTE-* code, but we
  flag in the diagnostic stream when an `incremental` model has
  `on_schema_change: ignore` because that interacts badly with
  schema-driver writes. (Surface as an info diagnostic, not a
  DBX-WASTE finding; users should route this through
  `dbt-best-practices` if they want to fix it.)

### `models.<project>.+incremental_strategy`

- **What we read.** Per-model effective value.
- **Healthy values on Databricks.** `merge` for upserts where late
  data is plausible; `append` for strictly append-only event streams;
  `insert_overwrite` for partition-wise rebuilds. Default for
  dbt-databricks is `merge`.
- **What triggers a finding.** No standalone rule. (DBX-WASTE-006,
  which would have surfaced this in its remediation, is withdrawn —
  see findings-catalog.md.)

### `models.<project>.+cluster_by`

- **What we read.** Per-model value.
- **Note.** We do not currently emit a `DBX-WASTE-*` for missing or
  excessive `cluster_by`. The signal exists in query_history
  (`spilled_local_bytes`, scan time) but the analysis is more
  involved than runtime waste; route to `optimize-dbsql-query` if
  the user asks for query-level tuning.

### `models.<project>.+file_format`

- **What we read.** Per-model value.
- **Healthy value.** `delta` is the only Databricks default we
  recommend. Other formats (`parquet`, `csv`) trigger no waste
  finding directly but disable Delta optimizations downstream.
- **What triggers a finding.** Not a `DBX-WASTE-*` rule, but a
  diagnostic is emitted when `+file_format` is something other than
  `delta` AND the model is materialized as `table` or `incremental`.

### `models.<project>.+location_root`

- **What we read.** Per-model value.
- **Note.** Strictly informational; affects external table location
  but not compute waste.

### `vars.dispatch`

- **What we read.** Top-level `vars.dispatch` and any package-level
  override.
- **Why we care.** The `dispatch` macro lets a project override
  which package's macro implementation runs. If a project sets
  `dispatch: [{macro_namespace: dbt, search_order: [my_pkg, dbt]}]`,
  then any subsequent `optimize-compute` recommendation that depends
  on macro behavior (e.g. the incremental merge predicate) needs to
  trace through `my_pkg` first. We do not emit a finding for this -
  we just log a diagnostic so the user knows the recommendation
  assumes default dispatch.

### `models.<project>.<layer>.+threads`

- **What we read.** Per-layer thread override.
- **What triggers a finding.** DBX-WASTE-004 evaluation must compute
  effective threads per layer if overrides are present. The
  profile-level `threads` is the fallback. If the per-layer override
  exists, we evaluate the rule once per layer.

## Resolving `http_path` (basis for DBX-WASTE-010)

`http_path` strings come in two well-defined shapes plus a templated
shape:

1. **Warehouse path.** `/sql/1.0/warehouses/<warehouse_id>`. We
   classify as `kind = "warehouse"` with `id = <warehouse_id>` and
   look up shape via `/api/2.0/sql/warehouses/{id}` (used to drive
   DBX-WASTE-008/009 elsewhere).

2. **Cluster path.** `/sql/protocolv1/o/<workspace_id>/<cluster_id>`.
   The audit script (parser-only) cannot reach
   `/api/2.0/clusters/get`, so it records cluster-path targets as
   `cluster_unknown` and leaves the all-purpose vs. job-cluster
   decision to DBX-WASTE-010's warning branch. A higher-fidelity
   collector (or a user-supplied override in the dbt snapshot's
   `resolved_compute` map) can upgrade the classification by setting
   `kind` to one of the values below, using `.cluster_source` and
   `.job_id` from `/api/2.0/clusters/get?cluster_id=<id>`:

   | `.cluster_source` | `.job_id` present? | Classification |
   |---|---|---|
   | `JOB` | yes | `job_cluster` |
   | `API` | no | `all_purpose_cluster` |
   | `UI` | no | `all_purpose_cluster` |
   | `JOB` | no | `all_purpose_cluster` (orphaned; flag as diagnostic) |
   | `PIPELINE` | no | out of scope (Delta Live Tables; skip with diagnostic) |

   With no upgrade applied, the kind stays `cluster_unknown` and
   DBX-WASTE-010 emits a `warning` (not `error`), which is the
   intended fail-safe — see `findings-catalog.md` § DBX-WASTE-010.

3. **Templated.** Anything containing `{{` or `${`. Pass the value
   through Python's `os.path.expandvars` + a dbt Jinja stub for
   `env_var('NAME')` style. If the template references an env var
   we can resolve from the calling shell, treat as resolved. If
   resolution fails, classify as `unresolved` and emit an
   `info`-severity diagnostic instead of an `error`.

   **Literal-default fallback.** Before classifying a templated
   `http_path` as `unresolved`, the audit script
   (`scripts/audit_dbt_config.py::extract_jinja_literal_default`)
   walks the Jinja expression for the deepest literal-string
   argument to `env_var()` / `var()` and treats that as the
   classification basis. This handles the dominant EDO
   `profiles.yml` shape:

   ```yaml
   http_path: "{{ env_var('DBT_HTTP_PATH', var('http_path', '/sql/1.0/warehouses/a0e57263293aee36')) }}"
   ```

   With no env var set and no project-level `var:` binding, the
   value dbt resolves to at runtime IS the innermost literal
   (`/sql/1.0/warehouses/a0e57263293aee36`), so the resolver
   classifies the target as `warehouse`. Supported shapes:

   - `"{{ var('NAME', 'literal_default') }}"`
   - `"{{ env_var('VAR', 'literal_default') }}"`
   - Nested: `"{{ env_var('X', var('y', 'literal_default')) }}"`

   When no literal default exists, the resolver still returns
   `unresolved` and the evaluator emits the `info`-severity
   diagnostic as before.

The resolver returns a small record:

```
ResolvedHttpPath {
  raw: str,
  kind: "job_cluster" | "all_purpose_cluster" | "cluster_unknown" | "warehouse" | "unresolved",
  id: str | None,
  reason: str | None,   # populated when unresolved
}
```

## dbt-on-Databricks gotchas worth knowing

- **`threads` semantics differ by target kind.** Against a SQL
  warehouse, each thread opens a separate Thrift connection;
  Databricks limits concurrent connections per warehouse and queues
  beyond that. Against a cluster, threads multiplex over a single
  Spark session and are bounded by cluster cores. DBX-WASTE-004 only
  applies to cluster targets; warehouse targets that have too many
  threads will show up as DBX-WASTE-009 (queueing) instead.

- **The `dispatch` macro override pattern.** A project can replace
  `dbt.snapshot_check_strategy` with its own implementation via
  `vars.dispatch`. If a remediation we recommend (e.g. switching to
  incremental merge) relies on dbt-databricks's default macro and
  the project has overridden it, the rewrite may not produce
  identical SQL. We surface this as a caveat in remediation text;
  we do not refuse to recommend.

- **`+file_format: delta` is the default.** On dbt-databricks >=1.0
  the default `file_format` is `delta`. Older projects may have
  inherited `parquet` from a previous adapter (dbt-spark). Background
  noted here for engineers manually evaluating a table->incremental
  conversion; the skill itself does not emit a finding (DBX-WASTE-006
  is withdrawn).

- **`+incremental_strategy: merge` vs `append`.** `merge` requires
  `unique_key` and a delta-format target table. `append` is faster
  but cannot deduplicate late arrivals. Engineers performing a
  manual table->incremental rewrite typically pick `merge` by
  default and reach for `append` only when the source is strictly
  append-only.

- **`http_path` and target file location.** The same dbt model can
  run on a warehouse in `dev` and a job cluster in `prod`. We
  evaluate each target independently. DBX-WASTE-004 (threads) on a
  warehouse target is a no-op; DBX-WASTE-010 on a warehouse target
  is a no-op; both rules can co-exist across targets without
  conflict.

## How findings cross-reference compute classification

| Finding | Cluster | Warehouse | Templated/Unresolved |
|---|---|---|---|
| DBX-WASTE-001 | applies | n/a | skipped (need cluster_id) |
| DBX-WASTE-002 | applies | n/a | skipped |
| DBX-WASTE-003 | applies (job_cluster only) | n/a | skipped |
| DBX-WASTE-004 | applies (job_cluster or all_purpose) | skipped (warehouse semantics differ) | skipped + diagnostic |
| DBX-WASTE-005 | applies (manifest-driven, not http_path-driven) | applies | n/a |
| DBX-WASTE-007 | applies (cluster only) | n/a | skipped |
| DBX-WASTE-008 | n/a | applies | skipped |
| DBX-WASTE-009 | n/a | applies | skipped |
| DBX-WASTE-010 | fires (`error`) on all_purpose; skipped on job_cluster | not applicable (warehouse is fine) | fires `info` diagnostic |

This matrix is the source of truth for which findings the skill
even attempts on a given target. `evaluate_findings.py` consults it
before invoking each per-rule evaluator.
