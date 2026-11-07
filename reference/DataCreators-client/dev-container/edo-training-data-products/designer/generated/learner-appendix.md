# Appendix H — Complete version2 learner challenges {#appendix-h}

This appendix includes every learner README in manifest order. Commands retain their documented workspace boundaries. Instructor solutions are packaged separately. The previous complete course chapters are retained; summaries below are additional teaching navigation.


## Source: README.md {#v2-readme-md}

## Version 2 training challenges {#v2-readme-md-version-2-training-challenges}

Seven tool routes connect local collaboration, containers, transformation, platform discovery, orchestration, optional events and an Atlas product. Each active Phase 1 establishes minimum understanding; each offered Phase 2 has a finite advanced core and separate optional stretch. Databricks CLI and Kafka have no Phase 2 assignment.

  -----------------------------------------------------------------------------------------------------------------------------------
  Order             Route                                            Core estimates, minutes   Course placement
  ----------------- ------------------------------------------------ ------------------------- --------------------------------------
  1                 [Git](#v2-git-readme-md)                         60--90 / 75--110          Preparation / collaboration clinic

  2                 [Docker](#v2-docker-readme-md)                   60--90 / 75--110          Wednesday / image clinic

  3                 [dbt](#v2-dbt-readme-md)                         75--110 / 90--120         Wednesday / advanced transformations

  4                 [Databricks CLI](#v2-databricks-cli-readme-md)   45--65 / notoffered       Platform discovery / readiness

  5                 [Airflow](#v2-airflow-readme-md)                 75--110 / 90--120         Thursday / operations clinic

  6                 [Kafka, optional](#v2-kafka-readme-md)           60--90 / notoffered       Optional event clinic

  7                 [Atlas capstone](#v2-capstone-readme-md)         90--120 / 90--120         Friday / advanced reporting
  -----------------------------------------------------------------------------------------------------------------------------------

### Environment and workspace {#v2-readme-md-environment-and-workspace}

[Client readiness](practice/client/challenges/v1/00-environment-check/README.md) covers the connected container. This pack additionally provides a prepared local DuckDB transformation route with isolated copied workspaces; it does not pretend those outputs were built on Databricks. Run `python3 scripts/challenge-v2.py --help` from the project root. Numeric legacy mise tasks remain v1.

Instructor preparation: install the pinned local tool environment using `bash scripts/setup-v2-tools.sh`; supply Docker/images for container phases, real private GitHub sandbox/reviewer for GitPhase2, metadata access for CLI, an isolated Astro binding for UI drills, and a prepared Kafka/Airflow chain for optional Kafka. Each learner phase declares its subset.

### Scheduling and evidence {#v2-readme-md-scheduling-and-evidence}

Twelve offered phases target 45--120 minutes each, with initial unpiloted totals 885--1255 minutes including optional Kafka. Mandatory Phase 1 routes alone total 405--585 minutes. These are complete learner journeys; schedule advanced routes as clinics/post-course work and audit whole-course capacity separately. No automated runtime duration is a junior-learner timing observation.

Learner work belongs in `.local/challenges-v2/<tool>/<phase>` or a new chosen directory. Preparation refuses overwrite; reset creates a new attempt rather than deleting old work. Starter checks, solution checks and live service checks report separately. A placeholder passing its baseline is not completion. Preserve every blocked access/runtime gate and deliberate failure explanation.

### Materials and preserved depth {#v2-readme-md-materials-and-preserved-depth}

The full README appendix and generated session/instructor views come from these files. All nested learner READMEs are included; instructor solutions are excluded. Legacy detailed exercises, all 14 Atlas extensions, and prior data products remain preserved in [v1](practice/client/challenges/v1/README.md). Optional legacy advanced references explicitly retain v1 commands and workspace semantics.


## Source: git/README.md {#v2-git-readme-md}

## git challenges {#v2-git-readme-md-git-challenges}

This route develops minimum competence followed by advanced behavioral proof. Read concept explanations before attempting the task; retain commands/results and your reasoning.

### Before you start {#v2-git-readme-md-before-you-start}

Local Git forPhase1; authorized private GitHub sandbox, gh, and arranged reviewer forPhase2. Work in a copied phase workspace. Phase 2, when offered, supplies its entry fixture. [Pack navigation](#v2-readme-md) explains the course/clinic placement and version selection.

### Suggested timeline and tasks {#v2-git-readme-md-suggested-timeline-and-tasks}

  --------------------------------------------------------------------------------------------------------------------------------------
  Phase       Task ID                   Title                                             Teaching concept    Core/stretch   Minutes
  ----------- ------------------------- ------------------------------------------------- ------------------- -------------- -----------
  Phase 1     [git-p1-01](#git-p1-01)   Inspect the three working states                  git-p1-01-concept   core           12--18

  Phase 1     [git-p1-02](#git-p1-02)   Commit an intentional contract change             git-p1-02-concept   core           12--18

  Phase 1     [git-p1-03](#git-p1-03)   Branch and combine compatible work                git-p1-03-concept   core           12--18

  Phase 1     [git-p1-04](#git-p1-04)   Resolve an ownership conflict                     git-p1-04-concept   core           12--18

  Phase 1     [git-p1-05](#git-p1-05)   Restore a mistake and explain the final history   git-p1-05-concept   core           12--18

  Phase 2     [git-p2-01](#git-p2-01)   Clone and inspect a collaboration boundary        git-p2-01-concept   core           15--22

  Phase 2     [git-p2-02](#git-p2-02)   Push and propose a scoped pull request            git-p2-02-concept   core           15--22

  Phase 2     [git-p2-03](#git-p2-03)   Respond to a review with a second commit          git-p2-03-concept   core           15--22

  Phase 2     [git-p2-04](#git-p2-04)   Integrate concurrent upstream work                git-p2-04-concept   core           15--22

  Phase 2     [git-p2-05](#git-p2-05)   Read the final review and merge state             git-p2-05-concept   core           15--22
  --------------------------------------------------------------------------------------------------------------------------------------

Inclusive phase estimates: Phase 1 60--90 minutes; Phase 2 75--110 minutes. These estimates are unpiloted. Reading, normal waits, checking and handoff are included; optional stretch is separately identified. [Timing review](practice/client/designer/reviews/TIMING-AUDIT.md) records current exceptions and the pilot protocol.

### Choose your phase {#v2-git-readme-md-choose-your-phase}

[Phase one---certified](#v2-git-phase-one-certified-readme-md) establishes minimum understanding. [Phase two---proficient](#v2-git-phase-two-proficient-readme-md) requires substantive design/diagnosis/replay evidence with a finite core.

### Teaching concepts {#v2-git-readme-md-teaching-concepts}

The concept column and phase concept headings identify what an instructor can demonstrate. A useful demonstration shows the before state, the relevant change, and independent output/state evidence. The generated instructor companion reproduces concept explanations from these phase READMEs, so notes and challenges share a source.

Suggested destination: Monday preparation / advanced collaboration clinic. Advanced clinics and optional work require separate time; they do not silently consume protected core teaching windows.


## Source: git/phase-one-certified/README.md {#v2-git-phase-one-certified-readme-md}

## git: Phase one --- certified {#v2-git-phase-one-certified-readme-md-git-phase-one-certified}

This phase has a fixed core of 5 tasks. The minimum standard is a working result with the underlying tool concepts explained. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

### Prerequisites and workspace {#v2-git-phase-one-certified-readme-md-prerequisites-and-workspace}

Local Git forPhase1; authorized private GitHub sandbox, gh, and arranged reviewer forPhase2.

From the project root run:

``` bash
python3 scripts/challenge-v2.py prepare git phase-one-certified
cd .local/challenges-v2/git/phase-one-certified
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

### Starter behavior {#v2-git-phase-one-certified-readme-md-starter-behavior}

The starter contract is ordinary text; no deliberate broken files. Start with git --version.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter git phase-one-certified --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

### Timeline and completion standard {#v2-git-phase-one-certified-readme-md-timeline-and-completion-standard}

Core estimate: **60--90 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Task              Outcome                                           Minutes           Evidence
  ----------------- ------------------------------------------------- ----------------- -----------------------------------------------------------------------------------------------------------
  git-p1-01         Inspect the three working states                  12--18            Show the first commit contains only contract

  git-p1-02         Commit an intentional contract change             12--18            Use git show on each hash

  git-p1-03         Branch and combine compatible work                12--18            Show the final contract contains both edits

  git-p1-04         Resolve an ownership conflict                     12--18            Intentional failure: git merge upstream-owner should stop with an ownership conflict and a nonzero status

  git-p1-05         Restore a mistake and explain the final history   12--18            git status --porcelain must be empty
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Core challenges {#v2-git-phase-one-certified-readme-md-core-challenges}

#### git-p1-01: Inspect the three working states {#git-p1-01}

##### Concept: git-p1-01-concept --- Inspect the three working states {#v2-git-phase-one-certified-readme-md-concept-git-p1-01-concept-inspect-the-three-working-states}

A working tree contains files you can edit. The index contains the exact next commit; a commit records a snapshot with parent history. An untracked file is not included just because it is in the same directory. This distinction lets you explain what a review will see before sharing work.

```{=html}
<!-- instructor-demo: git-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-git-phase-one-certified-readme-md-challenge}

Copy contract.md into a new lab directory. Run git init -b main, configure a local training name/email, and inspect git status. Stage only contract.md, inspect git diff --cached, then make the initial commit. Create an untracked notes.txt and explain its status.

##### Hint {#v2-git-phase-one-certified-readme-md-hint}

Use git status --short and git log --oneline. Configure identity in this lab, not globally.

##### Check {#v2-git-phase-one-certified-readme-md-check}

Show the first commit contains only contract.md. Explain why notes.txt is absent and remove or ignore it before the final clean-state check.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### git-p1-02: Commit an intentional contract change {#git-p1-02}

##### Concept: git-p1-02-concept --- Commit an intentional contract change {#v2-git-phase-one-certified-readme-md-concept-git-p1-02-concept-commit-an-intentional-contract-change}

A useful commit has one reviewable purpose. Staging selects content, and the message explains the change rather than describing the button you pressed. A data contract is an effective example because a deadline clarification can alter a consumer expectation without altering the dataset itself.

```{=html}
<!-- instructor-demo: git-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-git-phase-one-certified-readme-md-challenge-1}

Change Delivery to daily before 09:00 UTC. Compare the working diff, stage the edit, inspect the staged diff and commit it. Add an escalation contact in a separate commit. Save the two commit hashes in your evidence note.

##### Hint {#v2-git-phase-one-certified-readme-md-hint-1}

git diff shows unstaged changes; git diff --cached shows staged changes.

##### Check {#v2-git-phase-one-certified-readme-md-check-1}

Use git show on each hash. A reviewer should see the deadline change independently from the escalation change. Explain how you would unstage an unrelated edit without discarding it.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### git-p1-03: Branch and combine compatible work {#git-p1-03}

##### Concept: git-p1-03-concept --- Branch and combine compatible work {#v2-git-phase-one-certified-readme-md-concept-git-p1-03-concept-branch-and-combine-compatible-work}

A branch names a line of development; it is not a second physical copy of every file. Git moves your working files when you switch branches. A merge preserves two lines of history and combines compatible changes. Seeing both edits in the final file matters more than merely receiving a merge success message.

```{=html}
<!-- instructor-demo: git-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-git-phase-one-certified-readme-md-challenge-2}

Create clarify-owner and clarify-grain from a common main commit. Change Owner on one branch and clarify the grain on the other. Merge both into main. Inspect the graph and identify the common ancestor.

##### Hint {#v2-git-phase-one-certified-readme-md-hint-2}

Use git switch -c and git merge. Commit before switching away from a change.

##### Check {#v2-git-phase-one-certified-readme-md-check-2}

Show the final contract contains both edits. Explain whether each merge was fast-forward or created a merge commit, using git log --graph --oneline --all.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### git-p1-04: Resolve an ownership conflict {#git-p1-04}

##### Concept: git-p1-04-concept --- Resolve an ownership conflict {#v2-git-phase-one-certified-readme-md-concept-git-p1-04-concept-resolve-an-ownership-conflict}

When two branches edit the same line differently, Git cannot decide the business meaning. Conflict markers delimit candidate text; retaining markers is not a solution. Resolve the contract by choosing its required owner while retaining useful escalation information from the competing proposal.

```{=html}
<!-- instructor-demo: git-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-git-phase-one-certified-readme-md-challenge-3}

From the same main state create upstream-owner with Owner: Operations team. On main set Owner: Analytics team. Merge upstream-owner. Resolve to Analytics team and retain Escalation: Training support. Stage and commit the resolution.

##### Hint {#v2-git-phase-one-certified-readme-md-hint-3}

Read git status after the merge fails. Edit the text itself, remove all conflict markers, then stage it.

##### Check {#v2-git-phase-one-certified-readme-md-check-3}

Intentional failure: git merge upstream-owner should stop with an ownership conflict and a nonzero status. That is the expected exercise state. After repair, show both parents in the resolution commit, no markers, and the agreed owner/escalation text.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### git-p1-05: Restore a mistake and explain the final history {#git-p1-05}

##### Concept: git-p1-05-concept --- Restore a mistake and explain the final history {#v2-git-phase-one-certified-readme-md-concept-git-p1-05-concept-restore-a-mistake-and-explain-the-final-history}

Restoring an uncommitted edit replaces working content from an existing snapshot. It differs from reverting a published commit, which creates new history. A safe local correction starts by inspecting the diff and checking that the work being removed really is the accidental edit.

```{=html}
<!-- instructor-demo: git-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-git-phase-one-certified-readme-md-challenge-4}

Append Accidental text to the contract, inspect the diff, then use git restore contract.md. Confirm the deadline and escalation survived. Write a short explanation of working tree, staging, branching and the ownership decision.

##### Hint {#v2-git-phase-one-certified-readme-md-hint-4}

Do this only inside your disposable lab, after all intended changes were committed.

##### Check {#v2-git-phase-one-certified-readme-md-check-4}

git status --porcelain must be empty. git show HEAD:contract.md must match the working file. Explain why restoring this mistake did not delete a previous commit.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### Phase completion {#v2-git-phase-one-certified-readme-md-phase-completion}

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

``` bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify git phase-one-certified --workspace .local/challenges-v2/git/phase-one-certified --mode offline
```

Execution boundary: Local Git; Phase 2 additionally uses an authorized remote. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

### Optional stretch {#v2-git-phase-one-certified-readme-md-optional-stretch}

Try a small variation after completing the core: change one input or contract condition in a second disposable copy, predict the result, and verify your prediction. This does not replace a core task or contribute to its timing budget.


## Source: git/phase-one-certified/starter/README.md {#v2-git-phase-one-certified-starter-readme-md}

## git starter assets {#v2-git-phase-one-certified-starter-readme-md-git-starter-assets}

Copy this directory into an isolated workspace before editing. The phase README defines the exact baseline command and the completion evidence. Generated databases, logs and evidence belong in that workspace. A starter check passing confirms the baseline is usable; it does not certify completed work.

Files supplied here are part of the learner pack. The instructor solution is stored separately under `challenges/v2-solutions`; it is excluded from the learner appendix and learner archive. See the parent [phase instructions](#v2-git-phase-one-certified-readme-md) for the authored-file list, prerequisites and any deliberate defect.


## Source: git/phase-two-proficient/README.md {#v2-git-phase-two-proficient-readme-md}

## git: Phase two --- proficient {#v2-git-phase-two-proficient-readme-md-git-phase-two-proficient}

This phase has a fixed core of 5 tasks. The advanced standard is a justified design or repair, actual behavioral proof, and a useful handoff. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

### Prerequisites and workspace {#v2-git-phase-two-proficient-readme-md-prerequisites-and-workspace}

Local Git forPhase1; authorized private GitHub sandbox, gh, and arranged reviewer forPhase2.

From the project root run:

``` bash
python3 scripts/challenge-v2.py prepare git phase-two-proficient
cd .local/challenges-v2/git/phase-two-proficient
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

### Starter behavior {#v2-git-phase-two-proficient-readme-md-starter-behavior}

The starter contract is ordinary text; no deliberate broken files. Start with git --version.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter git phase-two-proficient --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

### Timeline and completion standard {#v2-git-phase-two-proficient-readme-md-timeline-and-completion-standard}

Core estimate: **75--110 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Task              Outcome                                      Minutes           Evidence
  ----------------- -------------------------------------------- ----------------- ------------------------------------------------------------------------------------------------------
  git-p2-01         Clone and inspect a collaboration boundary   15--22            Record remote repository identity, local branch and upstream

  git-p2-02         Push and propose a scoped pull request       15--22            Retain the PR URL and commit hash; the remote PR diff must contain only the intended training change

  git-p2-03         Respond to a review with a second commit     15--22            Record the review/comment identifier, revision hash and the PR diff after the revision

  git-p2-04         Integrate concurrent upstream work           15--22            Show the upstream commit is an ancestor of your final branch

  git-p2-05         Read the final review and merge state        15--22            Record final PR/check/review state and the relevant remote commit
  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Core challenges {#v2-git-phase-two-proficient-readme-md-core-challenges}

#### git-p2-01: Clone and inspect a collaboration boundary {#git-p2-01}

##### Concept: git-p2-01-concept --- Clone and inspect a collaboration boundary {#v2-git-phase-two-proficient-readme-md-concept-git-p2-01-concept-clone-and-inspect-a-collaboration-boundary}

A clone copies repository history and configures a remote. A tracking branch records the relationship used by fetch/pull/push; it does not mean your local branch automatically contains every upstream change. Collaborating safely requires knowing which repository receives a push and which branch will receive a PR.

```{=html}
<!-- instructor-demo: git-p2-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-git-phase-two-proficient-readme-md-challenge}

Use the instructor-designated training repository. Clone it into a fresh workspace, inspect git remote -v and git branch -vv, and run gh auth status. Record the intended PR base and your permitted training branch prefix.

##### Hint {#v2-git-phase-two-proficient-readme-md-hint}

Use an existing authorized training identity. Do not copy tokens into evidence.

##### Check {#v2-git-phase-two-proficient-readme-md-check}

Record remote repository identity, local branch and upstream. A fixture rehearsal must be labelled simulated; live completion needs the actual sandbox repository.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### git-p2-02: Push and propose a scoped pull request {#git-p2-02}

##### Concept: git-p2-02-concept --- Push and propose a scoped pull request {#v2-git-phase-two-proficient-readme-md-concept-git-p2-02-concept-push-and-propose-a-scoped-pull-request}

Pushing publishes branch commits to a remote; a pull request proposes integrating those commits into another branch. They are separate actions. A useful PR explains the problem, the resulting contract and the verification, so a colleague can review without reconstructing your terminal history.

```{=html}
<!-- instructor-demo: git-p2-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-git-phase-two-proficient-readme-md-challenge-1}

Create a feature branch clarifying the delivery deadline/timezone. Commit, push with an upstream, and run gh pr create for the training repository. Include before/after behavior and how you checked the contract. Inspect the PR diff and status.

##### Hint {#v2-git-phase-two-proficient-readme-md-hint-1}

Check gh pr create --help and gh pr view --help on the installed version.

##### Check {#v2-git-phase-two-proficient-readme-md-check-1}

Retain the PR URL and commit hash; the remote PR diff must contain only the intended training change. Do not count a local Markdown PR description as a real PR.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### git-p2-03: Respond to a review with a second commit {#git-p2-03}

##### Concept: git-p2-03-concept --- Respond to a review with a second commit {#v2-git-phase-two-proficient-readme-md-concept-git-p2-03-concept-respond-to-a-review-with-a-second-commit}

Review is a conversation about behavior, maintainability and ownership. Changing code without explaining how it addresses the comment can leave the reviewer uncertain. A second commit allows the review record to distinguish the original proposal from the response.

```{=html}
<!-- instructor-demo: git-p2-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-git-phase-two-proficient-readme-md-challenge-2}

Ask the instructor or paired reviewer to provide the supplied review scenario through the approved classroom workflow. Clarify the escalation contact and timezone, commit the revision and push it. Explain which comment it addresses.

##### Hint {#v2-git-phase-two-proficient-readme-md-hint-2}

The reviewer may use the prepared scenario in review-scenario.json. Instructor preparation includes arranging the reviewer.

##### Check {#v2-git-phase-two-proficient-readme-md-check-2}

Record the review/comment identifier, revision hash and the PR diff after the revision. Confirm the new commit is present remotely. This exercise does not authorize the assistant to send messages to others.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### git-p2-04: Integrate concurrent upstream work {#git-p2-04}

##### Concept: git-p2-04-concept --- Integrate concurrent upstream work {#v2-git-phase-two-proficient-readme-md-concept-git-p2-04-concept-integrate-concurrent-upstream-work}

Fetch obtains remote commits; merging or rebasing decides how they enter your branch. Pull combines these operations according to configuration. Upstream changes can arrive while your PR is open, so the final reviewed result must include both the contract clarification and the new shared input classification.

```{=html}
<!-- instructor-demo: git-p2-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-git-phase-two-proficient-readme-md-challenge-3}

Have the instructor supply the planned main-branch input classification change. Fetch origin, compare your branch to origin/main, then merge origin/main into the feature branch. Resolve any conflict by preserving both requirements, inspect and push.

##### Hint {#v2-git-phase-two-proficient-readme-md-hint-3}

Use git log --left-right --oneline HEAD...origin/main before combining history.

##### Check {#v2-git-phase-two-proficient-readme-md-check-3}

Show the upstream commit is an ancestor of your final branch. Both classification and your delivery/escalation changes must survive. Explain the difference between fetching and integrating.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### git-p2-05: Read the final review and merge state {#git-p2-05}

##### Concept: git-p2-05-concept --- Read the final review and merge state {#v2-git-phase-two-proficient-readme-md-concept-git-p2-05-concept-read-the-final-review-and-merge-state}

A green command exit cannot prove a reviewer approved the change or that branch protections were met. Advanced evidence includes the actual PR state, review outcome, checks and resulting main history. Some sandboxes deliberately leave a PR open; that state should be reported honestly instead of fabricating a merge.

```{=html}
<!-- instructor-demo: git-p2-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-git-phase-two-proficient-readme-md-challenge-4}

Inspect gh pr view and gh pr checks, explain the review state and merge eligibility, and follow the instructor sandbox merge policy. Synchronize local main after any authorized merge. Save a short collaboration handoff.

##### Hint {#v2-git-phase-two-proficient-readme-md-hint-4}

A real reviewer and repository permissions are prerequisites; missing access is a blocked live result.

##### Check {#v2-git-phase-two-proficient-readme-md-check-4}

Record final PR/check/review state and the relevant remote commit. Show the clean local branch and explain any unresolved gate. Optional stretch: compare a merge workflow with a rebase in a second disposable lab; do not rewrite the shared branch.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### Phase completion {#v2-git-phase-two-proficient-readme-md-phase-completion}

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

``` bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify git phase-two-proficient --workspace .local/challenges-v2/git/phase-two-proficient --mode offline
```

Execution boundary: Local Git; Phase 2 additionally uses an authorized remote. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

### Optional stretch {#v2-git-phase-two-proficient-readme-md-optional-stretch}

See the [stretch index](#v2-git-phase-two-proficient-stretch-readme-md). Each route has its own prerequisites, timing and completion check; none is part of this fixed core.


## Source: git/phase-two-proficient/starter/README.md {#v2-git-phase-two-proficient-starter-readme-md}

## git starter assets {#v2-git-phase-two-proficient-starter-readme-md-git-starter-assets}

Copy this directory into an isolated workspace before editing. The phase README defines the exact baseline command and the completion evidence. Generated databases, logs and evidence belong in that workspace. A starter check passing confirms the baseline is usable; it does not certify completed work.

Files supplied here are part of the learner pack. The instructor solution is stored separately under `challenges/v2-solutions`; it is excluded from the learner appendix and learner archive. See the parent [phase instructions](#v2-git-phase-two-proficient-readme-md) for the authored-file list, prerequisites and any deliberate defect.


## Source: git/phase-two-proficient/stretch/README.md {#v2-git-phase-two-proficient-stretch-readme-md}

## git: optional stretch selection {#v2-git-phase-two-proficient-stretch-readme-md-git-optional-stretch-selection}

Explore rebase/merge/reflog in a disposable repository (30--60 minutes). Explain history preservation and recovery; no rewriting of shared training branches.

These routes are separate from core completion. Record timing exceptions rather than shortening an exercise during the audit. Instructor review should select one follow-up based on the learner goal and available environment.


## Source: docker/README.md {#v2-docker-readme-md}

## docker challenges {#v2-docker-readme-md-docker-challenges}

This route develops minimum competence followed by advanced behavioral proof. Read concept explanations before attempting the task; retain commands/results and your reasoning.

### Before you start {#v2-docker-readme-md-before-you-start}

Docker daemon plus pulled python:3.11-slim image. No remote data account. Work in a copied phase workspace. Phase 2, when offered, supplies its entry fixture. [Pack navigation](#v2-readme-md) explains the course/clinic placement and version selection.

### Suggested timeline and tasks {#v2-docker-readme-md-suggested-timeline-and-tasks}

  -----------------------------------------------------------------------------------------------------------------------------------------------
  Phase       Task ID                         Title                                             Teaching concept       Core/stretch   Minutes
  ----------- ------------------------------- ------------------------------------------------- ---------------------- -------------- -----------
  Phase 1     [docker-p1-01](#docker-p1-01)   Run an image and inspect the lifecycle            docker-p1-01-concept   core           12--18

  Phase 1     [docker-p1-02](#docker-p1-02)   Explore an interactive shell                      docker-p1-02-concept   core           12--18

  Phase 1     [docker-p1-03](#docker-p1-03)   Use a bounded bind mount                          docker-p1-03-concept   core           12--18

  Phase 1     [docker-p1-04](#docker-p1-04)   Author and run a simple holdings image            docker-p1-04-concept   core           12--18

  Phase 1     [docker-p1-05](#docker-p1-05)   Prove repeatability and clean scoped resources    docker-p1-05-concept   core           12--18

  Phase 2     [docker-p2-01](#docker-p2-01)   Separate named build targets                      docker-p2-01-concept   core           15--22

  Phase 2     [docker-p2-02](#docker-p2-02)   Gate the runtime on a tested artifact             docker-p2-02-concept   core           15--22

  Phase 2     [docker-p2-03](#docker-p2-03)   Run with a bounded runtime user                   docker-p2-03-concept   core           15--22

  Phase 2     [docker-p2-04](#docker-p2-04)   Keep runtime contents focused                     docker-p2-04-concept   core           15--22

  Phase 2     [docker-p2-05](#docker-p2-05)   Repair a path assumption and explain the result   docker-p2-05-concept   core           15--22
  -----------------------------------------------------------------------------------------------------------------------------------------------

Inclusive phase estimates: Phase 1 60--90 minutes; Phase 2 75--110 minutes. These estimates are unpiloted. Reading, normal waits, checking and handoff are included; optional stretch is separately identified. [Timing review](practice/client/designer/reviews/TIMING-AUDIT.md) records current exceptions and the pilot protocol.

### Choose your phase {#v2-docker-readme-md-choose-your-phase}

[Phase one---certified](#v2-docker-phase-one-certified-readme-md) establishes minimum understanding. [Phase two---proficient](#v2-docker-phase-two-proficient-readme-md) requires substantive design/diagnosis/replay evidence with a finite core.

### Teaching concepts {#v2-docker-readme-md-teaching-concepts}

The concept column and phase concept headings identify what an instructor can demonstrate. A useful demonstration shows the before state, the relevant change, and independent output/state evidence. The generated instructor companion reproduces concept explanations from these phase READMEs, so notes and challenges share a source.

Suggested destination: Wednesday Docker practical / advanced image clinic. Advanced clinics and optional work require separate time; they do not silently consume protected core teaching windows.


## Source: docker/phase-one-certified/README.md {#v2-docker-phase-one-certified-readme-md}

## docker: Phase one --- certified {#v2-docker-phase-one-certified-readme-md-docker-phase-one-certified}

This phase has a fixed core of 5 tasks. The minimum standard is a working result with the underlying tool concepts explained. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

### Prerequisites and workspace {#v2-docker-phase-one-certified-readme-md-prerequisites-and-workspace}

Docker daemon plus pulled python:3.11-slim image. No remote data account.

From the project root run:

``` bash
python3 scripts/challenge-v2.py prepare docker phase-one-certified
cd .local/challenges-v2/docker/phase-one-certified
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

### Starter behavior {#v2-docker-phase-one-certified-readme-md-starter-behavior}

docker build -t v2-starter . then docker run --rm v2-starter prints the documented placeholder. Python app/test also work outside Docker.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter docker phase-one-certified --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

### Timeline and completion standard {#v2-docker-phase-one-certified-readme-md-timeline-and-completion-standard}

Core estimate: **60--90 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Task              Outcome                                          Minutes           Evidence
  ----------------- ------------------------------------------------ ----------------- ----------------------------------------------------------------------------------------------------------
  docker-p1-01      Run an image and inspect the lifecycle           12--18            Show hello holdings in the logs and exit code 0

  docker-p1-02      Explore an interactive shell                     12--18            Explain the result of the second-file check

  docker-p1-03      Use a bounded bind mount                         12--18            Show the six-holding summary and an expected read-only write failure

  docker-p1-04      Author and run a simple holdings image           12--18            The starter image intentionally prints Valid starter: complete the holdings image and exits successfully

  docker-p1-05      Prove repeatability and clean scoped resources   12--18            Retain both outputs and matching image identity
  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Core challenges {#v2-docker-phase-one-certified-readme-md-core-challenges}

#### docker-p1-01: Run an image and inspect the lifecycle {#docker-p1-01}

##### Concept: docker-p1-01-concept --- Run an image and inspect the lifecycle {#v2-docker-phase-one-certified-readme-md-concept-docker-p1-01-concept-run-an-image-and-inspect-the-lifecycle}

An image is a packaged filesystem and startup configuration. A container is an execution of that image with a writable layer and process state. A container exits when its main process exits; running a tiny Python summary to completion does not require keeping a service alive.

```{=html}
<!-- instructor-demo: docker-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-docker-phase-one-certified-readme-md-challenge}

Run docker version and docker info, then docker run --name v2-hello python:3.11-slim python -c "print('hello holdings')". Inspect its exit code, logs and image ID. Remove only v2-hello afterwards.

##### Hint {#v2-docker-phase-one-certified-readme-md-hint}

Use docker ps -a to include stopped containers. Instructor preparation supplies Docker and a pulled base image.

##### Check {#v2-docker-phase-one-certified-readme-md-check}

Show hello holdings in the logs and exit code 0. Explain why the container is stopped and how that differs from deleting its image.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### docker-p1-02: Explore an interactive shell {#docker-p1-02}

##### Concept: docker-p1-02-concept --- Explore an interactive shell {#v2-docker-phase-one-certified-readme-md-concept-docker-p1-02-concept-explore-an-interactive-shell}

An interactive shell lets you inspect the container environment independently from the host. Its root filesystem comes from the image plus the container writable layer. Files created there disappear when that disposable container is removed unless you deliberately persist them.

```{=html}
<!-- instructor-demo: docker-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-docker-phase-one-certified-readme-md-challenge-1}

Start docker run --rm -it python:3.11-slim bash. Inspect pwd, Python version and /etc/os-release. Create /tmp/inside.txt, exit, then start a new container and test whether that file exists.

##### Hint {#v2-docker-phase-one-certified-readme-md-hint-1}

The terminal flags attach standard input and a TTY; --rm removes the exited container.

##### Check {#v2-docker-phase-one-certified-readme-md-check-1}

Explain the result of the second-file check. Retain the version and OS observations. Do not claim the container is a virtual machine or has a separate kernel.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### docker-p1-03: Use a bounded bind mount {#docker-p1-03}

##### Concept: docker-p1-03-concept --- Use a bounded bind mount {#v2-docker-phase-one-certified-readme-md-concept-docker-p1-03-concept-use-a-bounded-bind-mount}

A bind mount exposes a chosen host path at a container path. It can make inputs available without rebuilding the image, but the path and access mode are part of the runtime contract. A read-only input mount prevents the summarizer from changing the source fixture.

```{=html}
<!-- instructor-demo: docker-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-docker-phase-one-certified-readme-md-challenge-2}

From the copied starter, run the supplied app using a read-only mount of app/ at /app and a working directory of /app. Compare the input on the host and in the container. Try a container-side write to that input directory and explain the denied write.

##### Hint {#v2-docker-phase-one-certified-readme-md-hint-2}

Use an absolute host path from pwd and the :ro mount suffix. Do not mount the entire host root.

##### Check {#v2-docker-phase-one-certified-readme-md-check-2}

Show the six-holding summary and an expected read-only write failure. Explain which data is in the image and which comes from the mount.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### docker-p1-04: Author and run a simple holdings image {#docker-p1-04}

##### Concept: docker-p1-04-concept --- Author and run a simple holdings image {#v2-docker-phase-one-certified-readme-md-concept-docker-p1-04-concept-author-and-run-a-simple-holdings-image}

A Dockerfile declares ordered filesystem/runtime instructions. WORKDIR changes subsequent relative paths; COPY brings build-context content into the image; CMD defines the default process. Choosing these deliberately turns the supplied app into a repeatable workload.

```{=html}
<!-- instructor-demo: docker-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-docker-phase-one-certified-readme-md-challenge-3}

Replace the benign placeholder Dockerfile with a Python 3.11 slim image, working directory /app, copied app files and default summarize.py command. Build as v2-holdings:p1, run it without a mount, and explain each instruction.

##### Hint {#v2-docker-phase-one-certified-readme-md-hint-3}

The build context is the copied starter directory; COPY cannot read an arbitrary parent directory.

##### Check {#v2-docker-phase-one-certified-readme-md-check-3}

The starter image intentionally prints Valid starter: complete the holdings image and exits successfully. That is baseline behavior, not a solution. The completed image must print Portfolio summary and 6 holdings, total market value 12,011,626.50.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### docker-p1-05: Prove repeatability and clean scoped resources {#docker-p1-05}

##### Concept: docker-p1-05-concept --- Prove repeatability and clean scoped resources {#v2-docker-phase-one-certified-readme-md-concept-docker-p1-05-concept-prove-repeatability-and-clean-scoped-resources}

Repeatability means the same inputs produce the same useful result in a fresh run. It includes understanding the difference between image state and container state. Cleanup should target names created by this exercise, so one learner does not remove another learner runtime.

```{=html}
<!-- instructor-demo: docker-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-docker-phase-one-certified-readme-md-challenge-4}

Run the completed image twice with --rm. Inspect its configured command and working directory. Explain how changing holdings.csv on the host would affect an already-built image. Remove only the exercise image when instructed.

##### Hint {#v2-docker-phase-one-certified-readme-md-hint-4}

Use docker image inspect v2-holdings:p1. Rebuilding is necessary for a copied input change.

##### Check {#v2-docker-phase-one-certified-readme-md-check-4}

Retain both outputs and matching image identity. Explain the process exit and the required rebuild for changed copied data. Do not use docker system prune as a lab cleanup command.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### Phase completion {#v2-docker-phase-one-certified-readme-md-phase-completion}

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

``` bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify docker phase-one-certified --workspace .local/challenges-v2/docker/phase-one-certified --mode offline
```

Execution boundary: Docker build/run; host Python checks supporting app only. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

### Optional stretch {#v2-docker-phase-one-certified-readme-md-optional-stretch}

Try a small variation after completing the core: change one input or contract condition in a second disposable copy, predict the result, and verify your prediction. This does not replace a core task or contribute to its timing budget.


## Source: docker/phase-one-certified/starter/README.md {#v2-docker-phase-one-certified-starter-readme-md}

## docker starter assets {#v2-docker-phase-one-certified-starter-readme-md-docker-starter-assets}

Copy this directory into an isolated workspace before editing. The phase README defines the exact baseline command and the completion evidence. Generated databases, logs and evidence belong in that workspace. A starter check passing confirms the baseline is usable; it does not certify completed work.

Files supplied here are part of the learner pack. The instructor solution is stored separately under `challenges/v2-solutions`; it is excluded from the learner appendix and learner archive. See the parent [phase instructions](#v2-docker-phase-one-certified-readme-md) for the authored-file list, prerequisites and any deliberate defect.


## Source: docker/phase-two-proficient/README.md {#v2-docker-phase-two-proficient-readme-md}

## docker: Phase two --- proficient {#v2-docker-phase-two-proficient-readme-md-docker-phase-two-proficient}

This phase has a fixed core of 5 tasks. The advanced standard is a justified design or repair, actual behavioral proof, and a useful handoff. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

### Prerequisites and workspace {#v2-docker-phase-two-proficient-readme-md-prerequisites-and-workspace}

Docker daemon plus pulled python:3.11-slim image. No remote data account.

From the project root run:

``` bash
python3 scripts/challenge-v2.py prepare docker phase-two-proficient
cd .local/challenges-v2/docker/phase-two-proficient
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

### Starter behavior {#v2-docker-phase-two-proficient-readme-md-starter-behavior}

docker build -t v2-starter . then docker run --rm v2-starter prints the documented placeholder. Python app/test also work outside Docker.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter docker phase-two-proficient --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

### Timeline and completion standard {#v2-docker-phase-two-proficient-readme-md-timeline-and-completion-standard}

Core estimate: **75--110 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Task              Outcome                                           Minutes           Evidence
  ----------------- ------------------------------------------------- ----------------- -----------------------------------------------------------------------------------------------
  docker-p2-01      Separate named build targets                      15--22            Run both tagged targets and retain their different successful outputs

  docker-p2-02      Gate the runtime on a tested artifact             15--22            Intentional experiment: the changed fixture must make the build fail at the summary assertion

  docker-p2-03      Run with a bounded runtime user                   15--22            Show UID 10001 and the correct summary

  docker-p2-04      Keep runtime contents focused                     15--22            Record the differing file lists and commands

  docker-p2-05      Repair a path assumption and explain the result   15--22            Intentional experiment: the default app command should fail in the wrong directory
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Core challenges {#v2-docker-phase-two-proficient-readme-md-core-challenges}

#### docker-p2-01: Separate named build targets {#docker-p2-01}

##### Concept: docker-p2-01-concept --- Separate named build targets {#v2-docker-phase-two-proficient-readme-md-concept-docker-p2-01-concept-separate-named-build-targets}

A multistage Dockerfile can define a test environment and a smaller runtime environment. Building one target does not automatically tag every stage as an image. Separate --target invocations explicitly select which final result you want and make the two contracts inspectable.

```{=html}
<!-- instructor-demo: docker-p2-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-docker-phase-two-proficient-readme-md-challenge}

Create base, test and runtime named stages. Build test as v2-holdings:test and runtime as v2-holdings:runtime. The test target runs test_summary.py; the runtime target runs summarize.py.

##### Hint {#v2-docker-phase-two-proficient-readme-md-hint}

Use FROM ... AS name and COPY --from=test for the selected runtime artifacts.

##### Check {#v2-docker-phase-two-proficient-readme-md-check}

Run both tagged targets and retain their different successful outputs. Explain which stages each build needed and why a single default build is not two separately tagged images.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### docker-p2-02: Gate the runtime on a tested artifact {#docker-p2-02}

##### Concept: docker-p2-02-concept --- Gate the runtime on a tested artifact {#v2-docker-phase-two-proficient-readme-md-concept-docker-p2-02-concept-gate-the-runtime-on-a-tested-artifact}

A build-time test can reject a broken artifact before producing the runtime image. A check that merely searches for the word test in the Dockerfile does not prove behavior. The oracle here is the supplied expected summary, which must actually execute against the copied application.

```{=html}
<!-- instructor-demo: docker-p2-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-docker-phase-two-proficient-readme-md-challenge-1}

Add RUN python test_summary.py in the test stage. Build it successfully, then change one holding amount in a temporary copy and rebuild. Diagnose the oracle failure, restore the fixture and rebuild the runtime.

##### Hint {#v2-docker-phase-two-proficient-readme-md-hint-1}

Keep the original workspace intact; make the controlled defect in a second copied build context.

##### Check {#v2-docker-phase-two-proficient-readme-md-check-1}

Intentional experiment: the changed fixture must make the build fail at the summary assertion. After restoration, the build and runtime output must pass. Record the failed and repaired commands.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### docker-p2-03: Run with a bounded runtime user {#docker-p2-03}

##### Concept: docker-p2-03-concept --- Run with a bounded runtime user {#v2-docker-phase-two-proficient-readme-md-concept-docker-p2-03-concept-run-with-a-bounded-runtime-user}

A runtime user determines the application process identity. Choosing a non-root user and readable owned inputs makes the runtime contract explicit. The learning objective is to explain why the app still works and which paths it can modify, rather than treating USER as a decorative Dockerfile line.

```{=html}
<!-- instructor-demo: docker-p2-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-docker-phase-two-proficient-readme-md-challenge-2}

Create UID 10001 in the runtime stage, copy the app/input with appropriate ownership and set USER 10001. Inspect id inside the runtime container and test that the summary works.

##### Hint {#v2-docker-phase-two-proficient-readme-md-hint-2}

COPY --chown can set ownership while copying from a named stage.

##### Check {#v2-docker-phase-two-proficient-readme-md-check-2}

Show UID 10001 and the correct summary. Explain which input permissions are required and which system paths are not writable to that user.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### docker-p2-04: Keep runtime contents focused {#docker-p2-04}

##### Concept: docker-p2-04-concept --- Keep runtime contents focused {#v2-docker-phase-two-proficient-readme-md-concept-docker-p2-04-concept-keep-runtime-contents-focused}

Every file included in an image becomes part of its distribution and runtime maintenance. A test stage may need test_summary.py while the runtime needs only the summarizer and data. Inspecting actual contents proves the separation more clearly than comparing image sizes alone.

```{=html}
<!-- instructor-demo: docker-p2-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-docker-phase-two-proficient-readme-md-challenge-3}

Copy only summarize.py and holdings.csv into runtime. Run ls /app in both targets. Confirm test_summary.py is absent from runtime. Compare their configured users, commands and image sizes, explaining why size is supporting evidence.

##### Hint {#v2-docker-phase-two-proficient-readme-md-hint-3}

Override the runtime command with ls or python -c when inspecting.

##### Check {#v2-docker-phase-two-proficient-readme-md-check-3}

Record the differing file lists and commands. Runtime must still produce the expected output without tests being present.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### docker-p2-05: Repair a path assumption and explain the result {#docker-p2-05}

##### Concept: docker-p2-05-concept --- Repair a path assumption and explain the result {#v2-docker-phase-two-proficient-readme-md-concept-docker-p2-05-concept-repair-a-path-assumption-and-explain-the-result}

A container command executes relative to its working directory unless given an absolute path. A wrong WORKDIR or COPY destination can break a perfectly valid app. A meaningful repair aligns image contents and process configuration rather than hiding the failure by running a different ad hoc command every time.

```{=html}
<!-- instructor-demo: docker-p2-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-docker-phase-two-proficient-readme-md-challenge-4}

In a disposable Dockerfile copy, deliberately change the runtime WORKDIR to /wrong. Build and run it, identify the missing-file symptom, repair the path and repeat both target checks. Write a short handoff explaining build/runtime boundaries.

##### Hint {#v2-docker-phase-two-proficient-readme-md-hint-4}

Inspect the image configured working directory and run a listing before editing Python code.

##### Check {#v2-docker-phase-two-proficient-readme-md-check-4}

Intentional experiment: the default app command should fail in the wrong directory. Repair must restore the default runtime output and non-root UID. Optional stretch: examine cache invalidation after a data-only change; keep it outside core time.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### Phase completion {#v2-docker-phase-two-proficient-readme-md-phase-completion}

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

``` bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify docker phase-two-proficient --workspace .local/challenges-v2/docker/phase-two-proficient --mode offline
```

Execution boundary: Docker build/run; host Python checks supporting app only. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

### Optional stretch {#v2-docker-phase-two-proficient-readme-md-optional-stretch}

See the [stretch index](#v2-docker-phase-two-proficient-stretch-readme-md). Each route has its own prerequisites, timing and completion check; none is part of this fixed core.


## Source: docker/phase-two-proficient/starter/README.md {#v2-docker-phase-two-proficient-starter-readme-md}

## docker starter assets {#v2-docker-phase-two-proficient-starter-readme-md-docker-starter-assets}

Copy this directory into an isolated workspace before editing. The phase README defines the exact baseline command and the completion evidence. Generated databases, logs and evidence belong in that workspace. A starter check passing confirms the baseline is usable; it does not certify completed work.

Files supplied here are part of the learner pack. The instructor solution is stored separately under `challenges/v2-solutions`; it is excluded from the learner appendix and learner archive. See the parent [phase instructions](#v2-docker-phase-two-proficient-readme-md) for the authored-file list, prerequisites and any deliberate defect.


## Source: docker/phase-two-proficient/stretch/README.md {#v2-docker-phase-two-proficient-stretch-readme-md}

## docker: optional stretch selection {#v2-docker-phase-two-proficient-stretch-readme-md-docker-optional-stretch-selection}

Inspect cache invalidation and image layers (30--60 minutes); predict which stages rerun after a data-only edit and prove it.

These routes are separate from core completion. Record timing exceptions rather than shortening an exercise during the audit. Instructor review should select one follow-up based on the learner goal and available environment.


## Source: dbt/README.md {#v2-dbt-readme-md}

## dbt challenges {#v2-dbt-readme-md-dbt-challenges}

This route develops minimum competence followed by advanced behavioral proof. Read concept explanations before attempting the task; retain commands/results and your reasoning.

### Before you start {#v2-dbt-readme-md-before-you-start}

Prepared dbt-core1.10.13, dbt-duckdb1.9.6, DuckDB1.4.1 local environment. Optional connected profile needs Databricks adapter and isolated provisioned V2_DB_SCHEMA. Work in a copied phase workspace. Phase 2, when offered, supplies its entry fixture. [Pack navigation](#v2-readme-md) explains the course/clinic placement and version selection.

### Suggested timeline and tasks {#v2-dbt-readme-md-suggested-timeline-and-tasks}

  ------------------------------------------------------------------------------------------------------------------------------------------
  Phase       Task ID                   Title                                                 Teaching concept    Core/stretch   Minutes
  ----------- ------------------------- ----------------------------------------------------- ------------------- -------------- -----------
  Phase 1     [dbt-p1-01](#dbt-p1-01)   Inspect the project and source grain                  dbt-p1-01-concept   core           15--22

  Phase 1     [dbt-p1-02](#dbt-p1-02)   Declare and use sources                               dbt-p1-02-concept   core           15--22

  Phase 1     [dbt-p1-03](#dbt-p1-03)   Normalize type, unit and key contracts                dbt-p1-03-concept   core           15--22

  Phase 1     [dbt-p1-04](#dbt-p1-04)   Build a useful mart through ref                       dbt-p1-04-concept   core           15--22

  Phase 1     [dbt-p1-05](#dbt-p1-05)   Add minimum key and relationship proof                dbt-p1-05-concept   core           15--22

  Phase 2     [dbt-p2-01](#dbt-p2-01)   Diagnose a join fan-out before repair                 dbt-p2-01-concept   core           18--24

  Phase 2     [dbt-p2-02](#dbt-p2-02)   Repair enrichment at the intended grain               dbt-p2-02-concept   core           18--24

  Phase 2     [dbt-p2-03](#dbt-p2-03)   Write reconciliation that detects the negative case   dbt-p2-03-concept   core           18--24

  Phase 2     [dbt-p2-04](#dbt-p2-04)   Prove incremental update and replay behavior          dbt-p2-04-concept   core           18--24

  Phase 2     [dbt-p2-05](#dbt-p2-05)   Explain dependency impact and hand over               dbt-p2-05-concept   core           18--24
  ------------------------------------------------------------------------------------------------------------------------------------------

Inclusive phase estimates: Phase 1 75--110 minutes; Phase 2 90--120 minutes. These estimates are unpiloted. Reading, normal waits, checking and handoff are included; optional stretch is separately identified. [Timing review](practice/client/designer/reviews/TIMING-AUDIT.md) records current exceptions and the pilot protocol.

### Choose your phase {#v2-dbt-readme-md-choose-your-phase}

[Phase one---certified](#v2-dbt-phase-one-certified-readme-md) establishes minimum understanding. [Phase two---proficient](#v2-dbt-phase-two-proficient-readme-md) requires substantive design/diagnosis/replay evidence with a finite core.

### Teaching concepts {#v2-dbt-readme-md-teaching-concepts}

The concept column and phase concept headings identify what an instructor can demonstrate. A useful demonstration shows the before state, the relevant change, and independent output/state evidence. The generated instructor companion reproduces concept explanations from these phase READMEs, so notes and challenges share a source.

Suggested destination: Wednesday dbt practical / advanced transformation clinic. Advanced clinics and optional work require separate time; they do not silently consume protected core teaching windows.


## Source: dbt/phase-one-certified/README.md {#v2-dbt-phase-one-certified-readme-md}

## dbt: Phase one --- certified {#v2-dbt-phase-one-certified-readme-md-dbt-phase-one-certified}

This phase has a fixed core of 5 tasks. The minimum standard is a working result with the underlying tool concepts explained. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

### Prerequisites and workspace {#v2-dbt-phase-one-certified-readme-md-prerequisites-and-workspace}

Prepared dbt-core1.10.13, dbt-duckdb1.9.6, DuckDB1.4.1 local environment. Optional connected profile needs Databricks adapter and isolated provisioned V2_DB_SCHEMA.

From the project root run:

``` bash
python3 scripts/challenge-v2.py prepare dbt phase-one-certified
cd .local/challenges-v2/dbt/phase-one-certified
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

### Local tool preparation {#v2-dbt-phase-one-certified-readme-md-local-tool-preparation}

The instructor runs `bash scripts/setup-v2-tools.sh` once from the project root. Before changing into your copied workspace, activate `.local/v2-tools/bin/activate` to make the pinned `dbt` executable available. For Airflow, use `.local/v2-airflow/bin/python` with a workspace-specific `AIRFLOW_HOME`; do not mix these two Python environments. The verifier supplies these paths automatically in a fresh copy.

### Starter behavior {#v2-dbt-phase-one-certified-readme-md-starter-behavior}

dbt seed --profiles-dir . and dbt build --profiles-dir . succeed on supplied baseline. Phase 2 exposure is a labelled placeholder.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter dbt phase-one-certified --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

### Timeline and completion standard {#v2-dbt-phase-one-certified-readme-md-timeline-and-completion-standard}

Core estimate: **75--110 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Task              Outcome                                  Minutes           Evidence
  ----------------- ---------------------------------------- ----------------- ----------------------------------------------------------------------------------------------------
  dbt-p1-01         Inspect the project and source grain     15--22            Show five holdings, three distinct funds and total 250

  dbt-p1-02         Declare and use sources                  15--22            Run dbt run --select stg_holdings stg_funds --profiles-dir .

  dbt-p1-03         Normalize type, unit and key contracts   15--22            The staged row count remains five, its total remains 250, and the zero-value C holding is retained

  dbt-p1-04         Build a useful mart through ref          15--22            Compare against A:2 holdings/150, B:2/100, C:1/0

  dbt-p1-05         Add minimum key and relationship proof   15--22            All tests must pass on a fresh build
  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Core challenges {#v2-dbt-phase-one-certified-readme-md-core-challenges}

#### dbt-p1-01: Inspect the project and source grain {#dbt-p1-01}

##### Concept: dbt-p1-01-concept --- Inspect the project and source grain {#v2-dbt-phase-one-certified-readme-md-concept-dbt-p1-01-concept-inspect-the-project-and-source-grain}

dbt compiles SQL models into relations and orders them using declared dependencies. The supplied seeds are small deterministic training inputs: five holding rows, three funds and a total market value of 250. Holding grain is fund/instrument; fund grain is fund_id. Profile configuration selects an adapter and database, not a business transformation.

```{=html}
<!-- instructor-demo: dbt-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-dbt-phase-one-certified-readme-md-challenge}

Activate the prepared local dbt environment. In your copied starter run dbt --version, dbt debug --profiles-dir ., dbt seed --profiles-dir ., then dbt build --profiles-dir . for the benign status model. Inspect both CSVs and record their keys/units.

##### Hint {#v2-dbt-phase-one-certified-readme-md-hint}

The default local route uses DuckDB; it needs no cloud account. The connected route uses the provided Databricks profile after instructor provisioning.

##### Check {#v2-dbt-phase-one-certified-readme-md-check}

Show five holdings, three distinct funds and total 250. The status model is intentionally a valid scaffold. Record adapter/version and distinguish the local rehearsal from a connected run.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### dbt-p1-02: Declare and use sources {#dbt-p1-02}

##### Concept: dbt-p1-02-concept --- Declare and use sources {#v2-dbt-phase-one-certified-readme-md-concept-dbt-p1-02-concept-declare-and-use-sources}

source names describe the external input boundary and let lineage/tests refer to it. A source declaration identifies a relation; it does not load CSVs by itself. In this local exercise seeds create the input relations in main, while sources teach the stable logical interface consumed by staging.

```{=html}
<!-- instructor-demo: dbt-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-dbt-phase-one-certified-readme-md-challenge-1}

Inspect sources.yml, verify its schema matches your seeded tables, and create stg_holdings.sql using source(training, holdings). Create stg_funds.sql from the funds source. Remove the status model when you have real staging outputs.

##### Hint {#v2-dbt-phase-one-certified-readme-md-hint-1}

Use the Jinja source function shown in the project references; quote its two logical names.

##### Check {#v2-dbt-phase-one-certified-readme-md-check-1}

Run dbt run --select stg_holdings stg_funds --profiles-dir . Inspect compiled SQL and explain the difference between the logical source name and physical table name.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### dbt-p1-03: Normalize type, unit and key contracts {#dbt-p1-03}

##### Concept: dbt-p1-03-concept --- Normalize type, unit and key contracts {#v2-dbt-phase-one-certified-readme-md-concept-dbt-p1-03-concept-normalize-type-unit-and-key-contracts}

Staging gives downstream models a consistent shape. A cast should preserve the meaning of a money amount and expose conversion errors, not silently coerce an invalid string. Retain fund_id and instrument_id because the next join and the holding grain rely on them.

```{=html}
<!-- instructor-demo: dbt-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-dbt-phase-one-certified-readme-md-challenge-2}

Cast market_value to decimal(18,2), preserve both identifiers, and inspect all staged rows. Explain that the fixture amounts are a single teaching currency and are already whole money units, not cents.

##### Hint {#v2-dbt-phase-one-certified-readme-md-hint-2}

Compare column names and values before writing a mart. Avoid SELECT DISTINCT as a substitute for a declared grain.

##### Check {#v2-dbt-phase-one-certified-readme-md-check-2}

The staged row count remains five, its total remains 250, and the zero-value C holding is retained. Explain why filtering that zero would alter the holdings-count meaning.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### dbt-p1-04: Build a useful mart through ref {#dbt-p1-04}

##### Concept: dbt-p1-04-concept --- Build a useful mart through ref {#v2-dbt-phase-one-certified-readme-md-concept-dbt-p1-04-concept-build-a-useful-mart-through-ref}

ref declares a dependency on another dbt model and resolves its physical relation. A mart answers a consumer question at a declared grain. Here the output is one row per fund, including a zero-valued fund, with a holding count and market-value exposure. A left join driven by the fund dimension preserves the fund population.

```{=html}
<!-- instructor-demo: dbt-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-dbt-phase-one-certified-readme-md-challenge-3}

Create fund_exposure.sql using ref(stg_funds) and ref(stg_holdings). Group by fund identifier/name. Produce holdings and exposure, using a zero default for absent money amounts. Build the mart and its parents.

##### Hint {#v2-dbt-phase-one-certified-readme-md-hint-3}

Use dbt run --select +fund_exposure --profiles-dir . Decide what count(column) means on an unmatched left join.

##### Check {#v2-dbt-phase-one-certified-readme-md-check-3}

Compare against A:2 holdings/150, B:2/100, C:1/0. There must be three rows and total 250. Explain why a shared grand total alone would not prove each fund is correct.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### dbt-p1-05: Add minimum key and relationship proof {#dbt-p1-05}

##### Concept: dbt-p1-05-concept --- Add minimum key and relationship proof {#v2-dbt-phase-one-certified-readme-md-concept-dbt-p1-05-concept-add-minimum-key-and-relationship-proof}

Uniqueness and non-null tests protect a dimension key; a relationship test finds holding fund IDs without a matching fund. These answer different questions. A relationship test alone does not guarantee a one-to-one join because duplicate dimension keys can still multiply rows. A useful minimum standard includes both structural checks and a known consumer output.

```{=html}
<!-- instructor-demo: dbt-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-dbt-phase-one-certified-readme-md-challenge-4}

Add schema.yml tests for stg_funds.fund_id uniqueness/not-null, holding fund_id relationship/not-null and mart key uniqueness/not-null. Add a singular total-250 check. Run dbt build --profiles-dir . and explain each test.

##### Hint {#v2-dbt-phase-one-certified-readme-md-hint-4}

The YAML examples use data_tests. Pair relationships with uniqueness on the referenced key.

##### Check {#v2-dbt-phase-one-certified-readme-md-check-4}

All tests must pass on a fresh build. In a copied fixture add an unknown fund ID, run `dbt seed --profiles-dir .` followed by `dbt build --profiles-dir .`, and show the relationship failure. Restore the original CSV, seed again, then rebuild and check the per-fund outputs. Changing a CSV does not reload its source table. Save the failed-test name, repair and per-fund evidence.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### Phase completion {#v2-dbt-phase-one-certified-readme-md-phase-completion}

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

``` bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify dbt phase-one-certified --workspace .local/challenges-v2/dbt/phase-one-certified --mode offline
```

Execution boundary: Local DuckDB dbt; optional Databricks rehearsal remains separately measured. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

### Optional stretch {#v2-dbt-phase-one-certified-readme-md-optional-stretch}

Try a small variation after completing the core: change one input or contract condition in a second disposable copy, predict the result, and verify your prediction. This does not replace a core task or contribute to its timing budget.


## Source: dbt/phase-one-certified/starter/README.md {#v2-dbt-phase-one-certified-starter-readme-md}

## dbt starter assets {#v2-dbt-phase-one-certified-starter-readme-md-dbt-starter-assets}

Copy this directory into an isolated workspace before editing. The phase README defines the exact baseline command and the completion evidence. Generated databases, logs and evidence belong in that workspace. A starter check passing confirms the baseline is usable; it does not certify completed work.

Files supplied here are part of the learner pack. The instructor solution is stored separately under `challenges/v2-solutions`; it is excluded from the learner appendix and learner archive. See the parent [phase instructions](#v2-dbt-phase-one-certified-readme-md) for the authored-file list, prerequisites and any deliberate defect.


## Source: dbt/phase-two-proficient/README.md {#v2-dbt-phase-two-proficient-readme-md}

## dbt: Phase two --- proficient {#v2-dbt-phase-two-proficient-readme-md-dbt-phase-two-proficient}

This phase has a fixed core of 5 tasks. The advanced standard is a justified design or repair, actual behavioral proof, and a useful handoff. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

### Prerequisites and workspace {#v2-dbt-phase-two-proficient-readme-md-prerequisites-and-workspace}

Prepared dbt-core1.10.13, dbt-duckdb1.9.6, DuckDB1.4.1 local environment. Optional connected profile needs Databricks adapter and isolated provisioned V2_DB_SCHEMA.

From the project root run:

``` bash
python3 scripts/challenge-v2.py prepare dbt phase-two-proficient
cd .local/challenges-v2/dbt/phase-two-proficient
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

### Local tool preparation {#v2-dbt-phase-two-proficient-readme-md-local-tool-preparation}

The instructor runs `bash scripts/setup-v2-tools.sh` once from the project root. Before changing into your copied workspace, activate `.local/v2-tools/bin/activate` to make the pinned `dbt` executable available. For Airflow, use `.local/v2-airflow/bin/python` with a workspace-specific `AIRFLOW_HOME`; do not mix these two Python environments. The verifier supplies these paths automatically in a fresh copy.

### Starter behavior {#v2-dbt-phase-two-proficient-readme-md-starter-behavior}

dbt seed --profiles-dir . and dbt build --profiles-dir . succeed on supplied baseline. Phase 2 exposure is a labelled placeholder.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter dbt phase-two-proficient --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

### Timeline and completion standard {#v2-dbt-phase-two-proficient-readme-md-timeline-and-completion-standard}

Core estimate: **90--120 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Task              Outcome                                               Minutes           Evidence
  ----------------- ----------------------------------------------------- ----------------- ----------------------------------------------------------------------------------------
  dbt-p2-01         Diagnose a join fan-out before repair                 18--24            The defective join has seven rows and total 400 instead of five/250

  dbt-p2-02         Repair enrichment at the intended grain               18--24            Repaired output must have A: 150 / B: 100 / C: 0, three distinct fund IDs and total250

  dbt-p2-03         Write reconciliation that detects the negative case   18--24            Record the expected failed test/result and repaired pass

  dbt-p2-04         Prove incremental update and replay behavior          18--24            First run:2 rows/180

  dbt-p2-05         Explain dependency impact and hand over               18--24            Show the dependency path and saved per-run row totals
  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Core challenges {#v2-dbt-phase-two-proficient-readme-md-core-challenges}

#### dbt-p2-01: Diagnose a join fan-out before repair {#dbt-p2-01}

##### Concept: dbt-p2-01-concept --- Diagnose a join fan-out before repair {#v2-dbt-phase-two-proficient-readme-md-concept-dbt-p2-01-concept-diagnose-a-join-fan-out-before-repair}

A dimension with two rows for the same join key turns one fact row into two joined rows. That can inflate money totals while every fact foreign key still has a match. The supplied duplicate-label fixture has two A labels; it is deliberately separate from the canonical funds seed so the baseline still builds.

```{=html}
<!-- instructor-demo: dbt-p2-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-dbt-phase-two-proficient-readme-md-challenge}

Load or inspect fixtures/fund_labels_duplicate.csv. Calculate the result of joining holdings to those labels. Record counts/totals before and after the join and identify the duplicated key.

##### Hint {#v2-dbt-phase-two-proficient-readme-md-hint}

For A the labels are active and priority. Compare per-fund totals, not only overall row counts.

##### Check {#v2-dbt-phase-two-proficient-readme-md-check}

The defective join has seven rows and total 400 instead of five/250. This fixture is intentional; it is not a broken starter. Explain why an ordinary foreign-key relationship test would miss the multiplicity.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### dbt-p2-02: Repair enrichment at the intended grain {#dbt-p2-02}

##### Concept: dbt-p2-02-concept --- Repair enrichment at the intended grain {#v2-dbt-phase-two-proficient-readme-md-concept-dbt-p2-02-concept-repair-enrichment-at-the-intended-grain}

Repair begins with a business rule for which dimension row is authoritative. Arbitrary DISTINCT after aggregation can hide a defect without explaining which facts were duplicated. The canonical funds relation has one row per fund, so it is the appropriate enrichment source for this consumer.

```{=html}
<!-- instructor-demo: dbt-p2-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-dbt-phase-two-proficient-readme-md-challenge-1}

Replace the placeholder fund_exposure model using the provided typed stages and the canonical fund dimension. Preserve fund names and zero-valued C. Add a uniqueness proof for the chosen dimension and explain why both A labels are not joinable at fund grain.

##### Hint {#v2-dbt-phase-two-proficient-readme-md-hint-1}

Phase 2 supplies the completed staging baseline; you do not need to recreate Phase 1.

##### Check {#v2-dbt-phase-two-proficient-readme-md-check-1}

Repaired output must have A: 150 / B: 100 / C: 0, three distinct fund IDs and total250. A reviewer must be able to connect the chosen grain rule to the corrected join.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### dbt-p2-03: Write reconciliation that detects the negative case {#dbt-p2-03}

##### Concept: dbt-p2-03-concept --- Write reconciliation that detects the negative case {#v2-dbt-phase-two-proficient-readme-md-concept-dbt-p2-03-concept-write-reconciliation-that-detects-the-negative-case}

An independent expected fixture can catch a bug shared by two derived totals. Comparing two models with the same faulty join may pass while both are wrong. Here the oracle is fixed per-fund values and a total of 250, accompanied by a deliberate fan-out case that the check must reject.

```{=html}
<!-- instructor-demo: dbt-p2-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-dbt-phase-two-proficient-readme-md-challenge-2}

Add a singular reconciliation test and a per-fund comparison. In a temporary copy introduce the duplicate-label join, run the tests and confirm the wrong output is rejected. Restore the correct mart and repeat the build.

##### Hint {#v2-dbt-phase-two-proficient-readme-md-hint-2}

Keep the oracle separate from the transformation SQL; do not derive expected numbers from the same output under test.

##### Check {#v2-dbt-phase-two-proficient-readme-md-check-2}

Record the expected failed test/result and repaired pass. Show that a400 total or an inflated A: 300 fails even if another derived total repeats the same mistake.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### dbt-p2-04: Prove incremental update and replay behavior {#dbt-p2-04}

##### Concept: dbt-p2-04-concept --- Prove incremental update and replay behavior {#v2-dbt-phase-two-proficient-readme-md-concept-dbt-p2-04-concept-prove-incremental-update-and-replay-behavior}

An incremental model maintains previous state between runs. A unique key and replacement strategy determine what happens when an existing event is replayed or corrected. This exercise uses event_id as identity and delete+insert in the local adapter; it does not promise exactly-once delivery across systems.

```{=html}
<!-- instructor-demo: dbt-p2-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-dbt-phase-two-proficient-readme-md-challenge-3}

Create arrival_ledger.sql as an incremental model with unique_key event_id and delete+insert strategy, reading arrivals. Build e1/A100 and e2/B80. Rerun unchanged, then append e3/C20 and change e1 to125. Reseed and run again.

##### Hint {#v2-dbt-phase-two-proficient-readme-md-hint-3}

Supply the whole tiny arrivals seed each time. This is replacement by event identity, not a watermark exercise.

##### Check {#v2-dbt-phase-two-proficient-readme-md-check-3}

First run:2 rows/180. Replay:2/180. Corrected+new input:3 rows/225, with e1=125. Rerun again and prove it remains3/225. Record adapter semantics; recheck the chosen strategy before connected Databricks use.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### dbt-p2-05: Explain dependency impact and hand over {#dbt-p2-05}

##### Concept: dbt-p2-05-concept --- Explain dependency impact and hand over {#v2-dbt-phase-two-proficient-readme-md-concept-dbt-p2-05-concept-explain-dependency-impact-and-hand-over}

Lineage connects the defect to affected consumers and helps bound a rebuild. It is useful when it supports an impact decision, not just a screenshot of nodes. The advanced handoff combines a correct grain, negative-case proof and incremental state observations.

```{=html}
<!-- instructor-demo: dbt-p2-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-dbt-phase-two-proficient-readme-md-challenge-4}

Run dbt docs generate --profiles-dir . and inspect manifest.json dependencies for staging, exposure and arrival_ledger. Write a short incident note explaining fan-out cause, affected result, repair and replay limits.

##### Hint {#v2-dbt-phase-two-proficient-readme-md-hint-4}

Use dbt ls --select +fund_exposure to inspect the parent selection without starting a web service.

##### Check {#v2-dbt-phase-two-proficient-readme-md-check-4}

Show the dependency path and saved per-run row totals. Core completion requires repair, negative-case and replay evidence. Optional stretch: port and measure the adapter-specific OPTIMIZE/ZORDER hook from v1, or author the legacy returns mart.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### Phase completion {#v2-dbt-phase-two-proficient-readme-md-phase-completion}

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

``` bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify dbt phase-two-proficient --workspace .local/challenges-v2/dbt/phase-two-proficient --mode offline
```

Execution boundary: Local DuckDB dbt; optional Databricks rehearsal remains separately measured. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

### Optional stretch {#v2-dbt-phase-two-proficient-readme-md-optional-stretch}

See the [stretch index](#v2-dbt-phase-two-proficient-stretch-readme-md). Each route has its own prerequisites, timing and completion check; none is part of this fixed core.


## Source: dbt/phase-two-proficient/starter/README.md {#v2-dbt-phase-two-proficient-starter-readme-md}

## dbt starter assets {#v2-dbt-phase-two-proficient-starter-readme-md-dbt-starter-assets}

Copy this directory into an isolated workspace before editing. The phase README defines the exact baseline command and the completion evidence. Generated databases, logs and evidence belong in that workspace. A starter check passing confirms the baseline is usable; it does not certify completed work.

Files supplied here are part of the learner pack. The instructor solution is stored separately under `challenges/v2-solutions`; it is excluded from the learner appendix and learner archive. See the parent [phase instructions](#v2-dbt-phase-two-proficient-readme-md) for the authored-file list, prerequisites and any deliberate defect.


## Source: dbt/phase-two-proficient/stretch/README.md {#v2-dbt-phase-two-proficient-stretch-readme-md}

## dbt: optional stretch selection {#v2-dbt-phase-two-proficient-stretch-readme-md-dbt-optional-stretch-selection}

Legacy Phase2supportingmodels, returns, adapter-specificOPTIMIZE/ZORDER, and new-mart exercises remain available under v1/02-dbt-pipeline (each 30--90 minutes). These require the corresponding prepared baseline; actual adapter operations need connected verification.

These routes are separate from core completion. Record timing exceptions rather than shortening an exercise during the audit. Instructor review should select one follow-up based on the learner goal and available environment.

### Full legacy advanced reference {#v2-dbt-phase-two-proficient-stretch-readme-md-full-legacy-advanced-reference}

The following is the preserved legacy advanced route. Its workspace/commands target **v1**; do not run it against the v2 workspace. Core-equivalent topics are retained here for complete teaching coverage, not additional core assignments.

### Phase 2: Intermediate, Marts, Tests & Docs {#v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-intermediate-marts-tests-docs}

Phase 1 left you with a running baseline: sources declared with freshness, five staging models cleaned and typed, the staging layer built green on Databricks. That was setup. Phase 2 is the build proper. Here you write the **intermediate** joins, the two **curated marts**, the **generic and singular tests** that enforce the contract, generate the **docs and lineage graph**, wire the Databricks `OPTIMIZE` performance post-hook, and finish with a capstone that adds a new mart end to end.

Every challenge is self-contained. Each defines the dbt or SQL idea it uses before you apply it, so you are never assumed to have met it before. The shape is always:

-   **Concept** --- the idea, in plain English.
-   **Goal** --- the business outcome in one line.
-   **Authoring task** --- exactly what you write, and into which stub file.
-   **How to check** --- a command to run, or an observable result.

Write your own answer first; a worked **Solution** follows each challenge for you to compare against. Budget roughly \~10 min per challenge --- a pacing target, not a deadline. Work the challenges in order: they build on each other, and Challenge 10 ties the marts together into a new end-to-end deliverable.

------------------------------------------------------------------------

### Phase 2 --- Challenge 1: The enrichment join --- `int_holdings_enriched` {#v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-1-the-enrichment-join-int_holdings_enriched}

**Concept.** The **intermediate** layer is where joins live; staging stayed 1:1 with its sources precisely so this layer can combine them without re-cleaning. `int_holdings_enriched` joins the cleaned holdings to prices and FX so each position carries a base-currency market value. The key move is the currency conversion: a holding is valued in its local currency, and to roll funds up you need a common base. `mv_base_ccy = mv_local_ccy * coalesce(fx_rate, 1.0)`. The FX feed ships a `GBP → GBP` rate of `1.0` alongside the `USD → GBP` and `EUR → GBP` rates, so a GBP holding converts through a real matched row; the `coalesce` is the safety net for the other case --- a left join that finds **no** rate for that currency and date returns `null`, and multiplying by `null` would silently wipe the value out. Defaulting to `1.0` keeps the holding at its local value instead of losing it. The output grain is unchanged from `stg_holdings`: one row per (fund, date, instrument).

**Goal.** One intermediate model that values every holding in the GBP base currency, ready for the marts to aggregate.

**Authoring task.** Complete `dbt/models/intermediate/int_holdings_enriched.sql`. Read `ref('stg_holdings')`, `ref('stg_prices')`, and `ref('stg_fx_rates')`. Left join prices on `(instrument_id, date)` and FX on `(local_ccy → GBP, date)`. Select the holding columns plus `close_price`, `fx_rate_to_base`, and the computed `mv_base_ccy`. Keep the grain at (fund, date, instrument) --- left joins, so a holding with no price or FX row still appears.

**How to check.**

``` bash
dbt build --select int_holdings_enriched
dbt show --select int_holdings_enriched --limit 10
```

Every row should carry an `mv_base_ccy`. All eight bundled holdings are quoted in GBP, so each one matches the `GBP → GBP` rate of `1.0` and its `mv_base_ccy` equals its `mv_local_ccy` --- that equality is the check that the join worked, not a sign it was skipped. To see a rate other than `1.0` actually bite, use the optional variation below. No row should be dropped --- the count matches `stg_holdings`.

Docs: dbt `ref()`: <https://docs.getdbt.com/reference/dbt-jinja-functions/ref>.

**Try a variation (optional).** The FX feed already carries `USD → GBP` at `0.78`, but no bundled holding is quoted in USD, so that rate never gets used. Prove the conversion works by running a one-off query that re-points a holding at USD --- no file edits, nothing to undo:

``` bash
dbt show --inline "select mv_local_ccy, mv_local_ccy * (select fx_rate from {{ ref('stg_fx_rates') }} where from_ccy = 'USD' and rate_date = '2026-05-20') as mv_if_usd from {{ ref('stg_holdings') }} where position_date = '2026-05-20'" --limit 5
```

`mv_if_usd` comes back at 78% of `mv_local_ccy` --- the same arithmetic `int_holdings_enriched` performs, now with a rate that is not `1.0`.

Worked answer 1 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

### Phase 2 --- Challenge 2: The two supporting intermediate models {#v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-2-the-two-supporting-intermediate-models}

**Concept.** Not every intermediate model is a big join. The other two are small, focused re-shapes that the marts need. `int_fund_attributes` selects the **active** funds and their reporting attributes --- filtering to `is_active = true` once here means no mart has to remember that filter. `int_positions_dated` rolls cash and accrued interest into one `cash_plus_accrued` figure per (fund, day). Each model does one job, named in its filename, so the marts read a clean, purpose-built input rather than re-deriving it.

**Goal.** Two ready-to-join intermediate models: one of active funds, one of cash per fund-day.

**Authoring task.** Complete two stubs. In `dbt/models/intermediate/int_fund_attributes.sql`, select `fund_id`, `fund_name`, `inception_date`, `base_ccy`, `strategy_code` from `ref('stg_funds')` where `is_active = true`. In `dbt/models/intermediate/int_positions_dated.sql`, select `fund_id`, `position_date`, `local_ccy`, and `cash_balance + accrued_interest as cash_plus_accrued` from `ref('stg_positions')`.

**How to check.**

``` bash
dbt build --select int_fund_attributes int_positions_dated --indirect-selection=cautious
dbt show --select int_fund_attributes --limit 10 --indirect-selection=cautious
```

`int_fund_attributes` should return only active funds. In the bundled raw fund master all four rows are active, so all four appear; the filter is still intentional and would exclude inactive fixture rows such as `PEF-LEGACY-X` from `seed_funds`. `int_positions_dated` returns one row per (fund, day) with a single `cash_plus_accrued` column.

**Why `--indirect-selection=cautious` here.** When you select a model, dbt also picks up the tests attached to it --- that is *indirect selection*, and its default mode (`eager`) pulls in a test as soon as **any one** of the test's inputs is selected. The shipped `models/marts/schema.yml` declares a `relationships` test that checks `fct_portfolio_returns.fund_id` against `int_fund_attributes.fund_id`, so that test has **two** inputs. Selecting `int_fund_attributes` is enough for `eager` to run it --- but `fct_portfolio_returns` is still the untouched `select 1 as placeholder` stub until Challenge 4, so the test asks for a `fund_id` column that does not exist yet and fails with `UNRESOLVED_COLUMN ... Did you mean [placeholder]`. `cautious` runs a test only when **all** of its inputs are selected, which skips that not-yet-buildable test and leaves you with just the two models you actually wrote. Drop the flag once you finish Challenge 4 --- from then on both inputs are real and the test passes on its own.

Docs: indirect selection: <https://docs.getdbt.com/reference/node-selection/test-selection-examples#indirect-selection>.

Docs: dbt SQL models: <https://docs.getdbt.com/docs/build/sql-models>.

Worked answer 2 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

### Phase 2 --- Challenge 3: First curated mart --- `agg_fund_exposure` {#v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-3-first-curated-mart-agg_fund_exposure}

**Concept.** A **mart** is the consumer-facing layer: it trades row-level detail for a report-ready shape and materialises as a table for fast reads. `agg_` is the prefix for a pre-aggregated mart --- measures grouped by reporting dimensions. `agg_fund_exposure` rolls the enriched holdings up to one row per (fund, date, strategy), summing base-currency exposure, counting distinct instruments, and isolating the cash-only slice with a `case` inside the `sum`. Compliance reads it for concentration alerts: how much is each fund exposed to, by strategy, and how much of that is cash.

**Goal.** A per-(fund, date, strategy) exposure aggregate compliance can read for concentration.

**Authoring task.** Complete `dbt/models/marts/agg_fund_exposure.sql`. Read `ref('int_holdings_enriched')` and join `ref('int_fund_attributes')` for the `strategy_code`. Group by `(fund_id, position_date, strategy_code)` and produce: `exposure_base_ccy` (sum of `mv_base_ccy`), `instrument_count` (`count(distinct instrument_id)`), and `cash_exposure_base_ccy` (the sum of `mv_base_ccy` only where `instrument_id like 'CASH_%'`).

**How to check.**

``` bash
dbt build --select agg_fund_exposure
dbt show --select agg_fund_exposure --limit 10
```

Each row is one (fund, date, strategy). `exposure_base_ccy` should be a positive GBP figure --- with the bundled holdings it lands around 0.9--1.5 billion, since each fund holds a single large position --- and `instrument_count` a small positive integer. The bundled holdings have no cash-only rows, so `cash_exposure_base_ccy` is `0`; if you add `CASH_<ccy>` holdings, cash exposure should never be larger than total exposure.

Docs: dbt marts: <https://docs.getdbt.com/best-practices/how-we-structure/4-marts>.

Worked answer 3 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

### Phase 2 --- Challenge 4: Second curated mart --- `fct_portfolio_returns` {#v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-4-second-curated-mart-fct_portfolio_returns}

**Concept.** `fct_` is the prefix for a **fact** table --- one row per event or measurement, at a fine grain. `fct_portfolio_returns` is the published daily-grain fact: one row per (fund, date, instrument), carrying the base-ccy MV and a calculated NAV-per-unit. NAV-per-unit is total fund market value divided by units outstanding; here units are synthesised (a real feed ships them), so you roll the per-instrument MV up to a per-fund total in a CTE, divide by units, and join that back to the instrument grain. This is the mart the RM dashboard, compliance, and the client app all read.

**Goal.** A daily-grain fact carrying each position's base-ccy value and the fund's calculated NAV-per-unit.

**Authoring task.** Complete `dbt/models/marts/fct_portfolio_returns.sql`. Read `ref('int_holdings_enriched')` and `ref('int_fund_attributes')`. In a `fund_mv` CTE, `sum(mv_base_ccy)` per (fund, date). In a `with_units` CTE, add `100000000.0 as units_outstanding` and keep the total. The final select is at the instrument grain: carry the holding columns through, join `fund_name` from the fund attributes, and compute `calc_nav_per_unit = total_mv_base / units_outstanding`.

**How to check.**

``` bash
dbt build --select fct_portfolio_returns
dbt show --select fct_portfolio_returns --limit 10
```

One row per (fund, date, instrument), each with an `mv_base_ccy` and a `calc_nav_per_unit`. The NAV-per-unit should land in a believable range --- single digits to low tens (the bundled funds run about 9 to 15), close to the custodian NAVs in `seed_custodian_nav.csv` --- not zero and not millions.

Docs: dbt SQL models: <https://docs.getdbt.com/docs/build/sql-models>.

Worked answer 4 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

### Phase 2 --- Challenge 5: Generic tests on the marts {#v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-5-generic-tests-on-the-marts}

**Concept.** dbt's four built-in **generic tests** turn your assumptions into executable checks: `not_null` and `unique` for keys, `accepted_values` for a closed set of categories, and `relationships` for referential integrity (every foreign-key value exists in a parent model). You attach them by column in a YAML file next to the model --- zero bad rows means pass. On a mart they guard the contract: a `not_null` on a grain column catches a join that dropped a key, a `relationships` test catches an orphaned fund id, an `accepted_values` test catches a new strategy code that slipped in unmapped.

**Goal.** The two marts guarded by generic tests so a broken build fails loudly rather than shipping wrong numbers.

**Authoring task.** The marts' `dbt/models/marts/schema.yml` ships with the test declarations already in place --- read it and run it. On `fct_portfolio_returns`: `not_null` on `fund_id`, `position_date`, `instrument_id`, `mv_base_ccy`, plus a `relationships` test from `fund_id` to `ref('int_fund_attributes')`. On `agg_fund_exposure`: `not_null` on `fund_id` and `position_date`, plus an `accepted_values` test on `strategy_code` (`EQ-LC`, `EQ-EM`, `EQ-GC`, `FI-IG`). Confirm you understand each, then run them.

**How to check.**

``` bash
dbt test --select fct_portfolio_returns agg_fund_exposure
```

Every attached column produces a test like `not_null_fct_portfolio_returns_fund_id` and `relationships_fct_portfolio_returns_fund_id__...`, all `PASS`. To prove the `accepted_values` test bites, drop `FI-IG` from the list and run `dbt test --no-partial-parse --select agg_fund_exposure` to watch the fixed-income fund fail the test, then restore it.

Docs: generic data tests: <https://docs.getdbt.com/docs/build/data-tests>.

Worked answer 5 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

### Phase 2 --- Challenge 6: A singular reconciliation test --- NAV within tolerance {#v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-6-a-singular-reconciliation-test-nav-within-tolerance}

**Concept.** A **singular test** is a single hand-written SQL file in `tests/` that fails when its query returns any rows. Unlike a generic test it is not attached to a column --- it tests one specific assertion across whatever models it references. The powerful case is **reconciliation**: your calculated number must agree with an independent source. `assert_nav_within_tolerance` compares the `calc_nav_per_unit` your `fct_portfolio_returns` produces against the custodian-reported NAV in `seed_custodian_nav.csv`, and returns a row only when they differ by more than **1 basis point** (1bp = 0.0001 fractional). Because a singular test returning any rows is a failure, this halts the pipeline if the calculated NAV ever drifts from the custodian's.

**Goal.** Prove the calculated NAV-per-unit reconciles to the custodian NAV within 1bp, enforced as a test.

**Authoring task.** Complete `dbt/tests/assert_nav_within_tolerance.sql`. In a `calc` CTE, select `fund_id, position_date, calc_nav_per_unit` from `ref('fct_portfolio_returns')` where it is not null. In a `custodian` CTE, select `fund_id, position_date, nav_per_unit` from `ref('seed_custodian_nav')`. Join them on `(fund_id, position_date)`, compute `variance_bps = (calc - custodian) / custodian * 10000`, and return rows where `abs(variance_bps) > 1.0`.

**How to check.**

``` bash
dbt build --select fct_portfolio_returns seed_custodian_nav
dbt test --select assert_nav_within_tolerance
```

The test should PASS (zero rows). To see it fire with the bundled data, temporarily change the final comparison to `>= 0.0` so even zero variance trips it, confirm it FAILS, then set it back to `> 1.0`.

Docs: singular data tests: <https://docs.getdbt.com/docs/build/data-tests>.

Worked answer 6 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

### Phase 2 --- Challenge 7: The full build --- `dbt build` {#v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-7-the-full-build-dbt-build}

**Concept.** `dbt build` runs seed → run → test in dependency order across the whole project. Crucially, if a model's upstream test fails, downstream models are **skipped** --- you do not propagate bad data. This is the command CI and scheduled jobs run, and it is your end-to-end proof that the pipeline is whole: seeds loaded, all ten models built, every generic and singular test passing.

**Goal.** One green end-to-end run: seeds, all ten models, every test.

**Authoring task.** Nothing new to write --- run the full build and read the summary:

``` bash
dbt build
```

Read the final summary line and confirm every resource passed with no errors and no skips.

**How to check.** The summary should end like:

``` text
Completed successfully
Done. PASS=N WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=N
```

`N` covers the eight seeds, ten models, and every test. `ERROR=0` and `SKIP=0` together mean nothing failed and nothing was skipped for a failed upstream.

To run the full verified gate: `mise run challenge:verify 02`

Docs: dbt build: <https://docs.getdbt.com/reference/commands/build>.

Worked answer 7 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

### Phase 2 --- Challenge 8: Docs and the lineage graph {#v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-8-docs-and-the-lineage-graph}

**Concept.** dbt generates a documentation site from your model and source descriptions plus the DAG it infers from every `ref()` and `source()` call. `dbt docs generate` writes the metadata; `dbt docs serve` serves an interactive site with column docs, the compiled SQL for each model, and a **lineage graph** you can click through. The lineage graph is the payoff of declaring sources and using `ref()` everywhere: it shows, end to end, that `fct_portfolio_returns` is fed by the intermediate holdings, which are fed by the staging models, which read the sources --- so you can see exactly what breaks if you change any one of them.

**Goal.** A browsable docs site whose lineage graph shows the full `source → staging → intermediate → marts` DAG.

**Authoring task.** Generate and serve the docs:

``` bash
dbt docs generate
dbt docs serve --host 127.0.0.1 --port 8081
```

`dbt docs serve` holds the terminal until you stop it with **Ctrl-C** --- open a second terminal if you want to keep working. Two flags matter here and are easy to miss:

-   **`--host 127.0.0.1` is required in this devcontainer.** `dbt docs serve` takes its bind address from the `DBT_HOST` environment variable, and this repo sets `DBT_HOST` to your Databricks workspace URL (the dbt *profiles* use it as the warehouse host). Without the flag, dbt tries to bind a local socket to `https://…databricks.com` and dies with `socket.gaierror: [Errno -2] Name or service not known`.
-   **Port 8081, not dbt's default 8080.** Challenge 03 runs the Airflow UI on 8080; if Airflow is up, 8080 gives you `OSError: [Errno 98] Address already in use`.

Then, in the served site, find the lineage graph for `fct_portfolio_returns` and trace it back to the four source tables used by that mart. The separately built `stg_positions → int_positions_dated` branch is visible in the project graph but does not feed this mart.

**How to check.** `dbt docs generate` writes `target/manifest.json` and `target/catalog.json` and prints a "Catalog written" line. In the served site, the lineage graph for `fct_portfolio_returns` should show it fed by `int_holdings_enriched` and `int_fund_attributes`, those fed by the staging models, and those staging models fed by four source tables.

Docs: dbt docs and lineage: <https://docs.getdbt.com/docs/collaborate/documentation>.

Worked answer 8 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

### Phase 2 --- Challenge 9: The Databricks performance post-hook --- `OPTIMIZE … ZORDER` {#v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-9-the-databricks-performance-post-hook-optimize-zorder}

**Concept.** A dbt **post-hook** is SQL that runs after a model is built. On Databricks, `OPTIMIZE <table> ZORDER BY (cols)` is a Delta-table optimisation: it compacts small files and co-locates rows by the columns most queries filter on, so reads prune faster. The marts in this project query by `fund_id` and `position_date`, so z-ordering on those two columns speeds up every dashboard and compliance query that filters on a fund or a date. The post-hook is set once at the folder level in `dbt_project.yml`, so every mart inherits it --- and because it is a table optimisation, it only makes sense on the mart tables, not the staging views.

**Goal.** Every mart table z-ordered on its query columns so reads prune efficiently.

**Authoring task.** The post-hook ships in `dbt/dbt_project.yml` on the `marts` folder --- read it and confirm it runs. Confirm the `marts` block carries `+post-hook: "OPTIMIZE {{ this }} ZORDER BY (fund_id, position_date)"`, then rebuild a mart and watch the `OPTIMIZE` statement run after the table is created.

**How to check.**

``` bash
dbt build --select agg_fund_exposure
```

In the dbt run log, after the `OK created sql table model ... agg_fund_exposure` line you should see the post-hook execute the `OPTIMIZE ... ZORDER BY (fund_id, position_date)` statement against that table. Staging models, being views, run no such hook.

**dbt does not print hook SQL to the console** --- at the default log level you only see the `OK created sql table model` line, so it looks like nothing ran. The statement is recorded in the debug log. Confirm it with either of these, run from `challenges/v1/02-dbt-pipeline/dbt`:

``` bash
grep "ZORDER BY" logs/dbt.log | tail -1
```

``` bash
dbt --debug build --select agg_fund_exposure 2>&1 | grep "ZORDER BY"
```

You should see `OPTIMIZE \`training_dev\`.\`training\_`<username>`{=html}\`.\`agg_fund_exposure\` ZORDER BY (fund_id, position_date)\`.

Docs: dbt hooks: <https://docs.getdbt.com/docs/build/hooks-operations>; Databricks OPTIMIZE/ZORDER: <https://docs.databricks.com/aws/en/delta/data-skipping>.

Worked answer 9 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

### Phase 2 --- Challenge 10: Capstone --- add a new mart end to end {#v2-dbt-phase-two-proficient-stretch-readme-md-phase-2-challenge-10-capstone-add-a-new-mart-end-to-end}

This is the integrative challenge. Earlier challenges each added one piece; here you compose the pattern into a new deliverable of your own and prove it is correct. You will add a new mart, a test that guards it, and confirm it lands in the lineage graph --- the full `model + test + docs` loop you have been building.

**Concept.** A new consumer question arrives: "what is each fund's total base-currency exposure per day, across all strategies?" `agg_fund_exposure` is at (fund, date, strategy) grain --- one grain too fine for this. The answer is a new mart, `agg_fund_daily_exposure`, at (fund, date) grain, built by re-aggregating the strategy-level mart up one level. Building it from `agg_fund_exposure` rather than from scratch reuses work and means the new total must reconcile to the strategy-level total --- which gives you a natural reconciliation test.

**Goal.** A per-(fund, date) total-exposure mart, tested and visible in lineage, that reconciles to the strategy-level aggregate.

**Authoring task.** Three pieces:

1.  Create `dbt/models/marts/agg_fund_daily_exposure.sql`: read `ref('agg_fund_exposure')`, group by `(fund_id, position_date)`, and sum `exposure_base_ccy` into `total_exposure_base_ccy` (plus a `sum(cash_exposure_base_ccy) as total_cash_base_ccy`).
2.  Add a `not_null` test on `fund_id` and `position_date` for the new mart in `dbt/models/marts/schema.yml`.
3.  Create a singular reconciliation test `dbt/tests/reconcile_daily_exposure.sql` that returns a row when `sum(total_exposure_base_ccy)` from the new mart differs from `sum(exposure_base_ccy)` from `agg_fund_exposure` by more than a small tolerance (`0.01`).

**How to check.**

``` bash
dbt build --select agg_fund_daily_exposure
dbt test --select reconcile_daily_exposure
dbt docs generate
```

`agg_fund_daily_exposure` returns one row per (fund, date) with a `total_exposure_base_ccy` that, for a single-strategy fund, equals that fund's strategy-level exposure. `reconcile_daily_exposure` should PASS (zero rows) --- that passing test is the integration proof. After `dbt docs generate`, the new mart appears in the lineage graph fed by `agg_fund_exposure`.

Docs: singular tests and marts: <https://docs.getdbt.com/docs/build/data-tests>, <https://docs.getdbt.com/best-practices/how-we-structure/4-marts>.

Worked answer 10 is supplied separately in the instructor pack: `challenges/v2-solutions/dbt/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

### Done {#v2-dbt-phase-two-proficient-stretch-readme-md-done}

You built the full pipeline: the enrichment join, the two supporting intermediate models, the two curated marts, generic tests on the marts, a singular NAV reconciliation, a green full build, the docs and lineage graph, the Databricks `OPTIMIZE` post-hook, and a new mart of your own with its reconciliation test. That is a complete, tested, documented dbt product running on Databricks.

Run the full verification gate at any time:

``` bash
mise run challenge:verify 02
```


## Source: databricks-cli/README.md {#v2-databricks-cli-readme-md}

## databricks-cli challenges {#v2-databricks-cli-readme-md-databricks-cli-challenges}

This route develops a bounded Phase 1 standard. Read concept explanations before attempting the task; retain commands/results and your reasoning.

### Before you start {#v2-databricks-cli-readme-md-before-you-start}

Databricks CLI0.236.0 in the supplied client container; DEFAULT profile and metadata permissions. Offline fixtures provide parsing practice only. Work in a copied phase workspace. Phase 2, when offered, supplies its entry fixture. [Pack navigation](#v2-readme-md) explains the course/clinic placement and version selection.

### Suggested timeline and tasks {#v2-databricks-cli-readme-md-suggested-timeline-and-tasks}

  -------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Phase       Task ID                                         Title                                         Teaching concept               Core/stretch   Minutes
  ----------- ----------------------------------------------- --------------------------------------------- ------------------------------ -------------- -----------
  Phase 1     [databricks-cli-p1-01](#databricks-cli-p1-01)   Establish the CLI identity boundary           databricks-cli-p1-01-concept   core           9--13

  Phase 1     [databricks-cli-p1-02](#databricks-cli-p1-02)   Separate workspace and Unity Catalog names    databricks-cli-p1-02-concept   core           9--13

  Phase 1     [databricks-cli-p1-03](#databricks-cli-p1-03)   Inspect permitted schema and table metadata   databricks-cli-p1-03-concept   core           9--13

  Phase 1     [databricks-cli-p1-04](#databricks-cli-p1-04)   Filter JSON and explain a limited result      databricks-cli-p1-04-concept   core           9--13

  Phase 1     [databricks-cli-p1-05](#databricks-cli-p1-05)   Produce a bounded discovery handoff           databricks-cli-p1-05-concept   core           9--13
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------

Inclusive phase estimates: Phase 1 45--65 minutes. These estimates are unpiloted. Reading, normal waits, checking and handoff are included; optional stretch is separately identified. [Timing review](practice/client/designer/reviews/TIMING-AUDIT.md) records current exceptions and the pilot protocol.

### Choose your phase {#v2-databricks-cli-readme-md-choose-your-phase}

[Phase one---certified](#v2-databricks-cli-phase-one-certified-readme-md) establishes minimum understanding. [Phase two---proficient](#v2-databricks-cli-phase-two-proficient-readme-md) is explicitly not offered; its page is a structural placeholder.

### Teaching concepts {#v2-databricks-cli-readme-md-teaching-concepts}

The concept column and phase concept headings identify what an instructor can demonstrate. A useful demonstration shows the before state, the relevant change, and independent output/state evidence. The generated instructor companion reproduces concept explanations from these phase READMEs, so notes and challenges share a source.

Suggested destination: Tuesday platform discovery / Wednesday readiness. Advanced clinics and optional work require separate time; they do not silently consume protected core teaching windows.


## Source: databricks-cli/phase-one-certified/README.md {#v2-databricks-cli-phase-one-certified-readme-md}

## databricks-cli: Phase one --- certified {#v2-databricks-cli-phase-one-certified-readme-md-databricks-cli-phase-one-certified}

This phase has a fixed core of 5 tasks. The minimum standard is a working result with the underlying tool concepts explained. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

### Prerequisites and workspace {#v2-databricks-cli-phase-one-certified-readme-md-prerequisites-and-workspace}

Databricks CLI0.236.0 in the supplied client container; DEFAULT profile and metadata permissions. Offline fixtures provide parsing practice only.

From the project root run:

``` bash
python3 scripts/challenge-v2.py prepare databricks-cli phase-one-certified
cd .local/challenges-v2/databricks-cli/phase-one-certified
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

### Starter behavior {#v2-databricks-cli-phase-one-certified-readme-md-starter-behavior}

python -m json.tool metadata.json validates the benign supplied fixture. No credentials are included.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter databricks-cli phase-one-certified --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

### Timeline and completion standard {#v2-databricks-cli-phase-one-certified-readme-md-timeline-and-completion-standard}

Core estimate: **45--65 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Task                   Outcome                                       Minutes           Evidence
  ---------------------- --------------------------------------------- ----------------- -----------------------------------------------------------------------------------------
  databricks-cli-p1-01   Establish the CLI identity boundary           9--13             A live result must show the remote identity from the real endpoint

  databricks-cli-p1-02   Separate workspace and Unity Catalog names    9--13             Write a two-row comparison: object type, qualified path/name and relevant command group

  databricks-cli-p1-03   Inspect permitted schema and table metadata   9--13             Record the object type/full name and one useful metadata field

  databricks-cli-p1-04   Filter JSON and explain a limited result      9--13             Show the parsed table name training_dev

  databricks-cli-p1-05   Produce a bounded discovery handoff           9--13             The handoff must be understandable by a teammate
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Core challenges {#v2-databricks-cli-phase-one-certified-readme-md-core-challenges}

#### databricks-cli-p1-01: Establish the CLI identity boundary {#databricks-cli-p1-01}

##### Concept: databricks-cli-p1-01-concept --- Establish the CLI identity boundary {#v2-databricks-cli-phase-one-certified-readme-md-concept-databricks-cli-p1-01-concept-establish-the-cli-identity-boundary}

The CLI uses a selected authentication profile and talks to a workspace endpoint. Your shell username does not prove the remote identity. Identity and metadata are safe evidence; tokens and full credential files are not useful learner artifacts.

```{=html}
<!-- instructor-demo: databricks-cli-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-databricks-cli-phase-one-certified-readme-md-challenge}

Run databricks --version and databricks current-user me --profile DEFAULT --output json in the prepared client container. Record the returned user name and selected profile without credential values. If access is missing, inspect the supplied metadata fixture and mark this step offline-only.

##### Hint {#v2-databricks-cli-phase-one-certified-readme-md-hint}

Run command-group --help before using flags on the installed CLI0.236.0.

##### Check {#v2-databricks-cli-phase-one-certified-readme-md-check}

A live result must show the remote identity from the real endpoint. An unavailable session is blocked, not pass. The offline fixture contains no claim about your actual remote identity.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### databricks-cli-p1-02: Separate workspace and Unity Catalog names {#databricks-cli-p1-02}

##### Concept: databricks-cli-p1-02-concept --- Separate workspace and Unity Catalog names {#v2-databricks-cli-phase-one-certified-readme-md-concept-databricks-cli-p1-02-concept-separate-workspace-and-unity-catalog-names}

A workspace directory holds workspace objects such as notebooks. A Unity Catalog catalog contains schemas/tables. A directory called training_dev is not automatically the catalog of the same name, and listing a workspace path is not searching table rows.

```{=html}
<!-- instructor-demo: databricks-cli-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-databricks-cli-phase-one-certified-readme-md-challenge-1}

Inspect databricks workspace list /Shared --profile DEFAULT --output json and databricks catalogs list --profile DEFAULT --output json. Identify whether training_dev exists as a catalog, directory, both or neither in this prepared environment.

##### Hint {#v2-databricks-cli-phase-one-certified-readme-md-hint-1}

The starter fixture includes both object families specifically to practice this distinction.

##### Check {#v2-databricks-cli-phase-one-certified-readme-md-check-1}

Write a two-row comparison: object type, qualified path/name and relevant command group. Do not infer Unity Catalog access from a successful workspace directory listing.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### databricks-cli-p1-03: Inspect permitted schema and table metadata {#databricks-cli-p1-03}

##### Concept: databricks-cli-p1-03-concept --- Inspect permitted schema and table metadata {#v2-databricks-cli-phase-one-certified-readme-md-concept-databricks-cli-p1-03-concept-inspect-permitted-schema-and-table-metadata}

Metadata discovery follows catalog→schema→table. Listing can reveal names/types within your permissions, but it does not execute arbitrary SQL or return dataset rows. A missing listing can reflect lack of visibility rather than an empty business dataset.

```{=html}
<!-- instructor-demo: databricks-cli-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-databricks-cli-phase-one-certified-readme-md-challenge-2}

Use databricks schemas list training_dev and databricks tables list training_dev `<instructor-schema>`{=html}, with the selected profile and JSON output. Inspect one returned table with tables get `<full-name>`{=html}. Record its qualified name/type.

##### Hint {#v2-databricks-cli-phase-one-certified-readme-md-hint-2}

The instructor supplies the actual provisioned schema; do not assume training_learner exists remotely.

##### Check {#v2-databricks-cli-phase-one-certified-readme-md-check-2}

Record the object type/full name and one useful metadata field. If blocked, identify the failing operation and permission boundary, then complete the parsing exercise with metadata.json labelled offline.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### databricks-cli-p1-04: Filter JSON and explain a limited result {#databricks-cli-p1-04}

##### Concept: databricks-cli-p1-04-concept --- Filter JSON and explain a limited result {#v2-databricks-cli-phase-one-certified-readme-md-concept-databricks-cli-p1-04-concept-filter-json-and-explain-a-limited-result}

Structured output can be filtered deterministically and is more useful than visually scanning a large listing. Filtering names is a metadata operation, not full-text table search. Distinguishing an empty list, wrong path and permission denial helps formulate a precise request for an instructor.

```{=html}
<!-- instructor-demo: databricks-cli-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-databricks-cli-phase-one-certified-readme-md-challenge-3}

Use Python json to extract full_name values from a saved, sanitized table listing. Compare with metadata.json. Write how you would investigate a nonexistent schema and a permission denial without changing grants.

##### Hint {#v2-databricks-cli-phase-one-certified-readme-md-hint-3}

Use json.load and examine whether the CLI output is an envelope object or list before indexing.

##### Check {#v2-databricks-cli-phase-one-certified-readme-md-check-3}

Show the parsed table name training_dev.training_learner.holdings from the fixture. Explain separately what an empty collection and denied access would mean; do not retry by granting yourself privileges.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### databricks-cli-p1-05: Produce a bounded discovery handoff {#databricks-cli-p1-05}

##### Concept: databricks-cli-p1-05-concept --- Produce a bounded discovery handoff {#v2-databricks-cli-phase-one-certified-readme-md-concept-databricks-cli-p1-05-concept-produce-a-bounded-discovery-handoff}

A useful handoff connects metadata to the next consumer question and states what remains unverified. It does not equate a table name with proof of freshness, row content or suitability. That distinction prevents later dbt work from assuming an unmeasured input contract.

```{=html}
<!-- instructor-demo: databricks-cli-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-databricks-cli-phase-one-certified-readme-md-challenge-4}

Write discovery.md with identity route, catalog/schema/table, workspace distinction, observations, access limitation and a next question about holdings grain/freshness. Mark every observation live or fixture.

##### Hint {#v2-databricks-cli-phase-one-certified-readme-md-hint-4}

Use qualified names and omit tokens. A SQL query would require a separately taught API/warehouse boundary.

##### Check {#v2-databricks-cli-phase-one-certified-readme-md-check-4}

The handoff must be understandable by a teammate. Core checks assess object-type reasoning and parsing; live CLI evidence remains a separate gate when unavailable.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### Phase completion {#v2-databricks-cli-phase-one-certified-readme-md-phase-completion}

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

``` bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify databricks-cli phase-one-certified --workspace .local/challenges-v2/databricks-cli/phase-one-certified --mode offline
```

Execution boundary: Read-only Databricks CLI or explicitly labelled metadata fixture. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

### Optional stretch {#v2-databricks-cli-phase-one-certified-readme-md-optional-stretch}

Try a small variation after completing the core: change one input or contract condition in a second disposable copy, predict the result, and verify your prediction. This does not replace a core task or contribute to its timing budget.


## Source: databricks-cli/phase-one-certified/starter/README.md {#v2-databricks-cli-phase-one-certified-starter-readme-md}

## databricks-cli starter assets {#v2-databricks-cli-phase-one-certified-starter-readme-md-databricks-cli-starter-assets}

Copy this directory into an isolated workspace before editing. The phase README defines the exact baseline command and the completion evidence. Generated databases, logs and evidence belong in that workspace. A starter check passing confirms the baseline is usable; it does not certify completed work.

Files supplied here are part of the learner pack. The instructor solution is stored separately under `challenges/v2-solutions`; it is excluded from the learner appendix and learner archive. See the parent [phase instructions](#v2-databricks-cli-phase-one-certified-readme-md) for the authored-file list, prerequisites and any deliberate defect.


## Source: databricks-cli/phase-two-proficient/README.md {#v2-databricks-cli-phase-two-proficient-readme-md}

## databricks-cli: Phase two --- not offered {#v2-databricks-cli-phase-two-proficient-readme-md-databricks-cli-phase-two-not-offered}

This tool has a Phase 1 route only. This structural placeholder contains no assignment, timing estimate or certification gate. The empty starter/ directory is retained by convention. Return to the [tool index](#v2-databricks-cli-readme-md).


## Source: airflow/README.md {#v2-airflow-readme-md}

## airflow challenges {#v2-airflow-readme-md-airflow-challenges}

This route develops minimum competence followed by advanced behavioral proof. Read concept explanations before attempting the task; retain commands/results and your reasoning.

### Before you start {#v2-airflow-readme-md-before-you-start}

Prepared Airflow3.1.0/standard provider1.8.0 runtime and a separate dbt executable selected with V2_DBT_BIN. Astro UI route needs instructor-bound isolated workspace. Work in a copied phase workspace. Phase 2, when offered, supplies its entry fixture. [Pack navigation](#v2-readme-md) explains the course/clinic placement and version selection.

### Suggested timeline and tasks {#v2-airflow-readme-md-suggested-timeline-and-tasks}

  ---------------------------------------------------------------------------------------------------------------------------------------------------
  Phase       Task ID                           Title                                              Teaching concept        Core/stretch   Minutes
  ----------- --------------------------------- -------------------------------------------------- ----------------------- -------------- -----------
  Phase 1     [airflow-p1-01](#airflow-p1-01)   Inspect a prepared orchestration baseline          airflow-p1-01-concept   core           15--22

  Phase 1     [airflow-p1-02](#airflow-p1-02)   Author a small Python DAG with real dbt tasks      airflow-p1-02-concept   core           15--22

  Phase 1     [airflow-p1-03](#airflow-p1-03)   Demonstrate the dependency graph and manual run    airflow-p1-03-concept   core           15--22

  Phase 1     [airflow-p1-04](#airflow-p1-04)   Inspect a controlled task failure                  airflow-p1-04-concept   core           15--22

  Phase 1     [airflow-p1-05](#airflow-p1-05)   Explain the run and environment boundaries         airflow-p1-05-concept   core           15--22

  Phase 2     [airflow-p2-01](#airflow-p2-01)   Define bounded replay and input identity           airflow-p2-01-concept   core           18--24

  Phase 2     [airflow-p2-02](#airflow-p2-02)   Inject failure and observe useful retry behavior   airflow-p2-02-concept   core           18--24

  Phase 2     [airflow-p2-03](#airflow-p2-03)   Prove output correctness after recovery            airflow-p2-03-concept   core           18--24

  Phase 2     [airflow-p2-04](#airflow-p2-04)   Use Astro UI to make an operational decision       airflow-p2-04-concept   core           18--24

  Phase 2     [airflow-p2-05](#airflow-p2-05)   Write a short incident handoff                     airflow-p2-05-concept   core           18--24
  ---------------------------------------------------------------------------------------------------------------------------------------------------

Inclusive phase estimates: Phase 1 75--110 minutes; Phase 2 90--120 minutes. These estimates are unpiloted. Reading, normal waits, checking and handoff are included; optional stretch is separately identified. [Timing review](practice/client/designer/reviews/TIMING-AUDIT.md) records current exceptions and the pilot protocol.

### Choose your phase {#v2-airflow-readme-md-choose-your-phase}

[Phase one---certified](#v2-airflow-phase-one-certified-readme-md) establishes minimum understanding. [Phase two---proficient](#v2-airflow-phase-two-proficient-readme-md) requires substantive design/diagnosis/replay evidence with a finite core.

### Teaching concepts {#v2-airflow-readme-md-teaching-concepts}

The concept column and phase concept headings identify what an instructor can demonstrate. A useful demonstration shows the before state, the relevant change, and independent output/state evidence. The generated instructor companion reproduces concept explanations from these phase READMEs, so notes and challenges share a source.

Suggested destination: Thursday orchestration practical / advanced operations clinic. Advanced clinics and optional work require separate time; they do not silently consume protected core teaching windows.


## Source: airflow/phase-one-certified/README.md {#v2-airflow-phase-one-certified-readme-md}

## airflow: Phase one --- certified {#v2-airflow-phase-one-certified-readme-md-airflow-phase-one-certified}

This phase has a fixed core of 5 tasks. The minimum standard is a working result with the underlying tool concepts explained. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

### Prerequisites and workspace {#v2-airflow-phase-one-certified-readme-md-prerequisites-and-workspace}

Prepared Airflow3.1.0/standard provider1.8.0 runtime and a separate dbt executable selected with V2_DBT_BIN. Astro UI route needs instructor-bound isolated workspace.

From the project root run:

``` bash
python3 scripts/challenge-v2.py prepare airflow phase-one-certified
cd .local/challenges-v2/airflow/phase-one-certified
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

### Local tool preparation {#v2-airflow-phase-one-certified-readme-md-local-tool-preparation}

The instructor runs `bash scripts/setup-v2-tools.sh` once from the project root. Before changing into your copied workspace, activate `.local/v2-tools/bin/activate` to make the pinned `dbt` executable available. For Airflow, use `.local/v2-airflow/bin/python` with a workspace-specific `AIRFLOW_HOME`; do not mix these two Python environments. The verifier supplies these paths automatically in a fresh copy.

### Starter behavior {#v2-airflow-phase-one-certified-readme-md-starter-behavior}

Phase 1 python pipeline.py prints scaffold status. Phase 2 actual DAG imports and supplied project builds; fail-quality is absent until your documented drill.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter airflow phase-one-certified --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

### Timeline and completion standard {#v2-airflow-phase-one-certified-readme-md-timeline-and-completion-standard}

Core estimate: **75--110 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Task              Outcome                                           Minutes           Evidence
  ----------------- ------------------------------------------------- ----------------- ---------------------------------------------------------------------------------------------------------------
  airflow-p1-01     Inspect a prepared orchestration baseline         15--22            Show the prepared project result A: 150 / B: 100 / C: 0

  airflow-p1-02     Author a small Python DAG with real dbt tasks     15--22            Import the actual DAG using DagBag and inspect task IDs and edges

  airflow-p1-03     Demonstrate the dependency graph and manual run   15--22            The run must execute dbt and finish success

  airflow-p1-04     Inspect a controlled task failure                 15--22            Intentional failure: the quality drill raises Intentional quality drill and publish must not create a receipt

  airflow-p1-05     Explain the run and environment boundaries        15--22            Core evidence includes the executed run and business output
  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Core challenges {#v2-airflow-phase-one-certified-readme-md-core-challenges}

#### airflow-p1-01: Inspect a prepared orchestration baseline {#airflow-p1-01}

##### Concept: airflow-p1-01-concept --- Inspect a prepared orchestration baseline {#v2-airflow-phase-one-certified-readme-md-concept-airflow-p1-01-concept-inspect-a-prepared-orchestration-baseline}

An Airflow DAG declares dependencies between task executions. dbt declares model dependencies within a transformation project. These graphs are related but have different responsibilities: Airflow decides when stages run, while dbt decides how model references are ordered.

```{=html}
<!-- instructor-demo: airflow-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-airflow-phase-one-certified-readme-md-challenge}

Run python pipeline.py in the starter to see the valid scaffold message. Inspect the prepared project/ and run its dbt seed/build in a fresh workspace. Draw prepare→build→quality→publish before writing the DAG.

##### Hint {#v2-airflow-phase-one-certified-readme-md-hint}

The dbt baseline is already solved; authoring it again is outside this phase.

##### Check {#v2-airflow-phase-one-certified-readme-md-check}

Show the prepared project result A: 150 / B: 100 / C: 0. Explain which graph orders tasks and which graph orders SQL models. The scaffold message is not an Airflow run.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### airflow-p1-02: Author a small Python DAG with real dbt tasks {#airflow-p1-02}

##### Concept: airflow-p1-02-concept --- Author a small Python DAG with real dbt tasks {#v2-airflow-phase-one-certified-readme-md-concept-airflow-p1-02-concept-author-a-small-python-dag-with-real-dbt-tasks}

TaskFlow functions become Airflow tasks through decorators. Executing a subprocess inside a task can run dbt directly and fail the task when dbt fails. A small graph is enough to prove scheduling and dependencies without requiring a full Cosmos project reconstruction.

```{=html}
<!-- instructor-demo: airflow-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-airflow-phase-one-certified-readme-md-challenge-1}

Replace pipeline.py with an Airflow3.1 SDK DAG: schedule=None, catchup=False, bounded retries and four tasks. prepare seeds project/, build runs models, quality runs tests, publish writes a receipt only after quality. Use subprocess.run with check=True. In quality, check whether the workspace file fail-quality exists; if so raise ValueError describing the intentional drill before running dbt test.

##### Hint {#v2-airflow-phase-one-certified-readme-md-hint-1}

Import dag/task from airflow.sdk. Use absolute project/profile paths derived from the file directory; V2_DBT_BIN selects the prepared executable.

##### Check {#v2-airflow-phase-one-certified-readme-md-check-1}

Import the actual DAG using DagBag and inspect task IDs and edges. Syntax-only checks are supporting evidence. Record any import error before trying a live run.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### airflow-p1-03: Demonstrate the dependency graph and manual run {#airflow-p1-03}

##### Concept: airflow-p1-03-concept --- Demonstrate the dependency graph and manual run {#v2-airflow-phase-one-certified-readme-md-concept-airflow-p1-03-concept-demonstrate-the-dependency-graph-and-manual-run}

A manual run is a specific DAG-run instance with its own task states. schedule=None means Airflow does not create periodic runs automatically; it does not prohibit manual execution. Seeing all tasks green without checking their output would miss a command that ran against the wrong project.

```{=html}
<!-- instructor-demo: airflow-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-airflow-phase-one-certified-readme-md-challenge-2}

In the isolated Airflow runtime import the DAG, run dag.test() or trigger the instructor-installed DAG in Astro, and inspect the four task states and dbt logs. Capture the run ID and result.

##### Hint {#v2-airflow-phase-one-certified-readme-md-hint-2}

Keep AIRFLOW_HOME in this copied workspace. Do not initialize or migrate a shared instructor metadata database.

##### Check {#v2-airflow-phase-one-certified-readme-md-check-2}

The run must execute dbt and finish success. Independently inspect fund_exposure in the workspace database and match A: 150 / B: 100 / C: 0. A parsed DAG alone cannot pass this live/local execution gate.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### airflow-p1-04: Inspect a controlled task failure {#airflow-p1-04}

##### Concept: airflow-p1-04-concept --- Inspect a controlled task failure {#v2-airflow-phase-one-certified-readme-md-concept-airflow-p1-04-concept-inspect-a-controlled-task-failure}

Task logs tell you which command and input failed; downstream state shows whether the dependency blocked publication. A failed data-quality task must not produce a new success receipt. Understanding that boundary is a minimum operational skill even before advanced retry/replay work.

```{=html}
<!-- instructor-demo: airflow-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-airflow-phase-one-certified-readme-md-challenge-3}

After one success remove the receipt, create fail-quality, and rerun the same prepared DAG. Inspect the expected ValueError and the quality/publish states. Remove the marker and repeat the run.

##### Hint {#v2-airflow-phase-one-certified-readme-md-hint-3}

The marker is the documented intentional failure switch. Keep the rest of the starter/project valid.

##### Check {#v2-airflow-phase-one-certified-readme-md-check-3}

Intentional failure: the quality drill raises Intentional quality drill and publish must not create a receipt. After removing the marker, quality and publish succeed and a new receipt exists.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### airflow-p1-05: Explain the run and environment boundaries {#airflow-p1-05}

##### Concept: airflow-p1-05-concept --- Explain the run and environment boundaries {#v2-airflow-phase-one-certified-readme-md-concept-airflow-p1-05-concept-explain-the-run-and-environment-boundaries}

A local Dag.test run proves task execution in the isolated environment; an Astro UI check proves an additional container/runtime integration. Neither proves remote Databricks access unless the tasks actually used that adapter. Honest evidence binds a run to its environment and output.

```{=html}
<!-- instructor-demo: airflow-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-airflow-phase-one-certified-readme-md-challenge-4}

Write a handoff with DAG graph, task/log evidence, result rows, run ID and whether execution was local DuckDB or Astro/Databricks. Explain manual scheduling and why publication depends on tests.

##### Hint {#v2-airflow-phase-one-certified-readme-md-hint-4}

Use the instructor runtime only when configured for this workspace and unique DAG ID.

##### Check {#v2-airflow-phase-one-certified-readme-md-check-4}

Core evidence includes the executed run and business output. Record Astro UI/connected verification separately if unavailable. Phase 2 starts from this supplied solved DAG, so it can be entered independently.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### Executing your local DAG {#v2-airflow-phase-one-certified-readme-md-executing-your-local-dag}

From the project root, `python3 scripts/challenge-v2.py verify airflow phase-one-certified --workspace .local/challenges-v2/airflow/phase-one-certified` copies your work and executes its actual Airflow DAG. It prepares an isolated metadata database, serializes the DAG with `airflow dags reserialize`, then checks a success, marker-induced failure, repair and replay. Inspect the printed task logs and business-result assertions. This avoids mutating an instructor metadata database. The Astro UI exercise still needs the prepared container runtime.

### Phase completion {#v2-airflow-phase-one-certified-readme-md-phase-completion}

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

``` bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify airflow phase-one-certified --workspace .local/challenges-v2/airflow/phase-one-certified --mode offline
```

Execution boundary: Airflow local Dag.test execution; Astro UI and connected adapter gates separate. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

### Optional stretch {#v2-airflow-phase-one-certified-readme-md-optional-stretch}

Try a small variation after completing the core: change one input or contract condition in a second disposable copy, predict the result, and verify your prediction. This does not replace a core task or contribute to its timing budget.


## Source: airflow/phase-one-certified/starter/README.md {#v2-airflow-phase-one-certified-starter-readme-md}

## airflow starter assets {#v2-airflow-phase-one-certified-starter-readme-md-airflow-starter-assets}

Copy this directory into an isolated workspace before editing. The phase README defines the exact baseline command and the completion evidence. Generated databases, logs and evidence belong in that workspace. A starter check passing confirms the baseline is usable; it does not certify completed work.

Files supplied here are part of the learner pack. The instructor solution is stored separately under `challenges/v2-solutions`; it is excluded from the learner appendix and learner archive. See the parent [phase instructions](#v2-airflow-phase-one-certified-readme-md) for the authored-file list, prerequisites and any deliberate defect.


## Source: airflow/phase-two-proficient/README.md {#v2-airflow-phase-two-proficient-readme-md}

## airflow: Phase two --- proficient {#v2-airflow-phase-two-proficient-readme-md-airflow-phase-two-proficient}

This phase has a fixed core of 5 tasks. The advanced standard is a justified design or repair, actual behavioral proof, and a useful handoff. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

### Prerequisites and workspace {#v2-airflow-phase-two-proficient-readme-md-prerequisites-and-workspace}

Prepared Airflow3.1.0/standard provider1.8.0 runtime and a separate dbt executable selected with V2_DBT_BIN. Astro UI route needs instructor-bound isolated workspace.

From the project root run:

``` bash
python3 scripts/challenge-v2.py prepare airflow phase-two-proficient
cd .local/challenges-v2/airflow/phase-two-proficient
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

### Local tool preparation {#v2-airflow-phase-two-proficient-readme-md-local-tool-preparation}

The instructor runs `bash scripts/setup-v2-tools.sh` once from the project root. Before changing into your copied workspace, activate `.local/v2-tools/bin/activate` to make the pinned `dbt` executable available. For Airflow, use `.local/v2-airflow/bin/python` with a workspace-specific `AIRFLOW_HOME`; do not mix these two Python environments. The verifier supplies these paths automatically in a fresh copy.

### Starter behavior {#v2-airflow-phase-two-proficient-readme-md-starter-behavior}

Phase 1 python pipeline.py prints scaffold status. Phase 2 actual DAG imports and supplied project builds; fail-quality is absent until your documented drill.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter airflow phase-two-proficient --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

### Timeline and completion standard {#v2-airflow-phase-two-proficient-readme-md-timeline-and-completion-standard}

Core estimate: **90--120 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Task              Outcome                                            Minutes           Evidence
  ----------------- -------------------------------------------------- ----------------- ------------------------------------------------------------------------------------------------------------------------
  airflow-p2-01     Define bounded replay and input identity           18--24            Both runs must produce three fund rows/250 and matching per-fund values

  airflow-p2-02     Inject failure and observe useful retry behavior   18--24            Show the failed task and blocked publication, then repaired quality and published receipt

  airflow-p2-03     Prove output correctness after recovery            18--24            Correct final state is A: 150 / B: 100 / C: 0, one row per fund, successful quality and a receipt for the repaired run

  airflow-p2-04     Use Astro UI to make an operational decision       18--24            Retain run/task identifiers and a description of the relevant log/state evidence

  airflow-p2-05     Write a short incident handoff                     18--24            The handoff must explain blocked publication and correct recovered output
  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Core challenges {#v2-airflow-phase-two-proficient-readme-md-core-challenges}

#### airflow-p2-01: Define bounded replay and input identity {#airflow-p2-01}

##### Concept: airflow-p2-01-concept --- Define bounded replay and input identity {#v2-airflow-phase-two-proficient-readme-md-concept-airflow-p2-01-concept-define-bounded-replay-and-input-identity}

Replay should state which input and run are repeated. A fixed training fixture makes it possible to distinguish pipeline idempotency from changing business data. max_active_runs=1 reduces overlap for this small exercise but does not automatically provide exactly-once behavior.

```{=html}
<!-- instructor-demo: airflow-p2-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-airflow-phase-two-proficient-readme-md-challenge}

Inspect the supplied solved DAG and project. Define the fixture version and expected output in an incident note. Trigger two distinctly identified runs against the same baseline and compare the output.

##### Hint {#v2-airflow-phase-two-proficient-readme-md-hint}

Use fresh run IDs; do not broadly clear every historical run.

##### Check {#v2-airflow-phase-two-proficient-readme-md-check}

Both runs must produce three fund rows/250 and matching per-fund values. Record run IDs and explain which state is replaced by dbt materialization.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### airflow-p2-02: Inject failure and observe useful retry behavior {#airflow-p2-02}

##### Concept: airflow-p2-02-concept --- Inject failure and observe useful retry behavior {#v2-airflow-phase-two-proficient-readme-md-concept-airflow-p2-02-concept-inject-failure-and-observe-useful-retry-behavior}

A retry repeats a failed task according to an explicit policy. It cannot repair permanently bad input by waiting. This drill uses a marker-controlled transient quality failure so you can explain when to retry, when to repair, and why downstream publication must remain blocked.

```{=html}
<!-- instructor-demo: airflow-p2-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-airflow-phase-two-proficient-readme-md-challenge-1}

Set a bounded retry count/delay, create fail-quality, trigger the run and inspect the failed/retrying task in logs and the prepared Astro UI. Remove the marker according to the instructor drill, then retry only quality for that run.

##### Hint {#v2-airflow-phase-two-proficient-readme-md-hint-1}

In a pure Dag.test rehearsal the persistent marker may exhaust retries. Record that behavior honestly; the UI recovery drill is a separate runtime check.

##### Check {#v2-airflow-phase-two-proficient-readme-md-check-1}

Show the failed task and blocked publication, then repaired quality and published receipt. Record attempts/run identity. Do not mark the task successful manually as a substitute for rerunning the test.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### airflow-p2-03: Prove output correctness after recovery {#airflow-p2-03}

##### Concept: airflow-p2-03-concept --- Prove output correctness after recovery {#v2-airflow-phase-two-proficient-readme-md-concept-airflow-p2-03-concept-prove-output-correctness-after-recovery}

A recovered task state is useful only if the output is correct and publication matches the intended run. Stale tables can fool a verifier when a command was skipped. Compare the independently expected values and receipt identity after the repaired run.

```{=html}
<!-- instructor-demo: airflow-p2-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-airflow-phase-two-proficient-readme-md-challenge-2}

After recovery inspect fund_exposure and receipt.json. Run the graph again with the same input and compare all fund rows. Explain which commands seed, materialize and test rather than relying on previous tables.

##### Hint {#v2-airflow-phase-two-proficient-readme-md-hint-2}

The supplied expected total is250, but use per-fund values too. Delete the old receipt before the failure drill.

##### Check {#v2-airflow-phase-two-proficient-readme-md-check-2}

Correct final state is A: 150 / B: 100 / C: 0, one row per fund, successful quality and a receipt for the repaired run. Show unchanged output after another replay.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### airflow-p2-04: Use Astro UI to make an operational decision {#airflow-p2-04}

##### Concept: airflow-p2-04-concept --- Use Astro UI to make an operational decision {#v2-airflow-phase-two-proficient-readme-md-concept-airflow-p2-04-concept-use-astro-ui-to-make-an-operational-decision}

The UI supports investigation through task state, logs, graph and run details. Opening the interface alone is not advanced proficiency. The useful decision is whether the failure is a stale input, connection issue, code defect or an intentional drill, and which scope should be rerun.

```{=html}
<!-- instructor-demo: airflow-p2-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-airflow-phase-two-proficient-readme-md-challenge-3}

In the prepared local Astro deployment locate this isolated DAG/run, inspect quality logs and the dependency graph, and write the specific repair/rerun decision. If Astro is unavailable, perform local execution and record the UI gate blocked.

##### Hint {#v2-airflow-phase-two-proficient-readme-md-hint-3}

Instructor setup binds the v2 workspace project and unique DAG ID into Astro; do not deploy infrastructure to finish the exercise.

##### Check {#v2-airflow-phase-two-proficient-readme-md-check-3}

Retain run/task identifiers and a description of the relevant log/state evidence. A hosted Astronomer route is optional and requires prepared access.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### airflow-p2-05: Write a short incident handoff {#airflow-p2-05}

##### Concept: airflow-p2-05-concept --- Write a short incident handoff {#v2-airflow-phase-two-proficient-readme-md-concept-airflow-p2-05-concept-write-a-short-incident-handoff}

A runbook entry links symptom, impact, repair, verification and escalation. It should tell another operator how to reproduce the bounded check without clearing unrelated runs or exposing credentials. Advanced skill is demonstrated by a defensible operational decision with output proof.

```{=html}
<!-- instructor-demo: airflow-p2-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-airflow-phase-two-proficient-readme-md-challenge-4}

Write incident.md documenting the marker failure, affected run/tasks, diagnosis, exact repair, scoped replay and result. Include the prepared runtime boundary and remaining access findings.

##### Hint {#v2-airflow-phase-two-proficient-readme-md-hint-4}

Separate the cause from the symptom; state why retry alone did not remove the persistent marker.

##### Check {#v2-airflow-phase-two-proficient-readme-md-check-4}

The handoff must explain blocked publication and correct recovered output. Optional stretch: connect an existing neutral alert transport or prepared Datadog monitor and demonstrate an actionable observation; configuration text alone is insufficient.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### Executing your local DAG {#v2-airflow-phase-two-proficient-readme-md-executing-your-local-dag}

From the project root, `python3 scripts/challenge-v2.py verify airflow phase-two-proficient --workspace .local/challenges-v2/airflow/phase-two-proficient` copies your work and executes its actual Airflow DAG. It prepares an isolated metadata database, serializes the DAG with `airflow dags reserialize`, then checks a success, marker-induced failure, repair and replay. Inspect the printed task logs and business-result assertions. This avoids mutating an instructor metadata database. The Astro UI exercise still needs the prepared container runtime.

### Phase completion {#v2-airflow-phase-two-proficient-readme-md-phase-completion}

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

``` bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify airflow phase-two-proficient --workspace .local/challenges-v2/airflow/phase-two-proficient --mode offline
```

Execution boundary: Airflow local Dag.test execution; Astro UI and connected adapter gates separate. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

### Optional stretch {#v2-airflow-phase-two-proficient-readme-md-optional-stretch}

See the [stretch index](#v2-airflow-phase-two-proficient-stretch-readme-md). Each route has its own prerequisites, timing and completion check; none is part of this fixed core.


## Source: airflow/phase-two-proficient/starter/README.md {#v2-airflow-phase-two-proficient-starter-readme-md}

## airflow starter assets {#v2-airflow-phase-two-proficient-starter-readme-md-airflow-starter-assets}

Copy this directory into an isolated workspace before editing. The phase README defines the exact baseline command and the completion evidence. Generated databases, logs and evidence belong in that workspace. A starter check passing confirms the baseline is usable; it does not certify completed work.

Files supplied here are part of the learner pack. The instructor solution is stored separately under `challenges/v2-solutions`; it is excluded from the learner appendix and learner archive. See the parent [phase instructions](#v2-airflow-phase-two-proficient-readme-md) for the authored-file list, prerequisites and any deliberate defect.


## Source: airflow/phase-two-proficient/stretch/README.md {#v2-airflow-phase-two-proficient-stretch-readme-md}

## airflow: optional stretch selection {#v2-airflow-phase-two-proficient-stretch-readme-md-airflow-optional-stretch-selection}

Legacy alert transport, tiered notifications, freshness, monitoring, publication, Databricks jobs and integrated operations remain under v1/03-airflow-orchestration (each 30--90 minutes; integration may exceed 120). Datadog/hostedAstronomer is conditional on prepared access. Demonstrate a useful operational signal and response, not just configuration.

These routes are separate from core completion. Record timing exceptions rather than shortening an exercise during the audit. Instructor review should select one follow-up based on the learner goal and available environment.

### Full legacy advanced reference {#v2-airflow-phase-two-proficient-stretch-readme-md-full-legacy-advanced-reference}

The following is the preserved legacy advanced route. Its workspace/commands target **v1**; do not run it against the v2 workspace. Core-equivalent topics are retained here for complete teaching coverage, not additional core assignments.

### Phase 2: Production operations {#v2-airflow-phase-two-proficient-stretch-readme-md-phase-2-production-operations}

Phase 1 left you with a running baseline: a scheduled DAG that drives the dbt pipeline on Databricks through a Cosmos `DbtTaskGroup`, with a freshness gate and retries. That makes the pipeline *run*. Phase 2 makes it **operable**: tiered alerting wired through callbacks, an SLA that catches a slow run, a monitoring config, the runbook and consumer-onboarding doc the next on-call engineer reads, structural tests that guard the DAG, the paved-path `DatabricksSubmitRunOperator` variant, and a capstone that assembles a complete production-ready DAG.

Every challenge is self-contained. Each defines the operations idea it uses before you apply it. The shape is always four parts:

-   **Concept** --- the idea, in plain English.
-   **Goal** --- the operational outcome in one line.
-   **Authoring task** --- exactly what you write, and into which starter file.
-   **How to check** --- a command to run, or an observable result.

Write your own answer first; a worked **Solution** follows each challenge for you to compare against. A few conventions hold throughout: Databricks is the only platform; alerting is **Slack-free, PagerDuty-free** --- P1 emits a Datadog event (support pages the on-call via xMatters from the payload), P2 notifies Microsoft Teams through the vendor-neutral `send_alert`, P3 opens a ticket; the transports degrade to a log line when their credential env var is unset, so everything runs offline in the DAG-load check.

Budget roughly \~10 min per challenge --- a pacing target, not a deadline. Work the challenges in order: they build on each other, and challenge 10 assembles the pieces into one production-ready DAG.

------------------------------------------------------------------------

#### Challenge 1: The vendor-neutral alert transport {#v2-airflow-phase-two-proficient-stretch-readme-md-challenge-1-the-vendor-neutral-alert-transport}

**Concept.** Every alert in this pipeline goes through one boundary: `send_alert` in `data_products/portfolio_analytics/include/alerting/notifications.py`. It posts to a team-chat **webhook** held in an Airflow HTTP connection (`alert_webhook`) --- there is no Slack SDK and no hard-coded webhook URL in the code (the Teams webhook lives in the connection, not the source). That single boundary is what keeps the pipeline vendor-neutral: swap the webhook behind the connection and nothing else changes. Callbacks call `send_alert(text=...)`; they never know which chat tool is on the other end.

**Goal.** One transport function the P2 (team-chat) tier calls, with no chat vendor named in the code.

**Authoring task.** Read `data_products/portfolio_analytics/include/alerting/notifications.py` and confirm its shape: it builds an `HttpHook(method="POST", http_conn_id="alert_webhook")`, assembles a `{"text": text}` payload (adding `channel` only when passed), and `hook.run(...)`s it. This file ships complete --- your job is to understand it, because every callback in the next challenge calls it. Confirm there is no hard-coded webhook URL or vendor name anywhere in the file.

**How to check.**

``` bash
python -c "import ast; ast.parse(open('data_products/portfolio_analytics/include/alerting/notifications.py').read()); print('parses OK')"
grep -niE 'https?://|slack_sdk|WebhookClient|hooks\.slack' data_products/portfolio_analytics/include/alerting/notifications.py || echo "no hard-coded URL or vendor SDK — good"
```

The parse should succeed and the grep should find nothing --- the only coupling is to the `alert_webhook` Airflow connection id.

Worked answer 1 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 2: Tiered failure alerting --- page on P1, notify on P2 {#v2-airflow-phase-two-proficient-stretch-readme-md-challenge-2-tiered-failure-alerting-page-on-p1-notify-on-p2}

**Concept.** Not every event deserves the same channel. A task that fails after exhausting its retries means the pipeline is down and the 07:30 UK SLA is at risk --- that is a **P1**: it emits a Datadog event (the auto sink; support pages the on-call via xMatters from the payload) *and* notifies Microsoft Teams. Matching severity to channel is the whole point of tiering: an xMatters page wakes a human, so it is reserved for "the mart will be late". The `on_failure_callback` is set in `default_args`, so it fires for any task in the DAG once its retries are spent.

**Goal.** A failure callback that emits a Datadog event (P1, the auto sink) and posts to Microsoft Teams (P2), wired so it fires once a task's retries are exhausted.

**Authoring task.** Read `on_failure_callback(context)` in `data_products/portfolio_analytics/dags/callbacks.py`. It ships complete --- your job is to understand it, not retype it. Trace how it pulls `task_instance` and `dag_run` from `context`, builds a `detail` dict (dag_id, task_id, run_id, log_url, exception), then calls the `_emit_datadog(...)` helper (severity `"error"`) and `send_alert(...)` with a message naming the DAG, task, log URL, and a runbook link. The `_emit_datadog` helper posts to the Datadog Events API (carrying the MDS routing tags; support pages the on-call via xMatters from the payload) and falls back to a log line when `DD_API_KEY` is unset.

**How to check.**

``` bash
python -c "import ast; ast.parse(open('data_products/portfolio_analytics/dags/callbacks.py').read()); print('parses OK')"
grep -niE 'slack_sdk|hooks\.slack|slack\.com' data_products/portfolio_analytics/dags/callbacks.py || echo "no Slack SDK — good"
```

The file parses and contains no Slack reference. The behavioural proof comes in challenge 8's structural test, which exercises the callback with the transports stubbed.

Worked answer 2 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 3: The P2 and P3 tiers --- SLA miss and retry {#v2-airflow-phase-two-proficient-stretch-readme-md-challenge-3-the-p2-and-p3-tiers-sla-miss-and-retry}

**Concept.** The other two tiers round out the taxonomy. An **SLA miss** means the pipeline was slow, not down --- the DAG still ran (or will), so it is a **P2**: notify team chat, do not page. A **retry** is expected (a transient warehouse blip) --- nobody needs paging or even pinging, but a flaky task should leave a trail, so it is a **P3**: open a ticket. `on_sla_miss_callback` has a fixed signature Airflow calls with the missed-task list; `on_retry_callback` gets the same `context` dict as the failure callback.

**Goal.** An SLA-miss callback that notifies team chat (P2) and a retry callback that opens a ticket (P3) --- neither pages.

**Authoring task.** Read the two remaining callbacks in `data_products/portfolio_analytics/dags/callbacks.py`. They ship complete --- your job is to understand them. `on_sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis)` builds a comma-joined list of the missed `task_id`s and `send_alert(...)`s a P2 message naming the DAG and the tasks past SLA. `on_retry_callback(context)` pulls `task_instance`, reads its `try_number`, and calls `open_ticket(...)` (the P3 helper that logs when `TICKET_WEBHOOK_URL` is unset) with the task id and log url.

**How to check.**

``` bash
python -c "import ast; ast.parse(open('data_products/portfolio_analytics/dags/callbacks.py').read()); print('parses OK')"
```

The file parses. In the DAG, `on_sla_miss_callback` is wired on the DAG object and `on_retry_callback` in `default_args`; the structural test in challenge 8 asserts the DAG carries an `sla_miss_callback`.

Worked answer 3 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 4: Wire the callbacks and the SLA into the DAG {#v2-airflow-phase-two-proficient-stretch-readme-md-challenge-4-wire-the-callbacks-and-the-sla-into-the-dag}

**Concept.** Callbacks do nothing until they are attached. Three attachment points, each at the right scope: `on_failure_callback` and `on_retry_callback` go in `default_args` (every task inherits them); `sla_miss_callback` goes on the `DAG(...)` object (it is a DAG-level event); `on_success_callback` goes on the **final task only** (so it fires once per successful run, not once per task). The SLA itself is a `timedelta` on the task you want to time --- here `publish_to_catalog`, because end-to-end-by-90-minutes is what the 07:30 UK deadline means.

**Goal.** The three callback tiers and the 90-minute SLA wired at the right scopes so a failure pages, an SLA miss notifies, and a green run pings once.

**Authoring task.** Nothing to write --- this one ships already wired, and your job is to verify each attachment point so you know where callbacks hang. In `data_products/portfolio_analytics/dags/portfolio_analytics_daily.py`: confirm the four callbacks are imported from `callbacks`; confirm `on_failure_callback` and `on_retry_callback` are in `default_args`; confirm `sla_miss_callback=on_sla_miss_callback` is on the `DAG(...)` call; and confirm `publish_to_catalog` has `sla=timedelta(minutes=90)` and `on_success_callback=on_success_callback`.

**How to check.**

``` bash
mise run challenge:verify 03
pytest data_products/portfolio_analytics/tests/ -q -k "callback or sla"
```

The DAG loads, and the structural tests confirm `default_args` carries a failure callback, the DAG carries an `sla_miss_callback`, and `publish_to_catalog` has an SLA.

Worked answer 4 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 5: The source-freshness gate as a contract {#v2-airflow-phase-two-proficient-stretch-readme-md-challenge-5-the-source-freshness-gate-as-a-contract}

**Concept.** Phase 1 wired the freshness task; here you make its thresholds a deliberate **contract** rather than a default. `dbt source freshness` fails the gate only on an `error_after` breach, so where you set `error_after` is where you draw the line between "stale enough to block" and "old but acceptable". The custodian feed is the binding one: it lands by 02:00 UK and the SLA is 07:30, so a 6-hour `error_after` means a feed more than 6 hours stale blocks the run --- but a feed 5 hours old (past the 4-hour `warn_after`) only warns and the pipeline proceeds on borderline data. That gap is a decision, not an accident.

**Goal.** A freshness contract whose `error_after` on the custodian source is set where you can defend it, gating the DAG.

**Authoring task.** Read `data_products/portfolio_analytics/dbt/models/sources.yml` and confirm the custodian source's `freshness` block: `warn_after: {count: 4, period: hour}` and `error_after: {count: 6, period: hour}`, with `loaded_at_field: _extracted_at`. This ships configured --- your task is to exercise it and decide whether 6 hours is the right blocking threshold for *your* SLA, then prove the gate fires.

**How to check.**

``` bash
(cd data_products/portfolio_analytics/dbt && dbt source freshness --select source:custodian)
```

With the bundled data the custodian line reports `pass` or `warn`. Tighten `error_after` to `{count: 0, period: hour}`, re-run, and watch it flip to `error` (exit non-zero) --- that is the gate that would stop the DAG. Put it back to 6 hours.

Worked answer 5 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 6: The monitoring config {#v2-airflow-phase-two-proficient-stretch-readme-md-challenge-6-the-monitoring-config}

**Concept.** Alerting tells you when something just broke; **monitoring** tells you when something is *drifting* before it breaks. A monitoring config declares the panels that track pipeline health --- each a metric, an alert condition, and a channel. Five panels cover most pipelines (run status, duration, task-failure rate, SLA compliance, source freshness). The sixth is the one that catches the nastiest failure mode: a **fresh-but-truncated** feed. Freshness watches the clock; a volume-anomaly panel watches the row count, so a short extract that passes freshness but fails completeness is caught at ingestion, not three steps later at the test gate.

**Goal.** A six-panel monitoring config whose channels are Slack-free and whose sixth panel catches a fresh-but-short feed.

**Authoring task.** Read `data_products/portfolio_analytics/include/monitoring/portfolio_analytics.yml` and confirm the six panels. Check that every `alert_channel` is one of `datadog` / `teams` / `ticket` (no Slack, no PagerDuty), that "SLA compliance" routes to `datadog, teams`, and that "Source volume anomaly" fires when today's `holdings_raw` row count drops below 80% of the trailing-7-day average. This file ships complete; understand why the sixth panel exists --- it is the `INC`-style fresh-but-truncated failure mode the first five all miss.

**How to check.**

``` bash
grep -cE '^  - name:' data_products/portfolio_analytics/include/monitoring/portfolio_analytics.yml   # expect 6
grep -niE 'alert_channel.*slack' data_products/portfolio_analytics/include/monitoring/portfolio_analytics.yml || echo "no Slack channel — good"
```

There are six panels, and no `alert_channel` routes to Slack.

Worked answer 6 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 7: The runbook and the consumer guide {#v2-airflow-phase-two-proficient-stretch-readme-md-challenge-7-the-runbook-and-the-consumer-guide}

**Concept.** Two documents turn a pipeline you understand into one anyone can operate. The **runbook** is the page the on-call engineer opens when an alert lands: service overview, architecture, a common-alerts table (symptom → diagnosis → remediation), an escalation matrix, and manual procedures. The **consumer guide** is the page a downstream user reads to adopt the data product: where the marts live, what each column means, sample queries, known limitations, and freshness. Both live in the repo next to the DAG so they change in the same pull request the code does.

**Goal.** A runbook the next on-call engineer can act on and a consumer guide a downstream user can onboard from --- both naming the real marts and the tiered, Slack-free alert channels.

**Authoring task.** Read `data_products/portfolio_analytics/include/runbooks/portfolio_analytics.md` and `data_products/portfolio_analytics/include/launch/consumer-guide.md`. Confirm the runbook's common-alerts table covers source-freshness error, dbt build failure, dbt test failure, SLA miss, and the fresh-but-truncated feed; that escalation names Datadog/xMatters and Microsoft Teams (no Slack); and that the consumer guide documents `fct_portfolio_returns`, `agg_fund_exposure` and `agg_fund_daily_exposure` with sample queries. These ship complete --- verify they are internally consistent with your DAG (task names, schedule, SLA, marts).

**How to check.**

``` bash
grep -c "^### Alert" data_products/portfolio_analytics/include/runbooks/portfolio_analytics.md       # expect 5
grep -E "fct_portfolio_returns|agg_fund_exposure|agg_fund_daily_exposure" data_products/portfolio_analytics/include/launch/consumer-guide.md
grep -niE 'slack' data_products/portfolio_analytics/include/runbooks/portfolio_analytics.md data_products/portfolio_analytics/include/launch/consumer-guide.md | grep -viE 'slack-free' || echo "no Slack — good"
```

Five alert entries, all three marts named in the consumer guide, no Slack anywhere.

Worked answer 7 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 8: Structural tests for the DAG {#v2-airflow-phase-two-proficient-stretch-readme-md-challenge-8-structural-tests-for-the-dag}

**Concept.** The cheapest, highest-value Airflow test is the **structural** test: does the file parse into the expected shape, without hitting Databricks? It runs in milliseconds and catches most breakage --- a bad import, a renamed task, a dropped dependency edge, a secret accidentally pasted into the DAG. The test parses the `dags/` files (no DagBag, no warehouse, no airflow), confirms the tiered callbacks and the SLA are wired at their scopes, and greps the DAG files for a token literal that must never be committed. The `freshness → pipeline → publish` chain is the learner deliverable and is checked separately by `mise run challenge:verify 03`.

**Goal.** A structural test suite that proves the DAG parses, has the right chain, carries the callbacks and SLA, and embeds no secret.

**Authoring task.** Read `data_products/portfolio_analytics/tests/test_dag_structure.py` and run it. Confirm it covers: both DAGs and the callbacks module parse; the primary DAG wires `on_failure_callback` / `on_retry_callback` (in `default_args`), `sla_miss_callback` (DAG-level), `on_success_callback` (publish task), and `sla=timedelta(minutes=90)` on `publish_to_catalog`; and no DAG file contains a `dapi…` token or a workspace-host literal. This ships complete --- your job is to run it and read what each assertion guards. (The wiring chain is checked by `mise run challenge:verify 03`.)

**How to check.**

``` bash
pytest data_products/portfolio_analytics/tests/ -q
```

All assertions pass. To prove the secret check bites, paste a fake `token = "dapi0123456789abcdef0123"` line into a DAG file and re-run --- the `test_no_secret_literals_in_dag_files` test fails. Remove it.

Worked answer 8 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 9: Stretch --- the paved-path `DatabricksSubmitRunOperator` variant {#v2-airflow-phase-two-proficient-stretch-readme-md-challenge-9-stretch-the-paved-path-databrickssubmitrunoperator-variant}

**Concept.** The Cosmos variant runs dbt **on the Airflow worker**. Capital Group's paved path runs dbt **inside Databricks** as a Job: each Airflow task submits one step via `DatabricksSubmitRunOperator` and polls until it finishes. The trade-off is granularity for locality --- you lose Cosmos's per-model tasks (the Databricks Job is one opaque step in the Airflow graph), but the warehouse autoscales for the build, logs live with the data in the Databricks Jobs UI, and the worker pool stays free. Knowing both shapes is the point: you will meet Cosmos in dbt-centric shops and Submit-Run in Databricks-centric ones.

**Goal.** A second DAG expressing the same pipeline as four `DatabricksSubmitRunOperator` steps that submit dbt-wrapping notebooks to Databricks.

**Authoring task.** Read `data_products/portfolio_analytics/dags/databricks_submit_run_dag.py` and confirm its shape: four `DatabricksSubmitRunOperator` tasks (`check_source_freshness` → `run_dbt_models` → `test_dbt_models` → `generate_dbt_docs`), each submitting a `notebook_task` under `/Workspace/data-creators/dbt/portfolio_analytics` to the `databricks_default` connection, with the SLA on `run_dbt_models` and the tiered callbacks reused from `callbacks.py`. This ships complete --- wire it by confirming it loads alongside the primary DAG.

**How to check.**

``` bash
mise run challenge:verify 03
```

`mise run challenge:verify 03` confirms the primary DAG's wiring. Both DAGs also parse (Challenge 8's structural test), and the submit-run DAG reuses `on_failure_callback` and `on_sla_miss_callback` --- so P1 (down) and P2 (slow) alert identically across both shapes. It does **not** wire `on_retry_callback` or `on_success_callback`, so despite setting `retries=2` it raises no P3 ticket on a flaky retry and emits no success signal. Spotting that gap is the exercise: compare its imports against the four in `portfolio_analytics_daily.py`.

Worked answer 9 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 10: Capstone --- a complete production-ready DAG {#v2-airflow-phase-two-proficient-stretch-readme-md-challenge-10-capstone-a-complete-production-ready-dag}

This is the integrative challenge. Earlier challenges each added one operational piece; here you confirm they compose into one DAG that an on-call team could own, and you prove it green end to end.

**Concept.** "Production-ready" is not one feature --- it is the sum: the pipeline runs on a defensible schedule, fails fast on bad inputs, retries the transient, pages the right person at the right severity, times itself against the business SLA, and ships with the runbook and consumer doc that let someone else operate it. `portfolio_analytics_daily` is that sum. The capstone is to walk the whole DAG against the checklist and run the verification gate.

**Goal.** One DAG that passes the full production checklist and the DAG-load verification gate.

**Authoring task.** Walk `data_products/portfolio_analytics/dags/portfolio_analytics_daily.py` against this checklist and fix any gap you find:

1.  **Schedule** --- timezone-aware weekday cron (`0 6 * * 1-5`, `Europe/London`), `catchup=False`, `max_active_runs=1`.
2.  **Fail fast** --- `source_freshness_check` is the first task and gates the build.
3.  **Build** --- the Cosmos `DbtTaskGroup` renders the dbt project.
4.  **Retries** --- `retries=2` with exponential backoff in `default_args`.
5.  **Tiered alerting** --- `on_failure_callback` (P1+P2) and `on_retry_callback` (P3) in `default_args`; `sla_miss_callback` (P2) on the DAG.
6.  **SLA** --- `publish_to_catalog` carries `sla=timedelta(minutes=90)` and the success notification.
7.  **Docs** --- the runbook, consumer guide, and monitoring config are present and consistent.
8.  **No secrets** --- no token or host literal in any DAG file.

**How to check.**

``` bash
pytest data_products/portfolio_analytics/tests/ -q
mise run challenge:verify 03
```

The structural tests pass and the DAG-wiring gate is green.

Worked answer 10 is supplied separately in the instructor pack: `challenges/v2-solutions/airflow/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Phase 2 Summary {#v2-airflow-phase-two-proficient-stretch-readme-md-phase-2-summary}

You took the running DAG and made it operable: a vendor-neutral alert transport, tiered Slack-free alerting (Datadog auto-sink + xMatters page / Teams notify / ticket) wired at the right scopes, the freshness gate as a deliberate contract, a six-panel monitoring config that catches a fresh-but-short feed, the runbook and consumer guide the next operator reads, structural tests that guard the DAG shape and ban committed secrets, the paved-path `DatabricksSubmitRunOperator` variant, and a capstone that proves the whole thing is a complete, production-ready orchestration.


## Source: kafka/README.md {#v2-kafka-readme-md}

## kafka challenges {#v2-kafka-readme-md-kafka-challenges}

This route develops a bounded Phase 1 standard. Kafka is optional throughout the course. Read concept explanations before attempting the task; retain commands/results and your reasoning.

### Before you start {#v2-kafka-readme-md-before-you-start}

Optional route. Prepared apache/kafka4.1.0 broker, confluent-kafka2.11.1 bridge and isolated Airflow3.1.0 runtime. Instructor supplies topic/group/runtime boundaries. Work in a copied phase workspace. Phase 2, when offered, supplies its entry fixture. [Pack navigation](#v2-readme-md) explains the course/clinic placement and version selection.

### Suggested timeline and tasks {#v2-kafka-readme-md-suggested-timeline-and-tasks}

  ------------------------------------------------------------------------------------------------------------------------------------------------
  Phase       Task ID                       Title                                                 Teaching concept      Core/stretch   Minutes
  ----------- ----------------------------- ----------------------------------------------------- --------------------- -------------- -----------
  Phase 1     [kafka-p1-01](#kafka-p1-01)   Read the dataset-arrived contract                     kafka-p1-01-concept   core           12--18

  Phase 1     [kafka-p1-02](#kafka-p1-02)   Start the prepared local broker and inspect a topic   kafka-p1-02-concept   core           12--18

  Phase 1     [kafka-p1-03](#kafka-p1-03)   Produce and follow a uniquely identified event        kafka-p1-03-concept   core           12--18

  Phase 1     [kafka-p1-04](#kafka-p1-04)   Verify the dbt output belongs to the event            kafka-p1-04-concept   core           12--18

  Phase 1     [kafka-p1-05](#kafka-p1-05)   Replay and explain duplicate policy                   kafka-p1-05-concept   core           12--18
  ------------------------------------------------------------------------------------------------------------------------------------------------

Inclusive phase estimates: Phase 1 60--90 minutes. These estimates are unpiloted. Reading, normal waits, checking and handoff are included; optional stretch is separately identified. [Timing review](practice/client/designer/reviews/TIMING-AUDIT.md) records current exceptions and the pilot protocol.

### Choose your phase {#v2-kafka-readme-md-choose-your-phase}

[Phase one---certified](#v2-kafka-phase-one-certified-readme-md) establishes minimum understanding. [Phase two---proficient](#v2-kafka-phase-two-proficient-readme-md) is explicitly not offered; its page is a structural placeholder.

### Teaching concepts {#v2-kafka-readme-md-teaching-concepts}

The concept column and phase concept headings identify what an instructor can demonstrate. A useful demonstration shows the before state, the relevant change, and independent output/state evidence. The generated instructor companion reproduces concept explanations from these phase READMEs, so notes and challenges share a source.

Suggested destination: Optional event-driven clinic, outside mandatory course route. Advanced clinics and optional work require separate time; they do not silently consume protected core teaching windows.


## Source: kafka/phase-one-certified/README.md {#v2-kafka-phase-one-certified-readme-md}

## kafka: Phase one --- certified {#v2-kafka-phase-one-certified-readme-md-kafka-phase-one-certified}

**Optional course route.** This phase has a fixed core of 5 tasks. The minimum standard is a working result with the underlying tool concepts explained. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

### Prerequisites and workspace {#v2-kafka-phase-one-certified-readme-md-prerequisites-and-workspace}

Optional route. Prepared apache/kafka4.1.0 broker, confluent-kafka2.11.1 bridge and isolated Airflow3.1.0 runtime. Instructor supplies topic/group/runtime boundaries.

From the project root run:

``` bash
python3 scripts/challenge-v2.py prepare kafka phase-one-certified
cd .local/challenges-v2/kafka/phase-one-certified
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

### Local tool preparation {#v2-kafka-phase-one-certified-readme-md-local-tool-preparation}

The instructor runs `bash scripts/setup-v2-tools.sh` once from the project root. Before changing into your copied workspace, activate `.local/v2-tools/bin/activate` to make the pinned `dbt` executable available. For Airflow, use `.local/v2-airflow/bin/python` with a workspace-specific `AIRFLOW_HOME`; do not mix these two Python environments. The verifier supplies these paths automatically in a fresh copy.

### Starter behavior {#v2-kafka-phase-one-certified-readme-md-starter-behavior}

python -m json.tool event.json succeeds; supplied DAG imports. Broker and live event chain require explicit runtime checks.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter kafka phase-one-certified --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

### Timeline and completion standard {#v2-kafka-phase-one-certified-readme-md-timeline-and-completion-standard}

Core estimate: **60--90 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Task              Outcome                                               Minutes           Evidence
  ----------------- ----------------------------------------------------- ----------------- ----------------------------------------------------------------------------------------------------------------
  kafka-p1-01       Read the dataset-arrived contract                     12--18            Record the event identity and expected A: 150 / B: 100 / C: 0 output

  kafka-p1-02       Start the prepared local broker and inspect a topic   12--18            A broker metadata call must return the intended topic/partition

  kafka-p1-03       Produce and follow a uniquely identified event        12--18            Capture event ID, broker partition/offset, run ID and eventual task outcome

  kafka-p1-04       Verify the dbt output belongs to the event            12--18            Live completion needs the broker event, actual Airflow run, matching receipt and A: 150 / B: 100 / C: 0 output

  kafka-p1-05       Replay and explain duplicate policy                   12--18            Show identical replay yields the same run ID and unchanged result without a second conflicting run
  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Core challenges {#v2-kafka-phase-one-certified-readme-md-core-challenges}

#### kafka-p1-01: Read the dataset-arrived contract {#kafka-p1-01}

##### Concept: kafka-p1-01-concept --- Read the dataset-arrived contract {#v2-kafka-phase-one-certified-readme-md-concept-kafka-p1-01-concept-read-the-dataset-arrived-contract}

Kafka retains records in an ordered partition log; consumer groups track offsets. A dataset-arrived event carries identity/version/location so downstream processing can select the intended dataset. It is not the dataset itself. This route deliberately uses a supplied immutable fixture location rather than executing arbitrary producer-provided paths.

```{=html}
<!-- instructor-demo: kafka-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-kafka-phase-one-certified-readme-md-challenge}

Inspect event.json, validate its required fields and change only event_id in learner-event.json. Explain dataset_id holdings, fixture-v1 and fixture://holdings-v1. Identify the prepared Airflow/dbt output.

##### Hint {#v2-kafka-phase-one-certified-readme-md-hint}

The supplied pipeline accepts exactly this prepared dataset contract. Kafka is optional and does not gate mandatory Airflow/capstone.

##### Check {#v2-kafka-phase-one-certified-readme-md-check}

Record the event identity and expected A: 150 / B: 100 / C: 0 output. A malformed event must be rejected by the bridge before a trigger.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### kafka-p1-02: Start the prepared local broker and inspect a topic {#kafka-p1-02}

##### Concept: kafka-p1-02-concept --- Start the prepared local broker and inspect a topic {#v2-kafka-phase-one-certified-readme-md-concept-kafka-p1-02-concept-start-the-prepared-local-broker-and-inspect-a-topic}

A topic is a retained stream; one consumer group can resume from committed offsets while a different group reads independently. The instructor supplies the broker runtime and unique topic/group names so learners focus on event flow rather than cluster provisioning.

```{=html}
<!-- instructor-demo: kafka-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-kafka-phase-one-certified-readme-md-challenge-1}

Run docker compose -p v2-kafka up -d in the copied starter. Use the supplied bridge topic preparation command with your topic prefix, then inspect broker/topic metadata. Wait for readiness before sending a record.

##### Hint {#v2-kafka-phase-one-certified-readme-md-hint-1}

The compose broker binds localhost:19092. Instructor preparation includes image pull and the isolated Airflow deployment.

##### Check {#v2-kafka-phase-one-certified-readme-md-check-1}

A broker metadata call must return the intended topic/partition. Record topic/group/offset observations. Without Docker/broker, this live gate is blocked; the offline contract check remains available.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### kafka-p1-03: Produce and follow a uniquely identified event {#kafka-p1-03}

##### Concept: kafka-p1-03-concept --- Produce and follow a uniquely identified event {#v2-kafka-phase-one-certified-readme-md-concept-kafka-p1-03-concept-produce-and-follow-a-uniquely-identified-event}

A successful producer delivery confirms broker acceptance; it does not prove orchestration or model output. The bridge validates the payload, derives a deterministic DAG-run ID from event identity and triggers the prepared DAG. Follow that identity across boundaries to assess the full chain.

```{=html}
<!-- instructor-demo: kafka-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-kafka-phase-one-certified-readme-md-challenge-2}

Use the supplied bridge produce command for learner-event.json and consume one record with your assigned topic/group. Inspect the emitted run ID, then wait for that Airflow run.

##### Hint {#v2-kafka-phase-one-certified-readme-md-hint-2}

The bridge uses the instructor-configured Airflow CLI inside the runtime boundary; keep broker/Airflow reachability explicit.

##### Check {#v2-kafka-phase-one-certified-readme-md-check-2}

Capture event ID, broker partition/offset, run ID and eventual task outcome. Producer exit alone cannot pass. The exact event payload must appear in the run configuration and publication receipt.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### kafka-p1-04: Verify the dbt output belongs to the event {#kafka-p1-04}

##### Concept: kafka-p1-04-concept --- Verify the dbt output belongs to the event {#v2-kafka-phase-one-certified-readme-md-concept-kafka-p1-04-concept-verify-the-dbt-output-belongs-to-the-event}

An event can be valid while referring to the wrong dataset version. The prepared DAG checks fixture identity and dbt produces the known holdings result. A receipt ties the result to run/event identity but independent output inspection still matters.

```{=html}
<!-- instructor-demo: kafka-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-kafka-phase-one-certified-readme-md-challenge-3}

Inspect receipt.json after the event-triggered run and query the copied project database. Compare the event ID/version/location to the produced record. Verify all three fund rows and total250.

##### Hint {#v2-kafka-phase-one-certified-readme-md-hint-3}

Use the supplied expected-output oracle and the event metadata, not just a successful task state.

##### Check {#v2-kafka-phase-one-certified-readme-md-check-3}

Live completion needs the broker event, actual Airflow run, matching receipt and A: 150 / B: 100 / C: 0 output. Offline event simulation must never be labelled end-to-end Kafka execution.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### kafka-p1-05: Replay and explain duplicate policy {#kafka-p1-05}

##### Concept: kafka-p1-05-concept --- Replay and explain duplicate policy {#v2-kafka-phase-one-certified-readme-md-concept-kafka-p1-05-concept-replay-and-explain-duplicate-policy}

The bridge retries the same deterministic run ID if it crashes before offset commit. An existing run can be reused only when its stored event payload matches. This makes trigger requests idempotent for identical events in the training setting; it does not promise distributed exactly-once processing or allow conflicting payloads to share identity.

```{=html}
<!-- instructor-demo: kafka-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-kafka-phase-one-certified-readme-md-challenge-4}

Produce the identical event again and consume it. Inspect the existing-run decision and group offset. In a disposable test change the payload while retaining event_id and explain why the conflict must be rejected. Clean only your compose project when instructed.

##### Hint {#v2-kafka-phase-one-certified-readme-md-hint-4}

The bridge commits offsets only after an accepted/new-or-identical run. A conflict remains uncommitted for operator diagnosis.

##### Check {#v2-kafka-phase-one-certified-readme-md-check-4}

Show identical replay yields the same run ID and unchanged result without a second conflicting run. Record the conflicting-payload failure. Cleanup uses docker compose -p v2-kafka down, never a global prune.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### Prepared bridge commands {#v2-kafka-phase-one-certified-readme-md-prepared-bridge-commands}

From the project root, use the pinned Airflow Python environment and the absolute path to your copied event/workspace. These are a command reference for the prepared runtime; Docker/Airflow availability remains a prerequisite.

``` bash
.local/v2-airflow/bin/python scripts/v2_kafka_bridge.py validate --event .local/challenges-v2/kafka/phase-one-certified/learner-event.json
.local/v2-airflow/bin/python scripts/v2_kafka_bridge.py prepare-topic --topic v2-dataset-arrived
.local/v2-airflow/bin/python scripts/v2_kafka_bridge.py produce --event .local/challenges-v2/kafka/phase-one-certified/learner-event.json
.local/v2-airflow/bin/python scripts/v2_kafka_bridge.py consume --airflow .local/v2-airflow/bin/airflow --receipt /path/to/prepared/receipt.json
.local/v2-airflow/bin/python scripts/v2_kafka_bridge.py verify-chain --event .local/challenges-v2/kafka/phase-one-certified/learner-event.json --receipt /path/to/prepared/receipt.json --project /path/to/prepared/project
```

The instructor replaces the prepared runtime paths and supplies `AIRFLOW_HOME`, a parsed/unpaused DAG, scheduler/API runtime, and `V2_DBT_BIN` visible to task workers. Topic/group flags must match on producer and consumer; use learner-specific names on a shared broker. The compose localhost listener supports a host-side bridge; a bridge inside another container needs an instructor-configured reachable listener.

Duplicate acknowledgement requires a matching **completed** receipt. A crash after trigger but before offset commit can leave an existing run without a receipt; the bridge deliberately stops and leaves the offset uncommitted for exact-run investigation. Its policy is bounded training idempotency, not automatic distributed recovery. `verify-chain` binds the actual broker evidence file, run receipt, event payload and per-fund dbt output. A JSON fixture alone cannot satisfy that check.

### Phase completion {#v2-kafka-phase-one-certified-readme-md-phase-completion}

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

``` bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify kafka phase-one-certified --workspace .local/challenges-v2/kafka/phase-one-certified --mode offline
```

Execution boundary: Kafka broker→consumer→Airflow→dbt; offline payload checks are supporting evidence. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

### Optional stretch {#v2-kafka-phase-one-certified-readme-md-optional-stretch}

Try a small variation after completing the core: change one input or contract condition in a second disposable copy, predict the result, and verify your prediction. This does not replace a core task or contribute to its timing budget.


## Source: kafka/phase-one-certified/starter/README.md {#v2-kafka-phase-one-certified-starter-readme-md}

## kafka starter assets {#v2-kafka-phase-one-certified-starter-readme-md-kafka-starter-assets}

Copy this directory into an isolated workspace before editing. The phase README defines the exact baseline command and the completion evidence. Generated databases, logs and evidence belong in that workspace. A starter check passing confirms the baseline is usable; it does not certify completed work.

Files supplied here are part of the learner pack. The instructor solution is stored separately under `challenges/v2-solutions`; it is excluded from the learner appendix and learner archive. See the parent [phase instructions](#v2-kafka-phase-one-certified-readme-md) for the authored-file list, prerequisites and any deliberate defect.


## Source: kafka/phase-two-proficient/README.md {#v2-kafka-phase-two-proficient-readme-md}

## kafka: Phase two --- not offered {#v2-kafka-phase-two-proficient-readme-md-kafka-phase-two-not-offered}

This tool has a Phase 1 route only. This structural placeholder contains no assignment, timing estimate or certification gate. The empty starter/ directory is retained by convention. Return to the [tool index](#v2-kafka-readme-md).


## Source: capstone/README.md {#v2-capstone-readme-md}

## capstone challenges {#v2-capstone-readme-md-capstone-challenges}

This route develops minimum competence followed by advanced behavioral proof. Read concept explanations before attempting the task; retain commands/results and your reasoning.

### Before you start {#v2-capstone-readme-md-before-you-start}

Prepared local dbt environment and seven supplied Atlas seed CSVs; no cloud access needed for this focused core. Connected Atlas rehearsal remains a separate instructor gate. Work in a copied phase workspace. Phase 2, when offered, supplies its entry fixture. [Pack navigation](#v2-readme-md) explains the course/clinic placement and version selection.

### Suggested timeline and tasks {#v2-capstone-readme-md-suggested-timeline-and-tasks}

  ------------------------------------------------------------------------------------------------------------------------------------------------------------
  Phase       Task ID                             Title                                                    Teaching concept         Core/stretch   Minutes
  ----------- ----------------------------------- -------------------------------------------------------- ------------------------ -------------- -----------
  Phase 1     [capstone-p1-01](#capstone-p1-01)   State the consumer population and grain                  capstone-p1-01-concept   core           18--24

  Phase 1     [capstone-p1-02](#capstone-p1-02)   Build the valid-trade domain fact                        capstone-p1-02-concept   core           18--24

  Phase 1     [capstone-p1-03](#capstone-p1-03)   Author the active portfolio summary                      capstone-p1-03-concept   core           18--24

  Phase 1     [capstone-p1-04](#capstone-p1-04)   Investigate expected omission and a defective join       capstone-p1-04-concept   core           18--24

  Phase 1     [capstone-p1-05](#capstone-p1-05)   Prove minimum data quality and give a consumer handoff   capstone-p1-05-concept   core           18--24

  Phase 2     [capstone-p2-01](#capstone-p2-01)   Build a meaningful performance report                    capstone-p2-01-concept   core           18--24

  Phase 2     [capstone-p2-02](#capstone-p2-02)   Rank advisor books with explicit ties                    capstone-p2-02-concept   core           18--24

  Phase 2     [capstone-p2-03](#capstone-p2-03)   Build the regional rollup from its declared dependency   capstone-p2-03-concept   core           18--24

  Phase 2     [capstone-p2-04](#capstone-p2-04)   Reconcile independently and reject a defect              capstone-p2-04-concept   core           18--24

  Phase 2     [capstone-p2-05](#capstone-p2-05)   Present a fixed completed core and select stretch        capstone-p2-05-concept   core           18--24
  ------------------------------------------------------------------------------------------------------------------------------------------------------------

Inclusive phase estimates: Phase 1 90--120 minutes; Phase 2 90--120 minutes. These estimates are unpiloted. Reading, normal waits, checking and handoff are included; optional stretch is separately identified. [Timing review](practice/client/designer/reviews/TIMING-AUDIT.md) records current exceptions and the pilot protocol.

### Choose your phase {#v2-capstone-readme-md-choose-your-phase}

[Phase one---certified](#v2-capstone-phase-one-certified-readme-md) establishes minimum understanding. [Phase two---proficient](#v2-capstone-phase-two-proficient-readme-md) requires substantive design/diagnosis/replay evidence with a finite core.

### Teaching concepts {#v2-capstone-readme-md-teaching-concepts}

The concept column and phase concept headings identify what an instructor can demonstrate. A useful demonstration shows the before state, the relevant change, and independent output/state evidence. The generated instructor companion reproduces concept explanations from these phase READMEs, so notes and challenges share a source.

Suggested destination: Friday capstone / advanced reporting clinic. Advanced clinics and optional work require separate time; they do not silently consume protected core teaching windows.


## Source: capstone/phase-one-certified/README.md {#v2-capstone-phase-one-certified-readme-md}

## capstone: Phase one --- certified {#v2-capstone-phase-one-certified-readme-md-capstone-phase-one-certified}

This phase has a fixed core of 5 tasks. The minimum standard is a working result with the underlying tool concepts explained. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

### Prerequisites and workspace {#v2-capstone-phase-one-certified-readme-md-prerequisites-and-workspace}

Prepared local dbt environment and seven supplied Atlas seed CSVs; no cloud access needed for this focused core. Connected Atlas rehearsal remains a separate instructor gate.

From the project root run:

``` bash
python3 scripts/challenge-v2.py prepare capstone phase-one-certified
cd .local/challenges-v2/capstone/phase-one-certified
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

### Local tool preparation {#v2-capstone-phase-one-certified-readme-md-local-tool-preparation}

The instructor runs `bash scripts/setup-v2-tools.sh` once from the project root. Before changing into your copied workspace, activate `.local/v2-tools/bin/activate` to make the pinned `dbt` executable available. For Airflow, use `.local/v2-airflow/bin/python` with a workspace-specific `AIRFLOW_HOME`; do not mix these two Python environments. The verifier supplies these paths automatically in a fresh copy.

### Starter behavior {#v2-capstone-phase-one-certified-readme-md-starter-behavior}

Phase 1 dbt seed/build succeeds on independent dimensions/status; two prepared dependent models are outside discovery. Phase 2 supplies a completed Phase 1 baseline.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter capstone phase-one-certified --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

### Timeline and completion standard {#v2-capstone-phase-one-certified-readme-md-timeline-and-completion-standard}

Core estimate: **90--120 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Task              Outcome                                                  Minutes           Evidence
  ----------------- -------------------------------------------------------- ----------------- ----------------------------------------------------------------------------------
  capstone-p1-01    State the consumer population and grain                  18--24            Record 10,000 raw trades, 2,500 conformed portfolios and 1,028 active portfolios

  capstone-p1-02    Build the valid-trade domain fact                        18--24            Build and inspect 9,880 valid trades; explain the 120 excluded rows

  capstone-p1-03    Author the active portfolio summary                      18--24            There must be3,717 positions and 1,028 summary portfolios

  capstone-p1-04    Investigate expected omission and a defective join       18--24            The defective query is an intentional teaching fixture, not a starter defect

  capstone-p1-05    Prove minimum data quality and give a consumer handoff   18--24            All minimum tests pass with known counts
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Core challenges {#v2-capstone-phase-one-certified-readme-md-core-challenges}

#### capstone-p1-01: State the consumer population and grain {#capstone-p1-01}

##### Concept: capstone-p1-01-concept --- State the consumer population and grain {#v2-capstone-phase-one-certified-readme-md-concept-capstone-p1-01-concept-state-the-consumer-population-and-grain}

The consumer asks for portfolios with qualifying trading activity. That is different from every portfolio in the dimension. A correct report can omit zero-activity portfolios by design, but the contract must make that population explicit. At portfolio grain retain portfolio/client/advisor identifiers; an aggregated regional report legitimately has another grain.

```{=html}
<!-- instructor-demo: capstone-p1-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-capstone-phase-one-certified-readme-md-challenge}

Read contract.md and all seven seeds. Write a short STTM/population note for an active-portfolio summary. Identify fields to retain and the expected raw/conformed/active populations. State the native-currency teaching simplification.

##### Hint {#v2-capstone-phase-one-certified-readme-md-hint}

The complete preserved Atlas route remains in v1; this core authors only the valid-trade fact and portfolio summary, with supplied dimension/prepared stages.

##### Check {#v2-capstone-phase-one-certified-readme-md-check}

Record 10,000 raw trades, 2,500 conformed portfolios and 1,028 active portfolios. Explain why a1472 portfolio gap is not proof of a missing ID column.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### capstone-p1-02: Build the valid-trade domain fact {#capstone-p1-02}

##### Concept: capstone-p1-02-concept --- Build the valid-trade domain fact {#v2-capstone-phase-one-certified-readme-md-concept-capstone-p1-02-concept-build-the-valid-trade-domain-fact}

A domain fact normalizes event meaning and preserves its business identity. Here quantity/price must be positive and side must be B/S; price_cents converts to price by dividing100, fee_bps divides10000, and signed quantity distinguishes buys/sells. Filtering must be accounted for separately from join loss.

```{=html}
<!-- instructor-demo: capstone-p1-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-capstone-phase-one-certified-readme-md-challenge-1}

Create dom_trading\_\_trade.sql reading the trades seed through ref. Retain trade_id, timestamp, portfolio/instrument keys; derive direction, signed_qty, price, gross_value and fee. Apply the declared validity filters. Copy prepared latest-price/position models into models/ after this fact exists.

##### Hint {#v2-capstone-phase-one-certified-readme-md-hint-1}

Two prepared models depend on the fact and are stored outside model discovery until you add it. This keeps the baseline build usable.

##### Check {#v2-capstone-phase-one-certified-readme-md-check-1}

Build and inspect 9,880 valid trades; explain the 120 excluded rows. Check trade_id uniqueness/non-null and money/sign conversions on representative buy/sell examples.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### capstone-p1-03: Author the active portfolio summary {#capstone-p1-03}

##### Concept: capstone-p1-03-concept --- Author the active portfolio summary {#v2-capstone-phase-one-certified-readme-md-concept-capstone-p1-03-concept-author-the-active-portfolio-summary}

The supplied position grain is portfolio/instrument. Rolling it up produces one active portfolio row with position count, trading count, value and fees. Joining to unique portfolio/client/advisor dimensions enriches the output without multiplying or dropping valid position keys.

```{=html}
<!-- instructor-demo: capstone-p1-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-capstone-phase-one-certified-readme-md-challenge-2}

Create rpt_portfolio_summary.sql using ref(dom_positions\_\_position) plus the supplied conformed dimensions. Retain portfolio/client/advisor IDs and descriptive fields, aggregate at portfolio grain and build the slice.

##### Hint {#v2-capstone-phase-one-certified-readme-md-hint-2}

Group all retained descriptors with portfolio_id. Inspect dimension key uniqueness before trusting inner joins.

##### Check {#v2-capstone-phase-one-certified-readme-md-check-2}

There must be3,717 positions and 1,028 summary portfolios. Check that every position portfolio is represented once in the summary. Explain the retained identifiers and native-currency valuation limit.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### capstone-p1-04: Investigate expected omission and a defective join {#capstone-p1-04}

##### Concept: capstone-p1-04-concept --- Investigate expected omission and a defective join {#v2-capstone-phase-one-certified-readme-md-concept-capstone-p1-04-concept-investigate-expected-omission-and-a-defective-join}

A population anti-join shows which conformed portfolios never enter the active report. An unrelated join key can also drop rows even though both columns exist. These are different causes and require different repairs. Comparing counts at each grain keeps the investigation precise.

```{=html}
<!-- instructor-demo: capstone-p1-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-capstone-phase-one-certified-readme-md-challenge-3}

Anti-join conformed portfolios to distinct valid-trade portfolio IDs and to the summary. Identify1472 zero-activity portfolios. In a disposable query run fixtures/defective_join.sql, which joins client_id to advisor_id, and compare its membership to the correct portfolio→advisor relationship.

##### Hint {#v2-capstone-phase-one-certified-readme-md-hint-3}

Use NOT EXISTS or a left anti-join for population comparison; do not compare unlike grains.

##### Check {#v2-capstone-phase-one-certified-readme-md-check-3}

The defective query is an intentional teaching fixture, not a starter defect. Show its lost membership and repair on pf.advisor_id=a.advisor_id. Explain why blindly changing every join to LEFT JOIN would not define a correct all-portfolio report.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### capstone-p1-05: Prove minimum data quality and give a consumer handoff {#capstone-p1-05}

##### Concept: capstone-p1-05-concept --- Prove minimum data quality and give a consumer handoff {#v2-capstone-phase-one-certified-readme-md-concept-capstone-p1-05-concept-prove-minimum-data-quality-and-give-a-consumer-handoff}

Structural tests protect key/relationship assumptions; an independent population oracle protects the stated consumer contract. Neither alone proves economic validity, currency normalization or completeness for another population. The handoff should make these limits intelligible to the consumer.

```{=html}
<!-- instructor-demo: capstone-p1-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-capstone-phase-one-certified-readme-md-challenge-4}

Add minimum trade-key uniqueness/non-null, trade portfolio/instrument relationships, summary-key tests and exact population checks. Run a fresh seed/build/test. Present one portfolio result plus the absence explanation and the source→domain→consumer path.

##### Hint {#v2-capstone-phase-one-certified-readme-md-hint-4}

Fresh builds matter: a file-only reset cannot prove a warehouse contains the current models.

##### Check {#v2-capstone-phase-one-certified-readme-md-check-4}

All minimum tests pass with known counts. Hand over contract, authored files, representative rows, anti-join evidence and native-currency limitation. Use the supplied orchestration baseline to explain where this slice would execute; connected Atlas execution is a separate gate.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### Phase completion {#v2-capstone-phase-one-certified-readme-md-phase-completion}

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

``` bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify capstone phase-one-certified --workspace .local/challenges-v2/capstone/phase-one-certified --mode offline
```

Execution boundary: Local dbt/DuckDB raw-to-consumer slice; separately recorded connected Atlas run. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

### Optional stretch {#v2-capstone-phase-one-certified-readme-md-optional-stretch}

Try a small variation after completing the core: change one input or contract condition in a second disposable copy, predict the result, and verify your prediction. This does not replace a core task or contribute to its timing budget.


## Source: capstone/phase-one-certified/starter/README.md {#v2-capstone-phase-one-certified-starter-readme-md}

## capstone starter assets {#v2-capstone-phase-one-certified-starter-readme-md-capstone-starter-assets}

Copy this directory into an isolated workspace before editing. The phase README defines the exact baseline command and the completion evidence. Generated databases, logs and evidence belong in that workspace. A starter check passing confirms the baseline is usable; it does not certify completed work.

Files supplied here are part of the learner pack. The instructor solution is stored separately under `challenges/v2-solutions`; it is excluded from the learner appendix and learner archive. See the parent [phase instructions](#v2-capstone-phase-one-certified-readme-md) for the authored-file list, prerequisites and any deliberate defect.


## Source: capstone/phase-two-proficient/README.md {#v2-capstone-phase-two-proficient-readme-md}

## capstone: Phase two --- proficient {#v2-capstone-phase-two-proficient-readme-md-capstone-phase-two-proficient}

This phase has a fixed core of 5 tasks. The advanced standard is a justified design or repair, actual behavioral proof, and a useful handoff. Completion produces classroom evidence; credential issuance remains an instructor/owner decision.

### Prerequisites and workspace {#v2-capstone-phase-two-proficient-readme-md-prerequisites-and-workspace}

Prepared local dbt environment and seven supplied Atlas seed CSVs; no cloud access needed for this focused core. Connected Atlas rehearsal remains a separate instructor gate.

From the project root run:

``` bash
python3 scripts/challenge-v2.py prepare capstone phase-two-proficient
cd .local/challenges-v2/capstone/phase-two-proficient
```

Edit the copied assets here, never the canonical starter or an unrelated data_products folder. The preparation command refuses to overwrite an existing workspace. To start another attempt choose --workspace with a new directory. Phase 2 includes its own prepared baseline; completed Phase 1 work is not a hidden prerequisite. Tool access, image pulls, identity and reviewer/runtime provisioning are instructor preparation and must be ready before the timed learner journey.

### Local tool preparation {#v2-capstone-phase-two-proficient-readme-md-local-tool-preparation}

The instructor runs `bash scripts/setup-v2-tools.sh` once from the project root. Before changing into your copied workspace, activate `.local/v2-tools/bin/activate` to make the pinned `dbt` executable available. For Airflow, use `.local/v2-airflow/bin/python` with a workspace-specific `AIRFLOW_HOME`; do not mix these two Python environments. The verifier supplies these paths automatically in a fresh copy.

### Starter behavior {#v2-capstone-phase-two-proficient-readme-md-starter-behavior}

Phase 1 dbt seed/build succeeds on independent dimensions/status; two prepared dependent models are outside discovery. Phase 2 supplies a completed Phase 1 baseline.

Run the baseline check from the project root with `python3 scripts/challenge-v2.py verify-starter capstone phase-two-proficient --mode offline`. This checks a fresh supplied starter. Use the learner workspace command below for your completed work. Deliberate negative-case experiments are described in their specific Check text; baseline starter errors are not silently expected.

### Timeline and completion standard {#v2-capstone-phase-two-proficient-readme-md-timeline-and-completion-standard}

Core estimate: **90--120 minutes**, including reading, authoring, checking, normal waits and the required explanation. Task budgets below sum to that phase range. These are unpiloted estimates for a generalist junior technical learner. Runtime installation and unplanned access failures need their own incident and experienced wall-clock timing. Optional stretch is excluded.

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Task              Outcome                                                  Minutes           Evidence
  ----------------- -------------------------------------------------------- ----------------- ---------------------------------------------------------------------------------------------------------------
  capstone-p2-01    Build a meaningful performance report                    18--24            One row per active portfolio, 1,028 rows

  capstone-p2-02    Rank advisor books with explicit ties                    18--24            Show one row per represented advisor, correct count/sums and equal rank for ties in the demonstration fixture

  capstone-p2-03    Build the regional rollup from its declared dependency   18--24            Inspect every regional row and verify the sum of portfolio counts is1,028

  capstone-p2-04    Reconcile independently and reject a defect              18--24            The wrong-key experiment must fail

  capstone-p2-05    Present a fixed completed core and select stretch        18--24            Core is complete only when the four output/proof themes are demonstrated
  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### Core challenges {#v2-capstone-phase-two-proficient-readme-md-core-challenges}

#### capstone-p2-01: Build a meaningful performance report {#capstone-p2-01}

##### Concept: capstone-p2-01-concept --- Build a meaningful performance report {#v2-capstone-phase-two-proficient-readme-md-concept-capstone-p2-01-concept-build-a-meaningful-performance-report}

The richer report folds buying/selling values into each portfolio and derives a realized fee rate in basis points. Net flow is bought minus sold; it differs from marked position value. A zero denominator has no meaningful realized rate, so NULL is preferable to a divide-by-zero or a fabricated zero.

```{=html}
<!-- instructor-demo: capstone-p2-01; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-capstone-phase-two-proficient-readme-md-challenge}

From the supplied solved Phase 1 baseline create rpt_portfolio_performance.sql with buy_value, sell_value, net_flow and fee_bps_realized. Guard the denominator with nullif. Explain units and test a tiny zero-volume case separately.

##### Hint {#v2-capstone-phase-two-proficient-readme-md-hint}

Reference existing summary/position models; do not rebuild the 23-modellegacyroute as a prerequisite.

##### Check {#v2-capstone-phase-two-proficient-readme-md-check}

One row per active portfolio, 1,028 rows. Independently compare sample values and show a zero-volume example yields NULL rate. The output is a training report, not FX-converted economic AUM.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### capstone-p2-02: Rank advisor books with explicit ties {#capstone-p2-02}

##### Concept: capstone-p2-02-concept --- Rank advisor books with explicit ties {#v2-capstone-phase-two-proficient-readme-md-concept-capstone-p2-02-concept-rank-advisor-books-with-explicit-ties}

An advisor book aggregates its active portfolios. Ranking semantics matter to consumer interpretation: dense_rank gives equal values equal rank and no gaps, while row_number chooses distinct row positions. Decide the business meaning before selecting a window function.

```{=html}
<!-- instructor-demo: capstone-p2-02; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-capstone-phase-two-proficient-readme-md-challenge-1}

Create rpt_advisor_book.sql from the summary and rpt_advisor_leaderboard.sql from that book. Carry advisor IDs/names/regions, portfolio counts, book value and fees. Apply dense_rank by book value descending.

##### Hint {#v2-capstone-phase-two-proficient-readme-md-hint-1}

Use a small tied-value fixture to explain dense_rank versus rank/row_number; do not force ties in the canonical dataset.

##### Check {#v2-capstone-phase-two-proficient-readme-md-check-1}

Show one row per represented advisor, correct count/sums and equal rank for ties in the demonstration fixture. Explain why advisors with no active portfolio are outside this report population.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### capstone-p2-03: Build the regional rollup from its declared dependency {#capstone-p2-03}

##### Concept: capstone-p2-03-concept --- Build the regional rollup from its declared dependency {#v2-capstone-phase-two-proficient-readme-md-concept-capstone-p2-03-concept-build-the-regional-rollup-from-its-declared-dependency}

A regional output summarizes advisor books and therefore has region grain. It intentionally omits portfolio_id as a row key, but must preserve the same active-portfolio/value population through aggregation. The declared prerequisite is the leaderboard, with reconciliation supporting correctness.

```{=html}
<!-- instructor-demo: capstone-p2-03; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-capstone-phase-two-proficient-readme-md-challenge-2}

Create rpt_region_report.sql from rpt_advisor_leaderboard, summing book value, fees and portfolio counts by region. Include represented advisor count and describe the consumer question.

##### Hint {#v2-capstone-phase-two-proficient-readme-md-hint-2}

This core maps legacyextension14 with extension2 as prerequisite; it does not invent a dependency on an asset-class stretch mart.

##### Check {#v2-capstone-phase-two-proficient-readme-md-check-2}

Inspect every regional row and verify the sum of portfolio counts is1,028. All represented advisors must belong to exactly one region in this fixture.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### capstone-p2-04: Reconcile independently and reject a defect {#capstone-p2-04}

##### Concept: capstone-p2-04-concept --- Reconcile independently and reject a defect {#v2-capstone-phase-two-proficient-readme-md-concept-capstone-p2-04-concept-reconcile-independently-and-reject-a-defect}

Totals can reconcile across a shared faulty upstream population. The independent oracle here starts from raw CSVs and the declared validity/valuation rules, then compares values at portfolio, advisor andregiongrain. A deliberate wrong-key join should be rejected rather than explained away.

```{=html}
<!-- instructor-demo: capstone-p2-04; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-capstone-phase-two-proficient-readme-md-challenge-3}

Add reconciliation tests for summary/performance/advisor/region values and counts. In a disposable copy introduce the provided incorrect client/advisor join into an advanced rollup, run the checker and record the failure. Repair and repeat.

##### Hint {#v2-capstone-phase-two-proficient-readme-md-hint-3}

The verifier oracle computes raw memberships separately; use its expected counts and per-key comparisons.

##### Check {#v2-capstone-phase-two-proficient-readme-md-check-3}

The wrong-key experiment must fail. Restored reports must agree per key within declared numeric tolerance, have correct grains and retain the 1,028 activepopulation. Save the failed assertion and repaired evidence.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

#### capstone-p2-05: Present a fixed completed core and select stretch {#capstone-p2-05}

##### Concept: capstone-p2-05-concept --- Present a fixed completed core and select stretch {#v2-capstone-phase-two-proficient-readme-md-concept-capstone-p2-05-concept-present-a-fixed-completed-core-and-select-stretch}

A finite completion standard lets a learner finish advanced work rather than spending the entire event choosing from an unbounded list. This core delivers performance, leaderboard, regionalrollup and reconciliations. Optional extensions deepen another topic but are not hidden requirements for proficiency.

```{=html}
<!-- instructor-demo: capstone-p2-05; demonstrate the state before and after this task, then ask the learner to explain the evidence boundary. -->
```
##### Challenge {#v2-capstone-phase-two-proficient-readme-md-challenge-4}

Prepare a brief consumer demonstration with one portfolio, one advisor andone region; explain ranking, fee units, zero denominators, population and oracle limits. Review the optional stretch index and select at most one later route for your own follow-up.

##### Hint {#v2-capstone-phase-two-proficient-readme-md-hint-4}

All 14 legacy extensions are accounted for in the coverage ledger and preserved in v1.

##### Check {#v2-capstone-phase-two-proficient-readme-md-check-4}

Core is complete only when the four output/proof themes are demonstrated. Optional stretch has separate estimates and never supplies missing minutes to this phase.

Record the command or inspection, its observed result, and your explanation in workspace/evidence.md. Mark unavailable runtime checks blocked; retain completed local evidence separately.

### Phase completion {#v2-capstone-phase-two-proficient-readme-md-phase-completion}

Present the authored result and the evidence for every core task, including the explanation of why the checks establish the intended outcome. The instructor assesses concept understanding and behavioral evidence together. Automation checks specified outputs; it cannot independently assess a learner's explanation or a real peer review.

``` bash
# From the project root, check your copied learner work:
python3 scripts/challenge-v2.py verify capstone phase-two-proficient --workspace .local/challenges-v2/capstone/phase-two-proficient --mode offline
```

Execution boundary: Local dbt/DuckDB raw-to-consumer slice; separately recorded connected Atlas run. A result is labelled with that boundary. An offline pass does not imply live Docker, GitHub, Astro, Databricks or Kafka access. For supported live checks use --mode live after preparation; inspect --help first. Keep any blocked gate visible in the handoff.

### Optional stretch {#v2-capstone-phase-two-proficient-readme-md-optional-stretch}

See the [stretch index](#v2-capstone-phase-two-proficient-stretch-readme-md). Each route has its own prerequisites, timing and completion check; none is part of this fixed core.


## Source: capstone/phase-two-proficient/starter/README.md {#v2-capstone-phase-two-proficient-starter-readme-md}

## capstone starter assets {#v2-capstone-phase-two-proficient-starter-readme-md-capstone-starter-assets}

Copy this directory into an isolated workspace before editing. The phase README defines the exact baseline command and the completion evidence. Generated databases, logs and evidence belong in that workspace. A starter check passing confirms the baseline is usable; it does not certify completed work.

Files supplied here are part of the learner pack. The instructor solution is stored separately under `challenges/v2-solutions`; it is excluded from the learner appendix and learner archive. See the parent [phase instructions](#v2-capstone-phase-two-proficient-readme-md) for the authored-file list, prerequisites and any deliberate defect.


## Source: capstone/phase-two-proficient/stretch/README.md {#v2-capstone-phase-two-proficient-stretch-readme-md}

## capstone: optional stretch selection {#v2-capstone-phase-two-proficient-stretch-readme-md-capstone-optional-stretch-selection}

Legacy extensions3,4,5,6,7,10,11,12,13 remain in v1/04-atlas-capstone (each 30--120 minutes; integration can exceed 120). The complete concepts and exercises below retain their original learner explanations and checks.

These routes are separate from core completion. Record timing exceptions rather than shortening an exercise during the audit. Instructor review should select one follow-up based on the learner goal and available environment.

### Full legacy advanced reference {#v2-capstone-phase-two-proficient-stretch-readme-md-full-legacy-advanced-reference}

The following complete original advanced route uses **v1** paths and runtime semantics. Core-equivalent topics remain here for teaching coverage; they are not additional v2 core tasks. All fourteen exercises remain available with their explanations, hints and checks.

### 🚀 Phase 2: Advanced Technical Extensions {#v2-capstone-phase-two-proficient-stretch-readme-md-phase-2-advanced-technical-extensions}

Phase 1 left you with a running baseline: seeds landed, source-aligned and domain-aligned products built, a first consumer-aligned mart, and the `atlas_elt` DAG configuration in place. Phase 2 is optional, advanced capstone work for technical learners who want to design and build richer consumer-aligned marts, dbt tests, macros, source-freshness and exposure metadata, incremental models, and snapshots.

Every challenge is self-contained. The shape is always:

-   **Concept** --- the idea, explained in plain English.
-   **Goal** --- the business outcome in one line.
-   **Authoring task** --- exactly what you write, and into which stub file.
-   **How to check** --- a command or observable result.

The complete set represents 3+ hours of work if pursued in depth. Pick the challenges that support your team's outcome; they build on each other roughly in order, and Challenge 14 is the integrative capstone that ties the marts together. You are not expected to finish all 14.

------------------------------------------------------------------------

#### Phase 2 dependency map {#v2-capstone-phase-two-proficient-stretch-readme-md-phase-2-dependency-map}

All Phase 2 challenges require the completed Phase 1 MVP. Most can then be attempted independently; use this map before choosing one:

  --------------------------------------------------------------------------------------------------------------------------------------------------
  Challenge                          Additional prerequisite                         Why
  ---------------------------------- ----------------------------------------------- ---------------------------------------------------------------
  1\. Portfolio performance          None                                            Uses Phase 1 portfolio summary and positions

  2\. Advisor leaderboard            None                                            Uses the Phase 1 advisor book

  3\. Asset-class activity           None                                            Uses Phase 1 trades and instruments

  4\. Source freshness               None                                            Uses the existing `trades` source declaration

  5\. Exposures                      None                                            Documents consumers of Phase 1 marts

  6\. Money macro                    None                                            Reviews macros already used by Phase 1 trades

  7\. Non-negative test              None                                            Applies a test to Phase 1 money columns

  8\. Relationship test              None                                            Connects Phase 1 trades and portfolios

  9\. Reconciliation tests           None                                            Compares Phase 1 mart totals

  10\. Incremental mart              None                                            Rebuilds the Phase 1 daily-market logic incrementally

  11\. Portfolio snapshot            None                                            Snapshots the Phase 1 portfolio model

  12\. Extend orchestration          Section 8 Airflow inspection                    Builds on the rendered DAG workflow

  13\. Params-driven orchestration   Section 8 Airflow inspection                    Traces runtime values through the bundle job

  14\. Regional capstone             Challenge 2 required; Challenge 9 recommended   Builds the leaderboard and applies the reconciliation pattern
  --------------------------------------------------------------------------------------------------------------------------------------------------

Before running any Phase 2 dbt command, return to the project:

``` bash
cd /workspaces/edo-training-data-products/data_products/atlas_elt
```

------------------------------------------------------------------------

#### Challenge 1: A richer executive report mart {#v2-capstone-phase-two-proficient-stretch-readme-md-challenge-1-a-richer-executive-report-mart}

##### Concept {#v2-capstone-phase-two-proficient-stretch-readme-md-concept}

The Phase 1 `rpt_portfolio_summary` answers "what is each portfolio worth?" An executive wants more in one place: how much was traded, how much flowed in versus out, and what fee rate the client actually paid. Fees are stored in basis points (bps), where one basis point is 0.01% of the traded value. Different trades carry different bps, so the *blended* rate a portfolio actually paid is the total fees divided by the total traded value, expressed back in basis points: `fees_paid / traded_value * 10000`. This is `fee_bps_realized`.

##### Goal {#v2-capstone-phase-two-proficient-stretch-readme-md-goal}

One mart an executive can read to see AUM, fees, trading volume, net flow, and the realised fee rate per portfolio.

##### Task {#v2-capstone-phase-two-proficient-stretch-readme-md-task}

Complete the stub at `data_products/atlas_elt/datasets/portfolio_perf/dbt/prepared/rpt_portfolio_performance.sql`, one row per portfolio with: `aum`, `fees_paid`, `trades`, `positions`, `buy_value`, `sell_value`, `net_flow` (buys minus sells), and `fee_bps_realized`. The AUM, fees, trades, and positions counts are already rolled up in `ref('rpt_portfolio_summary')`. The buy and sell values come from `total_bought` and `total_sold` in `ref('dom_positions__position')`, which is at portfolio/instrument grain --- re-aggregate to portfolio grain first. Guard the fee-rate division against a zero traded value.

##### Check {#v2-capstone-phase-two-proficient-stretch-readme-md-check}

``` bash
dbt build --select rpt_portfolio_performance
dbt show --select rpt_portfolio_performance --limit 5
```

The `fee_bps_realized` values should be in a believable range (low single digits to low tens of bps), not zero and not thousands. If a portfolio shows a wild number, your denominator is wrong.

Docs: [dbt marts](https://docs.getdbt.com/best-practices/how-we-structure/4-marts), [dbt SQL models](https://docs.getdbt.com/docs/build/sql-models)

Worked answer 1 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 2: Advisor leaderboard with `dense_rank()` {#v2-capstone-phase-two-proficient-stretch-readme-md-challenge-2-advisor-leaderboard-with-dense_rank}

##### Concept {#v2-capstone-phase-two-proficient-stretch-readme-md-concept-1}

A *window function* computes a value across a set of rows related to the current row, without collapsing them the way `group by` does. Ranking is the classic case. SQL gives you three ranking functions that differ in how they treat ties:

-   `row_number()` gives every row a distinct number, even on a tie.
-   `rank()` gives tied rows the same rank but then *skips* the next number.
-   `dense_rank()` gives tied rows the same rank and does *not* skip --- ties share a position, the ranking stays gap-free.

For a leaderboard you usually want `dense_rank()`: "rank 5" always means the fifth distinct AUM level. You write it as `dense_rank() over (order by book_aum desc)`.

##### Goal {#v2-capstone-phase-two-proficient-stretch-readme-md-goal-1}

A leaderboard a sales manager can read top-down: advisors ordered by the size of the book they run.

##### Task {#v2-capstone-phase-two-proficient-stretch-readme-md-task-1}

Complete the stub at `data_products/atlas_elt/datasets/advisors/dbt/integration/rpt_advisor_leaderboard.sql`. Select from `ref('rpt_advisor_book')` (which carries `advisor_id`, `advisor_name`, `region`, `book_aum`, `fees_generated`) and add a `rank` column computed with `dense_rank()` ordered by `book_aum` descending.

##### Check {#v2-capstone-phase-two-proficient-stretch-readme-md-check-1}

``` bash
dbt build --select rpt_advisor_leaderboard
dbt show --select rpt_advisor_leaderboard --limit 10
```

Rank 1 should be the largest `book_aum`. If you have ties, confirm they share a rank and the next rank is not skipped. Try swapping `dense_rank()` for `rank()` to see the gap behaviour change.

Docs: [dbt SQL models](https://docs.getdbt.com/docs/build/sql-models)

Worked answer 2 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 3: Daily activity by asset class, plus a rolling window {#v2-capstone-phase-two-proficient-stretch-readme-md-challenge-3-daily-activity-by-asset-class-plus-a-rolling-window}

##### Concept {#v2-capstone-phase-two-proficient-stretch-readme-md-concept-2}

The Phase 1 `ts_daily_market` totals trading per day across everything. Two refinements make it analyst-grade. First, *break it down by asset class* (Equity, Bond, ETF, Commodity) so you can see which kinds of instruments drove a given day. That needs a join to `dom_instrument__instrument` and a `group by trade_date, asset_class`. Second, add a *rolling window*. A window function can run a calculation over a sliding *frame* of rows defined by a `rows between` clause. A 7-day rolling sum is `sum(traded_value) over (... rows between 6 preceding and current row)`: the current row plus the six before it. The `partition by asset_class` keeps each asset class's window separate; `order by trade_date` defines what "preceding" means.

##### Goal {#v2-capstone-phase-two-proficient-stretch-readme-md-goal-2}

A daily activity mart split by asset class, with a 7-day rolling traded-value column for trend-spotting.

##### Task {#v2-capstone-phase-two-proficient-stretch-readme-md-task-2}

Complete the stub at `data_products/atlas_elt/datasets/market_daily/dbt/prepared/ts_daily_asset_class.sql`. Start from `ref('dom_trading__trade')` joined to `ref('dom_instrument__instrument')`, group by `trade_date` and `asset_class`, and produce `traded_value`, `fees`, and `trades` per group. Then add `rolling_7d_value`: a window sum of `traded_value` over a 7-row frame, partitioned by `asset_class` and ordered by `trade_date`.

##### Check {#v2-capstone-phase-two-proficient-stretch-readme-md-check-2}

``` bash
dbt build --select ts_daily_asset_class
dbt show --select ts_daily_asset_class --limit 20
```

For any asset class, on the earliest dates the rolling value equals the running sum (fewer than 7 days exist yet); once seven days have passed it tracks a 7-day total.

Docs: [dbt SQL models](https://docs.getdbt.com/docs/build/sql-models)

Worked answer 3 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 4: Declare source freshness on the source extracts {#v2-capstone-phase-two-proficient-stretch-readme-md-challenge-4-declare-source-freshness-on-the-source-extracts}

##### Concept {#v2-capstone-phase-two-proficient-stretch-readme-md-concept-3}

A dbt **source** is a named pointer to tables that dbt did not build. Declaring sources lets dbt run freshness checks: you tell dbt which column carries the load timestamp (`loaded_at_field`) and how old is too old (`freshness` thresholds: `warn_after` and `error_after`). Then `dbt source freshness` queries `max(loaded_at_field)`, compares it to now, and reports fresh/warn/error per source table. In a real pipeline this catches an upstream feed that silently stopped delivering before stale data poisons every downstream mart. The freshness config lives as metadata on the source declaration in `data_products/atlas_elt/datasets/sources.yml`.

##### Goal {#v2-capstone-phase-two-proficient-stretch-readme-md-goal-3}

Make dbt able to tell you, on demand, whether the source `trades` extract is recent enough to trust.

##### Task {#v2-capstone-phase-two-proficient-stretch-readme-md-task-3}

The `sources.yml` already ships with a freshness block on the `trades` table --- it uses `cast(timestamp_seconds(ts) as timestamp)` as the `loaded_at_field` (the trade's `ts` epoch second serves as the load timestamp for this exercise) and deliberately wide day-based thresholds so the historical sample reports `pass`/`warn`. Inspect `data_products/atlas_elt/datasets/sources.yml` to read the existing configuration, then:

1.  Confirm the `loaded_at_field` expression is valid by running the freshness check.
2.  Temporarily tighten the `warn_after` threshold to `{count: 1, period: day}` and re-run to watch the historical data flip to `warn`, then restore the original wide value.

##### Check {#v2-capstone-phase-two-proficient-stretch-readme-md-check-3}

``` bash
dbt source freshness
```

With the shipped wide thresholds, `trades` should report `pass` or `warn`.

Docs: [dbt source freshness](https://docs.getdbt.com/reference/resource-properties/freshness), [dbt sources](https://docs.getdbt.com/docs/build/sources)

Worked answer 4 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 5: Document who consumes the marts with exposures {#v2-capstone-phase-two-proficient-stretch-readme-md-challenge-5-document-who-consumes-the-marts-with-exposures}

##### Concept {#v2-capstone-phase-two-proficient-stretch-readme-md-concept-4}

A dbt **exposure** is a declared downstream *consumer* of your models: a dashboard, a report, an application, a notebook. It is metadata, not a model --- it does not build anything. You declare it in a YAML file, naming the models it `depends_on`, an owner, and a type. Exposures appear in `dbt docs` and the lineage graph, so anyone can see which marts feed which dashboards. You can also select on them: `dbt build --select +exposure:advisor_dashboard` builds everything that dashboard depends on.

##### Goal {#v2-capstone-phase-two-proficient-stretch-readme-md-goal-4}

Make the dependency from business-facing dashboards back to the consumer-aligned marts explicit and queryable.

##### Task {#v2-capstone-phase-two-proficient-stretch-readme-md-task-4}

Create `data_products/atlas_elt/datasets/exposures.yml`. Declare at least three exposures (an advisor dashboard, a portfolio dashboard, and a market-activity dashboard), each with a `name`, a `type` (`dashboard`), an `owner` (name and email), and a `depends_on` list written as `ref('...')` naming the consumer-aligned mart that feeds it.

##### Check {#v2-capstone-phase-two-proficient-stretch-readme-md-check-4}

``` bash
dbt parse
dbt ls --select +exposure:advisor_dashboard
```

`dbt parse` succeeds if the YAML is valid. The `dbt ls` line should list the advisor marts (and their upstreams) that the exposure depends on. It also lists the `reconcile_*` singular tests attached to those marts --- `dbt ls` returns every resource type unless you narrow it, so add `--resource-type model` if you want just the models.

Docs: [dbt exposures](https://docs.getdbt.com/docs/build/exposures), [exposure properties](https://docs.getdbt.com/reference/exposure-properties)

Worked answer 5 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 6: A reusable money macro {#v2-capstone-phase-two-proficient-stretch-readme-md-challenge-6-a-reusable-money-macro}

##### Concept {#v2-capstone-phase-two-proficient-stretch-readme-md-concept-5}

A dbt **macro** is a reusable snippet of SQL-generating logic, written in Jinja, that you call from models so a calculation is defined once and used everywhere. You have already used one: `{{ epoch_date('ts') }}` in `dom_trading__trade` expands to the date-conversion SQL. The money calculations in this project repeat: prices are stored as integer cents and must be divided by 100, and fee rates are stored in basis points and must be divided by 10000. Wrapping them in macros (`cents_to_decimal`, `basis_points`) means the conversion is named, consistent, and changed in one place.

##### Goal {#v2-capstone-phase-two-proficient-stretch-readme-md-goal-5}

Define money conversions once so every model uses the same named logic instead of scattered magic numbers.

##### Task {#v2-capstone-phase-two-proficient-stretch-readme-md-task-5}

This one is reading, not writing. `shared/` is a local dbt *package* shared across data products, so it ships complete and sits outside this challenge's reset scope --- there is no `TODO` in it to replace. Open `data_products/atlas_elt/shared/macros/money.sql` and read both macros: `cents_to_decimal(column_name)` returns `column_name / 100.0`, and `basis_points(amount_column, bps_column)` returns `amount_column * bps_column / 10000.0` (one basis point is 1/10000). Then find where they are already called --- `epoch_date` and `cents_to_decimal` in `dom_trading__trade`, and `basis_points` where a fee is applied --- and satisfy yourself that no model computes `/ 100.0` or `/ 10000.0` by hand. That is the point of the macro: the conversion is named once and changed in one place.

##### Check {#v2-capstone-phase-two-proficient-stretch-readme-md-check-5}

``` bash
dbt compile --select dom_trading__trade
```

Open the compiled file and confirm your `{{ cents_to_decimal(...) }}` call expanded to `price_cents / 100.0`. Then `dbt build --select dom_trading__trade` to confirm the model still produces the same numbers.

Docs: [dbt Jinja and macros](https://docs.getdbt.com/docs/build/jinja-macros)

Worked answer 6 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 7: A custom generic test for non-negative money {#v2-capstone-phase-two-proficient-stretch-readme-md-challenge-7-a-custom-generic-test-for-non-negative-money}

##### Concept {#v2-capstone-phase-two-proficient-stretch-readme-md-concept-6}

dbt tests are assertions that pass when a query returns zero rows. A **generic test** is one you can attach to any column by name, the way `not_null` and `unique` work. You write it once as a parametrised query in the `tests/generic/` folder, taking `model` and `column_name`, and selecting the *bad* rows (those that violate the rule). A natural one for this project is `non_negative`: money columns like AUM, fees, and traded value should never go below zero --- a negative value almost always means a join fanned out or a sign flipped upstream. Because it is generic, one definition guards every money column you point it at.

##### Goal {#v2-capstone-phase-two-proficient-stretch-readme-md-goal-6}

One reusable assertion that flags any negative value in any money column you attach it to.

##### Task {#v2-capstone-phase-two-proficient-stretch-readme-md-task-6}

Two parts. First, the generic test already ships in `data_products/atlas_elt/tests/generic/non_negative.sql` --- inspect it to understand the `{% test non_negative(model, column_name) %}` shape. Second, *apply* it by adding `non_negative` to money columns in the dataset YAML files (e.g. `aum` in the `advisors.yml` file under `rpt_portfolio_summary`).

> **Stuck? Try Copilot.** Ask: "In this dbt project, show me how to attach the existing `non_negative` generic test to `rpt_portfolio_summary.aum`. Explain the YAML change, but do not edit any files." Review the suggested model and column names before applying it.

##### Check {#v2-capstone-phase-two-proficient-stretch-readme-md-check-6}

``` bash
dbt test --select rpt_portfolio_summary --indirect-selection=cautious
```

Each attached column produces a `non_negative_<model>_<column>` test that should PASS. To prove it bites, temporarily attach it to `signed_qty` in `dom_trading__trade` (sell trades are negative) and watch it FAIL, then remove that line.

> `--indirect-selection=cautious` for the same reason as Section 7: `rpt_portfolio_summary` is an input to `reconcile_region_aum`, which also reads `rpt_region_report` --- a mart you do not write until Challenge 14. Without the flag dbt's default `eager` mode runs that test too, it fails on the still-stubbed mart, and the command exits non-zero for a reason that has nothing to do with the test you just wrote. Drop the flag once Challenge 14 is done.

Docs: [writing custom generic tests](https://docs.getdbt.com/best-practices/writing-custom-generic-tests), [dbt data tests](https://docs.getdbt.com/docs/build/data-tests)

Worked answer 7 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 8: A relationship (referential-integrity) test {#v2-capstone-phase-two-proficient-stretch-readme-md-challenge-8-a-relationship-referential-integrity-test}

##### Concept {#v2-capstone-phase-two-proficient-stretch-readme-md-concept-7}

A **relationships test** is dbt's built-in check for referential integrity: it asserts that every value in a foreign-key column exists as a key in another model --- the dbt equivalent of a foreign-key constraint. You declare it in a dataset YAML on the child column, naming the parent model (`to: ref('...')`) and the parent key (`field: ...`). dbt fails the test if any child row points at a key the parent does not have (an *orphan*). This matters because of how AUM is built: `rpt_portfolio_summary` joins trades to portfolios. If `dom_trading__trade.portfolio_id` contains an id with no matching portfolio, that trade's value is silently dropped by the join, and the firm's reported AUM is quietly understated. A relationships test turns that silent loss into a loud test failure.

##### Goal {#v2-capstone-phase-two-proficient-stretch-readme-md-goal-7}

Prove that every trade points at a real portfolio, so no trade value goes missing in the AUM rollup.

##### Task {#v2-capstone-phase-two-proficient-stretch-readme-md-task-7}

In the `trades` dataset YAML (`datasets/trades/dbt/trades.yml`), under `dom_trading__trade`, add a `relationships` test on `portfolio_id` with `to: ref('dom_portfolio__portfolio')` and `field: portfolio_id`.

##### Check {#v2-capstone-phase-two-proficient-stretch-readme-md-check-7}

``` bash
dbt test --select dom_trading__trade
```

The generated `relationships_dom_trading__trade_portfolio_id__...` test should PASS, confirming no orphan portfolio ids.

Docs: [dbt data tests](https://docs.getdbt.com/reference/resource-properties/data-tests)

Worked answer 8 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 9: Singular reconciliation tests within tolerance {#v2-capstone-phase-two-proficient-stretch-readme-md-challenge-9-singular-reconciliation-tests-within-tolerance}

##### Concept {#v2-capstone-phase-two-proficient-stretch-readme-md-concept-8}

A **singular test** is a single hand-written SQL file in `tests/` that fails when its query returns any rows. Unlike a generic test, it is not attached to a column; it tests one specific assertion across whatever models you reference. The powerful case is *reconciliation*: two marts roll the same money up different ways, so their totals must agree. `rpt_advisor_book` sums AUM by advisor; `rpt_portfolio_summary` sums it by portfolio. Because every portfolio has exactly one advisor, `sum(book_aum)` across advisors must equal `sum(aum)` across portfolios. You compare the two totals and return a row only when they differ by more than a small **tolerance** (for floating-point rounding). A reconciliation test proves a rollup did not lose or double-count money.

##### Goal {#v2-capstone-phase-two-proficient-stretch-readme-md-goal-8}

Prove the advisor and segment rollups preserve total AUM, so the firm reports one consistent number however it is sliced.

##### Task {#v2-capstone-phase-two-proficient-stretch-readme-md-task-8}

Before opening the shipped tests, choose one route to describe the advisor-book reconciliation:

1.  **Manual route:** write the invariant, the two totals being compared, and the tolerance in plain English, then sketch the SQL that should return only mismatches.
2.  **Copilot route:** use the prompt below to generate a draft, then identify its two `ref()` calls, tolerance, and failure condition.

> **Try with Copilot.** "Draft a dbt singular reconciliation test comparing total `rpt_advisor_book.book_aum` with total `rpt_portfolio_summary.aum`. It must return a row only when the totals differ by more than 0.01. Explain why zero returned rows means PASS. Do not edit files."

Now inspect `tests/reconcile_advisor_book_aum.sql` and `tests/reconcile_segment_aum.sql`. Compare the shipped implementation with your manual sketch or Copilot draft. Then:

1.  Run both tests to confirm they pass on the data you built.
2.  Temporarily change the tolerance to a negative number so any tiny drift trips it, confirm it fails, then restore it.

A third reconciliation, `tests/reconcile_trade_counts.sql`, ships alongside them and runs on every `dbt build`/`dbt test`, so you will see it in the output. It checks a *count* rather than a money total: every valid trade must be counted exactly once in `dom_positions__position`, `ts_daily_market` and `agg_instrument_activity`, so `sum(trades)` has to agree across all three. It needs no tolerance --- counts are exact, and any disagreement means a join dropped or duplicated rows.

##### Check {#v2-capstone-phase-two-proficient-stretch-readme-md-check-8}

``` bash
dbt test --select reconcile_advisor_book_aum reconcile_segment_aum
```

Both should PASS (return zero rows).

Docs: [dbt singular data tests](https://docs.getdbt.com/docs/build/data-tests)

Worked answer 9 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 10: An incremental market mart {#v2-capstone-phase-two-proficient-stretch-readme-md-challenge-10-an-incremental-market-mart}

##### Concept {#v2-capstone-phase-two-proficient-stretch-readme-md-concept-9}

By default a dbt model is fully rebuilt every run. For a small classroom dataset that is fine, but a real daily-market table grows forever and rebuilding all history every night is wasteful. An **incremental** model rebuilds only the new rows. You set `materialized='incremental'` and give dbt a `unique_key`. On the first run it builds everything. On later runs, the `is_incremental()` block adds a `where` clause that filters to only rows newer than what is already in the table: `where trade_date > (select max(trade_date) from {{ this }})`, where `{{ this }}` is the model's own existing table. `unique_key` lets dbt replace a row if the same key reappears, so a re-run of yesterday updates rather than duplicates.

##### Goal {#v2-capstone-phase-two-proficient-stretch-readme-md-goal-9}

A daily-market mart that, after its first build, only processes new trade dates instead of rebuilding all of history.

##### Task {#v2-capstone-phase-two-proficient-stretch-readme-md-task-9}

Complete the stub at `data_products/atlas_elt/datasets/market_daily/dbt/prepared/ts_daily_market_incremental.sql`. It produces the same daily aggregates as `ts_daily_market` (traded value, fees, trades, grouped by `trade_date`), but configured `materialized='incremental'` with `unique_key='trade_date'` and an `is_incremental()` filter that only selects trade dates later than the current `max(trade_date)` in the table.

> **Required AI Catalyst checkpoint.** In Copilot Chat, ask: "Use the dbt best practices skill to review the models in `data_products/atlas_elt`. Which models are reasonable candidates for incremental materialization, and why? Analyse only; do not edit files." Compare its recommendation with `ts_daily_market_incremental`. Check that it discusses table growth, a reliable date or key, late-arriving data, and the cost of rebuilding. The Catalyst interaction informs your decision; the dbt commands below remain the acceptance check.

##### Check {#v2-capstone-phase-two-proficient-stretch-readme-md-check-9}

``` bash
dbt build --select ts_daily_market_incremental
# Run it a second time:
dbt run --select ts_daily_market_incremental
```

On the second run dbt appends rather than rebuilding, because no trade dates are newer than what is already there. Note that the terminal text is **identical** both times (`OK created sql incremental model ...`) --- dbt prints no row count or incremental marker, so there is nothing visual to compare. To actually see the difference, read the compiled SQL:

``` bash
# This project normally writes artifacts to a Unity Catalog Volume, which is not mounted in
# the devcontainer. Override target-path for this inspection and clean it up afterwards:
TARGET=$(mktemp -d)
dbt compile --select ts_daily_market_incremental --target-path "$TARGET"
find "$TARGET/compiled" -name ts_daily_market_incremental.sql -exec grep -A3 "trade_date >" {} +
rm -rf "$TARGET"
```

Read the `compiled/` copy, not `run/`: for this Databricks `insert_overwrite` incremental strategy the `run/` artifact is only the `insert overwrite table ... select * from ...__dbt_tmp` wrapper, so the filter you are looking for appears only in `compiled/`.

The second run's version carries the `where trade_date > (select max(trade_date) ...)` filter that the first run --- which had no table to compare against --- did not. Use `--full-refresh` to rebuild the whole table when needed.

Docs: [dbt incremental models](https://docs.getdbt.com/docs/build/incremental-models), [unique_key](https://docs.getdbt.com/reference/resource-configs/unique_key)

Worked answer 10 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 11: A snapshot for slowly-changing portfolios {#v2-capstone-phase-two-proficient-stretch-readme-md-challenge-11-a-snapshot-for-slowly-changing-portfolios}

##### Concept {#v2-capstone-phase-two-proficient-stretch-readme-md-concept-10}

Dimension data changes over time: a portfolio's strategy is re-classified, or it is reassigned to a different advisor. A plain model only ever holds the *current* state, so last night's value overwrites last week's, and the history is gone. A dbt **snapshot** captures that history. It is a special kind of model defined in the `snapshots/` folder: on each run it compares the source rows to what it has stored and, when a tracked value has changed, *closes* the old record and *opens* a new one, recording validity ranges in `dbt_valid_from` / `dbt_valid_to` columns. This is **slowly-changing-dimension (SCD) type 2**.

**CG paved-path bridge.** This generic `dbt snapshot` teaches the SCD2 *concept*. In production at CG, slowly-changing history is not `dbt snapshot`; it is the caspian-core `bitemporal_load_v2` incremental strategy, which emits the `dl_*` audit canon via `get_audit_cols()` (`dl_business_from_date` / `dl_business_to_date` / `dl_system_from_date` / `dl_system_to_date`, `dl_row_uid`): bitemporal, richer than the single validity range here. Rough mapping: `dbt_valid_from` / `dbt_valid_to` ≈ `dl_business_from_date` / `dl_business_to_date`. Keep the generic snapshot below as the lab artefact.

##### Goal {#v2-capstone-phase-two-proficient-stretch-readme-md-goal-10}

Keep a full history of portfolio strategy and advisor assignments, so you can reconstruct the book as it stood on any past date.

##### Task {#v2-capstone-phase-two-proficient-stretch-readme-md-task-10}

The snapshot ships at `data_products/atlas_elt/shared/snapshots/portfolios_snapshot.sql`. Inspect it to understand the `{% snapshot %}` block structure, then run it:

``` bash
dbt snapshot
```

The log should say it snapshotted `portfolios_snapshot`. The physical snapshot table also has dbt-managed `dbt_valid_from`, `dbt_valid_to`, and `dbt_scd_id` columns. On a first run every row is open (`dbt_valid_to` is null). Run `dbt snapshot` again with no source change and the row count stays the same: snapshots only add rows when a tracked value actually changes.

##### Check {#v2-capstone-phase-two-proficient-stretch-readme-md-check-10}

Confirm the snapshot command built and `dbt show` can preview the snapshot input rows:

``` bash
dbt show --select portfolios_snapshot --limit 5
```

Docs: [dbt snapshots](https://docs.getdbt.com/docs/build/snapshots), [check_cols](https://docs.getdbt.com/reference/resource-configs/check_cols)

Worked answer 11 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

#### Challenge 12: Understand and extend the orchestration {#v2-capstone-phase-two-proficient-stretch-readme-md-challenge-12-understand-and-extend-the-orchestration}

##### Concept {#v2-capstone-phase-two-proficient-stretch-readme-md-concept-11}

The `atlas_elt` product ships per-dataset `*.dag.yml` orchestration files. Each YAML configures an Airflow DAG that wraps the Databricks bundle job for that dataset. This is the **CG paved-path orchestration model**: Airflow holds the schedule and Databricks Jobs executes the dbt run. A `@task.bash` TaskFlow approach (where each Airflow task runs a shell command like `dbt run --select tag:consumer-aligned`) is a valid teaching pattern, but the paved path delegates to a Databricks job for scalability and observability at production.

##### Goal {#v2-capstone-phase-two-proficient-stretch-readme-md-goal-11}

Understand how the paved-path DAG YAML wires to the Databricks job, and where you would extend it to add a new dataset's DAG.

##### Task {#v2-capstone-phase-two-proficient-stretch-readme-md-task-11}

Read the existing DAG YAMLs and answer these questions:

``` bash
cat datasets/advisors/airflow/advisors.dag.yml
cat datasets/portfolio_perf/airflow/portfolio_perf.dag.yml
```

1.  What schedule does each dataset's DAG use?
2.  Which Databricks bundle job name does the DAG trigger?
3.  If you added a brand-new consumer mart in a new dataset folder, what file would you create to give it an Airflow DAG?

##### Check {#v2-capstone-phase-two-proficient-stretch-readme-md-check-11}

Confirm the set of DAG YAMLs matches the set of dataset folders:

``` bash
ls datasets/*/airflow/*.dag.yml
```

------------------------------------------------------------------------

#### Challenge 13: Understand params-driven orchestration {#v2-capstone-phase-two-proficient-stretch-readme-md-challenge-13-understand-params-driven-orchestration}

##### Concept {#v2-capstone-phase-two-proficient-stretch-readme-md-concept-12}

Airflow **params** let you parametrise a DAG run: the operator passes a config dict at trigger time, and tasks read it via `{{ params.<name> }}`. This turns one DAG into a flexible tool --- a `selector` param lets an operator build only `tag:consumer-aligned` instead of everything; a `run_tests` flag lets them skip the test stage. In the paved path, the Databricks bundle job can similarly accept `--vars` at run time, overriding catalog, schema, or dbt vars.

##### Goal {#v2-capstone-phase-two-proficient-stretch-readme-md-goal-12}

Understand how a run-time parameter flows from the Airflow trigger form through to the dbt command that executes on Databricks.

##### Task {#v2-capstone-phase-two-proficient-stretch-readme-md-task-12}

Inspect the `variables_dev.yml` for the Atlas product:

``` bash
cat variables/variables_dev.yml
```

Then look at how a bundle job references variables:

``` bash
cat datasets/advisors/bundle/advisors.job.yml
```

Answer: 1. Which variables can be overridden at run time? 2. How would you run only the `advisors` dataset's dbt models via the CLI? 3. What is the analogy between `{{ params.selector }}` in a Python TaskFlow DAG and variable overrides in the bundle job?

##### Check {#v2-capstone-phase-two-proficient-stretch-readme-md-check-12}

Trace one variable from `variables/variables_dev.yml` into the advisor job file and explain which value changes without changing the DAG structure.

------------------------------------------------------------------------

#### Challenge 14: A reconciling regional report (capstone) {#v2-capstone-phase-two-proficient-stretch-readme-md-challenge-14-a-reconciling-regional-report-capstone}

This challenge ties the rest together. Earlier challenges each added one feature; here you compose them into an integrated deliverable and *prove it is correct*. The integration proof is reconciliation: a new rollup must agree, to the penny within tolerance, with the summary it derives from.

##### Concept {#v2-capstone-phase-two-proficient-stretch-readme-md-concept-13}

A regional report rolls the whole book up by advisor `region`. The correctness question is whether that rollup preserves total AUM. If you build `rpt_region_report` from `rpt_portfolio_summary` (which already carries each portfolio's `region`), then `sum(aum)` across regions must equal `sum(aum)` across portfolios --- no money created and none lost. The reconciliation singular test asserts exactly that, within a small tolerance, and returns rows only on a mismatch. The test already ships at `data_products/atlas_elt/tests/reconcile_region_aum.sql`; your job is to build the mart it validates, and to confirm the integration proof passes.

##### Goal {#v2-capstone-phase-two-proficient-stretch-readme-md-goal-13}

A regional AUM report that is provably consistent with the portfolio summary, enforced by an orchestrated reconciliation test.

##### Task {#v2-capstone-phase-two-proficient-stretch-readme-md-task-13}

Two pieces:

1.  Complete `data_products/atlas_elt/datasets/advisors/dbt/integration/rpt_region_report.sql`: per advisor `region`, the columns `portfolios`, `clients`, `aum`, `fees_generated`, built from `ref('rpt_portfolio_summary')`.
2.  Inspect `data_products/atlas_elt/tests/reconcile_region_aum.sql` to understand the reconciliation pattern, then run it against the mart you built.

##### Check {#v2-capstone-phase-two-proficient-stretch-readme-md-check-13}

``` bash
dbt build --select rpt_region_report rpt_advisor_leaderboard
dbt test --select reconcile_region_aum
```

`reconcile_region_aum` PASS is the integration proof. The final verification section explains the difference between offline compilation and a live end-to-end check.

Docs: [dbt singular data tests](https://docs.getdbt.com/docs/build/data-tests), [dbt exposures](https://docs.getdbt.com/docs/build/exposures)

Worked answer 12 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

### Use the product {#v2-capstone-phase-two-proficient-stretch-readme-md-use-the-product}

Building tables is not the outcome; helping someone make a decision is. Run at least the Phase 1 query below, then explain one finding supported by the rows you see.

Run from `data_products/atlas_elt`:

``` bash
dbt show --inline "select segment, clients, portfolios, aum from {{ ref('agg_segment_aum') }} order by aum desc" --limit 10
```

If you completed Challenge 14, also inspect the regional report:

``` bash
dbt show --inline "select region, portfolios, clients, aum, fees_generated from {{ ref('rpt_region_report') }} order by aum desc" --limit 10
```

> **Turn results into a decision.** Paste the displayed rows into Copilot Chat and ask: "Using only these Atlas query results, draft a four-bullet briefing. State one supported finding, the intended consumer, a decision that consumer could make, and one caveat or follow-up question. Do not invent values or facts not present in the rows."

Check every number in the response against your query output. The intended consumer might be a sales manager, advisor lead, trading desk, or product owner. A possible decision is where to investigate concentration, service coverage, or unusual activity next.

The pipeline standardises currency-code spelling but does not perform FX conversion. Monetary totals combine USD, EUR, GBP, CHF, JPY, and HKD, so treat cross-currency comparisons as indicative and include that limitation in your briefing.

PDF generation and scheduled email delivery are useful follow-on products, but they require additional rendering, access-control, and delivery design and are outside this capstone.

------------------------------------------------------------------------

### Appendix: Quick Reference and Opening Team Activity Example {#v2-capstone-phase-two-proficient-stretch-readme-md-appendix-quick-reference-and-opening-team-activity-example}

#### Working in the Devcontainer {#v2-capstone-phase-two-proficient-stretch-readme-md-working-in-the-devcontainer}

Run repository commands inside the VS Code devcontainer, not in a terminal on your host machine. The tools and environment settings used by this capstone are installed in the container.

##### Know where to run commands {#v2-capstone-phase-two-proficient-stretch-readme-md-know-where-to-run-commands}

  -------------------------------------------------------------------------------------------------
  Command type                                                  Directory
  ------------------------------------------------------------- -----------------------------------
  `mise run ...`, `astro dev ...`, and challenge verification   Repository root

  `dbt ...`                                                     `data_products/atlas_elt`
  -------------------------------------------------------------------------------------------------

``` bash
# Repository root
cd /workspaces/edo-training-data-products

# Atlas dbt project
cd /workspaces/edo-training-data-products/data_products/atlas_elt

# Show your current directory
pwd
```

##### Essential dbt commands {#v2-capstone-phase-two-proficient-stretch-readme-md-essential-dbt-commands}

Run these from `data_products/atlas_elt`:

``` bash
# Confirm that dbt can connect
dbt debug

# Install project packages
dbt deps

# List models without building them
dbt ls --resource-type model

# Build one model and its upstream dependencies without tests on unfinished models
dbt build --select +rpt_portfolio_summary --indirect-selection=cautious

# Build one alignment
dbt run --select tag:source-aligned

# Preview model results
dbt show --select rpt_portfolio_summary --limit 10

# Test one model without pulling in tests that depend on unfinished models
dbt test --select rpt_portfolio_summary --indirect-selection=cautious
```

In a selector, `+model_name` includes upstream dependencies, `tag:name` selects resources with that tag, and `--indirect-selection=cautious` runs a test only when all its inputs are selected. Start with the smallest relevant model or selector instead of rebuilding everything.

##### Databricks connection {#v2-capstone-phase-two-proficient-stretch-readme-md-databricks-connection}

Check the profile from the repository root:

``` bash
mise exec -- databricks auth describe --profile DEFAULT
```

Then check the dbt connection from `data_products/atlas_elt`:

``` bash
dbt debug
```

Do not assume every connection failure requires another login. If the profile cannot mint a valid token, return to the repository root and run:

``` bash
mise run setup:databricks
```

Never paste access tokens, passwords, or other credentials into chat, source files, or commands that will be retained in shell history.

##### Airflow quick reference {#v2-capstone-phase-two-proficient-stretch-readme-md-airflow-quick-reference}

Run these from the repository root:

``` bash
astro dev start
astro dev run dags list-import-errors
astro dev run dags list | grep atlas_elt
astro dev run dags details atlas_elt_advisors
astro dev stop
```

Use the Airflow URL printed by `astro dev start`; do not assume it uses port 8080. Configure Databricks before starting Astro so its containers receive the connection settings. Stop Astro when you finish to release local memory.

##### Verification commands {#v2-capstone-phase-two-proficient-stretch-readme-md-verification-commands}

Run these from the repository root:

``` bash
# Fast dependency, parsing, compilation, and bundle gate
mise run challenge:verify 04

# Phase 1 live gate
CERT_INTEGRATION_TESTS=1 ATLAS_VERIFY_SCOPE=mvp mise run challenge:verify 04

# Full live gate after the Phase 2 models are complete
CERT_INTEGRATION_TESTS=1 mise run challenge:verify 04

# Non-destructive instructor overview
challenges/v1/04-atlas-capstone/verify.sh --review
```

The following command is for maintainers only. It deliberately resets the learner tree before replaying the complete capstone:

``` bash
# MAINTAINERS ONLY: destructive to learner work
challenges/v1/04-atlas-capstone/verify.sh --from-scratch
```

##### Starting over {#v2-capstone-phase-two-proficient-stretch-readme-md-starting-over}

> **Warning:** This command deletes your authored challenge files under `data_products/atlas_elt/datasets/`. Run it only when you intend to discard that work.

``` bash
mise run challenge:reset 04
```

The reset restores files only. It does not delete tables or views left in your Databricks schema, so rebuild the relevant models before trusting a test result from a new attempt.

##### Where to find things {#v2-capstone-phase-two-proficient-stretch-readme-md-where-to-find-things}

  What                      Path
  ------------------------- ---------------------------------------------
  Learner model files       `data_products/atlas_elt/datasets/`
  dbt logs                  `data_products/atlas_elt/logs/dbt.log`
  Starter templates         `challenges/v1/04-atlas-capstone/stubs/`
  Solved references         `challenges/v1/04-atlas-capstone/solution/`
  Maintainer run evidence   `.devcontainer/verify/04-atlas-capstone/`

##### Common problems {#v2-capstone-phase-two-proficient-stretch-readme-md-common-problems}

  ----------------------------------------------------------------------------------------------------------------------------------------
  Symptom                                          First action
  ------------------------------------------------ ---------------------------------------------------------------------------------------
  dbt cannot find the project                      Run `cd /workspaces/edo-training-data-products/data_products/atlas_elt`.

  Databricks authentication fails                  Run the profile and token-delivery checks in Troubleshooting before logging in again.

  `No models match`                                Confirm you edited `data_products/atlas_elt/`, not `stubs/`.

  An unfinished model triggers an unrelated test   Add `--indirect-selection=cautious` to the focused command.

  Atlas DAGs do not appear                         Run `astro dev run dags list-import-errors`, then restart Astro.

  Airflow has old connection settings              Stop Astro, rerun Databricks setup, then start Astro again.

  You need to inspect generated SQL                Use the temporary `--target-path` pattern from Challenge 10.

  You are unsure what changed                      From the repository root, run `git status --short`.
  ----------------------------------------------------------------------------------------------------------------------------------------

##### Safe working habits {#v2-capstone-phase-two-proficient-stretch-readme-md-safe-working-habits}

-   Edit challenge work only under `data_products/atlas_elt/`; never edit `stubs/`.
-   Run one dbt command at a time and build the smallest relevant selection first.
-   Read the first real error, not only the final summary.
-   Run `git status --short` regularly so generated or unexpected changes are visible.
-   Do not commit logs, generated targets, credentials, or maintainer verification evidence.
-   Do not reset unless you intend to discard your authored work.

#### Opening Team Activity Example {#v2-capstone-phase-two-proficient-stretch-readme-md-opening-team-activity-example}

Worked answer 13 is supplied separately in the instructor pack: `challenges/v2-solutions/capstone/phase-two-proficient/legacy-stretch-answers.md`. Compare after your own attempt.

------------------------------------------------------------------------

### Glossary {#v2-capstone-phase-two-proficient-stretch-readme-md-glossary}

**Grain** --- what one row represents, such as one trade or one portfolio.

**Materialization** --- how dbt stores a model, such as a view, table, or incremental table.

**Source** --- a table dbt reads but does not build; `source()` records that dependency.

**`ref()`** --- a dbt function that names another model and adds it to the dependency graph.

**Natural key** --- a real-world identifier already present in the data, such as `trade_id`.

**Window function** --- a calculation across related rows without collapsing them into one row.

**Generic test** --- a reusable parameterised assertion attached to a model or column.

**Singular test** --- a purpose-built SQL query that passes when it returns zero failing rows.

**Reconciliation** --- checking that totals agree when the same measure is rolled up differently.

**Incremental model** --- a model that processes new or changed rows after its first build.

**Unique key** --- the column or columns dbt uses to identify the same row across incremental runs.

**Snapshot / SCD2** --- history that preserves old and new versions of a changing record with validity dates; SCD2 means slowly changing dimension type 2.

------------------------------------------------------------------------

### Troubleshooting {#v2-capstone-phase-two-proficient-stretch-readme-md-troubleshooting}

**`dbt debug` cannot connect.** Do not assume you need to log in again. From the repository root, first prove whether the existing OAuth profile can mint a token:

``` bash
mise exec -- databricks auth describe --profile DEFAULT
mise exec -- sh -c 'databricks auth token --profile DEFAULT --host "$DATABRICKS_HOST" --output json >/dev/null' && echo "OAuth token: OK"
mise exec -- sh -c 'test -n "${DBT_ACCESS_TOKEN:-}" && test "$DBT_ACCESS_TOKEN" != "MISSING_run__mise_run_setup_databricks"' && echo "dbt token delivery: OK"
```

If the second command fails with a login or expiry error, run `mise run setup:databricks` and complete OAuth. If it succeeds but the third command fails, authentication is healthy and delivery is the problem: run `mise run setup:mise`, open a new terminal, return to the repo, and retry `dbt debug`. Do not re-authenticate a working profile.

**`No models match tag:source-aligned`** (or `domain-aligned`/`consumer-aligned`). The stubs are still placeholders, or you have not authored that alignment yet. Complete the model files for that alignment first, then re-run the `--select tag:...` command.

**`dbt seed` fails on types.** Confirm each CSV in `data_products/atlas_elt/seeds/` still has its header row and that the `+column_types` in `dbt_project.yml` match the columns.

**Model produces different row count than expected.** For `dom_trading__trade`, a lower row count than `src_trading__trades` is correct and expected --- the quality filter drops bad trades. For consumer marts, confirm all `ref()` calls resolve to the domain-aligned products, not directly to source-aligned stubs.

**Want to start over.** The following command deletes your authored challenge work and copies the placeholder templates back into the product. Run it only when you explicitly want that:

``` bash
mise run challenge:reset 04
```

### Verify your work {#v2-capstone-phase-two-proficient-stretch-readme-md-verify-your-work}

Run the fast verification gate from the repository root:

``` bash
mise run challenge:verify 04
```

An `OFFLINE PASS` means dbt dependencies, parsing, compilation, and the available bundle validation completed. It does **not** mean models or tests ran on Databricks, and the output says so explicitly. The gate restores `package-lock.yml`, so it does not leave that generated file dirty.

To verify only the required Phase 1 MVP live, use the completion command from **Complete Phase 1**:

``` bash
CERT_INTEGRATION_TESTS=1 ATLAS_VERIFY_SCOPE=mvp mise run challenge:verify 04
```

After completing Challenge 14, run the live completion gate:

``` bash
CERT_INTEGRATION_TESTS=1 mise run challenge:verify 04
```

A `LIVE PASS` means the models ran and all dbt tests passed on Databricks. Only this mode prints `Atlas ELT capstone complete.` Bundle deployment is a separate operational action; it is not required to prove your dbt work is correct.

#### Maintainer-only from-scratch verification {#v2-capstone-phase-two-proficient-stretch-readme-md-maintainer-only-from-scratch-verification}

Maintainers can reproduce the full learner journey, including all optional Phase 2 challenges, from a reset starter tree:

``` bash
challenges/v1/04-atlas-capstone/verify.sh --from-scratch
```

This command is destructive to work under `data_products/atlas_elt/datasets/`: it runs the challenge reset first, applies the shipped solutions in learner order, exercises each documented check, and restores the starter files on exit. Per-step commands and logs are retained under `.devcontainer/verify/04-atlas-capstone/`, outside reset scope. Browser and Copilot Chat actions are recorded separately in `interactions.tsv`; the runner validates their prompts and executable acceptance checks, but does not claim to automate a human visual review or a nondeterministic chat response. Use `--dry-run` to validate the phase and file manifests without resetting anything.

For a non-destructive plain-text synopsis of Phase 1 and all 14 Phase 2 challenges, including each challenge's purpose, learner task, solution, and proof:

``` bash
challenges/v1/04-atlas-capstone/verify.sh --review
```
