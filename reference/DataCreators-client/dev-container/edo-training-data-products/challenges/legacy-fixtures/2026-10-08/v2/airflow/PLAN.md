# Airflow route: v2 plan (uplift of v1 Challenge 03)

## At a glance

| | |
|---|---|
| **v1 source** | [v1/03-airflow-orchestration](../../v1/03-airflow-orchestration/README.md), "Orchestrate the dbt Pipeline" |
| **Target folder** | `challenges/v2/03-airflow-orchestration/` (rename of this `airflow/` folder) |
| **Data / DAG** | Same as v1: `data_products/portfolio_analytics/dags/portfolio_analytics_daily.py`, the Cosmos `DbtTaskGroup` over `data_products/portfolio_analytics/dbt/`, and the four raw feeds seeded by Challenge 02 |
| **Engine** | **Databricks only.** dbt runs through Cosmos against the learner's SQL warehouse and schema; the local Airflow is the Astro stack (`astro dev start`) |
| **Phase 1 — Certified** | `phase-one-certified`, target **2 h**. Baseline standard: v1 Phase 1 (10 sections) **plus** a failure-and-recovery drill; the learner authors three pieces instead of one |
| **Phase 2 — Proficient** | `phase-two-proficient`, target **90 min**. Advanced practitioner: v1 Phase 2 (10 challenges) **trimmed to 5** core challenges; the rest move to Stretch |
| **mise** | `mise run setup:databricks`, `mise run challenge:seed 02`, `mise run challenge:verify 03 --phase 1\|2`, `mise run challenge:reset 03 --phase 1\|2`, plus a new `mise run airflow:start` |
| **Current v2 content dropped** | The toy `prepare/build/quality/publish` DAG, the DuckDB project copy, the `dag.test()` harness in `.local/v2-airflow`, the hardcoded `v2_training_pipeline` DAG ID and the `fail-quality` marker file |

---

## Ground rules (same in every route plan)

1. **v1 is the source of truth.** Use the same data products (`portfolio_analytics`, `atlas_elt`), the same seeds and CSVs, the same model and file names, and the same Atlas framing. v2 reorganises and improves v1; it does not add new datasets, toy projects or a separate harness.
2. **Databricks is the only dbt engine.** This applies to every route that runs dbt, including Airflow and the capstone.
   - Profiles are Databricks-only and follow [portfolio_analytics/dbt/profiles.yml](../../../data_products/portfolio_analytics/dbt/profiles.yml): `DATABRICKS_HOST`, `DATABRICKS_HTTP_PATH`, `DBT_CATALOG`, `DBT_SCHEMA`, and the `DBT_ACCESS_TOKEN` that `.mise/env.sh` mints from the OAuth session.
   - Everything builds in the learner's single pre-provisioned schema (`$DBT_SCHEMA` in `$DBT_CATALOG`).
   - No DuckDB, no `dbt-duckdb`, no offline dbt mode.
3. **mise for every command; work in place.** Run `mise run setup:databricks` once, then `mise run challenge:seed|dbt|verify|reset NN`, extended with `--phase 1|2`. Learners work in this repository, in the same files v1 uses. There are no sandbox repositories, no clones elsewhere, no copied `.local/challenges-v2/` workspaces, no `python3 scripts/challenge-v2.py` and no venv activation.
4. **No placeholders.** None in starter code (`select 1 as placeholder`, "Valid starter" echo commands), in config (`'unused'`, `'must_be_provisioned'`), in commands (`<instructor-schema>`, `OWNER/…`, `/path/to/…`), or as pages ("Phase 2 — not offered").
   - Every stub is real code that runs and does part of the job, with a `TODO` stating exactly what the learner adds. v1's Docker starter is the model: a real `FROM` line plus TODOs.
   - Every value in a command comes from the environment or from another command.
5. **Phase 1 — Certified; Phase 2 — Proficient.**
   - `phase-one-certified` certifies a learner to the baseline Data Creator standard. It is the core for everyone and ends with something that works end to end.
   - `phase-two-proficient` certifies a more advanced practitioner, through a small, fixed core of harder work.
   - **Time targets:** 2 h / 90 min for the main routes (dbt, Airflow, Atlas capstone); about 1 h / 45 min for the tool primers (Docker, environment and Databricks CLI, Git, optional Kafka).
   - Remaining v1 Phase 2 challenges go to a Stretch appendix, improved but unchanged in substance. Stretch counts toward neither certification.
6. **README layout (every route).** Use `#` for the title, `##` for top-level parts and `###` for each section. Put a `---` rule between every section. Follow this order:

   ```text
   # Route title: one-line outcome
   Two or three sentences: what you build and why it matters to the data product
   ## At A Glance        main task · files you edit · provided vs you write · start / verify / reset (mise) · time · finish line
   ## The two phases     opening discussion (§0 of the route plan)
   ## Learning outcomes  3–5 per phase, and what Certified vs Proficient means (§0b)
   ## What you will build   mermaid pipeline + the expected end result
   ## Before you start   where this route sits · entry check · one ordered mise block · which directory each command runs in
   ## Phase 1 — Certified
   ### Every section has the same shape
   ### Pacing guide     ranges, an environment-waits row, typical total = phase target
   ---
   ### 1. Section title … (recall prompt · Concept · Provided / You write · … · Common mistakes; each followed by ---)
   ### Certification task   a new problem, no scaffold, no solution shown
   ### Explain-back and check yourself   3–4 explain-back questions · 3–5 self-check questions · one reflection line
   ### Phase 1 summary
   ## Phase 2 — Proficient   (same pattern)
   ## Stretch
   ## Troubleshooting    symptom → cause → fix table
   ```

   - Use tables for budgets and comparisons, and `> **Note.**` callouts for warnings.
   - Put every command and every expected output in a fenced block.
   - Put level-2 hints and solutions in `<details>`.
7. **Content standard.** This defines "substantially improved":
   - **Concept:** plain English first, then why it matters for this data product, then one concrete example from the route's own data. Define every term on first use and give one docs link. Keep it to about 150 words.
   - **Provided / You write:** every section opens with these two lines, so scaffolding is announced rather than discovered.
   - **Challenge:** names the exact file and TODO, and states the outcome as something observable.
   - **Hint:** two levels. Level 1 says where to look; level 2 gives the shape (column list, command skeleton) but not the answer.
   - **How to check:** starts with **Predict:**, a one-line expectation the learner writes before running anything. Then the exact mise or tool command and the literal expected output. An intended failure shows its exact error text under a "this failure is the goal" callout.
   - **Try a variation:** a predict-then-run twist on the same data.
   - **Common mistakes:** the two or three mistakes seen in pilot runs, inline at the end of each section. Troubleshooting keeps only environment problems.
   - **Solution:** collapsible, behind a "try it first" prompt, with two or three lines on why it works. Certification tasks have no solution in the learner README; the reference answer lives in the facilitator guide.
8. **Learning design.** These rules make the two certifications mean something.
   - **Outcomes first.** Each phase states 3–5 outcomes ("By the end you can …"). Every section and every gate check maps to an outcome (§0b).
   - **What each level certifies.**
     - *Certified:* completes the guided build and explains why it works.
     - *Proficient:* solves an unfamiliar problem with little scaffolding, chooses between options and justifies the choice.
   - **Evidence = artefact + explanation.** The gate proves the files. Certification also needs:
     - a **certification task**: a new, unscaffolded problem on the same data, with no solution in the learner README;
     - **explain-back questions**, answered to a facilitator or partner and judged with the rubric in the facilitator guide.
   - **Fade the scaffolding.**
     - Phase 1 moves from worked example → completion problem (a stub with TODOs) → a file the learner creates from scratch.
     - Phase 2 starts at completion problems and ends at from-scratch work, framed as realistic requests: a bug report, a consumer request or a review comment.
   - **Debugging is core.** Each phase has at least one core section where something is broken on purpose and the learner reads the error, finds the cause and fixes it. Broken states come from a mise task (`mise run challenge:break NN --scenario …`), never from hand edits.
   - **Name the misconceptions.** Any Concept that touches a misconception listed in §0b states it and refutes it with evidence the learner sees in their own terminal.
   - **Recall before new material.** Key sections open with a one-question recall prompt that links to an earlier section or route.
   - **Fast feedback.** `mise run challenge:verify NN --section N` checks one section in under a minute and gives an actionable message. The phase gate runs all of them.
   - **Pacing guide, not a stopwatch.**
     - Budgets are ranges, with an explicit environment-waits row (warehouse start, Astro boot).
     - The typical total equals the phase target.
     - Re-baseline after pilot runs.
   - **Two tracks.**
     - *Fast track:* experienced learners skip reading-only sections once they answer that section's recall question.
     - *Support track:* a third hint level that gives the full shape, plus a suggested pairing point in each phase.
   - **Accessible visuals.** Put the diagram before the prose. Every mermaid diagram and screenshot has a one-sentence text alternative.
   - **Facilitator guide.** `FACILITATOR.md` sits beside each route README and contains timing checkpoints, likely sticking points, demo moments, the explain-back rubric and the certification-task reference answers.
   - **Course map.** Routes run 00 → Git → 01 → 02 → 03 → Kafka (optional) → 04. Each README states its prerequisites and opens with a two-question entry check.
9. **Plain language for first-time learners.** Write for a capable person meeting each idea for the first time, not for an expert.
   - **Reading level.** Concepts, Challenges and Hints aim for reading grade 9 or below (about age 14). Sentences average under 20 words. One idea per sentence, active voice, and address the reader as "you".
   - **Everyday words first, then the term.** For example: "what one row stands for, which dbt users call the **grain**". Bold a term once, where it is defined.
   - **Define every term at first use** in plain words, using the route's "Words to explain" list (§0c). Collect them in a glossary at the end of the README. Only these words need no definition: file, folder, command, terminal, table, row, column, query, CSV.
   - **Expand and explain acronyms** the first time they appear: SLA, DLQ, CTE, AUM, bps, NAV, FX, ISIN, JSON, CLI, PR, UC.
   - **Picture or example before the general rule.** Start with a two- or three-row example table, a diagram or an analogy. If you use an analogy, say where it stops being true.
   - **One new idea per section.** If a Concept runs past about 150 words or introduces more than two new terms, split the section.
   - **Why before how.** Each Concept opens with the problem the idea solves.
   - **Explain commands and errors.** The first time a command appears, a small table says what each part does. Every quoted error message is followed by one plain sentence: what it means and what to do.
   - **Rewrite dense v1 passages.** v1 is the base, but rewrite any passage that fails this rule. For example, v1 02 Phase 2 Ch1's Concept explains left joins, NULLs and `coalesce` in one 170-word paragraph; split it into three short steps with a two-row example.
   - **First-time-reader review.**
     - Before release, someone new to the tool reads the README and marks every word or sentence they had to reread or look up. Fix each mark by defining or replacing the word.
     - **(new)** `mise run challenge:lint-language NN` flags §0c terms used before their definition, unexpanded acronyms, and sentences over 30 words.

---

## 0. README opening: the two phases (draft text)

> In Challenge 02 you built tables by running dbt yourself. Real pipelines need to run on their own, on time, and tell someone when something goes wrong. **Airflow** does that job. It starts each step in the right order at the right time, and it retries or raises the alarm when a step fails.
>
> You run the Challenge 02 pipeline as a **DAG**, Airflow's name for a set of steps and the order they run in. Ours is called `portfolio_analytics_daily`. Airflow runs on your machine inside **Astro**, a packaged version of Airflow. dbt still runs the SQL on Databricks.
>
> **Phase 1 — Certified (about 2 hours).** Everyone does this phase.
> - The DAG already works. You read each part, then write three pieces yourself: when it runs, how it retries, and the order of its steps.
> - Then you run it, break it on purpose with out-of-date data, and fix it.
>
> Passing `mise run challenge:verify 03 --phase 1` and explaining your work reaches the baseline standard.
>
> **Phase 2 — Proficient (about 90 minutes)** makes the pipeline safe to run every day. You add:
> - alerts that match how serious a failure is;
> - a deadline the team can rely on;
> - an agreement with the team that sends the data;
> - a written guide for whoever is on call;
> - automatic checks on the DAG itself.
>
> **How the help works:** you edit files in `data_products/portfolio_analytics/dags/`, and everything else already works. Later tasks give you less help. Each phase ends with a problem you solve on your own.

---

## 0b. Learning design for this route

**Where it sits:** after 02, whose seeds and dbt project this route orchestrates; before Kafka and 04.

**Entry check:**
1. Has `mise run challenge:verify 02 --phase 1` passed?
2. Can you say in one sentence what `dbt build` runs?

**Scenario (opens the README):** Fund operations want `agg_fund_exposure` ready by 07:30 London time on weekdays. It must never be built on a stale custodian feed, and someone must be told when it isn't ready.

**Outcomes**

| Phase | By the end you can… | Evidence |
|---|---|---|
| 1 | Explain what Airflow, dbt and Databricks each do in one run | §1; explain-back |
| 1 | Read a DAG and its Cosmos task group in code and in the UI | §2, §5 |
| 1 | Set a schedule and a retry policy, and predict their effect | §7–§8 |
| 1 | Diagnose a failed run from the logs and recover with clear-and-rerun | §10–§11; certification task |
| 2 | Match alert tiers to business impact and wire them to the DAG | Ch1–Ch2 |
| 2 | Turn a freshness rule into a producer contract and a runbook another engineer can follow | Ch3–Ch4 |
| 2 | Protect a DAG with structural tests and triage a production failure | Ch5 certification task |

**Fading map**

| Stage | Sections |
|---|---|
| Worked example | §1 trigger the shipped DAG and watch it run |
| Reading | §2–§5 |
| Completion problems | §6 chain, §7 schedule, §8 retries (TODOs in the real DAG) |
| Debugging | §11; the certification task |
| Phase 2 | Ch1–Ch3 completion; Ch4 headings only; Ch5 from scratch |

**Certification tasks (no solution in the learner README)**

- **Phase 1:** `mise run challenge:break 03 --scenario p1-cert` introduces one undisclosed fault, drawn from three: a wrong Cosmos profile target, a dependency cycle, or the cron in UTC instead of London. Diagnose and fix it using the logs and `list-import-errors`, then write two lines: the symptom and the cause.
- **Phase 2:** Ch5, below.

**Explain-back questions**

- **Phase 1:**
  - Why is the freshness gate before the build, not after?
  - What does `catchup=False` prevent here?
  - Would retries have fixed the §11 failure? Why?
  - Where does dbt actually execute?
- **Phase 2:**
  - Why is a stale feed P2 and not P1?
  - What exactly does your SLA measure?
  - What can structural tests never catch?

**Misconceptions to refute**

- Retries fix bad data. §11 shows they don't.
- `start_date` is when the first run happens. A run fires at the end of its interval.
- Parsing the DAG file runs the pipeline.
- Airflow transforms the data.
- A green DAG means correct data.

**Recall prompts**

- §3 → 02 §2: where does the dbt profile get its token?
- §4 → 02 §3: the freshness thresholds
- Phase 2 Ch3 → the Git route freshness change

**Tracks**

- *Fast track:* §2 can be skipped once the recall question is answered.
- *Support track:* pair at §5 and §11; the third hint level gives the full `>>` chain shape.

---

## 0c. Words to explain

Define each term in plain words where it first appears in the README (ground rule 9).

| Term | Plain definition to use | First used |
|---|---|---|
| orchestration | Starting each step of a pipeline at the right time and in the right order, and handling failures | §1 |
| DAG | A set of steps and the order they run in. It stands for *directed acyclic graph*: the arrows point one way and never loop back | §1 |
| task | One step in a DAG, for example "check the data is fresh" | §2 |
| operator | The kind of task, for example one that runs Python, or one that only marks a point in the flow | §2 |
| catchup | Whether Airflow runs every missed past date when you switch a DAG on | §2 |
| Astro | Astronomer's packaged Airflow, running in containers on your machine | Before you start |
| Cosmos | A library that turns each dbt model into its own Airflow task | §5 |
| task group | Several tasks shown as one box on the Airflow screen | §5 |
| schedule / cron | When the DAG runs. Cron is a short code for times: `0 6 * * 1-5` means 06:00 on weekdays | §7 |
| retry / backoff | Trying a failed task again. Backoff means waiting longer before each new try | §8 |
| DAG run | One run of the whole DAG, for one date | §9 |
| clear | Telling Airflow to run a task again | §10 |
| `upstream_failed` | A task that did not run because a step before it failed | §11 |
| callback | Code that runs by itself when a task succeeds or fails, for example to send an alert | P2 Ch1 |
| on-call | The person responsible for answering alerts right now | P2 Ch1 |
| P1 / P2 / P3 | Alert priority. P1 = wake someone now, P2 = tell the team today, P3 = log a ticket | P2 Ch1 |
| SLA | Service level agreement: the deadline we promise, here "ready by 07:30" | P2 Ch2 |
| producer contract | The written agreement with the team that sends a feed: how fresh it will be, and what happens if it is late | P2 Ch3 |
| runbook | A step-by-step guide for fixing a known problem | P2 Ch4 |

---

## 1. What current v2 got wrong for this route

- It abandoned the v1 `portfolio_analytics_daily` DAG, Cosmos and the Astro stack in favour of a 4-task toy DAG running dbt on DuckDB through `subprocess`. Learners no longer orchestrate the pipeline they built in Challenge 02.
- The Phase 1 starter was a 4-line placeholder (`describe()` returning "Valid starter…"), while the task asked for a full DAG from scratch.
- It dropped v1's mermaid pipeline, cold-start troubleshooting, `list-import-errors` guidance and the operability content (alerting, SLA, runbook, structural tests).

---

## 2. Phase map: v1 → v2

| v1 | v2 | Change |
|---|---|---|
| P1 §1 Why orchestration | P1 §1 | **Opens hands-on:** trigger the shipped DAG once and watch the Grid view, then explain why orchestration matters |
| P1 §2 Anatomy of a DAG | P1 §2 | Add an annotated table of every `DAG(...)` argument used by the stub |
| P1 §3 Connect to Databricks (`dbt debug`) | P1 §3 | Run as `mise run challenge:dbt 03 -- debug`; add the three-step auth check |
| P1 §4 Freshness gate | P1 §4 | — |
| P1 §5 Cosmos `DbtTaskGroup` | P1 §5 | Add a screenshot or description of the rendered task group in the Graph view |
| P1 §6 Wire the dependency chain | P1 §6 | Still authored |
| P1 §7 Scheduling | P1 §7 | **Now authored**: the learner sets the timezone-aware cron (pre-built in v1) |
| P1 §8 Retries and backoff | P1 §8 | **Now authored**: the learner sets `retries`, `retry_delay`, `retry_exponential_backoff` in `default_args` |
| P1 §9 First full run | P1 §9 | — |
| P1 §10 Reading logs and re-running | P1 §10 | — |
| — | **P1 §11 (new): Break it and recover** | Re-seed with a stale `_extracted_at`, watch the freshness gate fail and downstream tasks go `upstream_failed`, re-seed fresh, clear and re-run. Same feeds and gate, no new data |
| P2 Ch1–3 Alert transport + tiered alerting P1/P2/P3 | P2 Ch1 (merged) | One challenge: `send_alert` and the tier callbacks |
| P2 Ch4 Wire callbacks + SLA | P2 Ch2 | — |
| P2 Ch5 Freshness gate as a contract | P2 Ch3 | — |
| P2 Ch6 Monitoring config + Ch7 Runbook | P2 Ch4 (merged) | Runbook written from the §11 drill the learner already performed |
| P2 Ch8 Structural tests for the DAG | P2 Ch5 | Its passing run is the Phase 2 gate, together with the v1 Ch10 production checklist |
| P2 Ch7 Consumer guide | Stretch | — |
| P2 Ch9 `DatabricksSubmitRunOperator` variant | Stretch | — |
| P2 Ch10 Capstone production DAG | Folded into the Phase 2 gate | The checklist becomes the Phase 2 completion section |

---

## 3. Phase 1 — Certified (target 2 h): improvements

| § | Section | Scaffold | Range (min) |
|---|---|---|---|
| — | Environment waits (Astro boot, first Cosmos parse) | — | 5–10 |
| 1 | Trigger the shipped DAG once, then: why orchestration | worked example | 10 |
| 2 | Anatomy of a DAG | reading | 5–10 |
| 3 | Connect to Databricks | run | 5–10 |
| 4 | Freshness gate (predict: what happens on a stale feed?) | reading | 10–15 |
| 5 | Cosmos `DbtTaskGroup` | reading | 10–15 |
| 6 | Wire the chain | completion | 10 |
| 7 | Scheduling | completion | 5–10 |
| 8 | Retries and backoff | completion | 5–10 |
| 9 | First full run (predict the task order first) | run | 10 |
| 10 | Logs and re-running | run | 5–10 |
| 11 | Break it and recover | debugging | 10 |
| Cert | Diagnose an undisclosed fault | none | 10 |
| — | Explain-back + check yourself | — | 5 |
| | **Typical total** | | **~120** |

- **At A Glance:** list the three TODOs (schedule, retries, chain), `mise run airflow:start`, the Airflow UI URL that `astro` prints, the verify command, and the finish line.
- **Prerequisites as one ordered block:** `mise run setup:databricks` → `mise run challenge:seed 02` → `mise run airflow:start`. Keep v1's "start it *after* setup" warning and the empty-catalog symptom box verbatim; they are good.
- **Expected outputs:**
  - `astro dev run dags list-import-errors` → `No data found`.
  - Task-state table after §9: all success.
  - Task-state table after §11 failure: `source_freshness_check` failed, `dbt_pipeline` and `publish_to_catalog` `upstream_failed`.
  - Log excerpt for the freshness failure.
- **Hints:** two levels. Level 2 gives the exact `>>` chain shape and the `default_args` keys.
- **Variations:** keep v1's. Add one for §7: change the cron to run on weekdays only and read `next_dagrun` in the UI.
- **Phase 1 Summary:** keep v1's.

## 4. Phase 2 — Proficient (target 90 min)

| Ch | Framed as | Content | Scaffold | Check | Range (min) |
|---|---|---|---|---|---|
| 1 | Review comment: "on-call can't tell a P1 from a P3" | Vendor-neutral `send_alert` + P1/P2/P3 tier callbacks | completion | Credentials unset → expected log-line fallback for each tier | 15–20 |
| 2 | Consumer request: "tell us if it isn't ready by 07:30" | Wire callbacks + `sla=timedelta(minutes=90)` into the DAG | completion | DAG-load check passes; callbacks visible on tasks | 10–15 |
| 3 | Producer meeting: agree freshness thresholds | `warn_after` / `error_after` as a contract in `sources.yml` | completion | `dbt source freshness` output for fresh and stale feeds | 10–15 |
| 4 | Handover: "write it down for the next on-call" | Monitoring config + runbook written from the §11 drill | headings only | Runbook names the symptom, cause, fix and rerun command actually used | 10–15 |
| 5 (cert) | Production-readiness review | Structural tests written in an empty test module, then triage of `mise run challenge:break 03 --scenario p2-cert` using your own runbook | none | `mise run challenge:verify 03 --phase 2` → PASS; triage note judged against the rubric | 20–25 |
| — | Explain-back + check yourself | | | | 5 |
| | **Typical total** | | | | **~90** |

## 5. Stretch appendix

- v1 Ch9: the paved-path `DatabricksSubmitRunOperator` variant (`databricks_submit_run_dag.py`).
- v1 Ch7: the consumer onboarding guide.

---

## 6. Starter code: no placeholders

- **`stubs/dags/portfolio_analytics_daily.py`:** stays the complete, parseable v1 DAG. The pieces the learner authors are written as real working defaults plus a TODO, for example:
  - `schedule=None  # TODO §7: run 06:00 Europe/London on weekdays`
  - `default_args={"retries": 0}  # TODO §8: add retries, retry_delay, exponential backoff`
  - The chain TODO from v1.

  The DAG imports and runs manually before the learner touches it.
- **`stubs/dags/callbacks.py`:** remove "placeholders; real values come from the MDS". Use the real training values, or read them from Airflow Variables set by `mise run setup:airflow-settings`.
- **Runbook, monitoring and consumer-guide stubs:** pre-filled headings with one worked row each, not empty templates.

## 7. mise

| Learner action | Command |
|---|---|
| Auth (before Astro) | `mise run setup:databricks` |
| Raw feeds | `mise run challenge:seed 02` |
| **(new)** Start Airflow | `mise run airflow:start`: checks `DBT_CATALOG` is set, runs `astro dev start --wait 5m`, then `astro dev run dags list-import-errors` |
| dbt connection check | `mise run challenge:dbt 03 -- debug` |
| Phase gate | `mise run challenge:verify 03 --phase 1` / `--phase 2` |
| One section | `mise run challenge:verify 03 --section 7` |
| **(new)** Deliberate faults | `mise run challenge:break 03 --scenario stale-feed\|p1-cert\|p2-cert` applies a known broken state; `mise run challenge:reset 03 --phase 1` undoes it |
| Start a phase over | `mise run challenge:reset 03 --phase 1` |

## 8. Retire from current v2

- `challenges/v2/airflow/phase-*/starter/**` (toy `pipeline.py`, DuckDB project).
- `challenges/v2-solutions/airflow/**`.
- The Airflow paths in `scripts/challenge-v2.py`, and the `.local/v2-airflow` venv in `scripts/setup-v2-tools.sh`.
- Update `tests/challenges/offline/test_v2_contracts.py` to the new layout.

## 9. Done when

- [ ] Same DAG, Cosmos group, feeds and Astro workflow as v1 03, running dbt on Databricks.
- [ ] Phase 1 — Certified = 11 sections with three authored pieces, piloted at about 2 h. Phase 2 — Proficient = 5 challenges, piloted at about 90 min. Stretch holds Ch7 consumer guide and Ch9.
- [ ] No placeholder text or values in any stub, callback or command.
- [ ] Expected outputs for parse, success run, failure drill and recovery.
- [ ] All commands are mise or `astro` launched after `mise run airflow:start`; gates pass on the solution and fail clearly on the stubs.
- [ ] §0b is implemented: outcomes mapped to sections and checks; certification tasks with no learner-visible solution; explain-back questions with a rubric; the fading map; a core debugging section per phase; misconceptions addressed; recall prompts; check-yourself questions; `--section N` checks; and `FACILITATOR.md`.
- [ ] A trainee run is recorded via the `challenge-trainee-runs` skill, and the pacing ranges are re-baselined from it.
