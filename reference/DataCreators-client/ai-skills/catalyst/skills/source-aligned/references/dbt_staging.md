# Staging dbt Model Generation Prompt

Generate a staging dbt model that selects all columns from the source.

## Input

Read from source.yml:
- `domain`: Process domain
- `sources`: Source table name
- `load_type`: Full or incremental

## Output Structure

```sql
{{
    config(
        schema = "cspn_work2_"|string + target.name,
        meta = { "dataset_load_type" : "{load_type}",
                 "dataset_load_catchup_strategy" : "chronological" }
    )
}}
{% set source_schema_suffix = var("source_schema_suffix") |string %}
{% set source_schema = 'cspn_std_{domain}_'|string + source_schema_suffix  %}

SELECT *
FROM {{ cspn_source(source_schema, '{source_table}' ) }} 
```

## Requirements

1. No transformations - just `SELECT *`
2. Use the `cspn_source` macro to reference source
3. Schema follows pattern: `cspn_work2_` + target.name
4. Set `dataset_load_type` from source.yml `load_type`

## Example Output

For a source with domain=`officerships`, source_table=`officerships`, load_type=`full`:

```sql
{{
    config(
        schema = "cspn_work2_"|string + target.name,
        meta = { "dataset_load_type" : "full",
                 "dataset_load_catchup_strategy" : "chronological" }
    )
}}
{% set source_schema_suffix = var("source_schema_suffix") |string %}
{% set source_schema = 'cspn_std_officerships_'|string + source_schema_suffix  %}

SELECT *
FROM {{ cspn_source(source_schema, 'officerships' ) }} 
```

## File Naming

Save as: `models/staging/stage_{source_table}.sql`

Example: `models/staging/stage_officerships.sql`
