# Catalyst Client Utilities

External system connectors for Catalyst DPLC skills.

## Available Clients

### Jira Client
**Location:** `skills/clients/jira.py`  
**Purpose:** Jira Cloud REST API integration  
**Features:**
- JQL search with pagination
- Issue creation/updating
- Epic and story management
- Field ID auto-discovery
- ADF (Atlassian Document Format) support
- Rate-limit handling with exponential backoff

**Example:**
```python
from skills.clients.jira import JiraClient

client = JiraClient(
    base_url="https://your-org.atlassian.net",
    username="you@company.com",
    api_token="your_api_token",
)

# Search issues
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
```

### Confluence Client
**Location:** `skills/clients/confluence.py`  
**Purpose:** Confluence Cloud/Server REST API integration  
**Features:**
- Page fetching with HTML→Markdown conversion
- Recursive tree traversal
- v2→v1 API fallback (Cloud vs. on-premise)
- Child page discovery

**Example:**
```python
from skills.clients.confluence import ConfluenceClient

client = ConfluenceClient(
    base_url="https://your-org.atlassian.net/wiki",
    email="you@company.com",
    token="your_api_token",
)

# Fetch a page
page = client.get_page("123456789")
title = page["title"]
content = page["body"]["storage"]["value"]

# Fetch page tree
pages = client.get_page_tree("123456789", max_depth=3)
```

### Databricks Client
**Location:** `skills/clients/databricks.py`  
**Purpose:** Databricks SQL Warehouse integration  
**Features:**
- SQL execution via Statement Execution API
- Unity Catalog queries
- Lazy SDK initialization
- Warehouse routing

**Example:**
```python
from skills.clients.databricks import DatabricksClient

client = DatabricksClient(
    host="https://your-workspace.cloud.databricks.com",
    token="dapi...",
    warehouse_id="abc123",
)

# Execute SQL
result = client.execute_sql("SELECT * FROM catalog.schema.table LIMIT 10")
columns = result["schema"]["columns"]
data = result["data"]
```

### Marketplace Client
**Location:** `skills/clients/marketplace/`  
**Purpose:** Capital Group marketplace integration  
**Features:**
- Product search
- Metadata retrieval
- Okta SSO authentication
- Token caching

**Example:**
```python
from skills.clients.marketplace import MarketplaceClient

# From cached token (after running `marketplace login`)
client = MarketplaceClient.from_cache()

# Search for products
results = client.search("client positions", limit=10)
for product in results:
    print(f"{product.name} — {product.description}")
```

## Credential Setup

### Interactive Setup (Recommended)

For first-time configuration, use the interactive setup tool:

```bash
python scripts/setup.py jira        # Set up Jira
python scripts/setup.py confluence  # Set up Confluence
python scripts/setup.py github      # Set up GitHub
python scripts/setup.py databricks  # Set up Databricks
```

The tool will:
- Open your browser to token generation pages
- Prompt for credentials with inline instructions
- Create/update your `.env` file automatically

### Manual Setup

Copy `.env.example` to `.env` and fill in credentials:

```bash
cp .env.example .env
# Edit .env with your credentials
```

### Validation

Check if a service is configured:

```python
from scripts.setup import check_integration

ready, missing = check_integration("jira")
if not ready:
    print(f"Missing: {', '.join(missing)}")
```

## Authentication Patterns

All Catalyst clients follow **explicit authentication** — no environment variable magic in `__init__`:

```python
# ✅ Good: Explicit credentials
client = JiraClient(
    base_url=os.getenv("JIRA_URL"),
    username=os.getenv("JIRA_USERNAME"),
    api_token=os.getenv("JIRA_API_TOKEN"),
)

# ❌ Bad: Implicit env var loading in __init__
client = JiraClient()  # Don't do this
```

### Why Explicit Auth?

- **Testability:** Easy to inject mock credentials
- **Transparency:** Clear what credentials are being used
- **Flexibility:** Can use different credentials for different clients
- **Security:** No accidental credential leakage via default behavior

## Error Handling

All clients raise exceptions from the `skills.clients.exceptions` hierarchy:

```python
from skills.clients.exceptions import (
    AuthError,
    RateLimitError,
    NotFoundError,
    CatalystClientError,  # Base class
)

try:
    issues = client.search_issues("project = DATA")
except AuthError:
    print("Check your credentials")
except RateLimitError:
    print("Rate limit exceeded — try again later")
except NotFoundError:
    print("Resource doesn't exist")
except CatalystClientError as e:
    print(f"Client error: {e}")
```

### Exception Hierarchy

```
CatalystClientError (base)
├── AuthError (401/403)
├── RateLimitError (429)
├── NotFoundError (404)
├── ValidationError (400)
├── ConflictError (409)
├── ServerError (5xx)
├── NetworkError (connection failed)
├── RequestTimeoutError (request timeout)
└── SSLError (certificate issues)
```

## Higher-Level Helpers

Higher-level orchestration helpers are in `skills/core/`:

### Jira Helpers

**Location:** `skills/core/jira.py`

```python
from skills.core.jira import (
    check_jira_connectivity,
    create_epic_with_stories,
    fetch_sprint_backlog,
)

# Connectivity check
success, msg = check_jira_connectivity(client)

# Create epic with stories
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
```

## Testing

### Running Tests

```bash
# Unit tests only (fast, no credentials needed)
pytest skills/tests/test_jira_client.py -m unit -v

# Integration tests (requires credentials)
pytest skills/tests/test_jira_client.py -m integration -v

# All tests
pytest skills/tests/test_jira_client.py -v
```

### Test Markers

- `@pytest.mark.unit` — Fast, mocked responses, no network calls
- `@pytest.mark.integration` — Slow, live credentials, real API calls

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
def test_my_feature(client):
    """Unit test with mocked response."""
    with patch.object(client._session, "request") as mock:
        mock.return_value = Mock(status_code=200, json=lambda: {"key": "DATA-123"})
        result = client.some_method()
        assert result["key"] == "DATA-123"

@pytest.mark.integration
def test_live_integration(client):
    """Integration test with live API."""
    result = client.some_method()
    assert "key" in result
```

## Common Patterns

### Rate-Limit Handling

All clients automatically retry on 429 (rate limit) with exponential backoff:

```python
client = JiraClient(
    ...,
    max_retries=5,              # Max retry attempts
    retry_base_delay=1.0,       # Base delay in seconds
    retry_max_delay=30.0,       # Max delay cap
)
```

Honors `Retry-After` header when present.

### Pagination

Use iterator methods for large result sets:

```python
# Jira pagination
for issue in client.iter_search_issues(jql="project = DATA", page_size=100):
    process(issue)

# Confluence tree traversal
pages = client.get_page_tree(root_page_id, max_depth=10)
```

### ADF Text Conversion

Jira Cloud requires Atlassian Document Format for rich-text fields:

```python
description = JiraClient.text_to_adf("""
First paragraph.

Second paragraph.
""")

client.create_issue({
    "fields": {
        ...,
        "description": description,
    }
})
```

## Troubleshooting

### SSL Certificate Errors

On corporate networks with SSL inspection:

```python
# Option 1: Disable SSL verification (not recommended for production)
import urllib3
urllib3.disable_warnings()
# Use requests with verify=False

# Option 2: Install corporate CA certificates
# See: https://pip.pypa.io/en/stable/topics/https-certificates/
```

### Jira Field ID Discovery

Custom fields (Epic Name, Sprint) have different IDs per instance:

```python
from skills.clients.jira import discover_field_ids

fields = client.get_fields()
field_ids = discover_field_ids(fields)

if not field_ids.epic_name:
    raise ValueError("Epic Name field not found")

# Use discovered IDs
payload = {
    "fields": {
        ...,
        field_ids.epic_name: "My Epic",
    }
}
```

### Databricks Warehouse Selection

Specify warehouse at client level or per-query:

```python
# Client-level default
client = DatabricksClient(..., warehouse_id="default-warehouse")
client.execute_sql("SELECT ...")

# Override per-query
client.execute_sql("SELECT ...", warehouse_id="specific-warehouse")
```

## Future Clients (R3+)

Planned for future releases:

- **ServiceNow** — Change management integration (AICAT-52)
- **Teams** — Deployment notifications (AICAT-53)
- **GitHub** — Repository operations (AICAT-35 Phase 3)

## Contributing

When adding new clients:

1. Follow the explicit auth pattern (pass credentials to `__init__`)
2. Use `requests.Session` for HTTP clients
3. Raise exceptions from `skills.clients.exceptions`
4. Add unit tests (mocked) and integration tests (marked)
5. Document in this README
6. Add interactive setup in `skills/clients/setup.py`

See existing clients for reference implementations.
