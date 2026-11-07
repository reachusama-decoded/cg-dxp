# airflow challenges

Airflow schedules the same supplied Portfolio Analytics graph used in the dbt projects. The prepared dbt baseline keeps authoring focused on readiness, real worker invocation, quality and run-bound evidence. Foundation work establishes the four-task chain and current scheduled success/failure/repair. Advanced practice develops explicit dates, freshness, bounded retries, replay correctness, worker/auth paths and an incident handoff. A green graph must be connected to independently checked warehouse output.

## Before you start

Prepare an owned attempt through mise in the training project, then inspect actual Astro mounts, worker executable and approved Databricks namespace. Choose a unique prefix/DAG identity and stage only through the helper that refuses an occupied destination. Seed the copied supporting project through the terminal and explicitly handle extraction-time freshness without changing May business dates. Worker credentials resolve at execution through the delivered connection; a terminal login alone is insufficient. Pause only the owned DAG after a bounded rehearsal and preserve evidence before scoped cleanup.

## Suggested timeline and tasks

Estimates include reading, practice, checks and explanation. Allow additional time for environment setup and optional extensions.

| Phase | Task | Minutes |
| --- | --- | --- |
| Foundation | [airflow-p1-01: Inspect a prepared orchestration baseline](phase-one-certified/README.md#airflow-p1-01) | 15–22 |
| Foundation | [airflow-p1-02: Author a small Python DAG with real dbt tasks](phase-one-certified/README.md#airflow-p1-02) | 15–22 |
| Foundation | [airflow-p1-03: Demonstrate the dependency graph and scheduled run](phase-one-certified/README.md#airflow-p1-03) | 15–22 |
| Foundation | [airflow-p1-04: Inspect a controlled task failure](phase-one-certified/README.md#airflow-p1-04) | 15–22 |
| Foundation | [airflow-p1-05: Explain the run and environment boundaries](phase-one-certified/README.md#airflow-p1-05) | 15–22 |
| Advanced | [airflow-p2-01: Define bounded replay and input identity](phase-two-proficient/README.md#airflow-p2-01) | 18–24 |
| Advanced | [airflow-p2-02: Inject failure and observe useful retry behavior](phase-two-proficient/README.md#airflow-p2-02) | 18–24 |
| Advanced | [airflow-p2-03: Prove output correctness after recovery](phase-two-proficient/README.md#airflow-p2-03) | 18–24 |
| Advanced | [airflow-p2-04: Use Astro UI to make an operational decision](phase-two-proficient/README.md#airflow-p2-04) | 18–24 |
| Advanced | [airflow-p2-05: Write a short incident handoff](phase-two-proficient/README.md#airflow-p2-05) | 18–24 |

## Choose your phase

- [Foundation](phase-one-certified/README.md): Foundation core with explicit completion evidence.
- [Advanced](phase-two-proficient/README.md): Independent advanced baseline and finite core, separately timed.

Finish the core tasks before choosing optional stretch.

## Teaching concepts

Schedule interval, business partition and extraction freshness are independent clocks. The tiny dbt build refreshes the complete fixture, while the receipt selects four fund rows for a named May date. Task ordering protects evidence after quality, but real run/task identity and independent values establish execution. Retries must fit their failure category. End-of-phase keys explain cause and recovery; full runnable DAG references stay instructor-only. Optional Cosmos or hosted monitoring has separate prepared-runtime and timing requirements.

## Question-led foundations and further study

Use questions 1–8 alongside the foundation tasks. Questions 9–13 introduce further study.

### Foundations

<a id="airflow-guide-q01"></a>

#### What problem does Airflow solve alongside dbt?

The Portfolio Analytics workflow orders source readiness, transformation/testing and publication evidence. dbt provides the model graph; Airflow controls when and under what conditions it runs. Databricks remains the data execution boundary. A final evidence task records a successful checked handoff and never performs production publication.

<a id="airflow-guide-q02"></a>

#### What are a DAG, task, operator, run and task instance?

The owned DAG is `<prefix>_portfolio_daily`. Its named tasks are source_ready, dbt_build, quality and publication_evidence. The DAG describes dependencies; each scheduled run has a distinct ID, logical date and instances of those tasks. Record their states from the fresh run rather than presenting an unrelated green grid. An operator is the implementation used to execute one task.

<a id="airflow-guide-q03"></a>

#### Which components parse, schedule, execute and record the work?

The terminal prepares files and seeds. Astro mounts data_products into the DAG processor/scheduler/worker path. The scheduler creates timed runs; workers execute tasks; the metadata database records orchestration state; Databricks executes dbt SQL. Inspect the actual compose mount and worker executable. Files visible in your terminal outside that mount are not automatically visible to a worker.

<a id="airflow-guide-q04"></a>

#### How do we define dependencies and pass information?

Wire source_ready >> dbt_build >> quality >> publication_evidence. Pass only a small partition/run identifier, never holdings through XCom. Every task checks the explicit May sample partition while preserving the actual logical date separately. Failure propagates through dependencies, not through a print statement saying the work is ready.

<a id="airflow-guide-q05"></a>

#### What do schedules, logical dates, intervals and catchup mean?

The owned classroom DAG has an explicit two-minute timetable, a timezone-aware start date, catchup=False and one active run. A scheduler-created interval is not the May business date in these historical CSVs. The fixture_partition parameter selects 2026-05-20 or 2026-05-21 explicitly. Record both the logical interval and selected partition. Unpause only this owned DAG during rehearsal and pause it after collecting evidence. A daily production cadence is a separate design choice. Replay the same business date to demonstrate idempotence rather than assuming each scheduler day creates new data. The prepared tiny dbt graph refreshes both fixture dates; the receipt selects four fund rows for the named partition. Do not describe that selection as date-filtered ingestion.

<a id="airflow-guide-q06"></a>

#### What should happen when a task fails or retries?

Bound retries and retry delay for transient connection failures. A deliberately missing FX rate or quality-fault marker must fail quality and block publication_evidence. Use logging-only callbacks. Keep the old accepted receipt unchanged on failure and prove that no receipt was created for the failed run. An auth/config error differs from business-quality failure and should be diagnosed from its first log error.

<a id="airflow-guide-q07"></a>

#### How do reruns and backfills produce correct results?

Replaying a business date reruns the same owned relations and compares their keys/values. Retain run-specific receipts and show which date they represent. A controlled holding correction exercises Delta merge in advanced dbt practice; do not claim a second green task proves idempotence. Restore baseline source data after the drill. Clearing a task is an operational action on a named run, not a repair to its input contract.

<a id="airflow-guide-q08"></a>

#### How do we inspect a run and prove completion?

Keep the current Astro graph/grid/log, exact run/task/attempt IDs, dbt run results and independent warehouse query. The publication receipt binds the contract, fixture partition, source hashes and checked artifacts. API checks compare scheduler-created identities and task states. Parsing or `dag.test()` checks do not establish scheduled worker execution. Use a fresh run to check the scheduler and worker.

<a id="airflow-further-study"></a>

### Further study

Questions 9–13 are separately timed advanced study.

<a id="airflow-guide-q09"></a>

#### How do readiness and freshness differ?

Readiness checks that each supplied raw relation exists with the required columns and population. Freshness checks _extracted_at separately. Historical May timestamps fail a current freshness threshold until an explicit recorded preparation refreshes only ingestion timestamps. A sensor waiting for presence cannot prove freshness. Keep freshness separate from business-date selection and avoid inventing new business rows.

<a id="airflow-guide-q10"></a>

#### How should Airflow orchestrate dbt, and when does Cosmos help?

The prepared PythonOperator route calls the delivered isolated worker dbt executable with explicit project/profile/airflow target and artifact paths. The same Portfolio graph runs as on Wednesday. An optional Cosmos adapter renders that graph using the installed integration, manifest load mode and task-time token env; its APIs and actual worker behavior must be checked on the measured stack. Do not replace dbt with a scaffold print or declare import success as execution.

<a id="airflow-guide-q11"></a>

#### What do Astro Runtime and the CLI add?

Astro supplies the project/image lifecycle around Airflow. Read the delivered Dockerfile and compose override, then inspect actual mounts and versions. The intended dbt executable is /home/astro/.venv/cosmos/bin/dbt. Token delivery uses the prepared databricks_default connection at task time; startup, refresh, expiry and restart are separate checks. A running scheduler does not prove the profile paths or warehouse permissions.

<a id="airflow-guide-q12"></a>

#### How do we test and operate a workflow as a team?

Review source/import checks before scheduling, then run success, intended failure, repair and replay with independent outputs. Keep owned DAG/relation names and cleanup in the handoff. Prove two simultaneous learner attempts do not contaminate one another and removal of one leaves the other intact. Resource provisioning, external alert transports and deployment remain optional/reference work.

<a id="airflow-guide-q13"></a>

#### Can we deliver a workflow and demonstrate recovery?

Present one scheduled success, one intentional quality failure with no premature evidence, and a repaired replay against the same holdings data. Bind logs, receipt, run results, versions and independent query to the contract. Explain the business partition and why task success alone is insufficient. Retain a restart/auth-expiry rehearsal before acceptance; human pacing and UI walkthrough are still required.
