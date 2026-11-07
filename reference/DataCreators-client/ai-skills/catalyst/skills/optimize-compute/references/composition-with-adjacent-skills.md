# Composition with Adjacent Skills

`optimize-compute` is one of four Catalyst skills that touch Databricks
performance. They overlap deliberately, and the decision tree here tells
the agent (and the user) when to invoke this skill versus one of the
others. The rule is simple: this skill owns **runtime waste evidence
gathered from the Databricks API**. Anything else routes elsewhere.

## Prerequisites

`optimize-compute`'s autoscale signals only make sense on a cluster
that **actually autoscales**. If `min_workers == max_workers` (a
fixed-worker cluster expressed via the autoscale block, or a
`num_workers`-only cluster), there is no autoscale behavior to
observe: WASTE-001 and WASTE-002 should **not** fire on such a
cluster. The right routing for fixed-worker clusters is
`optimize-databricks-job` (DBX-PERF-002), which treats fixed-size as
a static-config issue rather than a runtime one.

Run `optimize-databricks-job` first on any bundle whose clusters may
be fixed-size. Only run `optimize-compute` after the cluster spec is
confirmed to have a non-trivial autoscale band - otherwise the
runtime-evidence rules in this skill produce no useful signal.

The other waste rules (DBX-WASTE-003 through -010) do not depend on
autoscale and run regardless.

## Quick reference (use this table first)

| If the symptom is... | ...go to | ...because |
|---|---|---|
| Static YAML smell in a Databricks Asset Bundle (timeouts, max_concurrent_runs, autotermination) | `optimize-databricks-job` | DBX-PERF-* family is bundle-static; no API calls needed. |
| Job-level concurrency / `max_concurrent_runs` mis-set in a bundle | `optimize-databricks-job` (DBX-PERF-001) | Concurrency is a bundle-static field; no runtime evidence needed. |
| Photon disabled on a SQL-heavy workload declared in a bundle | `optimize-databricks-job` (DBX-PERF-005) | Photon enablement is a static bundle setting; route there. |
| Fixed-worker cluster (`min_workers == max_workers` or `num_workers` only) | `optimize-databricks-job` (DBX-PERF-002) | This is a static-config issue, not a runtime one; WASTE-001/-002 do not fire on non-autoscaling clusters. |
| Node type / instance type oversized (e.g. 11-worker peak on `i3.16xlarge`) | `databricks-execution-compute` | Node-type sizing requires CPU/memory utilization metrics this skill does not collect; DBX-WASTE-001 only checks worker count, not instance size. |
| A specific SQL query / dbt-compiled model with obvious anti-patterns (SELECT *, cross join, missing prune predicate) | `optimize-dbsql-query` | SQL-PERF-DBSQL-* family is per-query static analysis. |
| Provisioning, lifecycle, sizing decisions made *before* a workload exists | `databricks-execution-compute` | DBX-COMPUTE-* family covers create / start / stop / resize. |
| 30 days of run history shows the cluster is oversized, threads are wrong, or a warehouse queues | `optimize-compute` (this skill) | DBX-WASTE-* family is runtime-evidence-driven. |
| You want a "is my prod target pointing at an all-purpose cluster" check (DBX-WASTE-010) | `optimize-compute` (this skill) | Cross-cuts DBX-COMPUTE-001 but the detector lives here. |
| You want a "should this cluster exist at all" question | `databricks-execution-compute` | That skill owns lifecycle / inventory. |
| You see a runtime issue that the bundle YAML alone would not surface | `optimize-compute` (this skill) | API evidence is required. |
| You see a YAML issue that has no runtime component (e.g. missing tag) | `optimize-databricks-job` | Pure static check. |
| You compiled a dbt model and noticed `WHERE 1=1 AND ...` is slow | `optimize-dbsql-query` | Per-query. |

When in doubt, both this skill and the others surface their findings
under disjoint `DBX-WASTE-*` / `DBX-PERF-*` / `SQL-PERF-DBSQL-*` /
`DBX-COMPUTE-*` IDs - so running more than one is safe and produces
non-overlapping reports.

## `optimize-databricks-job`

**Scope.** Static analysis of a rendered Databricks Asset Bundle
(`resources/*.yml`). Emits `DBX-PERF-*` findings on concurrency,
timeouts, cluster sizing (as declared in YAML), runtime version,
Photon. Can auto-apply safe defaults for `max_concurrent_runs` and
`timeout_seconds`.

**What routes there instead of here.**

- The cluster `autoscale.max_workers` is set to `40` in the bundle
  YAML but the cluster has never run a real workload (it's new).
  This is a static-only judgement; route to `optimize-databricks-job`,
  which can flag "40 is unusually high for a new bundle". We can't
  fire DBX-WASTE-001 because we have no runs to compare against.
- `timeout_seconds` is unset on a daily job. Static check; route
  there.
- The job's `max_concurrent_runs` is 10 but the SLA only needs 1
  concurrent execution. Static; route there.

**What stays here.**

- The cluster `autoscale.max_workers` is 40 *and* 25 runs in the last
  30 days never peaked above 11 workers. Now we have runtime
  evidence; DBX-WASTE-001 fires here.

**Composition pattern.** A common workflow is to run
`optimize-databricks-job` first (cheap, no API calls), then
`optimize-compute` second (validates the static suggestions against
real history). When the two agree, the user has high confidence in
the change.

## `optimize-dbsql-query`

**Scope.** Static analysis of `.sql` files (compiled dbt models or
hand-written DBSQL). Emits `SQL-PERF-DBSQL-*` findings on per-query
anti-patterns (`SELECT *`, cross joins, missing predicates). Pure
static; no warehouse connection.

**What routes there instead of here.**

- A dbt model contains `SELECT *` against a source. Static SQL smell;
  route to `optimize-dbsql-query`.
- A query joins two tables without an `ON` clause. Route there.
- A query has a partition column but no predicate using it. Route
  there.

**What stays here.**

- A dbt model materialized as `table` is being read fewer than 3
  times per day. The read-count signal lives here (DBX-WASTE-005),
  but it is emitted as an **info-only diagnostic** - the skill
  surfaces the read count as an observation and does not recommend
  changing the materialization. Whether to switch materialization
  depends on refresh cost, SLA, view body complexity, and downstream
  tooling, none of which the skill can see.
- A SQL warehouse's p95 wall-clock is too short for its size class;
  fires DBX-WASTE-008 here. (`optimize-dbsql-query` cannot see
  history.)

**Composition pattern.** DBX-WASTE-005 is a **diagnostic signal
only**. It belongs on a quarterly performance review backlog where a
human can weigh refresh cost, SLA, and view body complexity - it is
not a CI-gate-grade signal and does not recommend a fix. (DBX-WASTE-006,
which would have flagged incremental-conversion candidates by runtime
growth, is withdrawn — the 14-point history it required couldn't be
sourced from the bundled collector. See findings-catalog.md for the
rationale.)

## `databricks-execution-compute`

**Scope.** The lifecycle skill - create cluster, resize cluster,
terminate cluster, create warehouse, pick node types, choose DBR
versions. Owns the `DBX-COMPUTE-*` standards (001 = scheduled jobs
on job clusters or warehouses, never all-purpose; 002 = right-size
on creation; 004 = autotermination configured).

**What routes there instead of here.**

- "I'm creating a new cluster for this workload; what size?" Lifecycle
  decision; route there.
- "I need to resize this cluster's autoscale to 4-12; please apply
  it." Cluster mutation; route there. (This skill only *suggests*
  the new bounds via DBX-WASTE-001/002.)
- "Terminate this stale cluster." Lifecycle; route there.
- "What DBR version should I use?" Lifecycle; route there.
- "Is `i3.16xlarge` the right node type for this workload?" Node-type
  / instance-type sizing requires CPU/memory utilization metrics that
  `optimize-compute`'s collector does not fetch. DBX-WASTE-001 only
  evaluates worker *count*; an 11-worker peak on an oversized node
  type can pass DBX-WASTE-001 and still be wasteful. Route node-type
  sizing to `databricks-execution-compute`, which owns instance-type
  selection against utilization profiles.

**What stays here.**

- "Is this existing cluster oversized given how it's been used?"
  Runtime evidence; DBX-WASTE-001 fires here.
- "Are my dbt scheduled targets pointing at an all-purpose cluster?"
  Cross-cuts `DBX-COMPUTE-001`, but the detector is in this skill
  (DBX-WASTE-010). We emit the finding here; `databricks-execution-compute`
  is the right place to *act* on it by creating a job cluster.

**Composition pattern.** Findings from this skill that recommend
cluster changes feed into `databricks-execution-compute` for
execution. A typical flow:

1. `optimize-compute` reports DBX-WASTE-001 with "lower
   max_workers from 20 to 12".
2. User invokes `databricks-execution-compute` to perform the resize
   safely (with the right API call, the right blue/green pattern,
   the right pause-before-resize behavior).

This skill stays read-only against the Databricks API; it never
mutates compute. Apply mode (local file edits) is planned for a
Phase 2 follow-up PR; in this release all findings emit with
`apply_mode_supported: false`.

## Edge case: simultaneous fire across skills

Two skills can fire on the same root cause. Example: a DAB bundle
declares `autoscale.max_workers: 20` and the cluster has run 25
times never peaking above 11.

- `optimize-databricks-job` may emit a `DBX-PERF-*` flagging "20 is
  high for this workload class" (static heuristic).
- `optimize-compute` emits `DBX-WASTE-001` flagging "20 is high
  given observed peak 11" (evidence-driven).

This is intentional. The two findings are independent signals
(static heuristic + evidence) that happen to point at the same fix.
The user gets two reasons to lower `max_workers`, not double-counted
waste. If the user runs both skills and both fire, do not collapse
the findings - keep both IDs in the report.

## Why the four skills are split this way

- **Cost model.** Static skills are cheap (no API calls). Runtime
  skills are expensive (API quota, token budget). Splitting them
  lets users choose which spend to make.
- **Auth model.** Static skills don't need Databricks credentials.
  This skill does. Splitting keeps the static skills runnable in
  CI without secret distribution.
- **Failure mode.** A failed API call shouldn't break a static
  bundle review. The split isolates failure domains.
- **Findings hygiene.** Disjoint `DBX-*` / `SQL-PERF-*` prefixes mean
  findings flow through Catalyst's central registry without
  collision and CI gates can opt in to families independently.

## Decision tree (collapsed form)

```
Does the issue need Databricks API run history to detect?
  YES -> optimize-compute (this skill)
  NO  -> Is the issue a single SQL query / model file?
           YES -> optimize-dbsql-query
           NO  -> Is the issue a static config in a DAB YAML?
                    YES -> optimize-databricks-job
                    NO  -> Is the issue cluster lifecycle (create/resize/delete)?
                             YES -> databricks-execution-compute
                             NO  -> Probably not a perf/compute issue; rethink the routing.
```
