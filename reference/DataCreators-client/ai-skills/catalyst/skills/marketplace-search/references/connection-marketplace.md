---
tool: marketplace
auth: okta-sso
verified: 2026-04
env_vars:
  - name: MARKETPLACE_UI_BASE_URL
    default: https://marketplace.capgroup.com
    when_to_set: pointing at non-prod marketplace UI
  - name: MARKETPLACE_API_BASE_URL
    default: https://marketplace-service.datalake.aws.capgroup.com
    when_to_set: API host moves; or testing against a fixture server
sniffer:
  profile: "~/.cache/catalyst-marketplace/ (Linux/Mac) or %LOCALAPPDATA%\\catalyst-marketplace\\Cache\\ (Windows)"
  ui_url: https://marketplace.capgroup.com
  api_host_filter: marketplace-service.datalake.aws.capgroup.com
  refresh_procedure: spike/marketplace/sniffer.py
---

# Marketplace Connection Guide

This is the operational runbook for the marketplace platform — what you need to know when something stops working or when the API surface changes.

## Architecture

- **UI:** `marketplace.capgroup.com` — React SPA, served from CloudFront/S3
- **API:** `marketplace-service.datalake.aws.capgroup.com` — REST, JSON
- **Auth:** Okta OAuth (issuer `aus1p1am4dzppj7CF1d8`, client `0oa1p1ainm363zIs01d8`)

The SPA's `/env-vars` endpoint exposes `REACT_APP_EAST_BASE_URL` — the canonical source for the API host. The login bootstrap reads this on every login so a marketplace migration is auto-discovered.

## Verify the connection

```bash
python -m skills.clients.marketplace whoami
```

| Exit | Meaning |
|---|---|
| 0 | Token valid; API reachable. |
| 2 | Token expired — run `marketplace login`. |
| 3 | No token cached — run `marketplace login`. |
| 1 | Network/server error; check Capital Group network status. |

## Auth (Okta SSO via Playwright)

Tokens are short-lived Okta access JWTs (~60 min). Refresh path:

```bash
python -m skills.clients.marketplace login
```

Opens headed Chromium against the marketplace. User completes Okta SSO if prompted (often skipped if recently authenticated elsewhere). The script reads the bearer from `localStorage["okta-token-storage"]` and writes it to a platform-appropriate config location (mode 0600 on Linux/Mac; ACL-default on Windows):
- **Linux/Mac:** `~/.config/catalyst/marketplace.json`
- **Windows:** `%APPDATA%\catalyst\marketplace.json`

The persistent browser profile keeps the SSO session warm — most logins should not require re-entering credentials:
- **Linux/Mac:** `~/.cache/catalyst-marketplace/`
- **Windows:** `%LOCALAPPDATA%\catalyst-marketplace\Cache\`

## Verified snippets (each ends with the actual output captured)

### Search for "client risk"

```bash
python -m skills.clients.marketplace search "client risk" --page-size 3 --json
```

Output (snipped to relevant fields):

```json
{
  "items": [
    {
      "entity_id": 93,
      "name": "Climate Value At Risk Scenario Analysis",
      "type": {"code": "dataset", "label": "Dataset"},
      "platform": {"code": "CSPN", "name": "Caspian"},
      "search_rank": 0.15952352
    }
  ],
  "total_count": 6,
  "current_page": 1,
  "page_size": 3
}
# verified: 2026-04
```

See `verified-snippets.md` for the complete set.

## Refresh procedure (when the API changes)

If a marketplace developer renames an endpoint or moves a field:

1. Run the sniffer at `spike/marketplace/sniffer.py` and reproduce the broken flow.
2. Inspect the captured JSONL — find the renamed/moved request.
3. Update the relevant parser in `skills/clients/marketplace/client.py`.
4. Update the corresponding fixture in `skills/clients/marketplace/tests/fixtures/`.
5. Bump the `verified:` date in this file's frontmatter.
6. Run `pytest skills/clients/marketplace/` — must pass.
7. Run an integration test against live API to confirm.

## Agent behavior

| Action | Risk | Behavior |
|---|---|---|
| `search` | Read | Run freely — no confirmation needed. |
| `details` | Read | Run freely. |
| `whoami` | Read | Run freely. |
| `login` | Opens a browser — needs user attention | **Always confirm with the user before invoking.** Tell them a browser will open. |
| Anything else (subscribe, request access, etc.) | Write | Out of scope — direct user to the UI's request page. |

## Notes

- Bearer tokens replay cleanly outside the browser with only `Authorization` + `Content-Type` headers — no CSRF, no host/UA binding (verified during the spike).
- `User-Agent: catalyst-marketplace/1.0` is sent on every request — makes any anomaly-detection flag easy to attribute.
- The marketplace runs DataHub under the hood (the `/aspects` endpoint pattern is a tell). DataHub-style metadata aspects exist if a future skill needs them.
