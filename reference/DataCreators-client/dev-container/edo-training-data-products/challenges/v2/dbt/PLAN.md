# dbt route: v2 plan (uplift of v1 Challenge 02)

## At a glance

| | |
|---|---|
| **v1 source** | [v1/02-dbt-pipeline](../../v1/02-dbt-pipeline/README.md), "Portfolio Analytics" |
| **Target folder** | `challenges/v2/02-dbt-pipeline/` (rename of this `dbt/` folder so v1 and v2 numbering match) |
| **Data** | The v1 seeds, unchanged: `custodian.holdings_raw`, `custodian.positions_raw`, `bloomberg.prices_raw`, `bloomberg.refdata_raw`, `fx_feed.fx_rates_raw`, `product_ref.fund_master_raw`, plus `seed_funds.csv` and `seed_custodian_nav.csv` |
| **Engine** | **Databricks only**, in the learner's pre-provisioned schema, with the same profile pattern as v1 and `portfolio_analytics` |
| **Phase 1 — Certified** | `phase-one-certified`, target **2 h**. Baseline Data Creator standard: v1 Phase 1 (8 sections) **plus** the first join and the first mart, ending with a working source → staging → intermediate → mart slice |
| **Phase 2 — Proficient** | `phase-two-proficient`, target **90 min**. Certified advanced practitioner: v1 Phase 2 (10 challenges) **trimmed to 4** harder core challenges; the rest move to Stretch |
| **mise** | `mise run challenge:seed 02`, `challenge:dbt 02 -- …`, `challenge:verify 02 --phase 1\|2`, `challenge:reset 02 --phase 1\|2` |
| **Current v2 content dropped** | The toy funds A/B/C project, the DuckDB profile, `arrivals`/`fund_labels_duplicate` fixtures, copied `.local/challenges-v2` workspaces, and generated task-template READMEs |

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

> In this challenge you turn raw data files into a clean, tested table that a team can rely on every morning. You use **dbt** (data build tool), which runs the SQL you write on **Databricks**, the company's data platform.
>
> The raw data comes from six **feeds**: files that other systems send us. They include fund holdings from the **custodian** (the bank that keeps a fund's assets), prices from Bloomberg, and currency exchange rates.
>
> **Phase 1 — Certified (about 2 hours).** Everyone does this phase.
> - You tell dbt where the raw data lives and clean each feed into a tidy table.
> - You join the tables and build your first finished table, `agg_fund_exposure`, which shows how much money each fund holds.
> - You add checks as you go (dbt calls them **tests**).
>
> When `mise run challenge:verify 02 --phase 1` passes and you can explain your work, you have reached the baseline standard.
>
> **Phase 2 — Proficient (about 90 minutes)** is for people going further. You build more tables, fix a check that is failing, and design a new table from a team's request with less help. Start it only after Phase 1 passes.
>
> **Stretch** tasks are optional extras. They don't count towards either level.
>
> **How the help works:**
> - Every file you write starts with some working SQL already in it. Lines marked `TODO` tell you exactly what to add.
> - Help fades as you go. Later files give you less, and the last task in each phase starts from an empty file.

---

## 0b. Learning design for this route

**Where it sits:** after 00, Git and 01; before 03 and 04.

**Entry check:**
1. Can you write a `select … join … group by` query? If not, do the SQL refresher linked in *Before you start*.
2. Does `mise run challenge:dbt 02 -- debug` end with `All checks passed!`? If not, run `mise run setup:databricks`.

**Scenario (opens the README):** Fund operations check each fund's exposure every morning by copying custodian files into spreadsheets. `agg_fund_exposure` replaces that: valued in GBP, refreshed daily and tested.

**Outcomes**

| Phase | By the end you can… | Evidence |
|---|---|---|
| 1 | Declare a source with freshness and explain `source()` vs `ref()` | §3 check; explain-back |
| 1 | Write a staging model that renames and casts without changing the grain | §4–§5; certification task |
| 1 | Join and aggregate to a mart at a stated grain | §9–§10 |
| 1 | Read a failing test and fix the cause | §8 |
| 2 | Diagnose a failing reconciliation and choose between a data fix and a tolerance change | Ch3 |
| 2 | Design a mart from a consumer request and justify its grain, materialization and tests | Ch4 certification task |

**Fading map**

| Stage | Sections |
|---|---|
| Worked example | §4 `stg_holdings`: one rename shown in full, with the solution walk-through |
| Completion problems | §5 `stg_funds`, `stg_fx_rates`, `stg_prices`; §9 and §10 with only the `ref()` CTEs given |
| From scratch | §5 `stg_positions` (no stub ships); the certification task |
| Phase 2 | Ch1–Ch2 completion; Ch3 debugging; Ch4 from scratch |

**Certification tasks (no solution in the learner README)**

- **Phase 1:** `bloomberg.refdata_raw` is provisioned but unmodelled. Create `stg_refdata` from scratch, with `unique` and `not_null` tests on the instrument key. Check: `mise run challenge:verify 02 --section cert`.
- **Phase 2:** Ch4, below. A consumer request answered with a new mart, a reconciliation test and a five-line design note.

**Explain-back questions**

- **Phase 1:**
  - Why does staging stay one-to-one with its source?
  - What would go wrong if `int_holdings_enriched` inner-joined FX?
  - Why is `stg_*` a view and `agg_*` a table here?
  - Who should decide the 4-hour freshness warning, and why?
- **Phase 2:**
  - How did you decide between fixing data and changing the tolerance?
  - Why that grain and materialization for your mart?
  - Which models does a change to `stg_holdings` affect? Show the lineage.

**Misconceptions to refute**

- `source()` and `ref()` are interchangeable.
- A passing `relationships` test means a join cannot duplicate rows. Refute with the §9 fan-out variation.
- A view stores data.
- `dbt run` also runs tests.
- `coalesce(fx_rate, 1.0)` is always safe. It hides missing rates, so pair it with a test.

**Recall prompts**

- §2 → 00 §3: where do you write? (`$DBT_CATALOG.$DBT_SCHEMA`)
- §9 → §1 grain table
- Phase 2 Ch1 → §10 grain

**Tracks**

- *Fast track:* §1, §2 and §6 can be skipped once the recall question is answered.
- *Support track:* pair at §5; the third hint level gives the full column list.

**Bridge to the capstone:** §10's Phase 1 summary includes a table mapping staging / intermediate / marts to source-aligned / domain-aligned / consumer-aligned. Challenge 04 shows the same table again.

---

## 0c. Words to explain

Define each term in plain words where it first appears in the README (ground rule 9). This list is the starting point; add any word the first-time-reader review marks.

| Term | Plain definition to use | First used |
|---|---|---|
| dbt | A tool that runs the SQL files you write, in the right order, and checks the results | §0 |
| Databricks | The company's data platform, where the tables live and the SQL runs | §0 |
| feed / source | Raw data another system sends us. Once you describe a feed to dbt, dbt calls it a **source** | §1 |
| seed | A small CSV file that dbt loads into a table for you | §1 |
| custodian | The bank that holds a fund's assets and reports what it holds | §1 |
| model | One SQL file that dbt turns into one table or view | §2 |
| profile | Settings that tell dbt how to connect to Databricks | §2 |
| schema | A named folder for tables in Databricks. Yours is `$DBT_SCHEMA` | §2 |
| `source()` / `ref()` | How a model points at a raw feed (`source`) or at another model (`ref`), so dbt knows what to build first | §3, §9 |
| freshness | How recently a feed was updated. dbt can warn you when it is too old | §3 |
| staging | The first cleaning step: rename columns and fix types, nothing else | §4 |
| grain | What one row stands for, for example "one fund's holding of one instrument on one day" | §4 |
| cast | Changing a value's type, for example the text `"12.5"` into the number `12.5` | §4 |
| CTE | A named step inside a query (`with step as (…)`) that keeps long SQL readable | §4 |
| view vs table | A view is a saved query that runs every time you read it; a table stores the results | §6 |
| materialization | dbt's word for whether a model becomes a view or a table | §6 |
| test | A query that looks for bad rows. If it finds any, the test fails | §8 |
| join / left join | Matching rows from two tables. A left join keeps every row from the first table, even when there is no match | §9 |
| NULL | An empty value meaning "unknown". Any sum with a NULL in it gives NULL | §9 |
| FX / base currency | FX is foreign exchange (converting currencies). The base currency is the one we report in: GBP | §9 |
| mart | A finished table built for one team to use | §10 |
| NAV | Net asset value: what one unit of a fund is worth | P2 Ch2 |
| reconciliation / tolerance | Checking that two numbers agree. Tolerance is how far apart they may be and still count as agreeing | P2 Ch3 |
| lineage | The map of which tables feed which | P2 Ch4 |

---

## 1. What current v2 got wrong for this route

- It replaced the v1 Portfolio Analytics project with a 5-row toy project (funds A/B/C, total 250). The learner never touches the feeds that Challenge 03 then orchestrates.
- It moved execution to local DuckDB with a separate pinned venv. Phase 2's incremental lesson depends on DuckDB `delete+insert` semantics, which do not match Databricks.
- It dropped v1's step-by-step sections, stubs, expected outputs (`Done. PASS=5 …`), variations and solutions, and replaced them with generated task cards.

---

## 2. Phase map: v1 → v2

| v1 | v2 | Change |
|---|---|---|
| P1 §1 Inspect the raw data | P1 §1 | Add the expected seed list and a grain table for each raw feed |
| P1 §2 Read the dbt project | P1 §2 | Annotated project tree; explain where `DBT_ACCESS_TOKEN` comes from |
| P1 §3 Declare sources + freshness | P1 §3 | Show the `dbt source freshness` expected output |
| P1 §4 `stg_holdings` | P1 §4 | Real starter SQL (see §6) |
| P1 §5 Remaining staging models | P1 §5 | One sub-heading per model, each with its own check |
| P1 §6 Materializations | P1 §6 | Show the view vs table difference in Databricks with `dbt show --inline "describe table extended …"` |
| P1 §7 Build the staging layer | P1 §7 | Unchanged; expected `PASS=5` |
| P1 §8 A staging test | P1 §8 | Add an expected-failure demo, then the fix |
| P2 Ch1 `int_holdings_enriched` | **P1 §9 (moved)** | First join; keep v1's USD→GBP variation |
| P2 Ch3 `agg_fund_exposure` | **P1 §10 (moved)** | First mart; Phase 1 now ends end-to-end |
| P2 Ch2 Supporting intermediates | P2 Ch1 | — |
| P2 Ch4 `fct_portfolio_returns` | P2 Ch2 | — |
| P2 Ch5 Generic tests + Ch6 NAV reconciliation | P2 Ch3 (merged) | One "prove the marts" challenge |
| P2 Ch10 Capstone `agg_fund_daily_exposure` (+ Ch7 full build, Ch8 docs) | P2 Ch4 | Full `dbt build` and the lineage check become this challenge's "How to check" |
| P2 Ch9 `OPTIMIZE … ZORDER` post-hook | Stretch | — |
| P2 Ch8 Docs site tour (beyond the lineage check) | Stretch | — |

---

## 3. Phase 1 — Certified (target 2 h): improvements per section

| § | Section | Scaffold | Range (min) |
|---|---|---|---|
| — | Environment waits (warehouse start, first seed) | — | 5–10 |
| 1 | Inspect the raw data | reading | 5–10 |
| 2 | Read the dbt project | reading | 5–10 |
| 3 | Declare sources + freshness | completion | 10–15 |
| 4 | `stg_holdings` | worked example | 10–15 |
| 5 | Remaining staging models (`stg_positions` from scratch) | completion → from scratch | 15–20 |
| 6 | Materializations (predict first) | reading | 5 |
| 7 | Build the staging layer | run | 5 |
| 8 | A staging test: read the failure, then fix it | debugging | 10 |
| 9 | `int_holdings_enriched` | completion | 10–15 |
| 10 | `agg_fund_exposure` | completion (CTEs only) | 10–15 |
| Cert | `stg_refdata` from scratch | none | 10 |
| — | Explain-back + check yourself | — | 5 |
| | **Typical total** | | **~120** |

Keep v1's text as the base and make these upgrades in every section:

- **At A Glance (new, top of README):** main task, runner commands, auth one-liner, and the Phase 1 finish line (`mise run challenge:verify 02 --phase 1` → PASS).
- **Expected output blocks** for every check, trimmed from real Databricks runs. For example, §7 `Done. PASS=5 WARN=0 ERROR=0`, and §10 `dbt show --select agg_fund_exposure --limit 5` with the real fund rows.
- **Two-level hints.** Level 1 says where to look; level 2 gives the column list or SQL shape.
- **Grain callouts** in §1, §4, §9 and §10: "one row per (fund, date, instrument)" and so on.
- **§9 extra variation:** join prices on `instrument_id` only (dropping the date) and observe the row count multiply. This is a fan-out lesson on the same data that replaces v2's separate duplicate-label fixture.
- **§10 extra variation:** compare `count(*)` with `count(distinct instrument_id)` per fund.
- **Phase 1 Summary** (as in v1 03): what you built, what Phase 2 adds.

## 4. Phase 2 — Proficient (target 90 min)

| Ch | Framed as | Content | Scaffold | Check | Range (min) |
|---|---|---|---|---|---|
| 1 | Consumer request: "fund ops need fund attributes and dated positions" | `int_fund_attributes`, `int_positions_dated` | completion | `--section 1`; expected row counts | 15–20 |
| 2 | Consumer request: "performance reporting needs a returns fact" | `fct_portfolio_returns` | completion (CTEs only) | `dbt show` sample with expected NAV columns | 15–20 |
| 3 | Bug report: "the NAV reconciliation fails for one fund" | Generic tests + the strict NAV reconciliation; find the failing rows, decide whether to fix data or apply the agreed tolerance, record the decision | debugging | Failing rows shown, decision recorded, then PASS | 15–20 |
| 4 (cert) | Consumer request: "exposure per fund per day for trend charts" | `agg_fund_daily_exposure` + `tests/reconcile_daily_exposure.sql` from scratch, plus a five-line design note (grain, materialization, tests) | none | `mise run challenge:verify 02 --phase 2` → PASS; design note judged against the rubric | 25–30 |
| — | Explain-back + check yourself | | | | 5 |
| | **Typical total** | | | | **~90** |

## 5. Stretch appendix

- v1 Ch9 `OPTIMIZE … ZORDER` post-hook (Databricks Delta). Check: `describe history` shows the OPTIMIZE operation.
- v1 Ch8 full docs site tour (`dbt docs generate` + `dbt docs serve`).

Each stretch keeps v1's text, with an added time estimate and expected output.

---

## 6. Starter code: no placeholders

Replace every `select 1 as placeholder` stub in `stubs/models/**` with real starter SQL. Each stub must build and return real (partial) data, and the TODO names exactly what is missing. Example for `stg_holdings.sql`:

```sql
with source as (
    select * from {{ source('custodian', 'holdings_raw') }}
)

select
    fund_cd as fund_id
    -- TODO: pos_dt → position_date (cast to date)
    -- TODO: isin → instrument_id
    -- TODO: qty → quantity, mkt_val_lc → mv_local_ccy (cast to decimal)
    -- TODO: ccy_cd → local_ccy
from source
```

Apply the same pattern to the other files:

- **Intermediate and mart stubs:** the `ref()` CTEs are given, plus the first column of the final select. Joins and aggregates are TODOs. By §10, only the CTEs are given.
- **No stub ships** for `stg_positions` (§5), `stg_refdata` (certification), or `agg_fund_daily_exposure` and its test (Phase 2 Ch4). The learner creates these files. Their absence is part of the fading, not a gap.
- **`tests/assert_nav_within_tolerance.sql`:** ships as a real, strict comparison (`abs(diff) > 0`) that fails on first run. The TODO is to apply the agreed tolerance. The failure is the lesson, not a placeholder.
- **Verify gate:** fails with a column-level message (for example "stg_holdings is missing position_date") rather than passing on an empty stub.

---

## 7. mise

| Learner action | Command |
|---|---|
| One-time auth | `mise run setup:databricks` |
| Load raw feeds | `mise run challenge:seed 02` |
| Any dbt command | `mise run challenge:dbt 02 -- build --select stg_holdings` |
| Phase gate | `mise run challenge:verify 02 --phase 1` / `--phase 2` |
| Start a phase over | `mise run challenge:reset 02 --phase 1` (says exactly which files it re-blanks) |

Task changes needed in [.mise.toml](../../../.mise.toml):

- Add a `--phase` flag to `challenge:verify` and `challenge:reset` (Phase 1 = staging + `int_holdings_enriched` + `agg_fund_exposure`).
- Resolve the challenge directory from v2 once v2 is promoted.
- Retire the `challenge:v2:*` tasks.

Raw `dbt` from the project folder remains valid inside a mise-activated shell; the README presents the mise form first.

## 8. Retire from current v2

- `challenges/v2/dbt/phase-*/starter/**` (toy project, DuckDB `profiles.yml`).
- `challenges/v2-solutions/dbt/**`. The solution becomes `solution/`, beside `stubs/`, as in v1.
- The dbt paths in `scripts/challenge-v2.py`, and `dbt-duckdb` in `scripts/setup-v2-tools.sh` / `scripts/v2-tools-requirements.txt`.
- Update `tests/challenges/offline/test_v2_contracts.py` and `scripts/sync-v2-course.py` to the new layout.

## 9. Done when

- [ ] Same seeds, sources, model names and narrative as v1 02, built on Databricks.
- [ ] Phase 1 — Certified = 10 sections ending at `agg_fund_exposure`, piloted at about 2 h. Phase 2 — Proficient = 4 challenges, piloted at about 90 min. Stretch holds the rest.
- [ ] No `select 1 as placeholder`, no `'unused'` defaults, no angle-bracket values in any learner file or command.
- [ ] Every check has a literal expected output; every section has a variation and a collapsible solution.
- [ ] All commands are mise; `challenge:verify 02 --phase 1|2` gates pass on the solution and fail clearly on the stubs.
- [ ] §0b is implemented: outcomes mapped to sections and checks; certification tasks with no learner-visible solution; explain-back questions with a rubric; the fading map; a core debugging section per phase; misconceptions addressed; recall prompts; check-yourself questions; `--section N` checks; and `FACILITATOR.md`.
- [ ] A trainee run is recorded via the `challenge-trainee-runs` skill, and the pacing ranges are re-baselined from it.
