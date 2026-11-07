from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    name: str
    args: dict[str, Any] = Field(default_factory=dict)
    result: Any = None
    is_error: bool = False


class RunResult(BaseModel):
    output: str
    tool_calls: list[ToolCall]
    sub_skills: list[str] = Field(default_factory=list)
    # Count of orchestrator self-invocations — Skill({skill: <itself>})
    # tool calls. Surfaced separately from sub_skills so a SequenceFailure
    # can name the AICAT-127 anti-pattern instead of just reporting
    # missing expected sub-skills. See runner/sub_skill_detection.py.
    self_invocations: int = 0
    duration_s: float
    input_tokens: int
    output_tokens: int
    error: Optional[str] = None

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class MaxStepsExceeded(RuntimeError):
    """Raised when a runner exceeds its max_steps budget."""
    def __init__(self, message: str, result: RunResult):
        super().__init__(message)
        self.result = result


CacheKey = tuple[str, str]  # (case_id, mode) — used by CachingRunner / CachedRunner


class SkillRunner(ABC):
    @abstractmethod
    def run(
        self,
        skill_path: Path,
        arguments: str,
        max_steps: Optional[int] = None,
        system_override: Optional[str] = None,
        cache_key: Optional[CacheKey] = None,
    ) -> RunResult:
        ...
