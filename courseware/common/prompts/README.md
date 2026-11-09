# Prompt library

One entry per AI beat in the week. The Copilot form comes first (what learners type in Copilot Chat inside the dev container, with the AI Catalyst plugin); the Claude Code form follows only where it differs. Safe to share with learners as it is.

**Three rules, every time.** Never paste a token, a password or a client record. Read one section of anything generated aloud and find the invented detail before accepting it. When the output is wrong, fix the input (the transcript, the contract, the context) before fixing the output by hand.

## The two harnesses in one line each

| | Copilot (learners) | Claude Code (instructor) |
|---|---|---|
| Run a Catalyst skill | `/ai-catalyst <skill-name> <your request>` | `/<skill-name> <your request>` |
| Attach a file | `#file:02-prd.md` (or drag it into the chat) | `@common/running-example/02-prd.md` |
| Whole repository as context | `@workspace` | Claude reads what it needs; name the folder |
| Let it run commands | Agent mode | Default; approvals asked unless auto-approved |
| Start fresh | New chat | `/clear` |

Skills installed on both sides and used this week: `product-requirements-document`, `data-contract`, `transformation-spec`, `sla-dashboard-spec`, `data-quality-controls-plan`, `setup-dbt-project`, `write-dbt-source`, `write-dbt-model`, `validate-dbt`, `adding-dbt-unit-test`, `dbt-best-practices`, `generate-dag`, `validate-dag`, `runbook`, `consumer-onboarding-guide`, `consumer-use-case-map`, `data-model`, `dplc-concierge`.

## Day 1: discovery and design

**Activity 2, justify a product.** Same in both.
> Act as a sceptical sponsor. Here is my one-paragraph product idea: [paste]. Ask me the five questions you would need answered before funding it, then say which of my answers you would not believe without evidence.

**Activity 3, compare independent PRDs.** Each table member runs the skill alone from the same one-paragraph brief, then the table compares.
> `/ai-catalyst product-requirements-document` A daily, US-only end-of-day price sheet for the performance team, sourced from the vendor price feed and the instrument master, published by 07:30 Eastern. Write the PRD; leave open questions as questions rather than inventing answers.

Claude: `/product-requirements-document` with the same text.

**Activity 4, PRD from an interview transcript.**
> `/ai-catalyst product-requirements-document` Write the PRD from this transcript. #file:01-interview-transcript.md Mark anything you could not find in the transcript as an open question.

Claude: `/product-requirements-document Write the PRD from @common/running-example/01-interview-transcript.md …`

**Data contract from the PRD.**
> `/ai-catalyst data-contract` Draft the data contract for the product in #file:02-prd.md. Use the transcript #file:01-interview-transcript.md for field names, owners and timings; do not invent any.

**Find the invented detail** (use after every generation).
> List every concrete fact in this document (names, dates, numbers, owners, field names, revision history) that does not appear in the transcript or the PRD. Quote the line for each.

**Activity 5, explore the lifecycle.**
> `/ai-catalyst dplc-concierge` What are the phases of the data product lifecycle, what does the build phase require, and which of those requirements have a skill?

## Day 2: contract to platform

**Activity 6, extend the contract with an STTM and service levels.**
> `/ai-catalyst transformation-spec` Add a source-to-target mapping to #file:03-data-contract.md for the fields in its schema section. For each target field give the source field, the transformation in English, the null rule and the check that guards it. Flag any field whose source you cannot find.

> `/ai-catalyst sla-dashboard-spec` Propose the service-level indicators, objectives and the consumer-facing agreement for this contract, with measurable numbers and the clock each one is measured on.

**Markdown to HTML** (pick a fast model with low effort first; the point is to see the harness, not the prose).
> Convert #file:03-data-contract.md into one self-contained HTML page with a table of contents, no external assets, printable in A4. Keep every word.

**Challenge 01, Docker, when stuck.**
> Explain this Dockerfile line by line and say which lines produce a layer. #file:Dockerfile

> My container exits straight away. Here is `docker ps -a` and `docker logs <id>`: [paste]. Tell me whether the problem is the command, the working directory, a missing file or the port, and the one change to make.

**Activity 8, generate the code from the contract.**
> `/ai-catalyst setup-dbt-project` Set up a dbt project for the product in #file:03-data-contract.md with staging, intermediate and mart layers, tagged by layer.

> `/ai-catalyst write-dbt-source` Define the sources from the contract's source section, with freshness thresholds from the service levels.

> `/ai-catalyst write-dbt-model` Implement the mart from the STTM in #file:03-data-contract.md. One model per layer; every STTM rule traceable to a line.

> `/ai-catalyst generate-dag` Generate the Airflow DAG for this dbt project: a freshness gate first, the dbt project as a task group, a publish step, a schedule that meets the contract's delivery time, retries and failure callbacks.

**Activity 8b, review another pair's generated code.**
> Here is STTM rule R3 from the contract and the model that should implement it. Point to the line that implements the source column, the transformation and the null rule. If any is missing, say so; do not fix it yet.

> `/ai-catalyst validate-dbt` and `/ai-catalyst validate-dag` on what the other pair generated: list what fails and why, in order of severity.

## Day 3: the dbt practical

**Read the project before changing it.**
> Using #file:dbt_project.yml and the models folder, list the layers, the tag that selects each, and the command that builds only the staging layer.

**Write a model from one STTM row.**
> `/ai-catalyst write-dbt-model` Implement `stg_holdings` from this STTM row: [paste the row]. Use the source defined in #file:sources.yml. Add the schema.yml entry with a not-null and a unique test for the key.

**A failing model.**
> Here is the error and the compiled SQL in `target/compiled/…`: [paste]. Explain the error in one paragraph, propose the smallest change to the model, and give me the `dbt build --select <model>` command to check it.

**A failing test.**
> Show me the SQL dbt compiled for this test, query the rows it returns, and tell me whether the data or the test is wrong. Do not change the test to make it pass.

**Auth or connection error.**
> Run the three-step Databricks auth check from `.github/copilot-instructions.md` and tell me which step fails before suggesting I log in again.

**A unit test.**
> `/ai-catalyst adding-dbt-unit-test` Add a unit test for `int_holdings_enriched` that checks the FX conversion for one holding in GBP and one in USD, with fixed input rows.

**A macro.**
> Write a dbt macro `to_base_ccy(amount, fx_rate)` that returns the amount in base currency with a cast that works on both Databricks and DuckDB, using `adapter.dispatch` on `target.type`. Show the call site in one model.

**Documentation.**
> Write the `description` for every column of `agg_fund_daily_exposure` in schema.yml from the STTM, one sentence each, naming the source field. Do not describe what the SQL does; describe what the number means.

**Activity 9, test review in pairs.**
> Here is a test another pair wrote: [paste]. Which contract rule does it guard, what wrong data would still slip through, and what one extra test would close that gap?

## Day 4: bitemporal loading and orchestration

**Which clock?**
> This table has `dl_business_start_dt`, `dl_business_end_dt`, `dl_system_start_ts`, `dl_system_end_ts` and `dl_current_ind`. Write the query for (a) what is current, (b) what was true on 2 November as we know it today, (c) what the report showed at 09:00 on 3 November. Say which clock each query uses.

**Challenge 03, when stuck.**
> Run `astro dev run dags list-import-errors`, paste the first error, and tell me whether it is a Python error, a Cosmos rendering error or a missing connection, and the one command that fixes it.

> `echo $DBT_CATALOG` is empty in my terminal. Walk me through `mise run setup:databricks`, a new terminal, and `astro dev restart --wait 5m`, and tell me how to confirm each step worked.

> Explain what `on_failure_callback` receives in `context`, which three values I need to find the failed run in the UI, and show the log line this callback writes. #file:callbacks.py

> `/ai-catalyst validate-dag` Check #file:portfolio_analytics_daily.py for the chain `start >> source_freshness_check >> dbt_pipeline >> publish_to_catalog >> end`, retries with backoff, a schedule in a named time zone and catchup off.

**Activity 10, release decision.** The decision is yours; use the assistant for the draft only.
> The nightly candidate has 500 rows and 497 distinct IDs, so the uniqueness check failed and it was not published; yesterday's accepted output is still available. Draft a two-sentence update to the consumer that says what is known, what is not, and when the next update comes. Do not speculate about the cause.

**Activity 11, explain a failure and repair.**
> From this task log [paste], fill in: DAG and run ID; the task that failed and the first useful log line; the cause (data quality, credentials, path or code); the action taken; the output check after the repair; what is still unresolved. One line each. If the log does not say, write "not in the log".

**Phase 2 extras.**
> `/ai-catalyst runbook` Write the runbook for `portfolio_analytics_daily`: how to find a failed run, the three failure classes and their first checks, how to re-run one task, and who to call.

> `/ai-catalyst consumer-onboarding-guide` Write the consumer guide for the mart: what it contains, when it is fresh, how to check the run that produced it, and how to raise a problem.

## Day 5: the Atlas capstone

**Activity 12, discovery.** Map first, then let the assistant check the map.
> Here are the seed headers [paste the CSV header lines] and the names of the output models [paste]. For `rpt_portfolio_summary`, list the consumer question it answers, the sources it needs, and the transformations in English. Do not write SQL.

> `/ai-catalyst consumer-use-case-map` Build the producer, creator and consumer map for the Atlas wealth-management product from these outputs: [paste the chosen outputs].

> `/ai-catalyst data-model` Propose the domain entities between the Atlas seeds and `rpt_portfolio_summary`, and say which definition (position, latest price, valid trade, gross value, fee) each entity owns.

**Reverse-engineer a mini-STTM.**
> For `rpt_portfolio_summary.aum`, write the STTM row: business meaning, source fields, transformation in English, units (cents, basis points, epoch seconds) and the check. Then the same for `fees_paid`.

**Phase 1, when stuck.**
> `dbt run --select tag:source-aligned` selects nothing. Show me where the tags are set in #file:dbt_project.yml and what I changed.

> `dbt deps` failed: [paste]. Say whether it is the packages file, the network or a path, and the one fix.

**Phase 2 extras.**
> `/ai-catalyst dbt-best-practices` Review `data_products/atlas_elt` and list the three changes that would most improve it, with the file and line for each.

> `/ai-catalyst adding-dbt-unit-test` Add a unit test for `dom_trading__latest_price` with two trades for one instrument at the same timestamp and different trade IDs.

**Activity 13, the presentation.**
> Turn these notes into a three-minute talk outline with five bullets: what we built and for whom, the hardest step, one finding in the data, one trust question and its answer, what we would do next. Keep our words; do not add claims.
