"""Deterministic fake runner+judge for offline tests / fake-mode CLI runs.

Both the CLI's `BEHAVIOR_TESTS_USE_FAKE_RUNNER=1` path and the conftest
pytest fixtures use these — keeping them in one place stops the two
copies from drifting.

The runner emits a single AssistantMessage with a structurally-valid
"Discovered Tables" markdown block; the judge returns score=1.0 with
"fake" rationale for every criterion in the prompt.
"""
from __future__ import annotations
import json
from typing import Any, AsyncIterator

from claude_agent_sdk import AssistantMessage, TextBlock


_FAKE_OUTPUT = (
    "# Discovered Tables\n\n"
    "| Schema | Table | Row Count | Key Columns | Relevance |\n"
    "|---|---|---|---|---|\n"
    "| test | cg_employee_v4 | 1000 | id, name | HIGH |\n"
)


async def fake_runner_query(prompt: str, options: Any = None) -> AsyncIterator[Any]:  # noqa: ARG001
    """Async-iterator factory that mimics claude-agent-sdk's query()."""
    yield AssistantMessage(
        content=[TextBlock(text=_FAKE_OUTPUT)],
        model="fake",
        usage={"input_tokens": 1, "output_tokens": 1},
    )


async def fake_judge_query(prompt: str, options: Any = None) -> AsyncIterator[Any]:  # noqa: ARG001
    """Async-iterator factory that returns a passing verdict for any rubric."""
    criteria = json.loads(prompt).get("criteria", [])
    payload = {
        "criteria": [
            {"id": c["id"], "score": 1.0, "rationale": "fake"} for c in criteria
        ]
    }
    yield AssistantMessage(
        content=[TextBlock(text=json.dumps(payload))],
        model="fake",
        usage={"input_tokens": 1, "output_tokens": 1},
    )
