#!/usr/bin/env python3
"""Generate dq.yml, pipeline.py, and source.yml from ingestion.yml.

Outputs are separated into:
- <base>/ingestion
- <base>/curation-emr
"""
from __future__ import annotations

import argparse
from pathlib import Path


def parse_ingestion_schema(ingestion_text: str) -> list[dict[str, str]]:
    lines = ingestion_text.splitlines()
    schema_start = None
    for i, line in enumerate(lines):
        if line.strip() == "schema:":
            schema_start = i
            break
    if schema_start is None:
        raise ValueError("schema section not found in ingestion.yml")

    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for line in lines[schema_start + 1 :]:
        if line.strip().startswith("schedule_info:"):
            break
        if line.strip().startswith("- alias:") or line.startswith("    - alias:"):
            if current:
                entries.append(current)
            current = {"alias": line.split(":", 1)[1].strip()}
            continue
        if current is None:
            continue
        stripped = line.strip()
        if stripped.startswith("data_type:"):
            current["data_type"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("field_name:"):
            current["field_name"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("is_nullable:"):
            current["is_nullable"] = stripped.split(":", 1)[1].strip()

    if current:
        entries.append(current)

    return entries


def write_dq_yml(output_path: Path, process_domain: str, process_name: str, pk_list: list[str]) -> None:
    pk_str = ", ".join([f'"{p}"' for p in pk_list])
    content = f"""model_version: 2
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
          columns: [{pk_str}]
          assert_value: 1.0
          hint: "Uniqueness check on primary key"
"""
    output_path.write_text(content)


def write_pipeline_py(output_path: Path, process_name: str) -> None:
    content = f"""# casper dag: generated

import logging
from pathlib import Path

from airflow import DAG  # this is needed. it probably starts the search tree

from casper.orchestration.templates.ingestion import Ingestion, IngestionConfiguration

logger = logging.getLogger(__name__)

pipeline_cxt = IngestionConfiguration.from_yaml(f"{{Path(__file__).parent}}/{process_name}.yml")

dag = DAG(
    IngestionConfiguration.dag_name(pipeline_cxt),
    schedule_interval=pipeline_cxt["schedule_info"]["cron"],
    default_args=pipeline_cxt["airflow_defaults"],
    catchup=pipeline_cxt["airflow_defaults"].get("catchup", False),
    is_paused_upon_creation=pipeline_cxt.get("is_paused_upon_creation", True),
)

IngestionConfiguration.validate_dag_structure(__file__, pipeline_cxt)

with dag:
    Ingestion.landing_to_raw(dag, pipeline_cxt) >> Ingestion.raw_to_standard(dag, pipeline_cxt)
    Ingestion.data_notifications(dag, pipeline_cxt)
"""
    output_path.write_text(content)


def write_source_yml(
    output_path: Path,
    process_domain: str,
    process_name: str,
    dc_tag: str,
    dataset_type: str,
    schedule_interval: str,
    columns: list[dict[str, str]],
    pk_list: list[str],
) -> None:
    target_table = f"{process_name}_v4"
    lines = []
    lines.append(f"dataset_type: {dataset_type}")
    lines.append(f"dc: {dc_tag}")
    lines.append(f"domain: {process_domain}")
    lines.append("sources:")
    lines.append(f"  - {process_name}:")
    lines.append("      table_type: file")
    lines.append(f"      schema: cspn_std_{process_domain}")
    lines.append(f"target_table: {target_table}")
    lines.append("target_schema: cspn_fndn2")
    lines.append("dag:")
    lines.append("  dependencies:")
    lines.append(f"    - ingestion-{process_domain}-{process_name}")
    lines.append("  run_calendar: global_holidays")
    lines.append(f"  schedule_interval: {schedule_interval}")
    lines.append("pipeline:")
    lines.append("  type: emr")
    lines.append("  scale: critical")
    lines.append(f"prompt: 1 to 1 Load data from source file. It depends on {process_name} ingestion file.")
    lines.append("load_type: full")
    lines.append("as_of_col:")
    lines.append("columns:")
    for col in columns:
        alias = col["alias"]
        dtype = col.get("data_type", "string")
        surrogate = "Y" if alias in pk_list else "N"
        lines.append(f"  - {alias}:")
        lines.append(f"      source_name: {alias}")
        lines.append(f"      source_data_type: {dtype}")
        lines.append(f"      target_name: {alias}")
        lines.append(f"      target_data_type: {dtype}")
        lines.append(f"      source_table: {process_name}")
        lines.append(f"      target_table: {target_table}")
        lines.append("      prompt: 1:1 load")
        lines.append(f"      surrogate_key: {surrogate}")
    output_path.write_text("
".join(lines) + "
")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingestion", required=True)
    parser.add_argument("--base-dir", required=True)
    parser.add_argument("--process-domain", required=True)
    parser.add_argument("--process-name", required=True)
    parser.add_argument("--dc-tag", required=True)
    parser.add_argument("--schedule-interval", required=True)
    parser.add_argument("--pk", action="append", required=True, help="Primary key alias; repeat for multiple")
    args = parser.parse_args()

    ingestion_text = Path(args.ingestion).read_text()
    columns = parse_ingestion_schema(ingestion_text)

    base_dir = Path(args.base_dir)
    ingestion_dir = base_dir / "ingestion"
    curation_emr_dir = base_dir / "curation-emr"
    ingestion_dir.mkdir(parents=True, exist_ok=True)
    curation_emr_dir.mkdir(parents=True, exist_ok=True)

    write_dq_yml(ingestion_dir / "dq.yml", args.process_domain, args.process_name, args.pk)
    write_pipeline_py(ingestion_dir / "pipeline.py", args.process_name)
    write_source_yml(
        curation_emr_dir / "source.yml",
        process_domain=args.process_domain,
        process_name=args.process_name,
        dc_tag=args.dc_tag,
        dataset_type="master",
        schedule_interval=args.schedule_interval,
        columns=columns,
        pk_list=args.pk,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
