# Interpretation Rules — Don't Infer

The marketplace CLI emits structured JSON with code-label pairs and explicit nulls *because* the agent should not have to guess at meaning. These rules tell the agent how to render the output without making things up.

## Treat null as null

If a field is `null`, render the explicit alternative.

| Field | If null, render |
|---|---|
| `health.rating` | "unrated" (use `health.status` directly — it already says "unrated") |
| `description` | "(no description)" — do not invent one. |
| `business_terms` | "no business terms linked" |
| `preview.rows` | "preview unavailable" |

Do **not** say "low quality," "unknown," "not applicable," or "missing." Use the explicit alternative.

## Don't parse entitlement strings

`CPZ_PRD_AA00002933_IM_MGRTRANSPOS_READ` is the AD entitlement name — render it verbatim. Do not parse the segments. Do not say:

- "the production environment entitlement" (don't infer `PRD` means production)
- "approval ticket AA00002933"
- "for IM team" or "for Manager Transactions Position table"

The user's IAM team knows what the string means; passing it through unmolested is the correct behavior.

## Empty arrays mean "none," not "unknown"

| Field empty | Means |
|---|---|
| `entitlements: []` | Access requires no entitlement (publicly accessible OR row-level / view-level only). NOT "entitlement details unavailable." |
| `business_terms: []` | No business glossary terms linked to this dataset. NOT "glossary not loaded." |
| `ancestry: []` | Top-level entity (no parent in hierarchy). NOT "hierarchy missing." |
| `items: []` (in search results) | Zero matches. NOT "search failed." |

## Access status

`access.has_access: false` means **the current authenticated user does not have read access right now**. Direct them to `access.request_access_url`. Do not:

- Promise access will be granted.
- Estimate request approval timelines.
- Guess at why they don't have access.

`access.has_access: true` means **the current authenticated user has read access now**. State that simply; do not assume it's a "fresh grant" or "permanent."

## Search rank

`search_rank` is a relevance score within the result set, not a probability or a percentage. Thresholds in the skill (`> 0.5 STOP`, `> 0.1 INVESTIGATE`, else `PROCEED`) are calibrated. Do **not**:

- Translate to percentages ("16% match")
- Add your own thresholds
- Compare ranks across different search queries (they aren't normalized)

A negative rank (yes, the API returns these) means "very weak match" — treat as `≤ 0.1`.

## When a field is missing from the response

If a field that should be present (per the JSON Schema) is missing or returns null when not expected, say so explicitly to the user:

> The marketplace API didn't return `<field>` for this entity. This usually means the field hasn't been populated; check the marketplace UI for the most current information.

Do not fill in from prior context, general knowledge, or the previous result.

## Type and platform codes

Always use the `label`/`name` form when speaking to the user:

- `"type": {"code": "dataset_table", "label": "Dataset Table"}` → say "Dataset Table"
- `"platform": {"code": "CSPN", "name": "Caspian"}` → say "Caspian"

Reserve the codes for technical contexts (logs, debugging, follow-up CLI calls).

## When in doubt

If you cannot decide what to render, paste the raw JSON for that field with a one-line note: "Verbatim from marketplace API." Better honest than wrong.
