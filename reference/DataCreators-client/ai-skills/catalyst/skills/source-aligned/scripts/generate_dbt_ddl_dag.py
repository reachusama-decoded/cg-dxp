#!/usr/bin/env python3
"""Generate DDL, dbt models, model yml, and dag.yml from source.yml.

Outputs are separated into:
- <base>/curation-emr
- <base>/curation-databricks
    - dag.yml
    - models/ (Databricks-patched dbt models)
"""
from __future__ import annotations

import argparse
from pathlib import Path

# Spark SQL reserved words that must be backtick-quoted when used as identifiers.
# Source: https://spark.apache.org/docs/latest/sql-ref-ansi-compliance.html
_SQL_RESERVED_WORDS = frozenset({
    "add", "after", "all", "alter", "always", "analyze", "and", "anti", "any",
    "archive", "array", "as", "asc", "at", "authorization", "between", "both",
    "bucket", "buckets", "by", "cache", "cascade", "case", "cast", "catalog",
    "change", "check", "clear", "cluster", "clustered", "codegen", "collate",
    "collection", "column", "columns", "comment", "commit", "compact",
    "compactions", "compute", "concatenate", "constraint", "cost", "create",
    "cross", "cube", "current", "current_date", "current_time",
    "current_timestamp", "current_user", "data", "database", "databases",
    "date", "day", "dbproperties", "default", "defined", "delete", "delimited",
    "desc", "describe", "dfs", "directories", "directory", "distinct",
    "distribute", "div", "drop", "else", "end", "escape", "except", "exchange",
    "exclude", "exists", "explain", "export", "extended", "external", "extract",
    "false", "fetch", "fields", "filter", "fileformat", "first", "following",
    "for", "foreign", "format", "formatted", "from", "full", "function",
    "functions", "global", "grant", "group", "grouping", "having", "hour",
    "if", "ignore", "import", "in", "include", "index", "indexes", "inner",
    "inpath", "inputformat", "insert", "int", "intersect", "interval", "into",
    "is", "items", "join", "keys", "last", "lateral", "lazy", "leading",
    "left", "like", "limit", "lines", "list", "load", "local", "location",
    "lock", "locks", "logical", "long", "macro", "map", "matched", "merge",
    "microsecond", "millisecond", "minute", "month", "msck", "namespace",
    "namespaces", "natural", "no", "not", "null", "nulls", "of", "on", "only",
    "option", "options", "or", "order", "out", "outer", "outputformat",
    "over", "overlaps", "overlay", "overwrite", "partition", "partitioned",
    "partitions", "percent", "pivot", "placing", "position", "preceding",
    "primary", "principals", "properties", "purge", "qualify", "query",
    "range", "recordreader", "recordwriter", "recover", "reduce", "references",
    "refresh", "regexp", "rename", "repair", "repeatable", "replace",
    "reset", "respect", "restrict", "revoke", "right", "rlike", "role",
    "roles", "rollback", "rollup", "row", "rows", "schema", "schemas",
    "second", "select", "semi", "separated", "serde", "serdeproperties",
    "session_user", "set", "sets", "show", "skewed", "some", "sort", "sorted",
    "start", "statistics", "stored", "stratify", "struct", "substr",
    "substring", "sync", "system_time", "system_version", "table",
    "tables", "tablesample", "tblproperties", "temp", "temporary",
    "terminated", "then", "time", "timestamp", "timestampadd", "timestampdiff",
    "to", "touch", "trailing", "transaction", "transactions", "transform",
    "trim", "true", "truncate", "try_cast", "type", "unarchive", "unbounded",
    "uncache", "union", "unique", "unknown", "unlock", "unpivot", "unset",
    "update", "use", "user", "using", "values", "version", "view", "views",
    "when", "where", "window", "with", "within", "year", "zone",
})


def _quote(name: str) -> str:
    """Backtick-quote a column name if it is a SQL reserved word."""
    if name.lower() in _SQL_RESERVED_WORDS:
        return f"`{name}`"
    return name


def parse_source_yml(text: str) -> dict:
    data: dict[str, str] = {}
    columns: list[dict[str, str]] = []
    source_table = None
    in_columns = False
    current: dict[str, str] | None = None

    for line in text.splitlines():
        if line.startswith("dataset_type:"):
            data["dataset_type"] = line.split(":", 1)[1].strip()
        elif line.startswith("dc:"):
            data["dc"] = line.split(":", 1)[1].strip()
        elif line.startswith("domain:"):
            data["domain"] = line.split(":", 1)[1].strip()
        elif line.startswith("target_table:"):
            data["target_table"] = line.split(":", 1)[1].strip()
        elif line.startswith("target_schema:"):
            data["target_schema"] = line.split(":", 1)[1].strip()
        elif line.strip().startswith("schedule_interval:"):
            data["schedule_interval"] = line.split(":", 1)[1].strip()
        elif line.startswith("load_type:"):
            data["load_type"] = line.split(":", 1)[1].strip()
        elif line.strip() == "sources:":
            continue
        elif line.startswith("  - ") and line.strip().endswith(":") and not in_columns:
            source_table = line.strip()[2:-1].strip()
        elif line.strip() == "columns:":
            in_columns = True
        elif in_columns and line.startswith("  - ") and line.strip().endswith(":"):
            if current:
                columns.append(current)
            current = {"column": line.strip()[2:-1].strip()}
        elif in_columns and current is not None:
            stripped = line.strip()
            if stripped.startswith("source_name:"):
                current["source_name"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("source_data_type:"):
                current["source_data_type"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("target_name:"):
                current["target_name"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("target_data_type:"):
                current["target_data_type"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("surrogate_key:"):
                current["surrogate_key"] = stripped.split(":", 1)[1].strip()

    if current:
        columns.append(current)

    if not source_table:
        raise ValueError("source table not found in source.yml")
    data["source_table"] = source_table
    data["columns"] = columns
    return data


def write_ddl(output_path: Path, data: dict) -> None:
    schema = data["target_schema"]
    table = data["target_table"]
    dataset_type = data["dataset_type"].lower()
    cols = data["columns"]

    audit_master = [
        "dl_row_uid string",
        "dl_checksum_value string",
        "dl_business_start_date date",
        "dl_business_end_date date",
        "dl_system_start_timestamp timestamp",
        "dl_system_end_timestamp timestamp",
        "dl_current_indicator string",
        "dl_last_update_process_id string",
        "dl_source_system_code string",
    ]
    audit_balance = [
        "dl_row_uid string",
        "dl_checksum_value string",
        "dl_system_start_timestamp timestamp",
        "dl_system_end_timestamp timestamp",
        "dl_current_indicator string",
        "dl_last_update_process_id string",
        "dl_source_system_code string",
    ]
    audit_cols = audit_master if dataset_type == "master" else audit_balance

    lines = [
        f"DROP TABLE IF EXISTS {schema}_{{env}}.{table};",
        "",
        f"CREATE EXTERNAL TABLE IF NOT EXISTS {schema}_{{env}}.{table} (",
    ]
    for col in cols:
        lines.append(f"    {_quote(col['target_name'])} {col['target_data_type']},")
    for i, col in enumerate(audit_cols):
        end = "," if i < len(audit_cols) - 1 else ""
        lines.append(f"    {col}{end}")
    lines.extend(
        [
            ")",
            "USING delta",
            "PARTITIONED BY (dl_current_indicator)",
            f"LOCATION 's3://datalake-curated-{{env}}-us-east-1/{schema}/{table}'",
            "TBLPROPERTIES ('table_type'='DELTA');",
            "",
        ]
    )
    output_path.write_text("
".join(lines))


def write_stage_model(output_path: Path, data: dict) -> None:
    domain = data["domain"]
    source_table = data["source_table"]
    load_type = data.get("load_type", "full")
    cols = data["columns"]
    selected_cols = ",
    ".join([c["source_name"] for c in cols])
    content = f"""{{{{
    config(
        schema = \"cspn_work2_\"|string + target.name,
        meta = {{ \"dataset_load_type\" : \"{load_type}\",
                 \"dataset_load_catchup_strategy\" : \"chronological\" }}
    )
}}}}
{{% set source_schema_suffix = var(\"source_schema_suffix\") |string %}}
{{% set source_schema = 'cspn_std_{domain}_'|string + source_schema_suffix  %}}

SELECT
    {selected_cols}
FROM {{{{ cspn_source(source_schema, '{source_table}' ) }}}} 
"""
    output_path.write_text(content)


def write_integration_model(output_path: Path, data: dict) -> None:
    source_table = data["source_table"]
    cols = data["columns"]

    select_lines = []
    checksum_lines = []
    for col in cols:
        target = col["target_name"]
        source = col.get("source_name", target)
        qt = _quote(target)
        qs = _quote(source)
        target_type = str(col.get("target_data_type", "")).lower()
        expression = qs
        if target_type in {"int", "integer", "bigint", "long"}:
            expression = f"cast({qs} as bigint)"
        select_lines.append(f"        {expression} as {qt},")
        checksum_lines.append(f"        coalesce(cast(cte.{qt} as string), '')")

    select_body = "
".join(select_lines).rstrip(",")
    checksum_body = ",
".join(checksum_lines)

    content = f"""{{{{
    config(
        schema = \"cspn_work2_\"|string + target.name,
        materialized = 'view',
    )
}}}}

WITH cte AS (
    SELECT
{select_body}
    FROM {{{{ ref(\"stage_{source_table}\") }}}}
)
SELECT
    cte.*,
    sha1(concat_ws('|', 
{checksum_body}
    )) as dl_checksum_value
FROM cte
"""
    output_path.write_text(content)


def write_prepared_model(output_path: Path, data: dict) -> None:
    target_schema = data["target_schema"]
    target_table = data["target_table"]
    dataset_type = data["dataset_type"].lower()
    load_type = data.get("load_type", "full")
    cols = data["columns"]
    surrogate_cols = [c["target_name"] for c in cols if c.get("surrogate_key") == "Y"]
    surrogate_cols_literal = str(surrogate_cols)

    meta_lines = [f"\"surrogate_key_cols\": {surrogate_cols}", "\"audit_column_list\": [\"dl_last_update_process_id\"]"]
    partition_config = "partition_by = [\"dl_current_indicator\"],"
    balance_config = ""
    if dataset_type == "balance":
        balance_config = "as_of_col = \"\",
        detect_change_flag = \"Y\","  # placeholder
        meta_lines.append('"cluster_by": ["dl_current_indicator", ""]')
        partition_config = ""

    meta = ",
                 ".join(meta_lines)
    all_cols = ",
    ".join([_quote(c["target_name"]) for c in cols])

    content = f"""{{{{
    config (
        schema = \"{target_schema}_\"|string + target.name,
        materialized = \"incremental\",
        incremental_strategy = \"bitemporal_load_v2\",
        load_type = \"{load_type}\",
        {partition_config}
        {balance_config}
        file_format = \"delta\",
        unique_key = \"dl_row_uid\",
        meta = {{ {meta} }},
        alias = '{target_table}',
        post_hook = [\"vacuum {{{{ this }}}} retain 0 hours\", \"{{{{ cspn_commit_checkpoints() }}}}\"]
    )
}}}}

{{% set domain = config.model.meta.get(\"domain\") -%}}

SELECT
    {all_cols},
    {{{{ generate_surrogate_key_v3({surrogate_cols_literal}) }}}},
    dl_checksum_value, 
    {{{{ get_audit_cols() }}}},
    '{{{{ domain }}}}' as dl_source_system_code
FROM {{{{ ref(\"int_{target_table}\") }}}}
"""
    output_path.write_text(content)


def write_model_yml(output_path: Path, data: dict) -> None:
    domain = data["domain"]
    source_table = data["source_table"]
    target_table = data["target_table"]
    target_schema = data["target_schema"]
    dataset_type = data["dataset_type"]
    dc = data["dc"]

    content = f"""version: 2

sources:
  - name: cspn_std_{domain}_{{{{target.name}}}}
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
      tags: {{'dc': '{dc}'}}
      process_schema: {target_schema}
"""
    output_path.write_text(content)


def patch_dbt_content(content: str) -> str:
    patched_lines: list[str] = []
    for line in content.splitlines():
        if "post_hook" in line:
            continue
        if "cspn_commit_checkpoints" in line:
            continue
        if "vacuum {{ this }} retain 0 hours" in line:
            continue
        patched_lines.append(line)
    patched = "
".join(patched_lines)
    patched = patched.replace("chronological", "latest")
    if not patched.endswith("
"):
        patched += "
"
    return patched


def write_databricks_models(source_dir: Path, target_dir: Path) -> None:
    for src in source_dir.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(source_dir)
        dst = target_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in {".sql", ".yml", ".yaml"}:
            content = src.read_text()
            dst.write_text(patch_dbt_content(content))
        else:
            dst.write_bytes(src.read_bytes())


def write_dag_yml(output_path: Path, data: dict) -> None:
    domain = data["domain"]
    process_name = data["source_table"]
    target_table = data["target_table"]
    dc = data["dc"]
    schedule_interval = data["schedule_interval"]

    hour = "21"
    if schedule_interval:
        parts = schedule_interval.split()
        if len(parts) >= 2 and parts[1].isdigit():
            hour = parts[1]

    content = f"""schedule_info:
  run_calendar: None
  schedule_interval: {schedule_interval}
  catchup: False
  start_date: !eval \"pendulum.datetime(2021, 9, 1, tz='America/Los_Angeles')\"
  end_date: !eval \"pendulum.datetime(2999, 12, 31, tz='America/Los_Angeles')\"

airflow_dag_args:
  tags: [\"op-tag:sor:{dc}\",\"op-tag:dev_pod:company\"]
  default_args:
    depends_on_past: False

tasks:
  ingestion:
    depends_on: []
    template_ref: dag_exec_check_v2
    params:
      ingestion_dag: ingestion-{domain}-{process_name}
      hours: {hour}
      mins: 15
      dag_exec_check_timeout: 25200
  scd_curate:
    depends_on: [ingestion]
    template_ref: dbt_emr_container_operator_critical
    params:
      driver_memory: 8G
      executor_memory: 8G
      driver_cores: 4
      executor_cores: 4
      max_executors: 8
      shuffle_partitions: 100
      kryo_max: 512m
      driver_max_result: 1g
      task_model: +{target_table}
      model_name: {target_table}
  xcom:
    depends_on: [scd_curate]
    template_ref: dbt_xcom_generation_bitemporal
    params:
      configuration: /apps/casper-im-foundation/models/{dc}/{target_table}_f/{target_table}.yml
      xcom_pull_task: scd_curate_emr_xcom_pull
      dl_system_start_column: dl_system_start_timestamp
      db_name: cspn_fndn2
      operation_type: change
  dq_validation:
    depends_on: [xcom]
    template_ref: emr_spark_deequ_verify_v11
    params:
      application_name: casper-im-foundation
      dataset_name: cspn_{target_table}
      ruleset_name: cspn_{target_table}-in_motion
      input_path: !conf \"{{{{ task_instance.xcom_pull(task_ids='xcom_generation', key='return_value')['current'] }}}}\"
      metrics_storage_indicator: True
      rule_group: Daily
  scd_tag:
    depends_on: [dq_validation]
    template_ref: dbt_casper_tag
    params:
      model: current
      xcom_pull_task: xcom_generation
  refresh_delta_ds:
    depends_on: [scd_tag]
    template_ref: refresh_pds_dremio
    params:
      db_path: !conf \"Casper Data Lake.{{{{ var.value.get('curated_zone')|replace('s3://','')|replace('s3a://','') }}}}.cspn_fndn2\"
      table_name: \"{target_table}\"
      table_type: \"Delta\"
  scd_notify:
    depends_on: [refresh_delta_ds]
    template_ref: dbt_kafka_balance_notify
    params:
      model: current
      xcom_pull_task: xcom_generation
"""
    output_path.write_text(content)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--base-dir", required=True)
    args = parser.parse_args()

    data = parse_source_yml(Path(args.source).read_text())

    base_dir = Path(args.base_dir)
    curation_emr = base_dir / "curation-emr"
    curation_dbx = base_dir / "curation-databricks"
    curation_emr.mkdir(parents=True, exist_ok=True)
    curation_dbx.mkdir(parents=True, exist_ok=True)

    models_dir = curation_emr / "models"
    (models_dir / "staging").mkdir(parents=True, exist_ok=True)
    (models_dir / "integration").mkdir(parents=True, exist_ok=True)
    (models_dir / "prepared").mkdir(parents=True, exist_ok=True)
    dbx_models_dir = curation_dbx / "models"

    write_ddl(curation_emr / "ddl.sql", data)
    write_stage_model(models_dir / "staging" / f"stage_{data['source_table']}.sql", data)
    write_integration_model(models_dir / "integration" / f"int_{data['target_table']}.sql", data)
    write_prepared_model(models_dir / "prepared" / f"{data['target_table']}.sql", data)
    write_model_yml(models_dir / f"{data['target_table']}.yml", data)
    write_dag_yml(curation_dbx / "dag.yml", data)
    write_databricks_models(models_dir, dbx_models_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
