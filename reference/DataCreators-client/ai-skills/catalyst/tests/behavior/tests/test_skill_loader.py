# tests/behavior/tests/test_skill_loader.py
from pathlib import Path
import pytest

from tests.behavior.runner.skill_loader import LoadedSkill, load_skill

FIXTURES = Path(__file__).parent / "fixtures"

class TestLoadSkill:
    def test_parses_frontmatter_and_body(self):
        skill = load_skill(FIXTURES / "tiny_skill.md", arguments="hello world")
        assert skill.name == "tiny-skill"
        assert skill.description == "A tiny skill for tests."
        assert skill.allowed_tools == ["Read", "Bash"]
        assert "Echo the argument: hello world" in skill.body

    def test_substitutes_arguments_token(self):
        skill = load_skill(FIXTURES / "tiny_skill.md", arguments="x")
        assert "$ARGUMENTS" not in skill.body
        assert "Echo the argument: x" in skill.body

    def test_resolves_directory_to_skill_md(self, tmp_path: Path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: my-skill\ndescription: dir skill.\nargument-hint: x\nallowed-tools: Read\n---\n\nDo $ARGUMENTS.\n"
        )
        skill = load_skill(skill_dir, arguments="test arg")
        assert skill.name == "my-skill"
        assert "test arg" in skill.body

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_skill(tmp_path / "nope.md", arguments="")

    def test_missing_frontmatter_raises(self, tmp_path: Path):
        bad = tmp_path / "bad.md"
        bad.write_text("# no frontmatter\n")
        with pytest.raises(ValueError, match="frontmatter"):
            load_skill(bad, arguments="")
