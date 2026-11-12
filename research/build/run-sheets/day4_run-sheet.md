# Day 4 run sheet — Bitemporal loading and Airflow orchestration

[Data Creators › Day 4 — run sheet for instructors]{.breadcrumb}

Instructor-only companion to the anchor notebook, in the notebook's order: the same numbered sections and labelled parts, each with its time, purpose, what is on screen, what to say, what to ask at the whiteboard (with the answers rooms give and what to add), the demo steps with their coaching, fallbacks, the transition and what to do if ahead or behind. Keep the notebook on the projector and this beside it. Times follow the instructor plan; adapt them to the room and keep the sequence.

## Before the day

- Both demos build on Day 3's price sheet. Section 1 runs in `demos/price_sheet/` (its first cell resets the folder to Day 3's finished project). Section 2 runs the same project as the `price_sheet_daily` DAG on the local Airflow stack in `demos/airflow_local/`.
- Before the day: Docker Desktop running, then `bash demos/airflow_local/run.sh start` and `bash demos/airflow_local/run.sh seed`. The Airflow UI is http://localhost:8080. Run sections 1 and 2 once before the room arrives.
- Backups, not shown in the notebook: `bash demos/bitemporal/demo.sh` (the associate example) and the `portfolio_analytics_daily` DAG in the same stack (the learners' challenge DAG).

## Sections

| # | Section | Time | What happens |
|---|---|---|---|
| 1 | Bitemporal loading | 09:00–09:45 | Demo: two clocks on the price sheet, three deliveries, three questions · Guest or volunteer: a real table · Shareback: which clock? |
| 2 | Airflow orchestration | 09:45–13:30 | Orientation: why orchestrate, and reading a DAG · Break · Demo: the challenge's steps 3 to 10 on the price sheet · Launch · Challenge 10: Airflow practical · Walkthrough: Phase 2 on the price sheet · Lunch · Shareback: one run, one log, one output check |
| 3 | CI/CD and release operations | 13:30–15:00 | Demo: GitOps, Harness, Datadog · Break · Activity 10: release decision · Activity 11: explain a failure and repair · Friday preparation |

## Day at a glance

| § | Time | Block | Type | On screen |
|---|---|---|---|---|
| 1 | 09:00–09:45 | Bitemporal loading, on yesterday's price sheet | Demo + shareback | Anchor › section 1, top to bottom (demos/price_sheet); a guest or volunteer's screen |
| 2 | 09:45–10:00 | Orchestration and capstone orientation | Demo | Anchor › section 2, steps 1 and 2 (demos/airflow_local); Friday preview |
| 2 | 10:00–10:15 | Break | Break |  |
| 2 | 10:15–10:45 | Airflow demonstration | Demo | Anchor › section 2, steps 3 to 10; the Airflow UI at localhost:8080 |
| 2 | 10:45–12:00 | Challenge 10 — Airflow practical | Challenge | Anchor › Challenge box; learners in challenges/v1/03-airflow-orchestration |
| 2 | 12:00–13:00 | Lunch | Break |  |
| 2 | 13:00–13:30 | Continue Airflow practical, regroup at 13:30 | Challenge + shareback | Anchor › Challenge box |
| 3 | 13:30–14:00 | CI/CD and deployment context | Demo | Anchor › CI/CD (diagram), Harness walkthrough, Datadog monitors |
| 3 | 14:00–14:15 | Break | Break |  |
| 3 | 14:15–14:35 | Release decision in pairs | Challenge + shareback | Anchor › Activity 10 card |
| 3 | 14:35–14:50 | Explain a failure and repair | Challenge + shareback | Anchor › Activity 11 card and template |
| 3 | 14:50–15:00 | Friday preparation and closing questions | Shareback | Anchor › Friday checklist |

## Timeline

### 1. Bitemporal loading

Demo: two clocks on the price sheet, three deliveries, three questions · Guest or volunteer: a real table · Shareback: which clock?

#### 09:00 · 45 min · Instructor-led demo — Demo — two clocks on the price sheet: three deliveries, three questions

**Purpose.** Business time and system time; loading strategies; a worked history with a correction; which clock answers which question.

**Instructor notes.**

- Eight steps on Day 3's price sheet, one command per cell: reset and build, look at the three FX deliveries, write the history model, write the macro, three loads with the GBP rows and a picture after each, then the three questions.
- The story: the vendor sends a wrong GBP rate for 4 November (1.628112, two digits swapped) and corrects it in the next delivery (1.268112). After load 3 GBP has four rows; name them A, B, C, D as the pictures do.
- The last query shows one GBP price in dollars twice, as was and as is: the link back to yesterday's price sheet, which could only ever show one.
- A volunteer or guest shows a real table for ten minutes if one was recruited yesterday; the demo covers the same ground either way.
- Shareback: each table answers one 'which clock?' question.
- Backup: bash demos/bitemporal/demo.sh runs the older associate example from one script.

**Say.**

- “The vendor sends a wrong rate on Wednesday and corrects it on Thursday. What was the rate, and what did Wednesday's report say?”
- “Yesterday's snapshot kept one clock. Two clocks tell a new day from a correction.”

**Ask at the whiteboard — loading strategies and two clocks.** Ask in order, write what the room says, add what is missing.

| Ask | Expect, then add |
|---|---|
| How can new data land in a table? | Truncate and reload; insert-overwrite; SCD type 2 (effective start and end dates keep history). Bitemporal is SCD2 with a second clock. |
| What are the two clocks? | Business time: when the fact was true in the world (the business date). System time: when the warehouse loaded or believed it. Separate columns for start and end of each, plus a current indicator and a row hash. |
| Full, incremental, balance? | Full: the source sends the whole book of record each run (expensive: every row re-versioned). Incremental: only new or changed records with a business key; a known key with new content ends the previous version. Balance: for monetary balances. Some models need a custom strategy. |
| Why does a correction matter? | Because 'as was' must still answer what the report said on Wednesday, and 'as of' must give the corrected value today. Overwriting destroys the first; a status flag cannot express either. |
| UTC or local? | The platform stamps system time in UTC; a run at 03:00 Pacific for the previous business day shows yesterday's business date. Always say which clock a date column is. |

**Guest or volunteer — a real bitemporal table.**

**Shareback — which clock?**

**Transition.** From history to timing: orchestration.

**Adapt.** Over time: show the macro picture but not the macro file; keep the three loads and the three questions.

**Assessment.** Anchor › section 1, top to bottom (demos/price_sheet); a guest or volunteer's screen

### 2. Airflow orchestration

Orientation: why orchestrate, and reading a DAG · Break · Demo: the challenge's steps 3 to 10 on the price sheet · Launch · Challenge 10: Airflow practical · Walkthrough: Phase 2 on the price sheet · Lunch · Shareback: one run, one log, one output check

#### 09:45 · 15 min · Explain — Orientation — why orchestrate, and reading a DAG

**Purpose.** What orchestration is, on yesterday's price sheet; how to read a DAG file; a preview of Friday's work and its starting files.

**Instructor notes.**

- Steps 1 and 2 of the challenge on the price_sheet_daily DAG: why orchestrate (the five-gaps picture), the path, the DAG picture, then the top of the DAG file and the DAG block.
- The first cell puts the TODO back (run.sh unwire), so the DAG starts as the learners' does.
- Friday: Phase 1 scope, two to three hours, the working folder rule.

**Say.**

- “Airflow plays no instrument. It tells dbt when to play, and what to do when it goes wrong.”

**Say.**

- “Friday: you get CSV files about a fictional wealth manager called Atlas and a README. Phase 1 is the certification bar: sources, the three layers, tests, and understanding the orchestration. Two to three hours for most teams. Phase 2 is fourteen extensions you choose from. We watch you build it; nobody hands out solutions.”
- “Work in data_products/atlas_elt, not in the challenge folder. If you run it in the wrong folder, that is on you, and now you have been told.”

**Transition.** Break, then the Airflow demo.

**Assessment.** Anchor › section 2, steps 1 and 2 (demos/airflow_local); Friday preview

#### 10:00 · 15 min · Break — Break, back at 10:15

#### 10:15 · 30 min · Instructor-led demo — Demo — connect, gate, group, wire, schedule, retry, run, repair

**Purpose.** Steps 3 to 10 of the challenge on the price sheet: the connection, the freshness gate, the Cosmos group, the one line of wiring, the schedule, retries, a green run, and a controlled failure with its repair.

**Instructor notes.**

- Start the stack before the day (bash run.sh start). Every step is one command per cell; keep the UI open beside the notebook and switch to it at steps 6, 9 and 10.
- Step 6 is the learners' one line: run.sh wire replaces the TODO. Read >> as 'and then'.
- Step 9: a green run takes about half a minute here. The dbt show cell is the evidence, not the green boxes.
- Step 10: stale, trigger, wait about a minute: the gate goes yellow twice, then red, and the rest is upstream_failed. Then fresh, and Clear the failed task in the UI with Include Downstream. The demo DAG waits 15 seconds between retries; the learners' waits 2 minutes, so tell them a failure takes about ten minutes to turn red.
- Close with the blueprint picture: at CG most DAGs come from a blueprint and YAML.
- Backup: portfolio_analytics_daily, the learners' own DAG, is in the same stack (bash run.sh trigger, wait, status with no DAG name).

**Say.**

- “A green graph is not evidence that the data is right. The rows are the evidence.”
- “You write one line today. Everything else, you read and prove.”

**Launch — from this demo to your challenge.**

**Transition.** Challenge 10 until lunch.

**Adapt.** Short of time: steps 4, 6, 9 and 10. If the stack misbehaves, the status cell still shows the earlier runs.

**Assessment.** Anchor › section 2, steps 3 to 10; the Airflow UI at localhost:8080

#### 10:45 · 75 min · Independent or pairs work — Challenge 10 — Airflow practical

**Purpose.** Launch the assigned Airflow project; learners wire the chain, run tasks inside the scheduler, inspect states and logs.

**Instructor notes.**

- Boot order matters: setup, then seeds, then astro dev start; the cold-start symptom and fix are in the anchor.
- Collect deployment and monitoring questions for the afternoon.

**Say.**

- “Which run produced this result, and what proves the data is right?”

**Challenge — Airflow practical (challenge 03).** `challenges/v1/03-airflow-orchestration/README.md` · until 13:30, with lunch.

**Walkthrough — Phase 2: production operations, on the price sheet.**

**Demo — Phase 2 on the price sheet.** The ten Phase 2 challenges, one or two cells each, for when learners reach them.

1. Use these cells at 13:00, or beside a learner who has reached Phase 2.
2. Every Phase 2 file ships complete: the task is to read each piece and prove it does what it says.
3. The failed run from step 10 is the evidence for challenges 1 to 4.

**Transition.** Lunch.

**Adapt.** Fast finishers: the extension questions (late input, failed check, repeated run), then Phase 2.

**Assessment.** Anchor › Challenge box; learners in challenges/v1/03-airflow-orchestration

#### 12:00 · 60 min · Break — Lunch, back at 13:00

#### 13:00 · 30 min · Feedback and discussion — Shareback — one run, one log line, one output check per pair

**Purpose.** Resolve blockers; Phase 2 for those on it; regroup with one run, one log and one output check per pair.

**Instructor notes.**

- Keep credential and path errors separate from the intended data-quality failure.
- Shareback: a pair shows the current run, a useful log line, and the warehouse output.
- For learners in Phase 2: the anchor's Phase 2 walkthrough shows each of the ten challenges on the price sheet, with the morning's failed run as the evidence for the alert tiers. Ten minutes on screen at 13:00 if several pairs are there.

**Say.**

- “Show me the run ID, the log line that told you what happened, and the table it produced.”

**Transition.** CI/CD and the deployment picture.

**Assessment.** Anchor › Challenge box

### 3. CI/CD and release operations

Demo: GitOps, Harness, Datadog · Break · Activity 10: release decision · Activity 11: explain a failure and repair · Friday preparation

#### 13:30 · 30 min · Instructor-led demo — Demo — GitOps, Harness, Datadog

**Purpose.** Where code goes, how deployment is initiated, where execution is visible, how failures are investigated: Harness, Astro, Datadog.

**Instructor notes.**

- Agree the agenda with a guest in advance; otherwise the anchor's walkthrough with screenshots.
- Say the downsides of CI/CD too; rooms respect it.

**Say.**

- “A pull request is where acceptance happens. A deleted test is a block of red lines that is easy to skim past.”

**Ask at the whiteboard — CI/CD.** Ask in order, write what the room says, add what is missing.

| Ask | Expect, then add |
|---|---|
| What do CI and CD mean? | Integration: merging a feature branch, often. Deployment: releasing to an environment, including production, often. |
| Why bother? | Faster feedback that something is broken; a shared understanding of the product across the team; observability of the lifecycle. |
| What are the downsides? | Automation without a real human in the loop; fragility; correlated failures (when one shared system is down, everything is); the maintenance, approval and audit burden. It is not free. |
| What is Harness here? | The CI/CD system, roughly GitOps: a pull request submitted and approved triggers the pipeline. It isolates the creator from the deployment machinery. |

**Demo — Harness, with screenshots or a guest.** Walk a deployment to SQA and then to production: live if someone has access, else from the pre-flight screenshots.

1. Pick the environment and find the repository's pipeline.
2. SQA: Run, apply the SQA input set, choose the feature branch, run; a few minutes.
3. Check who deployed to SQA last and whether they finished testing: SQA is shared.
4. Production: the PRD pipeline, fixed values, the release branch, and a change record (CRQ) number before anything runs.
5. Open the logs of a failed execution.
6. Say: secrets live in AWS Secrets Manager, never in code or a chat; an API token that lets an AI assistant trigger deployments is a risk, not a shortcut.

**Transition.** Break, then the release decision.

**Assessment.** Anchor › CI/CD (diagram), Harness walkthrough, Datadog monitors

#### 14:00 · 15 min · Break — Break, back at 14:15

#### 14:15 · 20 min · Independent or pairs work — Activity 10 — release decision

**Purpose.** A failed candidate with 500 rows and 497 distinct IDs, yesterday's accepted output available: decide what ships and what to tell the consumer.

**Instructor notes.**

- Ten minutes deciding and drafting, ten discussing. The failed candidate stays blocked; whether yesterday's output is acceptable depends on the consumer's freshness commitment.

**Say.**

- “What information is missing, and who can supply it?”

**Activity 10 — Release decision.** Pairs, 20 min; the card is in `activities/`.

**Transition.** Write the failure note.

**Assessment.** Anchor › Activity 10 card

#### 14:35 · 15 min · Independent or pairs work — Activity 11 — explain a failure and repair

**Purpose.** A short note another creator could use to locate the run and understand what happened; swapped and tested.

**Instructor notes.**

- If a pair's execution was blocked, they use the anchor's prepared failure example and separate expected from observed.

**Say.**

- “Could another creator find this run from your note alone?”

**Activity 11 — Explain a failure and repair.** Pairs, then swap, 15 min; the card is in `activities/`.

**Transition.** Friday preparation.

**Assessment.** Anchor › Activity 11 card and template

#### 14:50 · 10 min · Intro/Outro — Friday preparation — the checklist, then the close

**Purpose.** Check the starting files and environment; record remaining problems and who resolves them.

**Instructor notes.**

- Every learner opens the capstone README and runs the readiness checks; problems go on the list with a name.

**Say.**

- “Tomorrow starts sharp at nine. The sharper you start, the sharper you finish.”

**Assessment.** Anchor › Friday checklist

## Before learners leave

- [ ] The DAG, run and task identities, useful logs, an output check and a short explanation of the failure and repair, per pair.
- [ ] Every learner has opened challenges/v1/04-atlas-capstone/README.md and run the readiness checks in data_products/atlas_elt.
- [ ] A list of setup issues that could stop Friday's start, each with the person responsible for the next action.
- [ ] The Airflow stack stopped on the learners' laptops (astro dev stop) so Friday starts clean.
