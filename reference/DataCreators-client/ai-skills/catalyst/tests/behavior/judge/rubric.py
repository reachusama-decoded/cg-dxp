"""LLM-as-judge rubric scoring via claude-agent-sdk.

Auth comes from Claude Code (or ANTHROPIC_API_KEY if set). One agent call
per case, no tools needed — the judge reads the output and emits a single
JSON block.
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from typing import Any

import anyio
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

from tests.behavior.cases import Rubric
from tests.behavior.config import Config

JUDGE_SYSTEM_PROMPT = """\
You are a strict rubric grader for AI skill outputs.

You will be given:
1. A short description of the skill that produced the output.
2. The actual output the skill produced.
3. A list of scoring criteria, each with an id and a question.

For each criterion, return a score in [0.0, 1.0] and a one-sentence rationale.
Reply with a single JSON object and nothing else, in this shape:

{
  "criteria": [
    {"id": "<id>", "score": <float 0..1>, "rationale": "<one sentence>"}
  ]
}

Be strict. A score of 1.0 means the output fully and unambiguously meets the
criterion. A score of 0.0 means it does not meet the criterion at all.
"""

JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


@dataclass
class CriterionGrade:
    id: str
    score: float
    rationale: str


@dataclass
class Verdict:
    passed: bool
    weighted_score: float
    grades: list[CriterionGrade] = field(default_factory=list)
    judge_input_tokens: int = 0
    judge_output_tokens: int = 0


class RubricJudge:
    """Scores a runner's output against a rubric using claude-agent-sdk.

    query_fn is injectable so tests can substitute a fake without touching
    the SDK module-level import.
    """

    def __init__(self, *, config: Config, query_fn: Any = query):
        self.config = config
        self._query_fn = query_fn

    def score(self, *, rubric: Rubric, output: str, skill_description: str) -> Verdict:
        criterion_payload = [
            {"id": c.id, "question": c.prompt} for c in rubric.criteria
        ]
        user_message = json.dumps(
            {
                "skill_description": skill_description,
                "output": output,
                "criteria": criterion_payload,
            },
            indent=2,
        )

        # Judge has no tools at all — it only reads the runner output and
        # emits a JSON verdict. permission_mode stays default; nothing should
        # ever request a tool here.
        options_kwargs: dict[str, Any] = {
            "system_prompt": JUDGE_SYSTEM_PROMPT,
            "max_turns": 1,
            "disallowed_tools": ["Bash", "Read", "Edit", "Write", "Grep", "Glob"],
            "permission_mode": "default",
        }
        if self.config.judge_model:
            options_kwargs["model"] = self.config.judge_model
        options = ClaudeAgentOptions(**options_kwargs)

        async def _drive() -> tuple[str, int, int]:
            text_chunks: list[str] = []
            input_tokens = 0
            output_tokens = 0
            async for msg in self._query_fn(prompt=user_message, options=options):
                if isinstance(msg, AssistantMessage):
                    if msg.usage:
                        input_tokens += int(msg.usage.get("input_tokens", 0) or 0)
                        output_tokens += int(msg.usage.get("output_tokens", 0) or 0)
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            text_chunks.append(block.text)
                elif isinstance(msg, ResultMessage):
                    if getattr(msg, "usage", None):
                        usage = msg.usage
                        input_tokens = int(usage.get("input_tokens", input_tokens) or input_tokens)
                        output_tokens = int(usage.get("output_tokens", output_tokens) or output_tokens)
            return "".join(text_chunks), input_tokens, output_tokens

        text, in_tok, out_tok = anyio.run(_drive)

        m = JSON_BLOCK_RE.search(text)
        if not m:
            raise ValueError(f"Judge returned no JSON block: {text!r}")
        payload = json.loads(m.group(0))
        grades = {
            g["id"]: CriterionGrade(
                id=g["id"], score=float(g["score"]), rationale=g["rationale"]
            )
            for g in payload["criteria"]
        }

        weighted = 0.0
        ordered_grades: list[CriterionGrade] = []
        for c in rubric.criteria:
            if c.id not in grades:
                raise ValueError(f"Judge response missing criterion {c.id!r}")
            grade = grades[c.id]
            weighted += grade.score * c.weight
            ordered_grades.append(grade)

        return Verdict(
            passed=weighted >= rubric.threshold,
            weighted_score=weighted,
            grades=ordered_grades,
            judge_input_tokens=in_tok,
            judge_output_tokens=out_tok,
        )
