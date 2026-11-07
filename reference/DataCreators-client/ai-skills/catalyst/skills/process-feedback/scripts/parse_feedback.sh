#!/usr/bin/env bash
# parse_feedback.sh — Parse docs/feedback/feedback.md and sort items by priority.
#
# Usage:
#   bash skills/process-feedback/scripts/parse_feedback.sh [path-to-feedback.md]
#
# Output:
#   - Prints a human-readable sorted summary to stdout
#   - Writes sorted JSON array to /tmp/catalyst_feedback_sorted.json
#
# Requires: python3, jq

set -euo pipefail

FEEDBACK_FILE="${1:-docs/feedback/feedback.md}"
OUTPUT_FILE="/tmp/catalyst_feedback_sorted.json"

# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required. Install with: brew install jq"
  exit 1
fi

if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is required."
  exit 1
fi

if [ ! -f "$FEEDBACK_FILE" ]; then
  echo "Error: Feedback file not found at '$FEEDBACK_FILE'"
  echo "Expected: docs/feedback/feedback.md (run from repo root)"
  exit 1
fi

# ---------------------------------------------------------------------------
# Parse + sort via Python (reliable multi-line block handling)
# ---------------------------------------------------------------------------
ITEMS_JSON=$(python3 - "$FEEDBACK_FILE" <<'PYEOF'
import sys, json, re

filepath = sys.argv[1]
with open(filepath) as f:
    content = f.read()

# Priority config
BASELINE = {
    "platform-architecture-improvements":   3,
    "existing-skill-improvements":          2,
    "onboarding-installation-improvements": 2,
    "new-skill-requests":                   1,
    "feedback-process-improvements":        1,
}
HIGH_KW = {"broken","fails","error","crash","blocked","critical","wrong",
           "incorrect","missing","timeout","regression","failing"}
MED_KW  = {"slow","confusing","unclear","inconsistent","unexpected","difficult",
           "improve","fix","incomplete","misleading"}

def priority_from_keywords(text, base):
    words = set(re.findall(r'\w+', text.lower()))
    if words & HIGH_KW:
        return max(base, 3)
    if words & MED_KW:
        return max(base, 2)
    return base

def priority_label(p):
    return {3: "HIGH", 2: "MED", 1: "LOW"}.get(p, "LOW")

def jira_priority(p):
    return {3: "High", 2: "Medium", 1: "Low"}.get(p, "Low")

# Split on "## Feedback:" boundaries
blocks = re.split(r'\n(?=## Feedback:)', content)
items = []

for block in blocks:
    if not block.strip().startswith("## Feedback:"):
        continue

    lines = block.strip().split('\n')
    title = lines[0].replace("## Feedback:", "").strip()

    # Skip schema/template items (contain placeholder angle brackets)
    if "<" in title and ">" in title:
        continue

    skill        = ""
    reported_by  = ""
    context      = ""
    github_issue = ""   # source GitHub issue number (set by import_github_feedback.sh)
    github_url   = ""
    desc_lines   = []
    past_meta    = False

    for line in lines[1:]:
        m_skill = re.match(r'-\s+\*\*skill:\*\*\s*(.*)', line)
        m_by    = re.match(r'-\s+\*\*reported-by:\*\*\s*(.*)', line)
        m_ctx   = re.match(r'-\s+\*\*context:\*\*\s*(.*)', line)
        m_ghi   = re.match(r'-\s+\*\*github-issue:\*\*\s*(.*)', line)
        m_ghu   = re.match(r'-\s+\*\*github-url:\*\*\s*(.*)', line)
        if m_skill:  skill        = m_skill.group(1).strip();  continue
        if m_by:     reported_by  = m_by.group(1).strip();     continue
        if m_ctx:    context      = m_ctx.group(1).strip();    continue
        if m_ghi:    github_issue = m_ghi.group(1).strip();    continue
        if m_ghu:    github_url   = m_ghu.group(1).strip();    continue
        # Blank line after bullet list → description starts
        if not past_meta and line.strip() == "":
            past_meta = True
            continue
        # A horizontal rule ends this item's description (entry separator) —
        # without this, the trailing "---" leaks into the description text.
        if past_meta and line.strip() == "---":
            break
        if past_meta:
            desc_lines.append(line)

    description = " ".join(" ".join(desc_lines).split())

    base  = BASELINE.get(context, 1)
    final = priority_from_keywords(title + " " + context, base)

    items.append({
        "title":          title,
        "skill":          skill,
        "reported_by":    reported_by,
        "context":        context,
        "description":    description,
        "github_issue":   github_issue,
        "github_url":     github_url,
        "priority":       final,
        "priority_label": priority_label(final),
        "jira_priority":  jira_priority(final),
    })

# Sort HIGH → MED → LOW
items.sort(key=lambda x: x["priority"], reverse=True)
print(json.dumps(items, indent=2))
PYEOF
)

# ---------------------------------------------------------------------------
# Write output JSON
# ---------------------------------------------------------------------------
echo "$ITEMS_JSON" > "$OUTPUT_FILE"

total=$(echo "$ITEMS_JSON" | jq 'length')
echo ""
echo "Parsed $total feedback items from $FEEDBACK_FILE"
echo ""

# ---------------------------------------------------------------------------
# Print human-readable summary grouped by tier
# ---------------------------------------------------------------------------
global_idx=0
for tier in 3 2 1; do
  if   [ "$tier" -eq 3 ]; then label="HIGH"
  elif [ "$tier" -eq 2 ]; then label="MED"
  else                          label="LOW"
  fi

  count=$(echo "$ITEMS_JSON" | jq "[.[] | select(.priority == $tier)] | length")
  [ "$count" -eq 0 ] && continue

  echo "=== $label PRIORITY ($count items) ==="
  while IFS= read -r item; do
    global_idx=$((global_idx + 1))
    t=$(echo "$item"   | jq -r '.title')
    s=$(echo "$item"   | jq -r '.skill')
    by=$(echo "$item"  | jq -r '.reported_by')
    ctx=$(echo "$item" | jq -r '.context')
    gh=$(echo "$item"  | jq -r '.github_issue // ""')
    d=$(echo "$item"   | jq -r '.description' | cut -c1-120)
    echo "$global_idx. [$ctx] $t"
    echo "   skill: $s   reported-by: $by"
    if [ -n "$gh" ] && [ "$gh" != "null" ]; then echo "   github: #$gh"; fi
    echo "   $d"
    echo ""
  done < <(echo "$ITEMS_JSON" | jq -c ".[] | select(.priority == $tier)")
done

echo "Sorted JSON written to: $OUTPUT_FILE"
echo ""
