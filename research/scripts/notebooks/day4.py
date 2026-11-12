"""Day 4 — Bitemporal loading and Airflow orchestration."""
import dc
from day3 import fig, wf, one_per_cell      # the same picture, %%writefile and one-command-per-cell helpers as Day 3
DAY, SLUG, TITLE = 4, "day4-airflow", "Bitemporal loading and Airflow orchestration"

F_BT_MODEL = """
-- fx_rates_history: every FX rate the vendor has sent, with two clocks. Each run loads one delivery.
--   incremental_strategy  our own strategy: the macro in macros/bitemporal_load.sql
--   bitemporal_key        what makes two rows "the same thing": the currency
--   full_refresh=false    never rebuild this table from scratch: that would erase the history
{{ config(materialized='incremental', incremental_strategy='bitemporal_load',
          bitemporal_key='from_ccy', full_refresh=false) }}

select
    from_ccy,
    cast(rate as decimal(18, 6))                  as fx_rate,
    md5(cast(rate as varchar))                    as dl_row_hash,            -- a fingerprint: a different hash means the rate changed
    cast(rate_dt as date)                         as dl_business_start_dt,   -- business clock: the day the rate is for
    cast(null as date)                            as dl_business_end_dt,
    cast(now() at time zone 'UTC' as timestamp)   as dl_system_start_ts,     -- system clock: when the warehouse learned it, in UTC
    cast(null as timestamp)                       as dl_system_end_ts,
    true                                          as dl_current_ind          -- true while both clocks are open
from {{ ref('fx_deliveries') }}
where delivery_id = '{{ var("delivery") }}'       -- one delivery per run: dbt run --vars "delivery: D1"
"""
F_BT_MACRO = """
{# bitemporal_load: how a new delivery lands in the history table.
   dbt has written the model's SELECT (the delivery) to a temporary table and calls this macro with:
     target = the history table, source = the delivery, cols = the column names.
   Steps 1 and 2 run inside the macro (run_query); step 3 is returned, and dbt runs it last. #}
{% macro get_incremental_bitemporal_load_sql(arg_dict) %}
  {%- set target = arg_dict["target_relation"] -%}
  {%- set source = arg_dict["temp_relation"] -%}
  {%- set key = config.require('bitemporal_key') -%}
  {%- set cols = arg_dict["dest_columns"] | map(attribute='name') | list -%}

  {#- 1. Close the SYSTEM clock of every current row whose rate the delivery changes. -#}
  {%- set close_sql -%}
    update {{ target }} as t
    set dl_system_end_ts = s.dl_system_start_ts, dl_current_ind = false
    from {{ source }} as s
    where t.{{ key }} = s.{{ key }} and t.dl_current_ind and t.dl_row_hash <> s.dl_row_hash
  {%- endset -%}
  {% do run_query(close_sql) %}

  {#- 2. A later business date: carry the old row forward, with its BUSINESS clock ended the day before. -#}
  {%- set carry_sql -%}
    insert into {{ target }} ({{ cols | join(', ') }})
    select
      {%- for c in cols %}
        {%- if c == 'dl_business_end_dt' %} cast(s.dl_business_start_dt - interval 1 day as date)
        {%- elif c == 'dl_system_start_ts' %} s.dl_system_start_ts
        {%- elif c == 'dl_system_end_ts' %} cast(null as timestamp)
        {%- elif c == 'dl_current_ind' %} false
        {%- else %} t.{{ c }}
        {%- endif %}{{ "," if not loop.last }}
      {%- endfor %}
    from {{ target }} as t
    join {{ source }} as s
      on s.{{ key }} = t.{{ key }}
     and t.dl_system_end_ts = s.dl_system_start_ts          -- the rows step 1 has just closed
     and s.dl_business_start_dt > t.dl_business_start_dt    -- only for a later day, not for a correction
  {%- endset -%}
  {% do run_query(carry_sql) %}

  {#- 3. Insert the delivery's rows, unless the same rate is already current (so a re-run changes nothing). -#}
  insert into {{ target }} ({{ cols | join(', ') }})
  select {{ cols | join(', ') }}
  from {{ source }} as s
  where not exists (
      select 1 from {{ target }} as t
      where t.{{ key }} = s.{{ key }} and t.dl_current_ind and t.dl_row_hash = s.dl_row_hash
  )
{% endmacro %}
"""
# The GBP rows of the history table, in the order they were written. The times are the system clock (UTC), to the second.
H_GBP = ("!dbt show --inline \"select cast(fx_rate as varchar) as fx_rate, dl_business_start_dt as rate_for, dl_business_end_dt as rate_until, "
         "strftime(dl_system_start_ts, '%H:%M:%S') as believed_from, strftime(dl_system_end_ts, '%H:%M:%S') as believed_until, dl_current_ind as current "
         "from demo.fx_rates_history where from_ccy = 'GBP' order by dl_system_start_ts, dl_business_start_dt\" --limit 10")

BLOCKS = [
 dict(time="09:00–09:45", title="Bitemporal loading, on yesterday's price sheet", type="Demo + shareback", on_screen="Anchor › section 1, top to bottom (demos/price_sheet); a guest or volunteer's screen",
      purpose="Business time and system time; loading strategies; a worked history with a correction; which clock answers which question.",
      notes=["Eight steps on Day 3's price sheet, one command per cell: reset and build, look at the three FX deliveries, write the history model, write the macro, three loads with the GBP rows and a picture after each, then the three questions.",
             "The story: the vendor sends a wrong GBP rate for 4 November (1.628112, two digits swapped) and corrects it in the next delivery (1.268112). After load 3 GBP has four rows; name them A, B, C, D as the pictures do.",
             "The last query shows one GBP price in dollars twice, as was and as is: the link back to yesterday's price sheet, which could only ever show one.",
             "A volunteer or guest shows a real table for ten minutes if one was recruited yesterday; the demo covers the same ground either way.",
             "Shareback: each table answers one 'which clock?' question.",
             "Backup: bash demos/bitemporal/demo.sh runs the older associate example from one script."],
      say=["The vendor sends a wrong rate on Wednesday and corrects it on Thursday. What was the rate, and what did Wednesday's report say?",
           "Yesterday's snapshot kept one clock. Two clocks tell a new day from a correction."],
      transition="From history to timing: orchestration.", flex="Over time: show the macro picture but not the macro file; keep the three loads and the three questions."),
 dict(time="09:45–10:00", title="Orchestration and capstone orientation", type="Demo", on_screen="Anchor › section 2, steps 1 and 2 (demos/airflow_local); Friday preview",
      purpose="What orchestration is, on yesterday's price sheet; how to read a DAG file; a preview of Friday's work and its starting files.",
      notes=["Steps 1 and 2 of the challenge on the price_sheet_daily DAG: why orchestrate (the five-gaps picture), the path, the DAG picture, then the top of the DAG file and the DAG block.",
             "The first cell puts the TODO back (run.sh unwire), so the DAG starts as the learners' does.",
             "Friday: Phase 1 scope, two to three hours, the working folder rule."],
      say=["Airflow plays no instrument. It tells dbt when to play, and what to do when it goes wrong."],
      transition="Break, then the Airflow demo.", flex=""),
 dict(time="10:00–10:15", title="Break", type="Break", on_screen="", purpose="", notes=[], say=[], transition="", flex=""),
 dict(time="10:15–10:45", title="Airflow demonstration", type="Demo", on_screen="Anchor › section 2, steps 3 to 10; the Airflow UI at localhost:8080",
      purpose="Steps 3 to 10 of the challenge on the price sheet: the connection, the freshness gate, the Cosmos group, the one line of wiring, the schedule, retries, a green run, and a controlled failure with its repair.",
      notes=["Start the stack before the day (bash run.sh start). Every step is one command per cell; keep the UI open beside the notebook and switch to it at steps 6, 9 and 10.",
             "Step 6 is the learners' one line: run.sh wire replaces the TODO. Read >> as 'and then'.",
             "Step 9: a green run takes about half a minute here. The dbt show cell is the evidence, not the green boxes.",
             "Step 10: stale, trigger, wait about a minute: the gate goes yellow twice, then red, and the rest is upstream_failed. Then fresh, and Clear the failed task in the UI with Include Downstream. The demo DAG waits 15 seconds between retries; the learners' waits 2 minutes, so tell them a failure takes about ten minutes to turn red.",
             "Close with the blueprint picture: at CG most DAGs come from a blueprint and YAML.",
             "Backup: portfolio_analytics_daily, the learners' own DAG, is in the same stack (bash run.sh trigger, wait, status with no DAG name)."],
      say=["A green graph is not evidence that the data is right. The rows are the evidence.",
           "You write one line today. Everything else, you read and prove."],
      transition="Challenge 10 until lunch.", flex="Short of time: steps 4, 6, 9 and 10. If the stack misbehaves, the status cell still shows the earlier runs."),
 dict(time="10:45–12:00", title="Challenge 10 — Airflow practical", type="Challenge", on_screen="Anchor › Challenge box; learners in challenges/v1/03-airflow-orchestration",
      purpose="Launch the assigned Airflow project; learners wire the chain, run tasks inside the scheduler, inspect states and logs.",
      notes=["Boot order matters: setup, then seeds, then astro dev start; the cold-start symptom and fix are in the anchor.", "Collect deployment and monitoring questions for the afternoon."],
      say=["Which run produced this result, and what proves the data is right?"],
      transition="Lunch.", flex="Fast finishers: the extension questions (late input, failed check, repeated run), then Phase 2."),
 dict(time="12:00–13:00", title="Lunch", type="Break", on_screen="", purpose="", notes=[], say=[], transition="", flex=""),
 dict(time="13:00–13:30", title="Continue Airflow practical, regroup at 13:30", type="Challenge + shareback", on_screen="Anchor › Challenge box",
      purpose="Resolve blockers; Phase 2 for those on it; regroup with one run, one log and one output check per pair.",
      notes=["Keep credential and path errors separate from the intended data-quality failure.", "Shareback: a pair shows the current run, a useful log line, and the warehouse output.",
             "For learners in Phase 2: the anchor's Phase 2 walkthrough shows each of the ten challenges on the price sheet, with the morning's failed run as the evidence for the alert tiers. Ten minutes on screen at 13:00 if several pairs are there."],
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
      parts=["Demo: two clocks on the price sheet, three deliveries, three questions", "Guest or volunteer: a real table", "Shareback: which clock?"]),
 dict(n=2, title="Airflow orchestration", anchor="s2", start="09:45",
      parts=["Orientation: why orchestrate, and reading a DAG", "Break", "Demo: the challenge's steps 3 to 10 on the price sheet", "Launch", "Challenge 10: Airflow practical", "Walkthrough: Phase 2 on the price sheet", "Lunch", "Shareback: one run, one log, one output check"]),
 dict(n=3, title="CI/CD and release operations", anchor="s3", start="13:30",
      parts=["Demo: GitOps, Harness, Datadog", "Break", "Activity 10: release decision", "Activity 11: explain a failure and repair", "Friday preparation"]),
]

def cells():
    A = {a["number"]: a for a in ACTIVITIES}
    act = lambda n: dc.md(dc.activity(n, A[n]["title"], A[n]["grouping"], A[n]["minutes"], A[n]["brief"], A[n]["outputs"], A[n].get("debrief"), A[n].get("early")))
    
    PS = "demos/price_sheet"
    DAGF = "dags/price_sheet/dags/price_sheet_daily.py"
    Q = ' | grep -v "secrets backend"'       # astro prints one warning line before every result; drop it
    C = [dc.title(4, TITLE, "anchor notebook"),

         *dc.how_to_use(4, "- Both demos build on Day 3's price sheet. Section 1 runs in `demos/price_sheet/` (its first cell resets the folder to Day 3's finished project). Section 2 runs the same project as the `price_sheet_daily` DAG on the local Airflow stack in `demos/airflow_local/`.\n- Before the day: Docker Desktop running, then `bash demos/airflow_local/run.sh start` and `bash demos/airflow_local/run.sh seed`. The Airflow UI is http://localhost:8080. Run sections 1 and 2 once before the room arrives.\n- Backups, not shown in the notebook: `bash demos/bitemporal/demo.sh` (the associate example) and the `portfolio_analytics_daily` DAG in the same stack (the learners' challenge DAG)."),
         dc.code(dc.setup_cell(4)),
         dc.agenda(SECTIONS, lead="Morning: history (bitemporal loading) and orchestration (Airflow), both on yesterday's price sheet, then a long practical. Afternoon: the deployment picture, then two short exercises that turn a failed run into a decision and a note. Close by checking Friday's starting line."),
         dc.section(1, "Bitemporal loading", "s1"),
         dc.part("Demo", "two clocks on the price sheet: three deliveries, three questions", time="09:00"),
         dc.anchor("The vendor sends a wrong GBP rate on Wednesday and corrects it on Thursday. What was the rate, and what did Wednesday's report say?",
                   "Two clocks on every row: business time (the day the rate is for) and system time (when the warehouse believed it). Nothing is overwritten; a correction adds a row.",
                   "Audit, reproducible reports and 'as was' questions all need the second clock. Yesterday's price sheet overwrites: it cannot answer them.",
                   "On yesterday's price sheet: a history model, a macro, three FX deliveries, then three questions."),
         dc.md(dc.whiteboard("loading strategies and two clocks", [
             ("How can new data land in a table?", "Truncate and reload; insert-overwrite; SCD type 2 (effective start and end dates keep history). Bitemporal is SCD2 with a second clock."),
             ("What are the two clocks?", "Business time: when the fact was true in the world (the business date). System time: when the warehouse loaded or believed it. Separate columns for start and end of each, plus a current indicator and a row hash."),
             ("Full, incremental, balance?", "Full: the source sends the whole book of record each run (expensive: every row re-versioned). Incremental: only new or changed records with a business key; a known key with new content ends the previous version. Balance: for monetary balances. Some models need a custom strategy."),
             ("Why does a correction matter?", "Because 'as was' must still answer what the report said on Wednesday, and 'as of' must give the corrected value today. Overwriting destroys the first; a status flag cannot express either."),
             ("UTC or local?", "The platform stamps system time in UTC; a run at 03:00 Pacific for the previous business day shows yesterday's business date. Always say which clock a date column is."),
         ], open_=True)),
         fig("d4-two-clocks", "Two clocks on every row: when it was true, and when we believed it", [
                 "Business clock: the day the rate is for. It comes from the data: the `rate_dt` in the vendor's file.",
                 "System clock: when the warehouse learned it. It comes from the load: the time the run happened, in UTC.",
                 "Yesterday's snapshot kept one clock (when dbt saw the change). Two clocks separate a new day from a correction."], height=380),
         dc.md("#### The path for the next thirty minutes"),
         fig("d4-bt-path", "The path: eight steps from yesterday's price sheet to a table that remembers", height=380),
         dc.md("#### Step 1 — Start from yesterday's price sheet"),
         dc.code(f'%cd {{HERE}}/{PS}\n# Day 4\'s copy of yesterday\'s price sheet. dbt commands run from the project folder, as yesterday.'),
         dc.code('!bash reset.sh\n# The starting point: Day 3\'s finished project. Four models, the loop model, the to_usd macro and the tests.'),
         dc.code('!dbt seed\n# The raw data first, as yesterday. One new seed today: fx_deliveries.'),
         dc.code('!dbt build --exclude resource_type:seed\n# The models and the tests, in graph order: yesterday\'s price sheet, built and passing.'),
         dc.md("#### Step 2 — The deliveries: three FX files from the vendor"),
         dc.code('!dbt show --inline "select delivery_id, from_ccy, rate_dt as rate_for, cast(rate as varchar) as rate from demo.fx_deliveries order by delivery_id, from_ccy" --limit 10\n# Three deliveries in one seed. D1: the rates for 3 November. D2: the rates for 4 November, with a wrong GBP rate (1.628112: two digits swapped). D2-CORR: the vendor sends 4 November again, corrected (1.268112).'),
         dc.md("#### Step 3 — The history model: two clocks on every row"),
         wf("models/history/fx_rates_history.sql", F_BT_MODEL),
         dc.md("#### Step 4 — The macro: how a delivery lands in the table"),
         fig("d4-bt-macro", "What the macro does with each row of a new delivery", [
                 "The model names a strategy dbt does not know, `bitemporal_load`. dbt looks for a macro called `get_incremental_bitemporal_load_sql` and uses it: found in `macros/`, as yesterday.",
                 "A different rate with a later business date is a new day. A different rate for the same business date is a correction.",
                 "Rows are only added. The one update is closing a system clock, so nothing is lost.",
                 "CG's platform does the same job with `bitemporal_load_v2`, built on Delta `MERGE`."], height=380),
         wf("macros/bitemporal_load.sql", F_BT_MACRO),
         dc.md("#### Step 5 — Load 1: the first day"),
         dc.code('!dbt run --select fx_rates_history --vars "delivery: D1"\n# --vars passes a value into the model: which delivery to load. The table does not exist yet, so dbt creates it from the SELECT; the macro is not needed on the first run.'),
         dc.code(f'{H_GBP}\n# One row for GBP: the rate for 3 November, believed since load 1, open on both clocks.'),
         fig("d4-bt-load-1", "After load 1: one row, open on both clocks", height=200),
         dc.md("#### Step 6 — Load 2: a new day, with one wrong rate"),
         dc.code('!dbt run --select fx_rates_history --vars "delivery: D2"\n# The table exists now, so the macro runs: close, carry forward, insert.'),
         dc.code(f'{H_GBP}\n# Three rows. Row A: its system clock is closed. Row B: the same rate, carried forward with its business clock ended at 3 November. Row C: the new rate for 4 November, which is wrong, and current.'),
         fig("d4-bt-load-2", "After load 2: the old rate is kept for its own day, and the new rate is current", height=420),
         dc.md("#### Step 7 — Load 3: the vendor's correction"),
         dc.code('!dbt run --select fx_rates_history --vars "delivery: D2-CORR"\n# The same business date, a different rate: a correction.'),
         dc.code(f'{H_GBP}\n# Four rows. Row C, the wrong rate, has its system clock closed: it is kept, not erased. Row D is the corrected rate for the same day. Nothing was carried forward this time: a correction replaces a version, it does not end it.'),
         fig("d4-bt-load-3", "After load 3: the wrong rate is closed and kept; the corrected rate is current", height=460),
         dc.md("#### Step 8 — Three questions, one table"),
         fig("d4-bt-questions", "Three questions, each answered by filtering on the clocks", height=340),
         dc.code('!dbt show --inline "select from_ccy, cast(fx_rate as varchar) as fx_rate, dl_business_start_dt as rate_for from demo.fx_rates_history where dl_current_ind order by from_ccy" --limit 10\n# AS IS: what is true now. Both clocks open.'),
         dc.code('!dbt show --inline "select from_ccy, cast(fx_rate as varchar) as fx_rate, dl_business_start_dt as rate_for from demo.fx_rates_history where dl_business_start_dt <= date \'2026-11-03\' and coalesce(dl_business_end_dt, date \'9999-12-31\') >= date \'2026-11-03\' and dl_system_end_ts is null order by from_ccy" --limit 10\n# AS OF 3 November, with today\'s knowledge: the business clock covers the date, the system clock is open.'),
         dc.code('!dbt show --inline "select from_ccy, cast(fx_rate as varchar) as fx_rate, dl_business_start_dt as rate_for from demo.fx_rates_history where dl_system_start_ts < (select max(dl_system_start_ts) from demo.fx_rates_history) and coalesce(dl_system_end_ts, timestamp \'9999-12-31\') >= (select max(dl_system_start_ts) from demo.fx_rates_history) and dl_business_end_dt is null order by from_ccy" --limit 10\n# AS WAS, just before the correction arrived: the system clock covers that moment. GBP shows the wrong rate, because that is what we believed then.'),
         dc.code('!dbt show --inline "select p.instrument_id, p.price_date, cast(p.price_native as varchar) as price_gbp, cast(h.fx_rate as varchar) as fx_rate, cast(round(p.price_native * h.fx_rate, 4) as varchar) as price_usd, case when h.dl_system_end_ts is null then \'as is\' else \'as was\' end as version from demo.stg_prices p join demo.fx_rates_history h on h.from_ccy = p.native_ccy and h.dl_business_start_dt = p.price_date where p.native_ccy = \'GBP\' and p.price_date = date \'2026-11-04\' order by h.dl_system_start_ts" --limit 10\n# The same price in dollars, twice: what Wednesday\'s price sheet said, and what it says now. Both answers come from one table.'),
         dc.md("""
         | The question | Which clock | The filter |
         |---|---|---|
         | What is current? | both open | `dl_current_ind` |
         | What was true on date D, as we know it today? | business covers D, system open | `dl_business_start_dt <= D and coalesce(dl_business_end_dt, '9999-12-31') >= D and dl_system_end_ts is null` |
         | What did the report say at time T? | system covers T | `dl_system_start_ts <= T and coalesce(dl_system_end_ts, '9999-12-31') > T` |
         | Which versions did a correction replace? | same business start, later system start | order by `dl_system_start_ts` within the key |
         """),
         dc.code('%cd {HERE}'),
         dc.part("Guest or volunteer", "a real bitemporal table"),
         dc.md(dc.reflect("GUEST OR VOLUNTEER BRIEF — ten minutes", "Show one real bitemporal table, then take two questions.", [
                     "The DL columns, and one row's history ordered by system start.",
                     "One change that created a version; one correction if you have one.",
                     "Which strategy the model uses: full, incremental or balance.",
                     "If a defect once created a version, show it: the table is an audit of what the code did."])),
         dc.part("Shareback", "which clock?"),
         dc.md(dc.reflect("SHAREBACK — which clock?", "Each table takes one question: say the clock, then the filter.", [
                     "What was the GBP rate for 3 November?",
                     "What rate did Wednesday morning's price sheet use for 4 November?",
                     "When did we learn about the correction?",
                     "Which rows does an auditor need to see?"])),
         dc.section(2, "Airflow orchestration", "s2"),
         dc.part("Orientation", "why orchestrate, and reading a DAG", time="09:45"),
         dc.anchor("Yesterday's price sheet builds when you type dbt build. Who types it at six in the morning?",
                   "Orchestration: deciding when the pipeline's parts run, in what order, with retries, logs and alerts.",
                   "A product's promises about delivery time and freshness are kept by the scheduler, not by the SQL.",
                   "Yesterday's price sheet as an Airflow DAG, in the same ten steps as your challenge."),
         dc.md("#### 1 — Why orchestration"),
         fig("d4-why-orchestration", "Five things a hand-typed dbt build cannot do, and what Airflow gives you for each", height=400),
         dc.md("#### The path: the ten steps of the challenge, on the price sheet"),
         fig("d4-airflow-path", "The path: read the DAG, then wire it, run it and break it", height=380),
         fig("d4-ps-dag", "The DAG we will run: a gate, yesterday's models as tasks, a publish step", [
                 "The freshness gate runs first, so a stale feed stops the run before anything is built.",
                 "Cosmos turns the dbt project into one task per model, then the tests, in dbt's own order.",
                 "`publish_to_catalog` is the deliverable: it carries the 90-minute SLA.",
                 "`start` and `end` do no work: they make the graph easy to read."], height=300),
         dc.code('%cd {HERE}/demos/airflow_local\n# The local Airflow stack. From here on, the commands are the ones learners type in their container.'),
         dc.code('!bash run.sh unwire\n# The starting point: the DAG as learners get it. Every task is built; the one line that connects them is a TODO.'),
         dc.code(f"!sed -n '1,16p' {DAGF}\n# Read the top of the file. What runs first, and why? Which task carries the SLA? Where does dbt run?"),
         dc.md("#### 2 — Anatomy of a DAG"),
         fig("d4-dag-anatomy", "A DAG is a Python file: the DAG(...) block, the tasks inside it, and >> between them", height=320),
         dc.code(f"!sed -n '/^default_args/,/^) as dag:/p' {DAGF}\n# default_args: what every task inherits. Then the DAG itself: its id (the same as the file name), its schedule, its start date, its tags."),
         dc.code(f"!python -c \"import ast; ast.parse(open('{DAGF}').read()); print('parses OK')\"\n# The cheapest check: is the file valid Python? No Airflow needed."),
         dc.code(f'!astro dev run dags list-import-errors{Q}\n# The real check: did Airflow load every DAG file? "No data found" is the good answer. Airflow runs inside containers, so its commands start with: astro dev run'),
         dc.md(dc.say(["Friday: you get CSV files about a fictional wealth manager called Atlas and a README. Phase 1 is the certification bar: sources, the three layers, tests, and understanding the orchestration. Two to three hours for most teams. Phase 2 is fourteen extensions you choose from. We watch you build it; nobody hands out solutions.",
                       "Work in data_products/atlas_elt, not in the challenge folder. If you run it in the wrong folder, that is on you, and now you have been told."])),
         dc.break_(15, "10:15"),
         dc.part("Demo", "connect, gate, group, wire, schedule, retry, run, repair", time="10:15"),
         dc.anchor("What is actually running when you type astro dev start?",
                   "A DAG processor, a scheduler, workers, a triggerer, an API server with the UI, and a metadata database: on your laptop as containers, or hosted by Astronomer.",
                   "Knowing the pieces explains the symptoms: an import error is the processor; a queued task is the scheduler; a failed task is a worker log.",
                   "Steps 3 to 10 on the price sheet: one command per cell, and the UI at http://localhost:8080 beside it."),
         fig("d4-airflow-components", "Airflow's components, locally and hosted",
                   ["The DAG processor parses dags/ and reports import errors; the scheduler decides what is due; workers run tasks; the triggerer handles deferred waits; the API server serves the UI.",
                    "astro dev start runs all of them as containers on the laptop; a hosted Astro deployment is the same thing run for you and vended per team."]),
         dc.md("#### 3 — Connect: can dbt reach the warehouse from inside Airflow?"),
         dc.code('!bash run.sh dbt price_sheet debug --connection | tail -3\n# dbt debug, run inside the scheduler container, in the price sheet project. Learners: (cd data_products/portfolio_analytics/dbt && dbt debug), and the answer comes from Databricks.'),
         dc.code("!bash run.sh seed 2>&1 | grep -E 'Done|rror'\n# The vendor delivers: the raw feeds land in the warehouse. Learners do this once in the prerequisites: dbt seed."),
         dc.md("#### 4 — The first task: the freshness gate"),
         fig("d4-freshness-gate", "The freshness gate: how old is the feed, and does the run carry on?", [
                 "`dbt source freshness` reads the newest `vendor_ts` and compares it with now.",
                 "Only an `error_after` breach fails the command. A `warn_after` breach prints a warning and the run carries on, so where you put `error_after` is the real decision.",
                 "A `PythonOperator`, not a `BashOperator`: CG governance blocks operators that run arbitrary shell, so the dbt call is wrapped in a Python function."], height=340),
         dc.code("!grep -n -B1 -A4 'loaded_at_field' dags/price_sheet/dbt/models/sources.yml\n# The contract for the feed: which column says when it arrived, when to warn, when to stop."),
         dc.code(f"!sed -n '/^def _check_source_freshness/,/^        )/p' {DAGF}\n# The task's function: run dbt source freshness, and raise an error if it fails. Raising is what fails the task."),
         dc.code("!astro dev run tasks test price_sheet_daily source_freshness_check 2026-11-12 2>&1 | grep -E -o '(START|PASS|WARN|ERROR) freshness of [a-z_.]+|new_state=[a-z_]+'\n# Run this one task on its own: no schedule, no waiting for the tasks before it. PASS, then new_state=success."),
         dc.md("#### 5 — The Cosmos task group: yesterday's models become tasks"),
         fig("d4-cosmos", "Cosmos reads the dbt project and makes one Airflow task per model, in dbt's order", [
                 "The dbt project already knows its own graph, from `source()` and `ref()`. Cosmos reuses it.",
                 "It needs to know where the project is (`ProjectConfig`) and how to connect (`ProfileConfig`, which reads the project's `profiles.yml`).",
                 "`TestBehavior.AFTER_ALL`: the tests run once, after every model is built."], height=340),
         dc.code(f"!sed -n '/^    dbt_pipeline = DbtTaskGroup/,/^    )/p' {DAGF}\n# The whole dbt project in one call. Nobody writes a task per model."),
         dc.code(f'!astro dev run tasks list price_sheet_daily{Q}\n# Five tasks named dbt_pipeline.<model>_run and one dbt_test: yesterday\'s models. Plus the four tasks around them.'),
         dc.md("#### 6 — Wire the chain: the one line learners write"),
         dc.code(f'!grep -n "TODO" {DAGF} || echo "no TODO left: the chain is already wired"\n# Five tasks exist, and nothing connects them yet.'),
         dc.code('!bash run.sh wire\n# The TODO replaced by one line. Read >> as "and then". The task group counts as one step: it waits for the gate, and publish waits for all of it.'),
         dc.code("!astro dev run dags reserialize > /dev/null 2>&1; echo 'Airflow has read the DAG files again'\n# Ask Airflow to read the DAG files now, not at its next scan."),
         dc.code("!python -m pytest dags/price_sheet/tests -q -k chain\n# The check that the chain is wired. Learners: mise run challenge:verify 03. Then open the Graph view in the UI: five boxes, left to right."),
         dc.md("#### 7 — Scheduling: a cron in a time zone"),
         fig("d4-cron", "The schedule: five cron fields, and a start date that carries the time zone", [
                 "`0 6 * * 1-5` is 06:00, Monday to Friday. Weekdays only: markets are closed at the weekend.",
                 "Airflow stores times in UTC. A start date with no time zone would let 06:00 drift by an hour when the clocks change; `Europe/London` pins it.",
                 "`max_active_tasks` is a third setting: how many tasks run at once inside one run. Here 1, because the demo warehouse takes one writer; the learners' DAG has 4."], height=380),
         dc.code(f'!astro dev run dags details price_sheet_daily 2>&1 | grep -i -E "timetable|max_active"\n# The schedule as Airflow understood it.'),
         dc.md("#### 8 — Retries and backoff"),
         fig("d4-retries", "Retries: a task that fails waits and tries again, and only alerts a person when the retries run out", [
                 "`retries: 2` means three attempts. `retry_exponential_backoff` doubles the wait each time.",
                 "A task waiting to retry is `up_for_retry`, yellow in the UI: the policy is working, the task is not stuck.",
                 "The demo waits 15 seconds, so you see it within a minute. The learners' DAG waits 2 minutes, then 4: a failure takes about ten minutes to turn red."], height=340),
         dc.code(f"!sed -n '/^default_args/,/^}}/p' {DAGF}\n# Set once, inherited by every task."),
         dc.md("#### 9 — The first full run"),
         dc.code(f'!astro dev run dags unpause price_sheet_daily{Q}\n# A new DAG starts paused: Airflow knows it and will not run it. "No paused DAGs were found" means it was unpaused before.'),
         dc.code("!astro dev run dags trigger price_sheet_daily 2>&1 | grep -c queued\n# Ask for one run now, on top of the schedule. 1 means one run was queued."),
         dc.code("!bash run.sh wait price_sheet_daily\n# Watch it in the UI while this polls: Grid (runs over time), Graph (the tasks of one run), then a task's Logs."),
         dc.code("!bash run.sh status price_sheet_daily\n# The run, then the state of every task in it. Learners: astro dev run dags list-runs, then tasks states-for-dag-run."),
         dc.code("!bash run.sh dbt price_sheet show --select fct_prices_usd --limit 5\n# The proof is in the warehouse, not in the green boxes: the same rows a hand-typed dbt build produces."),
         dc.md("#### 10 — Reading logs and re-running: break it, read it, fix it, clear it"),
         fig("d4-clear", "A failed run: read the log, fix the cause, then clear the failed task to re-run it and everything after it", [
                 "Clearing re-queues the task and the tasks after it, in the same run. No new run is created.",
                 "Clear from the UI: it clears the one run you clicked. The command-line version selects by date and can clear several runs at once.",
                 "'Mark success' skips the check instead of fixing it: the tasks after it run on whatever data is there."], height=340),
         dc.code("!bash run.sh stale price_sheet_daily\n# Break it on purpose: the vendor feed now looks two days old."),
         dc.code("!astro dev run dags trigger price_sheet_daily 2>&1 | grep -c queued"),
         dc.code("!bash run.sh wait price_sheet_daily\n# About a minute. In the UI the gate goes yellow (up_for_retry) twice, then red."),
         dc.code("!bash run.sh status price_sheet_daily | grep -E 'task_id|freshness|dbt_pipeline|publish'\n# The gate failed; everything after it is upstream_failed. Nothing was built and nothing was published: yesterday's price sheet stands. In the UI: click the red task, then Logs, and read the first useful line."),
         dc.code("!bash run.sh fresh price_sheet_daily\n# Fix the cause: the feed arrives. Then, in the UI: click the failed task, Clear, tick Include Downstream, Confirm."),
         dc.code("!bash run.sh wait price_sheet_daily\n# After the Clear in the UI: the same run, green this time. (No browser? Trigger a new run with the cell above.)"),
         dc.md("#### At CG: most DAGs come from a blueprint"),
         dc.figure("d4-blueprints", "Astro blueprints: YAML in, a DAG out",
                   ["A blueprint is Python written once by the platform team with placeholders; a dataset's YAML fills them; the result is a registered DAG that triggers a Databricks job.",
                    "Over ninety percent of products fit a blueprint; a custom DAG is for the rest, and can become a new blueprint.",
                    "The challenge is Python on purpose: once the Python makes sense, the YAML is just configuration."]),
         dc.code("!sed -n '1,30p' ../../../../reference/DataCreators-client/dev-container/edo-training-data-products/data_products/.blueprints/dag_exec_check.py\n# A platform blueprint from the vended repository: the Python learners never write, filled from YAML."),
         dc.part("Launch", "from this demo to your challenge"),
         fig("d4-demo-to-challenge", "From this demo to the challenge: the same ten steps, on the Portfolio Analytics project", [
                 "Your DAG is `portfolio_analytics_daily`: the same five boxes, with yesterday's Portfolio Analytics models inside the group.",
                 "It runs on Databricks, so a run takes minutes, and a failed task takes about ten minutes to turn red.",
                 "Phase 1 has one line to write. Every other section asks you to read a piece and prove it works."], height=520),
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
         | The failed gate stays yellow for minutes | `up_for_retry`: two retries at 2 and 4 minutes before it turns red | Wait about ten minutes, or set `retries: 0` while practising |
         | `airflow: command not found` | The CLI lives in the containers | Prefix with `astro dev run` |
         | `astro dev parse` says 0 DAGs | It does not mount data_products | Use the README's `python -c "import ast…"` check and `astro dev run dags list-import-errors` |
         | `unpause` says `No paused DAGs were found` | The DAG was unpaused earlier; the state survives restarts | Nothing is wrong: go straight to `trigger` |
         | `tasks clear` wants to delete dozens of tasks | The CLI clears by date, not by run | Answer no; clear from the UI, which clears the run you clicked |
         | A BashOperator DAG is rejected | CG's cluster policy blocks arbitrary-shell operators | PythonOperator calling subprocess, as the starter does |
         | `dbt docs serve` fails to bind | `DBT_HOST` is the Databricks host | `--host 127.0.0.1 --port 8081` |
         | Two Astro environments on one laptop | Another project is running | `docker ps` and look for the devcontainer's scheduler |
         """),
         dc.part("Walkthrough", "Phase 2: production operations, on the price sheet"),
         dc.md(dc.demo("Phase 2 on the price sheet", "The ten Phase 2 challenges, one or two cells each, for when learners reach them.", [
                  "Use these cells at 13:00, or beside a learner who has reached Phase 2.",
                  "Every Phase 2 file ships complete: the task is to read each piece and prove it does what it says.",
                  "The failed run from step 10 is the evidence for challenges 1 to 4."])),
         dc.code('%cd {HERE}/demos/airflow_local'),
         dc.md("#### P1 — The alert transport: one function, no vendor in the code"),
         dc.code("!sed -n '/^def send_alert/,$p' dags/price_sheet/dags/notifications.py\n# Every chat message goes through send_alert. The webhook address lives in an Airflow connection called alert_webhook, not in the code."),
         dc.code("!grep -niE 'https?://|slack_sdk|hooks.slack' dags/price_sheet/dags/notifications.py || echo 'no hard-coded URL and no vendor SDK: good'"),
         dc.md("#### P2, P3 — Three tiers: who hears about what"),
         fig("d4-alert-tiers", "Four events, four callbacks, and who hears about each", [
                 "A page wakes a person, so it is kept for a task that failed after all its retries: the price sheet will be late.",
                 "An SLA miss means slow, not down: a message, no page. A retry is expected: a ticket, so a flaky task leaves a trail.",
                 "No Slack and no PagerDuty at CG: Datadog is the automatic sink, support pages through xMatters, Teams is the chat."], height=440),
         dc.code("!grep -n '^def \\|P[123]' dags/price_sheet/dags/callbacks.py | grep 'def \\|\"\"\"'\n# Each function, then the tier it serves: the two transports (Datadog, ticket) and the four callbacks."),
         dc.code("!bash run.sh alerts price_sheet_daily\n# What the callbacks did in the failed run from step 10: a ticket for each retry (P3), then a Datadog event (P1) and a Teams message (P2). No keys are set on this laptop, so each one logs instead of sending."),
         dc.md("#### P4 — Where each callback is attached"),
         dc.code(f'!grep -n "_callback\\|sla=" {DAGF} | grep -v ":    on_"\n# Three places: default_args (every task), the DAG (the SLA miss), and the last working task (success once per run, and the SLA itself).'),
         dc.md("#### P5 — The freshness gate as a contract"),
         dc.code("!bash run.sh dbt price_sheet source freshness --select source:vendor_feed\n# The same check the gate runs. warn_after 4 hours, error_after 6 hours: a feed five hours old only warns, and the run goes ahead. Is six hours the right line for a 07:30 deadline? That is a decision to defend, not a default."),
         dc.md("#### P6 — The monitoring config: six panels"),
         fig("d4-monitoring", "Alerting says something broke; monitoring shows something drifting", [
                 "Five panels cover most pipelines: run status, duration, task failures, SLA compliance, source freshness.",
                 "The sixth catches a feed that arrives on time but short. Freshness watches the clock; volume watches the row count."], height=380),
         dc.code("!grep -E 'name:|alert_condition:|alert_channel:' dags/price_sheet/include/monitoring/price_sheet.yml\n# Each panel: a metric, when it alerts, and where the alert goes."),
         dc.md("#### P7 — The runbook and the consumer guide"),
         dc.code("!grep -n '^## \\|^### Alert' dags/price_sheet/include/runbooks/price_sheet.md\n# The runbook: what the on-call engineer opens when an alert lands. Five alerts, each with symptom, diagnosis and remediation."),
         dc.code("!sed -n '1,16p' dags/price_sheet/include/launch/consumer-guide.md\n# The consumer guide: what a new user of the price sheet reads. Both documents live beside the DAG, so they change in the same pull request."),
         dc.md("#### P8 — Structural tests: the DAG's shape, checked in milliseconds"),
         dc.code("!python -m pytest dags/price_sheet/tests -v --no-header 2>&1 | grep -E 'PASSED|FAILED|passed|failed'\n# No Airflow and no warehouse: the files parse, the chain is wired, the callbacks and the SLA are attached, and no file holds a secret."),
         dc.md("#### P9 — Stretch: the other shape, dbt inside Databricks"),
         fig("d4-two-shapes", "Two ways to run dbt from Airflow: on the worker (Cosmos), or inside Databricks (CG's paved path)", [
                 "Cosmos: one Airflow task per model, so you see which model failed.",
                 "Submit-run: each Airflow task submits a Databricks job and waits. The job is one box; its logs live in Databricks.",
                 "The challenge's second DAG wires the failure and SLA callbacks but not the retry and success ones. Spotting that gap is the exercise."], height=420),
         dc.code("!sed -n '1,16p' ../../../../reference/DataCreators-client/dev-container/edo-training-data-products/challenges/v1/03-airflow-orchestration/solution/dags/databricks_submit_run_dag.py\n# The challenge's second DAG: the same pipeline, as jobs submitted to Databricks."),
         dc.md("""
         #### P10 — Capstone: the production checklist

         | Check | On the price sheet | Where you saw it |
         |---|---|---|
         | Schedule | `0 6 * * 1-5`, `Europe/London`, `catchup=False`, `max_active_runs=1` | step 7 |
         | Fail fast | `source_freshness_check` runs first | steps 4 and 10 |
         | Build | the Cosmos `DbtTaskGroup` | step 5 |
         | Retries | `retries=2` with backoff | step 8 |
         | Tiered alerting | failure and retry in `default_args`, SLA miss on the DAG | P2 to P4 |
         | SLA | `publish_to_catalog` carries `sla=timedelta(minutes=90)` | P4 |
         | Documents | runbook, consumer guide, monitoring config | P6, P7 |
         | No secrets | no token or host in any DAG file | P8 |
         """),
         dc.code('%cd {HERE}'),
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
         dc.code("!grep -E 'name:|alert_condition:|alert_channel:' demos/airflow_local/dags/price_sheet/include/monitoring/price_sheet.yml\n# The price sheet's monitoring config again: six panels, each with an alert condition and a channel. This is what a Datadog monitor is for: the promises from Day 2, watched."),
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
    return one_per_cell(C)
