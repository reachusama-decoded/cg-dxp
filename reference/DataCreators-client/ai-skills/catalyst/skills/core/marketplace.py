"""Core marketplace search — thin wrapper over skills.clients.marketplace.

Public surface (used by other skills' Python code that wants to bypass the CLI):

    from skills.core.marketplace import search_marketplace, details

The CLI at `python -m skills.clients.marketplace` is the canonical interface for
agent skills (via Bash). This wrapper exists for in-process Python callers.
"""

from __future__ import annotations

from typing import Optional

from skills.clients.marketplace import client as _client
from skills.clients.marketplace import exceptions as _exc
from skills.clients.marketplace import models


def search_marketplace(
    keyword: str,
    types: Optional[list[str]] = None,
    page: int = 1,
    page_size: int = 25,
    parent_id: Optional[int] = None,
) -> models.SearchResults:
    """Search the marketplace. Raises if no token cached or the API rejects.

    Callers that want pre-flight token validation can use `whoami()` first.
    """
    cli = _client.MarketplaceClient.from_cache()
    return cli.search(
        keyword=keyword,
        types=types,
        page=page,
        page_size=page_size,
        parent_id=parent_id,
    )


def details(entity_id: int) -> models.Entity:
    """Fetch full entity details — sources, schema, business terms, preview, access."""
    cli = _client.MarketplaceClient.from_cache()
    return cli.details(entity_id)


def whoami() -> dict:
    """Probe token validity. Returns {"valid": bool, "reason": str | None}."""
    cli = _client.MarketplaceClient.from_cache()
    return cli.whoami()


# Re-export common types for convenience
__all__ = [
    "search_marketplace",
    "details",
    "whoami",
    "models",
]
