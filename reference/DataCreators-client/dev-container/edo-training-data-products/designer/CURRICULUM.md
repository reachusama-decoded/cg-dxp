# Proposed v2 curriculum and preservation map

Planning proposal, 5 October 2026. These are challenge designs, not newly authored learner exercises. See [PLAN.md](PLAN.md), [CHALLENGE-SPEC.md](CHALLENGE-SPEC.md) and [timing audit](reviews/TIMING-AUDIT.md). Task titles below are provisional; assign stable IDs during authoring. Every phase includes explanations, hints, checks and a working/declared starter baseline.

## Git

Phase 1 minimum standard: the learner can work locally, distinguish working tree/index/history, preserve work on a branch and resolve a small conflict. Start with a disposable repository containing a tiny dataset README and independent changes to make.

| Task | Concept and learner action | Completion evidence |
|---|---|---|
| 1 | Inspect status, history and a diff; explain tracked/untracked files and staging. | Identify exactly what the next commit would contain. |
| 2 | Edit, stage and commit a small data-contract clarification. | Commit contents match intent; history and message explain the change. |
| 3 | Branch, make two scoped changes and merge a compatible branch. | Explain where each change lives and show the merge/history. |
| 4 | Resolve a small meaningful conflict between two contract edits. | Preserve the required facts from both changes, commit and explain the decision. |
| 5 | Restore an uncommitted mistake safely and review the final diff. | Correct file content and a clean, understandable final state. |

Phase 2 minimum advanced standard: carry a change through a collaboration workflow using actual remotes and `gh`. Use a designated training repository; permissions, identity, paired reviewer and branch protections are instructor preparation. A self-contained simulated review can support practice when peers are unavailable, but its evidence must identify what was simulated.

Core: clone the sandbox; inspect remote/tracking branches; push a feature branch; create and inspect a PR with `gh`; respond to a supplied review comment with a second commit; fetch/pull a separate upstream change and resolve/synchronize; explain the final review/merge state. A real authorized reviewer can supply the comment during the later exercise; this plan does not send messages or create PRs. Stretch: rebase versus merge comparison and recovery with reflog. Do not make advanced proficiency depend on maintaining a public account or publishing course code.

## Docker

Reuse the tiny portfolio summary app and its independently stated output. Phase 1 adds substantive lifecycle/inspection activity to the current approximately 35-minute lab rather than padding the guide with command repetitions.

Core: distinguish image/container; run a supplied image; open an interactive shell and explain isolation; inspect a running/stopped container and logs; use a controlled bind mount to compare host/container files; complete a simple Dockerfile; build and run the summary with the expected six-holding result; explain why the process exits and clean only this exercise's assets. A benign baseline Dockerfile can print instructions; the completion check must require the actual app output.

Phase 2 core: build a small multistage Dockerfile with named `test` and `runtime` targets; build/tag each target separately; explain why a single build normally produces the selected final target rather than automatically emitting every intermediate image; compare runtime contents with build contents; set a suitable runtime user and demonstrate configuration/input differences; diagnose one broken copy/path or entrypoint assumption and prove the repaired output. Stretch: cache invalidation, image size/layer analysis and a deliberately bounded Compose exercise. Do not require an unrelated service stack merely to claim complexity.

## dbt

Current Phase 1 already introduces sources, freshness, five typed staging models, materialization, builds and a test. Preserve that explanation and strengthen minimum understanding with grain, `ref`, relationships and one meaningful source→staging→mart result. Use a bounded mart and prepared intermediate baseline rather than requiring every existing Phase 2 asset as a new Phase 1 prerequisite.

Proposed Phase 1 core: inspect seeds/project/profile; declare sources and understandable freshness; author representative staging transformations with clear types/units; build the remaining supplied staging slice; build one small mart through `ref`; add minimum uniqueness/not-null/relationship checks; verify row counts and a business output. Require explanation of source grain and why a join is safe. Keep the connection readiness check explicit; setup is not proof of dbt knowledge.

Proposed Phase 2 core: diagnose a supplied join fan-out or dropped-key defect using a fixture with known expected totals; repair an enrichment/mart at the intended grain; add a reconciliation and a targeted negative case; implement a bounded incremental change/replay experiment; generate and inspect lineage showing the affected dependencies. This develops behavior and reasoning beyond “run build, run docs.” Use one advanced business slice and supply unrelated supporting models as the entry fixture. Version-specific incremental features need rehearsal on the actual adapter.

| Existing Phase 2 item | Proposed v2 treatment |
|---|---|
| 1 Enrichment join | Phase 2 core diagnosis/repair; preserve complete legacy implementation. |
| 2 Supporting intermediate models | Entry fixture plus explanation; author an additional model as stretch. |
| 3 Fund exposure mart | Candidate advanced core business output. |
| 4 Portfolio returns mart | Preserve as alternate/optional stretch when exposure is the chosen core. |
| 5 Generic mart tests | Minimum key/relationship subset in Phase 1; advanced assertions in Phase 2. |
| 6 NAV reconciliation | Core reconciliation pattern with an independently specified oracle. |
| 7 Full build | Phase completion evidence, not the sole advanced learning objective. |
| 8 Docs/lineage | Phase 2 supporting evidence; demo connected to the defect impact. |
| 9 Databricks OPTIMIZE/ZORDER hook | Optional adapter-specific stretch after actual runtime/API review. |
| 10 Add a mart end to end | Optional stretch; preserve its authored YAML and reconciliation requirements. |

Authoring review must select the exact core model and map every old section to a new concept/task/fixture/stretch destination. No old content is deleted from v1. The proposed incremental exercise extends the pack; it must not be claimed as an existing Phase 2 task.

## Databricks CLI

Phase 1 only, read-only by default. Teach the difference between a workspace directory, Unity Catalog catalog/schema/table, an SQL warehouse and an identity/profile. Confirm exactly what `training_dev` denotes in the prepared environment before writing instructions; do not assume it is simultaneously a folder, schema and catalog.

Core: inspect installed CLI version/help and active profile safely; establish which identity is used; list permitted workspace or catalog metadata through the relevant command groups; inspect a prepared schema/table or job's metadata where permissions allow; filter/interpret JSON output; explain an empty result, missing object or permission denial using a supplied example; retain a short discovery note containing object type, qualified name and next consumer question. A CLI listing is not arbitrary full-text data search or a SQL query. If sample data inspection uses a separate SQL API or query command, teach that boundary and verify availability before inclusion.

Use supplied metadata fixtures for an explicitly labelled offline practice route when access is unavailable. This does not count as live access evidence. No Phase 2 tasks, provisioning, broad grants or deployment are required. Avoid printing auth tokens in checks.

## Airflow

The current Phase 1 includes freshness gates, Cosmos, scheduling, retries, failure and scoped recovery; current Phase 2 includes ten operational sections. The review should distinguish authoring/diagnosis from simple inspection. Preserve all content in v1 and map it before moving concepts.

Phase 1 core: explain a DAG versus task and dependency; author a small Python DAG with a prepared dbt project and two or three meaningful dbt tasks/stages; connect `start → dbt build/test → result check → end` or an equivalent minimal graph; inspect import/graph; trigger one controlled run in the training environment; inspect task logs and independently check its output; explain schedule versus manual run. Prepared connections, Cosmos environment and a solved dbt baseline avoid an accidental second dbt challenge. Keep one basic failure/log interpretation; elaborate freshness, backoff and observability go into Phase 2. The exact operators/task grouping must match the measured Airflow/Cosmos versions.

Phase 2 core: configure an explicit input/data interval and a bounded replay; inject a documented temporary failure; implement useful retries or a data-quality gate; observe actual states/logs in the Astro local UI; repair and rerun only the affected run/tasks; prove no duplicate business result; write a short operational decision/runbook entry. Merely starting Astro or finding a menu is supporting activity, not proficiency. Hosted Astronomer adds an optional environment-specific route only if a prepared deployment and learner rights are available. Learners must not deploy production infrastructure to finish the core.

| Current Phase 2 section | Proposed treatment |
|---|---|
| 1 Neutral alert transport | Stretch/reference; use local logs in core. |
| 2 P1 failure alert | Core operational decision and callback behavior with local evidence; external transport stretch. |
| 3 P2/P3 SLA/retry tiers | Version-reviewed operational stretch; retry diagnosis retained in core. |
| 4 Callback and SLA wiring | Modern supported callback/time-budget mechanism, after installed-version review. Do not carry legacy SLA arguments blindly. |
| 5 Freshness contract | Candidate core failure/gating scenario. |
| 6 Monitoring config | Optional observability/Datadog route with actual useful evidence when prepared. |
| 7 Runbook/consumer guide | Short core incident handoff; longer publication guide stretch. |
| 8 DAG structural tests | Maintainer/advanced supporting checks plus actual execution evidence. |
| 9 DatabricksSubmitRunOperator | Optional prepared-jobs architecture alternative. |
| 10 Complete operational DAG | Integrative stretch; core has its own finite completion standard. |

Audit simple operational inspection steps for potential Phase 1 placement. Keep complexity-based moves visible in the coverage ledger. Do not move all operations into Phase 1 just because command snippets are short.

## Kafka — optional Phase 1 only

Teach Kafka as a retained topic/event log with consumer-group offsets, rather than implying it is simply a destructive queue. The learner route uses a prepared local training broker, one topic and a supplied minimal consumer bridge. The learner should not build Kafka infrastructure, write a full reliable bridge and author Airflow/dbt from scratch in the same phase.

Core: read a small `dataset_arrived` event contract containing event ID, dataset ID/version/location and arrival timestamp; start/inspect the prepared isolated runtime; produce the event; observe the consumer bridge triggering a uniquely identified prepared Airflow run; follow that run into the prepared dbt output; verify the output corresponds to the event's dataset; replay the event and inspect the bridge's documented duplicate policy; explain the consumer offset and cleanup. Choose one clear deduplication strategy and state its limits; do not promise distributed exactly-once behavior.

Runtime design review must decide topic naming, group isolation, fixture locations, Airflow triggering/auth mechanism, wait bounds and temporary failure behavior. Completion needs linked event/run/output evidence. If no broker/Airflow is available, mark the live route unavailable and use labelled fixtures for concept practice. Kafka stays optional and is never required for the mandatory capstone gate. Phase 2 is explicitly not offered.

## Atlas capstone

The capstone must remain a business/data-product exercise, with source→domain→consumer alignment and a coherent output, not merely a SQL completion sheet. See [the data review](reviews/2026-10-05-capstone-data-review.md) for the population finding and its limits.

Phase 1 proposed core: choose the supplied consumer question and state the output grain/population; inspect keys and a lightweight STTM; build a bounded source/domain/consumer slice using prepared non-focus scaffolding; account for valid/invalid trades; demonstrate the active-portfolio versus all-portfolio distinction with an anti-join; retain IDs at appropriate grain and add key/relationship checks; inspect output and a prepared orchestration run; explain the result in a short consumer handoff. Current full 23-model baseline stays available in v1; a v2 focused core must list which models are supplied and which learners actually author. Its 90–120-minute estimate remains high risk until piloted.

Phase 2 proposed finite core: build a richer portfolio performance mart and advisor leaderboard from the completed baseline; explicitly handle ties, units and zero denominators; build the regional rollup from that leaderboard; reconcile regional/advisor/portfolio totals using an independent expected fixture; explain and demonstrate one deliberate defect/repaired result. This combines existing extensions 1, 2, 9 and 14 into a bounded outcome. Do not imply extension 14 depends on extension 1 or 3: the current dependency map says leaderboard 2 is required and reconciliation 9 is recommended. Any new dependencies must be justified in v2.

| Legacy Phase 2 challenge | Proposed v2 disposition | Notes |
|---|---|---|
| 1 Portfolio performance | Phase 2 core | Rich consumer value and zero-safe fee-rate calculation. |
| 2 Advisor leaderboard | Phase 2 core | Rank semantics; prerequisite for regional output. |
| 3 Asset-class activity | Phase 2 stretch | Clarify rolling seven rows versus seven calendar days. |
| 4 Source freshness | Phase 2 stretch | Time-dependent fixtures and reproducible expected warnings. |
| 5 Consumer exposures | Phase 2 stretch | Consumer/lineage metadata without mandatory publication. |
| 6 Money macros | Phase 1 explanation; extension in stretch | Minimum understanding of units, not a long macro-authoring exercise. |
| 7 Non-negative test | Basic boundary test in Phase 1; reusable generic test in stretch | Avoid duplicating advanced generic-test work inside the minimum standard. |
| 8 Relationship test | Phase 1 core | Address silent row-loss concerns while explaining null/uniqueness limits. |
| 9 Reconciliations | Phase 2 core; minimum population check in Phase 1 | Reconciliation alone cannot prove completeness if both sides share a lost population. |
| 10 Incremental mart | Phase 2 stretch | Change/replay/late-data experiment, not compile-only proof. |
| 11 Portfolio snapshot | Phase 2 stretch | Demonstrate a change and history semantics. |
| 12 Extend orchestration | Phase 2 stretch | Prepared approved environment; meaningful dependency behavior. |
| 13 Params-driven orchestration | Phase 2 stretch | Trace actual parameter input/output; no deployment requirement. |
| 14 Regional capstone | Phase 2 core | Finite integrative output using 2 and reconciliation pattern 9. |

All stretch routes have independent estimates and prerequisites. Give the instructor a selection guide, but core completion means finishing the fixed core, not “do whatever fits.” Moving tasks is a proposed pedagogical change subject to the content/data review; a timing audit itself does not perform these moves.

## Course scheduling and Catalyst context

Suggested placement: Git preparation/early practical session; Docker and dbt on Wednesday; Databricks CLI before connected dbt or in readiness practice; Airflow on Thursday; capstone on Friday. Kafka belongs in a clearly optional clinic/appendix route. These are proposed destinations; review the full existing timetable before allocation, since adding Git and CLI needs real time rather than consuming protected dbt/Airflow teaching unnoticed. Phase 2 routes may be post-course/advanced clinics where the five-day schedule has no room.

Use the supplied Catalyst skills/templates as source-informed review aids: `data-contract` and `transformation-spec` for key/population requirements; `write-dbt-source`/`write-dbt-model` for reviewing generated code; native `adding-dbt-unit-test` versus pandas-based `dbt-unit-test` for distinct evidence; `generate-dag` and `validate-dag` for architecture review; `data-quality-controls-plan` and `runbook` for operational handoffs. Consult the existing [Catalyst course map](../../../../../designer/CATALYST-COURSE-MAP.md) and the actual supplied files before adoption. Skills do not replace learner understanding or an independent expected-output oracle. Skill invocation, external publication and infrastructure provisioning are not part of this planning delivery.
