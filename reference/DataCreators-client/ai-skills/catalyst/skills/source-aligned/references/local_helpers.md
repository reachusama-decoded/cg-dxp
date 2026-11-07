# Workspace-Local Helpers for Non-Flat-CSV Formats

The source-aligned skill ships a flat-CSV happy path. When the profile
step detects a format that doesn't fit (marker framing, multi-block
headers, request-response prefix columns, footer markers), the skill
scaffolds a workspace-local helper from
`templates/local_helper.py` rather than trying to handle the format
natively.

## When the skill scaffolds a helper

Triggers (any of):
- File extension `.out`, `.out.gz`, or other non-`csv`/`txt`/`dat` shape
- Profile detects `START-OF-DATA` / `END-OF-DATA` / `START-OF-FIELDS`
  markers, or comment-prefixed lines (`#`) inside the data block
- Header is multi-block (TIMESTARTED, FIELDS list, metadata) rather
  than a single delimiter-counted row
- Trailing footer block (`END-OF-DATA`, `TIMEFINISHED`, etc.)
- Request-response prefix columns (security identifier + return code)
  ahead of the actual business columns

## Where it lands

```
workspace/generated/source-aligned/<model_name>/ingestion/local_helper.py
```

The helper produces a flat CSV the standard ingestion pipeline
consumes. Wire it by pointing `ingestion.yml#l2r.file_pattern` at the
helper's output, not the raw file.

## Iteration loop

1. Fill in the TODOs in `local_helper.py` against your specific
   format.
2. Run it against a small slice of real data; confirm the output CSV
   has the columns and row count the profile step predicted.
3. Re-run the standard ingestion against the helper's output.
4. The live-data verification step (see SKILL.md "Order of Operations"
   step 11) runs against the helper output too.

## Graduation criteria — when to file an adapter ticket

Scaffold helpers are deliberately product-specific. They graduate to
first-class skill adapters only when:

- The same format shape (marker framing, prefix columns, footer block)
  appears in **3+ products** in the lake, OR
- A vendor publishes a format spec we expect to consume from going
  forward (Bloomberg POMS, Refinitiv DataScope, etc.) AND we have at
  least one product running on it today

File the adapter ticket under AI Catalyst with: pointer to the helper
files in `workspace/generated/source-aligned/.../local_helper.py`
across the affected products, a short note on what the common shape
looks like, and a proposed name for the adapter (e.g. `bloomberg-out`).

## Why not ship adapters preemptively

We don't have evidence yet that marker-framed Bloomberg feeds are a
category vs. a one-off. The helper-scaffolding approach lets us collect
evidence before committing to a registry shape. Replacing
`caspian-ingestion-libs` is out of scope — the helper coexists with
it; the helper just handles formats the platform library doesn't ship
support for.
