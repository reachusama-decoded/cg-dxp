# airflow: Phase one — certified

**Optional small-fixture follow-up.** The assigned course route is the supplied Portfolio Analytics pipeline on dbt-databricks/Astro. This preserved fixture supports separate further practice and its original command contract; it is not a second mandatory assignment.

This phase has a fixed core of 5 tasks. The minimum standard is a working result with the underlying tool concepts explained. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

## Prerequisites and workspace

Prepared Airflow3.1.0/standard provider1.8.0 runtime and a separate dbt executable selected with V2_DBT_BIN. Astro UI route needs instructor-bound isolated workspace.

From the project root run:

```bash
python3 scripts/challenge-v2.py prepare airflow phase-one-certified
cd .local/challenges-v2/airflow/phase-one-certified
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

## Local tool preparation

The instructor runs `bash scripts/setup-v2-tools.sh` once from the project root. Before changing into your copied workspace, activate `.local/v2-tools/bin/activate` to make the pinned `dbt` executable available. For Airflow, use `.local/v2-airflow/bin/python` with a workspace-specific `AIRFLOW_HOME`; do not mix these two Python environments. The verifier supplies these paths automatically in a fresh copy.

## Starter behavior

Phase 1 python pipeline.py prints scaffold status. Phase 2 actual DAG imports and supplied project builds; fail-quality is absent until your documented drill.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter airflow phase-one-certified --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

## Timeline and completion standard

Core estimate: **75–110 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

| Task | Outcome | Minutes | Evidence |
|---|---|---|---|
| airflow-p1-01 | Inspect a prepared orchestration baseline | 15–22 | Show the prepared project result A: 150 / B: 100 / C: 0 |
| airflow-p1-02 | Author a small Python DAG with real dbt tasks | 15–22 | Import the actual DAG using DagBag and inspect task IDs and edges |
| airflow-p1-03 | Demonstrate the dependency graph and manual run | 15–22 | The run must execute dbt and finish success |
| airflow-p1-04 | Inspect a controlled task failure | 15–22 | Intentional failure: the quality drill raises Intentional quality drill and publish must not create a receipt |
| airflow-p1-05 | Explain the run and environment boundaries | 15–22 | Core evidence includes the executed run and business output |

## Core challenges

### airflow-p1-01: Inspect a prepared orchestration baseline {#airflow-p1-01}

#### Concept: airflow-p1-01-concept — Inspect a prepared orchestration baseline

An Airflow DAG declares dependencies between task executions. dbt declares model dependencies within a transformation project. These graphs are related but have different responsibilities: Airflow decides when stages run, while dbt decides how model references are ordered.

<!-- instructor-demo: airflow-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Run python pipeline.py in the starter to see the valid scaffold message. Inspect the prepared project/ and run its dbt seed/build in a fresh workspace. Draw prepare→build→quality→publish before writing the DAG.

#### Hint

The dbt baseline is already solved; authoring it again is outside this phase.

#### Check

Show the prepared project result A: 150 / B: 100 / C: 0. Explain which graph orders tasks and which graph orders SQL models. The scaffold message is not an Airflow run.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### airflow-p1-02: Author a small Python DAG with real dbt tasks {#airflow-p1-02}

#### Concept: airflow-p1-02-concept — Author a small Python DAG with real dbt tasks

TaskFlow functions become Airflow tasks through decorators. Executing a subprocess inside a task can run dbt directly and fail the task when dbt fails. A small graph is enough to prove scheduling and dependencies without requiring a full Cosmos project reconstruction.

<!-- instructor-demo: airflow-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Replace pipeline.py with an Airflow3.1 SDK DAG: schedule=None, catchup=False, bounded retries and four tasks. prepare seeds project/, build runs models, quality runs tests, publish writes a receipt only after quality. Use subprocess.run with check=True. In quality, check whether the workspace file fail-quality exists; if so raise ValueError describing the intentional drill before running dbt test.

#### Hint

Import dag/task from airflow.sdk. Use absolute project/profile paths derived from the file directory; V2_DBT_BIN selects the prepared executable. The company Astro runtime rejects a DAG without the tags `usage-id:AA00002933` and `cost-center:52415`, so set `tags=[...]` on `@dag` if you will run it there.

#### Check

Import the actual DAG using DagBag and inspect task IDs and edges. Syntax-only checks are supporting evidence. Record any import error before trying a live run.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### airflow-p1-03: Demonstrate the dependency graph and manual run {#airflow-p1-03}

#### Concept: airflow-p1-03-concept — Demonstrate the dependency graph and manual run

A manual run is a specific DAG-run instance with its own task states. schedule=None means Airflow does not create periodic runs automatically; it does not prohibit manual execution. Seeing all tasks green without checking their output would miss a command that ran against the wrong project.

<!-- instructor-demo: airflow-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

In the isolated Airflow runtime import the DAG, run dag.test() or trigger the instructor-installed DAG in Astro, and inspect the four task states and dbt logs. Capture the run ID and result.

#### Hint

Keep AIRFLOW_HOME in this copied workspace. Do not initialize or migrate a shared instructor metadata database.

#### Check

The run must execute dbt and finish success. Independently inspect fund_exposure in the workspace database and match A: 150 / B: 100 / C: 0. A parsed DAG alone cannot pass this live/local execution gate.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### airflow-p1-04: Inspect a controlled task failure {#airflow-p1-04}

#### Concept: airflow-p1-04-concept — Inspect a controlled task failure

Task logs tell you which command and input failed; downstream state shows whether the dependency blocked publication. A failed data-quality task must not produce a new success receipt. Understanding that boundary is a minimum operational skill even before advanced retry/replay work.

<!-- instructor-demo: airflow-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

After one success remove the receipt, create fail-quality, and rerun the same prepared DAG. Inspect the expected ValueError and the quality/publish states. Remove the marker and repeat the run.

#### Hint

The marker is the documented intentional failure switch. Keep the rest of the starter/project valid.

#### Check

Intentional failure: the quality drill raises Intentional quality drill and publish must not create a receipt. After removing the marker, quality and publish succeed and a new receipt exists.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### airflow-p1-05: Explain the run and environment boundaries {#airflow-p1-05}

#### Concept: airflow-p1-05-concept — Explain the run and environment boundaries

A local Dag.test run proves task execution in the isolated environment; an Astro UI check proves an additional container/runtime integration. Neither proves remote Databricks access unless the tasks actually used that adapter. Honest evidence binds a run to its environment and output.

<!-- instructor-demo: airflow-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Write a handoff with DAG graph, task/log evidence, result rows, run ID and whether execution was local DuckDB or Astro/Databricks. Explain manual scheduling and why publication depends on tests.

#### Hint

Use the instructor runtime only when configured for this workspace and unique DAG ID.

#### Check

Core evidence includes the executed run and business output. Record Astro UI/connected verification separately if unavailable. Phase 2 starts from this supplied solved DAG, so it can be entered independently.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

## Executing your local DAG

From the project root, `python3 scripts/challenge-v2.py verify airflow phase-one-certified --workspace .local/challenges-v2/airflow/phase-one-certified` copies your work and executes its actual Airflow DAG. It prepares an isolated metadata database, serializes the DAG with `airflow dags reserialize`, then checks a success, marker-induced failure, repair and replay. Inspect the printed task logs and business-result assertions. This avoids mutating an instructor metadata database. The Astro UI exercise still needs the prepared container runtime.

## Phase completion

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

```bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify airflow phase-one-certified --workspace .local/challenges-v2/airflow/phase-one-certified --mode offline
```

Execution boundary: Airflow local Dag.test execution; Astro UI and connected adapter gates separate. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

## Optional stretch

Try a small variation after completing the core: change one input or contract condition in a second disposable copy, predict the result, and verify your prediction. This does not replace a core task or contribute to its timing budget.
