---
name: load-confluence-context
description: "Retrieve Confluence pages as Markdown context. Use when requirements, designs, or background information for a data product live in Confluence pages."
allowed-tools: Read Grep Bash
metadata:
  tier: workflow
  lifecycle-phase: cross-cutting
  dependencies:
    - fetch-confluence
  consumes: []
  shared-components:
    core: []
    platforms: [confluence]
---

# Load Confluence Context

Retrieve the Confluence page(s) specified in $ARGUMENTS and return their
content as clean Markdown, ready to use as context for artifact generation.

This is a **cross-phase utility skill**.  Call it early in any phase when the
user says "the requirements are in Confluence" or "see page 12345678".  The
retrieved content grounds downstream skills in documented decisions rather than
relying on the user to manually copy text into the conversation.

`load-confluence-context` is the **workflow-tier** entry point.  It does not fetch
pages itself — it delegates the retrieval to the capability skill
`fetch-confluence` and wraps it with the lifecycle framing below.  Higher tiers
compose lower tiers (see `skills/README.md`); the fetch logic lives in exactly
one place.

## Lifecycle Context

This skill is a context-loader.  It has no fixed phase — use it whenever a
Confluence page holds information needed to generate an AI Catalyst artifact:

| Scenario | Example page | Use the content for |
|:---------|:-------------|:--------------------|
| Phase 1 Triage | Business request or demand tracker | `demand-tracker-entry`, `consumer-use-case-map` |
| Phase 2 Discovery | Source system documentation | `feasibility-report` |
| Phase 3 Design | Architecture decision record | `data-contract`, `architecture-diagram` |
| Phase 4 Build | Technical design spec | `transformation-spec` |

## Instructions

1. Parse $ARGUMENTS:
   - Collect one or more numeric page IDs.
   - Check for `--children` flag — if present, pass it through to the fetch.

2. Hand off the fetch to the `fetch-confluence` capability skill: read
   `skills/fetch-confluence/SKILL.md` and follow it (or invoke it via the
   `Skill` tool), passing the page IDs and any `--children` flag.  Do **not**
   call `fetch_confluence_page()` or construct a `ConfluenceClient` here —
   `fetch-confluence` owns the retrieval, the HTML-storage→Markdown conversion
   (`markitdown` with a regex fallback), child-page handling, and the
   not-configured / 404 / 401 error paths.  This skill must not reimplement
   them.

3. Return the Markdown that `fetch-confluence` produces, unchanged.  Do not
   summarise or truncate — downstream skills need the full text.

4. If the user does not provide a page ID, ask: "What is the Confluence page ID?
   You can find it in the page URL: `/pages/<page-id>/`."  (Asking here avoids
   an empty hand-off; `fetch-confluence` prompts the same way as a backstop.)

## Output Format

Return the raw Markdown `fetch-confluence` emits — the page content followed by
its one-line source-attribution note:

```markdown
# Source System Documentation — Client Positions Feed

## Overview

The Client Positions feed is a daily flat-file extract from Aladdin...

## Schema

| Column | Type | Description |
|:-------|:-----|:------------|
| client_id | integer | Unique client identifier |
...

---

# Child Page: Data Dictionary

...

---

> _Fetched from Confluence page [12345678] — use this content as context for the next skill._
```

## Composition

- **Wraps:** `fetch-confluence` (capability) — the single owner of the fetch.
- **Used by:** `dplc-discovery` (Phase 2) and any phase orchestrator that needs
  Confluence-hosted requirements, designs, or source docs as input.

## Dependencies

- `fetch-confluence` (capability skill) — performs the actual page retrieval.
- Transitively, through `fetch-confluence`: `skills/core/confluence.py`
  (`fetch_confluence_page()`), `skills/clients/confluence.py`
  (`ConfluenceClient`), and the `CONFLUENCE_BASE_URL`, `CONFLUENCE_USERNAME`,
  `CONFLUENCE_API_TOKEN` environment variables.
