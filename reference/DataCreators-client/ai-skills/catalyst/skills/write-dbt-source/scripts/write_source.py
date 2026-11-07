#!/usr/bin/env python3
"""Write a dbt sources YAML for a data product.

Usage:
    write_source.py --product data-products/<domain>/datasets/<product>/
                    --source-name <snake_case>
                    --schema <uc_schema>
                    --tables <table> [--tables <table> ...]
                    [--layer staging]
                    [--catalog <uc_catalog>]

Renders `<product>/dbt/<layer>/_<layer>__sources.yml` declaring
the named source tables as Unity Catalog external tables
(SQL-DBSQL-005). Uses `<<VAR>>` placeholder substitution, mirroring
generate-dag.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR.parent / "templates"

_PLACEHOLDER = re.compile(r"<<([A-Z_][A-Z0-9_]*)>>")
_SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")

RULE_IDS = ["SQL-DBSQL-005", "PY-NAMING-001"]


def render(template_text: str, context: dict[str, str]) -> str:
    def _sub(m: re.Match[str]) -> str:
        key = m.group(1)
        if key not in context:
            raise KeyError(f"unknown template variable: {key}")
        return context[key]

    return _PLACEHOLDER.sub(_sub, template_text)


def _load_product_yaml(product: Path) -> dict[str, Any]:
    yaml_path = product / "specs" / "product.yaml"
    if not yaml_path.is_file():
        print(
            f"write-dbt-source: missing product metadata at {yaml_path}. "
            "Run scaffold-data-product first or create specs/product.yaml.",
            file=sys.stderr,
        )
        sys.exit(2)
    data = yaml.safe_load(yaml_path.read_text()) or {}
    for key in ("domain", "product", "owner"):
        if key not in data:
            print(
                f"write-dbt-source: {yaml_path} missing required key {key!r}.",
                file=sys.stderr,
            )
            sys.exit(2)
    return data


def _render_tables(tables: list[str], schema: str) -> str:
    """Render the indented `tables:` list body for the template."""
    lines: list[str] = []
    for name in tables:
        lines.append(f"      - name: {name}")
        lines.append(
            f'        description: "External source table {schema}.{name} '
            'registered via a Unity Catalog external location (SQL-DBSQL-005)."'
        )
        lines.append(
            f'        external:\n          location: "REPLACE_WITH_EXTERNAL_LOCATION_URI"'
        )
        lines.append("        loaded_at_field: _ingested_at")
        lines.append("        freshness:")
        lines.append("          warn_after: { count: 2, period: hour }")
        lines.append("          error_after: { count: 12, period: hour }")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Render a SQL-DBSQL-005 compliant dbt sources YAML for a data "
            "product."
        )
    )
    parser.add_argument("--product", required=True)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--layer", default="staging")
    parser.add_argument("--catalog", default=None)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--tables", action="append", required=True)
    args = parser.parse_args(argv)

    if not _SNAKE_CASE.match(args.source_name):
        print(
            f"write-dbt-source: --source-name {args.source_name!r} is not "
            "snake_case (PY-NAMING-001). Use lowercase letters, digits, "
            "and underscores; must start with a letter.",
            file=sys.stderr,
        )
        sys.exit(2)

    if not _SNAKE_CASE.match(args.layer):
        print(
            f"write-dbt-source: --layer {args.layer!r} is not snake_case "
            "(PY-NAMING-001).",
            file=sys.stderr,
        )
        sys.exit(2)

    product = Path(args.product).resolve()
    metadata = _load_product_yaml(product)
    domain = metadata["domain"]

    meta = metadata.get("meta") or {}
    catalog = args.catalog or meta.get("uc_catalog") or domain

    context = {
        "SOURCE_NAME": args.source_name,
        "CATALOG": catalog,
        "SCHEMA": args.schema,
        "TABLES": _render_tables(args.tables, args.schema),
    }

    layer_dir = product / "dbt" / args.layer
    layer_dir.mkdir(parents=True, exist_ok=True)
    out_path = layer_dir / f"_{args.layer}__sources.yml"

    rendered = render(
        (TEMPLATES_DIR / "sources.yml.tmpl").read_text(), context
    )
    out_path.write_text(rendered)

    print(f"wrote {out_path}")
    print("satisfies: " + ", ".join(RULE_IDS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
