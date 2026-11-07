# CG Core — programme structure, titles, modules, pathways

Source of scope: `designer/core/transcripts/cg-design-core.md` (line numbers below refer to it). Module titles are the brief's and are authoritative for scope. Unit, day and module titles were approved by MJB on 2026-11-02; the design document's "Programme at a glance" table holds them.

## Shape

- 8 taught half-days + 1 capstone half-day, arranged 2 + 2 + 2 + 2 + 1.
- Unit = a pair of half-days (six modules). Session = one half-day (three modules). Module = one hour: demo about 20, challenge 20 to 25, debrief 5, break 5 to 10. Each session ends with open challenge time, where Put it together is the optional stretch for fast finishers, then a 5-minute closing debrief and a 10-minute wrap-up (user, 2026-10-16).
- Learners self-select session pairs. Each pair publishes prerequisites and outcomes. The capstone certifies; entry needs the skills and tools, not attendance at every pair.
- Terminology clash with Fundamentals (where a unit is one half-day) is an open MJB item. Inside Core, always use unit = pair.

## Map (working order; brief line numbers point at the module's questions)

| Session | Unit | Title | Module | Module title | Brief source (line) |
|---|---|---|---|---|---|
| S01 | U1 Software engineering with AI | Notebooks to scripts, the command line and Python environments | M1 | Software engineering, your first programs and Copilot | U1 M1 (76) + set-up/workflow parts of U1 M4 (124) |
| | | | M2 | Command line, Linux and remote workflows | U1 M2 (93) |
| | | | M3 | Python packages, dependencies and reusable modules | U1 M3 (110) |
| S02 | U1 | Testing with pytest, Git and pull requests, containers and CI | M4 | Unit testing with pytest and AI | U1 M6 (156) |
| | | | M5 | Git, pull requests and AI-assisted review | U1 M5 (140) |
| | | | M6 | Containers and CI — build, run, check | U1 required integration (170); placement proposed |
| S03 | U2 AI engineering | AI product design, FastAPI and hosted-model calls with AI frameworks | M1 | Systems thinking — the shape of an AI product | Programme demonstration (26); U4 M6 proposed first question (456); U4 M1 proposed first question (405) |
| | | | M2 | Rapid JSON API development | U4 M5 proposed (444) |
| | | | M3 | Hosted models as components — calling, structured outputs and vendor isolation | U4 M1 proposed (403) + U2 M6 (261) + U4 M2 proposed integration and errors (412) + U4 M3 proposed structured outputs (422) |
| S04 | U2 | RAG and grounding, agents and tools, evals | M4 | RAG and grounding — documents, numbers and traceability | **Addition to the brief** (user, 2026-10-13): retrieval over documents; grounding itself from U4 M4 proposed (434) and the Deloitte 06/09 material. Flag to MJB |
| | | | M5 | Agents, tools and AI skills | U4 M3 proposed tool calling (422) + U4 M4 proposed agents and AI skills (434) |
| | | | M6 | Evals — gold sets, repeated trials and model choice | U4 M6 proposed (454) + U4 M2 proposed model choice (412) + Deloitte 03/05/10 |
| S05 | U3 Data science with AI | Exploratory analysis, statistics and time series | M1 | Exploratory data analysis in Python with AI | U2 M1 (182) |
| | | | M2 | Descriptive and inferential statistics | U2 M2 (198) |
| | | | M3 | Time-series analysis | U2 M3 (214) |
| S06 | U3 | Predictive modelling, leakage checks and local pretrained models | M4 | Predictive modelling — targets, baselines and reproducible pipelines | U2 M4 first half (230); working split |
| | | | M5 | Automated improvement, comparison and leakage checks | U2 M4 second half (230), with the original's supporting NumPy, scikit-learn and SciPy material |
| | | | M6 | Local pretrained models | U2 M5 (246) |
| S07 | U4 Data engineering with AI | Data products, platforms and dbt transformations | M1 | Introduction to data engineering | U3 M1 (285) |
| | | | M2 | Data platforms | U3 M2 (299) |
| | | | M3 | ETL/ELT and dbt | U3 M3 (315) |
| S08 | U4 | Data quality, Airflow orchestration and AI-assisted pipelines | M4 | Data quality and advanced dbt | U3 M4 (329) |
| | | | M5 | Airflow and orchestration | U3 M5 (343) |
| | | | M6 | AI-assisted pipeline development | U3 M6 (361) |
| S09 | Capstone | Build, containerise and present an AI-powered data API | P1–P3 | Data ingestion and preparation · Analysis, GenAI and API integration · Final demonstration and design review | Capstone (467) |

The brief's Unit 4 is a *proposed* outline adapted from the Deloitte GenAI reference (383); its allocation and this reorder are open MJB decisions. The brief's U1 M4 "Effective AI use for software engineering" is dissolved into S01 M1 plus the AI-assisted thread in every module and the *Working with Copilot* appendix.

## Module identifiers

Write a module as `S03 M2` in prose and `day03-m2` in file and folder names. Inside a unit the six modules are M1–M6 (first session M1–M3, second M4–M6), so `day02-m4` is Unit 1 Module 4. The Asana board still uses the brief's unit numbering; relabel it once MJB confirms the order, and until then quote the "brief source" column when talking to MJB.

## Programme goals and demonstrations

Brief lines 13–39. Six goals (transferable Python and engineering skills; reliable analytical practice; data-engineering capability; baseline modelling; production-minded GenAI and agentic patterns; an end-to-end capstone demonstrated with its evidence) and eight programme-level demonstrations (describe an end-to-end architecture; explain reproducibility, testing and maintainability; list core tools; compare tools and methods; write robust scripts, notebooks and packages; create ELT pipelines with quality evidence; design and evaluate predictive and generative workflows; package and demonstrate a backend JSON API). Session outcomes ladder up to these; each session's outcomes (about five, each naming its modules) are in `internal-programme-overview.md` §6, and a session lists only what it delivers.

## Pathways and prerequisites (user, 2026-11-02; the wording is `internal-programme-overview.md` §5's, word for word in the programme overview)

- Pair 1 (S01–S02): assumes comfort with code and an editor; no notebook, terminal or Git experience assumed.
- Pair 2 (S03–S04): assumes Pair 1 or equivalent (Python, environments, tests, Git, Docker). Uses the given analysis package; no data-science prerequisite.
- Pair 3 (S05–S06): assumes Pair 1's Python and environments or equivalent.
- Pair 4 (S07–S08): assumes Pair 1 or equivalent, and SQL basics: the dbt transformations are written in SQL. Never "helpful": what a unit needs is stated as needed (user, 2026-11-02).
- Capstone (S09): assumes Pairs 1, 2 and 4 skills and tools, SQL included, or demonstrated equivalents; Pair 3 isn't required (the analysis functions are supplied and predictive modelling isn't a required stage).

Each session's `dayNN_overview.md` states its prerequisites in a sentence under Before you start (S01: what it pairs with, what it assumes and what it doesn't). Publish a readiness route for learners who select only some pairs.

## Title conventions

- MJB approved the unit, day and module titles on 2026-11-02; they are final, from the design document's "Programme at a glance" table, word for word.
- Session titles name the content of their three modules and carry no hook phrase; the unit title carries the theme (user, 2026-10-15, because a hook such as "Writing software with AI" only echoed the unit). Sentence case, no colons, never "(cont.)"; a tool may appear where it is the content (pytest, dbt, Airflow).
- Module titles are copied from the brief verbatim (title case is the brief's; keep it in headings, do not re-case piecemeal).
- House shapes for titles you invent (challenges, figures, appendices): "X & Y" pairs, "From X to Y", verb-led imperatives. Brand-voice test: would a smart 16-year-old understand it?

## Exemplar data table (extend when a dataset is added)

| File (in each of `courseware/common/data/demo/` and `courseware/common/data/challenge/`) | Shape | Introduced | Used by |
|---|---|---|---|
| `funds.csv` | one row per fund share class: id, name, category, benchmark id, inception, fees | S01 | everywhere |
| `harbourline_analysis/` (package under `courseware/common/`) | given, tested analysis functions (returns, drawdown, benchmark comparison) returning plain dicts | S03 | S03, S04, S09 |
| `fund_nav_daily.parquet` | daily NAV and total return per share class, ~5 years | S01 | S03–S06, S09 |
| `holdings.csv` | fund × instrument × weight at month ends | S05 | S05, S07, S08 |
| `benchmarks.csv` | benchmark id, name, category (eight invented indices) | S03 | S03–S06 |
| `benchmark_levels_daily.parquet` | daily index level per benchmark, same London business-day calendar as the NAV file | S03 | S03–S06 |
| `documents/` | synthetic fund factsheets, commentary and policy notes for retrieval | S04 | S04, S09 |
| `raw/` | deliberately faulty source extracts (duplicates, nulls, late rows, type drift) | S07 | S07, S08, S09 |
| CG open product data (public website; MJB supplies) | a possible later dataset, run locally in the dev container like the other two (profile rule 3) | if supplied | S07, S08, S09 |

All synthetic, generated by `scripts/make_exemplar_data.py` (run with `.venv/bin/python`, dependencies pinned in `scripts/requirements.txt`) with a fixed seed per pack: the demo data is Harbourline's HLF fund family (instructor demos), the challenge data the HLP family (learner challenges); same files and schema, different funds, numbers, documents and faults (user, 2026-10-15). Each dataset carries its own README data dictionary. Regenerating changes numbers quoted in prose: rerun every module's demo and re-verify figures when the generator changes.
