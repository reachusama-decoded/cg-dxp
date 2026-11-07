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
