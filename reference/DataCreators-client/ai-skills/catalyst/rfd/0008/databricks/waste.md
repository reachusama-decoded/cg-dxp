# DBX-WASTE: Runtime Compute Waste (dbt on Databricks)

Detection rules for Databricks compute over-provisioning surfaced by the
`optimize-compute` skill. The DBX-WASTE-* family covers runtime-observed
waste in dbt pipelines: oversized job clusters, mis-tuned autoscale
floors, idle gaps inside job runs, dbt-threads vs. cluster-cores
mismatch, materialization signals, stale Spark config overrides, SQL
warehouse sizing, and dbt targets pointed at all-purpose clusters.

Authoritative source for thresholds and detection logic. The numbers
encoded in `optimize-compute`'s `evaluate_findings.py` must match the
ones in this file; if a threshold changes here, change it there too
(and vice versa).

## Serverless-first stance

The org's compute posture is **serverless-first** on both sides of the
Databricks platform:

- **Jobs.** [Lakeflow Jobs Serverless](https://docs.databricks.com/en/jobs/serverless-tasks.html)
  is the default for new production work. Classic **job compute** (and
  `job_cluster` autoscale) is the cost-optimization fallback when
  serverless doesn't fit a specific workload pattern (e.g., custom Spark
  configs, init scripts, niche DBR versions, GPU shapes). Running
  production jobs on **all-purpose / interactive** clusters is the
  actual anti-pattern — `DBX-WASTE-010` catches that explicitly and
  fires as `error`.
- **SQL warehouses.** Serverless SQL warehouses are the default for BI
  and dbt-on-warehouse work. Classic SQL warehouses are not recommended
  for new work (see `DBX-COMPUTE-006`).

Most rules in this family describe waste on **classic** compute (the
fallback path). Where a rule is meaningfully different on serverless,
each rule section calls it out explicitly under "Serverless behavior."
For the cases where serverless removes the knob entirely (autoscale
floor/ceiling, `spark_conf`), the rule is simply out of scope on
serverless and the skill skips it.

## Severity scale

Consistent with other `DBX-*` families:

| Severity | Meaning |
|---|---|
| `error`   | Misconfiguration that costs real money or violates a hard standard. Fails the skill's exit-non-zero gate. |
| `warning` | Strong signal of waste with high confidence (>=10 runs of evidence, large delta). Does not fail the gate but surfaces prominently. |
| `info`    | Optimization opportunity with weaker signal or shape-dependent fix. Surface to the user; never block. |

Apply-mode policy: only findings explicitly tagged **"auto-applicable"**
may be written by `apply` mode. Everything else is **suggestion only** —
the skill prints the recommended delta and exits without modifying
files.

## Universal preconditions

Apply to every rule below unless overridden:

- The cluster / warehouse must be live and reachable via the Databricks
  API (we do not infer from telemetry exports).
- `run-history-window-days`: **30** (caller can override; default 30).
- `runs-per-job-cap`: **200** (we stop pulling after the 200th most
  recent run).
- `min-runs-required`: **10**, except where a rule specifies otherwise.
  Below this threshold the runtime-waste rules are skipped with an
  explicit "insufficient run history" note instead of firing.

---

## DBX-WASTE-001 — Job cluster oversized vs. peak observed workers

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Scope note.** This rule examines **worker count only**, not node
type / instance size. An 11-worker peak on `i3.16xlarge` may still be
wasteful via oversized nodes; that dimension is owned by
`databricks-execution-compute`. Reviewers should consider node-type
sizing separately.

**Rule.** A job cluster's `autoscale.max_workers` is set materially
higher than the highest worker count actually observed across recent
runs of jobs that use it.

**Why warning, not error.** The cluster is functional and jobs succeed;
we are paying for headroom that never gets used. Concrete dollar waste
but not a correctness defect.

**Serverless behavior.** Out of scope. Lakeflow Jobs Serverless does
not expose `autoscale.max_workers` — Databricks manages the compute
shape. The skill skips this rule for serverless jobs and emits no
finding.

**Detection.**

```
inputs:
  cluster_id                              # job cluster
  runs = jobs that used cluster_id, last 30d, cap 200
  min_runs_required = 10
  peak_worker_utilization_threshold = 0.6

if len(runs) < min_runs_required:
    skip with reason "insufficient run history (<10 runs)"

# Per-run peak: ONLY `current_num_workers` from RESIZING and
# UPSIZE_COMPLETED events. Do NOT include
# AUTOSCALING_STATS_REPORT.details.max_workers -- that field is the
# *configured ceiling* (it echoes the cluster spec back at you), not an
# observation, so including it would always equal max_workers and
# suppress this rule on every cluster. Likewise exclude
# `target_num_workers` -- that's the autoscaler's *intent*, not a
# realized peak.
peak_per_run = [max(current_num_workers across RESIZING/UPSIZE_COMPLETED in run window) for run in runs]
observed_peak = max(peak_per_run)

if observed_peak <= ceil(cluster.autoscale.max_workers * 0.6):
    fire DBX-WASTE-001
```

**Edge cases that should NOT fire.**

- Fewer than 10 runs in the window: skip with reason.
- `autoscale` not set (fixed-size cluster): out of scope for this rule;
  consider DBX-WASTE-002 instead.
- The most recent run included a manual or programmatic `resize` call
  that pushed workers above the observed peak — the resize event is
  authoritative; trust the API event log over interpolated counts.
- Cluster has been live for less than 7 days *and* fewer than 10 runs:
  skip (cold-start: we don't have enough history to be confident the
  workload pattern is stable).
- Resolved compute is serverless: skip (no `autoscale.max_workers`
  knob exists).

**Worked example.** Job cluster `0125-abcd` is autoscale 4-20. In the
last 30 days it has executed 25 job runs. Across those, the highest
worker count ever observed (per `UPSIZE_COMPLETED` events) is 11.
`ceil(20 * 0.6) = 12`, `11 <= 12`, so DBX-WASTE-001 fires.
Remediation: drop `max_workers` from 20 to `observed_peak + 1 = 12`.

**Remediation.** Lower `autoscale.max_workers` to `observed_peak + 1`
(one worker of headroom). **Suggestion only** — touching cluster
sizing affects every job that uses the cluster; we don't auto-apply.

---

## DBX-WASTE-002 — Autoscale floor never relaxes

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Rule.** A job cluster's `autoscale.min_workers` is set higher than 1
or 2, but cluster events show the cluster spent the bulk of runtime
sitting at the floor; the floor is buying us nothing.

**Why warning.** We are paying for idle workers we don't use.

**Serverless behavior.** Out of scope. Serverless jobs do not expose
`autoscale.min_workers`. The skill skips this rule for serverless.

**Detection.**

```
inputs:
  cluster_id
  runs = last 30d, cap 200, min 10
  floor_time_share_threshold = 0.70  # 70%

events = /clusters/events, type in {RESIZING, UPSIZE_COMPLETED, AUTOSCALING_STATS_REPORT}
# Reconstruct a worker-count timeline; bucket per second.
total_active_seconds = sum(seconds the cluster was running during a job run)
floor_seconds = seconds where worker_count == cluster.autoscale.min_workers

if cluster.autoscale.min_workers <= 1:
    skip (no waste to cut)

if floor_seconds / total_active_seconds >= 0.70:
    # Cluster sat at the floor for >=70% of run wall-clock; floor is too high.
    fire DBX-WASTE-002
```

**Edge cases that should NOT fire.**

- `min_workers <= 1`: nothing to cut, skip silently.
- Cluster is shared across many jobs with bursty arrival (we trip on
  `AUTOSCALING_STATS_REPORT.upscale_pressure > 0` in >5% of samples) —
  the floor may be intentional warm capacity. Skip with reason
  "upscale pressure detected; floor likely intentional".
- The `min_workers` equals `max_workers` (fixed-size cluster expressed
  as autoscale): out of scope here; DBX-WASTE-001 will fire on max
  instead.
- Resolved compute is serverless: skip.

**Worked example.** Job cluster `0125-efgh` is autoscale 6-16. Over 18
runs in the last 30 days, total active seconds = 14,400. Seconds at 6
workers (the floor) = 11,200. Ratio = 77.8% >= 70% -> fires.
Remediation: lower `min_workers` from 6 to `max(1, 6 - 2) = 4`.

**Remediation.** Lower `autoscale.min_workers` to `max(1, current - 2)`
(catalog default; equivalent to "lower to 1 or 2" on small floors).
The remediation **does not** delete the autoscale block — shifting to
a fixed-size cluster is a separate decision the engineer should make
explicitly; this rule only argues the floor is too high.
**Suggestion only.**

---

## DBX-WASTE-003 — Long idle gaps between tasks within a job run

**Severity:** info
**Since:** v0.1.0
**Linter:** advisory

**Rule.** Within a single job run, the sum of time between task
completions and the next task starting (the "gap time") is a material
fraction of total run wall-clock. The cluster is up and billing but no
task is running.

**Why info.** The fix is structural (consolidate tasks, introduce
`depends_on`, switch to a shared job cluster) and not mechanical, so we
don't escalate above info.

**Serverless behavior.** Lakeflow Jobs Serverless bills only while a
task is actually executing, not for idle gaps between tasks on a
shared cluster. On serverless this rule does not apply — gap-time is
not a billing event. The skill skips DBX-WASTE-003 when the dbt
target's `resolved_compute` is serverless.

**Detection.**

```
inputs:
  job_id
  runs = /jobs/runs/list (job_id, last 30d, cap 200, min 10)
  gap_share_threshold = 0.20  # 20%

per_run:
  per task in run.tasks:
    task_busy_end = task.end_time
    next_task_start = min(t.start_time for t in run.tasks if t.start_time >= task_busy_end)
    gap = next_task_start - task_busy_end  (clip to >=0)
  total_gap = sum(gap across tasks in run)
  total_wall = run.end_time - run.start_time
  gap_share[run] = total_gap / total_wall

avg_gap_share = mean(gap_share across runs)

if avg_gap_share > 0.20:
    fire DBX-WASTE-003
```

**Edge cases that should NOT fire.**

- Single-task jobs: gap is undefined; skip.
- Tasks that intentionally `depends_on` an external sensor / wait
  operator: if the gap correlates 1:1 with sensor wait time
  (heuristic: tasks named `sensor`, `wait`, `poll`), exclude that gap.
- Jobs using `existing_cluster_id` for an all-purpose cluster: the user
  is not paying per-task for the gap (cluster bill is continuous
  anyway). Skip but flag DBX-WASTE-010 instead if scheduled.
- Serverless job: skip (no idle billing).

**Worked example.** Job `1234567` has 20 runs in the window. Each run
has 4 tasks. Mean total wall-clock = 42 minutes; mean total gap time
= 11 minutes. Ratio = 26.2% > 20% -> fires. Remediation: consolidate
the two smallest tasks into one notebook, or add `depends_on` so they
run on the same job-cluster instance.

**Remediation.** Three remediation paths in suggestion text:
(1) consolidate adjacent tasks into a single notebook;
(2) switch from per-task new clusters to a single shared job cluster on
the job;
(3) restructure `depends_on` so independent tasks run in parallel.
**Suggestion only.**

---

## DBX-WASTE-004 — dbt threads vs. cluster cores mismatch

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Rule.** `profiles.yml.threads` is set in a way that mismatches the
cluster the dbt target points at: either (a) higher than the observed
concurrent-task ceiling, indicating threads queue inside dbt for no
benefit; or (b) higher than 2x cluster cores, which oversubscribes the
cluster; or (c) less than 4 on a cluster with >=16 cores, leaving the
cluster idle.

**Why warning.** Either direction (over or under) burns money.

**Serverless behavior.** Serverless jobs do not expose a fixed core
count — Databricks scales compute behind the scenes — so the
"cores" denominator is undefined from the API. The rule keeps its
existing escape hatch: when
`resolved_compute.<cluster_id>.cores_per_worker` is supplied
explicitly by the caller (e.g., the dbt audit snapshot encodes a known
shape), the rule still evaluates. Without that caller-supplied input
the rule skips with reason "serverless compute; cores undefined".
Sub-case (a) — `over_provisioned_inside_dbt` based on
`observed_concurrent_tasks_peak` — does NOT require core count and
can still fire on serverless.

**Detection.**

```
inputs:
  profiles_yml_threads        # dbt config
  resolved_compute            # http_path resolved per dbt-config-audit.md
  cluster_cores               # from /clusters/get .driver_node_type_id and
                              # .node_type_id, multiplied by worker count
                              # at observed peak
  observed_concurrent_tasks_peak  # max in-flight model count
                                  # (parsed from dbt run logs in CI; fall
                                  #  back to threads value if unavailable)

over_provisioned_inside_dbt =
    profiles_yml_threads > observed_concurrent_tasks_peak * 1.5
    AND profiles_yml_threads >= 8

over_subscribing_cluster =
    profiles_yml_threads > cluster_cores * 2

under_utilizing_big_cluster =
    cluster_cores >= 16 AND profiles_yml_threads < 4

if any of the three: fire DBX-WASTE-004
    finding_body should mention which sub-case tripped, and
    suggested_threads = clamp(cluster_cores // avg_query_cost, 4, cluster_cores * 2)
    avg_query_cost defaults to 2 if we have no signal.
```

**Cores-per-worker resolution.** `cluster_cores` is computed as
`worker_count * cores_per_worker`. `cores_per_worker` is resolved by
looking up the cluster's `node_type_id` in the `NODE_TYPE_CORES`
catalog inside `evaluate_findings.py`. The catalog covers the common
AWS i/r/m families (i3, r5d, m5, m7gd, i7gd) and Azure DS / D / E
shapes that EDO uses. For unknown node types the evaluator falls back
to `DEFAULT_CORES_PER_WORKER = 4` and records `cores_assumed: true` in
the finding's evidence (alongside `node_type_id` and the resolution
source) so consumers can flag the imprecision. Caller-supplied
`resolved_compute.cores_per_worker` in the dbt snapshot overrides both
the catalog and the default — this is the path serverless callers
use to opt in.

**Edge cases that should NOT fire.**

- Resolved compute is a SQL warehouse, not a cluster: dbt threads
  semantics differ (one Thrift connection per thread); skip and emit
  warehouse-side findings (DBX-WASTE-008/009) instead.
- `threads` is 1: usually intentional (debugging or strict serialization
  for FKs); skip.
- A `+threads` model-level override is present that supersedes the
  profile value for that layer: evaluate the effective value per
  layer, not the profile default.
- Resolved compute is serverless and no `cores_per_worker` was supplied
  by the caller: skip sub-cases (b) and (c); sub-case (a) may still
  fire if `observed_concurrent_tasks_peak` is available.

**Worked example.** `profiles.yml` has `threads: 32`. Resolved compute
is job cluster `0125-abcd`, peak workers 6, each with 8 cores -> 48
cores total. `observed_concurrent_tasks_peak` from logs is 12.
`32 > 12 * 1.5 = 18` -> over_provisioned_inside_dbt is true. Fire
DBX-WASTE-004. Suggested threads ~= 16.

**Remediation.** Set `threads` to roughly `cluster_cores / avg_query_cost`
(concrete number in finding body). **Suggestion only** (`profiles.yml`
is often environment-specific; we don't auto-edit it).

---

## DBX-WASTE-005 — Materialization heavier than usage justifies

**Severity:** info
**Since:** v0.1.0
**Linter:** advisory

**Status.** **Info-only diagnostic. No automated recommendation.** The
20-reads/day cutoff for views ignores view-body complexity (a
50-read/day cheap pass-through view is fine; a 5-read/day expensive
join-heavy view isn't). The 3-reads/day cutoff for tables similarly
ignores refresh cost and SLA. The catalog still describes the rule
because the read-count signal is useful for engineers to eyeball, but
the skill emits it as an observation, not a recommendation.

**Rule.** A dbt model's materialization disagrees with downstream read
volume: `table` for a low-read model, or `view` for a heavily-read
model.

**Why info.** The fix is judgment-dependent (refresh window, SLA, view
body complexity, downstream tooling) and we don't have enough context
to be confident.

**Serverless behavior.** Materialization choice is independent of
whether the executing compute is serverless or classic — the signal
and the diagnostic are unchanged. No serverless-specific handling.

**Detection.**

```
inputs:
  manifest.json (dbt artifacts) - gives materialization per model
  query_history (last 14 days) - gives reads per object
  reads_low_threshold  = 3   # reads per day
  reads_high_threshold = 20  # reads per day (10x the low threshold,
                             # avoids middle-ground misfires)

reads_per_day[model] = count of queries referencing fully-qualified
                       table name / 14

if model.materialization == "table" and reads_per_day[model] < 3:
    fire DBX-WASTE-005 with hint "materialize as view"

if model.materialization == "view" and reads_per_day[model] > 20:
    # heavily read - paying compute to re-derive on every read
    fire DBX-WASTE-005 with hint "materialize as table or incremental"
```

**Known limitation.** Read count is computed via case-insensitive
substring search of fully-qualified model names against query text.
Substring collisions between model names can inflate counts. The
signal is intentionally informal; consumers should treat it as a
directional indicator, not a precise measurement.

**Edge cases that should NOT fire.**

- Model is tagged `+materialized: ephemeral`: skip.
- Model has no observed reads (truly zero): skip rather than fire on
  "0 < 3" — likely the model is unused entirely, which is a different
  problem out of scope here.
- Model is referenced only by downstream models in the same run (no
  external query history): skip; cross-model refs in the same dbt run
  aren't waste.
- Model is a source of a downstream `materialized: incremental` model:
  cannot be a view (incremental needs a table to read from). Skip in
  the view->table direction.

**Worked example.** Model `analytics.fct_orders_daily` is
`materialized: table`, refreshed nightly. Query history shows 18 reads
in 14 days -> 1.3/day. Skill emits a diagnostic record:
"`analytics.fct_orders_daily` (materialized: table) observed at
1.3 reads/day over 14 days." No materialization recommendation.

**Remediation.** **Report-only diagnostic: surface the read count as an
observation; no automated recommendation.** The engineer decides
whether to switch materialization based on refresh cost, SLA, view body
complexity, and downstream tooling — context the skill does not have.

---

## DBX-WASTE-006 — Incremental candidate still doing full refresh (withdrawn)

**Severity:** info
**Status:** withdrawn
**Since:** v0.1.0

**Status.** **Withdrawn.** The rule required a 14-point per-model
runtime history (linear-regression slope over time) to produce a
trustworthy signal. dbt's `run_results.json` carries one run at a time,
and this skill is intentionally stateless — there is no reliable way
for the bundled collector to assemble that history without an external
orchestration story (CI artifact retention, a system-table query, or a
dbt Cloud API call), and the rule was already info-only with no
automated recommendation. The cost of maintaining the data plumbing
exceeded the diagnostic value.

The rule ID is reserved per RFD 0008's stable-ID policy and will not be
reused. If a future PR resurrects this signal, it must come with
explicit history-source plumbing and an opt-in input to the audit step.

The original rule, for the record:

**Rule.** A `table` model has the structural shape of an incremental
candidate (clear partition column, monotonically growing runtime,
append-shaped source data) but isn't using `incremental` materialization.

**Detection.**

```
inputs:
  model.materialization == "table"
  partition_col_present   # source ref has a column matching r"(_date|_ts|_at|created|updated|loaded|ingested|event_time)$"
  runtime_growth          # linear regression slope of run duration over
                          # last 14 runs, normalized by start duration
  min_runs_for_trend = 14
  growth_threshold = 0.5  # 50% growth across observation window

if model.materialization != "table": skip
if not partition_col_present: skip
if len(historical_runs) < 14: skip with reason
if runtime_growth_normalized < 0.5: skip

# Model is a table, has a partition column, runtime has grown >=50%
# over the last 14 runs. Likely incremental candidate.
fire DBX-WASTE-006
```

**Worked example (historical).** Model `staging.stg_clickstream_events`
is materialized `table`. Source `raw.clickstream` has an `event_time`
column. Run durations over 14 runs: 45s -> 88s (95% growth). Skill
would have emitted a diagnostic record: "`staging.stg_clickstream_events`
(materialized: table) observed 95% runtime growth across 14 runs;
partition column `event_time` present." No materialization
recommendation.

**Remediation.** N/A — rule withdrawn.

---

## DBX-WASTE-007 — Spark config overrides likely stale or misconfigured

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Rule.** A job cluster has `spark_conf` entries overriding defaults
that DBR 13+ handles well on its own (notably AQE, shuffle partitions,
executor memory), without a justifying comment.

**Why warning.** These overrides are a common source of silent
performance regression; users often inherit them from old runbooks.

**Serverless behavior.** Out of scope. Serverless jobs and serverless
SQL warehouses do not expose a `spark_conf` field — Spark
configuration is managed by Databricks. The skill skips DBX-WASTE-007
for serverless compute.

**Detection.**

```
inputs:
  cluster.spark_conf              # dict from /clusters/get
  cluster.spark_version           # e.g. "13.3.x-scala2.12"
  dbr_major_version = parse(cluster.spark_version)
  watched_keys = {
    "spark.sql.shuffle.partitions",
    "spark.executor.memory",
    "spark.sql.adaptive.enabled",
    "spark.sql.adaptive.coalescePartitions.enabled",
    "spark.sql.adaptive.skewJoin.enabled",
    "spark.sql.adaptive.advisoryPartitionSizeInBytes",
    # Driver-side overrides. Common waste pattern: oversized drivers
    # paired with small workers (driver inherited from an old all-purpose
    # tuning). DBR 13+ defaults are usually right; manual overrides are
    # most often stale runbook inheritance.
    "spark.driver.memory",
    "spark.driver.cores",
    "spark.driver.maxResultSize",
  }

if dbr_major_version < 13:
    skip (AQE defaults less aggressive; override may be reasonable)

flagged = []
for key in watched_keys:
    if key in cluster.spark_conf:
        flagged.append(key)

if flagged: fire DBX-WASTE-007 (one finding per flagged key)
```

**Edge cases that should NOT fire.**

- Cluster `custom_tags` includes `spark-tuned: "true"` or a key
  matching `r"^optimize-compute-ignore-.*"`: respect the explicit user
  assertion that the override is intentional.
- Override sets the value to Databricks' documented default (we are
  fighting noise, not waste): compare value to known defaults
  per-DBR-version; if equal, skip.
- Resolved compute is serverless (no `spark_conf` exposed): skip.

**Worked example.** Job cluster `0125-ijkl`, DBR 13.3 LTS, `spark_conf`
contains `spark.sql.shuffle.partitions: "200"` and
`spark.executor.memory: "8g"`. Both fire (one finding each).
Remediation: remove the overrides; DBR 13+ AQE coalesces post-shuffle
partitions adaptively, and executor memory should be left to
Databricks node defaults.

**Remediation.** Remove the override entries.

**Apply mode.** **Suggestion only by default.** The skill will not
autonomously delete `spark_conf` keys, because a single misjudged
removal can regress performance silently (the key may be load-bearing
for a workload shape the skill cannot see). Auto-apply is planned for
a Phase 2 follow-up PR; in this release, all findings are emitted with
`apply_mode_supported: false`.

---

## DBX-WASTE-008 — SQL warehouse oversized vs. query history

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Rule.** A SQL warehouse is provisioned larger than its query mix
warrants, measured over a 14-day window.

**Serverless behavior.** Skipped. Serverless SQL warehouses are
already gated out by `_gate_warehouse_events` in the evaluator —
serverless warehouses don't expose the classic scale-out events
(`SCALED_UP` / `SCALED_DOWN`) the rule consumes, and the cost model
(per-DBU billing without idle) makes "oversized" detection
non-meaningful in the same way. Per the org's serverless-first SQL
posture, the remediation path for an oversized classic warehouse is
typically migration to serverless rather than tweaking
`max_num_clusters` on classic.

**Detection.**

The scale-out signal is derived from the warehouse **events** endpoint,
not from `/sql/history/queries` (the queries endpoint does not carry a
per-query cluster index, so prior drafts that referenced
`warehouse_cluster_id_offset` were referring to a non-existent field).
Build the concurrent-cluster timeline from the warehouse's lifecycle
and scale events.

```
inputs:
  warehouse_id
  warehouses_history_window_days = 14
  cluster_count_share_threshold = 0.50   # avg_cluster_count_share over
                                          #   window is <50% of
                                          #   max_num_clusters

# The /api/2.0/sql/warehouses/{id}/events endpoint accepts these event
# types: STARTING, RUNNING, STOPPING (lifecycle), SCALED_UP, SCALED_DOWN
# (scale deltas). Each event's `details.cluster_count` is the realized
# concurrent cluster count immediately after the event. CLUSTER_CREATED /
# CLUSTER_TERMINATED belong to /api/2.0/clusters/events (the all-purpose /
# job cluster endpoint) and are NOT valid here -- earlier drafts had
# this wrong.

events = /api/2.0/sql/warehouses/{id}/events
         (14d, event_types=[STARTING, RUNNING, STOPPING, SCALED_UP, SCALED_DOWN])

# Each event carries a cluster_count snapshot. Build a forward-filled
# timeline by sorting samples on timestamp and treating the most
# recent sample's cluster_count as the held value until the next
# sample. Treat STOPPING as cluster_count=0 if `details.cluster_count`
# is absent.
samples = [(ev.timestamp, ev.details.cluster_count) for ev in events]
samples.sort()
duration_weighted_avg_clusters = sum(cc0 * (ts1 - ts0)) / sum(ts1 - ts0)
    for (ts0, cc0), (ts1, _) in zip(samples, samples[1:])
avg_cluster_count_share = duration_weighted_avg_clusters / warehouse.max_num_clusters

if avg_cluster_count_share < 0.50:
    fire DBX-WASTE-008 "scale-out headroom unused"
```

**Edge cases that should NOT fire.**

- Warehouse is `serverless`: skip (gated out by
  `_gate_warehouse_events`; remediation is migration to serverless,
  not classic-side tuning).
- Warehouse is brand new (<7 days of data): skip with reason.
- Warehouse is explicitly tagged for a single tenant / dashboard with
  bursty patterns (`custom_tags.workload: "bi-bursty"`): skip.

**Worked example.** Warehouse `wh-prod`, size `Large`,
`max_num_clusters: 8`. Over 14 days: avg cluster count = 2.4, ratio =
0.30 < 0.50 -> DBX-WASTE-008 fires with remediation hint to reduce
`max_num_clusters` or migrate to serverless.

**Remediation.** Reduce `max_num_clusters` toward the observed
duration-weighted average, or migrate to a serverless SQL warehouse
(preferred direction per the org's serverless-first SQL posture).
**Suggestion only.**

---

## DBX-WASTE-009 — SQL warehouse under-provisioned (queueing)

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Rule.** A SQL warehouse is queueing queries at p95: requests sit in
queue for longer than 10% of the time they spend executing. Symmetric
to DBX-WASTE-008 but opposite-direction.

**Why warning.** Under-provisioning is also waste (slower analyst time
costs more than the marginal warehouse cluster).

**Serverless behavior.** Serverless SQL warehouses also report
`queued_overhead_ms` in `/sql/history/queries`, so the queue-share
signal is meaningful — but the remediation differs: on serverless you
adjust `max_num_clusters` (the auto-stop and warm-pool behavior is
managed). When the warehouse is serverless and the rule fires, the
suggestion is to raise `max_num_clusters`; "step size up" is not
applicable.

**Detection.**

The signal is the **p95 of per-query queue-share**, not a binary count
of queries with any queue time. The field name in
`/sql/history/queries` is **`queued_overhead_ms`** (the catalog and the
evaluator must agree on this name; earlier drafts mis-spelled it as
`queued_overload_time_ms`).

```
inputs:
  warehouse_id
  queue_share_threshold = 0.10
  exec_time_floor_ms = 1000              # divide-by-noise guard
  min_queries_required = 200

queries = /api/2.0/sql/history/queries (14d, warehouse_id=...)
if len(queries) < 200: skip with reason

# Per-query share (continuous value, not a 0/1 indicator).
for q in queries:
    # Check field presence ("queued_overhead_ms" in metrics dict), NOT
    # a value > 0 check. Zero is a legitimate observation (the query
    # did not queue); a `<= 0` fallback would override it with
    # (total_time_ms - execution_time_ms), which includes planning and
    # result-fetch overhead (50-500ms typical) -- not queue time.
    if "queued_overhead_ms" in q.metrics:
        queue_time_ms = q.metrics.queued_overhead_ms        # may be 0
    else:
        queue_time_ms = max(q.metrics.total_time_ms - q.metrics.execution_time_ms, 0)
    exec_time_ms  = q.metrics.execution_time_ms
    share = queue_time_ms / max(exec_time_ms, exec_time_floor_ms)

p95_share = percentile(share across queries, 95)

# The threshold is on the p95 of the continuous share, not on a count.
if p95_share > 0.10:
    fire DBX-WASTE-009
```

Implementation note: do **not** implement this as
`count(q where q.queued_overhead_ms > 0) / total`. A warehouse with
many queries each spending 1ms in queue would trip a binary count but
not represent real queueing pressure. The p95 of the continuous share
is what we want.

**Edge cases that should NOT fire.**

- Warehouse `max_num_clusters == 1` and `enable_serverless == False`:
  scale-out is disabled; queueing is structural. Emit but tag the
  remediation as "size up" rather than "raise max_num_clusters".
- Fewer than 200 finished queries: skip.
- The queue-share denominator is stabilized for every warehouse by
  computing share against a floor of 1000ms instead of raw exec_time,
  and the rule unconditionally also requires absolute queue p95 to
  exceed 2000ms before firing. This 2000ms absolute floor is an
  always-on noise-suppression gate, not a short-query special case:
  even on long-query workloads, an absolute queue of ~1.5s sits inside
  the percentile error bars and isn't meaningfully distinguishable
  from "no real queueing pressure." Applying the gate to all
  warehouses keeps the rule from firing on workloads where the p95
  share statistic is technically elevated but the underlying queue
  time is too small to act on.

**Worked example.** Warehouse `wh-bi`, size `Small`,
`max_num_clusters: 2`. 14d of history, 4,200 queries. p95 queue share
= 0.18 (queue time is 18% of exec time). Fires. Remediation: raise
`max_num_clusters` to 4, or step size up to `Medium` (classic only —
on serverless, raise `max_num_clusters`).

**Remediation.** Raise `max_num_clusters` or step warehouse size up
one tier (classic). On serverless: raise `max_num_clusters`.
**Suggestion only.**

---

## DBX-WASTE-010 — dbt target points at all-purpose cluster for scheduled runs

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Rule.** A dbt target intended for scheduled / CI execution (`prod`,
`ci`, `scheduled`, anything not in `DEV_TARGET_NAMES`) resolves its
`http_path` to an all-purpose cluster instead of a job cluster or SQL
warehouse. All-purpose clusters are billed at a much higher DBU rate
than job clusters for the same work.

**Why error.** This is the one rule with a directly attributable dollar
delta and a clear contract violation against DBX-COMPUTE-001
(execution-compute standards). It fails the skill's exit-non-zero gate.

**Serverless behavior.** The rule fires the same way regardless of the
org's serverless preference: pointing a scheduled dbt target at an
all-purpose cluster is always wrong. The correct remediation is one
of (in priority order):
1. Lakeflow Jobs Serverless task (default for new work),
2. A SQL warehouse endpoint (preferably serverless),
3. A classic job cluster bound to the dbt task.

All-purpose is never the right answer for scheduled execution.

**Detection.**

```
inputs:
  profiles.yml - all targets
  http_path_resolver - see dbt-config-audit.md "Resolving http_path"

DEV_TARGET_NAMES = {"dev", "developer", "local"}
scheduled_target_names = {t for t in targets if t.name not in DEV_TARGET_NAMES}

for target in scheduled_target_names:
    resolved = resolve(target.http_path)
    # `resolved.kind` is "warehouse" | "cluster" | "unresolved"; an
    # additional cluster_kind step (job_cluster vs all_purpose_cluster)
    # requires /clusters/get, which the collector does NOT fetch today.
    if resolved.kind != "cluster":
        continue
    cluster_kind = audit.resolved_compute[resolved.cluster_id].kind
        if available, else None
    if cluster_kind == "all_purpose_cluster":
        # Confirmed waste; severity = error, confidence = high.
        fire DBX-WASTE-010 (error)
    elif cluster_kind == "job_cluster":
        continue  # not waste
    else:
        # cluster_kind unresolvable: surface as warning, not error,
        # with confidence=low and an evidence note explaining the gap.
        # This avoids shipping false-positive `error`-severity findings
        # that would fail CI for every cluster-path dbt target.
        fire DBX-WASTE-010 (warning, confidence=low)
```

**Edge cases that should NOT fire.**

- Target name in `DEV_TARGET_NAMES` (`dev`, `developer`, `local`):
  interactive / developer usage where all-purpose is appropriate. Skip.
- `http_path` is templated with an environment variable we cannot
  resolve at scan time: emit `info`-severity diagnostic instead of
  `error` (we can't confirm waste, but flag it for the user).
- Resolver returns `warehouse` or `job_cluster`: out of scope, no
  finding.

**Worked example.** `profiles.yml` has target `prod` with
`http_path: /sql/protocolv1/o/123/0125-abcd-pqrs45`. Resolver
classifies `0125-abcd-pqrs45` as all-purpose (the cluster's
`cluster_source` is `UI` and `data_security_mode` is `SINGLE_USER`).
Fires as `error`.

**Remediation.** Repoint the target's `http_path` to (in preference
order) a Lakeflow Jobs Serverless task, a serverless SQL warehouse, or
a job cluster's endpoint referenced from a DAB job. **Suggestion only**
— the right replacement depends on workload shape and is out of band;
the skill shouldn't pick for the user.

---

## Cross-references

- The DBR-version interactions in DBX-WASTE-007 cite Databricks'
  documented AQE defaults; see the optimize-compute skill's
  `run-history-signals.md` for which endpoints provide the version
  string.
- The `http_path` resolution rule in DBX-WASTE-010 is fully described
  in the optimize-compute skill's `dbt-config-audit.md` under
  "Resolving `http_path`". The two documents agree on classification
  labels (`job_cluster`, `all_purpose_cluster`, `warehouse`,
  `unresolved`).
- For org-wide compute posture (serverless-first, all-purpose
  prohibition for production), see `compute.md` (DBX-COMPUTE-001,
  DBX-COMPUTE-006) and `workflow.md`.
- When a finding here overlaps with an adjacent skill (static YAML
  smells, raw SQL issues, cluster lifecycle), see the optimize-compute
  skill's `composition-with-adjacent-skills.md` for the routing rule.
