# Challenge v2 implementation review — 5 October 2026

The implementation preserves the existing pack under challenges/v1, authors seven v2 tool routes with twelve active phases and two explicit inactive placeholders, and supplies mirrored instructor solutions and Bash verifiers. Current numerical Mise tasks select v1. New version-explicit commands prepare fresh workspaces and refuse to overwrite existing attempts.

This is a built local review candidate. It is not a promoted replacement for the accepted v4 course. Connected services and representative junior timing pilots remain release gates.

## Evidence boundaries

| Boundary | Observed or pending |
|---|---|
| Existing offline source/compatibility tests | Fresh indexed disposable checkout; test results and the one baseline readiness-hint defect recorded in the run summary. |
| Git Phase 1 | Actual commits, branches, merges, conflict, repair and restore in a disposable repository. |
| Git Phase 2 | Local supporting rehearsal executed; real private GitHub PR/reviewer/synchronization gate blocked because gh/sandbox access are unavailable. |
| Docker | Supplied app and independent summary oracle executed. Image build/run, non-root UID, named-target failure/repair and lifecycle checks require Docker, absent in this shell. |
| dbt | Real dbt-core 1.10.13 / dbt-duckdb 1.9.6 / DuckDB 1.4.1 seed/build/test. Advanced fan-out negative test, repair, incremental insert/update/replay and lineage generation executed. |
| Databricks CLI | Metadata fixture parsing/object-type checks executed. Live identity/catalog/schema/table access remains blocked; fixture results are supporting-only. |
| Airflow | Airflow 3.1.0 / Task SDK 1.1.0 / standard provider 1.8.0 actual DagBag and Dag.test execution with real dbt subprocesses. Success → quality-marker failure → repair/replay verified. Astro UI/container and connected adapter checks remain pending. |
| Kafka | Event contract, deterministic run identity, malformed payload rejection and broker/bridge code provided. Broker→Airflow→dbt chain remains blocked without Docker/prepared runtime. No producer/fixture exit is counted as chain completion. |
| Atlas capstone | Local dbt outputs match an independent Decimal/raw-CSV oracle per portfolio, advisor and region. Actual model negative-case failure/reconciliation/repair executed. Connected Atlas casts, API/profile behavior and production-compatible economic semantics are not claimed. |
| Timing | All twelve offered phase estimates are within 45–120 minutes and task budgets reconcile. No representative learner pilot was available; all remain estimated/unpiloted. |
| Course candidate | All twelve baseline chapters retained; concise day/clinic summaries, full recursive learner README appendix and instructor concepts generated. Course render/word/page/link results are in the candidate audit. |

## Capstone contract and observed results

The focused consumer is **active portfolios with qualifying trades**. Raw trades: 10,000; valid trades: 9,880; positions: 3,717; conformed portfolios: 2,500; active report: 1,028; absent zero-activity portfolios: 1,472. The independent oracle computes prices, signed positions, fees and rollups directly from CSV rows rather than reusing model SQL. Advanced outputs include 120 represented advisors and 12 regions.

The deliberately incorrect portfolio.client_id = advisor.advisor_id join returns only 152 conformed portfolios. Learners compare this unintended loss with expected zero-activity omission. Phase 1 promotes minimum key/relationship/population proof; Phase 2 has a finite performance/leaderboard/region/reconciliation core. All fourteen legacy extensions remain preserved, mapped and reproduced in the optional advanced reference. Native-currency teaching amounts are not FX-normalized economic AUM.

## Migration and regression protection

The pre-migration snapshot fingerprints all 728 existing files. No original file is missing after mapping its new v1 path. Changes are enumerated in migration-preservation.json and migration-changes.json: current paths, relative root/link depth, tests, dispatch and ignore rules; one existing readiness hint gained the already-supported --pat fallback. Historical RCA and dated planning documents retain historical commands. The current v4 adapter resolves its original input through v1 while the new course adapter uses the v2 manifest.

Reset isolation is structural: v2 preparation/reset creates a new copy and rejects an existing workspace. V2 verifiers copy inputs, execute in a temporary directory, remove that directory and check input hashes. They never edit data_products or clear unrelated Airflow runs. Legacy v1 file reset retains its original shared-product semantics; numeric commands cannot select a v2 topic. Shell/manifest/source checks and indexed stub synchronization run in a disposable Git checkout, without staging the user's work.

## Synchronization and course depth

The v2 manifest inventories every learner README, including starters and optional references. The generator parses Pandoc blocks, validates task/concept/root-table parity, resolves links and retains full text/code block content. Generated instructor explanations come from the phase concept blocks; tool-root text is reused verbatim. Inline summaries identify phases, tasks, concepts, optionality, timing and execution prerequisites. Source edits cause stale generated outputs to fail --check.

The complete accepted v4 learner chapters are retained byte-for-byte or as exact prefixes; no teaching block is removed. The candidate adds a thirteenth full challenge appendix, and stays above the 100,000 substantive-word / 237-readable-page floors. Word counting excludes code, headings, reference/navigation/provenance material and exact duplicate prose globally. Candidate artifacts and their hashes are reviewed separately from release promotion.

The raw implementation run evidence remains in ignored .local/v2-evidence; verification-summary.json retains sanitized results, source/script hashes, commands, actual versions, cleanup and duration. Automated durations are technical evidence, never junior-learner timing. PILOT-LEDGER.csv is an empty recording template, not fabricated pilot data.

## Final candidate acceptance evidence

The rendered candidate has **629 PDF pages**, **135,690 substantive learner words**, all **39 learner READMEs**, **60 core tasks** and **35 diagrams**. All twelve baseline chapters remain intact. HTML checks resolve all 2,961 local links/anchors; 511 PDF pages contain at least 400 extracted alphabetic characters, supplementing the sampled visual review. Both sampled phase/table pages remain readable without cropped cells. Course-audit.json,readability.json,html-links.json and render-review.json are in the candidate reviews directory.

The final compatibility/isolation/drift suite reports **249 passed, one skipped** because Mise is unavailable. All 24 starter/reference shell entry points ran against current script/manifest hashes; supporting-only results are explicitly distinct from completed live boundaries. Learner and instructor ZIP archives are verified and separately packaged under designer/dist. The learner archive excludes solution directories and central v2-solutions.

## Reproduce

From the project root:

```bash
bash scripts/setup-v2-tools.sh
python3 scripts/challenge-v2.py list
bash challenges/v2-solutions/dbt/phase-two-proficient/verify-starter.sh --mode offline
bash challenges/v2-solutions/dbt/phase-two-proficient/verify.sh --mode offline
python3 scripts/sync-v2-course.py --check
bash scripts/build-v2-course.sh
bash scripts/package-v2.sh
```

Run each phase's matching shell scripts for the other boundaries. --mode live returns blocked when the necessary service/runtime is absent; it does not silently substitute local execution. Instructor preparation for Kafka binds a parsed, unpaused DAG and worker-visible project/dbt executable; duplicate reuse requires a matching completed receipt, and an existing run without receipt intentionally needs exact-run investigation before committing its offset.

## Remaining gates

Complete the real GitHub sandbox review, Docker targets/lifecycle drills, read-only Databricks metadata route, provisioned schema/dbt/Atlas rehearsal, Astro UI recovery and optional Kafka chain. Obtain representative junior pilots for every offered phase and a whole-course scheduling review. Record timing exceptions without automatically shortening content. External service absence and missing human pilots prevent a claim of full connected-course acceptance; the local pack and candidate materials remain reviewable now.

Primary technical references used alongside measured package source: [Docker multistage builds](https://docs.docker.com/build/building/multi-stage/), [Airflow Task SDK](https://airflow.apache.org/docs/task-sdk/stable/), [Databricks CLI command groups](https://docs.databricks.com/aws/en/dev-tools/cli/commands), and [schema commands](https://docs.databricks.com/aws/en/dev-tools/cli/reference/schemas-commands). Declared client pins remain distinct from observed local versions.
