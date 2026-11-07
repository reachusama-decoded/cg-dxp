# Phase timing audit and pilot protocol

Planning baseline, 5 October 2026. Target: **45–120 minutes per offered phase** for an average generalist junior technical learner. Phase 2 uses the same learner timing reference once its declared Phase 1-equivalent entry baseline is available; it does not require retiming against an expert to make advanced tasks appear shorter.

This audit records exceptions. It does not automatically trim exercises, move tasks or change estimates to meet the band. Curriculum changes proposed in [CURRICULUM.md](../CURRICULUM.md) are separate instructional design decisions and remain unimplemented.

## What counts

Include reading explanations, understanding the task, authoring, normal tool waits, checking output, reasonable diagnosis/repair and the required evidence/explanation. Include learner-facing phase preparation. If the instructor has already provided login, images, schemas, broker, baseline models or runtime services, explicitly declare that preparation and estimate it separately. Record unexpected access/installation incidents separately **and** report experienced wall-clock time so the advertised journey remains honest.

Do not include optional variations/stretch in the core total, count parallel team members' time as if it were one learner, or use an automated solved-project verifier's runtime as learner completion time. One task's time budget cannot be used twice to hide overlap. Capstone team discovery/presentations and the entire Friday event need a separate calendar; mandatory phase-specific discovery/handoff still belongs in the phase total.

An inactive phase has N/A, not zero minutes or an invented filler exercise. Optional Kafka must meet the target when a learner chooses it; optionality does not excuse an unbounded core.

## Current source baseline

| Existing phase/lab | Source estimate | Audit status | Evidence limits |
|---|---|---|---|
| Environment check | No assessed phase budget | Not applicable | Readiness is a prerequisite. |
| Docker lab | ~35 minutes, including optional variation | **Under-band** | Core alone is shorter; estimate printed in guide, not a new pilot. |
| dbt Phase 1 | ~1 hour | Estimated in-band | Printed section estimates roughly total 65 minutes; reconcile precision in authoring. |
| dbt Phase 2 | Ten sections; no reconciled phase total established in this review | **Unmeasured** | Do not infer duration from number of headings. |
| Airflow Phase 1 | ~1.5 hours | Estimated in-band | Section estimates roughly total 85 minutes; runtime/retry waits may increase actual duration. |
| Airflow Phase 2 | Ten operational sections; no reconciled phase total established here | **Unmeasured** | Requires per-task authoring and live-wait estimates. |
| Atlas Phase 1 | 1–3 hours | **Over-band range** | Includes a possible 180-minute completion; whole event has separate discovery/presentation time. |
| Atlas Phase 2, all extensions | 3+ hours | **Over-band** | Current pack explicitly says learners are not expected to finish all 14. |

These are source estimates, not measured user performance. Historical automated challenge runs cannot turn these rows into observed junior timing.

## Initial proposed v2 budgets

The following budgets allocate useful work, not padding. Component values are central estimates; the range reflects learner/runtime uncertainty. All rows remain **unpiloted** and high bounds are provisional.

| Phase | Read/orient | Author/perform | Check/diagnose | Explain/handoff | Central total | Initial range |
|---|---:|---:|---:|---:|---:|---|
| Git 1 | 10 | 35 | 15 | 10 | 70 | 60–90 |
| Git 2 | 10 | 45 | 20 | 10 | 85 | 75–110 |
| Docker 1 | 10 | 30 | 20 | 10 | 70 | 60–90 |
| Docker 2 | 10 | 40 | 25 | 10 | 85 | 75–110 |
| dbt 1 | 15 | 40 | 25 | 10 | 90 | 75–110 |
| dbt 2 | 15 | 45 | 30 | 10 | 100 | 90–120 |
| Databricks CLI 1 | 10 | 20 | 15 | 10 | 55 | 45–65 |
| Databricks CLI 2 | N/A | N/A | N/A | N/A | N/A | Not offered |
| Airflow 1 | 15 | 35 | 30 | 10 | 90 | 75–110 |
| Airflow 2 | 15 | 40 | 35 | 10 | 100 | 90–120 |
| Kafka 1, optional | 15 | 25 | 25 | 10 | 75 | 60–90 |
| Kafka 2 | N/A | N/A | N/A | N/A | N/A | Not offered |
| Capstone 1 | 15 | 40 | 35 | 15 | 105 | 90–120 |
| Capstone 2 | 15 | 40 | 35 | 15 | 105 | 90–120 |

The twelve offered phase ranges sum to **885–1,255 minutes (14h45–20h55)** including optional Kafka, before course teaching and stretch. The six non-Kafka Phase 1 ranges sum to **405–585 minutes (6h45–9h45)**. These totals show why a separate course schedule/advanced-clinic design is required. The 45–120-minute requirement is per phase, not the combined pack.

Particularly high-risk assumptions: Git reviewer availability; first image pulls; Databricks identity/access; dbt build/warehouse latency; Airflow startup/retry waits; Kafka broker/bridge preparation; and Atlas authoring depth. Any supplied scaffold that reduces authoring must be identified accurately in completion standards. Preserve these risks rather than making the maximum exactly 120 by assertion.

## Pilot and audit record

For each offered phase, first obtain a task-by-task estimate from the authored README. Then pilot a fresh starter journey with at least several representative junior learners where possible; record experience level and sample size. An expert rehearsal is useful technical evidence but not a substitute for the target cohort. If the available sample is small, state the uncertainty instead of claiming population statistics.

Record phase/tool ID and source hash; environment/tool versions; prerequisite preparation; task start/end times; active time and normal waits; unexpected incidents; hints/instructor interventions; completion artifacts; core completion time; stretch time separately; observed minimum/median/range when justified; and incomplete learners' stopping points. An incomplete observation is censored, not a successful fast completion. Review whether the specified minimum standard was achieved before accepting its timing.

| Finding ID | Phase/hash | Estimate/observations | Band status | Cause/uncertainty | Content decision |
|---|---|---|---|---|---|
| T01 | Existing Docker | ~35m including optional | Under-band | Short existing lab | Proposed v2 lifecycle work; no edit made by audit. |
| T02 | Existing Atlas 1 | 60–180m | Over-band range | Broad baseline and learner variation | Flag; focused v2 slice is a separate proposal. |
| T03 | Existing Atlas 2 | 180m+ all14 | Over-band | Open-ended extension set | Flag; fixed core/stretch split is a separate proposal. |
| T04 | New offered phases | Initial ranges above | Unpiloted | Actual authoring and environments pending | Keep estimates provisional; record future exceptions. |

A future observed 145-minute phase is recorded as over-band with its real evidence and effect on scheduling. Do not cut a task, relabel it stretch or change the estimate within the timing audit to suppress the result. Propose any later redesign separately, retaining the original finding and measurement. Published instructor schedules and release notes must expose unresolved timing exceptions.
