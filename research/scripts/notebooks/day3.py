"""Day 3 — dbt practical and consolidation."""
import textwrap
import dc
DAY, SLUG, TITLE = 3, "day3-dbt", "dbt practical and consolidation"

BLOCKS = [
 dict(time="09:00–09:10", title="Ice-breaker, then recap: yesterday's platform in four pictures", type="Recap", on_screen="Anchor › section 1, Ice-breaker box, then Recap (four Day 2 diagrams)",
      purpose="Put everyone on the same page before dbt: where the tables live, what runs the SQL, and which box of the tools picture today zooms into.",
      notes=["Open with the ice-breaker, two or three minutes: one thing you always double-check, even though it is almost always fine. One answer each; type a few into the notebook. Its link to the day is tests: a check written down once and run every time. Return to it at Step 5.",
             "Then about seven minutes, four pictures from Day 2, two or three lines each. Ask one question per picture and let the room answer; do not re-teach.",
             "End on the tools picture with a finger on the dbt box: today is that box, tomorrow is the Airflow box above it.",
             "Anyone who missed Day 2: point them at the Day 2 anchor's section 3 for the full version."],
      say=["One line each: what is a lakehouse, what does Databricks do with your SQL, what is a Delta table?",
           "dbt holds no data and does no computing. It sends SQL; everything on these pictures is what receives it."],
      transition="So what is in a dbt project? Two CSVs and an empty folder.", flex="Short of time: the under-the-hood picture and the tools picture only."),
 dict(time="09:10–09:50", title="dbt from zero: one transformation through the whole life cycle", type="Demo", on_screen="Anchor › section 1, top to bottom (demos/price_sheet)",
      purpose="Show every kind of file in a dbt project being written and run once, on a small example, so the challenge's tasks are recognisable: project and profile, seeds, a source, a model, Jinja, ref, materialisation, tests failing and fixed, build, docs.",
      notes=["Before Step 1, two pictures set up the build: the three layers (staging, intermediate, marts: each one's job, folder and prefix) and the plan (four dashed boxes). The plan picture returns after Steps 2 to 7 as a tracker: yellow is what the step built, blue was built earlier, red has a failing test. Point at it each time so the room knows where it is.",
             "Present from the notebook; no whiteboard. The flow is: what dbt is for (one picture), why use it (the same transformation as a hand-run script that is silently wrong, then the without-and-with table), the path (eight steps on one picture), then the build. About five minutes for what and why, thirty for the steps, five for docs and the map to the challenge.",
             "In the build, each cell writes one file (%%writefile) or runs one command. Read the file, ask the room to predict the output, run it.",
             "Learners do not run the demo cells; their hands-on is the challenge, on Databricks. Say so once before Step 1. The demo runs against a local warehouse file on your laptop so each step answers at once; the notebook does not name it, and there is no need to dwell on it.",
             "About four minutes a step. Steps 5 and 6 are the point: one test fails on three rows with an empty dollar price, one line in staging fixes it, the build goes green. Never skip them.",
             "Testing is kept to one red-then-green cycle. Step 7 only adds a test written as a SQL file (no price is zero or negative); it passes. There is no second failure and no deduplication.",
             "Step 4 has a view-or-table beat: the models block of dbt_project.yml sets it per folder (staging and intermediate views, marts tables, as in the challenge), then config() in one model overrides it and is taken out again. It is challenge S6 in two minutes.",
             "At Step 3, spend two minutes on the Jinja picture: learners meet source(), ref() and config() in the first hour of the challenge. Loops and macros wait until 13:00.",
             "Run the section once before the room arrives so dbt's first-run delay is gone; the reset cell empties the folder each time.",
             "Commands are plain: a %cd cell at the start of each demo sets the working folder once, then cells are just !dbt run, !dbt test and so on, with dbt's full output. If you jump to a cell out of order, run that part's %cd cell first, or dbt runs in the other project."],
      say=["This script ran without an error and three prices are wrong. The SQL is the easy part; dbt is for everything around the SQL.",
           "You write a SELECT. dbt writes the CREATE, works out the order, and checks the result.",
           "The run was green and three prices were missing. A successful run says the SQL executed, not that the answer is right.",
           "A test is only a query for the rows that break a rule. No rows, it passes."],
      transition="The same kinds of file, more of them: the Portfolio Analytics challenge.", flex="Behind at 09:40: skip Step 7 (the test of your own) and say it is the pattern of C6. Ahead: open the docs site and click through the lineage graph."),
 dict(time="09:50–10:00", title="Challenge 9 — dbt practical: launch and first sections", type="Practical", on_screen="Anchor › Launch box; learners in challenges/v1/02-dbt-pipeline",
      purpose="Launch the assigned dbt project, explain the task sequence and the checks, and get everyone into Phase 1 (sources and staging) before the break.",
      notes=["Five-minute launch from the anchor: where to work, the first three commands, what a green section looks like, what reset deletes.",
             "Then circulate with the three-point checklist. Collect questions in the Q&A table for the recap.", "Break at 10:00; most will be in S1 or S2."],
      say=["The README teaches dbt as you go: concept, task, hint, check, a variation, then the solution. Attempt before you open the solution."],
      transition="Break; carry on after it.", flex="Anyone who knows dbt: skip to Phase 2 and the stretch list."),
 dict(time="10:00–10:15", title="Break", type="Break", on_screen="", purpose="", notes=[], say=[], transition="", flex=""),
 dict(time="10:15–11:00", title="Continue dbt practical", type="Practical", on_screen="Anchor › Walkthrough cells (for support)",
      purpose="Phase 1 complete for most; Phase 2 started by some; blockers resolved; questions collected.",
      notes=["Use the anchor's DuckDB walkthrough cells to show an expected result when someone is stuck; never type in their project.",
             "Access problems to the platform contact; code problems to the pair next to them first."],
      say=["Could this join pass its tests and still double the reported value?"],
      transition="At 11:00 the practical carries on to lunch.", flex=""),
 dict(time="11:00–12:00", title="Continue dbt practical: Phase 2 to lunch", type="Practical", on_screen="Anchor › Circulation checklist and symptom table; learners in challenges/v1/02-dbt-pipeline",
      purpose="Phase 1 complete for everyone; Phase 2 under way for most; each learner asked the three circulation questions once before lunch.",
      notes=["No platform session this week: its content (Airflow at CG, Unity Catalog and the three catalog types, contracts, the vended repository) was covered on Day 2, so the hour goes to the practical.",
             "Walk the room with the three-point checklist; use the symptom table for the stalls; keep adding to the Q&A table for the recap.",
             "Platform questions that come up: answer from Day 2's platform section, or log them in the Q&A table for the platform team."],
      say=["Show me the grain of this model, the key on the right-hand side of the join, and what happens to a row with no match."],
      transition="Lunch.", flex="Anyone still in Phase 1 at 11:30: pair them with a neighbour who has finished S7."),
 dict(time="12:00–13:00", title="Lunch", type="Break", on_screen="", purpose="", notes=[], say=[], transition="", flex=""),
 dict(time="13:00–13:25", title="Advanced dbt: a loop, a macro, a custom test, snapshot, incremental, unit test", type="Demo", on_screen="Anchor › section 3 demo cells (demos/price_sheet, then demos/portfolio_analytics)",
      purpose="Show what Jinja does beyond filling in names, and the pieces a production project adds, so learners recognise them in the vended project and in Friday's capstone.",
      notes=["Two cells on this morning's price sheet (a for loop, a macro), then four on the Portfolio Analytics copy (dispatching macro and generic test, snapshot, incremental, unit test).",
             "Before the unit test there are two pictures for the Databricks post-hook in challenge C9: OPTIMIZE compacts small files into large ones; ZORDER BY puts similar rows in the same file so a filter can skip files. Two minutes; it answers the question learners ask when they reach C9.",
             "After each cell show the compiled SQL: the lesson is that Jinja runs at compile time and the warehouse sees plain SQL.",
             "None of this is needed to finish the challenge; say so, so nobody abandons Phase 2 for it."],
      say=["A macro is a function that returns SQL text. If you have pasted the same expression into three models, it wants to be a macro.",
           "A snapshot keeps the history of rows that change; an incremental model avoids rebuilding rows that do not."],
      transition="Back to the practical: Phase 2, then your choice of stretch.", flex="Short of time: the loop, the macro and the snapshot; point at the other cells."),
 dict(time="13:25–14:05", title="Complete and extend dbt practical", type="Practical", on_screen="Anchor › Launch box and walkthrough cells; learners in challenges/v1/02-dbt-pipeline",
      purpose="Complete and explain the work; Phase 2 for those on it; stretch (macros, snapshots, incremental, unit tests) for fast finishers.",
      notes=["About three and a half hours of practice across the day in total; nobody has to finish Phase 2.", "Early finishers investigate one planted error in a copied project and show the failure and the repair."],
      say=["A successful build is not evidence. Show me one value you checked a different way."],
      transition="Break, then the recap.", flex=""),
 dict(time="14:05–14:20", title="Break", type="Break", on_screen="", purpose="", notes=[], say=[], transition="", flex=""),
 dict(time="14:20–14:35", title="Second look at yesterday's AI-generated dbt", type="Pair activity", on_screen="Anchor › Activity 9b card; learners in the project Copilot and Catalyst generated on Day 2",
      purpose="Learners reopen the dbt project they generated yesterday, name two things in it they could not judge then, assess it now that they know dbt, and prompt Copilot again to fix one thing they caught.",
      notes=["This closes the loop the room opened yesterday: 'do we trust it, review all of it, or review some of it?' The answer the activity gives is an order to review in: sources, staging, joins, tests, then anything nobody asked for.",
             "Yesterday some projects did not finish generating. Those learners pair with a neighbour whose project did, or review the Day 2 example in courseware/day2-platform/demos/contract-to-code/eod_prices.",
             "Two minutes to write the two things down, eight to review and re-prompt in pairs, five of shareback: two or three pairs give what they caught, the prompt they wrote and whether the fix held. Things still not judged go in the Q&A table."],
      say=["Think back to yesterday afternoon. Write down two things in that project you could not judge. Can you judge them now?",
           "Yesterday your prompt was: build me a project. Today it can be: the join in this model drops rows with no FX rate; keep them and add a not_null test. That is the difference knowing dbt makes.",
           "You do not review five hundred files. You review in graph order, and you start with the tests: do they guard the promises in your contract?"],
      transition="From what you caught to what we learned today.", flex="Short of time: pairs check only their two things and the tests, and write the prompt without running it."),
 dict(time="14:35–14:45", title="Consolidation", type="Debrief", on_screen="Anchor › Recap table",
      purpose="Ask the room what it learned and fill gaps from the six topics, all from today. Bitemporal loading is not part of today; if tomorrow's plan needs volunteers for it or for the deployment demo, ask for them here.",
      notes=["Ask 'what did we learn?' and fill gaps from the recap table rather than lecturing.", "Only if tomorrow's plan still has them: ask for a volunteer for the bitemporal loading slot and one with Harness access for the deployment demo. Check with tomorrow's instructor first; nothing in the notebook asks for this."],
      say=["What did we learn today? Call them out and I will write them up."],
      transition="Pairs: swap a mapping and its test.", flex=""),
 dict(time="14:45–14:55", title="Test review in pairs", type="Pair activity", on_screen="Anchor › Activity 9 card",
      purpose="Pairs take one test, name a wrong result that would get past it, and agree one extra test.",
      notes=["If a pair is stuck for a wrong result, offer one: a join that doubles the rows, a missing FX rate, a value in the wrong unit."],
      say=["What wrong result would still get past this test? What one test would catch it?"],
      transition="Two or three examples to the room, then close.", flex=""),
 dict(time="14:55–15:00", title="Closing discussion", type="Debrief", on_screen="Anchor › Before learners leave",
      purpose="Share a missing check; save the dbt work for orchestration; confirm tomorrow's baseline.",
      notes=["Completing advanced dbt is not a prerequisite for tomorrow; the Airflow challenge ships the solved dbt project."],
      say=["Keep this project where it is. Tomorrow Airflow runs it."],
      transition="", flex=""),
]

LEAVE_WITH = ["Two things each learner could not judge in yesterday's generated project, marked as judged or still open; one thing they caught, and the prompt that fixed it.",
              "The working dbt project, model and test results, one independent output check and the outstanding questions for orchestration, kept where they are.",
              "Each learner can trace one plain-English mapping through its model and its test.",
              "The Airflow baseline is ready: Databricks auth works, challenge 02's seeds are loaded, and Astro has been started once after setup."]

ACTIVITIES = [
 dict(number="9b", title="Second look at yesterday's AI-generated dbt", grouping="Pairs", minutes=15,
      brief="Yesterday Copilot and Catalyst generated a dbt project from your contract, before you knew dbt. First, write down two things in that project you could not judge yesterday. Then reopen it with a partner (if yours did not finish, use your partner's) and assess it in graph order: the sources, then staging, then the joins, then the tests, then anything nobody asked for. Finally, pick one thing you caught and prompt Copilot again to fix it: name the file, say what is wrong and say how you will check the fix. Read what it changed and run the check.",
      outputs=["Two things you could not judge yesterday, each marked: can judge now, or still cannot",
               "One thing you catch now that you would have approved yesterday, with the file it is in",
               "The prompt you wrote to fix it, and whether the fix passed your check",
               "One thing you still cannot judge, for the questions table"],
      debrief=["What did you catch today that you would have approved yesterday?", "How is today's prompt different from yesterday's?", "Did the AI write anything nobody asked for? What would you delete?"],
      extra="""
      **What to look for, in order**

      | Where | Ask |
      |---|---|
      | `sources.yml` | Is every raw table declared, or are there hard-coded table names in the SQL? |
      | Staging models | One row per what? Are names, types and codes cleaned here, and are duplicates handled? |
      | Joins | Are the keys unique on the right-hand side? What happens to a row with no match: dropped, null, or a silent default? |
      | Tests | Does each promise in your contract (keys, not null, accepted values, a reconciliation) have a test? Would any test fail if the data were wrong? |
      | `dbt_project.yml`, `config()` | Which models are views and which are tables, and is that what consumers need? |
      | Everything else | Which files, models or macros did nobody ask for? |

      Open one model's file under `target/compiled/` if you are unsure what the warehouse receives.
      """),
 dict(number="9", title="Test review in pairs", grouping="Pairs", minutes=10,
      brief="Pick one test from your project and show it to your partner. Together, name one wrong result that would still get past it. Agree one extra test that would catch it.",
      outputs=["One test, and one wrong result it would miss", "One extra test that would catch it"],
      debrief=["Which wrong result would have passed every test in your project?"]),
]

SECTIONS = [
 dict(n=1, title="dbt from zero: one transformation through the whole life cycle", anchor="s1", start="09:00",
      parts=["Ice-breaker: one thing you always double-check", "Recap: yesterday's platform in four pictures", "Demo: what dbt is for, why use it, then the build: project, profile, seeds, source, model, Jinja, ref, tests, build, docs"]),
 dict(n=2, title="The dbt practical: launch, Phase 1 and the walkthrough", anchor="s2", start="09:50",
      parts=["Launch: the pipeline", "Challenge 9: dbt practical", "Walkthrough: Phase 1", "Break", "Walkthrough: Phase 2", "Circulating: Phase 2 to lunch", "Lunch"]),
 dict(n=3, title="Advanced dbt, then complete and extend the practical", anchor="s3", start="13:00",
      parts=["Demo: a loop, a macro, a custom test, snapshot, incremental, OPTIMIZE and ZORDER, unit test", "Challenge 9 continued: Phase 2 and the stretch", "Break"]),
 dict(n=4, title="Consolidation", anchor="s4", start="14:20",
      parts=["Activity 9b: second look at yesterday's AI-generated dbt", "Debrief: what did we learn?", "Activity 9: test review in pairs", "Close"]),
]

# ---------- the "dbt from zero" project: every file the notebook writes, in the order it writes them ----------
PS = "demos/price_sheet"
PSDB = "PRICE_SHEET"            # defined once in the notebook, in the cell after Setup

def fig(png: str, caption: str, notes: list[str] | None = None, height: int | None = None):
    """A picture with one caption line; the explanation is folded under 'Notes' so the screen stays visual."""
    src = f"../common/diagrams/png/{png}.png"
    img = f'<img src="{src}" alt="{caption}" style="max-height:{height}px; max-width:100%;">' if height else f"![{caption}]({src})"
    body = f"{img}\n\n*{caption}*"
    if notes:
        body += "\n\n<details><summary>Notes</summary>\n\n" + "\n".join(f"- {n}" for n in notes) + "\n\n</details>"
    return dc.md(body)

def recap_fig(png: str, alt: str, ask: str, answer: str, today: str, height: int | None = None) -> list:
    """A recap picture as three cells: the picture with the question to ask the room; a cell of its own to type the
    room's answers into (double-click, type, Shift+Enter); and the answer, folded under 'Facilitator notes'."""
    src = f"../common/diagrams/png/{png}.png"
    img = f'<img src="{src}" alt="{alt}" style="max-height:{height}px; max-width:100%;">' if height else f"![{alt}]({src})"
    return [dc.md(f"{img}\n\n**Ask:** {ask}"),
            dc.md("**Answers from the room:**\n\n- "),
            dc.md("<details><summary><strong>Facilitator notes</strong></summary>\n\n"
                  f"- **Answer:** {answer}\n- **Today:** {today}\n\n</details>")]

def wf(path: str, body: str):
    """A %%writefile cell: the cell is the file, so the room reads exactly what dbt reads. Paths are relative to the
    project folder: the notebook changes into it once with %cd."""
    return dc.code(f"%%writefile {path}\n" + textwrap.dedent(body).strip("\n") + "\n")

F_PROJECT = """
# dbt_project.yml: what this project is called and how each folder of models is built
name: price_sheet
version: '1.0'
profile: price_sheet          # which connection in profiles.yml to use

models:
  price_sheet:
    staging:                  # models/staging/: one model per raw table, cleaned
      +materialized: view
      +tags: ["staging"]
    intermediate:             # models/intermediate/: the joins and the business rules
      +materialized: view
      +tags: ["intermediate"]
    marts:                    # models/marts/: the tables consumers read
      +materialized: table
      +tags: ["marts"]
"""
F_PROFILES = """
# profiles.yml: where the SQL runs. One project, one or more targets.
price_sheet:
  target: dev
  outputs:
    dev:
      type: duckdb                          # the demo's warehouse: a local file. Yours says: type: databricks
      path: warehouse/price_sheet.duckdb    # ...and yours has: host, http_path, catalog
      schema: demo                          # the schema the models are created in
"""
F_SOURCES = """
# sources.yml: the raw tables this project reads but does not build
version: 2

sources:
  - name: vendor_feed
    description: "End-of-day close prices from the pricing vendor, in each instrument's own currency."
    schema: demo
    tables:
      - name: vendor_prices_raw
  - name: fx_feed
    description: "Daily FX closes to US dollars."
    schema: demo
    tables:
      - name: fx_rates_raw
"""
F_STG_PRICES_1 = """
-- stg_prices: one row per raw price, renamed and typed. No joins, no business logic.
select
    isin                               as instrument_id,
    cast(px_date as date)              as price_date,
    cast(px_close as decimal(18, 6))   as price_native,
    px_ccy                             as native_ccy,
    cast(vendor_ts as timestamp)       as vendor_ts
from {{ source('vendor_feed', 'vendor_prices_raw') }}
"""
F_STG_FX = """
-- stg_fx_rates: one row per currency per day
select
    from_ccy,
    cast(rate_dt as date)              as rate_date,
    cast(rate as decimal(18, 6))       as fx_rate
from {{ source('fx_feed', 'fx_rates_raw') }}
"""
F_STG_FX_TABLE = """
-- stg_fx_rates: one row per currency per day
{{ config(materialized='table') }}     -- this one model: a table, whatever the folder says

select
    from_ccy,
    cast(rate_dt as date)              as rate_date,
    cast(rate as decimal(18, 6))       as fx_rate
from {{ source('fx_feed', 'fx_rates_raw') }}
"""
F_INT_1 = """
-- int_prices_usd: every price joined to its day's FX rate and converted. Same rows as stg_prices.
select
    p.instrument_id,
    p.price_date,
    p.native_ccy,
    p.price_native,
    case when p.native_ccy = 'USD' then 1.0 else f.fx_rate end   as fx_rate_to_usd,
    cast(p.price_native * case when p.native_ccy = 'USD' then 1.0 else f.fx_rate end
         as decimal(18, 6))                                      as price_usd
from {{ ref('stg_prices') }} p
left join {{ ref('stg_fx_rates') }} f
    on  f.from_ccy  = p.native_ccy
    and f.rate_date = p.price_date
"""
F_FCT = """
-- fct_prices_usd: the price sheet consumers read. One row per instrument per day.
select
    instrument_id,
    price_date,
    native_ccy,
    price_native,
    fx_rate_to_usd,
    price_usd
from {{ ref('int_prices_usd') }}
"""
F_SCHEMA_MARTS = """
# schema.yml: what the model and its columns mean, and the promises dbt checks
version: 2

models:
  - name: fct_prices_usd
    description: "End-of-day prices in US dollars."
    columns:
      - name: instrument_id
        description: "ISIN: the instrument the price is for."
        tests:
          - not_null
      - name: price_usd
        description: "Close price times the day's FX rate to USD."
        tests:
          - not_null
"""
F_STG_PRICES_2 = """
-- stg_prices: one row per raw price, renamed and typed. No joins, no business logic.
select
    upper(trim(isin))                  as instrument_id,
    cast(px_date as date)              as price_date,
    cast(px_close as decimal(18, 6))   as price_native,
    upper(trim(px_ccy))                as native_ccy,      -- the fix: 'gbp' becomes 'GBP'
    cast(vendor_ts as timestamp)       as vendor_ts
from {{ source('vendor_feed', 'vendor_prices_raw') }}
"""
F_SINGULAR = """
-- A test of your own: a query that returns the rows that break the rule. No rows, the test passes.
-- Rule: a price is never zero or negative.
select instrument_id, price_date, price_usd
from {{ ref('fct_prices_usd') }}
where price_usd <= 0
"""
F_LOOP = """
-- agg_prices_by_ccy: one column per currency, written by a loop instead of by hand
{% set currencies = ['USD', 'EUR', 'GBP', 'JPY'] %}

select
    price_date,
    {% for ccy in currencies %}
    count(case when native_ccy = '{{ ccy }}' then 1 end) as prices_in_{{ ccy | lower }}{% if not loop.last %},{% endif %}
    {% endfor %}
from {{ ref('fct_prices_usd') }}
group by price_date
order by price_date
"""
F_MACRO = """
{# to_usd: the conversion rule, written once. A macro is a function that returns SQL text. #}
{% macro to_usd(amount, ccy, rate) %}
    cast({{ amount }} * case when {{ ccy }} = 'USD' then 1.0 else {{ rate }} end as decimal(18, 6))
{% endmacro %}
"""
F_INT_2 = """
-- int_prices_usd: every price joined to its day's FX rate and converted. Same rows as stg_prices.
select
    p.instrument_id,
    p.price_date,
    p.native_ccy,
    p.price_native,
    case when p.native_ccy = 'USD' then 1.0 else f.fx_rate end   as fx_rate_to_usd,
    {{ to_usd('p.price_native', 'p.native_ccy', 'f.fx_rate') }}  as price_usd
from {{ ref('stg_prices') }} p
left join {{ ref('stg_fx_rates') }} f
    on  f.from_ccy  = p.native_ccy
    and f.rate_date = p.price_date
"""

def one_per_cell(cells: list) -> list:
    """At most one shell command or one SQL query per code cell, so the room reads one thing and sees one result.
    A cell of several `!command` and `sql(...)` lines is split; its `#` comment lines stay with the statement above
    them. Cells that are a file (%%writefile) or multi-line Python (Setup, a query over several lines) are left whole."""
    out = []
    for c in cells:
        if c is None or c.cell_type != "code":
            out.append(c); continue
        lines = c.source.split("\n")
        simple = all(l.startswith(("!", "sql(", "#", "%cd ", "print(")) or not l.strip() for l in lines)
        statements = [l for l in lines if l.startswith(("!", "sql(", "%cd "))]
        if c.source.startswith(("%%", "# Setup")) or not simple or len(statements) <= 1:
            out.append(c); continue
        groups, lead = [], []
        for l in lines:
            if l.startswith(("!", "sql(", "%cd ")):
                groups.append(lead + [l]); lead = []
            elif groups:
                groups[-1].append(l)
            else:
                lead.append(l)
        out += [dc.code("\n".join(g)) for g in groups]
    return out

def cells():
    A = {a["number"]: a for a in ACTIVITIES}
    act = lambda n: dc.md(dc.activity(n, A[n]["title"], A[n]["grouping"], A[n]["minutes"], A[n]["brief"], A[n]["outputs"], A[n].get("debrief"), A[n].get("early")))
    
    PA = "demos/portfolio_analytics"
    DB = "PORTFOLIO"
    C = [dc.title(3, TITLE, "anchor notebook"),
         
         *dc.how_to_use(3, "- Section 1 builds a small dbt project from two CSVs in `demos/price_sheet/`, one cell at a time; its first cell resets the folder. Run the section once before the room arrives.\n- The walkthrough cells run the same project as the learners' challenge, on DuckDB in `demos/portfolio_analytics/`. Run `bash demos/portfolio_analytics/demo.sh stretch` once before the day; the cells then rebuild pieces on demand."),
         dc.code(dc.setup_cell(3)),
         dc.code(f'''# The two demo warehouses the cells below query: local files on the instructor's laptop
PRICE_SHEET = HERE / "{PS}/warehouse/price_sheet.duckdb"
PORTFOLIO = HERE / "demos/portfolio_analytics/warehouse/training_dev.duckdb"'''),
         dc.agenda(SECTIONS, lead='An ice-breaker and a short recap of yesterday\'s platform, forty minutes of dbt from zero on a small example, then self-paced practice from the README, with the instructor walking the room, all the way to lunch. After lunch, twenty-five minutes of advanced dbt, then more practice. Recap and a pair exercise at the end.'),
         dc.section(1, "dbt from zero: one transformation through the whole life cycle", "s1"),
         dc.part("Ice-breaker", "one thing you always double-check", time="09:00"),
         dc.md(dc.reflect("ICE-BREAKER — one thing you always double-check", "What is one thing you always double-check, even though it is almost always fine? One answer each, at work or at home.", [
                     "The front door. The oven. The attachment before you press send.",
                     "The recipient of an email. The total on a bill. The alarm for tomorrow."])),
         dc.md("**Answers from the room:**\n\n- "),
         dc.md("<details><summary><strong>Facilitator notes</strong></summary>\n\n"
               "- Two or three minutes: go round quickly, one answer each, type a few in the cell above.\n"
               "- **The link to today:** you double-check because being wrong is costly and you would not otherwise find out. That is what a dbt test is: a check you write down once, and dbt runs it every time, so nobody has to remember.\n"
               "- Come back to it at Step 5 of the demo: \"this is the oven check, for a price sheet\".\n\n</details>"),
         dc.part("Recap", "yesterday's platform in four pictures"),
         dc.md("Ten minutes to put everyone on the same page. Today's dbt models are SQL that runs on this platform; one question per picture."),
         *recap_fig("d3-recap-lakehouse", "Data warehouse, data lake, lakehouse",
                   "What does a lakehouse keep from the lake, and what does it add?",
                   "Cheap files in object storage, plus a table format (Delta) for transactions and versions, an engine (Spark) for SQL, and a catalog (Unity Catalog) for names and permissions.",
                   "Every dbt model becomes a table or a view in that lakehouse.", height=400),
         *recap_fig("d3-recap-databricks", "Databricks under the hood: sources, ingestion, Delta storage, Spark compute, Unity Catalog, consumers",
                   "Where is your data stored, and what runs your SQL?",
                   "Storage is your S3 bucket in Delta format. Compute is Spark, on a SQL warehouse. Unity Catalog names every table `catalog.schema.table`.",
                   "Your tables land in `training_dev.training_<you>`; the raw data arrives with `dbt seed`."),
         *recap_fig("d2-delta-format", "A Delta table: Parquet files plus a transaction log",
                   "What does the log give you that plain Parquet files do not?",
                   "Every write is a commit: ACID, versions and time travel, MERGE and DELETE on files.",
                   "`OPTIMIZE ... ZORDER` in challenge C9 is a Delta operation, run by dbt after each mart is built.", height=400),
         *recap_fig("d3-recap-tools", "How the tools fit together: write, ship, schedule, transform, run, store",
                   "Which tool decides when, which holds the rules, which does the work?",
                   "Airflow decides when. dbt holds the transformation rules and the tests. Databricks runs the SQL as Spark and writes Delta to S3.",
                   "This is the dbt box. Tomorrow: the Airflow box that runs today's project."),
         dc.part("Demo", "one price sheet, from two raw files to a tested, documented table", time="09:10"),
         dc.anchor("Yesterday Catalyst generated a dbt project for you. What is in it, and what does dbt do with each file?",
                   "dbt on the smallest useful example: two raw files, four models in three layers, three tests, one documented table, on Day 2's price data.",
                   "Every file in today's challenge is one of the kinds shown here. Once you have seen each one written and run, the README's tasks are recognisable.",
                   "Watch and predict: each cell on screen writes one file or runs one command. You do not run these cells. In forty minutes you build the real pipeline yourself, on Databricks."),
         dc.md("#### First: what dbt is for"),
         fig("d3-what-dbt-does", "dbt is the T in extract, load, transform: SQL files in, tables and views out", [
                 "Other tools load the raw data. You write SELECT statements in files, kept in Git; dbt wraps each in a CREATE, runs them in order and tests the results.",
                 "dbt holds no data and does no computing: the warehouse does the work.",
                 "Analysts, analytics engineers and data engineers use the same files. At Capital Group every data product on the paved path has a dbt project; Airflow triggers a Databricks job that runs it."]),
         dc.md("#### Why use it: the same price sheet without dbt"),
         dc.code(f'''# Without dbt: one SQL script, run by hand. Prices in US dollars = close price x the day's FX rate.
seeds = HERE / "{PS}/seeds"
sql(f"""
    select p.isin, p.px_date, p.px_ccy, p.px_close,
           round(p.px_close * coalesce(f.rate, 1), 4) as price_usd
    from '{{seeds}}/vendor_prices_raw.csv' p
    left join '{{seeds}}/fx_rates_raw.csv' f
      on f.from_ccy = p.px_ccy and f.rate_dt = p.px_date
    where p.px_ccy <> 'USD'
    order by p.isin, p.px_date
""", ":memory:", read_only=False)
# It ran, with no error. Now look at HSBC (GB0005405286): the dollar price equals the pound price. Who would have noticed?'''),
         dc.md("The script ran, and three prices are wrong. The SQL is the easy part; dbt is for everything around it."),
         fig("d3-script-vs-dbt", "Six questions a hand-run script cannot answer, and what dbt gives you for each", height=360),
         dc.md("#### How a dbt project comes together: the path for the next thirty minutes"),
         fig("d3-journey", "The path: eight steps from an empty folder to a tested, documented table",
                   ["Each step adds one kind of file and one command. First make it run (steps 1 to 4), then make it right and say what it is (steps 5 to 8).",
                    "It is the order you would work in on a real product, and the order of the challenge README."]),
         dc.md("#### The layers: staging, intermediate, marts"),
         fig("d3-layers", "Every dbt project here has the same three layers. Each has one job, a folder and a prefix.", [
                 "**staging/** (`stg_`): one model per raw table. Rename, cast, clean. No joins. Views.",
                 "**intermediate/** (`int_`): the joins and the business rules. Views; nobody outside the project reads them.",
                 "**marts/** (`fct_`, `agg_`): the tables consumers read. Tables, because they are queried often.",
                 "The challenge has the same folders and prefixes: five `stg_`, three `int_`, three marts. Catalyst and the capstone use the names source-aligned, domain-aligned and consumer-aligned for the same idea."]),
         dc.md("#### What we will build: four models in three layers"),
         fig("d3-build-plan", "The plan. Dashed boxes are not built yet; this picture comes back after each step with the new piece highlighted.", [
                 "Two raw tables, two staging models, one intermediate model that joins them, one mart.",
                 "Yellow: built in this step. Blue: built earlier. Red: a test is failing."], height=300),
         dc.md(dc.demo("dbt from zero, eight steps", f"A project that starts as two CSVs in <code>{PS}/seeds/</code>; each cell writes one file or runs one command.", [
                  "Read each file aloud before running the command that uses it; ask the room to predict the output.",
                  "Steps 5 and 6 are the point of the demo: two tests fail on real rows, one line fixes the model, the build goes green. Do not skip them.",
                  "Step 3's compiled SQL is the Jinja explanation: curly braces in, plain SQL out. Learners meet source(), ref() and config() within the first hour of the challenge.",
                  f"`{PS}/README.md` lists every step, file and expected result; `bash reset.sh` starts again."]) and None),
         dc.md("#### Step 1 — A dbt project is a folder: two YAML files and a folder of SQL"),
         fig("d3-project-anatomy", "The anatomy of a dbt project folder",
                   ["`dbt_project.yml`: the project's name and its defaults. `profiles.yml`: the connection, one entry per target (dev, prod).",
                    "`models/`: one SELECT per `.sql` file, in three folders, plus YAML that describes and tests them. `staging/` cleans one raw table per model (`stg_`), `intermediate/` joins and applies the rules (`int_`), `marts/` holds the tables consumers read (`fct_`, `agg_`). The challenge uses the same folders and prefixes.",
                    "`seeds/`: small CSVs dbt loads. `tests/` and `macros/`: later this morning and after lunch.",
                    "`target/`: what dbt writes when it runs (compiled SQL, run results, the docs site). Never edited, never committed."]),
         dc.code('%cd {HERE}/demos/price_sheet\n# Work inside the project folder from here on. dbt commands run from the folder that holds dbt_project.yml; in the challenge that is challenges/v1/02-dbt-pipeline/dbt.'),
         dc.code(f'!bash reset.sh\n# The starting point: two raw CSV files and nothing else. `dbt init` would scaffold the folder; here every file is written by hand so you see what is in it.'),
         wf("dbt_project.yml", F_PROJECT),
         wf("profiles.yml", F_PROFILES),
         dc.code(f'!dbt debug\n# dbt debug answers one question: can dbt find the project, find the profile and open the connection? It is the first command in the challenge too.'),
         dc.md("#### Step 2 — The raw data: seeds stand in for the feeds that land in the warehouse"),
         dc.code(f'!dbt seed\nsql("select isin, px_date, px_close, px_ccy from demo.vendor_prices_raw where px_ccy <> \'USD\' order by isin, px_date", {PSDB})\n# dbt seed loads each CSV in seeds/ as a table. These are the prices that are not in US dollars. Look closely at the currency of the second instrument: gbp, in lower case. It matters in a few minutes.'),
         dc.code(f'sql("select * from demo.fx_rates_raw order by rate_dt, from_ccy", {PSDB})\n# One rate per currency per day, to US dollars. The transformation: price in dollars = close price x that day\'s rate.'),
         fig("d3-build-2", "Where we are: the raw data is loaded. No models yet.", height=300),
         dc.md("#### Step 3 — Declare the source, write the first model, run it"),
         fig("d3-seed-vs-source", "Seeds stand in for the feeds: however a raw table arrives, you declare it in sources.yml and read it with source()", [
                 "Here and in the challenge, `dbt seed` loads the CSVs. We then declare those tables under `sources:` and read them with `source(...)`, as if another tool had landed them.",
                 "That is how raw data arrives on a real product: an ingestion tool lands it, and dbt only declares it and reads it.",
                 "So the models you write today would not change on a real product; only where the raw tables come from."], height=300),
         wf("models/sources.yml", F_SOURCES),
         fig("d3-yaml", "YAML files in dbt: .yml and .yaml are the same; only two names are fixed. Today every file is .yml, as in the challenge.",
             ["`dbt_project.yml` and `profiles.yml` must have exactly those names.",
              "Every other YAML file can have any name: dbt reads the top-level keys inside (`sources:`, `models:`, `seeds:`, `unit_tests:`), not the file name. `sources.yml` and `schema.yml` are habits; Catalyst writes `_staging__sources.yml` and `_staging__models.yml`.",
              "You will see `.yaml` in other tools this week: Airflow blueprints, Databricks bundles, data contracts.",
              "Indentation is the syntax: two spaces per level, never tabs."]),
         wf("models/staging/stg_prices.sql", F_STG_PRICES_1),
         fig("d3-compile", "What dbt run does with a model file: compile, wrap, send",
                   ["Compile: the curly braces are replaced, here `source(...)` becomes the real table name. The result is plain SQL in `target/compiled/`.",
                    "Wrap: dbt puts your SELECT inside `create view ... as` or `create table ... as`, according to the model's materialisation. That is in `target/run/`.",
                    "Send: the warehouse executes it. The model's file name is the name of the view or table."]),
         dc.code(f'!dbt run\nsql("select * from demo.stg_prices order by instrument_id, price_date limit 6", {PSDB})\n# One model, one view called stg_prices. You wrote a SELECT; dbt wrote the CREATE.'),
         fig("d3-build-3", "Where we are: the first staging model is built. Three models to go.", height=300),
         dc.code('!cat target/compiled/price_sheet/models/staging/stg_prices.sql\n# What dbt compiled: your SELECT, with the curly braces replaced by the real table name.'),
         dc.code('!cat target/run/price_sheet/models/staging/stg_prices.sql\n# What the warehouse ran: the same SELECT, wrapped in create view ... as.'),
         fig("d3-jinja", "Jinja, the curly braces: dbt replaces them before the warehouse sees the SQL", [
                 "Two curly braces print a value into the SQL. In the challenge: `source()` from S4, `config()` in S6, `ref()` from C1, `this` in C9.",
                 "A curly brace and a percent sign run logic and print nothing: `if`, `for`, `macro`. Not needed in the challenge; at 13:00.",
                 "Jinja runs on your machine at compile time. When a model misbehaves, read its file under `target/compiled/`."], height=460),
         dc.md("#### Step 4 — The other layers with ref(): staging, intermediate, marts, and dbt works out the order"),
         wf("models/staging/stg_fx_rates.sql", F_STG_FX),
         wf("models/intermediate/int_prices_usd.sql", F_INT_1),
         wf("models/marts/fct_prices_usd.sql", F_FCT),
         dc.code(f'!dbt run\n# Four models, built in graph order: the two staging models, then the intermediate one, then the mart. Read the log: three say "view model", one says "table model".'),
         fig("d3-build-4", "Where we are: all four models built, in the order dbt worked out from source() and ref()", [
                 "Every `source()` and `ref()` is an edge. dbt reads them all, then builds the models from left to right.",
                 "You never write the order down. Add a model and the graph changes by itself.",
                 "The same graph is the lineage picture in the docs, and what `--select +fct_prices_usd` walks."], height=300),
         dc.code(f'sql("select instrument_id, price_date, native_ccy, price_native, fx_rate_to_usd, price_usd from demo.fct_prices_usd where native_ccy <> \'USD\' order by instrument_id, price_date", {PSDB})\n# The run was green. Look at the HSBC rows (GB0005405286): no rate, no dollar price. A successful run says the SQL executed, not that the answer is right.'),
         dc.md("#### Step 4, continued — View or table? Set per folder in dbt_project.yml, overridden in one model with config()"),
         fig("d3-materialisations", "A materialisation is how dbt saves a model: view, table, incremental or snapshot", [
                 "View: a saved query, built on read. Cheap and always fresh. Staging and intermediate, because nobody reads them directly.",
                 "Table: written when dbt runs. Fast to read. Marts, because consumers and dashboards read them.",
                 "Set once per folder in `dbt_project.yml`; `config()` at the top of a model file overrides it for that model. Incremental and snapshot: at 13:00.",
                 "In the challenge: S6, and the `models:` block you read in S2."]),
         dc.code(f'''!cat dbt_project.yml
sql("select table_name, table_type from information_schema.tables where table_schema = 'demo' and table_name not like '%_raw' order by table_name", {PSDB})
# The folder decides: staging/ and intermediate/ are views, marts/ is a table. Nothing in the SQL files says so.'''),
         wf("models/staging/stg_fx_rates.sql", F_STG_FX_TABLE),
         dc.code(f'''!dbt run --select stg_fx_rates
sql("select table_name, table_type from information_schema.tables where table_schema = 'demo' and table_name = 'stg_fx_rates'", {PSDB})
# config() in the file beats the folder setting: the log now says "table model". This is the variation in challenge S6.'''),
         wf("models/staging/stg_fx_rates.sql", F_STG_FX),
         dc.code(f'''!dbt run --select stg_fx_rates
# Back to the folder's default, a view: one line removed, nothing else changed.'''),
         dc.md("#### Step 5 — Tests: write the promise down, and dbt checks it on every run"),
         fig("d3-tests", "Two kinds of dbt test, one idea: select the rows that break the rule",
                   ["A generic test is a named rule attached to a column in YAML: `not_null`, `unique`, `accepted_values`, `relationships`.",
                    "A singular test is a SQL file in `tests/` for a rule the four cannot express.",
                    "Both compile to a query for the violating rows. No rows returned: pass. The same YAML holds the descriptions the docs show."]),
         wf("models/marts/schema.yml", F_SCHEMA_MARTS),
         dc.code('!dbt test    # one test fails here, on purpose\n# Two promises: every row has an instrument, and every row has a dollar price. The second one fails, on three rows.'),
         dc.code('!cat target/compiled/price_sheet/models/marts/schema.yml/not_null_fct_prices_usd_price_usd.sql\n# A test is only a query: it selects the rows that break the promise. No rows back means PASS.'),
         dc.code(f'sql("select instrument_id, price_date, native_ccy, price_native, fx_rate_to_usd, price_usd from demo.fct_prices_usd where price_usd is null", {PSDB})\n# The three rows the test found. Their currency is written gbp, the rates table says GBP, so the join found no rate and the dollar price is empty.'),
         fig("d3-build-5", "Where we are: one test fails on the mart. The cause is upstream, in staging, where the currency should be cleaned.", height=300),
         dc.md("#### Step 6 — Fix the model, then dbt build: run and test together"),
         wf("models/staging/stg_prices.sql", F_STG_PRICES_2),
         fig("d3-commands", "The dbt commands, and dbt build that chains them",
                   ["`dbt build` runs seeds, models and tests in graph order; if a test fails, everything downstream of it is skipped.",
                    "`--select` narrows any command: one model, `+model` with everything upstream, `model+` with everything downstream, `tag:staging` for a layer.",
                    "Daily loop: edit a file, `dbt build --select` that model, read the result."]),
         dc.md("Every dbt command by objective, the `--select` syntax, the files dbt reads and writes, and what to do when something goes wrong: `common/glossaries/dbt-commands.md`. Keep it open during the challenge."),
         dc.code(f'!dbt build\nsql("select instrument_id, price_date, native_ccy, price_native, fx_rate_to_usd, price_usd from demo.fct_prices_usd where native_ccy = \'GBP\' order by price_date", {PSDB})\n# One line changed in staging: the currency is now upper case. Build re-created the models and re-ran the tests; both pass, and the three rows have a dollar price.'),
         fig("d3-build-6", "Where we are: one line fixed in staging, and both tests pass.", height=300),
         dc.md("#### Step 7 — A test of your own: any query that returns the rows that break a rule"),
         wf("tests/assert_prices_are_positive.sql", F_SINGULAR),
         dc.code('!dbt test --select assert_prices_are_positive\n# A SQL file in tests/ is a test. This one passes: no price is zero or negative. If one ever is, the build stops here.'),
         fig("d3-build-7", "Where we are: four models, three tests, all passing.", height=300),
         dc.md("#### Step 8 — Docs and lineage come from the same files"),
         dc.code(f'!dbt docs generate\n!dbt ls --resource-type model test --select +fct_prices_usd\n# To browse the site, in a terminal in this folder: dbt docs serve --host 127.0.0.1 --port 8082   (the lineage graph is the blue button, bottom right)\n# The descriptions in schema.yml, the columns from the warehouse and the graph from ref() become a website. Nothing extra was written for it.'),
         fig("d3-lifecycle", "The life cycle of a dbt model, as you just saw it",
                   ["Declare the source, write the SELECT, run it, look at the rows.",
                    "Write the promise as a test. When it fails, the fix goes in the model, never in the data.",
                    "Build, document, commit: the pull request carries the SQL, the tests and the descriptions together."]),
         fig("d3-demo-to-challenge", "From this demo to the challenge: the same kinds of file, more of them", height=520),
         dc.section(2, "The dbt practical: launch, Phase 1 and the walkthrough", "s2"),
         dc.part("Launch", "the pipeline you will build today", time="09:50"),
         dc.anchor("You have seen one model through its life cycle. Can you build a pipeline of ten, and tell when it is wrong?",
                   "dbt from the inside: sources, staging, intermediate, marts, tests, docs, on the Portfolio Analytics case, on Databricks.",
                   "Reviewing generated code needs the same knowledge as writing it; the practical builds that knowledge one section at a time.",
                   "Work the README in order: concept, task, hint, check, variation, solution. Phase 1 by about 11:00, Phase 2 from there and after lunch."),
         fig("d3-pipeline", "The Portfolio Analytics pipeline the learners build: five sources, staging, intermediate, three marts, tests",
                   ["Six raw feeds ship as seeds; five are modelled; refdata is there to inspect and for freshness practice.",
                    "Staging renames and casts, one model per source; intermediate does the joins; marts are the consumer-aligned facts and aggregates.",
                    "The tests are promises from a contract made executable: not null, unique, a relationship, accepted values, NAV within one basis point, the rollup reconciles."]),
         dc.part("Challenge 9", "dbt practical: Phase 1 first", time="09:55"),
         dc.md(dc.challenge("dbt practical (challenge 02)", "challenges/v1/02-dbt-pipeline/README.md", "about 3 hours across the day",
                      "Build, test and document the Portfolio Analytics pipeline: eight staging sections, then ten challenges.",
                      [("Where to work", [
                          "`cd challenges/v1/02-dbt-pipeline/dbt`; every `dbt` command runs from here.",
                          "`dbt debug` (connection), `dbt seed` (eight CSVs into `training_dev.training_<you>`), `dbt ls --resource-type model` (ten stubs).",
                          "`mise run challenge:verify 02` and `challenge:reset 02` run from anywhere; never reset to \"start clean\": it deletes authored work."]),
                       ("Phase 1, about an hour", [
                          "S1 Inspect the raw data.", "S2 Read the dbt project.", "S3 Declare sources and freshness.", "S4 First staging model: `stg_holdings`.",
                          "S5 The remaining staging models.", "S6 Materialisations: view vs table.", "S7 Build the whole staging layer.", "S8 A staging test."]),
                       ("Phase 2", [
                          "C1 The enrichment join: `int_holdings_enriched`.", "C2 The two supporting intermediate models.", "C3 First curated mart: `agg_fund_exposure`.",
                          "C4 Second curated mart: `fct_portfolio_returns`.", "C5 Generic tests on the marts.", "C6 A singular reconciliation test: NAV within tolerance.",
                          "C7 The full build: `dbt build`.", "C8 Docs and the lineage graph.", "C9 The Databricks post-hook: `OPTIMIZE … ZORDER`.", "C10 Capstone: a new mart end to end."])],
                      "`mise run challenge:verify 02` runs seeds, models and tests; green means solved.",
                      support=["Keep a list of commands, configuration changes, questions and discoveries; the recap is built from it."])),
         dc.md(dc.say(["Attempt each section before you open its solution. The solution is for comparing, not for copying.",
                       "You can run the raw dbt commands from the project folder. If dbt says it cannot find your credentials, open a fresh terminal so mise loads the environment, or rerun mise run setup:databricks."])),
         dc.part("Walkthrough", "Phase 1: sources and staging"),
         dc.md(dc.demo("the same project, section by section", f"The instructor's copy of the challenge 02 solution in <code>{PA}/</code>: one cell per README section, for \"what should I see?\".", [
                  "Same model names, layers, tags and tests; the Databricks-only post-hook is a no-op macro here.",
                  f"Use a cell when someone asks what they should see; `{PA}/README.md` maps each cell to its README section.",
                  "Say once: the SQL is the same; only the target differs."])),
         dc.code('%cd {HERE}/demos/portfolio_analytics\n# The walkthrough cells run in the instructor\'s copy of the challenge project.'),
         dc.md("#### S1 — Inspect the raw data: what feeds the models"),
         dc.code(f'!dbt seed --full-refresh \nsql("select * from training_demo.holdings_raw order by fund_cd, pos_dt limit 8", {DB})\n# A holding: one fund, one instrument, one day, valued in its local currency. Note fund_cd, pos_dt, isin, qty, mkt_val_lc, ccy_cd and _extracted_at.'),
         dc.md("#### S2 — Read the project: layers, materialisations, tags"),
         dc.code(f'!dbt ls --resource-type model --exclude tag:stretch\n!cat dbt_project.yml\n# Ten models in three layers. Layers are folders with +materialized and +tags: select a layer with --select tag:staging.'),
         dc.md("#### S3 — Sources and freshness: five lines per source table, because the fund master has no load timestamp"),
         dc.code(f'!dbt source freshness\n# Five sources report; product_ref has no loaded_at_field and is skipped. Tighten error_after to 0 hours and it flips to error: the check working, not a bug.'),
         dc.md("#### S4 — The first staging model: rename, cast, coalesce a null ISIN into CASH_<ccy>, no joins"),
         dc.code(f'!cat models/staging/stg_holdings.sql'),
         dc.code(f'!dbt build --select stg_holdings\nsql("select fund_id, position_date, instrument_id, quantity, mv_local_ccy, local_ccy from training_demo.stg_holdings order by 1,2 limit 8", {DB})\n# Same grain as the source. instrument_id is an ISIN or CASH_<ccy>, never null; quantities are typed decimals.'),
         dc.md("#### S5 to S7 — The remaining staging models, then the whole layer by tag"),
         dc.code(f'!dbt build --select tag:staging\nsql("select * from training_demo.stg_prices order by instrument_id, price_date limit 8", {DB})\n# stg_positions and stg_prices dedup to the latest extract per natural key with row_number(); staging never raises the row count.'),
         dc.md("#### S8 — A staging test is a query that must return no rows"),
         dc.code(f'!cat models/staging/schema.yml\n!dbt test --select stg_holdings\n# not_null and unique compile to select-the-violations queries. Zero rows is a pass.'),
         dc.break_(15, "10:15"),
         dc.part("Walkthrough", "Phase 2: intermediate, marts, tests, docs", time="10:15"),
         dc.md("#### C1 — The enrichment join: holdings × prices × FX, grain unchanged"),
         dc.code(f'!cat models/intermediate/int_holdings_enriched.sql\n# Left joins on (instrument, date) and (currency, GBP, date). Ask the room: what happens when the FX rate is missing? Here it defaults to 1.0 via coalesce; the running example on Day 2 chose to leave it null and fail the test. Both are decisions; the contract should say which.'),
         dc.md("#### C3, C4 — The marts: an aggregate by strategy and the daily-grain fact with a calculated NAV"),
         dc.code(f'!dbt build --select +agg_fund_exposure +fct_portfolio_returns\nsql("select fund_id, position_date, strategy_code, exposure_base_ccy, instrument_count from training_demo.agg_fund_exposure order by 1,2", {DB})'),
         dc.code(f'sql("select fund_id, position_date, instrument_id, mv_local_ccy, fx_rate_to_base, mv_base_ccy, round(calc_nav_per_unit, 6) as calc_nav_per_unit from training_demo.fct_portfolio_returns order by 1,2", {DB})\n# calc_nav_per_unit = total base-currency market value / 100,000,000 synthetic units. Holdings only; cash excluded; a teaching measure, not an official NAV.'),
         dc.md("#### C5, C6 — Generic tests on the marts, and a singular reconciliation: NAV within one basis point of the custodian"),
         dc.code(f'!cat tests/assert_nav_within_tolerance.sql\nsql("select c.fund_id, c.position_date, round(c.calc_nav_per_unit,4) as calc, cu.nav_per_unit as custodian, round((c.calc_nav_per_unit - cu.nav_per_unit)/cu.nav_per_unit*10000, 3) as variance_bps from training_demo.fct_portfolio_returns c join training_demo.seed_custodian_nav cu using (fund_id, position_date) order by 1,2", {DB})\n# The seeds are built so this passes within 1bp. Change one holding value and it will not: that is the test earning its keep.'),
         dc.md("#### C7, C8 — The full build, then docs and lineage"),
         dc.code(f'!dbt build --exclude tag:stretch\n!dbt docs generate\nprint("To browse the site, in a terminal in this folder: dbt docs serve --host 127.0.0.1 --port 8081   (the --host matters: DBT_HOST is used for the Databricks host in the learners\' profile)")'),
         dc.md("#### C9, C10 — The Databricks post-hook and the capstone mart"),
         dc.code(f'!cat macros/optimize_mart.sql\n# On Databricks: OPTIMIZE ... ZORDER BY (fund_id, position_date) after each mart, a Delta optimisation. Here: a no-op. A macro that dispatches on target.type is how one project runs on two warehouses.'),
         dc.code(f'sql("select * from training_demo.agg_fund_daily_exposure order by 1,2", {DB})\n!cat tests/reconcile_daily_exposure.sql\n# C10: the (fund, date) rollup must preserve the strategy-level total. Learners create both the mart and this test.'),
         dc.part("Circulating", "Phase 2 to lunch: three questions per learner, and the symptom table", time="11:00"),
         dc.md(dc.reflect("CIRCULATION CHECKLIST — three questions per learner", "Ask: could this join pass its tests and still double the reported value? A successful build alone is insufficient.", [
                     "Sources and staging: can they say what one row means, name its key, and explain the types and units?",
                     "Joins and models: are the lookup keys unique on the right-hand side, do dates belong in the join, and what happens to unmatched rows?",
                     "Tests and output: can they show a value checked independently of the model that produced it?",
                     "Check the row grain, right-side uniqueness, unmatched rows and an independent total."])),
         dc.md("""
         | Symptom | Cause | Fix |
         |---|---|---|
         | `auth_type: oauth is required when not using access token` | The shell has no `DBT_ACCESS_TOKEN`; mise did not load the environment | Open a fresh terminal, or `mise run setup:databricks`; do not re-authenticate blindly (the repo's Copilot instructions give a three-step check) |
         | `dbt show --inline "select …"` errors with unexpected extra arguments | Running through `mise run challenge:dbt` word-splits the SQL | Run raw `dbt` from the project folder, or use `dbt show --select <model>` |
         | `--select tag:staging` selects nothing | The `models:` block in `dbt_project.yml` is missing or mis-keyed | Compare with the shipped `dbt_project.yml`; the project name must match |
         | Full build fails in C7 on a placeholder mart | The capstone mart is created in C10, not shipped | Build with `--exclude agg_fund_daily_exposure` until C10 |
         | Python crashes on the first query that returns rows | pandas result conversion on this image | The shipped profile sets `_disable_pandas: true`; check it is still there |
         | `dbt docs serve` cannot bind | `DBT_HOST` holds the Databricks host | `dbt docs serve --host 127.0.0.1 --port 8081` |
         | A relationship test fails after a learner edits a key | Keys changed in staging without the fund master | Trace the key back to the source; staging must not invent keys |
         """),
         dc.break_(60, "13:00", lunch=True),
         dc.section(3, "Advanced dbt, then complete and extend the practical", "s3"),
         dc.part("Demo", "Jinja that writes SQL: a loop, a macro, then the production pieces", time="13:00"),
         dc.anchor("This morning's Jinja filled in names. What else can it do, and what does a production dbt project have that the challenge does not?",
                   "A loop and a macro on this morning's price sheet; then a macro that dispatches on the warehouse, a custom generic test, a snapshot (SCD type 2), an incremental mart and a unit test on the Portfolio Analytics project.",
                   "These are the pieces the platform's vended project uses, and the macros you will read in Friday's capstone.",
                   "Twenty-five minutes on screen. Then carry on with Phase 2, or ask Copilot to add one of these to your project."),
         fig("d3-macro", "A macro: SQL written once, expanded wherever it is called",
                   ["A macro lives in `macros/` and takes arguments, like a function. It returns SQL text.",
                    "Every model that calls it gets the same expression at compile time; change the macro and every model changes.",
                    "The warehouse never sees the macro, only the expanded SQL in `target/compiled/`."]),
         dc.code('%cd {HERE}/demos/price_sheet\n# Back in this morning\'s price sheet project.'),
         dc.md("#### A loop: four columns from one line"),
         wf("models/marts/agg_prices_by_ccy.sql", F_LOOP),
         dc.code(f'!dbt show --select agg_prices_by_ccy\n!cat target/compiled/price_sheet/models/marts/agg_prices_by_ccy.sql\n# The loop ran at compile time and wrote four count(...) lines. Add a currency to the list and the model gains a column.'),
         dc.md("#### A macro: the conversion rule in one place"),
         wf("macros/to_usd.sql", F_MACRO),
         wf("models/intermediate/int_prices_usd.sql", F_INT_2),
         dc.code(f'!dbt build --select int_prices_usd+\n!cat target/compiled/price_sheet/models/intermediate/int_prices_usd.sql\n# The model now calls to_usd(...); the compiled SQL shows the expression the macro returned. The tests still pass: same answer, one definition.'),
         dc.md("#### On the Portfolio Analytics project: a macro that dispatches on the warehouse, and a generic test of your own"),
         dc.code('%cd {HERE}/demos/portfolio_analytics\n# The rest of the demo runs in the instructor\'s copy of the challenge project.'),
         dc.code(f'!cat macros/to_base_ccy.sql\n!cat tests/generic/test_non_negative.sql\n# A macro names a repeated expression once; a generic test is a macro that returns the violating rows.'),
         dc.md("#### A snapshot: the history of rows that change (SCD type 2)"),
         dc.code(f'!dbt snapshot\nsql("select fund_cd, fund_name, strategy_code, is_active, dbt_valid_from, dbt_valid_to from training_demo.fund_master_snapshot order by 1", {DB})\n# A snapshot keeps history: change a watched column in the seed, snapshot again, and the old row closes (dbt_valid_to) while a new one opens. Tomorrow adds the second clock.'),
         dc.md("#### An incremental model: only the new rows"),
         dc.code(f'!dbt run --select agg_fund_daily_exposure_incremental\n!dbt run --select agg_fund_daily_exposure_incremental\n!cat models/stretch/agg_fund_daily_exposure_incremental.sql\n# First run: full load. Second run: only dates newer than the table holds, replaced on the unique key (delete+insert) so a re-delivered day does not duplicate.'),
         dc.md("#### On Databricks: OPTIMIZE and ZORDER, the post-hook in challenge C9"),
         dc.md("""
         ```yaml
         # dbt_project.yml in the challenge: after dbt builds each mart, Databricks runs this
             marts:
               +materialized: table
               +post-hook: "OPTIMIZE {{ this }} ZORDER BY (fund_id, position_date)"
         ```
         """),
         fig("d3-optimize", "OPTIMIZE: many small files become a few large ones. Same rows, faster to read.", [
                 "A Delta table is a folder of Parquet files, and every write adds more, often small ones. Opening thousands of small files is slow.",
                 "`OPTIMIZE` rewrites them into fewer, larger files. The data does not change; the old files stay until `VACUUM`, so time travel still works.",
                 "It costs compute: fine after every build for a small mart, usually scheduled for a large table."]),
         fig("d3-zorder", "ZORDER BY: rows with similar values share a file, so a query can skip the files it does not need", [
                 "Delta records the smallest and largest value of each column in every file. A filter can skip any file whose range cannot match.",
                 "`ZORDER BY (fund_id, position_date)` sorts the rows while compacting, so each file covers a narrow range of funds and dates.",
                 "Choose the columns that queries filter and join on; two or three at most, because each extra column weakens the effect.",
                 "These are Delta operations: they run on Databricks only. On the training data, a handful of rows, you will not see a difference; the hook shows the pattern."]),
         dc.md("#### A unit test: the model's logic on made-up rows"),
         dc.code(f'!cat models/stretch/stretch.yml\n!dbt test --select stg_holdings,test_type:unit\n# A unit test runs the model SQL on made-up rows and compares with expected rows: no warehouse data, pure logic.'),
         dc.md(dc.prompt("Chat view, in the learner project", "/ai-catalyst adding-dbt-unit-test\nAdd a dbt unit test for stg_holdings covering: a null ISIN becomes CASH_<ccy>; fund codes are trimmed and upper-cased; a row with a null position date is dropped.",
                         "/adding-dbt-unit-test  (same text) — or simply: add a unit_tests entry for stg_holdings in a YAML file covering those three cases")),
         dc.code('%cd {HERE}'),
         dc.part("Challenge 9 continued", "Phase 2, then your choice of stretch", time="13:25"),
         dc.md(dc.say(["Carry on where you stopped. Phase 2 first; nobody has to finish it.",
                       "Finished C10? Ask Copilot to add one of the pieces you just saw to your project: a unit test for stg_holdings is the quickest."])),
         dc.break_(15, "14:20"),
         dc.section(4, "Consolidation", "s4"),
         dc.part("Activity 9b", "second look at yesterday's AI-generated dbt", time="14:20"),
         dc.md(dc.reflect("FIRST — two things you could not judge yesterday", "Yesterday afternoon Copilot and Catalyst generated a dbt project for you, and the room asked: do we trust it, review all of it, or review some of it? Write down two things in that project you could not judge.", [
                     "A file or folder whose purpose you could not tell.",
                     "SQL you could not say was right: a join, a calculation, the curly braces.",
                     "A test you could not say was checking anything.",
                     "Something that looked like more than you asked for."])),
         act("9b"),
         dc.md(A["9b"]["extra"]),
         dc.md(dc.prompt("Chat view, in yesterday's generated project", "In models/<the file>, <what is wrong: for example, the join to FX rates drops prices with no rate for that date>.\nChange only that model: <what you want instead>. Add or tighten a test in the schema YAML that would fail if this went wrong again.\nShow me the diff, then run dbt build --select <the model>+ and show me the result.")),
         dc.part("Debrief", "what did we learn?", time="14:35"),
         dc.md(dc.whiteboard("what did we learn? (fill gaps from this list, do not lecture it)", [
             ("Models and layers", "A model is a SELECT in a file. Staging cleans one raw table (stg_), intermediate joins and applies rules (int_), marts are what consumers read (fct_, agg_)."),
             ("Dependencies", "source() and ref() build the graph; dbt works out the order, and the same graph is the lineage in the docs."),
             ("Tests", "A test is a query for the rows that break a rule. Generic tests in YAML, your own as a SQL file; dbt build runs them with the models."),
             ("Views and tables", "Set per folder in dbt_project.yml; config() in a model overrides it. Incremental and snapshot for large tables and for history."),
             ("Jinja and macros", "Curly braces are replaced before the warehouse sees the SQL; a macro is a rule written once."),
             ("Reviewing generated code", "Read it in graph order: sources, staging, joins, tests. Yesterday you could not judge it; today you can."),
         ], open_=True)),
         dc.part("Activity 9", "test review in pairs", time="14:45"),
         act("9"),
         dc.part("Close", "closing discussion", time="14:55"),
         dc.md(dc.say(["Two or three examples to the room: the wrong result, whether the test caught it, the improvement.",
                       "Save the project where it is; tomorrow Airflow runs it. Completing Phase 2 is not a prerequisite for tomorrow: the Airflow challenge ships the solved dbt project."])),
         dc.md(dc.leave_with(LEAVE_WITH)),
         *dc.qa_section(3)]
    return one_per_cell(C)
