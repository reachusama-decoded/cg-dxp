# DBX-DELTA: Delta Lake

Delta Lake operations: format, clustering, vacuum, schema evolution, time travel.

## DBX-DELTA-001 — Curated tables use Delta format

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Tables in the curated layer (intermediate, fact, dimension,
report) use Delta format. Set `file_format='delta'` in dbt configs;
`USING DELTA` in raw DDL.

**Why.** ACID transactions, time travel, schema enforcement, and CDF are
non-negotiable for governed data products. Parquet-only and CSV are
acceptable only at the raw landing layer.

**Exception.** None for curated. Raw landing zones may use the source's
native format.

## DBX-DELTA-002 — Liquid clustering for new managed tables; Z-ORDER on legacy

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** New tables use liquid clustering (`CLUSTER BY (col1, col2)`).
Existing tables on Z-ORDER continue to use Z-ORDER until migration.

**Why.** Liquid clustering is the strict-better successor — incremental,
no rewrite, no maximum-column ceiling. Z-ORDER remains supported and
appropriate for tables already optimized for it.

**Exception.** External Parquet tables (which can't use either feature).

## DBX-DELTA-003 — `VACUUM` retention >= 7 days

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + audit

**Decision.** Never override `delta.deletedFileRetentionDuration` below 168
hours (7 days) without an RFD.

**Why.** Lower retention breaks time-travel safety: any reader using a
snapshot older than the retention sees missing files. 7 days is the
documented Databricks-recommended minimum. See
<https://docs.databricks.com/aws/en/sql/language-manual/delta-vacuum>.

**Exception.** Test/development tables that are explicitly marked
non-production via UC tag (`environment=dev`).

## DBX-DELTA-004 — `OPTIMIZE` via predictive optimization where available

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Enable predictive optimization (`auto-optimize`,
`auto-compact`) on UC-managed Delta tables. For tables outside UC or on
older runtimes, schedule `OPTIMIZE` manually as a Workflow task.

**Why.** Predictive optimization reduces small-file proliferation without
manual scheduling. Manual `OPTIMIZE` is the fallback, not the default.

## DBX-DELTA-005 — Change Data Feed enabled on tables consumed downstream

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Enable `delta.enableChangeDataFeed = true` on tables that
downstream pipelines read incrementally. Document downstream consumers in
the schema YAML description.

**Why.** CDF gives downstream consumers a deterministic incremental read
without per-table watermark logic. Without CDF, downstream pipelines
re-implement watermarking inconsistently.

**Exception.** Terminal/leaf tables with no downstream consumers.

## DBX-DELTA-006 — Schema evolution is explicit

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Schema changes use `mergeSchema=true` on writes or dbt's
`on_schema_change` config. Never silent column add via permissive ingest.

**Why.** Silent schema evolution means a producer change can break a
consumer without anyone noticing until query failure.

**Examples.**
```sql
{{
    config(
        materialized='incremental',
        unique_key='event_id',
        incremental_strategy='merge',
        on_schema_change='append_new_columns',
    )
}}
```

## DBX-DELTA-007 — `CHECK` constraints for invariants; `PRIMARY KEY` advisory

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Use `CHECK` constraints for column-level invariants (range,
non-null, format). Declare `PRIMARY KEY` even though Delta enforces it
informationally — UC and downstream tools (BI, Federation) read the
declaration.

**Examples.**
```sql
ALTER TABLE catalog.schema.orders
ADD CONSTRAINT amount_non_negative CHECK (amount >= 0);

ALTER TABLE catalog.schema.orders
ADD CONSTRAINT pk_orders PRIMARY KEY (order_id);
```

## DBX-DELTA-008 — Time-travel readers pin to version or timestamp

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Tests, reproducibility checks, and audit queries pin to a
specific version (`VERSION AS OF`) or timestamp (`TIMESTAMP AS OF`).
Never read "latest" in a context that needs determinism.

**Why.** Without a pin, the same query returns different results across
runs as the table evolves.

**Exception.** Production reads of fresh data (the common case).

**Examples.**
```sql
-- ✓ deterministic
select * from catalog.schema.orders version as of 1234;
select * from catalog.schema.orders timestamp as of '2026-04-01T00:00:00Z';

-- ✗ non-deterministic in tests
select * from catalog.schema.orders;
```

## DBX-DELTA-009 — `DEEP CLONE` for backups; `SHALLOW CLONE` for tests only

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Production backups and cross-region copies use `DEEP CLONE`.
`SHALLOW CLONE` is acceptable only for ephemeral test fixtures.

**Why.** Shallow clones share data files with the source. When the source
is `VACUUM`ed, shallow clones break.

### Unity Catalog
