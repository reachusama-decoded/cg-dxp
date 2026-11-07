"""Unit tests for skills.clients.confluence.ConfluenceClient.

All tests are offline — HTTP calls are intercepted with unittest.mock.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch, call

import pytest
import requests

from skills.clients.confluence import ConfluenceClient
from skills.clients.exceptions import ConflictError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_client(**kwargs) -> ConfluenceClient:
    defaults = {
        "base_url": "https://confluence.example.com",
        "email": "user@example.com",
        "token": "my-api-token",
    }
    defaults.update(kwargs)
    return ConfluenceClient(**defaults)


def _mock_response(json_data: dict, status_code: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()  # no-op for 2xx
    return resp


# ---------------------------------------------------------------------------
# Construction tests
# ---------------------------------------------------------------------------


class TestInit:
    def test_init_requires_base_url(self):
        with pytest.raises(ValueError, match="base_url"):
            ConfluenceClient(base_url="", email="u@e.com", token="tok")

    def test_init_requires_email(self):
        with pytest.raises(ValueError, match="email"):
            ConfluenceClient(
                base_url="https://confluence.example.com",
                email="",
                token="tok",
            )

    def test_init_requires_token(self):
        with pytest.raises(ValueError, match="token"):
            ConfluenceClient(
                base_url="https://confluence.example.com",
                email="u@e.com",
                token="",
            )

    def test_init_stores_config(self):
        client = _make_client()
        assert client.base_url == "https://confluence.example.com"
        assert client.email == "user@example.com"

    def test_init_strips_trailing_slash(self):
        client = _make_client(base_url="https://confluence.example.com/")
        assert client.base_url == "https://confluence.example.com"

    def test_init_configures_session_auth(self):
        client = _make_client()
        assert client._session.auth == ("user@example.com", "my-api-token")


# ---------------------------------------------------------------------------
# get_page tests
# ---------------------------------------------------------------------------


class TestGetPage:
    def test_get_page_constructs_correct_url(self):
        """get_page must call the REST API with the right URL and expand params."""
        client = _make_client()

        page_payload = {
            "id": "12345",
            "title": "My Page",
            "body": {"storage": {"value": "<p>Hello</p>"}},
            "version": {"number": 3},
            "space": {"key": "PROJ", "name": "Project"},
            "ancestors": [],
        }

        with patch.object(client._session, "get") as mock_get:
            mock_get.return_value = _mock_response(page_payload)
            result = client.get_page("12345")

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        url_called = call_args.args[0] if call_args.args else call_args.kwargs.get("url")
        assert url_called == "https://confluence.example.com/wiki/api/v2/pages/12345"

        params = call_args.kwargs.get("params") or (
            call_args.args[1] if len(call_args.args) > 1 else {}
        )
        assert "body-format" in params
        assert result == page_payload

    def test_get_page_falls_back_to_v1_on_404(self):
        """When v2 returns 404, get_page retries with the v1 URL and expand params."""
        client = _make_client()

        page_payload = {
            "id": "12345",
            "title": "My Page",
            "body": {"storage": {"value": "<p>Hello</p>"}},
            "version": {"number": 3},
            "space": {"key": "PROJ", "name": "Project"},
            "ancestors": [],
        }

        v2_resp = MagicMock()
        v2_resp.status_code = 404
        v1_resp = _mock_response(page_payload)

        with patch.object(client._session, "get", side_effect=[v2_resp, v1_resp]) as mock_get:
            result = client.get_page("12345")

        assert mock_get.call_count == 2
        v1_call = mock_get.call_args_list[1]
        url_called = v1_call.args[0] if v1_call.args else v1_call.kwargs.get("url")
        assert url_called == "https://confluence.example.com/wiki/rest/api/content/12345"
        params = v1_call.kwargs.get("params") or {}
        assert params["expand"] == "body.storage,version,space,ancestors"
        assert result == page_payload

    def test_get_page_raises_on_empty_page_id(self):
        client = _make_client()
        with pytest.raises(ValueError, match="page_id"):
            client.get_page("")

    def test_get_page_propagates_http_errors(self):
        client = _make_client()
        error_response = MagicMock()
        error_response.status_code = 403
        http_error = requests.HTTPError(response=error_response)

        with patch.object(client._session, "get") as mock_get:
            bad_resp = MagicMock()
            bad_resp.raise_for_status.side_effect = http_error
            mock_get.return_value = bad_resp

            with pytest.raises(requests.HTTPError):
                client.get_page("99999")


# ---------------------------------------------------------------------------
# get_page_tree tests
# ---------------------------------------------------------------------------


class TestGetPageTree:
    def _make_page(self, page_id: str, title: str = "Page") -> dict:
        return {
            "id": page_id,
            "title": title,
            "body": {"storage": {"value": ""}},
            "version": {"number": 1},
            "space": {"key": "X", "name": "X"},
            "ancestors": [],
        }

    def _make_children_response(self, child_ids: list[str]) -> dict:
        return {
            "results": [{"id": cid, "title": f"Child {cid}"} for cid in child_ids],
            "_links": {},
        }

    def test_get_page_tree_single_page(self):
        """A page with no children should return a list with just that page."""
        client = _make_client()

        with patch.object(client, "get_page") as mock_get_page, \
             patch.object(client, "_get_children") as mock_children:
            mock_get_page.return_value = self._make_page("1")
            mock_children.return_value = []

            result = client.get_page_tree("1")

        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_get_page_tree_with_children(self):
        """Parent and children should both appear in the result list."""
        client = _make_client()

        pages = {
            "1": self._make_page("1", "Parent"),
            "2": self._make_page("2", "Child A"),
            "3": self._make_page("3", "Child B"),
        }
        children_map = {"1": [{"id": "2"}, {"id": "3"}], "2": [], "3": []}

        with patch.object(client, "get_page", side_effect=lambda pid: pages[pid]), \
             patch.object(client, "_get_children", side_effect=lambda pid: children_map[pid]):
            result = client.get_page_tree("1")

        ids = [p["id"] for p in result]
        assert "1" in ids
        assert "2" in ids
        assert "3" in ids
        assert len(ids) == 3

    def test_get_page_tree_avoids_cycles(self):
        """Already-seen page IDs must not be fetched a second time."""
        client = _make_client()

        pages = {"1": self._make_page("1")}
        call_count = {"get_page": 0}

        def _get_page(pid):
            call_count["get_page"] += 1
            return pages[pid]

        # Children always returns page 1 — would loop forever without cycle guard
        with patch.object(client, "get_page", side_effect=_get_page), \
             patch.object(client, "_get_children", return_value=[{"id": "1"}]):
            result = client.get_page_tree("1")

        # Should only have fetched page 1 once
        assert call_count["get_page"] == 1
        assert len(result) == 1


# ---------------------------------------------------------------------------
# _get_children tests
# ---------------------------------------------------------------------------


class TestGetChildren:
    def test_get_children_constructs_correct_url(self):
        """_get_children must call the v2 /children endpoint, not the v1 /child/page path."""
        client = _make_client()
        data = {"results": [{"id": "2", "title": "Child"}], "_links": {}}

        with patch.object(client._session, "get") as mock_get:
            mock_get.return_value = _mock_response(data)
            result = client._get_children("12345")

        url_called = mock_get.call_args.args[0]
        assert url_called == "https://confluence.example.com/wiki/api/v2/pages/12345/children"
        assert result == [{"id": "2", "title": "Child"}]

    def test_get_children_returns_empty_on_404(self):
        client = _make_client()
        error_response = MagicMock()
        error_response.status_code = 404
        http_error = requests.HTTPError(response=error_response)

        with patch.object(client._session, "get") as mock_get:
            bad_resp = MagicMock()
            bad_resp.raise_for_status.side_effect = http_error
            mock_get.return_value = bad_resp

            result = client._get_children("12345")

        assert result == []


# ---------------------------------------------------------------------------
# update_page tests
# ---------------------------------------------------------------------------


class TestUpdatePage:
    def test_update_page_success(self):
        client = _make_client()
        updated = {
            "id": "12345",
            "title": "My Page",
            "version": {"number": 4},
            "body": {"storage": {"value": "<h2>New content</h2>"}},
        }

        with patch.object(client._session, "put") as mock_put:
            mock_put.return_value = _mock_response(updated)
            result = client.update_page(
                page_id="12345",
                title="My Page",
                body_storage="<h2>New content</h2>",
                current_version=3,
            )

        mock_put.assert_called_once()
        call_args = mock_put.call_args
        url_called = call_args.args[0] if call_args.args else call_args.kwargs.get("url")
        assert url_called == "https://confluence.example.com/wiki/rest/api/content/12345"

        payload = call_args.kwargs["json"]
        assert payload["id"] == "12345"
        assert payload["type"] == "page"
        assert payload["title"] == "My Page"
        assert payload["body"]["storage"]["value"] == "<h2>New content</h2>"
        assert payload["body"]["storage"]["representation"] == "storage"
        assert payload["version"]["number"] == 4
        assert result == updated

    def test_update_page_raises_on_empty_page_id(self):
        client = _make_client()
        with pytest.raises(ValueError, match="page_id"):
            client.update_page(
                page_id="",
                title="My Page",
                body_storage="<p>Body</p>",
                current_version=1,
            )

    def test_update_page_raises_on_whitespace_page_id(self):
        client = _make_client()
        with pytest.raises(ValueError, match="page_id"):
            client.update_page(
                page_id="   ",
                title="My Page",
                body_storage="<p>Body</p>",
                current_version=1,
            )

    def test_update_page_raises_conflict_error_on_409(self):
        client = _make_client()
        with patch.object(client._session, "put") as mock_put:
            resp = MagicMock()
            resp.status_code = 409
            mock_put.return_value = resp

            with pytest.raises(ConflictError) as exc_info:
                client.update_page(
                    page_id="12345",
                    title="My Page",
                    body_storage="<p>Body</p>",
                    current_version=1,
                )
            assert "12345" in str(exc_info.value)
            assert "re-fetch" in str(exc_info.value).lower()

    def test_update_page_coerces_non_integer_version(self):
        """current_version is cast via int() — floats and numeric strings work."""
        client = _make_client()
        updated = {"id": "12345", "version": {"number": 3}}

        with patch.object(client._session, "put") as mock_put:
            mock_put.return_value = _mock_response(updated)
            client.update_page(
                page_id="12345",
                title="My Page",
                body_storage="<p>Body</p>",
                current_version=2.0,  # float — must not raise
            )
        payload = mock_put.call_args.kwargs["json"]
        assert payload["version"]["number"] == 3

    def test_update_page_propagates_http_error(self):
        client = _make_client()
        error_response = MagicMock()
        error_response.status_code = 403
        http_error = requests.HTTPError(response=error_response)

        with patch.object(client._session, "put") as mock_put:
            bad_resp = MagicMock()
            bad_resp.status_code = 403
            bad_resp.raise_for_status.side_effect = http_error
            mock_put.return_value = bad_resp

            with pytest.raises(requests.HTTPError) as exc_info:
                client.update_page(
                    page_id="12345",
                    title="My Page",
                    body_storage="<p>Body</p>",
                    current_version=1,
                )
            assert exc_info.value.response.status_code == 403


class TestFindChildByTitle:
    def test_returns_the_exact_title_match(self):
        client = _make_client()
        children = [{"id": "1", "title": "Other"},
                    {"id": "2", "title": "AI Catalyst: Getting Started FAQ"}]
        with patch.object(client, "_get_children", return_value=children):
            found = client.find_child_by_title("999", "AI Catalyst: Getting Started FAQ")
        assert found["id"] == "2"

    def test_tolerates_surrounding_whitespace(self):
        client = _make_client()
        with patch.object(client, "_get_children",
                          return_value=[{"id": "3", "title": "  Onboarding FAQ  "}]):
            assert client.find_child_by_title("999", "Onboarding FAQ")["id"] == "3"

    def test_does_not_match_a_near_title(self):
        """A publisher that 'finds' a near-match overwrites the wrong page, and a
        shared space has no undo for that."""
        client = _make_client()
        with patch.object(client, "_get_children",
                          return_value=[{"id": "4", "title": "Getting Started FAQ v2"}]):
            assert client.find_child_by_title("999", "Getting Started FAQ") is None

    def test_returns_none_when_there_are_no_children(self):
        client = _make_client()
        with patch.object(client, "_get_children", return_value=[]):
            assert client.find_child_by_title("999", "Anything") is None

    def test_rejects_an_empty_parent_id(self):
        client = _make_client()
        with pytest.raises(ValueError):
            client.find_child_by_title("", "Anything")


class TestCreatePage:
    def test_creates_a_child_page_with_storage_body(self):
        client = _make_client()
        with patch.object(client._session, "post") as mock_post:
            mock_post.return_value = _mock_response({"id": "55555"})
            result = client.create_page(
                space_key="ENTDATA",
                title="AI Catalyst: Getting Started FAQ",
                body_storage="<p>Body</p>",
                parent_id="404951408",
            )
        assert result["id"] == "55555"
        call = mock_post.call_args
        url = call.args[0] if call.args else call.kwargs.get("url")
        assert url == "https://confluence.example.com/wiki/rest/api/content"
        payload = call.kwargs["json"]
        assert payload["space"] == {"key": "ENTDATA"}
        assert payload["ancestors"] == [{"id": "404951408"}]
        assert payload["body"]["storage"]["representation"] == "storage"

    def test_omits_ancestors_when_no_parent_given(self):
        client = _make_client()
        with patch.object(client._session, "post") as mock_post:
            mock_post.return_value = _mock_response({"id": "1"})
            client.create_page("ENTDATA", "T", "<p>b</p>")
        assert "ancestors" not in mock_post.call_args.kwargs["json"]

    def test_rejects_empty_space_or_title(self):
        client = _make_client()
        with pytest.raises(ValueError):
            client.create_page("", "T", "<p>b</p>")
        with pytest.raises(ValueError):
            client.create_page("ENTDATA", "", "<p>b</p>")

    def test_rejects_a_malformed_parent_id(self):
        client = _make_client()
        with pytest.raises(ValueError):
            client.create_page("ENTDATA", "T", "<p>b</p>", parent_id="   ")
