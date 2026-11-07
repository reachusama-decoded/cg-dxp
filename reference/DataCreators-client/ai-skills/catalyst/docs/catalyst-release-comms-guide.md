# Catalyst Release Communications Guide

How to prepare and send release comms for each **Catalyst** version (the agentic platform itself). Runs after the GitHub release is published — see [`release-process.md`](release-process.md) for the full end-to-end cut (version bump → tag → release → comms).

> **Scope:** This guide covers Catalyst product releases — new skills, fixes, and improvements to the platform. It does not cover data product releases built using Catalyst.

## Artifacts

| Artifact | Location | Audience |
|---|---|---|
| HTML email | `docs/release-comms/releases/vX.Y.Z.html` | All users — Teams + email |
| Plain-text | Drafted inline, not committed | Teams message copy |
| CHANGELOG | `CHANGELOG.md` | Contributors / technical audience |
| GitHub release notes | GitHub Releases | Contributors / technical audience |

## Process

**1. Draft the HTML**
- Copy `docs/release-comms/template.html` → `docs/release-comms/releases/vX.Y.Z.html`
- The HTML is the **full release notes** for the email, structured as:
  - **Headline section(s)** — the biggest new skill/feature(s), teal headings
  - **Updates & Enhancements** — other shipped skills/tooling that aren't the headline
  - **Coming Soon** — approved RFDs / ratified standards, framed as upcoming direction (not shipped product)
- Add a one-line **thank-you** for each contributor outside the core maintainers, using plain **initials** (e.g. “Thank you to AGGB”) — never `@handle_capgroup`
- Update date, version number, and the three footer links

**2. Content rules**
- No PR numbers, no Jira tickets, no jargon
- Skill names in code style (`/validate-dag`)
- No repo-specific names as the lead (e.g. `edo-ig-data-products`) — describe what it does
- Internal-only changes (Catalyst dev team) go in `Updates & Enhancements` or `Also shipped`, not the headline
- Keep `behavior-test-triage` and similar dev-facing skills out of the headline sections
- **Approved RFDs are roadmap**, not shipped features — they belong under `Coming Soon`
- Thank-yous use **initials only**; skip core maintainers (currently MRQL, RBLW, RYQF) and the release-chore author

**3. Review**
- Check skill names match actual `skills/` directory names
- The footer **Read Release Notes** link points to the version being released (unprefixed tag, e.g. `1.11.0`); it resolves once that tag is published
- Footer carries three links: **Read Release Notes**, **Get Started**, **Join Catalyst Launchpad**
- Escape `&` as `&amp;` in any Teams/deep-link URLs so the HTML stays valid

**4. Send**
- Teams: `EDO AI` channel
- Email: Catalyst users distribution list
- Same message for both — HTML for email, plain-text adapted for Teams

## Template

`docs/release-comms/template.html` — use v1.7.0 as the canonical example.

## Reference releases

- `docs/release-comms/releases/v1.7.0.html` — first release using this format
