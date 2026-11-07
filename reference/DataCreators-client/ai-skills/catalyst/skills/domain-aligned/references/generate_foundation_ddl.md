# Generate Foundation DDL (Domain-Aligned)

Create the Hive/Spark DDL script for the prepared table in the curated zone.

## Template

```sql
DROP TABLE IF EXISTS <prepared_schema>{env}.<entity_name>
;
CREATE EXTERNAL TABLE IF NOT EXISTS <prepared_schema>{env}.<entity_name> (
  <column_definitions>,
  dl_source string,
  dl_bus_as_of_date date,
  dl_effective_date date,
  dl_last_update_timestamp timestamp,
  dl_load_timestamp timestamp,
  dl_last_update_process_id string,
  dl_source_system_code string)
PARTITIONED BY (
  <partition_column>)
ROW FORMAT SERDE
  'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
STORED AS INPUTFORMAT
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat'
LOCATION
  's3a://datalake-curated-'+{env}+'-us-east-1/<prepared_schema_short>/<entity_name>'
;
```

## Key Difference from Single-Source

- Include `dl_source string` in the column definitions to preserve the
  vendor/source provenance from the UNION integration layer.

## Partition Column

- **Balance datasets:** `partitiondate string`
- **Master datasets with bitemporal:** `dl_current_indicator string`

## Column Type Mapping

Map source column types to Hive types:

| Source Type | Hive Type |
|-------------|-----------|
| string, varchar | string |
| int, integer | int |
| bigint, long | bigint |
| float | float |
| double | double |
| decimal(p,s) | decimal(p,s) |
| date | date |
| timestamp, datetime | timestamp |
| boolean | string (stored as Y/N) |

## Audit Columns

Always include these audit columns at the end of the column list, before
the partition column:

| Column | Type | Description |
|--------|------|-------------|
| `dl_source` | string | Source vendor/system identifier (from UNION staging) |
| `dl_bus_as_of_date` | date | Business as-of date (bitemporal) |
| `dl_effective_date` | date | Effective date (bitemporal) |
| `dl_last_update_timestamp` | timestamp | Last update timestamp |
| `dl_load_timestamp` | timestamp | Load timestamp |
| `dl_last_update_process_id` | string | Process ID of last update |
| `dl_source_system_code` | string | Source system domain code |

For bitemporal tables, additional columns may include:
- `dl_row_uid` (string) -- surrogate key
- `dl_checksum_value` (string) -- row checksum
- `dl_system_start_timestamp` (timestamp)
- `dl_system_end_timestamp` (timestamp)

Check existing DDL files in the `database/` directory for the exact audit
column set used in this repo.

## Schema Prefix

- **IM:** `cspn_fndn2_` and S3 path uses `cspn_fndn2`
- **MSS:** `cspn_fndn2_` or `cspn_cons2_` and S3 path matches

## File Location

- **IM:** `database/<entity_name>.sql`
- **MSS:** `database/dbt_tables/<entity_name>.sql`

## Inputs Required

| Input | Description |
|-------|-------------|
| `entity_name` | Target entity name |
| `column_definitions` | Column name and type pairs (all business cols + dl_source) |
| `dataset_type` | `master` or `balance` (determines partition column) |
| `prepared_schema` | `cspn_fndn2_` or `cspn_cons2_` |
| `repo_type` | `im` or `mss` |
