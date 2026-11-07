import json
import shutil
import subprocess
import zipfile

from tests.challenges.conftest import repo_root


def test_learner_and_instructor_zips_exclude_authoring_paths(tmp_path):
    sandbox = tmp_path / "client"
    (sandbox / "scripts").mkdir(parents=True)
    for name in ["package-v2.sh", "package-v2.py", "separate-v2-stretch-answers.py"]:
        shutil.copy2(repo_root() / "scripts" / name, sandbox / "scripts" / name)
    files = {
        "challenges/v2/README.md": "learner",
        "challenges/v2/manifest.json": json.dumps({"source_revision": "fixture", "source_inventory": "designer/reviews/v2-source-inventory.json"}),
        "challenges/courseware/facilitator/answers.md": "course answers",
        ".devcontainer/authoring/devcontainer.json": "{}",
        ".devcontainer/devcontainer.json": "{}",
        "designer/generated/summary.md": "generated",
        "designer/reviews/review.md": "review",
    }
    for rel, text in files.items():
        (sandbox / rel).parent.mkdir(parents=True, exist_ok=True)
        (sandbox / rel).write_text(text)
    # The authoring link is pruned before symlink classification.
    (sandbox / "challenges/courseware/live-course").symlink_to(tmp_path / "outside")
    result = subprocess.run(["bash", "scripts/package-v2.sh"], cwd=sandbox, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    for name in ["DataCreators-challenges-v2-learner.zip", "DataCreators-challenges-v2-instructor.zip"]:
        names = zipfile.ZipFile(sandbox / "designer/dist" / name).namelist()
        assert "challenges/v2/README.md" in names
        assert ".devcontainer/devcontainer.json" in names
        assert not [n for n in names if n.startswith(("challenges/courseware/", ".devcontainer/authoring/"))], names
