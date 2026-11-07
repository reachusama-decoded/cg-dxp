# Version 2 challenge route

Practice building and reviewing data products through seven tools. Foundation and advanced phases have separate starters, so you can begin either route with the required prerequisites. Read the phase's purpose, dataset, starter behavior and completion standard before editing.

## Prepare your environment

Open the supplied training project in the dev container and inspect the delivered tool versions. Git foundation and local fixture inspection can proceed without cloud access. Docker needs its prepared engine and images; connected dbt and capstone need the approved Databricks identity/warehouse/namespace; Airflow needs the actual Astro scheduler and worker boundary. Sign in through the delivered setup outside recordings and keep credentials out of source, evidence and package files. Check installed versions with each tool's version command.

Use an isolated copied workspace for each attempt and inspect its execution directory. The version-explicit mise prepare task refuses an existing destination; reset also preserves existing attempts by requiring a fresh path. Choose owned relation prefixes, DAG names, container tags and optional event topic/groups so simultaneous learners do not collide. Never create extra schemas or delete broad resource sets to repair a training issue.

## Choose the work

| Tool | Foundation | Advanced | Classroom role |
|---|---|---|---|
| [Git](git/README.md) | Local snapshots, branches and conflict | Authorized sandbox review and synchronization | Preparation/collaboration clinic |
| [Docker](docker/README.md) | Lifecycle, mount and app packaging | Tested targets, user and runtime contents | Supervised runtime practice |
| [dbt](dbt/README.md) | Supplied Portfolio sources/staging/report | Dated joins, reconciliation, correction and history | Wednesday selected core |
| [Databricks CLI](databricks-cli/README.md) | Read-only identity and metadata discovery | Not offered | Environment preparation |
| [Airflow](airflow/README.md) | Same Portfolio product on Astro | Readiness, failure/repair/replay and handoff | Thursday selected core |
| [Kafka](kafka/README.md) | Optional prepared event clinic | Not offered | Optional further practice |
| [CG product-information capstone](../cg-public-products/README.md) | Individual ETF core | Pair integration and individual temporal/workflow work | Friday event |

Advanced phases have disclosed successful entry baselines and do not require a completed peer answer. Optional stretch follows the core completion gate with separate prerequisites and timing. Kafka cannot become a hidden requirement of mandatory work.

## Run and assess an attempt

From the training project root prepare and verify through mise; inside the copy use direct tool commands so you can inspect what the tool does. Explicit live mode reaches the declared connected boundary. Offline support, parsed SQL, local JSON and compilation cannot establish Databricks or Astro completion. An untouched starter may pass its baseline check while being rejected as completed learner work. Expected instructional failures are named before the drill, and unrelated prerequisite failures stay distinct.

```bash
mise run challenge:v2:prepare dbt phase-one-certified
mise run challenge:v2:verify-starter dbt phase-one-certified --mode offline
mise run challenge:v2:verify dbt phase-one-certified --workspace .local/challenges-v2/dbt/phase-one-certified --mode live
```

## Read the guides effectively

Each task presents Concept, Challenge, Hint and Check, with required work visible and optional hints in native details disclosures. Horizontal rules separate task boundaries. Use phase contents and task/reasoning return links; compare end-of-phase reasoning after your own attempt. Full runnable reference assets are supplied separately to instructors. Keep the commands, results and business explanation in your attempt's evidence note. Mark any check you could not run.

The supplied Portfolio Analytics and CG capstone cases have distinct fields, units and populations. The shared [runtime setup](runtime/portfolio/SETUP.md) explains the approved namespace, paths, profiles, worker credentials and owned cleanup for Portfolio Analytics. The [CG capstone](../cg-public-products/README.md) has its own product folder, workspace checks and execution instructions; create that product with `mise run challenge:cg:prepare`. Older numeric mise tasks select v1; use `challenge:v2:*` for these phases. Keep previous attempts when preparing a new workspace.
