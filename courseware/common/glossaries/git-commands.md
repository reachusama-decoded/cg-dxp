# Git and GitHub: the commands, and how to use them safely

One line per command. The flags listed are the ones that matter in practice; `git <command> --help` has the rest. Everything here runs in the dev container's terminal or in VS Code's own terminal; the Source Control view in VS Code runs the same commands behind its buttons, and the names here are what to look for when a button is greyed out.

# Part 1 — The commands, by what you are trying to do

## Set yourself up

| Command | What it does |
|---|---|
| `git --version` | Prints the client version; the first check when a command is "unknown". |
| `git config --global user.name "Your Name"` | Who the commits are by; Git refuses to commit until this and the email are set. |
| `git config --global user.email you@company.com` | The address on every commit; use the one GitHub knows, so commits link to your account. |
| `git config --global init.defaultBranch main` | New repositories start on `main`. |
| `git config --global pull.rebase false` | `git pull` merges rather than rebases, the simpler behaviour for a shared branch. |
| `git config --list --show-origin` | Shows every setting and which file it came from (system, global, this repository). |
| `git config --global core.autocrlf input` | On Windows, keeps line endings as LF in the repository; stops the CRLF problems that break Dockerfiles and shell scripts. |

## Get a repository

| Command | What it does |
|---|---|
| `git clone URL [FOLDER]` | Copies a repository and its whole history from GitHub into a folder; `origin` is the name it gives the remote. |
| `git clone --depth 1 URL` | A shallow copy with only the latest commit, when the history is huge and you only need the files. |
| `git init -b main` | Turns the current folder into a new, empty repository on `main`. |
| `git remote -v` | Lists the remotes and their URLs: where `push` goes and `pull` comes from. |
| `git remote add NAME URL` | Adds a remote, for example `upstream` for the repository you forked from. |

## See where you are and what changed

| Command | What it does |
|---|---|
| `git status` | The branch you are on, what is staged, what is modified, what is untracked; `-s` for the short form. |
| `git branch --show-current` | Just the branch name. |
| `git diff` | The exact lines changed in the working copy and not yet staged. |
| `git diff --staged` | The lines staged for the next commit: what the commit will contain. Read this before every commit. |
| `git diff main...HEAD` | Everything your branch changed since it left `main`: what the pull request will show. |
| `git diff --stat` | Only the files and the number of lines, for a quick look. |
| `git show [COMMIT]` | One commit: its message and its diff. |
| `git blame FILE` | Who last changed each line of a file, and in which commit. |

## Record changes

| Command | What it does |
|---|---|
| `git add FILE …` | Stages a file (or a folder) for the next commit; a new file is untracked until it is added. |
| `git add -p` | Stages hunk by hunk, so one commit holds one change even when a file has two. |
| `git add -A` | Stages everything, including deletions. Check `git status` first: this is how a `.env` gets in. |
| `git commit -m "Message"` | Records the staged changes as a commit with a message. |
| `git commit -am "Message"` | Stages every modified tracked file and commits; does not pick up new files. |
| `git commit --amend` | Replaces the last commit with the staged changes and a new message; only on a commit you have not pushed. |
| `git rm FILE` / `git mv OLD NEW` | Deletes or renames a file and stages the change in one step. |
| `git rm --cached FILE` | Stops tracking a file but keeps it on disk; the step after adding it to `.gitignore` too late. |

## Read the history

| Command | What it does |
|---|---|
| `git log` | The commits on this branch, newest first; `q` leaves the pager. |
| `git log --oneline --graph --all` | One line per commit, with branches drawn; the view to keep in your head. |
| `git log -5` / `git log -p FILE` | The last five commits; or every commit that touched a file, with its diff. |
| `git log --author=NAME --since="2 weeks"` | Filtered by author and time. |
| `git reflog` | Every position `HEAD` has been at on this machine, including commits no branch points to any more: how lost work is found. |

## Branches

| Command | What it does |
|---|---|
| `git branch` | Lists local branches with the current one starred; `-a` includes the remote ones; `-vv` shows what each tracks. |
| `git switch -c NAME` | Creates a branch from where you are and moves to it (older form: `git checkout -b`). |
| `git switch NAME` | Moves to an existing branch; uncommitted changes come along if they do not conflict. |
| `git switch -` | Back to the previous branch. |
| `git merge NAME` | Brings the commits of `NAME` into the current branch; `--no-ff` keeps a merge commit so the branch shows in the graph. |
| `git rebase main` | Replays your branch's commits on top of the latest `main`; only on a branch nobody else has. |
| `git branch -d NAME` | Deletes a merged branch; `-D` deletes an unmerged one. |
| `git branch -m NEW` | Renames the current branch. |

## Share: remotes, push and pull

| Command | What it does |
|---|---|
| `git fetch` | Downloads the remote's new commits and branches without changing your files; `--prune` forgets remote branches that were deleted. |
| `git pull` | `fetch` then `merge` of the remote branch into yours; run it on `main` before starting a branch. |
| `git push -u origin NAME` | Uploads a branch the first time and makes `origin/NAME` its upstream; afterwards `git push` alone is enough. GitHub prints the pull-request link. |
| `git push` | Uploads your new commits to the branch's upstream. |
| `git push --force-with-lease` | Overwrites the remote branch with yours, refusing if someone else pushed meanwhile; only on your own branch, after a rebase or an amend, never on `main`. |
| `git push origin --delete NAME` | Deletes a branch on GitHub after its pull request has merged. |

## Undo and recover

| Command | What it does |
|---|---|
| `git restore FILE` | Throws away the uncommitted changes to a file; back to the last commit. There is no undo for this one. |
| `git restore --staged FILE` | Unstages a file, keeping its changes in the working copy. |
| `git revert COMMIT` | Makes a new commit that undoes an old one; the safe undo on a shared branch, because history is not rewritten. |
| `git reset --soft HEAD~1` | Removes the last commit but keeps its changes staged, to redo it differently; only before pushing. |
| `git reset --hard HEAD~1` | Removes the last commit and its changes. Destructive; `git reflog` is the only way back. |
| `git checkout COMMIT -- FILE` | Brings back one file as it was in an older commit. |
| `git clean -n` / `git clean -fd` | Lists, then deletes, untracked files and folders (build output, scratch files). `-n` first, always. |

## Park work and move it around

| Command | What it does |
|---|---|
| `git stash` | Sets aside the uncommitted changes and gives you a clean working copy; `-u` includes untracked files. |
| `git stash list` / `git stash pop` | Shows the stashes; brings the latest one back and drops it from the list. |
| `git cherry-pick COMMIT` | Copies one commit from another branch onto the current one. |
| `git tag -a v1.0 -m "First release"` / `git push --tags` | Names a commit (a release) and shares the tag. |

## Resolve a conflict

| Command | What it does |
|---|---|
| `git status` | During a merge or rebase, lists the files with conflicts ("both modified"). |
| `git diff` | Shows the conflict markers `<<<<<<<`, `=======`, `>>>>>>>`: your version, then theirs. Edit the file to the result you want and delete the markers. |
| `git add FILE` then `git commit` | Marks the file resolved and finishes the merge; during a rebase, `git rebase --continue` instead. |
| `git merge --abort` / `git rebase --abort` | Gives up and returns to the state before the merge or rebase started. |
| `git checkout --ours FILE` / `--theirs FILE` | Takes one side of the conflict whole, when that is the right answer. |

## GitHub from the terminal: the `gh` CLI

| Command | What it does |
|---|---|
| `gh auth login` | Signs the terminal in to GitHub (browser flow); `gh auth status` checks it. |
| `gh repo clone OWNER/REPO` | Clones by name instead of URL. |
| `gh pr create --fill` | Opens a pull request for the current branch, using the commit messages as title and body; `--web` opens the form in the browser instead. |
| `gh pr list` / `gh pr status` | The open pull requests; the ones that are yours or need your review. |
| `gh pr view [N] --web` | Opens a pull request in the browser. |
| `gh pr checkout N` | Fetches a pull request's branch to review it locally. |
| `gh pr review N --approve` / `--request-changes -b "…"` | Reviews from the terminal. |
| `gh pr merge N --squash --delete-branch` | Merges a pull request and removes its branch, when branch protection allows you to. |
| `gh run list` / `gh run watch` | The CI runs for the repository; follow one as it runs. |

## The files Git reads, for reference

Files, not commands: what shapes Git's behaviour in a repository.

| File | What it does |
|---|---|
| `.gitignore` | Patterns for files Git must never offer for commit: `.env`, `target/`, `dbt_packages/`, `logs/`, `*.duckdb`, `__pycache__/`, `.venv/`, data dumps. Written before the first commit. |
| `.gitattributes` | Per-path rules: line endings (`* text=auto`), files to treat as binary, files stored with Git LFS. |
| `.git/config` | This repository's remotes, branches and settings; `git config` edits it. |
| `~/.gitconfig` | Your global settings: identity, aliases, default branch. |
| `.pre-commit-config.yaml` | The checks that run before each commit when `pre-commit install` has been run: in the training repository, whitespace and line endings, YAML and TOML syntax, `hadolint` on Dockerfiles, `ruff` on Python, `sqlfluff` on SQL. |
| `CODEOWNERS` | Who GitHub asks to review changes under each path. |
| `.github/pull_request_template.md` | The description every new pull request starts from. |
| `.github/workflows/*.yml` | GitHub Actions: the checks that run on every push and pull request. |

Two habits that keep a repository readable: commit small and often, one change per commit with a message that says what and why; and look at `git status` and `git diff --staged` before every commit, because the commit is what the reviewer reads.

# Part 2 — Work safely with Git and GitHub

The habits, in the order they bite. Most are one line in a file or one check before a command; CG's branch protection and the training repository's pre-commit hooks already enforce several, which is one reason the paved path starts from a vended repository.

## Before you commit

| Habit | How |
|---|---|
| Write `.gitignore` first | Before the first `git add`: `.env`, credentials, `target/`, `logs/`, virtualenvs, data files. Adding it later does not remove what is already committed. |
| Never commit a secret | No tokens, keys, passwords or connection strings in code, YAML, notebooks or `.env`. A secret in a commit stays in the history after the file is deleted, and a pushed secret is public to everyone with read access: rotate it first, then clean up, then tell the platform team. |
| Set your identity properly | `user.name` and the email GitHub knows, so every commit is traceable to a person and shows on your account. |
| Read the diff | `git status`, then `git diff --staged`, before every commit. Generated code from Catalyst goes in only after you have read it. |
| One change per commit | A commit that does one thing has a message that fits in one line and a revert that does not take anything else with it; `git add -p` when a file holds two changes. |
| Write the message for the reader | A line of what and why, imperative, under about seventy characters: "Add the price_gbp derive rule to the STTM"; a body when the why needs more. "Fix", "wip" and "changes" tell the reviewer nothing. |
| Let the hooks run | `pre-commit install` once per clone; then the hooks block a commit with CRLF endings, bad YAML or unformatted SQL before it reaches review. Do not use `--no-verify` to get past them. |
| Keep data out | No CSV extracts, DuckDB files, Parquet or notebooks with outputs; large or binary files go to storage or Git LFS, never into history. |
| Commit only what you own | In the training repository, the `.odcs.yaml` contract and the code; never the generated migration SQL that CI commits for you. |

## Branches and pull requests

| Habit | How |
|---|---|
| Never work on `main` | `git switch -c feature/<name>` from an up-to-date `main` (`git pull` first); `main` is protected and the pull request is the only way in. |
| Name the branch for the change | `feature/eod-prices-staging`, `fix/fx-null-rate`; your username in it when the repository is shared by a whole room. |
| One pull request, one change | Small enough to review in ten minutes; a second change is a second branch. |
| Describe it for the reviewer | What changed, why, and how to verify (`mise run challenge:verify 01`, `dbt build`); link the contract or ticket it implements. |
| Ask for a real review | A reviewer who reads the diff, not one who approves on sight; a deleted test is a block of red lines that is easy to skim past. |
| Let the checks finish | Do not merge with a red check; a failing check is information, not an obstacle. |
| Keep the branch current | `git pull` on `main` and merge (or rebase, if the branch is only yours) before asking for review, so the pull request shows only your change. |
| Merge the way the repository merges | Squash, merge commit or rebase is the repository's convention, set in branch protection; do not change it per pull request. |
| Delete the branch after merging | GitHub's button or `git push origin --delete NAME`; then `git fetch --prune` locally. |

## History and shared branches

| Habit | How |
|---|---|
| Do not rewrite shared history | `--amend`, `rebase` and `reset` are for commits that have not left your machine. On anything pushed and shared, `git revert`. |
| Force-push only your own branch | `--force-with-lease`, never `--force`, never on `main`; branch protection should refuse it anyway. |
| Revert, do not delete | A bad change on `main` is undone by a revert commit that the history explains; a deleted branch or rewritten history explains nothing. |
| Tag releases | `git tag -a` on the commit that shipped, so a deployment can be traced to exact code. |

## Credentials and access

| Habit | How |
|---|---|
| Sign in once, properly | `gh auth login` or an SSH key in your GitHub account; a credential manager stores the token. Never a token in a clone URL, a script or a notebook. |
| Use short-lived, scoped tokens | If a personal access token is unavoidable, the fine-grained kind, one repository, the minimum permissions, an expiry date; rotate it and delete it when done. |
| Mind the certificate | Behind CG's proxy, Git needs the corporate CA: `git config --global http.sslCAInfo /cacert.pem` in the dev container (`TROUBLESHOOTING.md`, Git SSL certificate errors). Never `http.sslVerify false`. |
| Least access | Read access by default; write access through a team, not individual grants; `CODEOWNERS` so the right people review the right paths. |
| Public is forever | A private repository can be made public; assume anything committed may one day be read by anyone, and keep secrets and client data out regardless. |

## A good commit and pull request, for the Challenge 7 Dockerfile

```text
# The commit: imperative, what and why, one line; a body only when the why needs it.
git switch -c feature/<username>-docker
git add challenges/v1/01-docker-intro/starter/Dockerfile
git commit -m "Add the portfolio-summary Dockerfile for challenge 01

The starter left WORKDIR, COPY and CMD as TODOs; the image now builds from
python:3.11-slim and prints the six-holding summary. Verified with
mise run challenge:verify 01."
git push -u origin feature/<username>-docker
```

```markdown
<!-- The pull request description: three short sections the reviewer can act on. -->
## What
The Dockerfile for the portfolio-summary app: FROM, WORKDIR, COPY, CMD.

## Why
Challenge 01, section 3. The starter had three TODO lines.

## How to verify
`mise run challenge:verify 01` prints PASS; `docker run --rm portfolio-summary`
prints "Portfolio summary" and "6 holdings, total market value 12,011,626.50".
```
