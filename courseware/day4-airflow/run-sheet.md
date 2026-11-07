# Day 4 run sheet — Bitemporal loading and Airflow orchestration

Instructor-only timing companion to the anchor notebook. Times follow the instructor plan; adapt them to the room and keep the sequence. Each row: purpose, what is on screen, notes, a line to say, the transition, and what to do if ahead or behind.

| Time | Block | Type | On screen |
|---|---|---|---|
| 09:00–09:45 | Bitemporal loading | Demo + shareback | Anchor › Bitemporal (diagram, demo cells, the macro); a guest or volunteer's screen |
| 09:45–10:00 | Orchestration and capstone orientation | Demo | Anchor › The DAG diagram; Friday preview |
| 10:00–10:15 | Break | Break |  |
| 10:15–10:45 | Airflow demonstration | Demo | Anchor › Airflow cells; the Airflow UI at localhost:8080 |
| 10:45–12:00 | Challenge 10 — Airflow practical | Challenge | Anchor › Challenge box; learners in challenges/v1/03-airflow-orchestration |
| 12:00–13:00 | Lunch | Break |  |
| 13:00–13:30 | Continue Airflow practical, regroup at 13:30 | Challenge + shareback | Anchor › Challenge box |
| 13:30–14:00 | CI/CD and deployment context | Demo | Anchor › CI/CD (diagram), Harness walkthrough, Datadog monitors |
| 14:00–14:15 | Break | Break |  |
| 14:15–14:35 | Release decision in pairs | Challenge + shareback | Anchor › Activity 10 card |
| 14:35–14:50 | Explain a failure and repair | Challenge + shareback | Anchor › Activity 11 card and template |
| 14:50–15:00 | Friday preparation and closing questions | Shareback | Anchor › Friday checklist |

## Blocks

### 09:00–09:45 · Bitemporal loading (Demo + shareback)

**Purpose.** Business time and system time; loading strategies; a worked history with a correction; which clock answers which question.

**On screen.** Anchor › Bitemporal (diagram, demo cells, the macro); a guest or volunteer's screen

**Instructor notes.**

- A volunteer or guest shows a real table for ten minutes if one was recruited yesterday; the anchor's demo on DuckDB covers the same ground either way.
- Ask the Monday/Wednesday question before opening any code; use one concrete timeline.
- Shareback: each table answers one 'which clock?' question.

**Say.**

- “The source corrects Monday's value on Wednesday. What was true on Monday, and what did we believe on Tuesday?”

**Transition.** From history to timing: orchestration.

**If ahead or behind.** Over time: skip the macro walk, keep the four queries.

### 09:45–10:00 · Orchestration and capstone orientation (Demo)

**Purpose.** What orchestration is, connected to the pipeline generated on Day 2; a preview of Friday's work and its starting files.

**On screen.** Anchor › The DAG diagram; Friday preview

**Instructor notes.**

- Open the eod_prices DAG from Day 2: it is the same shape as the challenge's.
- Friday: Phase 1 scope, two to three hours, the working folder rule.

**Say.**

- “Airflow plays no instrument. It tells dbt when to play, and what to do when it goes wrong.”

**Transition.** Break, then the Airflow demo.

### 10:00–10:15 · Break (Break)

**Purpose.** 

**On screen.** 

### 10:15–10:45 · Airflow demonstration (Demo)

**Purpose.** Operators, dependencies, callbacks, the UI, Astro blueprints, and a controlled failure, on a local Astro stack running Day 3's project.

**On screen.** Anchor › Airflow cells; the Airflow UI at localhost:8080

**Instructor notes.**

- Start the stack before the day (bash run.sh start); seed; trigger; show graph, grid, a task log, the code tab.
- Read >> as 'and then'. Open callbacks.py. Show a blueprint and its YAML.
- Controlled failure: stale, trigger, the freshness task fails and the rest is upstream_failed; fresh, trigger, green.

**Say.**

- “A green graph is not evidence that the data is right. The publish task shows the rows; that is evidence.”

**Transition.** Challenge 10 until lunch.

**If ahead or behind.** If the stack misbehaves, the status and log cells still show a previous green run.

### 10:45–12:00 · Challenge 10 — Airflow practical (Challenge)

**Purpose.** Launch the assigned Airflow project; learners wire the chain, run tasks inside the scheduler, inspect states and logs.

**On screen.** Anchor › Challenge box; learners in challenges/v1/03-airflow-orchestration

**Instructor notes.**

- Boot order matters: setup, then seeds, then astro dev start; the cold-start symptom and fix are in the anchor.
- Collect deployment and monitoring questions for the afternoon.

**Say.**

- “Which run produced this result, and what proves the data is right?”

**Transition.** Lunch.

**If ahead or behind.** Fast finishers: the extension questions (late input, failed check, repeated run), then Phase 2.

### 12:00–13:00 · Lunch (Break)

**Purpose.** 

**On screen.** 

### 13:00–13:30 · Continue Airflow practical, regroup at 13:30 (Challenge + shareback)

**Purpose.** Resolve blockers; Phase 2 for those on it; regroup with one run, one log and one output check per pair.

**On screen.** Anchor › Challenge box

**Instructor notes.**

- Keep credential and path errors separate from the intended data-quality failure.
- Shareback: a pair shows the current run, a useful log line, and the warehouse output.

**Say.**

- “Show me the run ID, the log line that told you what happened, and the table it produced.”

**Transition.** CI/CD and the deployment picture.

### 13:30–14:00 · CI/CD and deployment context (Demo)

**Purpose.** Where code goes, how deployment is initiated, where execution is visible, how failures are investigated: Harness, Astro, Datadog.

**On screen.** Anchor › CI/CD (diagram), Harness walkthrough, Datadog monitors

**Instructor notes.**

- Agree the agenda with a guest in advance; otherwise the anchor's walkthrough with screenshots.
- Say the downsides of CI/CD too; rooms respect it.

**Say.**

- “A pull request is where acceptance happens. A deleted test is a block of red lines that is easy to skim past.”

**Transition.** Break, then the release decision.

### 14:00–14:15 · Break (Break)

**Purpose.** 

**On screen.** 

### 14:15–14:35 · Release decision in pairs (Challenge + shareback)

**Purpose.** A failed candidate with 500 rows and 497 distinct IDs, yesterday's accepted output available: decide what ships and what to tell the consumer.

**On screen.** Anchor › Activity 10 card

**Instructor notes.**

- Ten minutes deciding and drafting, ten discussing. The failed candidate stays blocked; whether yesterday's output is acceptable depends on the consumer's freshness commitment.

**Say.**

- “What information is missing, and who can supply it?”

**Transition.** Write the failure note.

### 14:35–14:50 · Explain a failure and repair (Challenge + shareback)

**Purpose.** A short note another creator could use to locate the run and understand what happened; swapped and tested.

**On screen.** Anchor › Activity 11 card and template

**Instructor notes.**

- If a pair's execution was blocked, they use the anchor's prepared failure example and separate expected from observed.

**Say.**

- “Could another creator find this run from your note alone?”

**Transition.** Friday preparation.

### 14:50–15:00 · Friday preparation and closing questions (Shareback)

**Purpose.** Check the starting files and environment; record remaining problems and who resolves them.

**On screen.** Anchor › Friday checklist

**Instructor notes.**

- Every learner opens the capstone README and runs the readiness checks; problems go on the list with a name.

**Say.**

- “Tomorrow starts sharp at nine. The sharper you start, the sharper you finish.”

## Before learners leave

- [ ] The DAG, run and task identities, useful logs, an output check and a short explanation of the failure and repair, per pair.
- [ ] Every learner has opened challenges/v1/04-atlas-capstone/README.md and run the readiness checks in data_products/atlas_elt.
- [ ] A list of setup issues that could stop Friday's start, each with the person responsible for the next action.
- [ ] The Airflow stack stopped on the learners' laptops (astro dev stop) so Friday starts clean.
