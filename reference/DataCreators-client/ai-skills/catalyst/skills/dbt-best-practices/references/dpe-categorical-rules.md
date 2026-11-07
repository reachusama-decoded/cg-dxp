# dbt-project-evaluator Categorical Rules (Generation-Time Guidance)

> These rules are **generation-time guidance only** — Catalyst does not run
> `dbt-project-evaluator` at runtime. They are baked into skill prompts so
> models are generated conformant from the start.
>
> Authoritative package docs: https://github.com/dbt-labs/dbt-project-evaluator
>
> Where a rule overlaps an RFD 0008 SQL rule (Hard Coded References,
> schema.yml co-location, Test Coverage on PKs, Documentation Coverage),
> **RFD 0008 wins as authoritative**. The rules below are the net-new
> evaluator-derived content not covered by RFD 0008.

---

## Category 1 — Modeling

### DAG Fanout

**What it checks:** A single model that fans out to an unusually large number
of direct downstream dependents (typically > 10 in dbt-project-evaluator's
default threshold). This makes the model a structural bottleneck and a
high-blast-radius change point.

**When it matters:** Primarily in marts and intermediate layers. A staging
model that many intermediate models all read is acceptable; a domain mart that
half the org's reports all join directly is not.

**How Catalyst applies it:** When generating intermediate or marts models,
avoid designing a single "god" CTE or model that every consumer references.
Prefer narrowing by domain boundary — split wide fan-out intermediates into
domain-scoped views so changes are scoped. Warn in code comments when a
generated model is expected to have > 10 downstream refs.

---

### Source Fanout

**What it checks:** A raw source table that is read directly by more than one
staging model. dbt-project-evaluator flags this because it means the same
raw source is being re-interpreted in multiple places, risking drift between
definitions.

**When it matters:** Any time two staging models both reference the same
`source()` call with identical table names. One canonical `stg_<source>__<table>`
model should own each raw source; all other consumers should `ref()` that
staging model.

**How Catalyst applies it:** The `/source-aligned` skill generates exactly one
`stg_` model per source table. Other authoring skills are instructed to
`ref()` the staging model rather than calling `source()` directly, keeping
source fanout at 1.

---

### Rejoining of Upstream Concepts

**What it checks:** A model that joins two models which are themselves
downstream of a common ancestor — effectively a "diamond" dependency pattern
where the same grain flows through two paths and is re-joined. This can
produce row multiplication or double-counting bugs that are hard to diagnose.

**When it matters:** Common in lift-and-shift migrations where legacy SQL had
implicit deduplication. The evaluator flags the structural pattern; the
actual correctness depends on grain alignment.

**How Catalyst applies it:** When generating joins across intermediate models,
check whether both sides share an upstream `ref()`. If they do, emit a
warning comment in the generated SQL noting the rejoining risk and recommend
that the developer verify grain alignment and deduplication before promoting.

---

### Direct Join to Source

**What it checks:** A non-staging model (intermediate or mart) that calls
`source()` directly rather than going through a staging model. Staging models
exist to apply consistent type casting, renaming, and null handling; bypassing
them lets raw variance leak into business logic.

**When it matters:** Always — any intermediate or mart that calls `source()`
is a violation. This is one of the evaluator's strict rules.

**How Catalyst applies it:** `/source-aligned`, `/domain-aligned`, and
`/consumer-aligned` skills are instructed never to emit `source()` calls in
non-staging models. All upstream refs in intermediate and mart SQL use
`ref()` only.

---

## Category 2 — Testing

### Test Coverage Thresholds

**What it checks:** dbt-project-evaluator requires that every model has at
least one test, and that primary key columns have both `unique` and
`not_null` tests. It surfaces models or columns that fall below the threshold.

**When it matters:** Prototype mode can carry reduced coverage; production
and lift-and-shift require full coverage. The threshold distinction is
captured in `references/rule-severity-by-mode.md`.

**How Catalyst applies it:** Every generated `schema.yml` includes `unique`
and `not_null` tests on the declared primary key. In production mode, all
foreign-key columns get a `relationships` test. In prototype mode, only the
PK tests are required; additional tests are emitted as commented-out
suggestions so they can be activated on promotion.

---

### Relationship Tests on Foreign Keys

**What it checks:** Foreign-key columns in a model's schema that lack a
corresponding `relationships` test. Without this test, referential integrity
is only enforced by trust, not by the dbt test run.

**When it matters:** Most important in domain-aligned (intermediate) and
consumer-aligned (mart) models where grain boundaries meet. Less critical for
staging models where the goal is to mirror the source faithfully.

**How Catalyst applies it:** When a `data-model.md` artifact declares a
foreign key, the authoring skill emits a `relationships` test in schema.yml
pointing to the upstream model's primary key. In prototype mode this is
emitted as a commented block with a `TODO: activate on promotion` note.

---

## Category 3 — Documentation

### Documentation Coverage Thresholds

**What it checks:** dbt-project-evaluator requires that every model has a
`description` in schema.yml, and that all columns exposed in contracts or
accessed by downstream consumers are also described.

**When it matters:** Prototype mode skips this by default (cost vs. benefit
early in iteration). Production requires full coverage. Lift-and-shift gets a
warn rather than error because legacy column semantics may be unknown until
profiling is complete.

**How Catalyst applies it:** In production mode, every generated schema.yml
column entry includes a `description` field populated from the consumer-use-case-map
or data-contract artifact when available, falling back to a `# TODO: document`
stub. In prototype mode, only the model-level `description` is required;
column-level descriptions are stubbed.

---

### Public Models Without Contracts

**What it checks:** A model declared with `access: public` that has no
`contract: {enforced: true}` block. Public models are part of the API surface
for consumers outside the domain; without an enforced contract, column names
and types can drift without a breaking-change signal.

**When it matters:** Any model intended for cross-domain consumption. The
evaluator treats this as a governance violation, not just a style issue.

**How Catalyst applies it:** Whenever a generated model is classified as a
consumer-aligned (mart) model with `access: public` in the DPLC design phase,
the `/setup-dbt-project` and authoring skills emit a `contract: {enforced: true}`
block and a matching column list. Models without a signed data contract should
remain `access: protected` until the contract is finalised.

---

## Category 4 — Structure

### Model Naming Conventions

**What it checks:** dbt-project-evaluator enforces that staging models are
prefixed `stg_`, intermediate models are prefixed `int_`, and marts models
are prefixed the mart-layer name (typically the domain, e.g. `orders_`). It
also flags models in the wrong subdirectory relative to their prefix.

**When it matters:** Always — naming convention mismatches cause the evaluator
to flag the model even when it is otherwise correct.

**How Catalyst applies it:** File naming and directory placement follow the
convention enforced by RFD 0008 (SQL-NAMING-001, SQL-MODEL-004). The evaluator
conventions are a superset; Catalyst satisfies both by using the stricter RFD
0008 names and placing files under `models/staging/`, `models/intermediate/`,
and `models/marts/<domain>/` respectively.

---

### Source Definitions in Dedicated Files

**What it checks:** `source:` declarations that live outside a dedicated
`sources.yml` file (or equivalent named source file) rather than co-mingled
with model definitions.

**When it matters:** Structure clarity and navigation. Large schema.yml files
that mix source and model declarations become hard to maintain.

**How Catalyst applies it:** `/setup-dbt-project` emits a separate
`models/staging/_sources.yml` for each source system. Model schema.yml files
contain only model definitions, not source declarations.

---

## Category 5 — Performance

### Downstream Models Materialized as Views Referencing Expensive Intermediates

**What it checks:** A mart-layer model materialized as `view` that sits on
top of an intermediate chain including large incremental or table materializations.
Each view re-runs the full upstream query at query time, negating the cost of
pre-building the intermediates.

**When it matters:** Production and lift-and-shift modes where query cost
matters. Prototype can stay view-heavy for fast iteration.

**How Catalyst applies it:** The materialization selection logic in
`references/rule-severity-by-mode.md` ensures marts default to `table` (or
`incremental` for large row counts) in production and lift-and-shift. View
materializations in the mart layer trigger a warning comment in generated SQL.

---

## Category 6 — Governance

### Undocumented Exposures

**What it checks:** dbt `exposures:` blocks that lack `owner`, `type`, or
`description` fields. Exposures without owners cannot be contacted when a
model they depend on changes.

**When it matters:** Any project that declares BI tool exposures (Databricks
SQL Dashboards, Tableau, Power BI). Less relevant for pure API consumers.

**How Catalyst applies it:** When a consumer-use-case-map artifact declares
a BI tool consumer, the authoring skill emits a fully-populated `exposures:`
block in schema.yml including `owner.email`, `type`, `description`, and a
`depends_on: ref()` list. Stubbed owner fields use the product team's
distribution list from the data-contract artifact when available.

---

## Overlap with RFD 0008 (Deferred)

The following evaluator checks are covered by RFD 0008 and are **not** repeated
here — consult the spec at `docs/superpowers/specs/2026-05-14-dplc-build-skills-design.md`:

| Evaluator Check | RFD 0008 Rule |
|---|---|
| Hard Coded References | SQL-MODEL-002 |
| schema.yml co-location | SQL-MODEL-004 |
| Test Coverage on PKs (unique + not_null) | SQL-TEST-001, SQL-TEST-002 |
| Documentation Coverage (model description) | SQL-TEST-003 |
