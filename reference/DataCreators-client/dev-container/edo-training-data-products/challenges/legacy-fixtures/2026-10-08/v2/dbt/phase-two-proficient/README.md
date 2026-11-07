# dbt: Phase two — proficient

**Optional small-fixture follow-up.** The assigned course route is the supplied Portfolio Analytics pipeline on dbt-databricks/Astro. This preserved fixture supports separate further practice and its original command contract; it is not a second mandatory assignment.

This phase has a fixed core of 5 tasks. The advanced standard is a justified design or repair, actual behavioral proof, and a useful handoff. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

## Prerequisites and workspace

Prepared dbt-core1.10.13, dbt-duckdb1.9.6, DuckDB1.4.1 local environment. Optional connected profile needs Databricks adapter and isolated provisioned V2_DB_SCHEMA.

From the project root run:

```bash
python3 scripts/challenge-v2.py prepare dbt phase-two-proficient
cd .local/challenges-v2/dbt/phase-two-proficient
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

## Local tool preparation

The instructor runs `bash scripts/setup-v2-tools.sh` once from the project root. Before changing into your copied workspace, activate `.local/v2-tools/bin/activate` to make the pinned `dbt` executable available. For Airflow, use `.local/v2-airflow/bin/python` with a workspace-specific `AIRFLOW_HOME`; do not mix these two Python environments. The verifier supplies these paths automatically in a fresh copy.

## Starter behavior

dbt seed --profiles-dir . and dbt build --profiles-dir . succeed on supplied baseline. Phase 2 exposure is a labelled placeholder.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter dbt phase-two-proficient --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

## Timeline and completion standard

Core estimate: **90–120 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

| Task | Outcome | Minutes | Evidence |
|---|---|---|---|
| dbt-p2-01 | Diagnose a join fan-out before repair | 18–24 | The defective join has seven rows and total 400 instead of five/250 |
| dbt-p2-02 | Repair enrichment at the intended grain | 18–24 | Repaired output must have A: 150 / B: 100 / C: 0, three distinct fund IDs and total250 |
| dbt-p2-03 | Write reconciliation that detects the negative case | 18–24 | Record the expected failed test/result and repaired pass |
| dbt-p2-04 | Prove incremental update and replay behavior | 18–24 | First run:2 rows/180 |
| dbt-p2-05 | Explain dependency impact and hand over | 18–24 | Show the dependency path and saved per-run row totals |

## Core challenges

### dbt-p2-01: Diagnose a join fan-out before repair {#dbt-p2-01}

#### Concept: dbt-p2-01-concept — Diagnose a join fan-out before repair

A dimension with two rows for the same join key turns one fact row into two joined rows. That can inflate money totals while every fact foreign key still has a match. The supplied duplicate-label fixture has two A labels; it is deliberately separate from the canonical funds seed so the baseline still builds.

<!-- instructor-demo: dbt-p2-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Load or inspect fixtures/fund_labels_duplicate.csv. Calculate the result of joining holdings to those labels. Record counts/totals before and after the join and identify the duplicated key.

#### Hint

For A the labels are active and priority. Compare per-fund totals, not only overall row counts.

#### Check

The defective join has seven rows and total 400 instead of five/250. This fixture is intentional; it is not a broken starter. Explain why an ordinary foreign-key relationship test would miss the multiplicity.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### dbt-p2-02: Repair enrichment at the intended grain {#dbt-p2-02}

#### Concept: dbt-p2-02-concept — Repair enrichment at the intended grain

Repair begins with a business rule for which dimension row is authoritative. Arbitrary DISTINCT after aggregation can hide a defect without explaining which facts were duplicated. The canonical funds relation has one row per fund, so it is the appropriate enrichment source for this consumer.

<!-- instructor-demo: dbt-p2-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Replace the placeholder fund_exposure model using the provided typed stages and the canonical fund dimension. Preserve fund names and zero-valued C. Add a uniqueness proof for the chosen dimension and explain why both A labels are not joinable at fund grain.

#### Hint

Phase 2 supplies the completed staging baseline; you do not need to recreate Phase 1.

#### Check

Repaired output must have A: 150 / B: 100 / C: 0, three distinct fund IDs and total250. A reviewer must be able to connect the chosen grain rule to the corrected join.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### dbt-p2-03: Write reconciliation that detects the negative case {#dbt-p2-03}

#### Concept: dbt-p2-03-concept — Write reconciliation that detects the negative case

An independent expected fixture can catch a bug shared by two derived totals. Comparing two models with the same faulty join may pass while both are wrong. Here the oracle is fixed per-fund values and a total of 250, accompanied by a deliberate fan-out case that the check must reject.

<!-- instructor-demo: dbt-p2-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Add a singular reconciliation test and a per-fund comparison. In a temporary copy introduce the duplicate-label join, run the tests and confirm the wrong output is rejected. Restore the correct mart and repeat the build.

#### Hint

Keep the oracle separate from the transformation SQL; do not derive expected numbers from the same output under test.

#### Check

Record the expected failed test/result and repaired pass. Show that a400 total or an inflated A: 300 fails even if another derived total repeats the same mistake.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### dbt-p2-04: Prove incremental update and replay behavior {#dbt-p2-04}

#### Concept: dbt-p2-04-concept — Prove incremental update and replay behavior

An incremental model maintains previous state between runs. A unique key and replacement strategy determine what happens when an existing event is replayed or corrected. This exercise uses event_id as identity and delete+insert in the local adapter; it does not promise exactly-once delivery across systems.

<!-- instructor-demo: dbt-p2-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Create arrival_ledger.sql as an incremental model with unique_key event_id and delete+insert strategy, reading arrivals. Build e1/A100 and e2/B80. Rerun unchanged, then append e3/C20 and change e1 to125. Reseed and run again.

#### Hint

Supply the whole tiny arrivals seed each time. This is replacement by event identity, not a watermark exercise.

#### Check

First run:2 rows/180. Replay:2/180. Corrected+new input:3 rows/225, with e1=125. Rerun again and prove it remains3/225. Record adapter semantics; recheck the chosen strategy before connected Databricks use.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### dbt-p2-05: Explain dependency impact and hand over {#dbt-p2-05}

#### Concept: dbt-p2-05-concept — Explain dependency impact and hand over

Lineage connects the defect to affected consumers and helps bound a rebuild. It is useful when it supports an impact decision, not just a screenshot of nodes. The advanced handoff combines a correct grain, negative-case proof and incremental state observations.

<!-- instructor-demo: dbt-p2-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Run dbt docs generate --profiles-dir . and inspect manifest.json dependencies for staging, exposure and arrival_ledger. Write a short incident note explaining fan-out cause, affected result, repair and replay limits.

#### Hint

Use dbt ls --select +fund_exposure to inspect the parent selection without starting a web service.

#### Check

Show the dependency path and saved per-run row totals. Core completion requires repair, negative-case and replay evidence. Optional stretch: port and measure the adapter-specific OPTIMIZE/ZORDER hook from v1, or author the legacy returns mart.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

## Phase completion

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

```bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify dbt phase-two-proficient --workspace .local/challenges-v2/dbt/phase-two-proficient --mode offline
```

Execution boundary: Local DuckDB dbt; optional Databricks rehearsal remains separately measured. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

## Optional stretch

See the [stretch index](stretch/README.md). Each route has its own prerequisites, timing and completion check; none is part of this fixed core.
