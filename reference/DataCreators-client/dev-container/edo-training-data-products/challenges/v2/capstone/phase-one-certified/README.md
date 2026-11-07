# capstone: Phase 1 — foundations

## Purpose and outcome

Create an Atlas data product that an advisor or consumer can understand. This capstone applies Wednesday's grain, source/ref and independent checks to a distinct supplied client/portfolio/trade dataset. It is not a renamed Portfolio Analytics pipeline: Atlas stores trade prices in cents, fees in basis points and signed position quantities through buy/sell activity. Your team authors a bounded valid-trade fact and an active-portfolio report while prepared models supply supporting dimensions, latest prices and positions.

## Dataset and pipeline

Seven exact supplied CSVs describe trades, portfolios, clients, advisors, instruments, funds and fund holdings. The raw trade feed has ten thousand rows. The declared domain filter keeps positive quantity and price and recognized buy/sell side, yielding 9,880 valid trades. Those trades produce 3,717 portfolio/instrument positions and a report for 1,028 portfolios. The conformed portfolio dimension contains 2,500 rows, so 1,472 portfolios have no qualifying trade participation and do not appear in this trade-driven report.

Source-aligned models retain provenance and normalize input representation; domain-aligned models express reusable business entities; consumer-aligned reports answer a declared question. Keys carry the relationships between these layers. Price cents become decimal units and fee basis points become a fraction of traded value. No FX conversion is supplied, so cross-currency totals are explicitly nominal fixture aggregates. Net signed quantity can be negative; do not confuse that with a raw trade quantity failing the positive-quantity rule.

## Prerequisites and workspace

Open the training project in the supplied dev container, complete the delivered Databricks identity setup and use the approved single catalog/schema. Prepare an independent capstone attempt through mise and choose an owned relation prefix. Keep your team worksheet, contract and evidence in the copy. The starter uses container-safe local artifact paths rather than assuming a Unity Catalog Volume is mounted in the terminal.

```bash
mise run challenge:v2:prepare capstone phase-one-certified
cd .local/challenges-v2/capstone/phase-one-certified
export DC_RELATION_PREFIX=dc_team_atlas01
dbt debug --project-dir . --profiles-dir . --target local
```

Assign a producer, consumer and creator/reviewer role, then agree the report question and output population before writing SQL. The independent advanced baseline is available later; do not copy a completed instructor report over your own work. Record actual adapter and namespace identities, supplied files and any unavailable warehouse/orchestration prerequisite. Keep auth outside recording and tokens out of the team notes.

## Starter behavior

The trade fact and portfolio summary contain declared unfinished outcomes. The prepared supporting graph is disclosed baseline work, not evidence of your team's authoring. Source seeding and project parsing can run before every authored model is complete, while completion verification rejects placeholders. A broad build may fail on those named gaps; select the relevant supplied upstream models while developing. The CSV oracle can inspect expected populations locally, but it cannot prove loaded warehouse relations or executed joins. Restore any copied diagnostic variant before your final baseline evidence.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 90–120 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [capstone-p1-01: State the consumer population and grain](#capstone-p1-01) | 18–24 | Contract distinguishes 2,500 conformed portfolios from 1,028 trade-active report rows |
| [capstone-p1-02: Build the valid-trade domain fact](#capstone-p1-02) | 18–24 | 9,880 valid rows from 10,000 raw; retained trade/key identities and correct cents/bps arithmetic |
| [capstone-p1-03: Author the active portfolio summary](#capstone-p1-03) | 18–24 | 3,717 positions roll up to 1,028 portfolio keys with independent AUM/fee/count values |
| [capstone-p1-04: Investigate expected omission and a defective join](#capstone-p1-04) | 18–24 | 1,472 expected exclusions identified; deliberate client/advisor key mistake loses population |
| [capstone-p1-05: Prove minimum data quality and give a consumer handoff](#capstone-p1-05) | 18–24 | Authored slice, independent populations/values, clear limitation and reviewable presentation |

## Core challenges


<a id="capstone-p1-01"></a>

### capstone-p1-01: State the consumer population and grain


<a id="capstone-p1-01-concept"></a>

#### Concept


A consumer report needs a population as well as a row grain. One row per portfolio describes the shape of output, but does not say whether every known portfolio or only those with qualifying activity should appear. Atlas's core report is driven by valid trades and their resulting positions. A conformed portfolio with no qualifying trade participation can legitimately be absent under that contract. It should not silently disappear if the consumer expected an all-portfolio inventory.

The supplied fixture makes this distinction measurable: 2,500 conformed portfolios, 1,028 with qualifying trade-derived output, and 1,472 without it. Keys remain important even for omitted populations because an anti-join must identify exactly which portfolios are absent and why. Source→domain→consumer alignment connects that business meaning to transformations. For example, cents become decimal price units before position valuation, and a portfolio's advisor key connects to the advisor dimension. A diagram without the correct keys or units cannot protect against a plausible but wrong join. State the intended question and relationship before deciding how many tables to build.

#### Challenge


Write a small consumer contract and source-to-target mapping in the copied team project. State the consumer question, one-row-per-portfolio grain, active-by-qualifying-trade population, retained identifiers and money/fee units. List the seven supplied CSVs and trace trades through the valid domain fact and prepared positions into the summary. Identify the prepared supporting models and the two focus models your team authors.

For the opening team discussion, choose at least two possible business-facing outputs and work backwards from their consumers and decisions to sources and rules in plain English. Record a producer–creator–consumer map, a consumer-backwards map, a source-to-target mapping for four to six fields, and a shared glossary with trust questions in your team evidence note. Include price cents, fee basis points, valid trades, latest prices and the lack of FX conversion. Assign facilitator, scribe, quality challenger and playback roles, combining them for a small team. Use the separate 30–60 minute discovery timebox; then choose the trade-active portfolio summary as the finite implemented core. Keep the second output as a discussed candidate, and revisit the opening assumptions in your final handoff.

Inspect the source key relationships between portfolios, clients, advisors and instruments. Choose one portfolio and follow its identifiers through the supplied dimension files. State whether no-trade portfolios should be reported as absent or with an explicit empty status for this core; use the declared trade-active route for the assessed result, and describe the all-portfolio variant separately. Record the fixture's native-currency aggregation limitation and avoid importing the Portfolio Analytics GBP or synthetic NAV assumptions into Atlas.

#### Hint


<details>
<summary>State population separately from one-row-per-portfolio grain</summary>

Begin with the consumer's question and write population and grain on separate lines. Then identify the key that carries each relationship. Compare the raw/conformed portfolio inventory with trade-derived membership before selecting a join style. A null-filled all-portfolio result would be a different contract, not an automatic repair for a trade-active report. Keep prices in cents and fees in basis points until the mapping states their conversion.

</details>

#### Check


Inspect the team contract for an explicit consumer, population, grain, identifiers, units and limitation. Run the independent reference locally to establish the supplied fixture expectation, then compare warehouse populations when connected. Expect 2,500 conformed portfolios, 1,028 reported active portfolios and 1,472 without qualifying trade-derived output. Do not treat the difference as missing identifiers without inspecting membership.

Retain the chosen portfolio's source relationship trace and the authored-versus-supplied model inventory. Explain why an all-portfolio inventory needs a different population contract and why a single row count cannot reveal a wrong advisor join. The source-to-target mapping should identify the conversion from cents and basis points rather than merely list table names. Local CSV arithmetic and a drafted contract are useful preparation, while actual conformed/consumer warehouse counts remain pending until the model graph executes. This task establishes the intended meaning against which later SQL is assessed.

Check that the opening worksheet records two candidate consumer outputs, all four mapping/glossary sections and the team's assumptions. Explain why discussing a second output does not silently expand the assessed SQL scope. Compare those assumptions with the implemented result during the final playback.

```bash
python runtime/lab.py reference . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p1-01-reasoning)


---


<a id="capstone-p1-02"></a>

### capstone-p1-02: Build the valid-trade domain fact


<a id="capstone-p1-02-concept"></a>

#### Concept


A domain fact defines which raw observations represent valid business activity and how their values are expressed. Atlas keeps trades with positive quantity and price and a recognized buy/sell side. That rule excludes 120 of the ten thousand raw rows in this fixture. Retaining trade, portfolio and instrument identifiers allows the consumer and quality checks to trace that selection instead of relying on an unexplained reduction in count.

Price cents must be divided by one hundred to obtain decimal currency units. Fee basis points are divided by ten thousand when applied to traded value. For a simple worked example, two units at 12,500 cents create 250 currency units of traded value; a twenty-basis-point fee is 0.50 units. Multiplying by twenty as a percentage would be wrong by orders of magnitude. Buy and sell are directions used later for signed position quantity; a raw sell trade can have positive quantity and remain valid. A nonnegative test on derived signed net position would therefore enforce the wrong contract. Types, units and filters must be explained together.

#### Challenge


Complete the valid-trade domain SQL in the copied focus file. Read the supplied source-aligned trade relation, apply the declared quantity/price/side rules, retain the business identifiers and timestamp, and compute decimal price, traded value and fee using the documented conversions. Keep the sell direction explicit for downstream signed aggregation instead of changing valid raw quantity into an unexplained negative value.

Build the supplied upstream source slice and the authored trade fact, then inspect raw rows excluded by each rule. Record the independent raw/valid populations and a manually calculated trade-value/fee example from the actual copied CSV. Add or review the test that protects trade-key uniqueness, required relationships and valid population. Do not remove rows merely because a later portfolio summary is incomplete, and do not make the model's own count its only expected oracle.

#### Hint


<details>
<summary>Check filter rules and money units as separate obligations</summary>

Separate selection from arithmetic in readable CTEs so a failed population and a failed value can be diagnosed independently. State the units beside each derived expression. Inspect a valid sell and an invalid quantity or price row to confirm the intended filter. A decimal conversion should happen before money aggregation, not after a large integer or floating-point computation has already lost the intended meaning.

</details>

#### Check


Expect ten thousand raw trades and exactly 9,880 valid domain trades, with retained unique trade identifiers and no invented portfolio or instrument keys. Compare the selected key set with the independent CSV filter rather than only comparing counts. Inspect the chosen actual trade and reproduce its decimal value and fee manually. The price conversion is cents to currency units; the fee conversion is basis points to a fraction of traded value.

Retain the selected build/test artifacts, excluded-rule summary and independent value check. Introduce a bounded copied invalid side or quantity case only if you can predict its intended exclusion and restore it afterward. Explain why a valid sell can retain positive raw quantity and why the signed position aggregation is a different downstream rule. The final baseline must preserve the original supplied input hashes. A parsed model or correct-looking sample is insufficient until the warehouse population and values are checked against the independent contract.

```bash
dbt build --select +dom_trading__trade --project-dir . --profiles-dir . --target local
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p1-02-reasoning)


---


<a id="capstone-p1-03"></a>

### capstone-p1-03: Author the active portfolio summary


<a id="capstone-p1-03-concept"></a>

#### Concept


A portfolio summary aggregates positions at portfolio grain, then attaches the client and advisor context through the declared portfolio relationships. Positions are at portfolio/instrument grain, so several positions can contribute to one report row. Aggregating or joining at the wrong key can duplicate market value, attach another advisor or exclude a portfolio without an obvious SQL error. Retained identifiers make those defects inspectable.

The prepared position model sums signed quantity and fees across valid trades and uses a deterministic latest-price observation. The summary then reports nominal fixture market value, fees, trade count and position count. It does not convert currencies or establish realized investment performance. Those limitations matter when explaining a consumer metric. The supplied 3,717 positions yield 1,028 portfolio summaries, not one report row for every conformed portfolio. A correct grand total can still hide value shifted between portfolios, so compare full portfolio-key projections and relationship identities. Descriptive names enrich the result but cannot replace stable keys.

#### Challenge


Complete the copied portfolio-summary model through references to the prepared positions and portfolio/client/advisor dimensions. Use the declared portfolio, client and advisor relationships, aggregate at one row per portfolio, and retain the required identifiers alongside descriptive context. Include nominal AUM, fees, trade count and position count with consistent units. Keep the source-to-target mapping and consumer contract updated as you implement.

Inspect the prepared position and latest-price models to understand what was supplied. Pick one active portfolio and independently calculate its output from copied trades and dimensions, then compare the warehouse result. Build the summary's upstream graph and check membership before presenting totals. If a portfolio unexpectedly disappears, inspect its trade participation and each join predicate rather than adding a distinct or switching join types without a population decision. Do not invent rows for inactive portfolios inside this core report.

#### Hint


<details>
<summary>Trace each relationship key before attaching names</summary>

Follow the portfolio key from positions into the portfolio dimension, then follow the separate client and advisor keys from that dimension. Similar-looking integer IDs are not interchangeable. Count distinct portfolios before and after each relationship. Inspect one multi-position portfolio to confirm that position count and trade count represent different measures, and keep the latest-price tie-break rule in your explanation.

</details>

#### Check


The report must contain exactly 1,028 unique portfolio keys derived from 3,717 prepared positions. Compare each portfolio's client/advisor identity, nominal AUM, fees, trade count and position count against the independent CSV reference. Inspect at least one multi-position portfolio manually to explain the aggregation rather than accepting an output sample solely because it is nonempty.

Retain build/run-results identity, selected key/value projection and the relevant source-to-target mapping. Structural uniqueness/not-null/relationship checks must agree with the business population, and a grand sum cannot replace per-key comparison. Explain why names are attributes rather than join keys and why this fixture aggregate is not FX-normalized valuation. If a join loses a key, report the anti-join result and diagnose the actual predicate. Keep warehouse execution pending when only local fixture arithmetic is available; the independent expected output does not itself prove your SQL ran.

```bash
dbt build --select +rpt_portfolio_summary --project-dir . --profiles-dir . --target local
python runtime/lab.py check . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p1-03-reasoning)


---


<a id="capstone-p1-04"></a>

### capstone-p1-04: Investigate expected omission and a defective join


<a id="capstone-p1-04-concept"></a>

#### Concept


An anti-join answers which declared keys are absent from another population. It is more informative than subtracting two row counts because it identifies the missing members and lets you inspect their cause. For Atlas, comparing all conformed portfolios with the trade-active summary reveals the expected 1,472 portfolios without qualifying activity. Comparing a correct relationship with a deliberately wrong join reveals a different, avoidable loss.

Portfolio client identifiers and advisor identifiers can both be integers without describing the same entity. Joining a portfolio's client key to the advisor dimension can accidentally match a subset and drop the rest. The output may still contain familiar advisor names and plausible amounts. That defect cannot be explained as inactive population merely because the row count is smaller. Keep the business membership rule separate from the SQL relationship predicate. The consumer may later choose an all-portfolio variant, but that is a contract change with explicit empty-status semantics, not permission to disguise an erroneous join.

#### Challenge


Write a diagnostic comparison from the conformed portfolio dimension to the correctly built trade-active report. Identify the absent portfolio keys and show whether each lacks qualifying trade-derived positions. Retain the expected population counts and an example of an excluded portfolio in the team evidence note.

In a bounded diagnostic query, reproduce the wrong relationship that joins portfolio client identifiers to advisor identifiers. Compare its membership with the correct advisor-key join and identify at least one unexpectedly lost or misattached key. Keep the defect out of the final consumer model and restore the declared relationship before completion. Explain the difference between expected inactive omission, invalid-trade exclusion and defective join loss. Update the consumer contract only if your team deliberately chooses a separately scoped all-portfolio extension; do not rewrite it after seeing a bad result to make the defect acceptable.

#### Hint


<details>
<summary>Give every missing key an explicit population reason</summary>

Start with key sets and reason labels rather than a grand total. Trace the actual portfolio row's client and advisor fields into their corresponding dimensions. A matching integer value does not imply the same business entity. Use the supplied independent reference to anchor the correct active membership, and inspect an unexpected anti-join row before deciding whether missing trade participation explains it.

</details>

#### Check


The correct active report must contain 1,028 of the 2,500 conformed portfolio keys, with 1,472 explained as lacking qualifying trade-derived output. The deliberate wrong-key diagnostic must lose or misattach population for its stated predicate reason, and the final repaired model must return to the independent expected membership and values. A smaller count alone is insufficient evidence of either case.

Retain the anti-join SQL, representative missing keys, wrong and corrected predicates, and actual warehouse query identities when available. Explain why two reconciliations built downstream of the same dropped population could still agree numerically. Your consumer handoff should name the expected excluded population and show how a defect would be distinguished from it. Keep local CSV classification separate from executed warehouse diagnostics. Restore the baseline copied sources and relationship logic before running the final phase verifier; the diagnostic failure should remain evidence, not become the shipped report.

```bash
# Inspect anti-join membership and relationship predicates in the actual warehouse.
python runtime/lab.py reference . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p1-04-reasoning)


---


<a id="capstone-p1-05"></a>

### capstone-p1-05: Prove minimum data quality and give a consumer handoff


<a id="capstone-p1-05-concept"></a>

#### Concept


A data product is useful when its consumer can understand what the output represents, which quality promises were checked and what its limits are. SQL completion and a green test summary are technical evidence, but the consumer also needs population, units, timing and ownership. The Atlas minimum slice makes this concrete through valid trades, positions and an active-portfolio report with an independently accounted excluded population.

Quality assertions should protect keys, relationships, filter membership and business arithmetic. A relationship test alone may ignore nulls; a numeric reconciliation alone may share a lost population; an output sample alone cannot establish complete keys. The team therefore combines structural tests with independent per-key comparison and a controlled wrong-join diagnosis. The presentation describes the nominal-money limitation and supplied supporting baseline, avoiding claims of FX-normalized AUM or official performance. Roles help review the result: the producer explains source meaning, the creator explains transformations, and the consumer challenges whether the report answers its stated question.

#### Challenge


Finish the schema and singular quality checks for the authored trade fact and portfolio summary. Confirm the raw/valid/position/report populations, required identifiers, relationship keys and money/fee conversions. Retain the intended wrong-key failure and repaired result rather than presenting only the final green command.

Prepare a short consumer handoff and demonstration. State the question, active-portfolio population, excluded population, output grain, nominal-money limitation and actual observed runtime boundary. Show a representative independently checked portfolio and the lineage from supplied sources. Present the bounded authored diff and identify which dimensions/positions/helpers were supplied. Inspect prepared orchestration only when its actual environment is available; do not claim a scheduled Atlas run from source presence alone. Record pending warehouse, worker or human checks explicitly and choose optional advanced work only after the fixed minimum standard is met.

#### Hint


<details>
<summary>Explain the business result and the evidence that protects it</summary>

Build the presentation around one consumer decision and one fully traced portfolio rather than a tour of every file. Put independent population and unit evidence beside the metric being shown. Use the wrong-key diagnostic to explain why trust requires more than a matching grand total. Clearly separate a source-backed planned orchestration step from an observed scheduled run, and disclose any instructor-reference comparison after your own attempt.

</details>

#### Check


Run the final baseline build and independent Atlas comparison in the owned namespace. Expected populations remain ten thousand raw trades, 9,880 valid trades, 3,717 positions, 1,028 active reported portfolios and 1,472 conformed portfolios without qualifying output. The report's complete identifier/value projection must agree independently, not merely its row count or overall sum.

Inspect the handoff for consumer question, population, grain, units, limitations, authored-versus-supplied work, current artifacts and remaining gates. Retain a selected trade fee calculation and portfolio aggregation explanation, plus the failed/repaired relationship diagnostic. Demonstrate the Databricks output in your own attempt. If showing orchestration, identify the scheduled run that produced it. Review the presentation with your consumer role before handoff.

```bash
dbt build --project-dir . --profiles-dir . --target local
python runtime/lab.py check . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p1-05-reasoning)


## Phase completion


Your minimum capstone result is a meaningful source→domain→consumer slice, with a retained business key, explicit trade filters and a documented consumer population. Submit the valid-trade fact and portfolio-summary SQL, their structural/business checks, a small source-to-target mapping and a consumer handoff. The independent reference must identify 10,000 raw trades, 9,880 valid trades, 3,717 portfolio/instrument positions and 1,028 reported portfolios. Account separately for the 1,472 conformed portfolios without qualifying trades instead of labelling them accidental loss.

Retain one controlled wrong-key join and explain why it drops population, then show the repaired output and independent key/value comparison. State what the prepared dimensions, latest-price and position models supplied and what your team authored. Explain cents, decimal money, basis-point fees and the fixture's lack of FX conversion. The consumer report is a nominal teaching aggregate, not an investment recommendation or a complete real-world portfolio valuation. Warehouse execution and prepared orchestration remain pending until actually observed. Team roles, reviewable changes and a short presentation connect the technical result to a consumer question; optional extensions follow the fixed completion gate.

---


## Optional stretch


The core completion standard is independent of optional work. No additional stretch is required in this phase; the next phase has an independently prepared entry baseline.

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: State the consumer population and grain

<a id="capstone-p1-01-reasoning"></a>

<details>
<summary>Reasoning for capstone-p1-01: Population omission can be expected or a defect depending on contract</summary>

The core asks for trade-active portfolios, so 1,472 conformed portfolios without qualifying trades are expected exclusions. Their identifiers remain necessary for an anti-join and explanatory handoff. An all-portfolio inventory would use a different membership contract and likely an explicit empty status. The mapping connects units and relationship keys to the consumer result; it cannot borrow GBP/NAV assumptions from the separate Portfolio Analytics case. Local fixture expectations still need warehouse confirmation.

[Return to capstone-p1-01](#capstone-p1-01)

</details>

### Reasoning: Build the valid-trade domain fact

<a id="capstone-p1-02-reasoning"></a>

<details>
<summary>Reasoning for capstone-p1-02: Valid trade rules precede signed position and fee aggregation</summary>

The valid domain fact selects 9,880 recognized positive-quantity/price trades while retaining their business identifiers. Cents and basis points have different scaling factors. A sell is valid activity even though it later reduces signed position quantity. Independent membership and per-trade arithmetic detect filtering or unit mistakes that a model's own row count could conceal. Do not impose a raw-trade positivity rule on a derived signed net-position measure.

[Return to capstone-p1-02](#capstone-p1-02)

</details>

### Reasoning: Author the active portfolio summary

<a id="capstone-p1-03-reasoning"></a>

<details>
<summary>Reasoning for capstone-p1-03: Stable relationship keys and per-portfolio values establish the result</summary>

The consumer row is an active portfolio, built from portfolio/instrument positions and joined through its declared client/advisor keys. Position count is not trade count, and names cannot substitute for identifiers. Independent per-key comparison detects shifted values and misattached relationships despite plausible overall totals. The report's nominal fixture AUM lacks FX conversion, so the consumer explanation must preserve that limitation rather than present it as a complete investment valuation.

[Return to capstone-p1-03](#capstone-p1-03)

</details>

### Reasoning: Investigate expected omission and a defective join

<a id="capstone-p1-04-reasoning"></a>

<details>
<summary>Reasoning for capstone-p1-04: Expected omission and accidental loss need different evidence</summary>

The expected missing 1,472 keys have no qualifying trade-derived participation under the stated consumer contract. A wrong client-to-advisor relationship creates another loss that must not be relabelled inactive. Key-level anti-joins and source relationship traces distinguish these causes. Shared downstream totals can agree after the same population was lost, so independent membership is necessary. The final repaired consumer graph must reproduce both expected keys and values.

[Return to capstone-p1-04](#capstone-p1-04)

</details>

### Reasoning: Prove minimum data quality and give a consumer handoff

<a id="capstone-p1-05-reasoning"></a>

<details>
<summary>Reasoning for capstone-p1-05: A consumer handoff joins business meaning to independent technical evidence</summary>

The minimum result is a trusted active-portfolio slice, not every possible Atlas extension. Independent membership and per-key values complement structural tests and the wrong-join drill. The handoff states cents/basis-point conversions, nominal-money limitations and the expected inactive population. It identifies supplied support and actual runtime observations. Prepared source or a local reference calculation cannot stand in for warehouse/orchestration execution or human presentation acceptance.

[Return to capstone-p1-05](#capstone-p1-05)

</details>
