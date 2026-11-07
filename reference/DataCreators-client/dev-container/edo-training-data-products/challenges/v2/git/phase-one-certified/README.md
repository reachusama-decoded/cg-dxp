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
