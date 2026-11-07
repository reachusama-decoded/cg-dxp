#!/usr/bin/env python3
"""
Prepare feature branch with generated artifacts for PR submission.

Copies generated source-aligned artifacts to the correct locations in
casper-pipelines (ingestion) or casper-im-foundation (curation) repos,
creates a feature branch, commits, and pushes to remote.

Supports batch mode: multiple artifact directories → single branch.

Uses separate "working" repos for check-ins (workspace/working/repos/)
to keep reference repos (workspace/reference/repos/) pristine on main.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Tuple


# Repo locations
REFERENCE_REPOS_PATH = Path("workspace/reference/repos")
WORKING_REPOS_PATH = Path("workspace/working/repos")

# Repo names and their GitHub URLs (HTTPS - SSH is blocked)
REPOS = {
    "pipelines": {
        "name": "casper-pipelines",
        "url": "https://github.com/cg-open-itg/casper-pipelines.git",
    },
    "im-foundation": {
        "name": "casper-im-foundation",
        "url": "https://github.com/cg-open-itg/casper-im-foundation.git",
    },
}


def run_git(repo_path: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a git command in the specified repo."""
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        print(f"Git error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result


def get_default_branch(repo_path: Path) -> str:
    """Get the default branch name (main or master)."""
    result = run_git(repo_path, "symbolic-ref", "refs/remotes/origin/HEAD", check=False)
    if result.returncode == 0:
        return result.stdout.strip().split("/")[-1]
    
    for branch in ["main", "master"]:
        result = run_git(repo_path, "rev-parse", "--verify", f"origin/{branch}", check=False)
        if result.returncode == 0:
            return branch
    
    return "main"


def check_clean_working_tree(repo_path: Path) -> bool:
    """Check if working tree is clean."""
    result = run_git(repo_path, "status", "--porcelain", check=False)
    return len(result.stdout.strip()) == 0


def ensure_working_repo(repo_key: str) -> Path:
    """
    Ensure working repo exists. Clone from remote if not present.
    Returns path to working repo.
    """
    repo_info = REPOS[repo_key]
    repo_name = repo_info["name"]
    repo_url = repo_info["url"]
    
    working_path = WORKING_REPOS_PATH / repo_name
    
    if working_path.exists():
        print(f"✓ Working repo exists: {working_path}")
        return working_path
    
    # Shallow clone for speed (only need latest commit to branch from)
    print(f"Cloning {repo_name} to working directory (shallow)...")
    WORKING_REPOS_PATH.mkdir(parents=True, exist_ok=True)
    
    result = subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(working_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error cloning repo: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    print(f"✓ Cloned {repo_name} to {working_path}")
    return working_path


def collect_pipelines_files(
    artifact_dirs: List[Path],
    repo_path: Path,
    process_domain: str,
) -> List[Tuple[Path, Path]]:
    """
    Collect all ingestion files from multiple artifact directories.
    Returns list of (source, destination) tuples.
    """
    files_to_copy = []
    
    for artifact_dir in artifact_dirs:
        ingestion_src = artifact_dir / "ingestion"
        if not ingestion_src.exists():
            print(f"Warning: No ingestion folder in {artifact_dir}, skipping")
            continue
        
        # Derive process_name from artifact dir name
        process_name = artifact_dir.name
        dest_dir = repo_path / "dags" / "ingestion" / process_domain / process_name
        
        # Find ingestion YAML files
        for yml_file in ingestion_src.glob("*.yml"):
            if yml_file.name == "dq.yml":
                files_to_copy.append((yml_file, dest_dir / f"{process_name}.dq.yml"))
            elif yml_file.name != "source.yml":
                files_to_copy.append((yml_file, dest_dir / f"{process_name}.yml"))
        
        # Pipeline.py
        pipeline_file = ingestion_src / "pipeline.py"
        if pipeline_file.exists():
            files_to_copy.append((pipeline_file, dest_dir / "pipeline.py"))
    
    return files_to_copy


def collect_im_foundation_files(
    artifact_dirs: List[Path],
    repo_path: Path,
    dc_tag: str,
) -> List[Tuple[Path, Path]]:
    """
    Collect all curation files from multiple artifact directories.
    Returns list of (source, destination) tuples.
    """
    files_to_copy = []
    
    for artifact_dir in artifact_dirs:
        curation_src = artifact_dir / "curation-emr"
        if not curation_src.exists():
            print(f"Warning: No curation-emr folder in {artifact_dir}, skipping")
            continue
        
        # Derive table_name from artifact dir name
        base_name = artifact_dir.name
        table_name = f"{base_name}_v4"
        table_folder = f"{table_name}_f"
        dest_dir = repo_path / "models" / dc_tag / table_folder
        
        # Model YAML
        models_src = curation_src / "models"
        if models_src.exists():
            for yml_file in models_src.glob("*.yml"):
                files_to_copy.append((yml_file, dest_dir / f"{base_name}.yml"))
            
            # Staging
            staging_src = models_src / "staging"
            if staging_src.exists():
                for sql_file in staging_src.glob("*.sql"):
                    files_to_copy.append((sql_file, dest_dir / "staging" / sql_file.name))
            
            # Integration
            integration_src = models_src / "integration"
            if integration_src.exists():
                for sql_file in integration_src.glob("*.sql"):
                    files_to_copy.append((sql_file, dest_dir / "integration" / sql_file.name))
            
            # Prepared
            prepared_src = models_src / "prepared"
            if prepared_src.exists():
                for sql_file in prepared_src.glob("*.sql"):
                    files_to_copy.append((sql_file, dest_dir / "prepared" / sql_file.name))
        
        # Source YAML
        source_yml = curation_src / "source.yml"
        if source_yml.exists():
            files_to_copy.append((source_yml, dest_dir / "source.yml"))
    
    return files_to_copy


def prepare_branch(
    repo_key: str,
    branch_name: str,
    files_to_copy: List[Tuple[Path, Path]],
    commit_message: str,
    dry_run: bool = False,
) -> None:
    """
    Create branch, copy files, commit, and push.
    """
    if not files_to_copy:
        print("No files to copy. Nothing to do.")
        return
    
    # Ensure working repo exists
    repo_path = ensure_working_repo(repo_key)
    repo_name = REPOS[repo_key]["name"]
    
    print(f"
{'[DRY RUN] ' if dry_run else ''}Preparing branch: {branch_name}")
    print(f"Target repo: {repo_path}")
    print(f"
Files to copy ({len(files_to_copy)} total):")
    
    # Group by destination directory for cleaner output
    dest_dirs = set()
    for src, dst in files_to_copy:
        dest_dirs.add(dst.parent)
    
    print(f"  Destination folders: {len(dest_dirs)}")
    for dest_dir in sorted(dest_dirs):
        try:
            rel_dir = dest_dir.relative_to(repo_path)
            count = sum(1 for _, d in files_to_copy if d.parent == dest_dir)
            print(f"    {rel_dir}/ ({count} files)")
        except ValueError:
            pass
    
    if dry_run:
        print("
[DRY RUN] Files that would be copied:")
        for src, dst in files_to_copy[:10]:  # Show first 10
            try:
                print(f"  {src.name} -> {dst.relative_to(repo_path)}")
            except ValueError:
                print(f"  {src.name} -> {dst}")
        if len(files_to_copy) > 10:
            print(f"  ... and {len(files_to_copy) - 10} more files")
        print("
[DRY RUN] No changes made.")
        return
    
    # Check working tree is clean
    if not check_clean_working_tree(repo_path):
        print(f"
Warning: Working tree not clean in {repo_path}")
        print("Stashing existing changes...")
        run_git(repo_path, "stash", "push", "-m", "auto-stash before prepare_branch")
    
    # Fetch latest and create branch
    default_branch = get_default_branch(repo_path)
    print(f"
Fetching latest from origin/{default_branch}...")
    run_git(repo_path, "fetch", "origin", default_branch)
    
    print(f"Creating branch {branch_name}...")
    run_git(repo_path, "checkout", "-B", branch_name, f"origin/{default_branch}")
    
    # Copy all files
    print(f"
Copying {len(files_to_copy)} files...")
    for src, dst in files_to_copy:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    print(f"  ✓ Copied {len(files_to_copy)} files")
    
    # Stage all changes
    run_git(repo_path, "add", "-A")
    
    # Commit
    print(f"
Committing...")
    run_git(repo_path, "commit", "-m", commit_message)
    
    # Push
    print(f"Pushing to origin/{branch_name}...")
    run_git(repo_path, "push", "-u", "origin", branch_name, "--force-with-lease")
    
    # Get org from repo URL
    repo_url = REPOS[repo_key]["url"]
    # Extract org from https://github.com/<org>/<repo>.git
    org = repo_url.split("github.com/")[1].split("/")[0]
    
    print(f"
✅ Branch '{branch_name}' pushed successfully!")
    print(f"
Next steps:")
    print(f"  1. Open PR: https://github.com/{org}/{repo_name}/compare/{branch_name}")
    print(f"  2. Add reviewers and description")
    print(f"  3. Link to Jira ticket if applicable")


def main():
    parser = argparse.ArgumentParser(
        description="Prepare feature branch with generated artifacts (batch mode supported)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single artifact - ingestion (use timestamp for uniqueness)
  python prepare_branch.py \
    --artifact-dir workspace/generated/source-aligned/govt_agency_regl_asia_moody \
    --repo pipelines \
    --process-domain blmbrg \
    --branch feature/blmbrg-govt-20250120-143022

  # Batch mode - multiple artifacts
  python prepare_branch.py \
    --artifact-dir workspace/generated/source-aligned/govt_agency_regl_asia_moody \
    --artifact-dir workspace/generated/source-aligned/govt_national_asia_moody \
    --repo pipelines \
    --process-domain blmbrg \
    --branch feature/blmbrg-govt-batch-20250120-143022

  # Using glob pattern (shell expands)
  python prepare_branch.py \
    --artifact-dir workspace/generated/source-aligned/govt_* \
    --repo im-foundation \
    --dc-tag blmbrg \
    --branch feature/blmbrg-curation-20250120-143022

  # Auto-generate branch name with timestamp (omit --branch)
  python prepare_branch.py \
    --artifact-dir workspace/generated/source-aligned/govt_* \
    --repo pipelines --process-domain blmbrg

  # Dry run
  python prepare_branch.py \
    --artifact-dir workspace/generated/source-aligned/govt_* \
    --repo pipelines --process-domain blmbrg \
    --branch feature/test --dry-run
        """,
    )
    
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        action="append",
        required=True,
        dest="artifact_dirs",
        help="Path to generated artifacts directory (can specify multiple times)",
    )
    parser.add_argument(
        "--repo",
        choices=["pipelines", "im-foundation", "databricks"],
        required=True,
        help="Target repository",
    )
    parser.add_argument(
        "--branch",
        help="Branch name to create (default: auto-generated with timestamp, e.g., feature/blmbrg-ingestion-20250120-143022)",
    )
    parser.add_argument(
        "--process-domain",
        help="System of record (e.g., blmbrg) — required for pipelines",
    )
    parser.add_argument(
        "--dc-tag",
        help="Data classification tag (e.g., blmbrg, ref) — required for im-foundation",
    )
    parser.add_argument(
        "--commit-message",
        help="Custom commit message (default: auto-generated)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    
    args = parser.parse_args()
    
    # Validate artifact directories
    valid_dirs = []
    for d in args.artifact_dirs:
        if d.exists():
            valid_dirs.append(d)
        else:
            print(f"Warning: Artifact directory not found: {d}", file=sys.stderr)
    
    if not valid_dirs:
        print("Error: No valid artifact directories found", file=sys.stderr)
        sys.exit(1)
    
    print(f"Processing {len(valid_dirs)} artifact directories...")
    
    # Generate timestamp for branch name
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Collect files and prepare branch based on repo type
    if args.repo == "pipelines":
        if not args.process_domain:
            print("Error: --process-domain is required for pipelines", file=sys.stderr)
            sys.exit(1)
        
        # Auto-generate branch name if not provided
        branch_name = args.branch or f"feature/{args.process_domain}-ingestion-{timestamp}"
        
        files = collect_pipelines_files(valid_dirs, WORKING_REPOS_PATH / REPOS["pipelines"]["name"], args.process_domain)
        
        commit_msg = args.commit_message or (
            f"feat({args.process_domain}): add {len(valid_dirs)} ingestion configs

"
            f"Generated via source-aligned skill
"
            f"Configs: {', '.join(d.name for d in valid_dirs[:5])}"
            + (f" (+{len(valid_dirs)-5} more)" if len(valid_dirs) > 5 else "")
        )
        
        prepare_branch("pipelines", branch_name, files, commit_msg, args.dry_run)
    
    elif args.repo == "im-foundation":
        if not args.dc_tag:
            print("Error: --dc-tag is required for im-foundation", file=sys.stderr)
            sys.exit(1)
        
        # Auto-generate branch name if not provided
        branch_name = args.branch or f"feature/{args.dc_tag}-curation-{timestamp}"
        
        files = collect_im_foundation_files(valid_dirs, WORKING_REPOS_PATH / REPOS["im-foundation"]["name"], args.dc_tag)
        
        commit_msg = args.commit_message or (
            f"feat({args.dc_tag}): add {len(valid_dirs)} curation models

"
            f"Generated via source-aligned skill
"
            f"Models: {', '.join(d.name for d in valid_dirs[:5])}"
            + (f" (+{len(valid_dirs)-5} more)" if len(valid_dirs) > 5 else "")
        )
        
        prepare_branch("im-foundation", branch_name, files, commit_msg, args.dry_run)
    
    elif args.repo == "databricks":
        print("
⚠️  Databricks branch creation is TBD.")
        print("The curation-databricks target structure is not yet finalized.")
        sys.exit(0)


if __name__ == "__main__":
    main()
