# Delta table standards

Three sources combined: **RFD 0008 `databricks/delta.md`** (authoritative for Capital Group), **Capital Group operational decisions** (external-for-DR, UniForm-on, time-travel tuning), and **Databricks's published Delta best practices**.

When a rule has an RFD 0008 ID, cite it via `metadata.standards: [...]` in the skill emitting the table. When it doesn't, document under "Capital Group standard" or "Databricks-recommended" below.

## Capital Group-specific (load-bearing decisions)

### External tables for DR — NOT managed tables

**Decision.** All curated Capital Group tables in App Catalog and Domain Catalog are **External Tables** with storage paths in S3/ADLS controlled by the team. Managed tables are NOT the default.

**Why.** External tables let DR be implemented via storage replication (S3 CRR, ADLS GRS). Managed tables put data in Databricks-managed locations which are harder to recover and replicate to a secondary region.

**How.** Always use `LOCATION '<s3-or-adls-path>'` (or `EXTERNAL VOLUME` for Unity Catalog Volumes). In dbt:

```sql
{{ config(
    materialized='incremental',
    file_format='delta',
    location_root='s3://my-bucket/data_products/<product>/<dataset>/',
) }}
```

Or use the `external_location` table property if available in your dbt-databricks adapter version.

**Future direction.** This standard will flip to **managed tables** once Databricks ships native DR for managed tables (region-failover within UC). Until then, external + storage replication is the only path that meets Capital Group's recovery requirements. Track Databricks UC managed-table DR release in OQ-3 (compute migration); managed-table DR is a related but distinct unlock — open a follow-on OQ when the Databricks roadmap publishes a date.

### UniForm enabled for Iceberg compatibility

**Decision.** All new tables enable Delta UniForm (`delta.universalFormat.enabledFormats = 'iceberg'`).

**Why.** Allows consumers using Iceberg-native tools (Trino, Snowflake-via-Iceberg, AWS Athena Iceberg engine) to read Capital Group Delta tables without copying or migration. Single source of truth, multiple readers.

**How.** In dbt model config or `dbt_project.yml`:

```yaml
+tblproperties:
  delta.universalFormat.enabledFormats: 'iceberg'
  delta.enableIcebergCompatV2: 'true'
```

Or post_hook: `ALTER TABLE {{ this }} SET TBLPROPERTIES ('delta.universalFormat.enabledFormats' = 'iceberg')`.

### Time-travel retention — **35 days** to align with Capital Group backup standard

**Capital Group requirement.** Enterprise backup standard is **35 days** retention. All Catalyst Delta tables MUST match this for time-travel by setting **both** properties explicitly at 35 days by default:

```yaml
+tblproperties:
  delta.logRetentionDuration: 'interval 35 days'
  delta.deletedFileRetentionDuration: 'interval 35 days'
```

This is a **load-bearing org standard**, not a soft default — going below 35 days requires a documented compliance exception.

**Why explicit, not Databricks's 7-day default for `deletedFileRetentionDuration`?**
- 7 days is too short and conflicts with the 35-day backup standard.
- Time-travel must be set BEFORE you need it — once VACUUM runs at default retention, those versions are gone. Recovery is not retroactive.
- Setting explicitly makes the SLA discoverable in the code (teams can see "we have 35 days" without consulting Databricks docs or memory of an org standard).

**Why `delta.deletedFileRetentionDuration` MUST match `delta.logRetentionDuration`.** VACUUM removes files at `deletedFileRetentionDuration`. Once those files are gone, time-travel to that version fails even if the log history still exists. Setting only `logRetentionDuration` is a footgun.

**Per-product override (upward only).** If the data contract's SLA or compliance requirement demands **longer than 35 days** (regulatory hold, multi-year audit window), override per-product in `dbt_project.yml`:

```yaml
# Per-product override (in dbt_project.yml under that product's models block):
models:
  <product>:
    +tblproperties:
      delta.logRetentionDuration: 'interval 90 days'
      delta.deletedFileRetentionDuration: 'interval 90 days'
```

**Going below 35 days requires a documented compliance exception** referencing the CG backup standard and approved by data governance. Do not silently shorten retention even for high-churn tables — instead document the cost trade-off in the data contract and seek the exception.

**Trade-off.** Storage cost grows roughly linearly with retention window for tables with non-trivial DELETE/UPDATE/MERGE churn (each file rewrite leaves the old file retained). The 35-day cost is accepted as the org standard.

## RFD 0008 DBX-DELTA rules (authoritative)

| Rule | Decision (one line) |
|---|---|
| **DBX-DELTA-001** | Curated tables use Delta format (`file_format='delta'`) |
| **DBX-DELTA-002** | Liquid clustering for new managed tables; Z-ORDER on legacy. For external tables: same — liquid clustering preferred |
| **DBX-DELTA-003** | `VACUUM` retention >= 7 days (the Databricks default; never reduce below this) |
| **DBX-DELTA-004** | `OPTIMIZE` via predictive optimization (UC managed) where available; manual OPTIMIZE on a cadence otherwise |
| **DBX-DELTA-005** | Change Data Feed (`delta.enableChangeDataFeed = true`) on tables consumed downstream by streaming or incremental consumers |
| **DBX-DELTA-006** | Schema evolution is explicit (`ALTER TABLE ... ADD/RENAME/DROP COLUMN`); never rely on implicit schema-merge |
| **DBX-DELTA-007** | `CHECK` constraints for invariants; `PRIMARY KEY` is advisory in Delta (not enforced) |
| **DBX-DELTA-008** | Time-travel readers pin to version or timestamp (`VERSION AS OF` / `TIMESTAMP AS OF`); never assume "latest minus N" |
| **DBX-DELTA-009** | `DEEP CLONE` for backups (and for the App→Domain publish per catalog-architecture.md); `SHALLOW CLONE` for tests only |

## Databricks docs additions (not in RFD 0008)

| Topic | Recommendation | dbt config / property |
|---|---|---|
| **Predictive optimization** | Enable on UC managed tables; skip on external (not supported on external as of 2026-05) | (account-level setting; not per-table) |
| **CREATE OR REPLACE vs DROP+CREATE** | Always `CREATE OR REPLACE` — preserves protocol version, table properties, and Volume location | dbt's `--full-refresh` does the right thing |
| **Remove legacy Delta configs on Runtime upgrade** | When bumping Databricks Runtime, drop deprecated `delta.*` properties (e.g., `delta.compatibility.symlinkFormatManifest.enabled` if on a recent runtime) | review on Runtime bumps |
| **No Spark caching with Delta** | `df.cache()` against a Delta source can serve stale data after writes — don't | n/a (developer hygiene) |
| **Never manually edit Parquet files** | Direct file ops break the transaction log; use `MERGE` / `DELETE` / `UPDATE` SQL only | n/a |
| **Partition constraint in MERGE** | Add a `WHEN MATCHED AND <partition-filter>` clause to reduce search space | author MERGE source with partition filter |
| **Compact before MERGE** | Run `OPTIMIZE` before a heavy MERGE to reduce small-file shuffle | post-hook between dbt models if needed |
| **Optimized writes for partitioned tables** | `delta.autoOptimize.optimizeWrite = true` reduces small files on write | `+tblproperties: { delta.autoOptimize.optimizeWrite: 'true' }` |
| **Low Shuffle Merge** | `spark.databricks.delta.merge.enableLowShuffle = true` — faster MERGE on large tables | profile-level Spark conf in `profiles.yml` for the warehouse |
| **File size tuning for rewrite-heavy** | `delta.tuneFileSizesForRewrites = true` for MERGE-heavy workloads (smaller files = less rewrite cost) | `+tblproperties: { delta.tuneFileSizesForRewrites: 'true' }` |
| **Target file size** | Default is auto (Databricks tunes by table size); override only if you have a measured reason | `+tblproperties: { delta.targetFileSize: '256mb' }` |

## Other operationally-relevant settings

| Setting | When to use | Default we set |
|---|---|---|
| `delta.columnMapping.mode = 'name'` | Required for column rename / drop / type widening operations. Bumps reader version. | **Enable by default** on all new tables — cheap, future-proofs schema evolution |
| `delta.enableDeletionVectors = true` | Faster DELETE / UPDATE / MERGE (~10x on large tables). Bumps reader version to 3. | **Enable by default** on App Catalog tables; Domain Catalog inherits via Deep Clone |
| GENERATED columns | Computed partition / cluster keys, e.g., `date_partition GENERATED ALWAYS AS (CAST(event_ts AS DATE))` | Use freely for partition columns; document in schema.yml |
| IDENTITY columns | Surrogate keys: `id BIGINT GENERATED ALWAYS AS IDENTITY` | Use when no natural surrogate exists; document as PK |
| `delta.minReaderVersion` / `delta.minWriterVersion` | Set implicitly by features enabled (column mapping, deletion vectors, etc.). Bump readers/writers across the org before enabling features. | Auto-managed — don't set manually |
| `delta.checkpointInterval` | Lower for high-write tables (default 10 commits). Higher writes a checkpoint less often. | Leave default unless commit volume is very high |
| `delta.dataSkippingNumIndexedCols` | First N columns get stats for data skipping (default 32). For very wide tables (200+ cols), increase. | Default — increase only if profile shows skipping is missing |

## Default dbt `+tblproperties:` block for new Catalyst tables

Apply via `dbt_project.yml` model defaults:

```yaml
models:
  <project_name>:
    +materialized: incremental
    +file_format: delta
    +tblproperties:
      delta.universalFormat.enabledFormats: 'iceberg'          # UniForm
      delta.enableIcebergCompatV2: 'true'
      delta.columnMapping.mode: 'name'                          # schema evolution
      delta.enableDeletionVectors: 'true'                       # fast DELETE/UPDATE/MERGE
      delta.autoOptimize.optimizeWrite: 'true'                  # small-file mgmt
      delta.tuneFileSizesForRewrites: 'true'                    # MERGE-friendly file sizes
      delta.logRetentionDuration: 'interval 35 days'            # CG backup standard: 35 days
      delta.deletedFileRetentionDuration: 'interval 35 days'    # MUST match logRetention — VACUUM honors this
      # delta.enableChangeDataFeed: 'true'                       # uncomment when downstream consumers stream/CDC
```

Per-table overrides go in the model's `{{ config(...) }}` block.

## How skills consume this

- `/setup-dbt-project` includes the default `+tblproperties:` block in `dbt_project.yml` for the team's products.
- `/source-aligned`, `/domain-aligned`, `/consumer-aligned` reference this doc when picking per-model overrides (CDC on / time-travel longer).
- `/dbt-best-practices` cites the relevant DBX-DELTA-* rule IDs when emitting guidance.
- `/dplc-publish` (Phase 6, separate work) reads `delta.universalFormat.*` and Deep Clone behavior from here when emitting the publish SQL.
