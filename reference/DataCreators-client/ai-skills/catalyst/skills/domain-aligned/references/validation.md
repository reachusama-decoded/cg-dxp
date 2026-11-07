# Validation Criteria — Domain-Aligned dbt Models

Score each generated artifact on a 1–10 scale. The overall score must be **>= 7** to proceed.

## Scoring Rubric

### SQL Syntax (2 points)
- Valid SQL that compiles without errors
- Proper Jinja syntax (`{{ }}`, `{% %}`)
- No unclosed brackets, missing commas, or syntax errors

### Model Architecture (3 points)
- Staging models: one per source, identical column output
- Intermediate model: UNION ALL of all staging models
- Canonical model: surrogate key, bi-temporal columns, incremental merge
- Proper `{{ ref() }}` and `{{ source() }}` usage (no hardcoded table names)

### Column Consistency (2 points)
- All staging models output the same columns in the same order
- Types are consistent across staging models
- Canonical model includes all bi-temporal audit columns
- `dl_row_uid` is correctly generated via `generate_surrogate_key_v3()`

### Configuration (2 points)
- `dbt_project.yml` is valid YAML with correct model paths
- `profiles.yml` uses env_var() for all credentials
- Schema from `env_var('DATABRICKS_DEFAULT_SCHEMA')` — never hardcoded
- Correct materializations: staging=view, intermediate=view, canonical=incremental

### Testing (1 point)
- `schema.yml` defines sources and models
- `not_null` + `unique` on `dl_row_uid`
- `not_null` on natural key columns and `dl_source`

## Feedback Format

```
Score: <N>/10

Issues:
- <issue_1>
- <issue_2>

Recommendations:
- <fix_1>
- <fix_2>
```

If score < 7, return specific feedback for regeneration. Maximum 5 retry attempts.
