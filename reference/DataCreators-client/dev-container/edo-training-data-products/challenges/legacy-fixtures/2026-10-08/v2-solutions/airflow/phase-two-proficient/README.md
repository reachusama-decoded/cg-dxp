# Instructor: airflow Phase 2

Use solution/ as the completed reference in a fresh disposable workspace. verify-starter.sh checks the distinct scaffold baseline; verify.sh checks the completed reference by default. Pass --workspace to assess copied learner work. Never copy over an existing learner attempt.

Boundary: Airflow local Dag.test execution; Astro UI and connected adapter gates separate.

```bash
bash verify-starter.sh --mode offline
bash verify.sh --mode offline
```

--mode live performs the additional available runtime gate. Exit77 means blocked prerequisite, never PASS. GitPhase2needs a real sandbox PR/review; local history simulation is explicitly supporting evidence.

## airflow-p2-01: Define bounded replay and input identity

Reference outcome: Both runs must produce three fund rows/250 and matching per-fund values. Record run IDs and explain which state is replaced by dbt materialization.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## airflow-p2-02: Inject failure and observe useful retry behavior

Reference outcome: Show the failed task and blocked publication, then repaired quality and published receipt. Record attempts/run identity. Do not mark the task successful manually as a substitute for rerunning the test.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## airflow-p2-03: Prove output correctness after recovery

Reference outcome: Correct final state is A: 150 / B: 100 / C: 0, one row per fund, successful quality and a receipt for the repaired run. Show unchanged output after another replay.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## airflow-p2-04: Use Astro UI to make an operational decision

Reference outcome: Retain run/task identifiers and a description of the relevant log/state evidence. A hosted Astronomer route is optional and requires prepared access.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.

## airflow-p2-05: Write a short incident handoff

Reference outcome: The handoff must explain blocked publication and correct recovered output. Optional stretch: connect an existing neutral alert transport or prepared Datadog monitor and demonstrate an actionable observation; configuration text alone is insufficient.

Review the learner explanation as well as the executable result. The supplied assets implement this outcome; the negative cases and replay checks are exercised by the verifier when that runtime boundary is available.
