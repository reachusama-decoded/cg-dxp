# Instructor: dbt phase-two-proficient

The following reasoning is generated from the canonical learner phase. Runnable reference files are in `solution/`; learner setup and task prose remain authoritative in `challenges/v2/dbt/phase-two-proficient/README.md`. Use the complete updated instructor training workspace for runtime commands. Current local checks do not establish fresh connected reconstruction or human acceptance.

## Reference and starter commands

From the updated training project root, use the version-explicit interface. Verification preserves source bytes and runs reference work in a temporary owned copy. Airflow needs fresh scheduled/API/warehouse evidence from the owned stage.

```bash
mise run challenge:v2:verify-starter dbt phase-two-proficient --mode offline
mise run challenge:v2:verify-solution dbt phase-two-proficient --mode offline
```

Supporting or blocked output is not connected completion. Actual learner explanations and intended negative drills need review alongside business behavior.

## Phase-owned reasoning



Read these explanations after attempting the checks.

### Reasoning: Diagnose a join fan-out before repair

<a id="dbt-p2-01-reasoning"></a>

<details>
<summary>Reasoning for dbt-p2-01: Multiplicity reveals an incomplete join key</summary>

Both May price observations share an instrument identifier. The date-free join therefore doubles matching holdings even though raw keys are valid. Matching the business date repairs that particular predicate. A missing match remains a separate coverage concern and should not be solved by dropping the holding. The diagnostic evidence must show input keys, actual multiplicity and the corrected relation, so the reviewer can understand the cause without trusting a final aggregate.

Learner task: `dbt-p2-01` in `challenges/v2/dbt/phase-two-proficient/README.md`.

</details>

### Reasoning: Repair enrichment at the intended grain

<a id="dbt-p2-02-reasoning"></a>

<details>
<summary>Reasoning for dbt-p2-02: Explicit coverage and readable SQL make reuse trustworthy</summary>

The intermediate output should have the same holding grain as staging. Its left joins preserve unmatched observations for diagnosis, and the coverage test rejects them before a consumer result can be accepted. The decimal macro expresses a valuation rule rather than a relationship rule. A rate-of-one fallback would hide a missing declared feed observation; inferring currency from fund master would change the report contract. Both mistakes can yield plausible numbers, so inspect compiled arithmetic and matched keys together.

Learner task: `dbt-p2-02` in `challenges/v2/dbt/phase-two-proficient/README.md`.

</details>

### Reasoning: Write reconciliation that detects the negative case

<a id="dbt-p2-03-reasoning"></a>

<details>
<summary>Reasoning for dbt-p2-03: An independent expected population catches shared model errors</summary>

The useful reconciliation owns its expected keys and units independently of the enrichment. Missing FX should be rejected as coverage loss; restoration repairs that input cause. The correction exercise later changes an input value deliberately, so its expected result is recalculated from the copied input rather than accepted against a stale baseline NAV. A test that merely matches the mart to another aggregate of the same broken model would miss shared loss or duplication. Record the variant and failed assertion together.

Learner task: `dbt-p2-03` in `challenges/v2/dbt/phase-two-proficient/README.md`.

</details>

### Reasoning: Prove incremental update and replay behavior

<a id="dbt-p2-04-reasoning"></a>

<details>
<summary>Reasoning for dbt-p2-04: Replay correctness is a state transition, not a green command</summary>

The merge key identifies the exact dated holding. A copied older-date correction must reach that key even after the later date exists, and running the same correction again must leave the eight-key result unchanged. A new PEF-EM-GROWTH/instrument key then grows the relation to nine, adding 500 GBP without losing the correction; its replay stays at nine. Restoring seed inputs alone cannot delete that inserted target key, so the final owned full-refresh is an explicit restoration step. The independent replay checker uses the modified input, while the custodian NAV fixture still describes baseline data. Delta behavior requires actual warehouse execution and cannot be inferred from compiled SQL. A good report retains before/after state and discloses whether restoration also rebuilt the owned relation.

Learner task: `dbt-p2-04` in `challenges/v2/dbt/phase-two-proficient/README.md`.

</details>

### Reasoning: Explain dependency impact and hand over

<a id="dbt-p2-05-reasoning"></a>

<details>
<summary>Reasoning for dbt-p2-05: A useful handoff states meaning and observed boundaries</summary>

The feature should answer a supported question with a declared key and units. Two exposure observations do not automatically establish return. Snapshot history records a separate changing-attribute contract and needs actual validity queries after a controlled name change. Restoring raw inputs does not erase captured history. Lineage, tests and a reviewable diff explain the terminal result, while the Astro handoff identifies worker paths and authentication that remain unverified until scheduled execution. These distinctions make the product interpretable rather than merely executable.

Learner task: `dbt-p2-05` in `challenges/v2/dbt/phase-two-proficient/README.md`.

</details>
