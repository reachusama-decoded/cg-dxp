# Verified Snippets

Every example in this document is paired with the actual JSON output captured against the live marketplace. If the snippets fail to reproduce, the API has changed — refresh per `connection-marketplace.md`.

> **Discipline:** when adding a new example, run it against the real marketplace (or a fresh fixture) and paste the actual output below the command. Examples without `# verified: YYYY-MM` are not allowed in this file.

---

## 1. Search with results

```bash
python -m skills.clients.marketplace search "client risk" --page-size 3 --json
```

Output (truncated to top 3):
```json
{
  "items": [
    {
      "entity_id": 93,
      "name": "Climate Value At Risk Scenario Analysis",
      "description": "Climate Value at Risk (VaR) financial metric helps investors to better assess potential future costs and/or profits relating to their portfolio's exposur",
      "type": {"code": "dataset", "label": "Dataset"},
      "platform": {"code": "CSPN", "name": "Caspian"},
      "validated": false,
      "health": {"rating": null, "status": "unrated"},
      "ancestry": [],
      "detail_url": "https://marketplace.capgroup.com/entity/93",
      "search_rank": 0.15952352
    }
  ],
  "total_count": 6,
  "current_page": 1,
  "page_size": 3,
  "total_pages": 2
}
```
# verified: 2026-04

---

## 2. Search with no results

```bash
python -m skills.clients.marketplace search "xyzzy123nothere" --json
```

Output:
```json
{
  "items": [],
  "total_count": 0,
  "current_page": 1,
  "page_size": 25,
  "total_pages": 0
}
```
# verified: 2026-04

---

## 3. Details for a Caspian entity

```bash
python -m skills.clients.marketplace details 683 --json
```

Output (Caspian platform — entitlement format `CPZ_PRD_*`):
```json
{
  "entity": {
    "entity_id": 683,
    "name": "CG Positions",
    "type": {"code": "dataset_table", "label": "Dataset Table"},
    "platform": {"code": "CSPN", "name": "Caspian"},
    "validated": true,
    "health": {"rating": null, "status": "unrated"},
    "sources": {
      "dremio": ["investment_management.investment_transaction_position.portfolio_position.cg_positions_gp_v4_current"],
      "glue": ["cspn_cons2_prd.cg_positions_gp_v4"],
      "s3": ["s3a://datalake-curated-prd-us-east-1/cspn_cons2/cg_positions_gp_v4-..."]
    },
    "access": {
      "has_access": true,
      "entitlements": ["CPZ_PRD_AA00002933_IM_MGRTRANSPOS_READ"],
      "request_access_url": "https://marketplace.capgroup.com/entity/683/request-access",
      "platform_code": "CSPN"
    }
  },
  "_meta": {
    "fetched_at": "2026-04-29T18:00:00Z",
    "endpoints_called": 6,
    "schema_version": "1.0"
  }
}
```
# verified: 2026-04

---

## 4. whoami — token valid

```bash
python -m skills.clients.marketplace whoami
```

Output:
```json
{
  "valid": true,
  "expires_at": null
}
```
Exit code: 0
# verified: 2026-04

---

## 5. whoami — no token

```bash
python -m skills.clients.marketplace whoami
```

stderr:
```
No marketplace token cached. Run `python -m skills.clients.marketplace login`.
```
Exit code: 3
# verified: 2026-04
