from tests.challenges.conftest import repo_root


def test_pytest_ini_collects_challenge_suites() -> None:
    cfg = (repo_root() / "pytest.ini").read_text()
    assert "tests/challenges/offline" in cfg
    assert "tests/challenges/live" in cfg


def test_sqlfluff_ignores_challenges() -> None:
    ig = (repo_root() / ".sqlfluffignore").read_text()
    assert "challenges/" in ig


def test_dbt_ignores_challenge_solutions() -> None:
    ig = (repo_root() / ".dbtignore").read_text()
    assert "challenges/**/solution/**" in ig


def test_no_guide_uses_the_mise_wrapper_for_dbt_work() -> None:
    # Why: the challenges teach real dbt, so every guide's dbt/seed command must be raw
    # `dbt ...`; only the verify gate and reset stay on mise. This was enforced for
    # challenge 02 alone, and challenge 03 quietly drifted -- it told trainees to run
    # `mise run challenge:seed 02` for its raw-feed setup. Enforce it for every guide so
    # a new or edited challenge cannot reintroduce the wrapper.
    wrappers = ("mise run challenge:seed", "mise run challenge:dbt", "mise run dbt:")
    for guide in sorted((repo_root() / "challenges").glob("v1/*/README.md")):
        text = guide.read_text()
        for wrapper in wrappers:
            assert wrapper not in text, (
                f"{guide.relative_to(repo_root())} runs dbt through the mise wrapper "
                f"('{wrapper}'); use a raw `dbt ...` command instead"
            )


def test_challenge_run_ledger_and_brief_are_wired() -> None:
    # Why: agent runs of the challenges are recorded as ONE ledger row plus (only when a root
    # cause was fixed) an RCA -- never a per-run document, which would be mostly "everything
    # passed" and scale with the number of runs. The brief carries the scope limits and the
    # artifact-based audit steps; without it an agent can report PASS for a step it quietly
    # worked around. Keep all three wired so the convention survives.
    root = repo_root()
    ledger = root / "docs" / "challenge-runs.md"
    brief = root / "docs" / "challenge-run-brief.md"
    assert ledger.exists(), "docs/challenge-runs.md (the run ledger) must exist"
    assert brief.exists(), "docs/challenge-run-brief.md (the trainee brief) must exist"

    # The ledger's value is comparability, so the fixed columns must stay.
    header = ledger.read_text()
    # "Host OS" is load-bearing: the devcontainer is always Linux, so only the host varies,
    # and this repo has host-specific defects (see the profiles-symlink-windows RCA) plus
    # Windows-only Docker daemon crashes under concurrent runs.
    for column in ("Date", "Ch", "Host OS", "Model", "Result", "Blockers", "RCA", "Commit"):
        assert f"| {column} " in header or f" {column} |" in header, (
            f"ledger must keep the '{column}' column; rows are only useful if comparable"
        )

    # The brief must keep the audit steps -- prompt rules alone are not verification.
    brief_text = brief.read_text()
    assert "invocation_command" in brief_text, "brief must keep the dbt.log command audit"
    assert "shasum" in brief_text, "brief must keep the tamper/scope checksum audit"

    # The workflow lives in a SKILL (loaded on demand), not in the always-loaded
    # instructions. Why: the instructions are read by every session in this repo, including
    # trainees working through a challenge -- and step 1 of a validation run is
    # `challenge:reset`, which deletes their authored work. A trainee saying "help me run
    # challenge 02" must not be able to trigger that.
    # Path matters: Copilot auto-discovers PROJECT skills only from .github/skills,
    # .claude/skills or .agents/skills. A bare skills/ at the repo root is never loaded.
    skill = root / ".github" / "skills" / "challenge-trainee-runs" / "SKILL.md"
    assert skill.exists(), (
        "the maintainer workflow must ship as a skill in .github/skills/ to be discovered"
    )
    assert not (root / "skills").exists(), (
        "a bare skills/ dir at the repo root is not a discovery path; use .github/skills/"
    )
    skill_text = skill.read_text()
    assert skill_text.startswith("---"), "skill needs frontmatter for on-demand discovery"
    assert "description:" in skill_text.split("---")[1], "skill needs a description to match on"
    assert "docs/challenge-run-brief.md" in skill_text
    assert "docs/challenge-runs.md" in skill_text

    # The always-loaded instructions keep only the GUARD, and must point at the skill.
    instructions = (root / ".github" / "copilot-instructions.md").read_text()
    assert "challenge-trainee-runs" in instructions, (
        "instructions must route validation requests to the skill"
    )
    assert "challenge:reset" in instructions, (
        "the reset guard must stay always-loaded; it protects every trainee session"
    )
