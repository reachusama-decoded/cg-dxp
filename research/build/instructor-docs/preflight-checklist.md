# Pre-flight checklist

[Data Creators › instructor pack — pre-flight checklist]{.breadcrumb}

## Instructor laptop (do once, the week before; re-check the night before)

- [ ] Docker Desktop installed and running (the whale in the menu bar). `docker info` works in a terminal.
- [ ] Run `bash courseware/common/env/setup-env.sh` once (creates `~/.venvs/cg-dxp` with dbt-core 1.11.8 and dbt-duckdb, installs the Astro CLI into `~/.local/bin`).
- [ ] In every demo terminal: `source courseware/common/env/activate.sh`. Then `bash courseware/common/env/check-env.sh` prints `[ok]` on every line.
- [ ] VS Code: open `courseware/day1-design/day1_anchor.ipynb`, choose the `cg-dxp` kernel (registered by `setup-env.sh`) and run the setup cell; it defines `sql()` and `quick_diagram()` and prints nothing.
- [ ] Day 2 Docker demo: `bash courseware/day2-platform/demos/docker/portfolio-summary/demo.sh` prints the six-holding summary.
- [ ] Day 2 contract to code: `bash courseware/day2-platform/demos/contract-to-code/eod_prices/run.sh` ends with `dbt show` of the US price sheet.
- [ ] Day 2 platform: `python courseware/day2-platform/demos/delta-under-the-hood/demo.py` ends with the OPTIMIZE step; `python courseware/day2-platform/demos/spark-engine/demo.py --hold 20` prints a plan with an Exchange and the Spark UI answers at http://localhost:4040 while it holds (Java 17; `activate.sh` sets `JAVA_HOME`).
- [ ] Day 3 dbt: `bash courseware/day3-dbt/demos/portfolio_analytics/demo.sh stretch` ends green; open `target/index.html` (`dbt docs serve --host 127.0.0.1 --port 8081`) once to see the lineage graph loads.
- [ ] Day 4 bitemporal: `bash courseware/day4-airflow/demos/bitemporal/demo.sh` prints the four-row audit trail.
- [ ] Day 4 Airflow: `cd courseware/day4-airflow/demos/airflow_local && bash run.sh start` (first time builds the image, several minutes), then `bash run.sh seed`, `bash run.sh trigger`, `bash run.sh status` shows a green run, `bash run.sh stop`. Leave the image built; start the stack again on the morning of Day 4.
- [ ] Day 5 Atlas: `bash courseware/day5-capstone/support/atlas_duckdb/build.sh` ends green and `python courseware/day5-capstone/support/expected-results.py` writes the expected numbers.
- [ ] Claude Code: open the `courseware/` folder as the project, type `/` and check `data-contract` and `product-requirements-document` appear (installed by `courseware/common/catalyst/install-skills.sh`).
- [ ] Voice Memos on this laptop records and shows a transcript (Day 1 demo). Alternative: the Teams meeting transcript.
- [ ] The evening before each day: open that day's anchor in VS Code, Run All, and save it with outputs, so a cell that fails live still has yesterday's output on screen. `~/.venvs/cg-dxp/bin/python research/scripts/notebooks/smoke.py --full dayN` is the terminal check of the same cells (Day 4 needs the Airflow stack started).
- [ ] `quick_diagram()` downloads mermaid-cli through npx the first time: render one diagram on the office network before Monday.
- [ ] Screenshots to collect from CG beforehand if possible: the Databricks catalog view of a `training_<user>` schema, the Airflow UI of a vended Astro deployment, Harness pipelines and a run, a Datadog monitor. Used on Days 2 and 4 when live access is not available.

## Learner onboarding (send the week before; verify on Monday morning)

What learners need before Monday, in the order the training repository's `GETTING_STARTED.md` gives it:

1. **Catalyst plugin in VS Code**: user settings `chat.plugins.enabled`, `chat.useAgentSkills`, and `chat.plugins.marketplaces` pointing at `https://github.com/cg-open-itg/catalyst.git`; reload; `/plugins`; enable AI Catalyst. Proof: typing `/ai-catalyst` in Copilot Chat lists the skills. Needs membership of the GitHub team that can see `cg-open-itg`; "repository not found" means an access request, not a settings problem.
2. **Docker Desktop** with the `CPZ_INF_BB00000003_Docker_Desktop_User` role; Windows laptops in Linux-containers mode.
3. **The training repository** `cg-open-itg/edo-training-data-products` cloned and opened with **Dev Containers: Reopen in Container**; the first build takes minutes.
4. **Databricks**: `mise run setup:databricks` (browser OAuth), then `dpc-check` green. Proof: a screenshot of `dpc-check`.
5. **GitHub access** to the repository (needed again on Day 5).

Ask for one reply per learner: a screenshot of `/ai-catalyst` in Copilot Chat and of `dpc-check`. Whoever has not replied by Friday gets a platform-support contact before Monday.

## Monday 08:30–09:00 and the first break

- [ ] Walk the room: Copilot Chat answers, `/ai-catalyst` lists skills, the dev container is open. Anyone blocked on access raises it now; the platform support contact is in the room or on Teams.
- [ ] Table layout: three or four per table, paper and pens on every table, one whiteboard visible from everywhere.
- [ ] Projector: the run sheet and the activity cards render at a readable size; dark-on-light terminal theme, 16-point font.
- [ ] Teams channel for the cohort: post the day's links (agenda, challenge paths, the two Catalyst commands) at the start of each day.

## After each day

- [ ] Collect the artefacts the run sheet names (product notes, transcripts, PRDs, contracts, generated code, questions). Learners keep their own; the instructor keeps one example per table for the next day's demo.
- [ ] Reset the demos touched that day: `rm -rf` the `warehouse/` folders under `courseware/*/demos/*/` if you want a clean first run; `bash run.sh stop` for Airflow. The scripts rebuild everything.
- [ ] Note what ran over or under in the run sheet's margin; adjust the next day's flex rows.
