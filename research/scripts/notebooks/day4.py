"""Day 4 — Bitemporal loading and Airflow orchestration."""
import dc
DAY, SLUG, TITLE = 4, "day4-airflow", "Bitemporal loading and Airflow orchestration"

BLOCKS = [
 dict(time="09:00–09:45", title="Bitemporal loading", type="Demo + shareback", on_screen="Anchor › Bitemporal (diagram, demo cells, the macro); a guest or volunteer's screen",
      purpose="Business time and system time; loading strategies; a worked history with a correction; which clock answers which question.",
      notes=["A volunteer or guest shows a real table for ten minutes if one was recruited yesterday; the anchor's demo on DuckDB covers the same ground either way.",
             "Ask the Monday/Wednesday question before opening any code; use one concrete timeline.", "Shareback: each table answers one 'which clock?' question."],
      say=["The source corrects Monday's value on Wednesday. What was true on Monday, and what did we believe on Tuesday?"],
      transition="From history to timing: orchestration.", flex="Over time: skip the macro walk, keep the four queries."),
 dict(time="09:45–10:00", title="Orchestration and capstone orientation", type="Demo", on_screen="Anchor › The DAG diagram; Friday preview",
      purpose="What orchestration is, connected to the pipeline generated on Day 2; a preview of Friday's work and its starting files.",
      notes=["Open the eod_prices DAG from Day 2: it is the same shape as the challenge's.", "Friday: Phase 1 scope, two to three hours, the working folder rule."],
      say=["Airflow plays no instrument. It tells dbt when to play, and what to do when it goes wrong."],
      transition="Break, then the Airflow demo.", flex=""),
 dict(time="10:00–10:15", title="Break", type="Break", on_screen="", purpose="", notes=[], say=[], transition="", flex=""),
 dict(time="10:15–10:45", title="Airflow demonstration", type="Demo", on_screen="Anchor › Airflow cells; the Airflow UI at localhost:8080",
      purpose="Operators, dependencies, callbacks, the UI, Astro blueprints, and a controlled failure, on a local Astro stack running Day 3's project.",
      notes=["Start the stack before the day (bash run.sh start); seed; trigger; show graph, grid, a task log, the code tab.", "Read >> as 'and then'. Open callbacks.py. Show a blueprint and its YAML.",
             "Controlled failure: stale, trigger, the freshness task fails and the rest is upstream_failed; fresh, trigger, green."],
      say=["A green graph is not evidence that the data is right. The publish task shows the rows; that is evidence."],
      transition="Challenge 10 until lunch.", flex="If the stack misbehaves, the status and log cells still show a previous green run."),
 dict(time="10:45–12:00", title="Challenge 10 — Airflow practical", type="Challenge", on_screen="Anchor › Challenge box; learners in challenges/v1/03-airflow-orchestration",
      purpose="Launch the assigned Airflow project; learners wire the chain, run tasks inside the scheduler, inspect states and logs.",
      notes=["Boot order matters: setup, then seeds, then astro dev start; the cold-start symptom and fix are in the anchor.", "Collect deployment and monitoring questions for the afternoon."],
      say=["Which run produced this result, and what proves the data is right?"],
      transition="Lunch.", flex="Fast finishers: the extension questions (late input, failed check, repeated run), then Phase 2."),
 dict(time="12:00–13:00", title="Lunch", type="Break", on_screen="", purpose="", notes=[], say=[], transition="", flex=""),
 dict(time="13:00–13:30", title="Continue Airflow practical, regroup at 13:30", type="Challenge + shareback", on_screen="Anchor › Challenge box",
      purpose="Resolve blockers; Phase 2 for those on it; regroup with one run, one log and one output check per pair.",
      notes=["Keep credential and path errors separate from the intended data-quality failure.", "Shareback: a pair shows the current run, a useful log line, and the warehouse output."],
      say=["Show me the run ID, the log line that told you what happened, and the table it produced."],
      transition="CI/CD and the deployment picture.", flex=""),
 dict(time="13:30–14:00", title="CI/CD and deployment context", type="Demo", on_screen="Anchor › CI/CD (diagram), Harness walkthrough, Datadog monitors",
      purpose="Where code goes, how deployment is initiated, where execution is visible, how failures are investigated: Harness, Astro, Datadog.",
      notes=["Agree the agenda with a guest in advance; otherwise the anchor's walkthrough with screenshots.", "Say the downsides of CI/CD too; rooms respect it."],
      say=["A pull request is where acceptance happens. A deleted test is a block of red lines that is easy to skim past."],
      transition="Break, then the release decision.", flex=""),
 dict(time="14:00–14:15", title="Break", type="Break", on_screen="", purpose="", notes=[], say=[], transition="", flex=""),
 dict(time="14:15–14:35", title="Release decision in pairs", type="Challenge + shareback", on_screen="Anchor › Activity 10 card",
      purpose="A failed candidate with 500 rows and 497 distinct IDs, yesterday's accepted output available: decide what ships and what to tell the consumer.",
      notes=["Ten minutes deciding and drafting, ten discussing. The failed candidate stays blocked; whether yesterday's output is acceptable depends on the consumer's freshness commitment."],
      say=["What information is missing, and who can supply it?"],
      transition="Write the failure note.", flex=""),
 dict(time="14:35–14:50", title="Explain a failure and repair", type="Challenge + shareback", on_screen="Anchor › Activity 11 card and template",
      purpose="A short note another creator could use to locate the run and understand what happened; swapped and tested.",
      notes=["If a pair's execution was blocked, they use the anchor's prepared failure example and separate expected from observed."],
      say=["Could another creator find this run from your note alone?"],
      transition="Friday preparation.", flex=""),
 dict(time="14:50–15:00", title="Friday preparation and closing questions", type="Shareback", on_screen="Anchor › Friday checklist",
      purpose="Check the starting files and environment; record remaining problems and who resolves them.",
      notes=["Every learner opens the capstone README and runs the readiness checks; problems go on the list with a name."],
      say=["Tomorrow starts sharp at nine. The sharper you start, the sharper you finish."],
      transition="", flex=""),
]

LEAVE_WITH = ["The DAG, run and task identities, useful logs, an output check and a short explanation of the failure and repair, per pair.",
              "Every learner has opened challenges/v1/04-atlas-capstone/README.md and run the readiness checks in data_products/atlas_elt.",
              "A list of setup issues that could stop Friday's start, each with the person responsible for the next action.",
              "The Airflow stack stopped on the learners' laptops (astro dev stop) so Friday starts clean."]

ACTIVITIES = [
 dict(number="10", title="Release decision", grouping="Pairs", minutes=20,
      brief="The nightly build produced a candidate output with 500 rows but only 497 distinct IDs, so the uniqueness check failed and the candidate was not published. Yesterday's accepted output is still available to consumers. In ten minutes, decide what should happen next and draft a two-sentence update to the consumer. Then ten minutes of discussion.",
      outputs=["A decision: what is released, what stays blocked, and who decides", "A two-sentence update to the consumer", "The information you are missing and who can supply it"],
      debrief=["Does the consumer's freshness commitment allow yesterday's output to stand today?", "What would make the three duplicate IDs a data problem rather than a pipeline problem?", "Who gets to override a failed quality gate, and how is that recorded?"]),
 dict(number="11", title="Explain a failure and repair", grouping="Pairs, then swap", minutes=15,
      brief="Write a short note about the Airflow failure and repair you ran today (or the prepared example if your environment was blocked): the affected run, the useful error, the cause, the action taken, the output check, and anything still unresolved. Swap notes with another pair for five minutes: could they locate the run and explain what happened from the note alone?",
      outputs=["The note, using the template below", "The other pair's verdict: could they find the run?"],
      debrief=["Which line of the note was the most useful to the reader?", "What did you have to go back to the UI to find?"],
      extra="""
      **Template**

      | Field | Your note |
      |---|---|
      | DAG and run ID | `portfolio_analytics_daily`, `manual__2026-…` |
      | Task that failed, and the first useful log line | |
      | Cause (data quality, credentials, path, code) | |
      | Action taken | |
      | Output check after repair (query and result) | |
      | Still unresolved, and who owns it | |
      """),
]

SECTIONS = [
 dict(n=1, title="Bitemporal loading", anchor="s1", start="09:00",
      parts=["Demo: two clocks, three loads, four questions", "Guest or volunteer: a real table", "Shareback: which clock?"]),
 dict(n=2, title="Airflow orchestration", anchor="s2", start="09:45",
      parts=["Orientation: the DAG, and Friday", "Break", "Demo: the stack, a run, the UI, a controlled failure", "Challenge 10: Airflow practical", "Lunch", "Shareback: one run, one log, one output check"]),
 dict(n=3, title="CI/CD and release operations", anchor="s3", start="13:30",
      parts=["Demo: GitOps, Harness, Datadog", "Break", "Activity 10: release decision", "Activity 11: explain a failure and repair", "Friday preparation"]),
]

def cells():
    A = {a["number"]: a for a in ACTIVITIES}
    act = lambda n: dc.md(dc.activity(n, A[n]["title"], A[n]["grouping"], A[n]["minutes"], A[n]["brief"], A[n]["outputs"], A[n].get("debrief"), A[n].get("early")))
    
    BT = 'HERE / "demos/bitemporal/warehouse/bitemporal.duckdb"'
    AL = "demos/airflow_local"
    C = [dc.title(4, TITLE, "anchor notebook"),
         
         *dc.how_to_use(4, "- Before the day: `bash demos/airflow_local/run.sh start` (Docker Desktop running; the image is already built) and `bash demos/bitemporal/demo.sh` once. The Airflow UI is http://localhost:8080."),
         dc.code(dc.setup_cell(4)),
         dc.agenda(SECTIONS, lead="Morning: history (bitemporal loading) and orchestration (Airflow) with a long practical. Afternoon: the deployment picture, then two short exercises that turn a failed run into a decision and a note. Close by checking Friday's starting line."),
         dc.section(1, "Bitemporal loading", "s1"),
         dc.part("Demo", "two clocks, three loads, four questions", time="09:00"),
         dc.anchor("The source corrects Monday's value on Wednesday. What was true on Monday, and what did we believe on Tuesday?",
                   "Two clocks on every row: business time (when it was true) and system time (when the warehouse knew it). Nothing is overwritten; corrections add versions.",
                   "Audit, reproducible reports and 'as was' questions all need the second clock; a status flag or an overwrite loses it.",
                   "Three loads on a tiny associate table: a day-1 file, a day-2 file with a change and a defect, a corrected re-delivery. Then four queries."),
         dc.md(dc.whiteboard("loading strategies and two clocks", [
             ("How can new data land in a table?", "Truncate and reload; insert-overwrite; SCD type 2 (effective start and end dates keep history). Bitemporal is SCD2 with a second clock."),
             ("What are the two clocks?", "Business time: when the fact was true in the world (the business date). System time: when the warehouse loaded or believed it. Separate columns for start and end of each, plus a current indicator and a row hash."),
             ("Full, incremental, balance?", "Full: the source sends the whole book of record each run (expensive: every row re-versioned). Incremental: only new or changed records with a business key; a known key with new content ends the previous version. Balance: for monetary balances. Some models need a custom strategy."),
             ("Why does a correction matter?", "Because 'as was' must still answer what the report said on Tuesday, and 'as of' must give the corrected Monday value today. Overwriting destroys the first; a status flag cannot express either."),
             ("UTC or local?", "The platform stamps system time in UTC; a run at 03:00 Pacific for the previous business day shows yesterday's business date. Always say which clock a date column is."),
         ], open_=True)),
         dc.figure("d4-bitemporal-rows", "One associate across three loads: four rows, nothing overwritten",
                   ["Day 2's changed record closes the day-1 row's system clock and carries it forward with its business clock ended, then inserts the new version.",
                    "The corrected re-delivery for the same business date closes only the system clock of the defective row and inserts the corrected one.",
                    "As of Monday with today's knowledge: the carried-forward row. As was on Tuesday: the defective row. As is: the corrected row."]),
         dc.md(dc.demo("three loads on DuckDB, then the four questions", "Three loads of a tiny associate feed, then the four questions, from one script.", [
                  "Run the cell: `demos/bitemporal/demo.sh` seeds, loads day 1, loads day 2, loads the correction, and prints the history and the as-is, as-of and as-was queries.",
                  "Read the history row by row: which load wrote each row, and which clock closed it.",
                  "Run the two `sql()` cells: the audit trail for one associate, then as-of 2 November.",
                  "Open `demos/bitemporal/macros/bitemporal_load.sql` (the cell prints it): three steps on one screen.",
                  "Say: the paved path's `bitemporal_load_v2` does the same job with more strategies."])),
         dc.code("!bash demos/bitemporal/demo.sh 2>&1 | sed -n '/-- Full history/,$p'"),
         dc.code(f'sql("""select associate_id, job_title, tenure_months, dl_business_start_dt, dl_business_end_dt, dl_system_start_ts, dl_system_end_ts, dl_current_ind\n          from training_demo.dim_associate where associate_id = 1001 order by dl_system_start_ts, dl_business_start_dt""", {BT})\n# The audit trail for one associate. Point at each row: which load wrote it, and which clock closed it.'),
         dc.code(f'sql("select associate_id, job_title, tenure_months from training_demo.dim_associate where dl_business_start_dt <= date \'2026-11-02\' and coalesce(dl_business_end_dt, date \'9999-12-31\') >= date \'2026-11-02\' and dl_system_end_ts is null order by 1", {BT})\n# AS OF 2 November with today\'s knowledge: business clock covers the date, system clock open.'),
         dc.code("!sed -n '1,40p' demos/bitemporal/macros/bitemporal_load.sql\n# The whole strategy fits on a screen: close the system clock, carry the superseded business version forward, insert the new rows."),
         dc.md("""
         | The question | Which clock | The filter |
         |---|---|---|
         | What is current? | both open | `dl_current_ind` |
         | What was true on date D, as we know it today? | business covers D, system open | `dl_business_start_dt <= D and coalesce(dl_business_end_dt, '9999-12-31') >= D and dl_system_end_ts is null` |
         | What did the report say at time T? | system covers T | `dl_system_start_ts <= T and coalesce(dl_system_end_ts, '9999-12-31') > T` |
         | Which versions did a correction replace? | same business start, later system start | order by `dl_system_start_ts` within the key |
         """),
         dc.part("Guest or volunteer", "a real bitemporal table"),
         dc.md(dc.reflect("GUEST OR VOLUNTEER BRIEF — ten minutes", "Show one real bitemporal table, then take two questions.", [
                     "The DL columns, and one row's history ordered by system start.",
                     "One change that created a version; one correction if you have one.",
                     "Which strategy the model uses: full, incremental or balance.",
                     "If a defect once created a version, show it: the table is an audit of what the code did."])),
         dc.part("Shareback", "which clock?"),
         dc.md(dc.reflect("SHAREBACK — which clock?", "Each table takes one question: say the clock, then the filter.", [
                     "What was the associate's title on 2 November?",
                     "What did the dashboard show on the morning of day 2?",
                     "When did we learn about the correction?",
                     "Which rows does an auditor need to see?"])),
         dc.section(2, "Airflow orchestration", "s2"),
         dc.part("Orientation", "the DAG, and Friday's preview", time="09:45"),
         dc.anchor("Yesterday's project builds when you type dbt build. Who types it at six in the morning?",
                   "Orchestration: deciding when the pipeline's parts run, in what order, with retries, logs and alerts.",
                   "A product's promises about delivery time and freshness are kept by the scheduler, not by the SQL.",
                   "Read a DAG as a drawing; then the demo stack runs Day 3's project on a schedule."),
         dc.figure("d4-dag", "The challenge's DAG: start, a freshness gate, the dbt task group, publish, end, with callbacks",
                   ["The freshness gate runs first so a stale feed fails the run before any compute is spent.",
                    "Cosmos renders the dbt project as one task per model and test, in dbt's own order.",
                    "Callbacks live in configuration, not in the DAG's work: on failure, on retry, on SLA miss.",
                    "The schedule is a cron in a time zone; catchup is off; retries have backoff."]),
         dc.code(f"!sed -n '/^with DAG/,/^) as dag:/p' {AL}/dags/eod_prices/dags/eod_prices_daily.py\n!grep -n '>>' {AL}/dags/eod_prices/dags/eod_prices_daily.py\n# Day 2's generated product, orchestrated: the schedule is the contract's 07:30 ET commitment, 06:30 weekdays New York. Read >> as 'and then'."),
         dc.md(dc.say(["Friday: you get CSV files about a fictional wealth manager called Atlas and a README. Phase 1 is the certification bar: sources, the three layers, tests, and understanding the orchestration. Two to three hours for most teams. Phase 2 is fourteen extensions you choose from. We watch you build it; nobody hands out solutions.",
                       "Work in data_products/atlas_elt, not in the challenge folder. If you run it in the wrong folder, that is on you, and now you have been told."])),
         dc.break_(15, "10:15"),
         dc.part("Demo", "the stack, a run, the UI, a controlled failure", time="10:15"),
         dc.anchor("What is actually running when you type astro dev start?",
                   "A DAG processor, a scheduler, workers, a triggerer, an API server with the UI, and a metadata database: on your laptop as containers, or hosted by Astronomer.",
                   "Knowing the pieces explains the symptoms: an import error is the processor; a queued task is the scheduler; a failed task is a worker log.",
                   "Trigger a run, read the graph and the grid, open a task log, read the code tab, break it on purpose, fix it."),
         dc.figure("d4-airflow-components", "Airflow's components, locally and hosted",
                   ["The DAG processor parses dags/ and reports import errors; the scheduler decides what is due; workers run tasks; the triggerer handles deferred waits; the API server serves the UI.",
                    "astro dev start runs all of them as containers on the laptop; a hosted Astro deployment is the same thing run for you and vended per team."]),
         dc.md(dc.demo("the stack, a run, the UI", "Trigger a run on the local Astro stack and read it in the UI the way learners will.", [
                  f"Before the day, in `{AL}/`: `bash run.sh start`.",
                  "Run the cells below: seed, trigger, wait, status.",
                  "Open http://localhost:8080: the DAGs list with owner, schedule and tags.",
                  "Graph view: five boxes and the dbt task group.",
                  "Grid view: one column per run.",
                  "Click `publish_to_catalog` and open its log: the published rows are in it.",
                  "Code tab: the DAG file as deployed.",
                  "Say: learners use the same commands: `astro dev run dags list`, `dags trigger`, `tasks states-for-dag-run`."])),
         dc.code(f"!bash {AL}/run.sh seed 2>&1 | grep -E 'Done|rror'"),
         dc.code(f"!bash {AL}/run.sh trigger && bash {AL}/run.sh wait"),
         dc.code(f"!bash {AL}/run.sh status | tail -30"),
         dc.code(f"!sed -n '/^default_args/,/^}}/p' {AL}/dags/portfolio_analytics/dags/portfolio_analytics_daily.py\n!grep -n 'def on_' {AL}/dags/portfolio_analytics/dags/callbacks.py\n# default_args are inherited by every task: retries with backoff, the failure and retry callbacks. The SLA-miss callback sits on the DAG."),
         dc.figure("d4-blueprints", "Astro blueprints: YAML in, a DAG out",
                   ["A blueprint is Python written once by the platform team with placeholders; a dataset's YAML fills them; the result is a registered DAG that triggers a Databricks job.",
                    "Over ninety percent of products fit a blueprint; a custom DAG is for the rest, and can become a new blueprint.",
                    "The challenge is Python on purpose: once the Python makes sense, the YAML is just configuration."]),
         dc.code("!sed -n '1,30p' ../../reference/DataCreators-client/dev-container/edo-training-data-products/data_products/.blueprints/dag_exec_check.py\n# A platform blueprint from the vended repository: the Python learners never write, filled from YAML."),
         dc.md(dc.demo("a controlled failure, then the repair", "Break the freshness gate on purpose, read the log, repair, rerun.", [
                  "Run the stale cell: the custodian feed looks two days old; a run is triggered.",
                  "Watch the freshness gate fail and everything downstream go `upstream_failed`: no publish, no rows.",
                  "Open the failed task's log in the UI and read the first useful line aloud.",
                  "Run the fresh cell: the feed is stamped fresh, a run is triggered, green.",
                  "Say: this is the same drill as the challenge's Phase 2 and Friday's questions: late input, failed check, repeated run."])),
         dc.code(f"!bash {AL}/run.sh stale && bash {AL}/run.sh trigger && bash {AL}/run.sh wait && bash {AL}/run.sh status | grep -E 'source_freshness|publish|state' | head -6"),
         dc.code(f"!bash {AL}/run.sh fresh && bash {AL}/run.sh trigger && bash {AL}/run.sh wait"),
         dc.part("Challenge 10", "Airflow practical", time="10:45"),
         dc.md(dc.challenge("Airflow practical (challenge 03)", "challenges/v1/03-airflow-orchestration/README.md", "until 13:30, with lunch",
                      "Wire, schedule and run the Portfolio Analytics DAG with Cosmos; Phase 2 is production operations.",
                      [("Prerequisites, in this order", [
                          "`mise run setup:databricks` done, in a terminal where `echo $DBT_CATALOG` prints a value.",
                          "`(cd challenges/v1/02-dbt-pipeline/dbt && dbt seed)`: the DAG reads the same four feeds, refreshed.",
                          "From the repo root, `astro dev start`, only after setup finished; the UI address is the one astro prints, not a fixed localhost:8080."]),
                       ("Phase 1, about 1.5 hours", [
                          "1 Why orchestration.", "2 Anatomy of a DAG.", "3 Connect to Databricks: `dbt debug`.",
                          "4 The freshness gate: `astro dev run tasks test portfolio_analytics_daily source_freshness_check 2026-05-04`.",
                          "5 The Cosmos `DbtTaskGroup`.",
                          "6 Wire the chain, the one TODO: `start >> source_freshness_check >> dbt_pipeline >> publish_to_catalog >> end`.",
                          "7 Scheduling: a timezone-aware cron.", "8 Retries and exponential backoff.", "9 First full run.", "10 Reading logs and re-running."]),
                       ("Phase 2", [
                          "1 The vendor-neutral alert transport.", "2 Tiered failure alerting.", "3 The P2 and P3 tiers: SLA miss and retry.",
                          "4 Wire the callbacks and the SLA into the DAG.", "5 The freshness gate as a contract.", "6 The monitoring config.",
                          "7 The runbook and the consumer guide.", "8 Structural tests for the DAG.", "9 Stretch: the `DatabricksSubmitRunOperator` variant.", "10 Capstone: a production-ready DAG."])],
                      "`mise run challenge:verify 03` is a static check of the wiring; the live run is the evidence: graph, logs, states.",
                      stretch="What happens if the input is late? If the quality check fails? If the run is repeated? Show a log or output check for each answer.")),
         dc.md("""
         | Symptom | Cause | Fix |
         |---|---|---|
         | `dags list-import-errors` shows a Cosmos error ending in an empty catalog name | Astro started before Databricks setup wrote the env | New terminal where `echo $DBT_CATALOG` prints a value, then `astro dev restart --wait 5m` |
         | The freshness gate fails on a fresh seed | Connection error, not staleness: the task now says which | Same cold-start fix; then re-run the task |
         | `airflow: command not found` | The CLI lives in the containers | Prefix with `astro dev run` |
         | `astro dev parse` says 0 DAGs | It does not mount data_products | Use the README's `python -c "import ast…"` check and `astro dev run dags list-import-errors` |
         | A BashOperator DAG is rejected | CG's cluster policy blocks arbitrary-shell operators | PythonOperator calling subprocess, as the starter does |
         | Tasks run one at a time | `max_active_tasks` (learners: 4; this laptop: 1 for DuckDB) | Expected; explain why |
         | `dbt docs serve` fails to bind | `DBT_HOST` is the Databricks host | `--host 127.0.0.1 --port 8081` |
         | Two Astro environments on one laptop | Another project is running | `docker ps` and look for the devcontainer's scheduler |
         """),
         dc.break_(60, "13:00", lunch=True),
         dc.part("Shareback", "one run, one log line, one output check per pair", time="13:00"),
         dc.md(dc.reflect("SHAREBACK — 13:30, one pair at a time", "Show the run ID, the log line that told you what happened, and the table it produced.", ["Keep credential and path errors separate from the intended data-quality failure.", "Fast finishers: what happens if the input is late? If the quality check fails? If the run is repeated?"])),
         dc.section(3, "CI/CD and release operations", "s3"),
         dc.part("Demo", "GitOps, Harness, Datadog", time="13:30"),
         dc.anchor("Your DAG and dbt project are in Git. How do they get to production, and who presses the button?",
                   "Continuous integration (merge often) and continuous deployment (release often), driven by GitHub events through Harness, into Astro and Databricks, watched by Datadog.",
                   "Creators rarely operate this layer, but they read it: which pipeline ran, where the logs are, who deployed last night.",
                   "The GitOps picture; a Harness walkthrough (guest, screenshots, or the anchor); monitors as the SLIs made visible."),
         dc.figure("d4-cicd", "From a branch to production: pull request, merge, Harness, SQA, production with a change record",
                   ["Integration is merging; continuous means daily or hourly, not monthly. Deployment is releasing to an environment.",
                    "A merge fires a webhook; Harness builds, tests and deploys; the SQA environment is shared, so check who deployed last; production needs a change record.",
                    "GitOps: the Git history becomes the history of what was live. CG is 'halfway': events trigger pipelines, with an approval step between."]),
         dc.md(dc.whiteboard("CI/CD", [
             ("What do CI and CD mean?", "Integration: merging a feature branch, often. Deployment: releasing to an environment, including production, often."),
             ("Why bother?", "Faster feedback that something is broken; a shared understanding of the product across the team; observability of the lifecycle."),
             ("What are the downsides?", "Automation without a real human in the loop; fragility; correlated failures (when one shared system is down, everything is); the maintenance, approval and audit burden. It is not free."),
             ("What is Harness here?", "The CI/CD system, roughly GitOps: a pull request submitted and approved triggers the pipeline. It isolates the creator from the deployment machinery."),
         ])),
         dc.md(dc.demo("Harness, with screenshots or a guest", "Walk a deployment to SQA and then to production: live if someone has access, else from the pre-flight screenshots.", [
                  "Pick the environment and find the repository's pipeline.",
                  "SQA: Run, apply the SQA input set, choose the feature branch, run; a few minutes.",
                  "Check who deployed to SQA last and whether they finished testing: SQA is shared.",
                  "Production: the PRD pipeline, fixed values, the release branch, and a change record (CRQ) number before anything runs.",
                  "Open the logs of a failed execution.",
                  "Say: secrets live in AWS Secrets Manager, never in code or a chat; an API token that lets an AI assistant trigger deployments is a risk, not a shortcut."])),
         dc.code(f"!sed -n '1,40p' {AL}/dags/portfolio_analytics/include/monitoring/portfolio_analytics.yml\n# The challenge's monitoring config: six panels, each an SLI with an alert condition and a channel. This is what a Datadog monitor is for: the promises from Day 2, watched."),
         dc.break_(15, "14:15"),
         dc.part("Activity 10", "release decision", time="14:15"),
         act("10"),
         dc.md("""
         <details><summary><strong>Discussion notes for Activity 10</strong></summary>

         - The failed candidate stays blocked: three IDs appear twice, and until someone knows why, publishing it would publish a lie about uniqueness.
         - Yesterday's accepted output is acceptable only if the consumer's freshness commitment allows a one-day-old sheet; the contract says, not the engineer.
         - Missing information: which three IDs, whether the source re-delivered, whether the dedup rule or the source changed, who owns the source. The consumer update names what is known, what is not, and when the next update comes.
         - Who overrides a failed gate, and where that decision is recorded, is a governance question worth leaving open in the room.

         </details>
         """),
         dc.part("Activity 11", "explain a failure and repair", time="14:35"),
         act("11"),
         dc.md("""
         <details><summary><strong>Prepared failure example</strong> (for pairs whose environment was blocked)</summary>

         Expected: the freshness gate fails because the custodian feed is older than its `error_after` threshold; `dbt_pipeline` and `publish_to_catalog` are `upstream_failed`; no rows are published; the previous run's output stands. Observed in the demo stack: the `source_freshness_check` log ends with "dbt source freshness failed: the custodian feed breached its error_after threshold"; the repair was to refresh the feed and trigger a new run, which published eight rows. Distinguish this from a credentials or path error, whose first useful line names a missing environment value or executable.

         </details>
         """),
         dc.part("Friday preparation", "the checklist, then the close", time="14:50"),
         dc.md(dc.reflect("FRIDAY CHECKLIST — every learner, before leaving", "Five checks; any failure goes on the list with a name and a time it will be fixed.", [
                     "☐ Open `challenges/v1/04-atlas-capstone/README.md` and read the plan of the day.",
                     "☐ From the repo root: `test -f .mise.toml && test -d data_products/atlas_elt && echo OK`.",
                     "☐ `mise exec -- databricks auth describe --profile DEFAULT`.",
                     "☐ From `data_products/atlas_elt`: `dbt debug` passes.",
                     "☐ `astro dev stop`, so tomorrow starts clean."])),
         dc.md(dc.leave_with(LEAVE_WITH)),
         *dc.qa_section(4)]
    return C
