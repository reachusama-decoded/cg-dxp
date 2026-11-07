# Version2 instructor concept companion

Generated from tool-root READMEs and complete phase concept explanations. Demonstrate the relevant before/after state and ask for the evidence boundary.


# git challenges

This route develops minimum competence followed by advanced behavioral proof.  Read concept explanations before attempting the task; retain commands/results and your reasoning.

## Before you start

Local Git forPhase1; authorized private GitHub sandbox, gh, and arranged reviewer forPhase2. Work in a copied phase workspace. Phase 2, when offered, supplies its entry fixture. [Pack navigation](../README.md) explains the course/clinic placement and version selection.

## Suggested timeline and tasks

| Phase | Task ID | Title | Teaching concept | Core/stretch | Minutes |
|---|---|---|---|---|---|
| Phase 1 | [git-p1-01](phase-one-certified/README.md#git-p1-01) | Inspect the three working states | git-p1-01-concept | core | 12–18 |
| Phase 1 | [git-p1-02](phase-one-certified/README.md#git-p1-02) | Commit an intentional contract change | git-p1-02-concept | core | 12–18 |
| Phase 1 | [git-p1-03](phase-one-certified/README.md#git-p1-03) | Branch and combine compatible work | git-p1-03-concept | core | 12–18 |
| Phase 1 | [git-p1-04](phase-one-certified/README.md#git-p1-04) | Resolve an ownership conflict | git-p1-04-concept | core | 12–18 |
| Phase 1 | [git-p1-05](phase-one-certified/README.md#git-p1-05) | Restore a mistake and explain the final history | git-p1-05-concept | core | 12–18 |
| Phase 2 | [git-p2-01](phase-two-proficient/README.md#git-p2-01) | Clone and inspect a collaboration boundary | git-p2-01-concept | core | 15–22 |
| Phase 2 | [git-p2-02](phase-two-proficient/README.md#git-p2-02) | Push and propose a scoped pull request | git-p2-02-concept | core | 15–22 |
| Phase 2 | [git-p2-03](phase-two-proficient/README.md#git-p2-03) | Respond to a review with a second commit | git-p2-03-concept | core | 15–22 |
| Phase 2 | [git-p2-04](phase-two-proficient/README.md#git-p2-04) | Integrate concurrent upstream work | git-p2-04-concept | core | 15–22 |
| Phase 2 | [git-p2-05](phase-two-proficient/README.md#git-p2-05) | Read the final review and merge state | git-p2-05-concept | core | 15–22 |

Inclusive phase estimates: Phase 1 60–90 minutes; Phase 2 75–110 minutes. These estimates are unpiloted. Reading, normal waits, checking and handoff are included; optional stretch is separately identified. [Timing review](../../../designer/reviews/TIMING-AUDIT.md) records current exceptions and the pilot protocol.

## Choose your phase

[Phase one—certified](phase-one-certified/README.md) establishes minimum understanding. [Phase two—proficient](phase-two-proficient/README.md) requires substantive design/diagnosis/replay evidence with a finite core.

## Teaching concepts

The concept column and phase concept headings identify what an instructor can demonstrate. A useful demonstration shows the before state, the relevant change, and independent output/state evidence. The generated instructor companion reproduces concept explanations from these phase READMEs, so notes and challenges share a source.

Suggested destination: Monday preparation / advanced collaboration clinic. Advanced clinics and optional work require separate time; they do not silently consume protected core teaching windows.


## git-p1-01 — Inspect the three working states

#### Concept: git-p1-01-concept --- Inspect the three working states

A working tree contains files you can edit. The index contains the exact next commit; a commit records a snapshot with parent history. An untracked file is not included just because it is in the same directory. This distinction lets you explain what a review will see before sharing work.

```{=html}
<!-- instructor-demo: git-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## git-p1-02 — Commit an intentional contract change

#### Concept: git-p1-02-concept --- Commit an intentional contract change

A useful commit has one reviewable purpose. Staging selects content, and the message explains the change rather than describing the button you pressed. A data contract is an effective example because a deadline clarification can alter a consumer expectation without altering the dataset itself.

```{=html}
<!-- instructor-demo: git-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## git-p1-03 — Branch and combine compatible work

#### Concept: git-p1-03-concept --- Branch and combine compatible work

A branch names a line of development; it is not a second physical copy of every file. Git moves your working files when you switch branches. A merge preserves two lines of history and combines compatible changes. Seeing both edits in the final file matters more than merely receiving a merge success message.

```{=html}
<!-- instructor-demo: git-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## git-p1-04 — Resolve an ownership conflict

#### Concept: git-p1-04-concept --- Resolve an ownership conflict

When two branches edit the same line differently, Git cannot decide the business meaning. Conflict markers delimit candidate text; retaining markers is not a solution. Resolve the contract by choosing its required owner while retaining useful escalation information from the competing proposal.

```{=html}
<!-- instructor-demo: git-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## git-p1-05 — Restore a mistake and explain the final history

#### Concept: git-p1-05-concept --- Restore a mistake and explain the final history

Restoring an uncommitted edit replaces working content from an existing snapshot. It differs from reverting a published commit, which creates new history. A safe local correction starts by inspecting the diff and checking that the work being removed really is the accidental edit.

```{=html}
<!-- instructor-demo: git-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## git-p2-01 — Clone and inspect a collaboration boundary

#### Concept: git-p2-01-concept --- Clone and inspect a collaboration boundary

A clone copies repository history and configures a remote. A tracking branch records the relationship used by fetch/pull/push; it does not mean your local branch automatically contains every upstream change. Collaborating safely requires knowing which repository receives a push and which branch will receive a PR.

```{=html}
<!-- instructor-demo: git-p2-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## git-p2-02 — Push and propose a scoped pull request

#### Concept: git-p2-02-concept --- Push and propose a scoped pull request

Pushing publishes branch commits to a remote; a pull request proposes integrating those commits into another branch. They are separate actions. A useful PR explains the problem, the resulting contract and the verification, so a colleague can review without reconstructing your terminal history.

```{=html}
<!-- instructor-demo: git-p2-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## git-p2-03 — Respond to a review with a second commit

#### Concept: git-p2-03-concept --- Respond to a review with a second commit

Review is a conversation about behavior, maintainability and ownership. Changing code without explaining how it addresses the comment can leave the reviewer uncertain. A second commit allows the review record to distinguish the original proposal from the response.

```{=html}
<!-- instructor-demo: git-p2-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## git-p2-04 — Integrate concurrent upstream work

#### Concept: git-p2-04-concept --- Integrate concurrent upstream work

Fetch obtains remote commits; merging or rebasing decides how they enter your branch. Pull combines these operations according to configuration. Upstream changes can arrive while your PR is open, so the final reviewed result must include both the contract clarification and the new shared input classification.

```{=html}
<!-- instructor-demo: git-p2-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## git-p2-05 — Read the final review and merge state

#### Concept: git-p2-05-concept --- Read the final review and merge state

A green command exit cannot prove a reviewer approved the change or that branch protections were met. Advanced evidence includes the actual PR state, review outcome, checks and resulting main history. Some sandboxes deliberately leave a PR open; that state should be reported honestly instead of fabricating a merge.

```{=html}
<!-- instructor-demo: git-p2-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


# docker challenges

This route develops minimum competence followed by advanced behavioral proof.  Read concept explanations before attempting the task; retain commands/results and your reasoning.

## Before you start

Docker daemon plus pulled python:3.11-slim image. No remote data account. Work in a copied phase workspace. Phase 2, when offered, supplies its entry fixture. [Pack navigation](../README.md) explains the course/clinic placement and version selection.

## Suggested timeline and tasks

| Phase | Task ID | Title | Teaching concept | Core/stretch | Minutes |
|---|---|---|---|---|---|
| Phase 1 | [docker-p1-01](phase-one-certified/README.md#docker-p1-01) | Run an image and inspect the lifecycle | docker-p1-01-concept | core | 12–18 |
| Phase 1 | [docker-p1-02](phase-one-certified/README.md#docker-p1-02) | Explore an interactive shell | docker-p1-02-concept | core | 12–18 |
| Phase 1 | [docker-p1-03](phase-one-certified/README.md#docker-p1-03) | Use a bounded bind mount | docker-p1-03-concept | core | 12–18 |
| Phase 1 | [docker-p1-04](phase-one-certified/README.md#docker-p1-04) | Author and run a simple holdings image | docker-p1-04-concept | core | 12–18 |
| Phase 1 | [docker-p1-05](phase-one-certified/README.md#docker-p1-05) | Prove repeatability and clean scoped resources | docker-p1-05-concept | core | 12–18 |
| Phase 2 | [docker-p2-01](phase-two-proficient/README.md#docker-p2-01) | Separate named build targets | docker-p2-01-concept | core | 15–22 |
| Phase 2 | [docker-p2-02](phase-two-proficient/README.md#docker-p2-02) | Gate the runtime on a tested artifact | docker-p2-02-concept | core | 15–22 |
| Phase 2 | [docker-p2-03](phase-two-proficient/README.md#docker-p2-03) | Run with a bounded runtime user | docker-p2-03-concept | core | 15–22 |
| Phase 2 | [docker-p2-04](phase-two-proficient/README.md#docker-p2-04) | Keep runtime contents focused | docker-p2-04-concept | core | 15–22 |
| Phase 2 | [docker-p2-05](phase-two-proficient/README.md#docker-p2-05) | Repair a path assumption and explain the result | docker-p2-05-concept | core | 15–22 |

Inclusive phase estimates: Phase 1 60–90 minutes; Phase 2 75–110 minutes. These estimates are unpiloted. Reading, normal waits, checking and handoff are included; optional stretch is separately identified. [Timing review](../../../designer/reviews/TIMING-AUDIT.md) records current exceptions and the pilot protocol.

## Choose your phase

[Phase one—certified](phase-one-certified/README.md) establishes minimum understanding. [Phase two—proficient](phase-two-proficient/README.md) requires substantive design/diagnosis/replay evidence with a finite core.

## Teaching concepts

The concept column and phase concept headings identify what an instructor can demonstrate. A useful demonstration shows the before state, the relevant change, and independent output/state evidence. The generated instructor companion reproduces concept explanations from these phase READMEs, so notes and challenges share a source.

Suggested destination: Wednesday Docker practical / advanced image clinic. Advanced clinics and optional work require separate time; they do not silently consume protected core teaching windows.


## docker-p1-01 — Run an image and inspect the lifecycle

#### Concept: docker-p1-01-concept --- Run an image and inspect the lifecycle

An image is a packaged filesystem and startup configuration. A container is an execution of that image with a writable layer and process state. A container exits when its main process exits; running a tiny Python summary to completion does not require keeping a service alive.

```{=html}
<!-- instructor-demo: docker-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## docker-p1-02 — Explore an interactive shell

#### Concept: docker-p1-02-concept --- Explore an interactive shell

An interactive shell lets you inspect the container environment independently from the host. Its root filesystem comes from the image plus the container writable layer. Files created there disappear when that disposable container is removed unless you deliberately persist them.

```{=html}
<!-- instructor-demo: docker-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## docker-p1-03 — Use a bounded bind mount

#### Concept: docker-p1-03-concept --- Use a bounded bind mount

A bind mount exposes a chosen host path at a container path. It can make inputs available without rebuilding the image, but the path and access mode are part of the runtime contract. A read-only input mount prevents the summarizer from changing the source fixture.

```{=html}
<!-- instructor-demo: docker-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## docker-p1-04 — Author and run a simple holdings image

#### Concept: docker-p1-04-concept --- Author and run a simple holdings image

A Dockerfile declares ordered filesystem/runtime instructions. WORKDIR changes subsequent relative paths; COPY brings build-context content into the image; CMD defines the default process. Choosing these deliberately turns the supplied app into a repeatable workload.

```{=html}
<!-- instructor-demo: docker-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## docker-p1-05 — Prove repeatability and clean scoped resources

#### Concept: docker-p1-05-concept --- Prove repeatability and clean scoped resources

Repeatability means the same inputs produce the same useful result in a fresh run. It includes understanding the difference between image state and container state. Cleanup should target names created by this exercise, so one learner does not remove another learner runtime.

```{=html}
<!-- instructor-demo: docker-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## docker-p2-01 — Separate named build targets

#### Concept: docker-p2-01-concept --- Separate named build targets

A multistage Dockerfile can define a test environment and a smaller runtime environment. Building one target does not automatically tag every stage as an image. Separate --target invocations explicitly select which final result you want and make the two contracts inspectable.

```{=html}
<!-- instructor-demo: docker-p2-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## docker-p2-02 — Gate the runtime on a tested artifact

#### Concept: docker-p2-02-concept --- Gate the runtime on a tested artifact

A build-time test can reject a broken artifact before producing the runtime image. A check that merely searches for the word test in the Dockerfile does not prove behavior. The oracle here is the supplied expected summary, which must actually execute against the copied application.

```{=html}
<!-- instructor-demo: docker-p2-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## docker-p2-03 — Run with a bounded runtime user

#### Concept: docker-p2-03-concept --- Run with a bounded runtime user

A runtime user determines the application process identity. Choosing a non-root user and readable owned inputs makes the runtime contract explicit. The learning objective is to explain why the app still works and which paths it can modify, rather than treating USER as a decorative Dockerfile line.

```{=html}
<!-- instructor-demo: docker-p2-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## docker-p2-04 — Keep runtime contents focused

#### Concept: docker-p2-04-concept --- Keep runtime contents focused

Every file included in an image becomes part of its distribution and runtime maintenance. A test stage may need test_summary.py while the runtime needs only the summarizer and data. Inspecting actual contents proves the separation more clearly than comparing image sizes alone.

```{=html}
<!-- instructor-demo: docker-p2-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## docker-p2-05 — Repair a path assumption and explain the result

#### Concept: docker-p2-05-concept --- Repair a path assumption and explain the result

A container command executes relative to its working directory unless given an absolute path. A wrong WORKDIR or COPY destination can break a perfectly valid app. A meaningful repair aligns image contents and process configuration rather than hiding the failure by running a different ad hoc command every time.

```{=html}
<!-- instructor-demo: docker-p2-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


# dbt challenges

This route develops minimum competence followed by advanced behavioral proof.  Read concept explanations before attempting the task; retain commands/results and your reasoning.

## Before you start

Prepared dbt-core1.10.13, dbt-duckdb1.9.6, DuckDB1.4.1 local environment. Optional connected profile needs Databricks adapter and isolated provisioned V2_DB_SCHEMA. Work in a copied phase workspace. Phase 2, when offered, supplies its entry fixture. [Pack navigation](../README.md) explains the course/clinic placement and version selection.

## Suggested timeline and tasks

| Phase | Task ID | Title | Teaching concept | Core/stretch | Minutes |
|---|---|---|---|---|---|
| Phase 1 | [dbt-p1-01](phase-one-certified/README.md#dbt-p1-01) | Inspect the project and source grain | dbt-p1-01-concept | core | 15–22 |
| Phase 1 | [dbt-p1-02](phase-one-certified/README.md#dbt-p1-02) | Declare and use sources | dbt-p1-02-concept | core | 15–22 |
| Phase 1 | [dbt-p1-03](phase-one-certified/README.md#dbt-p1-03) | Normalize type, unit and key contracts | dbt-p1-03-concept | core | 15–22 |
| Phase 1 | [dbt-p1-04](phase-one-certified/README.md#dbt-p1-04) | Build a useful mart through ref | dbt-p1-04-concept | core | 15–22 |
| Phase 1 | [dbt-p1-05](phase-one-certified/README.md#dbt-p1-05) | Add minimum key and relationship proof | dbt-p1-05-concept | core | 15–22 |
| Phase 2 | [dbt-p2-01](phase-two-proficient/README.md#dbt-p2-01) | Diagnose a join fan-out before repair | dbt-p2-01-concept | core | 18–24 |
| Phase 2 | [dbt-p2-02](phase-two-proficient/README.md#dbt-p2-02) | Repair enrichment at the intended grain | dbt-p2-02-concept | core | 18–24 |
| Phase 2 | [dbt-p2-03](phase-two-proficient/README.md#dbt-p2-03) | Write reconciliation that detects the negative case | dbt-p2-03-concept | core | 18–24 |
| Phase 2 | [dbt-p2-04](phase-two-proficient/README.md#dbt-p2-04) | Prove incremental update and replay behavior | dbt-p2-04-concept | core | 18–24 |
| Phase 2 | [dbt-p2-05](phase-two-proficient/README.md#dbt-p2-05) | Explain dependency impact and hand over | dbt-p2-05-concept | core | 18–24 |

Inclusive phase estimates: Phase 1 75–110 minutes; Phase 2 90–120 minutes. These estimates are unpiloted. Reading, normal waits, checking and handoff are included; optional stretch is separately identified. [Timing review](../../../designer/reviews/TIMING-AUDIT.md) records current exceptions and the pilot protocol.

## Choose your phase

[Phase one—certified](phase-one-certified/README.md) establishes minimum understanding. [Phase two—proficient](phase-two-proficient/README.md) requires substantive design/diagnosis/replay evidence with a finite core.

## Teaching concepts

The concept column and phase concept headings identify what an instructor can demonstrate. A useful demonstration shows the before state, the relevant change, and independent output/state evidence. The generated instructor companion reproduces concept explanations from these phase READMEs, so notes and challenges share a source.

Suggested destination: Wednesday dbt practical / advanced transformation clinic. Advanced clinics and optional work require separate time; they do not silently consume protected core teaching windows.


## dbt-p1-01 — Inspect the project and source grain

#### Concept: dbt-p1-01-concept --- Inspect the project and source grain

dbt compiles SQL models into relations and orders them using declared dependencies. The supplied seeds are small deterministic training inputs: five holding rows, three funds and a total market value of 250. Holding grain is fund/instrument; fund grain is fund_id. Profile configuration selects an adapter and database, not a business transformation.

```{=html}
<!-- instructor-demo: dbt-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## dbt-p1-02 — Declare and use sources

#### Concept: dbt-p1-02-concept --- Declare and use sources

source names describe the external input boundary and let lineage/tests refer to it. A source declaration identifies a relation; it does not load CSVs by itself. In this local exercise seeds create the input relations in main, while sources teach the stable logical interface consumed by staging.

```{=html}
<!-- instructor-demo: dbt-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## dbt-p1-03 — Normalize type, unit and key contracts

#### Concept: dbt-p1-03-concept --- Normalize type, unit and key contracts

Staging gives downstream models a consistent shape. A cast should preserve the meaning of a money amount and expose conversion errors, not silently coerce an invalid string. Retain fund_id and instrument_id because the next join and the holding grain rely on them.

```{=html}
<!-- instructor-demo: dbt-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## dbt-p1-04 — Build a useful mart through ref

#### Concept: dbt-p1-04-concept --- Build a useful mart through ref

ref declares a dependency on another dbt model and resolves its physical relation. A mart answers a consumer question at a declared grain. Here the output is one row per fund, including a zero-valued fund, with a holding count and market-value exposure. A left join driven by the fund dimension preserves the fund population.

```{=html}
<!-- instructor-demo: dbt-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## dbt-p1-05 — Add minimum key and relationship proof

#### Concept: dbt-p1-05-concept --- Add minimum key and relationship proof

Uniqueness and non-null tests protect a dimension key; a relationship test finds holding fund IDs without a matching fund. These answer different questions. A relationship test alone does not guarantee a one-to-one join because duplicate dimension keys can still multiply rows. A useful minimum standard includes both structural checks and a known consumer output.

```{=html}
<!-- instructor-demo: dbt-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## dbt-p2-01 — Diagnose a join fan-out before repair

#### Concept: dbt-p2-01-concept --- Diagnose a join fan-out before repair

A dimension with two rows for the same join key turns one fact row into two joined rows. That can inflate money totals while every fact foreign key still has a match. The supplied duplicate-label fixture has two A labels; it is deliberately separate from the canonical funds seed so the baseline still builds.

```{=html}
<!-- instructor-demo: dbt-p2-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## dbt-p2-02 — Repair enrichment at the intended grain

#### Concept: dbt-p2-02-concept --- Repair enrichment at the intended grain

Repair begins with a business rule for which dimension row is authoritative. Arbitrary DISTINCT after aggregation can hide a defect without explaining which facts were duplicated. The canonical funds relation has one row per fund, so it is the appropriate enrichment source for this consumer.

```{=html}
<!-- instructor-demo: dbt-p2-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## dbt-p2-03 — Write reconciliation that detects the negative case

#### Concept: dbt-p2-03-concept --- Write reconciliation that detects the negative case

An independent expected fixture can catch a bug shared by two derived totals. Comparing two models with the same faulty join may pass while both are wrong. Here the oracle is fixed per-fund values and a total of 250, accompanied by a deliberate fan-out case that the check must reject.

```{=html}
<!-- instructor-demo: dbt-p2-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## dbt-p2-04 — Prove incremental update and replay behavior

#### Concept: dbt-p2-04-concept --- Prove incremental update and replay behavior

An incremental model maintains previous state between runs. A unique key and replacement strategy determine what happens when an existing event is replayed or corrected. This exercise uses event_id as identity and delete+insert in the local adapter; it does not promise exactly-once delivery across systems.

```{=html}
<!-- instructor-demo: dbt-p2-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## dbt-p2-05 — Explain dependency impact and hand over

#### Concept: dbt-p2-05-concept --- Explain dependency impact and hand over

Lineage connects the defect to affected consumers and helps bound a rebuild. It is useful when it supports an impact decision, not just a screenshot of nodes. The advanced handoff combines a correct grain, negative-case proof and incremental state observations.

```{=html}
<!-- instructor-demo: dbt-p2-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


# databricks-cli challenges

This route develops a bounded Phase 1 standard.  Read concept explanations before attempting the task; retain commands/results and your reasoning.

## Before you start

Databricks CLI0.236.0 in the supplied client container; DEFAULT profile and metadata permissions. Offline fixtures provide parsing practice only. Work in a copied phase workspace. Phase 2, when offered, supplies its entry fixture. [Pack navigation](../README.md) explains the course/clinic placement and version selection.

## Suggested timeline and tasks

| Phase | Task ID | Title | Teaching concept | Core/stretch | Minutes |
|---|---|---|---|---|---|
| Phase 1 | [databricks-cli-p1-01](phase-one-certified/README.md#databricks-cli-p1-01) | Establish the CLI identity boundary | databricks-cli-p1-01-concept | core | 9–13 |
| Phase 1 | [databricks-cli-p1-02](phase-one-certified/README.md#databricks-cli-p1-02) | Separate workspace and Unity Catalog names | databricks-cli-p1-02-concept | core | 9–13 |
| Phase 1 | [databricks-cli-p1-03](phase-one-certified/README.md#databricks-cli-p1-03) | Inspect permitted schema and table metadata | databricks-cli-p1-03-concept | core | 9–13 |
| Phase 1 | [databricks-cli-p1-04](phase-one-certified/README.md#databricks-cli-p1-04) | Filter JSON and explain a limited result | databricks-cli-p1-04-concept | core | 9–13 |
| Phase 1 | [databricks-cli-p1-05](phase-one-certified/README.md#databricks-cli-p1-05) | Produce a bounded discovery handoff | databricks-cli-p1-05-concept | core | 9–13 |

Inclusive phase estimates: Phase 1 45–65 minutes. These estimates are unpiloted. Reading, normal waits, checking and handoff are included; optional stretch is separately identified. [Timing review](../../../designer/reviews/TIMING-AUDIT.md) records current exceptions and the pilot protocol.

## Choose your phase

[Phase one—certified](phase-one-certified/README.md) establishes minimum understanding. [Phase two—proficient](phase-two-proficient/README.md) is explicitly not offered; its page is a structural placeholder.

## Teaching concepts

The concept column and phase concept headings identify what an instructor can demonstrate. A useful demonstration shows the before state, the relevant change, and independent output/state evidence. The generated instructor companion reproduces concept explanations from these phase READMEs, so notes and challenges share a source.

Suggested destination: Tuesday platform discovery / Wednesday readiness. Advanced clinics and optional work require separate time; they do not silently consume protected core teaching windows.


## databricks-cli-p1-01 — Establish the CLI identity boundary

#### Concept: databricks-cli-p1-01-concept --- Establish the CLI identity boundary

The CLI uses a selected authentication profile and talks to a workspace endpoint. Your shell username does not prove the remote identity. Identity and metadata are safe evidence; tokens and full credential files are not useful learner artifacts.

```{=html}
<!-- instructor-demo: databricks-cli-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## databricks-cli-p1-02 — Separate workspace and Unity Catalog names

#### Concept: databricks-cli-p1-02-concept --- Separate workspace and Unity Catalog names

A workspace directory holds workspace objects such as notebooks. A Unity Catalog catalog contains schemas/tables. A directory called training_dev is not automatically the catalog of the same name, and listing a workspace path is not searching table rows.

```{=html}
<!-- instructor-demo: databricks-cli-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## databricks-cli-p1-03 — Inspect permitted schema and table metadata

#### Concept: databricks-cli-p1-03-concept --- Inspect permitted schema and table metadata

Metadata discovery follows catalog→schema→table. Listing can reveal names/types within your permissions, but it does not execute arbitrary SQL or return dataset rows. A missing listing can reflect lack of visibility rather than an empty business dataset.

```{=html}
<!-- instructor-demo: databricks-cli-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## databricks-cli-p1-04 — Filter JSON and explain a limited result

#### Concept: databricks-cli-p1-04-concept --- Filter JSON and explain a limited result

Structured output can be filtered deterministically and is more useful than visually scanning a large listing. Filtering names is a metadata operation, not full-text table search. Distinguishing an empty list, wrong path and permission denial helps formulate a precise request for an instructor.

```{=html}
<!-- instructor-demo: databricks-cli-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## databricks-cli-p1-05 — Produce a bounded discovery handoff

#### Concept: databricks-cli-p1-05-concept --- Produce a bounded discovery handoff

A useful handoff connects metadata to the next consumer question and states what remains unverified. It does not equate a table name with proof of freshness, row content or suitability. That distinction prevents later dbt work from assuming an unmeasured input contract.

```{=html}
<!-- instructor-demo: databricks-cli-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


# airflow challenges

This route develops minimum competence followed by advanced behavioral proof.  Read concept explanations before attempting the task; retain commands/results and your reasoning.

## Before you start

Prepared Airflow3.1.0/standard provider1.8.0 runtime and a separate dbt executable selected with V2_DBT_BIN. Astro UI route needs instructor-bound isolated workspace. Work in a copied phase workspace. Phase 2, when offered, supplies its entry fixture. [Pack navigation](../README.md) explains the course/clinic placement and version selection.

## Suggested timeline and tasks

| Phase | Task ID | Title | Teaching concept | Core/stretch | Minutes |
|---|---|---|---|---|---|
| Phase 1 | [airflow-p1-01](phase-one-certified/README.md#airflow-p1-01) | Inspect a prepared orchestration baseline | airflow-p1-01-concept | core | 15–22 |
| Phase 1 | [airflow-p1-02](phase-one-certified/README.md#airflow-p1-02) | Author a small Python DAG with real dbt tasks | airflow-p1-02-concept | core | 15–22 |
| Phase 1 | [airflow-p1-03](phase-one-certified/README.md#airflow-p1-03) | Demonstrate the dependency graph and manual run | airflow-p1-03-concept | core | 15–22 |
| Phase 1 | [airflow-p1-04](phase-one-certified/README.md#airflow-p1-04) | Inspect a controlled task failure | airflow-p1-04-concept | core | 15–22 |
| Phase 1 | [airflow-p1-05](phase-one-certified/README.md#airflow-p1-05) | Explain the run and environment boundaries | airflow-p1-05-concept | core | 15–22 |
| Phase 2 | [airflow-p2-01](phase-two-proficient/README.md#airflow-p2-01) | Define bounded replay and input identity | airflow-p2-01-concept | core | 18–24 |
| Phase 2 | [airflow-p2-02](phase-two-proficient/README.md#airflow-p2-02) | Inject failure and observe useful retry behavior | airflow-p2-02-concept | core | 18–24 |
| Phase 2 | [airflow-p2-03](phase-two-proficient/README.md#airflow-p2-03) | Prove output correctness after recovery | airflow-p2-03-concept | core | 18–24 |
| Phase 2 | [airflow-p2-04](phase-two-proficient/README.md#airflow-p2-04) | Use Astro UI to make an operational decision | airflow-p2-04-concept | core | 18–24 |
| Phase 2 | [airflow-p2-05](phase-two-proficient/README.md#airflow-p2-05) | Write a short incident handoff | airflow-p2-05-concept | core | 18–24 |

Inclusive phase estimates: Phase 1 75–110 minutes; Phase 2 90–120 minutes. These estimates are unpiloted. Reading, normal waits, checking and handoff are included; optional stretch is separately identified. [Timing review](../../../designer/reviews/TIMING-AUDIT.md) records current exceptions and the pilot protocol.

## Choose your phase

[Phase one—certified](phase-one-certified/README.md) establishes minimum understanding. [Phase two—proficient](phase-two-proficient/README.md) requires substantive design/diagnosis/replay evidence with a finite core.

## Teaching concepts

The concept column and phase concept headings identify what an instructor can demonstrate. A useful demonstration shows the before state, the relevant change, and independent output/state evidence. The generated instructor companion reproduces concept explanations from these phase READMEs, so notes and challenges share a source.

Suggested destination: Thursday orchestration practical / advanced operations clinic. Advanced clinics and optional work require separate time; they do not silently consume protected core teaching windows.


## airflow-p1-01 — Inspect a prepared orchestration baseline

#### Concept: airflow-p1-01-concept --- Inspect a prepared orchestration baseline

An Airflow DAG declares dependencies between task executions. dbt declares model dependencies within a transformation project. These graphs are related but have different responsibilities: Airflow decides when stages run, while dbt decides how model references are ordered.

```{=html}
<!-- instructor-demo: airflow-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## airflow-p1-02 — Author a small Python DAG with real dbt tasks

#### Concept: airflow-p1-02-concept --- Author a small Python DAG with real dbt tasks

TaskFlow functions become Airflow tasks through decorators. Executing a subprocess inside a task can run dbt directly and fail the task when dbt fails. A small graph is enough to prove scheduling and dependencies without requiring a full Cosmos project reconstruction.

```{=html}
<!-- instructor-demo: airflow-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## airflow-p1-03 — Demonstrate the dependency graph and manual run

#### Concept: airflow-p1-03-concept --- Demonstrate the dependency graph and manual run

A manual run is a specific DAG-run instance with its own task states. schedule=None means Airflow does not create periodic runs automatically; it does not prohibit manual execution. Seeing all tasks green without checking their output would miss a command that ran against the wrong project.

```{=html}
<!-- instructor-demo: airflow-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## airflow-p1-04 — Inspect a controlled task failure

#### Concept: airflow-p1-04-concept --- Inspect a controlled task failure

Task logs tell you which command and input failed; downstream state shows whether the dependency blocked publication. A failed data-quality task must not produce a new success receipt. Understanding that boundary is a minimum operational skill even before advanced retry/replay work.

```{=html}
<!-- instructor-demo: airflow-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## airflow-p1-05 — Explain the run and environment boundaries

#### Concept: airflow-p1-05-concept --- Explain the run and environment boundaries

A local Dag.test run proves task execution in the isolated environment; an Astro UI check proves an additional container/runtime integration. Neither proves remote Databricks access unless the tasks actually used that adapter. Honest evidence binds a run to its environment and output.

```{=html}
<!-- instructor-demo: airflow-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## airflow-p2-01 — Define bounded replay and input identity

#### Concept: airflow-p2-01-concept --- Define bounded replay and input identity

Replay should state which input and run are repeated. A fixed training fixture makes it possible to distinguish pipeline idempotency from changing business data. max_active_runs=1 reduces overlap for this small exercise but does not automatically provide exactly-once behavior.

```{=html}
<!-- instructor-demo: airflow-p2-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## airflow-p2-02 — Inject failure and observe useful retry behavior

#### Concept: airflow-p2-02-concept --- Inject failure and observe useful retry behavior

A retry repeats a failed task according to an explicit policy. It cannot repair permanently bad input by waiting. This drill uses a marker-controlled transient quality failure so you can explain when to retry, when to repair, and why downstream publication must remain blocked.

```{=html}
<!-- instructor-demo: airflow-p2-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## airflow-p2-03 — Prove output correctness after recovery

#### Concept: airflow-p2-03-concept --- Prove output correctness after recovery

A recovered task state is useful only if the output is correct and publication matches the intended run. Stale tables can fool a verifier when a command was skipped. Compare the independently expected values and receipt identity after the repaired run.

```{=html}
<!-- instructor-demo: airflow-p2-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## airflow-p2-04 — Use Astro UI to make an operational decision

#### Concept: airflow-p2-04-concept --- Use Astro UI to make an operational decision

The UI supports investigation through task state, logs, graph and run details. Opening the interface alone is not advanced proficiency. The useful decision is whether the failure is a stale input, connection issue, code defect or an intentional drill, and which scope should be rerun.

```{=html}
<!-- instructor-demo: airflow-p2-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## airflow-p2-05 — Write a short incident handoff

#### Concept: airflow-p2-05-concept --- Write a short incident handoff

A runbook entry links symptom, impact, repair, verification and escalation. It should tell another operator how to reproduce the bounded check without clearing unrelated runs or exposing credentials. Advanced skill is demonstrated by a defensible operational decision with output proof.

```{=html}
<!-- instructor-demo: airflow-p2-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


# kafka challenges

This route develops a bounded Phase 1 standard. Kafka is optional throughout the course. Read concept explanations before attempting the task; retain commands/results and your reasoning.

## Before you start

Optional route. Prepared apache/kafka4.1.0 broker, confluent-kafka2.11.1 bridge and isolated Airflow3.1.0 runtime. Instructor supplies topic/group/runtime boundaries. Work in a copied phase workspace. Phase 2, when offered, supplies its entry fixture. [Pack navigation](../README.md) explains the course/clinic placement and version selection.

## Suggested timeline and tasks

| Phase | Task ID | Title | Teaching concept | Core/stretch | Minutes |
|---|---|---|---|---|---|
| Phase 1 | [kafka-p1-01](phase-one-certified/README.md#kafka-p1-01) | Read the dataset-arrived contract | kafka-p1-01-concept | core | 12–18 |
| Phase 1 | [kafka-p1-02](phase-one-certified/README.md#kafka-p1-02) | Start the prepared local broker and inspect a topic | kafka-p1-02-concept | core | 12–18 |
| Phase 1 | [kafka-p1-03](phase-one-certified/README.md#kafka-p1-03) | Produce and follow a uniquely identified event | kafka-p1-03-concept | core | 12–18 |
| Phase 1 | [kafka-p1-04](phase-one-certified/README.md#kafka-p1-04) | Verify the dbt output belongs to the event | kafka-p1-04-concept | core | 12–18 |
| Phase 1 | [kafka-p1-05](phase-one-certified/README.md#kafka-p1-05) | Replay and explain duplicate policy | kafka-p1-05-concept | core | 12–18 |

Inclusive phase estimates: Phase 1 60–90 minutes. These estimates are unpiloted. Reading, normal waits, checking and handoff are included; optional stretch is separately identified. [Timing review](../../../designer/reviews/TIMING-AUDIT.md) records current exceptions and the pilot protocol.

## Choose your phase

[Phase one—certified](phase-one-certified/README.md) establishes minimum understanding. [Phase two—proficient](phase-two-proficient/README.md) is explicitly not offered; its page is a structural placeholder.

## Teaching concepts

The concept column and phase concept headings identify what an instructor can demonstrate. A useful demonstration shows the before state, the relevant change, and independent output/state evidence. The generated instructor companion reproduces concept explanations from these phase READMEs, so notes and challenges share a source.

Suggested destination: Optional event-driven clinic, outside mandatory course route. Advanced clinics and optional work require separate time; they do not silently consume protected core teaching windows.


## kafka-p1-01 — Read the dataset-arrived contract

#### Concept: kafka-p1-01-concept --- Read the dataset-arrived contract

Kafka retains records in an ordered partition log; consumer groups track offsets. A dataset-arrived event carries identity/version/location so downstream processing can select the intended dataset. It is not the dataset itself. This route deliberately uses a supplied immutable fixture location rather than executing arbitrary producer-provided paths.

```{=html}
<!-- instructor-demo: kafka-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## kafka-p1-02 — Start the prepared local broker and inspect a topic

#### Concept: kafka-p1-02-concept --- Start the prepared local broker and inspect a topic

A topic is a retained stream; one consumer group can resume from committed offsets while a different group reads independently. The instructor supplies the broker runtime and unique topic/group names so learners focus on event flow rather than cluster provisioning.

```{=html}
<!-- instructor-demo: kafka-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## kafka-p1-03 — Produce and follow a uniquely identified event

#### Concept: kafka-p1-03-concept --- Produce and follow a uniquely identified event

A successful producer delivery confirms broker acceptance; it does not prove orchestration or model output. The bridge validates the payload, derives a deterministic DAG-run ID from event identity and triggers the prepared DAG. Follow that identity across boundaries to assess the full chain.

```{=html}
<!-- instructor-demo: kafka-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## kafka-p1-04 — Verify the dbt output belongs to the event

#### Concept: kafka-p1-04-concept --- Verify the dbt output belongs to the event

An event can be valid while referring to the wrong dataset version. The prepared DAG checks fixture identity and dbt produces the known holdings result. A receipt ties the result to run/event identity but independent output inspection still matters.

```{=html}
<!-- instructor-demo: kafka-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## kafka-p1-05 — Replay and explain duplicate policy

#### Concept: kafka-p1-05-concept --- Replay and explain duplicate policy

The bridge retries the same deterministic run ID if it crashes before offset commit. An existing run can be reused only when its stored event payload matches. This makes trigger requests idempotent for identical events in the training setting; it does not promise distributed exactly-once processing or allow conflicting payloads to share identity.

```{=html}
<!-- instructor-demo: kafka-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


# capstone challenges

This route develops minimum competence followed by advanced behavioral proof.  Read concept explanations before attempting the task; retain commands/results and your reasoning.

## Before you start

Prepared local dbt environment and seven supplied Atlas seed CSVs; no cloud access needed for this focused core. Connected Atlas rehearsal remains a separate instructor gate. Work in a copied phase workspace. Phase 2, when offered, supplies its entry fixture. [Pack navigation](../README.md) explains the course/clinic placement and version selection.

## Suggested timeline and tasks

| Phase | Task ID | Title | Teaching concept | Core/stretch | Minutes |
|---|---|---|---|---|---|
| Phase 1 | [capstone-p1-01](phase-one-certified/README.md#capstone-p1-01) | State the consumer population and grain | capstone-p1-01-concept | core | 18–24 |
| Phase 1 | [capstone-p1-02](phase-one-certified/README.md#capstone-p1-02) | Build the valid-trade domain fact | capstone-p1-02-concept | core | 18–24 |
| Phase 1 | [capstone-p1-03](phase-one-certified/README.md#capstone-p1-03) | Author the active portfolio summary | capstone-p1-03-concept | core | 18–24 |
| Phase 1 | [capstone-p1-04](phase-one-certified/README.md#capstone-p1-04) | Investigate expected omission and a defective join | capstone-p1-04-concept | core | 18–24 |
| Phase 1 | [capstone-p1-05](phase-one-certified/README.md#capstone-p1-05) | Prove minimum data quality and give a consumer handoff | capstone-p1-05-concept | core | 18–24 |
| Phase 2 | [capstone-p2-01](phase-two-proficient/README.md#capstone-p2-01) | Build a meaningful performance report | capstone-p2-01-concept | core | 18–24 |
| Phase 2 | [capstone-p2-02](phase-two-proficient/README.md#capstone-p2-02) | Rank advisor books with explicit ties | capstone-p2-02-concept | core | 18–24 |
| Phase 2 | [capstone-p2-03](phase-two-proficient/README.md#capstone-p2-03) | Build the regional rollup from its declared dependency | capstone-p2-03-concept | core | 18–24 |
| Phase 2 | [capstone-p2-04](phase-two-proficient/README.md#capstone-p2-04) | Reconcile independently and reject a defect | capstone-p2-04-concept | core | 18–24 |
| Phase 2 | [capstone-p2-05](phase-two-proficient/README.md#capstone-p2-05) | Present a fixed completed core and select stretch | capstone-p2-05-concept | core | 18–24 |

Inclusive phase estimates: Phase 1 90–120 minutes; Phase 2 90–120 minutes. These estimates are unpiloted. Reading, normal waits, checking and handoff are included; optional stretch is separately identified. [Timing review](../../../designer/reviews/TIMING-AUDIT.md) records current exceptions and the pilot protocol.

## Choose your phase

[Phase one—certified](phase-one-certified/README.md) establishes minimum understanding. [Phase two—proficient](phase-two-proficient/README.md) requires substantive design/diagnosis/replay evidence with a finite core.

## Teaching concepts

The concept column and phase concept headings identify what an instructor can demonstrate. A useful demonstration shows the before state, the relevant change, and independent output/state evidence. The generated instructor companion reproduces concept explanations from these phase READMEs, so notes and challenges share a source.

Suggested destination: Friday capstone / advanced reporting clinic. Advanced clinics and optional work require separate time; they do not silently consume protected core teaching windows.


## capstone-p1-01 — State the consumer population and grain

#### Concept: capstone-p1-01-concept --- State the consumer population and grain

The consumer asks for portfolios with qualifying trading activity. That is different from every portfolio in the dimension. A correct report can omit zero-activity portfolios by design, but the contract must make that population explicit. At portfolio grain retain portfolio/client/advisor identifiers; an aggregated regional report legitimately has another grain.

```{=html}
<!-- instructor-demo: capstone-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## capstone-p1-02 — Build the valid-trade domain fact

#### Concept: capstone-p1-02-concept --- Build the valid-trade domain fact

A domain fact normalizes event meaning and preserves its business identity. Here quantity/price must be positive and side must be B/S; price_cents converts to price by dividing100, fee_bps divides10000, and signed quantity distinguishes buys/sells. Filtering must be accounted for separately from join loss.

```{=html}
<!-- instructor-demo: capstone-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## capstone-p1-03 — Author the active portfolio summary

#### Concept: capstone-p1-03-concept --- Author the active portfolio summary

The supplied position grain is portfolio/instrument. Rolling it up produces one active portfolio row with position count, trading count, value and fees. Joining to unique portfolio/client/advisor dimensions enriches the output without multiplying or dropping valid position keys.

```{=html}
<!-- instructor-demo: capstone-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## capstone-p1-04 — Investigate expected omission and a defective join

#### Concept: capstone-p1-04-concept --- Investigate expected omission and a defective join

A population anti-join shows which conformed portfolios never enter the active report. An unrelated join key can also drop rows even though both columns exist. These are different causes and require different repairs. Comparing counts at each grain keeps the investigation precise.

```{=html}
<!-- instructor-demo: capstone-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## capstone-p1-05 — Prove minimum data quality and give a consumer handoff

#### Concept: capstone-p1-05-concept --- Prove minimum data quality and give a consumer handoff

Structural tests protect key/relationship assumptions; an independent population oracle protects the stated consumer contract. Neither alone proves economic validity, currency normalization or completeness for another population. The handoff should make these limits intelligible to the consumer.

```{=html}
<!-- instructor-demo: capstone-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## capstone-p2-01 — Build a meaningful performance report

#### Concept: capstone-p2-01-concept --- Build a meaningful performance report

The richer report folds buying/selling values into each portfolio and derives a realized fee rate in basis points. Net flow is bought minus sold; it differs from marked position value. A zero denominator has no meaningful realized rate, so NULL is preferable to a divide-by-zero or a fabricated zero.

```{=html}
<!-- instructor-demo: capstone-p2-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## capstone-p2-02 — Rank advisor books with explicit ties

#### Concept: capstone-p2-02-concept --- Rank advisor books with explicit ties

An advisor book aggregates its active portfolios. Ranking semantics matter to consumer interpretation: dense_rank gives equal values equal rank and no gaps, while row_number chooses distinct row positions. Decide the business meaning before selecting a window function.

```{=html}
<!-- instructor-demo: capstone-p2-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## capstone-p2-03 — Build the regional rollup from its declared dependency

#### Concept: capstone-p2-03-concept --- Build the regional rollup from its declared dependency

A regional output summarizes advisor books and therefore has region grain. It intentionally omits portfolio_id as a row key, but must preserve the same active-portfolio/value population through aggregation. The declared prerequisite is the leaderboard, with reconciliation supporting correctness.

```{=html}
<!-- instructor-demo: capstone-p2-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## capstone-p2-04 — Reconcile independently and reject a defect

#### Concept: capstone-p2-04-concept --- Reconcile independently and reject a defect

Totals can reconcile across a shared faulty upstream population. The independent oracle here starts from raw CSVs and the declared validity/valuation rules, then compares values at portfolio, advisor andregiongrain. A deliberate wrong-key join should be rejected rather than explained away.

```{=html}
<!-- instructor-demo: capstone-p2-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```


## capstone-p2-05 — Present a fixed completed core and select stretch

#### Concept: capstone-p2-05-concept --- Present a fixed completed core and select stretch

A finite completion standard lets a learner finish advanced work rather than spending the entire event choosing from an unbounded list. This core delivers performance, leaderboard, regionalrollup and reconciliations. Optional extensions deepen another topic but are not hidden requirements for proficiency.

```{=html}
<!-- instructor-demo: capstone-p2-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
