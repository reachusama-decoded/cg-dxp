---
phase: "02-Design"
artifact: "Security Design"
data_product: "[Product Name]"
date: "YYYY-MM-DD"
---

# Security Design

> **When is this needed?** This artifact is optional, required when the data product's sensitivity
> or criticality classification warrants security controls beyond platform defaults. Consult your
> organization's data classification policy to determine applicability.

---

## 1. Overview

| Field | Value |
|-------|-------|
| Product Name | [Product name] |
| Sensitivity | [e.g., Restricted / Highly Restricted] |
| Criticality | [e.g., High / Critical] |
| Regulatory Scope | [e.g., GDPR, CCPA, HIPAA, SOX — list all applicable] |
| Justification | [Why this product requires a security design beyond platform defaults] |

---

## 2. Access Control Model

### 2.1 Role-Based Grants

| Role | Scope | Permissions | Granted To | Approval Required |
|------|-------|-------------|------------|-------------------|
| `product_owner` | Full product | Read, write, admin | [Data product owner] | N/A |
| `domain_analyst` | Full product | Read | [Domain team members] | Manager approval |
| `restricted_consumer` | Filtered subset | Read (row/column filtered) | [Specific consumer teams] | Data owner + security approval |
| `service_account_ingest` | Raw layer only | Write | [Ingestion service] | Platform team approval |
| | | | | |

### 2.2 Column-Level Security

| Column | Sensitivity | Restricted From | Access Method |
|--------|-------------|-----------------|---------------|
| [e.g., `email`] | PII | All roles except `product_owner` | [e.g., Masked, tokenized, or hidden via column policy] |
| [e.g., `ssn`] | PII / Regulated | All roles except `product_owner` | [e.g., Fully restricted; available only via approved query with audit log] |
| [e.g., `salary`] | Restricted | Non-HR roles | [e.g., Column masking policy, returns `NULL` for unauthorized roles] |
| | | | |

### 2.3 Row-Level Security

| Filter Rule | Description | Applied To Roles | Implementation |
|-------------|-------------|------------------|----------------|
| [e.g., Region filter] | Users see only data for their assigned region | `regional_analyst` | [e.g., Row access policy matching `user_region` attribute] |
| [e.g., Tenant isolation] | Consumers see only their tenant's data | `restricted_consumer` | [e.g., Session variable or mapped attribute filter] |
| | | | |

---

## 3. Authentication & Authorization

| Component | Method | Details |
|-----------|--------|---------|
| User authentication | [e.g., SSO via identity provider, MFA required] | [Implementation details] |
| Service authentication | [e.g., Service account with short-lived tokens] | [Credential rotation policy] |
| Authorization model | [e.g., RBAC with attribute-based overrides] | [How roles are assigned and reviewed] |
| Privilege escalation | [e.g., Just-in-time access via approval workflow] | [Process for temporary elevated access] |
| Session management | [e.g., Tokens expire after X hours, no persistent sessions] | [Session timeout and refresh policy] |

---

## 4. Encryption

| Layer | Method | Details |
|-------|--------|---------|
| At rest | [e.g., Platform-managed encryption, customer-managed keys] | [Key management details, rotation policy] |
| In transit | [e.g., TLS 1.2+ enforced] | [Certificate management] |
| Field-level | [e.g., Application-level encryption for specific PII columns] | [Which columns, key management, decrypt permissions] |
| Key management | [e.g., Centralized key management service] | [Rotation cadence, access to key material] |

---

## 5. Audit & Monitoring

### 5.1 Audit Events

| Event | What Is Logged | Retention | Accessible To |
|-------|----------------|-----------|---------------|
| Data access (query) | User, timestamp, query, rows returned | [e.g., 1 year] | Security team, data owner |
| Data modification | User, timestamp, operation, affected rows | [e.g., 1 year] | Security team, data owner |
| Permission changes | User, timestamp, role granted/revoked, target | [e.g., 2 years] | Security team |
| Export / download | User, timestamp, volume, destination | [e.g., 1 year] | Security team, data owner |
| Failed access attempts | User, timestamp, resource, denial reason | [e.g., 1 year] | Security team |

### 5.2 Monitoring & Alerting

| Signal | Condition | Alert Threshold | Response |
|--------|-----------|-----------------|----------|
| Unusual access volume | Query count per user significantly above baseline | > [X]x 7-day average | Investigate; potential data exfiltration |
| Access from unexpected location | Query from IP range outside expected set | Any occurrence | Alert security team; verify legitimacy |
| Repeated failed access | Multiple permission denials for same user | > [X] denials in [Y] minutes | Alert security team; possible misconfiguration or attack |
| Privilege escalation | Admin/elevated role granted | Any occurrence | Verify approval exists; alert if unapproved |
| | | | |

---

## 6. Threat Model

| Threat | Attack Vector | Likelihood | Impact | Mitigation |
|--------|--------------|------------|--------|------------|
| Unauthorized data access | Compromised user credentials | [Low / Medium / High] | [e.g., PII exposure] | MFA, session limits, access monitoring |
| Data exfiltration | Authorized user exports bulk data | [Low / Medium / High] | [e.g., Customer data leak] | Export controls, volume alerts, DLP policies |
| Insider threat | Privileged user abuses access | [Low / Medium / High] | [e.g., Data manipulation or theft] | Least-privilege roles, audit logs, periodic access review |
| SQL injection | Malicious input via parameterized consumer queries | [Low / Medium / High] | [e.g., Unauthorized data retrieval] | Input sanitization, parameterized queries, platform protections |
| Supply chain compromise | Compromised transformation dependency or library | [Low / Medium / High] | [e.g., Data corruption, code execution] | Dependency scanning, pinned versions, code review |
| | | | | |

---

## 7. Compliance Controls

| Requirement | Control | Implementation | Verification |
|-------------|---------|----------------|--------------|
| [e.g., GDPR Art. 17 — Right to Erasure] | Deletion propagation | [e.g., Deletion requests processed within X days across all layers] | [e.g., Quarterly audit of deletion completeness] |
| [e.g., GDPR Art. 30 — Records of Processing] | Processing registry | [e.g., Data lineage and purpose documented in data contract] | [e.g., Annual review] |
| [e.g., SOX — Access Controls] | Segregation of duties | [e.g., Write access separated from approval access] | [e.g., Quarterly access certification] |
| [e.g., Data residency] | Geographic restriction | [e.g., Data stored and processed in approved regions only] | [e.g., Infrastructure audit, deployment guardrails] |
| | | | |

---

## 8. Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| Data Product Owner | | | [ ] Approved |
| Security / InfoSec | | | [ ] Approved |
| Privacy / Legal (if applicable) | | | [ ] Approved |
| Platform / Infrastructure | | | [ ] Approved |

---

## Appendix: Revision History

| Version | Date | Author | Summary of Changes |
|---------|------|--------|--------------------|
| 0.1 | | | Initial draft |
| | | | |
