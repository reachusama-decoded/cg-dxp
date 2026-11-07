# PRD Template 

version 1.0
---

## Overview 

### Key Product Information
| Field | Value |
|-------|-------|
| **Product Name** | [Short and Unique] |
| **Data Owner** | [Who approves this — accountable for the data] |
| **Data Steward** | [Who oversees day-to-day quality and governance] |
| **Data Product Creator** | [Who builds & delivers this product] |
| **Domain** | [L1 Data Domain] |
| **Sensitivity** | [Public \| General \| Restricted \| Highly Restricted] |
| **Current Phase** | [Triage & Discovery \| Design \| Build \| Validate \| Publish \| Operate] |
| **Author** | [Name, Team] |
| **Last Updated** | [YYYY-MM-DD] |

### Section Outline

| Section | Description | Required By |
|---------|-------------|-------------|
| 1. Executive Summary | Product overview, problem, users, and expected impact | Triage & Discovery |
| 2. Problem & Value | Existing product check, current/future state, why now | Triage & Discovery |
| 3. Consumers & Use Cases | Who uses the product and how | Triage & Discovery |
| 4. Solution Overview | What we're building, output ports, key terms, out of scope | Triage & Discovery |
| 5. Data Requirements | Source systems and data quality standards | Design |
| 6. Technical Design | Platform, framework, orchestration, consumption | Design |
| 7. Governance | Regulatory, PII, and retention considerations | Design |
| 8. Success Criteria | Measurable KPIs and targets | Publish |
| 9. Metadata  | Data Marketplace & Catalog for discoverability & Data Governance | Publish |
| 10. Approval | Sign-offs from Data Owner, Steward, Architecture | Publish |
| Appendix | Risks, dependencies, open questions (project-related) | Ongoing |

---

## 1. Executive Summary

*One paragraph summarizing the product, the problem it solves, the target users, and the expected business impact.*

> [Write 3-5 sentences: What is this product? What problem does it solve? Who benefits? What's the expected impact?]

---

## 2. Problem & Value

### Existing Product Check

*Confirm you've checked the data catalog/marketplace for duplicates. This is required before proceeding.*

> [What did you search? What did you find (or not find)? Why is this net-new or why don't existing products meet the need?]

### Current State

*Describe how things work today. Be specific about pain points, manual processes, data gaps, and workarounds.*

- [Pain point 1: What is broken, inefficient, or missing?]
- [Pain point 2]
- [Pain point 3]

### Future State

*Describe what the world looks like after this product ships. Be concrete and measurable.*

> [What changes? What improves? What becomes possible that wasn't before?]

### Why Now?

*List 2-3 reasons this must happen now, not later.*

1. [Compelling reason — e.g., regulatory deadline, strategic initiative, escalating pain]
2. [Second reason]

---

## 3. Consumers & Use Cases

*Identify who will use this data product and how they will use it.*

### Primary Consumers

| Consumer | Team | What They Need |
|----------|------|----------------|
| [Name/Role] | [Team] | [Their primary need from this product] |
| | | |

### Key Use Cases

*At least one use case per consumer. Use the format: As a [consumer], I want [capability] so that [outcome].*

| Use Case | Consumer | Business Value | Priority | Needed By |
|----------|----------|----------------|----------|-----------|
| [As a ___, I want ___ so that ___] | [Consumer] | [Value delivered] | [P1/P2/P3] | [YYYY-MM-DD] |
| | | | | |

---

## 4. Solution Overview

### What We're Building

*2-3 paragraphs describing the product at a level an engineer or executive can understand. What does it do? How does it work at a high level?*

> [Describe the product, its key capabilities, and the consumer experience.]

### What This Is NOT

*Be explicit about what's excluded to prevent scope creep and misunderstanding.*

- [Not a _____ (clarification)]
- [Not a _____ (clarification)]

### Output Ports

*How will consumers access this data product?*

| Port | Type | Access Method |
|------|------|---------------|
| [e.g., customer_360] | Table | [e.g., Unity Catalog] |
| [e.g., /api/v1/customers] | API | [e.g., REST] |
| | | |

### Key Terms

*Define 3-5 critical business terms to ensure shared understanding between producers and consumers.*

| Term | Definition |
|------|------------|
| [Business term] | [Precise definition as used in this product] |
| | |

---

## 5. Data Requirements

💡 *Optional during Discover; Required in Design.*

### Source Systems

*Identify the systems that will provide data for this product.*

| Source System | Data Provided | SoR? | Full/Delta | Contract Link | Sample Data Link | Notes |
|---------------|---------------|------|------------|---------------|------------------|-------|
| [System name] | [What data it provides] | [Yes/No] | [Full/Delta] | [Link] | [Link] | [Access method, known issues, etc.] |
| | | | | | | |

### Engineering Intake Snapshot

*Capture delivery-critical details early to reduce redesign during handoff to Design/Build.*

| Field | Value |
|-------|-------|
| Desired Technical Outcome | [Enhancement to existing asset \| New curated table \| New API/view \| Ingestion \| Managed file transfer \| Other] |
| Number of New Outputs | [e.g., 1 table, 2 views, 1 API endpoint] |
| Required SLA | [Day/time data must be available, e.g., Daily by 06:00 PT] |
| Historical Backfill Required | [Yes/No] |
| Backfill Start Date (if Yes) | [YYYY-MM-DD] |

### Data Quality Requirements

💡 *Optional during Discover; Required in Design.*

*Define the quality standards this product must meet.*

| Dimension | Target | How Measured |
|-----------|--------|--------------|
| Freshness | [e.g., Daily by 6 AM T+1] | [SLA monitoring] |
| Completeness | [e.g., ≥99% records present] | [Null checks, row counts] |
| Accuracy | [e.g., Reconciled to source] | [Validation rules] |

---

## 6. Technical Design

💡 *Optional during Discover; Required in Design.*

*High-level architecture decisions. Details will be refined in Design phase.*

| Component | Technology | Notes |
|-----------|------------|-------|
| Platform | [e.g., Databricks Unity Catalog] | |
| Framework | [e.g., dbt, Hourglass] | |
| Orchestration | [e.g., Airflow] | |
| Consumption | [e.g., Power BI, Dremio, API] | |

---

## 7. Governance

### Compliance

💡 *Required if data has regulatory or sensitivity implications.*

| Consideration | Applicable? | Notes |
|---------------|-------------|-------|
| Regulatory (GDPR, SOX, SEC) | [Yes / No / TBD] | [Requirements if applicable] |
| PII / Sensitive Data | [Yes / No] | [Handling approach] |
| Retention Requirements | [Yes / No] | [Retention period] |

---

## 8. Success Criteria

*Define how you'll know this product is successful. At least one measurable KPI required.*

💡 *Optional during Discover; Required in Publish.*

| KPI | Target | Measurement Method | By When |
|-----|--------|-------------------|---------|
| [Primary metric — what you're optimizing for] | [Numeric target] | [How you'll measure it] | [Date] |
| [Secondary metric] | | | |

---

## 9. Data Marketplace & Catalog

💡 *Required in Publish. Captures metadata for Data Marketplace discoverability and Data Governance tools (e.g., Collibra).*

### Catalog Metadata

*Information that will be published to the Data Marketplace for discoverability.*

| Field | Value |
|-------|-------|
| **Display Name** | [User-friendly name for the marketplace] |
| **Description** | [2-3 sentence description for catalog search] |
| **Domain** | [L1 / L2 Data Domain] |
| **Sub-Domain** | [If applicable] |
| **Data Category** | [e.g., Master Data, Transactional, Reference, Analytical] |
| **Update Frequency** | [Real-time \| Hourly \| Daily \| Weekly \| Monthly] |
| **Retention Period** | [e.g., 7 years, indefinite] |

### Discoverability

| Field | Value |
|-------|-------|
| **Tags** | [Comma-separated tags for search] |
| **Keywords** | [Business terms that consumers might search for] |
| **Related Products** | [Links to upstream/downstream data products] |

### Access & Entitlements

| Field | Value |
|-------|-------|
| **Access Level** | [Public \| Internal \| Restricted \| Highly Restricted] |
| **Entitlement Group** | [AD group or entitlement required for access] |
| **Request Process** | [How consumers request access] |

### Governance Tool Integration

*For Collibra or similar data governance platforms.*

| Field | Value |
|-------|-------|
| **Collibra Asset ID** | [If registered] |
| **Lineage Documented** | [Yes / No] |
| **Quality Rules Registered** | [Yes / No] |
| **Certification Status** | [Draft \| Certified \| Deprecated] |

---

## 10. Approval

### Approvals

| Role | Name | Status | Date |
|------|------|--------|------|
| Data Owner | | [Pending / Approved] | |
| Data Steward | | [Pending / Approved] | |
| Architecture Review | | [Pending / Approved / N/A] | |

---

## Appendix

### Related Documentation

*Links to other key artifacts created during the lifecycle of the Product.*

| Document | Location |
|----------|----------|
| [Product Canvas] | [Link] |
| [Technical Data Contract] | [Link] |
| [Architecture Diagram] | [Link] |
| [Test Plan & Cases] | [Link] |


### Glossary

| Term | Definition |
|------|------------|
| [Domain-specific term] | [Plain-language definition] |


### Risks & Dependencies

*Project-related risks and dependencies. Update during execution; archive after launch.*

#### Critical Dependencies

| Dependency | Owner | Status | Impact if Unresolved |
|------------|-------|--------|----------------------|
| [What you depend on] | [Who owns it] | [Status] | [What happens if not resolved] |
| | | | |

#### Open Questions

| Question | Owner | Decision Needed By |
|----------|-------|-------------------|
| [Blocking question] | [Who can answer] | [Date] |
| | | |

#### Key Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [What could go wrong] | [Low/Med/High] | [Low/Med/High] | [How you'll prevent or respond] |
| | | | |


---

**Document Status**: [Draft \| In Review \| Approved]  
**Version**: [X.X]  
**Created**: [YYYY-MM-DD]
