# Risks and fallbacks

[Data Creators › instructor pack — risks and fallbacks]{.breadcrumb}

One rule covers most of this page: a demo that fails live is not repaired live. Show the output saved in the anchor notebook from the day-before run, say what the room would have seen, move on, and fix it at the break. The learners' challenges carry the practice; the demos only set it up.

## Learner access and environment

| Risk | Signal | Fallback |
|---|---|---|
| Catalyst plugin not visible in Copilot Chat | `/ai-catalyst` lists nothing; "repository not found" on the marketplace | An access request to the GitHub team, not a settings change. Pair the learner with a neighbour for Day 1; Day 1's artefacts are shared at the table anyway. |
| Dev container will not build or open | Reopen in Container fails; the first build takes more than fifteen minutes | Keep working on the host for Day 1 (nothing needs the container until Day 2 afternoon). Platform support contact in the room or on Teams from 08:30. |
| Databricks setup incomplete | `dpc-check` red; `echo $DBT_CATALOG` empty | Cold start: `mise run setup:databricks`, a new terminal, then `astro dev restart --wait 5m` on Day 4. Until it works, the learner follows a neighbour's screen and reads the compiled SQL. |
| Docker Desktop on a Windows laptop in the wrong mode | Linux containers unavailable | Switch to Linux containers (Docker Desktop menu); if the role is missing, the Docker challenge is done in pairs on a working laptop. |
| Learners cannot push branches to the training repository | `git push` is refused with a permissions error | The optional Day 2 Git practical stops at the local log (branch, commit, `git log --graph`); the push and the pull request are the instructor's demo on screen. Ask the platform team before the day. |
| Astro started before Databricks setup | Cosmos import error ending in an empty catalog name | The cold-start fix above. Say it before the challenge starts and put it on the whiteboard. |
| Two Astro environments on one laptop | Port clash; the wrong UI opens | `docker ps`, stop the stray project, `astro dev start` again. |
| Transient Databricks errors on Day 5 | "Error during request to server" | Retry. If it persists for a table, compare their numbers with the expected results in the Day 5 anchor and carry on. |

## Instructor laptop and demos

| Risk | Signal | Fallback |
|---|---|---|
| Docker Desktop not running | `docker info` fails; Day 2 Docker demo and Day 4 Airflow stack cannot start | Start Docker Desktop first thing; the pre-flight has it. The Docker demo's steps are also screenshots in the anchor from the day-before run. |
| Airflow stack slow or stuck on Day 4 morning | `run.sh status` shows no run or a queued task for minutes | Start the stack before 08:30. Show the previous green run's status and log cells; the learners' practical does not depend on the instructor stack. |
| Spark demo cannot start | Java not found; `JAVA_HOME` wrong | `source common/env/activate.sh` sets it to the Homebrew OpenJDK 17. If it still fails, the Spark diagram and the saved plan output carry the point. |
| Mermaid `quick_diagram()` cannot download mermaid-cli | npx hangs on an office network | Draw on the whiteboard or in Excalidraw; the prepared diagrams are PNGs and need nothing. |
| A Claude generation goes wrong or slow live | Long thinking, a wrong skill, a flat network | Open the prepared artefact in `courseware/common/running-example/` and review it as if it had just been generated; the review is the lesson. |
| A DuckDB file is locked | "Could not set lock on file" | A notebook kernel or a dbt process still holds it: restart the kernel, or `pkill -f dbt`. The scripts rebuild every warehouse from seeds. |
| Google Drive path with spaces | A script fails on an unquoted path | All scripts quote their paths; if a new command fails, wrap the path in quotes or `cd` first. |

## Guests and people

| Risk | Signal | Fallback |
|---|---|---|
| A guest does not come (sponsor, platform team, bitemporal, Harness) | No confirmation by the evening before | Each slot has an instructor-led version in the anchor: the whiteboard script, the diagram and the demo. Run it as the plan says and keep the slot's questions for a later guest. |
| A guest runs long | Past the slot by ten minutes | Thank them, take two questions, and cut the next block's flex (every run sheet row names what to drop). |
| Extra attendees on Day 5 | People who were not in the week turn up for the capstone | Name cards, a table of their own, pair them with a team for the discovery hour; they can follow Phase 1 at their own pace. |
| Mixed experience in the room | Some have used dbt or Airflow in production, some never | Ask on Day 1 and write the names down; give the experienced the stretch tasks and the Day 4 morning teaching slots; sit them with beginners during practicals. |
| Nobody talks in the whiteboard sessions | Silence after the first question | Ask a table, not the room; take the first answer and write it up; the anchors carry the answers rooms usually give, so add the missing ones yourself. |

## Time and content

| Risk | Signal | Fallback |
|---|---|---|
| Day 1 overruns on discovery | The PRD comparison has not happened by 11:30 | Cut the lifecycle exploration to a ten-minute demo and run the interview activity in the afternoon as planned; the data contract can slip to Day 2 morning. |
| Day 2 platform block runs long | Still on Spark at 11:15 | Stop at the tools-together diagram; the Docker challenge needs the full slot. The scheduled-run diagram returns on Day 4. |
| Challenge 02 unfinished at the Day 3 regroup | Few pairs past C7 | Regroup anyway; show the build on the instructor copy; pairs finish the marts after the recap. Phase 1 of challenge 03 only needs the seeds. |
| Day 4 practical blocked by environments | Half the room on the cold-start fix at 11:15 | Run the controlled failure on the instructor stack for everyone, then give the failure-note exercise the prepared example. |
| Day 5 teams still in discovery at 10:30 | No `dbt seed` yet | Call time. The discovery worksheet is complete when the consumer-backwards map and four STTM rows exist; the rest is the build. |
| Day 5 Phase 1 not done by 14:00 | A team on domain-aligned models | The day ends when Phase 1 is done; presentations move to 14:45 and the other teams start Phase 2. Nobody is handed a solution; circulate with the section notes. |

## Data and safety

| Risk | Signal | Fallback |
|---|---|---|
| A learner pastes real data or a token into a chat | Visible in a shared screen | Stop, delete the chat, say the rule again. All example data this week is synthetic. |
| The courseware repository is pushed somewhere public | A link that opens without login | It holds client material and recordings; it stays private. Share the courseware folder and the prompt library with learners as files, not as the repository. |
