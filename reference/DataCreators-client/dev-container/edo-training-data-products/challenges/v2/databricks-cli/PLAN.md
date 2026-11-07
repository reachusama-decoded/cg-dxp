# Databricks CLI route: v2 plan (fold into the uplift of v1 Challenge 00)

## At a glance

| | |
|---|---|
| **v1 source** | [v1/00-environment-check](../../v1/00-environment-check/README.md). v1 has no separate Databricks CLI challenge; the CLI appears in 00 (auth) and in 04 (bundle gate) |
| **Recommendation** | **Do not keep a standalone CLI route.** Merge this folder into `challenges/v2/00-environment-check/`, which uplifts v1 00 into two phases and uses the CLI against the real v1 data |
| **Data** | The learner's own schema after `mise run challenge:seed 02` (the v1 Portfolio Analytics raw feeds), and the `data_products/atlas_elt` bundle from v1 04 |
| **Engine** | Databricks, via the mise-pinned CLI (`databricks-cli = "0.236.0"` in [.mise.toml](../../../.mise.toml)), always called as `mise exec -- databricks …` |
| **Phase 1 — Certified** | `phase-one-certified`, target **~1 h** (tool primer). v1 00 (toolchain + auth + Astro check) **plus**: who am I, where is my schema, what did seeding create |
| **Phase 2 — Proficient** | `phase-two-proficient`, target **~45 min**. 2 challenges: read the Atlas bundle and find the job it deploys. No "not offered" page |
| **mise** | `mise run setup:databricks`, `mise run challenge:verify 00 --phase 1\|2` |
| **Current v2 content dropped** | `metadata.json` fixture, hardcoded `training_dev` / `<instructor-schema>`, offline "fixture-only" completion, Phase 2 placeholder page |

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

> Before you build anything, you need to know three things: your tools work, Databricks knows who you are, and you know where your tables will be saved. **Databricks** is the company's data platform. You talk to it from the terminal with the **Databricks CLI** (command-line interface): commands you type instead of buttons you click.
>
> **Phase 1 — Certified (about 1 hour).** Everyone does this phase.
> - You check your tools, sign in and prove it worked.
> - You find your Databricks username and your own storage area.
> - Then you look at the raw data you will use in Challenge 02.
>
> Passing `mise run challenge:verify 00 --phase 1` and explaining your work reaches the baseline standard.
>
> **Phase 2 — Proficient (about 45 minutes).** You read the settings file that describes the Atlas jobs you will run in the capstone, and work out what it would set up. Nothing is changed.
>
> **How the help works:**
> - A small script, `list_tables.py`, tidies the CLI's output for you.
> - You start every Databricks command with `mise exec --`, which makes sure the right version of the CLI runs.

---

## 0b. Learning design for this route

**Where it sits:** first (route 00).

**Entry check:**
1. Does your terminal prompt show `/workspaces/edo-training-data-products`, meaning you are inside the devcontainer?
2. Does `mise --version` print a version?

**Outcomes**

| Phase | By the end you can… | Evidence |
|---|---|---|
| 1 | Prove that you are signed in, rather than assume it, and tell "signed out" apart from "the sign-in didn't reach the program" | §2 |
| 1 | Find your Databricks identity and where your tables are saved | §3 |
| 1 | Tell a workspace folder apart from a catalog.schema.table name | §3 |
| 1 | List and inspect tables, and read the CLI's JSON output | §4–§5; certification task |
| 2 | Read a bundle and explain its targets and jobs | Ch1 |
| 2 | Work out what a bundle would deploy, and with which parameters, without changing anything | Ch2 certification task |

**Fading map**

| Stage | Sections |
|---|---|
| Worked examples | §1–§3 |
| Completion problem | §4 (one TODO in `list_tables.py`) |
| Debugging | §2 (the error when `mise exec --` is left out); §5 (`NOT_FOUND` vs an empty list) |
| From scratch | Phase 1 certification task |
| Phase 2 | Ch1 guided; Ch2 none |

**Certification tasks (no solution in the learner README)**

- **Phase 1:** a teammate asks, "What is `fx_rates_raw`?" Using only the CLI, write five lines: its full name, table type, columns, owner and last-updated time. Check: `mise run challenge:verify 00 --section cert` compares the note with the live table.
- **Phase 2:** Ch2, below.

**Explain-back questions**

- **Phase 1:**
  - Why can `auth describe` pass while dbt still fails to sign in?
  - What is the difference between a workspace path and a catalog.schema.table name?
  - What does an empty list tell you that a `NOT_FOUND` error doesn't?
- **Phase 2:**
  - What is a bundle target?
  - Which parameter would change for production, and why?

**Misconceptions to refute**

- `auth describe` passing means dbt will sign in.
- Your terminal username is your Databricks identity.
- A workspace folder named like a catalog *is* the catalog.
- An empty list means you lack permission.

**Recall prompt:** Phase 2 Ch1 → §3: "Which catalog and schema will this bundle write to?"

**Tracks**

- *Fast track:* skip §1 after its recall question.
- *Support track:* pair at §2; the third hint level gives the full command.

---

## 0c. Words to explain

Define each term in plain words where it first appears in the README (ground rule 9).

| Term | Plain definition to use | First used |
|---|---|---|
| CLI | Command-line interface: a program you control by typing commands | §0 |
| mise / `mise exec --` | The tool that installs the right versions of our other tools. `mise exec --` runs a command with those versions | §1 |
| shim | A small stand-in program mise uses to pick the right version. "No version is set for shim" means you left out `mise exec --` | §2 |
| sign-in, OAuth, token | You sign in once in the browser (OAuth). Databricks then gives a short-lived pass (a token) that commands use | §2 |
| profile (`DEFAULT`) | A saved set of connection settings with a name | §2 |
| workspace | Databricks' file area for notebooks and folders. It is separate from where tables live | §3 |
| Unity Catalog; catalog.schema.table | Where tables live, named in three parts, for example `training_dev.training_jsmith.holdings_raw` | §3 |
| JSON | A text format for structured data, with `{ }` for objects and `[ ]` for lists | §4 |
| seed | A CSV file that dbt loads into a table | §4 |
| table type (managed / external) | Whether Databricks stores the data itself or points at files stored elsewhere | §5 |
| bundle | A Databricks Asset Bundle: a settings file describing jobs and where to deploy them | P2 Ch1 |
| target / job / parameter | An environment such as dev or prod / a scheduled piece of work / a value passed to a job when it runs | P2 Ch1 |

---

## 1. What current v2 got wrong for this route

- It invented a standalone route on a fake `metadata.json` (one catalog, one schema, one table). It allowed "offline" completion against that fixture.
- It told learners to type `<instructor-schema>` and assumed `training_dev`, although `mise run setup:databricks` already exports `DBT_CATALOG` / `DBT_SCHEMA` (and `DATABRICKS_CATALOG` / `DATABRICKS_SCHEMA`).
- It never used `mise exec --`, so the pinned CLI fails in a fresh shell with "No version is set for shim". The repo instructions call this out as the most common *false* auth failure.
- It shipped a "Phase 2 — not offered" placeholder page.

---

## 2. Phase map: v1 → v2

| v1 00 | v2 00 | Change |
|---|---|---|
| Goal + Toolchain list | At A Glance + "What each tool is for" table (dpc-check, databricks, astro, dbt, mise) | — |
| How To Use: run `verify.sh` | P1 §1 Run the environment check | `mise run challenge:verify 00 --phase 1`; expected PASS line; what each failure line means |
| "If auth is missing, run setup" | P1 §2 Sign in and prove it | `mise run setup:databricks`, then the three-step check from the repo instructions (describe → token → `DBT_ACCESS_TOKEN` prefix) with expected outputs |
| — | **P1 §3 Who am I, where do I write** | `mise exec -- databricks current-user me --profile DEFAULT --output json`; `echo "$DBT_CATALOG.$DBT_SCHEMA"`; workspace path vs Unity Catalog name, side by side |
| — | **P1 §4 See your raw feeds** | Start with one sentence of context: *"Seeding loads the CSV files that come with Challenge 02 into tables in your area. You will study them in 02 §1; run it now so there is something to find."* Then `mise run challenge:seed 02`, then `mise exec -- databricks tables list "$DBT_CATALOG" "$DBT_SCHEMA" --output json` piped to a supplied `list_tables.py` that prints `full_name`. Expected: the six `*_raw` tables plus the two seed tables |
| — | **P1 §5 Inspect one table** | `mise exec -- databricks tables get "$DBT_CATALOG.$DBT_SCHEMA.holdings_raw" --output json`; read the column names that Challenge 02 §1 relies on |
| — | **P2 Ch1 Read the Atlas bundle** | From `data_products/atlas_elt`: `mise exec -- databricks bundle validate`; identify targets, the job resource and its parameters (the same bundle v1 04 Ch13 discusses) |
| — | **P2 Ch2 Find what the bundle deploys** | `mise exec -- databricks bundle summary` and `jobs list --output json`, filtered by the job name printed in Ch1. Read-only |
| Notes | Troubleshooting | Shim error, expired OAuth, `PERMISSION_DENIED` vs `NOT_FOUND` vs an empty list, each with its real error text |

---

## 3. Time budget and improvements in every section

| Phase | § / Ch | Scaffold | Range (min) |
|---|---|---|---|
| 1 — Certified | §1 Run the environment check | worked example | 5–10 |
| | §2 Sign in and prove it, including the error when `mise exec --` is left out | debugging | 10 |
| | §3 Who am I, where do I write (predict first) | worked example | 5–10 |
| | §4 See your raw feeds | completion | 10 |
| | §5 Inspect one table, including `NOT_FOUND` vs an empty list | debugging | 5–10 |
| | Cert: describe `fx_rates_raw` | none | 10 |
| | Explain-back + check yourself | — | 5 |
| | **Phase 1 typical total** | | **~60** |
| 2 — Proficient | Ch1 Read the Atlas bundle | guided | 15–20 |
| | Ch2 (cert) Ops question: "which job does the bundle deploy to dev, with which parameters, and what changes in prod?" | none | 20–25 |
| | Explain-back + check yourself | — | 5 |
| | **Phase 2 typical total** | | **~45** |

- Expected JSON trimmed to the fields that matter (`userName`, `full_name`, `table_type`, `columns[].name`).
- Two-level hints. Level 2 gives the exact command.
- **Variations:**
  - `--output text` vs `json` (§3).
  - List `/Users/$(mise exec -- databricks current-user me --output json | python3 -c 'import json,sys; print(json.load(sys.stdin)["userName"])')` (§3).
  - `tables list` after `mise run challenge:seed 04` to see the Atlas seeds appear (§4).
- Collapsible solutions.

## 4. Starter code: no placeholders

- `list_tables.py`: real script that reads CLI JSON from stdin, unwraps the `{"tables": [...]}` envelope and prints names. A TODO adds a `--suffix _raw` filter.
- No fixture file; every observation comes from the learner's own workspace.

## 5. mise

| Learner action | Command |
|---|---|
| Sign in | `mise run setup:databricks` |
| Phase gate | `mise run challenge:verify 00 --phase 1` / `--phase 2`. Phase 1 extends v1's `verify.sh` with the identity, schema and seeded-table checks; Phase 2 runs `bundle validate` |
| Any CLI command | `mise exec -- databricks …` |

## 6. Retire from current v2

- This `databricks-cli/` folder (both phases, `metadata.json`, Phase 2 placeholder).
- `challenges/v2-solutions/databricks-cli/**` and the related paths in `scripts/challenge-v2.py`.
- In `tests/challenges/offline/test_v2_contracts.py`, update the manifest and phase-count assertions (`offered == 12`) to the new route list.

## 7. Done when

- [ ] `challenges/v2/00-environment-check/` exists, built from v1 00, with Phase 1 — Certified (5 sections, about 1 h) and Phase 2 — Proficient (2 challenges, about 45 min).
- [ ] Every CLI call uses `mise exec --` and environment-derived names; no fixture-only completion.
- [ ] Learners see the same raw tables they model in Challenge 02 and the same bundle they deploy in Challenge 04.
- [ ] §0b is implemented: outcomes mapped to sections and checks; certification tasks with no learner-visible solution; explain-back questions with a rubric; the fading map; a core debugging section per phase; misconceptions addressed; recall prompts; check-yourself questions; `--section N` checks; and `FACILITATOR.md`.
- [ ] A trainee run is recorded via the `challenge-trainee-runs` skill, and the pacing ranges are re-baselined from it.
