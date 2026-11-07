# GitHub Release Notes Guide

This doc covers the format for Catalyst GitHub releases. The goal: someone reading a release note understands what changed and why it matters — without needing to read a PR diff or remember ticket numbers.

For the full release cut (version bump, tagging, publishing), see [`release-process.md`](release-process.md). Scope each release from the **last published tag** — a version with a CHANGELOG entry but no tag was never shipped.

## Format

**Title:** `vX.Y.Z — [short headline theme]`

The headline should name the biggest thing in the release in plain language. One clause, not a list.

```
v1.6.0 — generate-dag RFD Alignment + Behavior Test Hardening
v1.5.0 — Phase 4 Build Suite GA + Quality Hardening
```

**Body:** named narrative sections, not a bullet list of PR titles.

```markdown
## [Feature or theme name]

1-3 sentence narrative. What changed, why it matters, what's new for the user.
Be specific — name the skill, the directive, the pattern — but don't paste the PR description.

## [Second theme if present]

Same pattern.

## Fixed

- Short description of each bug fix — one line, plain language, ticket ref in parens
- Another fix (AICAT-NNN)

---

Full entry with per-PR detail: [CHANGELOG.md](link)
```

## Rules

- **No flat PR lists.** Auto-generated notes (`* fix(x): ... by @author in PR #NNN`) are the floor, not the format.
- **Sections = themes, not PRs.** Multiple PRs can collapse into one section if they're the same theme.
- **`## Fixed` for bug-only items.** If a change is purely corrective with no user-facing feature, it goes under Fixed, not its own section.
- **Always close with CHANGELOG link.** Release notes are the summary; CHANGELOG.md has the full per-PR detail.
- **Thank contributors.** Add a one-line thank-you for each contributor outside the core maintainers (skip the release-chore author). See [`release-process.md`](release-process.md#contributor-credit).

## Template (copy-paste)

```markdown
## [Primary change — skill name or theme]

[1-3 sentences: what changed and why it matters]

## [Secondary change if present]

[1-3 sentences]

## Fixed

- [Bug fix description] (AICAT-NNN)
- [Bug fix description] (AICAT-NNN)

---

Full entry with per-PR detail: [CHANGELOG.md](https://github.com/cg-open-itg/catalyst/blob/main/CHANGELOG.md)
```

## Reference releases

- [`v1.6.0`](https://github.com/cg-open-itg/catalyst/releases/tag/1.6.0) — two feature sections + Fixed
- [`v1.5.0`](https://github.com/cg-open-itg/catalyst/releases/tag/1.5.0) — large feature GA + repairs + consolidation
