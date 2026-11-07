---
name: product-requirements-document
description: |
  Create a comprehensive product requirements document covering business context,
  functional requirements, data requirements, and acceptance criteria. Use when
  the user asks to "write the PRD", "document the requirements", "create the
  product spec", or "define what we are building".
allowed-tools: Read Grep
metadata:
  tier: document
  lifecycle-phase: phase-2-discovery
  dependencies: []
  consumes:
    - demand-tracker-entry
    - consumer-use-case-map
    - feasibility-report
    - requirements-acceptance-criteria
    - outcome-kpi-statement
    - effort-estimate
    - business-case
    - data-profiling
    - discover-data
  shared-components:
    core: []
    platforms: []
---

# Product Requirements Document

Generate a **Product Requirements Document (PRD)** for the data product described
in $ARGUMENTS.

The PRD is the **single source of truth** for a data product. It spans the full
lifecycle — from problem and consumers through technical design, governance, and
approval. Sections marked optional during Discovery are required by the time the
product reaches Design or Publish.

This is a **Phase 2 (Discovery)** artifact that evolves through later phases.

## Instructions

1. Read the template below to understand the exact document structure, sections,
   and field definitions.
2. Gather any required information from the user (skip what is already provided
   in the arguments or conversation context).
3. Produce a structured document that matches the template format exactly —
   same headings, same tables, same field names.
4. Fill in every section with specific, concrete content based on what the user
   has provided. Do not leave bare placeholder text like "[TBD]" or "[fill in]".
   If a field is genuinely undecided in the source material, state what is
   unknown and who owns the decision — e.g., "Pending decision by [owner]
   (per [source])" rather than just "TBD".

## Execution Context

When called by an orchestrator or after execution skills have run, the
conversation may contain additional context. Use it to produce a better PRD:

- **Prior phase artifacts:** If demand-tracker-entry, consumer-use-case-map,
  feasibility-report, or requirements-acceptance-criteria exist, pull product
  name, consumers, classification, requirements, and feasibility findings
  rather than re-asking.
- **Execution results:** If discover-data or data-profiling have run, use
  real table names, row counts, and quality metrics in the Data Requirements
  and Solution Overview sections.
- **Marketplace search:** If marketplace-search has run, reference its findings
  in the Existing Product Check section.

If no execution context is available, proceed normally with user-provided
information.

## Template

The PRD has these sections. Each must appear in the output with the exact
heading and table structure shown.

### Key Product Information

| Field | Value |
|-------|-------|
| **Product Name** | |
| **Data Owner** | |
| **Data Steward** | |
| **Data Product Creator** | |
| **Domain** | |
| **Sensitivity** | _Public / General / Restricted / Highly Restricted_ |
| **Current Phase** | _Triage & Discovery / Design / Build / Validate / Publish / Operate_ |
| **Author** | |
| **Last Updated** | _YYYY-MM-DD_ |

### 1. Executive Summary

Three to five sentences: what is this product, what problem does it solve, who
benefits, and what is the expected business impact? Understandable by an
executive stakeholder without reading the full document.

### 2. Problem & Value

- **Existing Product Check:** Confirm the data catalog/marketplace was searched.
  State what was searched, found, and why existing products don't meet the need.
- **Current State:** How things work today — pain points, manual processes, data
  gaps, workarounds.
- **Future State:** What changes once this product ships. Concrete and measurable.
- **Why Now?** 2-3 compelling reasons this must happen now, each referencing a
  specific deadline, initiative, or escalating pain.

### 3. Consumers & Use Cases

**Primary Consumers** table: Consumer, Team, What They Need

**Key Use Cases** table: Use Case (in "As a [consumer], I want [capability] so
that [outcome]" format), Consumer, Business Value, Priority (P1/P2/P3),
Needed By date.

### 4. Solution Overview

- **What We're Building:** 2-3 paragraphs at a level an engineer or executive
  can understand.
- **What This Is NOT:** Explicit exclusions to prevent scope creep.
- **Output Ports:** table of Port, Type (Table/API/File/Event), Access Method.
- **Key Terms:** 3-5 critical business terms with definitions.

### 5. Data Requirements

> Optional during Discovery; Required in Design.

- **Source Systems:** table of Source System, Data Provided, SoR?, Full/Delta,
  Contract Link, Sample Data Link, Notes.
- **Engineering Intake Snapshot:** Desired Technical Outcome, Number of New
  Outputs, Required SLA, Historical Backfill Required, Backfill Start Date.
- **Data Quality Requirements:** table of Dimension (Freshness, Completeness,
  Accuracy at minimum), Target (specific measurable threshold), How Measured.

### 6. Technical Design

> Optional during Discovery; Required in Design.

Table of Component (Platform, Framework, Orchestration, Consumption),
Technology, Notes.

### 7. Governance

> Required if data has regulatory or sensitivity implications.

Table of Consideration (Regulatory, PII/Sensitive Data, Retention), Applicable?
(Yes/No/TBD), Notes.

### 8. Success Criteria

> Optional during Discovery; Required in Publish.

Table of KPI, Target (specific numeric value), Measurement Method, By When.

### 9. Data Marketplace & Catalog

> Required in Publish.

- **Catalog Metadata:** Display Name, Description, Domain, Sub-Domain, Data
  Category, Update Frequency, Retention Period.
- **Discoverability:** Tags, Keywords, Related Products.
- **Access & Entitlements:** Access Level, Entitlement Group, Request Process.
- **Governance Tool Integration:** Collibra Asset ID, Lineage Documented,
  Quality Rules Registered, Certification Status.

### 10. Approval

Table of Role (Data Owner, Data Steward, Architecture Review), Name, Status
(Pending/Approved/N/A), Date.

### Appendix

- **Related Documentation:** table of Document, Location.
- **Glossary:** table of Term, Definition.
- **Critical Dependencies:** table of Dependency, Owner, Status, Impact if
  Unresolved.
- **Open Questions:** table of Question, Owner, Decision Needed By.
- **Key Risks:** table of Risk, Probability (Low/Med/High), Impact
  (Low/Med/High), Mitigation.
