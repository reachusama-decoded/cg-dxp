#!/usr/bin/env python3
"""Local-first Databricks ingestion adapter.

- Copies a local file into the landing path (raw landing convention).
- Copies landing file to raw path (raw zone convention).
- Reads raw file using ingestion.yml r2s options and writes a standard Delta table.
- Optionally runs dbt against Databricks (if dbt is installed).

Intended to be run in Databricks (notebook/job) or via databricks-connect.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import zipfile
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

SparkSession = None
BooleanType = None
DateType = None
DecimalType = None
DoubleType = None
IntegerType = None
LongType = None
StringType = None
StructField = None
StructType = None
TimestampType = None
USE_DATABRICKS_CONNECT = False


@dataclass
class IngestionConfig:
    process_domain: str
    process_name: str
    l2r: Dict[str, Any]
    r2s: Dict[str, Any]


def load_yaml(path: Path) -> Dict[str, Any]:
    path_str = str(path)
    if path_str.startswith("dbfs:/"):
        content = read_dbfs_text(path_str)
    else:
        content = normalize_path(path_str).read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
    except Exception:
        raise RuntimeError("PyYAML is required to read ingestion configs.")
    return yaml.safe_load(content) or {}


def load_ingestion_config(path: Path) -> IngestionConfig:
    cfg = load_yaml(path)
    return IngestionConfig(
        process_domain=str(cfg.get("process_domain")),
        process_name=str(cfg.get("process_name")),
        l2r=cfg.get("l2r", {}) or {},
        r2s=cfg.get("r2s", {}) or {},
    )


def load_env_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Env config not found: {path}")
    return load_yaml(p)


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def pick_setting(arg_value: Optional[str], env_key: str, cfg: Dict[str, Any], default: str) -> str:
    if arg_value:
        return arg_value
    if env_key in os.environ and os.environ.get(env_key):
        return str(os.environ.get(env_key))
    if env_key in cfg and cfg.get(env_key):
        return str(cfg.get(env_key))
    return default


def dbfs_to_local(path: str) -> str:
    if path.startswith("dbfs:/"):
        return "/dbfs/" + path[len("dbfs:/") :].lstrip("/")
    return path


def normalize_path(path: str) -> Path:
    return Path(dbfs_to_local(path))


def read_dbfs_text(dbfs_path: str) -> str:
    try:
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.getOrCreate()
        rows = spark.read.text(dbfs_path).collect()
        return "\n".join(row.value for row in rows)
    except Exception as exc:
        local_path = Path(dbfs_to_local(dbfs_path))
        try:
            return local_path.read_text(encoding="utf-8")
        except Exception as local_exc:
            raise RuntimeError(f"Unable to read dbfs path: {dbfs_path}") from local_exc


def ensure_dir(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def copy_file(src: str, dst: str) -> None:
    ensure_dir(str(Path(dst).parent))
    shutil.copy2(src, dst)


def upload_via_databricks_sdk(local_path: str, volume_path: str) -> None:
    try:
        from databricks.sdk import WorkspaceClient
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("databricks-sdk is required for --use-databricks-sdk") from exc

    profile = os.environ.get("DATABRICKS_CONFIG_PROFILE")
    client = WorkspaceClient(profile=profile) if profile else WorkspaceClient()

    with open(local_path, "rb") as f:
        client.files.upload(
            file_path=volume_path,
            overwrite=True,
            contents=f,
        )


def list_matching_files(directory: str, pattern: str) -> List[str]:
    base = Path(directory)
    if not base.exists():
        return []
    return [str(p) for p in base.glob(pattern)]


def parse_decimal_type(type_str: str) -> Optional[DecimalType]:
    if "decimal" not in type_str:
        return None
    try:
        inner = type_str[type_str.find("(") + 1 : type_str.find(")")]
        precision, scale = inner.split(",")
        return DecimalType(int(precision.strip()), int(scale.strip()))
    except Exception:
        return None


def to_spark_type(type_str: str):
    _ensure_pyspark()
    t = type_str.strip().lower()
    if t in {"string", "varchar", "char", "text"}:
        return StringType()
    if t in {"int", "integer"}:
        return IntegerType()
    if t in {"bigint", "long"}:
        return LongType()
    if t in {"double", "float", "real"}:
        return DoubleType()
    if t in {"boolean", "bool"}:
        return BooleanType()
    if t in {"date"}:
        return DateType()
    if t in {"timestamp", "datetime"}:
        return TimestampType()
    dec = parse_decimal_type(t)
    if dec is not None:
        return dec
    return StringType()


def build_schema(fields: List[Dict[str, Any]]) -> StructType:
    _ensure_pyspark()
    struct_fields = []
    for field in fields:
        col_name = field.get("alias") or field.get("field_name")
        data_type = field.get("data_type", "string")
        nullable = bool(field.get("is_nullable", True))
        struct_fields.append(StructField(col_name, to_spark_type(str(data_type)), nullable))
    return StructType(struct_fields)


def add_ingestion_columns(df, r2s: Dict[str, Any], file_path: str, process_date: datetime):
    _ensure_pyspark()
    from pyspark.sql.functions import lit, monotonically_increasing_id

    extra_fields = r2s.get("extra_standard_table_fields", []) or []
    if "landing_zone_file_name" in extra_fields:
        df = df.withColumn("landing_zone_file_name", lit(os.path.basename(file_path)))

    if r2s.get("add_correlation_id", False):
        df = df.withColumn("correlation_id__", monotonically_increasing_id())

    df = (
        df.withColumn("year__", lit(process_date.year))
        .withColumn("month__", lit(process_date.month))
        .withColumn("day__", lit(process_date.day))
        .withColumn("time__", lit(process_date.strftime("%H%M%S%f")))
    )
    return df, ["year__", "month__", "day__", "time__"]


def raw_timestamp_subdir(process_date: datetime) -> str:
    return "/".join(
        [
            process_date.strftime("%Y"),
            process_date.strftime("%m"),
            process_date.strftime("%d"),
            process_date.strftime("%H%M%S%f"),
        ]
    )


def _convert_excel_serial_dates(pdf, schema_fields: List[Dict[str, Any]]) -> None:
    """Convert Excel serial date numbers to datetime in-place for date/timestamp columns.

    Excel stores dates as the number of days since 1899-12-30 (the "Excel epoch").
    When openpyxl reads a cell whose value is stored as a plain number without
    date formatting, pandas sees a float (e.g. 45930.0) instead of a datetime.
    This helper detects such columns and converts them.
    """
    import pandas as pd
    import numpy as np

    date_types = {"date", "timestamp", "datetime"}
    alias_by_field = {
        str(f.get("alias") or f.get("field_name", "")).strip(): str(f.get("data_type", "string")).strip().lower()
        for f in schema_fields
    }
    excel_epoch = pd.Timestamp("1899-12-30")
    for col_name, dtype in alias_by_field.items():
        if dtype not in date_types or col_name not in pdf.columns:
            continue
        series = pdf[col_name]
        if pd.api.types.is_datetime64_any_dtype(series):
            continue  # already a proper datetime
        if pd.api.types.is_numeric_dtype(series):
            # Looks like Excel serial numbers — convert
            pdf[col_name] = pd.to_timedelta(series, unit="D") + excel_epoch


def read_raw_to_df(spark: SparkSession, r2s: Dict[str, Any], raw_path: str):
    _ensure_pyspark()
    file_format = str(r2s.get("file_format", "delimited")).lower()
    if file_format == "excel":
        schema_fields = r2s.get("schema", []) or []
        sheet_name = r2s.get("sheet_name", 0)
        header_enabled = bool(r2s.get("header", True))
        skip_header = int(r2s.get("skip_header_rows") or 0)
        skip_footer = int(r2s.get("skip_footer_rows") or 0)
        ordered_aliases = [str(field.get("alias", "")).strip() for field in schema_fields if field.get("alias")]

        try:
            import pandas as pd

            header_arg = 0 if header_enabled else None
            skiprows_arg = skip_header if skip_header > 0 else None
            skipfooter_arg = skip_footer if skip_footer > 0 else 0

            pdf = pd.read_excel(
                raw_path,
                sheet_name=sheet_name,
                header=header_arg,
                skiprows=skiprows_arg,
                skipfooter=skipfooter_arg,
                engine="openpyxl",
            )

            if schema_fields:
                alias_by_field = {
                    str(field.get("field_name", "")).strip(): str(field.get("alias", "")).strip()
                    for field in schema_fields
                    if field.get("field_name") and field.get("alias")
                }

                if header_enabled:
                    selected_cols = [name for name in alias_by_field.keys() if name in pdf.columns]
                    if selected_cols:
                        pdf = pdf[selected_cols].rename(columns=alias_by_field)
                else:
                    pdf = pdf.iloc[:, : len(ordered_aliases)]
                    pdf.columns = ordered_aliases

                for alias in ordered_aliases:
                    if alias and alias not in pdf.columns:
                        pdf[alias] = None
                if ordered_aliases:
                    pdf = pdf[ordered_aliases]

            # Convert Excel serial date numbers to datetime for date/timestamp columns
            _convert_excel_serial_dates(pdf, schema_fields)

            df = spark.createDataFrame(pdf)
        except ImportError:
            rows = _read_xlsx_rows_without_openpyxl(raw_path, sheet_name)
            if skip_header > 0:
                rows = rows[skip_header:]
            if skip_footer > 0:
                rows = rows[:-skip_footer] if len(rows) > skip_footer else []

            headers: List[str]
            data_rows: List[List[Optional[str]]]
            if header_enabled and rows:
                headers = [str(v).strip() if v is not None else "" for v in rows[0]]
                data_rows = rows[1:]
            else:
                width = max((len(r) for r in rows), default=0)
                headers = [f"col_{i+1}" for i in range(width)]
                data_rows = rows

            if schema_fields:
                field_names = [str(field.get("field_name", "")).strip() for field in schema_fields]
                alias_by_field = {
                    str(field.get("field_name", "")).strip(): str(field.get("alias", "")).strip()
                    for field in schema_fields
                    if field.get("field_name") and field.get("alias")
                }
                projected = []
                for row in data_rows:
                    row_dict: Dict[str, Optional[str]] = {}
                    if header_enabled:
                        row_map = {headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
                        for field_name in field_names:
                            alias = alias_by_field.get(field_name)
                            if alias:
                                row_dict[alias] = row_map.get(field_name)
                    else:
                        for idx, alias in enumerate(ordered_aliases):
                            row_dict[alias] = row[idx] if idx < len(row) else None
                    projected.append(row_dict)
                df = spark.createDataFrame(projected) if projected else spark.createDataFrame([], StructType([]))
            else:
                projected = []
                for row in data_rows:
                    row_dict = {headers[i]: row[i] if i < len(row) else None for i in range(len(headers))}
                    projected.append(row_dict)
                df = spark.createDataFrame(projected) if projected else spark.createDataFrame([], StructType([]))

        if schema_fields:
            from pyspark.sql.functions import col, expr

            date_types = {"date", "timestamp", "datetime"}
            for field in schema_fields:
                alias = field.get("alias") or field.get("field_name")
                dtype = str(field.get("data_type", "string")).strip().lower()
                if alias in df.columns:
                    if dtype in date_types:
                        # Try to detect Excel serial date numbers (numeric values
                        # representing days since 1899-12-30) and convert them
                        # before casting to timestamp/date.
                        df = df.withColumn(
                            alias,
                            expr(
                                f"CASE WHEN cast(`{alias}` as double) IS NOT NULL "
                                f"AND cast(`{alias}` as double) > 25569 "  # 1970-01-01 serial
                                f"AND cast(`{alias}` as double) < 73050 "  # ~2099-12-31 serial
                                f"THEN cast(date_add(date '1899-12-30', cast(cast(`{alias}` as double) as int)) as {dtype}) "
                                f"ELSE cast(`{alias}` as {dtype}) END"
                            ),
                        )
                    else:
                        df = df.withColumn(alias, col(alias).cast(to_spark_type(dtype)))

        return df

    if file_format != "delimited":
        raise NotImplementedError(f"Only file_format=delimited or file_format=excel is supported in this local adapter (got {file_format}).")

    schema_fields = r2s.get("schema", []) or []
    schema = build_schema(schema_fields) if schema_fields else None

    reader = spark.read
    if schema is not None:
        reader = reader.schema(schema)

    options = {
        "delimiter": r2s.get("delimiter", ","),
        "header": str(r2s.get("header", True)).lower(),
        "escape": r2s.get("escape", "\\"),
        "quote": r2s.get("quote", '"'),
        "multiLine": str(r2s.get("multiLine", True)).lower(),
    }

    if r2s.get("comment") is not None:
        options["comment"] = r2s.get("comment")

    if r2s.get("timestampFormat") is not None:
        options["timestampFormat"] = r2s.get("timestampFormat")

    if r2s.get("dateFormat") is not None:
        options["dateFormat"] = r2s.get("dateFormat")

    if r2s.get("nullValue") is not None:
        options["nullValue"] = r2s.get("nullValue")

    skip_header = r2s.get("skip_header_rows")
    skip_footer = r2s.get("skip_footer_rows")
    if skip_header is not None:
        options["skipRows"] = int(skip_header)

    if skip_footer is not None:
        options["skipFooter"] = int(skip_footer)

    df = reader.options(**options).csv(raw_path)

    return df


def _xlsx_col_to_index(col_ref: str) -> int:
    idx = 0
    for ch in col_ref:
        idx = idx * 26 + (ord(ch.upper()) - ord("A") + 1)
    return max(idx - 1, 0)


def _xlsx_shared_strings(zf: zipfile.ZipFile) -> List[str]:
    try:
        with zf.open("xl/sharedStrings.xml") as f:
            tree = ET.parse(f)
    except KeyError:
        return []
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    out: List[str] = []
    for si in tree.findall(".//x:si", ns):
        texts = [t.text or "" for t in si.findall(".//x:t", ns)]
        out.append("".join(texts))
    return out


def _xlsx_sheet_path(zf: zipfile.ZipFile, sheet_name: Any) -> str:
    ns_main = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    ns_rel = {"r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    wb = ET.parse(zf.open("xl/workbook.xml"))
    sheets = wb.findall(".//x:sheets/x:sheet", ns_main)
    if not sheets:
        raise ValueError("No sheets found in XLSX workbook")

    if isinstance(sheet_name, int):
        target = sheets[sheet_name] if 0 <= sheet_name < len(sheets) else sheets[0]
    else:
        wanted = str(sheet_name)
        target = next((s for s in sheets if s.attrib.get("name") == wanted), sheets[0])

    rel_id = target.attrib.get(f"{{{ns_rel['r']}}}id")
    if not rel_id:
        raise ValueError("Sheet relationship id not found")

    rels = ET.parse(zf.open("xl/_rels/workbook.xml.rels"))
    for rel in rels.findall(".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"):
        if rel.attrib.get("Id") == rel_id:
            target_path = rel.attrib.get("Target", "")
            if target_path.startswith("/"):
                target_path = target_path[1:]
            if not target_path.startswith("xl/"):
                target_path = f"xl/{target_path}"
            return target_path
    raise ValueError("Unable to resolve sheet xml path")


def _read_xlsx_rows_without_openpyxl(raw_path: str, sheet_name: Any) -> List[List[Optional[str]]]:
    rows: List[List[Optional[str]]] = []
    with zipfile.ZipFile(raw_path, "r") as zf:
        shared = _xlsx_shared_strings(zf)
        sheet_path = _xlsx_sheet_path(zf, sheet_name)
        sheet = ET.parse(zf.open(sheet_path))

    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    for row_elem in sheet.findall(".//x:sheetData/x:row", ns):
        values_by_idx: Dict[int, Optional[str]] = {}
        max_idx = -1
        for c in row_elem.findall("x:c", ns):
            ref = c.attrib.get("r", "")
            match = re.match(r"([A-Z]+)", ref)
            if not match:
                continue
            idx = _xlsx_col_to_index(match.group(1))
            max_idx = max(max_idx, idx)
            cell_type = c.attrib.get("t")
            value: Optional[str] = None
            if cell_type == "s":
                v = c.find("x:v", ns)
                if v is not None and v.text is not None:
                    sidx = int(v.text)
                    value = shared[sidx] if 0 <= sidx < len(shared) else None
            elif cell_type == "inlineStr":
                t = c.find("x:is/x:t", ns)
                value = t.text if t is not None else None
            else:
                v = c.find("x:v", ns)
                value = v.text if v is not None else None
            values_by_idx[idx] = value

        if max_idx < 0:
            rows.append([])
        else:
            rows.append([values_by_idx.get(i) for i in range(max_idx + 1)])
    return rows


def _ensure_pyspark() -> None:
    global SparkSession
    global BooleanType, DateType, DecimalType, DoubleType, IntegerType, LongType
    global StringType, StructField, StructType, TimestampType
    global USE_DATABRICKS_CONNECT
    if SparkSession is not None:
        return
    try:
        try:
            from databricks.connect import DatabricksSession as _SparkSession  # type: ignore
            USE_DATABRICKS_CONNECT = True
        except Exception:
            from pyspark.sql import SparkSession as _SparkSession
        from pyspark.sql.types import (
            BooleanType as _BooleanType,
            DateType as _DateType,
            DecimalType as _DecimalType,
            DoubleType as _DoubleType,
            IntegerType as _IntegerType,
            LongType as _LongType,
            StringType as _StringType,
            StructField as _StructField,
            StructType as _StructType,
            TimestampType as _TimestampType,
        )
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "pyspark is required for raw->standard in local runs. "
            "Use --landing-only or submit a Databricks serverless job via "
            "plugins/casper/skills/source-aligned/scripts/submit_serverless_raw_to_standard.py."
        ) from exc
    SparkSession = _SparkSession
    BooleanType = _BooleanType
    DateType = _DateType
    DecimalType = _DecimalType
    DoubleType = _DoubleType
    IntegerType = _IntegerType
    LongType = _LongType
    StringType = _StringType
    StructField = _StructField
    StructType = _StructType
    TimestampType = _TimestampType


def ensure_schema_exists(spark: SparkSession, catalog: str, schema: str) -> None:
    try:
        spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
    except Exception:
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {catalog}.{schema}")


def write_standard_table(
    df,
    spark: SparkSession,
    catalog: str,
    schema: str,
    table: str,
    standard_path: Optional[str],
    partition_cols: Optional[List[str]] = None,
):
    table_full = f"{catalog}.{schema}.{table}"
    writer = df.write.format("delta").mode("overwrite")
    if partition_cols:
        writer = writer.partitionBy(*partition_cols)
    if standard_path:
        writer.save(standard_path)
        spark.sql(
            f"CREATE TABLE IF NOT EXISTS {table_full} USING DELTA LOCATION '{standard_path}'"
        )
    else:
        writer.saveAsTable(table_full)
    return table_full


def run_dbt(dbt_project: str, profiles_dir: Optional[str], models: Optional[str]) -> int:
    cmd = ["dbt", "run", "--project-dir", dbt_project]
    if profiles_dir:
        cmd += ["--profiles-dir", profiles_dir]
    if models:
        cmd += ["--models", models]
    result = subprocess.run(cmd, check=False)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Local-first Databricks ingestion adapter")
    parser.add_argument(
        "--ingestion-yml",
        required=True,
        help="Path to generated ingestion.yml",
    )
    parser.add_argument("--input-file", help="Local file to upload to landing path")
    parser.add_argument("--landing-only", action="store_true", help="Only push to landing path")
    parser.add_argument(
        "--use-databricks-sdk",
        action="store_true",
        help="Upload to Volumes using databricks-sdk instead of local copy",
    )
    parser.add_argument("--env-config", help="Path to YAML with environment overrides")
    parser.add_argument("--landing-base", help="Landing base path")
    parser.add_argument("--raw-base", help="Raw base path")
    parser.add_argument("--standard-catalog", help="Standard catalog name")
    parser.add_argument("--standard-schema", help="Standard schema name (default: standard_<process_domain>)")
    parser.add_argument("--standard-table", help="Standard table name (default: <process_name>)")
    parser.add_argument("--standard-path-base", help="Optional standard path base (dbfs:/...) for table storage")
    parser.add_argument("--run-dbt", action="store_true", help="Run dbt after loading standard table")
    parser.add_argument("--dbt-project", help="Path to dbt project")
    parser.add_argument("--dbt-models", help="dbt models selector")
    parser.add_argument("--profiles-dir", help="dbt profiles dir")
    args = parser.parse_args()

    load_dotenv(Path.cwd() / ".env")

    cfg = load_ingestion_config(Path(args.ingestion_yml))
    env_cfg = load_env_config(args.env_config)

    landing_base = pick_setting(
        args.landing_base,
        "COI_DBX_LANDING_BASE",
        env_cfg,
        "",
    )
    raw_base = pick_setting(
        args.raw_base,
        "COI_DBX_RAW_BASE",
        env_cfg,
        "",
    )
    standard_catalog = pick_setting(
        args.standard_catalog,
        "COI_DBX_STANDARD_CATALOG",
        env_cfg,
        "",
    )
    standard_schema_override = pick_setting(
        args.standard_schema,
        "COI_DBX_STANDARD_SCHEMA",
        env_cfg,
        "",
    )
    standard_table_override = pick_setting(
        args.standard_table,
        "COI_DBX_STANDARD_TABLE",
        env_cfg,
        "",
    )
    standard_path_base = pick_setting(
        args.standard_path_base,
        "COI_DBX_STANDARD_PATH_BASE",
        env_cfg,
        "",
    )

    if not standard_catalog:
        standard_catalog = os.environ.get("DATABRICKS_DEFAULT_CATALOG", "") or env_cfg.get(
            "DATABRICKS_DEFAULT_CATALOG", ""
        )
    if not standard_catalog:
        raise ValueError(
            "Standard catalog must be set via COI_DBX_STANDARD_CATALOG or DATABRICKS_DEFAULT_CATALOG."
        )

    if not standard_schema_override:
        standard_schema_override = os.environ.get("DATABRICKS_DEFAULT_SCHEMA", "") or env_cfg.get(
            "DATABRICKS_DEFAULT_SCHEMA", ""
        )

    if not landing_base:
        if not standard_schema_override:
            raise ValueError(
                "Standard schema must be set via COI_DBX_STANDARD_SCHEMA or DATABRICKS_DEFAULT_SCHEMA."
            )
        landing_base = f"/Volumes/{standard_catalog}/{standard_schema_override}/landing"

    if not raw_base:
        if not standard_schema_override:
            raise ValueError(
                "Standard schema must be set via COI_DBX_STANDARD_SCHEMA or DATABRICKS_DEFAULT_SCHEMA."
            )
        raw_base = f"/Volumes/{standard_catalog}/{standard_schema_override}/raw"

    landing_path = str(cfg.l2r.get("landing_path", "")).strip("/")
    file_pattern = str(cfg.l2r.get("file_pattern", "*")).strip()

    landing_dir = f"{landing_base.rstrip('/')}/{landing_path}"
    landing_dir_local = dbfs_to_local(landing_dir)

    raw_files: List[str] = []

    if args.input_file:
        src = os.path.abspath(args.input_file)
        dest_name = os.path.basename(src)
        if args.use_databricks_sdk:
            landing_volume_dest = f"{landing_dir.rstrip('/')}/{dest_name}"
            upload_via_databricks_sdk(src, landing_volume_dest)
            print(f"Uploaded to landing via SDK: {landing_volume_dest}")
        else:
            dest = os.path.join(landing_dir_local, dest_name)
            copy_file(src, dest)
            print(f"Uploaded to landing: {dest}")

    if args.landing_only:
        print(f"Landing push complete. Files in: {landing_dir}")
        return 0

    process_date = datetime.utcnow().replace(tzinfo=timezone.utc)
    raw_dir = (
        f"{raw_base.rstrip('/')}/{cfg.process_domain}/{cfg.process_name}/"
        f"{raw_timestamp_subdir(process_date)}"
    )

    if args.use_databricks_sdk:
        if not args.input_file:
            raise ValueError("--input-file is required when --use-databricks-sdk is set.")
        dest_name = os.path.basename(os.path.abspath(args.input_file))
        raw_volume_dest = f"{raw_dir.rstrip('/')}/{dest_name}"
        upload_via_databricks_sdk(os.path.abspath(args.input_file), raw_volume_dest)
        print(f"Uploaded to raw via SDK: {raw_volume_dest}")
        raw_files = [raw_volume_dest]
    else:
        raw_dir_local = dbfs_to_local(raw_dir)

        ensure_dir(raw_dir_local)

        landing_files = list_matching_files(landing_dir_local, file_pattern)
        if not landing_files:
            raise FileNotFoundError(f"No landing files found in {landing_dir_local} matching {file_pattern}")

        for lf in landing_files:
            dest = os.path.join(raw_dir_local, os.path.basename(lf))
            copy_file(lf, dest)
            raw_files.append(dest)

    _ensure_pyspark()
    spark = SparkSession.builder.getOrCreate()

    df = read_raw_to_df(spark, cfg.r2s, raw_files[0])
    df, partition_cols = add_ingestion_columns(df, cfg.r2s, raw_files[0], process_date)

    if not standard_schema_override:
        raise ValueError(
            "Standard schema must be set via COI_DBX_STANDARD_SCHEMA or DATABRICKS_DEFAULT_SCHEMA."
        )
    standard_schema = standard_schema_override
    standard_table = standard_table_override or cfg.process_name
    ensure_schema_exists(spark, standard_catalog, standard_schema)

    standard_path = None
    if standard_path_base:
        standard_path = f"{standard_path_base.rstrip('/')}/{standard_schema}/{standard_table}"

    table_full = write_standard_table(
        df,
        spark,
        standard_catalog,
        standard_schema,
        standard_table,
        standard_path,
        partition_cols=partition_cols,
    )

    row_count = df.count()
    print(f"Standard table loaded: {table_full} (rows={row_count})")

    if args.run_dbt:
        if not args.dbt_project:
            raise ValueError("--dbt-project is required when --run-dbt is set")
        rc = run_dbt(args.dbt_project, args.profiles_dir, args.dbt_models)
        print(f"dbt run completed with exit code {rc}")
        return rc

    return 0


if __name__ == "__main__":
    main()
