---
name: fetch-confluence
description: >
  Fetch and parse Confluence pages as Markdown context. Trigger phrases:
  "fetch this confluence page", "get the spec from confluence",
  "pull confluence content", "read page 12345678".
allowed-tools: Read Bash
metadata:
  tier: capability
  lifecycle-phase: none
  dependencies: []
  consumes: []
  shared-components:
    core: [fetch_confluence_page]
    platforms: [confluence]
---

# Fetch Confluence

Retrieve Confluence page(s) specified in $ARGUMENTS and return their
content as clean Markdown for use as context by other skills.

## Instructions

1. Parse $ARGUMENTS:
   - Collect one or more numeric page IDs.
   - Check for `--children` flag -- if present, include child pages.

2. For each page ID, call `fetch_confluence_page()` from
   `skills/core/confluence.py`:

   ```python
   from skills.clients.confluence import ConfluenceClient
   from skills.core.confluence import fetch_confluence_page

   client = ConfluenceClient(
       base_url=CONFLUENCE_BASE_URL,
       username=CONFLUENCE_USERNAME,
       api_token=CONFLUENCE_API_TOKEN,
   )
   markdown = fetch_confluence_page(
       client,
       page_id=page_id,
       include_children=include_children,
   )
   ```

   The function converts Confluence HTML storage format to Markdown.
   Child pages are appended in pre-order, separated by `---`.

3. Return the Markdown content directly. Do not summarize or truncate --
   downstream skills need the full text.

4. If the user does not provide a page ID, ask: "What is the Confluence
   page ID? You can find it in the page URL: `/pages/<page-id>/`."

## Output Format

Return the raw Markdown content of the fetched page(s), followed by a
source attribution line:

```markdown
# Source System Documentation -- Client Positions Feed

## Overview

The Client Positions feed is a daily flat-file extract from Aladdin...

---

> _Fetched from Confluence page [12345678] -- use this content as
> context for the next skill._
```

## Error Handling

- **Confluence not configured** -- tell the user: "Confluence credentials
  are not configured. Set `CONFLUENCE_BASE_URL`, `CONFLUENCE_USERNAME`,
  and `CONFLUENCE_API_TOKEN` in your `.env` file." Offer to proceed if
  the user can paste the page content manually.
- **Page not found (404)** -- report the page ID and suggest verifying
  the ID is correct and the user has access.
- **Authentication failure (401/403)** -- suggest checking the API token
  and username.
- **Large pages** -- if the page is very large, return it in full but
  warn the user about context window usage.

## Standalone Usage

```
/fetch-confluence 12345678
/fetch-confluence 12345678 87654321 --children
```

## Composition

`fetch-confluence` is the **capability-tier** primitive and the single owner of
the fetch (`fetch_confluence_page()` call, HTML→Markdown conversion, child-page
handling, error paths). It is wrapped by:

- `load-confluence-context` (workflow) — adds cross-phase lifecycle framing and
  delegates the fetch here instead of reimplementing it; the standard entry
  point for orchestrators such as `dplc-discovery`.
- Any other orchestrator that needs Confluence-hosted requirements as input.

## Dependencies

- `skills/core/confluence.py` -- `fetch_confluence_page()`
- `skills/clients/confluence.py` -- `ConfluenceClient`
- Environment: `CONFLUENCE_BASE_URL`, `CONFLUENCE_USERNAME`,
  `CONFLUENCE_API_TOKEN`
