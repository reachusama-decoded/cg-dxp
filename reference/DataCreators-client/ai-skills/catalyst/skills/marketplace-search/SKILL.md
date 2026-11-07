---
name: marketplace-search
description: |
  Search the Capital Group marketplace for existing data products before triaging a new request. Use when the user asks "is there an existing data product for X?", "search the marketplace for Y", "what data products cover Z?", "before we build, check the marketplace for...", or any Phase 1 (Triage) step that needs to confirm a use case isn't already met.
allowed-tools: Read Grep Bash
metadata:
  tier: workflow
  lifecycle-phase: phase-1-triage
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: [marketplace]
---

# Marketplace Search

Search the marketplace for an existing data product matching $ARGUMENTS, before recommending the user build a new one.

## When to use

- Phase 1 (Triage) — confirming whether a request is already met by an existing product.
- Anytime someone asks "is there a data product for X?" or "what's available for Y?"
- When discussing scope of a new request — check first whether the work is already done.

## How it works

This skill calls a CLI: `python -m skills.clients.marketplace search`. The CLI handles authentication (one-time Okta SSO captured into a token cache outside the repo), API calls, and structured output. The skill itself is just orchestration.

## Workflow

1. **Run the search.** Use the Bash tool:
   ```bash
   python -m skills.clients.marketplace search "<keyword>" --json
   ```
   Replace `<keyword>` with a meaningful search term derived from the user's question. Prefer specific terms (e.g., `"client positions"`) over vague ones (e.g., `"client data"`).

2. **Handle the exit code.**

   - **Exit 0:** parse the JSON from stdout. Continue to step 3.
   - **Exit 2 or 3 (auth issue):** the user needs to log in. Tell the user verbatim:
     > Your marketplace login is missing or expired. Running login now will open a browser window so you can sign in via Okta SSO. The session is cached, so you should rarely have to do this. OK to proceed?

     If the user says yes, run `python -m skills.clients.marketplace login` (heads up: opens a browser; the script blocks until they close it). When login finishes, retry the original search ONCE. If it still returns exit 2/3, surface the error and stop — do NOT loop.

     If the user declines, stop and tell them how to run the login manually when ready.
   - **Exit 1 (other error):** read stderr, surface the message to the user.

3. **For each top result (up to 5), optionally fetch full details:**
   ```bash
   python -m skills.clients.marketplace details <entity_id> --json
   ```
   Use details when:
   - The user wants to know how to access the data (AD entitlements + request URL).
   - There's a strong match (`search_rank > 0.5`) and recommendation depends on health/validation.
   - The user asks "tell me more about this one."

4. **Apply the recommendation rule** based on the search rank of the top result:

   | Top result `search_rank` | Recommendation |
   |---|---|
   | `> 0.5` | **STOP** — strong match, point the requestor at it. |
   | `0.1` to `0.5` | **INVESTIGATE** — review existing before building. |
   | `≤ 0.1` or no items | **PROCEED** — no clear match; continue triage. |

5. **Consider pagination only when needed.** Search returns 25 results per page by default. The JSON output includes `total_pages` and `current_page`. **Don't paginate by default** — for triage ("does this already exist?"), if no strong match is on page 1, it almost certainly isn't anywhere. Only fetch additional pages when:
   - The user explicitly asks for "all results" or "more results."
   - The user's question is broad scope (e.g., "what data products cover risk?") and `total_pages > 1`.
   - Page 1 has matches but the user wants to see the full landscape.

   To fetch the next page:
   ```bash
   python -m skills.clients.marketplace search "<keyword>" --page 2 --json
   ```

   Or to get more results in one call (up to 100 should be safe):
   ```bash
   python -m skills.clients.marketplace search "<keyword>" --page-size 100 --json
   ```

   Don't loop through all pages without user confirmation — large result sets get noisy fast.

6. **Render results.** See `references/output-schema.md` for the full structured output format. See `references/interpretation-rules.md` for what each field means and what NOT to infer.

## Example output (representative)

```markdown
## Marketplace Search Results

Query: `client risk`

| Name | Type | Domain | Health | Rank |
|:-----|:-----|:-------|:-------|:----:|
| [Climate Value At Risk Scenario Analysis](https://marketplace.capgroup.com/entity/93) | Dataset | Investment Mgmt › Account Reference Data | unrated | 0.16 |
| [High Net Worth Investors](https://marketplace.capgroup.com/entity/...) | Data Domain | Client | unrated | 0.16 |
| [Instrument Equity Volatility](https://marketplace.capgroup.com/entity/...) | Dataset | Investment Mgmt | unrated | -0.79 |

### Recommendation

**INVESTIGATE** — `Climate Value At Risk Scenario Analysis` is a moderate match (rank 0.16). Review its scope before triaging a new request. To request access, see entitlement: run `python -m skills.clients.marketplace details 93 --json` for the AD group + request URL.
```

## See also

- `references/connection-marketplace.md` — auth/sniffer playbook (refresh procedure when the marketplace UI changes).
- `references/output-schema.md` — JSON Schema of CLI output.
- `references/interpretation-rules.md` — explicit "don't infer" rules.
- `references/verified-snippets.md` — example queries with captured outputs.
