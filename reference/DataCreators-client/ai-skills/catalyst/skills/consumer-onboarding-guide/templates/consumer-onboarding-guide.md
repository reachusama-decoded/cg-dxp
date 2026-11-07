# Consumer Onboarding Guide

```yaml
Phase:          6 - Publish
Artifact:       Consumer Onboarding Guide (Optional)
Data Product:   [Product Name]
Date:           [YYYY-MM-DD]
```

> **When to use:** This template is intended for data products with external or cross-team consumers who need guidance on discovery, access, and usage.

## Product Overview

| Field                 | Detail                                              |
|-----------------------|-----------------------------------------------------|
| Product Name          | [Name]                                              |
| Description           | [Brief description of what this product provides]   |
| Domain / Owner        | [Owning team or domain]                             |
| Data Sensitivity      | [e.g., Public, General, Restricted, Highly Restricted]  |
| Data Criticality      | [e.g., Low, Medium, High, Critical]                 |
| Current Version       | [e.g., v1.0.0]                                      |
| Refresh Frequency     | [e.g., Daily, Hourly, Near-real-time]               |

## Access Instructions

### How to Request Access

1. [Describe the access request process, e.g., submit a request through your organization's access management workflow]
2. [Specify any approvals required, e.g., data owner approval, manager approval]
3. [Expected turnaround time for access provisioning]

### Entitlements Required

| Entitlement / Role    | Description                          | Grants Access To        |
|-----------------------|--------------------------------------|-------------------------|
| [Role name]          | [What this role provides]            | [Tables, views, APIs]   |

## Schema Reference

The data contract defines the authoritative schema, SLAs, and quality expectations for this product.

- **Data Contract Location:** [Link or path to the data contract artifact]
- **Key Entities:** [List primary tables, topics, or endpoints]

## Query Examples

### Example 1: [Description]

```sql
-- [Brief explanation of what this query returns]
SELECT column_a, column_b
FROM schema.table
WHERE condition = 'value'
LIMIT 100;
```

### Example 2: [Description]

```sql
-- [Brief explanation]
SELECT ...
```

## SLA Expectations

| Metric        | Target                  | Measurement Window |
|---------------|-------------------------|--------------------|
| Freshness     | [e.g., < 2 hours]      | [e.g., Rolling]    |
| Completeness  | [e.g., >= 99.5%]       | [e.g., Per batch]  |
| Availability  | [e.g., 99.9% uptime]   | [e.g., Monthly]    |
| Quality Score | [e.g., >= 95]          | [e.g., Daily]      |

## Support Channels

| Channel          | Detail                                    |
|------------------|-------------------------------------------|
| Primary Contact  | [Team name or distribution list]          |
| Support Channel  | [e.g., team channel, ticketing queue]     |
| Escalation Path  | [Who to contact if primary is unresponsive]|
| Office Hours     | [If applicable]                           |

## FAQ

**Q: How often is the data refreshed?**
A: [Answer]

**Q: What should I do if the data looks stale or incomplete?**
A: [Answer]

**Q: Can I write back to this product or is it read-only?**
A: [Answer]

**Q: Who do I contact for schema change requests?**
A: [Answer]
