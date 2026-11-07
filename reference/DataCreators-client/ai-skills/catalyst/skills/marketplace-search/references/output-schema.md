# Output Schema

The marketplace CLI emits JSON whose structure is fully described by JSON Schema. The schema is the source of truth for what fields exist, what types they are, and which are required vs optional. Anywhere this doc and `--schema` disagree, `--schema` wins.

## Live access

Get the current schema at any time:

```bash
python -m skills.clients.marketplace --schema search
python -m skills.clients.marketplace --schema details
```

## `search` output (high-level)

| Field | Type | Required | Notes |
|---|---|---|---|
| `items` | `list[Entity]` | yes | May be empty (no matches). |
| `total_count` | `int` | yes | Total across all pages. |
| `current_page` | `int` | yes | 1-indexed. |
| `page_size` | `int` | yes | |
| `total_pages` | `int` | yes | |

## `details` output (high-level)

| Field | Type | Required | Notes |
|---|---|---|---|
| `entity` | `Entity` | yes | See Entity below. |
| `_meta` | `ResponseMeta` | yes | Provenance — fetched_at, endpoints_called, schema_version. |

## `Entity`

| Field | Type | Notes |
|---|---|---|
| `entity_id` | `int` | Marketplace entity ID. |
| `name` | `str` | |
| `description` | `str` | May be empty string but not null. |
| `type` | `EntityType` | `{code, label}` pair. |
| `platform` | `Platform` | `{code, name}` pair. |
| `validated` | `bool` | |
| `health` | `Health` | `{rating, status}`; status is "unrated" when rating is null. |
| `ancestry` | `list[str]` | Hierarchy from root to parent. May be `[]`. |
| `detail_url` | `str` | Deep link to the marketplace UI. |
| `search_rank` | `float \| null` | Set by `search()`; null after `details()`. |
| `sources` | `dict[str, list[str]] \| null` | Populated only by `details()`. Keys: `dremio`, `glue`, `s3`. |
| `access` | `AccessInfo \| null` | Populated by `details()` or `search(with_access=True)`. |
| `schema` | `SchemaInfo \| null` | `details()` only. |
| `business_terms` | `list[BusinessTerm] \| null` | `details()` only. |
| `preview` | `PreviewData \| null` | `details()` only. |

## `AccessInfo`

| Field | Type | Notes |
|---|---|---|
| `has_access` | `bool` | True if current user has read access. |
| `entitlements` | `list[str]` | AD entitlement names (verbatim). May be `[]`. |
| `request_access_url` | `str` | Deep link to the marketplace UI's request page. |
| `platform_code` | `str` | "CSPN" or "LASR" (or future). |

## `_meta`

```json
{"fetched_at": "ISO8601", "endpoints_called": 6, "schema_version": "1.0"}
```

`schema_version` will bump if the output structure changes in a non-backwards-compatible way.

## How to use the schema

For programmatic consumers (or strict agents):

```bash
python -m skills.clients.marketplace --schema details > schema.json
python -m skills.clients.marketplace details 683 --json > result.json
.venv/bin/python -c "import json, jsonschema; \
  jsonschema.validate(json.load(open('result.json')), json.load(open('schema.json')))"
```

If validation fails, the marketplace API has changed — refresh per `connection-marketplace.md`.
