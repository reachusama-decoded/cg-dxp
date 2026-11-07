"""
TestCase dataclass and seed-fixer wrappers for the dbt-unit-test agent skill.

The agent (SKILL.md / Copilot) handles all LLM-based analysis and test-case
generation.  This module provides only:

  - ``TestCase``            — the canonical dataclass used throughout the pipeline
  - ``AITestCaseGenerator`` — thin static wrappers around ``seed_fixer`` utilities
                              called by ``run_from_json.py`` after the agent has
                              produced the JSON test-case file.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from engine.generation.seed_fixer import (
    backfill_base_cte_seeds,
    parse_sql_join_structure,
    fix_seed_column_gaps,
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TestCase:
    test_id: str
    description: str
    category: str            # transformation | null_check | dedup | cast | filter | join
    input_scenario: str      # human-readable description of the input
    expected_behavior: str   # what the output must satisfy
    input_data: dict[str, list[dict[str, Any]]]   # ref_or_source_name → rows
    expected_output: list[dict[str, Any]]          # expected result rows
    pandas_query: str        # expression for DataFrame.query() to validate result
    tags: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Generator (seed-fixer wrappers only — LLM generation is handled by the agent)
# ---------------------------------------------------------------------------

class AITestCaseGenerator:
    """
    Static-method wrapper around seed_fixer utilities.

    All LLM-based analysis and test-case generation is handled by the
    Copilot agent (SKILL.md).  This class provides only the seed-fixing
    helpers called by ``run_from_json.py`` after the agent has produced
    the JSON test-case file.
    """

    @staticmethod
    def _backfill_base_cte_seeds(test_cases, raw_sql):
        return backfill_base_cte_seeds(test_cases, raw_sql)

    @staticmethod
    def _parse_sql_join_structure(raw_sql):
        return parse_sql_join_structure(raw_sql)

    @staticmethod
    def _fix_seed_column_gaps(test_cases, raw_sql=""):
        return fix_seed_column_gaps(test_cases, raw_sql)
