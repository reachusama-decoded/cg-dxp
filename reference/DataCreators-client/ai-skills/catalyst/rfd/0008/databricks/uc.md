# DBX-UC: Unity Catalog

Unity Catalog governance: three-part names, ownership, tags, IaC for grants.

## DBX-UC-001 — Three-part names everywhere

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** Always reference tables as `catalog.schema.table`. Never
two-part names (`schema.table`).

**Why.** Two-part names depend on the session's default catalog, which
changes silently across environments.

**Exception.** dbt `ref()` and `source()` macros expand to three-part
names automatically and are the preferred reference style.

**Examples.**
```sql
-- ✓
select * from investments_dev.curated.orders;
select * from {{ ref('fct_orders') }};

-- ✗
select * from curated.orders;
```

## DBX-UC-002 — Catalog assignment follows the data-product registry

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory + CI

**Decision.** A data product's catalog is determined by the data-product
registry (cross-references RFD 0003). Never hardcode catalog names that
deviate from the registry.

**Why.** Catalog naming is governance — products migrating across
environments must follow the registry's mapping.

## DBX-UC-003 — External tables preferred over managed (current posture)

**Severity:** warning
**Since:** v0.1.0
**Linter:** advisory

**Decision.** New Catalyst tables are external tables backed by a UC
external location. Managed tables are not the default today. When
creating a table, set `LOCATION` explicitly.

**Why.** Catalyst data lives in cloud storage already governed by other
tooling (cross-tool query via Athena/Trino, storage-level lifecycle
policies, existing IaC). Managed tables move data into Databricks-managed
storage, which doesn't fit the current architecture. Migration to
managed-by-default is gated on a separate decision (cost analysis +
cross-tool query parity).

**Exception.** Test/sandbox tables may be managed for convenience. UC
volumes for unstructured data follow their own rules (`DBX-UC-007`).

**Examples.**
```sql
-- ✓ external table with explicit location
create table investments_dev.curated.orders
using delta
location 's3://cg-investments-dev/curated/orders/'
as select * from staging;

-- ✗ managed table (not current default)
create table investments_dev.curated.orders
using delta
as select * from staging;
```

**Note on direction.** This rule will be revisited when the cost and
cross-tool query analysis lands. Treat this rule as a current state, not
a permanent architectural commitment.

## DBX-UC-004 — Every UC object has an owner and a comment

**Severity:** error
**Since:** v0.1.0
**Linter:** Terraform validation + CI

**Decision.** Every catalog, schema, table, view, and volume has an
owner (a service principal or group, not an individual) and a `COMMENT`.

**Why.** UC governance starts with knowing who's responsible and what the
object is for. Individual ownership creates bus-factor risk.

**Examples.**
```sql
alter table investments_dev.curated.orders
owner to `data-platform-engineering`;

alter table investments_dev.curated.orders
set comment 'Curated order facts. Grain: order_id. Refreshed daily 2am UTC.';
```

## DBX-UC-005 — UC tags for governance

**Severity:** error
**Since:** v0.1.0
**Linter:** Terraform validation + CI

**Decision.** Tag every table with at minimum:
- `data_classification`: one of `public`, `internal`, `confidential`, `restricted`
- `pii`: `true` or `false`
- `retention_days`: integer or `permanent`
- `data_product`: registry identifier

The full tag schema is governed separately in the data-product registry.

**Why.** Classification drives downstream RLS, masking, and
retention enforcement. Without tags, governance is invisible to query
engines.

**Examples.**
```sql
alter table investments_dev.curated.holdings set tags (
    'data_classification' = 'confidential',
    'pii' = 'true',
    'retention_days' = '2555',
    'data_product' = 'investments-positions'
);
```

## DBX-UC-006 — Storage credentials and external locations in IaC

**Severity:** error
**Since:** v0.1.0
**Linter:** Terraform required

**Decision.** Storage credentials and external locations are created and
managed in Terraform. Never via the Databricks UI or ad-hoc SQL.

**Why.** External locations grant access to cloud storage. Drift between
the UI state and IaC creates audit gaps.

## DBX-UC-007 — Volumes for unstructured data; never DBFS in new code

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Unstructured data (model artifacts, raw files, intermediate
blobs) lives in UC volumes. DBFS is deprecated for governance purposes
and forbidden in new code.

**Why.** UC volumes are governed; DBFS is a workspace-scoped escape hatch
that bypasses UC permissions and audit.

## DBX-UC-008 — Grants managed via Terraform, not SQL

**Severity:** error
**Since:** v0.1.0
**Linter:** Terraform required + CI

**Decision.** All `GRANT`/`REVOKE` statements are managed in Terraform.
Never run grants via ad-hoc SQL or the UI in production.

**Why.** Permissions drift is the most common UC misconfiguration source.
IaC makes the access model auditable and reviewable.

**Exception.** Temporary grants for incident response, with a
documented expiry and a follow-up Terraform PR within 24 hours.

## DBX-UC-009 — Use system schemas for metadata queries

**Severity:** advisory
**Since:** v0.1.0
**Linter:** advisory

**Decision.** Read metadata (lineage, audit, table stats) from
`system.access.audit`, `system.information_schema.*`, and
`system.lineage.*`. Don't write your own audit table when UC has one.

**Why.** UC system schemas are the canonical source. Hand-rolled audit
tables drift from reality.

## DBX-UC-010 — Lakehouse Federation requires security review

**Severity:** error
**Since:** v0.1.0
**Linter:** advisory (process gate)

**Decision.** Foreign catalogs and Lakehouse Federation connections cross
trust boundaries and require a security review before creation.

**Why.** Federated queries can pull data from external systems with
different access controls; the federation creates a new data exfiltration
surface.

### Compute (Clusters and Warehouses)
