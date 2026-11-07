# airflow: Phase two — proficient

**Optional small-fixture follow-up.** The assigned course route is the supplied Portfolio Analytics pipeline on dbt-databricks/Astro. This preserved fixture supports separate further practice and its original command contract; it is not a second mandatory assignment.

This phase has a fixed core of 5 tasks. The advanced standard is a justified design or repair, actual behavioral proof, and a useful handoff. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

## Prerequisites and workspace

Prepared Airflow3.1.0/standard provider1.8.0 runtime and a separate dbt executable selected with V2_DBT_BIN. Astro UI route needs instructor-bound isolated workspace.

From the project root run:

```bash
python3 scripts/challenge-v2.py prepare airflow phase-two-proficient
cd .local/challenges-v2/airflow/phase-two-proficient
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

## Local tool preparation

The instructor runs `bash scripts/setup-v2-tools.sh` once from the project root. Before changing into your copied workspace, activate `.local/v2-tools/bin/activate` to make the pinned `dbt` executable available. For Airflow, use `.local/v2-airflow/bin/python` with a workspace-specific `AIRFLOW_HOME`; do not mix these two Python environments. The verifier supplies these paths automatically in a fresh copy.

## Starter behavior

Phase 1 python pipeline.py prints scaffold status. Phase 2 actual DAG imports and supplied project builds; fail-quality is absent until your documented drill.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter airflow phase-two-proficient --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

## Timeline and completion standard

Core estimate: **90–120 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

| Task | Outcome | Minutes | Evidence |
|---|---|---|---|
| airflow-p2-01 | Define bounded replay and input identity | 18–24 | Both runs must produce three fund rows/250 and matching per-fund values |
| airflow-p2-02 | Inject failure and observe useful retry behavior | 18–24 | Show the failed task and blocked publication, then repaired quality and published receipt |
| airflow-p2-03 | Prove output correctness after recovery | 18–24 | Correct final state is A: 150 / B: 100 / C: 0, one row per fund, successful quality and a receipt for the repaired run |
| airflow-p2-04 | Use Astro UI to make an operational decision | 18–24 | Retain run/task identifiers and a description of the relevant log/state evidence |
| airflow-p2-05 | Write a short incident handoff | 18–24 | The handoff must explain blocked publication and correct recovered output |

## Core challenges

### airflow-p2-01: Define bounded replay and input identity {#airflow-p2-01}

#### Concept: airflow-p2-01-concept — Define bounded replay and input identity

Replay should state which input and run are repeated. A fixed training fixture makes it possible to distinguish pipeline idempotency from changing business data. max_active_runs=1 reduces overlap for this small exercise but does not automatically provide exactly-once behavior.

<!-- instructor-demo: airflow-p2-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Inspect the supplied solved DAG and project. Define the fixture version and expected output in an incident note. Trigger two distinctly identified runs against the same baseline and compare the output.

#### Hint

Use fresh run IDs; do not broadly clear every historical run.

#### Check

Both runs must produce three fund rows/250 and matching per-fund values. Record run IDs and explain which state is replaced by dbt materialization.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### airflow-p2-02: Inject failure and observe useful retry behavior {#airflow-p2-02}

#### Concept: airflow-p2-02-concept — Inject failure and observe useful retry behavior

A retry repeats a failed task according to an explicit policy. It cannot repair permanently bad input by waiting. This drill uses a marker-controlled transient quality failure so you can explain when to retry, when to repair, and why downstream publication must remain blocked.

<!-- instructor-demo: airflow-p2-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Set a bounded retry count/delay, create fail-quality, trigger the run and inspect the failed/retrying task in logs and the prepared Astro UI. Remove the marker according to the instructor drill, then retry only quality for that run.

#### Hint

In a pure Dag.test rehearsal the persistent marker may exhaust retries. Record that behavior honestly; the UI recovery drill is a separate runtime check.

#### Check

Show the failed task and blocked publication, then repaired quality and published receipt. Record attempts/run identity. Do not mark the task successful manually as a substitute for rerunning the test.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### airflow-p2-03: Prove output correctness after recovery {#airflow-p2-03}

#### Concept: airflow-p2-03-concept — Prove output correctness after recovery

A recovered task state is useful only if the output is correct and publication matches the intended run. Stale tables can fool a verifier when a command was skipped. Compare the independently expected values and receipt identity after the repaired run.

<!-- instructor-demo: airflow-p2-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

After recovery inspect fund_exposure and receipt.json. Run the graph again with the same input and compare all fund rows. Explain which commands seed, materialize and test rather than relying on previous tables.

#### Hint

The supplied expected total is250, but use per-fund values too. Delete the old receipt before the failure drill.

#### Check

Correct final state is A: 150 / B: 100 / C: 0, one row per fund, successful quality and a receipt for the repaired run. Show unchanged output after another replay.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### airflow-p2-04: Use Astro UI to make an operational decision {#airflow-p2-04}

#### Concept: airflow-p2-04-concept — Use Astro UI to make an operational decision

The UI supports investigation through task state, logs, graph and run details. Opening the interface alone is not advanced proficiency. The useful decision is whether the failure is a stale input, connection issue, code defect or an intentional drill, and which scope should be rerun.

<!-- instructor-demo: airflow-p2-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

In the prepared local Astro deployment locate this isolated DAG/run, inspect quality logs and the dependency graph, and write the specific repair/rerun decision. If Astro is unavailable, perform local execution and record the UI gate blocked.

#### Hint

Instructor setup binds the v2 workspace project and unique DAG ID into Astro; do not deploy infrastructure to finish the exercise.

#### Check

Retain run/task identifiers and a description of the relevant log/state evidence. A hosted Astronomer route is optional and requires prepared access.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### airflow-p2-05: Write a short incident handoff {#airflow-p2-05}

#### Concept: airflow-p2-05-concept — Write a short incident handoff

A runbook entry links symptom, impact, repair, verification and escalation. It should tell another operator how to reproduce the bounded check without clearing unrelated runs or exposing credentials. Advanced skill is demonstrated by a defensible operational decision with output proof.

<!-- instructor-demo: airflow-p2-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Write incident.md documenting the marker failure, affected run/tasks, diagnosis, exact repair, scoped replay and result. Include the prepared runtime boundary and remaining access findings.

#### Hint

Separate the cause from the symptom; state why retry alone did not remove the persistent marker.

#### Check

The handoff must explain blocked publication and correct recovered output. Optional stretch: connect an existing neutral alert transport or prepared Datadog monitor and demonstrate an actionable observation; configuration text alone is insufficient.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

## Executing your local DAG

From the project root, `python3 scripts/challenge-v2.py verify airflow phase-two-proficient --workspace .local/challenges-v2/airflow/phase-two-proficient` copies your work and executes its actual Airflow DAG. It prepares an isolated metadata database, serializes the DAG with `airflow dags reserialize`, then checks a success, marker-induced failure, repair and replay. Inspect the printed task logs and business-result assertions. This avoids mutating an instructor metadata database. The Astro UI exercise still needs the prepared container runtime.

## Phase completion

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

```bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify airflow phase-two-proficient --workspace .local/challenges-v2/airflow/phase-two-proficient --mode offline
```

Execution boundary: Airflow local Dag.test execution; Astro UI and connected adapter gates separate. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

## Optional stretch

See the [stretch index](stretch/README.md). Each route has its own prerequisites, timing and completion check; none is part of this fixed core.
