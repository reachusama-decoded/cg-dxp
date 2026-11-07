# capstone: Phase 2 — advanced practice

## Purpose and outcome

Extend the active-portfolio product into three useful reporting views: portfolio trading/fee detail, an advisor book leaderboard and regional aggregation. Build the three reports, reconcile their results and demonstrate a defect and repair before choosing optional extensions.

## Dataset and pipeline

Use the same seven supplied Atlas CSVs and prepared baseline models. The starter already supplies valid trades, positions, active portfolio summary and advisor book. Three consumer SQL files remain unfinished. Performance is one row per active portfolio, the leaderboard one row per participating advisor, and the regional report one row per region represented by that leaderboard. The regional dependency is the leaderboard; it does not depend on inventing a new trade source or completing every other extension.

The independent baseline identifies 9,880 valid trades, 3,717 positions and 1,028 active portfolios. Nominal AUM and fees follow the fixture's native-unit aggregation without FX conversion. Trading volume means buys plus sells, while net flow is buys minus sells; neither equals current market value. The realized fee rate is total fees divided by total traded value, expressed back in basis points. Ties share dense rank without gaps, and a zero denominator produces an explicitly documented null rather than an invalid division or silently accepted zero fee rate.

## Prerequisites and workspace

Prepare a fresh advanced capstone attempt from the training project root, then run direct dbt commands inside it with the approved namespace and unique owned prefix. The baseline represents the completed foundation semantics and is supplied even if your team did not complete the foundation route. Inspect its model contracts before extending them. Record actual dbt adapter/target and keep artifact paths local to the prepared container attempt.

```bash
mise run challenge:v2:prepare capstone phase-two-proficient
cd .local/challenges-v2/capstone/phase-two-proficient
export DC_RELATION_PREFIX=dc_team_atlas02
dbt debug --project-dir . --profiles-dir . --target local
```

Confirm the consumer's intended comparison and measurement limitations before choosing an extension. Team roles review business meaning, transformation grain and independent evidence. Installation/access preparation is outside the unpiloted core estimate, and optional work has separate timing. Credentials stay outside source and presentation evidence.

## Starter behavior

The performance, leaderboard and regional report files contain declared unfinished outcomes. Completion verification rejects those placeholders even though the supplied baseline graph is useful and parseable. Build the baseline supporting slice first when diagnosing dependencies; an empty placeholder output cannot establish the final report population. Negative reconciliation drills must change only copied models or inputs and predict the intended failure. Keep the original supplied CSVs and baseline outputs available for restoration. A local independent reference can establish expected populations and values while actual warehouse execution remains pending.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 90–120 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [capstone-p2-01: Build a meaningful performance report](#capstone-p2-01) | 18–24 | 1,028 portfolio keys; independent buys/sells/fees; explicit zero-safe basis-point rate |
| [capstone-p2-02: Rank advisor books with explicit ties](#capstone-p2-02) | 18–24 | One row per advisor; dense ties without gaps; independent book totals and counts |
| [capstone-p2-03: Build the regional rollup from its declared dependency](#capstone-p2-03) | 18–24 | Region advisor/portfolio counts and nominal totals reconcile independently |
| [capstone-p2-04: Reconcile independently and reject a defect](#capstone-p2-04) | 18–24 | Omitted advisor contribution fails reconciliation; repair restores all expected keys/values |
| [capstone-p2-05: Present a fixed completed core and select stretch](#capstone-p2-05) | 18–24 | Three report grains, independent values, defect/repair narrative and optional extension choices |

## Core challenges


<a id="capstone-p2-01"></a>

### capstone-p2-01: Build a meaningful performance report


<a id="capstone-p2-01-concept"></a>

#### Concept


A richer report adds measures with distinct business meanings rather than renaming the same total. Buy and sell value describe traded activity, net flow describes their difference, and current nominal AUM describes signed position quantity valued at the prepared latest price. These measures can differ substantially without being inconsistent. The portfolio performance report combines baseline summary fields with position-level bought/sold totals reaggregated to portfolio grain.

The realized fee rate is a weighted rate: aggregate fees divided by aggregate traded value, multiplied by ten thousand to express basis points. Averaging trade fee rates would weight a tiny trade the same as a large one and answer another question. For example, a fee of one on total traded value of one thousand corresponds to ten basis points, not one percent or a fraction mislabeled as basis points. A zero traded denominator needs an explicit null-safe rule. This fixture does not provide a flow-adjusted investment-return calculation or FX-normalized wealth measure, so the report title and consumer explanation must not claim either.

#### Challenge


Complete the copied performance-report SQL using the prepared portfolio summary and position model. Reaggregate bought and sold values to portfolio before joining them to the one-row-per-portfolio summary. Retain portfolio identifier, nominal AUM, fees, counts, buy/sell values, net flow and a null-safe realized fee rate with its units documented.

Calculate one actual portfolio independently from copied trades and compare its numerator and denominator with the prepared positions. Build the consumer model and inspect all active keys. Add a bounded zero-denominator expression test even if every supplied active portfolio has nonzero trading volume. Document why weighted fee rate differs from an average fee-basis-point field and why net flow differs from current valuation. Do not add an FX assumption or performance-return claim unsupported by these sources. Keep the supplied baseline and newly authored report responsibilities explicit.

#### Hint


<details>
<summary>Aggregate volume before joining and label the weighted rate</summary>

Check the grain of the bought/sold input before joining: the positions relation has multiple instrument rows per portfolio. Sum those values at portfolio grain first. Write the fee-rate numerator, denominator and scaling factor in words before SQL. The independent CSV calculation should use decimal price conversion and fee arithmetic rather than copying your report query, so it can detect the same mistake you are trying to test.

</details>

#### Check


The report must contain the same 1,028 active portfolio keys as the baseline summary. Compare buy value, sell value, net flow and realized fee rate per key with the independent reference; also retain the baseline AUM/fee/count fields without duplicating them through a position join. The standalone zero-denominator case must return the documented null rather than crash or manufacture a zero rate.

Inspect a selected portfolio's raw trades and explain its weighted rate calculation. Retain run-results identity, independent projection and zero-case evidence. A matching overall buy/sell sum cannot prove each portfolio's values. Explain why nominal AUM, traded volume and net flow represent different measures and why none automatically establishes investment return. Keep actual warehouse behavior pending when only SQL and local reference arithmetic have been prepared. The type and population assertions must agree with the consumer contract rather than a convenient sample.

```bash
dbt build --select +rpt_portfolio_performance --project-dir . --profiles-dir . --target local
python runtime/lab.py reference . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p2-01-reasoning)


---


<a id="capstone-p2-02"></a>

### capstone-p2-02: Rank advisor books with explicit ties


<a id="capstone-p2-02-concept"></a>

#### Concept


A leaderboard defines both the participating population and the ranking rule. Here the prepared advisor book aggregates active portfolio reports, so participation follows the declared trade-active consumer population rather than every advisor record in the raw reference. Stable advisor identifiers and region attributes must remain available for reconciliation and the later regional rollup. A display name alone is not a safe grouping or relationship key.

Dense ranking gives equal book values the same rank and assigns the next distinct value the next integer. With values ten, ten and five, dense ranks are one, one and two. A row-number function instead forces a unique order, while ordinary rank can leave a gap; those alternatives support different consumer interpretations. A separate deterministic display ordering can use advisor identifier after rank without breaking the tie meaning. The supplied nominal book values inherit the fixture's absence of FX conversion, so a leaderboard comparison must state that limitation rather than turn the ranking into a real-world advice claim.

#### Challenge


Complete the advisor-leaderboard model through a reference to the prepared advisor book. Retain advisor identifier/name, region, portfolio count, nominal book AUM and fees, then add the declared dense ranking by descending book value. Keep display tie-break ordering separate from rank semantics. Inspect how the prepared advisor book obtains its active-portfolio population.

Create a bounded three-value tie example and compare dense rank, rank and row-number behavior so your explanation does not depend on the fixture containing an accidental tie. Build the authored leaderboard and independently aggregate portfolio outputs by advisor to compare identities, participation, counts and values. Document the ranking rule and native-unit limitation for the intended advisor dashboard. Do not group solely by names or include inactive advisors with invented zero books without a separately stated population change.

#### Hint


<details>
<summary>Separate ranking semantics from stable display ordering</summary>

Use the prepared advisor book's declared grain rather than rejoining position-level data into the leaderboard. Inspect ties with a small explicit values relation and read the resulting rank sequence. A final display sort can be stable while several advisors still share the same dense rank. For population discrepancies, compare participating advisor keys from the portfolio summary before changing the rank function.

</details>

#### Check


Expect one row per independently participating advisor, with book AUM, fees and portfolio count matching aggregation of the active portfolio reference. The rank must agree with descending distinct book values, and the explicit ten/ten/five example must produce dense ranks one/one/two. An arbitrary row order in a preview is not the ranking contract; inspect rank values and display ordering separately.

Retain the actual model/test run identity, independent advisor-key projection and tie-example result. Explain the difference among dense rank, rank and row number, and why names cannot replace stable advisor IDs. The regional model depends on the leaderboard's retained region and aggregate fields, so do not remove them as presentation-only columns. State the nominal native-unit comparison limitation. A correct-looking first five advisors cannot prove complete participation or independent book values; keep warehouse execution pending when only the source and local reference are available.

```bash
dbt build --select +rpt_advisor_leaderboard --project-dir . --profiles-dir . --target local
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p2-02-reasoning)


---


<a id="capstone-p2-03"></a>

### capstone-p2-03: Build the regional rollup from its declared dependency


<a id="capstone-p2-03-concept"></a>

#### Concept


A rollup changes grain through aggregation, so each measure must be interpreted at the new grain. The regional report groups the advisor leaderboard by region, counting participating advisor rows and summing their portfolio counts, nominal AUM and fees. Counting raw trades would produce another measure entirely. Rejoining lower-grain positions after the leaderboard could duplicate advisor totals and make the report look larger without adding new consumer meaning.

This dependency is explicit: the regional report requires the completed leaderboard and its region/totals, while the separate performance mart supports another question. The core does not need every legacy extension before a region can be built. Region membership must be inherited from the declared advisor mapping, not guessed from an advisor name or client segment. Summing region totals can match a shared upstream error, so the independent oracle should rebuild expected regions from copied source relationships and valid-trade values. Key membership and counts complement the numeric comparison.

#### Challenge


Complete the regional-report SQL through a reference to the authored advisor leaderboard. Produce one row per represented region with participating advisor count, portfolio count, nominal AUM and fees. Keep the dependency visible in the model and document the grain change. Read the leaderboard contract to ensure the fields you aggregate retain their intended meanings.

Independently calculate one region from copied portfolio/advisor relationships and the active-portfolio reference, then compare all regions with the warehouse output. Inspect manifest lineage to show the regional report depends on the leaderboard. Verify that running the regional selection with its upstream graph supplies the right prerequisites without requiring the performance report as an accidental dependency. If a region is missing, inspect participating advisor keys before inserting an empty display row. An all-region inventory would be a separately scoped population contract.

#### Hint


<details>
<summary>Aggregate the declared advisor grain without rejoining activity</summary>

Start with one advisor row from the leaderboard and trace how its portfolio count and money values contribute to a region. Keep row count, summed portfolio count and monetary totals separate. Build the region from the declared one-row-per-advisor input instead of joining raw activity again. The independent reference should use source relationships so it can detect a wrong region assignment shared by two derived reports.

</details>

#### Check


The report must have one key per independently represented region, and each region's advisor count, portfolio count, nominal AUM and fees must agree with the copied-input oracle. Compare key membership and values for every region rather than only a grand sum. Inspect the manifest edge to the leaderboard and confirm the selected build includes the actual prerequisite graph.

Retain a manually traced advisor contribution, independent regional projection, artifact identity and the documented population limitation. Explain why counting leaderboard rows measures participating advisors and why summing portfolio counts differs from counting raw trades. A region-total reconciliation against only the same broken leaderboard would be insufficient independent evidence. When the warehouse is unavailable, author the SQL, calculate expectations locally and leave actual execution pending. Keep the report's nominal native-unit interpretation visible in the consumer handoff rather than relabelling it a globally converted valuation.

```bash
dbt build --select +rpt_region_report --project-dir . --profiles-dir . --target local
python runtime/lab.py check . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p2-03-reasoning)


---


<a id="capstone-p2-04"></a>

### capstone-p2-04: Reconcile independently and reject a defect


<a id="capstone-p2-04-concept"></a>

#### Concept


Reconciliation needs sensitivity to a realistic defect, not just a happy-path pass. A regional report that omits an advisor can still return familiar region names and plausible positive totals. The independent expected contribution must expose the lost advisor/portfolio membership and money. Comparing only two outputs that share the omission could miss it completely.

The controlled negative drill changes a copied report predicate to omit a participating advisor. Its failed assertion should identify the affected region/key/value contract. Restoring that predicate and rebuilding the model repairs the cause; changing the expected oracle or tolerance would merely hide it. Keep the baseline raw data unchanged so the difference comes from the deliberate model defect. Tie and zero-denominator examples protect separate semantics and should not be counted as this omission drill. A nonzero build exit alone could arise from credentials or an unfinished unrelated model, so inspect the actual failed node and diagnostic rows before declaring the negative case meaningful.

#### Challenge


Write or review the regional reconciliation test so it compares independently expected membership/counts and monetary values at region grain. State its tolerance and explain how it detects a missing advisor contribution. Run the complete authored core against the baseline copied inputs before injecting a defect.

In a disposable model copy, exclude one participating advisor contribution from the regional report and rerun the selected model/test. Retain the failed node, affected region and independently calculated difference. Restore the report predicate and rebuild the same graph, then rerun the complete performance/leaderboard/region comparison. Keep the failure and repair diff small enough for a reviewer to understand. Do not alter raw seed fixtures or the expected reference to make the defective output acceptable, and do not erase the failed artifact when collecting the final passing run.

#### Hint


<details>
<summary>Predict a nonempty omitted contribution before changing the query</summary>

Select a participating advisor whose contribution is nonempty, and predict the affected region before editing. Compare region membership and counts before monetary tolerance. Inspect the test's compiled SQL to ensure its expectation is not merely the same filtered report again. Keep the defective SQL outside your final authored version after recording the failure, then verify restoration through a fresh selected build.

</details>

#### Check


The baseline core must agree with all independently expected portfolio, advisor and region values. The deliberately filtered regional query must fail its named reconciliation for the omitted contribution, with a diagnostic difference in the expected region. After restoring the predicate, the same test and independent output comparison must pass. An unrelated authentication or compile failure is not the intended negative result.

Retain source/model hashes, baseline and failed/repaired run identities, affected membership/value projection and bounded repair diff. Explain why a comparison against the same filtered leaderboard/report would not be independent and why loosening the tolerance is the wrong repair. Recheck the performance rate and leaderboard tie semantics after the regional repair without rerunning an unrelated production deployment. If only static/local expectations can be prepared here, mark the warehouse defect/repair sequence pending rather than claiming the checker script alone has proved execution.

```bash
dbt test --select reconcile_region --project-dir . --profiles-dir . --target local
python runtime/lab.py check . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p2-04-reasoning)


---


<a id="capstone-p2-05"></a>

### capstone-p2-05: Present a fixed completed core and select stretch


<a id="capstone-p2-05-concept"></a>

#### Concept


An advanced capstone should have a finite completion standard so a team can demonstrate a coherent product rather than an arbitrary collection of files. Here the three consumer views support related but distinct questions: portfolio trading/fee detail, advisor book comparison and regional aggregation. Their grains and dependencies make that relationship understandable. The presentation must explain how independent checks and the omission drill protect the output, not merely display a long list of passed tests.

Optional depth can extend windows, freshness, exposures, macros, generic tests, incrementals, snapshots or orchestration, but each adds prerequisites and time. Selecting an extension does not erase unfinished core reports, and finishing every legacy extension is not mandatory. The team should choose based on a consumer question and available prepared runtime. Honest limits are part of the product: nominal native-unit money, active population, supplied baseline, unobserved warehouse/orchestration boundaries and unpiloted timing. A classroom artifact and reviewed source are valuable without implying production promotion or publication.

#### Challenge


Prepare a short team demonstration of the fixed core with a consumer contract, report grain/dependency map, independently checked values and a single deliberate-defect/repair narrative. Show one portfolio fee calculation, the explicit tie example and a traced regional contribution. Identify your authored files and the supplied foundation baseline, and present a bounded reviewable diff.

Document the active population and nominal-money limitation, current artifact/source hashes and actual runtime observations. Choose any optional extension only after the core completion standard passes, listing its consumer purpose, prerequisite models, additional estimate and expected independent evidence. Keep hosted monitoring, deployment and infrastructure work outside required classroom completion. Leave live warehouse, prepared orchestration, novice timing and human presentation checks pending unless they actually ran. Compare end-of-phase reasoning after your attempt and record instructor-reference exposure honestly.

#### Hint


<details>
<summary>Present a finite product story before selecting extensions</summary>

Use the dependency map to organize the story: a portfolio output, an advisor aggregate, a regional rollup and the assertion that rejected a lost contribution. Keep one explicit example per semantic rule instead of showing every row. Select optional depth because it answers a useful question, not because another table makes the project look advanced. A clear pending list is more useful than a generic production-ready label.

</details>

#### Check


Inspect the presentation and evidence against the completed core: 1,028 performance keys, independently participating advisors with correct dense ranks, and every represented region with reconciled counts/values. The zero-denominator and tie examples must match their declared semantics. Retain the actual failed/repaired regional assertion and explain the cause rather than presenting only final green output.

Check that each report's grain, population, units and dependency are stated, that supplied baseline work is disclosed, and that optional extensions have separate prerequisites/time/evidence. Review the actual warehouse output and consumer explanation together. Keep no-activity population and native-currency limitations visible. The demonstration should show the completed reports and the evidence supporting each claim.

```bash
dbt build --project-dir . --profiles-dir . --target local
python runtime/lab.py check . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p2-05-reasoning)


## Phase completion


Finish the finite advanced core: portfolio performance report, advisor leaderboard, regional rollup and independent reconciliation, plus a consumer explanation of one deliberate defect and repaired result. Keep the three authored output grains explicit and prove all retained identifiers and money/fee values against the copied-input oracle. Demonstrate tie semantics and zero-denominator behavior with bounded examples instead of relying on whether the supplied fixture happens to contain a tie or zero case.

Your presentation shows the consumer question, source→domain→consumer lineage, nominal-money limitation, independent population/value checks, failed and repaired regional assertion and a bounded authored diff. List optional extensions separately with their prerequisites and estimates; completing every legacy exercise is not the core standard. The advanced starter supplies the completed baseline deliberately, so disclose it rather than presenting all baseline SQL as newly authored work. Actual Databricks output, orchestration and human timing/presentation review remain separate pending gates unless observed. No production deployment, external publication or infrastructure provisioning is required to demonstrate this fixed reporting core.

---


## Optional stretch


The core completion standard is independent of optional work. Choose a separately timed route from [the stretch guide](stretch/README.md).

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Build a meaningful performance report

<a id="capstone-p2-01-reasoning"></a>

<details>
<summary>Reasoning for capstone-p2-01: Weighted rate and investment performance are different measures</summary>

Bought/sold values need portfolio-level aggregation before joining summary. Realized fee basis points divide total fees by total traded volume and scale by ten thousand; an average raw rate would answer another question. The zero case is explicitly null-safe. Net flow and nominal current AUM have different meanings, and the fixture does not establish flow-adjusted return or FX-normalized valuation. Independent per-portfolio values protect these distinctions.

[Return to capstone-p2-01](#capstone-p2-01)

</details>

### Reasoning: Rank advisor books with explicit ties

<a id="capstone-p2-02-reasoning"></a>

<details>
<summary>Reasoning for capstone-p2-02: Tie meaning is part of the consumer contract</summary>

Dense rank groups equal book values and advances by distinct values, while stable display ordering may add an advisor-ID tie-break. The leaderboard retains participating advisor keys, region and independently reconciled totals. Names are descriptive attributes. The explicit tie example tests the rule even if the supplied fixture lacks ties. Its book comparison remains a nominal teaching aggregate, not FX-normalized investment advice.

[Return to capstone-p2-02](#capstone-p2-02)

</details>

### Reasoning: Build the regional rollup from its declared dependency

<a id="capstone-p2-03-reasoning"></a>

<details>
<summary>Reasoning for capstone-p2-03: The regional dependency and aggregation grain stay explicit</summary>

The report aggregates the leaderboard's advisor-grain rows, retaining region membership and measure meanings. The performance report is another consumer view, not a hidden prerequisite. Independent source-derived region membership protects against a shared upstream mapping error. Advisor count, portfolio count and monetary totals are separate obligations, and the resulting native-unit sums retain their teaching limitation.

[Return to capstone-p2-03](#capstone-p2-03)

</details>

### Reasoning: Reconcile independently and reject a defect

<a id="capstone-p2-04-reasoning"></a>

<details>
<summary>Reasoning for capstone-p2-04: A useful negative case fails on the predicted business difference</summary>

The omission drill removes a known nonempty advisor contribution while leaving raw baseline inputs intact. A meaningful reconciliation detects the affected region's membership/count/value difference independently. Restoring the predicate repairs that cause. Shared filtered outputs or looser tolerance could conceal the loss, and an unrelated nonzero command would not establish the drill. Retain baseline, failure and repaired evidence as separate observed states.

[Return to capstone-p2-04](#capstone-p2-04)

</details>

### Reasoning: Present a fixed completed core and select stretch

<a id="capstone-p2-05-reasoning"></a>

<details>
<summary>Reasoning for capstone-p2-05: Completeness means the declared core, not every optional extension</summary>

The advanced core connects three explicit report grains with independent population/value evidence and a meaningful regional omission repair. Tie and zero cases demonstrate semantics even when absent from the main fixture. The team discloses supplied baseline and nominal-money limits, then selects optional depth with separate prerequisites and timing. A local authored candidate does not establish connected orchestration or human presentation acceptance, and it does not imply production publication.

[Return to capstone-p2-05](#capstone-p2-05)

</details>
