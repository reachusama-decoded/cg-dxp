#!/usr/bin/env python3
"""Generate ingestion.yml from profiling_output.md.

Avoids shell heredoc issues by running as a standalone script.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_profile_table(profile_text: str) -> list[dict[str, str]]:
    start_marker = None
    if "## Profiling Table" in profile_text:
        start_marker = "## Profiling Table"
    elif "## Column Profiles" in profile_text:
        start_marker = "## Column Profiles"
    elif "## Schema Profile" in profile_text:
        start_marker = "## Schema Profile"

    if start_marker:
        start = profile_text.index(start_marker)
        sub = profile_text[start:]
    else:
        # Fallback: use the whole file and let the table parser pick up rows
        sub = profile_text
    lines = sub.splitlines()
    rows = [ln for ln in lines if ln.strip().startswith("|")]
    if len(rows) < 3:
        raise ValueError("Profiling table not found or empty")
    header = [h.strip() for h in rows[0].strip("|").split("|")]
    header_map = {
        "Column": "Column Name",
        "Column Name": "Column Name",
        "Data Type": "Data Type",
        "Null Count": "Null Count",
    }
    normalized_header = [header_map.get(h, h) for h in header]
    records: list[dict[str, str]] = []
    for ln in rows[2:]:
        parts = [p.strip() for p in ln.strip("|").split("|")]
        if len(parts) != len(normalized_header):
            continue
        records.append(dict(zip(normalized_header, parts)))
    return records


# Map of special characters/sequences to meaningful replacements.
_SPECIAL_CHAR_MAP = [
    (">=", "gte"),
    ("<=", "lte"),
    ("!=", "ne"),
    ("%", "pct"),
    ("#", "num"),
    ("$", "amt"),
    ("&", "and"),
    ("@", "at"),
    ("+", "plus"),
    ("/", "per"),
    (">", "gt"),
    ("<", "lt"),
    ("=", "eq"),
]


def normalize_alias(col: str) -> str:
    """Convert a column name to a safe lowercase alias.

    - Known special chars get meaningful names (% → pct, # → num, etc.)
    - Remaining non-alphanumeric chars → '_'
    - Leading digits get 'n' prefix (e.g. '1 YR' → 'n1_yr')
    - Collapses consecutive underscores
    """
    name = col.strip().lower()
    for char, replacement in _SPECIAL_CHAR_MAP:
        name = name.replace(char, f"_{replacement}_")
    alias = re.sub(r"[^a-z0-9_]", "_", name).strip("_")
    alias = re.sub(r"_+", "_", alias)
    if alias and alias[0].isdigit():
        alias = "n" + alias
    return alias


def build_ingestion_yaml(
    records: list[dict[str, str]],
    process_domain: str,
    process_name: str,
    file_pattern: str,
    landing_path: str,
    dc_tag: str,
    cron: str,
    delimiter: str,
    header: bool,
    skip_header_rows: int,
    skip_footer_rows: int,
) -> str:
    out: list[str] = []
    cron_value = cron.strip()
    event_based_values = {"unscheduled", "event", "event-based", "event_based"}
    is_event_based = cron_value.lower() in event_based_values
    schedule_cron = cron_value
    out.append("consuming_teams:")
    out.append("  - cg-open-itg/AA00002933_IMDELIVERY_APPROVERS")
    out.append(f"process_domain: {process_domain}")
    out.append(f"process_name: {process_name}")
    out.append("delivery_sla: timedelta(minutes=30)")
    out.append("file_tags:")
    out.append(f"  dc: {dc_tag}")
    out.append("cg_deequ:")
    out.append("  enable: true")
    out.append("  sns_notification: false")
    out.append("airflow_defaults:")
    out.append("  catchup: false")
    out.append("  depends_on_past: false")
    out.append("  email_on_failure: true")
    out.append("  email_on_retry: true")
    out.append("  owner: airflow")
    out.append("  retries: 3")
    out.append("  retry_delay: timedelta(seconds=30)")
    out.append('  start_date: datetime(2025,1,1,tzinfo=timezone("America/Los_Angeles"))')
    out.append("schedule_info:")
    if is_event_based:
        out.append("  cron: null")
        out.append("  unscheduled_event_driven: null")
    else:
        out.append(f"  cron: \"{schedule_cron}\"")
        out.append("  unscheduled_event_driven: false")
        cron_parts = schedule_cron.split()
        if len(cron_parts) == 5:
            day_part = cron_parts[4]
            day_map = {'mon': 'mo', 'tue': 'tu', 'wed': 'we', 'thu': 'th', 'fri': 'fr', 'sat': 'sa', 'sun': 'su'}
            days = day_part.replace('*', 'mo,tu,we,th,fr,sa,su')
            for full, abbr in day_map.items():
                days = days.replace(full, abbr)
            out.append(f"  days_of_week: {days}")
        else:
            out.append("  days_of_week: mo,tu,we,th,fr")
        out.append("  exclude_calendar: global_holidays")
        out.append("  run_calendar: None")
    out.append("l2r:")
    out.append(f"  file_pattern: {file_pattern}")
    out.append(f"  landing_path: {landing_path}")
    out.append("  sensor_timeout: 36000")
    out.append("r2s:")
    is_excel = any(file_pattern.lower().endswith(ext) for ext in (".xlsx", ".xls", "*.xlsx", "*.xls"))
    if is_excel:
        out.append("  file_format: excel")
        out.append(f"  header: {'true' if header else 'false'}")
        out.append("  skip_fix_encode: true")
    else:
        out.append(f"  delimiter: \"{delimiter}\"")
        out.append("  file_format: delimited")
        out.append(f"  header: {'true' if header else 'false'}")
        out.append('  escape: "\\""')
        out.append('  quote: "\\""')
        out.append("  multiLine: true")
        out.append("  skip_fix_encode: true")
    if not header and skip_header_rows:
        out.append(f"  skip_header_rows: {skip_header_rows}")
    if skip_footer_rows:
        out.append(f"  skip_footer_rows: {skip_footer_rows}")
    out.append("  schema:")

    seq = 5
    seen_aliases: dict[str, int] = {}
    for rec in records:
        col = rec.get("Column Name", "").strip()
        if not col:
            continue
        data_type = rec.get("Data Type", "string").strip()
        null_count_raw = rec.get("Null Count", "0")
        try:
            null_count = int(float(str(null_count_raw).replace(",", "")))
        except ValueError:
            null_count = 0
        is_nullable = "true" if null_count > 0 else "false"
        alias = normalize_alias(col)
        # Deduplicate: append _2, _3, … if alias already seen
        if alias in seen_aliases:
            seen_aliases[alias] += 1
            alias = f"{alias}_{seen_aliases[alias]}"
        else:
            seen_aliases[alias] = 1
        out.append(f"    - alias: {alias}")
        out.append(f"      data_type: {data_type}")
        # Quote field_name if it contains YAML-special characters
        _yaml_special = set('%#&@!*|>{}[]')
        if any(c in _yaml_special for c in col):
            out.append(f'      field_name: "{col}"')
        else:
            out.append(f"      field_name: {col}")
        out.append(f"      is_nullable: {is_nullable}")
        out.append("      metadata:")
        out.append("        data_concept: unknown")
        out.append("        is_sensitive: true")
        out.append(f"      seq: {seq}")
        seq += 5
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, help="Path to profiling_output.md")
    parser.add_argument("--output", required=True, help="Path to write ingestion.yml")
    parser.add_argument("--process-domain", required=True)
    parser.add_argument("--process-name", required=True)
    parser.add_argument("--file-pattern", required=True)
    parser.add_argument("--landing-path", required=True)
    parser.add_argument("--dc-tag", required=True)
    parser.add_argument("--cron", required=True)
    parser.add_argument("--delimiter", default="|")
    parser.add_argument("--header", action="store_true")
    parser.add_argument("--skip-header-rows", type=int, default=0)
    parser.add_argument("--skip-footer-rows", type=int, default=0)
    args = parser.parse_args()

    profile_path = Path(args.profile)
    output_path = Path(args.output)
    if output_path.is_dir():
        output_path = output_path / f"{args.process_name}.yml"
    elif output_path.name == "ingestion.yml":
        output_path = output_path.with_name(f"{args.process_name}.yml")
    records = parse_profile_table(profile_path.read_text())

    content = build_ingestion_yaml(
        records=records,
        process_domain=args.process_domain,
        process_name=args.process_name,
        file_pattern=args.file_pattern,
        landing_path=args.landing_path,
        dc_tag=args.dc_tag,
        cron=args.cron,
        delimiter=args.delimiter,
        header=args.header,
        skip_header_rows=args.skip_header_rows,
        skip_footer_rows=args.skip_footer_rows,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)
    print(f"Wrote: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
