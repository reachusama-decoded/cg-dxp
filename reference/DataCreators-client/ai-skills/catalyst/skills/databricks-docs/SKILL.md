---
name: databricks-docs
description: |
  Databricks documentation reference via llms.txt index. Use when other skills do not cover
  a topic, looking up unfamiliar Databricks features, or needing authoritative docs on APIs,
  configurations, or platform capabilities.
  Catalyst trigger phrases: "fetch Databricks docs", "look up Databricks reference", "Databricks documentation lookup".
allowed-tools: Read Bash Write Edit WebFetch
metadata:
  tier: capability
  lifecycle-phase: cross-cutting
  dependencies: []
  consumes: []
  shared-components:
    core: []
    platforms: [databricks]
  standards: []
  upstream-source: databricks-solutions/ai-dev-kit/databricks-skills/databricks-docs
  upstream-commit: 8cb4456543d6413e8a12923d4d4b5394fea89b25
  upstream-license: Databricks (custom — see third-party/LICENSE-databricks.md)
  catalyst-modifications: |
    Modified by Capital Group on 2026-05-14:
    - dropped MCP tool references (Catalyst policy); replaced action guidance with
      "invoke the corresponding Python function in skills/clients/databricks_tools_core/"
    - removed references to MCP tools for actions (execute_sql, manage_pipeline, etc.)
    - added Catalyst trigger phrases in description
---

> _Modified from `databricks-solutions/ai-dev-kit/databricks-skills/databricks-docs` by Capital Group on 2026-05-14. See `metadata.catalyst-modifications` for the change set._

# Databricks Documentation Reference

This skill provides access to the complete Databricks documentation index via llms.txt - use it as a **reference resource** to supplement other skills.

## Role of This Skill

This is a **reference skill**, not an action skill. Use it to:

- Look up documentation when other skills don't cover a topic
- Get authoritative guidance on Databricks concepts and APIs
- Find detailed information to inform how you call Python functions in `skills/clients/databricks_tools_core/`
- Discover features and capabilities you may not know about

**Always prefer the Python SDK functions in `skills/clients/databricks_tools_core/` for actions** and **load specific skills for workflows** (databricks-python-sdk, etc.). Use this skill when you need reference documentation.

## How to Use

Fetch the llms.txt documentation index:

**URL:** `https://docs.databricks.com/llms.txt`

Use WebFetch to retrieve this index, then:

1. Search for relevant sections/links
2. Fetch specific documentation pages for detailed guidance
3. Apply what you learn using the appropriate Python SDK functions

## Documentation Structure

The llms.txt file is organized by category:

- **Overview & Getting Started** - Basic concepts and tutorials
- **Data Engineering** - Lakeflow, Spark, Delta Lake, pipelines
- **SQL & Analytics** - Warehouses, queries, dashboards
- **AI/ML** - MLflow, model serving, GenAI
- **Governance** - Unity Catalog, permissions, security
- **Developer Tools** - SDKs, CLI, APIs, Terraform

## Example: Complementing Other Skills

**Scenario:** User wants to configure a Delta Live Tables pipeline

1. Load `databricks-bundles` or `databricks-jobs` skill for workflow patterns
2. Use this skill to fetch docs if you need clarification on specific DLT features
3. Invoke the corresponding Python function in `skills/clients/databricks_tools_core/dabs/` to create the resource

**Scenario:** User asks about an unfamiliar Databricks feature

1. Fetch llms.txt to find relevant documentation
2. Read the specific docs to understand the feature
3. Determine which skill and `databricks_tools_core` functions apply, then use them

## Related Skills

- **[databricks-python-sdk](../databricks-python-sdk/SKILL.md)** - SDK patterns for programmatic Databricks access
- **[databricks-unity-catalog](../databricks-unity-catalog/SKILL.md)** - Governance and catalog management
- **[databricks-execution-compute](../databricks-execution-compute/SKILL.md)** - Execution modes and compute management
