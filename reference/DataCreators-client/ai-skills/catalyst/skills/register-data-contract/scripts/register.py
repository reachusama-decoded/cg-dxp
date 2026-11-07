#!/usr/bin/env python3
"""Register or update the ODCS contract.yaml for a data product.

Binds RFD 0009. Writes to
`<product-path>/contract/contract.yaml` per the minimal ODCS v3 shape.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
AVAILABILITY_RE = re.compile(r"^\d+(\.\d+)?%$")
FRESHNESS_RE = re.compile(r"^P(T\d+[HMS])+$")


def _load_schema(schema_file: Path) -> dict[str, Any]:
    if not schema_file.exists():
        raise FileNotFoundError(f"schema file not found: {schema_file}")
    data = yaml.safe_load(schema_file.read_text()) or {}
    if not isinstance(data, dict):
        raise ValueError("schema file must be a mapping with 'properties'")
    return data


def _resolve_domain_dataset(product_path: Path) -> tuple[str, str]:
    product_yaml = product_path / "product.yaml"
    if product_yaml.exists():
        data = yaml.safe_load(product_yaml.read_text()) or {}
        domain = data.get("domain")
        dataset = data.get("dataset")
        if domain and dataset:
            return str(domain), str(dataset)
    # Fall back to path: data-products/<domain>/datasets/<product>/
    parts = product_path.resolve().parts
    try:
        dp_idx = parts.index("data-products")
        return parts[dp_idx + 1], parts[dp_idx + 3]
    except (ValueError, IndexError) as exc:
        raise ValueError(
            "could not resolve domain/dataset from product.yaml or path"
        ) from exc


def _bump_patch(version: str) -> str:
    if not VERSION_RE.match(version):
        return "3.0.0"
    major, minor, patch = version.split(".")
    return f"{major}.{minor}.{int(patch) + 1}"


def _validate(contract: dict[str, Any]) -> None:
    if not VERSION_RE.match(contract.get("version", "")):
        raise ValueError(f"invalid version: {contract.get('version')!r}")
    for key in ("domain", "dataset"):
        value = contract.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"missing or empty {key}")
    body = contract.get("contract") or {}
    owner = (body.get("owner") or {}).get("team")
    if not isinstance(owner, str) or not owner:
        raise ValueError("missing owner.team")
    sla = body.get("sla") or {}
    availability = sla.get("availability", "")
    if not AVAILABILITY_RE.match(str(availability)):
        raise ValueError(f"invalid sla.availability: {availability!r}")
    freshness = sla.get("freshness", "")
    if not FRESHNESS_RE.match(str(freshness)):
        raise ValueError(
            f"invalid sla.freshness (expected ISO 8601 duration like PT15M): "
            f"{freshness!r}"
        )
    schema = body.get("schema") or {}
    props = schema.get("properties")
    if not isinstance(props, list) or not props:
        raise ValueError("schema.properties must be a non-empty list")
    for i, prop in enumerate(props):
        if not isinstance(prop, dict):
            raise ValueError(f"schema.properties[{i}] must be a mapping")
        if not prop.get("name") or not prop.get("logicalType"):
            raise ValueError(
                f"schema.properties[{i}] missing name or logicalType"
            )


def build_and_validate(
    product_path: Path,
    owner_team: str,
    sla_availability: str,
    sla_freshness: str,
    schema_file: Path,
) -> dict[str, Any]:
    """Construct and validate the ODCS contract dict. Does not write."""
    domain, dataset = _resolve_domain_dataset(product_path)
    schema_data = _load_schema(schema_file)
    properties = schema_data.get("properties")

    contract_path = product_path / "contract" / "contract.yaml"
    if contract_path.exists():
        existing = yaml.safe_load(contract_path.read_text()) or {}
        version = _bump_patch(str(existing.get("version", "3.0.0")))
    else:
        version = "3.0.0"

    contract = {
        "version": version,
        "domain": domain,
        "dataset": dataset,
        "status": "draft",
        "contract": {
            "owner": {"team": owner_team},
            "sla": {
                "availability": sla_availability,
                "freshness": sla_freshness,
            },
            "schema": {"properties": properties},
        },
    }
    _validate(contract)
    return contract


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Register or update the ODCS contract.yaml for a data product"
    )
    parser.add_argument("--product-path", required=True, type=Path)
    parser.add_argument("--owner-team", required=True)
    parser.add_argument("--sla-availability", required=True)
    parser.add_argument("--sla-freshness", required=True)
    parser.add_argument("--schema-file", required=True, type=Path)
    args = parser.parse_args(argv)

    if not args.product_path.exists():
        print(f"product path not found: {args.product_path}", file=sys.stderr)
        return 2
    if not args.schema_file.exists():
        print(f"schema file not found: {args.schema_file}", file=sys.stderr)
        return 2

    try:
        contract = build_and_validate(
            product_path=args.product_path,
            owner_team=args.owner_team,
            sla_availability=args.sla_availability,
            sla_freshness=args.sla_freshness,
            schema_file=args.schema_file,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    contract_dir = args.product_path / "contract"
    contract_dir.mkdir(parents=True, exist_ok=True)
    out = contract_dir / "contract.yaml"
    out.write_text(yaml.safe_dump(contract, sort_keys=False))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
