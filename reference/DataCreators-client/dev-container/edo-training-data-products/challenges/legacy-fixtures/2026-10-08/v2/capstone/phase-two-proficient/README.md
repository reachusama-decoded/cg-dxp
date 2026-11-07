# capstone: Phase two — proficient

This phase has a fixed core of 5 tasks. The advanced standard is a justified design or repair, actual behavioral proof, and a useful handoff. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

## Prerequisites and workspace

Prepared dbt-databricks environment, approved namespace and seven supplied Atlas CSVs. Connected execution is required; unavailable access stays pending.

From the project root run:

```bash
python "$DC_RUNTIME/lab.py" prepare .local/atlas-attempt --checkpoint atlas-advanced
cd .local/atlas-attempt
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

## Assigned tool preparation

Use the delivered training dbt-databricks environment and shared Portfolio/Atlas runtime setup. Record Python, dbt-core and adapter versions before timing; use strict namespace variables, the copied project/profile paths and local target artifacts. Historical pinned local tools belong only to separately labelled optional practice.

## Starter behavior

The assigned Phase 1 starter supplies dimension, latest-price and position baselines; the trade fact and portfolio summary are unfinished and must fail completion. Phase 2 independently supplies completed core models while performance, advisor ranking and region reporting remain unfinished.

Run the baseline authoring check from the copied project with `python "$DC_RUNTIME/lab.py" static .`. The assigned completion check rejects an unfinished starter with exit 1. This is baseline authoring evidence only; use the connected workspace command below after implementing the owning outcomes. Required negative drills remain separate from this initial rejection.

## Timeline and completion standard

Core estimate: **90–120 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

| Task | Outcome | Minutes | Evidence |
|---|---|---|---|
| capstone-p2-01 | Build a meaningful performance report | 18–24 | One row per active portfolio, 1,028 rows |
| capstone-p2-02 | Rank advisor books with explicit ties | 18–24 | Show one row per represented advisor, correct count/sums and equal rank for ties in the demonstration fixture |
| capstone-p2-03 | Build the regional rollup from its declared dependency | 18–24 | Inspect every regional row and verify the sum of portfolio counts is1,028 |
| capstone-p2-04 | Reconcile independently and reject a defect | 18–24 | The wrong-key experiment must fail |
| capstone-p2-05 | Present a fixed completed core and select stretch | 18–24 | Core is complete only when the four output/proof themes are demonstrated |

## Core challenges

### capstone-p2-01: Build a meaningful performance report {#capstone-p2-01}

#### Concept: capstone-p2-01-concept — Build a meaningful performance report

The richer report folds buying/selling values into each portfolio and derives a realized fee rate in basis points. Net flow is bought minus sold; it differs from marked position value. A zero denominator has no meaningful realized rate, so NULL is preferable to a divide-by-zero or a fabricated zero.

<!-- instructor-demo: capstone-p2-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

From the supplied solved Phase 1 baseline create rpt_portfolio_performance.sql with buy_value, sell_value, net_flow and fee_bps_realized. Guard the denominator with nullif. Explain units and test a tiny zero-volume case separately.

#### Hint

Reference existing summary/position models; do not rebuild the 23-modellegacyroute as a prerequisite.

#### Check

One row per active portfolio, 1,028 rows. Independently compare sample values and show a zero-volume example yields NULL rate. The output is a training report, not FX-converted economic AUM.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### capstone-p2-02: Rank advisor books with explicit ties {#capstone-p2-02}

#### Concept: capstone-p2-02-concept — Rank advisor books with explicit ties

An advisor book aggregates its active portfolios. Ranking semantics matter to consumer interpretation: dense_rank gives equal values equal rank and no gaps, while row_number chooses distinct row positions. Decide the business meaning before selecting a window function.

<!-- instructor-demo: capstone-p2-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Create rpt_advisor_book.sql from the summary and rpt_advisor_leaderboard.sql from that book. Carry advisor IDs/names/regions, portfolio counts, book value and fees. Apply dense_rank by book value descending.

#### Hint

Use a small tied-value fixture to explain dense_rank versus rank/row_number; do not force ties in the canonical dataset.

#### Check

Show one row per represented advisor, correct count/sums and equal rank for ties in the demonstration fixture. Explain why advisors with no active portfolio are outside this report population.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### capstone-p2-03: Build the regional rollup from its declared dependency {#capstone-p2-03}

#### Concept: capstone-p2-03-concept — Build the regional rollup from its declared dependency

A regional output summarizes advisor books and therefore has region grain. It intentionally omits portfolio_id as a row key, but must preserve the same active-portfolio/value population through aggregation. The declared prerequisite is the leaderboard, with reconciliation supporting correctness.

<!-- instructor-demo: capstone-p2-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Create rpt_region_report.sql from rpt_advisor_leaderboard, summing book value, fees and portfolio counts by region. Include represented advisor count and describe the consumer question.

#### Hint

This core maps legacyextension14 with extension2 as prerequisite; it does not invent a dependency on an asset-class stretch mart.

#### Check

Inspect every regional row and verify the sum of portfolio counts is1,028. All represented advisors must belong to exactly one region in this fixture.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### capstone-p2-04: Reconcile independently and reject a defect {#capstone-p2-04}

#### Concept: capstone-p2-04-concept — Reconcile independently and reject a defect

Totals can reconcile across a shared faulty upstream population. The independent oracle here starts from raw CSVs and the declared validity/valuation rules, then compares values at portfolio, advisor andregiongrain. A deliberate wrong-key join should be rejected rather than explained away.

<!-- instructor-demo: capstone-p2-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Add reconciliation tests for summary/performance/advisor/region values and counts. In a disposable copy introduce the provided incorrect client/advisor join into an advanced rollup, run the checker and record the failure. Repair and repeat.

#### Hint

The verifier oracle computes raw memberships separately; use its expected counts and per-key comparisons.

#### Check

The wrong-key experiment must fail. Restored reports must agree per key within declared numeric tolerance, have correct grains and retain the 1,028 activepopulation. Save the failed assertion and repaired evidence.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### capstone-p2-05: Present a fixed completed core and select stretch {#capstone-p2-05}

#### Concept: capstone-p2-05-concept — Present a fixed completed core and select stretch

A finite completion standard lets a learner finish advanced work rather than spending the entire event choosing from an unbounded list. This core delivers performance, leaderboard, regionalrollup and reconciliations. Optional extensions deepen another topic but are not hidden requirements for proficiency.

<!-- instructor-demo: capstone-p2-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Prepare a brief consumer demonstration with one portfolio, one advisor andone region; explain ranking, fee units, zero denominators, population and oracle limits. Review the optional stretch index and select at most one later route for your own follow-up.

#### Hint

All 14 legacy extensions are accounted for in the coverage ledger and preserved in v1.

#### Check

Core is complete only when the four output/proof themes are demonstrated. Optional stretch has separate estimates and never supplies missing minutes to this phase.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

## Phase completion

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

```bash
# From the project root, check your copied learner work:
python "$DC_RUNTIME/lab.py" run . --case atlas
```

Execution boundary: Assigned Databricks raw-to-consumer slice; scheduled Astro and human review evidenced separately. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

## Optional stretch

See the [stretch index](stretch/README.md). Each route has its own prerequisites, timing and completion check; none is part of this fixed core.
