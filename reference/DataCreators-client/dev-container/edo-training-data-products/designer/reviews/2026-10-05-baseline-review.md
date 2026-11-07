# Baseline challenge review — 5 October 2026

Review type: repository inspection and static data analysis. This review supports [PLAN.md](../PLAN.md); it is not a new learner, Docker, Astro, Databricks or Catalyst execution report. Existing source files are retained unchanged during this planning task.

## Sources and existing structure

The current [challenge index](../../challenges/README.md) lists five numbered folders and a single prerequisite: open the devcontainer and authenticate through `mise run setup:databricks`. Numeric verification/reset entry points remain the current working interface. The original challenge files, development-container configuration, task definitions, tests, product fixtures and support documents are fingerprinted in [baseline-inputs.json](baseline-inputs.json).

| Existing route | Structure and evidence | Planning implication |
|---|---|---|
| [00 readiness](../../challenges/00-environment-check/README.md) | Toolchain checks; no learner authoring. | Preserve in v1 and make readiness accessible from v2. Do not force it into an assessed 45-minute tool phase. |
| [01 Docker](../../challenges/01-docker-intro/README.md) | Concept → authoring → hint → check → optional variation. Complete app, TODO Dockerfile and solution. Printed total ~35 minutes. | Extend learning through lifecycle/inspection/configuration; explicitly audit the current under-band lab. Add substantive Phase 2. |
| [02 dbt](../../challenges/02-dbt-pipeline/README.md) | Phase 1 sources/staging/materialization/test, ~1 hour. Phase 2 ten tasks: joins, marts, tests, docs, optimization hook, new mart. Placeholder models are explained. | Preserve clear explanations, promote a small end-to-end output/relationship standard, and add behavior-driven advanced work. Pilot combined authoring/check time. |
| [03 Airflow](../../challenges/03-airflow-orchestration/README.md) | Phase 1 ten sections, ~1.5 hours, including Cosmos/freshness/retries/failure recovery. Phase 2 ten operational sections including alerting, monitoring, runbook and alternative operator. | Minimum DAG can be simplified; advanced tasks need authored decisions, failure/recovery and evidence rather than command repetition. |
| [04 Atlas](../../challenges/04-atlas-capstone/README.md) | Team discovery; source/domain/consumer layers; eight Phase 1 sections and 14 optional extensions. Phase 1 1–3h; Phase 2 3+h. | Both phases need honest timing findings. Propose finite Phase 2 core and preserved stretch. Resolve population semantics before moving tasks. |

Git, dedicated Databricks CLI and optional Kafka need new learner authoring. The current capstone may mention Kafka as platform architecture; that does not constitute a bounded beginner Kafka exercise.

## Runtime, migration and verifier findings

Inspect [.mise.toml](../../.mise.toml), [Atlas verifier](../../challenges/04-atlas-capstone/verify.sh), [wiring tests](../../tests/challenges/offline/test_wiring.py), [home/navigation tests](../../tests/challenges/offline/test_home.py) and [stub synchronization tests](../../tests/challenges/offline/test_ch03_stub_sync.py). Current task dispatch, test discovery and repository-relative paths assume the unversioned numbered layout. The migration must update them together.

Reset overwrites authored product assets and removes solution-only authored files. It explicitly warns that warehouse tables remain. Preserve this distinction; a solved relation left remotely can make an unfinished local test appear successful. New phase workspaces need declared reset/cleanup manifests and version isolation. Solution directories must remain outside dbt/DAG discovery.

The [from-scratch validation RCA](../../docs/rca/2026-08-31-challenge-04-from-scratch-gaps.md) describes an earlier defect: the final solution gate missed missing test declarations and an inaccessible compiled-SQL path. It reports a historical fixed runner completing 67/67 steps and building 28 models/eight tests remotely. Reuse its lesson—verify the learner journey, not only the completed state—but do not claim those historical results validate newly authored v2 scripts.

The [verifier lock-file RCA](../../docs/rca/2026-08-05-challenge-04-verify-rewrites-package-lock.md) records mutation of `package-lock.yml` caused by absolute project paths, and the snapshot/restore fix. Copying products into temporary roots without their `shared` relative package topology can introduce another breakage. New isolation must preserve package relationships and check the tracked diff after success and failure.

Other relevant source RCAs cover reset leftovers, eager dbt test selection, OAuth refresh/boot environment, profile portability and unscoped Airflow task clearing. Inventory exact affected paths during P0/P1 and retain targeted regression coverage. Historical dated RCAs remain historical; add new migration context rather than rewriting their execution logs.

## Catalyst and course boundary

The supplied Catalyst tree is `Capital/DataCreators-client/ai-skills/catalyst/`. Its source manifest/templates and the existing [v4 client audit](../../../../../DataCreators-v4/designer/CLIENT-SOURCE-AUDIT.md) / [Catalyst course map](../../../../../DataCreators-v4/designer/CATALYST-COURSE-MAP.md) provide usable context for contracts, model review, native-versus-pandas tests, DAG generation and operational evidence. This planning task does not install or invoke those skills.

The v4 source audit distinguishes the devcontainer's declared Python/CLI pins, the Astro image, the Cosmos virtual environment and the separate locally rehearsed course fallback. Actual client versions, corporate registry/network, OAuth identity, schema/warehouse rights and prepared jobs remain readiness items. Do not copy a generic `localhost:8080` assumption into new Astro UI instructions; record the endpoint printed by the actual runtime. Avoid transferring older SLA arguments into a newer Airflow API without inspection/rehearsal.

The released v4 edition excluded learner Kafka and Datadog configuration. The latest owner request explicitly adds optional Kafka and allows advanced observability in the new challenge design. Record the scope evolution and adapt a future edition deliberately. Keep the released v4 artifact unchanged. Old adaptations that truncated Airflow Phase 2 must not act as the new generator's content policy.

## Findings to carry into implementation

| ID | Finding | Required disposition |
|---|---|---|
| B01 | Current command/path contracts break under an extra directory level. | Version-aware resolver and compatibility tests before migration acceptance. |
| B02 | Existing Docker ~35-minute core is below the requested band. | Record the exception; proposed new learning tasks are a separate curriculum redesign. |
| B03 | Capstone's stated ranges already exceed 120 minutes. | Retain a timing audit; core/stretch design is proposed, not an observed fix. |
| B04 | dbt Phase 2 and Airflow Phase 2 lack a reconciled offered-core timing measure here. | Per-task estimation and junior pilot, including runtime waits. |
| B05 | Capstone report excludes zero-activity portfolios while keys are present. | Explicit consumer population contract, counts/anti-joins and independent oracle. |
| B06 | Learner starters, final solutions and live execution have different success meanings. | Separate baseline and completion checks; no offline-to-live PASS inflation. |
| B07 | Central solutions change ignore/discovery assumptions. | Test exclusion from learner extraction and runtime discovery; verify solutions separately. |
| B08 | Git/GitHub, CLI discovery and optional Kafka lack dedicated routes. | New authored tasks with access/preparation/fixture plans, not borrowed labels. |
| B09 | Full five-day timing cannot be inferred from a per-phase target. | Allocate preparation/clinics and preserve protected teaching time; audit schedule conflicts. |
| B10 | Multiple generated course views can drift or omit deep README files. | Deterministic manifest + complete appendix inventory/block coverage checks. |

Review completion means the risks and requirements have been specified. All runtime and instructional pilot findings remain for the later implementation; this file does not mark them passed.
