# Data Creators — instructor courseware

The pack for running Capital Group's five-day Data Creators programme. It follows the timetable in `../reference/instructor-plan.md` and the learners' challenges in the training repository (`challenges/v1/01…04`), which are not changed here. Everything the instructor shows runs on this laptop: DuckDB stands in for Databricks, Docker Desktop and the Astro CLI run the same images as the learners' environment, and Claude Code stands in for Copilot with the same Catalyst skills.

Start with [00-week/start-here.md](00-week/start-here.md).

## Layout

| Folder | What is in it |
|---|---|
| `00-week/` | The week at a glance, the pre-flight checklist, the LLM guide (Claude for the instructor, Copilot for learners), risks and fallbacks |
| `common/` | `env/` (setup and check scripts), `running-example/` (the "US end-of-day instrument prices" product: interview, PRD, contract, STTM, SLAs, planted errors), `prompts/` (prompt library with Copilot and Claude variants), `diagrams/` (Mermaid sources for every whiteboard), `catalyst/` (installs a subset of Catalyst skills for Claude Code) |
| `day1-design/` | Run sheet, activity cards 1–5, demo guides (Catalyst skill anatomy, Copilot settings, Voice Memos), fallback artefacts |
| `day2-platform/` | Run sheet, activity cards 6–8 plus the pair review, demo guides (STTM and service levels, Markdown to HTML, paved path and data systems, Docker, Databricks setup, contract to code), the Docker demo app and the contract-to-code dbt project |
| `day3-dbt/` | Run sheet, the Portfolio Analytics dbt project on DuckDB with a section-by-section demo guide (challenge 02 plus macros, snapshots, incremental, unit tests), the platform-session fallback, recap and pair test-review cards |
| `day4-airflow/` | Run sheet, the bitemporal loading demo (custom dbt strategy), the local Astro Airflow stack running the Day 3 and Day 2 projects with Cosmos, CI/CD and Harness guide, release-decision and failure-note cards |
| `day5-capstone/` | Briefing script, discovery worksheet, circulation notes, presentation cards, and the Atlas solution on DuckDB with expected results |
| `.claude/skills/` | Catalyst skills copied by `common/catalyst/install-skills.sh` (open this folder in Claude Code to use them) |

## Conventions

- Timings are the instructor plan's. Each run sheet row has a purpose, what is on screen, a whiteboard script with the answers a room typically gives, lines to say, the transition, and what to do if ahead or behind.
- Activity cards are written to be shown on the projector and printed one per table. They can be shared with learners as they are.
- Demo guides say what to open, what to type, what the room should see, and what to do if the tool is slow or blocked. Every demo has a script that runs it end to end (`demo.sh`, `run.sh` or `build.sh`).
- Learner-facing wording never names an instructor; "the instructor" and "you" are used throughout.
