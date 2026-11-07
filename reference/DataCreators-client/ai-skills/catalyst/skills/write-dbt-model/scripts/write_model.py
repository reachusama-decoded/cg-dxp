#!/usr/bin/env python3
"""Write a compliant dbt model `.sql` file plus a per-layer `_<layer>__models.yml`
into a data product subtree.

Usage:
    write_model.py --product data-products/<domain>/datasets/<product>/
                   --model-name stg_orders
                   --layer staging
                   --materialization view
                   [--unique-key order_id]

The renderer uses a `<<VAR>>` placeholder marker (not Jinja) so dbt's
own `{{ ... }}` config blocks in the templates pass through untouched.

Standards satisfied:
  SQL-DBSQL-003 — incremental_strategy='merge' + unique_key
  SQL-DBSQL-005 — location_root config (external table)
  SQL-DBSQL-009 — VACUUM RETAIN 168 HOURS hint in rendered SQL
  PY-NAMING-*   — snake_case model names enforced
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR.parent / "templates"

_PLACEHOLDER = re.compile(r"<<([A-Z_][A-Z0-9_]*)>>")
_SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")

VALID_LAYERS = ("staging", "intermediate", "marts")
VALID_MATERIALIZATIONS = ("table", "view", "incremental")

RULE_IDS = [
    "SQL-DBSQL-003",
    "SQL-DBSQL-005",
    "SQL-DBSQL-009",
    "PY-NAMING",
]


def render(template_text: str, context: dict[str, str]) -> str:
    def _sub(m: re.Match[str]) -> str:
        key = m.group(1)
        if key not in context:
            raise KeyError(f"unknown template variable: {key}")
        return context[key]

    return _PLACEHOLDER.sub(_sub, template_text)


def _primary_column(model_name: str, unique_key: str | None) -> str:
    if unique_key:
        return unique_key
    # Heuristic: <name>_id is a reasonable default for a not_null test stub.
    base = model_name
    for prefix in ("stg_", "int_", "fct_", "dim_"):
        if base.startswith(prefix):
            base = base[len(prefix) :]
            break
    return f"{base}_id"


def _merge_yml(
    yml_path: Path, model_name: str, layer: str, primary_column: str
) -> str:
    """Return the yml text after inserting/replacing the model entry."""
    new_model = {
        "name": model_name,
        "description": f"TODO: describe {model_name} ({layer} layer).",
        "columns": [
            {
                "name": primary_column,
                "description": f"TODO: describe {primary_column}.",
                "tests": ["not_null"],
            }
        ],
    }
    if yml_path.is_file():
        data = yaml.safe_load(yml_path.read_text()) or {}
        if not isinstance(data, dict):
            data = {}
        data.setdefault("version", 2)
        models = data.setdefault("models", [])
        replaced = False
        for i, m in enumerate(models):
            if isinstance(m, dict) and m.get("name") == model_name:
                models[i] = new_model
                replaced = True
                break
        if not replaced:
            models.append(new_model)
    else:
        data = {"version": 2, "models": [new_model]}
    return yaml.safe_dump(data, sort_keys=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a SQL-DBSQL-compliant dbt model file."
    )
    parser.add_argument("--product", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--layer", required=True, choices=VALID_LAYERS)
    parser.add_argument(
        "--materialization", required=True, choices=VALID_MATERIALIZATIONS
    )
    parser.add_argument("--unique-key", default=None)
    args = parser.parse_args(argv)

    if not _SNAKE_CASE.match(args.model_name):
        print(
            f"write-dbt-model: --model-name {args.model_name!r} must be "
            "snake_case (PY-NAMING-*).",
            file=sys.stderr,
        )
        return 2

    if args.materialization == "incremental" and not args.unique_key:
        print(
            "write-dbt-model: --materialization=incremental requires "
            "--unique-key (SQL-DBSQL-003).",
            file=sys.stderr,
        )
        return 2

    product = Path(args.product).resolve()
    layer_dir = product / "dbt" / args.layer
    layer_dir.mkdir(parents=True, exist_ok=True)

    location_root = (
        f"{{{{ env_var('CATALYST_EXTERNAL_LOCATION_ROOT') }}}}/"
        f"{args.layer}/{args.model_name}"
    )

    context = {
        "MODEL_NAME": args.model_name,
        "LAYER": args.layer,
        "MATERIALIZATION": args.materialization,
        "LOCATION_ROOT": location_root,
        "UNIQUE_KEY": args.unique_key or "",
    }

    if args.materialization == "incremental":
        tmpl = (TEMPLATES_DIR / "model_incremental.sql.tmpl").read_text()
    else:
        tmpl = (TEMPLATES_DIR / "model.sql.tmpl").read_text()
    sql_text = render(tmpl, context)

    sql_path = layer_dir / f"{args.model_name}.sql"
    sql_path.write_text(sql_text)

    yml_path = layer_dir / f"_{args.layer}__models.yml"
    primary_column = _primary_column(args.model_name, args.unique_key)
    yml_text = _merge_yml(yml_path, args.model_name, args.layer, primary_column)
    yml_path.write_text(yml_text)

    print(f"wrote {sql_path}")
    print(f"wrote {yml_path}")
    print("satisfies: " + ", ".join(RULE_IDS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
