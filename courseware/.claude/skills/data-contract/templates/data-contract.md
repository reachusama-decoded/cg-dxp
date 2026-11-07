---
phase: "02-Design"
artifact: "Data Contract"
data_product: "[Product Name]"
date: "YYYY-MM-DD"
---

# Data Contract

> The data contract is the authoritative agreement between producers and consumers.
> It defines what data is provided, at what quality, and under what terms.
> A follow-on RFD will define the minimum required contract structure.

---

## 1. Identity

| Field              | Value                                      |
|--------------------|--------------------------------------------|
| Product Name       | [Product name]                             |
| Domain Catalog     | [Domain or catalog this product belongs to] |
| Owner              | [Team or individual accountable]           |
| Steward            | [Day-to-day data steward, if different]    |
| Version            | [Semantic version, e.g., 1.0.0]           |
| Effective Date     | [Date this contract version takes effect]  |
| Review Cadence     | [e.g., Quarterly, on material change]     |
| Classification     | Sensitivity: [e.g., Public / General / Restricted / Highly Restricted] |
|                    | Criticality: [e.g., Low / Medium / High / Critical] |

---

## 2. Schema

| Column | Type | Nullable | Description | PII | Sensitivity | Criticality | Example |
|--------|------|----------|-------------|-----|-------------|-------------|---------|
| `id` | `STRING` | No | Primary identifier | No | General | High | `abc-123` |
| `email` | `STRING` | Yes | Customer email address | Yes | Restricted | Medium | `user@example.com` |
| `created_at` | `TIMESTAMP` | No | Record creation timestamp | No | General | Medium | `2026-01-15T08:30:00Z` |
| | | | | | | | |

> Add or remove rows as needed. Every column exposed to consumers must be documented here.

---

## 3. Service Level Agreements (SLAs)

### 3.1 SLA Targets

| Metric | Target | Measurement Method | Measurement Window |
|--------|--------|--------------------|--------------------|
| Freshness | Data available within [X] minutes/hours of source event | Compare latest record timestamp to wall clock at serving layer | Rolling 30 days |
| Completeness | >= [X]% of expected records present | Count of records delivered vs. count of records expected from source | Per delivery batch |
| Availability | >= [X]% uptime for query access | Synthetic monitoring of serving endpoint / platform health checks | Monthly |
| Data Quality | >= [X]% of records pass all quality rules | Ratio of records passing quality checks to total records | Per delivery batch |

### 3.2 Breach Response

| Severity | Definition | Response Time | Resolution Time | Escalation Path |
|----------|------------|---------------|-----------------|-----------------|
| Critical | Data unavailable or > [X]% quality failure affecting critical consumers | [X] minutes | [X] hours | On-call engineer -> Team lead -> Domain owner |
| High | SLA breach on freshness or completeness affecting production consumers | [X] hours | [X] business hours | On-call engineer -> Team lead |
| Medium | Partial quality degradation, non-critical consumers affected | [X] business hours | [X] business days | Data steward -> Team lead |
| Low | Cosmetic issues, documentation gaps, minor anomalies | [X] business days | [X] business days | Data steward |

---

## 4. Data Quality Rules

| Rule ID | Column(s) | Rule Description | Severity | Action on Failure |
|---------|-----------|------------------|----------|-------------------|
| DQ-001 | `id` | Must be non-null and unique | Critical | Block delivery |
| DQ-002 | `email` | Must match valid email format when non-null | High | Flag and deliver |
| DQ-003 | `created_at` | Must not be in the future | Medium | Flag and deliver |
| | | | | |

> This table is the **authoritative source of truth** for the product's quality rules. When a DQ Controls Plan
> (`/data-quality-controls-plan`) exists, populate these rows from its approved controls rather than re-deriving
> them — carry Column(s), rule description (note the DQ dimension in the text), Severity, and Action on Failure
> (STOP → Block delivery; WARN → Flag and deliver). Define pass/fail thresholds where applicable and align severity
> levels with the breach response table above.
> _(Whether §4 should carry a dedicated DQ Dimension column is an open standards question — see the RFD.)_

---

## 5. Access & Security

| Field | Value |
|-------|-------|
| Access Model | [e.g., Role-based, attribute-based] |
| Default Grant | [e.g., Read access to domain members] |
| Restricted Columns | [List columns with column-level security, if any] |
| Row-Level Filtering | [Describe row-level security rules, if any] |
| Encryption at Rest | [Yes / No / Platform default] |
| Encryption in Transit | [Yes / No / Platform default] |
| Retention Policy | [e.g., 7 years, 90 days rolling] |
| Masking / Tokenization | [Describe any PII masking or tokenization applied] |

---

## 6. Change Management

### 6.1 Breaking Changes

Breaking changes require consumer notification and a migration period.

| Change Type | Example | Minimum Notice Period | Migration Support |
|-------------|---------|----------------------|-------------------|
| Column removal | Dropping a consumed column | [X] days/weeks | Deprecation warning, then removal |
| Type change | `STRING` -> `INTEGER` | [X] days/weeks | Parallel column, then cutover |
| Semantic change | Redefining what a column means | [X] days/weeks | Documentation + consumer review |
| Grain change | Changing from daily to hourly grain | [X] days/weeks | Consumer impact assessment required |

### 6.2 Non-Breaking Changes

Non-breaking changes may be deployed without a migration period but must be communicated.

- Adding new nullable columns
- Relaxing a NOT NULL constraint
- Adding new data quality rules
- Improving documentation or descriptions

### 6.3 Versioning Policy

| Field | Value |
|-------|-------|
| Strategy | [e.g., Semantic versioning, date-based] |
| Breaking Change Increment | [e.g., Major version bump] |
| Non-Breaking Change Increment | [e.g., Minor or patch version bump] |
| Concurrent Versions Supported | [e.g., Current + 1 prior version] |

---

## 7. Consumer Registry

| Consumer | Team | Use Case | Access Level | Contact | Onboarded Date |
|----------|------|----------|--------------|---------|----------------|
| [Consumer name] | [Team] | [Brief description] | [Read / Filtered] | [Contact] | [Date] |
| | | | | | |

> Maintain this registry to understand downstream impact of changes.

---

## 8. Approvals

| Role | Name | Date | Status |
|------|------|------|--------|
| Data Product Owner | | | [ ] Approved |
| Domain Steward | | | [ ] Approved |
| Security / Privacy (if required) | | | [ ] Approved |
| Consumer Representative(s) | | | [ ] Approved |

---

## Appendix: Revision History

| Version | Date | Author | Summary of Changes |
|---------|------|--------|--------------------|
| 0.1 | | | Initial draft |
| | | | |
