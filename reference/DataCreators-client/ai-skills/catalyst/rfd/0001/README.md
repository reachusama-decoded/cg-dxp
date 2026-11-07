---
authors: RBLW
state: published
---

# RFD 1 Requests for Discussion

## Problem

Engineering teams need a lightweight, durable way to propose, discuss, and record
technical decisions. Decisions made in chat or meetings are hard to find later
and lack the context behind why a choice was made.

## Background

This process is modeled on the
[Oxide Computer Company RFD process](https://rfd.shared.oxide.computer/rfd/0001).
An RFD is a document that proposes a change or records a decision. The document
lives in the repository alongside the code it governs, versioned by git and
reviewed through pull requests.

## Proposal

### Reserve a number

Pick the next available number. Create a branch named `rfd/NNNN` (zero-padded to
four digits) and add your RFD at `rfd/NNNN/README.md`. Use the
[template](../0000/README.md) as a starting point.

### Frontmatter

Every RFD starts with YAML frontmatter containing at minimum:

```yaml
---
authors: First Last
state: prediscussion
discussion: (PR link, added when state changes to discussion)
---
```

The `discussion` field should be updated with the PR URL when the RFD enters
discussion.

### States

An RFD moves through the following states:

| State | Meaning |
|-------|---------|
| `ideation` | Early idea — topic and scope only, no detailed proposal yet |
| `prediscussion` | Draft in progress, not yet ready for review |
| `discussion` | PR is open, actively soliciting feedback |
| `published` | Merged to `main`, decision is recorded |
| `committed` | Fully implemented — describes how the system works, not a proposal |
| `abandoned` | Withdrawn by the author, kept for historical record |

Set the state in the YAML frontmatter of the document.

### Write

Fill in the template sections. The most important parts are **Problem** (why are
we doing this?) and **Proposal** (what exactly are we doing?). An RFD doesn't
need to be perfect to enter discussion — it needs to be clear enough to get
useful feedback.

### Discuss

Open a pull request from your `rfd/NNNN` branch to `main`. Set the state to
`discussion` and add the PR URL to the `discussion` frontmatter field. Reviewers
comment directly on the PR — line-level review keeps feedback anchored to the
text.

### Publish

When discussion converges, set the state to `published` and merge the PR. The
merged document is the permanent record of the decision.

### Amend

Published RFDs can be updated. Open a new PR against the existing document. If
the change is substantial, consider writing a new RFD that supersedes the
original.

### Commit

Once the work described by a published RFD is fully implemented, update the
state to `committed`. At that point the document describes how the system
actually works, not a proposal.

## Impact

All engineering decisions that cross team boundaries or set precedent should go
through an RFD. Day-to-day implementation choices do not need one.
