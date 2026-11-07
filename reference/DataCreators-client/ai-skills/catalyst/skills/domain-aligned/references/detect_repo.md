# Detect Repository Type

Determine whether the current foundation repository is **IM** or **MSS**.

## Procedure

1. **Read `dbt_project.yml`** in the repository root.
   - If `name: 'casper_im_foundation'` --> **IM** mode.
   - If `name: 'casper_mss_foundation'` --> **MSS** mode.
   - If neither is found, ask the user to confirm which foundation repo
     they are working in.

2. **Scan existing staging models** in the target `dc_tag` folder.
   - Look for `cspn_source_v2(` usage --> confirms IM.
   - Look for `cspn_source(` or `{{ source(` usage --> confirms MSS.
   - If the dc_tag folder has no existing models, fall back to
     `dbt_project.yml` detection only.

3. **Check directory conventions** for further confirmation:
   - IM: model directories end with `_f` (e.g., `account_daily_results_v4_f/`).
   - MSS: model directories match entity name exactly (e.g., `territory/`).

4. **Check for existing domain-aligned (multi-source) patterns:**
   - Look for integration models with `UNION ALL` in the dc_tag folder.
   - If found, study the UNION pattern, dedup strategy, and column alignment
     conventions used by existing domain-aligned models.
   - These patterns should be replicated in the new model.

5. **Record the following settings** for downstream generation steps:

   | Setting | IM Value | MSS Value |
   |---------|----------|-----------|
   | `repo_type` | `im` | `mss` |
   | `source_macro` | `cspn_source_v2` | `cspn_source` or `source()` |
   | `model_dir_suffix` | `_f` | (none) |
   | `ddl_path` | `database/` | `database/dbt_tables/` |
   | `dag_path` | `dags/` | `dags/<dc_tag>/` |
   | `deequ_path` | `deequ_rules/` | `deequ_rules/<dc_tag>/` |
   | `prepared_schema` | `cspn_fndn2_` | `cspn_fndn2_` or `cspn_cons2_` |
   | `curate_template` | `dbt_emr_critical_v4` | `dbt_emr_small` |

## Output

A set of key-value settings that all subsequent generation prompts will
consume to produce repo-appropriate artifacts.
