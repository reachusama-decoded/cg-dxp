# Data Creator glossary

Use this alongside the business brief and source disclosures. Status codes and role assignments below belong to the classroom exercise; they are not public CG product classifications or enterprise appointments.

## Investment products and costs

| Term | Meaning in this project |
|---|---|
| Capital Group (CG) | The investment manager whose public product information supplies the real-data portion of this project. |
| American Funds | A fund family associated with Capital Group. The ETF and SMA records are separate offering types. |
| The Capital System™ | CG’s investment approach, combining distinct investment perspectives with a long-term focus. |
| Financial professional | Someone who advises or works with investors. Their enquiry provides the scenario; your direct data consumer is the internal analyst. |
| RIA | Registered investment adviser. The SMA source is intended for this audience; classroom use needs instructor confirmation. |
| Investment vehicle | The fund or account arrangement through which an investor participates. This project distinguishes mutual funds, ETFs and SMAs. |
| Offering | A record in our catalogue: one ETF, mutual-fund share class or SMA strategy. The 109 records do not represent every CG product worldwide. |
| Strategy | An investment approach implemented through a fund or account. An SMA strategy record does not identify a client account. |
| Mutual fund | A pooled investment fund. Different share classes can provide ways to own the same fund. |
| Share class / Class F-3 | A class has its own identifiers and expense arrangements. This project selects Class F-3, written `F3` in detail records and sometimes `F-3` in the catalogue. Those labels do not establish investor eligibility. |
| ETF | Exchange-traded fund. Its shares trade at a market price that can differ from net asset value. The CG ETFs in this source are actively managed. |
| SMA | Separately managed account. The dataset describes strategies offered through account arrangements, not individual accounts. |
| Sponsor | A firm or platform through which an SMA arrangement is offered. Account terms and fees can depend on the sponsor. |
| Composite | A group of portfolios used to report strategy performance under a stated methodology. Its return is not a particular client’s return. |
| Expense ratio | Annual fund operating expenses expressed as a percentage. It does not necessarily include every cost paid by an investor. |
| Gross/net expense ratio | Expenses before/after applicable fee waivers or reimbursements. These are alternative measures; do not add them together. |
| Waiver / reimbursement | An arrangement that reduces expenses borne by the fund. Use its disclosure to understand the published net figure. |
| Basis point (bp/bps) | One hundredth of a percentage point. `0.39%` is 39 bps; the source stores that percentage as `0.39`. |
| Percentage point | The unit used by source percentage fields. Multiply the stored percentage-point value by 100 to obtain bps. Do not treat `0.39` as the decimal fraction `0.0039`. |
| All-in cost | The investor’s total cost, potentially including separately charged advice, platform or account fees. This dataset does not establish that total. |
| AUM | Assets under management: the value of assets managed. The teaching catalogue contains no complete AUM or revenue dataset. |

## Performance and identifiers

| Term | Meaning in this project |
|---|---|
| NAV | Net asset value per share. A NAV return uses this valuation basis. |
| Market price | The price at which ETF shares trade. Market-price returns have different calculation conventions from NAV returns. |
| MOP | Maximum offering price. Returns on this basis incorporate the applicable maximum sales charge. |
| Return basis | How the published return is calculated, such as NAV, market price or SMA composite gross/net performance. |
| Cumulative return | Total investment change over the stated period. |
| Annualized return | A compound annual rate summarizing change over the stated period. A three-year annualized return is not the total three-year change. |
| Horizon / `1Y`, `3Y`, `5Y`, `10Y` | The period measured: one, three, five or ten years. |
| Frequency | The source’s reporting label. The project explicitly maps `monthEnd` and `monthly` to the same monthly label. |
| Composite gross/net return | Strategy-composite performance before/after the fees specified in its methodology. Their difference does not establish an individual client’s fee. |
| Yield | An income measure with its own conventions. It is different from total investment return. |
| CUSIP | A security identifier used by some fund/ETF records. Preserve the supplied identifier; names alone are unsafe join keys. |
| Product ID | The snapshot’s key for an ETF, fund class or SMA strategy. Use it to connect records within this pack. |
| Listing ID | The identifier of a particular source listing. A product may appear in more than one listing. |
| Observation | One published value with its context: product, measure, basis, horizon, date and source. One product can have many observations. |

## Data design and quality

| Term | Meaning in this project |
|---|---|
| Data product | Data prepared for a named consumer, with a defined purpose, schema and quality expectations. |
| Data Creator / DPC | Your role: design, build and explain the data product. DPC is the course abbreviation for Data Product Creator. |
| DPM | Data Product Manager: the classroom role agreeing scope, version and consumer priorities. |
| Data Steward | The classroom role reviewing field meanings and quality rules. |
| Consumer | The person using the output. Here it is the fictional internal Product Information Analyst. |
| PRD | Product requirements document: the consumer’s problem, required outcomes and acceptance criteria. |
| Data contract | The agreed requirements for data: scope, fields, row meaning, units, quality, access and change handling. |
| ODCS | Open Data Contract Standard: the format used for the contract. The instructor supplies the version and validator. |
| STTM | Source-to-target mapping: which source fields produce each output field and how they are transformed. |
| RFD | Request for Discussion: the course decision-record format. Use Context, Decision and Consequences to explain your source-selection decision. |
| SLA | Service-level agreement: a promise about service, such as update timing. Do not invent a production SLA for this frozen snapshot. |
| DPLC | Data Product Lifecycle: the course’s enterprise lifecycle with phases 0–8. It is separate from this event’s learning phases 0–3. |
| Schema | Column names, types and related constraints. |
| Grain | What one row represents. The integrated catalogue has one row per product or strategy ID. |
| Population | The complete set of required IDs. A table with unique IDs can still be missing products. |
| Join fan-out | A join multiplies rows because several records match one key. Joining every return to the catalogue can break its one-row-per-ID requirement. |
| Provenance / lineage | Records of where a value came from and how it was transformed. Keep separate product, fee and return source references. |
| Source layer | The representation collected from the website, such as catalogue or detail records. Several layers can describe the same product. |
| Normalization | Putting source values into consistent forms while preserving meaning, such as a documented frequency-label mapping. |
| Extraction gap | Information absent from the extracted CSV, even though it may appear elsewhere on the source page. A blank does not establish that CG never published it. |
| Null | An unknown or absent value. It is different from numeric zero. |
| Fixture | A fixed input used for practice or testing. Synthetic fixtures are labeled and kept separate from real source claims. |
| Oracle | The instructor’s independently calculated expected results, used to check the learner’s output. |
| Negative test | A test using deliberately invalid input to show that a particular quality rule rejects it. First demonstrate that valid input passes. |
| Criterion status | Result of the stated cost filter: `matches`, `does_not_match` or `needs_review`. |
| Comparison status | Whether figures meet the declared comparison rules: `comparable_on_declared_dimensions`, `not_comparable` or `needs_review`. Matching those rules does not establish equal risk or suitability. |
| Source-/domain-/consumer-aligned | Model purposes: preserve source records; define reusable business meanings; answer a named consumer’s question. These differ from processing stages such as staging or curated. |

## Tools, execution and submission

| Term | Meaning in this project |
|---|---|
| CLI | Command-line interface: a tool run from a terminal. |
| Devcontainer | The prepared container-based development environment used for the event. |
| Host / worker / warehouse | Your terminal’s environment; the process executing an Airflow task; the Databricks service executing SQL. Each needs its own files and access settings. |
| mise | Selects the prepared environment and runs named tasks defined by this project. |
| Docker image / container | An image is the template for a runtime environment; a container is a running instance. |
| Astro / Astronomer | Astro tooling manages the Airflow environment used here; Astronomer provides that tooling. |
| Airflow / DAG | Airflow schedules and runs tasks. A DAG (directed acyclic graph) defines tasks and their dependency order. |
| Adapter | The library connecting a tool to a particular backend. `dbt-databricks` lets dbt compile and execute models for Databricks. The local assessment runner supports only a subset of that behavior. |
| Virtual environment / venv | A separate Python environment containing its own installed packages. The dbt environment inside Astro is separate from Airflow’s Python environment. |
| dbt seed / model | A seed loads CSV data; a model is SQL that defines a table or view. |
| dbt macro | Reusable instructions that generate SQL during compilation. The warehouse later executes that SQL. |
| Generic dbt test | A reusable SQL check. Rows returned by the test represent violations. |
| Databricks SQL warehouse | The connected service that executes this project’s SQL. |
| Working product / challenge template | Edit and run your owned folder under `data_products/`. `challenges/` contains the starting template and instructions. The workspace check pins the product/project/profile and compares target settings with the instructor’s assignment. |
| Catalog / schema / relation | Database locations: a catalog contains schemas; a schema contains relations such as tables and views. |
| Owned prefix / namespace | The instructor-assigned prefix for your table/view names within the approved catalog and schema. It keeps learners’ outputs separate. |
| Candidate / accepted view | A new output awaiting checks; the view pointing consumers to the last accepted output. A failed candidate must leave that accepted output unchanged. |
| Release gate | Dependencies and checks that allow acceptance only after required tasks succeed. |
| Receipt | A saved record identifying a run or accepted release. It is evidence, not enterprise publication approval. |
| Callback / sink | Code invoked after a task state change; the event writer it calls. A failure callback records diagnostics; it does not replace release dependencies. |
| Blueprint / DAG factory | A reusable workflow template; a function that creates configured DAGs. Two configurations must produce independent workflows. |
| Nonce | A unique marker identifying one readiness check. Matching markers help reject old receipts. |
| Hash / SHA | A content fingerprint. File hashes identify captured bytes; a Git commit SHA identifies a version of code. A URL is not a content fingerprint. |
| Manifest | A list of inputs, files or run records with identifiers and hashes used to check what ran. |
| Commit / tag / PR | A saved Git version; a name pointing to a commit; a pull request for reviewing changes. Record the code commit that actually ran. |
| Test double | A simplified stand-in used in local tests, such as a fake Airflow task. Passing it does not prove execution on a real worker. |
| Connected evidence | Results from actual Databricks and Airflow execution, with matching code and run identifiers. Local parsing and simulation provide different evidence. |
| Catalyst / AI skill | The course’s AI-assistance environment; a versioned set of instructions for a defined task. Invoke and revise your own skill, then check its claims independently. |
| Sanitized evidence | Logs or results with credentials and sensitive text removed, while retaining the identifiers needed to understand the run. |

## Two-clock history

| Term | Meaning in this project |
|---|---|
| Reporting / retrieval / load time | The date a source reports; when the source was captured; when your process loaded it. None automatically establishes when a fee took effect. |
| Business-valid time | When a statement applies in the business. The synthetic exercise specifies these dates explicitly. |
| System-known time | When the system knew a version of that statement. It allows reconstruction of earlier knowledge after a correction. |
| Bitemporal | Keeping both business-valid and system-known intervals for each fact. |
| Knowledge cutoff | The time whose available knowledge an enquiry asks you to reconstruct. |
| As-of query | A query for a stated date/time. The historical exercise needs both a business date and a knowledge cutoff. Source `as_of_date` instead means the published reporting date. |
| Half-open interval | Includes its start and excludes its end. `[September 15, October 1)` includes September 15 but excludes October 1. A null end means the interval remains open. |
| Payload / semantic identity | The fields making up an event’s statement; the fields used to decide whether it is the same statement. An attempt timestamp does not change that statement. |
| Idempotent retry | Repeating the same identified input leaves the stored facts unchanged. Attempt logs may still record another execution. |
| Replay | Processing previously supplied events again. It must preserve the same history when those events are unchanged. |
| Correction | A new statement that changes a fact for specified dates. Preserve what was previously known and limit the correction to its stated interval. |
| Two-dimensional overlap | Two versions of the same product/metric overlap in both business-valid and system-known time. The integrity test rejects this; overlap in business dates alone can be valid historical knowledge. |
