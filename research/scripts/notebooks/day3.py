"""Day 3 — dbt practical and consolidation."""
import dc
DAY, SLUG, TITLE = 3, "day3-dbt", "dbt practical and consolidation"

BLOCKS = [
 dict(time="09:00–10:00", title="Challenge 9 — dbt practical: launch and first hour", type="Practical", on_screen="Anchor › Launch box; learners in challenges/v1/02-dbt-pipeline",
      purpose="Launch the assigned dbt project, explain the task sequence and the checks, and get everyone building Phase 1 (sources and staging).",
      notes=["Ten-minute launch from the anchor: where to work, the first three commands, what a green section looks like, what reset deletes.",
             "Then circulate with the three-point checklist. Collect questions in the Q&A table for the recap.", "Remind people to break around 10:00."],
      say=["The README teaches dbt as you go: concept, task, hint, check, a variation, then the solution. Attempt before you open the solution."],
      transition="Break; carry on after it.", flex="Anyone who knows dbt: skip to Phase 2 and the stretch list."),
 dict(time="10:00–10:15", title="Break", type="Break", on_screen="", purpose="", notes=[], say=[], transition="", flex=""),
 dict(time="10:15–11:00", title="Continue dbt practical", type="Practical", on_screen="Anchor › Walkthrough cells (for support)",
      purpose="Phase 1 complete for most; Phase 2 started by some; blockers resolved; questions collected.",
      notes=["Use the anchor's DuckDB walkthrough cells to show an expected result when someone is stuck; never type in their project.",
             "Access problems to the platform contact; code problems to the pair next to them first."],
      say=["Could this join pass its tests and still double the reported value?"],
      transition="At 11:00 the platform session, or the instructor-led version.", flex=""),
 dict(time="11:00–12:00", title="Guest session: the platform", type="Talk", on_screen="Anchor › Platform session (two diagrams, agenda, questions)",
      purpose="Why the paved path works this way: Airflow on Astronomer, Databricks and Unity Catalog, contracts, the vended repository, compute, operations.",
      notes=["If a guest comes: send them the anchor's agenda line; keep the learners' questions list ready; record answers in the Q&A table.",
             "If nobody comes: the anchor's instructor-led script, twenty-five minutes, then questions."],
      say=["Every tool choice on the path has a reason and a trade-off. Ask about the trade-offs."],
      transition="Lunch.", flex="A short guest session returns time to the practical."),
 dict(time="12:00–13:00", title="Lunch", type="Break", on_screen="", purpose="", notes=[], say=[], transition="", flex=""),
 dict(time="13:00–14:15", title="Complete and extend dbt practical", type="Practical", on_screen="Anchor › Stretch section",
      purpose="Complete and explain the work; Phase 2 for those on it; stretch (macros, snapshots, incremental, unit tests) for fast finishers.",
      notes=["About three hours of practice across the day in total; nobody has to finish Phase 2.", "Early finishers investigate one planted error in a copied project and show the failure and the repair."],
      say=["A successful build is not evidence. Show me one value you checked a different way."],
      transition="Break, then the recap.", flex=""),
 dict(time="14:15–14:30", title="Break", type="Break", on_screen="", purpose="", notes=[], say=[], transition="", flex=""),
 dict(time="14:30–14:45", title="Consolidation", type="Debrief", on_screen="Anchor › Recap table",
      purpose="Ask the room what it learned and write the ten topics up; arrange tomorrow's contributions (bitemporal loading, deployment).",
      notes=["Ask 'what did we learn?' and fill gaps from the recap table rather than lecturing.", "Recruit two volunteers for tomorrow: one with bitemporal loading in production, one with Harness access; give them the anchor's brief."],
      say=["Who here has a bitemporal table in production? Would you show us tomorrow morning: the columns and one or two loading strategies, ten minutes?"],
      transition="Pairs: swap a mapping and its test.", flex=""),
 dict(time="14:45–14:55", title="Test review in pairs", type="Pair activity", on_screen="Anchor › Activity 9 card",
      purpose="Exchange one mapping rule and its test; propose a wrong result and decide whether the test would catch it; agree one improvement.",
      notes=["The three wrong results: a duplicated join, a missing dated FX rate, a changed unit."],
      say=["Would your test catch it? If not, write the expected failure before you write the fix."],
      transition="Two or three examples to the room, then close.", flex=""),
 dict(time="14:55–15:00", title="Closing discussion", type="Debrief", on_screen="Anchor › Before learners leave",
      purpose="Share a missing check; save the dbt work for orchestration; confirm tomorrow's baseline.",
      notes=["Completing advanced dbt is not a prerequisite for tomorrow; the Airflow challenge ships the solved dbt project."],
      say=["Keep this project where it is. Tomorrow Airflow runs it."],
      transition="", flex=""),
]

LEAVE_WITH = ["The working dbt project, model and test results, one independent output check and the outstanding questions for orchestration, kept where they are.",
              "Each learner can trace one plain-English mapping through its model and its test.",
              "Two volunteers (or a guest) confirmed for tomorrow's bitemporal and deployment slots, with the brief.",
              "The Airflow baseline is ready: Databricks auth works, challenge 02's seeds are loaded, and Astro has been started once after setup."]

ACTIVITIES = [
 dict(number="9", title="Test review in pairs", grouping="Pairs", minutes=10,
      brief="Swap one mapping rule and the test that guards it with the person next to you. The reviewer proposes a wrong result the pipeline could produce: a duplicated join, a missing dated FX rate, a changed unit. Decide together whether the test would catch it. Agree one improvement and write down the expected failure.",
      outputs=["One rule, its test, and a wrong result the test would or would not catch", "One improvement (a new test, a tightened test, or an independent check) and the failure it should produce"],
      debrief=["Which wrong results would have passed every test in the project?", "What value did you check without using the model that produced it?"]),
]

SECTIONS = [
 dict(n=1, title="The dbt practical: launch, Phase 1 and the walkthrough", anchor="s1", start="09:00",
      parts=["Launch: the pipeline", "Challenge 9: dbt practical", "Walkthrough: Phase 1 on DuckDB", "Break", "Walkthrough: Phase 2 on DuckDB", "Circulating"]),
 dict(n=2, title="The platform session", anchor="s2", start="11:00",
      parts=["Guest: the platform team (or the instructor-led version)", "Lunch"]),
 dict(n=3, title="Complete and extend the practical", anchor="s3", start="13:00",
      parts=["Challenge 9 continued: Phase 2", "Stretch: macros, snapshots, incremental, unit tests", "Break"]),
 dict(n=4, title="Consolidation", anchor="s4", start="14:30",
      parts=["Debrief: what did we learn?", "Activity 9: test review in pairs", "Close"]),
]

def cells():
    A = {a["number"]: a for a in ACTIVITIES}
    act = lambda n: dc.md(dc.activity(n, A[n]["title"], A[n]["grouping"], A[n]["minutes"], A[n]["brief"], A[n]["outputs"], A[n].get("debrief"), A[n].get("early")))
    
    PA = "demos/portfolio_analytics"
    DB = f'HERE / "{PA}/warehouse/training_dev.duckdb"'
    C = [dc.title(3, TITLE, "anchor notebook"),
         
         *dc.how_to_use(3, "- The walkthrough cells run the same project as the learners' challenge, on DuckDB in `demos/portfolio_analytics/`. Run `bash demos/portfolio_analytics/demo.sh stretch` once before the day; the cells then rebuild pieces on demand."),
         dc.code(dc.setup_cell(3)),
         dc.agenda(SECTIONS, lead='The rhythm changes: a short launch, then self-paced practice from the README, with the instructor walking the room. A platform session at 11:00 (guest or instructor-led). Recap and a pair exercise at the end.'),
         dc.section(1, "The dbt practical: launch, Phase 1 and the walkthrough", "s1"),
         dc.part("Launch", "the pipeline you will build today"),
         dc.anchor("Yesterday Catalyst generated a dbt project for you. Could you have written it, and could you tell if it is wrong?",
                   "dbt from the inside: sources, staging, intermediate, marts, tests, docs, on the Portfolio Analytics case, on Databricks.",
                   "Reviewing generated code needs the same knowledge as writing it; the practical builds that knowledge one section at a time.",
                   "Work the README in order: concept, task, hint, check, variation, solution. Build Phase 1 before lunch, Phase 2 after."),
         dc.figure("d3-pipeline", "The Portfolio Analytics pipeline the learners build: five sources, staging, intermediate, three marts, tests",
                   ["Six raw feeds ship as seeds; five are modelled; refdata is there to inspect and for freshness practice.",
                    "Staging renames and casts, one model per source; intermediate does the joins; marts are the consumer-aligned facts and aggregates.",
                    "The tests are promises from a contract made executable: not null, unique, a relationship, accepted values, NAV within one basis point, the rollup reconciles."]),
         dc.part("Challenge 9", "dbt practical: Phase 1 first"),
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
         dc.part("Walkthrough", "Phase 1 on DuckDB: sources and staging"),
         dc.md(dc.demo("the same project, on DuckDB, section by section", f"The learners' challenge 02 solution ported to DuckDB in <code>{PA}/</code>: one cell per README section, for \"what should I see?\".", [
                  "Same model names, layers, tags and tests; the Databricks-only post-hook is a no-op macro here.",
                  f"Use a cell when someone asks what they should see; `{PA}/README.md` maps each cell to its README section.",
                  "Say once: the SQL is the same; only the target differs."])),
         dc.md("#### S1 — Inspect the raw data: what feeds the models"),
         dc.code(f'!cd {PA} && dbt seed --full-refresh 2>&1 | grep -E "INSERT|Done" \nsql("select * from training_demo.holdings_raw order by fund_cd, pos_dt limit 8", {DB})\n# A holding: one fund, one instrument, one day, valued in its local currency. Note fund_cd, pos_dt, isin, qty, mkt_val_lc, ccy_cd and _extracted_at.'),
         dc.md("#### S2 — Read the project: layers, materialisations, tags"),
         dc.code(f'!cd {PA} && dbt ls --resource-type model --exclude tag:stretch\n!sed -n "/^models:/,/^seeds:/p" {PA}/dbt_project.yml | head -24\n# Ten models in three layers. Layers are folders with +materialized and +tags: select a layer with --select tag:staging.'),
         dc.md("#### S3 — Sources and freshness: five lines per source table, because the fund master has no load timestamp"),
         dc.code(f'!cd {PA} && dbt source freshness 2>&1 | grep -E "freshness|pass|warn|error|Done" | head -12\n# Five sources report; product_ref has no loaded_at_field and is skipped. Tighten error_after to 0 hours and it flips to error: the check working, not a bug.'),
         dc.md("#### S4 — The first staging model: rename, cast, coalesce a null ISIN into CASH_<ccy>, no joins"),
         dc.code(f'!sed -n "1,30p" {PA}/models/staging/stg_holdings.sql'),
         dc.code(f'!cd {PA} && dbt build --select stg_holdings 2>&1 | grep -E "OK|PASS|ERROR|Done"\nsql("select fund_id, position_date, instrument_id, quantity, mv_local_ccy, local_ccy from training_demo.stg_holdings order by 1,2 limit 8", {DB})\n# Same grain as the source. instrument_id is an ISIN or CASH_<ccy>, never null; quantities are typed decimals.'),
         dc.md("#### S5 to S7 — The remaining staging models, then the whole layer by tag"),
         dc.code(f'!cd {PA} && dbt build --select tag:staging 2>&1 | grep -E "OK created|PASS|FAIL|ERROR|Done"\nsql("select * from training_demo.stg_prices order by instrument_id, price_date limit 8", {DB})\n# stg_positions and stg_prices dedup to the latest extract per natural key with row_number(); staging never raises the row count.'),
         dc.figure("d3-materialisations", "View, table, incremental, snapshot: where each is set and when to use it",
                   ["Staging and intermediate as views: cheap, always fresh, nobody reads them directly.",
                    "Marts as tables: a stable, fast handoff for consumers.",
                    "Set per folder in dbt_project.yml; override per model with config(). Both are configuration, not SQL."]),
         dc.md("#### S8 — A staging test is a query that must return no rows"),
         dc.code(f'!sed -n "1,20p" {PA}/models/staging/schema.yml\n!cd {PA} && dbt test --select stg_holdings 2>&1 | grep -E "PASS|FAIL|Done"\n# not_null and unique compile to select-the-violations queries. Zero rows is a pass.'),
         dc.break_(15, "10:15"),
         dc.part("Walkthrough", "Phase 2 on DuckDB: intermediate, marts, tests, docs"),
         dc.md("#### C1 — The enrichment join: holdings × prices × FX, grain unchanged"),
         dc.code(f'!sed -n "1,45p" {PA}/models/intermediate/int_holdings_enriched.sql\n# Left joins on (instrument, date) and (currency, GBP, date). Ask the room: what happens when the FX rate is missing? Here it defaults to 1.0 via coalesce; the running example on Day 2 chose to leave it null and fail the test. Both are decisions; the contract should say which.'),
         dc.md("#### C3, C4 — The marts: an aggregate by strategy and the daily-grain fact with a calculated NAV"),
         dc.code(f'!cd {PA} && dbt build --select +agg_fund_exposure +fct_portfolio_returns 2>&1 | grep -E "OK created|PASS|FAIL|ERROR|Done" | tail -8\nsql("select fund_id, position_date, strategy_code, exposure_base_ccy, instrument_count from training_demo.agg_fund_exposure order by 1,2", {DB})'),
         dc.code(f'sql("select fund_id, position_date, instrument_id, mv_local_ccy, fx_rate_to_base, mv_base_ccy, round(calc_nav_per_unit, 6) as calc_nav_per_unit from training_demo.fct_portfolio_returns order by 1,2", {DB})\n# calc_nav_per_unit = total base-currency market value / 100,000,000 synthetic units. Holdings only; cash excluded; a teaching measure, not an official NAV.'),
         dc.md("#### C5, C6 — Generic tests on the marts, and a singular reconciliation: NAV within one basis point of the custodian"),
         dc.code(f'!sed -n "1,40p" {PA}/tests/assert_nav_within_tolerance.sql\nsql("select c.fund_id, c.position_date, round(c.calc_nav_per_unit,4) as calc, cu.nav_per_unit as custodian, round((c.calc_nav_per_unit - cu.nav_per_unit)/cu.nav_per_unit*10000, 3) as variance_bps from training_demo.fct_portfolio_returns c join training_demo.seed_custodian_nav cu using (fund_id, position_date) order by 1,2", {DB})\n# The seeds are built so this passes within 1bp. Change one holding value and it will not: that is the test earning its keep.'),
         dc.md("#### C7, C8 — The full build, then docs and lineage"),
         dc.code(f'!cd {PA} && dbt build --exclude tag:stretch 2>&1 | grep -E "Done"\n!cd {PA} && dbt docs generate 2>&1 | grep -E "Catalog|Done" | tail -2\nprint("open target/index.html with: cd {PA} && dbt docs serve --host 127.0.0.1 --port 8081   (the --host matters: DBT_HOST is used for the Databricks host in the learners\' profile)")'),
         dc.md("#### C9, C10 — The Databricks post-hook and the capstone mart"),
         dc.code(f'!cat {PA}/macros/optimize_mart.sql\n# On Databricks: OPTIMIZE ... ZORDER BY (fund_id, position_date) after each mart, a Delta optimisation. Here: a no-op. A macro that dispatches on target.type is how one project runs on two warehouses.'),
         dc.code(f'sql("select * from training_demo.agg_fund_daily_exposure order by 1,2", {DB})\n!sed -n "1,20p" {PA}/tests/reconcile_daily_exposure.sql\n# C10: the (fund, date) rollup must preserve the strategy-level total. Learners create both the mart and this test.'),
         dc.part("Circulating", "three questions per learner, and the symptom table"),
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
         dc.section(2, "The platform session", "s2"),
         dc.part("Guest", "the platform team, or the instructor-led version"),
         dc.anchor("Why does the paved path look the way it does?",
                   "An hour from the platform team: Airflow on Astronomer, Databricks and Unity Catalog, contracts and the Marketplace, the vended repository, compute, operations.",
                   "Learners will create products in that repository next month; the decisions behind it are the context the practicals cannot give.",
                   "Agree the agenda with the guest; keep the questions list ready; or give the instructor-led version from the diagrams."),
         dc.md("**Agenda to agree with a guest (one line each):** where code goes (the vended repository and its data_products folder) · how Airflow is vended (Astro per team, blueprints in YAML, Databricks jobs) · the three catalog types and how a product reaches the domain catalog · data contracts (ODCS) and the Marketplace · compute (serverless by default) · operations onboarding, warranty and Datadog · what is still changing."),
         dc.figure("d3-catalogs", "Unity Catalog on the paved path: application, source-aligned and domain catalogs, and the Marketplace",
                   ["Your workspace's application catalog is where you build and test; nothing is shared from it.",
                    "After the data quality rules pass, a vended blueprint copies the product to the domain catalog; that is how you share.",
                    "One source-aligned catalog for ingested feeds; some producing teams publish straight into it.",
                    "Access: schema-level groups automated today, table-level by request, attribute-level later. The contract (ODCS, YAML) records it and seeds the Marketplace."]),
         dc.figure("d3-airflow-federation", "From one central Airflow to a vended Astro deployment per team",
                   ["Today's single instance runs about twelve thousand DAGs on one cluster; noisy neighbours are the daily problem.",
                    "The path vends an Astro deployment and a Databricks workspace per team from a template; net-new jobs start there.",
                    "Cross-team dependencies: publish an asset; a platform plugin forwards it through Kafka; no shared API tokens.",
                    "Operations: onboarding with a criticality level, a warranty period, vended Datadog dashboards; non-production Airflow hibernates outside business hours."]),
         dc.md("""
         <details><summary><strong>Instructor-led version</strong> (twenty-five minutes, if no guest comes)</summary>

         1. **Airflow today and tomorrow.** One open-source Airflow 2.11 instance, about 12,000 live DAGs (15,000 total) on a very large Kubernetes cluster; the vendor's recommended maximum is about 2,000. Options weighed: many self-run clusters (too much to manage), the cloud provider's managed Airflow (scaling and recovery not good enough for tier-one data), Astronomer (chosen: recovery objectives met with a plugin then a managed feature, the largest open-source contributor, a CLI that runs everything locally, quick vending). Migration is a "messy middle" over months: new jobs go to Astro now, critical pipelines last. Airflow 2.11 is end of life, so vended instances are Airflow 3 with the new UI; learners live in the Airflow UI, not the Astro console.
         2. **Dependencies across teams.** Airflow assets: publish one, downstream DAGs subscribe. Across many Airflows a platform plugin forwards asset events through a Kafka topic using centrally managed secrets, so no team shares an API token. A system-lineage view helps discovery; it is not a data lineage tool. The legacy scheduler still exists; integration is by API in both directions.
         3. **Databricks and Unity Catalog.** Seven years of Databricks; the old metastore could not share. Unity Catalog holds data outside any workspace and binds catalogs to workspaces, one Unity per region. Three catalog types: application (one per workspace, your scratch pad and jump point), source-aligned (one; ingested feeds with minimal translation; some teams publish directly), domain (curation; domain data and consumer-aligned data). Access at schema level by group, automated; table level by request; attribute level later.
         4. **Contracts and the vended repository.** Contracts in the Open Data Contract Standard (YAML), required to publish to a domain catalog, seeding the Marketplace; a CI check for them is coming. The repository: dot-files for linters and tooling; `data_products/` with blueprints (dependency checks, a Databricks run-now task), clusters and pools, shared assets; a data product is a Databricks Asset Bundle plus a dbt project with datasets, each dataset holding its dbt, its Airflow YAML and its job YAML; an Airflow task only triggers the Databricks job, which runs the dbt commands. A Catalyst skill pulls template updates into your repository; review the pull request because you will have customised things.
         5. **Compute and cost.** Serverless by default; classic compute warms up and costs while idle. Health-check DAGs are vended but cost money; non-production Airflow hibernates outside business hours; cost reports are coming; teams now own patching and vulnerabilities in their platform.
         6. **Questions rooms ask:** tiering (the platform is tier one; disaster recovery rules will be the creator's to write), can an application catalog be shared (no: write to it, the blueprint copies after quality rules), should source teams publish directly to the source-aligned catalog (increasingly yes), is the DDL migration tool staying (probably replaced by contract-driven deployment), consumer workspaces for business users (being designed).

         </details>
         """),
         dc.break_(60, "13:00", lunch=True),
         dc.section(3, "Complete and extend the practical", "s3"),
         dc.part("Challenge 9 continued", "Phase 2, then the stretch: macros, snapshots, incremental, unit tests"),
         dc.anchor("The README's Phase 2 is done. What does a production dbt project have that this one does not?",
                   "Macros that dispatch on the warehouse, a custom generic test, a snapshot (SCD type 2), an incremental mart, a unit test, an exposure.",
                   "These are the pieces the platform's vended project uses, and what tomorrow's bitemporal macro builds on.",
                   "Run the cells; then ask Copilot or Claude to add the same to the learner project, with the Catalyst skill for unit tests."),
         dc.code(f'!cat {PA}/macros/to_base_ccy.sql\n!cat {PA}/tests/generic/test_non_negative.sql\n# A macro names a repeated expression once; a generic test is a macro that returns the violating rows.'),
         dc.code(f'!cd {PA} && dbt snapshot 2>&1 | grep -E "snapshot|Done"\nsql("select fund_cd, fund_name, strategy_code, is_active, dbt_valid_from, dbt_valid_to from training_demo.fund_master_snapshot order by 1", {DB})\n# A snapshot keeps history: change a watched column in the seed, snapshot again, and the old row closes (dbt_valid_to) while a new one opens. Tomorrow adds the second clock.'),
         dc.code(f'!cd {PA} && dbt run --select agg_fund_daily_exposure_incremental 2>&1 | grep -E "incremental|Done"\n!cd {PA} && dbt run --select agg_fund_daily_exposure_incremental 2>&1 | grep -E "incremental|Done"\n!sed -n "1,25p" {PA}/models/stretch/agg_fund_daily_exposure_incremental.sql\n# First run: full load. Second run: only dates newer than the table holds, replaced on the unique key (delete+insert) so a re-delivered day does not duplicate.'),
         dc.code(f'!sed -n "/unit_tests:/,\\$p" {PA}/models/stretch/stretch.yml\n!cd {PA} && dbt test --select stg_holdings,test_type:unit 2>&1 | grep -E "unit_test|PASS|FAIL|Done"\n# A unit test runs the model SQL on made-up rows and compares with expected rows: no warehouse data, pure logic.'),
         dc.md(dc.prompt("Chat view, in the learner project", "/ai-catalyst adding-dbt-unit-test\nAdd a dbt unit test for stg_holdings covering: a null ISIN becomes CASH_<ccy>; fund codes are trimmed and upper-cased; a row with a null position date is dropped.",
                         "/adding-dbt-unit-test  (same text) — or simply: add a unit_tests entry for stg_holdings in a YAML file covering those three cases")),
         dc.break_(15, "14:30"),
         dc.section(4, "Consolidation", "s4"),
         dc.part("Debrief", "what did we learn?"),
         dc.md(dc.whiteboard("what did we learn? (fill gaps from this list, do not lecture it)", [
             ("Models and conventions", "Staging and integration models; CG naming (stg_, int_, fct_, agg_; on Friday src_, dom_, rpt_); the SQL behind a transformation is a SELECT dbt wraps."),
             ("Dependencies and change", "ref() and source() build the graph; a source or schema change is visible in lineage; dbt docs show it."),
             ("Testing and contracts", "Schema tests and singular tests are the contract's quality rules made executable; catalog information and descriptions come from the same YAML."),
             ("Bitemporal loading", "Tomorrow morning: the columns and one or two strategies, from a volunteer or guest. Questions to carry: what is business time vs system time? what happens on a correction?"),
             ("Deployment context", "Tomorrow afternoon: Harness and CI/CD, with screenshots for anyone without access."),
             ("Catalyst", "Generation, iteration, and the repository's data_products area where the code goes; 80 to 90% of the code from a good contract."),
             ("Airflow preview", "YAML-configured blueprints are tomorrow's topic; today's dbt project is what they will run."),
             ("Execution and storage", "dbt SQL runs on Databricks as Spark; files on S3 in Delta: columnar, with logs and manifests that give transactions; you can insert and delete, unlike plain Parquet."),
             ("Catalogue conventions", "Application, domain and source-aligned catalogs; publish via the domain catalog; the Marketplace is discovery."),
             ("Quality and materialisation", "Checks at project and model level; materialisation set per folder in dbt_project.yml or in the model file."),
         ], open_=True)),
         dc.part("Activity 9", "test review in pairs"),
         act("9"),
         dc.part("Close", "closing discussion"),
         dc.md(dc.say(["Two or three examples to the room: the wrong result, whether the test caught it, the improvement.",
                       "Save the project where it is; tomorrow Airflow runs it. Completing Phase 2 is not a prerequisite for tomorrow: the Airflow challenge ships the solved dbt project."])),
         dc.md(dc.leave_with(LEAVE_WITH)),
         *dc.qa_section(3)]
    return C
