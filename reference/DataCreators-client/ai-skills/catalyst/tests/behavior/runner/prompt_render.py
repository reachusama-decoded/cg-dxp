"""Shared rubric-prompt render helpers.

Used by both the dispatch path (rendering grade text into status.json /
the dashboard) and the issues path (rendering rubric tables into issue
bodies). Single source of truth keeps the two surfaces consistent —
without it, a reviewer comparing dashboard output to filed issues sees
spurious differences.
"""
from __future__ import annotations
import re

# Quotes shorter than 60 chars (e.g., `[TBD]`, `[fill in]`) are kept
# verbatim — those are part of the question's actual content, not bloat.
_LONG_QUOTED_SPAN = re.compile(r"'[^']{60,}?'")


def shorten_criterion_prompt(prompt: str) -> str:
    """Collapse the auto-generated bloat in `request_addressed`-style prompts.

    Bootstrap rubrics include a `request_addressed` criterion whose prompt
    embeds the entire skill description in single quotes — often pre-
    truncated mid-word in the source YAML. Result: the criterion's intent
    drowns in a long inline quote when rendered in markdown tables and
    grade lines. The full prompt still goes to the judge (this is render
    only); long embedded quotes are substituted with a short placeholder.
    """
    text = (prompt or "").strip().replace("\n", " ")
    return _LONG_QUOTED_SPAN.sub("<skill description>", text)
