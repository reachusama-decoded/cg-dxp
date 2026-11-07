# Kafka route (optional): v2 plan (new primer, built on v1 Challenge 03)

## At a glance

| | |
|---|---|
| **v1 source** | None directly. v1 has no Kafka challenge. If kept, this optional primer **extends v1 Challenge 03**: a "feed arrived" event triggers the same `portfolio_analytics_daily` DAG learners wired in Airflow Phase 1 |
| **Recommendation** | Keep it **optional**, after Airflow Phase 1. If facilitators do not need event-driven triggering, drop the route rather than keep a disconnected toy |
| **Where learners work** | **In place, in this repository.** The broker compose file and the bridge script live in this repo (`challenges/v2/kafka/compose.yaml`, `scripts/v2_kafka_bridge.py`). The DAG is `data_products/portfolio_analytics/dags/portfolio_analytics_daily.py` in the running Astro stack. No copies, no other repos |
| **Data** | The v1 Portfolio Analytics feeds. The event names one of the four feeds declared in `challenges/v1/02-dbt-pipeline/dbt/models/sources.yml` (for example `custodian.holdings_raw`) |
| **Engine** | Databricks, through Cosmos in the Astro stack, exactly as in Airflow Phase 1 |
| **Phase 1 — Certified** | `phase-one-certified`, target **~1 h**. Event contract → broker → produce → consume and trigger the DAG → prove the run belongs to the event |
| **Phase 2 — Proficient** | `phase-two-proficient`, target **~45 min**. Replay without duplicate runs; reject a poison message without losing the good ones. Replaces the "not offered" placeholder |
| **mise** | New `mise run kafka:up`, `kafka:produce`, `kafka:consume`, `kafka:down`, plus `mise run challenge:verify kafka --phase 1\|2` |
| **Current v2 content dropped** | The separate DuckDB project and DAG copy, `/path/to/prepared/…` commands, the `.local/v2-airflow` runtime and `fixture://holdings-v1` events |

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

> In Challenge 03 your pipeline ran at a set time each morning. But what if the data arrives late, or early? Here the pipeline starts **when the data arrives**. The system that sends the data posts a short message saying "the holdings file is ready". A small program reads that message and starts your Airflow pipeline. This route is optional.
>
> The messages travel through **Kafka**, a system that keeps messages in order so programs can read them. Think of a shared notice board where every notice is numbered and nothing is taken down when someone reads it.
>
> **Phase 1 — Certified (about 1 hour).**
> - You start Kafka and post a message.
> - The reader program picks it up and starts your pipeline.
> - You prove that pipeline run belongs to your message.
>
> Passing `mise run challenge:verify kafka --phase 1` and explaining your work reaches the baseline standard.
>
> **Phase 2 — Proficient (about 45 minutes).** You make the trigger safe. The same message read twice must not start the pipeline twice, and a broken message must be set aside without stopping the good ones.
>
> **How the help works:** Kafka and the reader program are ready to use through mise commands. You edit one message file, and in Phase 2 you finish one small piece of the reader's error handling.

---

## 0b. Learning design for this route

**Where it sits:** optional, after 03 Phase 1.

**Entry check:**
1. Has `mise run challenge:verify 03 --phase 1` passed?
2. Can you say what starts a scheduled DAG run?

**Outcomes**

| Phase | By the end you can… | Evidence |
|---|---|---|
| 1 | Explain topic, partition, offset and consumer group, using offsets from your own run | §2–§3; explain-back |
| 1 | Check a message against its agreed format, and explain why unknown feeds are refused | §1 |
| 1 | Follow one message to one DAG run by its ID | §4–§5; certification task |
| 2 | Explain why the same message must not start two runs, and why a conflicting one is refused | Ch1 |
| 2 | Keep a pipeline running past a broken message | Ch2 certification task |

**Fading map**

| Stage | Sections |
|---|---|
| Worked examples | §1–§3 |
| Completion | §4–§5 |
| From scratch | Phase 1 certification task |
| Phase 2 | Ch1 guided; Ch2 from the stub's TODO only |

**Certification tasks (no solution in the learner README)**

- **Phase 1:** create `events/fx_arrived.json` from scratch for `fx_feed.fx_rates_raw`. Validate it, send it, let the reader pick it up, and prove the resulting run by its ID.
- **Phase 2:** Ch2. Finish the dead-letter handler so a broken message is set aside and the next good message still starts a run.

**Explain-back questions**

- **Phase 1:**
  - What does an offset tell you?
  - Why does the reader refuse a feed it doesn't know?
  - Is the message the data itself? Why not?
- **Phase 2:**
  - Why does the same message produce the same run ID?
  - What would happen without the dead-letter topic?

**Misconceptions to refute**

- Posting a message runs the pipeline. It only adds a numbered entry to the log.
- Reading a message removes it. §3 shows it is still there.
- Kafka guarantees each message is processed exactly once from end to end.
- A committed offset means the DAG succeeded.

**Recall prompts**

- §4 → 03 §9: what does a DAG run ID look like?
- §5 → 03 §4: what does the freshness gate check?

**Tracks**

- *Fast track:* skip §2 after its recall question.
- *Support track:* pair at §4; the third hint level gives the full mise command.

---

## 0c. Words to explain

Define each term in plain words where it first appears in the README (ground rule 9).

| Term | Plain definition to use | First used |
|---|---|---|
| event / message | A short note saying something happened, for example "the holdings file for 2026-05-20 is ready". It describes the data; it is not the data | §0 |
| Kafka / broker | The system that stores messages in order / the running Kafka server | §0, §2 |
| topic | A named stream of messages, like one notice board | §2 |
| partition | One ordered lane inside a topic. Ours has one | §2 |
| offset | A message's number in its lane: 0, 1, 2… | §2 |
| producer / consumer | The program that posts messages / the program that reads them | §3 |
| consumer group / commit | Readers that share the work / saving "I've handled up to offset N" so reading resumes there | §4 |
| payload / contract | The message's contents / the agreed fields and allowed values | §1 |
| validate | Check a message matches its contract before acting on it | §1 |
| bridge | Our reader program: it validates each message and starts the DAG | §4 |
| run ID (deterministic) | The name of a DAG run. Ours is built from the message ID, so the same message always gives the same name | §4 |
| idempotent | Doing it twice has the same effect as doing it once | P2 Ch1 |
| poison message / dead-letter topic (DLQ) | A broken message that would stop the reader / a separate topic where such messages are set aside to look at later | P2 Ch2 |
| compose | Docker Compose: starts several containers from one settings file. Here it starts Kafka | §2 |

---

## 1. What current v2 got wrong for this route

- It ran a second copy of a toy DAG and a DuckDB project in a separate `.local/v2-airflow` runtime, not the course's Astro stack and `portfolio_analytics_daily`.
- Learners could not run its commands: they contained `/path/to/prepared/receipt.json` and depended on an instructor-prepared `AIRFLOW_HOME`.
- Phase 2 was a "not offered" placeholder page.

**Kept from v2:** the deterministic run ID derived from `event_id`, the rule that a conflicting payload with the same `event_id` is rejected, and offsets committed only after an accepted trigger. These are good lessons. Re-key them to real feed names.

---

## 2. The chain (shown as a mermaid diagram in the README)

`feed-arrived event` → `kafka:produce` → topic `portfolio-analytics.feed-arrived` (partition 0, offsets) → `kafka:consume` (bridge, consumer group) → `astro dev run dags trigger portfolio_analytics_daily --run-id feed_arrived__<event_id> --conf …` → freshness gate → Cosmos dbt on Databricks → `publish_to_catalog`

In the README, `<event_id>` appears only in this diagram as notation. Every command takes it from the event file.

---

## 3. Phase 1 — Certified (target ~1 h)

**Prerequisites:** Airflow Phase 1 complete; `mise run airflow:start` running; `mise run challenge:seed 02` done today, so the freshness gate passes.

| § | Section | Content | Expected evidence | Scaffold | Range (min) |
|---|---|---|---|---|---|
| — | Environment waits (broker start) | | | — | 5 |
| 1 | The message format | Read `challenges/v2/kafka/events/holdings_arrived.json` (`event_id`, `feed: custodian.holdings_raw`, `as_of`, `row_count`). `mise run kafka:validate` shows OK; a copy with `feed: custodian.unknown` is rejected | Validator output for both | worked example | 5–10 |
| 2 | Start the broker (predict the end offset first) | `mise run kafka:up` (compose project `v2-kafka`; waits until ready; creates the topic) | Topic details: 1 partition, end offset 0 | worked example | 5–10 |
| 3 | Post a message | `mise run kafka:produce`, then read it twice and see it is still there | Delivery report: partition 0, offset 0 | worked example | 5 |
| 4 | Read it and start the DAG | `mise run kafka:consume`, which validates, starts the DAG with the run ID built from the message, and commits the offset | Bridge log line with the run ID; the run appears in the Airflow UI | completion | 10–15 |
| 5 | Prove the run belongs to the message | `astro dev run dags list-runs portfolio_analytics_daily` shows the run ID; the run's settings contain the message; all tasks succeed | Run ID matches `feed_arrived__` + `event_id`; task states table | completion | 10 |
| Cert | `fx_arrived.json` from scratch, followed to its run | See §0b | Run ID and task states | none | 10 |
| — | Explain-back + check yourself | | | — | 5 |
| | **Typical total** | | | | **~60** |

## 4. Phase 2 — Proficient (target ~45 min)

| Ch | Content | Expected evidence | Scaffold | Range (min) |
|---|---|---|---|---|
| 1 | **Replay safely.** Send the same message again: the reader finds the existing run with identical settings, does not start another, and commits. Then send the same `event_id` with a different `row_count`: the reader refuses it and leaves the offset uncommitted | One DAG run, not two; the conflict log line; the consumer group's offset before and after | guided | 15–20 |
| 2 (cert) | **Broken message.** Send a malformed message between two good ones. Finish the TODO in the reader's error handler so the broken message goes to `portfolio-analytics.feed-arrived.dlq` and reading continues | Two DAG runs for the good messages; one record on the dead-letter topic | stub's TODO only | 20–25 |
| — | Explain-back + check yourself | | — | 5 |
| | **Typical total** | | | **~45** |

`mise run kafka:down` stops only the `v2-kafka` compose project. It never runs a global prune.

## 5. Starter code: no placeholders

- `events/holdings_arrived.json` uses a real feed name, a real `as_of` date in the seeded data, and the `row_count` from `mise run challenge:dbt 02 -- show --inline "select count(*) from {{ source('custodian','holdings_raw') }}"`.
- `scripts/v2_kafka_bridge.py`: retarget from the toy DAG to `portfolio_analytics_daily` via `astro dev run`. The Phase 2 DLQ handler ships as working code that logs and skips, with a TODO to produce to the DLQ topic.

## 6. mise (new tasks)

| Task | Does |
|---|---|
| `kafka:up` / `kafka:down` | Start or stop `challenges/v2/kafka/compose.yaml` as project `v2-kafka`, and create the topics |
| `kafka:validate` / `kafka:produce` / `kafka:consume` | Run the in-repo bridge with the repo's Python. The event file defaults to `challenges/v2/kafka/events/holdings_arrived.json` |
| `challenge:verify kafka --phase 1\|2` | Checks the run ID, task states, offsets and DLQ record |

## 7. Retire from current v2

- `challenges/v2/kafka/phase-*/starter/**` (DuckDB project, `pipeline.py` copy, `fixture://` events) and `challenges/v2-solutions/kafka/**`.
- The `.local/v2-airflow` runtime and Kafka paths in `scripts/challenge-v2.py`.
- Update the `validate_event` tests in `tests/challenges/offline/test_v2_contracts.py` to the feed-name contract.

## 8. Done when

- [ ] The event triggers the learner's own `portfolio_analytics_daily` run in the Astro stack, with dbt on Databricks.
- [ ] Phase 1 — Certified = 5 sections, piloted at about 1 h. Phase 2 — Proficient = 2 challenges, piloted at about 45 min. No placeholder page.
- [ ] Every command is a mise task with no paths to fill in.
- [ ] §0b is implemented: outcomes mapped to sections and checks; certification tasks with no learner-visible solution; explain-back questions with a rubric; the fading map; a core debugging section per phase; misconceptions addressed; recall prompts; check-yourself questions; `--section N` checks; and `FACILITATOR.md`.
- [ ] A trainee run is recorded via the `challenge-trainee-runs` skill, and the pacing ranges are re-baselined from it.
