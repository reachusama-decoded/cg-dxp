---
name: consumer-aligned
description: >-
  Generate consumer-aligned data products from domain-aligned canonical tables.
  Creates denormalized views, pre-aggregated summaries, time-series rollups,
  and API-friendly formats optimized for consumer use cases. Part of the AI Catalyst
  DPLC plugin bundle, aligned with RFD2 Phase 4 (Build). Use when the user wants
  to build consumer-facing views, reporting tables, dashboard datasets, API endpoints,
  or denormalized data products from existing canonical models.
metadata:
  tier: workflow
  lifecycle-phase: phase-4-build
  dependencies:
    - data-modeling
    - discover-data
    - generate-dag
  consumes:
    - consumer-use-case-map
    - data-contract
  shared-components:
    core: []
    platforms: [databricks]
---

# AI Catalyst DPLC: Consumer-Aligned Data Product Generator

> **RFD2 Phase:** Phase 4 (Build) — Consumer-Aligned Pipeline  
> **Claude Code Users:** See *(planned — not yet created)* for equivalent command prompts

Build consumer-aligned data products from **existing domain-aligned canonical tables**. Unlike source-aligned (raw files) or domain-aligned (multiple sources UNIONed), this skill creates **consumer-optimized views** that flatten joins, pre-aggregate metrics, and format data for reporting, dashboards, and APIs.

## Decision Rule

| User Context | Action |
|---|---|
| Has **domain-aligned canonical tables** and wants **consumer views/dashboards** | --> Use this skill |
| Has **raw source file** (CSV/DAT) and **no existing project** | --> Use source-aligned instead |
| Has **existing UC tables** and wants a **canonical/domain model** | --> Use domain-aligned instead |
| Consumer needs **denormalized reporting table** from multiple entities | --> Use this skill |
| Consumer needs **pre-aggregated metrics** or **time-series rollups** | --> Use this skill |
| Consumer needs **API-friendly JSON format** or **simplified column names** | --> Use this skill |

## When to Use

- User wants to build consumer-facing data products from canonical tables
- User asks for "denormalized view", "reporting table", "dashboard dataset", "API endpoint"
- User needs to flatten joins across multiple domain entities
- User needs pre-aggregated summaries (daily/weekly/monthly metrics)
- User needs time-series rollups or trend tables
- User needs API-friendly formats (clean column names, null handling, JSON structure)
- Consumer personas identified in Triage phase need simplified data access

**Recommended pre-steps:** 
- Run `catalyst-triage-docs` to identify consumer personas and use cases
- Run `catalyst-design-docs` to define consumer schema requirements
- Run `domain-aligned` or have existing canonical tables in UC

## Outputs

Generates artifacts to `workspace/generated/catalyst-dplc/consumer-aligned/<product_name>/`:

```
workspace/generated/catalyst-dplc/consumer-aligned/<product_name>/
├── design/
│   ├── consumer_schema.yaml          # Consumer-facing schema design
│   ├── consumer_model.mmd            # Simplified ER diagram
│   └── use_case_mapping.md           # Consumer personas → views mapping
├── dbt/
│   ├── dbt_project.yml               # dbt project configuration
│   ├── profiles.yml                  # Databricks connection
│   ├── models/
│   │   ├── consumers/
│   │   │   ├── <consumer_view_1>.sql        # Denormalized view
│   │   │   ├── <consumer_view_2>.sql        # Aggregated summary
│   │   │   ├── <consumer_view_3>.sql        # Time-series rollup
│   │   │   └── <consumer_view_4>.sql        # API-friendly format
│   │   └── schema.yml                       # Tests + docs
│   ├── macros/
│   │   ├── consumer_helpers.sql             # Custom consumer macros
│   │   └── api_format.sql                   # JSON formatting helpers
│   └── tests/
│       └── consumer_assertions.sql          # Consumer-specific tests
├── documentation/
│   ├── consumer_guide.md             # Consumer onboarding guide
│   └── query_examples.sql            # Example queries for each use case
└── dag/
    └── consumer_pipeline.yml         # Airflow DAG for consumer refresh
```

## Consumer Patterns

This skill implements 4 core consumer-aligned patterns:

### 1. Denormalized Wide Tables

**When to use:** Reporting, dashboards, BI tools that prefer flat structures

**Pattern:**
```sql
-- Flatten multiple domain entities into a single wide table
-- Example: Employee with Organization, Position, and Manager details

{{ config(
    materialized='view',
    description='Denormalized employee view for reporting'
) }}

SELECT
    -- Employee core
    e.employee_id,
    e.employee_name,
    e.employee_email,
    
    -- Organization details (flattened)
    o.organization_name,
    o.organization_code,
    o.organization_level,
    
    -- Position details (flattened)
    p.position_title,
    p.position_level,
    p.position_family,
    
    -- Manager details (flattened)
    m.employee_name AS manager_name,
    m.employee_email AS manager_email,
    
    -- Metadata
    e.effective_date,
    e.expiration_date
    
FROM {{ ref('canonical_employee') }} e
LEFT JOIN {{ ref('canonical_organization') }} o
    ON e.organization_id = o.organization_id
LEFT JOIN {{ ref('canonical_position') }} p
    ON e.position_id = p.position_id
LEFT JOIN {{ ref('canonical_employee') }} m
    ON e.manager_id = m.employee_id
WHERE e.is_current = TRUE
```

**Key characteristics:**
- One row per primary entity (e.g., employee)
- All related entities joined and flattened
- Prefixed column names to avoid collisions (e.g., `manager_name` vs `employee_name`)
- Current records only (no history for reporting)
- Materialized as VIEW (no storage cost, always fresh)

### 2. Pre-Aggregated Summaries

**When to use:** Dashboards, KPI tracking, metrics reporting with GROUP BY dimensions

**Pattern:**
```sql
-- Pre-aggregate metrics by dimensions
-- Example: Employee counts by organization, position level, month

{{ config(
    materialized='table',
    description='Monthly employee headcount by organization and level'
) }}

SELECT
    DATE_TRUNC('month', effective_date) AS month,
    organization_name,
    position_level,
    
    -- Aggregated metrics
    COUNT(DISTINCT employee_id) AS employee_count,
    COUNT(DISTINCT CASE WHEN is_active = TRUE THEN employee_id END) AS active_count,
    COUNT(DISTINCT CASE WHEN is_manager = TRUE THEN employee_id END) AS manager_count,
    
    -- Calculated metrics
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN is_manager = TRUE THEN employee_id END) 
        / NULLIF(COUNT(DISTINCT employee_id), 0), 2) AS manager_ratio_pct,
    
    -- Metadata
    CURRENT_TIMESTAMP() AS last_updated
    
FROM {{ ref('denorm_employee_details') }}
WHERE effective_date >= '2020-01-01'
GROUP BY 1, 2, 3
```

**Key characteristics:**
- GROUP BY on reporting dimensions (time, org, level, etc.)
- Aggregated metrics (COUNT, SUM, AVG, etc.)
- Calculated metrics (ratios, percentages)
- Materialized as TABLE (faster query performance)
- Incremental strategy optional for large datasets

### 3. Time-Series Rollups

**When to use:** Trend analysis, forecasting, time-based reporting

**Pattern:**
```sql
-- Time-series rollup with multiple granularities
-- Example: Daily, weekly, monthly employee metrics

{{ config(
    materialized='table',
    description='Time-series employee metrics with multiple granularities',
    partition_by={
        'field': 'metric_date',
        'data_type': 'date',
        'granularity': 'day'
    }
) }}

WITH daily_snapshot AS (
    SELECT
        DATE(effective_date) AS metric_date,
        COUNT(DISTINCT employee_id) AS headcount,
        SUM(salary_amount) AS total_compensation
    FROM {{ ref('canonical_employee') }}
    WHERE is_current = TRUE
    GROUP BY 1
),

rolling_aggregates AS (
    SELECT
        metric_date,
        headcount,
        total_compensation,
        
        -- 7-day rolling average
        AVG(headcount) OVER (
            ORDER BY metric_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS headcount_7d_avg,
        
        -- 30-day rolling average
        AVG(headcount) OVER (
            ORDER BY metric_date 
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS headcount_30d_avg,
        
        -- Month-over-month change
        headcount - LAG(headcount, 30) OVER (ORDER BY metric_date) AS headcount_mom_change,
        
        -- Percent change
        ROUND(100.0 * (headcount - LAG(headcount, 30) OVER (ORDER BY metric_date)) 
            / NULLIF(LAG(headcount, 30) OVER (ORDER BY metric_date), 0), 2) AS headcount_mom_pct
        
    FROM daily_snapshot
)

SELECT * FROM rolling_aggregates
```

**Key characteristics:**
- Time dimension is primary key (date, week, month)
- Rolling windows (7-day, 30-day averages)
- Period-over-period comparisons (MoM, YoY)
- Window functions for trends
- Partitioned by date for efficient querying

### 4. API-Friendly Formats

**When to use:** REST APIs, microservices, JSON exports, external integrations

**Pattern:**
```sql
-- API-friendly format with clean column names and null handling
-- Example: Employee API endpoint with nested JSON structure

{{ config(
    materialized='view',
    description='API-friendly employee data with JSON structure'
) }}

SELECT
    -- Clean, camelCase column names for APIs
    employee_id AS employeeId,
    employee_name AS employeeName,
    employee_email AS employeeEmail,
    
    -- Nested JSON for related entities
    STRUCT(
        organization_id AS organizationId,
        organization_name AS organizationName,
        organization_code AS organizationCode
    ) AS organization,
    
    STRUCT(
        position_title AS title,
        position_level AS level,
        position_family AS family
    ) AS position,
    
    -- Null handling (APIs prefer empty strings over NULL)
    COALESCE(phone_number, '') AS phoneNumber,
    COALESCE(office_location, '') AS officeLocation,
    
    -- Boolean conversion (TRUE/FALSE instead of 1/0)
    CASE WHEN is_active = TRUE THEN 'true' ELSE 'false' END AS isActive,
    CASE WHEN is_manager = TRUE THEN 'true' ELSE 'false' END AS isManager,
    
    -- ISO 8601 date format
    DATE_FORMAT(effective_date, 'yyyy-MM-dd') AS effectiveDate,
    
    -- Metadata
    CURRENT_TIMESTAMP() AS lastUpdated
    
FROM {{ ref('denorm_employee_details') }}
WHERE is_current = TRUE
```

**Key characteristics:**
- camelCase column names (not snake_case)
- Nested STRUCT for related entities (JSON-friendly)
- Null handling (COALESCE to empty strings)
- Boolean as string ('true'/'false')
- ISO 8601 date format
- Materialized as VIEW (real-time API data)

## How to Execute

### Step 1: Identify Consumer Personas and Use Cases

Ask the user:
1. **Who are the consumers?** (teams, roles, systems)
2. **What are their use cases?** (reporting, dashboards, APIs, exports)
3. **What questions do they need to answer?** (KPIs, trends, drill-downs)
4. **What format do they prefer?** (flat table, nested JSON, time-series)

If `catalyst-triage-docs` was run, reference the Consumer Use Case Map.

### Step 2: Identify Source Canonical Tables

Ask the user:
- Which domain-aligned canonical tables should be used as sources?
- Are these tables in Unity Catalog? (verify with `discover-data`)
- What are the join keys between entities?

Common source patterns:
- Single canonical table → Consumer views with different filters/aggregations
- Multiple canonical tables → Denormalized joins across entities

### Step 3: Design Consumer Schema

For each consumer use case, determine the pattern:

| Use Case | Pattern | Materialization |
|----------|---------|-----------------|
| Executive dashboard (KPIs) | Pre-Aggregated Summary | table |
| Analyst drill-down reporting | Denormalized Wide Table | view |
| Trend analysis / forecasting | Time-Series Rollup | table (partitioned) |
| REST API / microservice | API-Friendly Format | view |
| BI tool (Tableau, PowerBI) | Denormalized Wide Table | view |
| Data export / file transfer | Denormalized Wide Table | table |

Invoke `data-modeling` skill if complex schema design is needed.

### Step 4: Generate Consumer Views

For each consumer use case, generate the appropriate dbt model using patterns above.

**File naming convention:**
- `consumers/rpt_<domain>_<use_case>.sql` (reporting tables)
- `consumers/api_<domain>_<entity>.sql` (API endpoints)
- `consumers/agg_<domain>_<grain>.sql` (aggregated summaries)
- `consumers/ts_<domain>_<metric>.sql` (time-series rollups)

**Example structure:**
```
models/consumers/
├── rpt_employee_directory.sql       # Denormalized employee listing
├── agg_employee_headcount_monthly.sql  # Monthly headcount by org/level
├── ts_employee_growth_daily.sql     # Daily headcount trend
└── api_employee_details.sql         # API endpoint for employee lookup
```

### Step 5: Add Tests and Documentation

Generate `schema.yml` with:

**Tests:**
- `not_null` on key consumer-facing columns
- `unique` on primary keys
- `accepted_values` for categorical dimensions
- `relationships` to verify join integrity with source canonical tables
- Custom assertions for consumer-specific business rules

**Documentation:**
- Description of each consumer view (purpose, use case, consumers)
- Column descriptions focused on business meaning (not technical details)
- Example queries for common consumer questions

### Step 6: Generate Consumer Macros (if needed)

For repeated consumer patterns, generate helper macros:

**Example: API JSON formatting macro**
```sql
{% macro to_api_json(table_name, key_columns, value_columns) %}
    SELECT
        {{ key_columns | join(', ') }},
        TO_JSON(STRUCT(
            {% for col in value_columns %}
            {{ col }}{% if not loop.last %},{% endif %}
            {% endfor %}
        )) AS json_payload
    FROM {{ ref(table_name) }}
{% endmacro %}
```

### Step 7: Generate DAG for Consumer Refresh

Generate Airflow DAG YAML that:
- Depends on source canonical table refreshes
- Refreshes consumer views in dependency order
- Includes data quality checks
- Notifies consumers on failures

Use `catalyst-dag-yaml` skill for DAG generation.

### Step 8: Generate Consumer Onboarding Guide

Create `consumer_guide.md` with:
- Overview of available consumer views
- Access instructions (how to query)
- Schema documentation
- Example queries for each use case
- Performance tips (materialized tables vs views)
- Support contact information

### Step 9: Validate and Test

1. **Validate SQL syntax:**
   - Run `dbt compile` to verify SQL correctness
   - Check for column name collisions in joins
   - Verify aggregation logic

2. **Test data quality:**
   - Run `dbt test` to verify tests pass
   - Check row counts match expectations
   - Verify join results (no unexpected NULLs)

3. **Performance testing:**
   - Measure query response time on consumer views
   - If > 5 seconds, recommend materialization as table
   - Suggest partitioning for large time-series tables

4. **Consumer UAT:**
   - Share views with actual consumers for validation
   - Verify views answer their questions
   - Collect feedback on column names, formats, performance

### Step 10: Deploy to Databricks (Optional)

If user wants to run against Databricks:
1. Generate dbt project structure with profiles.yml
2. Run `dbt run` to materialize consumer views
3. Run `dbt test` to verify data quality
4. Query sample data to confirm output format

## Example Output

**User:** "I need consumer views for the ESG Sustainability Metrics product. Consumers are: Compliance team (dashboard), Portfolio Analytics (API), and Executive reporting (monthly KPIs)"

**Skill:**

**Step 1: Identify use cases:**
- Compliance team: Dashboard showing current ESG ratings and violations
- Portfolio Analytics: API endpoint for ESG score lookup by company
- Executive reporting: Monthly aggregated ESG metrics by sector and rating

**Step 2: Identify sources:**
- `canonical_esg.company` (company master)
- `canonical_esg.esg_rating` (current ratings)
- `canonical_esg.carbon_footprint` (emissions data)

**Step 3: Design schemas:**
- Compliance dashboard → Denormalized Wide Table
- Portfolio API → API-Friendly Format
- Executive KPIs → Pre-Aggregated Summary

**Step 4: Generate 3 consumer views:**

1. `rpt_esg_compliance_dashboard.sql` (Denormalized):
```sql
-- Denormalized ESG view for compliance dashboard
SELECT
    c.company_id,
    c.company_name,
    c.ticker_symbol,
    c.sector,
    c.industry,
    
    -- ESG ratings (flattened)
    r.overall_rating,
    r.environmental_score,
    r.social_score,
    r.governance_score,
    r.rating_date,
    r.rating_agency,
    
    -- Carbon footprint (flattened)
    cf.scope1_emissions,
    cf.scope2_emissions,
    cf.scope3_emissions,
    cf.total_emissions,
    cf.emissions_year,
    
    -- Compliance flags
    CASE WHEN r.overall_rating < 'BBB' THEN TRUE ELSE FALSE END AS is_below_threshold,
    CASE WHEN cf.total_emissions > 10000 THEN TRUE ELSE FALSE END AS is_high_emitter,
    
    CURRENT_TIMESTAMP() AS last_updated
    
FROM {{ ref('canonical_company') }} c
LEFT JOIN {{ ref('canonical_esg_rating') }} r
    ON c.company_id = r.company_id AND r.is_current = TRUE
LEFT JOIN {{ ref('canonical_carbon_footprint') }} cf
    ON c.company_id = cf.company_id AND cf.is_current = TRUE
WHERE c.is_active = TRUE
```

2. `api_esg_company_lookup.sql` (API-Friendly):
```sql
-- API endpoint for ESG data lookup
SELECT
    company_id AS companyId,
    company_name AS companyName,
    ticker_symbol AS tickerSymbol,
    
    STRUCT(
        overall_rating AS overallRating,
        environmental_score AS environmentalScore,
        social_score AS socialScore,
        governance_score AS governanceScore,
        DATE_FORMAT(rating_date, 'yyyy-MM-dd') AS ratingDate
    ) AS esgRating,
    
    STRUCT(
        total_emissions AS totalEmissions,
        scope1_emissions AS scope1Emissions,
        scope2_emissions AS scope2Emissions,
        emissions_year AS emissionsYear
    ) AS carbonFootprint,
    
    DATE_FORMAT(CURRENT_TIMESTAMP(), "yyyy-MM-dd'T'HH:mm:ss'Z'") AS lastUpdated
    
FROM {{ ref('rpt_esg_compliance_dashboard') }}
```

3. `agg_esg_monthly_metrics.sql` (Pre-Aggregated):
```sql
-- Monthly ESG metrics for executive reporting
SELECT
    DATE_TRUNC('month', rating_date) AS month,
    sector,
    
    COUNT(DISTINCT company_id) AS company_count,
    AVG(environmental_score) AS avg_environmental_score,
    AVG(social_score) AS avg_social_score,
    AVG(governance_score) AS avg_governance_score,
    SUM(total_emissions) AS total_emissions,
    
    COUNT(DISTINCT CASE WHEN overall_rating >= 'A' THEN company_id END) AS high_rating_count,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN overall_rating >= 'A' THEN company_id END) 
        / NULLIF(COUNT(DISTINCT company_id), 0), 2) AS high_rating_pct,
    
    CURRENT_TIMESTAMP() AS last_updated
    
FROM {{ ref('rpt_esg_compliance_dashboard') }}
WHERE rating_date >= '2020-01-01'
GROUP BY 1, 2
```

**Step 5: Generate schema.yml with tests:**
- `rpt_esg_compliance_dashboard`: 8 not_null tests, 1 unique test on company_id, relationships to canonical tables
- `api_esg_company_lookup`: unique on companyId
- `agg_esg_monthly_metrics`: not_null on month/sector

**Step 6: Generate consumer guide:**
- Access: Query Unity Catalog `cspn_cons2_dev.esg_consumers.*`
- 3 views documented with use cases
- Example queries for each consumer persona

**Skill confirms:**
```
✅ Consumer views generated!

**Consumer Products:**
1. rpt_esg_compliance_dashboard (Denormalized)
   - Consumers: Compliance team
   - Use case: Dashboard with current ratings and violations
   - Materialization: view (real-time)
   - Columns: 18 (company + ratings + carbon + flags)

2. api_esg_company_lookup (API-Friendly)
   - Consumers: Portfolio Analytics
   - Use case: REST API for ESG lookup
   - Materialization: view (real-time)
   - Format: JSON with nested structures

3. agg_esg_monthly_metrics (Pre-Aggregated)
   - Consumers: Executive reporting
   - Use case: Monthly KPI dashboard
   - Materialization: table (faster queries)
   - Granularity: month + sector
   - Metrics: 8 aggregated KPIs

**Artifacts Created:**
- dbt/models/consumers/ (3 consumer views)
- dbt/models/schema.yml (tests + documentation)
- documentation/consumer_guide.md (onboarding guide)
- documentation/query_examples.sql (example queries)

**Next Steps:**
1. Review consumer views with actual consumers
2. Run dbt build to materialize in Databricks
3. Proceed to catalyst-validate for UAT sign-off
4. Deploy with catalyst-publish
```

## Related Skills

- **Previous Phase:** `catalyst-design-docs` (Phase 3) — Consumer schema design
- **Parallel Phase:** `source-aligned`, `domain-aligned` (Phase 4: Build) — Source/domain pipelines
- **Next Phase:** `catalyst-validate-docs` (Phase 5) — UAT and DQ validation
- **Supporting Skills:**
  - `hourglass-dbt-model` — For dbt model patterns and configuration
  - `data-modeling` — For complex consumer schema design
  - `catalyst-dag-yaml` — For consumer refresh DAG generation
  - `discover-data` — For source canonical table discovery

## Prerequisites

- `catalyst-triage` (recommended) — Identifies consumer personas and use cases
- `catalyst-design` (recommended) — Defines consumer schema requirements
- Domain-aligned canonical tables in Unity Catalog (from `domain-aligned` or existing)

## Template References

**RFD2 Templates:**
- *(planned — not yet created)*

**RFD2 Commands (Claude Code):**
- *(planned — not yet created)*

## Notes

- **Consumer views should be simple** — Flatten complexity, hide technical details
- **Materialization strategy matters** — Views for real-time, tables for performance
- **Naming is critical** — Use business-friendly column names, not technical IDs
- **Test with actual consumers** — Don't assume what they need, validate with UAT
- **Performance first** — If query takes > 5 seconds, materialize as table
- **Partition large tables** — Time-series tables should be partitioned by date
- **Document everything** — Consumer guide is as important as the views themselves
- **API format is different** — camelCase, nested JSON, no NULLs, ISO dates
- **Aggregations reduce cost** — Pre-aggregate if consumers always GROUP BY same dimensions
- **Incremental strategy for large views** — If view has millions of rows, use incremental materialization
