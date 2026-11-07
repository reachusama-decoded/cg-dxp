# DQ YML Generation Prompt

Generate a data quality rules YAML file from profiling results.

## Purpose

Create DQ rules that validate data quality during ingestion, focusing on uniqueness checks for primary key columns.

## Input Requirements

- Primary key columns from profiling output
- Process domain and process name from ingestion.yml

## Output Structure

```yaml
model_version: 2
name: {process_name}-dq-rules
description: {process_name} DQ In-Motion Rules
enabled: true
business_unit: casper
process_domain: {process_domain}

meta:
  author: Casper Sapient Team
  version: "1.0"

data_source:
  reader: spark
  load_type: FULL
  params:
    format: parquet
    path: !conf "context.variables.input_path"
    options:
      mergeSchema: true

profiling:
  enabled: True

metrics_key:
  dataset_timestamp_granularity: second

ruleset:
  - description: Critical checks
    level: ERROR
    group: semantic
    rules:
      - type: hasUniqueness
        rule_name: CSPN_Duplication_{process_name}
        params:
          columns: [{primary_key_columns}]
          assert_value: 1.0
          hint: "Uniqueness check on primary key"
```

## Requirements

1. Include **all** primary key columns in a single `hasUniqueness` rule
2. List PKs as a single array, not multiple separate rules
3. Use the primary keys confirmed by user during profiling
4. If no PK candidates were identified, use the combination of columns with highest uniqueness

## Example Output

```yaml
model_version: 2
name: officerships-dq-rules
description: officerships DQ In-Motion Rules
enabled: true
business_unit: casper
process_domain: officerships

meta:
  author: Casper Sapient Team
  version: "1.0"

data_source:
  reader: spark
  load_type: FULL
  params:
    format: parquet
    path: !conf "context.variables.input_path"
    options:
      mergeSchema: true

profiling:
  enabled: True

metrics_key:
  dataset_timestamp_granularity: second

ruleset:
  - description: Critical checks
    level: ERROR
    group: semantic
    rules:
      - type: hasUniqueness
        rule_name: CSPN_Duplication_officerships
        params:
          columns: ["officershipid"]
          assert_value: 1.0
          hint: "Uniqueness check on primary key"
```

## Validation

- Verify primary key columns exist in the source schema
- Ensure all PKs are in a single list, not duplicated rules
- Do not add any extra rules beyond hasUniqueness on PKs
