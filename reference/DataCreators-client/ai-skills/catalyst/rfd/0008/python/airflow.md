# PY-AIRFLOW: Airflow on Astronomer

Standards for paved-path Airflow DAGs running on Astronomer. These rules are
the canonical, ID-keyed home for the decisions argued in RFD 0011 — read that
RFD for the *why* and the cross-RFD bindings; read here for *what to do*. Rules
whose **Linter** is `assert_dag_compliant` are enforced by the shared structural
checker that runs in CI for every PR; the rest are secret/style lints, the
pytest integrity test, or PR-review items.

## PY-AIRFLOW-001 — Derive partitions and paths from the processing window

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory (PR review; idempotency is not statically checkable)

**Decision.** Re-running a DAG for the same logical date MUST produce the same
end state; replaying an Asset event MUST NOT double-write, double-emit, or
advance external state twice. Derive every partition, filter, and output path
from the run's **processing window**, never from `datetime.now()`. The window
source depends on the trigger:

- **Asset-driven DAGs** (the default, PY-AIRFLOW-019): take the window from the
  triggering event, not from `data_interval_*`. For asset-triggered runs Airflow
  collapses `data_interval_start`/`_end` to `logical_date` (a zero-width window),
  so templating those is meaningless. Read the event timestamps/URIs from
  `context["triggering_dataset_events"]` via the shared
  `get_processing_window(context)` helper in `edo_airflow_lib`.
- **Cron DAGs:** use `{{ data_interval_start }}` / `{{ data_interval_end }}` —
  the window the run is responsible for (`data_interval_start` *equals*
  `logical_date`; it is not a lag). For **sub-daily** schedules key on the full
  timestamp (`{{ data_interval_start | ts_nodash }}`), not `{{ ds }}`, which
  truncates to the date and collides across same-day runs.
- **Rolling windows** (e.g. "last 7 days"): carry the window in the upstream
  Asset's `extra` payload, or compute it inside the helper — never from
  wall-clock time.

The rule is the *property* — the write is idempotent against the window — and
the mechanism varies by sink:

- Unity Catalog (Delta) writes use `MERGE` or `INSERT OVERWRITE` keyed on the
  processing window, never bare `INSERT`.
- **OLTP sinks** (Postgres/SQL Server) have no `INSERT OVERWRITE`; use an upsert
  (`MERGE` / `ON CONFLICT`) or delete-by-window-then-insert.
- **Append-only audit/event tables** are legitimately append-only — idempotency
  is the consumer's dedupe responsibility, not the write's.
- **CDC pipelines** apply DELETE events as hard deletes, not MERGE upserts (a
  MERGE would resurrect deleted rows).
- S3 writes land under a partition path derived from the window —
  `s3://.../dt={{ data_interval_start | ts_nodash }}/` for sub-daily,
  `dt={{ ds }}/` only for daily-or-coarser — and overwrite that partition on
  rerun.

Prefer the processing window over an external checkpoint table or watermark
column: a rerun for the same window re-reads the same data automatically, with no
manual checkpoint reset. Where an external checkpoint is unavoidable (e.g. Kafka
consumer offsets), update it *after* the data write commits, and make the update
itself idempotent against the window. Gate side effects (Teams messages, ticket
creation) on a "first-success" check or route them through a deduplicating layer.

**Why.** A DAG that is not idempotent can double-insert rows, advance an external
checkpoint, or leave Unity Catalog and S3 out of sync when re-run for the same
logical date. At thousands-of-DAGs scale operators cannot rely on tribal
knowledge to know which DAGs are safe to rerun.

**Exception.** Append-only audit/event sinks push idempotency to the consumer
(dedupe on the window key); CDC DELETE handling is a hard delete, not a MERGE.

**Example:**
```python
# Bad — keyed on the wall clock; a rerun writes a different partition
out = f"s3://lake/positions/dt={datetime.now():%Y%m%d}/"

# Good — keyed on the processing window; a rerun overwrites the same partition
@task
def write_positions(**context):
    start, _end = get_processing_window(context)   # asset event or data_interval
    out = f"s3://lake/positions/dt={start:%Y%m%dT%H%M%S}/"
    df.write.mode("overwrite").parquet(out)
```

## PY-AIRFLOW-002 — Pin `start_date` to a static UTC datetime

**Severity:** error
**Since:** v0.1.0
**Linter:** `assert_dag_compliant`

**Decision.** `start_date` is a fixed `datetime` literal in UTC. Never use
`days_ago(...)` or `datetime.now()`.

**Why.** A dynamic `start_date` moves the first schedulable interval every time
the DAG is parsed, producing unpredictable scheduling and broken catchup.

**Exception.** None.

**Example:**
```python
# Bad — moves on every parse
start_date = days_ago(1)

# Good — fixed UTC literal
start_date = datetime(2026, 1, 1, tzinfo=timezone.utc)
```

## PY-AIRFLOW-003 — Declare a retry policy on every task

**Severity:** error
**Since:** v0.1.0
**Linter:** `assert_dag_compliant` (`retries` set and ≤ 5)

**Decision.** Every task declares a retry policy appropriate to the failure modes
it can experience. The default: `retries=3`, `retry_delay=timedelta(minutes=5)`,
`max_retry_delay=timedelta(minutes=30)`. Transient failures (HTTP timeouts,
throttling, cold-start cluster errors) propagate normally and rely on this
policy. Set it in `default_args` when it is the same across tasks.

**Why.** Transient cloud failures are routine and a rerun of the failed task is
usually all that's needed. Without a shared retry policy those failures land on
operators instead of self-healing, and the overhead scales linearly with DAG
count. The checker also bounds `retries ≤ 5`, because a high retry count masks
deterministic failures rather than failing fast (PY-AIRFLOW-016).

**Exception.** None.

**Example:**
```python
default_args = {
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
}
```

## PY-AIRFLOW-004 — Use exponential backoff for retries

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Set `retry_exponential_backoff=True` alongside the retry policy so
successive retries wait progressively longer, up to `max_retry_delay`.

**Why.** Linear retries against a throttled or cold-starting dependency hammer it
at a fixed cadence; exponential backoff gives the dependency time to recover and
reduces synchronized retry storms across DAGs.

**Exception.** None.

## PY-AIRFLOW-005 — Declare compute via approved T-shirt tiers

**Severity:** error
**Since:** v0.1.0
**Linter:** `assert_dag_compliant` (valid tier; `xl` justified)

**Decision.** Every task declares the compute it expects; no task runs on
"whatever the default is."

- DAG-level `default_args` set `pool`, `queue`, and `executor_config` for the
  common case; tasks override when they need more or less.
- Databricks jobs declare a named job-cluster spec per task, sourced from the
  approved T-shirt profiles `xs`, `s`, `m`, `l`, `xl` in `edo_airflow_lib`. Each
  profile is an **autoscaling min/max envelope** (size, node type, autoscaling
  bounds), not a fixed point size: pick the tier whose envelope covers normal
  load and let autoscaling absorb predictable spikes (e.g. month-end volume)
  *within* the tier rather than jumping to a larger profile. `xl` requires a
  one-line justification in `doc_md`; CI flags an unjustified `xl`
  (PY-AIRFLOW-022).
- dbt tasks declare the warehouse size and concurrency they expect.
- KubernetesExecutor tasks declare `request_cpu`, `request_memory`, and
  `limit_memory` explicitly; no unbounded pods.

`generate-dag` MUST emit these same five tier names — its current four-tier
`xs/sm/md/lg` set (no `xl`) is reconciled to these five.

**Why.** Worker slots and cluster spend are the scarce resources at
thousands-of-DAGs scale. Tasks submitted to whichever pool or cluster the author
copied from a neighbor produce noisy neighbors and oversized clusters that scale
poorly.

**Exception.** None. (A periodic resource-usage audit against declared size is a
tracked follow-up in RFD 0011.)

## PY-AIRFLOW-006 — Declare the schedule explicitly and set `catchup` to intent

**Severity:** warning
**Since:** v0.1.0
**Linter:** `assert_dag_compliant`

**Decision.** Every DAG declares its trigger explicitly — no implicit defaults,
no `days_ago(...)`.

- Use cron only when the trigger is genuinely temporal — calendar-bound reporting
  windows, billing cutoffs, external SLA deadlines — or when no upstream Asset is
  available to subscribe to (asset-driven is the default, PY-AIRFLOW-019).
  Document the reason in the DAG.
- Use `schedule=None` for manual-only DAGs (one-off backfills, operational
  utilities).
- `@daily` and other presets are allowed but discouraged in favor of explicit
  cron for clarity.
- `catchup` reflects intent. Use `catchup=False` for "from now forward" jobs
  (operational, polling, any DAG where missing a past interval doesn't matter).
  Use `catchup=True` when the DAG models a time series and every interval must be
  produced (daily aggregations, point-in-time snapshots). With `catchup=True`,
  also set `max_active_runs` to a bounded value (PY-AIRFLOW-018) — otherwise every
  missed interval queues at once and fires in parallel.

**Why.** Implicit scheduling defaults are a common source of surprise reruns and
gap-filling storms. Explicit declaration makes scheduling intent reviewable.

**Exception.** None.

## PY-AIRFLOW-007 — Tag every DAG with the required tag set

**Severity:** error
**Since:** v0.1.0
**Linter:** `assert_dag_compliant` (`l1_xmatters_group` allowlist; required keys present)

**Decision.** `tags` follow a `key:value` convention so tooling can parse them.
Required on every DAG:

- `l1_domain:<domain>` — primary business / data domain
- `l1_xmatters_group:<group>` — primary on-call group. Validated by
  `assert_dag_compliant` against the `xmatters_groups` allowlist in
  `edo_airflow_lib`, so a typo'd or dissolved group fails CI rather than silently
  paging nobody at 3am.
- `lifecycle_phase:<phase>` — `build`, `operate`, or `decom` (anchored to the
  RFD 0002 DPLC phases)
- `data_classification:<class>` — `internal`, `confidential`, `restricted`, or
  `public`
- `criticality:<level>` — `critical`, `high`, or `standard`. Read by Datadog's
  tag-based monitors and by support to set alert priority/routing
  (PY-AIRFLOW-008).

Required when `criticality: critical`, so SLA tooling can detect a breach
(PY-AIRFLOW-008):

- `deliver_by_day:<schedule>` — e.g. `M-F`, `daily`, `month-end`
- `deliver_by_time:<HH:MM tz>` — e.g. `23:00 ET`

Also required — MDS attribution tags, consumed for cost allocation and the DXP
catalog (a union with the set above, sharing `data_classification`):

- `owner:<email|team>`, `business_function:<function>`, `data_domain:<domain>`,
  `app_id:<mds-app-id>`

Optional: `l2_xmatters_group:<group>` and `l3_xmatters_group:<group>` for
escalation tiers. `doc_md` describes what the DAG produces, who consumes it, and
how to rerun it — the runbook entry point.

**Why.** Owner, alerting, and SLA fields only help operations if they're set
consistently on every DAG. Leave it to author discretion and a 3am failure sits
unrouted, ownership is ambiguous, and there's no shared bar for what counts as
late.

**Exception.** The `deliver_by_*` tags are required only at
`criticality: critical`.

## PY-AIRFLOW-008 — Rely on platform Datadog alerting, not a per-DAG callback

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Failure alerting to Datadog is **built into Astronomer at the
platform level** — it is **not** a per-DAG callback. DAGs do not wire an
`on_failure_callback` to Datadog, and there is no shared "Datadog dispatch
helper" on the DAG; every failure surfaces in Datadog automatically through the
Astronomer↔Datadog integration. From the Datadog alert, both the Teams
notification (Datadog→Teams integration) and any xMatters page are **manual**,
triggered by support. The `criticality`, `l1_xmatters_group`, and `deliver_by_*`
tags (PY-AIRFLOW-007) are the **context** support and Datadog's tag-based monitors
read to decide whether to notify Teams or escalate via xMatters — they are
metadata, not triggers. An author who sets `criticality: critical` should expect
a Datadog alert (not an automatic Teams message and not an automatic page) and
MUST ensure the owning team is enrolled in the platform's escalation process.
Don't roll your own `email_on_failure` or a custom alerting callback.

SLAs: you *can* still set Airflow's native `sla=` — it's harmless — but **nothing
acts on it** here: no `sla_miss_callback` is wired and we don't alert on SLA
misses, so it is effectively inert (and Airflow is reworking native SLAs in newer
versions). Don't *rely* on `sla=` for delivery SLAs; declare the delivery target
through the `deliver_by_*` tags. Monitoring those is an out-of-Airflow / Ops
responsibility (a tracked follow-up in RFD 0011). Tasks emit JSON logs through the
platform logger so log-based alerts and lineage tooling can parse them.

**Why.** A single shared alerting path that every DAG inherits is more reliable
than per-DAG callbacks an author can forget, misconfigure, or duplicate. Treating
tags as context rather than triggers keeps routing logic in one place
(Datadog/support), not scattered across DAG code.

**Exception.** Native `sla=` is allowed but inert; do not add a DAG-level Datadog
callback.

## PY-AIRFLOW-009 — No I/O at module scope

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory (the integrity test, PY-AIRFLOW-014, asserts cheap parse)

**Decision.** No imports, DB calls, or API calls at module scope; DAG parsing must
be cheap. Move work into task callables. In particular, avoid
`Variable.get("secret-name")` at module scope (PY-AIRFLOW-013): DAG parsing reads
the value on every parse cycle and risks leaking it into scheduler logs.

**Why.** The scheduler re-parses every DAG file on a short cycle. Module-scope I/O
multiplies that cost across every parse and every DAG, and turns a slow dependency
into scheduler-wide latency. The DAG file is a description of work, not the work
itself.

**Exception.** None.

**Example:**
```python
# Bad — runs on every parse cycle
rows = db.query("SELECT ...")            # module scope

# Good — runs only when the task executes
@task
def load():
    return db.query("SELECT ...")
```

## PY-AIRFLOW-010 — Prefer the TaskFlow API for new code

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Prefer `@task` / the TaskFlow API over `PythonOperator` for new
code; it collapses boilerplate and makes XCom flow explicit.

**Why.** TaskFlow removes manual XCom push/pull wiring and makes data
dependencies between tasks visible in the function signatures.

**Exception.** Existing `PythonOperator` code need not be rewritten solely for
this; operators with no TaskFlow equivalent are fine.

## PY-AIRFLOW-011 — Keep XCom to metadata, not row data

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** XCom carries metadata (paths, IDs, row counts), not row data.
Anything larger than a kilobyte lives in S3 / Unity Catalog and is passed by
reference.

**Why.** XCom is stored in the metadata DB; large payloads bloat it, slow the
scheduler, and can exceed backend size limits.

**Exception.** None.

## PY-AIRFLOW-012 — Follow the DAG ID naming convention

**Severity:** warning
**Since:** v0.1.0
**Linter:** `assert_dag_compliant`

**Decision.** DAG IDs follow `<domain>__<dataset>__<frequency>` (e.g.
`equity__positions__daily`). The `__` (double-underscore) delimiter is reserved
for this convention so DAG IDs are parseable.

**Why.** A parseable ID lets tooling group, route, and report on DAGs by
domain/dataset/frequency without a side lookup.

**Exception.** None.

## PY-AIRFLOW-013 — Resolve secrets through Connections and Variables

**Severity:** error
**Since:** v0.1.0
**Linter:** secret-scan lint

**Decision.** No credentials, tokens, or hostnames in DAG code or `default_args`.

- Use Airflow Connections (managed via the secrets backend) for every external
  system. Pass them by `conn_id` and let the operator's hook resolve the actual
  credential at runtime.
- Use Airflow Variables (also backed by the secrets backend) for tunable
  parameters that differ by environment.
- When the operator doesn't natively support a `conn_id` for what you need, fetch
  the secret *inside* the task callable (via a hook or a direct SDK call like
  `boto3.client("secretsmanager")`) so the value exists only in the worker's
  process memory for the duration of the task. Don't log it, don't push it
  through XCom.
- Avoid `Variable.get("secret-name")` at module scope (PY-AIRFLOW-009).

CI lints for hardcoded patterns (`https://`, `password=`, AWS access keys).

**Why.** Secrets in code or parse-time reads leak into version control and
scheduler logs. The secrets backend keeps credentials out of the DAG and resolves
them at runtime where they belong.

**Exception.** None.

## PY-AIRFLOW-014 — Cover every DAG with a pytest integrity test

**Severity:** error
**Since:** v0.1.0
**Linter:** pytest integrity test (CI)

**Decision.** A `pytest` integrity test imports the DAG file, asserts no errors,
and asserts `dag.test()` runs against a stub environment. Task callables with
non-trivial logic have their own unit tests; the DAG file itself does not.

**Why.** The cheapest class of failure — a DAG that doesn't import or parse —
should never reach the scheduler. The integrity test is the safety net under
PY-AIRFLOW-009's cheap-parse rule. Every DAG MUST be runnable locally
(PY-AIRFLOW-021) and covered by at least this integrity test and the structural
test (PY-AIRFLOW-022).

**Exception.** None.

## PY-AIRFLOW-015 — Emit the data-ready event only on success

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** On successful completion, the DAG publishes a data-ready event (per
RFD 0007) for each logical output dataset, keyed on the logical window. This is
what makes downstream Asset subscriptions work and what feeds lineage tooling.
Failed or partial runs MUST NOT emit. A **corrected re-run** that completes
successfully for the same window MAY re-emit — re-emission *is* the idempotent
path (downstream consumers dedupe on the window key per RFD 0007) and is the
intended mechanism for data corrections and control-plane replay. The prohibition
is on emitting from a run that did not complete, not on re-emitting a fixed
result. Use the shared event helper; don't hand-roll the payload.

**Why.** Downstream DAGs trigger off these events (PY-AIRFLOW-019). Emitting from
a failed or partial run would trigger consumers on incomplete data; never being
allowed to re-emit would make corrections impossible to propagate.

**Exception.** A corrected, successful re-run for the same window MAY re-emit.

## PY-AIRFLOW-016 — Fail fast on deterministic errors

**Severity:** warning
**Since:** v0.1.0
**Linter:** `assert_dag_compliant` (`retries ≤ 5`)

**Decision.** Deterministic failures (SQL compile errors, schema mismatches,
contract or validation failures) should fail fast rather than burn the retry
budget. Where the underlying client surfaces a distinct exception type, configure
the task to treat it as non-retriable — via `AirflowFailException` in custom code,
or operator-level `retry_on_exception` filters where the operator supports them.
Don't try to enumerate every possible deterministic error in DAG code.

**Why.** Retrying a deterministic failure just delays the inevitable while
consuming worker slots and obscuring the real error. The `retries ≤ 5` bound
(PY-AIRFLOW-022) catches the anti-pattern of masking deterministic failures behind
a high retry count.

**Exception.** Transient failures (timeouts, throttling, cold starts) should retry
normally (PY-AIRFLOW-003).

## PY-AIRFLOW-017 — Release the worker slot on long waits and bound the timeout

**Severity:** error
**Since:** v0.1.0
**Linter:** `assert_dag_compliant` (every wait `timeout` / `execution_timeout` set and ≤ 10h)

**Decision.** Tasks that spend time waiting on external state MUST release their
worker slot while they wait, and every wait sets a bounded `timeout` /
`execution_timeout`.

- Prefer deferrable operators (`*Async` variants, `Trigger`-based operators) over
  synchronous counterparts when the wait can exceed a few seconds; deferred tasks
  hand off to the Triggerer process and free the worker slot.
- Where no deferrable equivalent exists, classic sensors MUST set
  `mode="reschedule"` (not the default `mode="poke"`) so the slot is released
  between pokes.
- The timeout value is **category-matched, not a blanket default**:
  - **External-delivery sensors** (vendor file deposits, third-party APIs where
    you genuinely wait on an outside clock): ceiling of **10h** (`36000s`) — the
    DRE-derived figure that covers the real delivery window for late vendor files.
    This is a *category ceiling*, not a default for all waits.
  - **Internal-compute waits** (cross-DAG, Databricks job completion, SQL
    warehouse): set the timeout to the **upstream's actual SLA + a buffer**, not
    10h. A hung internal job held for 10h burns cluster spend and a worker slot
    for the rest of the business day before anything surfaces.
  - **Better still, avoid the wait:** if the upstream is itself an
    asset-producing DAG, subscribe to its Asset (PY-AIRFLOW-019) — no sensor, no
    timeout, no slot occupancy at all.

The checker enforces a 10h upper bound on any single wait (PY-AIRFLOW-022) so an
absurd `timeout` cannot satisfy "no unbounded waits."

**Why.** Worker slots are the scarce resource at thousands-of-DAGs scale; a sensor
or wait that holds one for hours is a slot-exhaustion incident in the making.

**Exception.** The 10h ceiling applies to external-delivery sensors;
internal-compute waits should be tighter (upstream SLA + buffer).

## PY-AIRFLOW-018 — Bound DAG parallelism

**Severity:** warning
**Since:** v0.1.0
**Linter:** `assert_dag_compliant`

**Decision.** Set `max_active_runs` and `max_active_tasks` at the DAG level to
bound worst-case parallelism. This is mandatory when `catchup=True`
(PY-AIRFLOW-006), where every missed interval would otherwise queue and fire at
once.

**Why.** Unbounded parallelism lets a single DAG — especially on a backfill or
catchup — saturate pools and starve every other DAG on the deployment.

**Exception.** None.

## PY-AIRFLOW-019 — Default to asset-driven scheduling

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Default: `schedule=Asset(...)` (or a list of `Asset`s). The DAG runs
when an upstream producer publishes new data; Airflow handles the wait, the
trigger, and the lineage — no polling sensors, no time-based guessing about when
upstream is "probably done." This is how **process dependencies** are expressed:
an upstream pipeline's completion publishes its Asset event (PY-AIRFLOW-015) and
the downstream subscribes to that event, rather than reacting to the clock. The
subscription point is the upstream data contract (RFD 0009 / ODCS).

**Why.** Reacting to data rather than the clock removes an entire class of timing
bugs (running before upstream is ready) and the slot cost of polling sensors.

**Exception.** Genuinely temporal triggers, or cases where no upstream Asset
exists to subscribe to, use cron (PY-AIRFLOW-006).

## PY-AIRFLOW-020 — Never pass secrets as operator arguments

**Severity:** error
**Since:** v0.1.0
**Linter:** secret-scan lint

**Decision.** Secret material MUST NOT be passed to operators as arguments — e.g.
`SomeOperator(api_key=Variable.get("my_api_key"))` or `params={"token": "..."}`.
Values passed this way land in the task instance's rendered fields, get persisted
to the metadata DB, and are visible in the UI under Task Instance Details →
Rendered Template. Resolve secrets at task runtime instead (PY-AIRFLOW-013).

**Why.** Airflow's name-based masking (`password`/`token`/`secret` patterns) is
best-effort and easy to bypass with an innocuous-looking field name. Rendered
template fields are a durable, UI-visible leak path.

**Exception.** None.

**Example:**
```python
# Bad — secret is rendered and persisted to the metadata DB
SomeOperator(task_id="call", api_key=Variable.get("vendor_api_key"))

# Good — fetch inside the callable; the value lives only in worker memory
@task
def call():
    key = Variable.get("vendor_api_key")
    return client(key).fetch()
```

## PY-AIRFLOW-021 — Develop and test DAGs locally before pushing

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Authors iterate against a local Airflow environment via
`astro dev start` (the Astro CLI spins up the same Astronomer runtime in Docker).
Exercise individual tasks in isolation with
`airflow tasks test <dag_id> <task_id> <logical_date>`. Validate locally before
pushing; don't use CI as your first feedback loop.

**Why.** Local dev is the inner loop; CI is the safety net. Round-tripping through
CI for basic feedback is slow and clogs the pipeline.

**Exception.** None.

## PY-AIRFLOW-022 — Enforce the standard with a value-bounded structural test

**Severity:** error
**Since:** v0.1.0
**Linter:** `assert_dag_compliant`

**Decision.** A shared `assert_dag_compliant(dag)` helper checks the rules above
and runs in CI for every PR. Checks are **value-bounded, not presence-only**, to
close gameable patterns:

- `retries` is set **and** `≤ 5` — a high retry count masks deterministic failures
  rather than failing fast (PY-AIRFLOW-016).
- every wait `timeout` / `execution_timeout` is set **and** `≤ 10h` (`36000s`),
  the PY-AIRFLOW-017 category ceiling, so an absurd value cannot satisfy "no
  unbounded waits."
- the T-shirt size is a valid tier, and `xl` carries a `doc_md` justification
  (PY-AIRFLOW-005).
- `l1_xmatters_group` is in the `xmatters_groups` allowlist (PY-AIRFLOW-007).
- `lifecycle_phase` is gated: a DAG tagged `criticality: critical` MUST NOT also
  be tagged `lifecycle_phase: build` — a production-critical DAG cannot use the
  build phase as an escape hatch from production rules.

To close the post-deploy drift gap, the checker also runs in `edo_airflow_lib`'s
own CI (so a library change that would break downstream DAGs fails the lib's
tests) and re-runs on every Astronomer deploy, not only on author PRs. Full
deploy-environment gating and a weekly post-deploy drift-reconciliation job are
tracked follow-ups in RFD 0011.

**Why.** Standards enforced by reviewer memory slip through under review fatigue,
and skill-generated DAGs need a programmatic check before submission.
Value-bounded assertions stop authors from satisfying the letter of a presence
check (e.g. `retries=999`, `timeout=10**9`) while violating its intent.

**Exception.** None.

## PY-AIRFLOW-023 — One task is one logical step

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Tasks are small, atomic, and free of top-level code with side
effects — the DAG file is a description of work, not the work itself. One task is
one logical step: the smallest unit with its own retry/restart boundary and a
single output. Concretely:

- "run dbt model `dim_equity_positions`" is a task; "run every dbt model in the
  equity domain" is too coarse — split by model or layer.
- one Python callable that extracts, transforms, *and* loads is too coarse —
  split at the I/O boundary.

`generate-dag`'s current "one task per DAG" default is reconciled to this: a DAG
is decomposed into atomic tasks, not collapsed into one.

**Why.** A task is the unit Airflow retries and restarts. Coarse tasks force a
rerun to redo work that already succeeded, blur the failure boundary, and make
the DAG harder to reason about. Atomic tasks retry cheaply and surface exactly
where a run failed.

**Exception.** None.

## PY-AIRFLOW-024 — Keep DAG files thin; shared logic in a versioned library

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** DAG files are thin. Shared logic lives in a versioned library, not
copy-pasted across DAGs.

- Common helpers (cluster specs, callback wiring, asset URIs, retry profiles, the
  `get_processing_window` helper, the `xmatters_groups` allowlist) live in a
  shared `edo_airflow_lib` package — **owned by the Platform team (Airflow
  track)** and **consumed as a published, versioned package from the internal
  cgpypi mirror**, not copied per repo. This is the target shape; `generate-dag`
  currently *vendors* these helpers (and names a pip-installable library an
  anti-goal), which is transitional and reconciled to this.
- The safety-critical helpers — the xMatters-group allowlist and the windowing
  helper — are prioritized onto the published path, because a stale vendored copy
  is exactly how a renamed on-call group silently pages nobody (PY-AIRFLOW-007).
- Pin a version; upgrade deliberately.
- Each DAG file owns the DAG definition, the task wiring, and DAG-specific
  parameters. Anything else is a smell.

**Why.** Copy-pasted helpers drift independently across repos, so a fix or a
safety-critical update (a renamed on-call group, a corrected windowing rule)
reaches some DAGs and not others. A single published, versioned package makes the
helper one source of truth that every DAG pins and upgrades deliberately.

**Exception.** None — the vendored arrangement `generate-dag` emits today is
transitional and reconciled to this target shape (publishing `edo_airflow_lib` to
the cgpypi mirror is a tracked follow-up in RFD 0011).
