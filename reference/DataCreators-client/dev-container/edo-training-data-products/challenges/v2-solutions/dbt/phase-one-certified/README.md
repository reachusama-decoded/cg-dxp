# Instructor: dbt phase-one-certified

The following reasoning is generated from the canonical learner phase. Runnable reference files are in `solution/`; learner setup and task prose remain authoritative in `challenges/v2/dbt/phase-one-certified/README.md`. Use the complete updated instructor training workspace for runtime commands. Current local checks do not establish fresh connected reconstruction or human acceptance.

## Reference and starter commands

From the updated training project root, use the version-explicit interface. Verification preserves source bytes and runs reference work in a temporary owned copy. Airflow needs fresh scheduled/API/warehouse evidence from the owned stage.

```bash
mise run challenge:v2:verify-starter dbt phase-one-certified --mode offline
mise run challenge:v2:verify-solution dbt phase-one-certified --mode offline
```

Supporting or blocked output is not connected completion. Actual learner explanations and intended negative drills need review alongside business behavior.

## Phase-owned reasoning



Read these explanations after attempting the checks.

### Reasoning: Inspect the project and source grain

<a id="dbt-p1-01-reasoning"></a>

<details>
<summary>Reasoning for dbt-p1-01: A connection is a prerequisite, not a product result</summary>

The expected inventory contains two observations for each of four funds. The composite holding key includes date and instrument, so an eight-row source can be valid even though fund identifiers repeat. Source declarations map logical inputs to already loaded relations; they cannot replace seeding. A target named local describes configuration selection, while its type selects Databricks execution. Good evidence separates CSV inspection, connection readiness and actual warehouse population, retaining an unavailable boundary as pending instead of combining them into one vague pass.

Learner task: `dbt-p1-01` in `challenges/v2/dbt/phase-one-certified/README.md`.

</details>

### Reasoning: Declare and use sources

<a id="dbt-p1-02-reasoning"></a>

<details>
<summary>Reasoning for dbt-p1-02: Logical dependencies and physical ownership must both be correct</summary>

A source call declares an external input; a model reference declares a derived dependency. The identifier expression resolves the source into an owned physical relation without putting environment-specific names into every model. Missing input and wrong source mapping can produce similar first errors, but their repairs differ. The manifest plus seed inventory distinguishes them. Reference data can be loaded and inspected without forcing it into this bounded consumer graph. The complete chain is evidence of understandable lineage, not proof that a compiled query has executed.

Learner task: `dbt-p1-02` in `challenges/v2/dbt/phase-one-certified/README.md`.

</details>

### Reasoning: Normalize type, unit and key contracts

<a id="dbt-p1-03-reasoning"></a>

<details>
<summary>Reasoning for dbt-p1-03: Typed staging preserves business observations</summary>

The expected transformation changes representation without losing either May date. Fund/date/instrument is the row identity; fund alone is a reporting dimension. Correct decimal and date types support later business calculations, but do not prove the join coverage by themselves. The duplicate-key drill should fail because it creates a second observation at the same declared grain. Restoring the copied raw input repairs that cause. Multiplying quantity by price would create a different valuation measure and must not replace the supplied native value.

Learner task: `dbt-p1-03` in `challenges/v2/dbt/phase-one-certified/README.md`.

</details>

### Reasoning: Build a useful mart through ref

<a id="dbt-p1-04-reasoning"></a>

<details>
<summary>Reasoning for dbt-p1-04: Reconciliation tests every business key and value</summary>

The correct report has eight rows because date is part of the consumer key. Its GBP numerator uses the supplied native valuation and a matching dated FX rate. The synthetic unit count creates a holdings value per synthetic unit measure; the cash exclusion and currency choice must travel with the result. A table materialization changes storage and refresh behavior, not the expected business values. Full per-key comparison detects collapsed dates and shifted fund totals that a single grand-total check could miss.

Learner task: `dbt-p1-04` in `challenges/v2/dbt/phase-one-certified/README.md`.

</details>

### Reasoning: Add minimum key and relationship proof

<a id="dbt-p1-05-reasoning"></a>

<details>
<summary>Reasoning for dbt-p1-05: A meaningful drill identifies the failing contract</summary>

Structural assertions and the independent reference protect different risks. An unknown fund should fail membership or retained-population checks; a missing FX observation should fail dated enrichment coverage rather than be replaced by a rate of one. The useful evidence connects the controlled change to the actual failed test, then connects restoration and reseeding to the recovered eight-key report. A generic command failure or a final green screenshot cannot establish that sequence. The untouched starter remains unfinished until the authored outcomes and their checks are complete.

Learner task: `dbt-p1-05` in `challenges/v2/dbt/phase-one-certified/README.md`.

</details>
