# airflow: optional stretch selection

**Optional small-fixture follow-up.** The assigned course route is the supplied Portfolio Analytics pipeline on dbt-databricks/Astro. This preserved fixture supports separate further practice and its original command contract; it is not a second mandatory assignment.

Legacy alert transport, tiered notifications, freshness, monitoring, publication, Databricks jobs and integrated operations remain under v1/03-airflow-orchestration (each 30–90 minutes; integration may exceed 120). Datadog/hostedAstronomer is conditional on prepared access. Demonstrate a useful operational signal and response, not just configuration.

These routes are separate from core completion. Record timing exceptions rather than shortening an exercise during the audit. Instructor review should select one follow-up based on the learner goal and available environment.

## Full legacy advanced reference

The following is the preserved legacy advanced route. Its workspace/commands target **v1**; do not run it against the v2 workspace. Core-equivalent topics are retained here for complete teaching coverage, not additional core assignments.

## Phase 2: Production operations

Phase 1 left you with a running baseline: a scheduled DAG that drives the dbt
pipeline on Databricks through a Cosmos `DbtTaskGroup`, with a freshness gate
and retries. That makes the pipeline *run*. Phase 2 makes it **operable**:
tiered alerting wired through callbacks, an SLA that catches a slow run, a
monitoring config, the runbook and consumer-onboarding doc the next on-call
engineer reads, structural tests that guard the DAG, the paved-path
`DatabricksSubmitRunOperator` variant, and a capstone that assembles a complete
production-ready DAG.

Every challenge is self-contained. Each defines the operations idea it uses
before you apply it. The shape is always four parts:

- **Concept** — the idea, in plain English.
- **Goal** — the operational outcome in one line.
- **Authoring task** — exactly what you write, and into which starter file.
- **How to check** — a command to run, or an observable result.

Write your own answer first; a worked **Solution** follows each challenge for
you to compare against. A few conventions hold throughout: Databricks is the
only platform; alerting is **Slack-free, PagerDuty-free** — P1 emits a Datadog
event (support pages the on-call via xMatters from the payload), P2 notifies
Microsoft Teams through the vendor-neutral `send_alert`, P3 opens a ticket; the
transports degrade to a log line when their credential env var is unset, so
everything runs offline in the DAG-load check.

Budget roughly ~10 min per challenge — a pacing target, not a deadline. Work
the challenges in order: they build on each other, and challenge 10 assembles
the pieces into one production-ready DAG.

---

### Challenge 1: The vendor-neutral alert transport

**Concept.** Every alert in this pipeline goes through one boundary:
`send_alert` in
`data_products/portfolio_analytics/include/alerting/notifications.py`. It posts
to a team-chat **webhook** held in an Airflow HTTP connection
(`alert_webhook`) — there is no Slack SDK and no hard-coded webhook URL in the
code (the Teams webhook lives in the connection, not the source). That single boundary is what keeps the pipeline vendor-neutral: swap the
webhook behind the connection and nothing else changes. Callbacks call
`send_alert(text=...)`; they never know which chat tool is on the other end.

**Goal.** One transport function the P2 (team-chat) tier calls, with no chat
vendor named in the code.

**Authoring task.** Read
`data_products/portfolio_analytics/include/alerting/notifications.py` and
confirm its shape: it builds an
`HttpHook(method="POST", http_conn_id="alert_webhook")`, assembles a
`{"text": text}` payload (adding `channel` only when passed), and
`hook.run(...)`s it. This file ships complete — your job is to understand it,
because every callback in the next challenge calls it. Confirm there is no
hard-coded webhook URL or vendor name anywhere in the file.

**How to check.**

```bash
python -c "import ast; ast.parse(open('data_products/portfolio_analytics/include/alerting/notifications.py').read()); print('parses OK')"
grep -niE 'https?://|slack_sdk|WebhookClient|hooks\.slack' data_products/portfolio_analytics/include/alerting/notifications.py || echo "no hard-coded URL or vendor SDK — good"
```

The parse should succeed and the grep should find nothing — the only coupling is
to the `alert_webhook` Airflow connection id.

Worked answer 1 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 2: Tiered failure alerting — page on P1, notify on P2

**Concept.** Not every event deserves the same channel. A task that fails after
exhausting its retries means the pipeline is down and the 07:30 UK SLA is at
risk — that is a **P1**: it emits a Datadog event (the auto sink; support pages
the on-call via xMatters from the payload) *and* notifies Microsoft Teams.
Matching severity to channel is the whole point of tiering: an xMatters page
wakes a human, so it is reserved for "the mart will be late". The
`on_failure_callback` is set in `default_args`, so it fires for any task in the
DAG once its retries are spent.

**Goal.** A failure callback that emits a Datadog event (P1, the auto sink) and
posts to Microsoft Teams (P2), wired so it fires once a task's retries are
exhausted.

**Authoring task.** Read `on_failure_callback(context)` in
`data_products/portfolio_analytics/dags/callbacks.py`. It ships complete — your
job is to understand it, not retype it. Trace how it pulls `task_instance` and
`dag_run` from `context`, builds a `detail` dict (dag_id, task_id, run_id,
log_url, exception), then calls the `_emit_datadog(...)` helper (severity
`"error"`) and `send_alert(...)` with a message naming the DAG, task, log URL,
and a runbook link. The `_emit_datadog` helper posts to the Datadog Events API
(carrying the MDS routing tags; support pages the on-call via xMatters from the
payload) and falls back to a log line when `DD_API_KEY` is unset.

**How to check.**

```bash
python -c "import ast; ast.parse(open('data_products/portfolio_analytics/dags/callbacks.py').read()); print('parses OK')"
grep -niE 'slack_sdk|hooks\.slack|slack\.com' data_products/portfolio_analytics/dags/callbacks.py || echo "no Slack SDK — good"
```

The file parses and contains no Slack reference. The behavioural proof comes in
challenge 8's structural test, which exercises the callback with the transports
stubbed.

Worked answer 2 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 3: The P2 and P3 tiers — SLA miss and retry

**Concept.** The other two tiers round out the taxonomy. An **SLA miss** means
the pipeline was slow, not down — the DAG still ran (or will), so it is a
**P2**: notify team chat, do not page. A **retry** is expected (a transient
warehouse blip) — nobody needs paging or even pinging, but a flaky task should
leave a trail, so it is a **P3**: open a ticket. `on_sla_miss_callback` has a
fixed signature Airflow calls with the missed-task list; `on_retry_callback`
gets the same `context` dict as the failure callback.

**Goal.** An SLA-miss callback that notifies team chat (P2) and a retry callback
that opens a ticket (P3) — neither pages.

**Authoring task.** Read the two remaining callbacks in
`data_products/portfolio_analytics/dags/callbacks.py`. They ship complete — your
job is to understand them.
`on_sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis)`
builds a comma-joined list of the missed `task_id`s and `send_alert(...)`s a P2
message naming the DAG and the tasks past SLA. `on_retry_callback(context)`
pulls `task_instance`, reads its `try_number`, and calls `open_ticket(...)` (the
P3 helper that logs when `TICKET_WEBHOOK_URL` is unset) with the task id and
log url.

**How to check.**

```bash
python -c "import ast; ast.parse(open('data_products/portfolio_analytics/dags/callbacks.py').read()); print('parses OK')"
```

The file parses. In the DAG, `on_sla_miss_callback` is wired on the DAG object
and `on_retry_callback` in `default_args`; the structural test in challenge 8
asserts the DAG carries an `sla_miss_callback`.

Worked answer 3 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 4: Wire the callbacks and the SLA into the DAG

**Concept.** Callbacks do nothing until they are attached. Three attachment
points, each at the right scope: `on_failure_callback` and `on_retry_callback`
go in `default_args` (every task inherits them); `sla_miss_callback` goes on
the `DAG(...)` object (it is a DAG-level event); `on_success_callback` goes on
the **final task only** (so it fires once per successful run, not once per
task). The SLA itself is a `timedelta` on the task you want to time — here
`publish_to_catalog`, because end-to-end-by-90-minutes is what the 07:30 UK
deadline means.

**Goal.** The three callback tiers and the 90-minute SLA wired at the right
scopes so a failure pages, an SLA miss notifies, and a green run pings once.

**Authoring task.** Nothing to write — this one ships already wired, and your job
is to verify each attachment point so you know where callbacks hang. In
`data_products/portfolio_analytics/dags/portfolio_analytics_daily.py`: confirm
the four callbacks are imported from `callbacks`; confirm `on_failure_callback`
and `on_retry_callback` are in `default_args`; confirm
`sla_miss_callback=on_sla_miss_callback` is on the `DAG(...)` call; and confirm
`publish_to_catalog` has `sla=timedelta(minutes=90)` and
`on_success_callback=on_success_callback`.

**How to check.**

```bash
mise run challenge:verify 03
pytest data_products/portfolio_analytics/tests/ -q -k "callback or sla"
```

The DAG loads, and the structural tests confirm `default_args` carries a failure
callback, the DAG carries an `sla_miss_callback`, and `publish_to_catalog` has
an SLA.

Worked answer 4 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 5: The source-freshness gate as a contract

**Concept.** Phase 1 wired the freshness task; here you make its thresholds a
deliberate **contract** rather than a default. `dbt source freshness` fails the
gate only on an `error_after` breach, so where you set `error_after` is where
you draw the line between "stale enough to block" and "old but acceptable". The
custodian feed is the binding one: it lands by 02:00 UK and the SLA is 07:30,
so a 6-hour `error_after` means a feed more than 6 hours stale blocks the run
— but a feed 5 hours old (past the 4-hour `warn_after`) only warns and the
pipeline proceeds on borderline data. That gap is a decision, not an accident.

**Goal.** A freshness contract whose `error_after` on the custodian source is
set where you can defend it, gating the DAG.

**Authoring task.** Read
`data_products/portfolio_analytics/dbt/models/sources.yml` and confirm the
custodian source's `freshness` block:
`warn_after: {count: 4, period: hour}` and
`error_after: {count: 6, period: hour}`, with
`loaded_at_field: _extracted_at`. This ships configured — your task is to
exercise it and decide whether 6 hours is the right blocking threshold for
*your* SLA, then prove the gate fires.

**How to check.**

```bash
(cd data_products/portfolio_analytics/dbt && dbt source freshness --select source:custodian)
```

With the bundled data the custodian line reports `pass` or `warn`. Tighten
`error_after` to `{count: 0, period: hour}`, re-run, and watch it flip to
`error` (exit non-zero) — that is the gate that would stop the DAG. Put it
back to 6 hours.

Worked answer 5 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 6: The monitoring config

**Concept.** Alerting tells you when something just broke; **monitoring** tells
you when something is *drifting* before it breaks. A monitoring config declares
the panels that track pipeline health — each a metric, an alert condition, and a
channel. Five panels cover most pipelines (run status, duration, task-failure
rate, SLA compliance, source freshness). The sixth is the one that catches the
nastiest failure mode: a **fresh-but-truncated** feed. Freshness watches the
clock; a volume-anomaly panel watches the row count, so a short extract that
passes freshness but fails completeness is caught at ingestion, not three steps
later at the test gate.

**Goal.** A six-panel monitoring config whose channels are Slack-free and whose
sixth panel catches a fresh-but-short feed.

**Authoring task.** Read
`data_products/portfolio_analytics/include/monitoring/portfolio_analytics.yml`
and confirm the six panels. Check that every `alert_channel` is one of
`datadog` / `teams` / `ticket` (no Slack, no PagerDuty), that "SLA compliance"
routes to `datadog, teams`, and that "Source volume anomaly" fires when today's
`holdings_raw` row count drops below 80% of the trailing-7-day average. This
file ships complete; understand why the sixth panel exists — it is the
`INC`-style fresh-but-truncated failure mode the first five all miss.

**How to check.**

```bash
grep -cE '^  - name:' data_products/portfolio_analytics/include/monitoring/portfolio_analytics.yml   # expect 6
grep -niE 'alert_channel.*slack' data_products/portfolio_analytics/include/monitoring/portfolio_analytics.yml || echo "no Slack channel — good"
```

There are six panels, and no `alert_channel` routes to Slack.

Worked answer 6 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 7: The runbook and the consumer guide

**Concept.** Two documents turn a pipeline you understand into one anyone can
operate. The **runbook** is the page the on-call engineer opens when an alert
lands: service overview, architecture, a common-alerts table (symptom →
diagnosis → remediation), an escalation matrix, and manual procedures. The
**consumer guide** is the page a downstream user reads to adopt the data
product: where the marts live, what each column means, sample queries, known
limitations, and freshness. Both live in the repo next to the DAG so they
change in the same pull request the code does.

**Goal.** A runbook the next on-call engineer can act on and a consumer guide a
downstream user can onboard from — both naming the real marts and the tiered,
Slack-free alert channels.

**Authoring task.** Read
`data_products/portfolio_analytics/include/runbooks/portfolio_analytics.md` and
`data_products/portfolio_analytics/include/launch/consumer-guide.md`. Confirm
the runbook's common-alerts table covers source-freshness error, dbt build
failure, dbt test failure, SLA miss, and the fresh-but-truncated feed; that
escalation names Datadog/xMatters and Microsoft Teams (no Slack); and that the
consumer guide documents `fct_portfolio_returns`, `agg_fund_exposure` and
`agg_fund_daily_exposure` with sample queries. These ship complete — verify they
are internally consistent with your DAG (task names, schedule, SLA, marts).

**How to check.**

```bash
grep -c "^### Alert" data_products/portfolio_analytics/include/runbooks/portfolio_analytics.md       # expect 5
grep -E "fct_portfolio_returns|agg_fund_exposure|agg_fund_daily_exposure" data_products/portfolio_analytics/include/launch/consumer-guide.md
grep -niE 'slack' data_products/portfolio_analytics/include/runbooks/portfolio_analytics.md data_products/portfolio_analytics/include/launch/consumer-guide.md | grep -viE 'slack-free' || echo "no Slack — good"
```

Five alert entries, all three marts named in the consumer guide, no Slack anywhere.

Worked answer 7 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 8: Structural tests for the DAG

**Concept.** The cheapest, highest-value Airflow test is the **structural**
test: does the file parse into the expected shape, without hitting Databricks?
It runs in milliseconds and catches most breakage — a bad import, a renamed
task, a dropped dependency edge, a secret accidentally pasted into the DAG. The
test parses the `dags/` files (no DagBag, no warehouse, no airflow), confirms the
tiered callbacks and the SLA are wired at their scopes, and greps the DAG files
for a token literal that must never be committed. The
`freshness → pipeline → publish` chain is the learner deliverable and is checked
separately by `mise run challenge:verify 03`.

**Goal.** A structural test suite that proves the DAG parses, has the right
chain, carries the callbacks and SLA, and embeds no secret.

**Authoring task.** Read
`data_products/portfolio_analytics/tests/test_dag_structure.py` and run it.
Confirm it covers: both DAGs and the callbacks module parse; the primary DAG
wires `on_failure_callback` / `on_retry_callback` (in `default_args`),
`sla_miss_callback` (DAG-level), `on_success_callback` (publish task), and
`sla=timedelta(minutes=90)` on `publish_to_catalog`; and no DAG file contains a
`dapi…` token or a workspace-host literal. This ships complete — your job is to
run it and read what each assertion guards. (The wiring chain is checked by
`mise run challenge:verify 03`.)

**How to check.**

```bash
pytest data_products/portfolio_analytics/tests/ -q
```

All assertions pass. To prove the secret check bites, paste a fake
`token = "dapi0123456789abcdef0123"` line into a DAG file and re-run — the
`test_no_secret_literals_in_dag_files` test fails. Remove it.

Worked answer 8 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 9: Stretch — the paved-path `DatabricksSubmitRunOperator` variant

**Concept.** The Cosmos variant runs dbt **on the Airflow worker**. Capital
Group's paved path runs dbt **inside Databricks** as a Job: each Airflow task
submits one step via `DatabricksSubmitRunOperator` and polls until it finishes.
The trade-off is granularity for locality — you lose Cosmos's per-model tasks
(the Databricks Job is one opaque step in the Airflow graph), but the warehouse
autoscales for the build, logs live with the data in the Databricks Jobs UI,
and the worker pool stays free. Knowing both shapes is the point: you will meet
Cosmos in dbt-centric shops and Submit-Run in Databricks-centric ones.

**Goal.** A second DAG expressing the same pipeline as four
`DatabricksSubmitRunOperator` steps that submit dbt-wrapping notebooks to
Databricks.

**Authoring task.** Read
`data_products/portfolio_analytics/dags/databricks_submit_run_dag.py` and
confirm its shape: four `DatabricksSubmitRunOperator` tasks
(`check_source_freshness` → `run_dbt_models` → `test_dbt_models` →
`generate_dbt_docs`), each submitting a `notebook_task` under
`/Workspace/data-creators/dbt/portfolio_analytics` to the
`databricks_default` connection, with the SLA on `run_dbt_models` and the
tiered callbacks reused from `callbacks.py`. This ships complete — wire it by
confirming it loads alongside the primary DAG.

**How to check.**

```bash
mise run challenge:verify 03
```

`mise run challenge:verify 03` confirms the primary DAG's wiring. Both DAGs also
parse (Challenge 8's structural test), and the submit-run DAG reuses
`on_failure_callback` and `on_sla_miss_callback` — so P1 (down) and P2 (slow)
alert identically across both shapes. It does **not** wire `on_retry_callback`
or `on_success_callback`, so despite setting `retries=2` it raises no P3 ticket
on a flaky retry and emits no success signal. Spotting that gap is the exercise:
compare its imports against the four in `portfolio_analytics_daily.py`.

Worked answer 9 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Challenge 10: Capstone — a complete production-ready DAG

This is the integrative challenge. Earlier challenges each added one operational
piece; here you confirm they compose into one DAG that an on-call team could
own, and you prove it green end to end.

**Concept.** "Production-ready" is not one feature — it is the sum: the
pipeline runs on a defensible schedule, fails fast on bad inputs, retries the
transient, pages the right person at the right severity, times itself against
the business SLA, and ships with the runbook and consumer doc that let someone
else operate it. `portfolio_analytics_daily` is that sum. The capstone is to
walk the whole DAG against the checklist and run the verification gate.

**Goal.** One DAG that passes the full production checklist and the
DAG-load verification gate.

**Authoring task.** Walk
`data_products/portfolio_analytics/dags/portfolio_analytics_daily.py` against
this checklist and fix any gap you find:

1. **Schedule** — timezone-aware weekday cron (`0 6 * * 1-5`, `Europe/London`),
   `catchup=False`, `max_active_runs=1`.
2. **Fail fast** — `source_freshness_check` is the first task and gates the
   build.
3. **Build** — the Cosmos `DbtTaskGroup` renders the dbt project.
4. **Retries** — `retries=2` with exponential backoff in `default_args`.
5. **Tiered alerting** — `on_failure_callback` (P1+P2) and `on_retry_callback`
   (P3) in `default_args`; `sla_miss_callback` (P2) on the DAG.
6. **SLA** — `publish_to_catalog` carries `sla=timedelta(minutes=90)` and the
   success notification.
7. **Docs** — the runbook, consumer guide, and monitoring config are present and
   consistent.
8. **No secrets** — no token or host literal in any DAG file.

**How to check.**

```bash
pytest data_products/portfolio_analytics/tests/ -q
mise run challenge:verify 03
```

The structural tests pass and the DAG-wiring gate is green.

Worked answer 10 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

---

### Phase 2 Summary

You took the running DAG and made it operable: a vendor-neutral alert transport,
tiered Slack-free alerting (Datadog auto-sink + xMatters page / Teams notify /
ticket) wired at the right scopes, the freshness gate as a deliberate contract,
a six-panel monitoring config that catches a fresh-but-short feed, the runbook
and consumer guide the next operator reads, structural tests that guard the DAG
shape and ban committed secrets, the paved-path `DatabricksSubmitRunOperator`
variant, and a capstone that proves the whole thing is a complete,
production-ready orchestration.
