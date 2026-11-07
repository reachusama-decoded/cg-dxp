# SQL warehouse sizing — process, not lookup table

Authoritative source: [Databricks docs — SQL warehouse sizing, scaling, and queuing behavior](https://docs.databricks.com/aws/en/sql/admin/warehouse-sizing).

## Core guidance — read the Databricks quote in context

Databricks-published:

> **"Start with a single larger warehouse and let serverless features manage concurrency and performance. It is usually more efficient to size down if necessary than to start small and scale up."**

Important context: that guidance is positioned for **concurrency**-driven workloads — multiple queries/users hitting the warehouse where IWM (Intelligent Workload Management) needs capacity to manage the workload. Starting small there forces queries into queue while autoscaling catches up.

**For Catalyst's most common workload — a single dbt run with one connection** — that concurrency overhead doesn't apply. Starting small (X-Small or 2X-Small) is fine; scale up only if you observe **spill-to-disk** in the query profile.

## Two sizing modes (apply the right one)

| Workload shape | Starting strategy | Up-scale signal |
|---|---|---|
| **Single dbt run / batch transform** — one connection, sequential queries | **Start small (X-Small or 2X-Small)** | Spill to disk in query profile → bump up |
| **High-concurrency dashboards / BI / multi-tenant query** — many users at once | **Start larger (Small to Medium)** per Databricks guidance — gives IWM room to manage concurrency, not just performance | Peak Queued Queries consistently > 0 → either size up OR increase max-cluster-count |

In both cases, **size DOWN** if utilization stays low for 15+ minutes (or let serverless autoscaler do it).

## Indicators the size is wrong (Databricks-published)

Check these in the warehouse monitoring page + query profile:

| Indicator | Where to find it | Action |
|---|---|---|
| **Bytes spilled to disk** | Query profile of a representative query | Size UP (cluster size too small) |
| **Peak Queued Queries** consistently > 0 | Warehouse monitoring tab | Size UP **or** increase max-cluster-count |
| **Low utilization for 15+ consecutive minutes** | Warehouse monitoring tab | Size DOWN (or let autoscaler do it on serverless) |
| **Queue wait > 5 min** | Query history | Triggers scale-up automatically; if persistent, size UP |

## Benchmarking methodology — one run is not enough

A single run at one size is **not sufficient** to pick a warehouse size. Caching effects, cold-vs-warm performance, and the cost/performance trade-off all require multiple measurements at multiple sizes.

### Run at multiple sizes, multiple times each

Pick at least **three sizes that bracket your guess** (e.g., if you think Small is right: also benchmark X-Small below and Medium above). For each size:

1. **Run cold** (first run after warehouse start, no Spark/disk/result cache). This is the worst-case runtime; the only run you can fully trust to reflect compute capacity.
2. **Run 3-5 more times** in succession. Subsequent runs may hit:
   - **Spark caches** (data fetched into executor memory)
   - **Disk cache** (data from cloud storage cached on cluster SSD)
   - **Result cache** (identical query within a short window — Databricks may return cached results)
   These give a warm-cache picture of steady-state performance, NOT compute capacity.
3. **Note the spread** — large variance run-to-run means the warehouse is contention-bound or the data layout is changing under it. Investigate before sizing decisions.

### Watch caching changes performance — don't be fooled by the happy path

A single "the second run was fast" measurement is meaningless if cache made it fast. For dbt-run-shaped batch workloads:

- **First run after a deploy** — likely cold; representative of worst case.
- **Subsequent daily runs** — warm; what most production runs look like.
- **Run after a data refresh** — partially cold (changed partitions); the realistic steady state.

For **interactive / dashboard** workloads, warm-cache performance is what users see most of the time, so it's a more relevant signal. But **don't rely on warm-cache numbers to size for SLA** — when a warehouse restarts (auto-stop fires), the first user request after that hits cold.

### Cost vs performance — compute the actual dollar/runtime trade-off

Each t-shirt size up is approximately **2x the cost per minute**. But the size up may give you anything from **2x faster** (well-parallelizable workloads) to **~no improvement** (single-threaded bottleneck, I/O-bound, or already-saturated workload).

Compute it explicitly:

```
cost = size_cost_per_minute * runtime_minutes
```

The **right size is the one that gives the best cost/runtime point relative to workload importance**:

- **Critical SLA workload** (downstream consumers waiting, missing SLA has real impact) → bias UP for predictable runtime even if cost-per-run is higher.
- **Scheduled batch with loose deadlines** → bias DOWN for lower cost-per-run even if runtime is longer (it runs at 2am, nobody cares).
- **Exploratory analytics** → smallest size that gets the job done; cost dominates.

### Understand resource constraints, not just runtime

A faster wall-clock at a bigger size isn't always evidence the bigger size is "right." Check **what's actually bottlenecking**:

| Bottleneck | Signal in query profile / metrics | Right action |
|---|---|---|
| **CPU bound** | High CPU utilization, low memory utilization, runtime scales ~linearly with workers | Size UP (more cores) |
| **Memory bound** | Bytes spilled to disk; OOMs in driver/executor logs | Size UP (more memory) |
| **I/O bound** | Low CPU + memory utilization; long time in shuffle / scan | Size up gives modest gain; consider partitioning / clustering changes or scaling OUT |
| **Skew bound** | Tasks-per-stage uneven runtime; one straggler | Size up doesn't help; fix the skew (better partitioning, salting, broadcast hints) |
| **Result-cache-dominated** | Subsequent runs ~instant, first run normal | Sizing isn't the variable; production sizing should be based on cold-run perf |

If the bottleneck isn't compute capacity, **don't pay for a bigger size** — the dollars go to idle headroom.

### Bare minimum benchmark protocol

For locking a production size:

1. Run cold at 3 sizes spanning your guess.
2. Run 3 times warm at each.
3. Inspect query profile at each for the bottleneck signal in the table above.
4. Compute total $$/run for each (size_cost_per_min × cold_runtime AND × warm_runtime).
5. Pick the smallest size that meets the SLA at *cold* runtime, biased UP only if the workload is SLA-critical.
6. Document the chosen size + the 3-size comparison + the bottleneck observed in `.catalyst-build.yml#warehouse_sizing_rationale`. This is auditable later when someone asks "why are we paying for Medium?"

## For concurrency, scale OUT not UP (Databricks-published)

For high-concurrency dashboard workloads, **increase max-cluster-count, do not increase t-shirt size**. Each cluster handles ~10 concurrent queries (fixed on classic/pro; may vary on serverless).

Max queue depth: **1,000 queries** for all warehouse types.

## Cluster size table (classic/pro warehouses; serverless instance types may differ)

| Cluster size | Driver | Worker count |
|---|---|---|
| 2X-Small | i3.2xlarge | 1 |
| X-Small | i3.2xlarge | 2 |
| Small | i3.4xlarge | 4 |
| Medium | i3.8xlarge | 8 |
| Large | i3.8xlarge | 16 |
| X-Large | i3.16xlarge | 32 |
| 2X-Large | i3.16xlarge | 64 |
| 3X-Large | i3.16xlarge | 128 |
| 4X-Large | i3.16xlarge | 256 |
| 5X-Large (Public Preview) | i3.16xlarge | 512 |

Each size up is approximately 2x the cost.

## Autoscaling (classic/pro warehouses only — serverless uses IWM)

| Estimated load time | Clusters added |
|---|---|
| 2-6 min | +1 |
| 6-12 min | +2 |
| 12-22 min | +3 |
| 22+ min | +3 plus +1 per additional 15 min |

Plus: queue wait > 5 min triggers scale-up; load low for 15 consecutive minutes triggers scale-down to peak needs.

## Auto-stop

- **Serverless SQL warehouse default**: 10 minutes
- Lower for cost-sensitive sandbox
- Higher for interactive dev where re-cold-starting is friction
- Production scheduled workloads can keep the default — the wrapper job starts/stops the warehouse via the bundle, so idle time is bounded anyway

## Channel selection (Databricks-published)

- **`CURRENT`** — production stability; pin here for all production warehouses
- **`PREVIEW`** — new features earlier; use only for testing with rollback plan
- Per `DBX-COMPUTE-002` (RFD 0008) — pin explicitly, don't leave auto-pick

## Catalyst-recommended starting points by environment (opinion — benchmark before locking)

**These are Catalyst-specific starting points, NOT Databricks-published.** Always benchmark with a representative query at production data volume before locking in a size.

| Environment | Workload shape | Starting size | Auto-stop | Max clusters | Channel |
|---|---|---|---|---|---|
| Production — scheduled dbt run | single connection, batch | **Small** | 10 min | 1 | CURRENT |
| Production — interactive / BI dashboards | high concurrency | **Medium** (start larger per Databricks "start larger" guidance) | 30 min | 4-8 | CURRENT |
| Dev | single developer iteration | **X-Small** | 30 min | 1 | CURRENT |
| Sandbox | exploratory | **2X-Small** | 5 min | 1 | CURRENT |

**Default starting position is small.** Scale up based on observed signals:

- **Spill to disk** in query profile → bump up one size
- **Peak Queued Queries > 0 consistently** (concurrency workloads only) → bump up size OR increase max-cluster-count
- After running representative queries against production-shape data, adjust based on the indicators in the previous table.

## How `/configure-sql-warehouse` uses this

1. Read `.catalyst-build.yml#mode` (prototype / production / lift-and-shift) and infer environment.
2. Apply the Catalyst-recommended starting point from the table above.
3. Document the chosen size + reasoning in `.catalyst-build.yml#warehouse_sizing_rationale`.
4. Prompt the user: "After your first production run, check the warehouse monitoring page for Peak Queued Queries and bytes-spilled-to-disk. Adjust per the indicator table."

## What NOT to do

- Don't pick a size from a public-internet "SQL warehouse sizing for X-rows" article. They're benchmark- and query-specific; no general lookup table is correct across workloads.
- Don't conflate Databricks's "start larger" guidance (which is for concurrency-driven workloads) with single-dbt-run sizing. For a single connection workload, start small and use spill-to-disk as the up-scale signal.
- Don't scale UP for concurrency. Scale OUT (max-cluster-count) for concurrency, UP for query complexity / data size.
