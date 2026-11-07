# capstone: Phase one — certified

This phase has a fixed core of 5 tasks. The minimum standard is a working result with the underlying tool concepts explained. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

## Prerequisites and workspace

Prepared dbt-databricks environment, approved namespace and seven supplied Atlas CSVs. Connected execution is required; unavailable access stays pending.

From the project root run:

```bash
python "$DC_RUNTIME/lab.py" prepare .local/atlas-attempt --checkpoint atlas
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
| capstone-p1-01 | State the consumer population and grain | 18–24 | Record 10,000 raw trades, 2,500 conformed portfolios and 1,028 active portfolios |
| capstone-p1-02 | Build the valid-trade domain fact | 18–24 | Build and inspect 9,880 valid trades; explain the 120 excluded rows |
| capstone-p1-03 | Author the active portfolio summary | 18–24 | There must be3,717 positions and 1,028 summary portfolios |
| capstone-p1-04 | Investigate expected omission and a defective join | 18–24 | The defective query is an intentional teaching fixture, not a starter defect |
| capstone-p1-05 | Prove minimum data quality and give a consumer handoff | 18–24 | All minimum tests pass with known counts |

## Core challenges

### capstone-p1-01: State the consumer population and grain {#capstone-p1-01}

#### Concept: capstone-p1-01-concept — State the consumer population and grain

The consumer asks for portfolios with qualifying trading activity. That is different from every portfolio in the dimension. A correct report can omit zero-activity portfolios by design, but the contract must make that population explicit. At portfolio grain retain portfolio/client/advisor identifiers; an aggregated regional report legitimately has another grain.

<!-- instructor-demo: capstone-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Read contract.md and all seven seeds. Write a short STTM/population note for an active-portfolio summary. Identify fields to retain and the expected raw/conformed/active populations. State the native-currency teaching simplification.

#### Hint

The complete preserved Atlas route remains in v1; this core authors only the valid-trade fact and portfolio summary, with supplied dimension/prepared stages.

#### Check

Record 10,000 raw trades, 2,500 conformed portfolios and 1,028 active portfolios. Explain why a1472 portfolio gap is not proof of a missing ID column.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### capstone-p1-02: Build the valid-trade domain fact {#capstone-p1-02}

#### Concept: capstone-p1-02-concept — Build the valid-trade domain fact

A domain fact normalizes event meaning and preserves its business identity. Here quantity/price must be positive and side must be B/S; price_cents converts to price by dividing100, fee_bps divides10000, and signed quantity distinguishes buys/sells. Filtering must be accounted for separately from join loss.

<!-- instructor-demo: capstone-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Create dom_trading__trade.sql reading the trades seed through ref. Retain trade_id, timestamp, portfolio/instrument keys; derive direction, signed_qty, price, gross_value and fee. Apply the declared validity filters. The independent starter already supplies latest-price/position models in models/. Inspect their grain and joins after this fact exists; no instructor-file copy is a learner prerequisite.

#### Hint

Two prepared models depend on the fact and are stored outside model discovery until you add it. This keeps the baseline build usable.

#### Check

Build and inspect 9,880 valid trades; explain the 120 excluded rows. Check trade_id uniqueness/non-null and money/sign conversions on representative buy/sell examples.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### capstone-p1-03: Author the active portfolio summary {#capstone-p1-03}

#### Concept: capstone-p1-03-concept — Author the active portfolio summary

The supplied position grain is portfolio/instrument. Rolling it up produces one active portfolio row with position count, trading count, value and fees. Joining to unique portfolio/client/advisor dimensions enriches the output without multiplying or dropping valid position keys.

<!-- instructor-demo: capstone-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Create rpt_portfolio_summary.sql using ref(dom_positions__position) plus the supplied conformed dimensions. Retain portfolio/client/advisor IDs and descriptive fields, aggregate at portfolio grain and build the slice.

#### Hint

Group all retained descriptors with portfolio_id. Inspect dimension key uniqueness before trusting inner joins.

#### Check

There must be3,717 positions and 1,028 summary portfolios. Check that every position portfolio is represented once in the summary. Explain the retained identifiers and native-currency valuation limit.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### capstone-p1-04: Investigate expected omission and a defective join {#capstone-p1-04}

#### Concept: capstone-p1-04-concept — Investigate expected omission and a defective join

A population anti-join shows which conformed portfolios never enter the active report. An unrelated join key can also drop rows even though both columns exist. These are different causes and require different repairs. Comparing counts at each grain keeps the investigation precise.

<!-- instructor-demo: capstone-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Anti-join conformed portfolios to distinct valid-trade portfolio IDs and to the summary. Identify1472 zero-activity portfolios. In a disposable query run fixtures/defective_join.sql, which joins client_id to advisor_id, and compare its membership to the correct portfolio→advisor relationship.

#### Hint

Use NOT EXISTS or a left anti-join for population comparison; do not compare unlike grains.

#### Check

The defective query is an intentional teaching fixture, not a starter defect. Show its lost membership and repair on pf.advisor_id=a.advisor_id. Explain why blindly changing every join to LEFT JOIN would not define a correct all-portfolio report.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### capstone-p1-05: Prove minimum data quality and give a consumer handoff {#capstone-p1-05}

#### Concept: capstone-p1-05-concept — Prove minimum data quality and give a consumer handoff

Structural tests protect key/relationship assumptions; an independent population oracle protects the stated consumer contract. Neither alone proves economic validity, currency normalization or completeness for another population. The handoff should make these limits intelligible to the consumer.

<!-- instructor-demo: capstone-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->

#### Challenge

Add minimum trade-key uniqueness/non-null, trade portfolio/instrument relationships, summary-key tests and exact population checks. Run a fresh seed/build/test. Present one portfolio result plus the absence explanation and the source→domain→consumer path.

#### Hint

Fresh builds matter: a file-only reset cannot prove a warehouse contains the current models.

#### Check

All minimum tests pass with known counts. Hand over contract, authored files, representative rows, anti-join evidence and native-currency limitation. Use the supplied orchestration baseline to explain where this slice would execute; connected Atlas execution is a separate gate.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

## Phase completion

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

```bash
# From the project root, check your copied learner work:
python "$DC_RUNTIME/lab.py" run . --case atlas
```

Execution boundary: Assigned Databricks raw-to-consumer slice; scheduled Astro and human review evidenced separately. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

## Optional stretch

Try a small variation after completing the core: change one input or contract condition in a second disposable copy, predict the result, and verify your prediction. This does not replace a core task or contribute to its timing budget.
