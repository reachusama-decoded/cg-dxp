"""Confluence client for Catalyst skills.

Provides a clean, testable wrapper around the Confluence REST API v1.
Auth is explicit — callers supply base_url, email, and token directly.
"""

from __future__ import annotations

import logging
from typing import Any
import requests

from skills.clients.exceptions import ConflictError

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 30  # seconds


class ConfluenceClient:
    """Thin wrapper around the Confluence REST API."""

    def __init__(self, base_url: str, email: str, token: str) -> None:
        """Initialise the Confluence client.

        Args:
            base_url: Base URL of the Confluence instance
                      (e.g. ``https://your-org.atlassian.net``).
                      Do not include the ``/wiki`` path segment — the client
                      appends it when constructing API URLs.
                      A trailing slash is normalised away.
            email: Atlassian account e-mail used for Basic auth.
            token: Atlassian API token (or personal access token for
                   on-premise Confluence).

        Raises:
            ValueError: If any argument is empty.
        """
        if not base_url:
            raise ValueError("base_url must be a non-empty string")
        if not email:
            raise ValueError("email must be a non-empty string")
        if not token:
            raise ValueError("token must be a non-empty string")

        self._base_url = base_url.rstrip("/")
        self._email = email
        self._token = token

        self._session = requests.Session()
        self._session.auth = (email, token)
        self._session.headers.update({"Accept": "application/json"})

    # ------------------------------------------------------------------
    # Properties (read-only access for tests)
    # ------------------------------------------------------------------

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def email(self) -> str:
        return self._email

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_page_id(page_id: str) -> None:
        """Raise ValueError if page_id is empty or whitespace-only."""
        if not page_id or not page_id.strip():
            raise ValueError("page_id must be a non-empty string")

    def get_page(self, page_id: str) -> dict[str, Any]:
        """Fetch a single Confluence page by ID.

        Returns the full API response including body.storage content,
        version, space, and ancestors.

        Args:
            page_id: Numeric Confluence page identifier.

        Returns:
            Parsed JSON response dict from the API.

        Raises:
            requests.HTTPError: On a non-2xx response.
            ValueError: If page_id is empty.
        """
        self._validate_page_id(page_id)

        url = self._content_url(page_id)
        params = {"body-format": "storage"}

        logger.debug("Fetching Confluence page %s via v2 API", page_id)
        response = self._session.get(url, params=params, timeout=_DEFAULT_TIMEOUT)

        if response.status_code == 404:
            # Fall back to v1 API
            logger.debug("v2 API returned 404, trying v1 for page %s", page_id)
            url = self._content_url_v1(page_id)
            params = {"expand": "body.storage,version,space,ancestors"}
            response = self._session.get(url, params=params, timeout=_DEFAULT_TIMEOUT)

        response.raise_for_status()
        return response.json()

    def get_page_tree(
        self,
        page_id: str,
        max_depth: int = 10,
        _depth: int = 0,
        _seen: set[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Recursively fetch a page and all its descendants.

        Pages are returned in pre-order (parent before children).

        Args:
            page_id: Root page ID.
            max_depth: Maximum recursion depth (inclusive).  Defaults to 10.

        Returns:
            List of page dicts as returned by :meth:`get_page`.

        Raises:
            requests.HTTPError: On a non-2xx response for the root page.
        """
        if _seen is None:
            _seen = set()

        if page_id in _seen or _depth >= max_depth:
            return []

        _seen.add(page_id)

        page = self.get_page(page_id)
        pages: list[dict[str, Any]] = [page]

        for child in self._get_children(page_id):
            child_id = child["id"]
            pages.extend(
                self.get_page_tree(
                    child_id,
                    max_depth=max_depth,
                    _depth=_depth + 1,
                    _seen=_seen,
                )
            )

        return pages

    def update_page(
        self,
        page_id: str,
        title: str,
        body_storage: str,
        current_version: int,
    ) -> dict[str, Any]:
        """Update a Confluence page body using storage representation.

        Args:
            page_id: Numeric Confluence page identifier.
            title: Page title to persist with the update.
            body_storage: Body content in Confluence storage format.
            current_version: Current page version from Confluence.

        Returns:
            Parsed JSON response dict from the API.

        Raises:
            requests.HTTPError: On a non-2xx response.
            ValueError: If page_id is empty.
        """
        self._validate_page_id(page_id)

        url = self._content_url_v1(page_id)
        payload = {
            "id": page_id,
            "type": "page",
            "title": title,
            "body": {
                "storage": {
                    "value": body_storage,
                    "representation": "storage",
                }
            },
            "version": {"number": int(current_version) + 1},
        }

        logger.debug("Updating Confluence page %s via v1 API", page_id)
        response = self._session.put(
            url,
            json=payload,
            headers={"X-Atlassian-Token": "no-check"},
            timeout=_DEFAULT_TIMEOUT,
        )
        if response.status_code == 409:
            raise ConflictError(
                f"Confluence version conflict on page {page_id} — "
                "another writer updated the page since it was fetched. "
                "Re-fetch the page and retry."
            )
        response.raise_for_status()
        return response.json()

    def find_child_by_title(self, parent_id: str, title: str) -> dict[str, Any] | None:
        """The child of *parent_id* with exactly this title, or None.

        Title match is exact, not fuzzy: a publisher that "finds" a near-match
        would overwrite the wrong page, and there is no undo for that in a shared
        space.
        """
        self._validate_page_id(parent_id)
        for child in self._get_children(parent_id):
            if (child.get("title") or "").strip() == title.strip():
                return child
        return None

    def create_page(
        self,
        space_key: str,
        title: str,
        body_storage: str,
        parent_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a page, optionally as a child of *parent_id*.

        Args:
            space_key: Space to create the page in (e.g. ``ENTDATA``).
            title: Page title. Confluence requires titles to be unique per space.
            body_storage: Body content in Confluence storage format.
            parent_id: Numeric id of the parent page, for placing it in a tree.

        Returns:
            Parsed JSON response dict from the API, including the new page id.

        Raises:
            requests.HTTPError: On a non-2xx response. A 400 here is usually a
                duplicate title in the space rather than malformed storage.
            ValueError: If space_key or title is empty.
        """
        if not space_key:
            raise ValueError("space_key must be a non-empty string")
        if not title:
            raise ValueError("title must be a non-empty string")

        payload: dict[str, Any] = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": body_storage,
                    "representation": "storage",
                }
            },
        }
        if parent_id:
            self._validate_page_id(parent_id)
            payload["ancestors"] = [{"id": str(parent_id)}]

        url = f"{self._base_url}/wiki/rest/api/content"
        logger.debug("Creating Confluence page %r in space %s", title, space_key)
        response = self._session.post(
            url,
            json=payload,
            headers={"X-Atlassian-Token": "no-check"},
            timeout=_DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _content_url(self, page_id: str) -> str:
        """Return the REST API URL for a content resource.

        Tries v2 API first (Confluence Cloud), falls back to v1.
        """
        return f"{self._base_url}/wiki/api/v2/pages/{page_id}"

    def _content_url_v1(self, page_id: str) -> str:
        """Return the v1 REST API URL (legacy fallback)."""
        return f"{self._base_url}/wiki/rest/api/content/{page_id}"

    def _get_children(self, page_id: str) -> list[dict[str, Any]]:
        """Return all direct child pages, handling pagination.

        Returns an empty list rather than raising on 404 (deleted/restricted).
        """
        url = f"{self._content_url(page_id)}/children"
        params: dict[str, Any] = {"limit": 100}
        children: list[dict[str, Any]] = []

        while True:
            try:
                response = self._session.get(url, params=params, timeout=_DEFAULT_TIMEOUT)
                response.raise_for_status()
            except requests.HTTPError as exc:
                if exc.response is not None and exc.response.status_code == 404:
                    logger.warning(
                        "Cannot fetch children for page %s (404) — deleted or restricted",
                        page_id,
                    )
                    return []
                raise

            data = response.json()
            children.extend(data.get("results", []))

            next_link = data.get("_links", {}).get("next")
            if not next_link:
                break
            url = f"{self._base_url}{next_link}"
            params = {}

        return [{"id": c["id"], "title": c["title"]} for c in children]
