"""Jira REST API client for Catalyst skills.

Provides a clean, testable wrapper around the Jira Cloud REST API.
Auth is explicit — callers supply base_url, username/email, and API token directly.

Key features:
- Automatic rate-limit handling with exponential backoff
- Field ID auto-discovery (Epic Name, Epic Link, Sprint)
- Pagination support (token-based for Cloud, startAt for Server)
- ADF (Atlassian Document Format) for rich text descriptions
- Comprehensive error handling with Catalyst exception hierarchy

Example usage:
    from skills.clients.jira import JiraClient
    from skills.clients.exceptions import RateLimitError, AuthError
    
    client = JiraClient(
        base_url="https://your-org.atlassian.net",
        username="you@company.com",
        api_token="your_api_token",
    )
    
    try:
        # Search with JQL
        issues = list(client.iter_search_issues(
            jql='project = "DATA" AND status = "In Progress"',
            fields=["summary", "assignee"],
            limit=50,
        ))
        
        # Create an issue
        issue = client.create_issue({
            "fields": {
                "project": {"key": "DATA"},
                "issuetype": {"name": "Story"},
                "summary": "New data pipeline",
                "description": client.text_to_adf("Build XYZ pipeline"),
            }
        })
        
    except AuthError:
        print("Invalid credentials — check your API token")
    except RateLimitError:
        print("Rate limit exceeded — try again later")
"""

from __future__ import annotations

import logging
import os
import random
import time
import urllib.parse
from typing import Any, Iterator

import requests

from skills.clients.exceptions import (
    AuthError,
    CatalystClientError,
    ConflictError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    RequestTimeoutError,
    ServerError,
    SSLError,
    ValidationError,
)

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 30  # seconds


class JiraClient:
    """Thin wrapper around the Jira REST API v3.
    
    Note: requests.Session is used for connection pooling but is not guaranteed
    to be thread-safe when shared across threads. For concurrent usage, create
    separate client instances per thread.
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        api_token: str,
        *,
        max_retries: int = 5,
        retry_base_delay: float = 1.0,
        retry_max_delay: float = 30.0,
    ) -> None:
        """Initialize the Jira client.

        Args:
            base_url: Base URL of the Jira instance
                      (e.g. ``https://your-org.atlassian.net``).
                      Trailing slash is normalized away.
            username: Atlassian account email used for Basic auth.
            api_token: Atlassian API token (generate at id.atlassian.com).
            max_retries: Maximum retry attempts for rate-limited requests.
            retry_base_delay: Base delay in seconds for exponential backoff.
            retry_max_delay: Maximum delay in seconds between retries.

        Raises:
            ValueError: If any required argument is empty.
        """
        if not base_url:
            raise ValueError("base_url must be a non-empty string")
        if not username:
            raise ValueError("username must be a non-empty string")
        if not api_token:
            raise ValueError("api_token must be a non-empty string")

        self._base_url = base_url.rstrip("/")
        self._username = username
        self._api_token = api_token
        self._max_retries = max_retries
        self._retry_base_delay = retry_base_delay
        self._retry_max_delay = retry_max_delay

        self._session = requests.Session()
        self._session.auth = (username, api_token)
        self._session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        # TODO: For high-volume operations, consider tuning HTTPAdapter pool size
        # Default is 10 connections per host, may want to increase for bulk operations

    # ------------------------------------------------------------------
    # Properties (read-only access for tests)
    # ------------------------------------------------------------------

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def username(self) -> str:
        return self._username

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_fields(self) -> list[dict[str, Any]]:
        """Fetch all field metadata from Jira.
        
        Returns list of field definitions including custom fields.
        Use this to discover field IDs for Epic Name, Sprint, etc.
        
        Returns:
            List of field definition dictionaries.
            
        Raises:
            CatalystClientError: On API failure.
        """
        response = self._request("GET", "/rest/api/3/field")
        return response

    def get_issue(self, key: str, *, fields: list[str] | None = None, expand: list[str] | None = None) -> dict[str, Any]:
        """Fetch a single issue by key.
        
        Args:
            key: Issue key (e.g. "DATA-123").
            fields: List of field names to include. None = all fields.
            expand: List of entities to expand (e.g. ["changelog"]).
            
        Returns:
            Issue data dictionary.
            
        Raises:
            NotFoundError: Issue doesn't exist or user lacks permission.
            CatalystClientError: On other API failure.
        """
        params: dict[str, str] = {}
        if fields:
            params["fields"] = ",".join(fields)
        if expand:
            params["expand"] = ",".join(expand)
        
        return self._request("GET", f"/rest/api/3/issue/{key}", params=params)

    def search_issues(
        self,
        jql: str,
        *,
        fields: list[str] | None = None,
        expand: list[str] | None = None,
        next_page_token: str | None = None,
        max_results: int = 50,
    ) -> dict[str, Any]:
        """Search for issues using JQL.

        Uses Jira Cloud's /rest/api/3/search/jql endpoint (legacy /search
        was removed Aug 2025). Pagination is token-based: pass
        ``response['nextPageToken']`` back on the next call until
        ``response['isLast']`` is True.

        Args:
            jql: JQL query string.
            fields: Field names to include. None = all fields.
            expand: Entities to expand.
            next_page_token: Opaque token from a prior response.
            max_results: Page size (max 100).

        Returns:
            Search response: ``{"issues": [...], "isLast": bool, "nextPageToken": str | None}``.

        Raises:
            ValidationError: Invalid JQL syntax.
            CatalystClientError: On other API failure.
        """
        qs = [
            f"jql={urllib.parse.quote(jql)}",
            f"maxResults={int(max_results)}",
        ]
        if fields:
            qs.append("fields=" + urllib.parse.quote(",".join(fields)))
        if expand:
            qs.append("expand=" + urllib.parse.quote(",".join(expand)))
        if next_page_token:
            qs.append("nextPageToken=" + urllib.parse.quote(next_page_token))

        return self._request("GET", "/rest/api/3/search/jql?" + "&".join(qs))

    def iter_search_issues(
        self,
        jql: str,
        *,
        fields: list[str] | None = None,
        expand: list[str] | None = None,
        page_size: int = 50,
        limit: int | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Iterate over all issues matching JQL query (auto-paginating).

        Args:
            jql: JQL query string.
            fields: Field names to include.
            expand: Entities to expand.
            page_size: Results per API call (max 100).
            limit: Maximum total issues to return. None = unlimited.

        Yields:
            Issue dictionaries.

        Raises:
            ValidationError: Invalid JQL syntax.
            CatalystClientError: On API failure.
        """
        token: str | None = None
        total_yielded = 0

        while True:
            response = self.search_issues(
                jql,
                fields=fields,
                expand=expand,
                next_page_token=token,
                max_results=page_size,
            )

            issues = response.get("issues") or []
            if not issues:
                return

            for issue in issues:
                yield issue
                total_yielded += 1
                if limit and total_yielded >= limit:
                    return

            if response.get("isLast") or not response.get("nextPageToken"):
                return
            token = str(response["nextPageToken"])

    def create_issue(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create a new issue.
        
        Args:
            payload: Issue creation payload. Must include:
                     {"fields": {"project": {...}, "issuetype": {...}, "summary": "..."}}.
            
        Returns:
            Created issue data with key, id, self URL.
            
        Raises:
            ValidationError: Invalid payload (missing required fields).
            CatalystClientError: On other API failure.
            
        Example:
            issue = client.create_issue({
                "fields": {
                    "project": {"key": "DATA"},
                    "issuetype": {"name": "Story"},
                    "summary": "New pipeline",
                    "description": client.text_to_adf("Build XYZ"),
                }
            })
        """
        return self._request("POST", "/rest/api/3/issue", body=payload)

    def update_issue(self, key: str, fields: dict[str, Any]) -> None:
        """Update an existing issue.
        
        Args:
            key: Issue key to update.
            fields: Field updates (partial update).
            
        Raises:
            NotFoundError: Issue doesn't exist.
            ValidationError: Invalid field values.
            CatalystClientError: On other API failure.
            
        Example:
            client.update_issue("DATA-123", {
                "summary": "Updated summary",
                "labels": ["urgent", "pipeline"],
            })
        """
        payload = {"fields": fields}
        self._request("PUT", f"/rest/api/3/issue/{key}", body=payload)

    def create_issue_link(
        self,
        link_type: str,
        inward_key: str,
        outward_key: str,
    ) -> None:
        """Create a link between two issues.
        
        Args:
            link_type: Link type name (e.g. "Blocks", "Relates").
            inward_key: Inward issue key.
            outward_key: Outward issue key.
            
        Raises:
            NotFoundError: Issue doesn't exist.
            ValidationError: Invalid link type.
            CatalystClientError: On other API failure.
            
        Example:
            client.create_issue_link("Blocks", "DATA-123", "DATA-456")
            # DATA-123 blocks DATA-456
        """
        payload = {
            "type": {"name": link_type},
            "inwardIssue": {"key": inward_key},
            "outwardIssue": {"key": outward_key},
        }
        self._request("POST", "/rest/api/3/issueLink", body=payload)

    def add_issues_to_sprint(self, sprint_id: int, issue_keys: list[str]) -> None:
        """Add issues to a sprint (Jira Agile).
        
        Args:
            sprint_id: Numeric sprint ID.
            issue_keys: List of issue keys to add.
            
        Raises:
            NotFoundError: Sprint doesn't exist.
            ValidationError: Issue keys invalid.
            CatalystClientError: On other API failure.
        """
        payload = {"issues": issue_keys}
        self._request("POST", f"/rest/agile/1.0/sprint/{sprint_id}/issue", body=payload)

    @staticmethod
    def text_to_adf(text: str) -> dict[str, Any]:
        """Convert plain text into Atlassian Document Format (ADF).
        
        Jira Cloud uses ADF for rich-text fields like description.
        This helper converts plain text with paragraph breaks into ADF JSON.
        
        Args:
            text: Plain text with newline-separated paragraphs.
            
        Returns:
            ADF document dictionary.
            
        Example:
            description = JiraClient.text_to_adf(\"\"\"
                This is paragraph 1.
                
                This is paragraph 2.
            \"\"\")
            # Returns {"type": "doc", "version": 1, "content": [...]}
        """
        text = text or ""
        paras = [p.strip() for p in text.replace("\r\n", "\n").split("\n\n")]
        content: list[dict[str, Any]] = []
        
        for para in paras:
            if not para:
                continue
            
            # Split paragraph into lines for potential formatting
            lines = [line.strip() for line in para.split("\n") if line.strip()]
            
            if not lines:
                continue
            
            # Simple paragraph with text
            content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": " ".join(lines)}],
            })
        
        return {"type": "doc", "version": 1, "content": content}

    # ------------------------------------------------------------------
    # Internal request handling
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
    ) -> Any:
        """Execute HTTP request with retry logic and error handling.
        
        Handles:
        - Rate limiting (HTTP 429) with exponential backoff
        - Auth errors (HTTP 401/403)
        - Not found (HTTP 404)
        - Validation errors (HTTP 400)
        - Server errors (HTTP 5xx)
        - Network/SSL/timeout errors
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            path: API path (relative to base_url).
            params: Query parameters.
            body: JSON request body.
            
        Returns:
            Parsed JSON response (dict or list).
            
        Raises:
            CatalystClientError: On any failure after retries exhausted.
        """
        # Build URL safely (supports base URLs with context paths)
        url = self._base_url.rstrip("/") + "/" + path.lstrip("/")
        attempt = 0
        
        while attempt <= self._max_retries:
            try:
                response = self._session.request(
                    method,
                    url,
                    params=params,
                    json=body,
                    timeout=_DEFAULT_TIMEOUT,
                )
                
                # Handle HTTP errors
                if response.status_code == 429:
                    # Rate limited — retry with backoff
                    if attempt < self._max_retries:
                        delay = self._calculate_retry_delay(attempt, response)
                        logger.warning(
                            "Jira rate limit (429) — retrying in %.1fs (attempt %d/%d)",
                            delay,
                            attempt + 1,
                            self._max_retries,
                        )
                        time.sleep(delay)
                        attempt += 1
                        continue
                    raise RateLimitError("Jira rate limit exceeded — max retries exhausted")
                
                if response.status_code == 401:
                    raise AuthError("Jira authentication failed — check credentials")
                
                if response.status_code == 403:
                    raise AuthError("Jira authorization failed — insufficient permissions")
                
                if response.status_code == 404:
                    raise NotFoundError(f"Resource not found: {path}")
                
                if response.status_code == 400:
                    try:
                        error_msg = response.json().get("errorMessages", [response.text])[0]
                    except Exception:
                        error_msg = response.text[:200]
                    raise ValidationError(f"Jira validation error: {error_msg}")
                
                if response.status_code == 409:
                    raise ConflictError(f"Jira conflict: {response.text[:200]}")
                
                if response.status_code >= 500:
                    if attempt < self._max_retries:
                        delay = self._calculate_retry_delay(attempt, response)
                        logger.warning(
                            "Jira server error (%d) — retrying in %.1fs",
                            response.status_code,
                            delay,
                        )
                        time.sleep(delay)
                        attempt += 1
                        continue
                    raise ServerError(f"Jira server error ({response.status_code})")
                
                # Raise for any other error status
                response.raise_for_status()
                
                # Success — return JSON if present
                if response.status_code == 204 or not response.content:
                    return None
                
                try:
                    return response.json()
                except ValueError as e:
                    # Response was not valid JSON (HTML error page, etc.)
                    body_preview = response.text[:200] if response.text else "(empty)"
                    raise ServerError(
                        f"Response body is not valid JSON: {e}. Body preview: {body_preview}"
                    ) from e
            
            except requests.exceptions.SSLError as e:
                raise SSLError(f"SSL certificate verification failed: {e}") from e
            
            except requests.exceptions.Timeout as e:
                if attempt < self._max_retries:
                    delay = self._calculate_retry_delay(attempt, None)
                    logger.warning("Jira request timeout — retrying in %.1fs", delay)
                    time.sleep(delay)
                    attempt += 1
                    continue
                raise RequestTimeoutError(f"Jira request timed out after {_DEFAULT_TIMEOUT}s") from e
            
            except requests.exceptions.ConnectionError as e:
                raise NetworkError(f"Failed to connect to Jira: {e}") from e
            
            except requests.exceptions.RequestException as e:
                raise CatalystClientError(f"Jira request failed: {e}") from e

    def _calculate_retry_delay(self, attempt: int, response: requests.Response | None) -> float:
        """Calculate exponential backoff delay with jitter.
        
        Respects Retry-After header if present.
        """
        if response and "Retry-After" in response.headers:
            try:
                return float(response.headers["Retry-After"])
            except ValueError:
                pass
        
        # Exponential backoff: base * (2 ** attempt) + jitter
        delay = self._retry_base_delay * (2 ** attempt)
        delay = min(delay, self._retry_max_delay)
        
        # Add jitter (±25%)
        # TODO: Consider capping jitter at min(1.0, delay * 0.25) to prevent large jitter with long delays
        jitter = delay * 0.25 * (2 * random.random() - 1)
        return delay + jitter


class FieldIds:
    """Container for Jira custom field IDs.

    Attributes:
        epic_name: Field ID for Epic Name (e.g. "customfield_10011").
        epic_link: Field ID for Epic Link (e.g. "customfield_10014").
        sprint: Field ID for Sprint (e.g. "customfield_10020").
        acceptance_criteria: Field ID for Acceptance Criteria (e.g. "customfield_10170").
    """

    def __init__(
        self,
        epic_name: str | None = None,
        epic_link: str | None = None,
        sprint: str | None = None,
        acceptance_criteria: str | None = None,
    ):
        self.epic_name = epic_name
        self.epic_link = epic_link
        self.sprint = sprint
        self.acceptance_criteria = acceptance_criteria

    def __repr__(self) -> str:
        return (
            f"FieldIds(epic_name={self.epic_name!r}, epic_link={self.epic_link!r}, "
            f"sprint={self.sprint!r}, acceptance_criteria={self.acceptance_criteria!r})"
        )


def discover_field_ids(fields: list[dict[str, Any]]) -> FieldIds:
    """Auto-discover Epic Name, Epic Link, Sprint, and Acceptance Criteria field IDs.

    Jira instances use different field IDs for custom fields.
    This function searches the field list for known field names.

    The Acceptance Criteria field id can be overridden via the
    ``JIRA_ACCEPTANCE_CRITERIA_FIELD_ID`` env var for projects where
    field-name search is unreliable.

    Args:
        fields: List of field definitions from get_fields().

    Returns:
        FieldIds with discovered IDs (None if not found).

    Example:
        fields = client.get_fields()
        field_ids = discover_field_ids(fields)
        if field_ids.epic_name:
            # Use field_ids.epic_name when creating epics
    """
    epic_name = None
    epic_link = None
    sprint = None
    acceptance_criteria = None

    for field in fields:
        name = field.get("name", "").lower()
        field_id = field.get("id", "")

        if "epic name" in name and not epic_name:
            epic_name = field_id
        elif "epic link" in name and not epic_link:
            epic_link = field_id
        elif name == "sprint" and not sprint:
            sprint = field_id
        elif name == "acceptance criteria" and not acceptance_criteria:
            acceptance_criteria = field_id

    env_override = os.environ.get("JIRA_ACCEPTANCE_CRITERIA_FIELD_ID")
    if env_override:
        acceptance_criteria = env_override

    return FieldIds(
        epic_name=epic_name,
        epic_link=epic_link,
        sprint=sprint,
        acceptance_criteria=acceptance_criteria,
    )
