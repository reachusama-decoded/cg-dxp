# dbt: Phase 2 — advanced practice

## Purpose and outcome

Develop the foundation pipeline into a reviewable data-product change. The core begins with dated-join diagnosis and repair, then adds a business reconciliation, controlled incremental replay and an explained feature/history handoff. The starter supplies the supporting models, so a completed foundation attempt is not required.

## Dataset and pipeline

The advanced starter uses the same six raw and two supplementary Portfolio Analytics CSVs as the foundation phase. Staging and supporting models are supplied; enrichment, its coverage/reconciliation tests, the reusable value macro, replay model, fund snapshot and final report contain declared unfinished outcomes. The two May business dates provide a concrete date-join risk. Joining a holding to a price by instrument alone can match both price dates, increasing the population while appearing to add useful price information. Missing dated FX creates a different risk: values become unmatched instead of duplicated.

The source valuation remains authoritative native market value. GBP conversion uses the corresponding dated currency rate; the teaching NAV denominator stays one hundred million synthetic units and excludes cash. A controlled correction is a copied input change, not evidence that the supplied fixture already contained historical corrections. A controlled fund-name change similarly creates snapshot history for the exercise rather than claiming history already exists.

## Prerequisites and workspace

Start in the training project root with the delivered Databricks environment, approved catalog/schema and an owned prefix different from another active attempt. Use the explicit advanced prepare task, then run direct dbt commands from the copied directory. The helper copies supporting files and runtime checks alongside your attempt; no authoring-repository path is needed once prepared. Record the actual adapter version and inspect the profile's local/dev/airflow Databricks targets before choosing one.

```bash
mise run challenge:v2:prepare dbt phase-two-proficient
cd .local/challenges-v2/dbt/phase-two-proficient
export DC_RELATION_PREFIX=dc_alex_dbt02
dbt debug --project-dir . --profiles-dir . --target local
```

Changing an approved schema variable does not grant permission to create a new schema. All seeds, models and snapshots use the declared relation prefix in the single provisioned namespace. Keep credentials out of evidence and perform sign-in outside any recording. If the warehouse is unavailable, author and inspect locally while leaving merge/history execution pending.

## Starter behavior

The supplied staging layer is a prepared successful entry fixture, not your assessed work. Advanced focus models and tests are intentionally unfinished and completion verification rejects them. Seeding is possible before downstream authoring; a broad build can fail on the named unfinished nodes. Diagnose the first failure rather than selecting every dependent model while editing only one. Inspect the checkpoint inventory to distinguish the new task gaps from a wrong source or profile. Negative drills must change only copied data and name their intended failed assertion. Restore source inputs after each drill before using the baseline NAV reconciliation again.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 90–120 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [dbt-p2-01: Diagnose a join fan-out before repair](#dbt-p2-01) | 18–24 | Eight input keys; date-free price join yields sixteen matches; dated repair retains eight |
| [dbt-p2-02: Repair enrichment at the intended grain](#dbt-p2-02) | 18–24 | Eight enriched keys; explicit matched-price/FX coverage and decimal GBP value |
| [dbt-p2-03: Write reconciliation that detects the negative case](#dbt-p2-03) | 18–24 | Coverage and NAV tests fail on copied missing-FX input and pass after restoration |
| [dbt-p2-04: Prove incremental update and replay behavior](#dbt-p2-04) | 18–24 | Older-date correction retains eight keys; a new holding inserts a ninth; replay remains stable |
| [dbt-p2-05: Explain dependency impact and hand over](#dbt-p2-05) | 18–24 | Declared fund report, meaningful snapshot intervals, lineage and explicit Astro boundary |

## Core challenges


<a id="dbt-p2-01"></a>

### dbt-p2-01: Diagnose a join fan-out before repair


<a id="dbt-p2-01-concept"></a>

#### Concept


A join's correctness depends on the relationship between its keys and the grain of each input, not on whether SQL executes. Holdings are at fund/date/instrument grain; prices are at instrument/date grain. An instrument-only price join can attach both May prices to every holding and duplicate the holding's native value. The resulting consumer sum may look plausible because it contains familiar columns and positive amounts, but it measures a fan-out rather than the intended position population.

Count the holding keys before enrichment and the matching price rows per key afterward. With this supplied fixture the date-free price join yields sixteen matches from eight holdings; including the position/price date restores one dated price per holding. An unmatched price or FX observation has a different symptom: a left join retains the holding with null enrichment, while an inner join can hide it by dropping the row. A correct pipeline must detect both duplication and loss. The appropriate diagnosis names which input relationship violated its key contract before choosing a repair. Merely adding distinct to the final report can hide multiplicity without selecting the right dated observation.

#### Challenge


Use the prepared staging inputs to reproduce a bounded date-free price join in a diagnostic query. Count input holdings, joined rows and the maximum matches per holding key. Inspect a representative instrument on both May dates and explain why the incomplete predicate duplicates its value. Keep this deliberately defective diagnostic separate from the consumer model and never treat it as the final answer.

Write the intended enrichment contract in your evidence note: holding grain remains unchanged, price matches by instrument/date, FX matches by native currency/reporting currency/date, and missing matches must be testable. Inspect the unfinished enrichment file and identify the selected source columns and required output fields before repairing it in the next task. Record the original diagnostic result and one key's two candidate prices. If a dependency is not yet built, build only its supplied upstream staging slice instead of copying an instructor enrichment model.

#### Hint


<details>
<summary>Expose the duplicate match before changing the mart</summary>

Start with the smallest join that can demonstrate the defect: holdings plus prices, without FX or aggregation. Compare one holding's date with both price dates. Group the diagnostic by the complete holding key and inspect the match count. A grand total is a later symptom; the duplicated key is the direct cause. Do not repair the join by selecting a latest price when the contract requires the same business date.

</details>

#### Check


Run the prepared upstream staging build, then inspect the defective and corrected diagnostic queries in the warehouse. Expect eight holding keys, sixteen rows from the instrument-only price join, and eight from the dated join. Confirm the discrepancy is actually explained by matching both fixture dates rather than by a duplicate raw key. Retain the query text, execution identity and a representative matching pair.

Explain why distinct over a selected projection might conceal this defect and why dropping unmatched rows would create another one. The negative diagnostic is successful teaching evidence only when it produces the predicted multiplicity. An authentication error or unfinished-model compile failure does not prove fan-out. Restore the intended predicate before any final consumer build, and use the later grain/coverage checks to enforce it. If the warehouse cannot run, retain the inspected fixture keys and diagnostic SQL with execution explicitly pending; a local prediction is not observed warehouse evidence.

```bash
dbt build --select stg_holdings stg_prices stg_fx_rates stg_funds --project-dir . --profiles-dir . --target local
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p2-01-reasoning)


---


<a id="dbt-p2-02"></a>

### dbt-p2-02: Repair enrichment at the intended grain


<a id="dbt-p2-02-concept"></a>

#### Concept


An intermediate model isolates business relationships that would otherwise be repeated in every consumer query. Its output contract is more important than its position in a folder: here it retains each typed holding and attaches a dated price, dated GBP conversion rate and converted value. Left joins make missing observations visible to a coverage assertion. They do not excuse incomplete data; they preserve evidence needed to reject it.

A reusable expression is valuable when it states an actual shared rule, such as converting a decimal native valuation by an explicitly matched rate with an agreed output precision. That macro should compile into understandable SQL and should not decide the join keys or manufacture a default rate. For example, a missing May 20 GBP rate must remain null and fail coverage even though GBP-to-GBP is normally one. The feed's declared observation is part of the readiness contract. Fund master may describe a USD base currency while this report remains explicitly GBP. Moving environment routing or relationship selection into an opaque macro would make the model harder to review and would not add useful abstraction.

The supplied `int_fund_attributes` and `int_positions_dated` retain v1's two smaller intermediate contracts. The first filters active funds and exposes their reporting attributes; the second adds cash balance and accrued interest once at fund/date/currency grain. All four raw fund-master entries are active here, and the positions helper retains eight dated rows. These are supplied supporting models to inspect rather than additional unfinished SQL assignments. Cash remains outside the declared teaching NAV, so an available cash field does not authorize silently adding it to that report.

#### Challenge

Retain the seven staging fields and append `close_price`, `fx_rate_to_base` and `mv_base_ccy`. Prices provide `instrument_id`, `price_date` and `close_price`; FX provides `from_ccy`, `to_ccy`, `rate_date` and `fx_rate`. Match the holding instrument/date to prices and its local currency/GBP/date to FX. Use `native_value` for the decimal GBP amount and retain the same holding key.


Complete the enrichment model with the declared dated price and FX predicates, preserving the holding fields and appending the expected enrichment columns. Implement the native-value macro with explicit decimal conversion and use it for a meaningful repeated expression. Keep input relationship logic visible in model SQL so a reviewer can see instrument/date and currency/date matching without tracing several macro layers.

Build enrichment as a view and inspect its row/key population before building the consumer report. Document the distinction between the supplied close price, native valuation and converted GBP amount. Show the rendered macro expression in compiled SQL and verify that the resolved source/model references still use your owned namespace. If you choose a different helper signature, preserve the same units and precision and explain that bounded change. Do not replace missing FX with a rate of one or derive native market value from quantity times price.

Build and inspect the two supplied intermediate helpers as well. `int_fund_attributes` exposes `fund_id`, `fund_name`, `inception_date`, `base_ccy` and `strategy_code` for active funds. `int_positions_dated` exposes `fund_id`, `position_date`, `local_ccy` and `cash_plus_accrued`. Trace their refs and explain why filtering or unit arithmetic belongs in one named model rather than being repeated independently by each consumer. Use cautious indirect test selection while downstream focus models are unfinished.

#### Hint


<details>
<summary>Keep joins visible and reuse only the value rule</summary>

Write the two join predicates separately and check each candidate key against the input grain. Add the conversion expression only after the joined fields make sense. Compile the macro in a selected model and read the emitted SQL as ordinary arithmetic; useful reuse should make the rule easier to inspect. Keep null coverage distinct from numeric reconciliation so a missing match cannot disappear inside an aggregate sum.

</details>

#### Check


The enriched view must retain eight holding keys with exactly one dated price and FX observation per key and decimal GBP values consistent with the independent calculation. Inspect selected rows and the actual relation metadata. The compiled macro expression should use the supplied native value and matched rate without hidden environment names or fallback currency assumptions.

Check four active helper fund rows and eight cash/accrued rows. Compare one helper amount directly with its copied source's cash balance plus accrued interest, and explain why it is excluded from the current NAV. Distinguish a legitimate supporting-model build from a relationships test that prematurely selects an unfinished downstream consumer.

```bash
dbt build --select int_fund_attributes int_positions_dated --indirect-selection=cautious --project-dir . --profiles-dir . --target local
dbt show --select int_positions_dated --limit 8 --project-dir . --profiles-dir . --target local
```

Temporarily remove the copied May 20 GBP FX observation, reseed that input and rebuild enrichment. The population can remain eight while matched coverage fails for the affected observations; do not interpret retained row count as a complete conversion. Restore the copied input and rebuild before comparing baseline values. Explain why the relationship predicates remain in the model, why a left join plus an explicit failure check is useful, and why reporting currency is not inferred from the fund master. Retain the compiled expression, missing-match result and repaired enrichment output as separate pieces of evidence.

```bash
dbt build --select int_holdings_enriched --project-dir . --profiles-dir . --target local
python runtime/lab.py mutate . --drill missing-fx
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p2-02-reasoning)


---


<a id="dbt-p2-03"></a>

### dbt-p2-03: Write reconciliation that detects the negative case


<a id="dbt-p2-03-concept"></a>

#### Concept


A business reconciliation compares a consumer result with an independently specified meaning. It should detect wrong units, key loss, joined duplication and changed values rather than simply compare two sums built from the same faulty model. The supplied custodian NAV fixture and Decimal CSV reference give concrete expected results for the unmodified teaching population. Key membership is as important as numeric closeness: a report missing one date should fail even when another row absorbs its value.

A negative case tests the assertion's sensitivity. Removing a copied FX observation should fail enrichment coverage; feeding that incomplete result into a holdings-only NAV report should not produce accepted output. Another controlled experiment intentionally changes a holding's value. That makes baseline NAV comparison fail for a legitimate reason until the variation's expected output is used. These cases require different interpretations. A test message without the input variant and failed node cannot tell a reviewer whether it detected a real defect, an intended correction or an unrelated connection issue. Keep the assertion's unit, tolerance, key set and applicable fixture state explicit.

#### Challenge


Author the matched-enrichment and NAV reconciliation SQL tests in the copied project. Preserve the complete holding and report key sets, test non-null matched price/rate fields, and compare the report against the declared baseline expected NAV with an appropriate decimal tolerance. Add descriptions explaining the reporting currency, synthetic unit denominator and cash exclusion. Use structural schema tests as complementary checks rather than replacing the business assertion.

Predict which node will fail when the copied May 20 GBP FX row is removed. Execute that mutation, selected reseed and build/test sequence in your owned attempt, then retain the failed node and diagnostic rows. Restore the source copy, reseed and rerun the same graph. Record the repaired comparison and a brief explanation of why a baseline oracle is inappropriate for the later deliberate value correction. Do not change the expected fixture merely to make a defective model agree with itself.

#### Hint


<details>
<summary>Compare membership before tolerating numeric differences</summary>

Compare keys before values and state the tolerance in money or NAV units. A left join from expected keys to actual results can expose missing report rows, while the reverse membership check exposes invented ones. Inspect the first failed assertion and its compiled SQL. If it only compares a grand sum, ask whether two offsetting errors or shared row loss could still pass. Strengthen the contract rather than adding a looser threshold.

</details>

#### Check


Run both authored assertions on an unmodified complete project and compare the report to the independent CSV reference. All eight report keys and their GBP/NAV values must agree. After the missing-FX mutation, the expected coverage assertion must fail because the declared rate is absent; an unrelated unfinished macro or profile failure is not the intended result. Restore and reseed before the final passing run.

Retain the original and mutated source hashes, failed node, observed failed rows, repair diff and final run-results identity. Explain how the test detects a missing date and how its tolerance handles decimal representation without accepting a wrong monetary result. Record that the subsequent corrected-value variant changes the independent oracle rather than the definition of the baseline input. A verifier can inspect values and artifacts, but your explanation must connect the failing contract to the controlled cause. Keep actual warehouse execution pending if only the assertion text and fixture arithmetic have been prepared.

```bash
dbt test --select matched_enrichment nav_reconciliation --project-dir . --profiles-dir . --target local
python runtime/lab.py restore .
python runtime/lab.py reference .
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p2-03-reasoning)


---


<a id="dbt-p2-04"></a>

### dbt-p2-04: Prove incremental update and replay behavior


<a id="dbt-p2-04-concept"></a>

#### Concept


Incremental materialization changes how a relation is maintained; it does not automatically make a pipeline correct under late data. A merge needs a stable unique key that identifies the business observation being replaced. For holdings that key includes fund, date and instrument. Choosing only a fund would overwrite another date, while appending without key matching would duplicate an existing observation when the same input is replayed.

This exercise creates a correction to the first copied May holding by increasing its native market value by one thousand. The selected observation is GBP-denominated, so its independently expected GBP value changes by the same amount. The date remains the older fixture date. A filter that processes only dates greater than the current maximum would miss this legitimate correction. Replaying the corrected input twice should produce the same eight-key state after both merges, with one changed value and no duplicate. A second controlled input appends a new holding key: PEF-EM-GROWTH, May 20, GB00B3M9JJ78, with native and GBP value 500. Its price and FX already exist, so the result must grow to nine keys with total exposure another 500 higher. Replaying that combined input must retain nine, proving insertion as well as update. The experiment is bounded to your namespace and copied fixture; it does not prove a general production late-arrival policy, transaction isolation or concurrent writer behavior. Those limitations belong in the handoff.

#### Challenge

The replay relation must expose `fund_id`, `position_date`, `instrument_id` and `exposure_gbp`, with the first three fields forming its unique key. Compute exposure from the matched native value/rate at decimal(28,2) precision; the independently queried checker uses these exact output names.


Implement the holdings replay model with Databricks incremental merge behavior and the composite holding key. Select enough of the current copied input to include an older-date correction rather than blindly filtering above the maximum stored date. Build an initial owned relation and retain its sorted key/value projection. Apply the controlled correction helper to the copied seed, reseed the changed input and run the replay model twice.

After the correction check, apply the new-holding helper to append the specified unseen key. Reseed and run the replay model twice again. Compare both nine-key states with the independently calculated input, including the retained older-date correction.

After each merge, compare the warehouse relation with the independent corrected input calculation. Record the exact changed key, original and corrected amount, unchanged date and overall row count. Keep the consumer baseline NAV comparison separate: its unmodified custodian fixture intentionally no longer agrees with the corrected holdings. Restore the raw copy after collecting the variation evidence, and state whether the owned replay relation has been rebuilt to baseline. Never reset another learner's prefix or call an empty-table first build proof of incremental replay.

#### Hint


<details>
<summary>Prove the older observation participates in both merges</summary>

First show that the selected business date is older than the maximum date already stored. Then inspect the unique-key configuration and the compiled merge predicate. Build from the full tiny copied input for this teaching experiment so a date watermark cannot hide the correction. The decisive check is the second corrected run: identical corrected input should retain eight keys; after the explicit arrival, identical combined input should retain nine. It must not add a tenth row or alter an unrelated key. Keep value-change evidence alongside membership evidence.

</details>

#### Check


Expect eight unique holding keys before the drill, after the corrected merge and after the second replay. Exactly one older-date GBP value should increase by one thousand; all other keys and values remain unchanged. After the new-holding drill, expect nine unique keys and exactly 500 additional GBP exposure; the second replay must retain the same nine-key/value projection. Query actual Databricks output and use the runtime replay checker, which calculates expected values from the copied holdings and FX inputs. A parse or local SQL emulation cannot prove Delta merge execution.

Retain the first and both corrected run-results identities, key/value projections, copied input hashes and the independently identified changed key. Explain why a maximum-date-only filter would reject a valid correction and why replay should not duplicate it. The ordinary baseline NAV assertion is expected to disagree while this variation is active; do not disable it permanently or change the baseline fixture to conceal that distinction. Restore source inputs and disclose the final relation state in your handoff. If connected execution cannot occur here, the implementation and expected transition can be reviewed locally but this check stays pending.

```bash
python runtime/lab.py mutate . --drill correction
dbt seed --select holdings_raw --project-dir . --profiles-dir . --target local
dbt run --select holdings_replay --project-dir . --profiles-dir . --target local
python runtime/lab.py check-replay .
# Repeat the run/check above, then prove insertion and replay.
python runtime/lab.py mutate . --drill new-holding
dbt seed --select holdings_raw --project-dir . --profiles-dir . --target local
dbt run --select holdings_replay --project-dir . --profiles-dir . --target local
python runtime/lab.py check-replay .
# Repeat the run/check above once more. Restore the copied input and owned table.
python runtime/lab.py restore .
dbt seed --select holdings_raw --project-dir . --profiles-dir . --target local
dbt run --select holdings_replay --full-refresh --project-dir . --profiles-dir . --target local
python runtime/lab.py check-replay .
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p2-04-reasoning)


---


<a id="dbt-p2-05"></a>

### dbt-p2-05: Explain dependency impact and hand over


<a id="dbt-p2-05-concept"></a>

#### Concept


An end-to-end feature needs a consumer question, output grain, units, lineage and evidence that someone can review. Generating another SQL file is insufficient if its result cannot be interpreted. A small fund-level report can answer how the two supplied dates differ in holdings exposure; it must label that observation difference without pretending it is investment return. The fixture lacks the flows and complete unit history needed to establish that stronger measure.

Attribute history is a separate feature. A snapshot can retain successive fund-name versions using a stable fund key and validity intervals. A copied fund-master name change creates the exercise's second observed version; it is not a correction to the holding value and does not change the reporting date. One current interval and one closed interval for the changed key demonstrate the intended history. Documentation connects these decisions to the next consumer and to Astro's worker boundary: the terminal's successful build does not prove worker executable paths, mounted files or task-time credentials. A useful handoff states what was actually executed and what still needs connected or human review.

#### Challenge

Use raw `fund_cd` as the snapshot key and track `fund_name`, `base_ccy`, `strategy_code` and `is_active`. Inspect the generated `dbt_valid_from` and `dbt_valid_to` columns for the changed key; the active version has an open validity end under the supplied snapshot configuration. The final report retains the five fund/date fields stated in foundation task dbt-p1-04.


Complete the report model and its documentation, keeping a useful bounded feature based on available fund/date inputs. State the consumer question and distinguish exposure difference from financial performance. Add descriptions and tests for the report key, GBP values and teaching NAV limitation. Inspect lineage showing sources, staging, enrichment and the new consumer output.

Implement the fund snapshot in the approved namespace with fund identifier as its unique key and the declared changing attributes. Run an initial snapshot, mutate only the copied fund name, reseed and snapshot again. Query current and closed validity intervals for that key, then restore the copied baseline input while preserving captured history evidence. Assemble a reviewable diff and a short Astro handoff listing the project/profile paths, selected target, owned prefix, required worker executable and pending task-time authentication checks. Full runnable instructor references are comparison material after your attempt, not a substitute for your authored feature.

#### Hint


<details>
<summary>Separate reporting meaning, attribute history and worker readiness</summary>

Choose a report whose inputs really support its claim. For history, inspect the snapshot key and check-column list before changing a copied fund name; changing a nontracked field should not create the expected new version. Query the changed key rather than assuming a larger snapshot row count proves valid intervals. Keep the source restoration and historical table state distinct so the handoff explains both.

</details>

#### Check


The final baseline report must reproduce all eight independently specified fund/date values and show understandable lineage and documentation. Your additional feature needs an independent calculation for its own declared output. The snapshot experiment must show a closed previous interval and one current interval for the changed fund, with unchanged fund identity. Query the actual owned snapshot relation; compilation cannot establish validity history.

Retain the report/test run-results identities, feature expectation, snapshot before/after projections and bounded diff. Explain the meanings of reporting date, ingestion time and snapshot validity time. Include actual terminal adapter/target details and mark worker mounts, task-time token delivery, managed versions and scheduled run evidence pending unless observed. Restore the copied source data and describe whether the snapshot intentionally retains the teaching variation. Query the Delta and snapshot results in Databricks; include worker connection requirements in the Astro handoff.

```bash
dbt snapshot --project-dir . --profiles-dir . --target local
python runtime/lab.py mutate . --drill fund-change
dbt seed --select fund_master_raw --project-dir . --profiles-dir . --target local
dbt snapshot --project-dir . --profiles-dir . --target local
dbt docs generate --project-dir . --profiles-dir . --target local
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p2-05-reasoning)


## Phase completion


Finish the advanced core with an enrichment that retains every declared holding key, business checks that reject missing matches, a useful reusable decimal expression, and a consumer report whose baseline values agree with the independent CSV calculation. Demonstrate a controlled correction to an older business date, replay it twice through the incremental model, and show that the corrected key appears once. Append the specified new holding and prove nine keys after both insertion and replay, then rebuild the owned replay table to the eight-key baseline after restoring copied inputs. Demonstrate a separate fund-name change through snapshot validity. Keep those experiments distinct: replay updates an observation, while a snapshot retains changing attribute versions.

Your handoff contains the authored files, a bounded diff, failed and repaired assertions, manifests/run results, independent key/value comparisons, and a short explanation of each supplied model. Include a small fund-level reporting feature whose population and units are explicit. Do not manufacture an investment-return measure from two valuation dates without the necessary flow inputs. Preserve baseline fixture bytes and document restoration after variations. Source preparation, parsed SQL and locally calculated expected values remain supporting evidence until the Databricks build, Delta merge and snapshot queries execute. The Astro handoff lists the worker paths and connection checks needed for the Airflow route.

---


## Optional stretch


The core completion standard is independent of optional work. Choose a separately timed route from [the stretch guide](stretch/README.md).

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Diagnose a join fan-out before repair

<a id="dbt-p2-01-reasoning"></a>

<details>
<summary>Reasoning for dbt-p2-01: Multiplicity reveals an incomplete join key</summary>

Both May price observations share an instrument identifier. The date-free join therefore doubles matching holdings even though raw keys are valid. Matching the business date repairs that particular predicate. A missing match remains a separate coverage concern and should not be solved by dropping the holding. The diagnostic evidence must show input keys, actual multiplicity and the corrected relation, so the reviewer can understand the cause without trusting a final aggregate.

[Return to dbt-p2-01](#dbt-p2-01)

</details>

### Reasoning: Repair enrichment at the intended grain

<a id="dbt-p2-02-reasoning"></a>

<details>
<summary>Reasoning for dbt-p2-02: Explicit coverage and readable SQL make reuse trustworthy</summary>

The intermediate output should have the same holding grain as staging. Its left joins preserve unmatched observations for diagnosis, and the coverage test rejects them before a consumer result can be accepted. The decimal macro expresses a valuation rule rather than a relationship rule. A rate-of-one fallback would hide a missing declared feed observation; inferring currency from fund master would change the report contract. Both mistakes can yield plausible numbers, so inspect compiled arithmetic and matched keys together.

[Return to dbt-p2-02](#dbt-p2-02)

</details>

### Reasoning: Write reconciliation that detects the negative case

<a id="dbt-p2-03-reasoning"></a>

<details>
<summary>Reasoning for dbt-p2-03: An independent expected population catches shared model errors</summary>

The useful reconciliation owns its expected keys and units independently of the enrichment. Missing FX should be rejected as coverage loss; restoration repairs that input cause. The correction exercise later changes an input value deliberately, so its expected result is recalculated from the copied input rather than accepted against a stale baseline NAV. A test that merely matches the mart to another aggregate of the same broken model would miss shared loss or duplication. Record the variant and failed assertion together.

[Return to dbt-p2-03](#dbt-p2-03)

</details>

### Reasoning: Prove incremental update and replay behavior

<a id="dbt-p2-04-reasoning"></a>

<details>
<summary>Reasoning for dbt-p2-04: Replay correctness is a state transition, not a green command</summary>

The merge key identifies the exact dated holding. A copied older-date correction must reach that key even after the later date exists, and running the same correction again must leave the eight-key result unchanged. A new PEF-EM-GROWTH/instrument key then grows the relation to nine, adding 500 GBP without losing the correction; its replay stays at nine. Restoring seed inputs alone cannot delete that inserted target key, so the final owned full-refresh is an explicit restoration step. The independent replay checker uses the modified input, while the custodian NAV fixture still describes baseline data. Delta behavior requires actual warehouse execution and cannot be inferred from compiled SQL. A good report retains before/after state and discloses whether restoration also rebuilt the owned relation.

[Return to dbt-p2-04](#dbt-p2-04)

</details>

### Reasoning: Explain dependency impact and hand over

<a id="dbt-p2-05-reasoning"></a>

<details>
<summary>Reasoning for dbt-p2-05: A useful handoff states meaning and observed boundaries</summary>

The feature should answer a supported question with a declared key and units. Two exposure observations do not automatically establish return. Snapshot history records a separate changing-attribute contract and needs actual validity queries after a controlled name change. Restoring raw inputs does not erase captured history. Lineage, tests and a reviewable diff explain the terminal result, while the Astro handoff identifies worker paths and authentication that remain unverified until scheduled execution. These distinctions make the product interpretable rather than merely executable.

[Return to dbt-p2-05](#dbt-p2-05)

</details>
