# Instructor: dbt Phase 1

Use solution/ as the completed reference in a fresh disposable workspace. verify-starter.sh checks the distinct scaffold baseline; verify.sh checks the completed reference by default. Pass --workspace to assess copied learner work. Never copy over an existing learner attempt.

Boundary: Local DuckDB dbt; optional Databricks rehearsal remains separately measured.

```bash
bash verify-starter.sh --mode offline
bash verify.sh --mode offline
```

--mode live performs the additional available runtime gate. Exit77 means blocked prerequisite, never PASS. GitPhase2needs a real sandbox PR/review; local history simulation is explicitly supporting evidence.

## dbt-p1-01: Inspect the project and source grain

Reference outcome: Show five holdings, three distinct funds and total 250. The status model is intentionally a valid scaffold. Record adapter/version and distinguish the local rehearsal from a connected run.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## dbt-p1-02: Declare and use sources

Reference outcome: Run dbt run --select stg_holdings stg_funds --profiles-dir .. Inspect compiled SQL and explain the difference between the logical source name and physical table name.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## dbt-p1-03: Normalize type, unit and key contracts

Reference outcome: The staged row count remains five, its total remains 250, and the zero-value C holding is retained. Explain why filtering that zero would alter the holdings-count meaning.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## dbt-p1-04: Build a useful mart through ref

Reference outcome: Compare against A:2 holdings/150, B:2/100, C:1/0. There must be three rows and total 250. Explain why a shared grand total alone would not prove each fund is correct.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## dbt-p1-05: Add minimum key and relationship proof

Reference outcome: All tests must pass on a fresh build: dbt seed, then dbt build, against an empty database. In a copied fixture add an unknown fund ID, reseed and show a relationship failure; restore it and rebuild. Save the failed-test name, repair and per-fund evidence.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.
