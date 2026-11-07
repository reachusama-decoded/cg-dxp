# Cohort 7 — Day 4 (Thursday): bitemporal loading, Airflow, CI/CD and Harness, capstone briefing

Source: `extracts/cohort7/d4-transcript.txt`, `d4-ai-notes.txt`.

## As delivered

| Time | What happened |
|---|---|
| 09:07 | Learner presentation (Chris, with a colleague) on bitemporal loading, 20 minutes, with a live query on the Caspian associate dimension. |
| 09:26 | Michael: Airflow introduction (operators, sequencing, DAG, callbacks, UI, Astro blueprints), then the plan for the day and Friday. |
| 09:45–13:30 | `challenges/03-airflow-orchestration` (v1): Phase 1 (wire the Cosmos DAG; about 1.5 hours) then Phase 2 (alerting, SLA, monitoring, runbooks, tests). Lunch somewhere in the middle; some learners started Phase 2 before lunch. |
| 13:30 | CI/CD and the deployment context (below). |
| 13:40 | Learner demo of Harness on Caspian (10 minutes). |
| 13:50 | Phase 2 continues; check-in at 14:30; dev-container trouble for one learner (delete the containers, ask platform support). End 15:00. |

## Bitemporal loading (learner presentation) — reusable content

- Loading strategies: truncate-and-reload, insert-overwrite, SCD2 (effective start/end dates to keep history). Bitemporal = "SCD2 on steroids": business time and system time.
- In the prepared (mart) layer: `incremental_strategy = bitemporal_load_v2` with load types full, incremental, balance. Full when the source sends the whole book of record each run (expensive: every record end-dated and re-inserted daily); incremental for transaction feeds (business key such as transaction ID; new keys inserted; a known key with changed content end-dates the previous version and inserts a new one, so corrections such as a changed rep ID on a trade are answerable historically); balance for monetary balances (less used). Eight strategies in the framework; two projects this year needed custom work.
- Columns: DL system start/end time (when loaded, stamped from an Airflow variable, UTC), business start/end (the business-effective day; in the macro it is the load timestamp minus one millisecond, so a 3 a.m. PST run for the previous business day shows the previous date), current indicator. Query business time for "as was at that business date", system time for "when did we load it".
- The associate example: successive versions ordered by system start; tenure-month changes create versions; a join bug on job code/title produced a wrong version, then the fix produced a corrected version — the table is an audit of what the code produced at each point. Jeff's point: model with effective dating, be careful with Boolean status flags across snapshots.
- Implementation: a chain of Jinja macros ending in Python that hashes each change and stamps versions; vended products include it; customise if needed. "DBT does not provide a bitemporal strategy natively."

## Airflow introduction (Michael, ~15 minutes)

Orchestration = the conductor timing the orchestra. A DAG file is a Python function: operators first (the Cosmos `DbtTaskGroup` reads a configured dbt project and renders each stage as a task; the Databricks operator runs a notebook or job; packages add Slack, Teams, Google Docs operators), then sequencing with `>>` read as "and then": `t1 >> t2 >> [t3, t4]` means t1, then t2, then t3 and t4 in parallel. Decorator/DAG-level configuration: callbacks for success, failure and SLA miss (an escape hatch for when the DAG itself fails; a callback is a function run on an event, for example to log to Datadog). The UI: DAGs list, task states in green/amber/red, code and configuration. Astro blueprints: Python already written with placeholders; you fill YAML; covers 90%-plus of products; write a new blueprint for a genuinely custom case. "The challenges are around the Python side; once you have that, the YAML is simple."

## CI/CD and the deployment context (Michael, ~10 minutes)

Continuous integration = merging a feature branch frequently (daily, hourly, not monthly); continuous deployment = releasing to production environments. Why: faster feedback that something is broken; a shared understanding of the product across a team; observability of the lifecycle. Downsides: automation without a real human in the loop ("yes, yes, yes"), fragility, correlated failures ("if GitHub is down half the internet is down"), the maintenance, approval and audit burden — "CI/CD is not free". Data products are dbt and Airflow code in Git, not notebooks. Harness is approximately GitOps: a GitHub event (PR submitted and approved) triggers integration and deployment, which isolates the creator from the deployment machinery and makes the Git history the history of the live environment; full GitOps would have repository configuration mirror the live environment, CG is "halfway".

## Harness (learner demo)

Environments (Laser, Caspian); pipelines per repository. SQA deployment: Run → apply the SQA input set → pick your feature branch → run; a few minutes; first check who deployed last and whether they have finished testing, because SQA is shared. Production: the PRD pipeline, not for everyone; fixed value, release branch, and a CRQ number is mandatory. Logs exist for failures. A learner mentioned triggering Harness through an API token from Copilot ("dangerous"); deployments are normally webhook-triggered on merge; secrets sit in AWS Secrets Manager.

## Capstone briefing (end of day)

Start sharply at 09:00. 30–60 minutes on tables working backwards from the case study (AI-generated "alternative wealth-management company" with its own meaning of portfolio and fund — deliberately not CG so the design conversation is not trivial; a CG-products version two exists for people who find it easy). Phase 1 is the certification bar, usually two to three hours; Phase 2 is stretch. If everyone is done by about 13:45 there is 50 minutes of reporting back: hardest part of the opening conversation, most confusing step.
