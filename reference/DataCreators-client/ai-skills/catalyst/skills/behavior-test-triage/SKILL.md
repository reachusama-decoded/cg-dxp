---
name: behavior-test-triage
description: |
  Automate the full behavior-test triage loop: generate a categorized
  triage report, open a Jira epic + per-finding tickets in AICAT, post
  back-link comments on the GitHub issues, and update the Confluence triage
  page with a ticket-to-issue mapping table. Trigger phrases: "run triage",
  "triage behavior tests", "create triage tickets", "file behavior test issues
  to Jira", "bt triage".
allowed-tools: Bash(python3:*) Bash(bin/bt:*) Bash(gh:*) Read Write
metadata:
  tier: capability
  # lifecycle-phase "none" — maintainer tooling, not a DPLC phase skill
  lifecycle-phase: none
  # dependencies lists cross-skill invocations only; platform prerequisites
  # (bin/bt triage subcommand, ConfluenceClient.update_page) are delivered by
  # AICAT-164 / PR #146 and must be merged before this skill is functional.
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: [jira, confluence]
---

# Behavior Test Triage

Automate the post-run triage loop: read cached behavior-test results,
classify failures, file Jira tickets, back-link GitHub issues, and update
the Confluence triage page.

**Prerequisites:**
- `bin/bt full` or `bin/bt execute` has been run (cache exists)
- Environment: `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`,
  `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN`
- `gh` CLI authenticated

---

## Step 0 — Check for cached results

Before doing anything else, verify that cached behavior-test results exist:

```bash
ls workspace/behavior-tests/cache/*__with_skill.json 2>/dev/null
```

**If cache files exist:** proceed to Step 1.

**If no cache files exist** (command produces no output), stop and tell the user:

> "No cached behavior-test results found in `workspace/behavior-tests/cache/`.
> Run `bin/bt execute` (or `bin/bt full`) first, then re-invoke
> `/behavior-test-triage`."

---

## Step 1 — Parse arguments and run `bin/bt triage`

Parse `$ARGUMENTS` for:
- `--version <v>` — runtime version string (e.g. `ai-catalyst-1.7.0`).
  **Required.** If absent, ask: "What is the plugin version for this triage
  run? (e.g. ai-catalyst-1.7.0)"
- `--confluence-page <id>` — Confluence page ID for the triage report.
  If absent, ask: "What is the Confluence page ID for the triage report?"

Run `bin/bt triage` with `--lookup-gh-issues` so findings include GitHub
issue numbers for back-linking in Step 5:

```bash
bin/bt triage --version <version> --lookup-gh-issues
```

If `bin/bt triage` exits 1 (no cached results), stop and tell the user:
> "No cached results found. Run `bin/bt full` or `bin/bt execute` first,
> then re-invoke this skill."

Bind the parsed output to variables for use in subsequent steps:

```python
import json, sys

version = "<version from --version argument>"
confluence_page_id = "<page id from --confluence-page argument>"

# Parse bin/bt triage JSON output (captured from the Bash step above)
report = json.loads(triage_output)   # triage_output = stdout from bin/bt triage
findings          = report["findings"]
failed_cases      = report["summary"]["failed_cases"]
```

---

## Step 2 — Initialize clients and discover custom field IDs

Write a runner script that will hold all shared state across Steps 2–6.
The model must write this file first, then execute it once in Step 6.

Create `_triage_runner.py` at repo root with the following structure
(fill in `version`, `confluence_page_id`, and `findings` from Step 1
before writing the file):

```python
import html
import json
import os
import subprocess
import sys

from skills.clients.jira import JiraClient, discover_field_ids
from skills.clients.confluence import ConfluenceClient

version            = "<substituted from Step 1>"
confluence_page_id = "<substituted from Step 1>"
findings           = <substituted from Step 1 JSON>
failed_cases       = <substituted from Step 1 JSON>

jira = JiraClient(
    base_url=os.environ["JIRA_URL"],
    username=os.environ["JIRA_USERNAME"],
    api_token=os.environ["JIRA_API_TOKEN"],
)
confluence = ConfluenceClient(
    base_url=os.environ["CONFLUENCE_URL"],
    email=os.environ.get("CONFLUENCE_USERNAME") or os.environ["JIRA_USERNAME"],
    token=os.environ["CONFLUENCE_API_TOKEN"],
)

# Discover field IDs at runtime — never hard-code customfield_NNNNN.
all_fields = jira.get_fields()
field_ids = discover_field_ids(all_fields)
# field_ids.epic_name, field_ids.epic_link, field_ids.acceptance_criteria
```

If any environment variable is missing, stop and list which ones are
absent with instructions to add them to `.env`.

---

## Step 3 — Create the triage epic in AICAT

Create a single Epic to group all findings for this release:

```python
epic_summary = f"Behavior test triage — {version}"

epic_payload = {
    "fields": {
        "project": {"key": "AICAT"},
        "issuetype": {"name": "Epic"},
        "summary": epic_summary,
        "description": JiraClient.text_to_adf(
            f"Triage epic for behavior test run against {version}.\n\n"
            f"Generated by behavior-test-triage skill.\n"
            f"{failed_cases} failing case(s) across "
            f"{len(findings)} finding(s)."
        ),
    }
}
if field_ids.epic_name:
    epic_payload["fields"][field_ids.epic_name] = epic_summary

epic = jira.create_issue(epic_payload)
epic_key = epic["key"]
```

---

## Step 4 — Create per-finding Jira tickets

Use the priority and issue type mapping from the AICAT-78 taxonomy:

| failure_type | Issue type | Priority | Batching |
|---|---|---|---|
| `orchestrator-delegation` | Story | High | One per finding |
| `harness` | Story | High | One per finding |
| `template-conformance` | Story | Medium | Batch all into one |
| `shared-code` | Task | Medium | One per finding |
| `quick-fix` | Task | Low | One per finding |

For the `template-conformance` batch: group all conformance findings into
a single Story titled "Fix template conformance — `{version}`" listing
each case in the description. For all other types: one ticket per finding.

```python
created_tickets = []  # list of dicts: {finding, ticket_key, ticket_url}

# Group template-conformance findings for batching
conformance = [f for f in findings if f["failure_type"] == "template-conformance"]
others = [f for f in findings if f["failure_type"] != "template-conformance"]

def _ticket_fields(summary, description_text, issuetype, priority_name, epic_key, field_ids):
    fields = {
        "project": {"key": "AICAT"},
        "issuetype": {"name": issuetype},
        "summary": summary,
        "description": JiraClient.text_to_adf(description_text),
        "priority": {"name": priority_name},
    }
    if field_ids.epic_link:
        fields[field_ids.epic_link] = epic_key
    return {"fields": fields}

# Batch conformance findings
if conformance:
    case_list = "\n".join(f"- {f['case_id']} ({f['skill_name']})" for f in conformance)
    issue = jira.create_issue(_ticket_fields(
        summary=f"Fix template conformance — {version}",
        description_text=(
            f"Template conformance sweep for {version}.\n\n"
            f"Affected cases:\n{case_list}\n\n"
            f"Each case output did not match the expected template structure."
        ),
        issuetype="Story",
        priority_name="Medium",
        epic_key=epic_key,
        field_ids=field_ids,
    ))
    for f in conformance:
        created_tickets.append({
            "finding": f,
            "ticket_key": issue["key"],
            "ticket_url": f"{os.environ['JIRA_URL']}/browse/{issue['key']}",
        })

# Individual tickets for all other findings
ISSUETYPE_MAP = {
    "orchestrator-delegation": ("Story", "High"),
    "harness": ("Story", "High"),
    "shared-code": ("Task", "Medium"),
    "quick-fix": ("Task", "Low"),
}
for f in others:
    issuetype, priority_name = ISSUETYPE_MAP.get(f["failure_type"], ("Task", "Medium"))
    issue = jira.create_issue(_ticket_fields(
        summary=f"Fix {f['failure_type']}: {f['skill_name']} — {f['case_id']}",
        description_text=(
            f"**Skill:** {f['skill_name']}\n"
            f"**Case:** {f['case_id']}\n"
            f"**Failure type:** {f['failure_type']}\n"
            f"**Severity:** {f['severity']}\n\n"
            f"{f['summary']}\n\n"
            f"**Test path:** {f['test_path']}"
        ),
        issuetype=issuetype,
        priority_name=priority_name,
        epic_key=epic_key,
        field_ids=field_ids,
    ))
    created_tickets.append({
        "finding": f,
        "ticket_key": issue["key"],
        "ticket_url": f"{os.environ['JIRA_URL']}/browse/{issue['key']}",
    })
```

---

## Step 5 — Back-link GitHub issues with the Jira ticket

For each finding where `gh_issue` is not null, post a comment on the
GitHub issue:

```bash
gh issue comment <gh_issue> \
  --body "Jira: [<ticket_key>](<ticket_url>) (due: <YYYY-MM-DD>)"
```

Use the current date as the due date. Skip silently if `gh_issue` is null
or if `gh` returns a non-zero exit code (log a warning, continue).

---

## Step 6 — Update the Confluence triage page

Append the Confluence update to `_triage_runner.py`, then run it:

```python
page = confluence.get_page(confluence_page_id)
current_version = page.get("version", {}).get("number", 1)

# Build an HTML table for the storage format body
rows = "\n".join(
    f"<tr><td>{html.escape(t['finding']['case_id'])}</td>"
    f"<td>{html.escape(t['finding']['failure_type'])}</td>"
    f"<td><a href='{html.escape(t['ticket_url'])}'>{html.escape(t['ticket_key'])}</a></td></tr>"
    for t in created_tickets
)
new_body = (
    f"<h2>Triage Report — {version}</h2>"
    f"<p>Generated by behavior-test-triage skill.</p>"
    f"<table><tr><th>Case</th><th>Failure Type</th><th>Jira Ticket</th></tr>"
    f"{rows}"
    f"</table>"
)

confluence.update_page(
    page_id=confluence_page_id,
    title=page["title"],
    body_storage=new_body,
    current_version=current_version,
)

print(json.dumps({
    "epic_key": epic_key,
    "tickets_created": len(created_tickets),
    "tickets": [{"key": t["ticket_key"], "url": t["ticket_url"]} for t in created_tickets],
}))
```

Once `_triage_runner.py` is fully written with all substitutions in place,
execute it:

```bash
python3 _triage_runner.py
rm _triage_runner.py
```

Capture the JSON output (epic_key, tickets_created, tickets list) for the
summary in Step 7.

---

## Step 7 — Output summary

Print a structured summary:

```
## Behavior Test Triage Complete

**Version:** {version}
**Epic:** {epic_key} — {JIRA_URL}/browse/{epic_key}
**Tickets created:** {len(created_tickets)}
**GitHub issues back-linked:** {count of linked}
**Confluence page updated:** {CONFLUENCE_URL}/wiki/spaces/.../pages/{confluence_page_id}

### Tickets by failure type
| Failure Type | Count | Severity |
|---|---|---|
| orchestrator-delegation | N | High |
| harness | N | High |
| template-conformance | N (batched) | Medium |
| shared-code | N | Medium |
| quick-fix | N | Low |
```

---

## Error Handling

- **Missing env vars** — list all absent ones, stop before creating any tickets.
- **`bin/bt execute` failure (Step 0 check)** — no cache; stop with instructions.
- **`bin/bt triage` exit 1** — show the error and stop.
- **Jira API error on epic/ticket creation** — report the error and stop creating further tickets; log all ticket keys already created so the user can triage or link them manually.
- **Confluence `update_page` failure** — report the error; tickets already
  created are not rolled back (log their keys so the user can link manually).
- **`gh issue comment` failure** — log a warning per failed back-link,
  continue with the rest.

## Dependencies

- `skills/clients/jira.py` — `JiraClient`, `discover_field_ids`
- `skills/clients/confluence.py` — `ConfluenceClient`
- `tests/behavior/triage.py` — called via `bin/bt triage`
- Environment: `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`,
  `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN`
