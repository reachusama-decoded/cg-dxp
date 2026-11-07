# Run-history Signals

How `optimize-compute` turns Databricks API responses into the signals
its rules evaluate. Every signal in `findings-catalog.md` (peak worker
count, floor time share, gap share, etc.) has exactly one canonical
derivation here. Worker C's `evaluate_findings.py` reads this file as
the contract for what fields to pull and how to reduce them.

## Signal -> endpoint -> JSON path -> normalization

| Signal | Endpoint | JSON path | Normalization rule |
|---|---|---|---|
| `cluster.autoscale.min_workers` | `GET /api/2.0/clusters/get?cluster_id=...` | `.autoscale.min_workers` | Integer. Treat absent + present `num_workers` as fixed-size cluster (no autoscale signals apply). |
| `cluster.autoscale.max_workers` | `GET /api/2.0/clusters/get?cluster_id=...` | `.autoscale.max_workers` | Integer. Required for DBX-WASTE-001. |
| `cluster.spark_conf` | `GET /api/2.0/clusters/get?cluster_id=...` | `.spark_conf` | Object. Keys lowercased for matching against `watched_keys` set; values left as-is. |
| `cluster.spark_version` | `GET /api/2.0/clusters/get?cluster_id=...` | `.spark_version` | Parse leading integer before first `.` as `dbr_major_version`. ML / Photon variants (`13.3.x-cpu-ml-scala2.12`) parse the same way. |
| `cluster.driver_node_cores` | `GET /api/2.0/clusters/get?cluster_id=...` | `.driver_node_type_id` | Look up cores via the node-type catalog cached in `_lib`; fall back to 4 if unknown. |
| `cluster.worker_node_cores` | `GET /api/2.0/clusters/get?cluster_id=...` | `.node_type_id` | Same lookup as driver. |
| `cluster.kind` | `GET /api/2.0/clusters/get?cluster_id=...` | `.cluster_source`, `.data_security_mode`, presence of `.job_id` | Classify: `JOB` source -> `job_cluster`; `API`/`UI` source without `.job_id` -> `all_purpose_cluster`; warehouses are not visible here (separate endpoint). |
| `run.tasks[*].start_time` | `GET /api/2.1/jobs/runs/get?run_id=...` | `.tasks[*].start_time` | Milliseconds since epoch. Skip tasks with start_time == 0 (queued / skipped). |
| `run.tasks[*].end_time` | `GET /api/2.1/jobs/runs/get?run_id=...` | `.tasks[*].end_time` | Milliseconds since epoch. If 0 for a still-running run, exclude run from analysis. |
| `run.start_time`, `run.end_time` | `GET /api/2.1/jobs/runs/get?run_id=...` | `.start_time`, `.end_time` | Used for total wall-clock; skip in-flight runs. |
| `events[].worker_count` | `POST /api/2.0/clusters/events` (type `RESIZING`, `UPSIZE_COMPLETED`) | `.events[].details.current_num_workers` | Build a stepwise timeline. Forward-fill: between events, worker count is the last reported value. Initial value = `cluster.autoscale.min_workers` (or `num_workers` for fixed-size). DO NOT read `.details.max_workers` here -- it's the configured ceiling (echoes the cluster spec), not an observation. DO NOT read `.details.target_num_workers` either -- it's autoscaler intent, not a realized count. |
| `events[].upscale_pressure` | `POST /api/2.0/clusters/events` (type `AUTOSCALING_STATS_REPORT`) | `.events[].details.target_num_workers - .events[].details.current_num_workers` (clip to >=0) | Used by DBX-WASTE-002 edge-case exclusion: high pressure means the floor is doing useful warm work. |
| `warehouse.size` | `GET /api/2.0/sql/warehouses/{id}` | `.cluster_size` | String enum: `2X-Small`, `X-Small`, `Small`, `Medium`, `Large`, `X-Large`, `2X-Large`, `3X-Large`, `4X-Large`. |
| `warehouse.max_num_clusters` | `GET /api/2.0/sql/warehouses/{id}` | `.max_num_clusters` | Integer. |
| `warehouse.enable_serverless` | `GET /api/2.0/sql/warehouses/{id}` | `.enable_serverless_compute` | Boolean. |
| `warehouse.cluster_count_timeseries` | `POST /api/2.0/sql/warehouses/{id}/events` | `.events[]` where `event_type` in `STARTING`, `RUNNING`, `STOPPING`, `SCALED_UP`, `SCALED_DOWN`; read `.details.cluster_count` from each | Forward-fill the cluster_count samples on event timestamp to build a per-time series; the average is duration-weighted across `[ts_i, ts_{i+1})` intervals. `CLUSTER_CREATED` / `CLUSTER_TERMINATED` are NOT valid for this endpoint -- those belong to `/api/2.0/clusters/events`. |
| `query.duration_ms` | `GET /api/2.0/sql/history/queries` (filter by warehouse_id, status=`FINISHED`, last 14d, page) | `.res[].duration` | Milliseconds. Used for p95 wall-clock. |
| `query.execution_time_ms` | `GET /api/2.0/sql/history/queries` | `.res[].metrics.execution_time_ms` | Milliseconds. Numerator/denominator pair with the next row. |
| `query.queued_overhead_ms` | `GET /api/2.0/sql/history/queries` | `.res[].metrics.queued_overhead_ms` | Milliseconds. Falls back to `total_time_ms - execution_time_ms` **only when the field is absent from the `metrics` dict**, not when the value is `0` -- zero is a legitimate "this query did not queue" observation; the fallback differs from queue time by 50-500ms of planning / result-fetch overhead and would inflate the share artificially. |

## Derived signals (computed in `_lib`, not raw fields)

| Derived signal | Inputs | Formula | Used by |
|---|---|---|---|
| `observed_peak_workers` | events worker_count timeline, run.start_time, run.end_time | `max(worker_count(t)) for t in [run.start_time, run.end_time]` per run; then `max` across runs. | DBX-WASTE-001 |
| `floor_seconds_share` | worker_count samples (from RESIZING / UPSIZE_COMPLETED), autoscale.min_workers | Sort samples on timestamp; forward-fill between consecutive samples; `sum(dt where forward-filled count == min_workers) / sum(dt total)`. Duration-weighted, NOT event-count-weighted. | DBX-WASTE-002 |
| `inter_task_gap_share` | run.tasks[*].start_time, end_time | per run: `sum(max(0, next_start - prev_end)) / (run.end_time - run.start_time)`; mean across runs. | DBX-WASTE-003 |
| `runtime_growth_normalized` | last 14 runs of a single model's task duration | linear regression slope * (14 runs) / `runs[0].duration`. | DBX-WASTE-006 (withdrawn; signal retained for reference) |
| `p95_query_duration_seconds` | query.duration_ms across window | `percentile_95(durations) / 1000`. | (unused; reserved for future warehouse-size signals) |
| `p95_queue_share` | query.execution_time_ms, queued_overhead_ms | per query: `queued / max(exec, 1000ms)`; `p95` across queries. | DBX-WASTE-009 |
| `avg_cluster_count_share` | warehouse events timeline, max_num_clusters | duration-weighted mean of cluster count divided by max_num_clusters. | DBX-WASTE-008 |

## `MIN_RUNS_REQUIRED` gate: 10 runs OR 7 calendar days

The minimum-runs gate referenced throughout `findings-catalog.md`
(default `min-runs-required = 10`) is not a flat 10-run threshold.
The effective gate is a disjunction:

```
sufficient_history =
    runs_in_window >= MIN_RUNS_REQUIRED
    OR (max(run.start_time) - min(run.start_time)) >= 7 calendar days
```

Fire the runtime rules when `(runs >= 10) OR (span >= 7 calendar
days)`. The first arm covers high-frequency jobs (hourly, daily) -
they accumulate enough runs quickly that the run count alone is
adequate evidence. The second arm covers low-frequency jobs (weekly,
monthly) that wouldn't reach 10 runs in any reasonable window but
have nonetheless been observed across enough wall-clock time to span
a normal cycle. Worker C encodes this disjunction in
`evaluate_findings.py`.

**Rationale.** Requiring both arms is overkill in practice. A daily
job with 10 runs in 10 days IS enough evidence about steady-state
workload shape - the calendar span comes "for free" with the run
count at daily frequency. Conversely, a weekly job that has run 5
times over 35 days has plenty of calendar coverage to characterize
its workload even though it cannot satisfy a `runs >= 10` arm
without waiting two more months. The OR gate admits both classes of
job; an AND gate would lock out the low-frequency class entirely.

The catalog's per-rule refusal messages should explain which arm
failed when the gate refuses: e.g. "DBX-WASTE-001 not evaluated: 6
runs observed and span only 4 days; need 10 runs or a 7-day span".

## 30-day window and 200-run cap rationale

Two limits bound the API spend and the analysis token budget:

- **30 days.** Three reasons. (1) Most Catalyst-tracked jobs run
  daily or more often, so 30 days yields >=10 runs - enough for the
  `min-runs-required` gate on DBX-WASTE-001/002/003. (2) Older runs
  reflect stale workloads (recent schema changes, source-row-count
  shifts) and contaminate the peak / gap statistics. (3) The
  `/jobs/runs/list` endpoint paginates at 25 per page; 30 days
  typically fits within 8 pages for a daily job, which is comfortably
  below the cap.
- **200 runs.** Hard ceiling regardless of date span. Prevents a job
  that runs every five minutes from pulling 8,640 runs in 30 days and
  exploding both API quota and the token budget when summarizing into
  the model context. 200 runs is empirically large enough to stabilize
  the per-cluster peak worker count signal (variance becomes
  monotonically small past ~50 runs in our tests on internal jobs).
- **Pagination.** Pull pages in order most-recent-first; stop when
  either (a) `start_time < now - 30d` for the next page, or (b) we
  have 200 runs in hand, whichever is first. Do not deduplicate by
  `run_id` because runs are append-only.

### Token-budget mitigations

- Cache `/clusters/events` responses by `(cluster_id, start_time,
  end_time)` for the duration of the skill run. A single 30-day pull
  is reused across all jobs touching that cluster.
- Aggregate query history into per-warehouse summary stats (count,
  p50, p95, mean queue share) before passing to the LLM context. Do
  not paste raw query rows; pass the summary.

## Insufficient-data behavior

The runtime-waste rules degrade gracefully when run history is thin.
The skill must refuse to fire and explain why; it must not "ride the
edge" with weak evidence.

| Rule | Min data required | Refusal message |
|---|---|---|
| `DBX-WASTE-001` | >=10 runs OR >=7-day span in window | "DBX-WASTE-001 not evaluated: only N runs and S-day span (need 10 runs or a 7-day span)." |
| `DBX-WASTE-002` | (>=10 runs OR >=7-day span) + >=1 `AUTOSCALING_STATS_REPORT` event | "DBX-WASTE-002 not evaluated: autoscale event history insufficient." |
| `DBX-WASTE-003` | >=10 multi-task runs OR >=7-day span of multi-task runs | "DBX-WASTE-003 not evaluated: not enough multi-task runs (need 10 or a 7-day span)." |
| `DBX-WASTE-004` | profiles.yml resolvable + cluster identified | "DBX-WASTE-004 not evaluated: could not resolve `http_path` to a cluster." |
| `DBX-WASTE-005` | manifest.json merged + >=1 query observed (info-only, no percentile gate) | "DBX-WASTE-005 not evaluated: no manifest merged or no query history." |
| `DBX-WASTE-007` | cluster.spark_version >= 13 | "DBX-WASTE-007 not evaluated: cluster DBR < 13; defaults differ." |
| `DBX-WASTE-008` | >=2 events spanning >=7 days from /sql/warehouses/{id}/events, non-serverless | "DBX-WASTE-008 not evaluated: <specific gate reason>." |
| `DBX-WASTE-009` | >=200 queries in 14d | "DBX-WASTE-009 not evaluated: only N queries in 14d (need 200)." |
| `DBX-WASTE-010` | profiles.yml + http_path resolvable | "DBX-WASTE-010 not evaluated: target's http_path is templated; could not resolve." |

Refusal messages are emitted as `info`-severity "diagnostic" records
in the report, distinct from real findings. They are not failures -
they are explicit "we looked and decided not to opine". The CI gate
treats them as zero-severity.

## API authentication and scope

- All endpoints accept a Databricks PAT or OAuth M2M token with
  workspace-scope `read` permissions. The skill never writes; even
  in `apply` mode the writes go to local files, not the workspace.
- `/api/2.0/sql/history/queries` requires the user to have query
  history visibility for the warehouse. If 403, the skill emits a
  diagnostic and skips DBX-WASTE-005/008/009 for that warehouse.
- `/api/2.0/clusters/events` requires the user to have at least
  `CAN_ATTACH_TO` on the cluster. If 403, skip DBX-WASTE-001/002.
