"""Day 5 — The Atlas capstone."""
import pathlib
import dc
DAY, SLUG, TITLE = 5, "day5-capstone", "The Atlas capstone"
ROOT = pathlib.Path(__file__).resolve().parents[3]

BLOCKS = [
 dict(time="09:00–09:15", title="Brief and individual reading", type="Intro", on_screen="Anchor › Brief; the capstone README",
      purpose="What the day is, where the project is, the caveats about the data, and ten minutes of reading alone.",
      notes=["Start sharp. The README is in challenges/v1/04-atlas-capstone; the work happens in data_products/atlas_elt.", "Extra attendees may join; name cards and a table for them."],
      say=["Read the first third of the README on your own. At 09:15 your table works out what you are being asked to build."],
      transition="Table discovery.", flex=""),
 dict(time="09:15–10:15", title="Table discovery and playback", type="Challenge + shareback", on_screen="Anchor › Activity 12 worksheet; the ERD and pipeline diagrams",
      purpose="Reverse-engineer the product from the outputs: producer-creator-consumer map, consumer-backwards map, mini-STTM, glossary and trust questions; two-minute playbacks.",
      notes=["Nudge tables towards different outputs so the playbacks differ.", "A PRD or contract from Catalyst during this hour is desirable, not required."],
      say=["Work backwards from the output to the sources. Describe the transformations in English; no SQL yet."],
      transition="Phase 1.", flex="Wrap by 10:15 at the latest; the build needs the time."),
 dict(time="10:15–12:00", title="Phase 1 build", type="Challenge", on_screen="Anchor › Phase 1 support, expected results",
      purpose="Every team establishes the baseline: readiness, seeds, source-aligned, domain-aligned, consumer-aligned, tests, orchestration understood.",
      notes=["Circulate with the section notes; compare numbers with the expected results; never type in a learner's project.", "Record each team's progress on the tally sheet."],
      say=["A successful build is a prerequisite. A number you checked another way is evidence."],
      transition="Lunch is flexible; everyone back by 13:30 at the latest.", flex=""),
 dict(time="12:00–13:00", title="Lunch (flexible)", type="Break", on_screen="", purpose="", notes=[], say=[], transition="", flex=""),
 dict(time="13:00–14:30", title="Phase 1 completion, Phase 2 extensions, presentation prep", type="Challenge", on_screen="Anchor › Phase 2 menu; Activity 13 card",
      purpose="Teams finish Phase 1, choose extensions that add value, and prepare a two-to-three-minute presentation.",
      notes=["The day ends when every team has completed Phase 1; bring presentations forward if that happens early.", "Technical work stops at 14:30 (or earlier) to prepare."],
      say=["Pick the extension that changes what your consumer can do, not the one that looks hardest."],
      transition="Presentations.", flex="Advanced learners who finish Phase 2 can take the advanced path in the README: a product of their own."),
 dict(time="14:30–15:00", title="Presentations and close", type="Shareback", on_screen="Anchor › Activity 13; tally sheet",
      purpose="One person per table, two to three minutes; the certification evidence recorded; the week closed.",
      notes=["If senior leaders attend, invite tables to mention Catalyst, the paved path and the mission.", "Prizes if there are any. Thank the guests and the platform team."],
      say=["Do we feel we can create a data product? Then you are done."],
      transition="", flex=""),
]

LEAVE_WITH = ["Each team's Phase 1 evidence recorded on the tally sheet: layers built, tests passed, one independent value check, orchestration explained.",
              "Each team's worksheet and presentation kept with their project.",
              "The week's artefacts (PRDs, contracts, STTMs, generated code, dbt and Airflow projects) saved where the learners can find them.",
              "The list of open questions for the platform team handed over with names."]

ACTIVITIES = [
 dict(number="12", title="Atlas discovery worksheet", grouping="Tables", minutes=60,
      brief="Before anyone builds, understand the product. Choose at least two business-facing outputs (for example `rpt_portfolio_summary`, `rpt_advisor_book`, `agg_segment_aum`, `agg_instrument_activity`, `agg_fund_nav`, `ts_daily_market`, `api_latest_price`) and work backwards from consumer need to source data. Assign roles: facilitator, scribe, quality challenger, playback spokesperson. Fill one shared worksheet with the four sections below. Describe transformations in plain English; no SQL, no physical keys, no schema design yet.",
      outputs=["Producer–creator–consumer map: who supplies, who creates, who consumes each chosen output", "Consumer-backwards map: consumer need | output | required sources | rules and assumptions", "Mini-STTM for four to six important fields: target field | business meaning | source field(s) | transformation in English | check", "Shared glossary (AUM, position, latest price, gross value, fee, basis point, advisor book, valid trade) and trust questions (latest-price selection, invalid trades, fee calculation, reconciliation, no FX conversion)"],
      early="Draft a PRD or a data contract with Catalyst for one output.",
      debrief=["Which definition did the table disagree about, and how did you settle it?", "Which assumption could make the result untrustworthy?", "Who is the consumer, and what decision changes?"],
      extra="""
      **Timebox.** About 5 minutes on roles and the scenario, 10 choosing outputs and decisions, 15 to 25 on reverse-mapping and the mini-STTM, 10 on definitions and quality checks, 5 to 10 on playback. Playback: two to three minutes per table.

      **Sources (seeds).** `trades` (Trading), `instruments` (Security Master), `portfolios` (Portfolio Administration), `clients` and `advisors` (CRM), `funds` and `fund_holdings` (Fund Reference).
      """),
 dict(number="13", title="Capstone presentation", grouping="One person per table", minutes=3,
      brief="Two to three minutes: what you built and for whom, what was hard and what was easy, one finding in the data, one trust question you answered and how, and what you would do next. If you used Catalyst or the design documents, show one. If senior leaders are in the room, say where the paved path and Catalyst helped.",
      outputs=["The outputs you built, with one number you checked independently", "The hardest step, and the finding", "One trust question and its answer"],
      debrief=["Which teams picked the same outputs, and did their numbers agree?", "What would you tell the next cohort before they start?"]),
]

SECTIONS = [
 dict(n=1, title="The brief and discovery", anchor="s1", start="09:00",
      parts=["Brief: the day, the rules, ten minutes of reading", "Activity 12: discovery worksheet", "Playback: two minutes per table"]),
 dict(n=2, title="Phase 1: the baseline", anchor="s2", start="10:15",
      parts=["Challenge: Atlas Phase 1", "Circulating: section notes, expected results, blockers", "Lunch (flexible)"]),
 dict(n=3, title="Phase 2: extensions and presentation prep", anchor="s3", start="13:00",
      parts=["Challenge: the fourteen extensions", "Presentation prep: technical work stops at 14:30"]),
 dict(n=4, title="Presentations and close", anchor="s4", start="14:30",
      parts=["Activity 13: presentations", "Tally sheet and certification evidence", "Close"]),
]

def cells():
    A = {a["number"]: a for a in ACTIVITIES}
    act = lambda n: dc.md(dc.activity(n, A[n]["title"], A[n]["grouping"], A[n]["minutes"], A[n]["brief"], A[n]["outputs"], A[n].get("debrief"), A[n].get("early")))
    
    exp = (ROOT / "courseware/day5-capstone/support/expected-results.md").read_text().split("\n", 2)[2]
    AT = "support/atlas_duckdb"
    DB = f'HERE / "{AT}/warehouse/training_dev.duckdb"'
    C = [dc.title(5, TITLE, "anchor notebook"),
         
         *dc.how_to_use(5, "- Before the day: `bash support/atlas_duckdb/build.sh` and `python support/expected-results.py`, so the expected numbers below are from this laptop's build of the solution."),
         dc.code(dc.setup_cell(5)),
         dc.agenda(SECTIONS, lead='The day ends when every table has completed Phase 1 and presented. Cohorts usually present early afternoon.'),
         dc.section(1, "The brief and discovery", "s1"),
         dc.part("Brief", "the day, the rules, ten minutes of reading", time="09:00"),
         dc.figure("d5-capstone-day", "Friday in one line",
                   ["Discovery first, then the baseline, then extensions, then presentations.",
                    "Phase 1 is the certification bar: every team establishes it; Phase 2 is for teams that have and can explain it."]),
         dc.md(dc.say(["The project is challenges/v1/04-atlas-capstone in your dev container. The work happens in data_products/atlas_elt. Not in the challenge folder.",
                       "First job: reverse-engineer the source-to-target mapping from the data you are given and the tables you are asked to produce.",
                       "The data is synthetic and has been through several rounds of generation; a few things will look odd. Portfolio and fund do not mean what they mean in our own model; that is deliberate, so the design conversation is real.",
                       "Read the first third of the README on your own now. At 09:15, as a table: what are we being asked to do? Stop discussing by 10:00, 10:15 at the latest, so there is time to build.",
                       "Phase 1 is what you must complete. Phase 2 is open-ended, for whoever finishes. Lunch when you like; everyone back by 13:30; presentations when every table is done with Phase 1."])),
         dc.part("Activity 12", "discovery worksheet, then playback", time="09:15"),
         dc.anchor("Seven CSV files and seven output tables. Where do you start?",
                   "From the consumer's question backwards to the sources: the discovery worksheet.",
                   "Teams that map first build faster and present better; teams that start with SQL find the definitions mid-afternoon.",
                   "Roles, two outputs, the four worksheet sections, a two-minute playback."),
         dc.figure("d5-atlas-erd", "The Atlas sources: one fact table and six dimensions",
                   ["Trades carry identifiers only; follow portfolio_id to the client and advisor, instrument_id to the security.",
                    "Prices are in cents, fees in basis points, timestamps in epoch seconds: three unit conversions to agree before any SQL.",
                    "No FX conversion in this dataset: money stays in the trade currency, a known simplification to write down."]),
         dc.figure("d5-atlas-pipeline", "What Phase 1 builds: seeds, source-aligned, domain-aligned, consumer-aligned",
                   ["src_ models are faithful pass-throughs; dom_ models conform one definition per entity; rpt_, agg_, ts_ and api_ are shaped for a consumer.",
                    "dom_trading__trade (valid trades, signed quantity, gross value, fee) and dom_trading__latest_price feed almost everything.",
                    "The four reconciliation tests tie the marts together: advisor books, segments and regions must sum to the portfolio summary; three marts must agree on trade counts."]),
         dc.figure("d5-alignment-naming", "The names: src_, dom_, rpt_/agg_/ts_/api_, and the older layer words you will hear",
                   ["Alignment says whose shape a table is built for; medallion and raw/curated names say how far it has been cleaned.",
                    "Communicate in alignment language; recognise the older names when you meet them."]),
         act("12"),
         dc.md("""
         <details><summary><strong>Hints for circulating during discovery</strong></summary>

         - **rpt_portfolio_summary** needs positions (trades netted per portfolio and instrument), the latest price per instrument, and the portfolio, client and advisor dimensions. AUM is net quantity times latest price; fees are gross value times bps over 10,000.
         - **rpt_advisor_book** is the summary rolled up to advisor; **agg_segment_aum** rolled up to client segment; both must sum to the summary.
         - **agg_instrument_activity** and **ts_daily_market** count trades; so does the position mart; the three must agree.
         - **agg_fund_nav** weights the latest price by fund holdings; **api_latest_price** is a thin lookup over the latest price.
         - Trust questions rooms raise: is the latest trade price a fair mark? what is a valid trade (positive quantity and price, side B or S)? are fees in bps of gross value? trades before a portfolio's inception date? no FX, so cross-currency totals are nominal.
         - Terms to settle: AUM, position, latest price, gross value, fee, basis point, advisor book, valid trade.

         </details>
         """),
         dc.section(2, "Phase 1: the baseline", "s2"),
         dc.part("Challenge", "Atlas Phase 1", time="10:15"),
         dc.md(dc.challenge("Atlas capstone, Phase 1", "challenges/v1/04-atlas-capstone/README.md", "two to three hours",
                      "Every team establishes the baseline: seeds, the three layers, the tests, and the orchestration understood.",
                      [("Readiness, from the repo root", [
                          "`test -f .mise.toml && test -d data_products/atlas_elt && echo OK`.",
                          "`mise exec -- databricks auth describe --profile DEFAULT`.",
                          "`cd data_products/atlas_elt && dbt debug`."]),
                       ("Sections", [
                          "1 Inspect the source data.", "2 Understand the dbt project: `dbt deps`, `dbt ls`.", "3 Set up the Databricks connection.", "4 `dbt seed`.",
                          "5 Build source-aligned: `dbt run --select tag:source-aligned`.", "6 Build domain-aligned.", "7 Build consumer-aligned and run the tests.", "8 Understand the orchestration."])],
                      "`mise run challenge:verify 04` (not a bare verify.sh: it needs mise's environment); compare numbers with the expected results below.",
                      support=["Edit only under `data_products/atlas_elt/`; the stubs under `challenges/` are reset templates; solutions live with the instructor."])),
         dc.part("Circulating", "section notes, expected results, blockers"),
         dc.md("""
         | Section | What to check when circulating | Expected |
         |---|---|---|
         | 1 Seeds | Can they name the key of each seed and the join columns in trades? | trade_id; portfolio_id → portfolios; instrument_id → instruments |
         | 2 Project | Do they see the tags per folder and that most models are views? | `dbt ls` lists the stub models; tags source-, domain-, consumer-aligned |
         | 4 Seed | Row counts | trades 10,000; instruments 1,502; portfolios 2,501; clients 2,002; advisors 120; funds 60; fund_holdings 3,205 |
         | 5 Source-aligned | Pass-through only; trades as a table | 7 models, same counts as the seeds |
         | 6 Domain-aligned | Valid-trade filter; epoch to date; cents and bps; latest price by (ts, trade_id); positions net signed quantity | dom_trading__trade below 10,000; latest price 788 instruments |
         | 7 Consumer-aligned and tests | The four reconciliations pass; one value checked by hand | See the expected results below |
         | 8 Orchestration | Can they say what the DAG YAML triggers and where dbt actually runs? | A Databricks job per dataset, triggered by Airflow |
         """),
         dc.md("### Expected results (from the solution built on this laptop)\n" + exp),
         dc.code(f'sql("select rank, advisor_name, region, round(book_aum, 2) as book_aum from training_demo.rpt_advisor_leaderboard order by rank limit 5", {DB})\n# Compare a team\'s advisor book with this; a different top five usually means a different latest-price rule or an unfiltered trade set.'),
         dc.code(f'sql("""select (select count(*) from training_demo.src_trading__trades) as raw_trades, (select count(*) from training_demo.dom_trading__trade) as valid_trades,\n                 round((select sum(aum) from training_demo.rpt_portfolio_summary), 2) as summary_aum, round((select sum(book_aum) from training_demo.rpt_advisor_book), 2) as advisor_book_aum""", {DB})'),
         dc.md("""
         | Symptom | Cause | Fix |
         |---|---|---|
         | `tag:source-aligned` selects nothing | The `models:` block in `dbt_project.yml` was edited | Restore the folder-level tags; they are per layer folder, not in model bodies |
         | `dbt deps` fails or `ref` to a shared macro is missing | The local shared package was not installed | `dbt deps` from `data_products/atlas_elt` |
         | A bare `bash verify.sh` fails on auth | It runs outside mise's environment | `mise run challenge:verify 04` |
         | `show --inline "select …"` errors | mise word-splits the SQL | `dbt show --select <model>` |
         | `bundle validate` warns about an expired key | A sandbox clock artefact | Non-fatal; the dbt gate still runs |
         | Target path under `/Volumes/...` is not mounted | The project writes artefacts to a Unity Catalog volume in production | Add `--target-path target` for local inspection and clean it up after |
         | Transient "Error during request to server" | Databricks | Retry |
         """),
         dc.break_(60, "13:30 at the latest", lunch=True),
         dc.section(3, "Phase 2: extensions and presentation prep", "s3"),
         dc.part("Challenge", "choose extensions by value to the consumer; technical work stops at 14:30", time="13:00"),
         dc.md("""
         Choose by value to the consumer, not by difficulty. Each is a README challenge with a solution kept by the instructor; the DuckDB build in `support/atlas_duckdb/` has them all, for comparing a team's result.

         | Group | Extensions |
         |---|---|
         | Richer consumer marts | 1 executive report mart · 2 advisor leaderboard with `dense_rank()` · 3 daily activity by asset class with a rolling window · 14 a reconciling regional report (the Phase 2 capstone) |
         | Documentation and freshness | 4 source freshness on the extracts · 5 exposures: who consumes the marts |
         | Reuse and tests | 6 a reusable money macro · 7 a custom generic test for non-negative money · 8 a relationship test · 9 singular reconciliation tests within tolerance |
         | Loading patterns | 10 an incremental market mart · 11 a snapshot for slowly changing portfolios |
         | Orchestration | 12 understand and extend the orchestration · 13 params-driven orchestration |
         """),
         dc.code(f"!cd {AT} && dbt ls --resource-type model --select tag:consumer-aligned && dbt ls --resource-type test | head -12\n# The solution's consumer-aligned models and tests, for reference while a team describes theirs."),
         dc.section(4, "Presentations and close", "s4"),
         dc.part("Activity 13", "capstone presentation", time="14:30"),
         act("13"),
         dc.part("Tally sheet and certification evidence"),
         dc.md("""
         **Tally sheet** (fill in during the day)

         | Table | Outputs chosen | Phase 1 built (src / dom / consumer) | Tests pass | Independent check shown | Orchestration explained | Phase 2 taken | Presenter |
         |---|---|---|---|---|---|---|---|
         | 1 |  |  |  |  |  |  |  |
         | 2 |  |  |  |  |  |  |  |
         | 3 |  |  |  |  |  |  |  |
         | 4 |  |  |  |  |  |  |  |
         | 5 |  |  |  |  |  |  |  |
         """),
         dc.md(dc.reflect("CERTIFICATION EVIDENCE — what Phase 1 shows per team", "Observed during the day, not handed in.", [
                     "The worksheet: consumer, decision, sources, rules, assumptions.",
                     "The three layers built with the tag selectors.",
                     "The tests passing, including the reconciliations.",
                     "One value checked independently of the model that produced it.",
                     "An explanation of what the orchestration triggers and where dbt runs.",
                     "A presentation that states a finding and a caveat."])),
         dc.part("Close"),
         dc.md(dc.say(["One person per table, two to three minutes: what you built, what was hard, one finding, one trust question and its answer.",
                       "Do we feel we can create a data product and make it work? Then you are done. Thank you for the week."])),
         dc.md(dc.leave_with(LEAVE_WITH)),
         *dc.qa_section(5)]
    return C
