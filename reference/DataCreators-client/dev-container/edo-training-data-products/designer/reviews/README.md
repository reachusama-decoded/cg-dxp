# Challenge v2 planning reviews

These reviews support [the implementation plan](../PLAN.md). They record source inspection, static findings and proposed review gates; no new runtime challenge verification or learner timing pilot is claimed.

| File | Purpose |
|---|---|
| [Baseline review](2026-10-05-baseline-review.md) | Existing challenge structure, migration/runtime risks and source-grounded findings. |
| [Capstone data review](2026-10-05-capstone-data-review.md) | ID/relationship checks, trade filtering and the active-portfolio population distinction. |
| [Static capstone results](capstone-static-audit.json) | CSV counts, key/relationship findings, reference-SQL membership analysis and seed hashes. |
| [Timing audit](TIMING-AUDIT.md) | 45–120-minute targets, current exceptions, proposed budgets and pilot protocol. |
| [Baseline input hashes](baseline-inputs.json) | Pre-planning project-file inventory for preservation and later migration comparison. |
| [Planning validation](planning-validation.json) | Document/link checks and proof that pre-existing project files were unchanged by this planning delivery. |

Evidence states: **inspected** means the source was read; **static** means local fixture analysis; **proposed** means unimplemented design; **historical** means an earlier supplied report; **observed runtime** requires a new recorded execution; **observed learner timing** requires an actual target-cohort journey. These states must not be substituted for one another.

Later implementation should extend the existing challenge run-ledger convention, retain machine evidence in an ignored/sanitized location, and add an RCA when a root cause is identified. Do not generate a new prose “all passed” report for every repeated run. Timing exceptions remain visible; the audit itself does not rewrite the curriculum to conceal them.

## Implementation evidence

- [Implementation status and limitations](IMPLEMENTATION.md)
- [Verification summary](verification-summary.json)
- [Migration preservation](migration-preservation.json)
- [Source-to-v2 coverage](source-to-v2-coverage.json)
- [Whole-course scheduling audit](SCHEDULING.md)
- [Pilot recording template](PILOT-LEDGER.csv)
