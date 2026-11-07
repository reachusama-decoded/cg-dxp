# Day 2 run sheet — Mappings, service levels and implementation foundations

Instructor-only timing companion to the anchor notebook. Times follow the instructor plan; adapt them to the room and keep the sequence. The § column is the notebook section the block belongs to. Each block: purpose, what is on screen, notes, a line to say, the transition, and what to do if ahead or behind.

## Sections

1. **Mappings and service commitments** (09:00–10:15): Demo: STTM and service levels · Activity 6: extend the contract · Break · Shareback: review and present a contract
2. **Platform architecture** (10:15–11:00): Demo: warehouse, lake, lakehouse · Demo: Databricks under the hood, Delta, Spark · Demo: how the tools fit together · Shareback · Break
3. **Docker** (11:00–13:00): Demo: the five steps and the dev container's Dockerfile · Challenge 7: Docker practical · Lunch
4. **Contract to code** (13:00–15:00): Demo: where output lands, live generation · Activity 8: generate and investigate · Break · Debrief · Activity 8b: review another pair's code · Close

## Timeline

| § | Time | Block | Type | On screen |
|---|---|---|---|---|
| 1 | 09:00–09:20 | Mappings and service commitments | Demo | Anchor › STTM and service levels (two diagrams, nines table) |
| 1 | 09:20–09:45 | Activity 6 — Extend the contract | Challenge | Anchor › Activity 6 card |
| 1 | 09:45–10:00 | Break | Break |  |
| 1 | 10:00–10:15 | Review and present a contract | Shareback + demo | VS Code Markdown editor, then Copilot/Claude, then the browser |
| 2 | 10:15–10:45 | Platform architecture: warehouse, lake, lakehouse and Databricks under the hood | Demo + shareback | Anchor › Platform architecture (five diagrams); the Delta and Spark demos |
| 2 | 10:45–11:00 | Break | Break |  |
| 3 | 11:00–11:25 | Docker demonstration | Demo | Anchor › Docker; a terminal; the dev container's Dockerfile |
| 3 | 11:25–12:00 | Challenge 7 — Docker practical | Challenge | Anchor › Challenge box; learners in challenges/v1/01-docker-intro |
| 3 | 12:00–13:00 | Lunch | Break |  |
| 4 | 13:00–13:15 | Contract to code, how the tools fit together, Databricks setup | Demo | Anchor › Contract to code; Databricks (learners) and DuckDB (instructor) |
| 4 | 13:15–14:05 | Challenge 8 — Generate and investigate | Challenge | Anchor › Activity 8 card and prompts |
| 4 | 14:05–14:15 | Break | Break |  |
| 4 | 14:15–14:30 | Debrief | Shareback | Anchor › Debrief (dbt flow diagram) |
| 4 | 14:30–14:50 | Review another pair's generated code | Challenge | Anchor › Activity 8b card |
| 4 | 14:50–15:00 | Corrections and closing discussion | Shareback | Anchor › Before learners leave |

## Blocks

### 09:00–09:20 · Mappings and service commitments (Demo, §1)

**Purpose.** Source-to-target mapping rule types; SLI, SLO and SLA as measure, ideal, tolerance; the indicators a product needs; availability in nines.

**On screen.** Anchor › STTM and service levels (two diagrams, nines table)

**Instructor notes.**

- Elicit rule types on the whiteboard; Catalyst returns a CG-specific list, say so.
- The nines table is in the anchor; say the month, week, day, hour, minute mnemonic.

**Say.**

- “An SLI is a number you can measure. An SLO is what you wish it were. An SLA is how far it may stray before you owe someone an explanation.”

**Transition.** Activity 6: put both into yesterday's contract.

**If ahead or behind.** Running late: skip how providers get nines; keep the table.

### 09:20–09:45 · Activity 6 — Extend the contract (Challenge, §1)

**Purpose.** Ask Catalyst for the transformation types and service measures, then add realistic STTM rules and commitments to a Day 1 contract.

**On screen.** Anchor › Activity 6 card

**Instructor notes.**

- Transcribe the table's rule discussion and feed it in, as on Day 1.
- Collect one revised contract per table for the review block.

**Say.**

- “Be specific enough that someone else could implement the rule without asking you what it means.”

**Transition.** Break; after it, one submitted contract on screen.

**If ahead or behind.** Overrun flows into the break; the review block uses whatever was submitted.

### 09:45–10:00 · Break (Break, §1)

**Purpose.** 

**On screen.** 

### 10:00–10:15 · Review and present a contract (Shareback + demo, §1)

**Purpose.** Review a submitted contract in the Markdown editor, then generate a self-contained HTML version with an overview, contents and diagrams.

**On screen.** VS Code Markdown editor, then Copilot/Claude, then the browser

**Instructor notes.**

- Open with 'Open with Markdown editor'; then the prompt in the anchor; use a fast model at low effort first and let the big model finish in the background.
- Open the HTML in the browser; show it is navigable and iterable.

**Say.**

- “Same file, two renderings. The AI does not care; you and your reviewers do.”

**Transition.** Before we leave design: what makes an English rule unimplementable?

**If ahead or behind.** If generation stalls, open common/running-example/data-contract.html.

### 10:15–10:45 · Platform architecture: warehouse, lake, lakehouse and Databricks under the hood (Demo + shareback, §2)

**Purpose.** Warehouse vs lake vs lakehouse; where Databricks fits; Delta tables under the hood; what the Spark engine does; how the tools fit together.

**On screen.** Anchor › Platform architecture (five diagrams); the Delta and Spark demos

**Instructor notes.**

- Elicit each tool's role first, then the tools-together diagram.
- Run the Delta demo: files plus a log, a merge, time travel, OPTIMIZE; then the Spark demo with the UI open.
- Shareback: each table names one thing Databricks does that a plain file store cannot, and one thing dbt relies on Databricks for.

**Say.**

- “A lakehouse is a relational database split in two: files on S3, compute on Databricks, and a transaction log in between to get the guarantees back.”

**Transition.** Break, then Docker.

**If ahead or behind.** Behind: show the tools-together diagram and the Delta demo only; the timeline and Spark are optional.

### 10:45–11:00 · Break (Break, §2)

**Purpose.** 

**On screen.** 

### 11:00–11:25 · Docker demonstration (Demo, §3)

**Purpose.** Dependencies, reproducibility, isolation and resource limits; Dockerfile to image to container; the dev container and its terminal.

**On screen.** Anchor › Docker; a terminal; the dev container's Dockerfile

**Instructor notes.**

- Finish the HTML review first if the big model has finished.
- Run the anchor's cells: run an image, look inside, build, run, tag.
- Show the training repo's Dockerfile: FROM, COPY, RUN, USER, ENV. Say EDO maintains it.

**Say.**

- “Your terminal in VS Code is inside a container. That is why dbt and astro are there and why your laptop's Python is not.”

**Transition.** Challenge 7 in the dev container until lunch.

### 11:25–12:00 · Challenge 7 — Docker practical (Challenge, §3)

**Purpose.** Run, inspect, build and rerun a small image; the one-command gate.

**On screen.** Anchor › Challenge box; learners in challenges/v1/01-docker-intro

**Instructor notes.**

- Sections 1–5 of the README, about 35 minutes; section 6 and the variations for fast finishers.
- Keep a working example ready for anyone blocked by engine access; pair them.

**Say.**

- “Why did the container stop, and what survives when you run a fresh one?”

**Transition.** Lunch.

**If ahead or behind.** Experienced people: multi-stage builds, resource limits, Kubernetes questions.

### 12:00–13:00 · Lunch (Break, §3)

**Purpose.** 

**On screen.** 

### 13:00–13:15 · Contract to code, how the tools fit together, Databricks setup (Demo, §4)

**Purpose.** Brief Challenge 8; show authentication, the training schema and where output lands.

**On screen.** Anchor › Contract to code; Databricks (learners) and DuckDB (instructor)

**Instructor notes.**

- Learners: mise run setup:databricks, dpc-check, the catalog training_dev and schema training_<user>. Instructor: the same thing in DuckDB with information_schema.
- Run the first minute of a generation live, then open the prepared eod_prices project.

**Say.**

- “Most of the Databricks UI you will never need on the paved path. You write dbt in files; the UI is where the tables appear.”

**Transition.** Challenge 8.

### 13:15–14:05 · Challenge 8 — Generate and investigate (Challenge, §4)

**Purpose.** Generate dbt and Airflow code from the contract, explain it, run as far as possible, and bring one discovery and one correction.

**On screen.** Anchor › Activity 8 card and prompts

**Instructor notes.**

- Pairs who finish choose one extension question from the card.
- Experienced learners: the bitemporal macro or Airflow-to-Datadog logging; keep findings short.

**Say.**

- “Run what you can. What you cannot run, read until you can explain it.”

**Transition.** Break, then the debrief in the stated order.

**If ahead or behind.** If Databricks auth is widespread trouble, let pairs generate and read without running; the debrief is unchanged.

### 14:05–14:15 · Break (Break, §4)

**Purpose.** 

**On screen.** 

### 14:15–14:30 · Debrief (Shareback, §4)

**Purpose.** dbt as ELT; SELECT, Jinja and YAML; views and tables; OLTP and OLAP; the commands; then DAGs, operators, blueprints and task groups.

**On screen.** Anchor › Debrief (dbt flow diagram)

**Instructor notes.**

- Follow the anchor's order; ask before telling.
- Land the 80/20 message: the contract produced most of the code.

**Say.**

- “If eighty percent of the code came from the contract, then the interview and the contract were the job.”

**Transition.** Review another pair's code.

### 14:30–14:50 · Review another pair's generated code (Challenge, §4)

**Purpose.** Trace one contract rule into code, find one assumption, propose one check and say what happens when it fails.

**On screen.** Anchor › Activity 8b card

**Instructor notes.**

- Five minutes explaining, ten reviewing, five discussing.
- Code that cannot run is still reviewable; everyone explains their own rule.

**Say.**

- “Find the line where the rule lives. Then find the assumption the rule does not mention.”

**Transition.** One correction each, then close.

### 14:50–15:00 · Corrections and closing discussion (Shareback, §4)

**Purpose.** Make one correction and share its reason; record questions for the dbt practical.

**On screen.** Anchor › Before learners leave

**Instructor notes.**

- Separate access problems from problems in the generated code when you write them up.
- Tomorrow's launch script is in the Day 3 anchor; tell learners to open challenges/v1/02-dbt-pipeline tonight if they want a head start.

**Say.**

- “Tomorrow is self-paced: the README teaches dbt as you go, and I walk the room.”

## Before learners leave

- [ ] The revised mapping and commitments, the generated dbt and Airflow project, the commands that worked and the unresolved setup issues, saved per pair.
- [ ] Each learner can locate one output table and explain one transformation in it.
- [ ] Access problems recorded separately from problems in the generated code, with an owner for each.
- [ ] Anyone still blocked on the dev container or Databricks has a platform-support contact for tonight.
