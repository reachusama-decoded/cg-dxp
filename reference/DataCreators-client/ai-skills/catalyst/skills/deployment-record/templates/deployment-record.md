---
phase: "6 - Publish"
artifact: "Deployment Record"
data_product: "[Product Name]"
date: "YYYY-MM-DD"
---

# Deployment Record

## Deployment Summary

| Field                | Detail                                      |
| -------------------- | ------------------------------------------- |
| Version / Commit     | [e.g., v1.2.0 / abc1234]                   |
| Deployed By          | [Name / Team]                               |
| Deployment Date/Time | [YYYY-MM-DD HH:MM TZ]                      |
| Target Environment   | [e.g., Production, Staging]                 |
| Deployment Method    | [e.g., CI/CD pipeline, manual, blue-green]  |

## Pre-Deployment Checklist

| # | Item                                                        | Done |
|---|-------------------------------------------------------------|------|
| 1 | Data contract reviewed and up to date                       | [ ]  |
| 2 | Quality gate criteria met (tests passing, scans clean)      | [ ]  |
| 3 | Infrastructure provisioned and validated                    | [ ]  |
| 4 | Access controls and entitlements configured                 | [ ]  |
| 5 | Monitoring and alerting configured                          | [ ]  |
| 6 | Rollback plan documented and tested                         | [ ]  |
| 7 | Downstream consumers notified (if applicable)               | [ ]  |
| 8 | Data sensitivity and criticality classifications confirmed  | [ ]  |

## Deployment Steps

| Step | Action                              | Status   | Notes |
|------|-------------------------------------|----------|-------|
| 1    | [Describe step]                     | [status] |       |
| 2    | [Describe step]                     | [status] |       |
| 3    | [Describe step]                     | [status] |       |

## Post-Deployment Verification

| Verification                          | Result  | Notes |
|---------------------------------------|---------|-------|
| Smoke tests passed                    | [Y/N]   |       |
| Data freshness within SLA             | [Y/N]   |       |
| Data completeness validated           | [Y/N]   |       |
| Availability confirmed                | [Y/N]   |       |
| Consumer access verified              | [Y/N]   |       |
| Quality score at or above threshold   | [Y/N]   |       |

## Rollback Plan

| Field              | Detail                                         |
|--------------------|-------------------------------------------------|
| Rollback Trigger   | [Conditions that warrant rollback]              |
| Rollback Procedure | [Steps to revert to previous state]             |
| Rollback Owner     | [Name / Team]                                   |
| Estimated Duration | [Time to complete rollback]                     |
| Last Tested        | [Date rollback was last validated]              |

## Issues Encountered

| # | Issue Description | Severity | Resolution | Impact |
|---|-------------------|----------|------------|--------|
|   |                   |          |            |        |

## Sign-Off

| Role              | Name | Date | Approved |
|-------------------|------|------|----------|
| Product Owner     |      |      | [ ]      |
| Engineering Lead  |      |      | [ ]      |
| DataOps Lead      |      |      | [ ]      |
