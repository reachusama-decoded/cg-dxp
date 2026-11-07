# Instructor: capstone Phase 1

Use solution/ as the completed reference in a fresh disposable workspace. verify-starter.sh checks the distinct scaffold baseline; verify.sh checks the completed reference by default. Pass --workspace to assess copied learner work. Never copy over an existing learner attempt.

Boundary: Local dbt/DuckDB raw-to-consumer slice; separately recorded connected Atlas run.

```bash
bash verify-starter.sh --mode offline
bash verify.sh --mode offline
```

--mode live performs the additional available runtime gate. Exit77 means blocked prerequisite, never PASS. GitPhase2needs a real sandbox PR/review; local history simulation is explicitly supporting evidence.

## capstone-p1-01: State the consumer population and grain

Reference outcome: Record 10,000 raw trades, 2,500 conformed portfolios and 1,028 active portfolios. Explain why a1472 portfolio gap is not proof of a missing ID column.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## capstone-p1-02: Build the valid-trade domain fact

Reference outcome: Build and inspect 9,880 valid trades; explain the 120 excluded rows. Check trade_id uniqueness/non-null and money/sign conversions on representative buy/sell examples.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## capstone-p1-03: Author the active portfolio summary

Reference outcome: There must be3,717 positions and 1,028 summary portfolios. Check that every position portfolio is represented once in the summary. Explain the retained identifiers and native-currency valuation limit.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## capstone-p1-04: Investigate expected omission and a defective join

Reference outcome: The defective query is an intentional teaching fixture, not a starter defect. Show its lost membership and repair on pf.advisor_id=a.advisor_id. Explain why blindly changing every join to LEFT JOIN would not define a correct all-portfolio report.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## capstone-p1-05: Prove minimum data quality and give a consumer handoff

Reference outcome: All minimum tests pass with known counts. Hand over contract, authored files, representative rows, anti-join evidence and native-currency limitation. Use the supplied orchestration baseline to explain where this slice would execute; connected Atlas execution is a separate gate.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.
