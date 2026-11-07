# Complete v2 source reference

Supporting learner reference; assigned route and ownership remain in each canonical phase.

# Version 2 challenge route

Practice building and reviewing data products through seven tools. Foundation and advanced phases have separate starters, so you can begin either route with the required prerequisites. Read the phase's purpose, dataset, starter behavior and completion standard before editing.

## Prepare your environment

Open the supplied training project in the dev container and inspect the delivered tool versions. Git foundation and local fixture inspection can proceed without cloud access. Docker needs its prepared engine and images; connected dbt and capstone need the approved Databricks identity/warehouse/namespace; Airflow needs the actual Astro scheduler and worker boundary. Sign in through the delivered setup outside recordings and keep credentials out of source, evidence and package files. Check installed versions with each tool's version command.

Use an isolated copied workspace for each attempt and inspect its execution directory. The version-explicit mise prepare task refuses an existing destination; reset also preserves existing attempts by requiring a fresh path. Choose owned relation prefixes, DAG names, container tags and optional event topic/groups so simultaneous learners do not collide. Never create extra schemas or delete broad resource sets to repair a training issue.

## Choose the work

| Tool | Foundation | Advanced | Classroom role |
|---|---|---|---|
| [Git](git/README.md) | Local snapshots, branches and conflict | Authorized sandbox review and synchronization | Preparation/collaboration clinic |
| [Docker](docker/README.md) | Lifecycle, mount and app packaging | Tested targets, user and runtime contents | Supervised runtime practice |
| [dbt](dbt/README.md) | Supplied Portfolio sources/staging/report | Dated joins, reconciliation, correction and history | Wednesday selected core |
| [Databricks CLI](databricks-cli/README.md) | Read-only identity and metadata discovery | Not offered | Environment preparation |
| [Airflow](airflow/README.md) | Same Portfolio product on Astro | Readiness, failure/repair/replay and handoff | Thursday selected core |
| [Kafka](kafka/README.md) | Optional prepared event clinic | Not offered | Optional further practice |
| [Atlas capstone](capstone/README.md) | Consumer-focused trade/report slice | Finite performance/leaderboard/region core | Friday product practice |

Advanced phases have disclosed successful entry baselines and do not require a completed peer answer. Optional stretch follows the core completion gate with separate prerequisites and timing. Kafka cannot become a hidden requirement of mandatory work.

## Run and assess an attempt

From the training project root prepare and verify through mise; inside the copy use direct tool commands so you can inspect what the tool does. Explicit live mode reaches the declared connected boundary. Offline support, parsed SQL, local JSON and compilation cannot establish Databricks or Astro completion. An untouched starter may pass its baseline check while being rejected as completed learner work. Expected instructional failures are named before the drill, and unrelated prerequisite failures stay distinct.

```bash
mise run challenge:v2:prepare dbt phase-one-certified
mise run challenge:v2:verify-starter dbt phase-one-certified --mode offline
mise run challenge:v2:verify dbt phase-one-certified --workspace .local/challenges-v2/dbt/phase-one-certified --mode live
```

## Read the guides effectively

Each task presents Concept, Challenge, Hint and Check, with required work visible and optional hints in native details disclosures. Horizontal rules separate task boundaries. Use phase contents and task/reasoning return links; compare end-of-phase reasoning after your own attempt. Full runnable reference assets are supplied separately to instructors. Keep the commands, results and business explanation in your attempt's evidence note. Mark any check you could not run.

The supplied Portfolio Analytics and Atlas cases have distinct fields, units and populations. The shared [runtime setup](runtime/portfolio/SETUP.md) explains approved namespace, paths, profiles, worker credentials and owned cleanup. Older numeric mise tasks select v1; use `challenge:v2:*` for these phases. Keep previous attempts when preparing a new workspace.


---

# Portfolio Analytics and Atlas runtime

Read [SETUP.md](SETUP.md) for the terminal and Astro worker setup. `lab.py` prepares independent checkpoints, validates configuration, computes CSV reference outputs and checks actual Databricks results. Use CSV reference outputs to predict results, then check the actual Databricks relations. `dataset-runtime-contract.json` binds the supplied data and routes.


---

# git challenges

Git makes a data-contract change inspectable through snapshots and ancestry. Foundation practice stays local: distinguish working/index/committed content, make intentional commits, combine branches, resolve a business ownership conflict and restore only an accidental edit. Advanced practice carries a prepared independent contract through an authorized private sandbox PR, real review revision and concurrent upstream change. The result is preserved requirements and an understandable history, not merely a command count.

## Before you start

Prepare an isolated attempt through mise and check its repository root before any change. Keep the baseline contract and evidence at the attempt root and local Git work in the inner lab. Foundation requires only delivered Git and a local training identity. Advanced requires an instructor-designated private repository, permitted branch prefix, CLI identity and arranged reviewer. Missing remote or human preparation remains pending; a local simulation can teach mechanics but does not establish peer review. Neither route authorizes publishing the course checkout or modifying a production branch.

## Suggested timeline and tasks

Estimates include reading, practice, checks and explanation. Allow additional time for environment setup and optional extensions.

| Phase | Task | Minutes |
| --- | --- | --- |
| Foundation | [git-p1-01: Inspect the three working states](phase-one-certified/README.md#git-p1-01) | 12–18 |
| Foundation | [git-p1-02: Commit an intentional contract change](phase-one-certified/README.md#git-p1-02) | 12–18 |
| Foundation | [git-p1-03: Branch and combine compatible work](phase-one-certified/README.md#git-p1-03) | 12–18 |
| Foundation | [git-p1-04: Resolve an ownership conflict](phase-one-certified/README.md#git-p1-04) | 12–18 |
| Foundation | [git-p1-05: Restore a mistake and explain the final history](phase-one-certified/README.md#git-p1-05) | 12–18 |
| Advanced | [git-p2-01: Clone and inspect a collaboration boundary](phase-two-proficient/README.md#git-p2-01) | 15–22 |
| Advanced | [git-p2-02: Push and propose a scoped pull request](phase-two-proficient/README.md#git-p2-02) | 15–22 |
| Advanced | [git-p2-03: Respond to a review with a second commit](phase-two-proficient/README.md#git-p2-03) | 15–22 |
| Advanced | [git-p2-04: Integrate concurrent upstream work](phase-two-proficient/README.md#git-p2-04) | 15–22 |
| Advanced | [git-p2-05: Read the final review and merge state](phase-two-proficient/README.md#git-p2-05) | 15–22 |

## Choose your phase

- [Foundation](phase-one-certified/README.md): Foundation core with explicit completion evidence.
- [Advanced](phase-two-proficient/README.md): Independent advanced baseline and finite core, separately timed.

Finish the core tasks before choosing optional stretch.

## Teaching concepts

Snapshots and ancestry protect different aspects of a change. Read working and staged diffs before committing; read branch history and final contract after merging. A clean status cannot prove preserved business facts. Review identity, revision head and actual hosted state extend that reasoning into collaboration. End-of-phase reasoning keys explain decisions after your attempt; full runnable references remain in the instructor package. Remote writes and reviewer participation are classroom-authorized actions, never automatic verifier behavior.


---

# git: Phase 1 — foundations

## Purpose and outcome

Learn to preserve and explain a small data-contract change using local Git. You will distinguish working files from staged content and committed history, make intentional commits, combine branch work, resolve a meaningful ownership conflict and restore an accidental edit. The contract is small so the tool behavior is visible. The point is reviewable changes and preserved requirements, not memorizing a long command sequence.

## Dataset and pipeline

The starter is an ordinary holdings contract with owner, grain, currency and daily delivery. It is a documentation fixture, not the later Databricks dataset. You will refine its deadline and escalation promises while keeping the original grain and currency facts. An untracked notes file demonstrates that a file can exist without entering the next commit. Compatible branches edit deliberately separated facts; competing owner edits create a known merge conflict. This local history becomes the evidence for your explanation of how requirements were combined.

## Prerequisites and workspace

Use the delivered Git executable and a configured training identity. Prepare an isolated attempt from the training project root through mise, then create a new inner lab repository inside that copy. Confirm the repository root before running change or restore commands. The course repository and another learner's directory are outside the exercise boundary. Keep the copied baseline contract and evidence note at the attempt root, with only the inner lab under its new Git history.

```bash
mise run challenge:v2:prepare git phase-one-certified
cd .local/challenges-v2/git/phase-one-certified
mkdir lab
cp contract.md lab/contract.md
cd lab
git init -b main
git --version
```

Record your configured author identity without changing another repository's global settings. If Git does not support the initial-branch option in the delivered version, inspect its help and create the main branch explicitly; record that measured variation. Use a new workspace for another attempt instead of resetting existing work. This phase performs local actions only and does not require a hosting account, production branch or public repository.

## Starter behavior

The supplied contract is valid text and there is no intentionally broken repository. Initial status shows an untracked contract until you stage it. The first task deliberately creates an additional notes file so you can identify exactly what enters a commit. A later ownership merge is expected to stop with a conflict; the README names that failure before it happens. A clean starter check establishes readable input, not completion. Keep the contract baseline and the new lab separate so the verifier can inspect both without overwriting your work.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 60–90 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [git-p1-01: Inspect the three working states](#git-p1-01) | 12–18 | First commit contains only contract.md; notes remain outside that snapshot |
| [git-p1-02: Commit an intentional contract change](#git-p1-02) | 12–18 | Commit diffs distinguish 09:00 UTC deadline from escalation policy |
| [git-p1-03: Branch and combine compatible work](#git-p1-03) | 12–18 | Both separated facts survive; history explains fast-forward or merge commit |
| [git-p1-04: Resolve an ownership conflict](#git-p1-04) | 12–18 | Expected merge failure; no markers; resolution retains owner and escalation decisions |
| [git-p1-05: Restore a mistake and explain the final history](#git-p1-05) | 12–18 | Clean lab; committed requirements unchanged; explanation distinguishes restore from revert |

## Core challenges


<a id="git-p1-01"></a>

### git-p1-01: Inspect the three working states


<a id="git-p1-01-concept"></a>

#### Concept


The working tree contains editable files. A commit records a snapshot and its parent history. The index is the proposed next snapshot, not a synonym for every file in the directory. Staging one file selects its current content for the next commit; changing that file again can leave one version staged and another in the working tree. An untracked file has no committed baseline, so its presence in a folder does not imply version control protects it. This distinction matters when a contract edit and an unrelated note share a workspace.

For the first snapshot, the baseline contract should enter history while the scratch notes should not. Inspecting the staged diff and the committed file list gives stronger evidence than a commit command returning success. The repository root is also part of the boundary: operating from the course checkout instead of the disposable lab would select the wrong work. Confirm that root before reasoning about status.


#### Challenge


Use the prepared inner lab and configure a local training name/email if needed. Confirm its repository root, inspect `git status`, and create an untracked `notes.txt`. Stage only `contract.md`, inspect `git diff --cached`, then make the initial commit. Explain why the note is absent from that snapshot.

Keep the commit hash in `evidence.md` at the parent attempt root. Remove or ignore the scratch file before later clean-state checks. Stage an explicit filename rather than the entire attempt, so runtime files and evidence stay outside this first snapshot.


#### Hint


<details>
<summary>Inspect the proposed snapshot before making history</summary>

Use git status `--short` and git log `--oneline`. Configure identity in this lab, not globally.

Compare status with the staged diff before committing, then compare the commit's file list afterward. A note visible in your editor may still be untracked. Use an explicit filename when staging the baseline. If the root probe names the outer course repository, stop and enter or initialize the intended lab before making a commit; the observed status belongs to the wrong boundary.

</details>

#### Check


Inspect the first commit's file list and content, verifying that only the contract was recorded and the scratch note was not. The committed contract must retain the supplied owner, grain, currency and daily-delivery facts. Record the hash and explain the difference between an untracked note, a staged contract and the committed snapshot.

A successful commit with extra files fails this task's intent even if status becomes clean. If an unrelated file was staged accidentally, unstage it without discarding its working content, inspect again and explain the correction before committing. Keep evidence outside the inner repository. The local verifier can inspect final contract/history, while the staged-before-commit evidence explains the first snapshot decision.

```bash
git rev-parse --show-toplevel
git diff --cached
git show --stat HEAD
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#git-p1-01-reasoning)


---


<a id="git-p1-02"></a>

### git-p1-02: Commit an intentional contract change


<a id="git-p1-02-concept"></a>

#### Concept


A useful commit makes one intention reviewable. A deadline clarification and an escalation rule can be related business work while still benefiting from separate snapshots: a reviewer can see the delivery promise and then the response to a missed promise. A commit message describes that intent; the actual diff proves what changed. Combining unrelated edits makes later diagnosis or reversal harder.

Staging also lets you choose when a change enters history. An accidental extra line in the working file need not be committed with the deadline, and unstaging differs from discarding content. Inspecting both ordinary and cached diffs reveals that boundary. The fixture remains ordinary contract text, so the review should preserve grain and currency while adding a clear time zone rather than silently replacing the original business assumptions.


#### Challenge


Change Delivery to daily before 09:00 UTC. Review the working diff, stage that edit, inspect the staged diff and commit it with a message explaining the deadline clarification. Add `Escalation: Training support` in a separate commit.

Save both hashes and their scoped diffs in the parent evidence note. Confirm the original grain, currency and owner remain. If an unrelated edit appears in the index, unstage it without discarding its working content. Each commit should let a reviewer assess one contract decision independently.


#### Hint


<details>
<summary>Make each contract decision independently reviewable</summary>

git diff shows unstaged changes; git diff `--cached` shows staged changes.

Read each staged diff as though reviewing someone else's contract. Does the deadline name a time zone, and does the second change name a usable escalation responsibility? If another edit appears, remove it from the index without deleting its working content. The two hashes should identify independently understandable decisions rather than two arbitrary saves of the same unfinished paragraph.

</details>

#### Check


Inspect both commits and confirm the first clarifies delivery at 09:00 UTC and the second adds the escalation text. Each diff should preserve grain, currency and owner facts except where a later ownership task intentionally changes them. Explain how staged content differed from the working file and why the separate commits help a reviewer assess intent.

Record the parent relationship and scoped content, not only two hash strings. A commit message claiming deadline work does not excuse an unrelated deletion in its diff. If you staged the wrong edit, show the bounded correction without rewriting or deleting another learner's history. The final local phase assessment needs the declared deadline/escalation result and your explanation of the commit boundaries.

```bash
git diff
git diff --cached
git show --stat HEAD
git log --oneline -3
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#git-p1-02-reasoning)


---


<a id="git-p1-03"></a>

### git-p1-03: Branch and combine compatible work


<a id="git-p1-03-concept"></a>

#### Concept


A branch names a position in commit history; it is not a separate copy of every file you must manage manually. Switching branches changes the checked-out snapshot, while merging combines ancestry and file changes. Compatible edits can be combined without conflict when they touch sufficiently separate content from a shared baseline. Adjacent edits in a tiny file can still conflict, so compatibility is a property to observe rather than assume from different branch names.

Use distinct contract facts for this demonstration, such as a nonadjacent delivery refinement and a newly separated producer note. The goal is to preserve both intentions and explain whether history advanced directly or recorded a merge. Fast-forward means the target simply reached a descendant commit; a merge commit records combined parents when histories diverged. Neither outcome alone tells whether the final text is correct.


#### Challenge


Create `clarify-grain` and `producer-note` from a common main commit. Clarify the existing grain on the first branch. On the second, append a separate Producer note section with a blank line before it. Commit each change before switching branches.

Inspect each branch's diff, merge both into local main and review the complete contract. Record the common ancestor and whether each merge fast-forwarded or created a merge commit. If the short file produces unintended overlap, record and repair the separated note layout; reserve the deliberate ownership conflict for the next task.


#### Hint


<details>
<summary>Verify separated changes before calling them compatible</summary>

Use git switch -c and git merge. Commit before switching away from a change.

Compare each branch with its shared ancestor before merging. Different branch names do not ensure different text regions. Keep this task's compatible demonstration distinct from the later deliberate owner conflict. Use the graph to identify whether main simply advanced or combined divergent parents, and use the final file to prove that both business edits survived.

</details>

#### Check


The final local contract must contain both intended branch facts with the original deadline, escalation and data meaning retained. Inspect branch diffs, merge output and the graph to explain the observed merge mode. A clean merge that dropped a requirement is not success, and an accidental conflict should be recorded and repaired rather than hidden.

Retain the shared baseline and resulting hashes, identifying the branch that carried each fact. Explain why a branch pointer and working-tree snapshot are different concepts. The later ownership task supplies the intentional conflict case; this task should demonstrate a genuinely compatible path through local history without remote activity or broad resets.

```bash
git log --graph --oneline --all
git diff main...producer-note
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#git-p1-03-reasoning)


---


<a id="git-p1-04"></a>

### git-p1-04: Resolve an ownership conflict


<a id="git-p1-04-concept"></a>

#### Concept


A conflict means Git cannot choose a combined text automatically. It does not mean either branch is necessarily wrong or that a valid business decision follows from accepting one side. The conflict markers show candidate content from two histories; the learner must understand the requirements and produce one coherent contract. For ownership, the resulting named owner and escalation responsibility must be compatible rather than two contradictory labels.

The merge remains unfinished until the resolved file is staged and committed. Removing markers without inspecting surrounding text can still lose the deadline or currency facts. A merge commit's parents record which histories were combined, while the resolution diff records the actual decision. That evidence is useful to a future reviewer who did not watch the editor. The exercise deliberately stops with a nonzero merge result so the expected failure can be distinguished from tool or identity setup problems.


#### Challenge


From the same main state, create `upstream-owner` with `Owner: Operations team`. On main, set `Owner: Analytics team`. Merge `upstream-owner` and retain the expected conflict state.

Inspect both candidate versions, then resolve to `Owner: Analytics team` with `Escalation: Training support`. Keep the existing deadline, grain and currency. Remove all markers, stage the resolved file, inspect its staged diff and complete the merge commit. Explain the ownership choice in the parent evidence note. A removed marker is only part of the repair; the resulting contract must be coherent.


#### Hint


<details>
<summary>Resolve the business decision, then complete the merge state</summary>

Read git status after the merge fails. Edit the text itself, remove all conflict markers, then stage it.

Read the entire conflict region and both parent versions before editing. The agreed contract may combine requirements without keeping either side verbatim. Check for markers after resolution and inspect the staged file, not only the visible editor buffer. If the merge failed for an unrelated configuration reason, repair that prerequisite before treating it as the intended ownership exercise.

</details>

#### Check


The initial merge should stop with the named ownership conflict and nonzero status. After resolution, the file must contain no markers, preserve the deadline/grain/currency promises and state the agreed owner/escalation responsibility. Inspect the completed commit's parents and resolution diff so the evidence links both histories to the final decision.

Explain why accepting an entire side could lose another requirement and why staging a marker-free file does not by itself finish the merge. Retain the expected initial failure and successful resolution separately. Do not reset the whole lab to the instructor answer to avoid the conflict. The local verifier's final-content check supplements the required reasoning about how your decision reconciled the two proposals.

```bash
git status
git show --format=fuller --stat HEAD
git rev-list --parents -n 1 HEAD
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#git-p1-04-reasoning)


---


<a id="git-p1-05"></a>

### git-p1-05: Restore a mistake and explain the final history


<a id="git-p1-05-concept"></a>

#### Concept


Restoring a working file replaces an uncommitted version with a known snapshot. That can safely remove an intentional teaching mistake after all useful work is committed, but it would discard wanted uncommitted edits if used without inspection. Reverting a committed change is different: it creates another historical decision rather than simply changing the current file. Choosing the operation depends on what state contains the mistake.

The final exercise adds accidental text after the completed ownership merge. Inspecting its diff establishes that only this new line is unwanted. Restoring that file should leave every committed deadline, escalation and ownership decision intact. A clean status then means working/index content agrees with history; it does not mean the contract is correct by itself. The committed file and complete prior evidence provide that additional check.


#### Challenge


After all intended contract work is committed, append `Accidental text` to `contract.md`. Inspect the working diff and confirm no wanted edit is mixed with it. Use `git restore contract.md`, then compare the working file with the current committed snapshot.

Confirm the deadline, escalation and resolved owner survived. Write a short explanation of the working tree, index, branching and ownership decision. Keep the evidence outside the inner repository so the final clean-state check does not require deleting it. Explain why restoring this uncommitted mistake differs from reversing a published commit.


#### Hint


<details>
<summary>Inspect the accidental diff before restoring a named file</summary>

Do this only inside your disposable lab, after all intended changes were committed.

Identify where the mistake lives before choosing a recovery operation. If a useful edit is still uncommitted, preserve it first rather than using a broad reset. Restore the named contract file, not every file in the attempt. Compare the current committed snapshot afterward; a green status is meaningful only alongside proof that the wanted requirements still exist.

</details>

#### Check


The disposable lab status must be clean and its contract must match the current committed snapshot. Verify that the explicit deadline, escalation and resolved owner remain, while the accidental line is absent. Retain the before/after working diff and explain why this operation did not delete the earlier commits.

Run the root phase verifier on the preserved attempt, then distinguish its behavioral result from the instructor's review of your explanation. A clean empty repository or a copied answer does not satisfy the recorded history sequence. State why restoring an uncommitted mistake differs from reversing an already published commit. No remote action is needed for this foundation outcome, and entering advanced practice should use a fresh independently prepared attempt rather than destroy this evidence.

```bash
git status --porcelain
git show HEAD:contract.md
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#git-p1-05-reasoning)


## Phase completion


Show the final contract, a clean disposable lab repository and a history that explains intentional commits, compatible branch work and the ownership-conflict decision. Your contract must retain the explicit 09:00 UTC delivery promise and escalation text. Keep a record of the staged-only first commit, separate deadline/escalation commits, both branch changes and the conflict resolution's parents. The final restoration should remove only the accidental uncommitted text while preserving every committed requirement.

Store evidence outside the inner lab repository, beside the copied starter, so a clean Git state does not require deleting the explanation. The local verifier inspects your actual copied repository and contract rather than substituting a fresh reference workflow. Its behavioral checks supplement the instructor's review of your explanations; a clean status alone cannot prove all intended edits survived. Phase 1 needs no remote push or peer review. Preserve this attempt when entering the independently prepared collaboration phase, and keep any optional rebase/reflog experiment separate from the minimum outcome.

---


## Optional stretch


The core completion standard is independent of optional work. No additional stretch is required in this phase; the next phase has an independently prepared entry baseline.

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Inspect the three working states

<a id="git-p1-01-reasoning"></a>

<details>
<summary>Reasoning for git-p1-01: Staged content determines the next snapshot</summary>

The first commit should contain the baseline contract alone. A scratch note can be visible and untracked without being in that snapshot. Status, staged diff and committed file list describe different states. Explicit file staging protects unrelated work, and checking the repository root prevents editing the outer course checkout. Evidence lives outside the lab so the final clean-state check can coexist with a complete explanation.

[Return to git-p1-01](#git-p1-01)

</details>

### Reasoning: Commit an intentional contract change

<a id="git-p1-02-reasoning"></a>

<details>
<summary>Reasoning for git-p1-02: Reviewable commits preserve intent and unrelated facts</summary>

The deadline and escalation changes have distinct purposes and should appear in separate diffs. A message alone cannot establish that scope. Staged inspection protects unrelated working edits, and the final contract retains its original grain/currency facts. Keeping hashes with their content lets a reviewer reconstruct the decisions rather than trusting a terminal success message.

[Return to git-p1-02](#git-p1-02)

</details>

### Reasoning: Branch and combine compatible work

<a id="git-p1-03-reasoning"></a>

<details>
<summary>Reasoning for git-p1-03: History shape and retained requirements are complementary checks</summary>

The branch graph explains ancestry and whether a fast-forward or merge occurred. The final contract proves both intended facts survived. Compatibility must be established from actual separated edits; the tiny original file can produce overlap despite different branch names. Keep accidental overlap distinct from the later planned ownership conflict, and preserve the prior deadline/escalation work.

[Return to git-p1-03](#git-p1-03)

</details>

### Reasoning: Resolve an ownership conflict

<a id="git-p1-04-reasoning"></a>

<details>
<summary>Reasoning for git-p1-04: The resolution is a reviewable business choice</summary>

Git exposes competing owner edits but cannot decide the correct responsibility contract. The learner resolves the requirements, retains other facts and completes the staged merge. Both parents explain combined history; the diff explains the actual choice. An unrelated setup failure is not the intended conflict, and removing markers alone does not prove a coherent or committed result.

[Return to git-p1-04](#git-p1-04)

</details>

### Reasoning: Restore a mistake and explain the final history

<a id="git-p1-05-reasoning"></a>

<details>
<summary>Reasoning for git-p1-05: Local restoration changes working state without erasing committed decisions</summary>

The accidental line is uncommitted, so named-file restoration can remove it after verifying that no useful edit is mixed in. The earlier commit history remains intact. Final cleanliness must be paired with retained contract requirements and before/after evidence. Reverting a committed or shared decision would be a different historical operation. Keep the explanation outside the inner lab so the clean-state check and complete evidence can both hold.

[Return to git-p1-05](#git-p1-05)

</details>


---

# git independent starter

Read the [owning phase](../README.md) before editing. Prepare from the training project root with `mise run challenge:v2:prepare git phase-one-certified`; edit the copied attempt.

## Authored-file list

| Task | Learner-authored paths |
|---|---|
| git-p1-01, git-p1-02, git-p1-03, git-p1-04, git-p1-05 | `lab/contract.md`, `evidence.md` |

## Declared baseline

The supplied contract is the starting point. Create the inner Git repository under `lab/` and keep `evidence.md` outside it, beside the copied starter. The advanced phase also supplies a review scenario; the training remote and reviewer are arranged separately.

Use a fresh workspace for another attempt; preparation and reset preserve existing work.


---

# git: Phase 2 — advanced practice

## Purpose and outcome

Carry a small contract clarification through a collaboration workflow. This phase extends local Git into a designated remote repository, an understandable pull request, an actual review response and synchronization with concurrent upstream work. The challenge is preserving intent and review evidence across participants, not merely making a push command succeed. The advanced route has an independent contract baseline and a supplied review scenario, so you do not need another learner's foundation repository.

## Dataset and pipeline

The fixture is the same style of holdings contract used in local practice. A delivery-timezone clarification and escalation responsibility form the proposed change. The review scenario asks for an explanation and revision, while a separate upstream edit adds input classification. These requirements must coexist in the final branch. The hosted PR contains the proposal and review state; local history contains your commits and integrated ancestry. They describe related but distinct collaboration evidence.

## Prerequisites and workspace

The instructor designates an authorized private training repository, branch prefix and reviewer. Use the delivered Git and GitHub CLI tools with the intended training identity. Prepare an independent attempt through mise, then clone only the designated sandbox into its inner lab directory. Keep the starter contract and evidence at the attempt root. Confirm remote URLs and repository root before any remote write; the course repository and production remotes are outside this exercise.

```bash
mise run challenge:v2:prepare git phase-two-proficient
cd .local/challenges-v2/git/phase-two-proficient
gh auth status
```

Account creation, sign-in, reviewer invitation and repository provisioning are arranged preparation, not automated assessment. If a real reviewer or remote is unavailable, use the supplied scenario locally with explicit simulated status and leave the corresponding collaboration gate pending. Do not count a Markdown draft as an actual PR or a self-comment as peer review.

## Starter behavior

The contract and review-scenario JSON are readable, benign inputs. There is no real remote state inside the copied starter. Phase verification requires your actual cloned repository and, for live review checks, the designated sandbox/PR identifiers. A local reference workflow can demonstrate Git mechanics but does not satisfy hosted review. The final merge decision follows the instructor's stated policy; an open PR may be the honest final state. Never rewrite the route to imply approval just because a check command exited successfully.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 75–110 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [git-p2-01: Clone and inspect a collaboration boundary](#git-p2-01) | 15–22 | Designated private sandbox, correct clone root, remote and tracking branch |
| [git-p2-02: Push and propose a scoped pull request](#git-p2-02) | 15–22 | PR URL/head hash and remote diff contain the intended deadline clarification |
| [git-p2-03: Respond to a review with a second commit](#git-p2-03) | 15–22 | Other reviewer/comment, second commit and remotely visible response |
| [git-p2-04: Integrate concurrent upstream work](#git-p2-04) | 15–22 | Upstream ancestor and retained classification/deadline/escalation facts |
| [git-p2-05: Read the final review and merge state](#git-p2-05) | 15–22 | Actual final state, current head and next authorized action |

## Core challenges


<a id="git-p2-01"></a>

### git-p2-01: Clone and inspect a collaboration boundary


<a id="git-p2-01-concept"></a>

#### Concept


A remote URL identifies where commits can be fetched or pushed, while a tracking relationship tells Git which remote branch a local branch follows. Neither proves that the signed-in hosting identity has the intended rights. The clone's default branch can also differ from the proposal branch. Those boundaries matter before the first push: a correct contract edit sent to the wrong repository is still the wrong collaboration result.

The independent starter gives content and review context, not remote approval. Inspecting identity, remote URLs, local branch and proposed PR base makes the collaboration destination reviewable. Fetch updates remote-tracking information without automatically rewriting your branch. A private sandbox protects the teaching scope, and a local simulation must retain that label even if its history closely resembles a hosted workflow.


#### Challenge


Clone the instructor-designated private training repository into a fresh `lab/` directory inside your attempt. Confirm the permitted branch prefix and reviewer before beginning the proposal. If you need a personal training sandbox, arrange that setup with the instructor first.

Inspect the clone root, `git remote -v`, `git branch -vv` and `gh auth status`. Record the training identity, intended PR base and remote destination in the parent evidence note without credential values. Use the supplied contract baseline where needed. If the remote or reviewer is unavailable, practice locally with the scenario labelled simulated.


#### Hint


<details>
<summary>Verify the destination before writing a remote branch</summary>

Use an existing authorized training identity. Do not copy tokens into evidence. If `gh repo create` reports that the name exists, you already have a sandbox: clone it with `gh repo clone`.

Compare the repository identity shown by the hosting CLI with the clone's remote URL. A valid login can still target another account or repository. Read branch tracking separately from the current branch name. Keep tokens outside evidence; the safe identity, intended base and remote destination are enough to establish the collaboration boundary.

</details>

#### Check


Inspect and record the designated remote identity, inner clone root, local branch, tracking branch and intended PR base. The repository must be the authorized private training sandbox. Explain what fetch can update and what still requires merge or rebase into your local proposal. A successful clone alone does not establish the reviewer's availability or your final branch permissions.

Retain redacted identity/context observations without credentials. Distinguish real hosted state from a local scenario fixture. If no authorized remote exists, mark the live collaboration check pending and continue the local preparation. Never substitute a course or production remote merely because its URL is already configured.

```bash
git remote -v
git branch -vv
git rev-parse --show-toplevel
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#git-p2-01-reasoning)


---


<a id="git-p2-02"></a>

### git-p2-02: Push and propose a scoped pull request


<a id="git-p2-02-concept"></a>

#### Concept


A push makes branch commits available remotely; a pull request proposes how they should enter another branch. The PR description explains why the contract change matters and how its result was checked, while the diff shows the actual scope. A branch can exist without a PR, and a well-written local description can exist without either. The assessment therefore needs actual remote identity and head commit.

The deadline clarification should name time zone and expected consumer behavior without deleting grain or currency promises. A reviewer who did not attend the terminal session should understand the before/after requirement from the PR. Keeping the proposal on a feature branch preserves the sandbox main baseline and gives the later review response an identifiable place to land.


#### Challenge


Create a feature branch using the permitted prefix and clarify the delivery deadline/timezone in `contract.md`. Review the diff, commit it, and push the sandbox branch with an upstream. Use `gh pr create` against the intended base.

Describe the before/after consumer expectation and how you checked that grain, currency and owner facts survived. Inspect the hosted PR diff and head commit, then save its URL, branch and hash in the parent evidence note. Keep the proposal limited to this contract change. Compare local HEAD with the PR head before handing it to the reviewer.


#### Hint


<details>
<summary>Connect the proposed behavior to the actual hosted diff</summary>

Check gh pr create `--help` and gh pr view `--help` on the installed version.

Inspect the installed CLI help for proposal and viewing commands, then compare the returned PR base/head with your recorded boundary. A useful description says what changed for the consumer and what stayed valid in the contract. Avoid including every terminal operation or unrelated setup file in the proposal diff.

</details>

#### Check


The hosted PR must reference the intended private sandbox, base branch and proposal head. Its diff contains only the scoped contract clarification and preserves original grain/currency facts. Compare local HEAD with the remote PR head instead of retaining a URL detached from the current revision. Explain the separate roles of commit, push and PR.

A local body file, screenshots of a draft or a successful push without a PR do not satisfy this outcome. If remote access is unavailable, retain a reviewable draft and mark hosted creation pending. Keep all remote work in the designated training sandbox.

```bash
git show --stat HEAD
gh pr view --json url,baseRefName,headRefName,headRefOid
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#git-p2-02-reasoning)


---


<a id="git-p2-03"></a>

### git-p2-03: Respond to a review with a second commit


<a id="git-p2-03-concept"></a>

#### Concept


Review supplies another participant's reasoning about the proposed behavior. A revision is useful when the new commit addresses a concrete comment and the response explains how. Merely adding any second commit can satisfy a numerical count while leaving the requirement unanswered. The supplied scenario concerns deadline time zone and late-feed responsibility, so the change should make those facts clearer without introducing unrelated policy.

A real peer review differs from a learner playing both sides of a local simulation. Both can teach revision mechanics, but only the former establishes the collaboration boundary required here. The reviewer/comment identity, revision hash and current hosted diff let another person trace that conversation. Approval is also separate from a comment or a pushed response; report it only when the actual review state supports it.


#### Challenge


Ask the arranged instructor or paired reviewer to apply `review-scenario.json` to the sandbox PR. Read the actual comment and identify the unclear deadline or escalation responsibility. Clarify that requirement in `contract.md`, commit the revision and push the permitted branch.

Explain how the new diff addresses the comment. Retain the comment/reviewer identity, revision hash and remotely visible response in the parent note. Preserve the original proposal so the reviewer can compare it with the revision. A second commit must answer the review requirement; adding an unrelated change does not fulfill this task.


#### Hint


<details>
<summary>Tie the revision to one actual review requirement</summary>

The reviewer may use the prepared scenario in review-scenario.json. Instructor preparation includes arranging the reviewer.

Quote or summarize the specific requirement in your evidence note and compare it with the revision diff. A second commit should visibly address that requirement. Keep the reviewer arrangement as instructor preparation and do not assume a self-comment establishes another person's review. Inspect the hosted head after the response so an unpushed local edit cannot masquerade as a reviewed revision.

</details>

#### Check


The review evidence must identify another participant, the relevant comment and the remotely visible revision commit. Compare the new hosted diff with the comment's requirement and confirm deadline and escalation facts are now explicit. Retain the original proposal and response identities rather than replacing all evidence with the final text.

Explain why a commit count alone does not establish a useful response or approval. A simulated review needs that label and cannot close the real-human gate. Use the live verifier to inspect the existing PR and review state; record a missing reviewer or access prerequisite.

```bash
gh pr view --json reviews,commits,headRefOid
git show --stat HEAD
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#git-p2-03-reasoning)


---


<a id="git-p2-04"></a>

### git-p2-04: Integrate concurrent upstream work


<a id="git-p2-04-concept"></a>

#### Concept


An open proposal can become stale while another participant changes its base branch. Fetch updates your information about that upstream history; merge or rebase decides how it enters your proposal. Pull combines these operations according to configuration, which can conceal the decision if used without inspection. The final review should include both your clarification and the shared input-classification requirement.

The supplied concurrent edit adds internal input classification on main. A second clone can demonstrate the mechanics when that role is explicitly simulated, but the handoff should say who actually supplied the edit. A merge conflict requires the same requirement-preservation reasoning as foundation practice. An ancestor check proves history includes the upstream commit, while the final contract proves its content and your proposal both survived.


#### Challenge


Have the instructor supply the planned main-branch edit, `Input classification: internal`. A second clone may play that role for a labelled local simulation. Fetch origin and compare your feature branch with `origin/main` before integrating.

Follow the instructor's merge/rebase policy, preserving classification, deadline and escalation through any conflict. Inspect the complete contract and diff before pushing the permitted proposal branch. Save the upstream hash, integration result and final head. Explain which operation updated remote-tracking information and which incorporated the change into your proposal. If rebase changes hashes, follow the sandbox's remote-update policy.


#### Hint


<details>
<summary>Fetch informs the decision; integration changes your proposal</summary>

Use git log `--left-right` `--oneline` HEAD...origin/main before combining history.

Compare left/right history before integrating so you can identify which commits belong to each side. An updated remote-tracking branch does not automatically place its commit in your local proposal. After conflict repair, inspect the whole contract; an ancestor alone does not prove that a later edit preserved the classification text.

</details>

#### Check


The intended upstream commit must be an ancestor of the final proposal according to the chosen history policy, and the contract must retain the input classification alongside your reviewed deadline/escalation changes. Inspect the hosted PR head after the update and compare it with local HEAD. Explain what fetch changed and what integration changed.

Keep the original upstream identity and final integration evidence. If rebase rewrites proposal hashes, state that effect and follow the classroom remote-update policy rather than applying a broad force push. No course or production branch is part of the exercise. A local second-clone simulation remains clearly labeled, while actual remote concurrency evidence requires the designated sandbox.

```bash
git log --left-right --oneline HEAD...origin/main
git merge-base --is-ancestor "$DC_UPSTREAM_COMMIT" HEAD
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#git-p2-04-reasoning)


---


<a id="git-p2-05"></a>

### git-p2-05: Read the final review and merge state


<a id="git-p2-05-concept"></a>

#### Concept


A proposal's state reflects review, checks and branch policy, not just the last command exit. A green local workflow can coexist with an open PR awaiting review, and a review comment can coexist with no approval. The learner should identify the exact current state and its next authorized action. Some training sandboxes intentionally stop before merge so the review record remains inspectable.

Synchronizing local main after an authorized merge is another action, distinct from declaring that a proposal is ready. If a gate remains blocked, a useful handoff names it rather than manufacturing a merge hash. The actual head, review outcome, check state and retained contract facts let another participant assess completeness. This classroom evidence does not authorize merging production work or publishing the course repository.


#### Challenge


Inspect `gh pr view` and `gh pr checks` after the revision and upstream integration. State the current review outcome, checks, head commit and whether the PR is open, blocked or merged. Identify the next action under the instructor's merge policy.

Merge only when that sandbox policy permits it. After an authorized merge, synchronize local main and inspect the resulting contract; otherwise retain the open PR state. Write a short handoff naming the final branch, preserved requirements and remaining decision or access step. A successful local command does not establish another person's approval.


#### Hint


<details>
<summary>Report observed policy state instead of assuming approval</summary>

A real reviewer and repository permissions are prerequisites; missing access is a blocked live result.

Read the actual review and check fields rather than infer readiness from a green local command. A check command can return nonzero because checks are pending or absent, so inspect its meaning in the installed tool. Compare PR head to your current branch before summarizing. An honest open-state handoff is better evidence than an invented merge or a guessed approval.

</details>

#### Check


The handoff must match the current PR state, review outcome, checks and head commit in the authorized private sandbox. Deadline, escalation and concurrent input classification remain in the proposed or merged contract. Explain any pending gate and the next authorized action. If an actual merge occurred, identify its resulting base history; if it did not, preserve the open state explicitly.

Run read-only live verification with the designated repository/PR environment variables when available. It checks current remote evidence and another account's review; offline local history remains supporting for this phase. Do not claim peer approval from a self-comment or merge eligibility from a generic command success. No remote write is performed by the verifier.

```bash
gh pr view --json state,reviews,headRefOid
gh pr checks
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#git-p2-05-reasoning)


## Phase completion


Present the actual authorized sandbox PR, its scoped contract diff, review/comment identity, response commit, integrated upstream change and honest final review/merge state. Your local branch must include the supplied concurrent input-classification requirement as well as the explicit deadline and escalation clarification. Show the relationship between local HEAD and the current remote PR head. A simulated local workflow can support practice but cannot establish a real peer review or remote collaboration outcome.

Keep the copied attempt and evidence note, using only the designated private training repository for any authorized push or PR. Do not publish the course checkout or assume the exercise authorizes production merging. The verifier reads existing sandbox evidence; it does not create a repository, push, invite a reviewer or merge automatically. A human reviewer and the instructor's merge policy remain real prerequisites. Report an open or blocked PR truthfully instead of inventing approval. Your handoff should let another participant understand which branch contains the final requirements and which decision or access step remains pending.

---


## Optional stretch


The core completion standard is independent of optional work. Choose a separately timed route from [the stretch guide](stretch/README.md).

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Clone and inspect a collaboration boundary

<a id="git-p2-01-reasoning"></a>

<details>
<summary>Reasoning for git-p2-01: Repository destination, identity and tracking are separate checks</summary>

The remote identifies where commits go; tracking identifies the remote branch relationship; hosting identity supplies permissions. All must agree with the designated sandbox before a write. Clone and fetch are prerequisites, not evidence of a PR or peer review. Keep a local simulation explicitly separate and record missing human/access preparation rather than silently choosing another repository.

[Return to git-p2-01](#git-p2-01)

</details>

### Reasoning: Push and propose a scoped pull request

<a id="git-p2-02-reasoning"></a>

<details>
<summary>Reasoning for git-p2-02: A proposal needs remote identity as well as clear prose</summary>

The branch commits and hosted PR are related but distinct artifacts. The actual base/head and diff must match the designated sandbox and current proposal. The description explains consumer behavior and verification without replacing the diff. A local draft remains useful supporting material but cannot be presented as a remotely created PR.

[Return to git-p2-02](#git-p2-02)

</details>

### Reasoning: Respond to a review with a second commit

<a id="git-p2-03-reasoning"></a>

<details>
<summary>Reasoning for git-p2-03: A review response must address the actual comment</summary>

The second commit should explain and implement the requested clarification. Its remote head and diff establish that the response is available for review; another participant's comment establishes peer involvement. A self-simulation remains supporting practice. Comment, response and approval are different states, so none should be inferred simply from two commits.

[Return to git-p2-03](#git-p2-03)

</details>

### Reasoning: Integrate concurrent upstream work

<a id="git-p2-04-reasoning"></a>

<details>
<summary>Reasoning for git-p2-04: An integrated requirement needs ancestry and retained content</summary>

Fetch obtains upstream history but does not decide how your proposal combines it. The chosen integration must retain both concurrent classification and the reviewed clarification. An ancestry check and final diff protect different parts of that result. If the concurrent role or remote action was simulated, record it honestly instead of treating local mechanics as actual hosted collaboration.

[Return to git-p2-04](#git-p2-04)

</details>

### Reasoning: Read the final review and merge state

<a id="git-p2-05-reasoning"></a>

<details>
<summary>Reasoning for git-p2-05: Completion evidence states the real collaboration boundary</summary>

The current hosted review/check/head state controls the handoff. Open or blocked states must remain visible when the sandbox policy stops there. Local mechanics and a second commit do not establish approval. The read-only verifier can inspect existing evidence, while reviewer participation and merge authorization remain separate classroom decisions. Preserve contract facts and identify the next action without inventing a merge.

[Return to git-p2-05](#git-p2-05)

</details>


---

# git independent starter

Read the [owning phase](../README.md) before editing. Prepare from the training project root with `mise run challenge:v2:prepare git phase-two-proficient`; edit the copied attempt.

## Authored-file list

| Task | Learner-authored paths |
|---|---|
| git-p2-01, git-p2-02, git-p2-03, git-p2-04, git-p2-05 | `lab/contract.md`, `evidence.md` |

## Declared baseline

The supplied contract is the starting point. Create the inner Git repository under `lab/` and keep `evidence.md` outside it, beside the copied starter. The advanced phase also supplies a review scenario; the training remote and reviewer are arranged separately.

Use a fresh workspace for another attempt; preparation and reset preserve existing work.


---

# git optional stretch


Choose an optional exercise after the advanced core. Allow 20–40 minutes for each and use a fresh copy of your completed baseline. Keep the assessed attempt unchanged.


## Optional exercises


<a id="git-stretch-01"></a>

### git-stretch-01: Compare merge and rebase on disposable local history


<a id="git-stretch-01-concept"></a>

#### Concept

Merge and rebase can combine related work while presenting different ancestry. A merge retains the divergent histories and can record a commit with both parents. Rebase reapplies commits onto another base, changing their identities even when the resulting contract content is similar. Neither automatically decides the right business requirement, and rebasing already shared work introduces a coordination question beyond this local comparison.

Use a disposable local copy with a known common baseline and two nonconflicting contract edits. The comparison should show final content, parent relationships and rewritten hashes rather than declare one graph universally better. The permitted sandbox review policy still governs the actual advanced collaboration route. Keeping the experiment separate prevents a history-style exercise from rewriting someone else's shared proposal.

#### Challenge

Create two independent local copies of a completed contract fixture. In one, merge the prepared upstream requirement into the feature branch; in the other, rebase the equivalent feature commits onto that upstream baseline. Inspect both graphs and final contract projections. Record which hashes changed and which business facts stayed identical. Do not push either comparison or rewrite a shared remote branch. Explain when a team might prefer each history presentation and what additional coordination shared rebasing would require.

Record the shared baseline and the two separate final projections before choosing a preferred explanation of their history.

#### Hint

<details>
<summary>Compare content separately from history</summary>

Choose genuinely separated edits so this comparison focuses on ancestry rather than another conflict exercise. Capture commit IDs before rebase; otherwise a claim that identities changed cannot be checked. Compare the final contract content separately from graph shape. If an unexpected conflict appears, record and resolve it intentionally rather than delete one requirement to obtain a tidy graph.

</details>

#### Check

Inspect the merge parents, rebased ancestry, original/new feature hashes and final file content. Both variants must preserve the same contract requirements, while the rebase variant should show rewritten feature identities. Retain commands and observations from the two disposable repositories and explain which conclusion follows from each projection.

A cleaner-looking graph is not a correctness test, and unchanged file content does not mean commit identities were preserved. No remote operation is necessary or authorized by this optional comparison. Keep the actual advanced PR untouched. If your history did not diverge, prepare a meaningful shared baseline before claiming the comparison. This is separately timed depth after core completion, not a substitute for real review evidence.

<!-- variation: none; this entire exercise is optional and separately timed. -->

[Optional contents](#optional-exercises) · [Reasoning key](#git-stretch-01-reasoning)

---


<a id="git-stretch-02"></a>

### git-stretch-02: Recover a lost local branch reference through reflog


<a id="git-stretch-02-concept"></a>

#### Concept

A branch is a reference into existing commit history. Moving or deleting a local reference can make a useful commit less visible without immediately destroying the underlying object. Reflog records recent reference movements and can help recover the intended local state. Its retention is bounded by repository behavior and garbage collection, so its bounded reference record cannot replace durable commits and a separately preserved backup.

The exercise uses only disposable committed work. A reflog entry can identify an earlier commit, but restoring that pointer does not automatically recover an uncommitted file that was discarded. Keep those recovery cases distinct. The foundation restore task handled an accidental uncommitted edit; this optional experiment concerns a committed change whose branch reference moved.

A recovered pointer still needs its committed file content checked.

#### Challenge

In a new disposable local copy, create `recovery-demo`, commit a distinctive contract note and record its hash. With that commit at the branch tip and no uncommitted edits, move only `recovery-demo` back one commit using `git reset --keep HEAD~1`. This intentionally removes the committed note from the working file; `--keep` refuses a change that conflicts with uncommitted edits. Inspect `git reflog` to locate the saved commit, then use `git switch -c recovered-note` with that hash to create a recovery branch at it. Compare recovered file content and history with the saved expected hash. Keep the production/course repository and actual advanced sandbox untouched, and preserve the original completed attempt before starting.

Keep the expected commit identity in the parent evidence note and inspect the recovered branch without changing another reference.

#### Hint

<details>
<summary>Save the expected commit before moving a reference</summary>

Write down which reference you intend to move and where the useful commit will remain observable. Use the saved hash as an independent recovery expectation rather than picking a plausible-looking reflog line. Reflog records reference activity, not every editor change. Prefer creating a recovery branch over deleting or rewriting more history while diagnosing the lost reference.

</details>

#### Check

The recovery branch must point to the intended committed note and retain its expected content. Inspect reflog entry, saved hash, recovery branch and file projection, explaining which operation moved a reference and which operation made the commit reachable again. The original completed core attempt must remain unchanged.

A branch with the same name but different content fails the recovery outcome. Do not claim that this technique recovers every discarded working edit or provides permanent retention. Keep remote actions out of the experiment and record its separate timing. The result should teach a bounded recovery mechanism after core completion, with any unsupported tool behavior recorded rather than worked around through broad resets.

<!-- variation: none; this entire exercise is optional and separately timed. -->

[Optional contents](#optional-exercises) · [Reasoning key](#git-stretch-02-reasoning)

---


## Reasoning keys


<a id="git-stretch-01-reasoning"></a>

<details>
<summary>Reasoning for git-stretch-01: Ancestry and content answer different questions</summary>

Merge preserves the original feature commits and combines divergent parents. Rebase creates new feature commits on the updated base, so their hashes change. Both histories can preserve the same contract text. Compare ancestry and final requirements separately; shared-branch policy determines whether rewritten history is appropriate for a team.

[Return to git-stretch-01](#git-stretch-01)

</details>

<a id="git-stretch-02-reasoning"></a>

<details>
<summary>Reasoning for git-stretch-02: Recover the intended commit, then check its content</summary>

A recovery branch makes the recorded commit reachable through a name again. The saved hash and committed note verify that you recovered the intended state. Reflog can help locate a moved reference, but its entries expire and it does not record every discarded working edit. Keep a durable backup for work that must survive.

[Return to git-stretch-02](#git-stretch-02)

</details>


---

# docker challenges

Docker packages a supplied six-holding summary app so its execution and filesystem boundary can be inspected. Foundation work develops image/container lifecycle, shell isolation, read-only mounts and simple packaging. Advanced work separates named test/runtime targets, verifies actual non-root identity and focused contents, and diagnoses a path assumption. The app is supplied so authoring focuses on runtime behavior. Its small fixture is separate from the later Databricks datasets.

## Before you start

Use the delivered client with the prepared training engine and pulled base image. Prepare a copied attempt through mise, choose unique owned names/tags and work from its root so the build context is clear. Mount only the chosen app directory when that task calls for a mount. Engine access and image downloads are preparation, not packaging evidence. The local Python oracle remains supporting when Docker is unavailable. Never use broad pruning, privileged execution or another learner's resource as a shortcut around a path or name collision.

## Suggested timeline and tasks

Estimates include reading, practice, checks and explanation. Allow additional time for environment setup and optional extensions.

| Phase | Task | Minutes |
| --- | --- | --- |
| Foundation | [docker-p1-01: Run an image and inspect the lifecycle](phase-one-certified/README.md#docker-p1-01) | 12–18 |
| Foundation | [docker-p1-02: Explore an interactive shell](phase-one-certified/README.md#docker-p1-02) | 12–18 |
| Foundation | [docker-p1-03: Use a bounded bind mount](phase-one-certified/README.md#docker-p1-03) | 12–18 |
| Foundation | [docker-p1-04: Author and run a simple holdings image](phase-one-certified/README.md#docker-p1-04) | 12–18 |
| Foundation | [docker-p1-05: Prove repeatability and clean scoped resources](phase-one-certified/README.md#docker-p1-05) | 12–18 |
| Advanced | [docker-p2-01: Separate named build targets](phase-two-proficient/README.md#docker-p2-01) | 15–22 |
| Advanced | [docker-p2-02: Gate the runtime on a tested artifact](phase-two-proficient/README.md#docker-p2-02) | 15–22 |
| Advanced | [docker-p2-03: Run with a bounded runtime user](phase-two-proficient/README.md#docker-p2-03) | 15–22 |
| Advanced | [docker-p2-04: Keep runtime contents focused](phase-two-proficient/README.md#docker-p2-04) | 15–22 |
| Advanced | [docker-p2-05: Repair a path assumption and explain the result](phase-two-proficient/README.md#docker-p2-05) | 15–22 |

## Choose your phase

- [Foundation](phase-one-certified/README.md): Foundation core with explicit completion evidence.
- [Advanced](phase-two-proficient/README.md): Independent advanced baseline and finite core, separately timed.

Finish the core tasks before choosing optional stretch.

## Teaching concepts

Image identity, process lifecycle, writable layer, mount path and working directory each explain a different observation. Build success does not establish runtime output, a USER line does not establish actual process identity, and a stage named test does not establish an enforced oracle. Pair artifact inspection with the independent six-holding result. The phase reasoning keys remain after the work, while full reference Dockerfiles are separate instructor material. Optional cache/size analysis does not replace the finite core.


---

# docker: Phase 1 — foundations

## Purpose and outcome

Package and run a tiny portfolio-summary application while learning image/container boundaries. The app is supplied so your authoring focuses on Docker rather than rewriting business logic. You inspect process lifecycle and filesystem isolation, use a controlled mount, write a simple Dockerfile and prove the packaged app's output.

## Dataset and pipeline

The fixture under app contains six holdings and a standard-library summary script. Its total market value is 12,011,626.50. This small Docker fixture is distinct from the eight-row supplied Databricks Portfolio Analytics case; do not present its output as that pipeline's completion. The app reads a file relative to its working directory, so runtime path and copied input matter. A supplied Python test independently checks the fixture/application result. A container can exit normally after printing the summary because its main process has finished.

## Prerequisites and workspace

Use the delivered Docker client with access to the prepared training engine, Python for the optional local app check, and a pulled base image. Prepare a copied attempt through the version-explicit mise task, then work from its root. Choose a unique container name and image tag so two learners do not collide. The engine and image-pull boundary should be ready before timed practice; source presence alone does not establish either.

```bash
mise run challenge:v2:prepare docker phase-one-certified
cd .local/challenges-v2/docker/phase-one-certified
export DC_DOCKER_NAME=dc_alex_docker01
export DC_DOCKER_TAG=dc-alex-docker01:practice
docker version
```

Keep commands inside this attempt and mount only its chosen app directory, using an absolute host path. Do not mount the host root, create privileged containers or remove shared images to repair a path mistake. If an interactive terminal is unavailable, use a documented noninteractive inspection command and label that variation. A new attempt gets a fresh workspace and name; reset does not delete existing work.

## Starter behavior

The supplied Dockerfile is a benign buildable placeholder that prints its unfinished status and exits successfully. That behavior proves a starter can launch, not that you packaged the app. The Python summary and test work outside Docker from the app directory. Replace the Dockerfile's placeholder with the named authoring outcome before expecting completion verification to pass. Read-only mount writes intentionally fail later; an unavailable engine or image download is a prerequisite failure, not that teaching drill. Keep those failure categories separate in evidence.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 60–90 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [docker-p1-01: Run an image and inspect the lifecycle](#docker-p1-01) | 12–18 | Hello output, actual image/container identity and exit status |
| [docker-p1-02: Explore an interactive shell](#docker-p1-02) | 12–18 | Inside file disappears in a fresh disposable execution; version/OS evidence |
| [docker-p1-03: Use a bounded bind mount](#docker-p1-03) | 12–18 | Actual fixture summary and expected write denial; host input unchanged |
| [docker-p1-04: Author and run a simple holdings image](#docker-p1-04) | 12–18 | Authored image emits independent six-holding result |
| [docker-p1-05: Prove repeatability and clean scoped resources](#docker-p1-05) | 12–18 | Two matching outputs from one image identity; only owned resources removed |

## Core challenges


<a id="docker-p1-01"></a>

### docker-p1-01: Run an image and inspect the lifecycle


<a id="docker-p1-01-concept"></a>

#### Concept


A container's main process determines its lifetime. A short program that prints and exits can be a successful container execution; keeping it alive with an unrelated sleep would change the behavior being inspected. The image is a reusable package, while the container is one process execution with its own writable layer and recorded state. Removing that container does not automatically delete the image.

The hello command makes this distinction visible before app packaging. Inspecting all containers includes stopped executions that a default running-only list omits. Logs and exit status answer whether the process ran as expected, while the image identifier answers which package ran. A familiar tag can point to a different image later, so retain the actual identifier when comparing runs.


#### Challenge


Run `docker version` and `docker info`, then launch the hello process using your unique container name:

```bash
docker run --name "$DC_DOCKER_NAME" python:3.11-slim python -c "print('hello holdings')"
```

Inspect its logs, state, exit code and actual image identifier. Explain why successful output leaves a stopped container. Retain those observations, then remove only this named execution. If the engine or base image is unavailable, resolve that preparation issue before interpreting program behavior. Do not keep the hello process alive with a sleep: its normal completion is the lifecycle observation.


#### Hint


<details>
<summary>A successful short process can leave a stopped container</summary>

Use docker ps -a to include stopped containers. Instructor preparation supplies Docker and a pulled base image.

Use the stopped-container view and inspect the named execution rather than searching for any green-looking process. The expected hello output comes from its main command, not an image build. Keep removal separate from image cleanup so you can explain which state disappears. A name already in use means choose or inspect your owned attempt, not delete an unknown container.

</details>

#### Check


Expect the named execution's logs to contain the declared hello output and its process exit status to be zero. Retain container and image identifiers and explain the stopped state. Removing the execution should leave the reusable image available; inspect that distinction rather than infer it from a command message.

A printed client version alone does not prove engine access or process execution. If a preexisting name prevents launch, use a unique owned name and record the collision instead of removing someone else's container. This lifecycle observation is separate from the final six-holding app result and cannot be counted as completed packaging.

```bash
docker ps -a
docker logs "$DC_DOCKER_NAME"
docker inspect "$DC_DOCKER_NAME"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p1-01-reasoning)


---


<a id="docker-p1-02"></a>

### docker-p1-02: Explore an interactive shell


<a id="docker-p1-02-concept"></a>

#### Concept


A container writable layer belongs to that execution. Creating a temporary file inside one disposable container does not place it in the base image or the host application folder. A fresh execution of the same image starts from its packaged filesystem and a new writable layer. This is why an unmounted scratch file disappears after the first container is removed.

An interactive shell changes how you inspect the process, not whether it shares the host kernel. The terminal flags attach input and a pseudo-terminal; a noninteractive command can inspect the same filesystem facts when the classroom interface lacks a terminal. Keep the image's OS/runtime observations distinct from the author's host environment. A container is not automatically a virtual machine with a separate kernel.


#### Challenge


Start a disposable shell with `docker run --rm -it python:3.11-slim bash`. Inspect `pwd`, Python's version and `/etc/os-release`. Create `/tmp/inside.txt`, exit, then launch a fresh container from the same image and test whether the file exists.

Record both execution identities and observations. If an interactive terminal is unavailable, use a noninteractive command for the same creation/removal experiment and explain that choice. Keep both executions unmounted and leave the shared base image unchanged. A volume or a committed replacement image would introduce persistence and change the question being tested.


#### Hint


<details>
<summary>Compare fresh executions without adding persistence</summary>

The terminal flags attach standard input and a TTY; `--rm` removes the exited container.

Compare the two executions' identities and filesystem observations. The first file was created after launch, so it belongs to that writable layer. Do not commit the container into another image or add a volume during this experiment; either would change the persistence contract. A missing interactive terminal should change the inspection method, not the expected filesystem result.

</details>

#### Check


The second fresh execution should not contain the temporary file from the first removed container. Retain the first successful creation and second absence check with Python/OS observations. Explain which filesystem content came from the image and which was created at runtime. An accidentally reused container would not test the same claim.

Record the interactive or noninteractive method and why it was used. Do not describe the outcome as a separate-kernel virtual machine demonstration. The observation establishes disposable writable-layer behavior, not every possible persistence mechanism; the next mount task deliberately changes that boundary.

```bash
docker run --rm python:3.11-slim python -c "from pathlib import Path; print(Path('/tmp/inside.txt').exists())"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p1-02-reasoning)


---


<a id="docker-p1-03"></a>

### docker-p1-03: Use a bounded bind mount


<a id="docker-p1-03-concept"></a>

#### Concept


A bind mount exposes a selected host path at a container path. The target can replace what the image would otherwise show there, so both path and access mode matter. Read-only access lets the supplied summary read its fixture while protecting that copied input from container writes. Mounting an entire workspace would broaden the boundary beyond what this task needs.

The app reads its CSV relative to the working directory. A correct mount at one path with execution in another can still fail, even though the file exists somewhere inside the container. Comparing the host and mounted input plus the app output distinguishes this path error from a business-data defect. The deliberate write denial demonstrates the mount promise and should not be repaired by removing read-only protection.


#### Challenge


From the copied starter, run the supplied summary with `app/` mounted read-only at `/app` and `/app` as the working directory. Use an absolute host path. Compare the copied input with what the container reads.

Attempt a container-side write to the mounted input directory, retain the expected denial and verify the host copy did not change. Explain the source path, target path and access mode separately. If the summary cannot find its CSV, inspect the working directory before changing permissions. Keep the mount limited to the app directory rather than broadening it to the whole workspace.


#### Hint


<details>
<summary>Align the mount target and app working directory</summary>

Use an absolute host path from pwd and the :ro mount suffix. Do not mount the entire host root.

Check source path, container target and working directory as three separate values. The read-only suffix belongs to the mount declaration; do not assume the app itself protects the input. If summary cannot find its CSV, inspect the current directory before weakening permissions or mounting more host content. The write should fail while the read remains successful.

</details>

#### Check


The mounted app run must produce six holdings with total market value 12,011,626.50, matching the local fixture oracle. The controlled container-side write must fail for the read-only mount reason, and the host input hash/content must remain unchanged. Retain command, exit categories and output rather than only an image of the mounted folder.

Explain which files come from the image and which from the host mount, and why the current directory affects this app's relative CSV path. An engine or image-pull failure does not count as the intended write-denial drill. Do not remove the protection to make the negative command green.

```bash
docker run --rm -v "$PWD/app:/app:ro" -w /app python:3.11-slim python summarize.py
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p1-03-reasoning)


---


<a id="docker-p1-04"></a>

### docker-p1-04: Author and run a simple holdings image


<a id="docker-p1-04-concept"></a>

#### Concept


An image build records filesystem content and startup configuration. Copying the supplied app into an image and selecting its working directory makes runtime independent of a host bind mount. The build context limits which files are available to copy, and the startup command determines which process runs. A benign placeholder Dockerfile can build successfully while still lacking the assessed application.

WORKDIR sets the directory for subsequent relative paths, COPY adds build-context files, and CMD selects the default process. The app's path assumption means copied files and working directory must agree. Packaging the test alone or printing the expected text would bypass the application behavior. The independently supplied test and fixture output make that distinction reviewable. Build success establishes that instructions could be executed; only running the resulting image establishes its main process and actual app result.


#### Challenge


Replace the placeholder Dockerfile with a `python:3.11-slim` image, working directory `/app`, copied app files and default `summarize.py` command. Use your attempt root as the build context and keep the supplied application logic unchanged.

Build with `$DC_DOCKER_TAG`, inspect the actual image identifier, then run without a host app mount. Retain the build log and summary output. Explain how FROM, WORKDIR, COPY and CMD contribute to the packaged workload. The resulting image must contain the script and its CSV at paths the default command can use; a successful build alone does not establish that result.


#### Hint


<details>
<summary>Run the packaged app without relying on a host mount</summary>

The build context is the copied starter directory; COPY cannot read an arbitrary parent directory.

Read the app's relative CSV path and arrange the copied filesystem accordingly. Use the copied attempt as build context, not an unrelated parent folder. If output still says valid starter, the placeholder command remains. Inspect the build/run logs and image identity before assuming the engine used your latest Dockerfile.

</details>

#### Check


The authored image must emit the actual summary: six holdings and total market value 12,011,626.50. It must do so without mounting the host app directory, and its main process should exit successfully. Run the supplied local test as the independent fixture/application oracle, then retain the build log, actual image identifier and runtime output.

Explain how working directory, copied files and startup command jointly satisfy the app's path contract. A successful placeholder build, hard-coded echo or local-only Python result does not satisfy image packaging. Keep unavailable engine checks pending; direct source inspection remains useful but cannot establish built-image contents.

```bash
docker build --progress=plain -t "$DC_DOCKER_TAG" .
docker run --rm "$DC_DOCKER_TAG"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p1-04-reasoning)


---


<a id="docker-p1-05"></a>

### docker-p1-05: Prove repeatability and clean scoped resources


<a id="docker-p1-05-concept"></a>

#### Concept


Repeatability means a known package and input produce the stated result across executions. A mutable tag alone is weaker identity than the image ID because the tag can be rebuilt between runs. Two disposable runs from the same image should both print the six-holding fixture result and exit normally. Their writable layers are separate even though their package is shared.

Cleanup is also an ownership decision. Removing every container or pruning all images would interfere with other learners and erase useful evidence. The exercise names its own containers/tags and retains logs and identities before removal. A build cache or shared base image need not be deleted to finish the core. Repeatability here concerns this supplied app and fixture, not every external dependency or production deployment scenario.


#### Challenge


Run the finished image twice with `--rm`, recording the actual image ID and both outputs. Inspect its configured command and working directory. Explain whether changing `holdings.csv` on the host would change an already-built image.

Compare both runs with the independent fixture expectation. List this attempt's leftover containers and tag, retain the needed logs, then remove only those named resources when instructed. Keep the authored Dockerfile and local app test for review. Explain how image, container, writable layer and mount differ, and why rebuilding copied input differs from mounting a changed host file.


#### Hint


<details>
<summary>Compare actual image identity before cleaning named resources</summary>

Use docker image inspect v2-holdings:p1. Rebuilding is necessary for a copied input change.

Capture image identity before both runs so a rebuilt tag cannot masquerade as one package. Disposable execution removal handles its container but does not necessarily remove the image tag. List owned resources explicitly before cleanup. If a name or tag was shared accidentally, resolve ownership rather than invoking a broad prune.

</details>

#### Check


Both finished runs must produce the same six-holding total and successful exit from the same actual image identity. Retain outputs and identity before cleanup, and show that only your named resources were removed. The final Dockerfile remains reviewable and its local test still establishes the fixture expectation.

Explain why matching tags are weaker evidence than matching image IDs and why container removal differs from image/tag removal. A broad prune or deletion of another learner's resource fails the safe completion contract. The local verifier can check supplied app arithmetic without an engine, but image runtime repeatability stays pending unless the real build/run boundary was exercised.

```bash
docker image inspect "$DC_DOCKER_TAG"
docker run --rm "$DC_DOCKER_TAG"
docker run --rm "$DC_DOCKER_TAG"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p1-05-reasoning)


## Phase completion


Submit the simple Dockerfile and evidence showing image identity, container lifecycle, isolated filesystem, a bounded read-only bind mount and the actual six-holding application output. The printed summary must be six holdings with total market value 12,011,626.50, matching the supplied app's independent fixture check. A valid starter message is deliberately not that result. Retain repeated runs from the same image and explain why an exiting application can be successful without becoming a long-lived service.

Clean only the named exercise containers and tags, preserving another learner's resources and any evidence needed for review. The local app test can run without Docker and gives supporting expected-output evidence; the build/run/user/filesystem boundaries require a real engine. Mark unavailable engine or image-pull checks pending instead of treating a source Dockerfile as a built image. Foundation work is independent of Databricks access and does not replace the later Portfolio Analytics pipeline. Optional multistage work belongs to the independently prepared advanced phase.

---


## Optional stretch


The core completion standard is independent of optional work. No additional stretch is required in this phase; the next phase has an independently prepared entry baseline.

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Run an image and inspect the lifecycle

<a id="docker-p1-01-reasoning"></a>

<details>
<summary>Reasoning for docker-p1-01: Lifecycle state follows the main process</summary>

A zero-exit hello process is successful even though the container is stopped. Logs, exit status and actual identifiers establish that execution. Container removal and image removal affect different resources. Client installation is only a prerequisite, and this hello result is not evidence that the supplied app was packaged.

[Return to docker-p1-01](#docker-p1-01)

</details>

### Reasoning: Explore an interactive shell

<a id="docker-p1-02-reasoning"></a>

<details>
<summary>Reasoning for docker-p1-02: A writable layer is different from image or mounted persistence</summary>

The temporary file belongs to the first execution's writable layer and is absent in a fresh container from the unchanged image. Reusing the same execution or adding a volume would change that experiment. Interactive flags affect inspection, not kernel isolation. Record actual runtime observations separately from the author's host.

[Return to docker-p1-02](#docker-p1-02)

</details>

### Reasoning: Use a bounded bind mount

<a id="docker-p1-03-reasoning"></a>

<details>
<summary>Reasoning for docker-p1-03: Mount permissions and runtime paths protect different obligations</summary>

The selected host app path is readable in the container but deliberately not writable. The working directory makes its relative CSV lookup correct. Expected summary and expected write denial are complementary observations; a failure before mounting proves neither. Keep the host input unchanged and avoid broad mounts that would obscure the intended boundary.

[Return to docker-p1-03](#docker-p1-03)

</details>

### Reasoning: Author and run a simple holdings image

<a id="docker-p1-04-reasoning"></a>

<details>
<summary>Reasoning for docker-p1-04: Build and runtime output establish different steps</summary>

The Dockerfile must package the supplied script and fixture at a working directory that satisfies its relative lookup. A real run without a host mount proves those files are in the image. The placeholder is intentionally buildable but incomplete. Independent app output, image identity and selected logs prevent build success or echoed text from substituting for the authored packaging result.

[Return to docker-p1-04](#docker-p1-04)

</details>

### Reasoning: Prove repeatability and clean scoped resources

<a id="docker-p1-05-reasoning"></a>

<details>
<summary>Reasoning for docker-p1-05: Repeatability needs package identity and bounded ownership</summary>

Distinct executions can share the same immutable image ID and independent writable layers. Matching expected output from that identity demonstrates this bounded app result. Cleanup preserves evidence and removes only named owned resources, leaving shared bases and other learners intact. Local fixture tests supplement rather than replace the actual image build/run observations.

[Return to docker-p1-05](#docker-p1-05)

</details>


---

# docker independent starter

Read the [owning phase](../README.md) before editing. Prepare from the training project root with `mise run challenge:v2:prepare docker phase-one-certified`; edit the copied attempt.

## Authored-file list

| Task | Learner-authored paths |
|---|---|
| docker-p1-01, docker-p1-02, docker-p1-03, docker-p1-05 | `evidence.md` |
| docker-p1-04 | `Dockerfile`, `evidence.md` |

## Declared baseline

The app and independent Python test are supplied. The Dockerfile builds a placeholder image; replace its unfinished configuration to package the app. A successful placeholder build is not completion.

Use a fresh workspace for another attempt; preparation and reset preserve existing work.


---

# docker: Phase 2 — advanced practice

## Purpose and outcome

Design a bounded multistage image for the supplied summary app. Advanced work separates test and execution concerns, selects named targets deliberately, runs with a suitable user and diagnoses a real path assumption. You author Docker configuration and evidence; the app and expected fixture result remain supplied so the focus stays on runtime boundaries.

## Dataset and pipeline

The advanced copy contains the same six-holding app fixture and independent test as foundation practice. Its expected total is 12,011,626.50. This app dataset is distinct from the assigned Databricks Portfolio/Atlas sources. A build stage supplies files, a named test target executes the oracle, and a runtime target includes only the app/input needed for execution. The exact stage graph determines whether runtime receives a tested artifact and what a target build actually executes.

The app resolves its CSV from the current working directory. A deliberately wrong copy destination or directory can therefore make a perfectly built image fail at runtime. The named targets and actual filesystem/user inspections provide evidence that cannot be replaced by reading FROM, USER or COPY text alone.

## Prerequisites and workspace

Prepare an independent advanced attempt through mise from the training project root. Use the delivered engine and prepared base image, then choose distinct test/runtime tags for your attempt. The advanced starter includes app/test inputs without requiring your completed foundation Dockerfile. Work from the copied root so build context and relative source paths are unambiguous.

```bash
mise run challenge:v2:prepare docker phase-two-proficient
cd .local/challenges-v2/docker/phase-two-proficient
export DC_DOCKER_TEST_TAG=dc-alex-docker02:test
export DC_DOCKER_RUNTIME_TAG=dc-alex-docker02:runtime
```

Record actual engine/base identities before comparing builds. Non-root identity and file permissions should be tested in a real container; source configuration only states intent. Avoid privileged options, broad host mounts and global image pruning. Engine access and image pulls belong to preparation outside the unpiloted task estimate. If unavailable, continue Dockerfile review and the local app oracle while leaving actual target/user/filesystem checks pending.

## Starter behavior

The copied Dockerfile still prints a benign placeholder and has no completed multistage outcome. A successful starter build is deliberate but cannot pass the finished target checks. Both app and Python oracle work from their supplied directory. You must author named test/runtime targets, meaningful test execution, required non-root user and focused runtime contents. The path defect is introduced later in a disposable version after a working baseline, so an initial missing engine or image is not its intended failure. Preserve a known working Dockerfile before the drill.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 75–110 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [docker-p2-01: Separate named build targets](#docker-p2-01) | 15–22 | Actual target image IDs and expected target outputs |
| [docker-p2-02: Gate the runtime on a tested artifact](#docker-p2-02) | 15–22 | Test failure blocks accepted runtime artifact path; repaired test/app succeeds |
| [docker-p2-03: Run with a bounded runtime user](#docker-p2-03) | 15–22 | Runtime UID 10001; app reads intended files and still prints expected summary |
| [docker-p2-04: Keep runtime contents focused](#docker-p2-04) | 15–22 | Required app/input present; test script absent; expected output preserved |
| [docker-p2-05: Repair a path assumption and explain the result](#docker-p2-05) | 15–22 | Predicted missing-file failure followed by repaired expected output and explanation |

## Core challenges


<a id="docker-p2-01"></a>

### docker-p2-01: Separate named build targets


<a id="docker-p2-01-concept"></a>

#### Concept


A multistage file defines a dependency graph of named build stages. Selecting one target chooses the output image and the stages it depends on; it does not automatically publish every intermediate stage as a separate tagged image. The test target and runtime target therefore need deliberate build/tag commands when both are review artifacts.

Named stages also communicate purpose. A runtime target should contain the executable app/input, while a test target can retain the independent test script and its command. The source file alone cannot show which target an actual build selected or whether a cached stage was reused. Record command, target and resulting image identity so a reviewer can connect intended architecture with observed output.


#### Challenge


Create named `base`, `test` and `runtime` stages in the Dockerfile. The test target runs `test_summary.py`; runtime runs `summarize.py`. State their dependency relationship and how tested app/input reaches runtime.

Build test with `$DC_DOCKER_TEST_TAG` and runtime with `$DC_DOCKER_RUNTIME_TAG`. Inspect both resulting image IDs and run the targets separately. Keep the selected target explicit in each command so a default final-stage build cannot stand in for two outputs. Retain the commands and explain which prerequisite stages each target used. Check that the named stages match the verifier's expected interface.


#### Hint


<details>
<summary>Target selection follows the stage graph, not every FROM line</summary>

Use FROM ... AS name and COPY `--from`=test for the selected runtime artifacts.

Draw the small stage dependency graph before writing COPY references. A target flag chooses an output, while a tag names the resulting image. Inspect the actual selected stage command and runtime output to distinguish a test image from an app image. If a stage is unreachable from the selected target, its existence in source is not proof it ran.

</details>

#### Check


The test and runtime target builds must produce identifiable separately tagged images. Running test must emit the supplied oracle success, and running runtime must emit the six-holding summary. Retain both target commands, image IDs and outputs, explaining which stages each depended on.

A default final-stage build alone does not prove the separate test image exists or executed. An echoed success string also does not replace the supplied test behavior. If the engine cannot run here, leave build/target observations pending while preserving a source graph that can be inspected. The finished verifier builds the named targets, not arbitrary intermediate indexes.

```bash
docker build --target test -t "$DC_DOCKER_TEST_TAG" .
docker build --target runtime -t "$DC_DOCKER_RUNTIME_TAG" .
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p2-01-reasoning)


---


<a id="docker-p2-02"></a>

### docker-p2-02: Gate the runtime on a tested artifact


<a id="docker-p2-02-concept"></a>

#### Concept


A testing stage is useful when it validates the artifact that runtime receives. An unrelated test command in an unreachable stage can look reassuring while providing no gate. The stage graph should connect the tested app/input to the runtime copy path, and a build-time assertion or equivalent explicit workflow should reject an incorrect artifact before acceptance.

The supplied Python test computes the fixture expectation independently of a hard-coded echo. The tiny app's baseline result is fixed, so a controlled copied input or app-path defect should make that assertion fail. Keeping the test's purpose visible prevents a Dockerfile from satisfying advanced work merely by naming a stage test. The runtime output remains a separate observation after the test succeeds.


#### Challenge


Add `RUN python test_summary.py` to the test stage. Wire runtime's COPY or inheritance path to the same app/input that the test validates. Build the valid target and retain its success.

In a separate copied build context, change one holding amount by a known value and predict the oracle failure. Rebuild, inspect the failed assertion, then restore the fixture and rebuild both targets. Keep the working Dockerfile available throughout. Do not suppress the nonzero test result or alter the expected baseline total. Explain why the tested artifact is the one the runtime receives.


#### Hint


<details>
<summary>Trace runtime content back to the actual oracle boundary</summary>

Keep the original workspace intact; make the controlled defect in a second copied build context.

Trace the exact file source of the runtime COPY back to the tested stage. If the test runs only as an optional container command, describe how acceptance enforces it rather than pretending the build itself is gated. Avoid appending an unconditional success echo after a failed assertion. Use the supplied test's expected result to diagnose the copied artifact cause.

</details>

#### Check


The valid test target must execute the real supplied summary test, and the finished runtime must use the corresponding tested app/input. The controlled incorrect artifact must be rejected for the predicted oracle or path reason; restore it and retain a successful test/runtime sequence. Record stage graph, command exit categories and actual identities.

Explain the difference between a stage named test and an enforced test boundary. A compiler/source inspection cannot establish the rejection transition. Keep source fixtures unchanged outside the disposable copy, and do not loosen the expected total merely to accept a broken artifact. Any unavailable engine execution remains pending rather than a source-only pass.

```bash
docker run --rm "$DC_DOCKER_TEST_TAG"
docker run --rm "$DC_DOCKER_RUNTIME_TAG"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p2-02-reasoning)


---


<a id="docker-p2-03"></a>

### docker-p2-03: Run with a bounded runtime user


<a id="docker-p2-03-concept"></a>

#### Concept


A runtime user changes the process's permission boundary, not the meaning of the app. The image should provide readable app/input files and an appropriate working directory for the declared non-root identity. A USER line can name an identity that lacks the necessary file access, so inspect actual UID and execute the app rather than trusting the Dockerfile keyword.

The expected training runtime UID is 10001. Its app only needs read access to the packaged fixture; adding broad writable host mounts or privileged flags would change the exercise boundary. An image can build under root while its final process runs non-root, because build and runtime identities are separate. That distinction should be visible in the explanation and actual command output.


#### Challenge


Create runtime UID 10001, give it the required read access to the packaged script/input, and set `USER 10001`. Use explicit ownership when copying from the test stage. Build runtime, inspect `id -u` inside it and run the default summary.

Retain both observations from the same image ID. If execution fails, distinguish a missing path from a file-permission error and repair only that cause. Confirm the process can read the app and fixture without privileged flags or a writable host mount. Explain which build steps used another identity and why runtime does not need root.


#### Hint


<details>
<summary>Prove actual runtime identity together with useful app access</summary>

COPY `--chown` can set ownership while copying from a named stage.

Inspect identity and file permissions as separate observations. The build's default user does not prove the final process's user. Read-only app access is sufficient for this fixture. If a file exists but cannot be read, diagnose its path and mode before changing the whole container security boundary.

</details>

#### Check


The finished runtime must report UID 10001 and still emit six holdings with total market value 12,011,626.50. Retain the identity probe and application run from the same image ID. Explain which build steps ran under another identity and how packaged file access supports the final process.

A USER declaration without successful execution is insufficient, and a successful app run forced back to root fails the stated runtime contract. Do not add broad write permissions or host mounts to conceal a packaging defect. The source may be reviewed locally, but actual UID and access observations require a real container engine.

```bash
docker run --rm "$DC_DOCKER_RUNTIME_TAG" id -u
docker run --rm "$DC_DOCKER_RUNTIME_TAG"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p2-03-reasoning)


---


<a id="docker-p2-04"></a>

### docker-p2-04: Keep runtime contents focused


<a id="docker-p2-04-concept"></a>

#### Concept


A focused runtime image contains what the executable needs, not every file available during build. The independent test is useful for acceptance but not required by the summary process. Copying the whole test stage can retain unnecessary scripts or temporary files. Narrow COPY decisions make the runtime boundary easier to inspect and reduce accidental content exposure.

Smaller size alone is not correctness: deleting the input CSV can shrink the image while breaking the app. The appropriate evidence combines required content presence, test-script absence and expected runtime behavior. Build/cache files and runtime files serve different roles. The exercise does not claim a production security audit from this small content check, but it teaches deliberate artifact selection.


#### Challenge


Copy only `summarize.py` and `holdings.csv` into runtime. Inspect `/app` in both targets and confirm `test_summary.py` is absent from the final runtime image. Compare their configured users, commands and sizes.

Run the summary after any COPY-path change and tie the filesystem inspection to that same image ID. Explain why each retained file is needed and why image size is only supporting information. A smaller image that lacks its CSV has not met the app contract. Inspect the final stage rather than assuming a narrow COPY statement produced the image your tag currently names.


#### Hint


<details>
<summary>Inspect the final filesystem and keep required behavior intact</summary>

Override the runtime command with ls or python -c when inspecting.

Inspect the final stage rather than a test-stage shell. Copying an entire directory may carry the test script even when no command executes it. Pair absence checks with app output so a missing required file cannot pass as a lean runtime. Use explicit source/destination paths rather than an unexplained broad directory copy.

</details>

#### Check


The runtime filesystem must exclude the supplied test script while retaining the app and holdings input at the expected paths. Its non-root process must still print the independent six-holding summary. Retain filesystem inspection and output tied to the actual runtime image ID.

Explain why an image-size comparison alone cannot establish focused contents or useful behavior. A source COPY statement is insufficient if actual execution uses another image/tag. Keep build/test stage evidence separate from runtime inspection. If an engine is unavailable, record the intended file inventory and leave its actual absence/presence assertions pending.

```bash
docker run --rm "$DC_DOCKER_RUNTIME_TAG" python -c "from pathlib import Path; assert not Path('/app/test_summary.py').exists()"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p2-04-reasoning)


---


<a id="docker-p2-05"></a>

### docker-p2-05: Repair a path assumption and explain the result


<a id="docker-p2-05-concept"></a>

#### Concept


Runtime path failures often come from an inconsistent relationship among build context, COPY destination and working directory. The summary opens its CSV by relative name. Moving its execution directory or copying that input elsewhere can cause a missing-file error even though the image built successfully. The diagnosis should identify that relationship rather than modify business data or install unrelated dependencies.

A controlled defective Dockerfile creates a useful before/after experiment after a known good baseline exists. The build can remain valid while the process fails, demonstrating the distinction between build-time and runtime checks. Repairing the minimal path assumption and rerunning the same fixture establishes recovery. Keep the defect out of the final image and retain evidence before cleaning owned tags.


#### Challenge


Save the working multistage Dockerfile. In a disposable copy, change runtime's WORKDIR to `/wrong` and predict how the default command will fail. Build and run the defective target, then inspect its configured directory and packaged paths.

Repair the path and repeat both target checks. Retain the failure, minimal Dockerfile diff and repaired summary from identifiable images. Confirm the fix preserves test gating, UID 10001 and the absence of `test_summary.py` from runtime. Write a short handoff explaining why the image built successfully but failed when its default process ran. Keep optional cache analysis separate.


#### Hint


<details>
<summary>Repair the path contract instead of bypassing the application</summary>

Inspect the image configured working directory and run a listing before editing Python code.

Follow the CSV path from the app source to final COPY destination and process working directory. A missing-file error differs from a read-permission failure. Change one assumption at a time and keep the known-good version available. Do not add a broad host mount or hard-code the expected output to make the defective container appear recovered.

</details>

#### Check


The controlled runtime failure must match the predicted path/entrypoint cause, and the repaired image must again emit the six-holding total with UID 10001 and no packaged test script. Retain failing and repaired command/category, bounded Dockerfile diff and actual image IDs. Explain why build success did not catch this runtime assumption.

Recheck both named targets after repair so a path fix cannot bypass the test boundary. Clean only owned tags/executions after preserving evidence. A missing engine or base-image download is not the intended defect, and local Python success does not prove repaired image behavior. Leave those actual runtime observations pending if they cannot run here.

```bash
docker build --target runtime -t "$DC_DOCKER_RUNTIME_TAG" .
docker run --rm "$DC_DOCKER_RUNTIME_TAG"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p2-05-reasoning)


## Phase completion


Finish a reviewable multistage Dockerfile with separately buildable test and runtime targets. The test target must run the supplied independent summary test, while the runtime target must emit six holdings and total market value 12,011,626.50. Inspect actual runtime user and filesystem to prove the declared non-root identity and absence of the test script. Retain a controlled working-directory/copy-path defect and its repaired output rather than relying on Dockerfile keyword inspection.

Explain the selected target dependency graph, why a tested artifact reaches runtime, and which files belong to build/test versus execution. Use owned tags/names and clean only this attempt's resources after retaining image identities and logs. A local Python test establishes fixture arithmetic but does not prove image stage, user or filesystem behavior. Mark engine/image-build evidence pending when unavailable. Optional cache/size analysis can follow the fixed core with its own estimate, but it cannot replace the test, runtime, identity and repair outcomes.

---


## Optional stretch


The core completion standard is independent of optional work. Choose a separately timed route from [the stretch guide](stretch/README.md).

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Separate named build targets

<a id="docker-p2-01-reasoning"></a>

<details>
<summary>Reasoning for docker-p2-01: Separate outputs require deliberate target builds</summary>

Named stages describe dependency and purpose. Selecting runtime does not automatically tag every stage, so retain explicit test/runtime builds and actual image IDs. Their commands produce different expected outputs. Source stage declarations are useful review evidence but cannot substitute for real target execution or an actual oracle run.

[Return to docker-p2-01](#docker-p2-01)

</details>

### Reasoning: Gate the runtime on a tested artifact

<a id="docker-p2-02-reasoning"></a>

<details>
<summary>Reasoning for docker-p2-02: The test must validate the artifact runtime actually uses</summary>

The meaningful gate is the supplied oracle executed on the same app/input passed to runtime. A disconnected stage or unconditional success message does not establish it. The bounded defective artifact should fail for its intended reason, and restoration should recover the expected summary. Build-time gating and an explicit separate acceptance test need truthful distinction.

[Return to docker-p2-02](#docker-p2-02)

</details>

### Reasoning: Run with a bounded runtime user

<a id="docker-p2-03-reasoning"></a>

<details>
<summary>Reasoning for docker-p2-03: Build identity and runtime identity are different boundaries</summary>

The finished process must actually run as UID 10001 while reading the correctly packaged app/input. Build steps may use another identity. Source USER text states intent, while identity plus successful output proves the runtime boundary. Minimal file access is the proper repair; root or privileged execution would bypass the assessed contract.

[Return to docker-p2-03](#docker-p2-03)

</details>

### Reasoning: Keep runtime contents focused

<a id="docker-p2-04-reasoning"></a>

<details>
<summary>Reasoning for docker-p2-04: Focused content requires both absence and functioning presence</summary>

The runtime does not need the test script, but it does need the summary and input. Actual final-stage inspection plus expected output establishes both sides of that boundary. Size or source COPY text alone can conceal missing required content or accidental test material. Tie the observations to the same runtime identity.

[Return to docker-p2-04](#docker-p2-04)

</details>

### Reasoning: Repair a path assumption and explain the result

<a id="docker-p2-05-reasoning"></a>

<details>
<summary>Reasoning for docker-p2-05: A minimal causal repair preserves the other runtime promises</summary>

The app's relative input lookup links COPY path and working directory. A valid build can still fail that runtime contract. The controlled defect and minimal repair must preserve test gating, non-root identity and focused contents. Actual failure/recovered output and image IDs establish the transition; host mounting or echoed output would bypass it.

[Return to docker-p2-05](#docker-p2-05)

</details>


---

# docker independent starter

Read the [owning phase](../README.md) before editing. Prepare from the training project root with `mise run challenge:v2:prepare docker phase-two-proficient`; edit the copied attempt.

## Authored-file list

| Task | Learner-authored paths |
|---|---|
| docker-p2-01, docker-p2-02, docker-p2-03, docker-p2-04, docker-p2-05 | `Dockerfile`, `evidence.md` |

## Declared baseline

The app and independent Python test are supplied. The Dockerfile builds a placeholder image; replace its unfinished configuration to package the app. A successful placeholder build is not completion.

Use a fresh workspace for another attempt; preparation and reset preserve existing work.


---

# docker optional stretch


Choose an optional exercise after the advanced core. Allow 20–40 minutes for each and use a fresh copy of your completed baseline. Keep the assessed attempt unchanged.


## Optional exercises


<a id="docker-stretch-01"></a>

### docker-stretch-01: Explain cache reuse and a controlled input rebuild


<a id="docker-stretch-01-concept"></a>

#### Concept

Build cache can reuse a stage whose relevant inputs and instructions have not changed. The observed rebuild log, selected target and actual resulting image determine what was reused; merely running the same command twice does not prove every stage executed again. A mutable tag can hide that distinction because it can point to a new image after a rebuild.

The supplied six-holding input provides a bounded invalidation experiment. Changing one copied CSV value can affect the application layer and expected summary without requiring an unrelated service stack. Keep that variation separate from the fixed core baseline and calculate its expected total independently. Image size alone cannot establish correctness or cache behavior. The useful explanation identifies the input boundary, affected build stage and actual output.

#### Challenge

Preserve a working completed Dockerfile and perform two builds with unchanged input, retaining plain build logs and image identifiers. In a separate copied variation, change one holding value by a known amount, predict the new total through an independent CSV calculation, and rebuild the selected runtime target. Inspect which stages reused cache and which consumed the changed input. The fixed baseline assertion should now fail. In this optional copy only, replace its expected total with your independently calculated variation total, label that test as variation-specific, and rebuild. Run the resulting image and compare its actual summary with the predicted variation. Restore the copied baseline afterward without loosening the fixed core oracle.

Record the copied input delta before rebuilding and name the specific layer whose changed content should invalidate reuse.

#### Hint

<details>
<summary>Trace the changed input to its COPY boundary</summary>

Compare the stage logs rather than only elapsed time. A fast network or already pulled base can make a build faster without the specific layer reuse you intend to explain. Trace the changed CSV to its COPY boundary. Preserve the original input hash and total so the variation cannot be mistaken for the assessed baseline. A changed tag name alone does not invalidate the relevant content.

</details>

#### Check

Retain unchanged and changed build logs, actual image IDs, input hashes and runtime summaries. The changed result must differ by the independently predicted amount while still containing six holdings; restoration must recover the baseline 12,011,626.50 result. Explain which input/stage boundary produced the observed reuse or invalidation.

Retain the original core test's rejection of the changed fixture and the separate variation-specific test result. Keep the assessed baseline test unchanged. Source inspection or duration alone cannot prove cache reuse. Use the actual engine when available and mark those observations pending otherwise. Clean only the optional experiment tags after preserving evidence, leaving the completed core image and another learner's resources intact.

<!-- variation: none; this entire exercise is optional and separately timed. -->

[Optional contents](#optional-exercises) · [Reasoning key](#docker-stretch-01-reasoning)

---


<a id="docker-stretch-02"></a>

### docker-stretch-02: Run the prepared app through bounded Compose configuration


<a id="docker-stretch-02-concept"></a>

#### Concept

Compose describes a local multi-container application configuration, but a single supplied app can also demonstrate its project/name and command boundaries. The optional experiment should not introduce a database, broker and web service merely to look more advanced. The same packaged summary and its read-only input can establish a useful configuration comparison.

Project identity scopes names and cleanup. A Compose file in source does not prove the selected service image, runtime user or working directory actually ran. The core Dockerfile remains the artifact under test, while Compose selects and starts its local execution. A service that finishes a batch summary can exit successfully; forcing it to stay alive would change the behavior. Retain the expected app result and owned project boundary.

#### Challenge

Author a small Compose configuration for the completed summary image, with an explicit owned project name and the required runtime path/input contract. Inspect the resolved configuration, execute only that supplied batch service and retain its logs/exit result. Compare it with the direct docker run outcome. If you explore a read-only mount, keep it limited to the copied app directory and explain how it changes packaging assumptions. Remove only this optional Compose project after collecting evidence.

Keep the resolved configuration and its project name beside the actual service result so the observed runtime can be reproduced.

#### Hint

<details>
<summary>Inspect the resolved service before starting it</summary>

Inspect the installed Compose help and resolved service definition before startup. Compare selected image, working directory, user and mount with the direct runtime contract. A completed batch service need not remain running. Keep project cleanup bounded; a global prune is unrelated to this optional configuration exercise. Do not require an extension-specific renderer to understand the Compose YAML.

</details>

#### Check

The resolved configuration and actual service execution must preserve the expected six-holding total, intended user and bounded filesystem access. Retain project/service identity, selected image ID, exit category and logs. Explain what Compose changed about orchestration/configuration and what remained the same application behavior.

A parsed YAML file alone is supporting evidence. Actual startup and cleanup need the prepared engine, and unavailable runtime stays pending. Do not introduce external infrastructure or another mandatory course dependency. After owned project removal, the completed core Dockerfile and evidence remain intact. The optional route has its own estimate and cannot replace the core multistage/test/user/path checks.

<!-- variation: none; this entire exercise is optional and separately timed. -->

[Optional contents](#optional-exercises) · [Reasoning key](#docker-stretch-02-reasoning)

---


## Reasoning keys


<a id="docker-stretch-01-reasoning"></a>

<details>
<summary>Reasoning for docker-stretch-01: Cache observations need logs and checked output</summary>

The build log identifies cached stages; runtime output checks the result of the changed input. A data-only COPY change should invalidate stages that depend on it while earlier unchanged work can be reused. The fixed core oracle may reject the changed fixture intentionally. Restore the baseline and its expected total before final cleanup.

[Return to docker-stretch-01](#docker-stretch-01)

</details>

<a id="docker-stretch-02-reasoning"></a>

<details>
<summary>Reasoning for docker-stretch-02: Configuration selects an execution of the same app</summary>

Compose selects the image and execution configuration for the same batch app. Its project name scopes resources, while the resolved service shows user, command, path and mounts. A successful summary can exit normally. Compare actual logs and image identity with the direct run to establish that the configuration preserved the app contract.

[Return to docker-stretch-02](#docker-stretch-02)

</details>


---

# dbt — Portfolio Analytics

Build a traceable transformation from supplied custodian feeds to a fund/date report on Databricks. The foundation phase teaches external sources, typed staging, business grain, model references and independent output checks. The advanced phase supplies that baseline and develops dated enrichment diagnosis, reconciliation, controlled corrections, history and a reviewable feature. The consumer question is what each fund's supplied holdings contribute to GBP exposure on each fixture date, with a carefully labelled teaching NAV measure.

## Before you start

Open the supplied training project in its dev container and complete the delivered Databricks sign-in before starting timed practice. Confirm the installed dbt executable includes the Databricks adapter, identify the approved catalog/schema and reconcile its aliases. Choose a unique relation prefix for each attempt. Your terminal runs dbt while the SQL warehouse executes the models; neither a local target name nor a successful parse establishes a warehouse result.

Prepare through the version-explicit mise interface from the training project root, then run direct dbt commands inside the copied attempt. Keep your original work and use a new workspace for another try. Advanced practice has an independently prepared starter; it does not assume you completed or viewed someone else's foundation answer. Both phases use the same eight supplied input CSVs and disclosed supporting models, with authoring responsibilities listed in the phase guide.

## Suggested timeline and tasks

The phase estimates include reading, authoring, checking and explanation. Allow additional time for sign-in, tool setup, source loading and optional extensions. Follow your instructor's selected route for Wednesday's practice block.

| Phase | Task | Minutes |
| --- | --- | --- |
| Foundation | [dbt-p1-01: Inspect the project and source grain](phase-one-certified/README.md#dbt-p1-01) | 15–22 |
| Foundation | [dbt-p1-02: Declare and use sources](phase-one-certified/README.md#dbt-p1-02) | 15–22 |
| Foundation | [dbt-p1-03: Normalize type, unit and key contracts](phase-one-certified/README.md#dbt-p1-03) | 15–22 |
| Foundation | [dbt-p1-04: Build a useful mart through ref](phase-one-certified/README.md#dbt-p1-04) | 15–22 |
| Foundation | [dbt-p1-05: Add minimum key and relationship proof](phase-one-certified/README.md#dbt-p1-05) | 15–22 |
| Advanced | [dbt-p2-01: Diagnose a join fan-out before repair](phase-two-proficient/README.md#dbt-p2-01) | 18–24 |
| Advanced | [dbt-p2-02: Repair enrichment at the intended grain](phase-two-proficient/README.md#dbt-p2-02) | 18–24 |
| Advanced | [dbt-p2-03: Write reconciliation that detects the negative case](phase-two-proficient/README.md#dbt-p2-03) | 18–24 |
| Advanced | [dbt-p2-04: Prove incremental update and replay behavior](phase-two-proficient/README.md#dbt-p2-04) | 18–24 |
| Advanced | [dbt-p2-05: Explain dependency impact and hand over](phase-two-proficient/README.md#dbt-p2-05) | 18–24 |

## Choose your phase

- [Foundation phase](phase-one-certified/README.md): complete the assigned source/staging/report slice and prove its minimum business contract.
- [Advanced phase](phase-two-proficient/README.md): begin from its supplied baseline and demonstrate diagnosis, replay and a useful handoff.

Finish the core tasks before choosing optional stretch. These phases use the supplied Portfolio Analytics data on Databricks.

## Teaching concepts

Trace source declarations to physical owned tables, distinguish source and model dependencies, preserve composite grain, choose deliberate materializations, and separate native valuation from dated GBP conversion. Structural tests and independent business calculations protect different failure modes. The advanced route extends those ideas into controlled Delta replay, snapshot validity, documentation and the Astro worker boundary. Reasoning keys stay at the end of their owning phase; full runnable instructor references are supplied separately.

## Question-led foundations and further study

Use questions 1–8 alongside the foundation tasks. Questions 9–13 introduce further study.

### Foundations

<a id="dbt-guide-q01"></a>

#### What problem does dbt solve, and where does it fit in a data pipeline?

Custodian feeds arrive as holdings and cash; prices, dated FX and fund metadata explain those positions. dbt orders SQL transformations and tests. The Databricks warehouse executes SQL and stores views/Delta tables. Running dbt in a local process does not create a local database. Our consumer output is a fund/date GBP exposure and a teaching NAV, with lineage back to the supplied raw tables.

<a id="dbt-guide-q02"></a>

#### What does a dbt project contain, and how do we connect it to our data?

The prepared Portfolio Analytics attempt contains models, eight seeds, tests, macros, profiles and a local target directory. Read the setup contract before connecting. Profile portfolio_analytics and target local point to the assigned Databricks warehouse. dev and airflow are also Databricks targets. Record the project/profile paths and installed versions; reject missing namespace or conflicting aliases rather than guessing a username.

<a id="dbt-guide-q03"></a>

#### How does a SQL query become a dbt model?

Author models/staging/stg_holdings.sql. Select fund_cd as fund_id, pos_dt as position_date, isin as instrument_id, qty as decimal quantity, mkt_val_lc as decimal native value and ccy_cd as local_ccy. Cast dates and retain extraction time. Its business key is fund/date/instrument. The baseline contains eight rows: one instrument for each of four funds on each of two dates. A model file becomes an owned view after execution; its filename is the ref name, while its physical alias includes your prefix.

<a id="dbt-guide-q04"></a>

#### How do we connect models using source() and ref()?

source('custodian','holdings_raw') reads the prefixed raw seed-backed Delta table. ref('stg_holdings') connects transformations and lets dbt establish order. Declare raw source database/schema from the target and identifier from the ownership prefix. A source declaration does not load data. Run the explicit eight-seed preparation, then inspect the compiled relation names and graph. Supplementary NAV/fund seeds alone leave six raw sources missing.

<a id="dbt-guide-q05"></a>

#### How should we split a large query into understandable, reusable models?

Keep cast/rename in five staging views; dated enrichment belongs in int_holdings_enriched. Join prices by instrument/date and FX by native currency, GBP and date. Fund metadata joins by fund key. Cash positions have fund/date/currency grain and remain separate until aggregated correctly. Validate right-side uniqueness before joining: an undated FX join fans eight holdings out across two dates. refdata_raw is available for a classification extension; it is not a substitute for fund_master_raw.

<a id="dbt-guide-q06"></a>

#### When should a model be a view or a table?

Views suit the small staging and intermediate transformations. A consumer table persists the report for repeated reads and a stable tested handoff. Inspect information_schema for the prefixed relation and its type; do not infer storage from a successful command. Tables on this adapter use Delta. The richer product has optional optimisation hooks, but the guide omits them to avoid adding managed-permission assumptions to the core exercise.

<a id="dbt-guide-q07"></a>

#### How do we know our models produce trustworthy data?

Test non-null keys, composite uniqueness, decimal types, dated join coverage and populations. Missing FX is an error, not an implicit rate of one. All supplied holdings happen to be GBP; fund PEF-EM-GROWTH has USD master currency, but this report explicitly values in GBP. Market value is supplied by the custodian and must not be replaced with quantity times price without an agreed contract. The reference NAV uses 100 million synthetic units and excludes cash. Compare each of eight fund/date rows independently with seed_custodian_nav.

<a id="dbt-guide-q08"></a>

#### How do we make a change confidently and explain the result?

Select the changed model and downstream dependencies, retain compiled SQL and run results, then query the actual warehouse. For a negative drill remove a dated GBP FX row in a disposable copy. matched_enrichment must fail; restore, reseed and rebuild before handoff. Documentation must state grain, units, source meaning and the NAV limitation. A green structural test can miss a correct-looking wrong business measure.

<a id="dbt-further-study"></a>

### Further study

Questions 9–13 are separately timed advanced study.

<a id="dbt-guide-q09"></a>

#### When does Jinja help, and when should we keep the logic in SQL?

A small native_value(value, rate) macro casts the GBP conversion to a declared decimal precision. Inspect its compiled multiplication and explain the arguments. Keep business joins in readable SQL. Reuse earns its place when the same expression has the same meaning in both the consumer model and the correction/replay model; a macro cannot settle currency or grain disagreements.

<a id="dbt-guide-q10"></a>

#### How can we process less data without producing incorrect results?

In the separately timed advanced phase, the required holdings_replay model uses Delta merge with fund/date/instrument as its composite key. Read the whole tiny fixture each time so older-date corrections are included. Copy one holding, add 1,000 GBP to its value, reseed, merge and replay. Query the original key after each run: corrected value and exactly one row. A maximum-date watermark would miss this controlled historical correction. This is a labelled variation, not history already present in the source.

<a id="dbt-guide-q11"></a>

#### How do we preserve history when source records change?

Snapshot a copied fund-master relation before and after one controlled name change using the check strategy and fund_cd key. Retain validity columns and verify the original closed row plus one current row. All snapshots remain in the assigned schema with owned aliases. Snapshots record observed states, not every event between observations. Restoring source CSVs does not delete history; a new attempt/prefix starts clean.

<a id="dbt-guide-q12"></a>

#### How does a dbt project move into reliable team delivery?

Review SQL, tests, contract and target routing together. Hand off the exact prepared project to Astro with a worker-visible path and inspected executable; resolve the token at task execution. Record versions at both boundaries. Production promotion remains a design discussion. A local compile or prior green run cannot prove a new scheduler/worker/output path.

<a id="dbt-guide-q13"></a>

#### Can we independently deliver a documented, tested model?

Build fund_nav_report at fund/date grain from the available enrichment. State GBP, the 100 million synthetic units and excluded cash. Include one independent business query, lineage, structural tests, reconciliation, failure/repair and a reviewable diff. Your evidence should let another person distinguish a missing model, stale data, join fan-out and a currency-definition mistake.


---

# dbt: Phase 1 — foundations

## Purpose and outcome

Build a small but complete Portfolio Analytics result on Databricks: supplied custodian inputs become typed holdings, dated enrichment and a fund/date consumer report. You write the holdings transformation and report. Other staging and enrichment models are supplied; inspect their dependencies to understand the complete pipeline.

## Dataset and pipeline

Eight supplied CSVs enter the project: six raw feeds plus fund and custodian-NAV reference fixtures. Holdings, positions and prices each contain eight rows; FX has six rates, fund master four funds and instrument reference four instruments. Holdings cover four funds on 20 and 21 May 2026. The modeled graph reads holdings, positions, prices, FX and funds. Instrument reference remains available for source inspection. Custodian raw cash is not included in the teaching NAV numerator. The report converts supplied native market value to GBP and divides the holdings-only amount by a synthetic one-hundred-million-unit denominator. It is not an official unit-price calculation.

## Prerequisites and workspace

Use the supplied training dev container, delivered OAuth setup and a dbt executable with the Databricks adapter. From the training project root prepare a fresh attempt with the version-explicit mise task. Record installed versions instead of assuming a pinned file proves the worker environment. Set the approved catalog/schema aliases consistently and choose an owned relation prefix before loading. Never create an extra schema as an experiment. Your terminal runs dbt; the warehouse executes its SQL. The local target name still selects Databricks, not DuckDB.

```bash
mise run setup:databricks
mise run challenge:v2:prepare dbt phase-one-certified
cd .local/challenges-v2/dbt/phase-one-certified
export DC_RELATION_PREFIX=dc_alex_dbt01
dbt --version
dbt debug --project-dir . --profiles-dir . --target local
```

Use a new workspace and prefix for a second simultaneous attempt. Work inside the copy, editing only the task's named files. Keep evidence beside the copied project. Do not place tokens in that note, commit local credentials or overwrite the canonical starter. The root mise verification command accepts the absolute or root-relative attempt path; direct dbt commands below run from this prepared directory.

## Starter behavior

The foundation starter deliberately contains unfinished holdings staging and report SQL. They are valid files for authoring, but the completion checker rejects their placeholder result. Source declarations, routing macros, remaining staging models and enrichment are supplied. Inspect that boundary before running a broad build: downstream failures from an unfinished model are expected until its task is complete. Seed loading can succeed first; it is not an assessment pass. Freshness uses extraction timestamps separately from the historical business dates. If current freshness fails, record that cause and use the documented timestamp-only preparation rather than changing the May holdings dates.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 75–110 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [dbt-p1-01: Inspect the project and source grain](#dbt-p1-01) | 15–22 | Eight holdings, four funds, two business dates; safe identity and seed inventory |
| [dbt-p1-02: Declare and use sources](#dbt-p1-02) | 15–22 | Compiled source relations and manifest dependencies agree with all raw seeds |
| [dbt-p1-03: Normalize type, unit and key contracts](#dbt-p1-03) | 15–22 | Eight unique holding keys; native decimal values preserved |
| [dbt-p1-04: Build a useful mart through ref](#dbt-p1-04) | 15–22 | Eight fund/date rows; independently derived GBP exposure and teaching NAV |
| [dbt-p1-05: Add minimum key and relationship proof](#dbt-p1-05) | 15–22 | Declared tests pass; unknown-fund membership fails, then passes after input restoration |

## Core challenges


<a id="dbt-p1-01"></a>

### dbt-p1-01: Inspect the project and source grain


<a id="dbt-p1-01-concept"></a>

#### Concept


A dbt project describes transformations and dependencies; it does not become a separate database simply because it lives in a container. The adapter compiles and submits SQL to Databricks, where the approved catalog, schema and warehouse determine the relations you read and write. Seeds load copied training inputs. Sources describe that input boundary, while models describe derived relations. Keeping those roles separate helps diagnose a missing table before changing a transformation.

In this fixture a holding is identified by fund, business date and instrument. The same fund appears on two dates, so fund alone cannot identify a row. A report with four rows after both dates are loaded has probably collapsed the date dimension. Inspecting the eight raw rows makes that mistake visible before SQL is written. Distinguish the position date from the extraction timestamp: one describes the observation being valued, the other describes ingestion freshness. An old business date can be the correct teaching input even when its original extraction timestamp is stale. Likewise, a successful connection says nothing about whether the six raw feeds have actually been loaded.

#### Challenge


Create an evidence note in the copied project and list each seed's name, row count, key fields and money units. Inspect the project and profile configuration, identifying the adapter, target, approved catalog/schema and relation prefix without copying credential values. Run the version and connection probes, then load all eight seeds. Find the raw holdings, funds, dated prices and FX sources in the declarations and note which physical prefixed tables they resolve to.

Use a small independent CSV inspection to count distinct funds and dates. Choose one holding and trace its native currency and value to the source field that supplies them. Explain why the product's two supplementary CSVs cannot provision the six raw feeds. Keep a record of any unavailable warehouse prerequisite; continue the CSV inspection locally while leaving the connection and actual loaded-relation checks pending. Do not substitute the optional five-row fixture or call its result this phase's completion.

#### Hint


<details>
<summary>Separate input inspection from warehouse readiness</summary>

Start with the headers in the copied seeds and the database/schema expressions in the source YAML. Write the composite holding key as three named fields before counting rows. If connection debug fails, inspect the adapter identity and alias consistency before trying a model build. A namespace mismatch can produce missing relations even when authentication succeeds; a username fallback would conceal that mismatch rather than fix it.

</details>

#### Check


Run the seed command from your attempt and inspect the resulting prefixed input relations. The independent CSV inventory should show eight holdings, four distinct fund identifiers and two business dates. Verify the corresponding warehouse counts when connected; CSV counts alone establish supporting input evidence. The six raw counts are eight holdings, eight positions, eight prices, six FX rates, four fund-master rows and four reference instruments. Supplementary funds and NAV inputs need their own listed counts.

Retain the installed adapter/version, selected target, redacted namespace identity, seed run-results identity and the independently calculated populations. Explain which command loaded inputs and which file only declared their names. If debug reports an authentication or permission error, record that category and leave this check pending rather than treating a local seed inspection as a warehouse pass. Your explanation should predict why removing the position date from a key would merge two otherwise valid observations.

```bash
dbt seed --project-dir . --profiles-dir . --target local --full-refresh
python runtime/lab.py reference .
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p1-01-reasoning)


---


<a id="dbt-p1-02"></a>

### dbt-p1-02: Declare and use sources


<a id="dbt-p1-02-concept"></a>

#### Concept


The source function gives a model a logical dependency on data loaded outside that model. Its first name identifies the source group and its second identifies the table inside that group. Those logical names need not equal the physical warehouse relation: the source identifier can add the owned training prefix while the SQL remains stable. A reference to another model instead declares a derived dependency that dbt can order and document.

Consider the holdings model reading the custodian holdings source. Databricks ultimately executes a fully qualified relation in your approved namespace; the source declaration explains why that relation is an input rather than a generated mart. A raw seed can be present but wrongly mapped to another learner's table. Conversely, a perfectly written declaration can resolve to a table that was never seeded. Compilation and an actual query expose different halves of this boundary. The instrument-reference input is useful to inspect even though the prepared consumer graph does not depend on it. Do not invent a lineage edge merely to make every loaded feed appear in the final report.

#### Challenge


Inspect all six raw table declarations in the copied source YAML and verify their identifiers use your relation prefix. Retain the prepared logical source groups for custodian, Bloomberg, FX and product reference. In the holdings staging file replace the unfinished scaffold with a source-based input CTE, then add the transformation required in the next task. Read the supplied fund, FX, price and position staging files to identify their source calls and the prepared enrichment model to identify its model references.

Compile a selected holdings model and trace one rendered relation back to its source declaration, seed file and approved namespace. Record that chain in the evidence note. Keep the supporting model files supplied unless an actual declared task requires a change. If a raw input is missing, fix loading or source mapping before adding a hard-coded qualified name to model SQL. That shortcut would bypass the lineage and ownership contract being learned.

#### Hint


<details>
<summary>Trace one logical name to its prefixed input table</summary>

Compare the logical table name in the source call with the identifier expression in YAML; they answer different questions. The source manifest node records database, schema and identifier after configuration is resolved. If compilation fails because the holdings scaffold is incomplete, keep the first error and use the supplied source declarations to complete the input CTE. Avoid changing all six source names at once while diagnosing one bad relation.

</details>

#### Check


Compile the holdings selection and inspect its SQL and manifest dependency entry. The rendered raw relation must belong to your approved catalog/schema and carry your owned prefix. The dependency must point to the custodian holdings source, while the later report depends on models through references. Confirm the source inventory contains the six declared raw inputs; instrument reference may have no consumer-model edge without being an error.

When connected, build the holdings model after its type transformation is complete and inspect the warehouse relation. Record the difference between compilation success and query success. To diagnose a deliberate source-mapping mistake in a disposable copy, point one identifier at a nonexistent owned name: the affected model should fail with a missing-relation category. Restore the declaration and rebuild before retaining completion evidence. Explain why loading the seed alone would not repair a wrong identifier and why bypassing the logical source with a literal table name would weaken lineage.

```bash
dbt compile --select stg_holdings --project-dir . --profiles-dir . --target local
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p1-02-reasoning)


---


<a id="dbt-p1-03"></a>

### dbt-p1-03: Normalize type, unit and key contracts


<a id="dbt-p1-03-concept"></a>

#### Concept


Staging gives raw data stable names and types while preserving its declared population. Renaming the custodian fund code and position date makes their purpose clearer, but it does not justify dropping a date, replacing a missing key or changing money units. Money stored as native market value must remain native market value until the dated FX join explicitly converts it. A fund's master base currency is a separate attribute, not permission to relabel a holding value.

For example, a holding observed on 20 May and the same instrument observed on 21 May represent different positions. The composite key preserves both; casting the date into a SQL date type makes later dated joins less ambiguous. Decimal conversion preserves exact cents within the stated precision, whereas an uncontrolled floating-point aggregation can introduce comparison noise. Quantity has its own precision and meaning. The supplied valuation is not necessarily quantity multiplied by the supplementary price, so reconstructing it that way would silently change the teaching contract. Filtering a zero or negative amount also changes population semantics unless the contract explicitly requires that rule.

#### Challenge

The exact staging columns are `fund_id` (string, trimmed uppercase `fund_cd`), `position_date` (date from `pos_dt`), `instrument_id` (string retaining `isin`), `quantity` (decimal(18,4) from `qty`), `mv_local_ccy` (decimal(18,2) from `mkt_val_lc`), `local_ccy` (uppercase string from `ccy_cd`) and `_src_loaded_at` (retained `_extracted_at`). Do not manufacture a missing instrument key; this holdings contract requires it, with cash supplied separately.


Complete the holdings staging SQL in the copied model file. Read through the custodian source, trim and normalize the fund code, cast the position date, retain the instrument identifier, cast quantity and native market value to their stated decimal types, normalize currency, and carry the source extraction timestamp for diagnostics. Keep cleaning separate from enrichment joins. Use the prepared column contract to name the resulting fund, date, instrument, quantity, native value and local-currency fields.

Build the selected staging model as a view, then inspect all eight output rows alongside the original CSV. Check the entire composite key and compare the native value of a chosen holding exactly. Read the supplied grain test and extend it if your transformation introduces an additional normalization assumption. Document any filtering and prove it does not conceal an invalid key in the supplied fixture. Do not erase null-key evidence by substituting a plausible fund identifier or invent a reporting currency during staging.

#### Hint


<details>
<summary>Check the three-field grain before changing population</summary>

Write the column mapping before the SQL so casts and renames can be reviewed independently. Compare the source and staging counts before joining any dimensions. For a duplicate-key failure, group on all three business fields; grouping only by fund will report valid repetitions as defects. Inspect Databricks full type metadata when proving decimal precision, because a broad type label may omit precision and scale.

</details>

#### Check


The staging view must return eight rows with eight unique fund/date/instrument keys and native market values matching the copied holdings input. Inspect the SQL type metadata and verify the intended decimal precision and scale, the date type and normalized currency. A count alone is insufficient: an invented key could preserve eight rows while breaking later joins. Compare a complete sorted key/value projection against the input mapping.

Run the grain test and inspect the selected build artifacts. In a separate copied-input variant set one native market value to zero, rebuild the selected staging slice and prove its business key remains among all eight rows with an exact zero value. Restore and reseed before baseline NAV comparison; changing an amount legitimately changes its expected value. In a disposable input copy, duplicate one holding key and show that the grain assertion detects it; restore the supplied CSV and reseed before the final build. Keep that negative result separate from the untouched starter's unfinished-model rejection. Explain why the same fund appearing on two dates should pass and why recomputing market value from quantity and price is outside this staging task. Retain the failed test identity, repaired selected run and one exact native-value comparison.

```bash
dbt build --select stg_holdings --project-dir . --profiles-dir . --target local
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p1-03-reasoning)


---


<a id="dbt-p1-04"></a>

### dbt-p1-04: Build a useful mart through ref


<a id="dbt-p1-04-concept"></a>

#### Concept


A mart combines modeled inputs into an output a consumer can interpret. Its grain must be declared before aggregation, because an apparently sensible total can conceal loss of dates or duplication from joins. Here the consumer result is one row per fund and position date, containing holding count, GBP exposure and teaching NAV per synthetic unit. The prepared enrichment provides native market value and the matching dated FX rate; the report sums converted holding values at that grain.

For the global-core fund on 20 May, the independent fixture calculation yields GBP exposure of 1,500,440,000 and teaching NAV of 15.004400 after division by one hundred million. The next date is a distinct report row, not an update to that same key. GBP reporting is fixed even when fund master says a fund has another base currency. Cash positions are deliberately excluded from this teaching numerator. Calling the result official custodian NAV would overstate its meaning. A three-column output with a correct grand total can still be wrong for each fund/date, so compare complete keys and values rather than relying on an aggregate smoke check.

#### Challenge

Return `fund_id` and `position_date` as the report key, `holdings` as the count of enriched holding rows, `exposure_gbp` as decimal(28,2), and `nav_per_unit` as decimal(28,6). The supplied enrichment value field is `mv_base_ccy`; sum it at fund/date grain and divide that sum by 100000000 for the teaching NAV. The name of each output is part of the consumer/checker contract.


Author the fund NAV report model through a reference to the supplied enrichment, grouping on fund and position date. Return the declared identifiers, holding count, GBP exposure and teaching NAV with the stated decimal types. Keep the synthetic denominator explicit and explain the cash exclusion in the model documentation. Configure the consumer report as a table while leaving the staging and enrichment layers as views.

Before running SQL, calculate one selected fund/date result from the copied holdings and FX files. Then build the report with its upstream dependencies and compare every output key/value with the independent reference command. Inspect the manifest to show why the report waits for enrichment and holdings. If one row has the right exposure but the wrong date, repair the grain instead of relaxing the reconciliation. Preserve the supplementary custodian NAV fixture as a comparison input and state its intended teaching role.

#### Hint


<details>
<summary>Declare the reporting grain and units before summing</summary>

Begin by selecting the enrichment columns and checking its row count before aggregation. The supplied native value is already a valuation; use the dated conversion rate rather than reconstructing price times quantity. Keep the denominator outside the sum so its units remain obvious. A missing FX rate should remain visible to a coverage test; replacing it with one would manufacture a convincing but unsupported answer.

</details>

#### Check


Build the report selection with its upstream graph, then run the independent reference over the copied CSVs. Expect eight report keys: four funds on each of two dates. Each holding count is one in this fixture. Check all exposures and NAV values, including global core on 20 May at 1,500,440,000 GBP and 15.004400 teaching NAV. The independent output must use your actual copied inputs, not a pasted instructor SQL result.

Inspect warehouse relation metadata to show that the report is a table and holdings staging is a view. Record the selected build/run-results identity and explain the difference between materialization and business grain. A view/table configuration change alone should not change the expected values. If either date disappears or a fund gains two identical report keys, the output fails even when an overall sum is plausible. Explain why excluding cash is a declared limitation and why a different fund-master base currency does not change this report's GBP label.

```bash
dbt build --select +fund_nav_report --project-dir . --profiles-dir . --target local
python runtime/lab.py reference .
python runtime/lab.py check .
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p1-04-reasoning)


---


<a id="dbt-p1-05"></a>

### dbt-p1-05: Add minimum key and relationship proof


<a id="dbt-p1-05-concept"></a>

#### Concept


A test is useful when it protects a stated failure mode and its result can be interpreted. A uniqueness test checks row identity, a not-null test checks required presence, and a relationship test checks membership in another relation. None independently proves all joins preserve the intended population. A relationship assertion can ignore nulls, and a reconciliation can compare two outputs that already lost the same fund. Combining structural checks with independent business values closes different gaps.

The holding grain includes a date, while fund-master membership is checked by fund identifier. A date-free fund uniqueness test would therefore reject valid holdings. Conversely, a report sum could stay numerically unchanged if an unknown fund's zero-valued holding were silently filtered out; the population and relationship assertions should still catch that loss. For missing dated FX, the correct failure is incomplete conversion coverage, not a guessed one-to-one rate. The teaching drill deliberately changes a copied input so you can observe the failed assertion, repair its cause and prove the restored output. A red test is not automatically a successful drill unless it failed for the intended reason.

#### Challenge


Review the supplied schema and singular tests, then add or repair assertions that match the authored models: holding composite grain, required fund/date/instrument fields, fund membership, complete dated enrichment and independent NAV reconciliation. Explain which checks protect population, which protect type/units and which protect the consumer calculation. Run a clean seed and full selected build after both authored SQL files are complete.

Create the required relationship negative case in a disposable copy by changing a holdings fund to an unknown identifier; retain the specific membership failure. Also use the runtime helper to inspect the separately declared missing-FX coverage failure when that drill is selected. Capture the specific failed node and its diagnostic output. Restore the input, reseed and rebuild the affected dependencies, then rerun the independent comparison. Keep the original CSVs and canonical starter unchanged. A later correction/replay exercise has a different expected output contract, so do not reuse its intentional baseline reconciliation failure as this phase's final evidence.

#### Hint


<details>
<summary>Predict the failed assertion before injecting a defect</summary>

Choose one defect at a time and name the test you expect to fail before running it. Inspect failed rows or compiled SQL to distinguish a genuine coverage failure from an unrelated unfinished model. A relationship check on fund identifiers needs a separately unique fund dimension; the holdings themselves are not unique by fund. Keep the fixture restore and selected reseed in your note so the repaired run can be reproduced.

</details>

#### Check


The final baseline build must pass the structural and business assertions and reproduce the independent eight-key report. The negative run must fail on the promised relationship, grain or missing-enrichment assertion, and the repaired run must pass after restoring and reseeding the copied input. Record all three states with their relevant artifact identities; replacing the failure log with the final green log loses the learning evidence.

Use the runtime helper only on your owned attempt, then select the affected seeds and upstream graph deliberately. Inspect the failing test result rather than inferring its cause from a nonzero command exit. Explain why the report's own total cannot be its only oracle and why not-null and relationships need complementary tests. The root phase verifier may validate finished warehouse output, but your explanation and negative-case evidence remain part of the completion standard. If warehouse access is absent, prepare the drill and its expected assertion locally while leaving execution pending.

```bash
dbt build --project-dir . --profiles-dir . --target local
python runtime/lab.py mutate . --drill missing-fx
# Reseed/rebuild and retain the intended failure, then restore the copied input.
python runtime/lab.py restore .
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p1-05-reasoning)


## Phase completion


Submit the authored holdings staging model, fund/date report, structural and business tests, and an evidence note that connects the raw feeds to the consumer result. Your explanation must distinguish the raw business key from a model name and the reporting currency from a fund master attribute. Show how you derived one result from the copied CSVs before looking at the warehouse output. Include a selected build, its manifest and run-results identities, the independent comparison, and the intended relationship failure followed by repair.

A successful seed operation establishes input loading; a parsed project establishes that dbt understands the files. Neither establishes this learning outcome. The completion verifier must reject unfinished models and compare actual warehouse values with the independent reference. Keep any unavailable connected check pending. Retain your attempt rather than replacing it with the instructor project, and explain which supporting models were supplied. You may enter the advanced phase through its prepared baseline without copying another learner's work. That baseline is disclosed assistance, not evidence that you authored its components.

---


## Optional stretch


The core completion standard is independent of optional work. No additional stretch is required in this phase; the next phase has an independently prepared entry baseline.

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Inspect the project and source grain

<a id="dbt-p1-01-reasoning"></a>

<details>
<summary>Reasoning for dbt-p1-01: A connection is a prerequisite, not a product result</summary>

The expected inventory contains two observations for each of four funds. The composite holding key includes date and instrument, so an eight-row source can be valid even though fund identifiers repeat. Source declarations map logical inputs to already loaded relations; they cannot replace seeding. A target named local describes configuration selection, while its type selects Databricks execution. Good evidence separates CSV inspection, connection readiness and actual warehouse population, retaining an unavailable boundary as pending instead of combining them into one vague pass.

[Return to dbt-p1-01](#dbt-p1-01)

</details>

### Reasoning: Declare and use sources

<a id="dbt-p1-02-reasoning"></a>

<details>
<summary>Reasoning for dbt-p1-02: Logical dependencies and physical ownership must both be correct</summary>

A source call declares an external input; a model reference declares a derived dependency. The identifier expression resolves the source into an owned physical relation without putting environment-specific names into every model. Missing input and wrong source mapping can produce similar first errors, but their repairs differ. The manifest plus seed inventory distinguishes them. Reference data can be loaded and inspected without forcing it into this bounded consumer graph. The complete chain is evidence of understandable lineage, not proof that a compiled query has executed.

[Return to dbt-p1-02](#dbt-p1-02)

</details>

### Reasoning: Normalize type, unit and key contracts

<a id="dbt-p1-03-reasoning"></a>

<details>
<summary>Reasoning for dbt-p1-03: Typed staging preserves business observations</summary>

The expected transformation changes representation without losing either May date. Fund/date/instrument is the row identity; fund alone is a reporting dimension. Correct decimal and date types support later business calculations, but do not prove the join coverage by themselves. The duplicate-key drill should fail because it creates a second observation at the same declared grain. Restoring the copied raw input repairs that cause. Multiplying quantity by price would create a different valuation measure and must not replace the supplied native value.

[Return to dbt-p1-03](#dbt-p1-03)

</details>

### Reasoning: Build a useful mart through ref

<a id="dbt-p1-04-reasoning"></a>

<details>
<summary>Reasoning for dbt-p1-04: Reconciliation tests every business key and value</summary>

The correct report has eight rows because date is part of the consumer key. Its GBP numerator uses the supplied native valuation and a matching dated FX rate. The synthetic unit count creates a teaching NAV measure; the cash exclusion and currency choice must travel with the result. A table materialization changes storage and refresh behavior, not the expected business values. Full per-key comparison detects collapsed dates and shifted fund totals that a single grand-total check could miss.

[Return to dbt-p1-04](#dbt-p1-04)

</details>

### Reasoning: Add minimum key and relationship proof

<a id="dbt-p1-05-reasoning"></a>

<details>
<summary>Reasoning for dbt-p1-05: A meaningful drill identifies the failing contract</summary>

Structural assertions and the independent reference protect different risks. An unknown fund should fail membership or retained-population checks; a missing FX observation should fail dated enrichment coverage rather than be replaced by a rate of one. The useful evidence connects the controlled change to the actual failed test, then connects restoration and reseeding to the recovered eight-key report. A generic command failure or a final green screenshot cannot establish that sequence. The untouched starter remains unfinished until the authored outcomes and their checks are complete.

[Return to dbt-p1-05](#dbt-p1-05)

</details>


---

# dbt independent starter

Read the [owning phase](../README.md) before editing. Prepare from the training project root with `mise run challenge:v2:prepare dbt phase-one-certified`; edit the copied attempt.

## Authored-file list

| Task | Learner-authored paths |
|---|---|
| dbt-p1-01 | `evidence.md` |
| dbt-p1-02 | `models/sources.yml`, `models/staging/stg_holdings.sql`, `evidence.md` |
| dbt-p1-03 | `models/staging/stg_holdings.sql`, `tests/holdings_grain.sql`, `evidence.md` |
| dbt-p1-04 | `models/marts/fund_nav_report.sql`, `evidence.md` |
| dbt-p1-05 | `models/schema.yml`, `tests/holdings_grain.sql`, `tests/matched_funds.sql`, `tests/matched_enrichment.sql`, `tests/nav_reconciliation.sql`, `evidence.md` |

## Declared baseline

These focus files are intentionally unfinished: `models/staging/stg_holdings.sql`, `models/marts/fund_nav_report.sql`. Supporting models and profiles are supplied. Complete the listed files, then verify their output in the required Databricks or Astro environment.

Keep `evidence.md` beside the copied project. Create a named file when its task asks for it. Use a fresh workspace for another attempt; preparation and reset preserve existing work.


---

# dbt: Phase 2 — advanced practice

## Purpose and outcome

Develop the foundation pipeline into a reviewable data-product change. The core begins with dated-join diagnosis and repair, then adds a business reconciliation, controlled incremental replay and an explained feature/history handoff. The starter supplies the supporting models, so a completed foundation attempt is not required.

## Dataset and pipeline

The advanced starter uses the same six raw and two supplementary Portfolio Analytics CSVs as the foundation phase. Staging and supporting models are supplied; enrichment, its coverage/reconciliation tests, the reusable value macro, replay model, fund snapshot and final report contain declared unfinished outcomes. The two May business dates provide a concrete date-join risk. Joining a holding to a price by instrument alone can match both price dates, increasing the population while appearing to add useful price information. Missing dated FX creates a different risk: values become unmatched instead of duplicated.

The source valuation remains authoritative native market value. GBP conversion uses the corresponding dated currency rate; the teaching NAV denominator stays one hundred million synthetic units and excludes cash. A controlled correction is a copied input change, not evidence that the supplied fixture already contained historical corrections. A controlled fund-name change similarly creates snapshot history for the exercise rather than claiming history already exists.

## Prerequisites and workspace

Start in the training project root with the delivered Databricks environment, approved catalog/schema and an owned prefix different from another active attempt. Use the explicit advanced prepare task, then run direct dbt commands from the copied directory. The helper copies supporting files and runtime checks alongside your attempt; no authoring-repository path is needed once prepared. Record the actual adapter version and inspect the profile's local/dev/airflow Databricks targets before choosing one.

```bash
mise run challenge:v2:prepare dbt phase-two-proficient
cd .local/challenges-v2/dbt/phase-two-proficient
export DC_RELATION_PREFIX=dc_alex_dbt02
dbt debug --project-dir . --profiles-dir . --target local
```

Changing an approved schema variable does not grant permission to create a new schema. All seeds, models and snapshots use the declared relation prefix in the single provisioned namespace. Keep credentials out of evidence and perform sign-in outside any recording. If the warehouse is unavailable, author and inspect locally while leaving merge/history execution pending.

## Starter behavior

The supplied staging layer is a prepared successful entry fixture, not your assessed work. Advanced focus models and tests are intentionally unfinished and completion verification rejects them. Seeding is possible before downstream authoring; a broad build can fail on the named unfinished nodes. Diagnose the first failure rather than selecting every dependent model while editing only one. Inspect the checkpoint inventory to distinguish the new task gaps from a wrong source or profile. Negative drills must change only copied data and name their intended failed assertion. Restore source inputs after each drill before using the baseline NAV reconciliation again.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 90–120 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [dbt-p2-01: Diagnose a join fan-out before repair](#dbt-p2-01) | 18–24 | Eight input keys; date-free price join yields sixteen matches; dated repair retains eight |
| [dbt-p2-02: Repair enrichment at the intended grain](#dbt-p2-02) | 18–24 | Eight enriched keys; explicit matched-price/FX coverage and decimal GBP value |
| [dbt-p2-03: Write reconciliation that detects the negative case](#dbt-p2-03) | 18–24 | Coverage and NAV tests fail on copied missing-FX input and pass after restoration |
| [dbt-p2-04: Prove incremental update and replay behavior](#dbt-p2-04) | 18–24 | Older-date correction retains eight keys; a new holding inserts a ninth; replay remains stable |
| [dbt-p2-05: Explain dependency impact and hand over](#dbt-p2-05) | 18–24 | Declared fund report, meaningful snapshot intervals, lineage and explicit Astro boundary |

## Core challenges


<a id="dbt-p2-01"></a>

### dbt-p2-01: Diagnose a join fan-out before repair


<a id="dbt-p2-01-concept"></a>

#### Concept


A join's correctness depends on the relationship between its keys and the grain of each input, not on whether SQL executes. Holdings are at fund/date/instrument grain; prices are at instrument/date grain. An instrument-only price join can attach both May prices to every holding and duplicate the holding's native value. The resulting consumer sum may look plausible because it contains familiar columns and positive amounts, but it measures a fan-out rather than the intended position population.

Count the holding keys before enrichment and the matching price rows per key afterward. With this supplied fixture the date-free price join yields sixteen matches from eight holdings; including the position/price date restores one dated price per holding. An unmatched price or FX observation has a different symptom: a left join retains the holding with null enrichment, while an inner join can hide it by dropping the row. A correct pipeline must detect both duplication and loss. The appropriate diagnosis names which input relationship violated its key contract before choosing a repair. Merely adding distinct to the final report can hide multiplicity without selecting the right dated observation.

#### Challenge


Use the prepared staging inputs to reproduce a bounded date-free price join in a diagnostic query. Count input holdings, joined rows and the maximum matches per holding key. Inspect a representative instrument on both May dates and explain why the incomplete predicate duplicates its value. Keep this deliberately defective diagnostic separate from the consumer model and never treat it as the final answer.

Write the intended enrichment contract in your evidence note: holding grain remains unchanged, price matches by instrument/date, FX matches by native currency/reporting currency/date, and missing matches must be testable. Inspect the unfinished enrichment file and identify the selected source columns and required output fields before repairing it in the next task. Record the original diagnostic result and one key's two candidate prices. If a dependency is not yet built, build only its supplied upstream staging slice instead of copying an instructor enrichment model.

#### Hint


<details>
<summary>Expose the duplicate match before changing the mart</summary>

Start with the smallest join that can demonstrate the defect: holdings plus prices, without FX or aggregation. Compare one holding's date with both price dates. Group the diagnostic by the complete holding key and inspect the match count. A grand total is a later symptom; the duplicated key is the direct cause. Do not repair the join by selecting a latest price when the contract requires the same business date.

</details>

#### Check


Run the prepared upstream staging build, then inspect the defective and corrected diagnostic queries in the warehouse. Expect eight holding keys, sixteen rows from the instrument-only price join, and eight from the dated join. Confirm the discrepancy is actually explained by matching both fixture dates rather than by a duplicate raw key. Retain the query text, execution identity and a representative matching pair.

Explain why distinct over a selected projection might conceal this defect and why dropping unmatched rows would create another one. The negative diagnostic is successful teaching evidence only when it produces the predicted multiplicity. An authentication error or unfinished-model compile failure does not prove fan-out. Restore the intended predicate before any final consumer build, and use the later grain/coverage checks to enforce it. If the warehouse cannot run, retain the inspected fixture keys and diagnostic SQL with execution explicitly pending; a local prediction is not observed warehouse evidence.

```bash
dbt build --select stg_holdings stg_prices stg_fx_rates stg_funds --project-dir . --profiles-dir . --target local
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p2-01-reasoning)


---


<a id="dbt-p2-02"></a>

### dbt-p2-02: Repair enrichment at the intended grain


<a id="dbt-p2-02-concept"></a>

#### Concept


An intermediate model isolates business relationships that would otherwise be repeated in every consumer query. Its output contract is more important than its position in a folder: here it retains each typed holding and attaches a dated price, dated GBP conversion rate and converted value. Left joins make missing observations visible to a coverage assertion. They do not excuse incomplete data; they preserve evidence needed to reject it.

A reusable expression is valuable when it states an actual shared rule, such as converting a decimal native valuation by an explicitly matched rate with an agreed output precision. That macro should compile into understandable SQL and should not decide the join keys or manufacture a default rate. For example, a missing May 20 GBP rate must remain null and fail coverage even though GBP-to-GBP is normally one. The feed's declared observation is part of the readiness contract. Fund master may describe a USD base currency while this report remains explicitly GBP. Moving environment routing or relationship selection into an opaque macro would make the model harder to review and would not add useful abstraction.

The supplied `int_fund_attributes` and `int_positions_dated` retain v1's two smaller intermediate contracts. The first filters active funds and exposes their reporting attributes; the second adds cash balance and accrued interest once at fund/date/currency grain. All four raw fund-master entries are active here, and the positions helper retains eight dated rows. These are supplied supporting models to inspect rather than additional unfinished SQL assignments. Cash remains outside the declared teaching NAV, so an available cash field does not authorize silently adding it to that report.

#### Challenge

Retain the seven staging fields and append `close_price`, `fx_rate_to_base` and `mv_base_ccy`. Prices provide `instrument_id`, `price_date` and `close_price`; FX provides `from_ccy`, `to_ccy`, `rate_date` and `fx_rate`. Match the holding instrument/date to prices and its local currency/GBP/date to FX. Use `native_value` for the decimal GBP amount and retain the same holding key.


Complete the enrichment model with the declared dated price and FX predicates, preserving the holding fields and appending the expected enrichment columns. Implement the native-value macro with explicit decimal conversion and use it for a meaningful repeated expression. Keep input relationship logic visible in model SQL so a reviewer can see instrument/date and currency/date matching without tracing several macro layers.

Build enrichment as a view and inspect its row/key population before building the consumer report. Document the distinction between the supplied close price, native valuation and converted GBP amount. Show the rendered macro expression in compiled SQL and verify that the resolved source/model references still use your owned namespace. If you choose a different helper signature, preserve the same units and precision and explain that bounded change. Do not replace missing FX with a rate of one or derive native market value from quantity times price.

Build and inspect the two supplied intermediate helpers as well. `int_fund_attributes` exposes `fund_id`, `fund_name`, `inception_date`, `base_ccy` and `strategy_code` for active funds. `int_positions_dated` exposes `fund_id`, `position_date`, `local_ccy` and `cash_plus_accrued`. Trace their refs and explain why filtering or unit arithmetic belongs in one named model rather than being repeated independently by each consumer. Use cautious indirect test selection while downstream focus models are unfinished.

#### Hint


<details>
<summary>Keep joins visible and reuse only the value rule</summary>

Write the two join predicates separately and check each candidate key against the input grain. Add the conversion expression only after the joined fields make sense. Compile the macro in a selected model and read the emitted SQL as ordinary arithmetic; useful reuse should make the rule easier to inspect. Keep null coverage distinct from numeric reconciliation so a missing match cannot disappear inside an aggregate sum.

</details>

#### Check


The enriched view must retain eight holding keys with exactly one dated price and FX observation per key and decimal GBP values consistent with the independent calculation. Inspect selected rows and the actual relation metadata. The compiled macro expression should use the supplied native value and matched rate without hidden environment names or fallback currency assumptions.

Check four active helper fund rows and eight cash/accrued rows. Compare one helper amount directly with its copied source's cash balance plus accrued interest, and explain why it is excluded from the current NAV. Distinguish a legitimate supporting-model build from a relationships test that prematurely selects an unfinished downstream consumer.

```bash
dbt build --select int_fund_attributes int_positions_dated --indirect-selection=cautious --project-dir . --profiles-dir . --target local
dbt show --select int_positions_dated --limit 8 --project-dir . --profiles-dir . --target local
```

Temporarily remove the copied May 20 GBP FX observation, reseed that input and rebuild enrichment. The population can remain eight while matched coverage fails for the affected observations; do not interpret retained row count as a complete conversion. Restore the copied input and rebuild before comparing baseline values. Explain why the relationship predicates remain in the model, why a left join plus an explicit failure check is useful, and why reporting currency is not inferred from the fund master. Retain the compiled expression, missing-match result and repaired enrichment output as separate pieces of evidence.

```bash
dbt build --select int_holdings_enriched --project-dir . --profiles-dir . --target local
python runtime/lab.py mutate . --drill missing-fx
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p2-02-reasoning)


---


<a id="dbt-p2-03"></a>

### dbt-p2-03: Write reconciliation that detects the negative case


<a id="dbt-p2-03-concept"></a>

#### Concept


A business reconciliation compares a consumer result with an independently specified meaning. It should detect wrong units, key loss, joined duplication and changed values rather than simply compare two sums built from the same faulty model. The supplied custodian NAV fixture and Decimal CSV reference give concrete expected results for the unmodified teaching population. Key membership is as important as numeric closeness: a report missing one date should fail even when another row absorbs its value.

A negative case tests the assertion's sensitivity. Removing a copied FX observation should fail enrichment coverage; feeding that incomplete result into a holdings-only NAV report should not produce accepted output. Another controlled experiment intentionally changes a holding's value. That makes baseline NAV comparison fail for a legitimate reason until the variation's expected output is used. These cases require different interpretations. A test message without the input variant and failed node cannot tell a reviewer whether it detected a real defect, an intended correction or an unrelated connection issue. Keep the assertion's unit, tolerance, key set and applicable fixture state explicit.

#### Challenge


Author the matched-enrichment and NAV reconciliation SQL tests in the copied project. Preserve the complete holding and report key sets, test non-null matched price/rate fields, and compare the report against the declared baseline expected NAV with an appropriate decimal tolerance. Add descriptions explaining the reporting currency, synthetic unit denominator and cash exclusion. Use structural schema tests as complementary checks rather than replacing the business assertion.

Predict which node will fail when the copied May 20 GBP FX row is removed. Execute that mutation, selected reseed and build/test sequence in your owned attempt, then retain the failed node and diagnostic rows. Restore the source copy, reseed and rerun the same graph. Record the repaired comparison and a brief explanation of why a baseline oracle is inappropriate for the later deliberate value correction. Do not change the expected fixture merely to make a defective model agree with itself.

#### Hint


<details>
<summary>Compare membership before tolerating numeric differences</summary>

Compare keys before values and state the tolerance in money or NAV units. A left join from expected keys to actual results can expose missing report rows, while the reverse membership check exposes invented ones. Inspect the first failed assertion and its compiled SQL. If it only compares a grand sum, ask whether two offsetting errors or shared row loss could still pass. Strengthen the contract rather than adding a looser threshold.

</details>

#### Check


Run both authored assertions on an unmodified complete project and compare the report to the independent CSV reference. All eight report keys and their GBP/NAV values must agree. After the missing-FX mutation, the expected coverage assertion must fail because the declared rate is absent; an unrelated unfinished macro or profile failure is not the intended result. Restore and reseed before the final passing run.

Retain the original and mutated source hashes, failed node, observed failed rows, repair diff and final run-results identity. Explain how the test detects a missing date and how its tolerance handles decimal representation without accepting a wrong monetary result. Record that the subsequent corrected-value variant changes the independent oracle rather than the definition of the baseline input. A verifier can inspect values and artifacts, but your explanation must connect the failing contract to the controlled cause. Keep actual warehouse execution pending if only the assertion text and fixture arithmetic have been prepared.

```bash
dbt test --select matched_enrichment nav_reconciliation --project-dir . --profiles-dir . --target local
python runtime/lab.py restore .
python runtime/lab.py reference .
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p2-03-reasoning)


---


<a id="dbt-p2-04"></a>

### dbt-p2-04: Prove incremental update and replay behavior


<a id="dbt-p2-04-concept"></a>

#### Concept


Incremental materialization changes how a relation is maintained; it does not automatically make a pipeline correct under late data. A merge needs a stable unique key that identifies the business observation being replaced. For holdings that key includes fund, date and instrument. Choosing only a fund would overwrite another date, while appending without key matching would duplicate an existing observation when the same input is replayed.

This exercise creates a correction to the first copied May holding by increasing its native market value by one thousand. The selected observation is GBP-denominated, so its independently expected GBP value changes by the same amount. The date remains the older fixture date. A filter that processes only dates greater than the current maximum would miss this legitimate correction. Replaying the corrected input twice should produce the same eight-key state after both merges, with one changed value and no duplicate. A second controlled input appends a new holding key: PEF-EM-GROWTH, May 20, GB00B3M9JJ78, with native and GBP value 500. Its price and FX already exist, so the result must grow to nine keys with total exposure another 500 higher. Replaying that combined input must retain nine, proving insertion as well as update. The experiment is bounded to your namespace and copied fixture; it does not prove a general production late-arrival policy, transaction isolation or concurrent writer behavior. Those limitations belong in the handoff.

#### Challenge

The replay relation must expose `fund_id`, `position_date`, `instrument_id` and `exposure_gbp`, with the first three fields forming its unique key. Compute exposure from the matched native value/rate at decimal(28,2) precision; the independently queried checker uses these exact output names.


Implement the holdings replay model with Databricks incremental merge behavior and the composite holding key. Select enough of the current copied input to include an older-date correction rather than blindly filtering above the maximum stored date. Build an initial owned relation and retain its sorted key/value projection. Apply the controlled correction helper to the copied seed, reseed the changed input and run the replay model twice.

After the correction check, apply the new-holding helper to append the specified unseen key. Reseed and run the replay model twice again. Compare both nine-key states with the independently calculated input, including the retained older-date correction.

After each merge, compare the warehouse relation with the independent corrected input calculation. Record the exact changed key, original and corrected amount, unchanged date and overall row count. Keep the consumer baseline NAV comparison separate: its unmodified custodian fixture intentionally no longer agrees with the corrected holdings. Restore the raw copy after collecting the variation evidence, and state whether the owned replay relation has been rebuilt to baseline. Never reset another learner's prefix or call an empty-table first build proof of incremental replay.

#### Hint


<details>
<summary>Prove the older observation participates in both merges</summary>

First show that the selected business date is older than the maximum date already stored. Then inspect the unique-key configuration and the compiled merge predicate. Build from the full tiny copied input for this teaching experiment so a date watermark cannot hide the correction. The decisive check is the second corrected run: identical corrected input should retain eight keys; after the explicit arrival, identical combined input should retain nine. It must not add a tenth row or alter an unrelated key. Keep value-change evidence alongside membership evidence.

</details>

#### Check


Expect eight unique holding keys before the drill, after the corrected merge and after the second replay. Exactly one older-date GBP value should increase by one thousand; all other keys and values remain unchanged. After the new-holding drill, expect nine unique keys and exactly 500 additional GBP exposure; the second replay must retain the same nine-key/value projection. Query actual Databricks output and use the runtime replay checker, which calculates expected values from the copied holdings and FX inputs. A parse or local SQL emulation cannot prove Delta merge execution.

Retain the first and both corrected run-results identities, key/value projections, copied input hashes and the independently identified changed key. Explain why a maximum-date-only filter would reject a valid correction and why replay should not duplicate it. The ordinary baseline NAV assertion is expected to disagree while this variation is active; do not disable it permanently or change the baseline fixture to conceal that distinction. Restore source inputs and disclose the final relation state in your handoff. If connected execution cannot occur here, the implementation and expected transition can be reviewed locally but this check stays pending.

```bash
python runtime/lab.py mutate . --drill correction
dbt seed --select holdings_raw --project-dir . --profiles-dir . --target local
dbt run --select holdings_replay --project-dir . --profiles-dir . --target local
python runtime/lab.py check-replay .
# Repeat the run/check above, then prove insertion and replay.
python runtime/lab.py mutate . --drill new-holding
dbt seed --select holdings_raw --project-dir . --profiles-dir . --target local
dbt run --select holdings_replay --project-dir . --profiles-dir . --target local
python runtime/lab.py check-replay .
# Repeat the run/check above once more. Restore the copied input and owned table.
python runtime/lab.py restore .
dbt seed --select holdings_raw --project-dir . --profiles-dir . --target local
dbt run --select holdings_replay --full-refresh --project-dir . --profiles-dir . --target local
python runtime/lab.py check-replay .
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p2-04-reasoning)


---


<a id="dbt-p2-05"></a>

### dbt-p2-05: Explain dependency impact and hand over


<a id="dbt-p2-05-concept"></a>

#### Concept


An end-to-end feature needs a consumer question, output grain, units, lineage and evidence that someone can review. Generating another SQL file is insufficient if its result cannot be interpreted. A small fund-level report can answer how the two supplied dates differ in holdings exposure; it must label that observation difference without pretending it is investment return. The fixture lacks the flows and complete unit history needed to establish that stronger measure.

Attribute history is a separate feature. A snapshot can retain successive fund-name versions using a stable fund key and validity intervals. A copied fund-master name change creates the exercise's second observed version; it is not a correction to the holding value and does not change the reporting date. One current interval and one closed interval for the changed key demonstrate the intended history. Documentation connects these decisions to the next consumer and to Astro's worker boundary: the terminal's successful build does not prove worker executable paths, mounted files or task-time credentials. A useful handoff states what was actually executed and what still needs connected or human review.

#### Challenge

Use raw `fund_cd` as the snapshot key and track `fund_name`, `base_ccy`, `strategy_code` and `is_active`. Inspect the generated `dbt_valid_from` and `dbt_valid_to` columns for the changed key; the active version has an open validity end under the supplied snapshot configuration. The final report retains the five fund/date fields stated in foundation task dbt-p1-04.


Complete the report model and its documentation, keeping a useful bounded feature based on available fund/date inputs. State the consumer question and distinguish exposure difference from financial performance. Add descriptions and tests for the report key, GBP values and teaching NAV limitation. Inspect lineage showing sources, staging, enrichment and the new consumer output.

Implement the fund snapshot in the approved namespace with fund identifier as its unique key and the declared changing attributes. Run an initial snapshot, mutate only the copied fund name, reseed and snapshot again. Query current and closed validity intervals for that key, then restore the copied baseline input while preserving captured history evidence. Assemble a reviewable diff and a short Astro handoff listing the project/profile paths, selected target, owned prefix, required worker executable and pending task-time authentication checks. Full runnable instructor references are comparison material after your attempt, not a substitute for your authored feature.

#### Hint


<details>
<summary>Separate reporting meaning, attribute history and worker readiness</summary>

Choose a report whose inputs really support its claim. For history, inspect the snapshot key and check-column list before changing a copied fund name; changing a nontracked field should not create the expected new version. Query the changed key rather than assuming a larger snapshot row count proves valid intervals. Keep the source restoration and historical table state distinct so the handoff explains both.

</details>

#### Check


The final baseline report must reproduce all eight independently specified fund/date values and show understandable lineage and documentation. Your additional feature needs an independent calculation for its own declared output. The snapshot experiment must show a closed previous interval and one current interval for the changed fund, with unchanged fund identity. Query the actual owned snapshot relation; compilation cannot establish validity history.

Retain the report/test run-results identities, feature expectation, snapshot before/after projections and bounded diff. Explain the meanings of reporting date, ingestion time and snapshot validity time. Include actual terminal adapter/target details and mark worker mounts, task-time token delivery, managed versions and scheduled run evidence pending unless observed. Restore the copied source data and describe whether the snapshot intentionally retains the teaching variation. Query the Delta and snapshot results in Databricks; include worker connection requirements in the Astro handoff.

```bash
dbt snapshot --project-dir . --profiles-dir . --target local
python runtime/lab.py mutate . --drill fund-change
dbt seed --select fund_master_raw --project-dir . --profiles-dir . --target local
dbt snapshot --project-dir . --profiles-dir . --target local
dbt docs generate --project-dir . --profiles-dir . --target local
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#dbt-p2-05-reasoning)


## Phase completion


Finish the advanced core with an enrichment that retains every declared holding key, business checks that reject missing matches, a useful reusable decimal expression, and a consumer report whose baseline values agree with the independent CSV calculation. Demonstrate a controlled correction to an older business date, replay it twice through the incremental model, and show that the corrected key appears once. Append the specified new holding and prove nine keys after both insertion and replay, then rebuild the owned replay table to the eight-key baseline after restoring copied inputs. Demonstrate a separate fund-name change through snapshot validity. Keep those experiments distinct: replay updates an observation, while a snapshot retains changing attribute versions.

Your handoff contains the authored files, a bounded diff, failed and repaired assertions, manifests/run results, independent key/value comparisons, and a short explanation of each supplied model. Include a small fund-level reporting feature whose population and units are explicit. Do not manufacture an investment-return measure from two valuation dates without the necessary flow inputs. Preserve baseline fixture bytes and document restoration after variations. Source preparation, parsed SQL and locally calculated expected values remain supporting evidence until the Databricks build, Delta merge and snapshot queries execute. The Astro handoff lists the worker paths and connection checks needed for the Airflow route.

---


## Optional stretch


The core completion standard is independent of optional work. Choose a separately timed route from [the stretch guide](stretch/README.md).

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Diagnose a join fan-out before repair

<a id="dbt-p2-01-reasoning"></a>

<details>
<summary>Reasoning for dbt-p2-01: Multiplicity reveals an incomplete join key</summary>

Both May price observations share an instrument identifier. The date-free join therefore doubles matching holdings even though raw keys are valid. Matching the business date repairs that particular predicate. A missing match remains a separate coverage concern and should not be solved by dropping the holding. The diagnostic evidence must show input keys, actual multiplicity and the corrected relation, so the reviewer can understand the cause without trusting a final aggregate.

[Return to dbt-p2-01](#dbt-p2-01)

</details>

### Reasoning: Repair enrichment at the intended grain

<a id="dbt-p2-02-reasoning"></a>

<details>
<summary>Reasoning for dbt-p2-02: Explicit coverage and readable SQL make reuse trustworthy</summary>

The intermediate output should have the same holding grain as staging. Its left joins preserve unmatched observations for diagnosis, and the coverage test rejects them before a consumer result can be accepted. The decimal macro expresses a valuation rule rather than a relationship rule. A rate-of-one fallback would hide a missing declared feed observation; inferring currency from fund master would change the report contract. Both mistakes can yield plausible numbers, so inspect compiled arithmetic and matched keys together.

[Return to dbt-p2-02](#dbt-p2-02)

</details>

### Reasoning: Write reconciliation that detects the negative case

<a id="dbt-p2-03-reasoning"></a>

<details>
<summary>Reasoning for dbt-p2-03: An independent expected population catches shared model errors</summary>

The useful reconciliation owns its expected keys and units independently of the enrichment. Missing FX should be rejected as coverage loss; restoration repairs that input cause. The correction exercise later changes an input value deliberately, so its expected result is recalculated from the copied input rather than accepted against a stale baseline NAV. A test that merely matches the mart to another aggregate of the same broken model would miss shared loss or duplication. Record the variant and failed assertion together.

[Return to dbt-p2-03](#dbt-p2-03)

</details>

### Reasoning: Prove incremental update and replay behavior

<a id="dbt-p2-04-reasoning"></a>

<details>
<summary>Reasoning for dbt-p2-04: Replay correctness is a state transition, not a green command</summary>

The merge key identifies the exact dated holding. A copied older-date correction must reach that key even after the later date exists, and running the same correction again must leave the eight-key result unchanged. A new PEF-EM-GROWTH/instrument key then grows the relation to nine, adding 500 GBP without losing the correction; its replay stays at nine. Restoring seed inputs alone cannot delete that inserted target key, so the final owned full-refresh is an explicit restoration step. The independent replay checker uses the modified input, while the custodian NAV fixture still describes baseline data. Delta behavior requires actual warehouse execution and cannot be inferred from compiled SQL. A good report retains before/after state and discloses whether restoration also rebuilt the owned relation.

[Return to dbt-p2-04](#dbt-p2-04)

</details>

### Reasoning: Explain dependency impact and hand over

<a id="dbt-p2-05-reasoning"></a>

<details>
<summary>Reasoning for dbt-p2-05: A useful handoff states meaning and observed boundaries</summary>

The feature should answer a supported question with a declared key and units. Two exposure observations do not automatically establish return. Snapshot history records a separate changing-attribute contract and needs actual validity queries after a controlled name change. Restoring raw inputs does not erase captured history. Lineage, tests and a reviewable diff explain the terminal result, while the Astro handoff identifies worker paths and authentication that remain unverified until scheduled execution. These distinctions make the product interpretable rather than merely executable.

[Return to dbt-p2-05](#dbt-p2-05)

</details>


---

# dbt independent starter

Read the [owning phase](../README.md) before editing. Prepare from the training project root with `mise run challenge:v2:prepare dbt phase-two-proficient`; edit the copied attempt.

## Authored-file list

| Task | Learner-authored paths |
|---|---|
| dbt-p2-01 | `models/intermediate/int_holdings_enriched.sql`, `evidence.md` |
| dbt-p2-02 | `models/intermediate/int_holdings_enriched.sql`, `macros/native_value.sql`, `evidence.md` |
| dbt-p2-03 | `tests/matched_enrichment.sql`, `tests/nav_reconciliation.sql`, `models/schema.yml`, `evidence.md` |
| dbt-p2-04 | `models/marts/holdings_replay.sql`, `evidence.md` |
| dbt-p2-05 | `models/marts/fund_nav_report.sql`, `snapshots/fund_history.sql`, `models/schema.yml`, `evidence.md` |

## Declared baseline

These focus files are intentionally unfinished: `macros/native_value.sql`, `models/marts/holdings_replay.sql`, `snapshots/fund_history.sql`, `models/marts/fund_nav_report.sql`, `models/intermediate/int_holdings_enriched.sql`, `tests/matched_enrichment.sql`, `tests/nav_reconciliation.sql`. Supporting models and profiles are supplied. Complete the listed files, then verify their output in the required Databricks or Astro environment.

Keep `evidence.md` beside the copied project. Create a named file when its task asks for it. Use a fresh workspace for another attempt; preparation and reset preserve existing work.


---

# Historical dbt extension

The earlier extension is retained in the separate instructor archive and authoring workspace. Its setup and claims require review before reuse; it is outside the current learner assignment.

Earlier examples assume missing FX can default to 1.0. The current project requires a matching dated rate; missing enrichment must fail its checks. Storage tuning also needs measured query evidence.

Use the [current advanced phase](../README.md) for the supported tasks, independently prepared baseline and evidence checks. Ask the instructor to select any additional historical exercise.

<a id="v2-dbt-phase-two-proficient-stretch-readme-md-dbt-optional-stretch-selection"></a>
<a id="v2-dbt-phase-two-proficient-stretch-readme-md-full-legacy-advanced-reference"></a>
<a id="v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-intermediate-marts-tests-docs"></a>
<a id="v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-1-the-enrichment-join-int_holdings_enriched"></a>
<a id="v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-2-the-two-supporting-intermediate-models"></a>
<a id="v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-3-first-curated-mart-agg_fund_exposure"></a>
<a id="v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-4-second-curated-mart-fct_portfolio_returns"></a>
<a id="v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-5-generic-tests-on-the-marts"></a>
<a id="v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-6-a-singular-reconciliation-test-nav-within-tolerance"></a>
<a id="v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-7-the-full-build-dbt-build"></a>
<a id="v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-8-docs-and-the-lineage-graph"></a>
<a id="v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-9-the-databricks-performance-post-hook-optimize-zorder"></a>
<a id="v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-10-capstone-add-a-new-mart-end-to-end"></a>
<a id="v2-dbt-phase-two-proficient-stretch-readme-md-done"></a>


---

# databricks-cli challenges

The Databricks command-line interface (CLI) provides a read-only discovery route into the prepared training environment. You establish actual profile/identity, distinguish workspace objects from catalog/schema/table metadata, inspect permitted qualified names, interpret JSON and explain an access limitation. A visible workspace directory is not a queried table, and a valid identity is not proof of every grant. This route contributes context for later warehouse work without provisioning resources.

## Before you start

Use the delivered CLI and instructor-provided profile, permitted workspace path and approved namespace/table. Prepare a copied attempt through mise and keep discovery/evidence notes there. Sign in outside recordings and retain safe names/types rather than tokens. Inspect installed help/version instead of treating source pins as measured facts. The metadata JSON is a labelled offline example; its familiar training names do not prove current resources or permissions. No catalog/schema creation, grant changes or deployment is necessary for this read-only core.

## Suggested timeline and tasks

Estimates include reading, practice, checks and explanation. Allow additional time for environment setup and optional extensions.

| Phase | Task | Minutes |
| --- | --- | --- |
| Foundation | [databricks-cli-p1-01: Establish the CLI identity boundary](phase-one-certified/README.md#databricks-cli-p1-01) | 9–13 |
| Foundation | [databricks-cli-p1-02: Separate workspace and Unity Catalog names](phase-one-certified/README.md#databricks-cli-p1-02) | 9–13 |
| Foundation | [databricks-cli-p1-03: Inspect permitted schema and table metadata](phase-one-certified/README.md#databricks-cli-p1-03) | 9–13 |
| Foundation | [databricks-cli-p1-04: Filter JSON and explain a limited result](phase-one-certified/README.md#databricks-cli-p1-04) | 9–13 |
| Foundation | [databricks-cli-p1-05: Produce a bounded discovery handoff](phase-one-certified/README.md#databricks-cli-p1-05) | 9–13 |

## Choose your phase

- [Foundation](phase-one-certified/README.md): Foundation core with explicit completion evidence.
- [Advanced](phase-two-proficient/README.md): Not offered: no tasks or completion gate.

Finish the core tasks before choosing optional stretch.

## Teaching concepts

Profile, identity, workspace path, qualified data name and warehouse execution are separate boundaries. Structured output preserves those distinctions, while empty/missing/denied observations require different explanations. Metadata discovery does not query row values or execute a dbt model. Use the end-of-phase reasoning keys after your attempt and record remaining connected probes individually. Full instructor reference observations belong separately, and no invented advanced assignment is needed to make this route complete.

Keep a discovery trail that another participant can repeat safely: the exact profile, permitted namespace, command category and selected metadata fields. When an object is denied or missing, preserve that limitation with its context instead of replacing it with a more convenient fixture response. This makes the subsequent connection and source-loading work easier to diagnose without pretending discovery granted access.


---

# databricks-cli: Phase 1 — foundations

## Purpose and outcome

Use the Databricks CLI to discover a prepared training environment without confusing its object types. You establish identity, distinguish workspace files from Unity Catalog metadata, inspect permitted catalog/schema/table information, interpret JSON and explain a limited result. The core is read-only. It prepares you to ask accurate questions about the later dbt warehouse boundary rather than provisioning resources to make a listing succeed.

## Dataset and pipeline

The starter metadata JSON contains a labelled snapshot of one training catalog, schema, table and workspace directory. It is an example response for offline interpretation, not proof that these objects currently exist or are accessible. The workspace path is a filesystem-like object; a catalog/schema/table name identifies governed data metadata. A SQL warehouse is an execution resource rather than another folder in that hierarchy. The local snapshot deliberately uses familiar training names so you can practice those distinctions.

The connected route uses the actual approved namespace and object paths provided by the instructor. Those values may differ from the example. Identity and metadata access remain separate prerequisites: a valid login can still lack permission to enumerate a particular catalog or workspace directory. The report must distinguish such a denial from an empty permitted result or missing object.

## Prerequisites and workspace

Prepare an independent copied attempt through mise from the training project root. Use the delivered CLI and identity setup, then inspect the actual installed version/help. Keep your discovery and evidence files inside the attempt. The instructor supplies the profile, permitted workspace path, approved catalog/schema and inspected table; do not guess them from the fixture or create replacement objects.

```bash
mise run challenge:v2:prepare databricks-cli phase-one-certified
cd .local/challenges-v2/databricks-cli/phase-one-certified
databricks --version
databricks current-user me --profile "$V2_DBX_PROFILE" --output json
```

Sign-in happens outside recordings. Record safe identity and qualified object names without tokens. If no cloud access exists here, inspect the labelled fixture and draft the exact probes with their actual connected observations pending. Source pins are intended versions, not measured installation facts. The class does not require broad grants, new schemas, infrastructure deployment or production job changes.

## Connection variables

Before running connected probes, set `V2_DBX_PROFILE` to the delivered profile name, `V2_WORKSPACE_PATH` to the permitted workspace directory, `DBT_CATALOG` and `DBT_SCHEMA` to the approved namespace, and `V2_DBX_TABLE` to the fully qualified inspection table supplied by the instructor. These values describe existing resources; do not create replacements or copy the fixture names into actual-evidence fields. Record the configured names safely and keep authentication values outside the notes.

## Starter behavior

The metadata snapshot parses successfully and there is no deliberate broken resource. Offline verification checks that example structure and reports supporting evidence only. Completion requires actual read-only environment observations and an explanation of the distinct object types. A denied path may be a meaningful permitted exercise observation if its boundary is stated; it is not an excuse to label every unavailable probe successful. Phase two is explicitly not offered and has no tasks or invented timing.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 45–65 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [databricks-cli-p1-01: Establish the CLI identity boundary](#databricks-cli-p1-01) | 9–13 | Installed version/help and intended authenticated profile without secrets |
| [databricks-cli-p1-02: Separate workspace and Unity Catalog names](#databricks-cli-p1-02) | 9–13 | Correct object types and separate qualified-name/path examples |
| [databricks-cli-p1-03: Inspect permitted schema and table metadata](#databricks-cli-p1-03) | 9–13 | Approved namespace and metadata/type of one qualified table |
| [databricks-cli-p1-04: Filter JSON and explain a limited result](#databricks-cli-p1-04) | 9–13 | Correct structured projection and diagnostic categories |
| [databricks-cli-p1-05: Produce a bounded discovery handoff](#databricks-cli-p1-05) | 9–13 | Identity/object/type/limitation and next consumer question linked to actual probes |

## Core challenges


<a id="databricks-cli-p1-01"></a>

### databricks-cli-p1-01: Establish the CLI identity boundary


<a id="databricks-cli-p1-01-concept"></a>

#### Concept


A profile selects connection and authentication context; it is not a business namespace or proof of table permissions. The CLI executable version determines available command groups and output options, while the active identity determines whose rights those commands use. A copied source configuration can describe an intended profile/version without establishing the environment currently loaded in the terminal.

Inspecting current user is a read-only identity probe. It should return a safe account identity in the prepared environment, but its success does not imply access to every catalog or warehouse. Keep tokens out of notes and screenshots. When cloud access is absent, the metadata fixture can teach response interpretation but cannot establish authenticated identity. This distinction prevents a local JSON parse from becoming a false readiness pass for later dbt work.


#### Challenge


Inspect `databricks --version` and the installed current-user help. Select `$V2_DBX_PROFILE`, supplied by the instructor, and run the read-only current-user probe. Record the returned account identity, profile and CLI version in `discovery.md` without credential values.

Confirm the intended identity before listing resources. Explain how your shell username differs from the remote account and how profile selection affects the request. If authentication is unavailable, record that prerequisite and interpret the local metadata fixture separately. Keep fixture examples labelled; they cannot provide a current-user response or establish the rights of an authenticated training account.


#### Hint


<details>
<summary>Separate profile selection from observed authenticated identity</summary>

Inspect command-group `--help` for the installed CLI.

Compare the selected profile and account identity; similar host names can belong to different contexts. Use installed help when a documented flag is unavailable. Record a command's failure category without dumping authentication configuration or tokens. Version/source pins describe intent, while the executable response is the measured boundary.

</details>

#### Check


Inspect the current-user response for the intended training identity and retain the measured CLI version/help. The evidence note must avoid secrets and state whether the probe actually reached Databricks. Explain why a successful identity response does not establish later catalog/table privileges.

An offline fixture parse remains labelled supporting, and an auth error remains a prerequisite failure rather than an empty resource list. If multiple profiles exist, identify which one produced the retained observation. Do not switch to another person's credentials or create broad grants to make the exercise pass. The live verifier reads identity and permitted metadata without provisioning.

```bash
databricks current-user me --profile "$V2_DBX_PROFILE" --output json
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#databricks-cli-p1-01-reasoning)


---


<a id="databricks-cli-p1-02"></a>

### databricks-cli-p1-02: Separate workspace and Unity Catalog names


<a id="databricks-cli-p1-02-concept"></a>

#### Concept


Workspace objects organize notebooks, directories and other workspace content; Unity Catalog organizes governed data objects through catalog, schema and table names. A path containing training_dev does not mean it is the same object as a catalog named training_dev. The CLI uses different command groups and response fields for those boundaries.

The fixture's workspace directory under Shared and its qualified holdings table illustrate that naming similarity. A SQL warehouse supplies execution for queries, while listing a directory or table metadata does not run model SQL. Misidentifying these objects can send a learner to a filesystem command when they need governed table metadata, or lead them to infer data access from a visible notebook folder. State type, identifier and purpose together rather than retaining only a familiar name.


#### Challenge


Inspect `metadata.json` and make a short map of its workspace directory, catalog, schema and table. Use the corresponding read-only command groups to inspect `$V2_WORKSPACE_PATH` and the approved catalog in the connected environment.

Record each object's type, qualified path/name and relevant command group. The familiar `training_dev` spelling may appear as a catalog, directory, both or neither; inspect actual responses rather than infer identity from the name. Identify the warehouse separately as an execution resource. Explain why seeing a notebook directory cannot establish SELECT access to a table or execution of a dbt model.


#### Hint


<details>
<summary>Record type and qualified identity alongside the familiar name</summary>

The starter fixture includes both object families specifically to practice this distinction.

Look at response fields such as object type, path, catalog name, schema name and full table name. Compare the corresponding command groups in installed help. The separator convention and object type matter as much as the displayed word training. Keep fixture names labelled examples until actual connected probes establish their current counterparts.

</details>

#### Check


The discovery note must correctly distinguish a workspace directory, catalog, schema, table and SQL warehouse, with appropriate identifiers and safe read-only inspection commands. Inspect actual responses when connected and label fixture-only examples otherwise. Explain why workspace visibility does not establish table SELECT rights or warehouse execution.

Retain the two distinct identifiers and their response categories. A listing cannot be described as a full-text search over table data or a SQL query result. If the provided path is unavailable, record whether it was denied, missing or unprepared; do not invent another directory to satisfy the expected shape.

```bash
databricks workspace list "$V2_WORKSPACE_PATH" --profile "$V2_DBX_PROFILE" --output json
databricks catalogs list --profile "$V2_DBX_PROFILE" --output json
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#databricks-cli-p1-02-reasoning)


---


<a id="databricks-cli-p1-03"></a>

### databricks-cli-p1-03: Inspect permitted schema and table metadata


<a id="databricks-cli-p1-03-concept"></a>

#### Concept


Metadata discovery answers what objects exist or are visible and how they are described. It does not automatically return their data rows. Catalog/schema/table listings can be filtered by permissions, so a user may see less than an administrator. A table's qualified identity and type help connect a later dbt source declaration to its physical relation.

Use the instructor's approved namespace rather than assuming a training label is globally unique. The same table short name can exist in several schemas, and a source profile can resolve one while a manual CLI command inspects another. Retaining the full qualified name prevents that confusion. Read-only discovery must not become provisioning: creating schemas, changing grants or deleting a denied object would change the environment rather than explain the observed access boundary.


#### Challenge


List schemas under `$DBT_CATALOG`, then tables under `$DBT_CATALOG` and `$DBT_SCHEMA`, using `$V2_DBX_PROFILE` and JSON output. Inspect the instructor-provided `$V2_DBX_TABLE` with `tables get`.

Confirm the returned full name belongs to the approved catalog/schema. Record its type and one useful available owner/description field in `discovery.md`. Keep the table identifier separate from the workspace path. Compare it with the source-loading namespace used by the dbt route. If you need row values, name the separate warehouse query tool; these listings inspect metadata. Explain any missing or denied operation without creating replacement resources.


#### Hint


<details>
<summary>Inspect the fully qualified relation in the approved namespace</summary>

The instructor supplies the actual provisioned schema; do not assume training_learner exists remotely.

Pass catalog and schema as distinct arguments where installed help requires them, and use a full table name for metadata inspection. If the expected short name appears twice, compare namespace rather than picking the first row. A permission denial needs an access explanation, not a create/grant command. Preserve the returned metadata category and exact permitted scope.

</details>

#### Check


The retained metadata must identify the actual approved catalog/schema and one permitted fully qualified table, with its observed type and available descriptive fields. Explain how this metadata relates to a dbt source identifier and what further SQL/query access would still need verification. Compare namespace identity rather than only a short table name.

If access is limited, record the exact operation and denied/missing category, preserving any successful independent discovery checks. Do not call a partially visible list proof of complete catalog inventory. Local fixture metadata can support interpretation but cannot close these connected probes. No grants or schema creation are part of the completion evidence.

```bash
databricks schemas list "$DBT_CATALOG" --profile "$V2_DBX_PROFILE" --output json
databricks tables list "$DBT_CATALOG" "$DBT_SCHEMA" --profile "$V2_DBX_PROFILE" --output json
databricks tables get "$V2_DBX_TABLE" --profile "$V2_DBX_PROFILE" --output json
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#databricks-cli-p1-03-reasoning)


---


<a id="databricks-cli-p1-04"></a>

### databricks-cli-p1-04: Filter JSON and explain a limited result


<a id="databricks-cli-p1-04-concept"></a>

#### Concept


JSON output preserves field names and nested structure, making a small selected projection more reliable than visually scanning a long terminal response. The learner should distinguish a response wrapper from its object list and handle an empty list without inventing an error. A filter selecting one qualified table can also return empty because the name or namespace was wrong.

Missing object, denied access and a permitted empty result have different meanings. The installed CLI's exit category and structured response help distinguish them; a blank-looking terminal alone does not. The supplied snapshot offers a stable local interpretation example, while actual cloud observations may differ. Avoid printing entire auth context as a diagnostic shortcut. A useful discovery note retains the selected safe fields and explains what the observation supports and what it cannot establish.


#### Challenge


Use Python's `json` module to inspect `metadata.json` and extract safe object types and fully qualified names. Explain whether the top-level response is a list or an envelope containing a list. Retain the projection and its result.

Apply the same approach to a saved, sanitized connected table listing when available. Inspect an instructor-provided empty, missing or denied example, or a safe permitted probe. Record its category and the next question you would ask. An unmatched name filter, a nonexistent schema and a permission denial have different explanations; do not change grants to manufacture a successful result.


#### Hint


<details>
<summary>Interpret response structure before interpreting absence</summary>

Use json.load and examine whether the CLI output is an envelope object or list before indexing.

Read the top-level type before indexing a response and check for the actual list field. Select safe names/types, not credential fields. Compare a filter that matches the supplied holdings example with one deliberately unmatched name. Keep an empty successful projection distinct from a command that failed because permission or object lookup was denied.

</details>

#### Check


Show the parsed table name training_dev.training_learner.holdings from the fixture. Explain separately what an empty collection and denied access would mean; do not retry by granting yourself privileges.


The local projection must correctly identify the fixture's directory and fully qualified holdings table without changing the snapshot. Retain the filter and result and explain its wrapper/list shape. For actual discovery, retain the command exit/category and safe projected fields, labeling connected or fixture-only evidence accurately.

Explain three distinct cases: permitted empty list, missing requested object and denied access. A generic nonzero status or empty screen cannot substitute for that interpretation. If a live example is unavailable, use the supplied labelled example and keep actual access behavior pending. Do not create or delete an object just to manufacture a probe result.

```bash
python -c "import json; d=json.load(open('metadata.json')); print([t['full_name'] for t in d['tables']])"
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#databricks-cli-p1-04-reasoning)


---


<a id="databricks-cli-p1-05"></a>

### databricks-cli-p1-05: Produce a bounded discovery handoff


<a id="databricks-cli-p1-05-concept"></a>

#### Concept


A discovery handoff makes the inspected environment useful to another learner. It identifies the actual profile/identity, permitted object types and qualified names, relevant metadata and access limitations. A list of commands without interpretation leaves the next person to repeat every probe. Conversely, a claim that the environment is ready can overstate what metadata alone established.

The later dbt route needs a warehouse, approved namespace, loaded sources and usable credentials. CLI discovery contributes identity and object context but does not prove all those execution steps. State the next consumer question, such as which declared holdings relation the prepared pipeline should read, and which separate query/build check remains. This finite phase is read-only and has no advanced provisioning assignment.


#### Challenge


Write `discovery.md` with the identity route, approved catalog/schema/table, workspace distinction, filtered JSON result and one interpreted access limitation. Label each observation connected or fixture-only and keep its command beside the safe result.

Add a specific next question about holdings grain, freshness or source loading for the later dbt route. State what row/query/build check is still needed; metadata alone cannot answer it. Review the note for tokens, unsupported readiness claims and accidental provisioning instructions. Share it through the agreed course review workflow so another learner can follow the evidence without repeating every probe.


#### Hint


<details>
<summary>Turn safe observations into a specific next question</summary>

Use qualified names and omit tokens. A SQL query would require a separately taught API/warehouse boundary.

Organize the note by observed identity, object, meaning, limitation and next check. Keep a command beside the safe result it produced. If an entire boundary is unavailable, say so directly rather than filling its fields from the local fixture. The useful conclusion is a bounded discovery result, not a claim that every data product or permission was verified.

</details>

#### Check


Inspect the note for the intended profile/identity, distinct workspace and catalog objects, approved qualified table, interpreted JSON and explicit access limitation. Each claim must identify actual connected or local-fixture evidence and its command category. Explain what additional row/query/build verification the later dbt journey still requires.

Run read-only phase verification in the prepared environment when available and preserve any blocked probes individually. No credential, broad grant, new schema or deployment belongs in the handoff. Phase two remains not offered. Identify any probe you could not run and the access needed to complete it.

```bash
# From the training root after the supplied profile/object variables are configured.
mise run challenge:v2:verify databricks-cli phase-one-certified --workspace "$DC_CLI_ATTEMPT" --mode live
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#databricks-cli-p1-05-reasoning)


## Phase completion


Submit a bounded discovery note identifying the actual training profile/identity, permitted workspace path, approved catalog/schema and one table's qualified name/type/owner or available metadata. Explain what each object represents and which command/API inspected it. Include a filtered JSON interpretation and one empty, missing or denied example with its correct category. Do not include credential values or imply a metadata listing is a query over table rows.

The supplied metadata fixture supports local practice and expected response interpretation. Actual identity, grants and discovered objects require the prepared Databricks environment; keep them pending when unavailable. This phase offers no advanced assignment and grants no provisioning, deployment or broad access changes. Your handoff gives a consumer or instructor an understandable next question and a safe read-only command rather than a vague statement that everything is accessible. Record actual version/help behavior and source/command hashes so later changes can be rechecked.

---


## Optional stretch


This route has one phase. There is no required stretch or advanced assignment.

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Establish the CLI identity boundary

<a id="databricks-cli-p1-01-reasoning"></a>

<details>
<summary>Reasoning for databricks-cli-p1-01: Measured identity is narrower than data access</summary>

The profile selects context, and the current-user response establishes the observed training identity. Installed help/version establishes executable behavior. Neither grants or proves table access. Local fixtures remain supporting interpretation examples, while missing authentication stays pending. Keep safe identity and command category without recording credential values.

[Return to databricks-cli-p1-01](#databricks-cli-p1-01)

</details>

### Reasoning: Separate workspace and Unity Catalog names

<a id="databricks-cli-p1-02-reasoning"></a>

<details>
<summary>Reasoning for databricks-cli-p1-02: Shared names do not imply shared object semantics</summary>

Workspace path, catalog/schema/table hierarchy and warehouse are different boundaries. Their response types and command groups establish what was inspected. A visible directory cannot prove data permissions or executed SQL, and a fixture name remains an example until connected discovery confirms the actual environment.

[Return to databricks-cli-p1-02](#databricks-cli-p1-02)

</details>

### Reasoning: Inspect permitted schema and table metadata

<a id="databricks-cli-p1-03-reasoning"></a>

<details>
<summary>Reasoning for databricks-cli-p1-03: Qualified metadata discovery is narrower than row querying</summary>

Catalog/schema/full table identity anchors the observed relation. Metadata type/description helps later source mapping but does not establish row access or SQL execution. Permission-filtered visibility is a limitation to explain, not a reason to provision new objects. Keep actual namespace and response category rather than a familiar short name.

[Return to databricks-cli-p1-03](#databricks-cli-p1-03)

</details>

### Reasoning: Filter JSON and explain a limited result

<a id="databricks-cli-p1-04-reasoning"></a>

<details>
<summary>Reasoning for databricks-cli-p1-04: Absence needs structure, exit category and context</summary>

A structured filter reveals selected safe fields and can legitimately return an empty list. Missing or denied operations have different categories. Interpret the response wrapper and intended namespace before inferring that no data exists. Fixture projections teach that logic but do not establish actual cloud access.

[Return to databricks-cli-p1-04](#databricks-cli-p1-04)

</details>

### Reasoning: Produce a bounded discovery handoff

<a id="databricks-cli-p1-05-reasoning"></a>

<details>
<summary>Reasoning for databricks-cli-p1-05: Discovery readiness remains bounded by the probes actually run</summary>

The handoff joins safe identity and qualified object meaning with interpreted limitations and a next consumer question. Metadata is not executed dbt SQL or complete access proof. Local fixtures stay labelled, missing live probes remain pending and the route stays read-only. No invented advanced phase or provisioning action is needed to finish the discovery core.

[Return to databricks-cli-p1-05](#databricks-cli-p1-05)

</details>


---

# databricks-cli independent starter

Read the [owning phase](../README.md) before editing. Prepare from the training project root with `mise run challenge:v2:prepare databricks-cli phase-one-certified`; edit the copied attempt.

## Authored-file list

| Task | Learner-authored paths |
|---|---|
| databricks-cli-p1-01, databricks-cli-p1-02, databricks-cli-p1-03, databricks-cli-p1-04, databricks-cli-p1-05 | `discovery.md`, `evidence.md` |

## Declared baseline

`metadata.json` is a saved example for local interpretation. Create `discovery.md` and `evidence.md` for your observations. Real identity and metadata probes use the instructor-provided profile and resources.

Use a fresh workspace for another attempt; preparation and reset preserve existing work.


---

# databricks-cli: Phase two — not offered

This tool has a foundation route only. Return to the [tool index](../README.md).


---

# airflow challenges

Airflow schedules the same supplied Portfolio Analytics graph used in the dbt projects. The prepared dbt baseline keeps authoring focused on readiness, real worker invocation, quality and run-bound evidence. Foundation work establishes the four-task chain and current scheduled success/failure/repair. Advanced practice develops explicit dates, freshness, bounded retries, replay correctness, worker/auth paths and an incident handoff. A green graph must be connected to independently checked warehouse output.

## Before you start

Prepare an owned attempt through mise in the training project, then inspect actual Astro mounts, worker executable and approved Databricks namespace. Choose a unique prefix/DAG identity and stage only through the helper that refuses an occupied destination. Seed the copied supporting project through the terminal and explicitly handle extraction-time freshness without changing May business dates. Worker credentials resolve at execution through the delivered connection; a terminal login alone is insufficient. Pause only the owned DAG after a bounded rehearsal and preserve evidence before scoped cleanup.

## Suggested timeline and tasks

Estimates include reading, practice, checks and explanation. Allow additional time for environment setup and optional extensions.

| Phase | Task | Minutes |
| --- | --- | --- |
| Foundation | [airflow-p1-01: Inspect a prepared orchestration baseline](phase-one-certified/README.md#airflow-p1-01) | 15–22 |
| Foundation | [airflow-p1-02: Author a small Python DAG with real dbt tasks](phase-one-certified/README.md#airflow-p1-02) | 15–22 |
| Foundation | [airflow-p1-03: Demonstrate the dependency graph and scheduled run](phase-one-certified/README.md#airflow-p1-03) | 15–22 |
| Foundation | [airflow-p1-04: Inspect a controlled task failure](phase-one-certified/README.md#airflow-p1-04) | 15–22 |
| Foundation | [airflow-p1-05: Explain the run and environment boundaries](phase-one-certified/README.md#airflow-p1-05) | 15–22 |
| Advanced | [airflow-p2-01: Define bounded replay and input identity](phase-two-proficient/README.md#airflow-p2-01) | 18–24 |
| Advanced | [airflow-p2-02: Inject failure and observe useful retry behavior](phase-two-proficient/README.md#airflow-p2-02) | 18–24 |
| Advanced | [airflow-p2-03: Prove output correctness after recovery](phase-two-proficient/README.md#airflow-p2-03) | 18–24 |
| Advanced | [airflow-p2-04: Use Astro UI to make an operational decision](phase-two-proficient/README.md#airflow-p2-04) | 18–24 |
| Advanced | [airflow-p2-05: Write a short incident handoff](phase-two-proficient/README.md#airflow-p2-05) | 18–24 |

## Choose your phase

- [Foundation](phase-one-certified/README.md): Foundation core with explicit completion evidence.
- [Advanced](phase-two-proficient/README.md): Independent advanced baseline and finite core, separately timed.

Finish the core tasks before choosing optional stretch.

## Teaching concepts

Schedule interval, business partition and extraction freshness are independent clocks. The tiny dbt build refreshes the complete fixture, while the receipt selects four fund rows for a named May date. Task ordering protects evidence after quality, but real run/task identity and independent values establish execution. Retries must fit their failure category. End-of-phase keys explain cause and recovery; full runnable DAG references stay instructor-only. Optional Cosmos or hosted monitoring has separate prepared-runtime and timing requirements.

## Question-led foundations and further study

Use questions 1–8 alongside the foundation tasks. Questions 9–13 introduce further study.

### Foundations

<a id="airflow-guide-q01"></a>

#### What problem does Airflow solve alongside dbt?

The Portfolio Analytics workflow orders source readiness, transformation/testing and publication evidence. dbt provides the model graph; Airflow controls when and under what conditions it runs. Databricks remains the data execution boundary. A final evidence task records a successful checked handoff and never performs production publication.

<a id="airflow-guide-q02"></a>

#### What are a DAG, task, operator, run and task instance?

The owned DAG is `<prefix>_portfolio_daily`. Its named tasks are source_ready, dbt_build, quality and publication_evidence. The DAG describes dependencies; each scheduled run has a distinct ID, logical date and instances of those tasks. Record their states from the fresh run rather than presenting an unrelated green grid. An operator is the implementation used to execute one task.

<a id="airflow-guide-q03"></a>

#### Which components parse, schedule, execute and record the work?

The terminal prepares files and seeds. Astro mounts data_products into the DAG processor/scheduler/worker path. The scheduler creates timed runs; workers execute tasks; the metadata database records orchestration state; Databricks executes dbt SQL. Inspect the actual compose mount and worker executable. Files visible in your terminal outside that mount are not automatically visible to a worker.

<a id="airflow-guide-q04"></a>

#### How do we define dependencies and pass information?

Wire source_ready >> dbt_build >> quality >> publication_evidence. Pass only a small partition/run identifier, never holdings through XCom. Every task checks the explicit May sample partition while preserving the actual logical date separately. Failure propagates through dependencies, not through a print statement saying the work is ready.

<a id="airflow-guide-q05"></a>

#### What do schedules, logical dates, intervals and catchup mean?

The owned classroom DAG has an explicit two-minute timetable, a timezone-aware start date, catchup=False and one active run. A scheduler-created interval is not the May business date in these historical CSVs. The fixture_partition parameter selects 2026-05-20 or 2026-05-21 explicitly. Record both the logical interval and selected partition. Unpause only this owned DAG during rehearsal and pause it after collecting evidence. A daily production cadence is a separate design choice. Replay the same business date to demonstrate idempotence rather than assuming each scheduler day creates new data. The prepared tiny dbt graph refreshes both fixture dates; the receipt selects four fund rows for the named partition. Do not describe that selection as date-filtered ingestion.

<a id="airflow-guide-q06"></a>

#### What should happen when a task fails or retries?

Bound retries and retry delay for transient connection failures. A deliberately missing FX rate or quality-fault marker must fail quality and block publication_evidence. Use logging-only callbacks. Keep the old accepted receipt unchanged on failure and prove that no receipt was created for the failed run. An auth/config error differs from business-quality failure and should be diagnosed from its first log error.

<a id="airflow-guide-q07"></a>

#### How do reruns and backfills produce correct results?

Replaying a business date reruns the same owned relations and compares their keys/values. Retain run-specific receipts and show which date they represent. A controlled holding correction exercises Delta merge in advanced dbt practice; do not claim a second green task proves idempotence. Restore baseline source data after the drill. Clearing a task is an operational action on a named run, not a repair to its input contract.

<a id="airflow-guide-q08"></a>

#### How do we inspect a run and prove completion?

Keep the current Astro graph/grid/log, exact run/task/attempt IDs, dbt run results and independent warehouse query. The publication receipt binds the contract, fixture partition, source hashes and checked artifacts. API checks compare scheduler-created identities and task states. Parsing or `dag.test()` checks do not establish scheduled worker execution. Use a fresh run to check the scheduler and worker.

<a id="airflow-further-study"></a>

### Further study

Questions 9–13 are separately timed advanced study.

<a id="airflow-guide-q09"></a>

#### How do readiness and freshness differ?

Readiness checks that each supplied raw relation exists with the required columns and population. Freshness checks _extracted_at separately. Historical May timestamps fail a current freshness threshold until an explicit recorded preparation refreshes only ingestion timestamps. A sensor waiting for presence cannot prove freshness. Keep freshness separate from business-date selection and avoid inventing new business rows.

<a id="airflow-guide-q10"></a>

#### How should Airflow orchestrate dbt, and when does Cosmos help?

The prepared PythonOperator route calls the delivered isolated worker dbt executable with explicit project/profile/airflow target and artifact paths. The same Portfolio graph runs as on Wednesday. An optional Cosmos adapter renders that graph using the installed integration, manifest load mode and task-time token env; its APIs and actual worker behavior must be checked on the measured stack. Do not replace dbt with a scaffold print or declare import success as execution.

<a id="airflow-guide-q11"></a>

#### What do Astro Runtime and the CLI add?

Astro supplies the project/image lifecycle around Airflow. Read the delivered Dockerfile and compose override, then inspect actual mounts and versions. The intended dbt executable is /home/astro/.venv/cosmos/bin/dbt. Token delivery uses the prepared databricks_default connection at task time; startup, refresh, expiry and restart are separate checks. A running scheduler does not prove the profile paths or warehouse permissions.

<a id="airflow-guide-q12"></a>

#### How do we test and operate a workflow as a team?

Review source/import checks before scheduling, then run success, intended failure, repair and replay with independent outputs. Keep owned DAG/relation names and cleanup in the handoff. Prove two simultaneous learner attempts do not contaminate one another and removal of one leaves the other intact. Resource provisioning, external alert transports and deployment remain optional/reference work.

<a id="airflow-guide-q13"></a>

#### Can we deliver a workflow and demonstrate recovery?

Present one scheduled success, one intentional quality failure with no premature evidence, and a repaired replay against the same holdings data. Bind logs, receipt, run results, versions and independent query to the contract. Explain the business partition and why task success alone is insufficient. Retain a restart/auth-expiry rehearsal before acceptance; human pacing and UI walkthrough are still required.


---

# airflow: Phase 1 — foundations

## Purpose and outcome

Orchestrate the same Portfolio Analytics product you transformed on Wednesday. Airflow orders source readiness, dbt transformation, quality verification and a publication-evidence step; Databricks still computes and stores the business data. The prepared dbt project prevents this from becoming a second complete modeling exercise. Your authored outcome is a small scheduled workflow whose task relationships and results can be explained.

## Dataset and pipeline

The copied project contains six raw feeds and two supplementary Portfolio Analytics CSVs. The modeled result has four funds on each of two May dates. Each dbt build refreshes the complete tiny fixture graph; the run's explicit business partition selects four fund/date rows for its receipt. This distinction is deliberate: changing a receipt label is not a claim that dbt processed only that date. Logical schedule time and the historical fixture business date are separate concepts.

The four tasks are source_ready, dbt_build, quality and publication_evidence. The readiness task checks raw populations and extraction-time freshness. The build invokes the delivered worker dbt executable. Quality compares actual warehouse output with independent copied-CSV calculations. The last step records checked output for an exact run and partition. A failed quality task must prevent that receipt. Data remains in Databricks; only small control information belongs in task messages.

## Prerequisites and workspace

Use the prepared Astro project, delivered connection setup and approved Databricks namespace. The terminal must have dbt-databricks access and the worker must receive credentials at task execution. Discover actual mounts and executable versions; the terminal's Python environment is not proof of the worker's environment. Set an owned relation prefix and use the matching DAG identifier, generated from that prefix, so simultaneous learners remain isolated.

```bash
mise run challenge:v2:prepare airflow phase-one-certified
cd .local/challenges-v2/airflow/phase-one-certified
export DC_RELATION_PREFIX=dc_alex_air01
```

Run direct dbt preparation inside the copied project subdirectory. Restore or record a timestamp-only extraction refresh before seeding when the supplied historical timestamps are stale; the May business dates must remain unchanged. From the attempt root, use the runtime staging helper with the actual Astro project root. It refuses an existing owned destination and writes ownership metadata needed by the DAG. Never stage into another learner's prefix or assume any terminal directory is mounted into the worker.

## Starter behavior

The DAG file contains deliberate authoring gaps in dbt invocation, publication evidence or dependency wiring. Static compilation checks Python syntax but completion verification rejects these unfinished outcomes. Importing the unstaged file can fail because ownership metadata is not yet available; first prepare the owned stage as documented, then inspect the actual worker import. The dbt project is a disclosed solved baseline. Use it to understand the product and avoid changing its business logic while diagnosing Airflow. Unavailable scheduler, mount or warehouse access remains a pending prerequisite rather than a reason to substitute a local no-op DAG.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 75–110 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [airflow-p1-01: Inspect a prepared orchestration baseline](#airflow-p1-01) | 15–22 | Actual mount/executable identities, owned namespace and supplied-vs-authored inventory |
| [airflow-p1-02: Author a small Python DAG with real dbt tasks](#airflow-p1-02) | 15–22 | Four meaningful tasks with explicit paths, target and actual warehouse checks |
| [airflow-p1-03: Demonstrate the dependency graph and scheduled run](#airflow-p1-03) | 15–22 | Readiness → build → quality → evidence; fresh scheduled task identities |
| [airflow-p1-04: Inspect a controlled task failure](#airflow-p1-04) | 15–22 | Quality failed; evidence upstream_failed; no failed-run receipt; repair succeeds |
| [airflow-p1-05: Explain the run and environment boundaries](#airflow-p1-05) | 15–22 | Coherent handoff links run/task IDs, artifacts and independent fund/date output |

## Core challenges


<a id="airflow-p1-01"></a>

### airflow-p1-01: Inspect a prepared orchestration baseline


<a id="airflow-p1-01-concept"></a>

#### Concept


A DAG definition describes tasks and dependencies; the scheduler decides when a run is due, and a worker executes its task code. The terminal that edits the file is another process boundary. Databricks is yet another boundary, executing dbt SQL remotely. A file visible to the terminal may not be mounted in the worker, and a dbt executable on the terminal path may not exist inside Astro. Diagnosing those differences before writing operators prevents a successful local command from becoming misleading run evidence.

The supplied project contains a complete Portfolio Analytics baseline and a partly authored orchestration file. Its root is discovered relative to the staged DAG, while ownership metadata binds the namespace and relation prefix. For example, the worker must find the staged project directory, its profiles and an artifact directory it can write, not a path copied from your laptop. The same approved warehouse and schema must be reached by terminal seeding and worker transformations. Source presence and a running scheduler do not prove either mount correctness or database permission. The inspection task records those prerequisites explicitly without pretending that setup alone demonstrates orchestration competence.

#### Challenge


Inspect the copied DAG and project before filling its gaps. List the four task responsibilities, the supplied dbt models and the exact learner-authored DAG paths. Read the delivered Astro Dockerfile and compose mount configuration, then record the actual running mount when the prepared environment is available. Identify the intended worker dbt executable, project/profiles directories and artifact locations. Keep measured versions distinct from source-configured expectations.

Prepare the supplied seeds through the terminal's Databricks profile in the project subdirectory and record the approved namespace/prefix used. Stage only this owned attempt into the actual Astro mount using the helper; inspect its ownership metadata without copying token values. Identify what happens if that stage does not exist or uses an already occupied prefix. If Astro or credentials are unavailable, write the source-backed boundary inventory and mark actual mount, worker and warehouse checks pending. Continue reading the prepared graph rather than constructing an unrelated local fixture.

#### Hint


<details>
<summary>Follow the staged path across the worker boundary</summary>

Follow the DAG's root-path expression and the stage helper's output together. The ownership file should agree with the terminal source-loading namespace. Inspect the worker executable inside the actual container rather than assuming a shell activation also affects it. Keep configuration probes separate from secrets: names, paths and redacted identities are useful evidence, while a token is not. A missing mount is a preparation problem, not a SQL defect.

</details>

#### Check


Inspect the actual mount, worker executable/version and owned stage when connected. The stage should contain the copied project, profiles, runtime helper, ownership metadata and writable artifact/evidence locations. Terminal and worker namespace identities must agree, and the raw input counts must match the supplied contract. Record which files are solved supporting assets and which orchestration functions remain unfinished.

Run static compilation locally to identify syntax errors without claiming a worker import or scheduled result. The untouched completion verifier should reject declared DAG gaps rather than accept the prepared dbt project as your solution. Explain why a terminal folder and a running scheduler cannot establish worker visibility, and why two learners need distinct prefixes/DAG identities even inside one approved schema. Retain source-backed paths and measured runtime observations in separate fields. If a probe cannot run, leave that individual prerequisite pending; do not fill it with the intended Dockerfile value.

```bash
python runtime/lab.py static .
# Stage only after the approved namespace and actual Astro root are prepared.
python runtime/lab.py stage-astro . --astro-root "$DC_ASTRO_ROOT"
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#airflow-p1-01-reasoning)


---


<a id="airflow-p1-02"></a>

### airflow-p1-02: Author a small Python DAG with real dbt tasks


<a id="airflow-p1-02-concept"></a>

#### Concept


An operator executes work; the task identifier is only the name Airflow uses to track that execution. A task called dbt_build that prints a message does not build a data product. The prepared PythonOperator route invokes the delivered dbt executable with explicit project, profile, target and artifact paths. Its exit status and artifacts then connect task state to actual Databricks model and test results. Airflow controls ordering while dbt controls the transformation graph.

The publication-evidence step has a narrower classroom meaning than production release. It checks the consumer output, selects the run's four fund/date rows and writes a receipt tied to run identity, input hashes and the shared contract. A successful no-op marker would be insufficient because it could exist without any correct warehouse result. A small partition identifier can be passed between tasks, but holdings data itself stays in Databricks rather than being copied through XCom. This boundary makes the DAG easier to reason about and prevents a green graph from becoming the only evidence of business correctness.

#### Challenge


Complete the declared gaps in the copied DAG's worker function. The build branch must run the actual dbt build with the prepared project/profile directories, airflow target and writable artifact path. The evidence branch must independently check warehouse output, select the configured business date, and write a run-specific receipt under the owned stage. Retain the supplied readiness and quality helpers, reviewing their contracts before changing them.

Use the generated owned DAG identity, timezone-aware start date, two-minute classroom schedule, one active run and explicit fixture partition. Keep catchup disabled for this bounded rehearsal. Set task-time connection templating rather than copying a terminal token into source. Compile the Python file and inspect the worker import after staging. Do not replace the prepared dbt graph with shell echoes or create an external publication operation to make the last task sound more realistic. Document each authored branch and the supplied behavior it relies on.

#### Hint


<details>
<summary>A task name is not evidence that its work executed</summary>

Trace the subprocess command from executable through target and target-path flags. The worker should use its own delivered dbt environment, not the interpreter running the authoring shell. For receipts, use the actual run identifier in the filename and the independently checked partition result in its body. Review the difference between a callback logging a failure and an operator that performs transformation work; they serve different purposes.

</details>

#### Check


Static inspection must show four meaningful task branches and reject any remaining unfinished marker. In the prepared worker environment, verify that the DAG imports with the expected identity and that the dbt command resolves its real executable, project, profiles and artifact directories. Actual execution should produce fresh dbt run results and a warehouse-checked receipt; these runtime outputs remain pending until the scheduler and worker run.

Inspect the receipt contract: exact run identity, fixture partition, shared contract hash, copied input hashes, full eight-key output verification and four selected partition rows. Explain why the whole tiny fixture can be refreshed while the receipt describes one business date, and why that should not be called date-filtered ingestion. Retain a selected command and its output rather than treating a successful Python compilation as dbt execution. The final evidence task must fail instead of writing a receipt when its independent query fails. Keep credentials outside source and logs.

```bash
python runtime/lab.py static .
# In the actual staged worker, inspect the imported DAG and delivered dbt version.
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#airflow-p1-02-reasoning)


---


<a id="airflow-p1-03"></a>

### airflow-p1-03: Demonstrate the dependency graph and scheduled run


<a id="airflow-p1-03-concept"></a>

#### Concept


Dependencies state which task must finish successfully before another becomes eligible. They do not themselves move business data or guarantee that the downstream task reads the right relation. The required chain is readiness, dbt build, quality and publication evidence. This protects the receipt from being created before inputs and results have been checked. Leaving a branch disconnected can make a green task appear even when its upstream product work failed.

A manual trigger and a scheduler-created run can execute the same graph, but they establish different things. The manual run can help diagnose code and logs; only the scheduled run proves the configured timetable, scheduler and worker boundary required here. The schedule's logical date/data interval is not automatically the May business partition. Catchup is disabled and the fixture date is explicit. A prior green UI run may belong to old code or another prefix, so record current DAG/run/task identities and the start of this rehearsal. Both the dependency graph and the actual task state transitions matter.

#### Challenge


Complete the graph wiring in the copied DAG so each task depends on its declared predecessor. Inspect the rendered worker graph after staging and identify how a failed quality task blocks evidence. Use a controlled manual trigger only as supporting diagnosis, retaining its distinct run identity. Then unpause only the owned DAG for a bounded scheduled rehearsal and record a fresh scheduler-created run after your session start.

Inspect readiness, build, quality and evidence task instances in that run. Follow the build log to dbt artifacts and the final receipt to the selected partition output. Confirm the worker is using the current staged source rather than an old imported copy. After collecting the run, pause the owned DAG so the two-minute timetable does not keep generating classroom evidence indefinitely. Do not clear unrelated DAGs, broad date ranges or another learner's tasks to repair a local wiring error.

#### Hint


<details>
<summary>Compare graph edges with the exact current run type</summary>

Read the dependency expression as a sequence of obligations and compare it with the actual graph. An operator can be instantiated without being connected. Check the run type and start timestamp before calling a UI result scheduled evidence. If the expected current task identifiers are missing, inspect staged source and import state before retrying the warehouse. A manual run's success does not answer whether the scheduler produced a new run.

</details>

#### Check


The graph must contain the four required tasks in order, with no evidence task eligible before quality succeeds. For the scheduled run, retain the owned DAG identifier, fresh run identifier, run type, start time and all task states. Its successful dbt artifacts and receipt must correspond to the same run and stage. The full warehouse output contains eight keys; the receipt's selected May partition contains four fund/date rows.

Use the scheduled-evidence command after the controlled failure and repaired runs are available; it checks three distinct scheduler-created identities rather than accepting a historical green graph. Explain the difference between logical schedule interval and explicit fixture business date, and between a manual diagnostic trigger and this acceptance boundary. A missing scheduler/API prerequisite leaves the check pending even if local compilation succeeds. Keep the task-state and product-output evidence linked so a correct SQL query from another attempt cannot satisfy this run's graph evidence.

```bash
mise run challenge:v2:airflow-evidence "$DC_ASTRO_STAGE" --success "$DC_SUCCESS_RUN" --failure "$DC_FAILURE_RUN" --repair "$DC_REPAIR_RUN" --after "$DC_SESSION_STARTED_AT"
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#airflow-p1-03-reasoning)


---


<a id="airflow-p1-04"></a>

### airflow-p1-04: Inspect a controlled task failure


<a id="airflow-p1-04-concept"></a>

#### Concept


A task failure is a state with a cause, not merely a red UI tile. A controlled business-quality fault should fail the quality task after dbt has built its input and prevent downstream evidence. A bad executable path or expired token is a different failure category and should not be counted as the intended quality drill. Reading the first useful log error distinguishes these cases and guides the repair.

The supplied fault marker belongs to your owned stage. While it exists, the quality branch raises its declared teaching failure and the evidence task becomes upstream-failed. The last accepted receipt should remain available, but this failed run must create no new accepted receipt. Removing the marker repairs the controlled cause; rerunning without removing it merely repeats the failure. Retries can repeat transient work, but they cannot turn a permanent business-quality violation into correct data. This small experiment teaches failure propagation and bounded recovery without requiring external alert transports or production deployment.

#### Challenge


After a successful current scheduled run, place the declared quality-fault marker in your owned staged attempt. Wait for or inspect the next fresh scheduled run, then record the quality task's first useful error, task state and downstream evidence state. Confirm there is no receipt for that failed run and preserve the previous successful receipt rather than overwriting it with an ambiguous latest file.

Remove the marker and retain a repaired fresh scheduled run. Compare its warehouse output and partition receipt with the independent baseline expectation. Explain whether retries occurred and why the marker had to be removed for recovery. Keep changes bounded to the copied stage and do not clear unrelated tasks or modify raw fixtures to manufacture a different failure. If a token, path or permission error prevents this sequence, diagnose it as a prerequisite failure and leave the intended quality drill pending.

#### Hint


<details>
<summary>Retain the previous receipt and reject only the failed run</summary>

Name the expected failure message category and task before creating the marker. Inspect the per-run receipt filename instead of relying on whether an evidence directory contains any file. A receipt from the earlier success is legitimate historical evidence for that run; it cannot prove publication for the failed one. Check the upstream-failed downstream state and the quality log together to establish the causal chain.

</details>

#### Check


The failed scheduler-created run must show quality as failed and publication evidence as upstream-failed, with no receipt named for that run. The log should identify the intentional quality marker, not an authentication or missing-file error. After removing the marker, a different fresh scheduled run must succeed and reproduce the expected independent output. Retain the success, failure and repair identities distinctly.

The API evidence checker validates run type, freshness, task states and receipts; inspect the corresponding UI/log readability separately. Explain why repeatedly clearing the quality task without repairing its marker would not recover the workflow, and why a saved successful receipt does not mean the failed run published. Keep source and fixture hashes for the bounded drill so the next reader understands what changed. A no-op callback, a stale green screenshot or a manual local test cannot replace actual scheduled worker failure propagation.

```bash
# Only within the owned stage, create and later remove this teaching marker.
touch "$DC_ASTRO_STAGE/fail-quality"
# Retain the intended failed scheduled run before removing it.
rm "$DC_ASTRO_STAGE/fail-quality"
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#airflow-p1-04-reasoning)


---


<a id="airflow-p1-05"></a>

### airflow-p1-05: Explain the run and environment boundaries


<a id="airflow-p1-05-concept"></a>

#### Concept


Completion evidence connects an executed workflow to a business result a reader can assess. Airflow's run and task identities establish which orchestration instance ran; dbt artifacts identify transformations and tests; an independent warehouse query establishes the intended population and values. None can substitute for all the others. A correct report queried from an old prefix says little about whether your current scheduled worker produced it.

The receipt ties a current run to its selected fixture partition and input hashes, while checking the complete small report. It is useful because the May business date differs from the October timetable. The handoff must distinguish those clocks and explain the build's full-fixture scope. Authentication is another boundary: a terminal login does not automatically make a cached worker connection fresh, and a first successful run does not prove expiry/restart recovery. Describe these unexecuted checks honestly. The classroom evidence step also does not grant consumers access, publish a catalog product or authorize deployment. That narrow meaning avoids overclaiming a successful practice workflow.

#### Challenge


Write a short evidence and incident handoff for your owned attempt. Link the three current scheduled run identities to their task states, useful logs, dbt manifests/run results, independent report comparison and per-run receipts. State the chosen fixture partition, its four selected fund rows, the complete eight-row build scope and the two-minute schedule interval. Include actual worker paths and versions where observed, and source-backed expectations where not measured.

Describe the controlled failure cause, repair and remaining authentication/restart/UI gates. Identify the code you authored and the prepared dbt/helper baseline you used. Provide the owned cleanup boundary and a reviewable DAG diff without deleting shared resources. Compare against the end-of-phase reasoning keys after your attempt and note any instructor-answer exposure. The handoff should let a colleague understand why this result is trusted and what still requires the prepared runtime or a human.

#### Hint


<details>
<summary>Connect identities to business values and remaining checks</summary>

Start with a compact identity chain: owned DAG, current run, task instances, dbt artifacts, input variant and consumer result. Use that chain to find missing evidence rather than listing every terminal command. State the earliest useful failure cause and the precise repair. Keep observed versions and configured paths in different fields; copying a Dockerfile tag into a measured-version field would mislead the next reader.

</details>

#### Check


Inspect the handoff against the actual receipts and API report. Each successful or repaired receipt must name the correct run, contract and fixture partition; the failed run must have none. The report comparison must identify all eight fund/date keys and the selected four-row partition. Check that the DAG was paused after the bounded rehearsal and that cleanup targets only its owned stage and prefixed relations.

Explain why parse, local manual testing, terminal connection and an old green UI do not establish the scheduled worker outcome. State whether token refresh, expiry, restart and two-workspace isolation were actually exercised; leave them pending otherwise. Retain a readable diagnostic log excerpt without secrets and a bounded authored diff. Use the live verifier for API and warehouse checks, then review the corresponding UI and diagnostic excerpt with your instructor.

```bash
# From the training root, assess the owned staged attempt after fresh evidence exists.
mise run challenge:v2:verify airflow phase-one-certified --workspace "$DC_ASTRO_STAGE" --mode live
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#airflow-p1-05-reasoning)


## Phase completion


Complete the foundation with a readable four-task DAG, the declared dependency chain, explicit worker project/profile paths and a fresh scheduled run in the prepared Astro environment. The independent checks must show the complete eight-row fund/date report and the four fund rows selected for the run's named business partition. Retain the actual run and task-instance identities, useful logs, dbt artifacts and a run-bound receipt. Manual execution and syntax compilation remain supporting evidence; they cannot replace the scheduled worker boundary.

Demonstrate one controlled quality failure that blocks publication evidence, remove its cause and retain the repaired scheduled result. Explain which inputs, models and helper functions were supplied and which DAG gaps you authored. Your handoff distinguishes the terminal, scheduler, worker and Databricks warehouse, and states what remains pending about authentication refresh, restart and human UI review. Keep the owned DAG paused after rehearsal and preserve its evidence before cleanup. The receipt is classroom evidence, not production publication or a catalog registration. Do not make an external notification, deployment or another learner's complete project a prerequisite for this core.

---


## Optional stretch


The core completion standard is independent of optional work. No additional stretch is required in this phase; the next phase has an independently prepared entry baseline.

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Inspect a prepared orchestration baseline

<a id="airflow-p1-01-reasoning"></a>

<details>
<summary>Reasoning for airflow-p1-01: Separate configured expectations from observed runtime identities</summary>

The terminal, scheduler, worker and warehouse do different jobs. A useful boundary inventory follows the owned stage into the actual worker mount and verifies executable/profile/artifact paths there. The supplied dbt solution is an input to orchestration practice, not proof of your DAG authoring. An unstaged file may fail import because ownership metadata is absent; a staged file can still fail because its worker executable is wrong. Both are different from a business-quality failure and need distinct observations.

[Return to airflow-p1-01](#airflow-p1-01)

</details>

### Reasoning: Author a small Python DAG with real dbt tasks

<a id="airflow-p1-02-reasoning"></a>

<details>
<summary>Reasoning for airflow-p1-02: Operators must connect task state to actual product work</summary>

The build branch executes the real prepared dbt graph on Databricks. Quality and evidence read independently specified warehouse results rather than trusting the task name. The receipt binds the current run to its selected business-date result while explaining that this tiny build refreshes the full fixture. A no-op publication marker or a copied terminal token would break those boundaries. Static and import checks are prerequisites; fresh worker artifacts and output establish the executed behavior.

[Return to airflow-p1-02](#airflow-p1-02)

</details>

### Reasoning: Demonstrate the dependency graph and scheduled run

<a id="airflow-p1-03-reasoning"></a>

<details>
<summary>Reasoning for airflow-p1-03: Graph structure and scheduled identity prove different obligations</summary>

The required edges ensure checked readiness precedes transformation and checked quality precedes evidence. A disconnected evidence task defeats that guard. Manual execution is useful diagnosis, but the scheduled run proves the timetable and worker boundary. Its exact task identities, artifacts and receipt must agree with the owned stage and current session. The May business partition is explicit and independent of the schedule interval. Pausing only the owned DAG preserves other learners and ends the bounded rehearsal.

[Return to airflow-p1-03](#airflow-p1-03)

</details>

### Reasoning: Inspect a controlled task failure

<a id="airflow-p1-04-reasoning"></a>

<details>
<summary>Reasoning for airflow-p1-04: Recovery repairs the cause and retains per-run evidence</summary>

The quality marker creates a known business-gate failure. It should block only that run's publication evidence while preserving the previous successful receipt. Removing the marker repairs the cause; a fresh repaired run then needs independent output verification. An expired token or wrong path may also fail a task, but does not establish this intended drill. Task state, useful log and receipt identity together show the propagation and recovery rather than merely documenting red then green colors.

[Return to airflow-p1-04](#airflow-p1-04)

</details>

### Reasoning: Explain the run and environment boundaries

<a id="airflow-p1-05-reasoning"></a>

<details>
<summary>Reasoning for airflow-p1-05: Evidence must identify both executed work and its limits</summary>

A coherent handoff joins current run/task identities to dbt artifacts and independently checked warehouse values. It states the distinction between fixture partition, complete build scope and schedule interval. The controlled quality failure and repaired run need separate receipts and causal explanation. Worker auth, restart, isolation and human readability are additional checks, not conclusions inferred from a first success. Classroom publication evidence does not perform production publication. Recording these limits makes the result reviewable without hiding unfinished acceptance work.

[Return to airflow-p1-05](#airflow-p1-05)

</details>


---

# airflow independent starter

Read the [owning phase](../README.md) before editing. Prepare from the training project root with `mise run challenge:v2:prepare airflow phase-one-certified`; edit the copied attempt.

## Authored-file list

| Task | Learner-authored paths |
|---|---|
| airflow-p1-01 | `evidence.md` |
| airflow-p1-02, airflow-p1-03, airflow-p1-04 | `dags/portfolio_daily.py`, `evidence.md` |
| airflow-p1-05 | `evidence.md`, `incident.md` |

## Declared baseline

These focus files are intentionally unfinished: `dags/portfolio_daily.py`. Supporting models and profiles are supplied. Complete the listed files, then verify their output in the required Databricks or Astro environment.

Keep `evidence.md` beside the copied project. Create a named file when its task asks for it. Use a fresh workspace for another attempt; preparation and reset preserve existing work.


---

# airflow: Phase 2 — advanced practice

## Purpose and outcome

Develop the four-task Portfolio workflow into a bounded recovery and handoff exercise. The prepared entry includes the solved dbt product, readiness helper and task scaffold so advanced work can start without another learner's foundation answer. You author the missing gate/recovery/evidence behavior and demonstrate why the repaired result is correct. Check source freshness and worker authentication while investigating recovery.

## Dataset and pipeline

The eight supplied Portfolio CSVs remain the only business inputs. Four funds on each of two May dates produce eight report keys. Each dbt build refreshes that full teaching graph; the run's explicit partition determines four selected fund/date rows in its receipt. Supported partitions are 20 and 21 May 2026. Reject another date instead of silently substituting the latest input. Schedule intervals are current operational time; business dates and extraction freshness are independent clocks.

Readiness checks population and extraction timestamp; build invokes the actual worker dbt executable; quality validates the independent report and a controlled teaching fault; evidence writes a run-bound receipt only after success. A stale input or a missing raw relation fails readiness, while a quality marker fails the quality gate. A token or path error belongs to another category. The incident note must explain which category occurred and why the selected repair addresses it.

## Prerequisites and workspace

Use the approved training container and Astro project, delivered connection/refresh setup and single provisioned Databricks namespace. Prepare an independent advanced copy and choose a unique owned prefix. Inspect the staged worker paths instead of copying an old terminal directory into an operator. The runtime helper requires ownership metadata and writes only this attempt's stage. Credential values remain task-time inputs, never saved in receipts or source.

```bash
mise run challenge:v2:prepare airflow phase-two-proficient
cd .local/challenges-v2/airflow/phase-two-proficient
export DC_RELATION_PREFIX=dc_alex_air02
```

Provisioning, image builds and unplanned access delays are instructor preparation outside the core estimate. Record measured managed versions and source-backed expectations separately. Set a rehearsal start timestamp and retain exact fresh scheduled run IDs so old accepted recordings cannot masquerade as evidence for the changed DAG. The actual scheduler/API/UI and warehouse are needed to finish this exercise; unavailable boundaries remain pending while authoring, parsing and fixture calculations proceed locally.

## Starter behavior

The advanced starter contains declared unfinished DAG behavior and a complete supporting dbt baseline. Completion verification rejects those gaps. Static Python compilation is useful without credentials, but importing an unstaged file may fail because the owned metadata has not been generated. Stage through the helper after configuring the actual namespace and mount. Historical extraction timestamps need an explicit recorded timestamp-only refresh before a current freshness gate can pass; business dates and values remain unchanged. Do not weaken a stale-source assertion to make the teaching input look current.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 90–120 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [airflow-p2-01: Define bounded replay and input identity](#airflow-p2-01) | 18–24 | Supported May partition, explicit schedule interval and reproducible source readiness |
| [airflow-p2-02: Inject failure and observe useful retry behavior](#airflow-p2-02) | 18–24 | Known quality/readiness cause, observed attempts and no premature receipt |
| [airflow-p2-03: Prove output correctness after recovery](#airflow-p2-03) | 18–24 | Eight unique report keys, four partition rows, stable values across repeated input |
| [airflow-p2-04: Use Astro UI to make an operational decision](#airflow-p2-04) | 18–24 | Exact graph/grid/log identities, causal diagnosis and observed repair decision |
| [airflow-p2-05: Write a short incident handoff](#airflow-p2-05) | 18–24 | Current success/failure/repair/replay chain, reviewable diff and explicit pending gates |

## Core challenges


<a id="airflow-p2-01"></a>

### airflow-p2-01: Define bounded replay and input identity


<a id="airflow-p2-01-concept"></a>

#### Concept


Replay asks a workflow to repeat work for an identified business input, so correctness depends on more than the new run's timestamp. The scheduler interval describes when Airflow created work; the fixture partition describes which business-date result the receipt presents. The copied graph refreshes both supplied dates, and its output check must still select the declared partition explicitly. A current run can therefore describe historical holdings without claiming that old holdings were newly generated.

Readiness has two separate conditions: the declared raw population exists, and extraction timestamps meet the freshness promise for this rehearsal. A presence sensor alone cannot establish freshness, while a fresh timestamp alone cannot establish complete rows. The supplied May timestamps intentionally reveal that distinction. A documented timestamp-only refresh changes ingestion observation time but keeps fund/date keys and valuations unchanged. The run must reject an unsupported business date rather than silently attach an empty or latest result. Those explicit contracts prevent a green replay from referring to the wrong input or a receipt that only relabels yesterday's evidence.

#### Challenge


Implement or review the run's supported fixture-partition validation, logical interval recording and readiness checks. Keep the two supported May dates explicit. List the six raw populations and extraction-time fields checked before transformation. Record a controlled timestamp-only preparation with its actual observation time when current freshness needs it, then seed the copied inputs into the owned namespace.

Stage the advanced attempt and execute each supported date in a bounded rehearsal, retaining the selected partition rows in its receipt. Demonstrate an unsupported date being rejected for that input-contract reason. Also demonstrate a stale or missing source failing readiness and repair the actual copied input cause before continuing. The full fixture build scope stays explicit; do not claim per-date ingestion filtering that the supplied models do not implement. Keep date identity, source variant and scheduler-created run identity together in the evidence note.

#### Hint


<details>
<summary>Separate business identity from extraction and schedule clocks</summary>

Write the three clocks in separate fields: business position date, extraction observation time and Airflow logical interval. Inspect the readiness function before deciding which one a stale-input warning refers to. The helper's timestamp refresh records what it changed; compare input hashes and business keys afterward. For partition selection, verify all four receipt rows carry the requested May date rather than relying on the receipt's text label.

</details>

#### Check


For each supported partition, expect four fund/date receipt rows and independently correct values from the complete eight-row report. The unsupported date must fail validation, not produce a successful empty receipt. A stale or missing input must fail the source-readiness obligation before the build task is accepted. After the recorded refresh or source restoration, the same raw counts and May business keys should remain and readiness should recover.

Retain the source hashes, preparation timestamp, failed readiness category, repaired result and fresh run identities. Explain why relabeling a receipt cannot prove that the selected data changed and why a timestamp-only refresh does not create new holdings observations. Inspect the actual warehouse sources when connected; local CSV inspection proves only the copied inputs. Leave scheduled/API and freshness execution pending when those boundaries are unavailable. Do not disable catchup or freshness in an undocumented way merely to make a current screen green.

```bash
# From the copied project subdirectory; use a real recorded ISO8601 observation time.
python ../runtime/lab.py restore . --observed-at "$DC_OBSERVED_AT"
dbt seed --project-dir . --profiles-dir . --target local --full-refresh
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#airflow-p2-01-reasoning)


---


<a id="airflow-p2-02"></a>

### airflow-p2-02: Inject failure and observe useful retry behavior


<a id="airflow-p2-02-concept"></a>

#### Concept


Retry policies express a belief about which failures might disappear without changing business inputs. A transient connection interruption can merit a bounded retry; a missing required FX observation or a deliberate quality marker requires repair. Retrying the latter only repeats the violated contract. The task log, attempt identity and delay reveal what happened; a final state alone cannot explain whether retry was useful.

The prepared classroom default uses a bounded retry and a short delay, with logging-only failure callbacks. Keep those controls within the rehearsal window rather than introducing unlimited waits. The callback observes a failure; it must not swallow the operator exception or write an accepted publication receipt. With one active run and a two-minute schedule, an unrepaired fault can affect a later scheduled run as well, so pause or bound the owned rehearsal while collecting evidence. Compare a readiness failure with a quality failure to show where the graph stops. Both should block downstream accepted evidence, but their causes and repair locations differ.

#### Challenge


Review the retry and delay configuration in the copied DAG and state which failure category it is meant to address. Add the declared controlled quality marker in your owned stage, observe the affected task's attempts and useful error, and retain the downstream blocked state. Implement missing quality/evidence behavior without turning callbacks into hidden transformation or release logic.

Remove the marker and retain a repaired fresh scheduled run. For a separate readiness drill, use only a copied stale/missing input and explain why restoring or refreshing that input repairs readiness. Record whether a retry succeeded, exhausted its bound or simply repeated an unrepaired fault. Keep the DAG and date range bounded to your prefix, and avoid broad task clearing. An expired OAuth token may need connection refresh and worker checks rather than an SQL change; identify that as a prerequisite/auth failure if it occurs.

#### Hint


<details>
<summary>Use retries for the failure category they can repair</summary>

Predict the task, error category, expected attempt count and downstream state before injecting the fault. Look for the first meaningful exception in the task log, then compare attempt identifiers and delay rather than reading the final UI color alone. A callback that logs and returns should not change the failed operator's result. Repair the marker or source cause before deciding whether clearing a named task is a useful recovery action.

</details>

#### Check


The quality-marker drill must show the intended quality failure, bounded retry behavior and publication evidence blocked for that run. No receipt may be written for the failed run, even if an earlier accepted receipt remains in the directory. After repairing the marker, a fresh scheduled success must produce the independent expected partition result. For readiness, retain a distinct failure cause and graph stopping point.

Record run/task/attempt identities, useful log excerpts, observed timing, repair and final output checks. Explain why retrying permanent missing data does not produce valid data and why a logging callback cannot be accepted as a release gate. A token failure or malformed path is not evidence of the intended quality drill; separate that diagnosis. Human readability and notification design remain distinct from task-state assertions. If the scheduler cannot execute here, retain the prepared failure contract and leave observed attempts and timing pending rather than inventing a retry story.

```bash
# Only the owned staged attempt receives this controlled fault.
touch "$DC_ASTRO_STAGE/fail-quality"
# Retain the failed task/attempt evidence, then repair its actual cause.
rm "$DC_ASTRO_STAGE/fail-quality"
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#airflow-p2-02-reasoning)


---


<a id="airflow-p2-03"></a>

### airflow-p2-03: Prove output correctness after recovery


<a id="airflow-p2-03-concept"></a>

#### Concept


Recovery is successful when the workflow's repaired result satisfies its business contract. A later green run could still read stale relations, duplicate a date or select another learner's output. Independent key/value checking establishes what the consumer actually receives. The shared contract and owned prefix bind the query to the staged attempt; the receipt binds it to a run and business partition.

Replaying identical copied input should preserve the complete eight-key report and the selected four-row partition result. Distinct runs may write distinct evidence files while producing identical business values; that is expected, not duplicate business data. Replaying the other May date should produce a different selected partition without erasing the first run's receipt. The supplied tiny graph rebuilds the fixture, so this exercise proves repeatable checked output rather than every possible incremental/backfill algorithm. The dbt advanced route demonstrates the separate Delta correction transition. Explain that limit instead of calling two green tasks a general exactly-once guarantee.

#### Challenge


After repairing the intended failure, retain a fresh scheduled run and independently query its owned report. Compare all fund/date keys and values against copied-CSV calculations, then verify the four selected partition rows in its receipt. Replay the same supported date with unchanged input and compare business results while retaining distinct run identities.

Run the second supported partition and confirm its selected receipt changes date without removing the earlier receipt or the full report's other keys. Preserve source hashes and dbt artifacts so a reviewer can tell whether input was actually identical. Do not compare a warehouse relation from a previous prefix or use a stale target directory as current output evidence. If you also choose the optional controlled holdings correction, use its modified independent oracle and label it separately from baseline replay. Restore the copied fixture after that additional drill.

#### Hint


<details>
<summary>Distinct run receipts can describe identical correct data</summary>

Compare sorted business projections rather than receipt filenames: filenames should differ for distinct runs, while unchanged-input data should agree. Check both key membership and values so an offsetting numeric error cannot hide loss. The selected partition field must match every receipt row's date. Inspect source hashes alongside the replay result to establish that the repeated input was actually unchanged.

</details>

#### Check


Expect the baseline report to retain eight unique fund/date keys after repaired execution and identical-input replay. The chosen partition has four fund rows with matching values in each accepted receipt. Distinct run identifiers remain distinct evidence files, while the failed run still has no accepted receipt. The second May partition should select its own four rows without erasing the first run's evidence.

Use the current scheduled API checker and independent warehouse comparison, then retain the before/after projections and input hashes. Explain why a repeated build does not itself prove incremental merge correctness and why an unchanged grand total does not prove unchanged membership. A local compilation or copied instructor output cannot establish the current worker result. Record the actual artifact freshness and run identities, with any unavailable service check pending. This result is a bounded classroom repeatability demonstration, not a claim about concurrent writers, production backfill or distributed exactly-once processing.

```bash
mise run challenge:v2:airflow-evidence "$DC_ASTRO_STAGE" --success "$DC_SUCCESS_RUN" --failure "$DC_FAILURE_RUN" --repair "$DC_REPAIR_RUN" --after "$DC_SESSION_STARTED_AT"
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#airflow-p2-03-reasoning)


---


<a id="airflow-p2-04"></a>

### airflow-p2-04: Use Astro UI to make an operational decision


<a id="airflow-p2-04-concept"></a>

#### Concept


An operational screen is useful when it helps answer a decision, not when it merely looks green. The graph shows dependencies, the grid shows run/task state over time, and a task log shows the causal error and attempt. These views need the exact owned DAG and fresh run identity. A bookmarked old run can look convincing while describing different code, inputs or namespace.

For the controlled marker, the decision is to remove the known fault and rerun a bounded owned scope, not clear every task or change warehouse grants. For expired credentials, the decision concerns delivered connection refresh and worker token resolution, not replacing business values. For missing mounted files, inspect the worker path. The API validates machine-readable identities and states; human review assesses whether the corresponding UI and logs are understandable and safe to present. Neither automatically establishes auth expiry/restart behavior. A short operational note should explain the chosen action and its evidence so another learner can distinguish diagnosis from trial-and-error clicking.

#### Challenge


Open the prepared Astro UI at the exact owned DAG and current success, failure and repair runs. Inspect graph, grid and the quality failure log, retaining useful run/task/attempt identifiers and a redacted diagnostic excerpt. Compare those views with the API evidence report and receipt files. State what the first useful error implies and choose a bounded repair action that addresses that cause.

Inspect the actual worker project/profile/executable path and task-time connection boundary for any auth or file-location issue. In the prepared environment, rehearse delivered refresh and restart behavior and confirm the worker still reaches the approved namespace. Keep two active learner stages isolated if that check is available. Record any unavailable runtime check and its prerequisite. Do not use an old recording as evidence for newly authored sources.

#### Hint


<details>
<summary>Use the exact failed run to select a causal repair</summary>

Begin with the run ID from the API report and navigate to that run rather than the DAG's latest overview. Compare the task log's attempt with the task-instance entry. If the error mentions credentials or an executable path, inspect the corresponding boundary before editing SQL. A useful screenshot or excerpt includes enough identity to locate the current run while excluding secrets and irrelevant browser context.

</details>

#### Check


The graph/grid/log evidence must bind the same fresh owned run identities checked by the API. The quality failure should be explained by the marker and its repaired run by marker removal plus correct warehouse output. Record a bounded recovery action and why it was appropriate, including any task clearing scope actually used. The UI cannot replace independent report values, and an API pass cannot replace human readability review.

For auth/restart or simultaneous-workspace checks, retain measured worker/namespace identity before and after the action; otherwise leave that individual check pending. Explain why a successful terminal seed does not prove worker token freshness and why broad cleanup would risk another learner. If capturing a screen, keep current run identifiers visible and perform authentication outside recording. The instructor can review the incident decision locally from prepared evidence contracts, but actual UI and worker recovery require the approved environment. Do not assign a guessed installed version to a measured field.

```bash
# Inspect the exact API-verified run in Astro; worker/UI behavior is a live check.
mise run challenge:v2:verify airflow phase-two-proficient --workspace "$DC_ASTRO_STAGE" --mode live
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#airflow-p2-04-reasoning)


---


<a id="airflow-p2-05"></a>

### airflow-p2-05: Write a short incident handoff


<a id="airflow-p2-05-concept"></a>

#### Concept


An incident handoff explains impact, cause, action and evidence of recovery so someone else can decide what to do next. In this classroom pipeline the impact is blocked publication evidence for a named fixture partition, not a claimed production outage. The cause must be the observed marker, readiness, auth or path condition; vague statements such as Airflow was broken do not guide a successor.

The handoff also states ownership: which DAG, stage and prefixed warehouse relations belong to this attempt and how cleanup preserves others. A prepared Cosmos or hosted observability route can be useful optional depth, but does not become a missing mandatory deployment step. The finite core demonstrates an understandable data result, intended failure and recovery. Distinguish configured behavior from the recovery you actually observed. A good note names the remaining checks and their exact environment without replacing them with reassuring prose.

#### Challenge


Write an incident note covering the chosen consumer question and fixture partition, exact current run/task identities, controlled failure cause, downstream blocked receipt, bounded repair and independently verified replay. Link relevant logs, API report, dbt artifacts, copied input hashes and selected partition receipts. Include the authored DAG diff and identify supplied supporting models and helper code.

Document terminal/worker paths, approved namespace/prefix, actual versions, task-time credential delivery and cleanup boundaries. State whether auth expiry/refresh, restart/reconnect, two learners and human UI/timing review ran; keep each absent observation pending. Pause only the owned DAG and restore copied baseline inputs after the drill. Provide a next-step checklist that is specific enough for another instructor to resume without creating extra schemas or deleting shared resources. Compare reasoning keys after your own attempt and disclose any prior answer exposure.

#### Hint


<details>
<summary>Write the smallest handoff that proves cause and recovery</summary>

Use a short causal sequence rather than a terminal diary: observed impact, first useful error, targeted repair, independent recovered output and remaining checks. Anchor each claim to its run or artifact. If a sentence says everything passed, replace it with the actual checks and pending boundaries. Keep cleanup as owned resources and explicit reviewable statements instead of an unrestricted delete command.

</details>

#### Check


Inspect the note against the current artifacts: successful and repaired receipts exist for distinct runs, the failed run has none, business values agree independently, and replay preserves the declared keys. The note must explain full-fixture build scope, selected four-row partition evidence and current schedule interval without conflating them. Confirm the owned DAG is paused and cleanup cannot target another prefix.

Retain the current source/contract hashes and separate status for authored source, local static checks, connected execution and human acceptance. List any authentication, restart or isolation check that remains to run. A complete incident narrative cannot compensate for missing actual execution evidence, but it can make prepared local work reviewable. Full runnable solutions belong in the instructor package. No production promotion, external notification, infrastructure provisioning or publication is part of this core handoff.

```bash
# Inspect owned cleanup statements; do not execute broad deletion.
cd "$DC_ASTRO_STAGE/project"
python ../runtime/lab.py cleanup-sql .
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#airflow-p2-05-reasoning)


## Phase completion


The advanced core ends with a demonstrated operational decision, not merely a running Astro screen. Retain fresh scheduled success, intended quality failure, repaired success and a bounded replay of the same business partition. Link each run to task states, useful logs, current dbt artifacts and independent warehouse results. Show that failed quality created no accepted receipt and that replay did not duplicate or erase the declared product population. Explain how the full tiny fixture refresh differs from the selected four-row partition evidence.

Submit the authored DAG, incident note, source/contract hashes, owned namespace and stage identity, and a short reviewable diff. Record actual worker executable/profile/mount and task-time authentication observations. Exercise restart, token expiry/refresh and simultaneous learners only in the prepared environment; leave each unexecuted check pending here. Restore the copied source variant and pause the owned DAG after rehearsal. Cleanup must preserve another learner's stage, DAG and relations. The fixed core is complete only when its business evidence and explanation agree; optional Cosmos, hosted alerts, monitoring configuration and deployment remain separately timed reference work.

---


## Optional stretch


The core completion standard is independent of optional work. Choose a separately timed route from [the stretch guide](stretch/README.md).

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Define bounded replay and input identity

<a id="airflow-p2-01-reasoning"></a>

<details>
<summary>Reasoning for airflow-p2-01: A replay must identify its business input independently</summary>

The run's timetable and May input partition are different clocks. Readiness checks both presence/population and extraction freshness, while the selected receipt rows prove which business date the consumer evidence describes. Refreshing copied extraction timestamps is a recorded preparation change, not a new holdings history. Unsupported partitions must fail explicitly. The full tiny fixture refresh remains the build contract; partition evidence cannot be presented as unimplemented date-filtered ingestion.

[Return to airflow-p2-01](#airflow-p2-01)

</details>

### Reasoning: Inject failure and observe useful retry behavior

<a id="airflow-p2-02-reasoning"></a>

<details>
<summary>Reasoning for airflow-p2-02: A bounded retry cannot repair a permanent contract violation</summary>

The marker deliberately fails quality, so retries repeat the same known error until the cause is removed. Evidence must show attempts and downstream blocking rather than infer them from a final state. Readiness failures occur earlier and have different repairs. A callback can log a failure without converting it into success. Keep failed-run receipt absence separate from the preserved earlier receipt, and use actual scheduled attempts to establish behavior instead of a hypothetical retry configuration.

[Return to airflow-p2-02](#airflow-p2-02)

</details>

### Reasoning: Prove output correctness after recovery

<a id="airflow-p2-03-reasoning"></a>

<details>
<summary>Reasoning for airflow-p2-03: Business idempotence and run identity are different observations</summary>

A replay creates a distinct orchestration identity but should leave unchanged-input business keys and values stable. The receipt files therefore differ while their selected partition result agrees. Checking all eight report keys detects lost dates or duplication; checking four selected rows proves partition meaning. The supplied rebuild route establishes bounded repeatability, while Delta merge and correction behavior belong to a separately observed dbt exercise. Keep these claims distinct and preserve failed-run receipt absence.

[Return to airflow-p2-03](#airflow-p2-03)

</details>

### Reasoning: Use Astro UI to make an operational decision

<a id="airflow-p2-04-reasoning"></a>

<details>
<summary>Reasoning for airflow-p2-04: The UI supports a decision tied to a current causal error</summary>

Graph, grid and logs describe different aspects of the same run. Identity binding prevents old or unrelated evidence from passing as current. The marker requires a bounded marker repair, while auth and path failures require their own boundary diagnoses. Machine states and human readability are complementary. Worker refresh/restart and two-workspace isolation need measured before/after observations; neither follows automatically from a green run or a terminal login.

[Return to airflow-p2-04](#airflow-p2-04)

</details>

### Reasoning: Write a short incident handoff

<a id="airflow-p2-05-reasoning"></a>

<details>
<summary>Reasoning for airflow-p2-05: A reviewable handoff preserves evidence and states what remains</summary>

The incident note should connect observed cause to bounded repair and independently checked recovery. It identifies owned resources, copied input state and current run/artifact hashes. Source authoring, static checks, scheduler/warehouse execution and human review have separate statuses. Pausing the owned DAG ends the rehearsal without disrupting another learner. Optional integrations remain separately scoped, and no classroom evidence receipt implies production promotion or publication.

[Return to airflow-p2-05](#airflow-p2-05)

</details>


---

# airflow independent starter

Read the [owning phase](../README.md) before editing. Prepare from the training project root with `mise run challenge:v2:prepare airflow phase-two-proficient`; edit the copied attempt.

## Authored-file list

| Task | Learner-authored paths |
|---|---|
| airflow-p2-01, airflow-p2-03 | `dags/portfolio_daily.py`, `evidence.md` |
| airflow-p2-02 | `dags/portfolio_daily.py`, `incident.md`, `evidence.md` |
| airflow-p2-04 | `incident.md`, `evidence.md` |
| airflow-p2-05 | `incident.md`, `evidence.md`, `dags/portfolio_daily.py` |

## Declared baseline

These focus files are intentionally unfinished: `dags/portfolio_daily.py`. Supporting models and profiles are supplied. Complete the listed files, then verify their output in the required Databricks or Astro environment.

Keep `evidence.md` beside the copied project. Create a named file when its task asks for it. Use a fresh workspace for another attempt; preparation and reset preserve existing work.


---

# Historical airflow extension

The earlier extension is retained in the separate instructor archive and authoring workspace. Its setup and claims require review before reuse; it is outside the current learner assignment.

Earlier SLA and readiness statements describe a different runtime. A static check does not establish scheduled success, worker access, publication or production readiness.

Use the [current advanced phase](../README.md) for the supported tasks, independently prepared baseline and evidence checks. Ask the instructor to select any additional historical exercise.

<a id="v2-airflow-phase-two-proficient-stretch-readme-md-airflow-optional-stretch-selection"></a>
<a id="v2-airflow-phase-two-proficient-stretch-readme-md-full-legacy-advanced-reference"></a>
<a id="v2-airflow-phase-two-proficient-stretch-readme-md-phase-2-production-operations"></a>
<a id="v2-airflow-phase-two-proficient-stretch-readme-md-challenge-1-the-vendor-neutral-alert-transport"></a>
<a id="v2-airflow-phase-two-proficient-stretch-readme-md-challenge-2-tiered-failure-alerting-page-on-p1-notify-on-p2"></a>
<a id="v2-airflow-phase-two-proficient-stretch-readme-md-challenge-3-the-p2-and-p3-tiers-sla-miss-and-retry"></a>
<a id="v2-airflow-phase-two-proficient-stretch-readme-md-challenge-4-wire-the-callbacks-and-the-sla-into-the-dag"></a>
<a id="v2-airflow-phase-two-proficient-stretch-readme-md-challenge-5-the-source-freshness-gate-as-a-contract"></a>
<a id="v2-airflow-phase-two-proficient-stretch-readme-md-challenge-6-the-monitoring-config"></a>
<a id="v2-airflow-phase-two-proficient-stretch-readme-md-challenge-7-the-runbook-and-the-consumer-guide"></a>
<a id="v2-airflow-phase-two-proficient-stretch-readme-md-challenge-8-structural-tests-for-the-dag"></a>
<a id="v2-airflow-phase-two-proficient-stretch-readme-md-challenge-9-stretch-the-paved-path-databrickssubmitrunoperator-variant"></a>
<a id="v2-airflow-phase-two-proficient-stretch-readme-md-challenge-10-capstone-a-complete-production-ready-dag"></a>
<a id="v2-airflow-phase-two-proficient-stretch-readme-md-phase-2-summary"></a>


---

# kafka challenges

Kafka is an optional event-bridge clinic with a prepared broker, consumer and processing runtime. It teaches event meaning, partition/offset progress, run identity, checked output and a bounded replay policy. The retained small A/B/C fixture and local processing chain are distinct from assigned Databricks Portfolio work. Completing this clinic cannot replace the required dbt/Airflow evidence, and skipping it cannot block the mandatory capstone.

## Before you start

The instructor supplies the allocated bootstrap address, topic/group, bridge interpreter and isolated processing runtime. Prepare a copied optional attempt through mise and inspect actual versions and resource ownership. Do not point experimental records at a production broker or share another learner's consumer group. Broker/image preparation stays outside the timed core. A port collision or unavailable engine is a prerequisite condition, not the intended contract rejection. The valid event JSON and allowed immutable fixture location can be inspected locally while actual broker/run checks remain pending.

## Suggested timeline and tasks

Estimates include reading, practice, checks and explanation. Allow additional time for environment setup and optional extensions.

| Phase | Task | Minutes |
| --- | --- | --- |
| Foundation | [kafka-p1-01: Read the dataset-arrived contract](phase-one-certified/README.md#kafka-p1-01) | 12–18 |
| Foundation | [kafka-p1-02: Start the prepared local broker and inspect a topic](phase-one-certified/README.md#kafka-p1-02) | 12–18 |
| Foundation | [kafka-p1-03: Produce and follow a uniquely identified event](phase-one-certified/README.md#kafka-p1-03) | 12–18 |
| Foundation | [kafka-p1-04: Verify the dbt output belongs to the event](phase-one-certified/README.md#kafka-p1-04) | 12–18 |
| Foundation | [kafka-p1-05: Replay and explain duplicate policy](phase-one-certified/README.md#kafka-p1-05) | 12–18 |

## Choose your phase

- [Foundation](phase-one-certified/README.md): Optional clinic; mandatory course work does not depend on it.
- [Advanced](phase-two-proficient/README.md): Not offered: no tasks or completion gate.

Finish the core tasks before choosing optional stretch.

## Teaching concepts

Producer acknowledgement, consumer offset and downstream receipt describe different progress. Event identity/version/location must agree across broker, bridge and actual run/output. An identical completed replay can reuse a run under the supplied bounded policy; same identity with changed content is a conflict. This is not a general distributed exactly-once guarantee. Reasoning keys follow the owning phase, full runnable bridge references remain separate, and the optional clinic's runtime boundary is stated without borrowing assigned Databricks acceptance.


---

# kafka: Phase 1 — foundations

## Purpose and outcome

Explore how a dataset-arrived event can trigger a prepared processing workflow without making the event the dataset itself. This is an optional event clinic. You inspect a contract, use a supplied broker/consumer bridge, follow event identity into an actual run/output and reason about replay. The bridge and processing baseline are prepared so learners do not need to build Kafka infrastructure, author a complete consumer and repeat dbt/Airflow labs in one phase.

## Dataset and pipeline

The event contains event identifier, type, dataset identifier/version, controlled fixture location and arrival timestamp. The small immutable holdings fixture produces exposure A 150, B 100 and C zero. This retained event fixture is intentionally separate from the assigned eight-seed Portfolio Analytics pipeline. Its prepared local Airflow/DuckDB chain demonstrates event identity and offset semantics; it cannot establish Databricks/Astro completion for the assigned guides.

Kafka retains records in an ordered partition log, and a consumer group tracks progress through offsets. The supplied bridge validates allowed input identity/location, triggers the prepared DAG and records partition/offset/run evidence. A receipt and actual data check establish downstream completion separately from producer acknowledgement. Identical completed replay can reuse the same run, while a conflicting payload with the same event identity is rejected according to the declared bounded policy.

## Prerequisites and workspace

The instructor supplies the prepared broker, unique topic/group, bridge interpreter and isolated Airflow/dbt runtime. Inspect actual installed versions rather than copying source pins into measured evidence. Use version-explicit mise preparation from the training project root and keep event/evidence edits inside the copied attempt. Image pulls, broker setup and port allocation belong to preparation outside the unpiloted clinic estimate.

```bash
mise run challenge:v2:prepare kafka phase-one-certified
cd .local/challenges-v2/kafka/phase-one-certified
python -m json.tool event.json
```

Record the approved bootstrap address and owned topic/group. Do not point an experiment at a production broker or consume a shared group's offsets. The prepared local port may already be occupied; diagnose that ownership/preparation condition rather than stop an unknown service. The runtime path and bridge flags should be inspected through delivered help. No hosting account, infrastructure deployment or mandatory capstone dependency is introduced.

## Starter behavior

The event JSON is valid and the supporting processing graph is supplied. A starter parse/contract validation can succeed before any broker or workflow runs. It is not a completion pass. Keep learner event edits separate from the immutable baseline and never execute an arbitrary producer-provided filesystem path. Broker absence, port collision or missing runtime is a prerequisite failure, while malformed or conflicting event identity is an intentional contract rejection described by its task.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 60–90 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [kafka-p1-01: Read the dataset-arrived contract](#kafka-p1-01) | 12–18 | Valid unique event and predicted small-fixture output without arbitrary path execution |
| [kafka-p1-02: Start the prepared local broker and inspect a topic](#kafka-p1-02) | 12–18 | Current intended topic/partition metadata in prepared isolated broker |
| [kafka-p1-03: Produce and follow a uniquely identified event](#kafka-p1-03) | 12–18 | Event ID, broker partition/offset and current Airflow run identity |
| [kafka-p1-04: Verify the dbt output belongs to the event](#kafka-p1-04) | 12–18 | Matching event/run receipt and independent A 150, B 100, C 0 output |
| [kafka-p1-05: Replay and explain duplicate policy](#kafka-p1-05) | 12–18 | Completed run reused, output unchanged; conflicting payload rejected without accepted duplicate |

## Core challenges


<a id="kafka-p1-01"></a>

### kafka-p1-01: Read the dataset-arrived contract


<a id="kafka-p1-01-concept"></a>

#### Concept


An event describes an occurrence and the input it refers to; it does not carry every row of that dataset. Identity supports tracing and replay decisions, version identifies the expected fixture semantics, and location is a controlled reference rather than permission to execute an arbitrary path. The arrival timestamp describes event context, not automatic proof of processing completion.

The bridge validates the small fixture contract before it triggers work. A valid record can therefore be accepted as input while its downstream run remains pending. Reusing an event identifier with a different payload changes its meaning and must be rejected under the declared policy. Kafka's retained log and consumer offsets track broker progress; they are separate from a receipt that says the data result was checked. Keeping those boundaries explicit prevents a syntactically valid JSON event from becoming a false end-to-end pass.


#### Challenge


Inspect `event.json` and create `learner-event.json`, changing only `event_id` to your unique value. Retain `dataset_id` holdings, version `fixture-v1` and location `fixture://holdings-v1`. Explain what each field identifies and predict the A/B/C exposure output.

Validate your copy using the supplied bridge and retain the validator result in `evidence.md`. Keep the baseline event unchanged. A location is a controlled input reference, not permission to execute a host path. Explain how arrival time differs from processing completion and why another payload under an accepted event ID tests a conflict rule rather than a fresh trace.


#### Hint


<details>
<summary>Validate input meaning before following its execution</summary>

The supplied pipeline accepts exactly this prepared dataset contract. Kafka is optional and does not gate mandatory Airflow/capstone.

Compare your event with the validator's allowed dataset/version/location contract. A new event ID is appropriate for a new trace; changing a payload under an already accepted identity tests a different rule. Inspect validation output without assuming its run identifier means a run actually exists. Arrival time and processing state should remain separate evidence fields.

</details>

#### Check


The learner-event copy must parse and pass the declared contract validator, with a unique identity and allowed fixture reference. Retain the predicted A/B/C exposure values and explain why the event is not the holdings dataset itself. A malformed location or unsupported version must be rejected for that contract reason rather than executed.

Validation output is supporting input evidence only. It cannot prove producer delivery, consumer progress, Airflow execution or dbt output. Record those downstream boundaries as pending until their tasks execute. Keep canonical input bytes and any deliberate invalid-event copy separate so the valid baseline can be reproduced.

```bash
python -m json.tool learner-event.json
# From the training root, inspect the delivered bridge interface.
python3 scripts/v2_kafka_bridge.py --help
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#kafka-p1-01-reasoning)


---


<a id="kafka-p1-02"></a>

### kafka-p1-02: Start the prepared local broker and inspect a topic


<a id="kafka-p1-02-concept"></a>

#### Concept


A Kafka topic contains partition logs: ordered lanes of retained records. Each record has an offset, its position in that lane. A consumer group maintains its own progress. Two groups can consume retained records independently, but two learners accidentally using the same group can affect each other's observed offset progression. Topic/group ownership is therefore part of the classroom setup rather than an optional naming preference.

A broker metadata response establishes that the intended topic/partition is reachable. It does not mean an event was produced or a workflow completed. The prepared local runtime keeps infrastructure work outside this short clinic. A port collision or missing container engine is a setup condition; it should not be repaired by deleting unrelated services. The learner's task is to inspect the actual allocated boundary and explain its role.


#### Challenge


Use the instructor-prepared broker, bootstrap address and allocated topic/group. From the copied starter, start only this clinic's Compose project when needed, then run the bridge's topic preparation and metadata inspection through the supplied runtime interpreter.

Retain the topic, partition and group identity before producing a record. Confirm the Compose project and local port belong to your attempt. Wait for broker readiness and distinguish an unreachable broker from an absent allocated topic. Resolve collisions with the instructor instead of stopping an unknown service. Explain what the metadata response establishes and which later producer/consumer observations are still needed.


#### Hint


<details>
<summary>Inspect the allocated log and group boundary before producing</summary>

The compose broker binds localhost:19092. Instructor preparation includes image pull and the isolated Airflow deployment.

Compare the bootstrap port and Compose project ownership before diagnosing a connection failure. A metadata response should identify the allocated topic, not merely any topic in the broker. Keep group identity separate from topic name. The bridge's preparation action may create the owned topic but does not publish a dataset-arrived record.

</details>

#### Check


The current broker metadata must return the intended owned topic and partition without an error. Retain bootstrap/topic/group identity and measured runtime context. Explain what remains unproven: record delivery, consumer processing and data output. A source Compose file or successful JSON parse is not broker readiness.

If the local port is occupied or engine unavailable, record that exact prerequisite and leave broker observations pending rather than removing an unknown service. Topic inspection must not use a shared production consumer group. The finite optional clinic assumes prepared infrastructure and does not assess broad provisioning.

```bash
# Inspect actual bridge/broker metadata using the allocated topic and group.
# Use the prepared runtime interpreter and supplied --bootstrap/--topic flags.
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#kafka-p1-02-reasoning)


---


<a id="kafka-p1-03"></a>

### kafka-p1-03: Produce and follow a uniquely identified event


<a id="kafka-p1-03-concept"></a>

#### Concept


Producer acknowledgement means the broker accepted a record at a partition/offset. It does not mean a consumer processed it or a downstream data job succeeded. The supplied bridge reads the event, validates its input contract and triggers the prepared Airflow run with a deterministic identity. Its evidence records broker position and the corresponding run so those boundaries can be traced.

Consumer offset progress also has a policy: acknowledging or committing a consumed record can occur before downstream success, depending on the bridge contract. The learner must inspect that behavior rather than call every committed offset completed data. A uniquely identified event avoids confusing a current trace with a prior record already retained in the topic. Actual task states and receipts provide later execution evidence.


#### Challenge


Use the supplied bridge to produce `learner-event.json` to the allocated topic, then consume one record with your assigned group. Retain the producer acknowledgement's partition/offset and the bridge's decision and Airflow run ID.

Follow that exact run in the prepared processing runtime until it completes or reaches the supplied wait bound. Keep event JSON, bridge evidence and run identity together. Compare the run configuration with the consumed payload rather than inspecting any latest green DAG. Explain whether consumer progress was committed before downstream completion, and what a pending or failed run means for recovery. Do not execute producer-provided paths.


#### Hint


<details>
<summary>Link broker position to the exact downstream run</summary>

The bridge uses the instructor-configured Airflow CLI inside the runtime boundary; keep broker/Airflow reachability explicit.

Read the producer acknowledgement and consumer evidence as two different records. Follow the event identifier and deterministic run ID into the actual prepared Airflow runtime. A producer's successful exit says only what its acknowledgement reports. If the run is pending, retain that state and wait within the supplied bound instead of calling the chain complete.

</details>

#### Check


Retain the produced event identity, broker partition/offset, consumer decision and actual matching Airflow run. The event fields must agree across those artifacts. Inspect eventual task state and mark it pending until execution finishes; a successful producer command alone cannot close this task's chain observation.

Explain whether the supplied bridge commits consumer progress before or after downstream acceptance, and what a pending/failed run means for recovery. Use the owned topic/group and bounded wait. Missing broker or processing runtime remains a blocked prerequisite, while a malformed event rejection should retain its specific cause. Do not fabricate a receipt to make the trace look complete.

```bash
# Inspect the exact event-evidence.json and its identified prepared Airflow run.
python -m json.tool event-evidence.json
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#kafka-p1-03-reasoning)


---


<a id="kafka-p1-04"></a>

### kafka-p1-04: Verify the dbt output belongs to the event


<a id="kafka-p1-04-concept"></a>

#### Concept


An event-driven result must be associated with the input event that selected it. Correct-looking fund totals from a previous run or another fixture are not sufficient. The receipt should bind event payload and run identity, while independent dbt output checking confirms the controlled fixture's per-fund values and population. A shared grand total cannot reveal values shifted between funds.

This optional clinic deliberately uses the small A/B/C fixture and local prepared chain. Its evidence must not be presented as the assigned Databricks Portfolio product. The independent reference protects both fund membership and native fixture values. A zero-valued C holding still belongs to the expected population, so dropping it because it contributes nothing to a sum would change the output contract. Trace identity and business values together.


#### Challenge


After the event-triggered run completes, inspect `receipt.json` and compare its event ID, version, location and run ID with the produced record and `event-evidence.json`. Query the copied processing database or use the supplied output checker.

Verify all three fund rows: A 150, B 100 and C zero, with total exposure 250. Keep C in the population even though it adds nothing to the sum. Retain the per-fund comparison and explain which artifact identifies input, execution and checked output. Use this run's project/output path so a database from an earlier attempt cannot supply misleadingly correct values.


#### Hint


<details>
<summary>Verify event identity and each fund value independently</summary>

Use the supplied expected-output oracle and the event metadata, not just a successful task state.

Compare the complete event payload, not only its ID, with the receipt. Then compare per-fund output rather than an overall 250 total. The C row's zero value is a membership obligation. Inspect the exact project's output path and run identity so a retained database from a prior attempt cannot provide apparently correct evidence.

</details>

#### Check


The actual receipt and bridge evidence must agree on the event payload and run ID, and the current prepared dbt output must show A 150, B 100 and C zero with all three keys retained. Retain independent per-fund checks and actual run/task completion. A producer acknowledgement or a manually written JSON receipt does not satisfy the chain.

Explain why the zero-valued fund remains part of the expected result and why a grand sum alone is weaker. State the local optional fixture execution boundary honestly; it cannot close assigned Databricks/Astro acceptance. Keep missing runtime or pending run states explicit, and preserve baseline source bytes throughout the check.

```bash
# Inspect the prepared run receipt and invoke the delivered verify-chain interface.
python -m json.tool receipt.json
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#kafka-p1-04-reasoning)


---


<a id="kafka-p1-05"></a>

### kafka-p1-05: Replay and explain duplicate policy


<a id="kafka-p1-05-concept"></a>

#### Concept


Replay policy defines how retained records are interpreted when the same event is seen again. The supplied bridge can reuse an identical completed run when its receipt matches the event payload. A record with the same event identity but changed payload is a conflict, not a new legitimate input under that policy. The broker can assign a later offset while the bridge reuses the prior run.

This is a bounded teaching strategy based on a matching completed receipt, not a general exactly-once guarantee. An existing run without a matching completed receipt needs explicit recovery inspection, and concurrent events or a broader deduplication store introduce additional design questions. The learner should explain those limits rather than claiming that a successful replay solved all distributed failure modes. Business output stability and run reuse are separate checks.


#### Challenge


Produce the identical valid event again and consume it through your allocated group. Inspect completed-run reuse, the new broker offset and unchanged per-fund output. Retain the accepted receipt before the replay.

In a separate event copy, change a payload field while retaining `event_id`. Predict and inspect the conflicting-payload rejection and its offset behavior. Keep the accepted receipt and baseline event unchanged. Explain what recovery requires if an earlier run exists without a matching completed receipt. After saving both experiments, remove only the clinic's named Compose project when instructed; broad pruning would affect unrelated resources.


#### Hint


<details>
<summary>Replay depends on matching completed meaning, not ID alone</summary>

The bridge commits offsets only after an accepted/new-or-identical run. A conflict remains uncommitted for operator diagnosis.

Inspect the complete accepted receipt before replay so the reuse precondition is real. A later broker offset does not require another data run when the policy accepts identical completed replay. For the conflict, change only a declared payload field under the same identity and predict rejection. An incomplete prior run is a separate recovery state, not permission to fabricate a matching receipt.

</details>

#### Check


Identical completed replay must retain the same run identity and unchanged A/B/C output while recording the new broker position and reuse decision. The conflicting-payload copy must be rejected for the intended identity/content reason according to the documented offset policy. No accepted conflicting run or overwritten baseline receipt may appear.

Explain what happens if the earlier run exists without a matching completed receipt and why this bounded strategy is not distributed exactly-once processing. Retain input/receipt hashes and both decisions. Clean only owned topic/group/Compose resources after preserving evidence. Offline event validation remains supporting; actual replay and rejection through broker/bridge/runtime stay pending without the prepared environment.

```bash
# Inspect replay evidence and compare it with the retained accepted receipt.
python -m json.tool event-evidence.json
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#kafka-p1-05-reasoning)


## Phase completion


This optional clinic completes with a uniquely identified dataset-arrived record, observed broker partition/offset, the actual prepared Airflow run, a matching receipt and independently checked fixture output. The local event fixture expects fund exposure A 150, B 100 and C 0; it is a separate event-bridge clinic, not the assigned Portfolio Analytics Databricks product. Retain an identical-event replay that reuses the completed run and preserves output, plus a conflicting-payload rejection with the stated offset policy.

Explain producer acknowledgement, consumer offset and downstream completion as separate observations. The supplied bridge is bounded and its completed-receipt policy does not establish distributed exactly-once behavior or arbitrary concurrent event deduplication. Use the instructor-provided topic/group/runtime and clean only the owned clinic resources after preserving evidence. Offline JSON validation is supporting input evidence; the broker, actual Airflow and dbt chain remain pending without their prepared runtime. Kafka is optional everywhere and phase two is not offered. Mandatory dbt/Airflow/Atlas completion never depends on this clinic.

---


## Optional stretch


This route has one phase. There is no required stretch or advanced assignment.

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Read the dataset-arrived contract

<a id="kafka-p1-01-reasoning"></a>

<details>
<summary>Reasoning for kafka-p1-01: Event validation is not downstream completion</summary>

Identity and controlled dataset/version/location establish which input the event means. The validator must reject arbitrary locations and conflicting semantics. A computed run ID is a trace identifier, not proof that a run exists. Broker delivery, consumer offset and independently checked output are later separate observations.

[Return to kafka-p1-01](#kafka-p1-01)

</details>

### Reasoning: Start the prepared local broker and inspect a topic

<a id="kafka-p1-02-reasoning"></a>

<details>
<summary>Reasoning for kafka-p1-02: Broker readiness is narrower than event or workflow success</summary>

Topic metadata establishes the allocated broker/log boundary. Group identity controls this learner's progress and should not be shared accidentally. It does not establish production or downstream completion. Missing engine/port/topic preparation stays a specific prerequisite condition, and only owned clinic resources may be started or cleaned.

[Return to kafka-p1-02](#kafka-p1-02)

</details>

### Reasoning: Produce and follow a uniquely identified event

<a id="kafka-p1-03-reasoning"></a>

<details>
<summary>Reasoning for kafka-p1-03: Acknowledgement, offset and run state describe different progress</summary>

The broker's partition/offset proves accepted record position. The bridge maps that record to an actual run, while task state indicates execution progress. Offset commit policy does not automatically imply checked data completion. Retain matching event fields and current identities, leaving pending runs visible rather than turning producer success into an end-to-end claim.

[Return to kafka-p1-03](#kafka-p1-03)

</details>

### Reasoning: Verify the dbt output belongs to the event

<a id="kafka-p1-04-reasoning"></a>

<details>
<summary>Reasoning for kafka-p1-04: Correct values need a matching input and execution identity</summary>

The receipt ties the full event to its run, and independent per-fund output confirms the selected fixture. C remains a valid zero-valued member. Correct totals from another project or manually authored receipts do not establish the chain. This optional local clinic has its own evidence boundary and cannot substitute for the main Databricks route.

[Return to kafka-p1-04](#kafka-p1-04)

</details>

### Reasoning: Replay and explain duplicate policy

<a id="kafka-p1-05-reasoning"></a>

<details>
<summary>Reasoning for kafka-p1-05: Bounded duplicate handling has explicit preconditions and limits</summary>

An identical payload with a matching completed receipt can reuse the prior run despite a later broker offset. Same identity with different content is rejected. Existing incomplete work needs another recovery decision, and this simple receipt strategy is not a general exactly-once solution. Compare business values as well as run reuse and preserve the accepted baseline evidence before owned cleanup.

[Return to kafka-p1-05](#kafka-p1-05)

</details>


---

# kafka independent starter

Read the [owning phase](../README.md) before editing. Prepare from the training project root with `mise run challenge:v2:prepare kafka phase-one-certified`; edit the copied attempt.

## Authored-file list

| Task | Learner-authored paths |
|---|---|
| kafka-p1-01, kafka-p1-02, kafka-p1-03, kafka-p1-04, kafka-p1-05 | `learner-event.json`, `evidence.md` |

## Declared baseline

`event.json` is the valid baseline. Create `learner-event.json` with a unique event ID and keep your explanation in `evidence.md`. The bridge generates `event-evidence.json` and the completed workflow generates `receipt.json`; inspect these outputs without editing them.

Use a fresh workspace for another attempt; preparation and reset preserve existing work.


---

# kafka: Phase two — not offered

This tool has a foundation route only. Return to the [tool index](../README.md).


---

# capstone challenges

The Atlas capstone connects a consumer question to source, domain and consumer-aligned models using the supplied client/portfolio/trade dataset. Its cents, basis-point fees and trade-active population differ from Portfolio Analytics. Foundation teams author a meaningful trade/report slice with independent population and value checks. Advanced teams complete a finite performance/leaderboard/region core and demonstrate an omitted-contribution defect and repair before choosing additional depth.

## Before you start

Prepare an independent owned attempt through mise with the delivered Databricks adapter and approved single catalog/schema. Keep artifacts inside the copied container project rather than assume a governed Volume mount. Agree producer, consumer and creator/reviewer roles and state output grain/population before coding. Supporting dimensions, latest prices and positions are disclosed baseline assets. Advanced has its own completed-baseline starter. Record actual runtime identities and retain supplied input hashes; credentials and instructor runnable solutions stay outside learner output and presentation evidence.

## Suggested timeline and tasks

Estimates include reading, practice, checks and explanation. Allow additional time for environment setup and optional extensions.

| Phase | Task | Minutes |
| --- | --- | --- |
| Foundation | [capstone-p1-01: State the consumer population and grain](phase-one-certified/README.md#capstone-p1-01) | 18–24 |
| Foundation | [capstone-p1-02: Build the valid-trade domain fact](phase-one-certified/README.md#capstone-p1-02) | 18–24 |
| Foundation | [capstone-p1-03: Author the active portfolio summary](phase-one-certified/README.md#capstone-p1-03) | 18–24 |
| Foundation | [capstone-p1-04: Investigate expected omission and a defective join](phase-one-certified/README.md#capstone-p1-04) | 18–24 |
| Foundation | [capstone-p1-05: Prove minimum data quality and give a consumer handoff](phase-one-certified/README.md#capstone-p1-05) | 18–24 |
| Advanced | [capstone-p2-01: Build a meaningful performance report](phase-two-proficient/README.md#capstone-p2-01) | 18–24 |
| Advanced | [capstone-p2-02: Rank advisor books with explicit ties](phase-two-proficient/README.md#capstone-p2-02) | 18–24 |
| Advanced | [capstone-p2-03: Build the regional rollup from its declared dependency](phase-two-proficient/README.md#capstone-p2-03) | 18–24 |
| Advanced | [capstone-p2-04: Reconcile independently and reject a defect](phase-two-proficient/README.md#capstone-p2-04) | 18–24 |
| Advanced | [capstone-p2-05: Present a fixed completed core and select stretch](phase-two-proficient/README.md#capstone-p2-05) | 18–24 |

## Choose your phase

- [Foundation](phase-one-certified/README.md): Foundation core with explicit completion evidence.
- [Advanced](phase-two-proficient/README.md): Independent advanced baseline and finite core, separately timed.

Finish the core tasks before choosing optional stretch.

## Teaching concepts

Source→domain→consumer alignment connects representation, business entities and report meaning. Retained identifiers and explicit population protect against silent row loss. Cents, basis-point fees, signed positions, weighted rates and dense ties need independently checked semantics. The active report legitimately excludes no-qualifying-trade portfolios; wrong-key loss does not. Nominal native-unit money is a fixture limitation. Reasoning keys stay phase-owned and full runnable answers instructor-only; optional extensions have their own dependencies and cannot blur the fixed core.

Review the product through the consumer role as well as its SQL implementation. A report with plausible totals can still hide wrong population, shifted advisor ownership or mislabeled units. The presentation should trace one actual key through the declared relationships and demonstrate an assertion that rejects a meaningful defect. Preserve the unsuccessful diagnostic alongside repaired output so trust is explained rather than asserted.


---

# capstone: Phase 1 — foundations

## Purpose and outcome

Create an Atlas data product that an advisor or consumer can understand. This capstone applies Wednesday's grain, source/ref and independent checks to a distinct supplied client/portfolio/trade dataset. It is not a renamed Portfolio Analytics pipeline: Atlas stores trade prices in cents, fees in basis points and signed position quantities through buy/sell activity. Your team authors a bounded valid-trade fact and an active-portfolio report while prepared models supply supporting dimensions, latest prices and positions.

## Dataset and pipeline

Seven exact supplied CSVs describe trades, portfolios, clients, advisors, instruments, funds and fund holdings. The raw trade feed has ten thousand rows. The declared domain filter keeps positive quantity and price and recognized buy/sell side, yielding 9,880 valid trades. Those trades produce 3,717 portfolio/instrument positions and a report for 1,028 portfolios. The conformed portfolio dimension contains 2,500 rows, so 1,472 portfolios have no qualifying trade participation and do not appear in this trade-driven report.

Source-aligned models retain provenance and normalize input representation; domain-aligned models express reusable business entities; consumer-aligned reports answer a declared question. Keys carry the relationships between these layers. Price cents become decimal units and fee basis points become a fraction of traded value. No FX conversion is supplied, so cross-currency totals are explicitly nominal fixture aggregates. Net signed quantity can be negative; do not confuse that with a raw trade quantity failing the positive-quantity rule.

## Prerequisites and workspace

Open the training project in the supplied dev container, complete the delivered Databricks identity setup and use the approved single catalog/schema. Prepare an independent capstone attempt through mise and choose an owned relation prefix. Keep your team worksheet, contract and evidence in the copy. The starter uses container-safe local artifact paths rather than assuming a Unity Catalog Volume is mounted in the terminal.

```bash
mise run challenge:v2:prepare capstone phase-one-certified
cd .local/challenges-v2/capstone/phase-one-certified
export DC_RELATION_PREFIX=dc_team_atlas01
dbt debug --project-dir . --profiles-dir . --target local
```

Assign a producer, consumer and creator/reviewer role, then agree the report question and output population before writing SQL. The independent advanced baseline is available later; do not copy a completed instructor report over your own work. Record actual adapter and namespace identities, supplied files and any unavailable warehouse/orchestration prerequisite. Keep auth outside recording and tokens out of the team notes.

## Starter behavior

The trade fact and portfolio summary contain declared unfinished outcomes. The prepared supporting graph is disclosed baseline work, not evidence of your team's authoring. Source seeding and project parsing can run before every authored model is complete, while completion verification rejects placeholders. A broad build may fail on those named gaps; select the relevant supplied upstream models while developing. The CSV oracle can inspect expected populations locally, but it cannot prove loaded warehouse relations or executed joins. Restore any copied diagnostic variant before your final baseline evidence.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 90–120 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [capstone-p1-01: State the consumer population and grain](#capstone-p1-01) | 18–24 | Contract distinguishes 2,500 conformed portfolios from 1,028 trade-active report rows |
| [capstone-p1-02: Build the valid-trade domain fact](#capstone-p1-02) | 18–24 | 9,880 valid rows from 10,000 raw; retained trade/key identities and correct cents/bps arithmetic |
| [capstone-p1-03: Author the active portfolio summary](#capstone-p1-03) | 18–24 | 3,717 positions roll up to 1,028 portfolio keys with independent AUM/fee/count values |
| [capstone-p1-04: Investigate expected omission and a defective join](#capstone-p1-04) | 18–24 | 1,472 expected exclusions identified; deliberate client/advisor key mistake loses population |
| [capstone-p1-05: Prove minimum data quality and give a consumer handoff](#capstone-p1-05) | 18–24 | Authored slice, independent populations/values, clear limitation and reviewable presentation |

## Core challenges


<a id="capstone-p1-01"></a>

### capstone-p1-01: State the consumer population and grain


<a id="capstone-p1-01-concept"></a>

#### Concept


A consumer report needs a population as well as a row grain. One row per portfolio describes the shape of output, but does not say whether every known portfolio or only those with qualifying activity should appear. Atlas's core report is driven by valid trades and their resulting positions. A conformed portfolio with no qualifying trade participation can legitimately be absent under that contract. It should not silently disappear if the consumer expected an all-portfolio inventory.

The supplied fixture makes this distinction measurable: 2,500 conformed portfolios, 1,028 with qualifying trade-derived output, and 1,472 without it. Keys remain important even for omitted populations because an anti-join must identify exactly which portfolios are absent and why. Source→domain→consumer alignment connects that business meaning to transformations. For example, cents become decimal price units before position valuation, and a portfolio's advisor key connects to the advisor dimension. A diagram without the correct keys or units cannot protect against a plausible but wrong join. State the intended question and relationship before deciding how many tables to build.

#### Challenge


Write a small consumer contract and source-to-target mapping in the copied team project. State the consumer question, one-row-per-portfolio grain, active-by-qualifying-trade population, retained identifiers and money/fee units. List the seven supplied CSVs and trace trades through the valid domain fact and prepared positions into the summary. Identify the prepared supporting models and the two focus models your team authors.

For the opening team discussion, choose at least two possible business-facing outputs and work backwards from their consumers and decisions to sources and rules in plain English. Record a producer–creator–consumer map, a consumer-backwards map, a source-to-target mapping for four to six fields, and a shared glossary with trust questions in your team evidence note. Include price cents, fee basis points, valid trades, latest prices and the lack of FX conversion. Assign facilitator, scribe, quality challenger and playback roles, combining them for a small team. Use the separate 30–60 minute discovery timebox; then choose the trade-active portfolio summary as the finite implemented core. Keep the second output as a discussed candidate, and revisit the opening assumptions in your final handoff.

Inspect the source key relationships between portfolios, clients, advisors and instruments. Choose one portfolio and follow its identifiers through the supplied dimension files. State whether no-trade portfolios should be reported as absent or with an explicit empty status for this core; use the declared trade-active route for the assessed result, and describe the all-portfolio variant separately. Record the fixture's native-currency aggregation limitation and avoid importing the Portfolio Analytics GBP or synthetic NAV assumptions into Atlas.

#### Hint


<details>
<summary>State population separately from one-row-per-portfolio grain</summary>

Begin with the consumer's question and write population and grain on separate lines. Then identify the key that carries each relationship. Compare the raw/conformed portfolio inventory with trade-derived membership before selecting a join style. A null-filled all-portfolio result would be a different contract, not an automatic repair for a trade-active report. Keep prices in cents and fees in basis points until the mapping states their conversion.

</details>

#### Check


Inspect the team contract for an explicit consumer, population, grain, identifiers, units and limitation. Run the independent reference locally to establish the supplied fixture expectation, then compare warehouse populations when connected. Expect 2,500 conformed portfolios, 1,028 reported active portfolios and 1,472 without qualifying trade-derived output. Do not treat the difference as missing identifiers without inspecting membership.

Retain the chosen portfolio's source relationship trace and the authored-versus-supplied model inventory. Explain why an all-portfolio inventory needs a different population contract and why a single row count cannot reveal a wrong advisor join. The source-to-target mapping should identify the conversion from cents and basis points rather than merely list table names. Local CSV arithmetic and a drafted contract are useful preparation, while actual conformed/consumer warehouse counts remain pending until the model graph executes. This task establishes the intended meaning against which later SQL is assessed.

Check that the opening worksheet records two candidate consumer outputs, all four mapping/glossary sections and the team's assumptions. Explain why discussing a second output does not silently expand the assessed SQL scope. Compare those assumptions with the implemented result during the final playback.

```bash
python runtime/lab.py reference . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p1-01-reasoning)


---


<a id="capstone-p1-02"></a>

### capstone-p1-02: Build the valid-trade domain fact


<a id="capstone-p1-02-concept"></a>

#### Concept


A domain fact defines which raw observations represent valid business activity and how their values are expressed. Atlas keeps trades with positive quantity and price and a recognized buy/sell side. That rule excludes 120 of the ten thousand raw rows in this fixture. Retaining trade, portfolio and instrument identifiers allows the consumer and quality checks to trace that selection instead of relying on an unexplained reduction in count.

Price cents must be divided by one hundred to obtain decimal currency units. Fee basis points are divided by ten thousand when applied to traded value. For a simple worked example, two units at 12,500 cents create 250 currency units of traded value; a twenty-basis-point fee is 0.50 units. Multiplying by twenty as a percentage would be wrong by orders of magnitude. Buy and sell are directions used later for signed position quantity; a raw sell trade can have positive quantity and remain valid. A nonnegative test on derived signed net position would therefore enforce the wrong contract. Types, units and filters must be explained together.

#### Challenge


Complete the valid-trade domain SQL in the copied focus file. Read the supplied source-aligned trade relation, apply the declared quantity/price/side rules, retain the business identifiers and timestamp, and compute decimal price, traded value and fee using the documented conversions. Keep the sell direction explicit for downstream signed aggregation instead of changing valid raw quantity into an unexplained negative value.

Build the supplied upstream source slice and the authored trade fact, then inspect raw rows excluded by each rule. Record the independent raw/valid populations and a manually calculated trade-value/fee example from the actual copied CSV. Add or review the test that protects trade-key uniqueness, required relationships and valid population. Do not remove rows merely because a later portfolio summary is incomplete, and do not make the model's own count its only expected oracle.

#### Hint


<details>
<summary>Check filter rules and money units as separate obligations</summary>

Separate selection from arithmetic in readable CTEs so a failed population and a failed value can be diagnosed independently. State the units beside each derived expression. Inspect a valid sell and an invalid quantity or price row to confirm the intended filter. A decimal conversion should happen before money aggregation, not after a large integer or floating-point computation has already lost the intended meaning.

</details>

#### Check


Expect ten thousand raw trades and exactly 9,880 valid domain trades, with retained unique trade identifiers and no invented portfolio or instrument keys. Compare the selected key set with the independent CSV filter rather than only comparing counts. Inspect the chosen actual trade and reproduce its decimal value and fee manually. The price conversion is cents to currency units; the fee conversion is basis points to a fraction of traded value.

Retain the selected build/test artifacts, excluded-rule summary and independent value check. Introduce a bounded copied invalid side or quantity case only if you can predict its intended exclusion and restore it afterward. Explain why a valid sell can retain positive raw quantity and why the signed position aggregation is a different downstream rule. The final baseline must preserve the original supplied input hashes. A parsed model or correct-looking sample is insufficient until the warehouse population and values are checked against the independent contract.

```bash
dbt build --select +dom_trading__trade --project-dir . --profiles-dir . --target local
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p1-02-reasoning)


---


<a id="capstone-p1-03"></a>

### capstone-p1-03: Author the active portfolio summary


<a id="capstone-p1-03-concept"></a>

#### Concept


A portfolio summary aggregates positions at portfolio grain, then attaches the client and advisor context through the declared portfolio relationships. Positions are at portfolio/instrument grain, so several positions can contribute to one report row. Aggregating or joining at the wrong key can duplicate market value, attach another advisor or exclude a portfolio without an obvious SQL error. Retained identifiers make those defects inspectable.

The prepared position model sums signed quantity and fees across valid trades and uses a deterministic latest-price observation. The summary then reports nominal fixture market value, fees, trade count and position count. It does not convert currencies or establish realized investment performance. Those limitations matter when explaining a consumer metric. The supplied 3,717 positions yield 1,028 portfolio summaries, not one report row for every conformed portfolio. A correct grand total can still hide value shifted between portfolios, so compare full portfolio-key projections and relationship identities. Descriptive names enrich the result but cannot replace stable keys.

#### Challenge


Complete the copied portfolio-summary model through references to the prepared positions and portfolio/client/advisor dimensions. Use the declared portfolio, client and advisor relationships, aggregate at one row per portfolio, and retain the required identifiers alongside descriptive context. Include nominal AUM, fees, trade count and position count with consistent units. Keep the source-to-target mapping and consumer contract updated as you implement.

Inspect the prepared position and latest-price models to understand what was supplied. Pick one active portfolio and independently calculate its output from copied trades and dimensions, then compare the warehouse result. Build the summary's upstream graph and check membership before presenting totals. If a portfolio unexpectedly disappears, inspect its trade participation and each join predicate rather than adding a distinct or switching join types without a population decision. Do not invent rows for inactive portfolios inside this core report.

#### Hint


<details>
<summary>Trace each relationship key before attaching names</summary>

Follow the portfolio key from positions into the portfolio dimension, then follow the separate client and advisor keys from that dimension. Similar-looking integer IDs are not interchangeable. Count distinct portfolios before and after each relationship. Inspect one multi-position portfolio to confirm that position count and trade count represent different measures, and keep the latest-price tie-break rule in your explanation.

</details>

#### Check


The report must contain exactly 1,028 unique portfolio keys derived from 3,717 prepared positions. Compare each portfolio's client/advisor identity, nominal AUM, fees, trade count and position count against the independent CSV reference. Inspect at least one multi-position portfolio manually to explain the aggregation rather than accepting an output sample solely because it is nonempty.

Retain build/run-results identity, selected key/value projection and the relevant source-to-target mapping. Structural uniqueness/not-null/relationship checks must agree with the business population, and a grand sum cannot replace per-key comparison. Explain why names are attributes rather than join keys and why this fixture aggregate is not FX-normalized valuation. If a join loses a key, report the anti-join result and diagnose the actual predicate. Keep warehouse execution pending when only local fixture arithmetic is available; the independent expected output does not itself prove your SQL ran.

```bash
dbt build --select +rpt_portfolio_summary --project-dir . --profiles-dir . --target local
python runtime/lab.py check . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p1-03-reasoning)


---


<a id="capstone-p1-04"></a>

### capstone-p1-04: Investigate expected omission and a defective join


<a id="capstone-p1-04-concept"></a>

#### Concept


An anti-join answers which declared keys are absent from another population. It is more informative than subtracting two row counts because it identifies the missing members and lets you inspect their cause. For Atlas, comparing all conformed portfolios with the trade-active summary reveals the expected 1,472 portfolios without qualifying activity. Comparing a correct relationship with a deliberately wrong join reveals a different, avoidable loss.

Portfolio client identifiers and advisor identifiers can both be integers without describing the same entity. Joining a portfolio's client key to the advisor dimension can accidentally match a subset and drop the rest. The output may still contain familiar advisor names and plausible amounts. That defect cannot be explained as inactive population merely because the row count is smaller. Keep the business membership rule separate from the SQL relationship predicate. The consumer may later choose an all-portfolio variant, but that is a contract change with explicit empty-status semantics, not permission to disguise an erroneous join.

#### Challenge


Write a diagnostic comparison from the conformed portfolio dimension to the correctly built trade-active report. Identify the absent portfolio keys and show whether each lacks qualifying trade-derived positions. Retain the expected population counts and an example of an excluded portfolio in the team evidence note.

In a bounded diagnostic query, reproduce the wrong relationship that joins portfolio client identifiers to advisor identifiers. Compare its membership with the correct advisor-key join and identify at least one unexpectedly lost or misattached key. Keep the defect out of the final consumer model and restore the declared relationship before completion. Explain the difference between expected inactive omission, invalid-trade exclusion and defective join loss. Update the consumer contract only if your team deliberately chooses a separately scoped all-portfolio extension; do not rewrite it after seeing a bad result to make the defect acceptable.

#### Hint


<details>
<summary>Give every missing key an explicit population reason</summary>

Start with key sets and reason labels rather than a grand total. Trace the actual portfolio row's client and advisor fields into their corresponding dimensions. A matching integer value does not imply the same business entity. Use the supplied independent reference to anchor the correct active membership, and inspect an unexpected anti-join row before deciding whether missing trade participation explains it.

</details>

#### Check


The correct active report must contain 1,028 of the 2,500 conformed portfolio keys, with 1,472 explained as lacking qualifying trade-derived output. The deliberate wrong-key diagnostic must lose or misattach population for its stated predicate reason, and the final repaired model must return to the independent expected membership and values. A smaller count alone is insufficient evidence of either case.

Retain the anti-join SQL, representative missing keys, wrong and corrected predicates, and actual warehouse query identities when available. Explain why two reconciliations built downstream of the same dropped population could still agree numerically. Your consumer handoff should name the expected excluded population and show how a defect would be distinguished from it. Keep local CSV classification separate from executed warehouse diagnostics. Restore the baseline copied sources and relationship logic before running the final phase verifier; the diagnostic failure should remain evidence, not become the shipped report.

```bash
# Inspect anti-join membership and relationship predicates in the actual warehouse.
python runtime/lab.py reference . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p1-04-reasoning)


---


<a id="capstone-p1-05"></a>

### capstone-p1-05: Prove minimum data quality and give a consumer handoff


<a id="capstone-p1-05-concept"></a>

#### Concept


A data product is useful when its consumer can understand what the output represents, which quality promises were checked and what its limits are. SQL completion and a green test summary are technical evidence, but the consumer also needs population, units, timing and ownership. The Atlas minimum slice makes this concrete through valid trades, positions and an active-portfolio report with an independently accounted excluded population.

Quality assertions should protect keys, relationships, filter membership and business arithmetic. A relationship test alone may ignore nulls; a numeric reconciliation alone may share a lost population; an output sample alone cannot establish complete keys. The team therefore combines structural tests with independent per-key comparison and a controlled wrong-join diagnosis. The presentation describes the nominal-money limitation and supplied supporting baseline, avoiding claims of FX-normalized AUM or official performance. Roles help review the result: the producer explains source meaning, the creator explains transformations, and the consumer challenges whether the report answers its stated question.

#### Challenge


Finish the schema and singular quality checks for the authored trade fact and portfolio summary. Confirm the raw/valid/position/report populations, required identifiers, relationship keys and money/fee conversions. Retain the intended wrong-key failure and repaired result rather than presenting only the final green command.

Prepare a short consumer handoff and demonstration. State the question, active-portfolio population, excluded population, output grain, nominal-money limitation and actual observed runtime boundary. Show a representative independently checked portfolio and the lineage from supplied sources. Present the bounded authored diff and identify which dimensions/positions/helpers were supplied. Inspect prepared orchestration only when its actual environment is available; do not claim a scheduled Atlas run from source presence alone. Record pending warehouse, worker or human checks explicitly and choose optional advanced work only after the fixed minimum standard is met.

#### Hint


<details>
<summary>Explain the business result and the evidence that protects it</summary>

Build the presentation around one consumer decision and one fully traced portfolio rather than a tour of every file. Put independent population and unit evidence beside the metric being shown. Use the wrong-key diagnostic to explain why trust requires more than a matching grand total. Clearly separate a source-backed planned orchestration step from an observed scheduled run, and disclose any instructor-reference comparison after your own attempt.

</details>

#### Check


Run the final baseline build and independent Atlas comparison in the owned namespace. Expected populations remain ten thousand raw trades, 9,880 valid trades, 3,717 positions, 1,028 active reported portfolios and 1,472 conformed portfolios without qualifying output. The report's complete identifier/value projection must agree independently, not merely its row count or overall sum.

Inspect the handoff for consumer question, population, grain, units, limitations, authored-versus-supplied work, current artifacts and remaining gates. Retain a selected trade fee calculation and portfolio aggregation explanation, plus the failed/repaired relationship diagnostic. Demonstrate the Databricks output in your own attempt. If showing orchestration, identify the scheduled run that produced it. Review the presentation with your consumer role before handoff.

```bash
dbt build --project-dir . --profiles-dir . --target local
python runtime/lab.py check . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p1-05-reasoning)


## Phase completion


Your minimum capstone result is a meaningful source→domain→consumer slice, with a retained business key, explicit trade filters and a documented consumer population. Submit the valid-trade fact and portfolio-summary SQL, their structural/business checks, a small source-to-target mapping and a consumer handoff. The independent reference must identify 10,000 raw trades, 9,880 valid trades, 3,717 portfolio/instrument positions and 1,028 reported portfolios. Account separately for the 1,472 conformed portfolios without qualifying trades instead of labelling them accidental loss.

Retain one controlled wrong-key join and explain why it drops population, then show the repaired output and independent key/value comparison. State what the prepared dimensions, latest-price and position models supplied and what your team authored. Explain cents, decimal money, basis-point fees and the fixture's lack of FX conversion. The consumer report is a nominal teaching aggregate, not an investment recommendation or a complete real-world portfolio valuation. Warehouse execution and prepared orchestration remain pending until actually observed. Team roles, reviewable changes and a short presentation connect the technical result to a consumer question; optional extensions follow the fixed completion gate.

---


## Optional stretch


The core completion standard is independent of optional work. No additional stretch is required in this phase; the next phase has an independently prepared entry baseline.

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: State the consumer population and grain

<a id="capstone-p1-01-reasoning"></a>

<details>
<summary>Reasoning for capstone-p1-01: Population omission can be expected or a defect depending on contract</summary>

The core asks for trade-active portfolios, so 1,472 conformed portfolios without qualifying trades are expected exclusions. Their identifiers remain necessary for an anti-join and explanatory handoff. An all-portfolio inventory would use a different membership contract and likely an explicit empty status. The mapping connects units and relationship keys to the consumer result; it cannot borrow GBP/NAV assumptions from the separate Portfolio Analytics case. Local fixture expectations still need warehouse confirmation.

[Return to capstone-p1-01](#capstone-p1-01)

</details>

### Reasoning: Build the valid-trade domain fact

<a id="capstone-p1-02-reasoning"></a>

<details>
<summary>Reasoning for capstone-p1-02: Valid trade rules precede signed position and fee aggregation</summary>

The valid domain fact selects 9,880 recognized positive-quantity/price trades while retaining their business identifiers. Cents and basis points have different scaling factors. A sell is valid activity even though it later reduces signed position quantity. Independent membership and per-trade arithmetic detect filtering or unit mistakes that a model's own row count could conceal. Do not impose a raw-trade positivity rule on a derived signed net-position measure.

[Return to capstone-p1-02](#capstone-p1-02)

</details>

### Reasoning: Author the active portfolio summary

<a id="capstone-p1-03-reasoning"></a>

<details>
<summary>Reasoning for capstone-p1-03: Stable relationship keys and per-portfolio values establish the result</summary>

The consumer row is an active portfolio, built from portfolio/instrument positions and joined through its declared client/advisor keys. Position count is not trade count, and names cannot substitute for identifiers. Independent per-key comparison detects shifted values and misattached relationships despite plausible overall totals. The report's nominal fixture AUM lacks FX conversion, so the consumer explanation must preserve that limitation rather than present it as a complete investment valuation.

[Return to capstone-p1-03](#capstone-p1-03)

</details>

### Reasoning: Investigate expected omission and a defective join

<a id="capstone-p1-04-reasoning"></a>

<details>
<summary>Reasoning for capstone-p1-04: Expected omission and accidental loss need different evidence</summary>

The expected missing 1,472 keys have no qualifying trade-derived participation under the stated consumer contract. A wrong client-to-advisor relationship creates another loss that must not be relabelled inactive. Key-level anti-joins and source relationship traces distinguish these causes. Shared downstream totals can agree after the same population was lost, so independent membership is necessary. The final repaired consumer graph must reproduce both expected keys and values.

[Return to capstone-p1-04](#capstone-p1-04)

</details>

### Reasoning: Prove minimum data quality and give a consumer handoff

<a id="capstone-p1-05-reasoning"></a>

<details>
<summary>Reasoning for capstone-p1-05: A consumer handoff joins business meaning to independent technical evidence</summary>

The minimum result is a trusted active-portfolio slice, not every possible Atlas extension. Independent membership and per-key values complement structural tests and the wrong-join drill. The handoff states cents/basis-point conversions, nominal-money limitations and the expected inactive population. It identifies supplied support and actual runtime observations. Prepared source or a local reference calculation cannot stand in for warehouse/orchestration execution or human presentation acceptance.

[Return to capstone-p1-05](#capstone-p1-05)

</details>


---

# capstone independent starter

Read the [owning phase](../README.md) before editing. Prepare from the training project root with `mise run challenge:v2:prepare capstone phase-one-certified`; edit the copied attempt.

## Authored-file list

| Task | Learner-authored paths |
|---|---|
| capstone-p1-01, capstone-p1-04 | `contract.md`, `evidence.md` |
| capstone-p1-02 | `models/dom_trading__trade.sql`, `tests/valid_trade_population.sql`, `evidence.md` |
| capstone-p1-03 | `models/rpt_portfolio_summary.sql`, `evidence.md` |
| capstone-p1-05 | `models/schema.yml`, `tests/`, `contract.md`, `evidence.md` |

## Declared baseline

These focus files are intentionally unfinished: `models/dom_trading__trade.sql`, `models/rpt_portfolio_summary.sql`. Supporting models and profiles are supplied. Complete the listed files, then verify their output in the required Databricks or Astro environment.

Keep `evidence.md` beside the copied project. Create a named file when its task asks for it. Use a fresh workspace for another attempt; preparation and reset preserve existing work.


---

# capstone: Phase 2 — advanced practice

## Purpose and outcome

Extend the active-portfolio product into three useful reporting views: portfolio trading/fee detail, an advisor book leaderboard and regional aggregation. Build the three reports, reconcile their results and demonstrate a defect and repair before choosing optional extensions.

## Dataset and pipeline

Use the same seven supplied Atlas CSVs and prepared baseline models. The starter already supplies valid trades, positions, active portfolio summary and advisor book. Three consumer SQL files remain unfinished. Performance is one row per active portfolio, the leaderboard one row per participating advisor, and the regional report one row per region represented by that leaderboard. The regional dependency is the leaderboard; it does not depend on inventing a new trade source or completing every other extension.

The independent baseline identifies 9,880 valid trades, 3,717 positions and 1,028 active portfolios. Nominal AUM and fees follow the fixture's native-unit aggregation without FX conversion. Trading volume means buys plus sells, while net flow is buys minus sells; neither equals current market value. The realized fee rate is total fees divided by total traded value, expressed back in basis points. Ties share dense rank without gaps, and a zero denominator produces an explicitly documented null rather than an invalid division or silently accepted zero fee rate.

## Prerequisites and workspace

Prepare a fresh advanced capstone attempt from the training project root, then run direct dbt commands inside it with the approved namespace and unique owned prefix. The baseline represents the completed foundation semantics and is supplied even if your team did not complete the foundation route. Inspect its model contracts before extending them. Record actual dbt adapter/target and keep artifact paths local to the prepared container attempt.

```bash
mise run challenge:v2:prepare capstone phase-two-proficient
cd .local/challenges-v2/capstone/phase-two-proficient
export DC_RELATION_PREFIX=dc_team_atlas02
dbt debug --project-dir . --profiles-dir . --target local
```

Confirm the consumer's intended comparison and measurement limitations before choosing an extension. Team roles review business meaning, transformation grain and independent evidence. Installation/access preparation is outside the unpiloted core estimate, and optional work has separate timing. Credentials stay outside source and presentation evidence.

## Starter behavior

The performance, leaderboard and regional report files contain declared unfinished outcomes. Completion verification rejects those placeholders even though the supplied baseline graph is useful and parseable. Build the baseline supporting slice first when diagnosing dependencies; an empty placeholder output cannot establish the final report population. Negative reconciliation drills must change only copied models or inputs and predict the intended failure. Keep the original supplied CSVs and baseline outputs available for restoration. A local independent reference can establish expected populations and values while actual warehouse execution remains pending.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 90–120 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [capstone-p2-01: Build a meaningful performance report](#capstone-p2-01) | 18–24 | 1,028 portfolio keys; independent buys/sells/fees; explicit zero-safe basis-point rate |
| [capstone-p2-02: Rank advisor books with explicit ties](#capstone-p2-02) | 18–24 | One row per advisor; dense ties without gaps; independent book totals and counts |
| [capstone-p2-03: Build the regional rollup from its declared dependency](#capstone-p2-03) | 18–24 | Region advisor/portfolio counts and nominal totals reconcile independently |
| [capstone-p2-04: Reconcile independently and reject a defect](#capstone-p2-04) | 18–24 | Omitted advisor contribution fails reconciliation; repair restores all expected keys/values |
| [capstone-p2-05: Present a fixed completed core and select stretch](#capstone-p2-05) | 18–24 | Three report grains, independent values, defect/repair narrative and optional extension choices |

## Core challenges


<a id="capstone-p2-01"></a>

### capstone-p2-01: Build a meaningful performance report


<a id="capstone-p2-01-concept"></a>

#### Concept


A richer report adds measures with distinct business meanings rather than renaming the same total. Buy and sell value describe traded activity, net flow describes their difference, and current nominal AUM describes signed position quantity valued at the prepared latest price. These measures can differ substantially without being inconsistent. The portfolio performance report combines baseline summary fields with position-level bought/sold totals reaggregated to portfolio grain.

The realized fee rate is a weighted rate: aggregate fees divided by aggregate traded value, multiplied by ten thousand to express basis points. Averaging trade fee rates would weight a tiny trade the same as a large one and answer another question. For example, a fee of one on total traded value of one thousand corresponds to ten basis points, not one percent or a fraction mislabeled as basis points. A zero traded denominator needs an explicit null-safe rule. This fixture does not provide a flow-adjusted investment-return calculation or FX-normalized wealth measure, so the report title and consumer explanation must not claim either.

#### Challenge


Complete the copied performance-report SQL using the prepared portfolio summary and position model. Reaggregate bought and sold values to portfolio before joining them to the one-row-per-portfolio summary. Retain portfolio identifier, nominal AUM, fees, counts, buy/sell values, net flow and a null-safe realized fee rate with its units documented.

Calculate one actual portfolio independently from copied trades and compare its numerator and denominator with the prepared positions. Build the consumer model and inspect all active keys. Add a bounded zero-denominator expression test even if every supplied active portfolio has nonzero trading volume. Document why weighted fee rate differs from an average fee-basis-point field and why net flow differs from current valuation. Do not add an FX assumption or performance-return claim unsupported by these sources. Keep the supplied baseline and newly authored report responsibilities explicit.

#### Hint


<details>
<summary>Aggregate volume before joining and label the weighted rate</summary>

Check the grain of the bought/sold input before joining: the positions relation has multiple instrument rows per portfolio. Sum those values at portfolio grain first. Write the fee-rate numerator, denominator and scaling factor in words before SQL. The independent CSV calculation should use decimal price conversion and fee arithmetic rather than copying your report query, so it can detect the same mistake you are trying to test.

</details>

#### Check


The report must contain the same 1,028 active portfolio keys as the baseline summary. Compare buy value, sell value, net flow and realized fee rate per key with the independent reference; also retain the baseline AUM/fee/count fields without duplicating them through a position join. The standalone zero-denominator case must return the documented null rather than crash or manufacture a zero rate.

Inspect a selected portfolio's raw trades and explain its weighted rate calculation. Retain run-results identity, independent projection and zero-case evidence. A matching overall buy/sell sum cannot prove each portfolio's values. Explain why nominal AUM, traded volume and net flow represent different measures and why none automatically establishes investment return. Keep actual warehouse behavior pending when only SQL and local reference arithmetic have been prepared. The type and population assertions must agree with the consumer contract rather than a convenient sample.

```bash
dbt build --select +rpt_portfolio_performance --project-dir . --profiles-dir . --target local
python runtime/lab.py reference . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p2-01-reasoning)


---


<a id="capstone-p2-02"></a>

### capstone-p2-02: Rank advisor books with explicit ties


<a id="capstone-p2-02-concept"></a>

#### Concept


A leaderboard defines both the participating population and the ranking rule. Here the prepared advisor book aggregates active portfolio reports, so participation follows the declared trade-active consumer population rather than every advisor record in the raw reference. Stable advisor identifiers and region attributes must remain available for reconciliation and the later regional rollup. A display name alone is not a safe grouping or relationship key.

Dense ranking gives equal book values the same rank and assigns the next distinct value the next integer. With values ten, ten and five, dense ranks are one, one and two. A row-number function instead forces a unique order, while ordinary rank can leave a gap; those alternatives support different consumer interpretations. A separate deterministic display ordering can use advisor identifier after rank without breaking the tie meaning. The supplied nominal book values inherit the fixture's absence of FX conversion, so a leaderboard comparison must state that limitation rather than turn the ranking into a real-world advice claim.

#### Challenge


Complete the advisor-leaderboard model through a reference to the prepared advisor book. Retain advisor identifier/name, region, portfolio count, nominal book AUM and fees, then add the declared dense ranking by descending book value. Keep display tie-break ordering separate from rank semantics. Inspect how the prepared advisor book obtains its active-portfolio population.

Create a bounded three-value tie example and compare dense rank, rank and row-number behavior so your explanation does not depend on the fixture containing an accidental tie. Build the authored leaderboard and independently aggregate portfolio outputs by advisor to compare identities, participation, counts and values. Document the ranking rule and native-unit limitation for the intended advisor dashboard. Do not group solely by names or include inactive advisors with invented zero books without a separately stated population change.

#### Hint


<details>
<summary>Separate ranking semantics from stable display ordering</summary>

Use the prepared advisor book's declared grain rather than rejoining position-level data into the leaderboard. Inspect ties with a small explicit values relation and read the resulting rank sequence. A final display sort can be stable while several advisors still share the same dense rank. For population discrepancies, compare participating advisor keys from the portfolio summary before changing the rank function.

</details>

#### Check


Expect one row per independently participating advisor, with book AUM, fees and portfolio count matching aggregation of the active portfolio reference. The rank must agree with descending distinct book values, and the explicit ten/ten/five example must produce dense ranks one/one/two. An arbitrary row order in a preview is not the ranking contract; inspect rank values and display ordering separately.

Retain the actual model/test run identity, independent advisor-key projection and tie-example result. Explain the difference among dense rank, rank and row number, and why names cannot replace stable advisor IDs. The regional model depends on the leaderboard's retained region and aggregate fields, so do not remove them as presentation-only columns. State the nominal native-unit comparison limitation. A correct-looking first five advisors cannot prove complete participation or independent book values; keep warehouse execution pending when only the source and local reference are available.

```bash
dbt build --select +rpt_advisor_leaderboard --project-dir . --profiles-dir . --target local
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p2-02-reasoning)


---


<a id="capstone-p2-03"></a>

### capstone-p2-03: Build the regional rollup from its declared dependency


<a id="capstone-p2-03-concept"></a>

#### Concept


A rollup changes grain through aggregation, so each measure must be interpreted at the new grain. The regional report groups the advisor leaderboard by region, counting participating advisor rows and summing their portfolio counts, nominal AUM and fees. Counting raw trades would produce another measure entirely. Rejoining lower-grain positions after the leaderboard could duplicate advisor totals and make the report look larger without adding new consumer meaning.

This dependency is explicit: the regional report requires the completed leaderboard and its region/totals, while the separate performance mart supports another question. The core does not need every legacy extension before a region can be built. Region membership must be inherited from the declared advisor mapping, not guessed from an advisor name or client segment. Summing region totals can match a shared upstream error, so the independent oracle should rebuild expected regions from copied source relationships and valid-trade values. Key membership and counts complement the numeric comparison.

#### Challenge


Complete the regional-report SQL through a reference to the authored advisor leaderboard. Produce one row per represented region with participating advisor count, portfolio count, nominal AUM and fees. Keep the dependency visible in the model and document the grain change. Read the leaderboard contract to ensure the fields you aggregate retain their intended meanings.

Independently calculate one region from copied portfolio/advisor relationships and the active-portfolio reference, then compare all regions with the warehouse output. Inspect manifest lineage to show the regional report depends on the leaderboard. Verify that running the regional selection with its upstream graph supplies the right prerequisites without requiring the performance report as an accidental dependency. If a region is missing, inspect participating advisor keys before inserting an empty display row. An all-region inventory would be a separately scoped population contract.

#### Hint


<details>
<summary>Aggregate the declared advisor grain without rejoining activity</summary>

Start with one advisor row from the leaderboard and trace how its portfolio count and money values contribute to a region. Keep row count, summed portfolio count and monetary totals separate. Build the region from the declared one-row-per-advisor input instead of joining raw activity again. The independent reference should use source relationships so it can detect a wrong region assignment shared by two derived reports.

</details>

#### Check


The report must have one key per independently represented region, and each region's advisor count, portfolio count, nominal AUM and fees must agree with the copied-input oracle. Compare key membership and values for every region rather than only a grand sum. Inspect the manifest edge to the leaderboard and confirm the selected build includes the actual prerequisite graph.

Retain a manually traced advisor contribution, independent regional projection, artifact identity and the documented population limitation. Explain why counting leaderboard rows measures participating advisors and why summing portfolio counts differs from counting raw trades. A region-total reconciliation against only the same broken leaderboard would be insufficient independent evidence. When the warehouse is unavailable, author the SQL, calculate expectations locally and leave actual execution pending. Keep the report's nominal native-unit interpretation visible in the consumer handoff rather than relabelling it a globally converted valuation.

```bash
dbt build --select +rpt_region_report --project-dir . --profiles-dir . --target local
python runtime/lab.py check . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p2-03-reasoning)


---


<a id="capstone-p2-04"></a>

### capstone-p2-04: Reconcile independently and reject a defect


<a id="capstone-p2-04-concept"></a>

#### Concept


Reconciliation needs sensitivity to a realistic defect, not just a happy-path pass. A regional report that omits an advisor can still return familiar region names and plausible positive totals. The independent expected contribution must expose the lost advisor/portfolio membership and money. Comparing only two outputs that share the omission could miss it completely.

The controlled negative drill changes a copied report predicate to omit a participating advisor. Its failed assertion should identify the affected region/key/value contract. Restoring that predicate and rebuilding the model repairs the cause; changing the expected oracle or tolerance would merely hide it. Keep the baseline raw data unchanged so the difference comes from the deliberate model defect. Tie and zero-denominator examples protect separate semantics and should not be counted as this omission drill. A nonzero build exit alone could arise from credentials or an unfinished unrelated model, so inspect the actual failed node and diagnostic rows before declaring the negative case meaningful.

#### Challenge


Write or review the regional reconciliation test so it compares independently expected membership/counts and monetary values at region grain. State its tolerance and explain how it detects a missing advisor contribution. Run the complete authored core against the baseline copied inputs before injecting a defect.

In a disposable model copy, exclude one participating advisor contribution from the regional report and rerun the selected model/test. Retain the failed node, affected region and independently calculated difference. Restore the report predicate and rebuild the same graph, then rerun the complete performance/leaderboard/region comparison. Keep the failure and repair diff small enough for a reviewer to understand. Do not alter raw seed fixtures or the expected reference to make the defective output acceptable, and do not erase the failed artifact when collecting the final passing run.

#### Hint


<details>
<summary>Predict a nonempty omitted contribution before changing the query</summary>

Select a participating advisor whose contribution is nonempty, and predict the affected region before editing. Compare region membership and counts before monetary tolerance. Inspect the test's compiled SQL to ensure its expectation is not merely the same filtered report again. Keep the defective SQL outside your final authored version after recording the failure, then verify restoration through a fresh selected build.

</details>

#### Check


The baseline core must agree with all independently expected portfolio, advisor and region values. The deliberately filtered regional query must fail its named reconciliation for the omitted contribution, with a diagnostic difference in the expected region. After restoring the predicate, the same test and independent output comparison must pass. An unrelated authentication or compile failure is not the intended negative result.

Retain source/model hashes, baseline and failed/repaired run identities, affected membership/value projection and bounded repair diff. Explain why a comparison against the same filtered leaderboard/report would not be independent and why loosening the tolerance is the wrong repair. Recheck the performance rate and leaderboard tie semantics after the regional repair without rerunning an unrelated production deployment. If only static/local expectations can be prepared here, mark the warehouse defect/repair sequence pending rather than claiming the checker script alone has proved execution.

```bash
dbt test --select reconcile_region --project-dir . --profiles-dir . --target local
python runtime/lab.py check . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p2-04-reasoning)


---


<a id="capstone-p2-05"></a>

### capstone-p2-05: Present a fixed completed core and select stretch


<a id="capstone-p2-05-concept"></a>

#### Concept


An advanced capstone should have a finite completion standard so a team can demonstrate a coherent product rather than an arbitrary collection of files. Here the three consumer views support related but distinct questions: portfolio trading/fee detail, advisor book comparison and regional aggregation. Their grains and dependencies make that relationship understandable. The presentation must explain how independent checks and the omission drill protect the output, not merely display a long list of passed tests.

Optional depth can extend windows, freshness, exposures, macros, generic tests, incrementals, snapshots or orchestration, but each adds prerequisites and time. Selecting an extension does not erase unfinished core reports, and finishing every legacy extension is not mandatory. The team should choose based on a consumer question and available prepared runtime. Honest limits are part of the product: nominal native-unit money, active population, supplied baseline, unobserved warehouse/orchestration boundaries and unpiloted timing. A classroom artifact and reviewed source are valuable without implying production promotion or publication.

#### Challenge


Prepare a short team demonstration of the fixed core with a consumer contract, report grain/dependency map, independently checked values and a single deliberate-defect/repair narrative. Show one portfolio fee calculation, the explicit tie example and a traced regional contribution. Identify your authored files and the supplied foundation baseline, and present a bounded reviewable diff.

Document the active population and nominal-money limitation, current artifact/source hashes and actual runtime observations. Choose any optional extension only after the core completion standard passes, listing its consumer purpose, prerequisite models, additional estimate and expected independent evidence. Keep hosted monitoring, deployment and infrastructure work outside required classroom completion. Leave live warehouse, prepared orchestration, novice timing and human presentation checks pending unless they actually ran. Compare end-of-phase reasoning after your attempt and record instructor-reference exposure honestly.

#### Hint


<details>
<summary>Present a finite product story before selecting extensions</summary>

Use the dependency map to organize the story: a portfolio output, an advisor aggregate, a regional rollup and the assertion that rejected a lost contribution. Keep one explicit example per semantic rule instead of showing every row. Select optional depth because it answers a useful question, not because another table makes the project look advanced. A clear pending list is more useful than a generic production-ready label.

</details>

#### Check


Inspect the presentation and evidence against the completed core: 1,028 performance keys, independently participating advisors with correct dense ranks, and every represented region with reconciled counts/values. The zero-denominator and tie examples must match their declared semantics. Retain the actual failed/repaired regional assertion and explain the cause rather than presenting only final green output.

Check that each report's grain, population, units and dependency are stated, that supplied baseline work is disclosed, and that optional extensions have separate prerequisites/time/evidence. Review the actual warehouse output and consumer explanation together. Keep no-activity population and native-currency limitations visible. The demonstration should show the completed reports and the evidence supporting each claim.

```bash
dbt build --project-dir . --profiles-dir . --target local
python runtime/lab.py check . --case atlas
```

<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#capstone-p2-05-reasoning)


## Phase completion


Finish the finite advanced core: portfolio performance report, advisor leaderboard, regional rollup and independent reconciliation, plus a consumer explanation of one deliberate defect and repaired result. Keep the three authored output grains explicit and prove all retained identifiers and money/fee values against the copied-input oracle. Demonstrate tie semantics and zero-denominator behavior with bounded examples instead of relying on whether the supplied fixture happens to contain a tie or zero case.

Your presentation shows the consumer question, source→domain→consumer lineage, nominal-money limitation, independent population/value checks, failed and repaired regional assertion and a bounded authored diff. List optional extensions separately with their prerequisites and estimates; completing every legacy exercise is not the core standard. The advanced starter supplies the completed baseline deliberately, so disclose it rather than presenting all baseline SQL as newly authored work. Actual Databricks output, orchestration and human timing/presentation review remain separate pending gates unless observed. No production deployment, external publication or infrastructure provisioning is required to demonstrate this fixed reporting core.

---


## Optional stretch


The core completion standard is independent of optional work. Choose a separately timed route from [the stretch guide](stretch/README.md).

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Build a meaningful performance report

<a id="capstone-p2-01-reasoning"></a>

<details>
<summary>Reasoning for capstone-p2-01: Weighted rate and investment performance are different measures</summary>

Bought/sold values need portfolio-level aggregation before joining summary. Realized fee basis points divide total fees by total traded volume and scale by ten thousand; an average raw rate would answer another question. The zero case is explicitly null-safe. Net flow and nominal current AUM have different meanings, and the fixture does not establish flow-adjusted return or FX-normalized valuation. Independent per-portfolio values protect these distinctions.

[Return to capstone-p2-01](#capstone-p2-01)

</details>

### Reasoning: Rank advisor books with explicit ties

<a id="capstone-p2-02-reasoning"></a>

<details>
<summary>Reasoning for capstone-p2-02: Tie meaning is part of the consumer contract</summary>

Dense rank groups equal book values and advances by distinct values, while stable display ordering may add an advisor-ID tie-break. The leaderboard retains participating advisor keys, region and independently reconciled totals. Names are descriptive attributes. The explicit tie example tests the rule even if the supplied fixture lacks ties. Its book comparison remains a nominal teaching aggregate, not FX-normalized investment advice.

[Return to capstone-p2-02](#capstone-p2-02)

</details>

### Reasoning: Build the regional rollup from its declared dependency

<a id="capstone-p2-03-reasoning"></a>

<details>
<summary>Reasoning for capstone-p2-03: The regional dependency and aggregation grain stay explicit</summary>

The report aggregates the leaderboard's advisor-grain rows, retaining region membership and measure meanings. The performance report is another consumer view, not a hidden prerequisite. Independent source-derived region membership protects against a shared upstream mapping error. Advisor count, portfolio count and monetary totals are separate obligations, and the resulting native-unit sums retain their teaching limitation.

[Return to capstone-p2-03](#capstone-p2-03)

</details>

### Reasoning: Reconcile independently and reject a defect

<a id="capstone-p2-04-reasoning"></a>

<details>
<summary>Reasoning for capstone-p2-04: A useful negative case fails on the predicted business difference</summary>

The omission drill removes a known nonempty advisor contribution while leaving raw baseline inputs intact. A meaningful reconciliation detects the affected region's membership/count/value difference independently. Restoring the predicate repairs that cause. Shared filtered outputs or looser tolerance could conceal the loss, and an unrelated nonzero command would not establish the drill. Retain baseline, failure and repaired evidence as separate observed states.

[Return to capstone-p2-04](#capstone-p2-04)

</details>

### Reasoning: Present a fixed completed core and select stretch

<a id="capstone-p2-05-reasoning"></a>

<details>
<summary>Reasoning for capstone-p2-05: Completeness means the declared core, not every optional extension</summary>

The advanced core connects three explicit report grains with independent population/value evidence and a meaningful regional omission repair. Tie and zero cases demonstrate semantics even when absent from the main fixture. The team discloses supplied baseline and nominal-money limits, then selects optional depth with separate prerequisites and timing. A local authored candidate does not establish connected orchestration or human presentation acceptance, and it does not imply production publication.

[Return to capstone-p2-05](#capstone-p2-05)

</details>


---

# capstone independent starter

Read the [owning phase](../README.md) before editing. Prepare from the training project root with `mise run challenge:v2:prepare capstone phase-two-proficient`; edit the copied attempt.

## Authored-file list

| Task | Learner-authored paths |
|---|---|
| capstone-p2-01 | `models/rpt_portfolio_performance.sql`, `evidence.md` |
| capstone-p2-02 | `models/rpt_advisor_leaderboard.sql`, `evidence.md` |
| capstone-p2-03 | `models/rpt_region_report.sql`, `evidence.md` |
| capstone-p2-04 | `tests/reconcile_region.sql`, `evidence.md` |
| capstone-p2-05 | `contract.md`, `evidence.md`, `models/schema.yml` |

## Declared baseline

These focus files are intentionally unfinished: `models/rpt_portfolio_performance.sql`, `models/rpt_advisor_leaderboard.sql`, `models/rpt_region_report.sql`. Supporting models and profiles are supplied. Complete the listed files, then verify their output in the required Databricks or Astro environment.

Keep `evidence.md` beside the copied project. Create a named file when its task asks for it. Use a fresh workspace for another attempt; preparation and reset preserve existing work.


---

# Historical capstone extension

The earlier extension is retained in the separate instructor archive and authoring workspace. Its setup and claims require review before reuse; it is outside the current learner assignment.

Earlier examples include an incorrect API dependency and inferred history from row counts. The current project checks model dependencies, business dates, population and replay explicitly.

Use the [current advanced phase](../README.md) for the supported tasks, independently prepared baseline and evidence checks. Ask the instructor to select any additional historical exercise.

<a id="v2-capstone-phase-two-proficient-stretch-readme-md-capstone-optional-stretch-selection"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-full-legacy-advanced-reference"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-phase-2-advanced-technical-extensions"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-phase-2-dependency-map"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-challenge-1-a-richer-executive-report-mart"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-concept"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-goal"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-task"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-check"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-challenge-2-advisor-leaderboard-with-dense_rank"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-concept-1"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-goal-1"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-task-1"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-check-1"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-challenge-3-daily-activity-by-asset-class-plus-a-rolling-window"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-concept-2"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-goal-2"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-task-2"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-check-2"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-challenge-4-declare-source-freshness-on-the-source-extracts"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-concept-3"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-goal-3"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-task-3"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-check-3"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-challenge-5-document-who-consumes-the-marts-with-exposures"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-concept-4"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-goal-4"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-task-4"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-check-4"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-challenge-6-a-reusable-money-macro"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-concept-5"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-goal-5"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-task-5"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-check-5"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-challenge-7-a-custom-generic-test-for-non-negative-money"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-concept-6"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-goal-6"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-task-6"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-check-6"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-challenge-8-a-relationship-referential-integrity-test"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-concept-7"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-goal-7"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-task-7"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-check-7"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-challenge-9-singular-reconciliation-tests-within-tolerance"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-concept-8"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-goal-8"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-task-8"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-check-8"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-challenge-10-an-incremental-market-mart"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-concept-9"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-goal-9"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-task-9"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-check-9"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-challenge-11-a-snapshot-for-slowly-changing-portfolios"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-concept-10"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-goal-10"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-task-10"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-check-10"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-challenge-12-understand-and-extend-the-orchestration"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-concept-11"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-goal-11"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-task-11"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-check-11"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-challenge-13-understand-params-driven-orchestration"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-concept-12"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-goal-12"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-task-12"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-check-12"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-challenge-14-a-reconciling-regional-report-capstone"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-concept-13"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-goal-13"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-task-13"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-check-13"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-use-the-product"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-appendix-quick-reference-and-opening-team-activity-example"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-working-in-the-devcontainer"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-know-where-to-run-commands"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-essential-dbt-commands"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-databricks-connection"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-airflow-quick-reference"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-verification-commands"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-starting-over"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-where-to-find-things"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-common-problems"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-safe-working-habits"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-opening-team-activity-example"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-glossary"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-troubleshooting"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-verify-your-work"></a>
<a id="v2-capstone-phase-two-proficient-stretch-readme-md-maintainer-only-from-scratch-verification"></a>

