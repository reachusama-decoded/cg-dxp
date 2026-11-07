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
