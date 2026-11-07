"""Playwright-driven Okta SSO + token extraction.

Run interactively via `python -m skills.clients.marketplace login`.
Headed Chromium opens against the marketplace; user completes SSO; the
script reads the bearer from `localStorage` (Okta's `okta-token-storage`
key, OIDC PKCE flow) and writes it to the token cache via auth.save_token.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

import platformdirs

from . import auth as auth_mod
from . import exceptions as exc

DEFAULT_UI_BASE_URL = "https://marketplace.capgroup.com"
DEFAULT_API_BASE_URL = "https://marketplace-service.datalake.aws.capgroup.com"
# Per-OS persistent browser profile.
# Linux/Mac: ~/.cache/catalyst-marketplace/
# Windows:   C:\\Users\\<user>\\AppData\\Local\\catalyst-marketplace\\Cache
PROFILE_DIR = Path(platformdirs.user_cache_dir("catalyst-marketplace", appauthor=False))

# Okta's localStorage key for the OIDC token bundle (verified empirically — see
# spike findings). If the marketplace SPA changes its auth library this may
# need to change.
LOCALSTORAGE_KEY = "okta-token-storage"


def extract_bearer(storage: dict) -> str:
    """Read the Okta accessToken from a localStorage snapshot.

    Raises MarketplaceAuthError if the token is missing, malformed, or expired.
    The poll loop in login() retries on this exception, so an expired stale
    token causes the loop to wait for the SPA to refresh.
    """
    import time

    raw = storage.get(LOCALSTORAGE_KEY)
    if not raw:
        raise exc.MarketplaceAuthError(
            f"No {LOCALSTORAGE_KEY!r} key in browser localStorage. "
            "Did Okta SSO complete? Try running `marketplace login` again."
        )
    try:
        bundle = json.loads(raw)
    except json.JSONDecodeError as e:
        raise exc.MarketplaceAuthError(
            f"Malformed Okta token bundle in localStorage: {e}"
        )
    access = bundle.get("accessToken") or {}
    token = access.get("accessToken")
    if not token or not token.startswith("ey"):
        raise exc.MarketplaceAuthError(
            "Okta access token is missing or doesn't look like a JWT. "
            "If the marketplace's auth flow changed, this code needs updating."
        )

    # Reject stale/expired tokens. The Okta auth-js bundle exposes expiresAt
    # in seconds since epoch. If it's in the past (or missing — decode the JWT
    # exp claim as a fallback), treat as not-yet-ready so the poll loop waits.
    now = int(time.time())
    expires_at = access.get("expiresAt")
    if expires_at is None:
        # Fall back to decoding the JWT's exp claim.
        expires_at = _jwt_exp(token)
    if expires_at is not None and expires_at <= now:
        raise exc.MarketplaceAuthError(
            f"Okta access token in localStorage is expired (exp={expires_at}, now={now}). "
            "Waiting for SPA to refresh."
        )

    return f"Bearer {token}"


def _jwt_exp(jwt: str) -> Optional[int]:
    """Decode a JWT's `exp` claim (seconds since epoch). Returns None on failure."""
    import base64

    try:
        parts = jwt.split(".")
        if len(parts) != 3:
            return None
        payload_b64 = parts[1]
        # URL-safe base64 with padding fix.
        padded = payload_b64 + "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded))
        exp = payload.get("exp")
        return int(exp) if exp is not None else None
    except (ValueError, json.JSONDecodeError, KeyError, TypeError):
        return None


_ENV_VARS_PATTERN = re.compile(
    r'window\.__ENV__\s*=\s*({.+?})\s*[;]?\s*$', re.MULTILINE | re.DOTALL
)


def extract_api_base_url(env_vars_body: str) -> str:
    """Pull REACT_APP_EAST_BASE_URL from the SPA's /env-vars response.

    Falls back to DEFAULT_API_BASE_URL if missing.
    """
    m = _ENV_VARS_PATTERN.search(env_vars_body)
    if not m:
        return DEFAULT_API_BASE_URL
    try:
        env = json.loads(m.group(1))
    except json.JSONDecodeError:
        return DEFAULT_API_BASE_URL
    return env.get("REACT_APP_EAST_BASE_URL", DEFAULT_API_BASE_URL)


try:
    from playwright.sync_api import sync_playwright  # noqa: F401  (patched in tests)
except ImportError:  # pragma: no cover
    sync_playwright = None  # type: ignore[assignment]


def login(
    ui_base_url: str = DEFAULT_UI_BASE_URL,
    wait_for_close: bool = True,
    poll_interval: float = 1.0,
    poll_timeout: float = 300.0,
) -> None:
    """Open headed Chromium, auto-detect Okta bearer, save to token cache.

    Polls localStorage for the Okta accessToken — no user interaction
    required after Okta SSO completes (or immediately if SSO is warm).
    Browser closes automatically once the token is captured.

    poll_interval: seconds between localStorage checks (default 1s)
    poll_timeout: max seconds to wait for the token (default 300s = 5 min)
    wait_for_close=False is for tests; skips polling and explicit close.
    """
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1280, "height": 900},
        )
        page = ctx.new_page()

        page.goto(ui_base_url, wait_until="domcontentloaded")

        if wait_for_close:
            # Clear any stale Okta token from the persistent profile's
            # localStorage so the SPA is forced to mint a fresh one. Without
            # this, the poller can pick up an expired token from a prior
            # session before the SPA gets around to refreshing.
            try:
                page.evaluate(
                    f"() => window.localStorage.removeItem({LOCALSTORAGE_KEY!r})"
                )
            except Exception:
                pass  # Best-effort. If clear fails, expiry validation still catches stale tokens.
            # Force a reload so the SPA's auth flow re-runs against the now-empty cache.
            page.reload(wait_until="domcontentloaded")

            print("=" * 70)
            print("Browser opened. Complete Okta SSO if prompted.")
            print(f"Polling for fresh token (timeout {int(poll_timeout)}s)…")
            print("=" * 70, flush=True)
            try:
                bearer = _poll_for_bearer(page, poll_interval, poll_timeout)
            except (KeyboardInterrupt, exc.MarketplaceAuthError):
                ctx.close()
                raise
        else:
            # Test path — Playwright is fully mocked.
            storage = page.evaluate(
                "() => Object.fromEntries(Object.entries(localStorage))"
            )
            bearer = extract_bearer(storage)

        env_resp = page.goto(f"{ui_base_url}/env-vars", wait_until="domcontentloaded")
        body = env_resp.text() if env_resp else ""
        api_base = extract_api_base_url(body)

        if wait_for_close:
            ctx.close()

    auth_mod.save_token(bearer=bearer, api_base_url=api_base)
    print(f"Token cached at {auth_mod.token_path()}")


def _poll_for_bearer(page, interval: float, timeout: float) -> str:
    """Poll localStorage until the Okta accessToken appears or timeout.

    Returns the "Bearer <jwt>" string. Raises MarketplaceAuthError on timeout.

    Tolerant of navigation-in-progress errors: during Okta SSO the page
    redirects between marketplace.capgroup.com and capgroup.okta.com, and
    page.evaluate can raise "Execution context was destroyed" mid-navigation.
    Those errors are treated as "not ready yet" and the loop continues.
    """
    import time

    # Local import — Playwright might not be installed in test environments.
    try:
        from playwright.sync_api import Error as PlaywrightError
    except ImportError:
        PlaywrightError = Exception  # type: ignore[assignment, misc]

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            storage = page.evaluate(
                "() => Object.fromEntries(Object.entries(localStorage))"
            )
        except PlaywrightError:
            # Page mid-navigation (SSO flow). Wait and retry.
            time.sleep(interval)
            continue

        try:
            bearer = extract_bearer(storage)
            return bearer
        except exc.MarketplaceAuthError:
            # Token not yet present — wait and try again.
            time.sleep(interval)
            continue
    raise exc.MarketplaceAuthError(
        f"Timed out after {int(timeout)}s waiting for Okta accessToken in localStorage. "
        "Did SSO complete?"
    )
