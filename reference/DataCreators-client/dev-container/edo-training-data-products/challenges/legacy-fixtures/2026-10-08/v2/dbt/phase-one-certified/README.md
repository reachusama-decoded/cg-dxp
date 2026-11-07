# dbt: Phase one — certified

**Optional small-fixture follow-up.** The assigned course route is the supplied Portfolio Analytics pipeline on dbt-databricks/Astro. This preserved fixture supports separate further practice and its original command contract; it is not a second mandatory assignment.

This phase has a fixed core of 5 tasks. The minimum standard is a working result with the underlying tool concepts explained. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

## Prerequisites and workspace

Prepared dbt-core1.10.13, dbt-duckdb1.9.6, DuckDB1.4.1 local environment. Optional connected profile needs Databricks adapter and isolated provisioned V2_DB_SCHEMA.

From the project root run:

```bash
python3 scripts/challenge-v2.py prepare dbt phase-one-certified
cd .local/challenges-v2/dbt/phase-one-certified
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

## Local tool preparation

The instructor runs `bash scripts/setup-v2-tools.sh` once from the project root. Before changing into your copied workspace, activate `.local/v2-tools/bin/activate` to make the pinned `dbt` executable available. For Airflow, use `.local/v2-airflow/bin/python` with a workspace-specific `AIRFLOW_HOME`; do not mix these two Python environments. The verifier supplies these paths automatically in a fresh copy.

## Starter behavior

dbt seed --profiles-dir . and dbt build --profiles-dir . succeed on supplied baseline. Phase 2 exposure is a labelled placeholder.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter dbt phase-one-certified --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

## Timeline and completion standard

Core estimate: **75–110 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

| Task | Outcome | Minutes | Evidence |
|---|---|---|---|
| dbt-p1-01 | Inspect the project and source grain | 15–22 | Show five holdings, three distinct funds and total 250 |
| dbt-p1-02 | Declare and use sources | 15–22 | Run dbt run --select stg_holdings stg_funds --profiles-dir . |
| dbt-p1-03 | Normalize type, unit and key contracts | 15–22 | The staged row count remains five, its total remains 250, and the zero-value C holding is retained |
| dbt-p1-04 | Build a useful mart through ref | 15–22 | Compare against A:2 holdings/150, B:2/100, C:1/0 |
| dbt-p1-05 | Add minimum key and relationship proof | 15–22 | All tests must pass on a fresh build |

## Core challenges

### dbt-p1-01: Inspect the project and source grain {#dbt-p1-01}

#### Concept: dbt-p1-01-concept — Inspect the project and source grain

dbt compiles SQL models into relations and orders them using declared dependencies. The supplied seeds are small deterministic training inputs: five holding rows, three funds and a total market value of 250. Holding grain is fund/instrument; fund grain is fund_id. Profile configuration selects an adapter and database, not a business transformation.

<!-- instructor-demo: dbt-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Activate the prepared local dbt environment. In your copied starter run dbt --version, dbt debug --profiles-dir ., dbt seed --profiles-dir ., then dbt build --profiles-dir . for the benign status model. Inspect both CSVs and record their keys/units.

#### Hint

The default local route uses DuckDB; it needs no cloud account. The connected route uses the provided Databricks profile after instructor provisioning.

#### Check

Show five holdings, three distinct funds and total 250. The status model is intentionally a valid scaffold. Record adapter/version and distinguish the local rehearsal from a connected run.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### dbt-p1-02: Declare and use sources {#dbt-p1-02}

#### Concept: dbt-p1-02-concept — Declare and use sources

source names describe the external input boundary and let lineage/tests refer to it. A source declaration identifies a relation; it does not load CSVs by itself. In this local exercise seeds create the input relations in main, while sources teach the stable logical interface consumed by staging.

<!-- instructor-demo: dbt-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Inspect sources.yml, verify its schema matches your seeded tables, and create stg_holdings.sql using source(training, holdings). Create stg_funds.sql from the funds source. Remove the status model when you have real staging outputs.

#### Hint

Use the Jinja source function shown in the project references; quote its two logical names.

#### Check

Run dbt run --select stg_holdings stg_funds --profiles-dir . Inspect compiled SQL and explain the difference between the logical source name and physical table name.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### dbt-p1-03: Normalize type, unit and key contracts {#dbt-p1-03}

#### Concept: dbt-p1-03-concept — Normalize type, unit and key contracts

Staging gives downstream models a consistent shape. A cast should preserve the meaning of a money amount and expose conversion errors, not silently coerce an invalid string. Retain fund_id and instrument_id because the next join and the holding grain rely on them.

<!-- instructor-demo: dbt-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Cast market_value to decimal(18,2), preserve both identifiers, and inspect all staged rows. Explain that the fixture amounts are a single teaching currency and are already whole money units, not cents.

#### Hint

Compare column names and values before writing a mart. Avoid SELECT DISTINCT as a substitute for a declared grain.

#### Check

The staged row count remains five, its total remains 250, and the zero-value C holding is retained. Explain why filtering that zero would alter the holdings-count meaning.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### dbt-p1-04: Build a useful mart through ref {#dbt-p1-04}

#### Concept: dbt-p1-04-concept — Build a useful mart through ref

ref declares a dependency on another dbt model and resolves its physical relation. A mart answers a consumer question at a declared grain. Here the output is one row per fund, including a zero-valued fund, with a holding count and market-value exposure. A left join driven by the fund dimension preserves the fund population.

<!-- instructor-demo: dbt-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Create fund_exposure.sql using ref(stg_funds) and ref(stg_holdings). Group by fund identifier/name. Produce holdings and exposure, using a zero default for absent money amounts. Build the mart and its parents.

#### Hint

Use dbt run --select +fund_exposure --profiles-dir . Decide what count(column) means on an unmatched left join.

#### Check

Compare against A:2 holdings/150, B:2/100, C:1/0. There must be three rows and total 250. Explain why a shared grand total alone would not prove each fund is correct.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### dbt-p1-05: Add minimum key and relationship proof {#dbt-p1-05}

#### Concept: dbt-p1-05-concept — Add minimum key and relationship proof

Uniqueness and non-null tests protect a dimension key; a relationship test finds holding fund IDs without a matching fund. These answer different questions. A relationship test alone does not guarantee a one-to-one join because duplicate dimension keys can still multiply rows. A useful minimum standard includes both structural checks and a known consumer output.

<!-- instructor-demo: dbt-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Add schema.yml tests for stg_funds.fund_id uniqueness/not-null, holding fund_id relationship/not-null and mart key uniqueness/not-null. Add a singular total-250 check. Run dbt build --profiles-dir . and explain each test.

#### Hint

The YAML examples use data_tests. Pair relationships with uniqueness on the referenced key.

#### Check

All tests must pass on a fresh build. In a copied fixture add an unknown fund ID, run `dbt seed --profiles-dir .` followed by `dbt build --profiles-dir .`, and show the relationship failure. Restore the original CSV, seed again, then rebuild and check the per-fund outputs. Changing a CSV does not reload its source table. Save the failed-test name, repair and per-fund evidence.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

## Phase completion

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

```bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify dbt phase-one-certified --workspace .local/challenges-v2/dbt/phase-one-certified --mode offline
```

Execution boundary: Local DuckDB dbt; optional Databricks rehearsal remains separately measured. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

## Optional stretch

Try a small variation after completing the core: change one input or contract condition in a second disposable copy, predict the result, and verify your prediction. This does not replace a core task or contribute to its timing budget.
