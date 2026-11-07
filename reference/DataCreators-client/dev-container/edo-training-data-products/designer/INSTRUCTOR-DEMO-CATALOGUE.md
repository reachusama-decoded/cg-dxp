# Initial instructor-demo catalogue

Status: partial. Four dbt stories have real DuckDB captures; the eight Docker/Airflow definitions remain blocked draft contracts. Current evidence and candidate links are in root devc.md and instructor-demos/README.md. Reconcile these
task IDs against the current challenges/v2/manifest.json before implementation.
The learner challenge remains the authority for exact instructions and outputs.

## Three pilots and twelve initial stories

`Main` identifies the initial curated subset: three of twelve stories (25%).
It is a selection of stories, not a fraction of course pages. Selection can change
after pedagogical review; preserve stable IDs. All twelve belong in the demo book
once captured and reviewed. Complete stories can span multiple pages.

| Story ID | Teaching outcome and key frames | Current task mapping | Main |
|---|---|---|---|
| docker-image-to-shell | Pull/inspect image → open real interactive shell → inspect filesystem/Python → exit and explain container/image state. | docker-p1-01, docker-p1-02 | Yes; pilot |
| docker-container-lifecycle | Run one-shot workload twice → observe actual running/exited/removed states as appropriate → show image reuse and scoped cleanup. | docker-p1-01, docker-p1-05 | No |
| docker-bind-mounted-data | Inspect source file → bounded read-only mount → run app against mounted data → explain changed input without rebuilding. | docker-p1-03 | No |
| docker-build-holdings-app | Inspect valid stub → author Dockerfile → build/run → verify six holdings and portfolio total → inspect command/workdir. | docker-p1-04, docker-p1-05 | No |
| dbt-build-and-inspect | Inspect declared input grain → seed/build an explicitly identified instructor-completed project → independently query fund exposure and verify results. | dbt-p1-01 through dbt-p1-05 | Yes; pilot |
| dbt-sources-refs-and-sql | Source definition → staging source() → mart ref() → compiled SQL and available lineage → explain dependency ordering. | dbt-p1-02, dbt-p1-03, dbt-p1-04 | No |
| dbt-test-failure-and-repair | Introduce task-aligned invalid input/key → run applicable test → read actual diagnostic → repair → prove correct data as well as green tests. | dbt-p1-05, dbt-p2-03 | No |
| dbt-fanout-and-replay | Observe join fan-out → repair grain/reconcile → changed-batch incremental build → replay same input → verify no duplicate effect. | dbt-p2-01 through dbt-p2-04 | No; may split into two stories |
| airflow-trigger-graph-and-log | Trigger fresh instructor-installed DAG → observe graph/run/task states → inspect relevant dbt task log → verify business output/receipt. | airflow-p1-02, airflow-p1-03, airflow-p1-05 | Yes; pilot |
| airflow-locate-task-evidence | Navigate from run to task → read failed/successful command and context → identify execution environment → connect log to independent output. | airflow-p1-03, airflow-p1-05, airflow-p2-04 | No |
| airflow-quality-blocks-publication | Establish success → remove old receipt → introduce documented fail-quality drill → observe actual quality failure and blocked publish → verify no new receipt. | airflow-p1-04 | No |
| airflow-recover-and-replay | Remove documented defect → rerun → verify output/run-bound receipt → bounded replay → compare input/output identities → short incident handoff. | airflow-p1-04, airflow-p2-01 through airflow-p2-05 | No; may split |

Ranges in this table are shorthand for planning. Each executable definition must
list its actual task IDs individually. A compact story does not claim to teach
every task in a mapped phase, and a mixed-phase story must identify advanced steps.

## First pilot checkpoints

### docker-image-to-shell

1. Developer/dev-container prompt, current Docker context and image reference.
2. Pull result and recorded image digest; no story container started by the pull.
3. Interactive container entry, with a visible DEMO CONTAINER context label.
4. Actual filesystem and Python inspection; describe container user-space and
   shared kernel accurately without using hostname alone as proof of isolation.
5. Exit, inspect the declared removal/lifecycle behavior and remaining image.
6. Closing question: what is shared, and what differs, between two containers
   started from this image?

Use actual task commands and a run-scoped container name. For `--rm`, verify the
named container is absent after exit. For retained containers, show their real
state; captions must match the flags actually used.

### dbt-build-and-inspect

Use an explicitly instructor-completed copy for a compact build tour; the fresh
starter is not necessarily the completed mart. Identify the selected adapter and
profiles, execute the build, then independently query the resulting relations.
Current v2 Phase 1 documents five holdings and fund exposure A:150/B:100/C:0;
confirm those values from the current fixture/contract. Do not reuse the older
v4 customer/order fallback figures as if they describe this project.

Separate connected Databricks and DuckDB recordings if both routes are offered.
The environment being live does not make every story a connected warehouse run.

### airflow-trigger-graph-and-log

Use a real scheduler/worker/UI route for this UI pilot. Bind the DAG to the copied
workspace and correct dbt executable; trigger a new run and inspect its graph,
actual task states and a useful log excerpt. Independently verify the business
result and publication receipt are bound to this run. Explain Airflow task order
versus dbt model order. A separate local dag.test() story can be useful, but cannot
stand in for the UI pilot.

## Expansion after pilots

Prioritize learner confusion, repeated classroom actions and failure diagnosis.
Further candidates are Git conflict/repair, Databricks CLI object discovery,
Docker build targets/runtime user, dbt join diagnosis, Astro worker boundaries,
Atlas output validation and optional Kafka event/replay. Keep optional/advanced
stories clearly marked. Catalyst stories require actual supported invocation and
an explicit audience/task mapping; historic screenshots do not prove a new run.

Use one main concept per story, normally four to eight checkpoints. Split a long
sequence rather than reducing frames until commands become unreadable. Record
estimated teaching duration separately from measured execution time; neither is
a measured junior-learner challenge completion time.

## Per-story acceptance

- Current task/concept IDs, route, runtime and source fixture hashes recorded.
- Real actions, fresh state and independently checked relevant outcomes.
- Captions state action plus what to notice; context labels are accurate.
- Intentional failures are recognizable and followed by observed repair where
  the story promises repair.
- Frames are readable at printed size; video uses the same events/caption data.
- Exact commands, transcripts and portable assets packaged.
- Reviewer verdict and cleanup recorded; blocked stories remain visible in the
  catalogue and are excluded from a success-labelled published story sequence.
