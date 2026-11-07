# Instructor: dbt Phase 2

Use solution/ as the completed reference in a fresh disposable workspace. verify-starter.sh checks the distinct scaffold baseline; verify.sh checks the completed reference by default. Pass --workspace to assess copied learner work. Never copy over an existing learner attempt.

Boundary: Local DuckDB dbt; optional Databricks rehearsal remains separately measured.

```bash
bash verify-starter.sh --mode offline
bash verify.sh --mode offline
```

--mode live performs the additional available runtime gate. Exit77 means blocked prerequisite, never PASS. GitPhase2needs a real sandbox PR/review; local history simulation is explicitly supporting evidence.

## dbt-p2-01: Diagnose a join fan-out before repair

Reference outcome: The defective join has seven rows and total 400 instead of five/250. This fixture is intentional; it is not a broken starter. Explain why an ordinary foreign-key relationship test would miss the multiplicity.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## dbt-p2-02: Repair enrichment at the intended grain

Reference outcome: Repaired output must have A: 150 / B: 100 / C: 0, three distinct fund IDs and total250. A reviewer must be able to connect the chosen grain rule to the corrected join.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## dbt-p2-03: Write reconciliation that detects the negative case

Reference outcome: Record the expected failed test/result and repaired pass. Show that a400 total or an inflated A: 300 fails even if another derived total repeats the same mistake.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## dbt-p2-04: Prove incremental update and replay behavior

Reference outcome: First run:2 rows/180. Replay:2/180. Corrected+new input:3 rows/225, with e1=125. Rerun again and prove it remains3/225. Record adapter semantics; recheck the chosen strategy before connected Databricks use.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## dbt-p2-05: Explain dependency impact and hand over

Reference outcome: Show the dependency path and saved per-run row totals. Core completion requires repair, negative-case and replay evidence. Optional stretch: port and measure the adapter-specific OPTIMIZE/ZORDER hook from v1, or author the legacy returns mart.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.
