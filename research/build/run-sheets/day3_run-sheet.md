# Day 3 run sheet — dbt practical and consolidation

[Data Creators › Day 3 — run sheet for instructors]{.breadcrumb}

Instructor-only companion to the anchor notebook, in the notebook's order: the same numbered sections and labelled parts, each with its time, purpose, what is on screen, what to say, what to ask at the whiteboard (with the answers rooms give and what to add), the demo steps with their coaching, fallbacks, the transition and what to do if ahead or behind. Keep the notebook on the projector and this beside it. Times follow the instructor plan; adapt them to the room and keep the sequence.

## Before the day

- The walkthrough cells run the same project as the learners' challenge, on DuckDB in `demos/portfolio_analytics/`. Run `bash demos/portfolio_analytics/demo.sh stretch` once before the day; the cells then rebuild pieces on demand.

## Sections

| # | Section | Time | What happens |
|---|---|---|---|
| 1 | The dbt practical: launch, Phase 1 and the walkthrough | 09:00–11:00 | Launch: the pipeline · Challenge 9: dbt practical · Walkthrough: Phase 1 on DuckDB · Break · Walkthrough: Phase 2 on DuckDB · Circulating |
| 2 | The platform session | 11:00–13:00 | Guest: the platform team (or the instructor-led version) · Lunch |
| 3 | Complete and extend the practical | 13:00–14:30 | Challenge 9 continued: Phase 2 · Stretch: macros, snapshots, incremental, unit tests · Break |
| 4 | Consolidation | 14:30–15:00 | Debrief: what did we learn? · Activity 9: test review in pairs · Close |

## Day at a glance

| § | Time | Block | Type | On screen |
|---|---|---|---|---|
| 1 | 09:00–10:00 | Challenge 9 — dbt practical: launch and first hour | Practical | Anchor › Launch box; learners in challenges/v1/02-dbt-pipeline |
| 1 | 10:00–10:15 | Break | Break |  |
| 1 | 10:15–11:00 | Continue dbt practical | Practical | Anchor › Walkthrough cells (for support) |
| 2 | 11:00–12:00 | Guest session: the platform | Talk | Anchor › Platform session (two diagrams, agenda, questions) |
| 2 | 12:00–13:00 | Lunch | Break |  |
| 3 | 13:00–14:15 | Complete and extend dbt practical | Practical | Anchor › Stretch section |
| 3 | 14:15–14:30 | Break | Break |  |
| 4 | 14:30–14:45 | Consolidation | Debrief | Anchor › Recap table |
| 4 | 14:45–14:55 | Test review in pairs | Pair activity | Anchor › Activity 9 card |
| 4 | 14:55–15:00 | Closing discussion | Debrief | Anchor › Before learners leave |

## Timeline

### 1. The dbt practical: launch, Phase 1 and the walkthrough

Launch: the pipeline · Challenge 9: dbt practical · Walkthrough: Phase 1 on DuckDB · Break · Walkthrough: Phase 2 on DuckDB · Circulating

#### 09:00 · 10 min · Explain — Launch — the pipeline you will build today

**Assessment.** Anchor › Launch box; learners in challenges/v1/02-dbt-pipeline

**Purpose.** Launch the assigned dbt project, explain the task sequence and the checks, and get everyone building Phase 1 (sources and staging).

**Instructor notes.**

- Ten-minute launch from the anchor: where to work, the first three commands, what a green section looks like, what reset deletes.
- Then circulate with the three-point checklist. Collect questions in the Q&A table for the recap.
- Remind people to break around 10:00.

**Say.**

- “The README teaches dbt as you go: concept, task, hint, check, a variation, then the solution. Attempt before you open the solution.”

#### 09:10 · 50 min · Independent or pairs work — Challenge 9 — dbt practical: Phase 1 first

**Assessment.** Anchor › Launch box; learners in challenges/v1/02-dbt-pipeline

**Challenge — dbt practical (challenge 02).** `challenges/v1/02-dbt-pipeline/README.md` · about 3 hours across the day.

**Say.**

- “Attempt each section before you open its solution. The solution is for comparing, not for copying.”
- “You can run the raw dbt commands from the project folder. If dbt says it cannot find your credentials, open a fresh terminal so mise loads the environment, or rerun mise run setup:databricks.”

**Walkthrough — Phase 1 on DuckDB: sources and staging.**

**Demo — the same project, on DuckDB, section by section.** The learners' challenge 02 solution ported to DuckDB in `demos/portfolio_analytics/`: one cell per README section, for "what should I see?".

1. Same model names, layers, tags and tests; the Databricks-only post-hook is a no-op macro here.
2. Use a cell when someone asks what they should see; `demos/portfolio_analytics/README.md` maps each cell to its README section.
3. Say once: the SQL is the same; only the target differs.

**Transition.** Break; carry on after it.

**Adapt.** Anyone who knows dbt: skip to Phase 2 and the stretch list.

#### 10:00 · 15 min · Break — Break, back at 10:15

#### 10:15 · 45 min · Instructor-led demo — Walkthrough — Phase 2 on DuckDB: intermediate, marts, tests, docs

**Assessment.** Anchor › Walkthrough cells (for support)

**Purpose.** Phase 1 complete for most; Phase 2 started by some; blockers resolved; questions collected.

**Instructor notes.**

- Use the anchor's DuckDB walkthrough cells to show an expected result when someone is stuck; never type in their project.
- Access problems to the platform contact; code problems to the pair next to them first.

**Say.**

- “Could this join pass its tests and still double the reported value?”

**Circulating — three questions per learner, and the symptom table.**

**Transition.** At 11:00 the platform session, or the instructor-led version.

### 2. The platform session

Guest: the platform team (or the instructor-led version) · Lunch

#### 11:00 · 60 min · Explain — Guest — the platform team, or the instructor-led version

**Assessment.** Anchor › Platform session (two diagrams, agenda, questions)

**Purpose.** Why the paved path works this way: Airflow on Astronomer, Databricks and Unity Catalog, contracts, the vended repository, compute, operations.

**Instructor notes.**

- If a guest comes: send them the anchor's agenda line; keep the learners' questions list ready; record answers in the Q&A table.
- If nobody comes: the anchor's instructor-led script, twenty-five minutes, then questions.

**Say.**

- “Every tool choice on the path has a reason and a trade-off. Ask about the trade-offs.”

**Transition.** Lunch.

**Adapt.** A short guest session returns time to the practical.

#### 12:00 · 60 min · Break — Lunch, back at 13:00

### 3. Complete and extend the practical

Challenge 9 continued: Phase 2 · Stretch: macros, snapshots, incremental, unit tests · Break

#### 13:00 · 75 min · Independent or pairs work — Challenge 9 continued — Phase 2, then the stretch: macros, snapshots, incremental, unit tests

**Assessment.** Anchor › Stretch section

**Purpose.** Complete and explain the work; Phase 2 for those on it; stretch (macros, snapshots, incremental, unit tests) for fast finishers.

**Instructor notes.**

- About three hours of practice across the day in total; nobody has to finish Phase 2.
- Early finishers investigate one planted error in a copied project and show the failure and the repair.

**Say.**

- “A successful build is not evidence. Show me one value you checked a different way.”

**Transition.** Break, then the recap.

#### 14:15 · 15 min · Break — Break, back at 14:30

### 4. Consolidation

Debrief: what did we learn? · Activity 9: test review in pairs · Close

#### 14:30 · 15 min · Feedback and discussion — Debrief — what did we learn?

**Assessment.** Anchor › Recap table

**Purpose.** Ask the room what it learned and write the ten topics up; arrange tomorrow's contributions (bitemporal loading, deployment).

**Instructor notes.**

- Ask 'what did we learn?' and fill gaps from the recap table rather than lecturing.
- Recruit two volunteers for tomorrow: one with bitemporal loading in production, one with Harness access; give them the anchor's brief.

**Say.**

- “Who here has a bitemporal table in production? Would you show us tomorrow morning: the columns and one or two loading strategies, ten minutes?”

**Ask at the whiteboard — what did we learn? (fill gaps from this list, do not lecture it).** Ask in order, write what the room says, add what is missing.

| Ask | Expect, then add |
|---|---|
| Models and conventions | Staging and integration models; CG naming (stg_, int_, fct_, agg_; on Friday src_, dom_, rpt_); the SQL behind a transformation is a SELECT dbt wraps. |
| Dependencies and change | ref() and source() build the graph; a source or schema change is visible in lineage; dbt docs show it. |
| Testing and contracts | Schema tests and singular tests are the contract's quality rules made executable; catalog information and descriptions come from the same YAML. |
| Bitemporal loading | Tomorrow morning: the columns and one or two strategies, from a volunteer or guest. Questions to carry: what is business time vs system time? what happens on a correction? |
| Deployment context | Tomorrow afternoon: Harness and CI/CD, with screenshots for anyone without access. |
| Catalyst | Generation, iteration, and the repository's data_products area where the code goes; 80 to 90% of the code from a good contract. |
| Airflow preview | YAML-configured blueprints are tomorrow's topic; today's dbt project is what they will run. |
| Execution and storage | dbt SQL runs on Databricks as Spark; files on S3 in Delta: columnar, with logs and manifests that give transactions; you can insert and delete, unlike plain Parquet. |
| Catalogue conventions | Application, domain and source-aligned catalogs; publish via the domain catalog; the Marketplace is discovery. |
| Quality and materialisation | Checks at project and model level; materialisation set per folder in dbt_project.yml or in the model file. |

**Transition.** Pairs: swap a mapping and its test.

#### 14:45 · 10 min · Independent or pairs work — Activity 9 — test review in pairs

**Assessment.** Anchor › Activity 9 card

**Purpose.** Exchange one mapping rule and its test; propose a wrong result and decide whether the test would catch it; agree one improvement.

**Instructor notes.**

- The three wrong results: a duplicated join, a missing dated FX rate, a changed unit.

**Say.**

- “Would your test catch it? If not, write the expected failure before you write the fix.”

**Activity 9 — Test review in pairs.** Pairs, 10 min; the card is in `activities/`.

**Transition.** Two or three examples to the room, then close.

#### 14:55 · 5 min · Feedback and discussion — Close — closing discussion

**Assessment.** Anchor › Before learners leave

**Purpose.** Share a missing check; save the dbt work for orchestration; confirm tomorrow's baseline.

**Instructor notes.**

- Completing advanced dbt is not a prerequisite for tomorrow; the Airflow challenge ships the solved dbt project.

**Say.**

- “Keep this project where it is. Tomorrow Airflow runs it.”

**Say.**

- “Two or three examples to the room: the wrong result, whether the test caught it, the improvement.”
- “Save the project where it is; tomorrow Airflow runs it. Completing Phase 2 is not a prerequisite for tomorrow: the Airflow challenge ships the solved dbt project.”

## Before learners leave

- [ ] The working dbt project, model and test results, one independent output check and the outstanding questions for orchestration, kept where they are.
- [ ] Each learner can trace one plain-English mapping through its model and its test.
- [ ] Two volunteers (or a guest) confirmed for tomorrow's bitemporal and deployment slots, with the brief.
- [ ] The Airflow baseline is ready: Databricks auth works, challenge 02's seeds are loaded, and Astro has been started once after setup.
