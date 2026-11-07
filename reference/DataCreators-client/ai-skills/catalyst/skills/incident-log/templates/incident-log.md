# Incident Log

```yaml
Phase:          7 - Operate
Artifact:       Incident Log
Data Product:   [Product Name]
Date:           [YYYY-MM-DD]
```

## Incident Register

| ID     | Date       | Severity | Description         | Root Cause          | Resolution          | Time to Detect | Time to Resolve | Follow-Up Actions      |
|--------|------------|----------|---------------------|---------------------|---------------------|----------------|-----------------|------------------------|
| INC-001| YYYY-MM-DD | [S1-S4]  | [Brief description] | [Root cause]        | [How it was fixed]  | [e.g., 5 min]  | [e.g., 45 min]  | [Actions / ticket ref] |
| INC-002| YYYY-MM-DD | [S1-S4]  | [Brief description] | [Root cause]        | [How it was fixed]  | [e.g., 10 min] | [e.g., 2 hrs]   | [Actions / ticket ref] |

### Severity Definitions

| Severity | Label    | Description                                                  |
|----------|----------|--------------------------------------------------------------|
| S1       | Critical | Complete data product outage or data corruption              |
| S2       | High     | SLA breach or significant degradation affecting consumers    |
| S3       | Medium   | Partial degradation, no SLA breach, workaround available     |
| S4       | Low      | Minor issue, no consumer impact                              |

## Post-Incident Review

> Complete this section after any S1 or S2 incident. Recommended for recurring S3 incidents.

### Incident: [INC-XXX] — [Title]

| Field                    | Detail                                              |
|--------------------------|-----------------------------------------------------|
| Incident ID              | [INC-XXX]                                           |
| Date of Review           | [YYYY-MM-DD]                                        |
| Facilitator              | [Name]                                              |
| Attendees                | [Names / Teams]                                     |

**Timeline of Events**

| Time           | Event                                    |
|----------------|------------------------------------------|
| [HH:MM TZ]    | [What happened]                          |
| [HH:MM TZ]    | [Detection / alert triggered]            |
| [HH:MM TZ]    | [Response initiated]                     |
| [HH:MM TZ]    | [Resolution confirmed]                   |

**Contributing Factors**

- [Factor 1]
- [Factor 2]

**What Went Well**

- [Positive observation]

**What Could Be Improved**

- [Improvement area]

**Action Items**

| # | Action                          | Owner        | Due Date    | Status   |
|---|---------------------------------|--------------|-------------|----------|
| 1 | [Describe action]               | [Name/Team]  | [YYYY-MM-DD]| [Status] |
| 2 | [Describe action]               | [Name/Team]  | [YYYY-MM-DD]| [Status] |

## Trends & Patterns

> Review periodically (e.g., monthly or quarterly) to identify systemic issues.

| Period          | Total Incidents | S1 | S2 | S3 | S4 | Avg Time to Detect | Avg Time to Resolve |
|-----------------|-----------------|----|----|----|----|--------------------|--------------------|
| [e.g., 2026-Q1]| [count]         |    |    |    |    | [duration]         | [duration]         |

**Recurring Themes**

- [Theme 1: e.g., pipeline timeout failures — occurred N times]
- [Theme 2: e.g., upstream schema drift — occurred N times]

**Recommended Systemic Improvements**

- [Recommendation 1]
- [Recommendation 2]
