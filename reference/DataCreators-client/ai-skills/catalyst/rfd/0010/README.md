---
authors: DMRS
state: published
discussion: https://github.com/cg-open-itg/catalyst/pull/5
---

# RFD 0010 Lake Versioning Strategy

## Introduction

Caspian is a core data platform within Capital Group’s Enterprise Data Office (EDO), supporting multiple domains and downstream consumers across Databricks and Dremio. As the platform has scaled, multiple active versions of the same logical datasets have emerged, creating confusion for consumers, increasing maintenance overhead, and introducing governance gaps.

## Terminology

| Term | Definition |
|------|------------|
| **IAT** (Impact Assessment Template) | A structured communication artifact published by producing team before any schema change is introduced. An IAT describes nature of the change, the migration timeline, affected views/tables etc, and actions consumers must take. It serves as the formal notification and governance record for schema evolution events. |
| **Producer** | data engineering team that owns and maintains a curated table and its associated consumer-facing views. |
| **Consumer** | A downstream team or application that queries a consumer-facing view. |
| **Backward-compatibility version** | A temporary view created to preserve an older schema shape during a migration window, allowing consumers time to adopt a breaking change. |


## Two‑Perspective Versioning Model

This strategy explicitly separates responsibilities between producer‑owned curated tables and consumer‑facing views. This separation keeps Caspian operationally simple while allowing consumers to migrate at different speeds.

## Caspian Curated Tables – Producer Perspective

•	Only one authoritative version of each curated table exists
•	Curated tables do not include version suffixes
•	Schema changes are applied directly to the curated table
•	Historical recovery is handled via bitemporal logic and downstream S3 snapshots


## Consumer‑Facing Views – Consumer Perspective

Consumers never access curated tables directly. Views act as the versioned contract and are the only supported access mechanism.

## View Versioning Options


| Option            | Description                                                                 | Consumer Impact                                                                 | Governance Impact                                                                 |
|-------------------|-----------------------------------------------------------------------------|----------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| `view` / `view_prev` | Alias‑based views where no suffix reflects the latest schema and `_prev` exposes the previous schema | Fast adopters move immediately; slower adopters switch to `_prev` with minimal changes | Low overhead; requires strict retirement enforcement                              |
| `_v1` / `_v2` / … | Incremental, immutable versioned views for each schema change               | Early adopters transition immediately; later adopters remain on the current version and upgrade within defined timeframes | Increased overhead; risk of unused versions persisting and introducing operational risk |
| **Single evolving view (forced alignment)** | A single consumer‑facing view is continuously updated to latest schema, with consumers required to align their code within published timelines | All consumers must update queries and downstream code within defined migration window to avoid breakage | Lowest version sprawl, but highest coordination and enforcement overhead, requires strict timelines and robust consumer change management |


Third option (`Single evolving view`) prioritizes platform simplicity and minimal version sprawl,
but shifts responsibility to consumers to proactively align with schema changes within enforced timelines.
This model is most suitable when strong governance, communication, and migration enforcement mechanisms
are in place.

### Recommended Option: Single Evolving View — Adoption Timelines

Both producers and consumers operate under agreed timelines when schema changes are introduced under this model.

**Producer responsibilities:**
- Publish an IAT before any breaking change is merged, describing nature of the change, multi-stage release plan, and consumer migration deadline
- Introduce breaking changes using multi-stage release pattern (see below), never dropping or altering a column in a single release without prior co-existence
- Execute the cleanup stage only after consumer migration deadline has passed

**Consumer responsibilities:**
- Acknowledge IAT and commit to a migration deadline within defined window
- Migrate queries and downstream code to new column or schema before the agreed deadline
- Migration window is agreed between producer and consumer at the time of the IAT, timeline will vary based on the complexity and nature of the change
- After the deadline, consumers who have not migrated assume full responsibility for any breakage caused by the cleanup stage

### Multi‑Stage Release Pattern for Breaking Changes (Saga)

When a schema change would break existing consumers (e.g. a nullable-to-not-nullable constraint, a type change, a column rename), producers must use a multi-stage release rather than applying change in a single deployment. This allows early adopters to benefit immediately while later adopters continue unbroken until the migration deadline.

**Stage 1 — Additive Release (Producer)**

The producer introduces new or transformed column **alongside the existing column** in the same curated table and consumer view. The existing column is preserved unchanged.

- **Nullable → Not-null constraint**: add new not-null column and backfill it with existing column's value (or a default). Both columns are now present in view.
- **Type change**: add new column with transformed value and expose it in the view alongside the original column.
- **Column rename**: add new column name as an alias to the existing column in the view, both names resolve to the same underlying data.

Both columns live side by side. Early adopters can immediately adopt new column. Consumers not yet migrated continue using the old column without any breakage.

**Stage 2 — Migration Window (Consumers)**

During migration window, consumers migrate their queries and downstream code to reference the new column. Producer monitors adoption. No further changes are made to old column.

**Stage 3 — Cleanup Release (Producer)**

Once the migration deadline has passed, Producer removes deprecated column (or alias) from the curated table and view. This stage is announced in advance as part of the original IAT. If any consumer has not migrated by deadline, Cleanup proceeds as scheduled and consumer is responsible for any resulting breakage.


## Consumer Migration Model

### View Terminology

In this document, a **view** refers to a SQL view built directly on top of a curated table, exposing all rows and columns of that table to consumers. Views are the exclusive access mechanism — consumers never query curated tables directly.

Multiple views may exist over the same curated table to serve different consumer segments (e.g. `listing_extd`, `listing_cspn`). Each of these is a distinct logical view with its own version lifetime. The two-version limit and the saga pattern apply per logical view — governing backward-compatibility versions created when a breaking schema change is introduced to that view.

**Example:** `listing_extd` is a view over the `listing` curated table. If a breaking change is made, `listing_extd_prev` may temporarily exist alongside it during the migration window. Once all consumers of `listing_extd` have migrated, `listing_extd_prev` is retired. At no point do more than two versions of the same logical view coexist.

### Migration Rules

•	Maximum of two active backward-compatibility versions of any given view at any time (current and previous schema shape)
•	An Impact Assessment Template (IAT) must be published when a new version is introduced
•	Migration window is agreed at the time of the IAT and varies based on the complexity and nature of the change
•	Consumers unable to migrate immediately may temporarily use the previous version

## Example Curated Table to Consumer View Mapping

| Curated Table                  | Consumer View                                   |
|--------------------------------|-------------------------------------------------|
| `index_constituent_position`   | `index_constituent_position`            |
| `index_constituent_position`   | `index_constituent_position_russell`    |
| `index_constituent_position`   | `index_constituent_position_ftse`       |
| `index_constituent_position`   | `index_constituent_position_ftse_fi`    |
| `listing`                      | `listing_extd`                          |
| `listing`                      | `listing_cspn`                          |
| `listing`                      | `listing_characteristics`               |


## Schema Change Handling

Quick Summary
| Change Type        | Strategy                                        | Consumer Expectation              | IAT Type |
|--------------------|------------------------------------------------|----------------------------------|----------|
| Add Column         | Single release — additive, no co-existence needed | Explicit column selection         | Soft IAT |
| Drop Column        | Multi-stage release (saga)                      | Remove column from queries        | Soft IAT |
| Rename Column      | Multi-stage release (saga) — treated as add + drop; both names coexist during migration window | Adopt new column name             | Soft IAT |
| Data Type Change   | Multi-stage release (saga) or forced cutover if semantics change | Mandatory migration               | Hard IAT |
| Table Type Change  | Forced cutover — drop + create; no co-existence | Mandatory migration               | Hard IAT |

This table consolidates schema change scenarios, release strategy, consumer expectations, IAT requirements, and governance rationale into a single authoritative reference for Caspian versioning.

| Schema Change Type            | How the Change Happens                                                                 | Release Strategy                                                                                  | Consumer Expectation                                                       | IAT Requirement        | Notes / Rationale                                                                                                   |
|------------------------------|----------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|------------------------|---------------------------------------------------------------------------------------------------------------------|
| Add Column                   | New attribute introduced as part of schema evolution                                    | Single release — new column added to view immediately; no co-existence needed                     | Consumers must explicitly select required columns (no `SELECT *`)           | Soft‑IAT               | Backward‑compatible. Consumers adopting the new column benefit immediately; others are unaffected.                  |
| Drop Column                  | Column is no longer required or meaningful                                              | Multi-stage release (saga): Stage 1 — column deprecated in view; Stage 3 — column removed after migration deadline | Consumers must remove the deprecated column from queries before the deadline | Soft‑IAT               | Column remains in the view during the migration window and is removed in the cleanup release once all consumers have migrated. |
| Rename Column                | Column name changes in the curated layer                                                | Multi-stage release (saga): Stage 1 — new name added alongside old name as alias; Stage 3 — old alias removed | Consumers must adopt the new column name before the deadline                | Soft‑IAT               | Treated as add + drop. Both names resolve to the same underlying data during the migration window.                  |
| Data Type Change             | Column data type requires modification; evaluated case‑by‑case                         | Multi-stage release (saga): Stage 1 — new typed column added alongside original; Stage 3 — original removed | Consumers must migrate to the new column before the deadline                | Hard‑IAT               | Both columns coexist during migration window. Semantic changes require forced migration.                            |
| Table Type Change            | Table modeled incorrectly (e.g., master vs balance, snapshot vs transactional)         | Forced cutover — drop and recreate; no co-existence period                                        | Consumers must migrate at the same time as the producer release             | Hard‑IAT               | Old table is semantically incorrect; parallel co-existence risks continued misuse and must be avoided.              |
| Large‑Scale Structural Change | Multiple breaking changes introduced together                                           | Multi-stage release (saga) with extended migration window; each individual change follows its respective pattern | Consumers may begin adopting early; must complete migration by deadline     | Hard‑IAT               | Requires coordinated rollout, testing window, and firm deadlines due to higher blast radius.                        |

## Additional Governance Rules (Applies to All Scenarios)

- When any new backward-compatibility view version is created, an IAT must already be published announcing retirement of the prior version.
- Maximum two active backward-compatibility versions are supported at any time for any given logical view: current and previous schema shape.
- Consumers unable to migrate immediately may temporarily use the previous version but must commit to a migration deadline.
- DE teams are responsible for retiring deprecated views after the IAT window expires.


## Enforcement

Defining the versioning strategy is only effective if migration deadlines and release pattern compliance can be enforced. Following mechanisms are under consideration; a decision on the enforcement model is can be made before this RFD moves to **accepted** state.

| Mechanism | Description | Effort |
|-----------|-------------|--------|
| **PR review rules / Copilot review** | Automated checks on pull requests that detect schema changes (e.g. column drops, type changes) without a corresponding IAT reference or a Stage 1 additive companion change. Can be implemented as custom GitHub Actions or Copilot review instructions. | Low–Medium |
| **CI gates** | Pipeline jobs that validate schema change PRs against a checklist: IAT published, backward-compat column present, migration deadline set. Blocks merge if criteria are not met. | Medium |
| **Catalogue / data contract enforcement** | Schema contracts registered in a data catalogue (e.g. Unity Catalog, DataHub) with automated drift detection that alerts when a view diverges from its registered contract without a corresponding migration record. | Medium–High |
| **Manual governance** | DE team leads verify IAT publication and stage completion as part of sprint ceremonies. Relies on process discipline rather than automation. | Low (but fragile) |

**Open question for discussion:** Which combination of these mechanisms should be mandated, and who owns tooling? A lightweight starting point would be CI gates on PR merges combined with a required IAT ticket reference in the PR description, with Copilot review rules as a second layer.


## Conclusion
This RFD establishes a clear separation between producer stability and consumer flexibility. By enforcing a single‑version model for curated tables and controlled versioning at the view layer, Caspian enables predictable schema evolution, strong governance, and scalable platform growth.

The recommended approach is **Single Evolving View** model. A single consumer-facing view per dataset evolves continuously, with breaking changes delivered through a multi-stage release (saga) pattern. New or transformed columns are introduced alongside existing ones, allowing early adopters to benefit immediately while others continue unbroken. Once all consumers have migrated within the agreed timeline (determined by the complexity and nature of the change), deprecated column is removed in a cleanup release. Producers are accountable for publishing an IAT and executing each stage on schedule, consumers are accountable for migrating before the deadline.



