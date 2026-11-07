# AI Catalyst Feedback

Feedback items collected from skill users. Each item follows the schema below.
Processed by the `process-feedback` skill, which sorts by priority and creates
Jira Stories in project AICAT.

Most feedback now arrives as GitHub issues filed by the `catalyst-feedback`
skill and is pulled in automatically by
`skills/process-feedback/scripts/import_github_feedback.sh` (which carries the
source `github-issue`/`github-url` so the Jira link can be commented back to the
reporter). This file is for **hand-curated** items added directly.

## Schema

```markdown
## Feedback: <short title>
- **skill:** <skill-name or "platform">
- **reported-by:** @<github-handle>
- **context:** <platform-architecture-improvements | existing-skill-improvements | onboarding-installation-improvements | new-skill-requests | feedback-process-improvements>
- **github-issue:** <issue number — optional; set automatically on imported items>
- **github-url:** <issue URL — optional; set automatically on imported items>

<freeform description of the issue or request>
```

The two `github-*` fields are optional for hand-curated items and are populated
automatically for imported ones. When present, `create_jira_stories.sh` comments
the Jira link back on that issue and labels it `promoted`.

## Priority rules (applied by process-feedback skill)

**Baseline by context:**
| context | baseline priority |
|---|---|
| platform-architecture-improvements | HIGH |
| existing-skill-improvements | MED |
| onboarding-installation-improvements | MED |
| new-skill-requests | LOW |
| feedback-process-improvements | LOW |

**Keyword upgrades** (match against title + context field, case-insensitive; keywords only upgrade, never downgrade):
- HIGH: broken, fails, error, crash, blocked, critical, wrong, incorrect, missing, timeout, regression, failing
- MED: slow, confusing, unclear, inconsistent, unexpected, difficult, improve, fix, incomplete, misleading
- LOW: enhancement, suggestion, would be nice, consider, minor, cosmetic, style, future, wish

---

## Feedback: dplc-discovery times out on large catalogs

- **skill:** dplc-discovery
- **reported-by:** @manw
- **context:** existing-skill-improvements

The skill times out when the source catalog has more than ~500 tables. It would help
if it estimated the catalog size first and warned the user before attempting a full
scan. A --limit flag or a "sample mode" would prevent silent failures on large workspaces.

---

## Feedback: install instructions missing Databricks CLI version requirement

- **skill:** platform
- **reported-by:** @manw
- **context:** onboarding-installation-improvements

The install guide does not specify which version of the Databricks CLI is required.
Users on older CLI versions hit auth errors that are hard to diagnose. Should add
a minimum version check to the prereq checklist.

---

## Feedback: add a skill for generating dbt snapshots

- **skill:** write-dbt-model
- **reported-by:** @manw
- **context:** new-skill-requests

It would be nice to have a skill that scaffolds dbt snapshot models (type-2 SCD).
The current write-dbt-model skill only handles incremental and table materializations.
A snapshot variant would cover the slowly-changing-dimension use case cleanly.
