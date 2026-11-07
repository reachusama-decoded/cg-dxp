# Generate Foundation Model YAML (Domain-Aligned, Multi-Source)

Create the dbt model YAML file that defines sources, model metadata, and tags
for a domain-aligned (multi-source UNION) entity.

## Key Difference from Single-Source (entity-scaffold)

- **Multiple sources** listed in the `sources` block (one per UC table).
- The integration model has the `_union` suffix.
- Staging models are NOT listed in the YAML.

## Template -- IM Foundation (with multiple sources)

```yaml
version: 2

sources:
  - name: cspn_std_<domain_1>_{{target.name}}
    tables:
      - name: <source_table_1>
  - name: cspn_std_<domain_2>_{{target.name}}
    tables:
      - name: <source_table_2>

models:
  - name: int_<entity_name>_union
    meta:
      enabled: true
      domain: <primary_domain>
  - name: <entity_name>
    meta:
      enabled: true
      domain: <primary_domain>
      dataset_type: <master|balance>
      table_name: <entity_name>
      tags: {"dc": "<dc_tag>"}
      process_schema: cspn_fndn2
```

### When Sources Share the Same Domain

If all source tables come from the same domain (e.g., all from `rapid`),
use a single `sources` entry with multiple tables:

```yaml
sources:
  - name: cspn_std_rapid_{{target.name}}
    tables:
      - name: rapid_security_bloomberg_f1_v1_t1
      - name: rapid_security_refinitiv_f1_v1_t1
      - name: rapid_security_msci_f1_v1_t1
```

### When Sources Come from Different Domains

If source tables come from different domains (e.g., `rapid` and `cdm`),
use separate `sources` entries:

```yaml
sources:
  - name: cspn_std_rapid_{{target.name}}
    tables:
      - name: rapid_security_bloomberg_f1_v1_t1
  - name: cspn_std_cdm_{{target.name}}
    tables:
      - name: cdm_security_master_f1_v1_t1
```

## Template -- MSS Foundation

MSS models that use `cspn_source()` or reference consolidated tables may
not need a `sources` block. Check existing model YAMLs in the dc_tag folder.

If MSS models DO use `{{ source() }}`, include a sources block:

```yaml
version: 2

sources:
  - name: cspn_cons2_{{target.name}}
    tables:
      - name: taco_vendor1_data_curr
      - name: taco_vendor2_data_curr

models:
  - name: int_<entity_name>_union
    meta:
      enabled: true
      domain: <primary_domain>
  - name: <entity_name>
    meta:
      enabled: true
      domain: <primary_domain>
      dataset_type: <master|balance>
      table_name: <entity_name>
      tags: {"dc": "<dc_tag>"}
      process_schema: cspn_fndn2
```

If MSS models use `cspn_source()` directly (no `{{ source() }}`), omit the
sources block entirely:

```yaml
version: 2

models:
  - name: int_<entity_name>_union
    meta:
      enabled: true
      domain: <primary_domain>
  - name: <entity_name>
    meta:
      enabled: true
      domain: <primary_domain>
      dataset_type: <master|balance>
      table_name: <entity_name>
      tags: {"dc": "<dc_tag>"}
      process_schema: cspn_fndn2
```

## Key Rules

### Sources

- Include a `sources` block if the staging models use `cspn_source_v2` (IM)
  or `{{ source() }}`.
- The source name follows the pattern `cspn_std_<domain>_{{target.name}}`.
- The table names must exactly match the table names used in each staging
  model's `cspn_source_v2()` or `{{ source() }}` call.
- Group tables by domain schema.

### Models

- List the integration model (`int_<entity_name>_union`) and the prepared
  model (`<entity_name>`).
- Staging models are NOT listed in the YAML.
- Each model entry must have `meta.enabled: true` and `meta.domain`.
- Use the **primary domain** for the domain value -- the most authoritative
  source system.
- The prepared model entry must additionally include:
  - `dataset_type`: `master` or `balance`
  - `table_name`: the entity name
  - `tags`: `{"dc": "<dc_tag>"}`
  - `process_schema`: `cspn_fndn2` (or `cspn_cons2` for MSS consolidated)

### Process Schema

- IM: always `cspn_fndn2`.
- MSS: `cspn_fndn2` for foundation tables, `cspn_cons2` for consolidated
  tables. Check existing model YAMLs in the dc_tag folder.

## File Location

- **IM:** `models/<dc_tag>/<entity_name>_f/<entity_name>.yml`
- **MSS:** `models/<dc_tag>/<entity_name>/<entity_name>.yml`

## Inputs Required

| Input | Description |
|-------|-------------|
| `entity_name` | Target entity name |
| `source_tables` | List of source table names grouped by domain |
| `primary_domain` | The primary source system domain |
| `dc_tag` | Data classification tag |
| `dataset_type` | `master` or `balance` |
| `repo_type` | `im` or `mss` |
