"""Core function: minimal raw-requests Databricks API client.

Fallback for skills that need to call the Databricks REST API when the
vendored ``databricks_tools_core.client.DatabricksClient`` isn't on
``sys.path``. Honors ``DATABRICKS_HOST`` + ``DATABRICKS_TOKEN`` and
implements the same 429 retry policy the vendored client uses, including
``Retry-After`` (delta-seconds or HTTP-date per RFC 7231 §7.1.3).

The public surface:

- :class:`RawRequestsClient` — ``get`` / ``post`` against a Databricks
  workspace, with bearer auth and 429 retries.
- :func:`should_retry_databricks` — pure predicate over a response;
  returns ``(retry?, wait_seconds)``. Other skills sharing the same
  retry policy (e.g. the vendored client's own retry wrapper) can call
  this directly without instantiating a client.
- :data:`RETRY_AFTER_MAX_SECONDS` — cap on server-provided
  ``Retry-After``. A stale or malicious header sending a multi-year
  date won't block the caller indefinitely; the predicate returns the
  sentinel ``-1.0`` past the cap so the caller substitutes its own
  default.
- :class:`AuthNotConfigured` — exception class distinct from generic
  API errors. Lets the CLI map "missing creds" to an actionable hint
  separate from "API call failed".

This module deliberately has no platform-specific decoders — it returns
parsed JSON or an empty dict; rule logic, schema parsing, and pagination
live with the caller.
"""

from __future__ import annotations

import email.utils
import sys
import time
from datetime import datetime, timezone
from typing import Any, Optional

__all__ = [
    "AuthNotConfigured",
    "RETRY_AFTER_MAX_SECONDS",
    "RETRY_MAX_ATTEMPTS",
    "RETRY_BACKOFF_SECONDS",
    "RawRequestsClient",
    "should_retry_databricks",
]


# ---------------------------------------------------------------------------
# Retry policy constants
# ---------------------------------------------------------------------------

#: Maximum number of retry attempts after the initial request.
RETRY_MAX_ATTEMPTS: int = 3

#: Per-attempt backoff seconds when the server doesn't supply ``Retry-After``.
RETRY_BACKOFF_SECONDS: tuple[float, ...] = (1.0, 2.0, 4.0)

#: Upper bound on a server-supplied ``Retry-After`` value. Past this the
#: predicate returns the sentinel ``-1.0`` so the caller falls back to its
#: default backoff schedule rather than sleeping for years.
RETRY_AFTER_MAX_SECONDS: float = 60.0


# ---------------------------------------------------------------------------
# Exception types
# ---------------------------------------------------------------------------


class AuthNotConfigured(Exception):
    """Raised when Databricks auth pre-flight fails in a user-fixable way.

    Distinct from generic API errors so callers can map this to an
    actionable hint ("set DATABRICKS_HOST + DATABRICKS_TOKEN", "run
    /connect-databricks") instead of a generic "API call failed".
    """


# ---------------------------------------------------------------------------
# Retry predicate
# ---------------------------------------------------------------------------


def should_retry_databricks(resp: Any) -> tuple[bool, float]:
    """Decide whether a Databricks response is retryable and how long to wait.

    Pure predicate. Only HTTP 429 is considered retryable; everything
    else returns ``(False, 0.0)``. When the response carries a
    ``Retry-After`` header the parsed value overrides any default
    backoff:

    - ``Retry-After: 5`` → delta-seconds → returns ``(True, 5.0)``.
    - ``Retry-After: <HTTP date>`` → parsed per RFC 7231 §7.1.3,
      converted to seconds-from-now, clamped to ``>= 0``.
    - Header missing, unparseable, or longer than
      :data:`RETRY_AFTER_MAX_SECONDS` → returns ``(True, -1.0)``, a
      sentinel telling the caller "yes retry, but pick your own
      backoff" (typically a stepped schedule from
      :data:`RETRY_BACKOFF_SECONDS`).

    The cap exists because a malicious or misconfigured server sending
    ``Retry-After: <year-2099>`` would otherwise block the caller
    indefinitely. Past the cap we still retry on a sane cadence rather
    than refusing entirely.
    """
    if getattr(resp, "status_code", None) != 429:
        return False, 0.0
    retry_after = (
        resp.headers.get("Retry-After") if getattr(resp, "headers", None) else None
    )
    if retry_after:
        retry_after = retry_after.strip()
        parsed: Optional[float] = None
        try:
            parsed = float(retry_after)
        except ValueError:
            try:
                target = email.utils.parsedate_to_datetime(retry_after)
            except (TypeError, ValueError):
                target = None
            if target is not None:
                if target.tzinfo is None:
                    target = target.replace(tzinfo=timezone.utc)
                parsed = (target - datetime.now(timezone.utc)).total_seconds()
        if parsed is not None:
            parsed = max(0.0, parsed)
            if parsed > RETRY_AFTER_MAX_SECONDS:
                return True, -1.0  # treat unreasonable values as "use default"
            return True, parsed
    return True, -1.0  # caller substitutes the per-attempt default


# ---------------------------------------------------------------------------
# Raw-requests client
# ---------------------------------------------------------------------------


class RawRequestsClient:
    """Minimal Databricks REST client backed by ``requests``.

    Exposes ``get`` and ``post`` since the Databricks API mixes both
    verbs. Both methods accept an endpoint path (e.g. ``/api/2.1/jobs/get``)
    and return parsed JSON; ``post`` takes a JSON body via the ``json``
    keyword.

    Constructor raises ``RuntimeError`` if ``host`` or ``token`` is
    empty — the caller is expected to translate that into
    :class:`AuthNotConfigured` if appropriate.
    """

    def __init__(self, host: str, token: str) -> None:
        import requests  # local import so missing requests fails clearly

        if not host:
            raise RuntimeError("DATABRICKS_HOST is not set")
        if not token:
            raise RuntimeError("DATABRICKS_TOKEN is not set")
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {token}"})
        self.host = host.rstrip("/")

    def _request_with_retry(self, method: str, url: str, **kwargs: Any) -> Any:
        """Issue an HTTP call and retry up to RETRY_MAX_ATTEMPTS times on 429."""
        resp = None
        for attempt in range(1, RETRY_MAX_ATTEMPTS + 2):  # initial + retries
            resp = self._session.request(method, url, **kwargs)
            retry, wait = should_retry_databricks(resp)
            if not retry or attempt > RETRY_MAX_ATTEMPTS:
                break
            if wait < 0:
                wait = RETRY_BACKOFF_SECONDS[
                    min(attempt - 1, len(RETRY_BACKOFF_SECONDS) - 1)
                ]
            print(
                f"note: 429 from Databricks, retrying in {wait:g}s "
                f"(attempt {attempt}/{RETRY_MAX_ATTEMPTS})",
                file=sys.stderr,
            )
            time.sleep(wait)
        assert resp is not None  # loop always assigns at least once
        resp.raise_for_status()
        return resp

    def get(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        url = f"{self.host}{endpoint}"
        resp = self._request_with_retry("GET", url, params=params)
        if not resp.content:
            return {}
        return resp.json()

    def post(
        self, endpoint: str, json: dict[str, Any] | None = None  # noqa: A002
    ) -> dict[str, Any]:
        url = f"{self.host}{endpoint}"
        resp = self._request_with_retry("POST", url, json=json)
        if not resp.content:
            return {}
        return resp.json()
