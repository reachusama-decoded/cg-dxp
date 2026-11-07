# dbt: Phase 1 — foundations

## Purpose and outcome

Build a small but complete Portfolio Analytics result on Databricks: supplied custodian inputs become typed holdings, dated enrichment and a fund/date consumer report. You write the holdings transformation and report. Other staging and enrichment models are supplied; inspect their dependencies to understand the complete pipeline.

## Dataset and pipeline

Eight supplied CSVs enter the project: six raw feeds plus fund and custodian-NAV reference fixtures. Holdings, positions and prices each contain eight rows; FX has six rates, fund master four funds and instrument reference four instruments. Holdings cover four funds on 20 and 21 May 2026. The modeled graph reads holdings, positions, prices, FX and funds. Instrument reference remains available for source inspection. Custodian raw cash is not included in the teaching NAV numerator. The report converts supplied native market value to GBP and divides the holdings-only amount by a synthetic one-hundred-million-unit denominator. It is not an official unit-price calculation.

## Prerequisites and workspace

Use the supplied training dev container, delivered OAuth setup and a dbt executable with the Databricks adapter. From the training project root prepare a fresh attempt with the version-explicit mise task. Record installed versions instead of assuming a pinned file proves the worker environment. Set the approved catalog/schema aliases consistently and choose an owned relation prefix before loading. Never create an extra schema as an experiment. Your terminal runs dbt; the warehouse executes its SQL. The local target name still selects Databricks, not DuckDB.

```bash
mise run setup:databricks
mise run challenge:v2:prepare dbt phase-one-certified
cd .local/challenges-v2/dbt/phase-one-certified
export DC_RELATION_PREFIX=dc_alex_dbt01
dbt --version
dbt debug --project-dir . --profiles-dir . --target local
```

Use a new workspace and prefix for a second simultaneous attempt. Work inside the copy, editing only the task's named files. Keep evidence beside the copied project. Do not place tokens in that note, commit local credentials or overwrite the canonical starter. The root mise verification command accepts the absolute or root-relative attempt path; direct dbt commands below run from this prepared directory.

## Starter behavior

The foundation starter deliberately contains unfinished holdings staging and report SQL. They are valid files for authoring, but the completion checker rejects their placeholder result. Source declarations, routing macros, remaining staging models and enrichment are supplied. Inspect that boundary before running a broad build: downstream failures from an unfinished model are expected until its task is complete. Seed loading can succeed first; it is not an assessment pass. Freshness uses extraction timestamps separately from the historical business dates. If current freshness fails, record that cause and use the documented timestamp-only preparation rather than changing the May holdings dates.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 75–110 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [dbt-p1-01: Inspect the project and source grain](#dbt-p1-01) | 15–22 | Eight holdings, four funds, two business dates; safe identity and seed inventory |
| [dbt-p1-02: Declare and use sources](#dbt-p1-02) | 15–22 | Compiled source relations and manifest dependencies agree with all raw seeds |
| [dbt-p1-03: Normalize type, unit and key contracts](#dbt-p1-03) | 15–22 | Eight unique holding keys; native decimal values preserved |
| [dbt-p1-04: Build a useful mart through ref](#dbt-p1-04) | 15–22 | Eight fund/date rows; independently derived GBP exposure and teaching NAV |
| [dbt-p1-05: Add minimum key and relationship proof](#dbt-p1-05) | 15–22 | Declared tests pass; unknown-fund membership fails, then passes after input restoration |

## Core challenges


<a id="dbt-p1-01"></a>

### dbt-p1-01: Inspect the project and source grain


<a id="dbt-p1-01-concept"></a>

#### Concept


A dbt project describes transformations and dependencies; it does not become a separate database simply because it lives in a container. The adapter compiles and submits SQL to Databricks, where the approved catalog, schema and warehouse determine the relations you read and write. Seeds load copied training inputs. Sources describe that input boundary, while models describe derived relations. Keeping those roles separate helps diagnose a missing table before changing a transformation.

In this fixture a holding is identified by fund, business date and instrument. The same fund appears on two dates, so fund alone cannot identify a row. A report with four rows after both dates are loaded has probably collapsed the date dimension. Inspecting the eight raw rows makes that mistake visible before SQL is written. Distinguish the position date from the extraction timestamp: one describes the observation being valued, the other describes ingestion freshness. An old business date can be the correct teaching input even when its original extraction timestamp is stale. Likewise, a successful connection says nothing about whether the six raw feeds have actually been loaded.

#### Challenge


Create an evidence note in the copied project and list each seed's name, row count, key fields and money units. Inspect the project and profile configuration, identifying the adapter, target, approved catalog/schema and relation prefix without copying credential values. Run the version and connection probes, then load all eight seeds. Find the raw holdings, funds, dated prices and FX sources in the declarations and note which physical prefixed tables they resolve to.

Use a small independent CSV inspection to count distinct funds and dates. Choose one holding and trace its native currency and value to the source field that supplies them. Explain why the product's two supplementary CSVs cannot provision the six raw feeds. Keep a record of any unavailable warehouse prerequisite; continue the CSV inspection locally while leaving the connection and actual loaded-relation checks pending. Do not substitute the optional five-row fixture or call its result this phase's completion.

#### Hint


<details>
<summary>Separate input inspection from warehouse readiness</summary>

Start with the headers in the copied seeds and the database/schema expressions in the source YAML. Write the composite holding key as three named fields before counting rows. If connection debug fails, inspect the adapter identity and alias consistency before trying a model build. A namespace mismatch can produce missing relations even when authentication succeeds; a username fallback would conceal that mismatch rather than fix it.

</details>

#### Check


Run the seed command from your attempt and inspect the resulting prefixed input relations. The independent CSV inventory should show eight holdings, four distinct fund identifiers and two business dates. Verify the corresponding warehouse counts when connected; CSV counts alone establish supporting input evidence. The six raw counts are eight holdings, eight positions, eight prices, six FX rates, four fund-master rows and four reference instruments. Supplementary funds and NAV inputs need their own listed counts.

Retain the installed adapter/version, selected target, redacted namespace identity, seed run-results identity and the independently calculated populations. Explain which command loaded inputs and which file only declared their names. If debug reports an authentication or permission error, record that category and leave this check pending rather than treating a local seed inspection as a warehouse pass. Your explanation should predict why removing the position date from a key would merge two otherwise valid observations.

```bash
dbt seed --project-dir . --profiles-dir . --target local --full-refresh
python runtime/lab.py reference .
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p1-01-reasoning)


---


<a id="dbt-p1-02"></a>

### dbt-p1-02: Declare and use sources


<a id="dbt-p1-02-concept"></a>

#### Concept


The source function gives a model a logical dependency on data loaded outside that model. Its first name identifies the source group and its second identifies the table inside that group. Those logical names need not equal the physical warehouse relation: the source identifier can add the owned training prefix while the SQL remains stable. A reference to another model instead declares a derived dependency that dbt can order and document.

Consider the holdings model reading the custodian holdings source. Databricks ultimately executes a fully qualified relation in your approved namespace; the source declaration explains why that relation is an input rather than a generated mart. A raw seed can be present but wrongly mapped to another learner's table. Conversely, a perfectly written declaration can resolve to a table that was never seeded. Compilation and an actual query expose different halves of this boundary. The instrument-reference input is useful to inspect even though the prepared consumer graph does not depend on it. Do not invent a lineage edge merely to make every loaded feed appear in the final report.

#### Challenge


Inspect all six raw table declarations in the copied source YAML and verify their identifiers use your relation prefix. Retain the prepared logical source groups for custodian, Bloomberg, FX and product reference. In the holdings staging file replace the unfinished scaffold with a source-based input CTE, then add the transformation required in the next task. Read the supplied fund, FX, price and position staging files to identify their source calls and the prepared enrichment model to identify its model references.

Compile a selected holdings model and trace one rendered relation back to its source declaration, seed file and approved namespace. Record that chain in the evidence note. Keep the supporting model files supplied unless an actual declared task requires a change. If a raw input is missing, fix loading or source mapping before adding a hard-coded qualified name to model SQL. That shortcut would bypass the lineage and ownership contract being learned.

#### Hint


<details>
<summary>Trace one logical name to its prefixed input table</summary>

Compare the logical table name in the source call with the identifier expression in YAML; they answer different questions. The source manifest node records database, schema and identifier after configuration is resolved. If compilation fails because the holdings scaffold is incomplete, keep the first error and use the supplied source declarations to complete the input CTE. Avoid changing all six source names at once while diagnosing one bad relation.

</details>

#### Check


Compile the holdings selection and inspect its SQL and manifest dependency entry. The rendered raw relation must belong to your approved catalog/schema and carry your owned prefix. The dependency must point to the custodian holdings source, while the later report depends on models through references. Confirm the source inventory contains the six declared raw inputs; instrument reference may have no consumer-model edge without being an error.

When connected, build the holdings model after its type transformation is complete and inspect the warehouse relation. Record the difference between compilation success and query success. To diagnose a deliberate source-mapping mistake in a disposable copy, point one identifier at a nonexistent owned name: the affected model should fail with a missing-relation category. Restore the declaration and rebuild before retaining completion evidence. Explain why loading the seed alone would not repair a wrong identifier and why bypassing the logical source with a literal table name would weaken lineage.

```bash
dbt compile --select stg_holdings --project-dir . --profiles-dir . --target local
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p1-02-reasoning)


---


<a id="dbt-p1-03"></a>

### dbt-p1-03: Normalize type, unit and key contracts


<a id="dbt-p1-03-concept"></a>

#### Concept


Staging gives raw data stable names and types while preserving its declared population. Renaming the custodian fund code and position date makes their purpose clearer, but it does not justify dropping a date, replacing a missing key or changing money units. Money stored as native market value must remain native market value until the dated FX join explicitly converts it. A fund's master base currency is a separate attribute, not permission to relabel a holding value.

For example, a holding observed on 20 May and the same instrument observed on 21 May represent different positions. The composite key preserves both; casting the date into a SQL date type makes later dated joins less ambiguous. Decimal conversion preserves exact cents within the stated precision, whereas an uncontrolled floating-point aggregation can introduce comparison noise. Quantity has its own precision and meaning. The supplied valuation is not necessarily quantity multiplied by the supplementary price, so reconstructing it that way would silently change the teaching contract. Filtering a zero or negative amount also changes population semantics unless the contract explicitly requires that rule.

#### Challenge

The exact staging columns are `fund_id` (string, trimmed uppercase `fund_cd`), `position_date` (date from `pos_dt`), `instrument_id` (string retaining `isin`), `quantity` (decimal(18,4) from `qty`), `mv_local_ccy` (decimal(18,2) from `mkt_val_lc`), `local_ccy` (uppercase string from `ccy_cd`) and `_src_loaded_at` (retained `_extracted_at`). Do not manufacture a missing instrument key; this holdings contract requires it, with cash supplied separately.


Complete the holdings staging SQL in the copied model file. Read through the custodian source, trim and normalize the fund code, cast the position date, retain the instrument identifier, cast quantity and native market value to their stated decimal types, normalize currency, and carry the source extraction timestamp for diagnostics. Keep cleaning separate from enrichment joins. Use the prepared column contract to name the resulting fund, date, instrument, quantity, native value and local-currency fields.

Build the selected staging model as a view, then inspect all eight output rows alongside the original CSV. Check the entire composite key and compare the native value of a chosen holding exactly. Read the supplied grain test and extend it if your transformation introduces an additional normalization assumption. Document any filtering and prove it does not conceal an invalid key in the supplied fixture. Do not erase null-key evidence by substituting a plausible fund identifier or invent a reporting currency during staging.

#### Hint


<details>
<summary>Check the three-field grain before changing population</summary>

Write the column mapping before the SQL so casts and renames can be reviewed independently. Compare the source and staging counts before joining any dimensions. For a duplicate-key failure, group on all three business fields; grouping only by fund will report valid repetitions as defects. Inspect Databricks full type metadata when proving decimal precision, because a broad type label may omit precision and scale.

</details>

#### Check


The staging view must return eight rows with eight unique fund/date/instrument keys and native market values matching the copied holdings input. Inspect the SQL type metadata and verify the intended decimal precision and scale, the date type and normalized currency. A count alone is insufficient: an invented key could preserve eight rows while breaking later joins. Compare a complete sorted key/value projection against the input mapping.

Run the grain test and inspect the selected build artifacts. In a separate copied-input variant set one native market value to zero, rebuild the selected staging slice and prove its business key remains among all eight rows with an exact zero value. Restore and reseed before baseline NAV comparison; changing an amount legitimately changes its expected value. In a disposable input copy, duplicate one holding key and show that the grain assertion detects it; restore the supplied CSV and reseed before the final build. Keep that negative result separate from the untouched starter's unfinished-model rejection. Explain why the same fund appearing on two dates should pass and why recomputing market value from quantity and price is outside this staging task. Retain the failed test identity, repaired selected run and one exact native-value comparison.

```bash
dbt build --select stg_holdings --project-dir . --profiles-dir . --target local
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p1-03-reasoning)


---


<a id="dbt-p1-04"></a>

### dbt-p1-04: Build a useful mart through ref


<a id="dbt-p1-04-concept"></a>

#### Concept


A mart combines modeled inputs into an output a consumer can interpret. Its grain must be declared before aggregation, because an apparently sensible total can conceal loss of dates or duplication from joins. Here the consumer result is one row per fund and position date, containing holding count, GBP exposure and teaching NAV per synthetic unit. The prepared enrichment provides native market value and the matching dated FX rate; the report sums converted holding values at that grain.

For the global-core fund on 20 May, the independent fixture calculation yields GBP exposure of 1,500,440,000 and teaching NAV of 15.004400 after division by one hundred million. The next date is a distinct report row, not an update to that same key. GBP reporting is fixed even when fund master says a fund has another base currency. Cash positions are deliberately excluded from this teaching numerator. Calling the result official custodian NAV would overstate its meaning. A three-column output with a correct grand total can still be wrong for each fund/date, so compare complete keys and values rather than relying on an aggregate smoke check.

#### Challenge

Return `fund_id` and `position_date` as the report key, `holdings` as the count of enriched holding rows, `exposure_gbp` as decimal(28,2), and `nav_per_unit` as decimal(28,6). The supplied enrichment value field is `mv_base_ccy`; sum it at fund/date grain and divide that sum by 100000000 for the teaching NAV. The name of each output is part of the consumer/checker contract.


Author the fund NAV report model through a reference to the supplied enrichment, grouping on fund and position date. Return the declared identifiers, holding count, GBP exposure and teaching NAV with the stated decimal types. Keep the synthetic denominator explicit and explain the cash exclusion in the model documentation. Configure the consumer report as a table while leaving the staging and enrichment layers as views.

Before running SQL, calculate one selected fund/date result from the copied holdings and FX files. Then build the report with its upstream dependencies and compare every output key/value with the independent reference command. Inspect the manifest to show why the report waits for enrichment and holdings. If one row has the right exposure but the wrong date, repair the grain instead of relaxing the reconciliation. Preserve the supplementary custodian NAV fixture as a comparison input and state its intended teaching role.

#### Hint


<details>
<summary>Declare the reporting grain and units before summing</summary>

Begin by selecting the enrichment columns and checking its row count before aggregation. The supplied native value is already a valuation; use the dated conversion rate rather than reconstructing price times quantity. Keep the denominator outside the sum so its units remain obvious. A missing FX rate should remain visible to a coverage test; replacing it with one would manufacture a convincing but unsupported answer.

</details>

#### Check


Build the report selection with its upstream graph, then run the independent reference over the copied CSVs. Expect eight report keys: four funds on each of two dates. Each holding count is one in this fixture. Check all exposures and NAV values, including global core on 20 May at 1,500,440,000 GBP and 15.004400 teaching NAV. The independent output must use your actual copied inputs, not a pasted instructor SQL result.

Inspect warehouse relation metadata to show that the report is a table and holdings staging is a view. Record the selected build/run-results identity and explain the difference between materialization and business grain. A view/table configuration change alone should not change the expected values. If either date disappears or a fund gains two identical report keys, the output fails even when an overall sum is plausible. Explain why excluding cash is a declared limitation and why a different fund-master base currency does not change this report's GBP label.

```bash
dbt build --select +fund_nav_report --project-dir . --profiles-dir . --target local
python runtime/lab.py reference .
python runtime/lab.py check .
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p1-04-reasoning)


---


<a id="dbt-p1-05"></a>

### dbt-p1-05: Add minimum key and relationship proof


<a id="dbt-p1-05-concept"></a>

#### Concept


A test is useful when it protects a stated failure mode and its result can be interpreted. A uniqueness test checks row identity, a not-null test checks required presence, and a relationship test checks membership in another relation. None independently proves all joins preserve the intended population. A relationship assertion can ignore nulls, and a reconciliation can compare two outputs that already lost the same fund. Combining structural checks with independent business values closes different gaps.

The holding grain includes a date, while fund-master membership is checked by fund identifier. A date-free fund uniqueness test would therefore reject valid holdings. Conversely, a report sum could stay numerically unchanged if an unknown fund's zero-valued holding were silently filtered out; the population and relationship assertions should still catch that loss. For missing dated FX, the correct failure is incomplete conversion coverage, not a guessed one-to-one rate. The teaching drill deliberately changes a copied input so you can observe the failed assertion, repair its cause and prove the restored output. A red test is not automatically a successful drill unless it failed for the intended reason.

#### Challenge


Review the supplied schema and singular tests, then add or repair assertions that match the authored models: holding composite grain, required fund/date/instrument fields, fund membership, complete dated enrichment and independent NAV reconciliation. Explain which checks protect population, which protect type/units and which protect the consumer calculation. Run a clean seed and full selected build after both authored SQL files are complete.

Create the required relationship negative case in a disposable copy by changing a holdings fund to an unknown identifier; retain the specific membership failure. Also use the runtime helper to inspect the separately declared missing-FX coverage failure when that drill is selected. Capture the specific failed node and its diagnostic output. Restore the input, reseed and rebuild the affected dependencies, then rerun the independent comparison. Keep the original CSVs and canonical starter unchanged. A later correction/replay exercise has a different expected output contract, so do not reuse its intentional baseline reconciliation failure as this phase's final evidence.

#### Hint


<details>
<summary>Predict the failed assertion before injecting a defect</summary>

Choose one defect at a time and name the test you expect to fail before running it. Inspect failed rows or compiled SQL to distinguish a genuine coverage failure from an unrelated unfinished model. A relationship check on fund identifiers needs a separately unique fund dimension; the holdings themselves are not unique by fund. Keep the fixture restore and selected reseed in your note so the repaired run can be reproduced.

</details>

#### Check


The final baseline build must pass the structural and business assertions and reproduce the independent eight-key report. The negative run must fail on the promised relationship, grain or missing-enrichment assertion, and the repaired run must pass after restoring and reseeding the copied input. Record all three states with their relevant artifact identities; replacing the failure log with the final green log loses the learning evidence.

Use the runtime helper only on your owned attempt, then select the affected seeds and upstream graph deliberately. Inspect the failing test result rather than inferring its cause from a nonzero command exit. Explain why the report's own total cannot be its only oracle and why not-null and relationships need complementary tests. The root phase verifier may validate finished warehouse output, but your explanation and negative-case evidence remain part of the completion standard. If warehouse access is absent, prepare the drill and its expected assertion locally while leaving execution pending.

```bash
dbt build --project-dir . --profiles-dir . --target local
python runtime/lab.py mutate . --drill missing-fx
# Reseed/rebuild and retain the intended failure, then restore the copied input.
python runtime/lab.py restore .
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p1-05-reasoning)


## Phase completion


Submit the authored holdings staging model, fund/date report, structural and business tests, and an evidence note that connects the raw feeds to the consumer result. Your explanation must distinguish the raw business key from a model name and the reporting currency from a fund master attribute. Show how you derived one result from the copied CSVs before looking at the warehouse output. Include a selected build, its manifest and run-results identities, the independent comparison, and the intended relationship failure followed by repair.

A successful seed operation establishes input loading; a parsed project establishes that dbt understands the files. Neither establishes this learning outcome. The completion verifier must reject unfinished models and compare actual warehouse values with the independent reference. Keep any unavailable connected check pending. Retain your attempt rather than replacing it with the instructor project, and explain which supporting models were supplied. You may enter the advanced phase through its prepared baseline without copying another learner's work. That baseline is disclosed assistance, not evidence that you authored its components.

---


## Optional stretch


The core completion standard is independent of optional work. No additional stretch is required in this phase; the next phase has an independently prepared entry baseline.

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Inspect the project and source grain

<a id="dbt-p1-01-reasoning"></a>

<details>
<summary>Reasoning for dbt-p1-01: A connection is a prerequisite, not a product result</summary>

The expected inventory contains two observations for each of four funds. The composite holding key includes date and instrument, so an eight-row source can be valid even though fund identifiers repeat. Source declarations map logical inputs to already loaded relations; they cannot replace seeding. A target named local describes configuration selection, while its type selects Databricks execution. Good evidence separates CSV inspection, connection readiness and actual warehouse population, retaining an unavailable boundary as pending instead of combining them into one vague pass.

[Return to dbt-p1-01](#dbt-p1-01)

</details>

### Reasoning: Declare and use sources

<a id="dbt-p1-02-reasoning"></a>

<details>
<summary>Reasoning for dbt-p1-02: Logical dependencies and physical ownership must both be correct</summary>

A source call declares an external input; a model reference declares a derived dependency. The identifier expression resolves the source into an owned physical relation without putting environment-specific names into every model. Missing input and wrong source mapping can produce similar first errors, but their repairs differ. The manifest plus seed inventory distinguishes them. Reference data can be loaded and inspected without forcing it into this bounded consumer graph. The complete chain is evidence of understandable lineage, not proof that a compiled query has executed.

[Return to dbt-p1-02](#dbt-p1-02)

</details>

### Reasoning: Normalize type, unit and key contracts

<a id="dbt-p1-03-reasoning"></a>

<details>
<summary>Reasoning for dbt-p1-03: Typed staging preserves business observations</summary>

The expected transformation changes representation without losing either May date. Fund/date/instrument is the row identity; fund alone is a reporting dimension. Correct decimal and date types support later business calculations, but do not prove the join coverage by themselves. The duplicate-key drill should fail because it creates a second observation at the same declared grain. Restoring the copied raw input repairs that cause. Multiplying quantity by price would create a different valuation measure and must not replace the supplied native value.

[Return to dbt-p1-03](#dbt-p1-03)

</details>

### Reasoning: Build a useful mart through ref

<a id="dbt-p1-04-reasoning"></a>

<details>
<summary>Reasoning for dbt-p1-04: Reconciliation tests every business key and value</summary>

The correct report has eight rows because date is part of the consumer key. Its GBP numerator uses the supplied native valuation and a matching dated FX rate. The synthetic unit count creates a teaching NAV measure; the cash exclusion and currency choice must travel with the result. A table materialization changes storage and refresh behavior, not the expected business values. Full per-key comparison detects collapsed dates and shifted fund totals that a single grand-total check could miss.

[Return to dbt-p1-04](#dbt-p1-04)

</details>

### Reasoning: Add minimum key and relationship proof

<a id="dbt-p1-05-reasoning"></a>

<details>
<summary>Reasoning for dbt-p1-05: A meaningful drill identifies the failing contract</summary>

Structural assertions and the independent reference protect different risks. An unknown fund should fail membership or retained-population checks; a missing FX observation should fail dated enrichment coverage rather than be replaced by a rate of one. The useful evidence connects the controlled change to the actual failed test, then connects restoration and reseeding to the recovered eight-key report. A generic command failure or a final green screenshot cannot establish that sequence. The untouched starter remains unfinished until the authored outcomes and their checks are complete.

[Return to dbt-p1-05](#dbt-p1-05)

</details>
