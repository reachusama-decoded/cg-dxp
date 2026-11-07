# Day 3 run sheet — dbt practical and consolidation

Instructor-only timing companion to the anchor notebook. Times follow the instructor plan; adapt them to the room and keep the sequence. The § column is the notebook section the block belongs to. Each block: purpose, what is on screen, notes, a line to say, the transition, and what to do if ahead or behind.

## Sections

1. **The dbt practical: launch, Phase 1 and the walkthrough** (09:00–11:00): Launch: the pipeline · Challenge 9: dbt practical · Walkthrough: Phase 1 on DuckDB · Break · Walkthrough: Phase 2 on DuckDB · Circulating
2. **The platform session** (11:00–13:00): Guest: the platform team (or the instructor-led version) · Lunch
3. **Complete and extend the practical** (13:00–14:30): Challenge 9 continued: Phase 2 · Stretch: macros, snapshots, incremental, unit tests · Break
4. **Consolidation** (14:30–15:00): Debrief: what did we learn? · Activity 9: test review in pairs · Close

## Timeline

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

## Blocks

### 09:00–10:00 · Challenge 9 — dbt practical: launch and first hour (Practical, §1)

**Purpose.** Launch the assigned dbt project, explain the task sequence and the checks, and get everyone building Phase 1 (sources and staging).

**On screen.** Anchor › Launch box; learners in challenges/v1/02-dbt-pipeline

**Instructor notes.**

- Ten-minute launch from the anchor: where to work, the first three commands, what a green section looks like, what reset deletes.
- Then circulate with the three-point checklist. Collect questions in the Q&A table for the recap.
- Remind people to break around 10:00.

**Say.**

- “The README teaches dbt as you go: concept, task, hint, check, a variation, then the solution. Attempt before you open the solution.”

**Transition.** Break; carry on after it.

**If ahead or behind.** Anyone who knows dbt: skip to Phase 2 and the stretch list.

### 10:00–10:15 · Break (Break, §1)

**Purpose.** 

**On screen.** 

### 10:15–11:00 · Continue dbt practical (Practical, §1)

**Purpose.** Phase 1 complete for most; Phase 2 started by some; blockers resolved; questions collected.

**On screen.** Anchor › Walkthrough cells (for support)

**Instructor notes.**

- Use the anchor's DuckDB walkthrough cells to show an expected result when someone is stuck; never type in their project.
- Access problems to the platform contact; code problems to the pair next to them first.

**Say.**

- “Could this join pass its tests and still double the reported value?”

**Transition.** At 11:00 the platform session, or the instructor-led version.

### 11:00–12:00 · Guest session: the platform (Talk, §2)

**Purpose.** Why the paved path works this way: Airflow on Astronomer, Databricks and Unity Catalog, contracts, the vended repository, compute, operations.

**On screen.** Anchor › Platform session (two diagrams, agenda, questions)

**Instructor notes.**

- If a guest comes: send them the anchor's agenda line; keep the learners' questions list ready; record answers in the Q&A table.
- If nobody comes: the anchor's instructor-led script, twenty-five minutes, then questions.

**Say.**

- “Every tool choice on the path has a reason and a trade-off. Ask about the trade-offs.”

**Transition.** Lunch.

**If ahead or behind.** A short guest session returns time to the practical.

### 12:00–13:00 · Lunch (Break, §2)

**Purpose.** 

**On screen.** 

### 13:00–14:15 · Complete and extend dbt practical (Practical, §3)

**Purpose.** Complete and explain the work; Phase 2 for those on it; stretch (macros, snapshots, incremental, unit tests) for fast finishers.

**On screen.** Anchor › Stretch section

**Instructor notes.**

- About three hours of practice across the day in total; nobody has to finish Phase 2.
- Early finishers investigate one planted error in a copied project and show the failure and the repair.

**Say.**

- “A successful build is not evidence. Show me one value you checked a different way.”

**Transition.** Break, then the recap.

### 14:15–14:30 · Break (Break, §3)

**Purpose.** 

**On screen.** 

### 14:30–14:45 · Consolidation (Debrief, §4)

**Purpose.** Ask the room what it learned and write the ten topics up; arrange tomorrow's contributions (bitemporal loading, deployment).

**On screen.** Anchor › Recap table

**Instructor notes.**

- Ask 'what did we learn?' and fill gaps from the recap table rather than lecturing.
- Recruit two volunteers for tomorrow: one with bitemporal loading in production, one with Harness access; give them the anchor's brief.

**Say.**

- “Who here has a bitemporal table in production? Would you show us tomorrow morning: the columns and one or two loading strategies, ten minutes?”

**Transition.** Pairs: swap a mapping and its test.

### 14:45–14:55 · Test review in pairs (Pair activity, §4)

**Purpose.** Exchange one mapping rule and its test; propose a wrong result and decide whether the test would catch it; agree one improvement.

**On screen.** Anchor › Activity 9 card

**Instructor notes.**

- The three wrong results: a duplicated join, a missing dated FX rate, a changed unit.

**Say.**

- “Would your test catch it? If not, write the expected failure before you write the fix.”

**Transition.** Two or three examples to the room, then close.

### 14:55–15:00 · Closing discussion (Debrief, §4)

**Purpose.** Share a missing check; save the dbt work for orchestration; confirm tomorrow's baseline.

**On screen.** Anchor › Before learners leave

**Instructor notes.**

- Completing advanced dbt is not a prerequisite for tomorrow; the Airflow challenge ships the solved dbt project.

**Say.**

- “Keep this project where it is. Tomorrow Airflow runs it.”

## Before learners leave

- [ ] The working dbt project, model and test results, one independent output check and the outstanding questions for orchestration, kept where they are.
- [ ] Each learner can trace one plain-English mapping through its model and its test.
- [ ] Two volunteers (or a guest) confirmed for tomorrow's bitemporal and deployment slots, with the brief.
- [ ] The Airflow baseline is ready: Databricks auth works, challenge 02's seeds are loaded, and Astro has been started once after setup.
