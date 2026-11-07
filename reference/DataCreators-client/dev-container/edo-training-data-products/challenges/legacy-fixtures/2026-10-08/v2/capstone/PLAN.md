# Atlas capstone route: v2 plan (uplift of v1 Challenge 04)

## At a glance

| | |
|---|---|
| **v1 source** | [v1/04-atlas-capstone](../../v1/04-atlas-capstone/README.md), "Build the Atlas ELT Data Product" |
| **Target folder** | `challenges/v2/04-atlas-capstone/` (rename of this `capstone/` folder) |
| **Framing** | **Atlas, unchanged.** The fictional wealth-management platform, its producers (Trading, Security Master, Portfolio Administration, CRM, Fund Reference), its consumers, the Data Creator certification purpose, the Plan of the Day, team roles, and the Discovery and Reverse-Mapping activity |
| **Data / product** | Same as v1: the seven seeds in `data_products/atlas_elt/seeds/` and the `data_products/atlas_elt/datasets/**` source-, domain- and consumer-aligned models |
| **Engine** | **Databricks only**, using the `atlas_elt` profile and the learner's schema |
| **Phase 1 — Certified** | `phase-one-certified`, target **2 h**. Baseline Data Creator standard: v1 Phase 1 (discovery + 8 sections) **plus** two short sections, a quality proof and "use the product" (moved forward so every team has evidence and a finding to present) |
| **Phase 2 — Proficient** | `phase-two-proficient`, target **90 min**. Certified advanced practitioner: v1 Phase 2 (14 challenges, 3+ hrs) **trimmed to 4** core challenges; the other 10 move to Stretch |
| **mise** | `mise run challenge:verify 04 --phase 1\|2` (replaces `CERT_INTEGRATION_TESTS=1 ATLAS_VERIFY_SCOPE=mvp …`), `mise run challenge:dbt 04 -- …`, `mise run challenge:reset 04 --phase 1\|2` |
| **Current v2 content dropped** | The copied DuckDB mini-project, the `prepared/` move-in step, `starter_status.sql`, and the generated task cards that dropped the Atlas brief, team activity and audiences |

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

Place this directly after v1's Purpose / Learning Outcomes / Who This Is For, before the Plan of the Day.

> **Phase 1 — Certified (about 2 hours per team).** Every team does this phase.
> - First, as a team, you work out who needs the Atlas data and what decisions they make with it.
> - Then you build the Atlas tables on Databricks in three steps: copy each source as it arrives; clean it and agree one definition for each business idea; then shape finished tables for each team that uses them.
> - You check that one important number adds up, and use your tables to answer a question from Atlas leadership.
>
> The check `mise run challenge:verify 04 --phase 1` ends with `MVP LIVE PASS`. That is your finish line.
>
> **Phase 2 — Proficient (about 90 minutes)** is for the more technical people in each team. You build:
> - richer reports;
> - a ranked list of advisors;
> - a table that adds only new data instead of rebuilding everything;
> - a regional report whose numbers must agree with the others.
>
> **Stretch** keeps the remaining v1 extensions as optional extras. The **Advanced Path** is still there for people who already build data products at work.
>
> **How the help works:** you edit only files under `data_products/atlas_elt/datasets/`. Each file you complete starts as a working query, and its `TODO` lines say what is missing. Help fades as you go. Each phase ends with a problem your team solves on its own.

---

## 0b. Learning design for this route

**Where it sits:** last.

- Technical members need 02 Phase 1; 03 Phase 1 helps with §8.
- Everyone needs 00.
- Non-technical members need no prerequisite beyond the discovery activity.

**Entry check (per team):**
1. Has at least one member passed `mise run challenge:verify 02 --phase 1`?
2. Does `mise run challenge:dbt 04 -- debug` pass?

**Scenario:** v1's Atlas brief, unchanged.

**Outcomes** (aligned to v1's Learning Outcomes)

| Phase | By the end your team can… | Evidence |
|---|---|---|
| 1 | Explain the product's consumers and the decisions it supports | Discovery worksheet; explain-back |
| 1 | Place every model in source-, domain- or consumer-aligned, and say why | §5–§7 |
| 1 | Explain a population gap (2,500 → 1,028) with an anti-join, and spot a wrong-key join | §7 debugging |
| 1 | Reconcile one number and answer a leadership question with stated caveats | §9–§10; certification task |
| 2 | Build consumer marts for a stated decision and justify ranking and incremental choices | Ch1–Ch3 |
| 2 | Reconcile across grains and defend a tolerance | Ch4 certification task |

**Bridge from Challenge 02:** after v1's "Alignment" section, add a three-column table mapping staging / intermediate / marts (02), source- / domain- / consumer-aligned (04), and bronze / silver / gold.

**Fading map**

| Stage | Sections |
|---|---|
| Worked example | §5 `src_trading__trades` shown in full |
| Completion problems | Other `src_*`; §6 `dom_*` (one validity rule worked); §7 consumer models |
| From scratch | §9 relationship test and reconciliation; the certification task |
| Phase 2 | Ch1–Ch2 completion; Ch3 `config()` block only; Ch4 from scratch |

**Certification tasks (no solution in the learner README)**

- **Phase 1:** the facilitator gives the team an unseen leadership question from `FACILITATOR.md`, for example *"Which client segment holds the most AUM, and does it reconcile to the portfolio summary?"* The team answers from the marts with the query, one reconciliation and one caveat. Every member answers at least one explain-back question.
- **Phase 2:** Ch4, below.

**Explain-back questions**

- **Phase 1:**
  - Why is a trade with `qty <= 0` excluded in domain-aligned, not source-aligned?
  - Why does `rpt_portfolio_summary` have 1,028 rows, not 2,500?
  - What does AUM mean here, and what is missing? (No FX conversion.)
  - Which consumer uses your chosen output, and for which decision?
- **Phase 2:**
  - Why `dense_rank()` and not `row_number()`?
  - Why is the incremental merge key what it is?
  - How did you choose the reconciliation tolerance?

**Misconceptions to refute**

- More rows means more complete (1,028 vs 2,500).
- `LEFT JOIN` everywhere fixes missing rows.
- AUM here is FX-converted.
- A passing relationship test means a join cannot drop rows.

**Recall prompts**

- §5 → 02 §4 (staging)
- §7 → 02 §9 (grain and fan-out)
- §8 → 03 §5 (Cosmos)

**Tracks:** keep v1's role guidance.

- Non-technical members own discovery, §1, §10 and the explain-back.
- Engineers may fast-track §1–§4.
- Support track: pair on §6; the third hint level gives the join keys.

---

## 0c. Words to explain

v1's Domain concepts and Glossary already define client, advisor, portfolio, instrument, trade, position, AUM and basis points well. Keep those definitions, move each one to where the word first appears, and add the terms below (ground rule 9).

| Term | Plain definition to use | First used |
|---|---|---|
| producer / consumer / Data Creator | Who supplies the data / who uses it / you, the team that turns one into the other | Scenario |
| STTM | Source-to-target mapping: a table showing where each output column comes from and how it is changed | Discovery |
| source-, domain-, consumer-aligned | Three steps. A faithful copy of each source; a cleaned version with one agreed definition per business idea; tables shaped for one team's questions | Alignment |
| seed | A CSV file that dbt loads into a table | §4 |
| grain | What one row stands for | §6 |
| valid trade | A trade we keep: positive quantity and price, and a side of B (buy) or S (sell) | §6 |
| population | Which things a table includes, for example "portfolios that traded" (1,028), not "all portfolios" (2,500) | §7 |
| anti-join | A query that finds rows in one table with no match in another, for example portfolios with no trades | §7 |
| reconciliation / tolerance | Checking that two numbers agree. Tolerance is how close counts as agreeing | §9 |
| bundle | A Databricks Asset Bundle: a config file describing the jobs to deploy | §8 |
| `dense_rank()` | Ranks rows so that ties share a rank and no numbers are skipped (1, 1, 2) | P2 Ch2 |
| incremental / merge | A table that adds only new rows each run instead of rebuilding everything. Merge inserts new rows and updates changed ones in one step | P2 Ch3 |

---

## 1. What current v2 got wrong for this route

- It lost the Atlas framing entirely: no scenario, no producers or consumers, no certification purpose, no team discovery worksheet, no Plan of the Day, no audience guidance, no presentation.
- It ran a cut-down copy of the seeds on local DuckDB instead of building `data_products/atlas_elt` on Databricks.
- It replaced v1's alignment teaching (source-aligned → domain-aligned → consumer-aligned) with unexplained jargon ("STTM", "population oracle").

**Kept from v2:** the exact population numbers (10,000 raw trades → 9,880 valid; 2,500 portfolios → 1,028 active and 1,472 with no trades; 3,717 positions) and the anti-join / wrong-key lesson. Re-measure the numbers on the Databricks build and use them as expected outputs in v1's sections.

---

## 2. Phase map: v1 → v2

| v1 | v2 | Change |
|---|---|---|
| Purpose, Learning Outcomes, Who This Is For, Plan of the Day | Unchanged, at the top | Add At A Glance after Purpose |
| Discovery and Reverse-Mapping, worksheet, path choice | Unchanged | Example answer stays in the appendix |
| Understand the data, domain concepts, alignment, pipeline | Unchanged | Add a one-row worked example of `price_cents → price` and `fee_bps → fee` |
| P1 §1 Inspect source data | P1 §1 | Expected row counts per seed |
| P1 §2 Understand the dbt project | P1 §2 | — |
| P1 §3 Databricks connection | P1 §3 | `mise run challenge:dbt 04 -- debug` + three-step auth check |
| P1 §4 Seed | P1 §4 | Expected `PASS=7` seed summary |
| P1 §5 Source-aligned | P1 §5 | — |
| P1 §6 Domain-aligned | P1 §6 | Expected: 9,880 valid trades; break down the 120 excluded rows by rule |
| P1 §7 Consumer-aligned + tests | P1 §7 | Expected: 1,028 rows in `rpt_portfolio_summary`. **Core debugging step (was a variation):** anti-join to find the 1,472 portfolios with no trades; then join on the wrong key and explain the rows that disappear |
| P1 §8 Orchestration | P1 §8 | — |
| P2 Ch8 Relationship test + Ch9 one reconciliation | **P1 §9 (new): prove one number** | Trades → portfolios relationship test, plus portfolio-summary vs advisor-book AUM reconciliation |
| "Use the product" (after Phase 2 in v1) | **P1 §10 (moved)** | Answer one Discovery question with the marts and feed the presentation |
| Complete Phase 1 gate | P1 gate | `mise run challenge:verify 04 --phase 1` |
| P2 Ch1 Portfolio performance | P2 Ch1 | — |
| P2 Ch2 Advisor leaderboard `dense_rank()` | P2 Ch2 | Add a `rank` vs `dense_rank` vs `row_number` comparison on the real book values |
| P2 Ch10 Incremental market mart | P2 Ch3 | Databricks `merge` with `unique_key`; show run 1 and run 2 row counts |
| P2 Ch14 Regional report (capstone), with the rest of Ch9's reconciliations | P2 Ch4 | Phase 2 gate: `mise run challenge:verify 04 --phase 2` |
| P2 Ch3, 4, 5, 6, 7, 11, 12, 13 | Stretch | Kept with a dependency map, time estimate and check each |

---

## 3. Phase 1 — Certified (target 2 h): improvements

| § | Section | Scaffold | Range (min) |
|---|---|---|---|
| — | Discovery and Reverse-Mapping (team) | — | 20–30 |
| — | Environment waits (warehouse start, seed) | — | 5 |
| 1–4 | Inspect, project tour, connection, seed | reading + run | 15–20 |
| 5 | Source-aligned | worked example → completion | 10–15 |
| 6 | Domain-aligned | completion | 15–20 |
| 7 | Consumer-aligned + tests + anti-join / wrong-key investigation | completion + debugging | 15–20 |
| 8 | Orchestration | reading | 5 |
| 9 | Prove one number | from scratch | 10 |
| 10 | Use the product | team | 5 |
| Cert | Unseen leadership question + explain-back | none | 10 |
| | **Typical total (per team)** | | **~120** |

Teams that split the work can run §5–§7 in parallel; the 2-hour target is per team, not per person. Presentation preparation sits outside both certifications, as in v1's Plan of the Day.

- **At A Glance:** the team task, the Phase 1 outputs list, `mise run challenge:verify 04 --phase 1`, and the finish line (`MVP LIVE PASS` / `Atlas ELT Phase 1 MVP complete.`).
- **Expected-results table** shown once, after "Understand the data", and referenced by each section's check:

  | Check | Value |
  |---|---|
  | raw trades | 10,000 |
  | valid trades | 9,880 |
  | portfolios | 2,500 |
  | positions | 3,717 |
  | portfolios with trades (summary rows) | 1,028 |
  | portfolios with no trades | 1,472 |

- **Two-level hints** in §5–§7 (level 2 gives the column list and join keys).
- **Collapsible solutions** remain, as in v1.
- **Glossary:** keep it, and add *population*, *grain* and *anti-join*.
- **Change one sentence:** "several models are intentionally placeholders" (Prepare section) becomes "several models are starter queries you complete in Phase 1".

## 4. Phase 2 — Proficient (target 90 min)

| Ch | Framed as | Content | Scaffold | Check | Range (min) |
|---|---|---|---|---|---|
| 1 | Consumer request: "portfolio oversight wants net flow and realised fees" | `rpt_portfolio_performance` with a `nullif` guard | completion | 1,028 rows; a sample row matches a hand calculation | 15–20 |
| 2 | Consumer request: "advisor leaders want a ranked book" | `rpt_advisor_leaderboard` with `dense_rank()` | completion | One row per advisor with portfolios; ranking-function comparison table | 15–20 |
| 3 | Bug report: "the daily market mart rebuilds everything on every run" | `ts_daily_market_incremental` (merge) | `config()` block only | The second run inserts 0 rows; totals equal `ts_daily_market` | 15–20 |
| 4 (cert) | Leadership request: "a regional view that reconciles" | `rpt_region_report` + reconciliations from scratch, plus a five-line design note | none | `mise run challenge:verify 04 --phase 2` → PASS; note judged against the rubric | 25–30 |
| — | Explain-back + check yourself | | | | 5 |
| | **Typical total** | | | | **~90** |

## 5. Stretch appendix

v1 Challenges 3 (asset-class activity), 4 (source freshness), 5 (exposures), 6 (money macro), 7 (custom generic test), 11 (snapshot), 12 (extend orchestration) and 13 (params-driven orchestration), plus the Advanced Path ("Build your own paved-path data product"). Keep v1's dependency map, limited to these.

---

## 6. Starter code: no placeholders

Replace every `select 1 as placeholder` under `challenges/.../stubs/datasets/**` (about 30 files) with real starter queries:

- **`src_*` stubs:** `select` from the correct `source('atlas', …)` with the first column renamed. TODOs list the remaining renames and casts.
- **`dom_*` stubs:** the `ref()` CTEs, with one validity rule written as a worked example. TODOs list the rest.
- **`rpt_*` / `agg_*` / `ts_*` / `api_*` stubs:** the `ref()` CTEs and the grain columns. Aggregates are TODOs.

Every stub builds and returns real rows. The Phase 1 gate fails with a named missing column or wrong count, not because a model is empty.

Following the fading map, no stub ships for the §9 tests, `ts_daily_market_incremental` (only its `config()` block ships), `rpt_region_report` or its reconciliations. The learner creates these files.

## 7. mise

| Learner action | Command |
|---|---|
| Auth | `mise run setup:databricks` |
| dbt deps / any dbt command | `mise run setup:dbt-deps`; `mise run challenge:dbt 04 -- build --select +rpt_portfolio_summary` |
| Phase 1 gate | `mise run challenge:verify 04 --phase 1` (wraps the `CERT_INTEGRATION_TESTS=1 ATLAS_VERIFY_SCOPE=mvp` form) |
| Phase 2 gate | `mise run challenge:verify 04 --phase 2` |
| Start a phase over | `mise run challenge:reset 04 --phase 2` (only re-blanks Phase 2 models) |
| Instructor overview | `mise run challenge:review 04` (wraps `verify.sh --review`) |

## 8. Retire from current v2

- `challenges/v2/capstone/phase-*/starter/**` (copied seeds, DuckDB profile, `prepared/`, `starter_status.sql`).
- `challenges/v2-solutions/capstone/**`.
- The capstone paths in `scripts/challenge-v2.py`.
- Update `tests/challenges/offline/test_v2_contracts.py` to the new layout.

## 9. Done when

- [ ] Atlas brief, team discovery, Plan of the Day and presentation are intact; data and models are `data_products/atlas_elt` on Databricks.
- [ ] Phase 1 — Certified = discovery + 10 sections (with quality proof and a business answer), piloted at about 2 h per team. Phase 2 — Proficient = 4 challenges, piloted at about 90 min. Stretch = 8 v1 challenges + Advanced Path.
- [ ] Expected-results table measured on Databricks and used in checks.
- [ ] No placeholder stubs; every command is mise.
- [ ] §0b is implemented: outcomes mapped to sections and checks; certification tasks with no learner-visible solution; explain-back questions with a rubric; the fading map; a core debugging section per phase; misconceptions addressed; recall prompts; check-yourself questions; `--section N` checks; and `FACILITATOR.md`.
- [ ] A trainee run is recorded via the `challenge-trainee-runs` skill, and the pacing ranges are re-baselined from it.
