"""Render-time prompt shortener tests.

The bootstrap rubric generator embedded the entire skill description
inside the request_addressed criterion prompt, often truncated mid-word.
At render time we collapse those long single-quoted spans so issue
bodies and grade lines stay readable. Judge prompts pass through intact.
"""
from __future__ import annotations

from tests.behavior.runner.prompt_render import shorten_criterion_prompt


class TestShortenCriterionPrompt:
    def test_collapses_long_embedded_quote(self):
        prompt = (
            "Does the output meaningfully address the request described by the skill: "
            "'Query Unity Catalog for tables relevant to a data product. Use during Phase 2 "
            "Discovery to inventory available sources before writing the fe'? Score 0-1."
        )
        out = shorten_criterion_prompt(prompt)
        assert "Query Unity Catalog" not in out
        assert "<skill description>" in out
        assert out.startswith("Does the output meaningfully address")
        assert out.endswith("Score 0-1.")

    def test_short_quotes_unchanged(self):
        prompt = "Output free of [TBD], [fill in], lorem-ipsum stubs? Score 0-1."
        # No long embedded quote — prompt should be untouched.
        assert shorten_criterion_prompt(prompt) == prompt

    def test_format_conformant_unchanged(self):
        prompt = "Does the output follow the structure the skill prescribes (sections, tables, fields, etc.)? Score 0-1."
        assert shorten_criterion_prompt(prompt) == prompt

    def test_collapses_newlines_and_strips(self):
        prompt = "  multi-line\n  prompt  "
        # strip outer whitespace + newlines collapsed to single spaces
        assert shorten_criterion_prompt(prompt) == "multi-line   prompt"

    def test_empty_or_none(self):
        assert shorten_criterion_prompt("") == ""
        assert shorten_criterion_prompt(None) == ""  # type: ignore[arg-type]
