#!/usr/bin/env bash
# import_github_feedback.sh — Front bridge of the AI Catalyst feedback loop.
#
# Pulls the feedback GitHub Issues filed by the `catalyst-feedback` skill and
# converts them into feedback-schema items that `parse_feedback.sh` can
# prioritize and `create_jira_stories.sh` can promote to Jira. This is what
# connects *captured* feedback (GitHub) to the *work* surface (Jira AICAT).
#
# Usage:
#   bash skills/process-feedback/scripts/import_github_feedback.sh [options]
#
# Options:
#   -o <file>        Output file (default: /tmp/catalyst_github_feedback.md)
#   --repo <o/r>     GitHub repo (default: $CATALYST_REPO or cg-open-itg/catalyst)
#   --state <state>  Issue state to pull: open|closed|all (default: open)
#   --include-wins   Also import pure feedback-win issues (default: skip — wins
#                    are a morale signal, not actionable work)
#
# Dedup: issues already carrying the `promoted` label are skipped. That label is
# added by create_jira_stories.sh once an issue becomes a Jira Story, so a
# re-run never double-promotes. Create it once with:
#   gh label create promoted --color 5319e7 \
#     --description "Feedback promoted to a Jira ticket" --repo <repo>
#
# Output: a feedback.md-format document (same schema parse_feedback.sh reads),
# with two extra fields per item — github-issue and github-url — so the
# downstream status-back step can comment on the originating issue.
#
# Requires: gh (authenticated), jq, python3

set -euo pipefail

OUT="/tmp/catalyst_github_feedback.md"
REPO="${CATALYST_REPO:-cg-open-itg/catalyst}"
STATE="open"
INCLUDE_WINS=0

while [ $# -gt 0 ]; do
  case "$1" in
    -o)             OUT="$2"; shift 2 ;;
    --repo)         REPO="$2"; shift 2 ;;
    --state)        STATE="$2"; shift 2 ;;
    --include-wins) INCLUDE_WINS=1; shift ;;
    -h|--help)      sed -n '2,30p' "$0"; exit 0 ;;
    *)              echo "Error: unknown argument '$1' (try --help)"; exit 2 ;;
  esac
done

# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
for cmd in gh jq python3; do
  command -v "$cmd" &>/dev/null || { echo "Error: $cmd is required."; exit 1; }
done

if ! gh auth status &>/dev/null; then
  echo "Error: gh is not authenticated. Run: gh auth login"
  exit 1
fi

# ---------------------------------------------------------------------------
# Fetch feedback issues
# ---------------------------------------------------------------------------
echo "Fetching feedback issues from $REPO (state=$STATE)..." >&2

# Paginate fully via the REST API so we never silently cap the import the way
# `gh issue list --limit` would. The issues endpoint also returns PRs, so we
# filter those out (.pull_request) and normalize to the fields the mapper
# expects. With --paginate + a streaming --jq, each issue prints as one compact
# JSON line, which the mapper reads as JSONL.
tmp_in=$(mktemp)
trap 'rm -f "$tmp_in"' EXIT
gh api --paginate \
  "repos/$REPO/issues?state=$STATE&labels=feedback&per_page=100" \
  --jq '.[] | select(.pull_request | not) | {number, title, body, url: .html_url, author: {login: .user.login}, labels: [.labels[] | {name: .name}]}' \
  > "$tmp_in"

# ---------------------------------------------------------------------------
# Map issues → feedback-schema items (Python for reliable body parsing)
# ---------------------------------------------------------------------------
INCLUDE_WINS="$INCLUDE_WINS" python3 - "$tmp_in" "$OUT" <<'PYEOF'
import json, os, re, sys

in_path, out_path = sys.argv[1], sys.argv[2]
include_wins = os.environ.get("INCLUDE_WINS", "0") == "1"

# gh api --paginate --jq streams one compact JSON object per line (JSONL).
issues = []
with open(in_path) as f:
    for line in f:
        line = line.strip()
        if line:
            issues.append(json.loads(line))
print(f"Fetched {len(issues)} feedback issue(s) (paginated, no cap).", file=sys.stderr)

def clean_title(title):
    t = re.sub(r'^\[feedback\]\s*', '', title or "").strip()
    return t or "(untitled feedback)"

def extract_skill(body, raw_title):
    m = re.search(r'##\s*Feedback for\s*`([^`]+)`', body or "")
    if m:
        return m.group(1).strip()
    # Fallback: "[feedback] <skill> — <words>" (em dash or hyphen separator)
    m = re.match(r'\[feedback\]\s*(.+?)\s*[—-]\s', raw_title or "")
    if m:
        return m.group(1).strip()
    return "platform"

def section(body, header):
    """Text under '### <header>' up to the next '### ', a '---' rule, or EOF."""
    pat = re.compile(r'###\s*' + re.escape(header) + r'\s*\n(.*?)(?=\n###\s|\n---|\Z)', re.S)
    m = pat.search(body or "")
    return m.group(1).strip() if m else ""

def collapse(s):
    return " ".join((s or "").split())

blocks = []
n_import = n_promoted = n_wins = 0

for it in issues:
    labels = {l.get("name", "") for l in it.get("labels", [])}
    if "promoted" in labels:
        n_promoted += 1
        continue

    is_gap   = "feedback-gap" in labels
    is_mixed = "feedback-mixed" in labels
    is_win   = "feedback-win" in labels
    if is_win and not (is_gap or is_mixed) and not include_wins:
        n_wins += 1
        continue

    body   = it.get("body", "") or ""
    title  = clean_title(it.get("title", ""))
    skill  = extract_skill(body, it.get("title", ""))
    author = (it.get("author") or {}).get("login", "unknown")
    num    = it.get("number")
    url    = it.get("url", "")

    didnt  = section(body, "What didn't / could be better")
    worked = section(body, "What worked")
    em = re.search(r'\*\*Errors surfaced:\*\*\s*(.+)', body)
    errors = em.group(1).strip() if em else ""

    desc = didnt or errors
    if not desc:
        # Last resort: whole body minus the auto-filed footer
        desc = re.sub(r'\n---\s*\n\s*\*Auto-filed.*', '', body, flags=re.S)
    if worked and is_mixed:
        desc = f"{collapse(desc)}  (Reporter also noted what worked: {collapse(worked)})"
    desc = collapse(desc)

    # Default category. Keyword upgrades in parse_feedback.sh + the human review
    # gate refine the tier; we don't try to auto-classify GitHub feedback into
    # the five context buckets here.
    context = "existing-skill-improvements"

    blocks.append(
        f"## Feedback: {title}\n"
        f"- **skill:** {skill}\n"
        f"- **reported-by:** @{author}\n"
        f"- **context:** {context}\n"
        f"- **github-issue:** {num}\n"
        f"- **github-url:** {url}\n\n"
        f"{desc}\n"
    )
    n_import += 1

header = (
    "# AI Catalyst Feedback — imported from GitHub Issues\n\n"
    "Generated by import_github_feedback.sh. Do not hand-edit — re-run to refresh.\n"
    "Each item carries its source github-issue so create_jira_stories.sh can\n"
    "comment the Jira link back on the originating issue.\n"
)

with open(out_path, "w") as f:
    f.write(header + "\n---\n\n" + "\n---\n\n".join(blocks))
    if blocks:
        f.write("\n")

print(f"Imported {n_import} feedback issue(s) -> {out_path}", file=sys.stderr)
print(f"Skipped: {n_promoted} already-promoted, {n_wins} pure-win.", file=sys.stderr)
for b in blocks:
    first = b.splitlines()[0].replace("## Feedback:", "").strip()
    gh = re.search(r'github-issue:\*\*\s*(\d+)', b)
    print(f"  - #{gh.group(1) if gh else '?'}  {first}", file=sys.stderr)
PYEOF

echo "" >&2
echo "Next: bash skills/process-feedback/scripts/parse_feedback.sh $OUT" >&2
