#!/usr/bin/env bash
# fetch_tickets.sh — Fetch Jira Story details for given ticket IDs, or link a PR to a ticket.
#
# Usage:
#   bash skills/implement-feedback/scripts/fetch_tickets.sh AICAT-123 [AICAT-124 ...]
#   bash skills/implement-feedback/scripts/fetch_tickets.sh link AICAT-123 "<pr-url>" "<pr-title>"
#
# Fetch mode:
#   Downloads each ticket as /tmp/catalyst_ticket_<ID>.json
#   Prints a human-readable summary of each Story.
#
# Link mode:
#   Attaches a remote link (PR URL) to the given Jira ticket.
#
# Requires: jq, curl
# Env vars (from repo root .env): JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
ENV_FILE="$REPO_ROOT/.env"

# ---------------------------------------------------------------------------
# Load .env
# ---------------------------------------------------------------------------
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
missing_vars=()
[ -z "${JIRA_URL:-}"       ] && missing_vars+=("JIRA_URL")
[ -z "${JIRA_USERNAME:-}"  ] && missing_vars+=("JIRA_USERNAME")
[ -z "${JIRA_API_TOKEN:-}" ] && missing_vars+=("JIRA_API_TOKEN")

if [ ${#missing_vars[@]} -gt 0 ]; then
  echo "Error: Missing required env vars: ${missing_vars[*]}"
  echo "Add them to $ENV_FILE"
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: jq is required. Install with: brew install jq"
  exit 1
fi

# Strip trailing slash from JIRA_URL if present
JIRA_URL="${JIRA_URL%/}"

if [ $# -eq 0 ]; then
  echo "Usage:"
  echo "  fetch mode: $0 AICAT-123 [AICAT-124 ...]"
  echo "  link mode:  $0 link AICAT-123 <pr-url> <pr-title>"
  exit 1
fi

# ---------------------------------------------------------------------------
# Link mode
# ---------------------------------------------------------------------------
if [ "$1" = "link" ]; then
  issue_key="${2:-}"
  pr_url="${3:-}"
  pr_title="${4:-Pull Request}"

  if [ -z "$issue_key" ] || [ -z "$pr_url" ]; then
    echo "Error: link mode requires: link <issue-key> <pr-url> [pr-title]"
    exit 1
  fi

  echo "Linking PR to $issue_key..."
  payload=$(jq -n \
    --arg url   "$pr_url" \
    --arg title "$pr_title" \
    '{
      object: {
        url:   $url,
        title: $title
      }
    }')

  response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -u "$JIRA_USERNAME:$JIRA_API_TOKEN" \
    -d "$payload" \
    "$JIRA_URL/rest/api/3/issue/$issue_key/remotelink")

  http_code=$(printf '%s' "$response" | tail -1)
  if ! [[ "$http_code" =~ ^[0-9]+$ ]]; then
    echo "Failed to link PR (no HTTP code from curl — network/proxy?)"
    exit 1
  fi
  if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
    echo "Linked: $pr_url → $issue_key"
  else
    body=$(printf '%s' "$response" | sed '$d')
    echo "Failed to link PR (HTTP $http_code): $body"
    exit 1
  fi
  exit 0
fi

# ---------------------------------------------------------------------------
# Fetch mode — process each ticket ID
# ---------------------------------------------------------------------------
echo ""
failed=()

for issue_key in "$@"; do
  output_file="/tmp/catalyst_ticket_${issue_key}.json"
  echo "Fetching $issue_key..."

  response=$(curl -s -w "\n%{http_code}" -X GET \
    -H "Content-Type: application/json" \
    -u "$JIRA_USERNAME:$JIRA_API_TOKEN" \
    "$JIRA_URL/rest/api/3/issue/$issue_key?fields=summary,description,priority,labels,status,assignee,comment")

  http_code=$(printf '%s' "$response" | tail -1)
  body=$(printf '%s' "$response" | sed '$d')

  if ! [[ "$http_code" =~ ^[0-9]+$ ]]; then
    echo "  ERROR (no HTTP code from curl — network/proxy?)"
    failed+=("$issue_key")
    continue
  fi
  if [ "$http_code" -ne 200 ]; then
    error=$(echo "$body" | jq -r '.errorMessages[0] // .message // "unknown error"' 2>/dev/null || echo "$body")
    echo "  ERROR ($http_code): $error"
    failed+=("$issue_key")
    continue
  fi

  # Extract and flatten the description text from ADF format
  summary=$(echo "$body"  | jq -r '.fields.summary')
  priority=$(echo "$body" | jq -r '.fields.priority.name // "Unknown"')
  status=$(echo "$body"   | jq -r '.fields.status.name // "Unknown"')
  assignee=$(echo "$body" | jq -r '.fields.assignee.displayName // "Unassigned"')
  labels=$(echo "$body"   | jq -r '[.fields.labels[]] | join(", ")')

  # Flatten ADF description to plain text
  description_text=$(echo "$body" | jq -r '
    .fields.description.content[]?.content[]?.text // empty
  ' 2>/dev/null | tr '\n' ' ' | sed 's/  */ /g' | sed 's/^ *//;s/ *$//')

  # Build clean JSON for the implementing agent
  clean_json=$(jq -n \
    --arg key         "$issue_key" \
    --arg summary     "$summary" \
    --arg priority    "$priority" \
    --arg status      "$status" \
    --arg assignee    "$assignee" \
    --arg labels      "$labels" \
    --arg description "$description_text" \
    --arg url         "$JIRA_URL/browse/$issue_key" \
    '{
      key:         $key,
      summary:     $summary,
      priority:    $priority,
      status:      $status,
      assignee:    $assignee,
      labels:      $labels,
      description: $description,
      url:         $url
    }')

  echo "$clean_json" > "$output_file"

  # Human-readable summary
  echo "  Summary:  $summary"
  echo "  Priority: $priority  |  Status: $status  |  Assignee: $assignee"
  echo "  Labels:   $labels"
  echo "  Desc:     $(echo "$description_text" | cut -c1-140)"
  echo "  JSON:     $output_file"
  echo "  URL:      $JIRA_URL/browse/$issue_key"
  echo ""
done

if [ ${#failed[@]} -gt 0 ]; then
  echo "Failed to fetch: ${failed[*]}"
  exit 1
fi
