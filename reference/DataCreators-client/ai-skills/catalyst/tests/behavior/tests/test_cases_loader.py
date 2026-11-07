# tests/behavior/tests/test_cases_loader.py
from pathlib import Path
import pytest
import shutil

from tests.behavior.cases import load_cases

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def cases_tree(tmp_path: Path) -> Path:
    (tmp_path / "execution" / "discover-data").mkdir(parents=True)
    shutil.copy(FIXTURES / "artifact_case.yaml",
                tmp_path / "execution" / "discover-data" / "case-01.yaml")
    (tmp_path / "orchestrators" / "dplc-discovery").mkdir(parents=True)
    shutil.copy(FIXTURES / "behavior_case.yaml",
                tmp_path / "orchestrators" / "dplc-discovery" / "case-01.yaml")
    return tmp_path


class TestLoadCases:
    def test_discovers_yaml_under_tree(self, cases_tree: Path):
        cases = load_cases(cases_tree)
        assert len(cases) == 2
        ids = {c.id for c in cases}
        assert ids == {
            "discover-data.case-01-happy-path",
            "dplc-discovery.case-01-behavior",
        }

    def test_ignores_non_yaml_files(self, cases_tree: Path):
        (cases_tree / "execution" / "discover-data" / "README.md").write_text("# notes")
        cases = load_cases(cases_tree)
        assert len(cases) == 2

    def test_ignores_fixtures_subdirectory(self, cases_tree: Path):
        fixtures_dir = cases_tree / "execution" / "discover-data" / "fixtures"
        fixtures_dir.mkdir()
        (fixtures_dir / "prior.yaml").write_text("not a case file")
        cases = load_cases(cases_tree)
        assert len(cases) == 2

    def test_duplicate_ids_raises(self, cases_tree: Path, tmp_path: Path):
        shutil.copy(FIXTURES / "artifact_case.yaml",
                    cases_tree / "execution" / "discover-data" / "case-02.yaml")
        with pytest.raises(ValueError, match="Duplicate case id"):
            load_cases(cases_tree)

    def test_invalid_yaml_message_includes_path(self, tmp_path: Path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("id: x\ntype: bogus\nskill: y\ninput:\n  arguments: ''\n")
        with pytest.raises(ValueError, match=str(bad)):
            load_cases(tmp_path)


class TestRunReference:
    """Run primitive: a case can reference a shared (skill, input) Run by
    id instead of inlining. Two cases referencing the same Run produce
    identical transcript_ids → share a cache entry → only one agent
    invocation."""

    def test_case_resolves_run_reference(self, tmp_path: Path):
        import textwrap
        (tmp_path / "discover").mkdir()
        (tmp_path / "discover" / "run.yaml").write_text(textwrap.dedent("""\
            type: run
            id: discover.shared-run
            skill: skills/discover-data
            input:
              arguments: "find employee tables"
        """))
        (tmp_path / "discover" / "case-01.yaml").write_text(textwrap.dedent("""\
            id: discover.case-01
            type: artifact
            run: discover.shared-run
            structural_checks: [non_empty_output]
            rubric:
              threshold: 0.5
              criteria:
                - id: only
                  weight: 1.0
                  prompt: anything? Score 0-1.
        """))
        cases = load_cases(tmp_path)
        assert len(cases) == 1
        c = cases[0]
        assert c.skill == "skills/discover-data"
        assert c.input.arguments == "find employee tables"

    def test_two_cases_sharing_run_resolve_identically(self, tmp_path: Path):
        import textwrap
        (tmp_path / "run.yaml").write_text(textwrap.dedent("""\
            type: run
            id: shared
            skill: skills/x
            input: {arguments: "Q"}
        """))
        for i in (1, 2):
            (tmp_path / f"case-0{i}.yaml").write_text(textwrap.dedent(f"""\
                id: x.case-0{i}
                type: artifact
                run: shared
                structural_checks: [non_empty_output]
                rubric:
                  threshold: 0.5
                  criteria:
                    - id: only
                      weight: 1.0
                      prompt: anything? Score 0-1.
            """))
        cases = load_cases(tmp_path)
        skills = {c.skill for c in cases}
        argstrs = {c.input.arguments for c in cases}
        assert skills == {"skills/x"}
        assert argstrs == {"Q"}

    def test_unknown_run_id_raises(self, tmp_path: Path):
        import textwrap
        (tmp_path / "case.yaml").write_text(textwrap.dedent("""\
            id: x.case-01
            type: artifact
            run: nope-does-not-exist
            structural_checks: [non_empty_output]
            rubric:
              threshold: 0.5
              criteria:
                - id: only
                  weight: 1.0
                  prompt: "anything? Score 0-1."
        """))
        with pytest.raises(ValueError, match="unknown run"):
            load_cases(tmp_path)

    def test_duplicate_run_id_raises(self, tmp_path: Path):
        import textwrap
        for name in ("a.yaml", "b.yaml"):
            (tmp_path / name).write_text(textwrap.dedent("""\
                type: run
                id: dup
                skill: skills/x
                input: {arguments: ""}
            """))
        with pytest.raises(ValueError, match="Duplicate run id"):
            load_cases(tmp_path)
