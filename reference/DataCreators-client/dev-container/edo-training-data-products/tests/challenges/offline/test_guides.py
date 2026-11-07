import pytest

from tests.challenges.conftest import repo_root

# Challenges 02-04 must ship the ported pedagogical guide (converted from the preflight
# CHALLENGES*.md sources), not a thin operational stub. 00 is intentionally reframed for the
# devcontainer (see test_ch00) and 01 is a verbatim guide port, so they are not covered here.
# This guards the regression where a guide requiring transformation was shortcut to a stub.
GUIDES = {
    "02-dbt-pipeline": ("staging", "source", "mart"),
    "03-airflow-orchestration": ("dag", "freshness", "publish"),
    "04-atlas-capstone": ("source", "domain", "consumer"),
}


@pytest.mark.parametrize("name,terms", GUIDES.items())
def test_challenge_guide_is_substantive(name: str, terms: tuple[str, ...]) -> None:
    readme = (repo_root() / "challenges" / "v1" / name / "README.md").read_text()

    assert len(readme) >= 6000, (
        f"challenges/{name}/README.md is only {len(readme)} bytes — this looks like a stub. "
        "Port the preflight CHALLENGES*.md guide (strip preflight-runner framing, swap commands "
        "for `mise run challenge:*`, wrap Solutions in <details>); do not summarize it away."
    )

    headers = sum(1 for line in readme.splitlines() if line.lstrip().startswith("#"))
    assert headers >= 4, (
        f"challenges/{name}/README.md has only {headers} section headers — the guide's "
        "pedagogical section structure (Concept / Challenge / How to check ...) is missing."
    )

    low = readme.lower()
    missing = [t for t in terms if t.lower() not in low]
    assert not missing, f"challenges/{name}/README.md is missing key concepts: {missing}"


def test_guides_have_no_preflight_runner_framing() -> None:
    # The port must strip preflight-only framing. These tokens must not survive into the guides.
    banned = ["verify-with-databricks.sh", "START_HERE", "RUN.md", "Preflight note", "\\newpage"]
    for name in GUIDES:
        text = (repo_root() / "challenges" / "v1" / name / "README.md").read_text()
        hits = [b for b in banned if b in text]
        assert not hits, f"challenges/{name}/README.md still contains preflight-runner framing: {hits}"
