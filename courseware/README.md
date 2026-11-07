# Data Creators — instructor courseware

The pack for running Capital Group's five-day Data Creators programme. It follows the timetable in `../reference/instructor-plan.md` and the learners' challenges in the training repository (`challenges/v1/01…04`), which are not changed here. Everything the instructor shows runs on this laptop: DuckDB stands in for Databricks, Docker Desktop and the Astro CLI run the same images as the learners' environment, and Claude Code stands in for Copilot with the same Catalyst skills.

Start with [00-week/start-here.md](00-week/start-here.md).

## Layout

| Folder | What is in it |
|---|---|
| `00-week/` | The week at a glance, the pre-flight checklist, the LLM guide (Claude for the instructor, Copilot for learners), risks and fallbacks |
| `common/` | `env/` (setup and check scripts), `running-example/` (the "US end-of-day instrument prices" product: interview, PRD, contract, STTM, SLAs, planted errors), `prompts/` (prompt library with Copilot and Claude variants), `diagrams/` (Mermaid sources and rendered PNGs for every diagram in the anchors; `render.sh` rebuilds them), `catalyst/` (installs a subset of Catalyst skills for Claude Code) |
| `day1-design/` | `day1_anchor.ipynb` (the notebook on the projector: agenda, a diagram per concept with its whiteboard script, demo cells, activity and challenge boxes, a live Q&A section), run sheet, activity cards 1–5 |
| `day2-platform/` | `day2_anchor.ipynb`, run sheet, activity cards 6–8b, and the demos (`demos/README.md`): the Docker app, Delta under the hood, the Spark engine, the contract-to-code dbt project |
| `day3-dbt/` | `day3_anchor.ipynb`, run sheet, activity card 9, and the Portfolio Analytics dbt project on DuckDB (challenge 02 plus macros, snapshots, incremental, unit tests; `demos/portfolio_analytics/README.md` maps its cells to the challenge sections) |
| `day4-airflow/` | `day4_anchor.ipynb`, run sheet, activity cards 10–11, the bitemporal loading demo (a custom dbt strategy) and the local Astro Airflow stack running the Day 3 and Day 2 projects with Cosmos (`demos/README.md`) |
| `day5-capstone/` | `day5_anchor.ipynb` (brief, discovery, Phase 1 circulation notes with expected results, Phase 2 menu, tally sheet), run sheet, activity cards 12–13, and the Atlas solution on DuckDB (`support/README.md`) |
| `.claude/skills/` | Catalyst skills copied by `common/catalyst/install-skills.sh` (open this folder in Claude Code to use them) |

## Conventions

- Timings are the instructor plan's. Each run sheet row has a purpose, what is on screen, a whiteboard script with the answers a room typically gives, lines to say, the transition, and what to do if ahead or behind.
- Activity cards are written to be shown on the projector and printed one per table. They can be shared with learners as they are.
- The anchor notebook is what goes on the projector each day: the agenda, one diagram per concept with the whiteboard script folded beneath it, demo cells that run the day's code, the activity and challenge boxes, and a Questions section at the end for live notes and sketches (`quick_diagram()` renders Mermaid typed on the spot). Open it in VS Code with the `cg-dxp` kernel from its own folder.
- The anchors, run sheets and activity cards are generated from one source per day in `../research/scripts/notebooks/` (`build_all.py`); edit there and rebuild rather than editing the `.ipynb`. `smoke.py` runs every code cell from the terminal.
- Every demo has a README beside it and a script that runs it end to end (`demo.sh`, `run.sh` or `build.sh`).
- Learner-facing wording never names an instructor; "the instructor" and "you" are used throughout.
