---
name: dplc-prereq
description: >-
  Phase 0 Pre-requisites -- sub-orchestrator of dplc-design-stage. Verifies roles,
  infrastructure, and organizational readiness before starting the lifecycle.
  Trigger phrases: "check prerequisites", "Phase 0", "prereq check",
  "am I ready to start", "verify readiness".
allowed-tools: Read Grep
metadata:
  tier: orchestrator
  lifecycle-phase: phase-0-prereq
  dependencies:
    - phase-zero-checklist
  consumes: []
  shared-components:
    core: []
    platforms: []
---

# Phase 0: Pre-requisite Orchestrator

This orchestrator guides you through **Phase 0 — Pre-requisite** of the Data
Product Lifecycle (see `rfd/0002/README.md` for the full definition).

**Phase 0 purpose:** Verify that the foundational organizational conditions
exist before a data product request enters the lifecycle. These are not
product-specific — they confirm that the right roles, infrastructure, and
demand management processes are in place.

**Who this is for:** Anyone about to start a new data product — especially
teams new to the lifecycle, or after a long gap since the last product was
launched and you want to confirm nothing has changed.

**Phase 0 gate:** *Ready for Triage?*
- Data Owner is identified and informed
- At least one Data Product Creator has capacity to support Discovery
- A Data Product Manager (or equivalent) is identified and available
- Yes → Triage (Phase 1)
- No → Address blockers first

---

## Progress Reporting

As you work through each step, report progress clearly so the user can
follow along. For each sub-skill or action:

1. **Announce** what you're about to do before doing it
2. **Report** what you found or produced after each step
3. **Show counts and specifics** — not "searched for tables" but "Searched
   caspian_prd for index-related tables — found 5 matches"
4. **Use a checklist** format so the user can see what's done and what's left:

Example:
```
- [x] Read Phase 1 artifacts (product: Index Data Product, 6 consumers mapped)
- [x] discover-data: Searched 3 catalogs, found 5 relevant tables
- [x] data-profiling: Profiled rimes_asset_universe (1.79M rows, 24 indexes)
- [ ] feasibility-report: generating...
- [ ] requirements-acceptance-criteria
- [ ] outcome-kpi-statement
- [ ] effort-estimate
```

Never run silently. The user should always know where you are.

---

## Sub-Skills Invoked

This is the simplest orchestrator. It delegates to **one** document skill,
which produces the entire Phase 0 deliverable:

| Skill | Type | Purpose |
|:------|:-----|:--------|
| `phase-zero-checklist` | document | Produce the Phase 0 checklist confirming roles and infrastructure |

No execution skills are needed at Phase 0 — this phase is about organizational
readiness, not data discovery. **The orchestrator must not produce checklist
content itself; it routes to `phase-zero-checklist` and surfaces that skill's
output verbatim.**

---

## Sequencing

### Step 1 — Gather product context

Check the conversation for any description of the intended data product. If
$ARGUMENTS contains a product name or description, use it. If not, ask the user
one concise question:

> "What data product are you planning to build? A short description is enough
> to get started."

Do not ask about roles or infrastructure yet — the checklist sub-skill will
handle that.

### Step 2 — Delegate to `/phase-zero-checklist` (MANDATORY)

This is the heart of the orchestrator. **You must hand off Phase 0 verification
to the purpose-built `phase-zero-checklist` sub-skill — do not produce the
checklist inline.** Invoke it as `/phase-zero-checklist` using the Skill tool,
passing the product name/description and any role/infrastructure context the
user has already shared. The sub-skill will read its template, walk through
the gate criteria, and produce the full readiness artifact.

Concretely:

1. Invoke the sub-skill via the Skill tool: `Skill(skill="phase-zero-checklist",
   args="<product-name-or-description>; <any-role-or-infra-context-already-shared>")`.
   (Equivalent slash-command invocation: `/phase-zero-checklist <args>`.)
2. Wait for the sub-skill to return its output.
3. **Surface the sub-skill's output to the user verbatim.** Do not paraphrase,
   summarize, abbreviate, or substitute your own version of the checklist.
   The user needs the full structured artifact — roles table, infrastructure
   table, determination — exactly as `phase-zero-checklist` produced it.

If the Skill tool is unavailable in this environment, fall back to reading
`skills/phase-zero-checklist/SKILL.md` and following its instructions to
produce the artifact — but still treat that artifact as the sub-skill's
output and present it verbatim. Never invent a shorter or different checklist
format.

### Step 3 — Report the gate determination

The gate verdict comes from the `phase-zero-checklist` output produced in
Step 2 — it already contains a Determination section. After surfacing the
checklist verbatim, append one short follow-up message that points the user
at the next action:

**If all gate criteria are met (per the checklist's Determination):**
> "Phase 0 complete. All prerequisites are confirmed. You are ready to proceed
> to Phase 1 Triage. Run `/dplc-triage [product-name]` to continue."

**If blockers exist (per the checklist's Determination):**
> Reference the specific "Not Met" rows from the checklist (do not rewrite
> them). Explain that Phase 0 is a hard gate — Triage cannot begin until
> the listed blockers are resolved. Point at the owners / remediation paths
> the checklist already recorded.

### Step 4 — Invite feedback

After the gate determination, append this one-line prompt as the final line
of your response:

> "Anything to flag about this run? Hit enter to skip, or tell me what
> worked / what didn't."

Then:
- **If the user replies with anything substantive** — a sentence, a
  reaction, a problem description, even a short "worked great": invoke
  the `catalyst-feedback` skill with `$ARGUMENTS = "dplc-prereq
  reply=<their reply verbatim>"`. The skill extracts session context
  (sub-skills that ran, current phase, any errors), composes a draft
  issue, **shows the user the full draft for review**, and files after
  they confirm.
- **If the user hits enter / moves on / gives a non-substantive reply**
  (e.g. just "k", "ok", an emoji alone): do nothing. No file, no
  re-prompt. Silence means satisfied.

---

## Notes

- The demand tracker must be a real organizational system, not just the markdown
  template. If no org-wide demand tracker exists, Phase 0 is not met — flag this
  explicitly.
- Phase 0 is verified once per team or program, not repeated for every request.
  If the user says "we've done this before," ask them to confirm the checklist
  items are still current before proceeding.
- Keep this interaction short. Phase 0 should take minutes, not a meeting.
