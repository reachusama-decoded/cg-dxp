#!/usr/bin/env bash
# create_jira_stories.sh — Create Jira Stories from parsed feedback JSON, and
# close the loop back to the reporter.
#
# For each selected item this:
#   1. Creates a Jira Story in project AICAT (label Customer-satisfaction).
#   2. If the item came from a GitHub feedback issue (github_issue, set by
#      import_github_feedback.sh) it runs the "status-back" bridge:
#        a. comments the Jira link on that issue so the reporter knows which
#           ticket to watch,
#        b. adds the `promoted` label (so import_github_feedback.sh dedups it),
#        c. adds a Jira->GitHub remote link for traceability.
#
# Usage:
#   bash skills/process-feedback/scripts/create_jira_stories.sh [--dry-run] [<json-file>] [indices...]
#
#   --dry-run     Print what would happen; make no Jira or GitHub changes.
#   <json-file>   Sorted JSON from parse_feedback.sh (default: /tmp/catalyst_feedback_sorted.json)
#   [indices...]  Optional 1-based item indices to create. Omit to create all.
#
# Requires: jq, curl, and (for the status-back step) an authenticated gh.
# Env (from repo root .env): JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN
# Optional env: CATALYST_REPO (default cg-open-itg/catalyst)
#
# One-time setup for the status-back label:
#   gh label create promoted --color 5319e7 \
#     --description "Feedback promoted to a Jira ticket" --repo cg-open-itg/catalyst

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ".")"
ENV_FILE="$REPO_ROOT/.env"

# ---------------------------------------------------------------------------
# Args
# ---------------------------------------------------------------------------
DRY_RUN=0
positional=()
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    -h|--help) sed -n '2,28p' "$0"; exit 0 ;;
    *)         positional+=("$arg") ;;
  esac
done
if [ ${#positional[@]} -gt 0 ]; then set -- "${positional[@]}"; else set --; fi

JSON_FILE="${1:-/tmp/catalyst_feedback_sorted.json}"
shift || true   # remaining args are optional 1-based indices

GH_REPO="${CATALYST_REPO:-cg-open-itg/catalyst}"
JIRA_PROJECT_ID="12843"
JIRA_LABEL="Customer-satisfaction"
JIRA_ISSUE_TYPE="Story"
JIRA_BOARD_URL="https://capitalgroup.atlassian.net/jira/software/c/projects/AICAT/boards/14045"

# ---------------------------------------------------------------------------
# Load .env BEFORE any Jira call (the prototype sourced it too late, which left
# JIRA_URL/creds unset for the assignee lookup and created unassigned stories).
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
command -v jq   &>/dev/null || { echo "Error: jq is required. Install with: brew install jq"; exit 1; }
command -v curl &>/dev/null || { echo "Error: curl is required."; exit 1; }

JIRA_URL="${JIRA_URL:-https://capitalgroup.atlassian.net}"
JIRA_URL="${JIRA_URL%/}"   # strip trailing slash

# Live runs require credentials; --dry-run makes no calls, so it can preview
# without them.
if [ "$DRY_RUN" -eq 0 ]; then
  missing_vars=()
  [ -z "${JIRA_USERNAME:-}"  ] && missing_vars+=("JIRA_USERNAME")
  [ -z "${JIRA_API_TOKEN:-}" ] && missing_vars+=("JIRA_API_TOKEN")
  if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "Error: Missing required env vars in .env: ${missing_vars[*]}"
    echo "Add them to $ENV_FILE"
    exit 1
  fi
fi

if [ ! -f "$JSON_FILE" ]; then
  echo "Error: JSON file not found at '$JSON_FILE'"
  echo "Run parse_feedback.sh (or import_github_feedback.sh) first."
  exit 1
fi

# gh is only needed for the status-back step (items with a github_issue).
HAVE_GH=0
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  HAVE_GH=1
fi

# ---------------------------------------------------------------------------
# Resolve assignee account ID (skip in dry-run)
# ---------------------------------------------------------------------------
JIRA_DEFAULT_ASSIGNEE=""
if [ "$DRY_RUN" -eq 0 ]; then
  JIRA_DEFAULT_ASSIGNEE=$(curl -s -X GET \
    -H "Content-Type: application/json" \
    -u "$JIRA_USERNAME:$JIRA_API_TOKEN" \
    "$JIRA_URL/rest/api/3/myself" | jq -r '.accountId // empty')
  if [ -z "$JIRA_DEFAULT_ASSIGNEE" ]; then
    echo "Warning: Could not resolve account ID for ${JIRA_USERNAME:-?} — stories will be unassigned."
  fi
fi

# ---------------------------------------------------------------------------
# Resolve which indices to create
# ---------------------------------------------------------------------------
total=$(jq 'length' "$JSON_FILE")
if [ "$total" -eq 0 ]; then
  echo "No feedback items found in $JSON_FILE. Nothing to create."
  exit 0
fi

declare -a indices_to_create
if [ $# -gt 0 ]; then
  for i in "$@"; do
    idx=$((i - 1))   # 1-based -> 0-based
    if [ "$idx" -lt 0 ] || [ "$idx" -ge "$total" ]; then
      echo "Warning: index $i is out of range (1-$total), skipping."
      continue
    fi
    indices_to_create+=("$idx")
  done
else
  for ((i=0; i<total; i++)); do indices_to_create+=("$i"); done
fi

if [ ${#indices_to_create[@]} -eq 0 ]; then
  echo "No valid indices to create. Exiting."
  exit 0
fi

echo ""
if [ "$DRY_RUN" -eq 1 ]; then
  echo "[DRY-RUN] Would create ${#indices_to_create[@]} Jira Stories in project AICAT (no changes made)."
else
  echo "Creating ${#indices_to_create[@]} Jira Stories in project AICAT..."
fi
echo ""

# ---------------------------------------------------------------------------
# Idempotency guard. Prints the AICAT key of a Story already promoted from this
# GitHub issue (matched by its gh-<n> label), or nothing if none exists.
#
# Returns 0 ONLY when the search itself succeeded (HTTP 200). On any other
# outcome (401/403/5xx/proxy blip/empty body) it returns non-zero so the caller
# fails closed — skipping the item rather than falling through to create. Failing
# open here would re-open the duplicate-Story bug the gh-<n> label prevents,
# because an empty result would be indistinguishable from "no existing Story".
#
# Assumes the gh-<n> label is already indexed — always true for the weekly-sweep
# workflow. A *rapid* re-run inside Jira's label-index window could still
# double-create; acceptable for this use case.
# ---------------------------------------------------------------------------
jira_key_for_gh_issue() {
  local n="$1" jql enc resp code body
  jql="project = AICAT AND labels = \"gh-$n\""
  enc=$(jq -rn --arg q "$jql" '$q|@uri')
  resp=$(curl -s -w "\n%{http_code}" -u "$JIRA_USERNAME:$JIRA_API_TOKEN" \
    "$JIRA_URL/rest/api/3/search/jql?jql=$enc&fields=key&maxResults=1" || true)
  code=$(printf '%s' "$resp" | tail -1)
  body=$(printf '%s' "$resp" | sed '$d')
  [ "$code" = "200" ] || return 1
  # A 200 whose body isn't a well-formed search response (e.g. an SSO/proxy
  # interstitial, which can also come back 200) must fail closed too — require an
  # issues array before trusting the result.
  printf '%s' "$body" | jq -e 'has("issues") and (.issues | type == "array")' >/dev/null 2>&1 || return 1
  printf '%s' "$body" | jq -r '.issues[0].key // empty' 2>/dev/null || return 1
}

# ---------------------------------------------------------------------------
# Status-back: tell the reporter which Jira ticket their feedback became, mark
# the issue promoted (dedup), and add a Jira->GitHub remote link.
# Args: <github-issue#> <jira-key> <github-url>
# ---------------------------------------------------------------------------
status_back() {
  local gh_issue="$1" key="$2" gh_url="$3"
  local jira_browse="$JIRA_URL/browse/$key"
  local comment
  comment="Thanks for the feedback — it's now tracked in Jira as **$key** and will be prioritized there. Follow that ticket for status: $jira_browse

_Linked automatically by the process-feedback skill._"

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "      [DRY-RUN] would comment Jira link on $GH_REPO#$gh_issue"
    echo "      [DRY-RUN] would add label 'promoted' to $GH_REPO#$gh_issue"
    echo "      [DRY-RUN] would add Jira remote link $key -> #$gh_issue"
    return 0
  fi

  if [ "$HAVE_GH" -ne 1 ]; then
    echo "      ! gh not authenticated — skipped status-back for #$gh_issue (Story $key still created)."
    return 0
  fi

  # Capture gh stderr and surface it — the failure reason (e.g. "label
  # 'promoted' not found") is what tells the operator how to fix it.
  if err=$(gh issue comment "$gh_issue" --repo "$GH_REPO" --body "$comment" 2>&1 >/dev/null); then
    echo "      -> commented Jira link on $GH_REPO#$gh_issue"
  else
    echo "      ! failed to comment on #$gh_issue: $err"
  fi

  if err=$(gh issue edit "$gh_issue" --repo "$GH_REPO" --add-label promoted 2>&1 >/dev/null); then
    echo "      -> labeled #$gh_issue 'promoted'"
  else
    echo "      ! could not add 'promoted' label: $err (create it once: gh label create promoted --repo $GH_REPO)"
  fi

  if [ -n "$gh_url" ]; then
    # curl -o /dev/null exits 0 on HTTP errors too, so gate on the status code
    # rather than curl's exit — otherwise a 401/403/400 reports false success.
    rl_code=$(curl -s -o /dev/null -w '%{http_code}' -X POST \
      -H "Content-Type: application/json" \
      -u "$JIRA_USERNAME:$JIRA_API_TOKEN" \
      -d "$(jq -n --arg url "$gh_url" --arg title "GitHub feedback #$gh_issue" \
            '{object: {url: $url, title: $title}}')" \
      "$JIRA_URL/rest/api/3/issue/$key/remotelink" || true)
    if [ "$rl_code" = "200" ] || [ "$rl_code" = "201" ]; then
      echo "      -> added Jira remote link on $key"
    else
      echo "      ! Jira remote link failed (HTTP ${rl_code:-none}) on $key"
    fi
  fi
}

# ---------------------------------------------------------------------------
# Create each Story
# ---------------------------------------------------------------------------
created=()
failed=()
skipped=()

for idx in "${indices_to_create[@]}"; do
  item=$(jq -c ".[$idx]" "$JSON_FILE")

  title=$(echo "$item"          | jq -r '.title')
  skill=$(echo "$item"          | jq -r '.skill')
  reported_by=$(echo "$item"    | jq -r '.reported_by')
  context=$(echo "$item"        | jq -r '.context')
  description=$(echo "$item"    | jq -r '.description')
  jira_priority=$(echo "$item"  | jq -r '.jira_priority')
  priority_label=$(echo "$item" | jq -r '.priority_label')
  github_issue=$(echo "$item"   | jq -r '.github_issue // ""')
  github_url=$(echo "$item"     | jq -r '.github_url // ""')

  # Jira rejects empty ADF text nodes and requires a summary — fall back to
  # placeholders so an item with a sparse body still files cleanly.
  title="${title:-untitled feedback}"
  skill="${skill:-unspecified}"
  reported_by="${reported_by:-unknown}"
  context="${context:-uncategorized}"
  [ -z "$description" ] && description="(no description provided)"

  # gh-<n> label is both a cross-ref on the Story and the idempotency key.
  gh_label=""; [ -n "$github_issue" ] && gh_label="gh-$github_issue"

  # Build Atlassian Document Format (ADF) description; include the source link
  # when the item came from a GitHub feedback issue.
  description_adf=$(jq -n \
    --arg skill       "$skill" \
    --arg reported_by "$reported_by" \
    --arg context     "$context" \
    --arg description "$description" \
    --arg gh_url      "$github_url" \
    '{
      type: "doc",
      version: 1,
      content: (
        [
          { type: "paragraph", content: [ { type: "text", text: "Skill: ",       marks: [{ type: "strong" }] }, { type: "text", text: $skill } ] },
          { type: "paragraph", content: [ { type: "text", text: "Reported by: ", marks: [{ type: "strong" }] }, { type: "text", text: $reported_by } ] },
          { type: "paragraph", content: [ { type: "text", text: "Category: ",    marks: [{ type: "strong" }] }, { type: "text", text: $context } ] }
        ]
        + (if $gh_url != "" then
            [ { type: "paragraph", content: [ { type: "text", text: "Source: ", marks: [{ type: "strong" }] }, { type: "text", text: $gh_url, marks: [{ type: "link", attrs: { href: $gh_url } }] } ] } ]
           else [] end)
        + [
          { type: "rule" },
          { type: "paragraph", content: [ { type: "text", text: $description } ] },
          { type: "rule" },
          { type: "paragraph", content: [ { type: "text", text: "Auto-created by the process-feedback skill from captured user feedback.", marks: [{ type: "em" }] } ] }
        ]
      )
    }')

  payload=$(jq -n \
    --arg summary     "$title" \
    --arg project_id  "$JIRA_PROJECT_ID" \
    --arg issue_type  "$JIRA_ISSUE_TYPE" \
    --arg priority    "$jira_priority" \
    --arg label       "$JIRA_LABEL" \
    --arg gh_label    "$gh_label" \
    --arg assignee_id "$JIRA_DEFAULT_ASSIGNEE" \
    --argjson desc_adf "$description_adf" \
    '{
      fields: {
        project:     { id: $project_id },
        summary:     $summary,
        issuetype:   { name: $issue_type },
        priority:    { name: $priority },
        labels:      ([$label] + (if $gh_label != "" then [$gh_label] else [] end)),
        description: $desc_adf
      }
    } | if $assignee_id != "" then .fields.assignee = { accountId: $assignee_id } else . end')

  if [ "$DRY_RUN" -eq 1 ]; then
    src=""; [ -n "$github_issue" ] && src=" (from #$github_issue)"
    echo "  [DRY-RUN] [$priority_label] $title$src"
    echo "            type=$JIRA_ISSUE_TYPE  priority=$jira_priority  label=$JIRA_LABEL  project=$JIRA_PROJECT_ID"
    if [ -n "$github_issue" ]; then
      echo "            (live run checks Jira for an existing gh-$github_issue Story first and skips if already promoted)"
      status_back "$github_issue" "AICAT-XXX" "$github_url"
    fi
    continue
  fi

  # Idempotency: if a Story already exists for this GH issue, skip creating a
  # second one. If the dedup search itself FAILS, skip too (fail closed) — we
  # can't prove there's no existing Story, so creating one risks a duplicate.
  if [ -n "$github_issue" ]; then
    if existing=$(jira_key_for_gh_issue "$github_issue"); then
      if [ -n "$existing" ]; then
        echo "  [$priority_label] $title ... already promoted as $existing (skipped)"
        [ "$HAVE_GH" -eq 1 ] && gh issue edit "$github_issue" --repo "$GH_REPO" --add-label promoted >/dev/null 2>&1 || true
        skipped+=("$existing|$priority_label|$title")
        continue
      fi
      # search succeeded, no existing Story -> fall through and create
    else
      echo "  [$priority_label] $title ... FAILED (Jira dedup search errored — skipped to avoid a possible duplicate)"
      failed+=("$title (dedup search failed)")
      continue
    fi
  fi

  echo -n "  [$priority_label] $title ... "

  response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -u "$JIRA_USERNAME:$JIRA_API_TOKEN" \
    -d "$payload" \
    "$JIRA_URL/rest/api/3/issue" || true)

  http_code=$(printf '%s' "$response" | tail -1)
  body=$(printf '%s' "$response" | sed '$d')

  # A network/proxy/DNS failure yields empty output; guard the numeric test so
  # set -e + [ "" -eq 201 ] can't abort the whole batch mid-flight.
  if ! [[ "$http_code" =~ ^[0-9]+$ ]]; then
    echo "FAILED (no HTTP code from curl — network/proxy?)"
    failed+=("$title")
    continue
  fi

  if [ "$http_code" -eq 201 ]; then
    key=$(echo "$body" | jq -r '.key')
    echo "created $key"
    created+=("$key|$priority_label|$title")
    [ -n "$github_issue" ] && status_back "$github_issue" "$key" "$github_url"
  else
    error=$(echo "$body" | jq -r '.errors // .errorMessages // . | tostring' 2>/dev/null || echo "$body")
    echo "FAILED (HTTP $http_code)"
    echo "    Error: $error"
    failed+=("$title")
  fi
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "========================================"
if [ "$DRY_RUN" -eq 1 ]; then
  echo "[DRY-RUN] No Jira Stories or GitHub changes were made."
  echo ""
  echo "Board: $JIRA_BOARD_URL"
  echo ""
  exit 0
fi

if [ ${#created[@]} -gt 0 ]; then
  echo "Created ${#created[@]} Stories:"
  for entry in "${created[@]}"; do
    IFS='|' read -r key plabel ptitle <<< "$entry"
    echo "  $key  [$plabel] $ptitle"
    echo "         $JIRA_URL/browse/$key"
  done
fi

if [ ${#skipped[@]} -gt 0 ]; then
  echo ""
  echo "Skipped — already promoted (${#skipped[@]}):"
  for entry in "${skipped[@]}"; do
    IFS='|' read -r ekey eplabel etitle <<< "$entry"
    echo "  $ekey  [$eplabel] $etitle"
  done
fi

if [ ${#failed[@]} -gt 0 ]; then
  echo ""
  echo "Failed (${#failed[@]}):"
  for t in "${failed[@]}"; do
    echo "  - $t"
  done
fi

echo ""
echo "Board: $JIRA_BOARD_URL"
echo ""
