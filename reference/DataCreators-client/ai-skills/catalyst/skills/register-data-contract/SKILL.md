---
name: register-data-contract
description: |
  Capability skill that creates or updates the ODCS (Open Data Contract
  Standard) `contract.yaml` for a scaffolded data product at
  `data-products/{domain}/datasets/{product}/contract/contract.yaml`. Binds
  RFD 0009 (Data Contract Standard). Validates required fields, SLA format,
  and ISO 8601 freshness; refuses to register on missing inputs.
  Trigger phrases: "register data contract", "create odcs contract",
  "write contract.yaml", "bind contract to product".
allowed-tools: Read Bash Write
metadata:
  tier: capability
  lifecycle-phase: phase-3-design
  dependencies:
    - scaffold-data-product
  consumes:
    - data-contract
  shared-components:
    core: []
    platforms: []
  standards: []
  binds-rfds:
    - "0009"
---

# register-data-contract

Create or update an ODCS contract file for a data product. Binds RFD 0009.

## When to use

- After `scaffold-data-product` has produced a product directory and the
  team needs to declare its contract.
- When updating an existing contract (owner, SLAs, schema). Re-running
  bumps the contract `version` patch digit deterministically.
- Before any DPLC Build-phase artifact references the contract path.

## Inputs

Required CLI flags:
- `--product-path PATH` -- path to the scaffolded product directory.
- `--owner-team STRING` -- producer team alias.
- `--sla-availability STRING` -- percentage like `99.5%`.
- `--sla-freshness STRING` -- ISO 8601 duration like `PT15M`.
- `--schema-file PATH` -- YAML/JSON file with `properties: [...]`.

The product directory is expected to contain `product.yaml` declaring
`domain` and `dataset`. If absent, those values are inferred from the path
(`data-products/{domain}/datasets/{product}/`).

## Outputs

- `contract/contract.yaml` written under the product path, conforming to
  the minimal ODCS v3 shape:

```yaml
version: 3.0.0
domain: <domain>
dataset: <product>
status: draft
contract:
  owner: {team: <team>}
  sla: {availability: <pct>, freshness: <iso8601>}
  schema:
    properties:
      - {name: ..., logicalType: ..., required: ...}
```

## Standards

None direct. This skill binds **RFD 0009 -- Data Contract Standard** and
enforces the ODCS v3 minimal shape required by that RFD.

## Procedure

1. Resolve `domain` and `dataset` from `product.yaml` (or path).
2. Load the schema file; assert it contains a non-empty `properties` list.
3. Build the ODCS dict.
4. Validate required fields, version pattern, SLA availability percent,
   and ISO 8601 freshness duration.
5. If `contract/contract.yaml` already exists, bump its patch digit;
   otherwise write `version: 3.0.0`.
6. Write the YAML; exit 0.

## Failure modes

- Missing `--schema-file` or unreadable -- exit 2.
- Invalid SLA freshness duration -- raises `ValueError("...freshness...")`.
- Invalid SLA availability percentage -- raises `ValueError`.
- Empty `properties` -- raises `ValueError`.
- Missing owner team -- raises `ValueError`.

## References

- RFD 0009 -- Data Contract Standard.
- Open Data Contract Standard (ODCS) v3 minimal shape.
