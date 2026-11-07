# Usage Analytics Report

```yaml
Phase:          8 - Evolve
Artifact:       Usage Analytics Report
Data Product:   [Product Name]
Date:           [YYYY-MM-DD]
```

## Review Context

| Field              | Detail                                                      |
|--------------------|-------------------------------------------------------------|
| Review Period      | [YYYY-MM-DD] to [YYYY-MM-DD]                               |
| Review Type        | [ ] Annual (default) / [ ] Event-triggered                  |
| Trigger (if event) | [e.g., major schema change, cost spike, consumer complaint] |
| Prepared By        | [Name / Team]                                               |

## Usage Metrics

| Metric                   | Current Period | Prior Period | Change     |
|--------------------------|----------------|--------------|------------|
| Active Consumers         | [count]        | [count]      | [+/- N]    |
| Total Query Volume       | [count]        | [count]      | [+/- %]    |
| Unique Access Patterns   | [count]        | [count]      | [+/- N]    |
| Peak Usage Window        | [time range]   | [time range] |            |
| Growth Trend             | [description]  |              |            |

### Consumer Breakdown

| Consumer / Team        | Access Frequency | Primary Use Case         |
|------------------------|------------------|--------------------------|
| [Consumer 1]           | [e.g., Daily]   | [Brief description]      |
| [Consumer 2]           | [e.g., Weekly]  | [Brief description]      |

## SLA Performance Summary

| SLA Metric     | Target       | Actual       | Met   | Notes            |
|----------------|--------------|--------------|-------|------------------|
| Freshness      | [threshold]  | [actual]     | [Y/N] |                  |
| Completeness   | [threshold]  | [actual]     | [Y/N] |                  |
| Availability   | [threshold]  | [actual]     | [Y/N] |                  |
| Quality Score  | [threshold]  | [actual]     | [Y/N] |                  |

| SLA Summary        | Value       |
|--------------------|-------------|
| Total SLA Breaches | [count]     |
| S1/S2 Incidents    | [count]     |

## Cost Summary

| Cost Category     | Current Period | Prior Period | Change   | Budget   |
|-------------------|----------------|--------------|----------|----------|
| Compute           | [$X]           | [$X]         | [+/- %]  | [$X]     |
| Storage           | [$X]           | [$X]         | [+/- %]  | [$X]     |
| Egress / Transfer | [$X]           | [$X]         | [+/- %]  | [$X]     |
| **Total**         | **[$X]**       | **[$X]**     | [+/- %]  | **[$X]** |

## Value Assessment

| Original KPI               | Target          | Actual          | Met   |
|-----------------------------|-----------------|-----------------|-------|
| [KPI 1 from design phase]  | [target value]  | [actual value]  | [Y/N] |
| [KPI 2 from design phase]  | [target value]  | [actual value]  | [Y/N] |

## Consumer Feedback Summary

| Source              | Sentiment       | Key Themes                        |
|---------------------|-----------------|-----------------------------------|
| [e.g., survey]     | [Positive/Mixed/Negative] | [Summary of feedback]   |
| [e.g., support tickets] | [Positive/Mixed/Negative] | [Summary of feedback] |

## Health Score

| Dimension       | Score (0-100) | Weight | Weighted Score |
|-----------------|---------------|--------|----------------|
| Usage           | [score]       | [%]    | [calculated]   |
| SLA Compliance  | [score]       | [%]    | [calculated]   |
| Cost Efficiency | [score]       | [%]    | [calculated]   |
| Consumer Satisfaction | [score] | [%]    | [calculated]   |
| **Overall**     |               |        | **[total]**    |

_Health score is optional. If not tracked, remove this section._

## Recommendation

| Recommendation | Selected |
|----------------|----------|
| **Continue**   | [ ] No changes needed; product is healthy and delivering value |
| **Improve**    | [ ] Product is valuable but requires changes (see action items) |
| **Deprecate**  | [ ] Product should be retired (see deprecation notice template) |

**Rationale:** [Explain the reasoning behind the recommendation]

## Action Items

| # | Action                          | Owner        | Priority | Due Date     |
|---|---------------------------------|--------------|----------|--------------|
| 1 | [Describe action]               | [Name/Team]  | [H/M/L]  | [YYYY-MM-DD] |
| 2 | [Describe action]               | [Name/Team]  | [H/M/L]  | [YYYY-MM-DD] |

## Next Review

| Field              | Detail                                              |
|--------------------|-----------------------------------------------------|
| Next Scheduled     | [YYYY-MM-DD] (annual default)                       |
| Event Triggers     | [Conditions that would prompt an earlier review]    |
