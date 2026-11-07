"""One-shot: extract redacted fixtures from spike captures for unit tests.

Run once to populate skills/clients/marketplace/tests/fixtures/.
Idempotent — re-running overwrites with current canonical responses.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CAPTURES = REPO / "spike" / "marketplace" / "captures"
FIXTURES = REPO / "skills" / "clients" / "marketplace" / "tests" / "fixtures"


def redact(record: dict) -> dict:
    """Replace any bearer token with a fake but realistic-shaped JWT."""
    fake = "Bearer " + "ey" + "X" * 500
    headers = record.get("request", {}).get("headers", {})
    if "authorization" in headers:
        headers["authorization"] = fake
    return record


def find_first(records, predicate):
    for r in records:
        if predicate(r):
            return r
    return None


def main() -> int:
    captures = sorted(CAPTURES.glob("sniff-*.jsonl"))
    if not captures:
        print(f"No captures in {CAPTURES}", file=sys.stderr)
        return 1
    records = []
    for cap in captures:
        for line in cap.read_text().splitlines():
            records.append(json.loads(line))

    FIXTURES.mkdir(parents=True, exist_ok=True)

    targets = {
        "search_response.json": lambda r: "/search/entities" in r["url"]
            and r.get("method") == "POST"
            and "page=1" in r["url"]
            and r.get("response", {}).get("status") == 200
            and "keyword" in (r.get("request", {}).get("post_data") or ""),
        "consumable_response.json": lambda r: "/683/consumable" in r["url"]
            and r.get("response", {}).get("status") == 200,
        "entity_detail_response.json": lambda r: r["url"].endswith("/entities/683")
            and r.get("response", {}).get("status") == 200,
        "view_access_response.json": lambda r: "/table/view-access" in r["url"]
            and r.get("response", {}).get("status") == 200
            and "entitlements" in (r.get("response", {}).get("body") or ""),
        # NOTE: all /entities/table-access records in captures returned 400
        # (server requires table values in request body — the sniffer missed a
        # populated call). We keep the best available record (status 400) so the
        # fixture exists and downstream tests can use it for error-path coverage.
        "table_access_response_lasr.json": lambda r: "/entities/table-access" in r["url"],
        # Prefer the richer "territory" query which has actual field items
        "fields_response.json": lambda r: "/table/fields/search" in r["url"]
            and r.get("response", {}).get("status") == 200
            and len(r.get("response", {}).get("body") or "") > 100,
        "business_terms_response.json": lambda r: "/business-terms/by-tables" in r["url"]
            and r.get("response", {}).get("status") == 200,
        "preview_response.json": lambda r: "/datadelivery/preview/by-views" in r["url"]
            and r.get("response", {}).get("status") == 200,
    }

    for fname, predicate in targets.items():
        rec = find_first(records, predicate)
        if rec is None:
            print(f"WARN: no record matched {fname}; skipping")
            continue
        rec = redact(rec)
        out = {
            "request": {
                "method": rec["method"],
                "url": rec["url"],
                "post_data": rec.get("request", {}).get("post_data"),
            },
            "response": rec.get("response", {}),
        }
        (FIXTURES / fname).write_text(json.dumps(out, indent=2))
        status = rec.get("response", {}).get("status")
        print(f"wrote {fname} (status={status})")

    # /env-vars (text) for bootstrap tests
    env_vars = find_first(records, lambda r: r["url"].endswith("/env-vars")
                                          and r.get("response", {}).get("status") == 200)
    if env_vars is not None:
        (FIXTURES / "env_vars_response.txt").write_text(
            env_vars.get("response", {}).get("body", ""))
        print("wrote env_vars_response.txt")

    # Token cache fixtures
    (FIXTURES / "valid_token.json").write_text(json.dumps({
        "bearer": "Bearer ey" + "V" * 500,
        "captured_at": "2026-04-29T17:00:00Z",
        "expires_at": "2099-01-01T00:00:00Z",
        "api_base_url": "https://marketplace-service.datalake.aws.capgroup.com",
    }, indent=2))
    print("wrote valid_token.json")

    (FIXTURES / "expired_token.json").write_text(json.dumps({
        "bearer": "Bearer ey" + "E" * 500,
        "captured_at": "2020-01-01T00:00:00Z",
        "expires_at": "2020-01-01T01:00:00Z",
        "api_base_url": "https://marketplace-service.datalake.aws.capgroup.com",
    }, indent=2))
    print("wrote expired_token.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
