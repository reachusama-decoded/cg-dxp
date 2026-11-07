"""Unit tests for skills/core/jira.py.

Covers:
- check_jira_connectivity (success + AuthError)
- create_epic_with_stories (happy path, sprint assignment, no sprint)
- fetch_sprint_backlog (happy path)
"""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, call, patch

import pytest

from skills.clients.exceptions import AuthError, CatalystClientError
from skills.clients.jira import FieldIds, JiraClient
from skills.core.jira import (
    check_jira_connectivity,
    create_epic_with_stories,
    fetch_sprint_backlog,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_client(**kwargs) -> Mock:
    """Return a Mock with JiraClient spec and sane defaults."""
    client = Mock(spec=JiraClient)
    client.base_url = "https://test.atlassian.net"
    client.text_to_adf = JiraClient.text_to_adf  # use real static method
    for k, v in kwargs.items():
        setattr(client, k, v)
    return client


def _field_ids(*, epic_name="customfield_10011", epic_link="customfield_10014"):
    return FieldIds(epic_name=epic_name, epic_link=epic_link)


# ---------------------------------------------------------------------------
# check_jira_connectivity
# ---------------------------------------------------------------------------

class TestCheckJiraConnectivity:

    @pytest.mark.unit
    def test_success(self):
        """Returns (True, message) when get_fields succeeds."""
        client = _make_client()
        client.get_fields.return_value = [{"id": "summary"}]

        ok, msg = check_jira_connectivity(client)

        assert ok is True
        assert "verified" in msg.lower()
        client.get_fields.assert_called_once()

    @pytest.mark.unit
    def test_auth_error(self):
        """Returns (False, message) on AuthError."""
        client = _make_client()
        client.get_fields.side_effect = AuthError("401 Unauthorized")

        ok, msg = check_jira_connectivity(client)

        assert ok is False
        assert "authentication" in msg.lower()

    @pytest.mark.unit
    def test_generic_client_error(self):
        """Returns (False, message) on any other CatalystClientError."""
        client = _make_client()
        client.get_fields.side_effect = CatalystClientError("timeout")

        ok, msg = check_jira_connectivity(client)

        assert ok is False
        assert "connection" in msg.lower() or "failed" in msg.lower()


# ---------------------------------------------------------------------------
# create_epic_with_stories
# ---------------------------------------------------------------------------

class TestCreateEpicWithStories:

    @pytest.mark.unit
    def test_happy_path_creates_epic_and_stories(self):
        """Creates epic, then creates and links each story."""
        client = _make_client()
        client.create_issue.side_effect = [
            {"key": "DATA-1"},   # epic
            {"key": "DATA-2"},   # story 1
            {"key": "DATA-3"},   # story 2
        ]
        fids = _field_ids()

        result = create_epic_with_stories(
            client,
            project_key="DATA",
            epic_name="Q2 Work",
            epic_summary="Q2 2026 Epic",
            epic_description="Build things",
            stories=[
                {"summary": "Story A"},
                {"summary": "Story B", "description": "Details"},
            ],
            field_ids=fids,
        )

        assert result["epic_key"] == "DATA-1"
        assert result["story_keys"] == ["DATA-2", "DATA-3"]
        assert result["stories_added_to_sprint"] is False

        # Epic create payload has the epic_name custom field
        epic_call_fields = client.create_issue.call_args_list[0][0][0]["fields"]
        assert epic_call_fields["issuetype"]["name"] == "Epic"
        assert epic_call_fields[fids.epic_name] == "Q2 Work"

        # Stories linked via epic_link field
        assert client.update_issue.call_count == 2
        update_calls = client.update_issue.call_args_list
        assert update_calls[0] == call("DATA-2", {fids.epic_link: "DATA-1"})
        assert update_calls[1] == call("DATA-3", {fids.epic_link: "DATA-1"})

    @pytest.mark.unit
    def test_sprint_assignment_fires_when_sprint_id_provided(self):
        """Stories are added to sprint when sprint_id is passed."""
        client = _make_client()
        client.create_issue.side_effect = [
            {"key": "DATA-10"},  # epic
            {"key": "DATA-11"},  # story
        ]
        fids = _field_ids()

        result = create_epic_with_stories(
            client,
            project_key="DATA",
            epic_name="Sprint Work",
            epic_summary="Sprint Epic",
            epic_description="Sprint scope",
            stories=[{"summary": "Do a thing"}],
            field_ids=fids,
            sprint_id=42,
        )

        assert result["stories_added_to_sprint"] is True
        client.add_issues_to_sprint.assert_called_once_with(42, ["DATA-11"])

    @pytest.mark.unit
    def test_no_sprint_skips_sprint_call(self):
        """add_issues_to_sprint is NOT called when sprint_id is None."""
        client = _make_client()
        client.create_issue.side_effect = [{"key": "P-1"}, {"key": "P-2"}]
        fids = _field_ids()

        result = create_epic_with_stories(
            client,
            project_key="P",
            epic_name="E",
            epic_summary="S",
            epic_description="D",
            stories=[{"summary": "T"}],
            field_ids=fids,
        )

        assert result["stories_added_to_sprint"] is False
        client.add_issues_to_sprint.assert_not_called()

    @pytest.mark.unit
    def test_acceptance_criteria_populates_custom_field_and_description(self):
        """When story has acceptance_criteria, both the AC custom field
        (ADF bulletList) and the description bullet section are populated."""
        client = _make_client()
        client.create_issue.side_effect = [
            {"key": "AICAT-1"},  # epic
            {"key": "AICAT-2"},  # story
        ]
        fids = FieldIds(
            epic_name="customfield_10011",
            epic_link="customfield_10014",
            acceptance_criteria="customfield_10170",
        )

        create_epic_with_stories(
            client,
            project_key="AICAT",
            epic_name="AC Epic",
            epic_summary="AC Epic Summary",
            epic_description="Epic body",
            stories=[{
                "summary": "Story with AC",
                "description": "Story body",
                "acceptance_criteria": ["AC1", "AC2"],
            }],
            field_ids=fids,
        )

        story_fields = client.create_issue.call_args_list[1][0][0]["fields"]

        assert story_fields["customfield_10170"] == {
            "type": "doc",
            "version": 1,
            "content": [{
                "type": "bulletList",
                "content": [
                    {"type": "listItem", "content": [
                        {"type": "paragraph", "content": [
                            {"type": "text", "text": "AC1"}
                        ]}
                    ]},
                    {"type": "listItem", "content": [
                        {"type": "paragraph", "content": [
                            {"type": "text", "text": "AC2"}
                        ]}
                    ]},
                ],
            }],
        }

        assert "acceptance_criteria" not in story_fields

        description_text_nodes = [
            node["content"][0]["text"]
            for node in story_fields["description"]["content"]
            if node.get("type") == "paragraph"
        ]
        joined = " ".join(description_text_nodes)
        assert "Acceptance Criteria:" in joined
        assert "AC1" in joined
        assert "AC2" in joined

    @pytest.mark.unit
    def test_acceptance_criteria_without_field_id_falls_back_to_description(self, caplog):
        """When AC field id is not discovered, description still gets the AC
        section and a warning is logged; no AC custom field is set."""
        client = _make_client()
        client.create_issue.side_effect = [
            {"key": "P-1"},
            {"key": "P-2"},
        ]
        fids = FieldIds(
            epic_name="customfield_10011",
            epic_link="customfield_10014",
            acceptance_criteria=None,
        )

        import logging as _logging
        with caplog.at_level(_logging.WARNING):
            create_epic_with_stories(
                client,
                project_key="P",
                epic_name="E",
                epic_summary="S",
                epic_description="",
                stories=[{
                    "summary": "Story no AC field",
                    "acceptance_criteria": ["only AC"],
                }],
                field_ids=fids,
            )

        story_fields = client.create_issue.call_args_list[1][0][0]["fields"]
        custom_field_keys = [k for k in story_fields if k.startswith("customfield_")]
        assert custom_field_keys == []
        assert "description" in story_fields
        assert any("Acceptance Criteria field id not discovered" in r.message for r in caplog.records)

    @pytest.mark.unit
    def test_field_ids_auto_discovered_when_not_provided(self):
        """get_fields + discover_field_ids is called when field_ids is None."""
        client = _make_client()
        # Return enough field data for discover_field_ids to find epic_name
        client.get_fields.return_value = [
            {"id": "customfield_10011", "name": "Epic Name", "schema": {"type": "string"}},
        ]
        client.create_issue.side_effect = [{"key": "X-1"}, {"key": "X-2"}]

        create_epic_with_stories(
            client,
            project_key="X",
            epic_name="Auto",
            epic_summary="Auto Epic",
            epic_description="",
            stories=[{"summary": "Auto Story"}],
            field_ids=None,  # trigger auto-discovery
        )

        client.get_fields.assert_called_once()


# ---------------------------------------------------------------------------
# fetch_sprint_backlog
# ---------------------------------------------------------------------------

class TestFetchSprintBacklog:

    @pytest.mark.unit
    def test_happy_path(self):
        """Returns sprint_id, issues list, and total count."""
        issues = [
            {"key": "DATA-1", "fields": {"summary": "Task 1"}},
            {"key": "DATA-2", "fields": {"summary": "Task 2"}},
        ]
        client = _make_client()
        client.iter_search_issues.return_value = iter(issues)

        result = fetch_sprint_backlog(client, sprint_id=99)

        assert result["sprint_id"] == 99
        assert result["issues"] == issues
        assert result["total"] == 2
        client.iter_search_issues.assert_called_once_with("sprint = 99", fields=None)

    @pytest.mark.unit
    def test_fields_forwarded(self):
        """fields param is forwarded to iter_search_issues."""
        client = _make_client()
        client.iter_search_issues.return_value = iter([])

        fetch_sprint_backlog(client, sprint_id=7, fields=["summary", "status"])

        client.iter_search_issues.assert_called_once_with("sprint = 7", fields=["summary", "status"])
