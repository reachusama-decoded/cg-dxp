## Summary

<!-- One sentence. What does this PR do? -->

**Jira:** [AICAT-NNN](https://capitalgroup.atlassian.net/browse/AICAT-NNN) | **GitHub issue:** #N

## Problem

<!-- What's broken or missing? For fix/bug tickets: paste the verbatim failure output. -->

## Fix

<!-- What changed and why. Be specific — reference the file and the line-level decision. -->

## Testing

<!-- Paste the required offline suite result. No CI runs it for you — this
     paste is the evidence. Behavior-test output is optional (see
     CONTRIBUTING.md); project admins run the behavior suite before merge. -->

```
python -m pytest tests/ci tests/skills -q → PASS
# optional, only if you have a test workspace:
# bin/bt smoke <skill>.case-01-happy-path → PASS (Xs)
```

## Design Notes

<!-- Why this approach? Any tradeoffs or alternatives considered? Explain duplication if present. -->

## Context

<!-- Batch/epic context, related PRs, or anything a reviewer needs to understand scope. -->

## Pre-submit checklist

<!-- See CONTRIBUTING.md for the full cookbook. -->

- [ ] Skill supports the DPLC (scope per `CONTRIBUTING.md`)
- [ ] `python -m pytest tests/ci tests/skills` passes locally
- [ ] Frontmatter complete (`name`, `description`, `metadata.tier`, `metadata.lifecycle-phase`, `allowed-tools`)
- [ ] `plugin.json` and `skills/README.md` updated if a skill was added/removed/renamed
- [ ] RFD 0008 coding standards honored; linters pass
- [ ] Any `pip install` routes through cgrepo (no public registries)
