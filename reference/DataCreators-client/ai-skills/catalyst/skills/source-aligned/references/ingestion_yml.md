# Ingestion YML Generation Prompt

Generate an ingestion YAML file from data profiling results.

## Prerequisites

Before generating, ensure user has provided:
- **dc_tag**: Data classification tag (e.g., "aix", "ofs", "imap")
- **schedule_info**: Cron expression or "unscheduled"

Before accepting `dc_tag`, confirm against existing ingestion configs in `caspian-pipelines`:
1. Check `workspace/reference/repos/caspian-pipelines/config/dc_tag_list.yml` for valid tags.
2. Search `workspace/reference/repos/caspian-pipelines/dags/ingestion/**` for related files by `process_domain`,
   `process_name`, or similar filename patterns. If a close match exists, reuse its `file_tags.dc`.
3. If no match exists, proceed with the user-provided `dc_tag` and note it was user-supplied.

Helper script (optional):
`python plugins/casper/skills/source-aligned/scripts/find_related_ingestion_configs.py --process-domain <domain> --process-name <name> --file-pattern <pattern>`

If not provided, ask for these values before proceeding.

## Naming Conventions

| Field | Derivation |
|-------|------------|
| `process_domain` | First part of filename (e.g., `aix` from `aix_analyst_index.csv`) |
| `process_name` | Full filename without extension; remove timestamp portions like `_20251027092703` |
| `landing_path` | `{vendor_or_dc_tag}/inbound` (e.g., `blmbrg/inbound` for Bloomberg feeds) |
| `file_pattern` | Original filename |

## Requirements

1. Include **every column** from profiling in the schema section
2. Never truncate or omit columns
3. Set `is_nullable: true` if Null Count > 0, else `false`
4. If original file has `.zip` extension, add `compression: digest_zip` to l2r section
5. For CSV/DAT files without zip, add `skip_fix_encode: true` to r2s section
6. Use comma delimiter for `.csv`, pipe `|` for `.dat`
7. If the source file has a preamble/header block (marker lines, `key=value` metadata, or delimiter-count mismatch), set `header: false` and add `skip_header_rows: <preamble_line_count>` so the data starts immediately after that block.
8. If the source file has a trailer block (marker lines or delimiter-count mismatch), add `skip_footer_rows: <trailing_line_count>`.

## Authoritative Config Options (caspian-ingestion-libs)

Use these options when needed. The authoritative schema is in:
- `casper/orchestration/templates/ingestion/model/__init__.py`
- `docs/PipelineConfigSpec.yml`

**Top-level keys (IngestionTemplateSchema)**
- `consuming_teams` (required)
- `process_domain` (required)
- `process_name` (required)
- `process_type`
- `delivery_sla`
- `enable_cdex`
- `is_paused_upon_creation`
- `replicate_to_azure`
- `replicate_curr_to_azure`
- `trigger_upon_completion`
- `dag_tags`
- `use_deferrable_operator`
- `deferrable_operator_poll_interval`
- `deferrable_operator_logging_interval`
- `deploy_autosys_job`
- `file_tags`
- `owner_details`
- `airflow_defaults`
- `schedule_info`
- `api`
- `database`
- `l2r`
- `r2s`
- `sf2s`
- `pub`
- `preprocess`
- `cg_deequ`

**Landing-to-Raw (`l2r`) options**
- `file_pattern` (required)
- `compression`
- `poke_interval`
- `sensor_timeout`
- `sensor_mode`
- `landing_path` (required)
- `landing_base`
- `delete_from_source`
- `startup_timeout_seconds`
- `file_filter_identifier`
- `file_header`
- `output_file_prefix`
- `find_replace_regex`
- `encoding`
- `dask_blocksize`
- `dask_processes`
- `multiple_files_check`

**Raw-to-Standard (`r2s`) options**
- `file_format` (required: delimited | fixed_width | excel | json | xml | avro | parquet)
- `json_row_tag`
- `json_root_tag`
- `flatten_nested_json`
- `json_key_value_pair`
- `parsed_json_schema_file`
- `json_hierarchy_depth`
- `delimiter`
- `encoding`
- `skip_fix_encode`
- `nullValue`
- `header`
- `inferSchema`
- `escape`
- `comment`
- `quote`
- `timestampFormat`
- `dateFormat`
- `skip_header_rows`
- `skip_footer_rows`
- `concat_rows`
- `skip_preheader_flag`
- `skip_footer_flag`
- `trim_column_cleanup`
- `inflate_file`
- `execution_timeout`
- `find_replace_regex`
- `use_col_range_for_excel`
- `secret_manager_file_password`
- `dataframe_parquet_partitions`
- `read_all_sheets`
- `multiLine`
- `optionalFields`
- `strictNullCheck`
- `startup_timeout_seconds`
- `skip_prefix_filter`
- `header_layout_change`
- `excel_sheet_name`
- `skip_row_number`
- `extra_standard_table_fields`
- `ignoreLeadingWhiteSpace`
- `ignoreTrailingWhiteSpace`
- `allow_zero_byte_file`
- `xml_parser_opts`
- `metadata_extract`
- `schema`
- `schema_file`
- `spark_config`
- `kafka`
- `add_correlation_id`

## Output Structure

```yaml
consuming_teams:
  - cg-open-itg/AA00002933_IMDELIVERY_APPROVERS
process_domain: {process_domain}
process_name: {process_name}
delivery_sla: timedelta(minutes=30)
file_tags:
  dc: {dc_tag}
cg_deequ:
  enable: true
  sns_notification: false
airflow_defaults:
  catchup: false
  depends_on_past: false
  email_on_failure: true
  email_on_retry: true
  owner: airflow
  retries: 3
  retry_delay: timedelta(seconds=30)
  start_date: datetime(2025,1,1,tzinfo=timezone("America/Los_Angeles"))
l2r:
  file_pattern: {file_pattern}
  landing_path: {landing_path}
  sensor_timeout: 36000
  # compression: digest_zip  # Only if .zip file
r2s:
  delimiter: ","  # or "|" for .dat
  file_format: delimited
  header: true
  escape: '"'
  quote: '"'
  multiLine: true
  skip_fix_encode: true  # Only for non-zip files
  schema:
    - alias: {column_alias}
      data_type: {data_type}
      field_name: {original_column_name}
      is_nullable: {true|false}
      metadata:
        data_concept: unknown
        is_sensitive: true
      seq: {sequence_number}  # Increment by 5: 5, 10, 15...
```

## Schedule Info Requirements

**Always include schedule_info section with:**
- `cron`: Cron expression for schedule (e.g., "0 9 * * mon,tue,wed,thu,fri")
- `days_of_week`: Abbreviated days (e.g., "mo,tu,we,th,fr" for weekdays, "su,mo,tu,we,th,fr,sa" for daily)
- `exclude_calendar`: Use "global_holidays" for business day schedules, "None" for 24/7
- `run_calendar`: Usually "None" unless specific calendar required

**Common patterns:**
- Weekday business hours: `cron: 0 9 * * mon,tue,wed,thu,fri`, `exclude_calendar: global_holidays`
- Daily: `cron: 0 1 * * sun,mon,tue,wed,thu,fri,sat`, `exclude_calendar: None`
- Event-driven (no schedule): `cron: null`, set `event_driven: true`

## Schema Field Rules

For each column from profiling:

| Field | Value |
|-------|-------|
| `alias` | Column name in lowercase, special chars replaced (`%`→`pct`, `#`→`num`, `$`→`amt`, `&`→`and`, `@`→`at`, `+`→`plus`, `/`→`per`, `>`→`gt`, `<`→`lt`, `=`→`eq`), remaining non-alphanumeric→`_`, leading digit prefixed with `n`, duplicates suffixed `_2`, `_3`, … |
| `data_type` | From profiling Data Type column |
| `field_name` | Original column name exactly as in file |
| `is_nullable` | `true` if Null Count > 0 |
| `seq` | Start at 5, increment by 5 |

## Example Output

```yaml
consuming_teams:
  - cg-open-itg/AA00002933_IMDELIVERY_APPROVERS
process_domain: officerships
process_name: officerships
delivery_sla: timedelta(minutes=30)
file_tags:
  dc: ofs
cg_deequ:
  enable: true
  sns_notification: false
airflow_defaults:
  catchup: false
  depends_on_past: false
  email_on_failure: true
  email_on_retry: true
  owner: airflow
  retries: 3
  retry_delay: timedelta(seconds=30)
  start_date: datetime(2025,1,1,tzinfo=timezone("America/Los_Angeles"))
schedule_info:
  cron: 0 9 * * mon,tue,wed,thu,fri
  days_of_week: mo,tu,we,th,fr
  exclude_calendar: global_holidays
  run_calendar: None
l2r:
  file_pattern: Officerships[_a-zA-Z0-9]*.csv
  landing_path: officerships/inbound
  sensor_timeout: 36000
r2s:
  delimiter: ","
  file_format: delimited
  header: true
  escape: '"'
  quote: '"'
  multiLine: true
  skip_fix_encode: true
  schema:
    - alias: officershipid
      data_type: string
      field_name: OfficershipID
      is_nullable: false
      metadata:
        data_concept: unknown
        is_sensitive: true
      seq: 5
    - alias: initials
      data_type: string
      field_name: Initials
      is_nullable: false
      metadata:
        data_concept: unknown
        is_sensitive: true
      seq: 10
    - alias: startdate
      data_type: date
      field_name: StartDate
      is_nullable: false
      metadata:
        data_concept: unknown
        is_sensitive: true
      seq: 65
```

## Validation

Before finalizing:
- Verify all columns from profiling are included
- Confirm column count matches profiling output
- Check nullable flags match null counts
- There may be special schedules and holidays to ignore.  Check existing ingestion yamls and suggest likely candidates based on other files coming from the same source or process domain.
