# Instructor: capstone Phase 2

Use solution/ as the completed reference in a fresh disposable workspace. verify-starter.sh checks the distinct scaffold baseline; verify.sh checks the completed reference by default. Pass --workspace to assess copied learner work. Never copy over an existing learner attempt.

Boundary: Local dbt/DuckDB raw-to-consumer slice; separately recorded connected Atlas run.

```bash
bash verify-starter.sh --mode offline
bash verify.sh --mode offline
```

--mode live performs the additional available runtime gate. Exit77 means blocked prerequisite, never PASS. GitPhase2needs a real sandbox PR/review; local history simulation is explicitly supporting evidence.

## capstone-p2-01: Build a meaningful performance report

Reference outcome: One row per active portfolio, 1,028 rows. Independently compare sample values and show a zero-volume example yields NULL rate. The output is a training report, not FX-converted economic AUM.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## capstone-p2-02: Rank advisor books with explicit ties

Reference outcome: Show one row per represented advisor, correct count/sums and equal rank for ties in the demonstration fixture. Explain why advisors with no active portfolio are outside this report population.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## capstone-p2-03: Build the regional rollup from its declared dependency

Reference outcome: Inspect every regional row and verify the sum of portfolio counts is1,028. All represented advisors must belong to exactly one region in this fixture.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## capstone-p2-04: Reconcile independently and reject a defect

Reference outcome: The wrong-key experiment must fail. Restored reports must agree per key within declared numeric tolerance, have correct grains and retain the 1,028 activepopulation. Save the failed assertion and repaired evidence.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## capstone-p2-05: Present a fixed completed core and select stretch

Reference outcome: Core is complete only when the four output/proof themes are demonstrated. Optional stretch has separate estimates and never supplies missing minutes to this phase.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.
