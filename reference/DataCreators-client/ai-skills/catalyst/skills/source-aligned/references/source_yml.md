# Source YML Generation Prompt

Generate a source-to-target mapping YAML from ingestion.yml and dq.yml.

## Prerequisites

Before generating:
1. **Determine dataset type:**
   - **Master**: No date field in primary key
   - **Balance**: Has date field in primary key

2. **Ask user to confirm** dataset type with reasoning

3. **If Balance**, ask user for `as_of_col` (business date column name). Do NOT assume.

## Naming Conventions

| Field | Derivation |
|-------|------------|
| `target_table` | Process name + `_v4`, removing `f1_v1_t1` suffix if present |
| `target_schema` | Default to `cspn_fndn2` |
| `source schema` | `cspn_std_{domain}` |

**Examples:**
- `imap_active_transaction_types_f1_v1_t1` → `active_transaction_types_v4`
- `currency_evolve` → `currency_evolve_v4`

## Output Structure

```yaml
dataset_type: {master|balance}
dc: {dc_tag}
domain: {process_domain}
sources:
  - {source_table}:
      table_type: file
      schema: cspn_std_{domain}
target_table: {target_table}
target_schema: cspn_fndn2
dag:
  dependencies:
    - ingestion-{domain}-{process_name}
  run_calendar: global_holidays
  schedule_interval: {schedule_with_30_min_added}
pipeline:
  type: emr
  scale: critical
prompt: 1 to 1 Load data from source file. It depends on {process_name} ingestion file.
load_type: full
as_of_col: {as_of_col}  # Required for balance, blank for master
columns:
  - {column_name}:
      source_name: {alias_from_ingestion}
      source_data_type: {data_type}
      target_name: {column_name_snake_case}
      target_data_type: {data_type}
      source_table: {process_name}
      target_table: {target_table}
      prompt: 1:1 load
      surrogate_key: {Y|N}  # Y if in primary key
```

## Column Mapping Rules

For each column from ingestion.yml schema:

| Field | Value |
|-------|-------|
| `source_name` | The `alias` from ingestion.yml |
| `source_data_type` | The `data_type` from ingestion.yml |
| `target_name` | Convert CamelCase to snake_case |
| `target_data_type` | Same as source unless user specifies different |
| `surrogate_key` | `Y` if column is in primary key list, else `N` |

## Schedule Interval

Add 30 minutes to the cron schedule from ingestion.yml:
- Input: `0 21 * * 1-5` → Output: `30 21 * * 1-5`
- If unscheduled: `null`

## Example Output

```yaml
dataset_type: master
dc: currency
domain: currency
sources:
  - currency_evolve:
      table_type: file
      schema: cspn_std_currency
target_table: currency_evolve_v4
target_schema: cspn_fndn2
dag:
  dependencies:
    - ingestion-currency-currency_evolve
  run_calendar: global_holidays
  schedule_interval: null
pipeline:
  type: emr
  scale: critical
prompt: 1 to 1 Load data from source file. It depends on currency_evolve ingestion file.
load_type: full
as_of_col:
columns:
  - currencyuid:
      source_name: currencyuid
      source_data_type: string
      target_name: currencyuid
      target_data_type: string
      source_table: currency_evolve
      target_table: currency_evolve_v4
      prompt: 1:1 load
      surrogate_key: Y
  - currencyname:
      source_name: currencyname
      source_data_type: string
      target_name: currencyname
      target_data_type: string
      source_table: currency_evolve
      target_table: currency_evolve_v4
      prompt: 1:1 load
      surrogate_key: N
  - effectivefromdate:
      source_name: effectivefromdate
      source_data_type: date
      target_name: effectivefromdate
      target_data_type: date
      source_table: currency_evolve
      target_table: currency_evolve_v4
      prompt: 1:1 load
      surrogate_key: N
```

## Human-in-the-Loop

**Before generating, ask:**

1. "Based on the primary keys [{pk_list}], I identified this as a **{Master|Balance}** dataset because {reasoning}. Is this correct?"

2. If Balance: "Please provide the `as_of_col` (business date column) name."

## Validation

- All columns from ingestion.yml must be present
- Column count must match
- Surrogate keys must match confirmed PKs
- as_of_col must be provided for Balance datasets
