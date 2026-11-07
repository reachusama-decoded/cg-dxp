---
authors: DMRS
state: published
discussion: https://github.com/cg-open-itg/catalyst/pull/132
labels: testing, quality, ai-assisted, data-engineering, guardrails
---

# RFD 0018 Data Engineering Testing Strategy

## Objectives

This testing strategy establishes a comprehensive, AI-assisted approach to testing investment data pipelines that ensures quality, enables confident refactoring, and accelerates delivery across federated teams. As investment data pipelines expand across lakehouse platforms and teams, this strategy provides the foundation for:

**Quality & Reliability**
- **Prevent production incidents** through comprehensive test coverage that validates data correctness before deployment
- **Enable safe refactoring** with regression test suites that provide confidence when modifying pipelines
- **Maintain consistent quality standards** across all teams building data products

**Velocity & Efficiency**
- **Accelerate development** by automating test generation using AI, reducing manual test authoring effort
- **Speed up PR reviews** through automated test coverage validation and quality checks
- **Reduce cognitive load** by providing clear patterns and reusable templates for common testing scenarios

**Platform Confidence**
- **Enable fearless platform upgrades** with regression test suites that validate runtime and framework changes before production rollout
- **Support infrastructure evolution** by providing fast validation mechanisms for platform-wide changes
- **Facilitate scaling** as more engineers contribute to data pipelines across the organization

**Core Principles**

This strategy delivers on these objectives by:
1. **Defining clear standards** for what constitutes adequate test coverage for data products
2. **Codifying testing patterns** specific to data engineering (not generic software testing)
3. **Automating test generation** using AI to reduce friction and ensure consistency
4. **Ensuring availability of quality test data** — representative fixtures, sample datasets, and production-like test environments
5. **Enforcing guardrails** so every data engineer follows the same quality bar
6. **Integrating with the Data Product Lifecycle** (RFD 0002) as gate requirements at each phase

## Background

### Symptoms of Low Maturity Testing Practices

Without a comprehensive testing strategy, data engineering organizations typically exhibit these patterns:

- **Manual test authoring** — engineers create tests from scratch using inconsistent patterns, leading to varying test quality and coverage approaches across teams
- **Unclear coverage standards** — teams lack clarity on what constitutes "sufficient" test coverage for different data product types, resulting in either over-testing or under-testing
- **Limited test data availability** — engineers resort to overly simplistic fixtures that don't represent real-world complexity; performance testing and integration testing are frequently skipped due to lack of production-like test datasets
- **Documentation-driven testing** — test reports (`unit-test-report.md`, `integration-test-report.md`) record results after the fact rather than driving test-driven development from design artifacts
- **Absence of test generation automation** — no tooling to generate executable test code from data contracts, transformation specs, or business logic, forcing engineers to write every test manually
- **Reinvented patterns** — common test scenarios (row count checks, schema validation, referential integrity, business rule validation) are recreated rather than reused from battle-tested templates

These symptoms lead to production incidents that testing could have caught, regression anxiety when refactoring, slow PR reviews due to manual validation, and hesitation to upgrade platforms without extensive manual testing.

### Test Categories by Data Product Lifecycle Phase

Data engineering testing differs from traditional software testing. The following test categories are organized by the DPLC phase where they are typically executed:

**Phase 4 (Build) — Core Testing**
- **Unit Tests** — Individual functions/transformations in isolation (Python UDFs, SQL functions)
- **Integration Tests** — Interactions between pipeline components (source → staging → curated)
- **Schema Tests** — Structure, types, nullability validation (dbt schema tests)
- **Transformation Logic Tests** — SQL/PySpark business logic correctness
- **Referential Integrity Tests** — Cross-table relationships and foreign key validation
- **Idempotency Tests** — Re-running same job produces same output
- **Incremental Load Tests** — Incremental processing matches full-refresh baseline
- **Observability Tests** — Monitoring, logging, and alerting configuration validation

**Phase 4 (Build) — Specialized Testing**
- **Reconciliation Tests** — Data consistency across systems (row counts, checksums, control totals)
- **Reference Data Validation** — Lookup/dimension table integrity
- **Performance Tests** — SLA compliance (latency, throughput)
- **Scalability Tests** — Pipeline handles data volume growth
- **Security & Compliance Tests** — PII masking, access controls, audit trails

**Phase 6 (Publish) — Deployment Validation**
- **End-to-End (E2E) Tests** — Complete pipeline from source to consumption with production-like data
- **Timeliness & SLA Tests** — Data available when consumers need it
- **Historical Consistency Tests** — Temporal integrity for bi-temporal models

**Phase 7 (Operate) & Phase 8 (Evolve) — Ongoing Validation**
- **Regression Tests** — Existing pipelines still work after platform/code changes
- **Lineage & Impact Tests** — Track data dependencies and downstream impact before changes

Engineers need patterns and AI-assisted tooling for all these categories, not just generic unit tests. Detailed guidance for each phase is provided in Section 2.

### Integration with Data Product Lifecycle (RFD 0002)

Testing must be integrated throughout the entire lifecycle, not just in Build and Validate phases. The table below maps testing activities to each lifecycle phase:

| Phase | Testing Activity | Artifacts & Deliverables |
|-------|-----------------|--------------------------|
| **Phase 0: Pre-requisite** | Verify testing capability exists | Testing infrastructure, CI/CD pipelines, test environments available |
| **Phase 1: Triage** | Assess product scope and criticality | Document scope, consumers, and data sensitivity in demand tracker |
| **Phase 2: Discovery** | Define test scope and test data strategy | Assess transformation complexity; define test data strategy (synthetic vs production-like); document in feasibility report |
| **Phase 3: Design** | Define test strategy and plan | Create test-plan.md with test categories, coverage targets, acceptance criteria; define data contract with testable SLAs |
| **Phase 4: Build** | Implement and execute tests | Generate tests via AI skills; implement unit, integration, E2E tests; execute tests in CI/CD; produce test reports |
| **Phase 5: Validate** | Test sign-off and governance review | UAT testing by data owners; formal test coverage and quality sign-off |
| **Phase 6: Publish** | Production smoke tests | Execute smoke tests post-deployment; confirm monitoring/alerting works; validate consumer access |
| **Phase 7: Operate** | Continuous monitoring & regression testing | Monitor SLAs; run periodic regression tests; track incidents; validate fixes with tests |
| **Phase 8: Evolve** | Impact assessment testing | Test breaking changes; validate backward compatibility; assess downstream impact before schema changes |

**Key capabilities enabled by this RFD:**
- **Upfront test planning** (Phase 3 Design) — test-plan.md artifact defines what will be tested before code is written
- **Automated test generation** from design artifacts (data contracts, transformation specs) via AI skills
- **CI/CD enforcement** with tests as automated gates and coverage thresholds

### AI-Driven Test Generation Opportunity

Large language models excel at generating test code from specifications:
- Given a **data contract** → generate schema validation tests
- Given a **transformation spec** → generate transformation logic unit tests
- Given **example data** → infer edge cases and generate test fixtures

The Catalyst skills framework provides the infrastructure to operationalize this through skills that:
1. **Parse upstream artifacts** (data contracts, transformation specs, data models)
2. **Generate executable test code** (dbt schema tests, transformation logic tests, PySpark unit tests)
3. **Scaffold test fixtures** (sample input data, expected output data)
4. **Run tests and report results** (integrate with CI/CD pipelines)

### Strategic Context

This testing strategy supports key organizational initiatives:
- **Federated data product teams** — provide consistent quality standards as teams scale across the organization
- **Lakehouse democratization** — enable more engineers to confidently build production pipelines with testing guardrails
- **Investment data evolution** — support increasing complexity (real-time feeds, cross-domain models) with comprehensive validation
- **Regulatory compliance** — provide audit trails demonstrating data validation and quality controls
- **Platform modernization** — enable confident runtime and framework upgrades (Databricks, dbt, Spark) with regression validation
- **Growth platform initiatives** — facilitate repository consolidations and framework migrations with proof that business logic is preserved
- **Catalyst adoption** provides the AI skills infrastructure to make this practical

## Proposal

This testing strategy is organized by **Data Product Lifecycle phases** (Phase 0 through Phase 8). Each phase defines testing activities, skills to use, gate criteria, and artifacts. Platform regression testing (separate from the standard lifecycle) is covered at the end.

### 1. Testing Standards Overview

All data products must implement tests from applicable categories based on complexity, business criticality, and data sensitivity (see Background section for 15 test categories).

#### Test Data Strategy

Match test data realism to the test objective — synthetic data for logic testing, masked production data for realistic patterns and scale testing.

##### Test Data Type Definitions

Three distinct test data types are used in this strategy. These are **not interchangeable** — each serves different testing purposes:

| Test Data Type | Description | Key Characteristics | When to Use |
|----------------|-------------|---------------------|-------------|
| **Synthetic (AI-Generated)** | Fabricated data created by AI based on schema and business rules — **NO production data involved** | Designed to exercise all code paths; includes edge cases that may not exist in production; fast generation; no data access constraints | Unit tests, schema tests, transformation logic tests, edge case testing, idempotency tests |
| **Masked Production Data** | Real production data with PII/sensitive fields masked, anonymized, or format-preserving encrypted | Retains realistic distributions, cardinality, and data patterns; PII/sensitive fields protected per InfoSec policy; **distinct from synthetic generation** | Integration tests, reconciliation tests (baseline validation), establishing test baselines for comparison, E2E tests |
| **Production-Like (Full Volume, Masked)** | Full production data volumes with PII/sensitive fields masked | Realistic scale testing; represents actual data volumes and complexity; requires significant storage/compute | Performance tests, scalability tests, E2E tests (for performance-critical products), regression tests (full validation mode) |
| **Production (Live, Restricted Access)** | Actual production data with no modifications | Real operational data; highest access restrictions; audit trail required | Production smoke tests (Phase 6 Publish), post-deployment validation, incident investigation |

---

## 2. Data Product Lifecycle Testing Strategy

### Testing Maturity: Current State vs. Target State

This RFD establishes a mature, systematic approach to data pipeline testing that contrasts sharply with our current ad-hoc practices.

#### Current State (Low Maturity)

Our current testing approach exhibits these characteristics:

**Reactive & Inconsistent**
- Tests written after code is complete (if at all)
- No standardized test categories or coverage requirements
- Each engineer decides what "sufficient testing" means
- Testing scope varies dramatically by team and individual

**Manual & Time-Consuming**
- Engineers write all test code from scratch
- No AI-assisted test generation
- Test fixtures manually created with unrealistic simplistic data
- Production-like test data unavailable due to access/masking challenges

**Disconnected from Lifecycle**
- Testing happens primarily in Build phase only
- No upfront test planning during Design phase
- No regression testing for enhancements or platform changes
- Impact assessment for changes lacks test validation strategy

**Limited Visibility & Enforcement**
- No automated coverage tracking or enforcement
- Test results recorded in static documents after execution
- PRs merged without minimum coverage requirements
- No distinction between testing strategies for new features vs. enhancements vs. defects

**Result:** Production incidents, regression anxiety, slow refactoring, inconsistent quality across teams, hesitation to upgrade platforms.

#### Target State (Mature Testing)

This RFD establishes these mature testing practices:

**Proactive & Standardized**
- Test planning begins in Design phase (Phase 3) with test-plan.md artifact
- Clear test categories with coverage requirements defined per product type
- Standardized patterns library for all common testing scenarios
- Test scope explicitly defined based on pipeline work type (new feature | enhancement | defect fix)

**Automated & Efficient**
- AI skills generate test code from data contracts and transformation specs
- Synthetic test fixtures generated automatically with edge case coverage
- Production-sample procurement automated with PII masking
- Test execution integrated into CI/CD with automated coverage reporting

**Integrated Throughout Lifecycle**
- **Phase 0-1:** Infrastructure readiness and scope assessment
- **Phase 2:** Test scope and test data strategy defined upfront
- **Phase 3:** Comprehensive test plan created before coding begins
- **Phase 4:** AI-generated tests implemented and executed
- **Phase 5:** Formal test sign-off with coverage validation
- **Phase 6:** Production smoke tests post-deployment
- **Phase 7:** Continuous regression testing during operations
- **Phase 8:** Impact assessment includes test validation for downstream consumers

**Enforced & Traceable**
- Pre-commit hooks and CI/CD gates enforce minimum coverage thresholds
- Test results tracked throughout lifecycle phases with explicit traceability
- Testing strategy differentiated by work type (new | enhancement | defect)
- Automated PR review validates test quality and coverage
- Requirements traced from Phase 1 (Triage) → Phase 8 (Evolve) with test validation at each gate

**Result:** Confident deployments, safe refactoring, fast PR reviews, consistent quality, fearless platform upgrades, clear traceability.

---

### Traceability Framework

Testing requirements and artifacts must be traceable throughout the entire lifecycle — from initial scope assessment (Phase 1) to production evolution (Phase 8). This traceability ensures:

- **Requirements → Tests:** Business requirements documented in Triage phase are validated by tests in Build phase
- **Design → Implementation:** Test plans created in Design phase drive test implementation in Build phase
- **Tests → Sign-off:** Test execution results in Build phase inform UAT sign-off in Validate phase
- **Production → Evolution:** Baseline tests established in Publish phase are reused as regression tests in Evolve phase

The table below shows traceability linkages across phases:

| Phase | Testing Artifact | Traces From | Traces To | Purpose |
|-------|-----------------|-------------|-----------|---------|
| **Phase 1: Triage** | Demand tracker (scope, consumers, sensitivity) | — | Phase 2 test data strategy | Informs test scope and data access requirements |
| **Phase 2: Discovery** | Test data strategy (synthetic vs production-like) | Phase 1 scope/sensitivity | Phase 3 test plan | Defines feasibility of test data procurement |
| **Phase 3: Design** | test-plan.md | Phase 2 test data strategy | Phase 4 test implementation | Specifies what will be tested and with what data |
| **Phase 3: Design** | data-contract.md (testable SLAs) | Phase 1 consumer requirements | Phase 4 test generation | Defines acceptance criteria for automated tests |
| **Phase 4: Build** | Test code & fixtures | Phase 3 test plan | Phase 5 UAT sign-off | Implements tests per design plan |
| **Phase 4: Build** | unit-test-report.md, integration-test-report.md | Phase 3 test plan | Phase 5 sign-off | Evidence of test execution and coverage |
| **Phase 5: Validate** | uat-sign-off.md | Phase 4 test reports | Phase 6 deployment approval | Formal approval to deploy based on test results |
| **Phase 6: Publish** | Production smoke test results | Phase 4 test baseline | Phase 7 monitoring baselines | Establishes production baseline for ongoing monitoring |
| **Phase 7: Operate** | Incident logs with test gaps | Phase 4 test coverage | Phase 8 test plan updates | Identifies gaps for future test enhancements |
| **Phase 8: Evolve** | Regression test results | Phase 4 original tests | Phase 4 (next iteration) | Proves changes don't break existing functionality |
| **Phase 8: Evolve** | downstream-impact-assessment.md | Phase 1 consumer map | Phase 3 (downstream) test plans | Triggers test updates for impacted consumers |

This traceability matrix is referenced in each phase section below.

---

### Testing Strategy by Pipeline Work Type

Testing strategies must be explicitly differentiated based on the type of pipeline work being performed. The three primary work types are:

1. **New Features** — Net-new data pipelines, tables, or transformations that don't exist in production
2. **Enhancements** — Modifications to existing pipelines (new columns, changed logic, schema evolution)
3. **Defect Fixes** — Corrections to bugs or data quality issues in production pipelines

Each work type requires different testing emphasis, as detailed in each phase below:

| Work Type | Testing Emphasis | Key Considerations |
|-----------|-----------------|-------------------|
| **New Features** | Comprehensive test coverage from scratch; establish baseline for future regression | No existing tests to reuse; must define coverage thresholds; test data strategy critical |
| **Enhancements** | Regression tests (existing behavior preserved) + incremental tests (new behavior validated) | Reuse existing test fixtures; compare before/after behavior; validate backward compatibility |
| **Defect Fixes** | Root cause reproduction test + regression tests to prevent recurrence | Test must fail before fix, pass after fix; add to regression suite |

---

The following sections detail testing activities, skills, gate criteria, and artifacts for each phase of the Data Product Lifecycle (RFD 0002). Each phase includes:
- **Overview:** Purpose and general activities
- **Testing Strategy by Work Type:** Specific guidance for new features, enhancements, and defect fixes
- **Preparation for Next Phase:** Analysis, profiling, or artifacts needed to enable testing in subsequent phases
- **Traceability:** How this phase's testing artifacts link to previous and subsequent phases

### Phase 0: Pre-requisite — Testing Infrastructure Readiness

**Purpose:** Ensure testing infrastructure and capabilities exist before any data product development begins.

**Prerequisites:**
- CI/CD pipelines configured with test execution capability
- Test environments provisioned (dev, SQA) with production-like configuration
- Astro CLI installed for local Airflow DAG testing
- Testing patterns library available in Catalyst skills
- Test data management infrastructure:
  - Production sampling pipeline with PII masking capability
  - InfoSec approval process for production samples  
  - Test environment catalogs for storing masked samples
  - Production data access request process documentation

**Gate Criteria:**
- ✅ CI/CD pipelines operational with test execution steps
- ✅ Test environments accessible (dev, SQA)
- ✅ Astro CLI available for Airflow DAG development
- ✅ Test data infrastructure provisioned

**Artifacts:**
- CI/CD pipeline configuration
- Test environment access documentation
- Astro CLI setup guide
- Test data infrastructure runbook

#### Testing Strategy by Work Type

**All Work Types (New Features | Enhancements | Defect Fixes):**

Infrastructure prerequisites are **identical** regardless of work type. Testing infrastructure must be operational and accessible before any pipeline development work begins.

- **New Features:** Requires full testing infrastructure stack (CI/CD, test environments, test data management, patterns library)
- **Enhancements:** Same infrastructure requirements; may reuse existing test fixtures and test environment data
- **Defect Fixes:** Same infrastructure requirements; critical that CI/CD is operational to validate fixes before production deployment

**Why no differentiation:** Phase 0 is a platform-level prerequisite, not product-specific. All pipeline work depends on the same foundational capabilities.

#### Preparation for Next Phase (Phase 1: Triage)

Before proceeding to Triage, ensure:

- **Infrastructure validation:** Run a sample test pipeline end-to-end (synthetic fixture → test execution → CI/CD reporting) to confirm all components work
- **Access verification:** Confirm engineers can access test environments and execute tests locally (Astro CLI functional)
- **Documentation review:** Ensure testing standards document and patterns library are published and accessible
- **Training readiness:** Confirm engineers know where to find testing resources and how to request test data access

**Deliverable for Phase 1:** Infrastructure readiness checklist signed off by platform team, confirming all capabilities are operational.

#### Traceability

| Traces From | Traces To | Artifact/Linkage |
|-------------|-----------|------------------|
| — (foundational phase) | Phase 2 test data strategy | Test data infrastructure capabilities inform feasibility |
| — | Phase 4 test execution | CI/CD and test environment availability enables test runs |
| — | All phases | Patterns library and standards document guide testing throughout lifecycle |

---

### Phase 1: Triage — Product Scope Assessment

**Purpose:** Assess product scope, consumers, and data sensitivity to inform test planning.

**Activities:**
- Review product scope, consumers, data sensitivity, and business impact
- Document product characteristics in demand tracker entry
- Identify downstream consumers (informs test planning in later phases)
- Assess regulatory/compliance requirements
- Identify data sensitivity (PII, sensitive financial data, etc.)

**Gate Criteria:**
- ✅ Product scope documented in demand tracker
- ✅ Consumers and use cases identified
- ✅ Data sensitivity assessment completed
- ✅ Downstream consumers identified

**Artifacts:**
- Demand tracker entry with product characteristics
- Consumer use case map (identifies testing scope for downstream impact)

#### Testing Strategy by Work Type

Testing scope assessment differs significantly by work type:

**New Features:**
- **Scope:** Comprehensive assessment required — no existing tests or baselines to reference
- **Consumers:** Identify all downstream consumers (reports, APIs, ML models, other pipelines)
- **Sensitivity:** Full PII/sensitivity assessment needed to determine test data strategy
- **Criticality:** Assess business impact to determine test coverage requirements (e.g., financial data = higher coverage thresholds)
- **Complexity:** Document transformation complexity to inform test categories (simple SQL = unit tests sufficient; complex multi-stage = integration + E2E tests required)

**Enhancements:**
- **Scope:** Document what's changing (new columns, changed logic, schema evolution) and what remains unchanged
- **Consumers:** Review existing consumer use case map; identify if enhancement impacts downstream consumers (triggers Phase 8 impact assessment for consumers)
- **Sensitivity:** Re-assess if enhancement introduces new PII fields or changes data classification
- **Regression risk:** Document areas of existing pipeline that must not break (informs regression test scope)
- **Backward compatibility:** Identify if change is breaking (requires consumer notification and downstream test updates)

**Defect Fixes:**
- **Scope:** Document root cause, impacted data, and time period affected
- **Consumers:** Identify which consumers were impacted by defect (may require data corrections)
- **Incident severity:** Assess production impact to prioritize fix urgency
- **Reproducibility:** Document steps to reproduce defect (informs test case creation in Phase 4)
- **Prevention:** Identify why existing tests missed this defect (informs test gap analysis)

**Why differentiation matters:** Test scope, data requirements, and coverage thresholds vary dramatically based on whether you're building net-new, enhancing existing, or fixing defects. This assessment drives all downstream testing decisions.

#### Preparation for Next Phase (Phase 2: Discovery)

Before proceeding to Discovery, prepare:

- **Consumer impact analysis:** For enhancements/defects, document which downstream consumers are affected (informs test data strategy in Phase 2)
- **Complexity assessment:** Rate transformation complexity (simple | moderate | complex) to guide test category selection in Phase 2
- **Data access scoping:** Identify if production data access will be required for testing (triggers InfoSec approval process in Phase 2)
- **Baseline identification:** For enhancements/defects, identify existing test baselines and coverage to reuse

**Deliverable for Phase 2:** Product characteristics summary with complexity rating, consumer impact assessment, and data sensitivity classification.

#### Traceability

| Traces From | Traces To | Artifact/Linkage |
|-------------|-----------|------------------|
| Phase 0 infrastructure readiness | Phase 2 test data strategy | Confirms test data infrastructure is available |
| Demand tracker (scope, consumers, sensitivity) | Phase 2 test data strategy | Informs synthetic vs production-like test data needs |
| Consumer use case map | Phase 3 test plan | Defines testing scope for downstream impact |
| Sensitivity classification | Phase 2 test data strategy | Determines PII masking requirements |
| Complexity rating | Phase 3 test plan | Guides test category selection (unit vs integration vs E2E) |
| Downstream consumers | Phase 8 impact assessment | Identifies who needs regression testing when changes occur |

---

### Phase 2: Discovery — Test Scope & Test Data Strategy

**Purpose:** Understand test scope based on source data complexity and define test data strategy (synthetic vs production-like).

**Activities:**

1. **Assess test scope and complexity:**
   - Identify source data characteristics that impact testing (schema complexity, join keys, cardinality)
   - Document transformation complexity (number of stages, business logic, edge cases)
   - Identify test categories needed based on pipeline complexity

2. **Define test data strategy:**
   - Determine synthetic vs production-like needs by test category
   - Assess production access constraints and PII masking requirements
   - Document procurement plan (requestor, approvers, refresh frequency)

**Skills:**
- `column-lineage` ✓ — Understand transformation complexity and dependencies *(existing)*

**Gate Criteria:**
- ✅ **Test data strategy documented in feasibility report:**
  - Test data type by test category (synthetic | masked production sample | production-like full volume)
  - Production data access approved (if needed) with InfoSec sign-off for masked samples
  - Masking rules defined for PII/sensitive fields
  - Sample procurement and refresh plan documented
- ✅ Test scope documented (applicable test categories based on pipeline complexity)

**Artifacts:**
- Feasibility report with **test data strategy** (synthetic vs production-like by test category, access constraints, masking approach)

#### Testing Strategy by Work Type

Test scope and data strategy differ significantly by work type:

**New Features:**
- **Test data strategy:** Must be defined from scratch
  - Start with synthetic data for unit/schema/transformation logic tests (AI-generated fixtures)
  - Assess if production samples needed for integration/E2E tests (depends on complexity and criticality)
  - Document production access requirements if realistic data patterns are critical (e.g., cardinality, referential integrity)
- **Test scope:** Identify all applicable test categories based on transformation complexity:
  - Simple SQL transformation → unit tests + schema tests sufficient
  - Multi-stage pipeline → add integration tests + idempotency tests
  - Performance-critical pipeline → add performance tests + scalability tests
  - PII/sensitive data → add security/compliance tests
- **Baseline establishment:** Plan to capture test baseline (expected outputs) after initial implementation for future regression testing

**Enhancements:**
- **Test data strategy:** Leverage existing test fixtures where possible
  - **Reuse existing synthetic fixtures** if schema unchanged
  - **Augment fixtures** if new columns/transformations added
  - **Production samples:** Reuse existing masked samples if available; procure new samples only if enhancement requires new data patterns
- **Test scope:** Incremental test strategy
  - **Regression tests:** Reuse existing tests to validate unchanged behavior
  - **Incremental tests:** Add new tests for enhanced functionality only
  - **Comparison tests:** Before/after comparison to prove existing behavior preserved
- **Baseline update:** Plan to update test baseline if enhancement changes expected outputs

**Defect Fixes:**
- **Test data strategy:** Focus on reproducing defect
  - **Reproduction data:** Identify production data patterns that triggered defect (may require production sample with specific characteristics)
  - **Synthetic reproduction:** Attempt to synthesize minimal test fixture that reproduces defect (preferred for speed)
  - **Edge case identification:** Document edge cases that existing tests missed
- **Test scope:** Minimal, targeted testing
  - **Reproduction test:** Test that fails before fix, passes after fix (regression prevention)
  - **Regression tests:** Run existing test suite to ensure fix doesn't break other functionality
  - **Performance impact:** If defect was performance-related, add performance test to prevent recurrence
- **Test gap analysis:** Document why existing tests missed this defect (informs test coverage improvements)

**Why differentiation matters:** Test data procurement timelines and costs vary significantly. New features require full strategy definition; enhancements can reuse existing assets; defects require targeted reproduction data.

#### Preparation for Next Phase (Phase 3: Design)

Before proceeding to Design, prepare:

**Test Data Readiness:**
- **Production sample approval:** If production data required, initiate InfoSec approval process (can take 2-4 weeks)
- **Masking rules definition:** Document PII fields and masking approach (e.g., email → `user_***@domain.com`, SSN → `XXX-XX-1234`)
- **Sample size estimation:** Estimate row counts needed per test category (unit tests = 10-100 rows; integration tests = 1K-10K rows; performance tests = production-like volumes)
- **Refresh strategy:** For enhancements, determine if existing production samples are still valid or need refresh

**Test Scope Documentation:**
- **Applicable test categories:** List test categories needed (from 15 categories in Background section)
- **Coverage targets:** Propose coverage thresholds (e.g., 80% code coverage for new features; 100% coverage for changed code in enhancements)
- **Complexity analysis:** Document transformation stages, dependencies, and business logic complexity (informs test plan depth in Phase 3)

**Deliverable for Phase 3:** Test data strategy summary with procurement timeline, test scope with applicable categories, and complexity analysis.

#### Traceability

| Traces From | Traces To | Artifact/Linkage |
|-------------|-----------|------------------|
| Phase 1 sensitivity classification | Test data strategy (PII masking requirements) | Determines masking rules and InfoSec approval needs |
| Phase 1 complexity rating | Test scope (applicable test categories) | Simple pipelines = fewer test categories; complex = comprehensive |
| Phase 1 consumer map | Test data strategy (sample size) | High-criticality products with many consumers = production-like test data |
| Test data strategy | Phase 3 test plan (test data fixtures) | Defines what data will be used for each test category |
| Test scope (applicable categories) | Phase 3 test plan (coverage targets) | Defines which test categories will be planned in Phase 3 |
| Production access approval | Phase 4 test fixture generation | Enables production sample procurement in Phase 4 |

---

### Phase 3: Design — Test Planning

**Purpose:** Create comprehensive test plan defining what will be tested, how, and with what data.

**Activities:**

1. **Create test-plan.md:** Test categories, transformation logic to test, performance scenarios, coverage thresholds
2. **Document test data fixtures:** Type by category, generation approach, size, refresh strategy, timeline
3. **Define data contract:** Testable SLAs (freshness, quality, availability)
4. **Define NFR specification:** Performance SLOs, scalability targets

**Skills:**
- `generate-test-plan` 🆕 — Generates test-plan.md from data contract + transformation spec *(proposed new skill)*
- `data-contract` ✓ — Define schema, SLAs, and quality rules *(existing)*
- `column-lineage` ✓ — Document transformation lineage *(existing)*
- `nfr-specification` ✓ — Set performance test thresholds *(existing)*

**Gate Criteria:**
- ✅ Test plan reviewed and approved as part of design review
- ✅ Test plan covers all applicable test categories for the product
- ✅ Data contract defines testable SLAs (freshness, quality, availability)
- ✅ Performance test thresholds align with NFR specification
- ✅ Test data fixtures strategy aligns with Phase 2 test data strategy

**Artifacts:**
- `test-plan.md` — Comprehensive test strategy for the product
- `data-contract.md` — Schema, SLAs, and quality thresholds
- `nfr-specification.md` — Performance test acceptance criteria

#### Testing Strategy by Work Type

Test planning depth and focus vary by work type:

**New Features:**
- **Test plan scope:** Comprehensive, covering all applicable test categories from Phase 2 test scope
  - **Unit tests:** Every transformation function, UDF, SQL query
  - **Integration tests:** Multi-stage pipeline interactions (source → staging → curated)
  - **Schema tests:** All columns (not null, unique, accepted values, relationships)
  - **E2E tests:** Complete pipeline from source to consumption
  - **Performance tests:** SLA validation (if NFR specified)
  - **Security/compliance tests:** PII masking validation (if PII present)
- **Coverage targets:** Define minimum thresholds
  - Code coverage: 80% minimum (functions, transformations)
  - Schema coverage: 100% (all critical columns tested)
  - Business logic coverage: 100% (all business rules validated)
- **Test data fixtures:** Document all fixtures needed
  - Synthetic: Unit tests, schema tests, transformation logic tests
  - Masked production: Integration tests, E2E tests (if realistic patterns required)
  - Production-like: Performance tests (if SLA-critical)
- **Acceptance criteria:** Define clear pass/fail criteria for each test category (e.g., "E2E test passes if output row count matches expected within 0.1%")

**Enhancements:**
- **Test plan scope:** Incremental + regression
  - **Regression tests:** Identify existing tests that must continue to pass (validates unchanged behavior)
  - **Incremental tests:** Define new tests for enhanced functionality only
    - New columns → schema tests for new fields
    - Changed logic → transformation logic tests for modified functions
    - New stage → integration tests for new pipeline stage
  - **Comparison tests:** Before/after comparison to prove backward compatibility
    - Example: "Enhancement to revenue calculation preserves existing values for historical dates"
- **Coverage targets:** Incremental requirements
  - Changed code: 100% coverage (all modified functions tested)
  - Unchanged code: Maintain existing coverage (no reduction)
  - New functionality: Same as new features (80% minimum)
- **Test data fixtures:** Reuse + augment
  - **Reuse:** Existing synthetic fixtures (if schema compatible)
  - **Augment:** Add fixtures for new edge cases introduced by enhancement
  - **Baseline:** Capture before/after outputs for comparison tests
- **Acceptance criteria:** Dual focus
  - Regression: "All existing tests pass with no failures"
  - Incremental: "New tests validate enhancement per requirements"

**Defect Fixes:**
- **Test plan scope:** Minimal, focused on defect reproduction and regression prevention
  - **Reproduction test:** Test that fails before fix, passes after fix
    - Document exact reproduction steps
    - Identify minimal test fixture that triggers defect
    - Define expected behavior (correct output)
  - **Regression tests:** Run full existing test suite to ensure fix doesn't break other functionality
  - **Related tests:** Identify similar scenarios that may have same defect (add preventive tests)
- **Coverage targets:** Narrow scope
  - Defect area: 100% coverage (test must validate fix)
  - Related areas: No new coverage required (regression tests sufficient)
- **Test data fixtures:** Reproduction-focused
  - **Minimal fixture:** Smallest dataset that reproduces defect (e.g., single row with specific values)
  - **Edge case fixture:** Variations that may trigger similar defect
  - **Production sample:** Only if defect is non-reproducible with synthetic data (rare)
- **Acceptance criteria:** Binary validation
  - "Reproduction test fails on code before fix"
  - "Reproduction test passes on code after fix"
  - "All existing regression tests still pass"

**Why differentiation matters:** Test planning effort and review depth vary significantly. New features require comprehensive upfront planning; enhancements focus on delta testing; defects require targeted reproduction validation.

#### Preparation for Next Phase (Phase 4: Build)

Before proceeding to Build, prepare:

**Test Plan Validation:**
- **Design review:** Present test plan to DPM, data owner, and engineering lead for approval
- **Coverage review:** Confirm coverage targets are appropriate for product criticality
- **AI skill readiness:** Confirm all required skills are available (`generate-data-tests`, `dbt-unit-test`, etc.)

**Test Data Preparation:**
- **Production sample procurement:** If Phase 2 identified production data needs, initiate sample generation (masked, InfoSec-approved)
- **Synthetic fixture design:** Document fixture schemas and edge cases for AI generation in Phase 4
- **Baseline capture plan:** For enhancements, document how to capture "before" baseline for comparison

**Test Environment Setup:**
- **Test catalogs:** Provision Unity Catalog schemas for test fixtures (e.g., `test_catalog.product_fixtures`)
- **CI/CD config:** Configure test execution steps in CI/CD pipeline (test commands, coverage thresholds)
- **Local testing:** Document local testing workflow (Astro CLI commands for Airflow DAGs, dbt commands for models)

**Deliverable for Phase 4:** Approved test-plan.md, test data fixtures ready (synthetic generated, production samples procured), test environment configured.

#### Traceability

| Traces From | Traces To | Artifact/Linkage |
|-------------|-----------|------------------|
| Phase 2 test data strategy | test-plan.md (test data fixtures) | Defines what data will be used for each test |
| Phase 2 test scope (applicable categories) | test-plan.md (test categories) | Lists all test categories to implement |
| Phase 1 consumer requirements | data-contract.md (testable SLAs) | Defines acceptance criteria from consumer needs |
| Phase 2 complexity analysis | test-plan.md (coverage targets) | Complex pipelines = higher coverage thresholds |
| test-plan.md | Phase 4 test implementation | Drives what tests are generated and executed |
| data-contract.md | Phase 4 test generation (AI skills) | Provides input to `generate-data-tests` skill |
| nfr-specification.md | Phase 4 performance test thresholds | Defines SLA targets for performance tests |
| test-plan.md | Phase 5 UAT sign-off | Defines what will be validated during UAT |

---

### Phase 4: Build — Test Implementation and Execution

**Purpose:** Implement and execute all tests defined in test plan using AI skills and local/CI testing.

**Activities:**

1. **Generate synthetic test fixtures** (default for unit, schema, transformation logic tests):
   - Use `generate-synthetic-fixtures` skill (AI-generated data)
   - Fixtures stored in `tests/fixtures/synthetic/` and versioned with pipeline code
   - Include edge cases (nulls, zeros, boundary values, extreme values)

2. **Procure production samples** (if required by test plan and InfoSec-approved):
   - Use `sample-production-data` skill (requires Phase 2 InfoSec sign-off)
   - Coordinate with platform team for production read access
   - Apply masking to PII/sensitive fields per InfoSec policy
   - Store masked samples in `tests/fixtures/production-masked/` with provenance metadata (source table, sample date, masking rules applied)

3. **Implement tests via AI skills:**
   - `generate-data-tests` for schema and transformation logic tests (synthetic fixtures)
   - `dbt-unit-test` for integration tests with synthetic or production-sample data
   - `generate-airflow-dag-tests` for Airflow DAG pytest tests

4. **Build remaining tests:**
   - E2E tests (test data type depends on test data strategy)
   - Reconciliation tests (requires production sample for baseline validation)
   - Idempotency tests (synthetic data sufficient)
   - Performance tests (test data depends on performance requirements and criticality)
   - Security/compliance tests for PII masking (requires production sample to validate masking works)
   - Observability tests (synthetic data sufficient)

5. **Local testing with Astro CLI** (for Airflow DAGs):
   - `astro dev parse` — Validate DAG parsing
   - `astro dev pytest` — Run unit tests
   - `astro dev run` — Test execution locally
   - Pre-commit hooks enforce local test passage

6. **Execute tests in CI/CD pipeline:**
   - Run tests on every PR
   - Use synthetic fixtures for speed
   - Use production samples for integration/E2E tests as defined in test plan
   - Generate coverage reports

**Skills:**
- `generate-data-tests` 🆕 — Generate executable test code from data contracts *(proposed new skill)*
- `generate-synthetic-fixtures` 🆕 — Generate AI-created synthetic test data *(proposed new skill)*
- `sample-production-data` 🆕 — Sample and mask production data (requires InfoSec approval) *(proposed new skill)*
- `adding-dbt-unit-test` ✓ — AI-powered integration test generator for dbt models *(existing)*
- `generate-airflow-dag-tests` 🆕 — Generate pytest tests for Airflow DAGs *(proposed new skill)*
- `run-dbt-on-databricks` ✓ — Execute dbt models for testing *(existing)*
- `connect-astro` ✓ — Authenticate to Astronomer for local testing *(existing)*
- `dbt-best-practices` ✓ — Validate against coding standards *(existing)*
- `setup-monitoring-and-logging` ✓ — Configure observability *(existing)*

**Gate Criteria:**
- ✅ All tests from test-plan.md implemented
- ✅ Test fixtures match test data strategy (synthetic vs production-like per test category)
- ✅ Production samples masked and InfoSec-approved (if used)
- ✅ Test coverage meets defined thresholds (automated check via `test-coverage-report` skill)
- ✅ All tests pass in CI/CD pipeline
- ✅ Test fixtures cover edge cases identified in test plan
- ✅ Code review sign-off includes test coverage review
- ✅ Astro DAG parsing tests pass (`astro dev parse`)
- ✅ Astro pytest tests pass (`astro dev pytest`)

**Artifacts:**
- `unit-test-report.md` — Generated from test execution results
- `integration-test-report.md` — Generated from pipeline test runs
- Test code and fixtures in `tests/` and `tests/fixtures/`
- CI/CD pipeline configured with test execution steps
- Airflow DAG tests in `tests/dags/` directory

**CI/CD Enforcement:**
- PRs blocked if test coverage < defined threshold
- PRs blocked if any tests fail
- Coverage report auto-posted as PR comment
- Pre-commit hooks validate test code quality and coverage

**Astro CLI Local Testing Workflow:**

```bash
# 1. Start local Airflow
astro dev start

# 2. Develop/modify DAG
# ... edit dags/my_pipeline.py ...

# 3. Validate parsing
astro dev parse

# 4. Run unit tests
astro dev pytest

# 5. Test execution locally
astro dev run my_pipeline

# 6. Commit and push
git add dags/my_pipeline.py tests/
git commit -m "Add my_pipeline DAG with tests"
git push
```

#### Testing Strategy by Work Type

Test implementation and execution strategy differs significantly by work type:

**New Features:**

- **Test implementation:** Comprehensive from scratch
  - **Unit tests:** Generate via `generate-data-tests` skill from data contract
    - Test every transformation function, UDF, SQL query
    - Include edge cases (nulls, zeros, boundary values)
  - **Schema tests:** Generate via `dbt-unit-test` skill
    - not_null, unique, accepted_values for all critical columns
    - Referential integrity tests for foreign keys
  - **Integration tests:** Generate via `dbt-unit-test` skill with multi-stage fixtures
    - Source → staging → curated pipeline flow
    - Test data propagation and transformations across stages
  - **E2E tests:** Build manually (AI skill planned but not yet available)
    - Full pipeline from source ingestion to final output
    - Use production-sample data if realistic patterns required
  - **Performance tests:** Build manually if SLA-critical
    - Measure execution time against NFR specification thresholds
    - Use production-like data volumes
  - **Security tests:** Build manually if PII present
    - Validate PII masking rules applied correctly
    - Requires production sample to validate masking

- **Test execution:** Full suite every PR
  - **Local:** Run all tests locally before committing (`astro dev pytest`, `dbt test`)
  - **CI/CD:** Full test suite on every PR (synthetic fixtures for speed)
  - **Coverage validation:** Automated check that coverage meets thresholds (e.g., 80% code coverage)

- **Test baseline establishment:** Critical for future regression
  - **Capture outputs:** Save expected outputs from initial test runs
  - **Version baselines:** Store baselines in `tests/baselines/` directory
  - **Document assumptions:** Record data assumptions for future reference

**Enhancements:**

- **Test implementation:** Incremental + regression
  - **Regression tests:** Reuse existing tests without modification
    - Run all existing tests to validate unchanged behavior
    - Confirm existing fixtures still produce expected outputs
  - **Incremental tests:** Generate tests for enhanced functionality only
    - New columns → schema tests for new fields (via `generate-data-tests`)
    - Changed logic → transformation logic tests for modified functions (via `generate-data-tests`)
    - New stage → integration tests for new pipeline stage (via `dbt-unit-test`)
  - **Comparison tests:** Before/after validation
    - Capture "before" outputs using existing code version
    - Capture "after" outputs using enhanced code version
    - Compare to prove unchanged areas preserved (e.g., "historical revenue values match")
  - **Test fixture augmentation:** Add new fixtures for new edge cases
    - Reuse existing fixtures where schema compatible
    - Generate new fixtures only for new columns/scenarios

- **Test execution:** Differential focus
  - **Local:** Run full test suite (regression + incremental) before committing
  - **CI/CD:** Full suite on every PR, with emphasis on comparison tests
  - **Coverage validation:** 100% coverage for changed code (incremental), maintain coverage for unchanged code

- **Test baseline update:** Update expected outputs if enhancement changes behavior
  - **Before/after comparison:** Document intentional changes to expected outputs
  - **Baseline refresh:** Update baselines in `tests/baselines/` if enhancement changes expected behavior
  - **Backward compatibility check:** Validate that historical data processing unchanged

**Defect Fixes:**

- **Test implementation:** Reproduction + regression
  - **Reproduction test:** Create test that fails before fix, passes after fix
    - Document exact defect reproduction steps
    - Create minimal test fixture that triggers defect
    - Define expected behavior (correct output)
    - Test must fail on code before fix (validates test reproduces defect)
  - **Regression tests:** Run full existing test suite
    - Ensure fix doesn't break other functionality
    - No new tests needed unless defect exposed test gap
  - **Related tests:** Add preventive tests for similar scenarios
    - Identify variations that may have same defect
    - Add tests to prevent future recurrence
  - **Test gap analysis:** Document why existing tests missed defect
    - Missing edge case → add edge case to test patterns library
    - Missing test category → add to test plan for next enhancement
    - Insufficient coverage → increase coverage thresholds

- **Test execution:** Focused validation
  - **Local:** Run reproduction test first (must fail), then apply fix, then rerun (must pass)
  - **CI/CD:** Full regression suite to ensure no new breaks
  - **Production validation:** Plan smoke test for Phase 6 (validate fix in production)

- **Test baseline preservation:** Minimal changes
  - **No baseline changes** unless defect was incorrect baseline
  - **Baseline correction:** If defect was incorrect expected output, update baseline and document

**Why differentiation matters:** Test implementation effort varies dramatically. New features require full test generation; enhancements reuse existing tests; defects focus on reproduction validation. CI/CD enforcement and coverage thresholds also differ.

#### Preparation for Next Phase (Phase 5: Validate)

Before proceeding to Validate, prepare:

**Test Reports:**
- **unit-test-report.md:** Generate from test execution results (pass/fail counts, coverage metrics, execution times)
- **integration-test-report.md:** Generate from pipeline test runs (E2E results, data quality validation)
- **Test coverage summary:** Automated report showing coverage by module/function (via `test-coverage-report` skill)
- **Failed tests documentation:** For any failing tests, document waiver justification and risk acceptance

**UAT Preparation:**
- **UAT test scenarios:** Extract high-level business scenarios from test plan for data owner validation
- **UAT test data:** Prepare production-sample datasets for UAT (masked, representative)
- **UAT environment:** Ensure UAT environment (SQA) has latest code and test data deployed

**Sign-off Readiness:**
- **Code review completion:** Ensure all PRs merged with test coverage sign-off
- **Coverage validation:** Confirm automated checks passed (coverage thresholds met, all tests passed)
- **Known issues log:** Document any test failures with accepted waivers

**Deliverable for Phase 5:** Test reports (unit, integration, coverage), UAT scenarios ready, test baseline established and versioned.

#### Traceability

| Traces From | Traces To | Artifact/Linkage |
|-------------|-----------|------------------|
| Phase 3 test-plan.md | Test code implementation | Defines what tests to generate and execute |
| Phase 3 data-contract.md | Test generation (AI skills input) | Provides schema and rules to `generate-data-tests` |
| Phase 2 test data strategy | Test fixtures (synthetic vs production) | Determines fixture generation approach |
| Test code and fixtures | Phase 5 UAT validation | Provides evidence of test execution |
| unit-test-report.md, integration-test-report.md | Phase 5 sign-off decision | Evidence for approval/rejection |
| Test baseline (expected outputs) | Phase 7 regression testing | Reference for validating future changes |
| Test baseline | Phase 8 comparison testing | "Before" baseline for enhancements |
| Test gap analysis (defects) | Phase 8 test plan updates | Improves future test coverage |

---

### Phase 5: Validate — Test Sign-Off and UAT

**Purpose:** Formal test coverage review and UAT validation before production deployment.

**Activities:**
- Data owners execute UAT testing against real-world scenarios
- Review test reports for completeness and accuracy
- Verify test coverage meets defined thresholds
- Validate failed tests have documented waivers with risk acceptance
- Governance review of security/compliance test results (for products with PII)

**Skills:**
- `test-coverage-report` 🆕 — Analyze test coverage and report gaps *(proposed new skill)*

**Gate Criteria:**
- ✅ Test reports reviewed by DPM, data owner and engineering lead
- ✅ Test coverage signed off as sufficient for the product
- ✅ Failed tests have documented waivers with risk acceptance
- ✅ UAT test results confirm business logic correctness

**Artifacts:**
- `uat-sign-off.md` — References test results and coverage
- Test coverage report attached to sign-off documentation

#### Testing Strategy by Work Type

UAT and sign-off focus differs by work type:

**New Features:**
- **UAT scope:** Comprehensive business scenario validation
  - **Business scenarios:** Data owner validates all user stories and acceptance criteria
  - **Data quality:** Validate output data accuracy, completeness, and consistency
  - **Performance:** Validate execution times meet consumer expectations
  - **Downstream integration:** Validate consumers can access and use data
- **Sign-off review:** Full test coverage assessment
  - **Coverage validation:** Confirm 80%+ code coverage (or project-specific threshold)
  - **Test category completeness:** Validate all applicable test categories implemented (unit, integration, E2E, etc.)
  - **Edge case validation:** Review edge case test coverage
  - **Security review:** Governance review if PII present (PII masking validation)
- **Waiver process:** Formal risk acceptance for any failing tests
  - Document business justification for waiver
  - Assign owner for future remediation
  - Record in known issues log

**Enhancements:**
- **UAT scope:** Incremental + regression validation
  - **Incremental validation:** Data owner validates new/changed functionality only
  - **Regression validation:** Spot-check existing functionality to confirm unchanged behavior
  - **Comparison validation:** Review before/after comparisons to confirm backward compatibility
  - **Consumer impact:** If breaking change, coordinate with downstream consumers for their UAT
- **Sign-off review:** Delta-focused
  - **Changed code coverage:** Confirm 100% coverage for modified code
  - **Regression test pass rate:** Confirm all existing tests pass
  - **Comparison test results:** Review before/after outputs for intentional vs. unintentional changes
- **Waiver process:** Limited scope
  - Waivers only for new functionality
  - Regression test failures not waiverable (must be fixed)

**Defect Fixes:**
- **UAT scope:** Defect reproduction and validation
  - **Defect validation:** Data owner confirms defect is fixed using reproduction test
  - **Regression validation:** Spot-check critical functionality to ensure fix didn't break other areas
  - **Production validation plan:** Document smoke test plan for Phase 6 (production validation)
- **Sign-off review:** Focused on defect fix
  - **Reproduction test validation:** Confirm test fails before fix, passes after fix
  - **Regression test pass rate:** Confirm all existing tests pass
  - **Root cause documentation:** Review root cause and preventive measures
- **Waiver process:** Not applicable
  - Defect fix must resolve defect (no waivers)
  - Regression test failures must be fixed

**Why differentiation matters:** UAT effort and sign-off rigor vary significantly. New features require comprehensive business validation; enhancements focus on delta validation; defects focus on reproduction confirmation.

#### Preparation for Next Phase (Phase 6: Publish)

Before proceeding to Publish, prepare:

**Deployment Readiness:**
- **Sign-off documentation:** Ensure uat-sign-off.md completed with approvals from DPM, data owner, and engineering lead
- **Known issues log:** Document any waivers and remediation plans
- **Deployment checklist:** Prepare deployment record template for Phase 6

**Production Smoke Test Plan:**
- **Critical scenarios:** Identify 3-5 critical test scenarios to execute in production post-deployment
- **Test data:** Prepare production test data queries (read-only, minimal scope)
- **Expected outputs:** Document expected results for smoke tests
- **Rollback criteria:** Define failure conditions that trigger rollback

**Monitoring & Alerting Validation:**
- **Alert configuration:** Validate monitoring alerts configured per observability tests
- **Dashboard readiness:** Confirm operational dashboards available for Phase 7

**Deliverable for Phase 6:** Approved uat-sign-off.md, production smoke test plan, rollback criteria defined.

#### Traceability

| Traces From | Traces To | Artifact/Linkage |
|-------------|-----------|------------------|
| Phase 4 test reports (unit, integration) | uat-sign-off.md | Evidence for approval decision |
| Phase 4 test coverage report | Sign-off decision (approve/reject) | Validates coverage meets thresholds |
| Phase 3 test-plan.md (acceptance criteria) | UAT validation | Defines what data owner validates |
| Phase 1 consumer requirements | UAT business scenarios | Validates consumer needs met |
| uat-sign-off.md | Phase 6 deployment approval | Formal approval to deploy |
| Known issues log (waivers) | Phase 7 incident tracking | Documents accepted risks for monitoring |

---

### Phase 6: Publish — Production Smoke Tests

**Purpose:** Validate production environment post-deployment with limited production testing.

**Activities:**
- Execute smoke tests post-deployment
- Run subset of critical tests against production data (limited scope)
- Confirm monitoring and alerting configuration works as expected
- Test consumer access and permissions

**Test Data:** Production (Live, Restricted Access) — read-only, audit trail required

**Gate Criteria:**
- ✅ Production smoke tests pass before go-live announcement
- ✅ Monitoring/alerting validated with test incidents

**Artifacts:**
- Deployment record with smoke test results
- Production validation checklist confirms test execution

#### Testing Strategy by Work Type

Production smoke testing strategy differs by work type:

**New Features:**
- **Smoke test scope:** End-to-end validation with production data
  - **Data ingestion:** Confirm source data accessible and ingested successfully
  - **Transformation execution:** Confirm pipeline executes without errors
  - **Output validation:** Confirm output tables created with expected schema
  - **Row count validation:** Confirm row counts reasonable (compare to expected order of magnitude)
  - **Consumer access:** Confirm downstream consumers can query output tables
  - **Monitoring validation:** Trigger test alert to confirm alerting works
- **Test execution:** Limited production queries
  - Execute 3-5 critical queries against production output tables
  - Compare results to expected patterns (not exact values)
  - Audit trail: Log all production queries for security compliance
- **Rollback criteria:** Define failure conditions
  - Pipeline execution fails → rollback
  - Output schema mismatch → rollback
  - Row count orders of magnitude off → rollback
  - Consumer access fails → rollback

**Enhancements:**
- **Smoke test scope:** Regression + incremental validation
  - **Regression validation:** Confirm existing functionality unchanged
    - Query historical data (pre-enhancement date) and compare to baseline
    - Validate backward compatibility (existing consumers still work)
  - **Incremental validation:** Confirm enhancement deployed correctly
    - Query new/changed data (post-enhancement date)
    - Validate new columns present and populated
    - Validate changed logic produces expected results
  - **Consumer validation:** Confirm downstream consumers not broken
    - Test existing consumer queries still work
    - If breaking change, validate consumers updated their queries
- **Test execution:** Comparison-focused
  - Before/after comparison on production data
  - Historical data (pre-enhancement) should match previous production baseline
  - New data (post-enhancement) should reflect changes
- **Rollback criteria:** Stricter for enhancements
  - Regression test failure → immediate rollback (unchanged behavior broken)
  - Incremental test failure → assess severity (may not require rollback if minor)
  - Consumer query failures → immediate rollback (breaking change)

**Defect Fixes:**
- **Smoke test scope:** Defect validation only
  - **Defect validation:** Confirm defect is fixed in production
    - Execute reproduction query that previously triggered defect
    - Confirm correct output now returned
  - **Regression validation:** Minimal spot-check of critical functionality
    - Execute 2-3 critical queries to ensure no new breaks
  - **Monitoring validation:** Confirm alert that detected defect is now clear
- **Test execution:** Targeted production queries
  - Execute defect reproduction query
  - Compare result to expected correct output
  - Execute 2-3 regression queries for critical areas
- **Rollback criteria:** Binary
  - Defect still occurs → immediate rollback (fix didn't work)
  - New defect introduced → immediate rollback (regression)
  - Defect fixed and no regressions → proceed to go-live

**Why differentiation matters:** Production smoke testing scope and rollback criteria vary significantly. New features require comprehensive E2E validation; enhancements require regression comparison; defects require targeted fix validation. Rollback criteria strictness differs (enhancements stricter than new features).

#### Preparation for Next Phase (Phase 7: Operate)

Before proceeding to Operate, prepare:

**Operational Handoff:**
- **Deployment record:** Document smoke test results, deployment timestamp, deployed version
- **Known issues:** Document any issues observed during smoke testing (even if not blocking)
- **Monitoring baselines:** Establish production monitoring baselines (row counts, execution times, data quality metrics)
- **Runbook update:** Finalize operational runbook with production-validated procedures

**Monitoring Configuration:**
- **Alert validation:** Confirm all alerts triggered correctly during smoke testing
- **Dashboard validation:** Confirm operational dashboards displaying production data correctly
- **Incident response:** Document incident response procedures (who to contact, escalation path)

**Consumer Notification:**
- **Go-live announcement:** Notify downstream consumers that data product is live
- **Access documentation:** Provide consumers with access instructions and query examples
- **Support channels:** Document how consumers can report issues

**Deliverable for Phase 7:** Deployment record with smoke test results, production monitoring baselines established, operational runbook finalized, consumers notified.

#### Traceability

| Traces From | Traces To | Artifact/Linkage |
|-------------|-----------|------------------|
| Phase 5 uat-sign-off.md | Deployment approval | Formal approval to deploy |
| Phase 5 smoke test plan | Production smoke tests | Defines what to validate in production |
| Phase 4 test baseline (expected outputs) | Smoke test expected results | Reference for production validation |
| Smoke test results | Deployment record | Evidence of production validation |
| Production monitoring baselines | Phase 7 operational monitoring | Reference for anomaly detection |
| Deployment record | Phase 7 incident log | Links incidents to deployed versions |

---

### Phase 7: Operate — Continuous Testing and Validation

**Purpose:** Ongoing testing validation and periodic health checks.

**Activities:**
- Monitor that tests continue to pass as data evolves
- Run periodic platform health checks (quarterly regression tests)
- Test pipeline changes in dev/SQA before production promotion
- Validate incident fixes with regression tests

**Skills:**
- `optimize-databricks-job` ✓ — Performance regression checks *(existing)*
- `runbook` ✓ — Operational procedures *(existing)*

**Ongoing Activities:**
- Regression test execution for platform changes
- Test baseline updates when source schemas evolve
- Incident root cause analysis includes test gap identification

**Artifacts:**
- Incident log documenting test gaps
- Runbook with operational procedures
- Updated test baselines when patterns change

**Note:** Platform regression testing (for upgrades) is covered in Section 8 below.

#### Testing Strategy by Work Type

Ongoing operational testing differs by work type:

**New Features:**
- **Operational testing scope:** Monitor test health
  - **Continuous validation:** CI/CD runs full test suite on every commit (dev/SQA environments)
  - **Periodic regression:** Quarterly full regression test suite execution against production data (validates production data patterns still match test assumptions)
  - **Monitoring validation:** Validate that operational monitoring detects anomalies (row count deviations, execution time spikes, data quality issues)
  - **Test baseline refresh:** Update test baselines if source data patterns evolve (e.g., new enum values, cardinality changes)
- **Incident response:** Test-driven incident resolution
  - **Root cause analysis:** For every production incident, analyze why tests didn't catch it
  - **Test gap identification:** Document test gaps exposed by incidents
  - **Preventive testing:** Add tests to prevent recurrence (becomes defect fix workflow)
- **Performance regression:** Monitor for performance degradation
  - **Execution time tracking:** Track pipeline execution times; investigate if trends upward
  - **Performance tests:** Periodically run performance tests to validate SLA compliance
  - **Optimization validation:** When optimizations applied, run performance tests to measure improvement

**Enhancements:**
- **Operational testing scope:** Validate enhancements in production
  - **Post-deployment monitoring:** Monitor enhanced pipeline for first 48 hours post-deployment
  - **Comparison monitoring:** Compare production metrics (row counts, execution times) to pre-enhancement baseline
  - **Consumer validation:** Monitor downstream consumer queries for failures (may indicate breaking change)
  - **Regression monitoring:** Watch for incidents in unchanged areas (may indicate unintended regression)
- **Incident response:** Distinguish enhancement-related vs. unrelated
  - **Enhancement-related incidents:** Roll back enhancement, reproduce in dev, fix, re-test, re-deploy
  - **Unrelated incidents:** Standard incident response (not caused by enhancement)
- **Test baseline update:** Update baselines if enhancement intentionally changes expected outputs
  - Document baseline changes in deployment record
  - Version old baselines for rollback scenarios

**Defect Fixes:**
- **Operational testing scope:** Validate fix and prevent recurrence
  - **Fix validation:** Monitor production for 24-48 hours post-deployment to confirm defect resolved
  - **Recurrence monitoring:** Watch for same defect pattern in other areas (may indicate systemic issue)
  - **Test suite validation:** Confirm reproduction test now passes in CI/CD (prevents future regressions)
  - **Alert validation:** If defect triggered monitoring alert, confirm alert now clear
- **Incident response:** Track defect recurrence
  - **Recurrence:** If same defect recurs, indicates reproduction test was insufficient → enhance test
  - **Related defects:** If similar defects occur, indicates test gap → add preventive tests
- **Test baseline preservation:** No baseline changes unless defect was incorrect baseline
  - If baseline was wrong, document correction in incident log

**Why differentiation matters:** Operational testing focus varies. New features require baseline monitoring; enhancements require comparison monitoring; defects require recurrence prevention monitoring.

#### Preparation for Next Phase (Phase 8: Evolve)

When enhancements or changes are planned, prepare for Phase 8:

**Enhancement Planning:**
- **Baseline capture:** Capture current production state as "before" baseline for future enhancements
  - Production row counts, data quality metrics, execution times
  - Test baseline outputs (for comparison testing in future Phase 4)
- **Incident log review:** Review incident log to identify areas needing enhancement or refactoring
- **Test gap analysis:** Aggregate test gaps from incidents to inform next enhancement's test plan
- **Consumer feedback:** Collect consumer feedback on data quality or feature requests (informs next Phase 1 Triage)

**Platform Change Readiness:**
- **Regression suite readiness:** Ensure full regression test suite operational (for platform upgrades or framework changes)
- **Test environment sync:** Ensure test environments (dev, SQA) mirror production configuration (for testing platform changes)

**Deliverable for Phase 8:** Production baseline captured, incident log with test gaps documented, consumer feedback collected, regression suite validated.

#### Traceability

| Traces From | Traces To | Artifact/Linkage |
|-------------|-----------|------------------|
| Phase 6 production monitoring baselines | Anomaly detection | Reference for identifying deviations |
| Phase 6 deployment record | Incident log (version tracking) | Links incidents to deployed versions |
| Phase 4 test baseline | Periodic regression validation | Reference for validating production data patterns |
| Incident log (test gaps) | Phase 8 test plan updates | Improves future test coverage |
| Production baseline (current state) | Phase 8 comparison testing | "Before" baseline for future enhancements |
| Phase 4 test code | CI/CD continuous validation | Tests run on every commit |

---

### Phase 8: Evolve — Impact Assessment Testing

**Purpose:** Test changes to existing products and assess downstream impact.

**Activities:**
- Assess downstream impact before making schema changes
- Test backward compatibility for breaking changes
- Validate migration scripts with test data
- Execute regression tests after changes to ensure no business logic regressions
- Update tests when requirements change (new transformations, schema evolution)

**Skills:**
- `downstream-impact-assessment` ✓ — Assess consumer impact with risk ratings *(existing)*
- `column-lineage` ✓ — Assess change impact on downstream models *(existing)*
- `impact-assessment` 🆕 — Assess downstream impact of data changes via OpenLineage *(proposed new skill)*

**Gate Criteria:**
- ✅ Downstream impact assessment completed before breaking changes
- ✅ Regression tests pass for evolved product version
- ✅ Test plan updated to reflect new requirements

**Artifacts:**
- `downstream-impact-assessment.md` — Test validation plan for impacted consumers
- Updated test plan for product enhancements
- Regression test results comparing before/after changes

#### Testing Strategy by Work Type

Evolution testing strategy is primarily focused on **enhancements** and **defect fixes**, as these represent changes to existing products. **New features** don't apply to Phase 8 (they enter Phase 8 only after they've been deployed and are being evolved).

**New Features:**
- **Not applicable in Phase 8** — New features don't "evolve" until they've been deployed (Phase 6) and operated (Phase 7) for some time
- When a previously new feature needs changes, it becomes an **enhancement** (see below)

**Enhancements:**
- **Impact assessment:** Analyze downstream consumers before making changes
  - **Consumer identification:** Use Phase 1 consumer use case map to identify all downstream consumers
  - **Breaking change analysis:** Determine if change is breaking (schema changes, column removal, logic changes that alter output)
  - **Impact rating:** Rate impact severity (high = breaking change requiring consumer updates; low = backward compatible)
  - **Consumer notification:** Notify impacted consumers with timeline and migration guidance
- **Testing strategy for enhancements:** Triggers new lifecycle iteration
  - **Re-enter Phase 1 (Triage):** Document enhancement scope, impacted consumers, complexity
  - **Re-enter Phase 2 (Discovery):** Assess test data strategy (reuse existing or procure new)
  - **Re-enter Phase 3 (Design):** Create incremental test plan (regression + incremental tests)
  - **Re-enter Phase 4 (Build):** Implement tests per enhancement testing strategy (see Phase 4 above)
  - **Continue through Phase 5-7:** UAT, production smoke test, operational monitoring
- **Downstream consumer testing:** Validate consumers not broken
  - **Consumer regression tests:** Request downstream consumers run their regression tests against enhancement in SQA environment
  - **Consumer test validation:** Confirm downstream tests pass before production deployment
  - **Consumer migration tests:** If breaking change, validate consumer migration scripts work
- **Regression testing focus:** Before/after comparison critical
  - **Historical data validation:** Confirm enhancement doesn't alter historical data processing (unless intentional)
  - **Backward compatibility:** Validate existing consumer queries continue to work
  - **Test baseline comparison:** Compare production outputs before/after to identify unintended changes

**Defect Fixes:**
- **Impact assessment:** Determine if defect fix affects downstream consumers
  - **Defect scope:** Document which data was incorrect and time period affected
  - **Consumer notification:** Notify consumers if they consumed incorrect data (may require data corrections)
  - **Fix impact:** Determine if fix changes output data (triggers consumer re-validation)
- **Testing strategy for defect fixes:** Minimal lifecycle re-entry
  - **Phase 1 (Triage):** Document defect root cause, impacted consumers, severity (see Phase 1 defect strategy above)
  - **Phase 4 (Build):** Implement reproduction test + regression tests (see Phase 4 defect strategy above)
  - **Phase 5-7:** Expedited UAT (defect validation only), production smoke test, operational monitoring
- **Downstream consumer testing:** Limited scope
  - **Consumer notification:** Inform consumers fix is deployed (may affect their data if they consumed incorrect data)
  - **Consumer re-validation:** Request consumers re-run their tests if defect impacted their downstream processing
- **Regression testing focus:** Ensure fix doesn't break anything else
  - **Full regression suite:** Run all existing tests to validate no new breaks
  - **Reproduction test:** Validate test fails before fix, passes after fix (see Phase 4 defect strategy)

**Why differentiation matters:** Enhancements require comprehensive downstream impact assessment and full lifecycle re-entry; defects require focused fix validation with expedited lifecycle. Consumer coordination critical for enhancements; limited for defects.

#### Phase 8 and Lifecycle Iteration

**Key insight:** Phase 8 is the **feedback loop** that triggers new lifecycle iterations. When evolving existing products, you don't stay in Phase 8 — you re-enter earlier phases:

```
Phase 8 (Evolve) → Identify enhancement needed
  ↓
Phase 1 (Triage) → Document enhancement scope
  ↓
Phase 2 (Discovery) → Assess test data strategy (reuse vs. new)
  ↓
Phase 3 (Design) → Create incremental test plan
  ↓
Phase 4 (Build) → Implement regression + incremental tests
  ↓
Phase 5 (Validate) → UAT with comparison testing
  ↓
Phase 6 (Publish) → Production smoke test with regression validation
  ↓
Phase 7 (Operate) → Monitor enhanced pipeline
  ↓
Phase 8 (Evolve) → Identify next enhancement ... (cycle repeats)
```

This cyclical pattern ensures every enhancement follows the same testing rigor as the original feature.

#### Preparation for Lifecycle Re-Entry (Phase 1)

When evolution is needed, prepare to re-enter Phase 1:

**Enhancement Scoping:**
- **Change documentation:** Document what needs to change (new columns, changed logic, schema evolution, performance improvements)
- **Consumer impact analysis:** Use `downstream-impact-assessment` skill to identify impacted consumers and breaking changes
- **Business justification:** Document why enhancement needed (consumer request, performance issue, defect fix, regulatory requirement)
- **Complexity assessment:** Rate enhancement complexity (simple | moderate | complex) to inform test planning

**Test Strategy Planning:**
- **Existing test inventory:** Review existing tests and baselines (what can be reused vs. what needs augmentation)
- **Test data assessment:** Determine if existing test fixtures sufficient or new procurement needed
- **Regression scope:** Identify critical areas that must not break (informs regression test scope)
- **Test gap remediation:** Incorporate test gaps from Phase 7 incident log into enhancement test plan

**Deliverable for Phase 1 (Re-Entry):** Enhancement scope document with downstream impact assessment, complexity rating, test strategy overview, consumer notification plan.

#### Traceability (Full Lifecycle Traceability)

Phase 8 completes the traceability loop, linking back to Phase 1:

| Traces From | Traces To | Artifact/Linkage |
|-------------|-----------|------------------|
| Phase 7 incident log (test gaps) | Phase 1 (re-entry) scope | Test gaps inform enhancement requirements |
| Phase 7 production baseline | Phase 4 (re-entry) comparison tests | "Before" baseline for regression validation |
| Phase 1 consumer use case map | downstream-impact-assessment.md | Identifies consumers to validate |
| downstream-impact-assessment.md | Phase 1 (re-entry) scope | Defines impact of changes on consumers |
| Phase 4 test baseline (original) | Phase 4 (re-entry) regression tests | Original baseline reused for regression |
| Regression test results | Phase 5 (re-entry) UAT sign-off | Evidence of backward compatibility |
| Phase 8 enhancement scope | Phase 1 (re-entry) demand tracker | New lifecycle iteration begins |

**Key Traceability Principle:** Every phase traces forward and backward, creating an unbroken chain from initial product scoping (Phase 1) through deployment (Phase 6), operations (Phase 7), and evolution (Phase 8), which then triggers a new cycle starting at Phase 1 again.

---

## 3. Guardrails and Enforcement

Ensure every data engineer follows testing standards:

**Pre-commit Hooks:**
- Lint test code (naming conventions, structure)
- Verify test coverage meets minimum threshold before allowing commit
- Check that new models have corresponding tests

**CI/CD Pipeline Checks:**
- Run all tests on every PR
- Generate and post test coverage report as PR comment
- Block merge if coverage < defined threshold
- Block merge if any critical test fails

**Flaky Test Management:**

Without flake handling, engineers will route around merge gates with `pytest.mark.skip`. Strategy:

- **Auto-retry:** CI retries failed tests 3x before blocking merge. Log flakes but allow merge if retry passes.
- **Quarantine bucket:** Persistent flakes moved to `@pytest.mark.quarantine` (run but don't block merge)
  - Test owner has 30 days to fix with daily Slack alerts
  - Waiver requires dual approval (eng lead + product owner) if unfixable, expires in 90 days
  - Quarantined tests auto-deleted at waiver expiry
- **Metrics dashboard:** Track quarantined count by team (target < 5%), mean-time-to-fix, waiver expiry dates. Monthly engineering lead review.

**Automated PR Review:**
- AI skill (`test-reviewer`) reviews test code quality
- Checks for common anti-patterns (hard-coded values, missing edge cases, weak assertions)
- Posts review comments on PR

**Quarterly Audit:**
- Generate organization-wide test coverage dashboard
- Identify products below defined coverage thresholds
- Escalate non-compliance to product owners

**Training and Onboarding:**
- **Testing guide** in Catalyst documentation
- **Interactive skill demos** showing test generation workflows
- **Office hours** for engineers learning testing patterns
- **Champions network** of engineers who model best practices

---

## 4. Testing Patterns Library

Create a **reusable patterns library** as part of the Catalyst skills repository:

- `patterns/testing/dbt-schema-tests.md` — dbt schema test patterns
- `patterns/testing/pytest-unit-tests.md` — PySpark/pandas unit test patterns
- `patterns/testing/integration-tests.md` — multi-stage pipeline integration test patterns
- `patterns/testing/e2e-tests.md` — end-to-end testing with production-like data
- `patterns/testing/reconciliation-tests.md` — cross-system reconciliation patterns
- `patterns/testing/reference-data-validation.md` — lookup table validation patterns
- `patterns/testing/idempotency-tests.md` — idempotency validation patterns
- `patterns/testing/performance-tests.md` — SLA validation and scalability test patterns
- `patterns/testing/security-compliance-tests.md` — PII masking, access control validation
- `patterns/testing/observability-monitoring.md` — testing that logging/alerting/monitoring is configured correctly (build-time validation)
- `patterns/testing/lineage-impact-tests.md` — dependency tracking patterns
- `patterns/testing/baseline-establishment.md` — establishing test baselines and validating pipeline behavior under data pattern changes
- `patterns/testing/fixture-design.md` — test data fixture design principles
- `patterns/testing/test-data-management.md` — production sampling, masking strategies
- `patterns/testing/regression-suites.md` — regression test suite design patterns
- `patterns/testing/bulk-dag-execution.md` — orchestration patterns for bulk testing

Skills reference these patterns when generating tests. Engineers can also consult them directly.

---

## 5. Catalyst Skills Catalog for Testing

This section catalogs all AI skills (existing and proposed) organized by lifecycle phase and testing category.

### Proposed New Skills

| Skill | Purpose | Used in Phase |
|-------|---------|---------------|
| `generate-data-tests` | Generate executable test code from data contracts | Phase 4 (Build) |
| `generate-synthetic-fixtures` | Generate AI-created synthetic test data | Phase 4 (Build) |
| `sample-production-data` | Sample and mask production data (requires InfoSec approval) | Phase 2 (Discovery), Phase 4 (Build) |
| `test-coverage-report` | Analyze test coverage and report gaps | Phase 4 (Build), Phase 5 (Validate) |
| `test-plan-reviewer` | Review test plans for completeness | Phase 3 (Design), Phase 4 (Build) |
| `generate-test-plan` | Generate test-plan.md from data contract | Phase 3 (Design) |
| `generate-regression-suite` | Generate regression test suite configs | Platform Regression (Section 8) |
| `run-regression-suite` | Execute regression test suite | Platform Regression (Section 8) |
| `compare-regression-results` | Compare before/after regression results | Platform Regression (Section 8) |
| `generate-airflow-dag-tests` | Generate pytest tests for Airflow DAGs | Phase 4 (Build) |
| `local-astro-test-runner` | Orchestrate Astro CLI local testing | Phase 4 (Build) |

### Existing Catalyst Skills

| Skill | Testing Category | Used in Phase |
|-------|-----------------|---------------|
| **`adding-dbt-unit-test`** | Unit Tests | Phase 4 (Build) |
| **`unit-test-report`** | Unit Tests (Reporting) | Phase 4 (Build) |
| **`integration-test-report`** | Integration Tests (Reporting) | Phase 4 (Build) |
| **`column-lineage`** | Lineage & Impact Tests | Phase 2 (Discovery), Phase 3 (Design), Phase 8 (Evolve) |
| **`parse-lineage`** | Lineage & Impact Tests | Phase 3 (Design) |
| **`downstream-impact-assessment`** | Lineage & Impact Tests | Phase 8 (Evolve) |
| **`impact-assessment`** | Lineage & Impact Tests | Phase 8 (Evolve) |
| **`optimize-databricks-job`** | Performance Tests | Phase 7 (Operate) |
| **`optimize-dbsql-query`** | Performance Tests | Phase 4 (Build) |
| **`nfr-specification`** | Performance & Scalability Tests | Phase 3 (Design) |
| **`setup-monitoring-and-logging`** | Observability Tests | Phase 4 (Build) |
| **`runbook`** | Observability Tests | Phase 7 (Operate) |
| **`run-dbt-on-databricks`** | E2E Tests, Integration Tests | Phase 4 (Build) |
| **`databricks-jobs`** | E2E Tests, Regression Tests | Phase 4 (Build), Platform Regression |
| **`connect-astro`** | Local Testing (Airflow) | Phase 4 (Build) |
| **`data-contract`** | Test Planning | Phase 3 (Design) |
| **`dbt-best-practices`** | All Testing Categories | Phase 4 (Build) |
| **`dbt-test`** | Integration Tests, AI-powered | Phase 4 (Build) |

**Detailed skill descriptions** are available in Section 5 (Catalyst Skills Catalog).

---

## 6. Implementation Roadmap

**Note:** This roadmap focuses on building testing infrastructure and skills. Integration with lifecycle phases (Section 2) happens in parallel.

**Phase 1: Foundations (Weeks 1-4)**
- [ ] Define testing standards document (coverage requirements, test categories, test data strategy)
- [ ] Establish test data infrastructure (sampling pipeline, masking, InfoSec approval process)
- [ ] Create patterns library (reusable test templates)
- [ ] Update RFD 0002 lifecycle documentation
- [ ] Create `test-plan.md` template for Phase 3 (Design)
- [ ] Build `generate-data-tests` skill (MVP)
- [ ] Build `test-coverage-report` skill
- [ ] Document Astro CLI local testing workflow
- [ ] Create Astro DAG test templates

**Phase 2: AI-Assisted Generation (Weeks 5-8)**
- [ ] Enhance `generate-data-tests` for transformation logic tests
- [ ] Build `generate-synthetic-fixtures` skill (AI-generated data, no special approvals)
- [ ] Build `sample-production-data` skill (requires InfoSec sign-off workflow, masking enforcement, provenance tracking)
- [ ] Build `generate-regression-suite` skill
- [ ] Build `generate-airflow-dag-tests` skill
- [ ] Build `local-astro-test-runner` skill
- [ ] Build `generate-test-plan` skill
- [ ] Integrate skills with CI/CD
- [ ] Pilot with 3 data products (varying complexity levels)

**Phase 3: Guardrails and Enforcement (Weeks 9-12)**
- [ ] Implement pre-commit hooks
- [ ] Build `test-plan-reviewer` skill
- [ ] Build `run-regression-suite` and `compare-regression-results` skills
- [ ] Set up CI/CD gates (coverage/test failure blocks)
- [ ] Update Phase 5 (Validate) gate criteria
- [ ] Generate test coverage dashboard
- [ ] Create platform regression test suites (smoke + full)
- [ ] Roll out to all critical and high-priority products

**Phase 4: Adoption and Scale (Weeks 13-16)**
- [ ] Expand to remaining products
- [ ] Build training materials and workshops
- [ ] Establish testing champions network
- [ ] Integrate regression testing into platform upgrade procedures
- [ ] Integrate impact assessment testing into Phase 8 (Evolve)
- [ ] Promote Astro CLI as standard for Airflow development
- [ ] Run quarterly platform health checks
- [ ] Quarterly audit and compliance reporting
- [ ] Collect feedback and iterate

---

## 7. Platform Regression Testing (Separate from Data Product Lifecycle)

Platform regression testing is **separate from the standard data product lifecycle** (Phases 0-8). It addresses platform-wide changes (runtime upgrades, framework migrations, infrastructure changes) that affect multiple products simultaneously.

### Purpose

Validate that platform changes (Databricks runtime upgrades, dbt version migrations, infrastructure updates) don't break existing production pipelines. Unlike product-specific testing (which happens during development), regression testing happens **at the platform level** before rolling out changes to production.

### Regression Test Suite Types

**1. Smoke Test Suite**
- **Purpose:** Quick validation of platform changes (30-60 min execution)
- **Scope:** 20-30 representative Critical and High-tier pipelines covering key patterns
- **When to run:** Before every platform change, as a first-pass validation

**2. Full Regression Suite**
- **Purpose:** Comprehensive validation before production rollout
- **Scope:** All Critical and High-tier products (100-200+ pipelines)
- **When to run:** After smoke suite passes, before production deployment

**3. Domain-Specific Suites**
- **Purpose:** Validate domain-specific patterns (equity, fixed income, risk, etc.)
- **Scope:** All products within a domain
- **When to run:** For changes affecting specific domains (e.g., dbt macro changes affecting equity pipelines only)

### Test Execution Modes

**Execution-Only Mode (Fast)**
- Validate pipelines run to completion without execution errors
- No data validation (row counts, schema checks only)
- Suitable for infrastructure changes (cluster config, network settings)

**Full Validation Mode (Slow)**
- Validate data correctness (row counts, checksums, reconciliation)
- Compare outputs before/after change (data diff)
- Required for runtime/framework upgrades that may affect business logic

### Regression Testing Workflow

**Pre-Change Baseline**
1. Run regression suite against current platform configuration
2. Capture baseline results (execution status, duration, data outputs)
3. Store baseline for comparison

**Post-Change Validation**
1. Deploy platform change to dev/SQA environment
2. Run regression suite against new configuration
3. Compare results to baseline:
   - **Execution status:** Identify newly failing pipelines
   - **Performance:** Identify pipelines >15% slower
   - **Data outputs:** Identify data differences (for full validation mode)
4. Investigate regressions and determine root cause
5. Fix breaking changes or document acceptable regressions
6. Re-run regression suite until pass rate meets threshold

**Production Rollout Criteria**
- Regression rate < 5% for Critical-tier products
- All newly failing pipelines have documented root cause and mitigation plan
- Performance degradations acceptable (business approved)

**Post-Rollout Monitoring**
- Run regression suite in production after rollout
- Monitor for late-breaking issues
- Rollback if critical failures detected

### Regression Testing Use Cases

**Use Case 1: Databricks Runtime Upgrade** — Run smoke/full regression suite in dev/SQA with new runtime, identify breaking changes (PySpark APIs, libraries), document regressions before production rollout.

**Use Case 2: dbt Version Migration** — Generate domain-specific suites, validate DAG execution and data outputs, fix breaking changes (incremental_strategy syntax).

**Use Case 3: Repository Consolidation** — Baseline old repos, consolidate, compare model outputs to prove equivalence.

**Use Case 4: Infrastructure Changes** — Test new cluster configs with smoke suite, compare performance metrics, validate no execution failures.

**Use Case 5: Platform Health Checks** — Quarterly full regression suite to catch pipeline drift/rot, escalate failures to owners.

### Catalyst Skills for Regression Testing

**Skill: `generate-regression-suite`**
- Generate regression test suite configurations for bulk DAG execution
- Inputs: List of pipelines, suite type (smoke/full/domain), test tier (execution/validation)
- Outputs: Suite config (YAML), execution manifest, orchestration script

**Skill: `run-regression-suite`**
- Execute regression test suite and generate results report
- Inputs: Suite config, target environment, test mode
- Outputs: Test execution log, pass/fail summary, performance comparison, failure details

**Skill: `compare-regression-results`**
- Compare regression test results before/after platform change
- Inputs: Baseline report, current report, comparison criteria
- Outputs: Regression analysis report, newly failing pipelines, performance degradations, recommendations

---

### Existing Catalyst Skills for Testing

The following skills **already exist** in the Catalyst skills repository and should be leveraged as part of the testing strategy:

#### Unit & Integration Testing

| Skill | Testing Category | How to Use |
|-------|-----------------|------------|
| **`adding-dbt-unit-test`** | Unit Tests | Create dbt unit test YAML definitions with mocked inputs and expected outputs. Supports TDD workflow for dbt models. |
| **`unit-test-report`** | Unit Tests (Reporting) | Generate structured unit test reports documenting coverage, pass rates, and findings. Part of Phase 4 Build gate. |
| **`integration-test-report`** | Integration Tests (Reporting) | Document end-to-end integration test scenarios, performance results, and validation status. Phase 4 Build artifact. |

#### Lineage & Impact Testing

| Skill | Testing Category | How to Use |
|-------|-----------------|------------|
| **`column-lineage`** | Lineage & Impact Tests | Trace column-level lineage across transformation layers. Use during Phase 3 Design to document lineage, or Phase 8 Evolve to assess impact of schema changes. |
| **`parse-lineage`** | Lineage & Impact Tests | Parse SQL to trace lineage from inline queries or files. Produces lineage tables and Mermaid flowcharts. |
| **`downstream-impact-assessment`** | Lineage & Impact Tests | Assess downstream consumer impact from proposed changes with risk ratings and communication plan. Critical for Phase 8 Evolve. |

#### Performance & Scalability Testing

| Skill | Testing Category | How to Use |
|-------|-----------------|------------|
| **`optimize-databricks-job`** | Performance Tests | Scan DAB jobs for performance issues (concurrency, timeouts, cluster sizing, Photon). Applies DBX-PERF-* standards. |
| **`optimize-dbsql-query`** | Performance Tests | Analyze and optimize SQL queries for performance. Identifies bottlenecks and suggests improvements. |
| **`nfr-specification`** | Performance & Scalability Tests | Define non-functional requirements including performance SLOs, scalability targets, and reliability thresholds. Use to set test acceptance criteria. |

#### Observability

| Skill | Testing Category | How to Use |
|-------|-----------------|------------|
| **`setup-monitoring-and-logging`** | Observability Tests | Configure cluster log capture, Airflow callbacks, and UC Volume log destinations during build. Generates operational runbooks for log escalation. |
| **`runbook`** | Observability Tests | Generate operational runbooks with health checks, alert responses, escalation paths. Use to document expected monitoring behavior and validate configuration. |

#### Test Orchestration & Execution

| Skill | Testing Category | How to Use |
|-------|-----------------|------------|
| **`run-dbt-on-databricks`** | E2E Tests, Integration Tests | Execute dbt models locally, via bundle-deploy, or bundle-run. Three modes support different testing stages. |
| **`databricks-jobs`** | E2E Tests, Regression Tests | Create, configure, and execute Databricks Jobs. Essential for running regression test suites and bulk DAG execution. |
| **`connect-astro`** | Local Testing (Airflow) | Authenticate to Astronomer Cloud for local Airflow DAG testing. Required before running Astro CLI test commands. |

#### Data Contracts

| Skill | Testing Category | How to Use |
|-------|-----------------|------------|
| **`data-contract`** | Test Planning (all categories) | Define schema, SLAs, and quality rules that drive test generation. Use as input to AI test generation skills. |

#### Best Practices & Standards

| Skill | Testing Category | How to Use |
|-------|-----------------|------------|
| **`dbt-best-practices`** | All Testing Categories | Generation-time guidance for dbt projects including test coverage requirements, naming conventions, and mode-aware severity rules. References RFD 0008 SQL standards. |

**Note:** The proposed AI test generation skills complement existing skills by automating test code generation and coverage analysis.

### Advanced Testing Skills

| Skill | Testing Category | Capabilities | Status |
|-------|-----------------|-------------|--------|
| **`dbt-test`** (Hourglass) | Integration, Transformation Logic, Unit, Reconciliation | AI-powered test generator for **Hourglass dbt models**: analyzes dbt SQL, generates 8-25 test cases covering happy paths/NULL handling/edge cases, creates synthetic seed data, executes via pandas/PySpark, produces pytest scripts + JUnit XML + reports. Supports Jira AC integration and caching. **Use for Hourglass-specific testing.** | ✓ Existing (Hourglass plugin) |
| **`generate-data-tests`** (Catalyst) | Schema, Transformation Logic | AI test generator for **Catalyst data products**: takes data contracts as input, generates dbt schema tests (not_null, unique, accepted_values, relationships) and transformation logic tests. Produces dbt test YAML + SQL. **Use for Catalyst data products; simpler than dbt-test, focused on contract-driven testing.** | 🆕 Proposed |
| **`impact-assessment`** | Lineage & Impact | Traverses OpenLineage to identify downstream impacts of schema changes (column rename/drop/type change). Returns impacted datasets, columns, jobs, DAGs. | 🆕 Proposed |
| **`hourglass-macros-testing`** | Unit Tests, Macros | Creates dbt macros and tests for Hourglass platform. Supports custom singular tests, schema validation, audit macros. | ✓ Existing (Hourglass plugin) |

**Boundary clarification for dbt test generators:**
- **`dbt-test`** (Hourglass): Comprehensive test generator for Hourglass dbt models — analyzes SQL directly, generates pytest scripts with synthetic seeds, executes tests, produces JUnit XML. More complex, full-featured, Hourglass-specific.
- **`generate-data-tests`** (Catalyst): Contract-driven test generator for Catalyst data products — takes data contracts as input (schema + SLAs), generates dbt schema test YAML files. Simpler, focused on contract validation, framework-agnostic.

**When to use which:** If building a Catalyst data product with a data-contract.md artifact, invoke `generate-data-tests`. If working in Hourglass with dbt SQL models, invoke `dbt-test` for more comprehensive test coverage.

### 3. Local Development and Testing with Astronomer (Astro CLI)

Astro CLI (`astro dev`) provides local Airflow environments via Docker Compose for fast iteration before production deployment.

**Key Commands:**
- `astro dev start` — Start local Airflow
- `astro dev parse` — Validate DAG parsing
- `astro dev pytest` — Run pytest unit tests
- `astro dev run <dag_id>` — Execute DAG locally

**Benefits:** Pre-commit testing, rapid iteration, regression testing with production-like configuration, local test data management.

**Integration:** Proposed `generate-airflow-dag-tests` skill generates pytest tests that run via `astro dev pytest`. Pre-commit hooks enforce local test passage.

**CI/CD Integration Example:**

```yaml
# .github/workflows/test-dags.yml
name: Test Airflow DAGs
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Astro CLI
        run: curl -sSL install.astronomer.io | sudo bash -s
      
      - name: Start Astro environment
        run: astro dev start --wait
      
      - name: Parse DAGs
        run: astro dev parse
      
      - name: Run pytest
        run: astro dev pytest
      
      - name: Stop environment
        run: astro dev stop
```

**Platform Upgrade Testing**

When upgrading Airflow runtime (e.g., Airflow 2.7 → 2.9):

```bash
# 1. Update astro runtime version in Dockerfile
# Dockerfile: FROM cgregistry-aws.capgroup.com/astronomer/astro-runtime:11.5.0

# 2. Rebuild local environment
astro dev stop
astro dev start

# 3. Run full test suite
astro dev parse  # Check for deprecation warnings
astro dev pytest # Run all unit tests
astro dev run --all  # Execute all DAGs (regression test)

# 4. Compare results to baseline
# - Any new failures?
# - Performance regressions?
# - Deprecation warnings?

# 5. If all tests pass → proceed to SQA deployment
# 6. If failures → fix DAGs and re-test locally
```

#### Limitations and Considerations

**Local Environment Differences**
- Local runs use Docker resources (limited compute/memory)
- Production connectors (databases, S3, APIs) may not be accessible locally
- Need mock data sources or VPN access to dev databases

**Test Data Management**
- Maintain separate test datasets (small, representative samples)
- Avoid testing with full production data volumes locally
- Use data mocking for external API dependencies

**Environment Drift**
- Keep `astro-runtime` version in sync with production
- Regularly update provider packages to match production
- Document environment-specific configuration differences

---

## Alternatives

### Alternative 1: Off-the-Shelf Testing Tools Only

**Rejected because:** Still requires manual test authoring; doesn't reduce friction; generic tools don't encode investment data pipeline patterns; no lifecycle integration; no automated enforcement. **Note:** We still use standard testing tools (dbt tests, pytest) but layer AI generation and lifecycle integration on top.

### Alternative 2: Fully Automated Testing (No Human Review)

**Rejected because:** AI-generated tests need human validation for domain-specific edge cases; risk of false confidence; regulatory requirements demand human sign-off; engineers must understand tests to maintain them. **Note:** We automate test generation but require human review and sign-off.

### Alternative 3: Test Generation at Runtime

**Rejected because:** No version control for test definitions; no PR-based review workflow; harder to debug failures; doesn't integrate with standard CI/CD tooling.

## Impact

### Who Is Affected

| Stakeholder | Impact |
|------------|--------|
| **Data Engineers** | Must write tests for all data products; AI skills reduce manual effort but testing becomes mandatory |
| **Data Product Owners** | Must review and sign off on test coverage; gates in lifecycle ensure quality before production |
| **Data Platform Team** | Builds and maintains testing skills, patterns library, CI/CD enforcement; owns regression test suites for platform upgrades |
| **Platform Engineering** | Can confidently roll out platform upgrades (Databricks, dbt, infrastructure) with regression test validation; reduced risk of breaking production |
| **Consumers** | Higher data quality → fewer production incidents, more trust in data products |
| **Reviewers** | Automated test coverage reports reduce manual review burden |

### Migration Path

- **Existing products:** Critical-tier within 90 days, High-tier within 6 months, Medium/Low-tier within 12 months. Quarterly audits with escalation for non-compliance.
- **New products:** Testing standards apply to all products entering Phase 3 (Design) after publication. AI skills available immediately.

### Operational Changes

- **CI/CD:** Add test execution, coverage reporting, branch protection rules, and automated PR comments
- **Lifecycle gates:** Testing requirements integrated at each phase (test planning in Design, coverage validation in Build, sign-off in Validate, smoke tests in Publish, regression testing in Operate/Evolve)
- **Platform upgrades:** Run baseline regression suite before upgrade; post-upgrade validation in dev/SQA; production rollout only if regression rate < 5% and all Critical pipelines pass
- **Training:** Update Catalyst onboarding with testing module; patterns library documentation; monthly testing office hours
- **Metrics:** Track coverage by tier, production incidents, test-writing velocity, skill adoption, regression pass rates, and platform health

### Success Criteria (12 Months Post-Rollout)

- ✅ 100% of Critical/High-tier products meet testing standards
- ✅ 50% reduction in production data quality incidents
- ✅ 80% reduction in test coverage audit violations
- ✅ 30% faster PR review cycle time (automated validation)
- ✅ Platform regression suites cover all major domains; >95% pass rate before production upgrades
- ✅ Zero production incidents from platform upgrades (caught in regression testing)
- ✅ Majority of engineers use AI test generation skills and Astro CLI for DAG testing

## Open Questions

1. **Tool standardization:** Should we mandate specific testing tools or allow teams to choose? 
   - **Recommendation:** Standardize on dbt tests (for schema) + pytest (for transformation logic) + Astro CLI (for Airflow DAG testing) to enable skill reusability and consistent patterns across products.

2. **Test data management:** Where do test fixtures live? How are they versioned?
   - **Recommendation:** Fixtures in `tests/fixtures/` directory, versioned with pipeline code. Skills generate fixtures as part of test scaffolding.

3. **Regression suite ownership:** Who maintains platform regression test suites as pipelines are added/deprecated?
   - **Recommendation:** Platform team owns regression suite curation. AI skill auto-detects new Critical/High-tier products and suggests additions to suite.

4. **Regression test frequency:** How often should platform-level regression suites run?
   - **Recommendation:** Before every platform upgrade (mandatory); quarterly health checks (proactive monitoring); on-demand for large-scale changes (repository migrations, infra changes).
