#!/usr/bin/env python3
"""Scaffold a data-product subtree per RFD 0003.

Usage:
    scaffold.py --domain <name> --product <name> --team <alias>
                [--target-dir .] [--force]

Writes data-products/<domain>/datasets/<product>/{airflow,bundle,dbt,contract,specs}/
under --target-dir. Refuses to overwrite an existing tree unless --force is
passed. Domain and product must be lowercase snake_case (PY-NAMING-*).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR.parent / "templates"

NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")

SUBDIRS = ("airflow", "bundle", "dbt", "contract", "specs")

# (template_filename, target_relative_path_within_product_root)
FILE_PLAN: list[tuple[str, str]] = [
    ("README.md.j2", "README.md"),
    ("databricks.yml.j2", "bundle/databricks.yml"),
    ("dbt_project.yml.j2", "dbt/dbt_project.yml"),
]


def validate_name(value: str, *, field: str) -> str:
    """Enforce lowercase snake_case per PY-NAMING-*. Raises ValueError on miss."""
    if not NAME_RE.match(value):
        raise ValueError(
            f"--{field} must match {NAME_RE.pattern!r} (lowercase snake_case); "
            f"got {value!r}. See PY-NAMING-*."
        )
    return value


def render(template_text: str, context: dict[str, str]) -> str:
    def _sub(m: re.Match[str]) -> str:
        key = m.group(1)
        if key not in context:
            raise KeyError(f"unknown template variable: {key}")
        return context[key]

    return _PLACEHOLDER.sub(_sub, template_text)


def _product_root(target_dir: Path, domain: str, product: str) -> Path:
    return target_dir / "data-products" / domain / "datasets" / product


def _planned_paths(root: Path) -> list[Path]:
    return [root / rel for _, rel in FILE_PLAN]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a data-product subtree per RFD 0003."
    )
    parser.add_argument("--domain", required=True)
    parser.add_argument("--product", required=True)
    parser.add_argument("--team", required=True)
    parser.add_argument("--target-dir", default=".")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    try:
        validate_name(args.domain, field="domain")
        validate_name(args.product, field="product")
    except ValueError as exc:
        print(f"scaffold-data-product: {exc}", file=sys.stderr)
        return 2

    target_dir = Path(args.target_dir).resolve()
    root = _product_root(target_dir, args.domain, args.product)

    # Refuse if any planned artifact already exists, unless --force.
    if not args.force:
        existing = [p for p in _planned_paths(root) if p.exists()]
        if existing:
            print(
                "scaffold-data-product: refusing to overwrite existing tree. "
                "Re-run with --force to regenerate.",
                file=sys.stderr,
            )
            for p in existing:
                print(f"  conflict: {p}", file=sys.stderr)
            return 1

    # Create the five subdirectories. The three that ship without files
    # (airflow/, contract/, specs/) exist on disk as an affordance for the
    # next skill that will write into them; git won't track them until the
    # first real file lands. No .gitkeep markers — avoids the cleanup
    # churn of removing them later.
    for sub in SUBDIRS:
        (root / sub).mkdir(parents=True, exist_ok=True)

    context = {
        "domain": args.domain,
        "product": args.product,
        "team": args.team,
        "bundle_name": f"{args.domain}_{args.product}",
    }

    # Render and write the three stub files.
    for tmpl_name, rel_target in FILE_PLAN:
        out_path = root / rel_target
        out_path.parent.mkdir(parents=True, exist_ok=True)
        rendered = render((TEMPLATES_DIR / tmpl_name).read_text(), context)
        out_path.write_text(rendered)

    print(f"scaffolded {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
