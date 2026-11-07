# Deprecation Notice

```yaml
Phase:          8 - Evolve
Artifact:       Deprecation Notice
Data Product:   [Product Name]
Date:           [YYYY-MM-DD]
```

## Product Identity

| Field                 | Detail                                              |
|-----------------------|-----------------------------------------------------|
| Product Name          | [Name]                                              |
| Domain / Owner        | [Owning team or domain]                             |
| Current Version       | [e.g., v2.1.0]                                      |
| Data Sensitivity      | [e.g., Public, General, Restricted, Highly Restricted]  |
| Data Criticality      | [e.g., Low, Medium, High, Critical] <!-- Note: criticality levels are currently under review and subject to change --> |

## Reason for Deprecation

[Provide a clear explanation of why this product is being deprecated. Examples: superseded by a new product, no longer delivers sufficient value, underlying source decommissioned, consumer base no longer exists.]

## Timeline

| Milestone              | Date           | Notes                                  |
|------------------------|----------------|----------------------------------------|
| Announcement Date      | [YYYY-MM-DD]   | [When consumers were first notified]   |
| Migration Deadline     | [YYYY-MM-DD]   | [Last date for consumers to migrate]   |
| Read-Only / Freeze     | [YYYY-MM-DD]   | [When updates stop, if applicable]     |
| Decommission Date      | [YYYY-MM-DD]   | [When the product is fully removed]    |

## Affected Consumers

| Consumer / Team       | Impact Level | Contact          | Migration Status  |
|-----------------------|--------------|------------------|-------------------|
| [Consumer 1]          | [H/M/L]      | [Contact info]   | [Not started / In progress / Complete] |
| [Consumer 2]          | [H/M/L]      | [Contact info]   | [Not started / In progress / Complete] |

## Migration Path

### Alternative Product

| Field              | Detail                                              |
|--------------------|-----------------------------------------------------|
| Replacement Name   | [Name of replacement product, or "None"]            |
| Location           | [Where to find the replacement]                     |
| Key Differences    | [What consumers should know about the replacement]  |

### Migration Instructions

1. [Step 1: e.g., identify queries or pipelines referencing this product]
2. [Step 2: e.g., update references to point to the replacement]
3. [Step 3: e.g., validate output matches expectations]
4. [Step 4: e.g., confirm migration with product owner]

_If no replacement exists, describe what consumers should do instead (e.g., source data directly, remove dependency)._

## Data Archival Plan

| Field                     | Detail                                          |
|---------------------------|-------------------------------------------------|
| Archival Required         | [Yes / No]                                      |
| Archival Location         | [Where data will be stored long-term]           |
| Retention Period          | [e.g., 7 years per policy]                      |
| Archival Format           | [e.g., Parquet, CSV, database snapshot]         |
| Archival Owner            | [Name / Team]                                   |
| Archival Completion Date  | [YYYY-MM-DD]                                    |

## Support During Migration

| Field                  | Detail                                          |
|------------------------|-------------------------------------------------|
| Support Window         | [Start date] to [End date]                      |
| Support Channel        | [How consumers can get help during migration]   |
| Office Hours           | [If applicable]                                 |
| Escalation Contact     | [Name / Team]                                   |

## Sign-Off

| Role              | Name | Date | Approved |
|-------------------|------|------|----------|
| Product Owner     |      |      | [ ]      |
| DataOps Lead      |      |      | [ ]      |
| Domain Lead       |      |      | [ ]      |
