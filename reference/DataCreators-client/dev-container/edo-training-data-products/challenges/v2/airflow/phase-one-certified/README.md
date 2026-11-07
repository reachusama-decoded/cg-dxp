# airflow: Phase 1 — foundations

## Purpose and outcome

Orchestrate the same Portfolio Analytics product you transformed on Wednesday. Airflow orders source readiness, dbt transformation, quality verification and a publication-evidence step; Databricks still computes and stores the business data. The prepared dbt project prevents this from becoming a second complete modeling exercise. Your authored outcome is a small scheduled workflow whose task relationships and results can be explained.

## Dataset and pipeline

The copied project contains six raw feeds and two supplementary Portfolio Analytics CSVs. The modeled result has four funds on each of two May dates. Each dbt build refreshes the complete tiny fixture graph; the run's explicit business partition selects four fund/date rows for its receipt. This distinction is deliberate: changing a receipt label is not a claim that dbt processed only that date. Logical schedule time and the historical fixture business date are separate concepts.

The four tasks are source_ready, dbt_build, quality and publication_evidence. The readiness task checks raw populations and extraction-time freshness. The build invokes the delivered worker dbt executable. Quality compares actual warehouse output with independent copied-CSV calculations. The last step records checked output for an exact run and partition. A failed quality task must prevent that receipt. Data remains in Databricks; only small control information belongs in task messages.

## Prerequisites and workspace

Use the prepared Astro project, delivered connection setup and approved Databricks namespace. The terminal must have dbt-databricks access and the worker must receive credentials at task execution. Discover actual mounts and executable versions; the terminal's Python environment is not proof of the worker's environment. Set an owned relation prefix and use the matching DAG identifier, generated from that prefix, so simultaneous learners remain isolated.

```bash
mise run challenge:v2:prepare airflow phase-one-certified
cd .local/challenges-v2/airflow/phase-one-certified
export DC_RELATION_PREFIX=dc_alex_air01
```

Run direct dbt preparation inside the copied project subdirectory. Restore or record a timestamp-only extraction refresh before seeding when the supplied historical timestamps are stale; the May business dates must remain unchanged. From the attempt root, use the runtime staging helper with the actual Astro project root. It refuses an existing owned destination and writes ownership metadata needed by the DAG. Never stage into another learner's prefix or assume any terminal directory is mounted into the worker.

## Starter behavior

The DAG file contains deliberate authoring gaps in dbt invocation, publication evidence or dependency wiring. Static compilation checks Python syntax but completion verification rejects these unfinished outcomes. Importing the unstaged file can fail because ownership metadata is not yet available; first prepare the owned stage as documented, then inspect the actual worker import. The dbt project is a disclosed solved baseline. Use it to understand the product and avoid changing its business logic while diagnosing Airflow. Unavailable scheduler, mount or warehouse access remains a pending prerequisite rather than a reason to substitute a local no-op DAG.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 75–110 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [airflow-p1-01: Inspect a prepared orchestration baseline](#airflow-p1-01) | 15–22 | Actual mount/executable identities, owned namespace and supplied-vs-authored inventory |
| [airflow-p1-02: Author a small Python DAG with real dbt tasks](#airflow-p1-02) | 15–22 | Four meaningful tasks with explicit paths, target and actual warehouse checks |
| [airflow-p1-03: Demonstrate the dependency graph and scheduled run](#airflow-p1-03) | 15–22 | Readiness → build → quality → evidence; fresh scheduled task identities |
| [airflow-p1-04: Inspect a controlled task failure](#airflow-p1-04) | 15–22 | Quality failed; evidence upstream_failed; no failed-run receipt; repair succeeds |
| [airflow-p1-05: Explain the run and environment boundaries](#airflow-p1-05) | 15–22 | Coherent handoff links run/task IDs, artifacts and independent fund/date output |

## Core challenges


<a id="airflow-p1-01"></a>

### airflow-p1-01: Inspect a prepared orchestration baseline


<a id="airflow-p1-01-concept"></a>

#### Concept


A DAG definition describes tasks and dependencies; the scheduler decides when a run is due, and a worker executes its task code. The terminal that edits the file is another process boundary. Databricks is yet another boundary, executing dbt SQL remotely. A file visible to the terminal may not be mounted in the worker, and a dbt executable on the terminal path may not exist inside Astro. Diagnosing those differences before writing operators prevents a successful local command from becoming misleading run evidence.

The supplied project contains a complete Portfolio Analytics baseline and a partly authored orchestration file. Its root is discovered relative to the staged DAG, while ownership metadata binds the namespace and relation prefix. For example, the worker must find the staged project directory, its profiles and an artifact directory it can write, not a path copied from your laptop. The same approved warehouse and schema must be reached by terminal seeding and worker transformations. Source presence and a running scheduler do not prove either mount correctness or database permission. The inspection task records those prerequisites explicitly without pretending that setup alone demonstrates orchestration competence.

#### Challenge


Inspect the copied DAG and project before filling its gaps. List the four task responsibilities, the supplied dbt models and the exact learner-authored DAG paths. Read the delivered Astro Dockerfile and compose mount configuration, then record the actual running mount when the prepared environment is available. Identify the intended worker dbt executable, project/profiles directories and artifact locations. Keep measured versions distinct from source-configured expectations.

Prepare the supplied seeds through the terminal's Databricks profile in the project subdirectory and record the approved namespace/prefix used. Stage only this owned attempt into the actual Astro mount using the helper; inspect its ownership metadata without copying token values. Identify what happens if that stage does not exist or uses an already occupied prefix. If Astro or credentials are unavailable, write the source-backed boundary inventory and mark actual mount, worker and warehouse checks pending. Continue reading the prepared graph rather than constructing an unrelated local fixture.

#### Hint


<details>
<summary>Follow the staged path across the worker boundary</summary>

Follow the DAG's root-path expression and the stage helper's output together. The ownership file should agree with the terminal source-loading namespace. Inspect the worker executable inside the actual container rather than assuming a shell activation also affects it. Keep configuration probes separate from secrets: names, paths and redacted identities are useful evidence, while a token is not. A missing mount is a preparation problem, not a SQL defect.

</details>

#### Check


Inspect the actual mount, worker executable/version and owned stage when connected. The stage should contain the copied project, profiles, runtime helper, ownership metadata and writable artifact/evidence locations. Terminal and worker namespace identities must agree, and the raw input counts must match the supplied contract. Record which files are solved supporting assets and which orchestration functions remain unfinished.

Run static compilation locally to identify syntax errors without claiming a worker import or scheduled result. The untouched completion verifier should reject declared DAG gaps rather than accept the prepared dbt project as your solution. Explain why a terminal folder and a running scheduler cannot establish worker visibility, and why two learners need distinct prefixes/DAG identities even inside one approved schema. Retain source-backed paths and measured runtime observations in separate fields. If a probe cannot run, leave that individual prerequisite pending; do not fill it with the intended Dockerfile value.

```bash
python runtime/lab.py static .
# Stage only after the approved namespace and actual Astro root are prepared.
python runtime/lab.py stage-astro . --astro-root "$DC_ASTRO_ROOT"
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#airflow-p1-01-reasoning)


---


<a id="airflow-p1-02"></a>

### airflow-p1-02: Author a small Python DAG with real dbt tasks


<a id="airflow-p1-02-concept"></a>

#### Concept


An operator executes work; the task identifier is only the name Airflow uses to track that execution. A task called dbt_build that prints a message does not build a data product. The prepared PythonOperator route invokes the delivered dbt executable with explicit project, profile, target and artifact paths. Its exit status and artifacts then connect task state to actual Databricks model and test results. Airflow controls ordering while dbt controls the transformation graph.

The publication-evidence step has a narrower classroom meaning than production release. It checks the consumer output, selects the run's four fund/date rows and writes a receipt tied to run identity, input hashes and the shared contract. A successful no-op marker would be insufficient because it could exist without any correct warehouse result. A small partition identifier can be passed between tasks, but holdings data itself stays in Databricks rather than being copied through XCom. This boundary makes the DAG easier to reason about and prevents a green graph from becoming the only evidence of business correctness.

#### Challenge


Complete the declared gaps in the copied DAG's worker function. The build branch must run the actual dbt build with the prepared project/profile directories, airflow target and writable artifact path. The evidence branch must independently check warehouse output, select the configured business date, and write a run-specific receipt under the owned stage. Retain the supplied readiness and quality helpers, reviewing their contracts before changing them.

Use the generated owned DAG identity, timezone-aware start date, two-minute classroom schedule, one active run and explicit fixture partition. Keep catchup disabled for this bounded rehearsal. Set task-time connection templating rather than copying a terminal token into source. Compile the Python file and inspect the worker import after staging. Do not replace the prepared dbt graph with shell echoes or create an external publication operation to make the last task sound more realistic. Document each authored branch and the supplied behavior it relies on.

#### Hint


<details>
<summary>A task name is not evidence that its work executed</summary>

Trace the subprocess command from executable through target and target-path flags. The worker should use its own delivered dbt environment, not the interpreter running the authoring shell. For receipts, use the actual run identifier in the filename and the independently checked partition result in its body. Review the difference between a callback logging a failure and an operator that performs transformation work; they serve different purposes.

</details>

#### Check


Static inspection must show four meaningful task branches and reject any remaining unfinished marker. In the prepared worker environment, verify that the DAG imports with the expected identity and that the dbt command resolves its real executable, project, profiles and artifact directories. Actual execution should produce fresh dbt run results and a warehouse-checked receipt; these runtime outputs remain pending until the scheduler and worker run.

Inspect the receipt contract: exact run identity, fixture partition, shared contract hash, copied input hashes, full eight-key output verification and four selected partition rows. Explain why the whole tiny fixture can be refreshed while the receipt describes one business date, and why that should not be called date-filtered ingestion. Retain a selected command and its output rather than treating a successful Python compilation as dbt execution. The final evidence task must fail instead of writing a receipt when its independent query fails. Keep credentials outside source and logs.

```bash
python runtime/lab.py static .
# In the actual staged worker, inspect the imported DAG and delivered dbt version.
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#airflow-p1-02-reasoning)


---


<a id="airflow-p1-03"></a>

### airflow-p1-03: Demonstrate the dependency graph and scheduled run


<a id="airflow-p1-03-concept"></a>

#### Concept


Dependencies state which task must finish successfully before another becomes eligible. They do not themselves move business data or guarantee that the downstream task reads the right relation. The required chain is readiness, dbt build, quality and publication evidence. This protects the receipt from being created before inputs and results have been checked. Leaving a branch disconnected can make a green task appear even when its upstream product work failed.

A manual trigger and a scheduler-created run can execute the same graph, but they establish different things. The manual run can help diagnose code and logs; only the scheduled run proves the configured timetable, scheduler and worker boundary required here. The schedule's logical date/data interval is not automatically the May business partition. Catchup is disabled and the fixture date is explicit. A prior green UI run may belong to old code or another prefix, so record current DAG/run/task identities and the start of this rehearsal. Both the dependency graph and the actual task state transitions matter.

#### Challenge


Complete the graph wiring in the copied DAG so each task depends on its declared predecessor. Inspect the rendered worker graph after staging and identify how a failed quality task blocks evidence. Use a controlled manual trigger only as supporting diagnosis, retaining its distinct run identity. Then unpause only the owned DAG for a bounded scheduled rehearsal and record a fresh scheduler-created run after your session start.

Inspect readiness, build, quality and evidence task instances in that run. Follow the build log to dbt artifacts and the final receipt to the selected partition output. Confirm the worker is using the current staged source rather than an old imported copy. After collecting the run, pause the owned DAG so the two-minute timetable does not keep generating classroom evidence indefinitely. Do not clear unrelated DAGs, broad date ranges or another learner's tasks to repair a local wiring error.

#### Hint


<details>
<summary>Compare graph edges with the exact current run type</summary>

Read the dependency expression as a sequence of obligations and compare it with the actual graph. An operator can be instantiated without being connected. Check the run type and start timestamp before calling a UI result scheduled evidence. If the expected current task identifiers are missing, inspect staged source and import state before retrying the warehouse. A manual run's success does not answer whether the scheduler produced a new run.

</details>

#### Check


The graph must contain the four required tasks in order, with no evidence task eligible before quality succeeds. For the scheduled run, retain the owned DAG identifier, fresh run identifier, run type, start time and all task states. Its successful dbt artifacts and receipt must correspond to the same run and stage. The full warehouse output contains eight keys; the receipt's selected May partition contains four fund/date rows.

Use the scheduled-evidence command after the controlled failure and repaired runs are available; it checks three distinct scheduler-created identities rather than accepting a historical green graph. Explain the difference between logical schedule interval and explicit fixture business date, and between a manual diagnostic trigger and this acceptance boundary. A missing scheduler/API prerequisite leaves the check pending even if local compilation succeeds. Keep the task-state and product-output evidence linked so a correct SQL query from another attempt cannot satisfy this run's graph evidence.

```bash
mise run challenge:v2:airflow-evidence "$DC_ASTRO_STAGE" --success "$DC_SUCCESS_RUN" --failure "$DC_FAILURE_RUN" --repair "$DC_REPAIR_RUN" --after "$DC_SESSION_STARTED_AT"
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#airflow-p1-03-reasoning)


---


<a id="airflow-p1-04"></a>

### airflow-p1-04: Inspect a controlled task failure


<a id="airflow-p1-04-concept"></a>

#### Concept


A task failure is a state with a cause, not merely a red UI tile. A controlled business-quality fault should fail the quality task after dbt has built its input and prevent downstream evidence. A bad executable path or expired token is a different failure category and should not be counted as the intended quality drill. Reading the first useful log error distinguishes these cases and guides the repair.

The supplied fault marker belongs to your owned stage. While it exists, the quality branch raises its declared teaching failure and the evidence task becomes upstream-failed. The last accepted receipt should remain available, but this failed run must create no new accepted receipt. Removing the marker repairs the controlled cause; rerunning without removing it merely repeats the failure. Retries can repeat transient work, but they cannot turn a permanent business-quality violation into correct data. This small experiment teaches failure propagation and bounded recovery without requiring external alert transports or production deployment.

#### Challenge


After a successful current scheduled run, place the declared quality-fault marker in your owned staged attempt. Wait for or inspect the next fresh scheduled run, then record the quality task's first useful error, task state and downstream evidence state. Confirm there is no receipt for that failed run and preserve the previous successful receipt rather than overwriting it with an ambiguous latest file.

Remove the marker and retain a repaired fresh scheduled run. Compare its warehouse output and partition receipt with the independent baseline expectation. Explain whether retries occurred and why the marker had to be removed for recovery. Keep changes bounded to the copied stage and do not clear unrelated tasks or modify raw fixtures to manufacture a different failure. If a token, path or permission error prevents this sequence, diagnose it as a prerequisite failure and leave the intended quality drill pending.

#### Hint


<details>
<summary>Retain the previous receipt and reject only the failed run</summary>

Name the expected failure message category and task before creating the marker. Inspect the per-run receipt filename instead of relying on whether an evidence directory contains any file. A receipt from the earlier success is legitimate historical evidence for that run; it cannot prove publication for the failed one. Check the upstream-failed downstream state and the quality log together to establish the causal chain.

</details>

#### Check


The failed scheduler-created run must show quality as failed and publication evidence as upstream-failed, with no receipt named for that run. The log should identify the intentional quality marker, not an authentication or missing-file error. After removing the marker, a different fresh scheduled run must succeed and reproduce the expected independent output. Retain the success, failure and repair identities distinctly.

The API evidence checker validates run type, freshness, task states and receipts; inspect the corresponding UI/log readability separately. Explain why repeatedly clearing the quality task without repairing its marker would not recover the workflow, and why a saved successful receipt does not mean the failed run published. Keep source and fixture hashes for the bounded drill so the next reader understands what changed. A no-op callback, a stale green screenshot or a manual local test cannot replace actual scheduled worker failure propagation.

```bash
# Only within the owned stage, create and later remove this teaching marker.
touch "$DC_ASTRO_STAGE/fail-quality"
# Retain the intended failed scheduled run before removing it.
rm "$DC_ASTRO_STAGE/fail-quality"
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#airflow-p1-04-reasoning)


---


<a id="airflow-p1-05"></a>

### airflow-p1-05: Explain the run and environment boundaries


<a id="airflow-p1-05-concept"></a>

#### Concept


Completion evidence connects an executed workflow to a business result a reader can assess. Airflow's run and task identities establish which orchestration instance ran; dbt artifacts identify transformations and tests; an independent warehouse query establishes the intended population and values. None can substitute for all the others. A correct report queried from an old prefix says little about whether your current scheduled worker produced it.

The receipt ties a current run to its selected fixture partition and input hashes, while checking the complete small report. It is useful because the May business date differs from the October timetable. The handoff must distinguish those clocks and explain the build's full-fixture scope. Authentication is another boundary: a terminal login does not automatically make a cached worker connection fresh, and a first successful run does not prove expiry/restart recovery. Describe these unexecuted checks honestly. The classroom evidence step also does not grant consumers access, publish a catalog product or authorize deployment. That narrow meaning avoids overclaiming a successful practice workflow.

#### Challenge


Write a short evidence and incident handoff for your owned attempt. Link the three current scheduled run identities to their task states, useful logs, dbt manifests/run results, independent report comparison and per-run receipts. State the chosen fixture partition, its four selected fund rows, the complete eight-row build scope and the two-minute schedule interval. Include actual worker paths and versions where observed, and source-backed expectations where not measured.

Describe the controlled failure cause, repair and remaining authentication/restart/UI gates. Identify the code you authored and the prepared dbt/helper baseline you used. Provide the owned cleanup boundary and a reviewable DAG diff without deleting shared resources. Compare against the end-of-phase reasoning keys after your attempt and note any instructor-answer exposure. The handoff should let a colleague understand why this result is trusted and what still requires the prepared runtime or a human.

#### Hint


<details>
<summary>Connect identities to business values and remaining checks</summary>

Start with a compact identity chain: owned DAG, current run, task instances, dbt artifacts, input variant and consumer result. Use that chain to find missing evidence rather than listing every terminal command. State the earliest useful failure cause and the precise repair. Keep observed versions and configured paths in different fields; copying a Dockerfile tag into a measured-version field would mislead the next reader.

</details>

#### Check


Inspect the handoff against the actual receipts and API report. Each successful or repaired receipt must name the correct run, contract and fixture partition; the failed run must have none. The report comparison must identify all eight fund/date keys and the selected four-row partition. Check that the DAG was paused after the bounded rehearsal and that cleanup targets only its owned stage and prefixed relations.

Explain why parse, local manual testing, terminal connection and an old green UI do not establish the scheduled worker outcome. State whether token refresh, expiry, restart and two-workspace isolation were actually exercised; leave them pending otherwise. Retain a readable diagnostic log excerpt without secrets and a bounded authored diff. Use the live verifier for API and warehouse checks, then review the corresponding UI and diagnostic excerpt with your instructor.

```bash
# From the training root, assess the owned staged attempt after fresh evidence exists.
mise run challenge:v2:verify airflow phase-one-certified --workspace "$DC_ASTRO_STAGE" --mode live
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#airflow-p1-05-reasoning)


## Phase completion


Complete the foundation with a readable four-task DAG, the declared dependency chain, explicit worker project/profile paths and a fresh scheduled run in the prepared Astro environment. The independent checks must show the complete eight-row fund/date report and the four fund rows selected for the run's named business partition. Retain the actual run and task-instance identities, useful logs, dbt artifacts and a run-bound receipt. Manual execution and syntax compilation remain supporting evidence; they cannot replace the scheduled worker boundary.

Demonstrate one controlled quality failure that blocks publication evidence, remove its cause and retain the repaired scheduled result. Explain which inputs, models and helper functions were supplied and which DAG gaps you authored. Your handoff distinguishes the terminal, scheduler, worker and Databricks warehouse, and states what remains pending about authentication refresh, restart and human UI review. Keep the owned DAG paused after rehearsal and preserve its evidence before cleanup. The receipt is classroom evidence, not production publication or a catalog registration. Do not make an external notification, deployment or another learner's complete project a prerequisite for this core.

---


## Optional stretch


The core completion standard is independent of optional work. No additional stretch is required in this phase; the next phase has an independently prepared entry baseline.

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Inspect a prepared orchestration baseline

<a id="airflow-p1-01-reasoning"></a>

<details>
<summary>Reasoning for airflow-p1-01: Separate configured expectations from observed runtime identities</summary>

The terminal, scheduler, worker and warehouse do different jobs. A useful boundary inventory follows the owned stage into the actual worker mount and verifies executable/profile/artifact paths there. The supplied dbt solution is an input to orchestration practice, not proof of your DAG authoring. An unstaged file may fail import because ownership metadata is absent; a staged file can still fail because its worker executable is wrong. Both are different from a business-quality failure and need distinct observations.

[Return to airflow-p1-01](#airflow-p1-01)

</details>

### Reasoning: Author a small Python DAG with real dbt tasks

<a id="airflow-p1-02-reasoning"></a>

<details>
<summary>Reasoning for airflow-p1-02: Operators must connect task state to actual product work</summary>

The build branch executes the real prepared dbt graph on Databricks. Quality and evidence read independently specified warehouse results rather than trusting the task name. The receipt binds the current run to its selected business-date result while explaining that this tiny build refreshes the full fixture. A no-op publication marker or a copied terminal token would break those boundaries. Static and import checks are prerequisites; fresh worker artifacts and output establish the executed behavior.

[Return to airflow-p1-02](#airflow-p1-02)

</details>

### Reasoning: Demonstrate the dependency graph and scheduled run

<a id="airflow-p1-03-reasoning"></a>

<details>
<summary>Reasoning for airflow-p1-03: Graph structure and scheduled identity prove different obligations</summary>

The required edges ensure checked readiness precedes transformation and checked quality precedes evidence. A disconnected evidence task defeats that guard. Manual execution is useful diagnosis, but the scheduled run proves the timetable and worker boundary. Its exact task identities, artifacts and receipt must agree with the owned stage and current session. The May business partition is explicit and independent of the schedule interval. Pausing only the owned DAG preserves other learners and ends the bounded rehearsal.

[Return to airflow-p1-03](#airflow-p1-03)

</details>

### Reasoning: Inspect a controlled task failure

<a id="airflow-p1-04-reasoning"></a>

<details>
<summary>Reasoning for airflow-p1-04: Recovery repairs the cause and retains per-run evidence</summary>

The quality marker creates a known business-gate failure. It should block only that run's publication evidence while preserving the previous successful receipt. Removing the marker repairs the cause; a fresh repaired run then needs independent output verification. An expired token or wrong path may also fail a task, but does not establish this intended drill. Task state, useful log and receipt identity together show the propagation and recovery rather than merely documenting red then green colors.

[Return to airflow-p1-04](#airflow-p1-04)

</details>

### Reasoning: Explain the run and environment boundaries

<a id="airflow-p1-05-reasoning"></a>

<details>
<summary>Reasoning for airflow-p1-05: Evidence must identify both executed work and its limits</summary>

A coherent handoff joins current run/task identities to dbt artifacts and independently checked warehouse values. It states the distinction between fixture partition, complete build scope and schedule interval. The controlled quality failure and repaired run need separate receipts and causal explanation. Worker auth, restart, isolation and human readability are additional checks, not conclusions inferred from a first success. Classroom publication evidence does not perform production publication. Recording these limits makes the result reviewable without hiding unfinished acceptance work.

[Return to airflow-p1-05](#airflow-p1-05)

</details>
