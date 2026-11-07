# dbt — Portfolio Analytics

Build a traceable transformation from supplied custodian feeds to a fund/date report on Databricks. The foundation phase teaches external sources, typed staging, business grain, model references and independent output checks. The advanced phase supplies that baseline and develops dated enrichment diagnosis, reconciliation, controlled corrections, history and a reviewable feature. The consumer question is what each fund's supplied holdings contribute to GBP exposure on each fixture date, with a carefully labelled teaching NAV measure.

## Before you start

Open the supplied training project in its dev container and complete the delivered Databricks sign-in before starting timed practice. Confirm the installed dbt executable includes the Databricks adapter, identify the approved catalog/schema and reconcile its aliases. Choose a unique relation prefix for each attempt. Your terminal runs dbt while the SQL warehouse executes the models; neither a local target name nor a successful parse establishes a warehouse result.

Prepare through the version-explicit mise interface from the training project root, then run direct dbt commands inside the copied attempt. Keep your original work and use a new workspace for another try. Advanced practice has an independently prepared starter; it does not assume you completed or viewed someone else's foundation answer. Both phases use the same eight supplied input CSVs and disclosed supporting models, with authoring responsibilities listed in the phase guide.

## Suggested timeline and tasks

The phase estimates include reading, authoring, checking and explanation. Allow additional time for sign-in, tool setup, source loading and optional extensions. Follow your instructor's selected route for Wednesday's practice block.

| Phase | Task | Minutes |
| --- | --- | --- |
| Foundation | [dbt-p1-01: Inspect the project and source grain](phase-one-certified/README.md#dbt-p1-01) | 15–22 |
| Foundation | [dbt-p1-02: Declare and use sources](phase-one-certified/README.md#dbt-p1-02) | 15–22 |
| Foundation | [dbt-p1-03: Normalize type, unit and key contracts](phase-one-certified/README.md#dbt-p1-03) | 15–22 |
| Foundation | [dbt-p1-04: Build a useful mart through ref](phase-one-certified/README.md#dbt-p1-04) | 15–22 |
| Foundation | [dbt-p1-05: Add minimum key and relationship proof](phase-one-certified/README.md#dbt-p1-05) | 15–22 |
| Advanced | [dbt-p2-01: Diagnose a join fan-out before repair](phase-two-proficient/README.md#dbt-p2-01) | 18–24 |
| Advanced | [dbt-p2-02: Repair enrichment at the intended grain](phase-two-proficient/README.md#dbt-p2-02) | 18–24 |
| Advanced | [dbt-p2-03: Write reconciliation that detects the negative case](phase-two-proficient/README.md#dbt-p2-03) | 18–24 |
| Advanced | [dbt-p2-04: Prove incremental update and replay behavior](phase-two-proficient/README.md#dbt-p2-04) | 18–24 |
| Advanced | [dbt-p2-05: Explain dependency impact and hand over](phase-two-proficient/README.md#dbt-p2-05) | 18–24 |

## Choose your phase

- [Foundation phase](phase-one-certified/README.md): complete the assigned source/staging/report slice and prove its minimum business contract.
- [Advanced phase](phase-two-proficient/README.md): begin from its supplied baseline and demonstrate diagnosis, replay and a useful handoff.

Finish the core tasks before choosing optional stretch. These phases use the supplied Portfolio Analytics data on Databricks.

## Teaching concepts

Trace source declarations to physical owned tables, distinguish source and model dependencies, preserve composite grain, choose deliberate materializations, and separate native valuation from dated GBP conversion. Structural tests and independent business calculations protect different failure modes. The advanced route extends those ideas into controlled Delta replay, snapshot validity, documentation and the Astro worker boundary. Reasoning keys stay at the end of their owning phase; full runnable instructor references are supplied separately.

## Question-led foundations and further study

Use questions 1–8 alongside the foundation tasks. Questions 9–13 introduce further study.

### Foundations

<a id="dbt-guide-q01"></a>

#### What problem does dbt solve, and where does it fit in a data pipeline?

Custodian feeds arrive as holdings and cash; prices, dated FX and fund metadata explain those positions. dbt orders SQL transformations and tests. The Databricks warehouse executes SQL and stores views/Delta tables. Running dbt in a local process does not create a local database. Our consumer output is a fund/date GBP exposure and a teaching NAV, with lineage back to the supplied raw tables.

<a id="dbt-guide-q02"></a>

#### What does a dbt project contain, and how do we connect it to our data?

The prepared Portfolio Analytics attempt contains models, eight seeds, tests, macros, profiles and a local target directory. Read the setup contract before connecting. Profile portfolio_analytics and target local point to the assigned Databricks warehouse. dev and airflow are also Databricks targets. Record the project/profile paths and installed versions; reject missing namespace or conflicting aliases rather than guessing a username.

<a id="dbt-guide-q03"></a>

#### How does a SQL query become a dbt model?

Author models/staging/stg_holdings.sql. Select fund_cd as fund_id, pos_dt as position_date, isin as instrument_id, qty as decimal quantity, mkt_val_lc as decimal native value and ccy_cd as local_ccy. Cast dates and retain extraction time. Its business key is fund/date/instrument. The baseline contains eight rows: one instrument for each of four funds on each of two dates. A model file becomes an owned view after execution; its filename is the ref name, while its physical alias includes your prefix.

<a id="dbt-guide-q04"></a>

#### How do we connect models using source() and ref()?

source('custodian','holdings_raw') reads the prefixed raw seed-backed Delta table. ref('stg_holdings') connects transformations and lets dbt establish order. Declare raw source database/schema from the target and identifier from the ownership prefix. A source declaration does not load data. Run the explicit eight-seed preparation, then inspect the compiled relation names and graph. Supplementary NAV/fund seeds alone leave six raw sources missing.

<a id="dbt-guide-q05"></a>

#### How should we split a large query into understandable, reusable models?

Keep cast/rename in five staging views; dated enrichment belongs in int_holdings_enriched. Join prices by instrument/date and FX by native currency, GBP and date. Fund metadata joins by fund key. Cash positions have fund/date/currency grain and remain separate until aggregated correctly. Validate right-side uniqueness before joining: an undated FX join fans eight holdings out across two dates. refdata_raw is available for a classification extension; it is not a substitute for fund_master_raw.

<a id="dbt-guide-q06"></a>

#### When should a model be a view or a table?

Views suit the small staging and intermediate transformations. A consumer table persists the report for repeated reads and a stable tested handoff. Inspect information_schema for the prefixed relation and its type; do not infer storage from a successful command. Tables on this adapter use Delta. The richer product has optional optimisation hooks, but the guide omits them to avoid adding managed-permission assumptions to the core exercise.

<a id="dbt-guide-q07"></a>

#### How do we know our models produce trustworthy data?

Test non-null keys, composite uniqueness, decimal types, dated join coverage and populations. Missing FX is an error, not an implicit rate of one. All supplied holdings happen to be GBP; fund PEF-EM-GROWTH has USD master currency, but this report explicitly values in GBP. Market value is supplied by the custodian and must not be replaced with quantity times price without an agreed contract. The reference NAV uses 100 million synthetic units and excludes cash. Compare each of eight fund/date rows independently with seed_custodian_nav.

<a id="dbt-guide-q08"></a>

#### How do we make a change confidently and explain the result?

Select the changed model and downstream dependencies, retain compiled SQL and run results, then query the actual warehouse. For a negative drill remove a dated GBP FX row in a disposable copy. matched_enrichment must fail; restore, reseed and rebuild before handoff. Documentation must state grain, units, source meaning and the NAV limitation. A green structural test can miss a correct-looking wrong business measure.

<a id="dbt-further-study"></a>

### Further study

Questions 9–13 are separately timed advanced study.

<a id="dbt-guide-q09"></a>

#### When does Jinja help, and when should we keep the logic in SQL?

A small native_value(value, rate) macro casts the GBP conversion to a declared decimal precision. Inspect its compiled multiplication and explain the arguments. Keep business joins in readable SQL. Reuse earns its place when the same expression has the same meaning in both the consumer model and the correction/replay model; a macro cannot settle currency or grain disagreements.

<a id="dbt-guide-q10"></a>

#### How can we process less data without producing incorrect results?

In the separately timed advanced phase, the required holdings_replay model uses Delta merge with fund/date/instrument as its composite key. Read the whole tiny fixture each time so older-date corrections are included. Copy one holding, add 1,000 GBP to its value, reseed, merge and replay. Query the original key after each run: corrected value and exactly one row. A maximum-date watermark would miss this controlled historical correction. This is a labelled variation, not history already present in the source.

<a id="dbt-guide-q11"></a>

#### How do we preserve history when source records change?

Snapshot a copied fund-master relation before and after one controlled name change using the check strategy and fund_cd key. Retain validity columns and verify the original closed row plus one current row. All snapshots remain in the assigned schema with owned aliases. Snapshots record observed states, not every event between observations. Restoring source CSVs does not delete history; a new attempt/prefix starts clean.

<a id="dbt-guide-q12"></a>

#### How does a dbt project move into reliable team delivery?

Review SQL, tests, contract and target routing together. Hand off the exact prepared project to Astro with a worker-visible path and inspected executable; resolve the token at task execution. Record versions at both boundaries. Production promotion remains a design discussion. A local compile or prior green run cannot prove a new scheduler/worker/output path.

<a id="dbt-guide-q13"></a>

#### Can we independently deliver a documented, tested model?

Build fund_nav_report at fund/date grain from the available enrichment. State GBP, the 100 million synthetic units and excluded cash. Include one independent business query, lineage, structural tests, reconciliation, failure/repair and a reviewable diff. Your evidence should let another person distinguish a missing model, stale data, join fan-out and a currency-definition mistake.
