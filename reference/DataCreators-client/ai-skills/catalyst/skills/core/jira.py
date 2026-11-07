"""Higher-level Jira helpers for Catalyst skills.

Builds on the JiraClient to provide workflow orchestration:
- Creating epics with stories
- Fetching sprint backlogs
- Connectivity validation

These helpers make it easier for skills to work with Jira without
dealing with low-level API details.

Consuming skill: ``skills/jira-create-epics-stories/`` (landing in a follow-up
PR, AICAT-54) — that skill is the primary caller of ``create_epic_with_stories``
and ``fetch_sprint_backlog``. ``check_jira_connectivity`` is used by
``scripts/setup.py`` during credential validation.
"""

from __future__ import annotations

import logging
from typing import Any

from skills.clients.exceptions import AuthError, CatalystClientError
from skills.clients.jira import FieldIds, JiraClient, discover_field_ids

logger = logging.getLogger(__name__)


def _acceptance_criteria_adf(items: list[str]) -> dict[str, Any]:
    """Render an acceptance-criteria bullet list as an ADF document.

    The Jira AC custom field reports schema.type=string from field-search
    but the issue update endpoint requires ADF — hence the bulletList
    shape rather than a plain string.
    """
    return {
        "type": "doc",
        "version": 1,
        "content": [{
            "type": "bulletList",
            "content": [
                {"type": "listItem", "content": [
                    {"type": "paragraph", "content": [
                        {"type": "text", "text": item}
                    ]}
                ]}
                for item in items
            ],
        }],
    }


def check_jira_connectivity(client: JiraClient) -> tuple[bool, str]:
    """Validate Jira connectivity and credentials.
    
    Quick health check before running Jira operations.
    Attempts to fetch field metadata as a lightweight auth test.
    
    Args:
        client: Configured JiraClient instance.
        
    Returns:
        Tuple of (success: bool, message: str).
        
    Example:
        client = JiraClient(...)
        success, msg = check_jira_connectivity(client)
        if not success:
            print(f"Jira connection failed: {msg}")
    """
    try:
        # Fetch a lightweight resource to verify auth
        client.get_fields()
        return True, "Jira connectivity verified"
    except AuthError as e:
        return False, f"Authentication failed: {e}"
    except CatalystClientError as e:
        return False, f"Connection failed: {e}"


def create_epic_with_stories(
    client: JiraClient,
    project_key: str,
    epic_name: str,
    epic_summary: str,
    epic_description: str,
    stories: list[dict[str, Any]],
    *,
    field_ids: FieldIds | None = None,
    sprint_id: int | None = None,
) -> dict[str, Any]:
    """Create an epic and associate stories to it.
    
    Orchestrates:
    1. Field ID discovery (if not provided)
    2. Epic creation with Epic Name field
    3. Story creation
    4. Linking stories to epic
    5. Optional sprint assignment
    
    Args:
        client: JiraClient instance.
        project_key: Jira project key (e.g. "DATA").
        epic_name: Short epic name for agile boards.
        epic_summary: Epic summary/title.
        epic_description: Epic description (plain text, converted to ADF).
        stories: List of story definitions. Each must have:
                 - summary: str
                 - description: str (optional)
                 - Additional fields can be included
        field_ids: Pre-discovered field IDs. If None, auto-discovers.
        sprint_id: Optional sprint ID to add stories to.
        
    Returns:
        Dictionary with:
        - epic_key: Created epic key
        - epic_url: Epic URL
        - story_keys: List of created story keys
        - stories_added_to_sprint: bool (if sprint_id provided)
        
    Raises:
        CatalystClientError: On any API failure.
        ValueError: If field IDs can't be discovered and not provided.
        
    Example:
        result = create_epic_with_stories(
            client,
            project_key="DATA",
            epic_name="Q2 Pipeline Work",
            epic_summary="Q2 2026 Data Pipeline Epic",
            epic_description="Build new pipelines for Q2 roadmap",
            stories=[
                {"summary": "Build ingestion layer", "description": "..."},
                {"summary": "Add data quality checks", "description": "..."},
            ],
            sprint_id=123,
        )
        print(f"Created {result['epic_key']} with {len(result['story_keys'])} stories")
    """
    # Discover field IDs if not provided
    if field_ids is None:
        logger.info("Discovering Jira custom field IDs...")
        fields = client.get_fields()
        field_ids = discover_field_ids(fields)
        logger.info("Discovered field IDs: %s", field_ids)
    
    if not field_ids.epic_name:
        raise ValueError(
            "Epic Name field ID not found. Provide field_ids explicitly or ensure "
            "your Jira instance has an 'Epic Name' custom field."
        )
    
    # Create the epic
    logger.info("Creating epic '%s' in project %s...", epic_summary, project_key)
    epic_payload = {
        "fields": {
            "project": {"key": project_key},
            "issuetype": {"name": "Epic"},
            "summary": epic_summary,
            "description": client.text_to_adf(epic_description),
            field_ids.epic_name: epic_name,
        }
    }
    epic_result = client.create_issue(epic_payload)
    epic_key = epic_result["key"]
    epic_url = f"{client.base_url}/browse/{epic_key}"
    logger.info("Created epic %s", epic_key)
    
    # Create stories
    story_keys: list[str] = []
    for idx, story in enumerate(stories, 1):
        logger.info("Creating story %d/%d: %s", idx, len(stories), story["summary"])

        story_payload = {
            "fields": {
                "project": {"key": project_key},
                "issuetype": {"name": "Story"},
                "summary": story["summary"],
            }
        }

        ac_items = story.get("acceptance_criteria") or []

        description_text = story.get("description", "")
        if ac_items:
            ac_block = "Acceptance Criteria:\n" + "\n".join(f"- {item}" for item in ac_items)
            description_text = f"{description_text}\n\n{ac_block}" if description_text else ac_block

        if description_text:
            story_payload["fields"]["description"] = client.text_to_adf(description_text)

        if ac_items:
            if field_ids.acceptance_criteria:
                story_payload["fields"][field_ids.acceptance_criteria] = _acceptance_criteria_adf(ac_items)
            else:
                logger.warning(
                    "Acceptance Criteria field id not discovered for story '%s'; "
                    "falling back to description-only. Transition validators that "
                    "require the AC custom field will block status changes. Set "
                    "JIRA_ACCEPTANCE_CRITERIA_FIELD_ID to override.",
                    story["summary"],
                )

        # Copy any additional fields from story dict
        for key, value in story.items():
            if key not in {"summary", "description", "acceptance_criteria"}:
                story_payload["fields"][key] = value

        story_result = client.create_issue(story_payload)
        story_key = story_result["key"]
        story_keys.append(story_key)
        logger.info("Created story %s", story_key)
        
        # Link story to epic
        if field_ids.epic_link:
            # Use Epic Link field (Jira Classic)
            logger.debug("Linking %s to epic via Epic Link field", story_key)
            client.update_issue(story_key, {field_ids.epic_link: epic_key})
        else:
            # Use parent relationship (Jira Next-Gen)
            logger.debug("Linking %s to epic via parent relationship", story_key)
            client.update_issue(story_key, {"parent": {"key": epic_key}})
    
    # Add stories to sprint if requested
    stories_added_to_sprint = False
    if sprint_id and story_keys:
        logger.info("Adding %d stories to sprint %d...", len(story_keys), sprint_id)
        client.add_issues_to_sprint(sprint_id, story_keys)
        stories_added_to_sprint = True
        logger.info("Stories added to sprint")
    
    return {
        "epic_key": epic_key,
        "epic_url": epic_url,
        "story_keys": story_keys,
        "stories_added_to_sprint": stories_added_to_sprint,
    }


def fetch_sprint_backlog(
    client: JiraClient,
    sprint_id: int,
    *,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Fetch all issues in a sprint.
    
    Args:
        client: JiraClient instance.
        sprint_id: Numeric sprint ID.
        fields: Field names to include. None = all fields.
        
    Returns:
        Dictionary with:
        - sprint_id: int
        - issues: list[dict] — Issue data
        - total: int — Total issue count
        
    Raises:
        CatalystClientError: On API failure.
        
    Example:
        backlog = fetch_sprint_backlog(client, sprint_id=123, fields=["summary", "status"])
        for issue in backlog["issues"]:
            print(f"{issue['key']}: {issue['fields']['summary']}")
    """
    # Use JQL to find issues in sprint
    jql = f"sprint = {sprint_id}"
    
    issues = list(client.iter_search_issues(jql, fields=fields))
    
    return {
        "sprint_id": sprint_id,
        "issues": issues,
        "total": len(issues),
    }
