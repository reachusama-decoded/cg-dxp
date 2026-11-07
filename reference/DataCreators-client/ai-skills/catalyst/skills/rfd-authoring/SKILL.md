---
name: rfd-authoring
description: |
  Author a new Request for Discussion (RFD) or edit an existing one. Use when
  the user asks to "draft an RFD", "write an RFD", "propose an RFD", "edit
  RFD NNNN", "open RFD NNNN", or when authoring or modifying files under
  `rfd/NNNN/` in this repository.
allowed-tools: Read Grep Glob Bash Edit Write
metadata:
  tier: capability
  lifecycle-phase: none
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: []
---

# RFD Authoring

Guide for drafting or editing a Request for Discussion (RFD) in this repository.

The canonical specification for the RFD process is **RFD 1** at
`rfd/0001/README.md`. The canonical template is at `rfd/0000/README.md`. This
skill exists because both of those documents are easy to skim past — and the
result is RFDs that drift from the local convention.

## Mandatory pre-read

Before drafting or substantively editing any RFD, **read these two documents
in full**:

1. `rfd/0001/README.md` — the RFD process itself (reserve a number, branch
   naming, state lifecycle, frontmatter requirements)
2. `rfd/0000/README.md` — the canonical template

If you find yourself reaching for a section heading not in the template, stop
and ask the user before adding it. The canonical sections exist because
reviewers expect to find specific content in specific places.

## Canonical structure

Every RFD has these top-level sections, in this order:

| Section | Content |
|---|---|
| `## Problem` | What problem are we solving? Why now? |
| `## Background` | Context the reader needs to understand the proposal |
| `## Proposal` | The proposed change or decision in detail |
| `## Alternatives` | What other approaches were considered, and why rejected |
| `## Impact` | Who and what is affected? Migration path, rollout plan, operational changes |

Sub-headings within each section are fine (and encouraged for long sections).
**Top-level sections outside this list require explicit user approval.** Common
anti-patterns to refuse without permission:

- `## Implementation` — implementation status is not a decision; it belongs
  in `Impact` or in a separate doc
- `## Goals` / `## Non-Goals` — these belong as sub-headings under `Problem`
  or `Proposal`, not as their own top-level sections, unless the local
  convention says otherwise (verify against recent merged RFDs)
- `## Schema` / `## API` — sub-sections of `Proposal`
- `## Risks` — sub-section of `Impact`
- `## TODO` / `## Open Questions` — these belong inline in the relevant
  section, not as their own top-level. An RFD ready for discussion should
  not have a TODO section.

## Frontmatter

Every RFD starts with YAML frontmatter containing at minimum:

```yaml
---
authors: First Last <email@example.com>
state: prediscussion
discussion: (PR link, added when state changes to discussion)
---
```

Verify the `state` is appropriate for the document's stage:

| State | Use when |
|---|---|
| `ideation` | Topic and scope only, no detailed proposal yet |
| `prediscussion` | Draft in progress, not yet ready for review |
| `discussion` | PR open, actively soliciting feedback |
| `published` | Merged to `main`, decision is recorded |
| `committed` | Fully implemented — describes how the system works |
| `abandoned` | Withdrawn by the author |

When opening the PR for review, update `state: discussion` and add the PR URL
to `discussion:`.

## Number and branch conventions

- Pick the next available RFD number. Check `ls rfd/` for existing numbers.
- Use zero-padded four-digit format: `rfd/0042`, not `rfd/42`.
- Branch name matches: `rfd/0042` (same as the directory).
- The RFD itself lives at `rfd/NNNN/README.md`. Diagrams and supporting
  artifacts go under `rfd/NNNN/` as well (e.g. `rfd/NNNN/diagrams/`).

If you are writing an alternative draft to an existing RFD without
superseding it (rare), put it at `rfd/NNNN/README-<descriptor>.md` and
explain the relationship in the leading blockquote — the alternative
should reuse the canonical sections so a reviewer can diff it against
the primary draft section-by-section.

## Voice and style

Before drafting, **scan two or three recently-merged RFDs in this repo** to
absorb the local voice:

```bash
ls rfd/ | sort -n | head -10
# read a few of the most-recent merged ones
```

Calibrate against the existing corpus rather than inventing a new style.
Common local conventions to look for:

- Bold lead-ins inside paragraphs (`**The argument here.**`) vs. plain prose
- Use of `--` em-dashes vs. `—`
- Section-introduction sentences before the first sub-heading
- Tables vs. bullet lists for structured data
- Code blocks vs. inline backticks for short examples

## Discussion etiquette

- Open the PR from `rfd/NNNN` against `main`
- Set `state: discussion` and populate `discussion:` with the PR URL in the
  same commit as the PR-opening
- Line-level review is preferred over PR-comment-level review — reviewers
  comment on specific lines so the conversation stays anchored
- The author makes the final call on whether to incorporate suggestions; the
  RFD process is consensus-seeking, not consensus-required

## When done drafting

Self-review the document before marking it `discussion`-ready:

1. Every top-level section is in the canonical list above
2. Frontmatter is complete; `state` matches the stage
3. The "Problem" section is clear enough that a reviewer who hasn't been in
   the room can understand why this RFD exists
4. The "Proposal" section is concrete enough that a reviewer can disagree
   with a specific choice (vague proposals don't generate useful discussion)
5. The "Alternatives" section names at least one rejected approach with a
   reason — even if it's "the status quo was rejected because X"
6. No TODOs / placeholder text / "TBD" remain
