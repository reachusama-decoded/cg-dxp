# DDL Generation Prompt

Generate CREATE TABLE DDL from source.yml.

## Input

Read from source.yml:
- `target_table`: Table name
- `target_schema`: Schema name (default: `cspn_fndn2`)
- `dataset_type`: Master or Balance (determines audit columns)
- `columns`: List of columns with target_name and target_data_type

## Audit Columns

Include audit columns based on dataset type:

### Master Dataset Audit Columns
```sql
dl_row_uid string,
dl_checksum_value string,
dl_business_start_date date,
dl_business_end_date date,
dl_system_start_timestamp timestamp,
dl_system_end_timestamp timestamp,
dl_current_indicator string,
dl_last_update_process_id string,
dl_source_system_code string
```

### Balance Dataset Audit Columns
```sql
dl_row_uid string,
dl_checksum_value string,
dl_system_start_timestamp timestamp,
dl_system_end_timestamp timestamp,
dl_current_indicator string,
dl_last_update_process_id string,
dl_source_system_code string
```

**Note:** Balance does NOT have `dl_business_start_date` and `dl_business_end_date`.

## Output Structure

```sql
DROP TABLE IF EXISTS {target_schema}_{env}.{target_table};

CREATE EXTERNAL TABLE IF NOT EXISTS {target_schema}_{env}.{target_table} (
    {column_name} {data_type},
    ... all columns from source.yml ...
    {audit_columns}
)
USING delta
PARTITIONED BY (dl_current_indicator)
LOCATION 's3://datalake-curated-{env}-us-east-1/{target_schema}/{target_table}'
TBLPROPERTIES ('table_type'='DELTA');
```

## Requirements

1. Include **all** columns from source.yml
2. Use `target_data_type` exactly as specified
3. Add appropriate audit columns based on dataset_type
4. Partition by `dl_current_indicator` for both Master and Balance
5. Use `{env}` placeholder for environment name

## Example Output - Balance Dataset

```sql
DROP TABLE IF EXISTS cspn_fndn2_{env}.analyst_index_member_v4;

CREATE EXTERNAL TABLE IF NOT EXISTS cspn_fndn2_{env}.analyst_index_member_v4 (
    index_member_uid bigint,
    index_uid bigint,
    constituent_by_index_data_source_uid bigint,
    member_end_date date,
    member_start_date date,
    created_by_initial string,
    created_date date,
    modified_by_initial string,
    modified_date date,
    dl_row_uid string,
    dl_checksum_value string,
    dl_system_start_timestamp timestamp,
    dl_system_end_timestamp timestamp,
    dl_current_indicator string,
    dl_last_update_process_id string,
    dl_source_system_code string
)
USING delta
PARTITIONED BY (dl_current_indicator)
LOCATION 's3://datalake-curated-{env}-us-east-1/cspn_fndn2/analyst_index_member_v4'
TBLPROPERTIES ('table_type'='DELTA');
```

## Example Output - Master Dataset

```sql
DROP TABLE IF EXISTS cspn_fndn2_{env}.custom_index_type_v4;

CREATE EXTERNAL TABLE IF NOT EXISTS cspn_fndn2_{env}.custom_index_type_v4 (
    custom_index_type_id bigint,
    custom_index_type_name string,
    research_company_name string,
    custom_index_type_description string,
    inactive_date date,
    created_by_name string,
    created_date date,
    modified_by_name string,
    modified_date date,
    dl_row_uid string,
    dl_checksum_value string,
    dl_business_start_date date,
    dl_business_end_date date,
    dl_system_start_timestamp timestamp,
    dl_system_end_timestamp timestamp,
    dl_current_indicator string,
    dl_last_update_process_id string,
    dl_source_system_code string
)
USING delta
PARTITIONED BY (dl_current_indicator)
LOCATION 's3://datalake-curated-{env}-us-east-1/cspn_fndn2/custom_index_type_v4'
TBLPROPERTIES ('table_type'='DELTA');
```

## Validation

- All columns from source.yml are present
- Correct audit columns for dataset type
- Valid Delta table syntax
- Proper S3 location format
