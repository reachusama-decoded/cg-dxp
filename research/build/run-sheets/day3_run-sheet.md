# Day 3 run sheet — dbt practical and consolidation

[Data Creators › Day 3 — run sheet for instructors]{.breadcrumb}

Instructor-only companion to the anchor notebook, in the notebook's order: the same numbered sections and labelled parts, each with its time, purpose, what is on screen, what to say, what to ask at the whiteboard (with the answers rooms give and what to add), the demo steps with their coaching, fallbacks, the transition and what to do if ahead or behind. Keep the notebook on the projector and this beside it. Times follow the instructor plan; adapt them to the room and keep the sequence.

## Before the day

- Section 1 builds a small dbt project from two CSVs in `demos/price_sheet/`, one cell at a time; its first cell resets the folder. Run the section once before the room arrives.
- The walkthrough cells run the same project as the learners' challenge, on DuckDB in `demos/portfolio_analytics/`. Run `bash demos/portfolio_analytics/demo.sh stretch` once before the day; the cells then rebuild pieces on demand.

## Sections

| # | Section | Time | What happens |
|---|---|---|---|
| 1 | dbt from zero: one transformation through the whole life cycle | 09:00–09:50 | Recap: yesterday's platform in four pictures · Demo: what dbt is for, why use it, then the build: project, profile, seeds, source, model, Jinja, ref, tests, build, docs |
| 2 | The dbt practical: launch, Phase 1 and the walkthrough | 09:50–13:00 | Launch: the pipeline · Challenge 9: dbt practical · Walkthrough: Phase 1 on DuckDB · Break · Walkthrough: Phase 2 on DuckDB · Circulating: Phase 2 to lunch · Lunch |
| 3 | Advanced dbt, then complete and extend the practical | 13:00–14:20 | Demo: a loop, a macro, a custom test, snapshot, incremental, unit test · Challenge 9 continued: Phase 2 and the stretch · Break |
| 4 | Consolidation | 14:20–15:00 | Activity 9b: second look at yesterday's AI-generated dbt · Debrief: what did we learn? · Activity 9: test review in pairs · Close |

## Day at a glance

| § | Time | Block | Type | On screen |
|---|---|---|---|---|
| 1 | 09:00–09:10 | Recap: yesterday's platform in four pictures | Recap | Anchor › section 1, Recap (four Day 2 diagrams) |
| 1 | 09:10–09:50 | dbt from zero: one transformation through the whole life cycle | Demo | Anchor › section 1, top to bottom (demos/price_sheet) |
| 2 | 09:50–10:00 | Challenge 9 — dbt practical: launch and first sections | Practical | Anchor › Launch box; learners in challenges/v1/02-dbt-pipeline |
| 2 | 10:00–10:15 | Break | Break |  |
| 2 | 10:15–11:00 | Continue dbt practical | Practical | Anchor › Walkthrough cells (for support) |
| 2 | 11:00–12:00 | Continue dbt practical: Phase 2 to lunch | Practical | Anchor › Circulation checklist and symptom table; learners in challenges/v1/02-dbt-pipeline |
| 2 | 12:00–13:00 | Lunch | Break |  |
| 3 | 13:00–13:25 | Advanced dbt: a loop, a macro, a custom test, snapshot, incremental, unit test | Demo | Anchor › section 3 demo cells (demos/price_sheet, then demos/portfolio_analytics) |
| 3 | 13:25–14:05 | Complete and extend dbt practical | Practical | Anchor › Launch box and walkthrough cells; learners in challenges/v1/02-dbt-pipeline |
| 3 | 14:05–14:20 | Break | Break |  |
| 4 | 14:20–14:35 | Second look at yesterday's AI-generated dbt | Pair activity | Anchor › Activity 9b card; learners in the project Copilot and Catalyst generated on Day 2 |
| 4 | 14:35–14:45 | Consolidation | Debrief | Anchor › Recap table |
| 4 | 14:45–14:55 | Test review in pairs | Pair activity | Anchor › Activity 9 card |
| 4 | 14:55–15:00 | Closing discussion | Debrief | Anchor › Before learners leave |

## Timeline

### 1. dbt from zero: one transformation through the whole life cycle

Recap: yesterday's platform in four pictures · Demo: what dbt is for, why use it, then the build: project, profile, seeds, source, model, Jinja, ref, tests, build, docs

#### 09:00 · 10 min · Explain — Recap — yesterday's platform in four pictures

**Purpose.** Put everyone on the same page before dbt: where the tables live, what runs the SQL, and which box of the tools picture today zooms into.

**Instructor notes.**

- Ten minutes, four pictures from Day 2, two or three lines each. Ask one question per picture and let the room answer; do not re-teach.
- End on the tools picture with a finger on the dbt box: today is that box, tomorrow is the Airflow box above it.
- Anyone who missed Day 2: point them at the Day 2 anchor's section 3 for the full version.

**Say.**

- “One line each: what is a lakehouse, what does Databricks do with your SQL, what is a Delta table?”
- “dbt holds no data and does no computing. It sends SQL; everything on these pictures is what receives it.”

**Transition.** So what is in a dbt project? Two CSVs and an empty folder.

**Adapt.** Short of time: the under-the-hood picture and the tools picture only.

**Assessment.** Anchor › section 1, Recap (four Day 2 diagrams)

#### 09:10 · 40 min · Instructor-led demo — Demo — one price sheet, from two raw files to a tested, documented table

**Purpose.** Show every kind of file in a dbt project being written and run once, on a small example, so the challenge's tasks are recognisable: project and profile, seeds, a source, a model, Jinja, ref, materialisation, tests failing and fixed, build, docs.

**Instructor notes.**

- Present from the notebook; no whiteboard. The flow is: what dbt is for (one picture), why use it (the same transformation as a hand-run script that is silently wrong, then the without-and-with table), the path (eight steps on one picture), then the build. About five minutes for what and why, thirty for the steps, five for docs and the map to the challenge.
- In the build, each cell writes one file (%%writefile) or runs one command. Read the file, ask the room to predict the output, run it.
- Learners do not run the demo: it is DuckDB on your laptop, and their hands-on is the challenge on Databricks. The 'Where things run today' table says so; point at it once before Step 1.
- About four minutes a step. Steps 5 and 6 (two tests fail on the HSBC rows, one line fixes it, the build goes green) are the point: never skip them.
- Step 4 has a view-or-table beat: the models block of dbt_project.yml sets it per folder (staging and intermediate views, marts tables, as in the challenge), then config() in one model overrides it and is taken out again. It is challenge S6 in two minutes.
- At Step 3, spend two minutes on the Jinja picture: learners meet source(), ref() and config() in the first hour of the challenge. Loops and macros wait until 13:00.
- Run the section once before the room arrives so dbt's first-run delay is gone; the first cell resets the folder each time.

**Say.**

- “This script ran without an error and three prices are wrong. The SQL is the easy part; dbt is for everything around the SQL.”
- “You write a SELECT. dbt writes the CREATE, works out the order, and checks the result.”
- “The run was green and three prices were missing. A successful run says the SQL executed, not that the answer is right.”
- “A test is only a query for the rows that break a rule. No rows, it passes.”

**Demo — dbt from zero, eight steps.** A project that starts as two CSVs in `demos/price_sheet/seeds/`; each cell writes one file or runs one command.

1. Read each file aloud before running the command that uses it; ask the room to predict the output.
2. Steps 5 and 6 are the point of the demo: two tests fail on real rows, one line fixes the model, the build goes green. Do not skip them.
3. Step 3's compiled SQL is the Jinja explanation: curly braces in, plain SQL out. Learners meet source(), ref() and config() within the first hour of the challenge.
4. `demos/price_sheet/README.md` lists every step, file and expected result; `bash demos/price_sheet/reset.sh` starts again.

**Transition.** The same kinds of file, more of them: the Portfolio Analytics challenge.

**Adapt.** Behind at 09:40: skip Step 7 (the singular test) and say it is the pattern of C6. Ahead: open the docs site and click through the lineage graph.

**Assessment.** Anchor › section 1, top to bottom (demos/price_sheet)

### 2. The dbt practical: launch, Phase 1 and the walkthrough

Launch: the pipeline · Challenge 9: dbt practical · Walkthrough: Phase 1 on DuckDB · Break · Walkthrough: Phase 2 on DuckDB · Circulating: Phase 2 to lunch · Lunch

#### 09:50 · 5 min · Explain — Launch — the pipeline you will build today

**Purpose.** Launch the assigned dbt project, explain the task sequence and the checks, and get everyone into Phase 1 (sources and staging) before the break.

**Instructor notes.**

- Five-minute launch from the anchor: where to work, the first three commands, what a green section looks like, what reset deletes.
- Then circulate with the three-point checklist. Collect questions in the Q&A table for the recap.
- Break at 10:00; most will be in S1 or S2.

**Say.**

- “The README teaches dbt as you go: concept, task, hint, check, a variation, then the solution. Attempt before you open the solution.”

**Assessment.** Anchor › Launch box; learners in challenges/v1/02-dbt-pipeline

#### 09:55 · 5 min · Independent or pairs work — Challenge 9 — dbt practical: Phase 1 first

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

**Assessment.** Anchor › Launch box; learners in challenges/v1/02-dbt-pipeline

#### 10:00 · 15 min · Break — Break, back at 10:15

#### 10:15 · 45 min · Instructor-led demo — Walkthrough — Phase 2 on DuckDB: intermediate, marts, tests, docs

**Purpose.** Phase 1 complete for most; Phase 2 started by some; blockers resolved; questions collected.

**Instructor notes.**

- Use the anchor's DuckDB walkthrough cells to show an expected result when someone is stuck; never type in their project.
- Access problems to the platform contact; code problems to the pair next to them first.

**Say.**

- “Could this join pass its tests and still double the reported value?”

**Transition.** At 11:00 the practical carries on to lunch.

**Assessment.** Anchor › Walkthrough cells (for support)

#### 11:00 · 60 min · Independent or pairs work — Circulating — Phase 2 to lunch: three questions per learner, and the symptom table

**Purpose.** Phase 1 complete for everyone; Phase 2 under way for most; each learner asked the three circulation questions once before lunch.

**Instructor notes.**

- No platform session this week: its content (Airflow at CG, Unity Catalog and the three catalog types, contracts, the vended repository) was covered on Day 2, so the hour goes to the practical.
- Walk the room with the three-point checklist; use the symptom table for the stalls; keep adding to the Q&A table for the recap.
- Platform questions that come up: answer from Day 2's platform section, or log them in the Q&A table for the platform team.

**Say.**

- “Show me the grain of this model, the key on the right-hand side of the join, and what happens to a row with no match.”

**Transition.** Lunch.

**Adapt.** Anyone still in Phase 1 at 11:30: pair them with a neighbour who has finished S7.

**Assessment.** Anchor › Circulation checklist and symptom table; learners in challenges/v1/02-dbt-pipeline

#### 12:00 · 60 min · Break — Lunch, back at 13:00

### 3. Advanced dbt, then complete and extend the practical

Demo: a loop, a macro, a custom test, snapshot, incremental, unit test · Challenge 9 continued: Phase 2 and the stretch · Break

#### 13:00 · 25 min · Instructor-led demo — Demo — Jinja that writes SQL: a loop, a macro, then the production pieces

**Purpose.** Show what Jinja does beyond filling in names, and the pieces a production project adds, so learners recognise them in the vended project and in tomorrow's bitemporal macro.

**Instructor notes.**

- Two cells on this morning's price sheet (a for loop, a macro), then four on the Portfolio Analytics copy (dispatching macro and generic test, snapshot, incremental, unit test).
- After each cell show the compiled SQL: the lesson is that Jinja runs at compile time and the warehouse sees plain SQL.
- None of this is needed to finish the challenge; say so, so nobody abandons Phase 2 for it.

**Say.**

- “A macro is a function that returns SQL text. If you have pasted the same expression into three models, it wants to be a macro.”
- “A snapshot keeps the history of rows that change; an incremental model avoids rebuilding rows that do not.”

**Transition.** Back to the practical: Phase 2, then your choice of stretch.

**Adapt.** Short of time: the loop, the macro and the snapshot; point at the other cells.

**Assessment.** Anchor › section 3 demo cells (demos/price_sheet, then demos/portfolio_analytics)

#### 13:25 · 40 min · Independent or pairs work — Challenge 9 continued — Phase 2, then your choice of stretch

**Purpose.** Complete and explain the work; Phase 2 for those on it; stretch (macros, snapshots, incremental, unit tests) for fast finishers.

**Instructor notes.**

- About three and a half hours of practice across the day in total; nobody has to finish Phase 2.
- Early finishers investigate one planted error in a copied project and show the failure and the repair.

**Say.**

- “A successful build is not evidence. Show me one value you checked a different way.”

**Say.**

- “Carry on where you stopped. Phase 2 first; nobody has to finish it.”
- “Finished C10? Ask Copilot to add one of the pieces you just saw to your project: a unit test for stg_holdings is the quickest.”

**Transition.** Break, then the recap.

**Assessment.** Anchor › Launch box and walkthrough cells; learners in challenges/v1/02-dbt-pipeline

#### 14:05 · 15 min · Break — Break, back at 14:20

### 4. Consolidation

Activity 9b: second look at yesterday's AI-generated dbt · Debrief: what did we learn? · Activity 9: test review in pairs · Close

#### 14:20 · 15 min · Independent or pairs work — Activity 9b — second look at yesterday's AI-generated dbt

**Purpose.** Learners reopen the dbt project they generated yesterday, name two things in it they could not judge then, assess it now that they know dbt, and prompt Copilot again to fix one thing they caught.

**Instructor notes.**

- This closes the loop the room opened yesterday: 'do we trust it, review all of it, or review some of it?' The answer the activity gives is an order to review in: sources, staging, joins, tests, then anything nobody asked for.
- Yesterday some projects did not finish generating. Those learners pair with a neighbour whose project did, or review the Day 2 example in courseware/day2-platform/demos/contract-to-code/eod_prices.
- Two minutes to write the two things down, eight to review and re-prompt in pairs, five of shareback: two or three pairs give what they caught, the prompt they wrote and whether the fix held. Things still not judged go in the Q&A table.

**Say.**

- “Think back to yesterday afternoon. Write down two things in that project you could not judge. Can you judge them now?”
- “Yesterday your prompt was: build me a project. Today it can be: the join in this model drops rows with no FX rate; keep them and add a not_null test. That is the difference knowing dbt makes.”
- “You do not review five hundred files. You review in graph order, and you start with the tests: do they guard the promises in your contract?”

**Activity 9b — Second look at yesterday's AI-generated dbt.** Pairs, 15 min; the card is in `activities/`.

**Transition.** From what you caught to what we learned today.

**Adapt.** Short of time: pairs check only their two things and the tests, and write the prompt without running it.

**Assessment.** Anchor › Activity 9b card; learners in the project Copilot and Catalyst generated on Day 2

#### 14:35 · 10 min · Feedback and discussion — Debrief — what did we learn?

**Purpose.** Ask the room what it learned and fill gaps from the ten topics; arrange tomorrow's contributions (bitemporal loading, deployment).

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

**Assessment.** Anchor › Recap table

#### 14:45 · 10 min · Independent or pairs work — Activity 9 — test review in pairs

**Purpose.** Exchange one mapping rule and its test; propose a wrong result and decide whether the test would catch it; agree one improvement.

**Instructor notes.**

- The three wrong results: a duplicated join, a missing dated FX rate, a changed unit.

**Say.**

- “Would your test catch it? If not, write the expected failure before you write the fix.”

**Activity 9 — Test review in pairs.** Pairs, 10 min; the card is in `activities/`.

**Transition.** Two or three examples to the room, then close.

**Assessment.** Anchor › Activity 9 card

#### 14:55 · 5 min · Feedback and discussion — Close — closing discussion

**Purpose.** Share a missing check; save the dbt work for orchestration; confirm tomorrow's baseline.

**Instructor notes.**

- Completing advanced dbt is not a prerequisite for tomorrow; the Airflow challenge ships the solved dbt project.

**Say.**

- “Keep this project where it is. Tomorrow Airflow runs it.”

**Say.**

- “Two or three examples to the room: the wrong result, whether the test caught it, the improvement.”
- “Save the project where it is; tomorrow Airflow runs it. Completing Phase 2 is not a prerequisite for tomorrow: the Airflow challenge ships the solved dbt project.”

**Assessment.** Anchor › Before learners leave

## Before learners leave

- [ ] Two things each learner could not judge in yesterday's generated project, marked as judged or still open; one thing they caught, and the prompt that fixed it.
- [ ] The working dbt project, model and test results, one independent output check and the outstanding questions for orchestration, kept where they are.
- [ ] Each learner can trace one plain-English mapping through its model and its test.
- [ ] Two volunteers (or a guest) confirmed for tomorrow's bitemporal and deployment slots, with the brief.
- [ ] The Airflow baseline is ready: Databricks auth works, challenge 02's seeds are loaded, and Astro has been started once after setup.
