# dbt Model YML Generation Prompt

Generate a dbt model YAML file for documentation and DAG configuration.

## Input

Read from source.yml:
- `domain`: Process domain
- `sources[0]`: Source table name
- `target_table`: Target table name
- `target_schema`: Target schema
- `dataset_type`: Master or Balance
- `dc`: DC tag

## Output Structure

```yaml
version: 2

sources:
  - name: cspn_std_{domain}_{{target.name}}
    tables:
      - name: {source_table}

models:
  - name: int_{target_table}
    meta:
      enabled: true
      domain: {domain}
  - name: {target_table}
    meta:
      enabled: true
      domain: {domain}
      dataset_type: {dataset_type}
      table_name: {target_table}
      tags: {'dc': '{dc_tag}'}
      process_schema: {target_schema}
```

## Requirements

1. Define source pointing to standard schema
2. Define integration model metadata
3. Define prepared model metadata with full config
4. Use `{{target.name}}` Jinja syntax in source name

## Example Output

```yaml
version: 2

sources:
  - name: cspn_std_aix_{{target.name}}
    tables:
      - name: aix_index_custom_index_type_association_f1_v1_t1

models:
  - name: int_analyst_index_investment_division_v4
    meta:
      enabled: true
      domain: aix
  - name: analyst_index_investment_division_v4
    meta:
      enabled: true
      domain: aix
      dataset_type: balance
      table_name: analyst_index_investment_division_v4
      tags: {'dc': 'aix'}
      process_schema: cspn_fndn2
```

## File Naming

Save as: `models/{target_table}.yml`

Example: `models/analyst_index_investment_division_v4.yml`

## Validation

- Source name includes domain and target.name variable
- Source table matches the first source from source.yml
- Both integration and prepared models defined
- All meta fields populated correctly
