"""Decode the cached marketplace bearer token to inspect Okta JWT claims.

Diagnostic only — used to figure out why a freshly-captured token is being
rejected by the marketplace API. Run from repo root:

    .venv/bin/python scripts/decode_marketplace_token.py
"""

from __future__ import annotations

import base64
import json
import sys
import time
from pathlib import Path

# Make the repo root importable when run as a standalone script.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skills.clients.marketplace import auth


def _b64decode(seg: str) -> bytes:
    """URL-safe base64 decode with auto-padding."""
    return base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4))


def main() -> int:
    tok = auth.load_token()
    if tok is None:
        print("No token cached. Run `python -m skills.clients.marketplace login` first.")
        return 1

    raw = tok.bearer.replace("Bearer ", "")
    parts = raw.split(".")
    if len(parts) != 3:
        print(f"Token is not a 3-part JWT (got {len(parts)} parts).")
        print(f"Raw value (truncated): {raw[:80]}…")
        return 1

    try:
        header = json.loads(_b64decode(parts[0]))
        payload = json.loads(_b64decode(parts[1]))
    except Exception as exc:
        print(f"Failed to decode JWT segments: {exc}")
        return 1

    now = int(time.time())
    exp = payload.get("exp", 0)

    print("=" * 60)
    print("OKTA TOKEN INSPECTION")
    print("=" * 60)
    print(f"alg / typ:        {header.get('alg')}  /  {header.get('typ')}")
    print(f"issuer (iss):     {payload.get('iss')}")
    print(f"audience (aud):   {payload.get('aud')}")
    print(f"client_id (cid):  {payload.get('cid')}")
    print(f"subject (sub):    {payload.get('sub')}")
    print(f"scopes (scp):     {payload.get('scp')}")
    print(f"issued (iat):     {payload.get('iat')}")
    print(f"expires (exp):    {exp}")
    print(f"current time:     {now}")
    print(f"expires_in_sec:   {exp - now}  ({(exp - now) / 60:.1f} min)")
    print(f"api_base_url:     {tok.api_base_url}")
    print()
    if exp - now <= 0:
        print("VERDICT: token is EXPIRED.")
    elif (exp - now) < 60:
        print("VERDICT: token expires in <60s — likely fine but borderline.")
    else:
        print("VERDICT: token is fresh; rejection is likely audience/scope, not expiration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
