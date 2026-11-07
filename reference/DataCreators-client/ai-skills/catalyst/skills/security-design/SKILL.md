---
name: security-design
description: |
  Document authentication, authorization, encryption, audit trails, and threat
  model. Use when the user asks to "create the security design", "document
  access control", "write the security spec", "design the auth model", or
  "assess security requirements".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-3-design
  dependencies: []
  consumes:
    - privacy-impact-assessment
    - data-contract
  shared-components:
    core: []
    platforms: []
---

# Security Design

Generate a **Security Design** for the data product described in $ARGUMENTS.

Use when the user asks to "design the security model", "document access
controls", "create a threat model", "define encryption requirements", or
"specify authentication and authorization for this data product".

## Lifecycle Context

| Field | Value |
|-------|-------|
| Phase | **Phase 3 — Design** |
| Precedes | Build Checklist (Phase 4), UAT Sign-Off (Phase 5) |
| Depends on | Privacy Impact Assessment (Phase 2), Data Contract (Phase 3) |
| Gate | Security review must approve before entering Build; mandatory for Restricted+ data |

The security design specifies how the data product is protected — authentication,
authorization, encryption, masking, audit logging, and threat mitigations. For
products classified Restricted or above, InfoSec sign-off is required.

## Instructions

1. Read the template at `templates/security-design.md` to understand the
   exact document structure, sections, and field definitions.
2. Gather any required information from the user (skip what is already provided
   in the arguments or conversation context).
3. Produce a structured document that matches the template format exactly —
   same headings, same tables, same field names. Use `## ` (H2) headings
   with the exact text shown below — numbered prefixes are required.
   The output **must** contain these H2 sections in order:
   - `## 1. Overview` — Field/Value table with rows: Product Name,
     Sensitivity, Criticality, Regulatory Scope, Justification
   - `## 2. Access Control Model` — three sub-sections:
     - `### 2.1 Role-Based Grants` (columns: Role, Scope, Permissions,
       Granted To, Approval Required)
     - `### 2.2 Column-Level Security` (columns: Column, Sensitivity,
       Restricted From, Access Method)
     - `### 2.3 Row-Level Security` (columns: Filter Rule, Description,
       Applied To Roles, Implementation)
   - `## 3. Authentication & Authorization` — table with columns:
     Component, Method, Details
   - `## 4. Encryption` — table with columns: Layer, Method, Details
   - `## 5. Audit & Monitoring` — two sub-sections:
     - `### 5.1 Audit Events` (columns: Event, What Is Logged, Retention,
       Accessible To)
     - `### 5.2 Monitoring & Alerting` (columns: Signal, Condition, Alert
       Threshold, Response)
   - `## 6. Threat Model` — table with columns: Threat, Attack Vector,
     Likelihood, Impact, Mitigation
   - `## 7. Compliance Controls` — table with columns: Requirement,
     Control, Implementation, Verification
   - `## 8. Sign-Off` — table with columns: Role, Name, Date, Status
   - `## Appendix: Revision History` — table with columns: Version, Date,
     Author, Summary of Changes (no numbering prefix on this heading)
4. Fill in every section with specific, concrete content based on what the user
   has provided. Do not leave bare placeholder text like "[TBD]" or "[fill in]".
   If a field is genuinely undecided in the source material, state what is
   unknown and who owns the decision — e.g., "Pending decision by [owner]
   (per [source])" rather than just "TBD".

## Quality Checks

Before finalizing the document, verify:

- [ ] No placeholder text remains (no `[TBD]`, `[fill in]`, `[Name]` etc.)
- [ ] Authentication method is specific (OAuth2, service account, etc.)
- [ ] Authorization model names concrete roles/groups, not just "role-based"
- [ ] Encryption details specify algorithms and key management approach
- [ ] Threat model identifies at least three threats with mitigations
- [ ] Tables have data rows, not just headers

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce better artifacts:

- **Prior phase artifacts:** If a `privacy-impact-assessment` exists in the
  conversation, use its PII inventory and risk findings to populate the threat
  model and required controls. If a `data-contract` exists, use its access
  control section as the starting point for authorization design.

If no execution context is available, proceed normally with user-provided
information.
