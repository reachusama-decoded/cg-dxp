"""Generate dbt models for a domain-aligned canonical data product.

Reads a model specification YAML and produces:
  - Staging models (one per source table)
  - Intermediate UNION ALL model
  - Canonical model with surrogate key and bi-temporal columns
  - schema.yml with source definitions and tests
  - dbt_project.yml and profiles.yml

Usage:
    python generate_domain_dbt.py \
        --model-spec <path/to/model.yaml> \
        --output-dir <path/to/dbt/> \
        [--templates-dir <path/to/templates/>]
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from textwrap import dedent

import yaml

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_model_spec(spec_path: Path) -> dict:
    """Load and validate the model specification YAML."""
    with open(spec_path, encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    required_keys = ["model_name", "sources", "columns"]
    missing = [k for k in required_keys if k not in spec]
    if missing:
        print(f"error: model spec missing required keys: {missing}", file=sys.stderr)
        sys.exit(1)

    return spec


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------


def generate_staging_model(
    vendor: str,
    entity: str,
    source_name: str,
    table_name: str,
    columns: list[dict],
    column_mappings: dict[str, str] | None = None,
) -> str:
    """Generate a staging model SQL string for one source table."""
    mappings = column_mappings or {}
    col_lines = []
    for col in columns:
        canon_name = col["name"]
        src_name = mappings.get(canon_name, canon_name)
        col_type = col.get("type", "STRING")
        if src_name != canon_name:
            col_lines.append(f"    CAST({src_name} AS {col_type}) AS {canon_name}")
        else:
            col_lines.append(f"    CAST({canon_name} AS {col_type}) AS {canon_name}")

    col_lines.append(f"    '{vendor}' AS dl_source")
    col_lines.append("    CURRENT_TIMESTAMP() AS dl_system_from_date")

    select_body = ",
".join(col_lines)

    return dedent(f"""\
        {{{{ config(materialized='view') }}}}

        {{# Staging model for {vendor} {entity} data #}}

        SELECT
        {select_body}
        FROM {{{{ source('{source_name}', '{table_name}') }}}}
    """).strip() + "
"


def generate_intermediate_model(
    model_name: str,
    staging_refs: list[str],
) -> str:
    """Generate the UNION ALL intermediate model."""
    unions = "
UNION ALL
".join(
        f"SELECT * FROM {{{{ ref('{ref}') }}}}" for ref in staging_refs
    )

    return dedent(f"""\
        {{{{ config(materialized='view') }}}}

        {{# Union of all source staging models for {model_name} #}}

        {unions}
    """).strip() + "
"


def generate_canonical_model(
    model_name: str,
    int_ref: str,
    natural_key_cols: list[str],
    business_cols: list[str],
    load_type: str = "master",
) -> str:
    """Generate the final canonical model with surrogate key and bi-temporal cols."""
    sk_cols = ", ".join(f"'{c}'" for c in natural_key_cols)
    checksum_parts = ",
            ".join(
        f"COALESCE(CAST({c} AS STRING), '')" for c in business_cols
    )
    business_select = ",
        ".join(business_cols)

    return dedent(f"""\
        {{{{
          config(
            materialized='incremental',
            unique_key='dl_row_uid',
            incremental_strategy='merge',
            schema=env_var('DATABRICKS_DEFAULT_SCHEMA'),
            file_format='delta',
            meta={{{{
              'surrogate_key_cols': [{sk_cols}],
              'load_type': '{load_type}'
            }}}})
        }}}}

        WITH source_data AS (
            SELECT * FROM {{{{ ref('{int_ref}') }}}}
        ),

        enriched AS (
            SELECT
                {{{{ generate_surrogate_key_v3([{sk_cols}]) }}}} AS dl_row_uid,
                {business_select},
                dl_source,
                CURRENT_TIMESTAMP() AS dl_business_from_date,
                CAST('9999-12-31' AS TIMESTAMP) AS dl_business_to_date,
                dl_system_from_date,
                CAST(NULL AS TIMESTAMP) AS dl_system_to_date,
                TRUE AS is_current,
                MD5(CONCAT_WS('||',
                    {checksum_parts}
                )) AS checksum
            FROM source_data
        )

        SELECT * FROM enriched

        {{% if is_incremental() %}}
        WHERE dl_system_from_date > (SELECT MAX(dl_system_from_date) FROM {{{{ this }}}})
        {{% endif %}}
    """).strip() + "
"


def generate_schema_yml(
    model_name: str,
    sources: list[dict],
    staging_refs: list[str],
    int_ref: str,
    columns: list[dict],
    natural_key_cols: list[str],
) -> str:
    """Generate schema.yml with sources, models, and tests."""
    source_tables = []
    for src in sources:
        source_tables.append(
            {
                "name": src["table"],
                "description": f"{src.get('vendor', 'unknown')} source for {model_name}",
            }
        )

    # Use first source's catalog/schema as default (env_var in real dbt)
    source_def = {
        "version": 2,
        "sources": [
            {
                "name": sources[0].get("source_name", "domain_sources"),
                "database": "{{ env_var('DATABRICKS_DEFAULT_CATALOG') }}",
                "schema": "{{ env_var('DATABRICKS_DEFAULT_SCHEMA') }}",
                "tables": source_tables,
            }
        ],
        "models": [],
    }

    # Staging models
    for ref in staging_refs:
        source_def["models"].append(
            {
                "name": ref,
                "description": f"Staging model — {ref}",
                "columns": [
                    {
                        "name": natural_key_cols[0],
                        "tests": ["not_null"],
                    }
                ],
            }
        )

    # Intermediate
    source_def["models"].append(
        {"name": int_ref, "description": f"Intermediate UNION ALL for {model_name}"}
    )

    # Canonical
    canon_cols = [
        {"name": "dl_row_uid", "description": "Surrogate key", "tests": ["not_null", "unique"]},
        {"name": "dl_source", "description": "Source vendor identifier", "tests": ["not_null"]},
        {"name": "dl_business_from_date", "description": "Business validity start", "tests": ["not_null"]},
        {"name": "is_current", "description": "Current record flag", "tests": ["not_null"]},
    ]
    for col in columns:
        if col["name"] in natural_key_cols:
            canon_cols.append(
                {"name": col["name"], "description": col.get("description", ""), "tests": ["not_null"]}
            )
        else:
            canon_cols.append(
                {"name": col["name"], "description": col.get("description", "")}
            )

    source_def["models"].append(
        {
            "name": model_name,
            "description": f"Canonical {model_name} — domain-aligned, bi-temporal",
            "columns": canon_cols,
        }
    )

    return yaml.dump(source_def, default_flow_style=False, sort_keys=False)


def generate_dbt_project_yml(model_name: str) -> str:
    """Generate dbt_project.yml."""
    project = {
        "name": f"{model_name}_domain",
        "version": "1.0.0",
        "config-version": 2,
        "profile": "domain_databricks",
        "model-paths": ["models"],
        "macro-paths": ["macros"],
        "models": {
            f"{model_name}_domain": {
                "staging": {"+materialized": "view"},
                "intermediate": {"+materialized": "view"},
                "canonical": {
                    "+materialized": "incremental",
                    "+file_format": "delta",
                    "+incremental_strategy": "merge",
                },
            }
        },
    }
    return yaml.dump(project, default_flow_style=False, sort_keys=False)


def generate_profiles_yml() -> str:
    """Generate profiles.yml using env vars."""
    return dedent("""\
        domain_databricks:
          target: dev
          outputs:
            dev:
              type: databricks
              catalog: "{{ env_var('DATABRICKS_DEFAULT_CATALOG') }}"
              schema: "{{ env_var('DATABRICKS_DEFAULT_SCHEMA') }}"
              host: "{{ env_var('DATABRICKS_HOST') }}"
              http_path: "{{ env_var('DATABRICKS_HTTP_PATH', '/sql/1.0/warehouses/' ~ env_var('DATABRICKS_WAREHOUSE_ID', '')) }}"
              token: "{{ env_var('DATABRICKS_TOKEN') }}"
              threads: 4
    """)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate domain-aligned dbt models")
    parser.add_argument("--model-spec", required=True, help="Path to model spec YAML")
    parser.add_argument("--output-dir", required=True, help="Output directory for dbt project")
    parser.add_argument(
        "--templates-dir",
        default=None,
        help="Path to macro templates (default: auto-detect)",
    )
    args = parser.parse_args()

    spec = _load_model_spec(Path(args.model_spec))
    output = Path(args.output_dir)

    model_name = spec["model_name"]
    sources = spec["sources"]
    columns = spec["columns"]
    natural_key_cols = spec.get("natural_key_cols", [columns[0]["name"]])
    load_type = spec.get("load_type", "master")
    entity = spec.get("entity", model_name)

    # Directories
    staging_dir = _ensure_dir(output / "models" / "staging")
    int_dir = _ensure_dir(output / "models" / "intermediate")
    canon_dir = _ensure_dir(output / "models" / "canonical")
    macros_dir = _ensure_dir(output / "macros")

    staging_refs = []

    # Generate staging models
    for src in sources:
        vendor = src.get("vendor", "unknown")
        table = src["table"]
        source_name = src.get("source_name", "domain_sources")
        ref_name = f"stg_{vendor}_{entity}"
        staging_refs.append(ref_name)

        sql = generate_staging_model(
            vendor=vendor,
            entity=entity,
            source_name=source_name,
            table_name=table,
            columns=columns,
            column_mappings=src.get("column_mappings"),
        )
        (staging_dir / f"{ref_name}.sql").write_text(sql, encoding="utf-8")
        print(f"  wrote staging: {ref_name}.sql")

    # Generate intermediate model
    int_ref = f"int_{model_name}_union"
    sql = generate_intermediate_model(model_name, staging_refs)
    (int_dir / f"{int_ref}.sql").write_text(sql, encoding="utf-8")
    print(f"  wrote intermediate: {int_ref}.sql")

    # Generate canonical model
    business_cols = [c["name"] for c in columns]
    sql = generate_canonical_model(
        model_name=model_name,
        int_ref=int_ref,
        natural_key_cols=natural_key_cols,
        business_cols=business_cols,
        load_type=load_type,
    )
    (canon_dir / f"{model_name}.sql").write_text(sql, encoding="utf-8")
    print(f"  wrote canonical: {model_name}.sql")

    # Generate schema.yml
    schema = generate_schema_yml(
        model_name=model_name,
        sources=sources,
        staging_refs=staging_refs,
        int_ref=int_ref,
        columns=columns,
        natural_key_cols=natural_key_cols,
    )
    (output / "models" / "schema.yml").write_text(schema, encoding="utf-8")
    print("  wrote schema.yml")

    # Generate project files
    (output / "dbt_project.yml").write_text(
        generate_dbt_project_yml(model_name), encoding="utf-8"
    )
    (output / "profiles.yml").write_text(generate_profiles_yml(), encoding="utf-8")
    print("  wrote dbt_project.yml, profiles.yml")

    # Copy macro templates
    templates_dir = Path(args.templates_dir) if args.templates_dir else (
        Path(__file__).resolve().parent.parent / "templates" / "dbt_project" / "macros"
    )
    if templates_dir.exists():
        for macro_file in templates_dir.glob("*.sql"):
            dest = macros_dir / macro_file.name
            dest.write_text(macro_file.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"  copied macro: {macro_file.name}")

    print(f"
dbt project generated at: {output}")


if __name__ == "__main__":
    main()
