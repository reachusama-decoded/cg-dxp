"""Unit tests for the Jira REST API client.

Tests cover:
- Client initialization and validation
- HTTP request/response handling
- Error handling and exception mapping
- Rate-limit retry logic
- ADF text conversion
- Field ID discovery
- Pagination

Integration tests (marked with @pytest.mark.integration) require live credentials:
  JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from skills.clients.exceptions import (
    AuthError,
    NotFoundError,
    RateLimitError,
    ServerError,
    SSLError,
    RequestTimeoutError,
    ValidationError,
)
from skills.clients.jira import FieldIds, JiraClient, discover_field_ids


class TestJiraClientInit:
    """Test client initialization and validation."""

    def test_init_success(self):
        """Client initializes with valid params."""
        client = JiraClient(
            base_url="https://test.atlassian.net",
            username="test@example.com",
            api_token="test-token",
        )
        assert client.base_url == "https://test.atlassian.net"
        assert client.username == "test@example.com"
        assert client._api_token == "test-token"

    def test_init_strips_trailing_slash(self):
        """Base URL trailing slash is normalized."""
        client = JiraClient(
            base_url="https://test.atlassian.net/",
            username="test@example.com",
            api_token="test-token",
        )
        assert client.base_url == "https://test.atlassian.net"

    def test_init_empty_base_url_raises(self):
        """Empty base_url raises ValueError."""
        with pytest.raises(ValueError, match="base_url must be a non-empty string"):
            JiraClient(base_url="", username="test@example.com", api_token="token")

    def test_init_empty_username_raises(self):
        """Empty username raises ValueError."""
        with pytest.raises(ValueError, match="username must be a non-empty string"):
            JiraClient(base_url="https://test.atlassian.net", username="", api_token="token")

    def test_init_empty_api_token_raises(self):
        """Empty api_token raises ValueError."""
        with pytest.raises(ValueError, match="api_token must be a non-empty string"):
            JiraClient(base_url="https://test.atlassian.net", username="test@example.com", api_token="")


class TestJiraClientTextToADF:
    """Test ADF text conversion."""

    def test_empty_string(self):
        """Empty string produces empty ADF doc."""
        result = JiraClient.text_to_adf("")
        assert result == {"type": "doc", "version": 1, "content": []}

    def test_single_paragraph(self):
        """Single paragraph converted correctly."""
        result = JiraClient.text_to_adf("This is a test.")
        assert result == {
            "type": "doc",
            "version": 1,
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "This is a test."}]}
            ],
        }

    def test_multiple_paragraphs(self):
        """Multiple paragraphs with blank lines."""
        text = "First paragraph.\n\nSecond paragraph."
        result = JiraClient.text_to_adf(text)
        assert result == {
            "type": "doc",
            "version": 1,
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "First paragraph."}]},
                {"type": "paragraph", "content": [{"type": "text", "text": "Second paragraph."}]},
            ],
        }

    def test_multiline_paragraph(self):
        """Lines within a paragraph are joined."""
        text = "Line 1\nLine 2\nLine 3"
        result = JiraClient.text_to_adf(text)
        assert result == {
            "type": "doc",
            "version": 1,
            "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "Line 1 Line 2 Line 3"}]}
            ],
        }


class TestFieldIdDiscovery:
    """Test field ID auto-discovery."""

    def test_discover_all_fields(self):
        """Discovers Epic Name, Epic Link, and Sprint fields."""
        fields = [
            {"id": "customfield_10001", "name": "Epic Name"},
            {"id": "customfield_10002", "name": "Epic Link"},
            {"id": "customfield_10003", "name": "Sprint"},
        ]
        result = discover_field_ids(fields)
        assert result.epic_name == "customfield_10001"
        assert result.epic_link == "customfield_10002"
        assert result.sprint == "customfield_10003"

    def test_discover_case_insensitive(self):
        """Field name matching is case-insensitive."""
        fields = [
            {"id": "customfield_10001", "name": "EPIC NAME"},
            {"id": "customfield_10002", "name": "epic link"},
            {"id": "customfield_10003", "name": "sprint"},
        ]
        result = discover_field_ids(fields)
        assert result.epic_name == "customfield_10001"
        assert result.epic_link == "customfield_10002"
        assert result.sprint == "customfield_10003"

    def test_discover_missing_fields(self):
        """Returns None for fields not found."""
        fields = [{"id": "summary", "name": "Summary"}]
        result = discover_field_ids(fields)
        assert result.epic_name is None
        assert result.epic_link is None
        assert result.sprint is None


@pytest.mark.unit
class TestJiraClientMocked:
    """Unit tests with mocked requests (no network calls)."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return JiraClient(
            base_url="https://test.atlassian.net",
            username="test@example.com",
            api_token="test-token",
        )

    @pytest.fixture
    def mock_response(self):
        """Create a mock response."""
        def _make_response(status_code: int = 200, json_data: Any | None = None, text: str = ""):
            response = Mock(spec=requests.Response)
            response.status_code = status_code
            response.headers = {}
            
            if json_data is not None:
                # If json_data provided, use it for both json() and content
                response.json.return_value = json_data
                json_text = json.dumps(json_data)
                response.text = json_text
                response.content = json_text.encode()
            else:
                response.json.side_effect = ValueError("No JSON")
                response.text = text
                response.content = text.encode()
            
            response.raise_for_status = Mock()
            return response
        return _make_response

    def test_get_fields_success(self, client, mock_response):
        """get_fields returns field list on success."""
        expected_fields = [
            {"id": "summary", "name": "Summary"},
            {"id": "customfield_10001", "name": "Epic Name"},
        ]
        
        with patch.object(client._session, "request") as mock_request:
            mock_request.return_value = mock_response(200, expected_fields)
            result = client.get_fields()
        
        assert result == expected_fields
        mock_request.assert_called_once()

    def test_get_issue_success(self, client, mock_response):
        """get_issue returns issue data."""
        expected_issue = {
            "key": "DATA-123",
            "fields": {"summary": "Test issue"},
        }
        
        with patch.object(client._session, "request") as mock_request:
            mock_request.return_value = mock_response(200, expected_issue)
            result = client.get_issue("DATA-123")
        
        assert result == expected_issue

    def test_auth_error_raises(self, client, mock_response):
        """401 response raises AuthError."""
        with patch.object(client._session, "request") as mock_request:
            mock_request.return_value = mock_response(401, text="Unauthorized")
            
            with pytest.raises(AuthError, match="authentication failed"):
                client.get_fields()

    def test_not_found_error_raises(self, client, mock_response):
        """404 response raises NotFoundError."""
        with patch.object(client._session, "request") as mock_request:
            mock_request.return_value = mock_response(404, text="Not found")
            
            with pytest.raises(NotFoundError, match="Resource not found"):
                client.get_issue("DATA-999")

    def test_validation_error_raises(self, client, mock_response):
        """400 response raises ValidationError."""
        error_response = {"errorMessages": ["Invalid JQL syntax"]}
        
        with patch.object(client._session, "request") as mock_request:
            mock_request.return_value = mock_response(400, error_response)
            
            with pytest.raises(ValidationError, match="Invalid JQL syntax"):
                client.search_issues("invalid jql")

    def test_rate_limit_retry(self, client, mock_response):
        """429 response triggers retry logic."""
        # First call: rate-limited, second call: success
        success_response = mock_response(200, [])
        rate_limit_response = mock_response(429, text="Too many requests")
        rate_limit_response.headers = {"Retry-After": "0.1"}
        
        with patch.object(client._session, "request") as mock_request, \
             patch("time.sleep"):  # Skip actual sleep in tests
            mock_request.side_effect = [rate_limit_response, success_response]
            
            result = client.get_fields()
            
            assert result == []
            assert mock_request.call_count == 2

    def test_rate_limit_exhausted_raises(self, client, mock_response):
        """429 with max retries exhausted raises RateLimitError."""
        client._max_retries = 1
        rate_limit_response = mock_response(429, text="Too many requests")
        
        with patch.object(client._session, "request") as mock_request:
            mock_request.return_value = rate_limit_response
            
            with pytest.raises(RateLimitError, match="max retries exhausted"):
                client.get_fields()

    def test_server_error_retries(self, client, mock_response):
        """5xx response triggers retry logic."""
        success_response = mock_response(200, [])
        server_error = mock_response(503, text="Service unavailable")
        
        with patch.object(client._session, "request") as mock_request, \
             patch("time.sleep"):  # Skip actual sleep in tests
            mock_request.side_effect = [server_error, success_response]
            
            result = client.get_fields()
            
            assert result == []
            assert mock_request.call_count == 2

    def test_timeout_error_raises(self, client):
        """Timeout raises RequestTimeoutError."""
        with patch.object(client._session, "request") as mock_request:
            mock_request.side_effect = requests.exceptions.Timeout("Timed out")
            
            with pytest.raises(RequestTimeoutError, match="timed out"):
                client.get_fields()

    def test_ssl_error_raises(self, client):
        """SSL error raises SSLError."""
        with patch.object(client._session, "request") as mock_request:
            mock_request.side_effect = requests.exceptions.SSLError("Certificate verify failed")
            
            with pytest.raises(SSLError, match="SSL certificate verification failed"):
                client.get_fields()

    def test_create_issue_success(self, client, mock_response):
        """create_issue returns created issue data."""
        payload = {
            "fields": {
                "project": {"key": "DATA"},
                "issuetype": {"name": "Story"},
                "summary": "Test story",
            }
        }
        expected_result = {"key": "DATA-123", "id": "12345", "self": "https://test.atlassian.net/rest/api/3/issue/12345"}
        
        with patch.object(client._session, "request") as mock_request:
            mock_request.return_value = mock_response(201, expected_result)
            result = client.create_issue(payload)
        
        assert result == expected_result

    def test_iter_search_issues_pagination(self, client, mock_response):
        """iter_search_issues handles token-based pagination correctly."""
        # Page 1: 2 issues, more pages available
        page1 = {
            "issues": [{"key": "DATA-1"}, {"key": "DATA-2"}],
            "isLast": False,
            "nextPageToken": "token-page-2",
        }
        # Page 2: 1 issue, last page
        page2 = {
            "issues": [{"key": "DATA-3"}],
            "isLast": True,
        }
        
        with patch.object(client._session, "request") as mock_request:
            mock_request.side_effect = [
                mock_response(200, page1),
                mock_response(200, page2),
            ]
            
            issues = list(client.iter_search_issues("project = DATA", page_size=2))
        
        assert len(issues) == 3
        assert [issue["key"] for issue in issues] == ["DATA-1", "DATA-2", "DATA-3"]


@pytest.mark.integration
class TestJiraClientIntegration:
    """Integration tests requiring live Jira credentials.
    
    Set these environment variables to run:
      JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN
    
    Run with: pytest -m integration
    """

    @pytest.fixture(scope="class")
    def client(self):
        """Create client from environment."""
        import os
        base_url = os.getenv("JIRA_URL")
        username = os.getenv("JIRA_USERNAME")
        api_token = os.getenv("JIRA_API_TOKEN")
        
        if not all([base_url, username, api_token]):
            pytest.skip("Jira credentials not configured")
        
        return JiraClient(base_url=base_url, username=username, api_token=api_token)

    def test_get_fields_live(self, client):
        """Fetch fields from live Jira instance."""
        fields = client.get_fields()
        assert isinstance(fields, list)
        assert len(fields) > 0
        assert "id" in fields[0]
        assert "name" in fields[0]

    def test_search_issues_live(self, client):
        """Search issues on live instance."""
        # Search for recent issues (any project)
        response = client.search_issues(
            jql="ORDER BY created DESC",
            max_results=5,
        )
        assert "issues" in response
        assert "total" in response
