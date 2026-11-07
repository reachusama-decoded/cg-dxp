# Data Creators — course materials

The materials for Capital Group's five-day Data Creators programme. Everything here can be shared with learners as it is.

| Folder | What is in it |
|---|---|
| `day1-design/` … `day5-capstone/` | One anchor notebook per day (`dayN_anchor.ipynb`): the agenda, one numbered section per topic with its diagrams, the demo cells, the activity briefs and the pointers into the training repository's challenges, and a Questions section filled in during the day. `activities/` holds the activity cards; `demos/` (and `day5-capstone/support/`) the code the demos run, on DuckDB and local containers, each with a README. |
| `common/running-example/` | The product used in every demo: the interview transcript, PRD, data contract (with a planted-errors version), source-to-target mapping and service levels for a US end-of-day instrument price sheet. |
| `common/prompts/` | The prompt library: one entry per activity, Copilot first and Claude Code where it differs. |
| `common/diagrams/` | Every diagram in the notebooks, as Mermaid sources and rendered PNGs. |
| `common/env/` | Scripts that create the local demo environment (a Python virtualenv with dbt and DuckDB, the Astro CLI) and check it. |
| `common/catalyst/` | Installs a subset of the Catalyst skills for Claude Code into `.claude/skills/`, so the same skills learners run in Copilot can be run here. |

How to use a notebook: open it in VS Code from its own folder with the `cg-dxp` kernel, run the Setup cell, then follow the sections. Cells that start with `!` run in a shell with the demo environment on `PATH`. The challenges themselves live in the training repository (`challenges/v1/01` to `04`); the notebooks point at them and do not change them.

The notebooks, activity cards and run sheets are generated from one source per day in `../research/scripts/notebooks/`; edit there and rebuild rather than editing the `.ipynb`. The instructor material (run sheets, prep guides, the week's start-here, pre-flight checklist, LLM guide and risks) is in `../instructor/`.
