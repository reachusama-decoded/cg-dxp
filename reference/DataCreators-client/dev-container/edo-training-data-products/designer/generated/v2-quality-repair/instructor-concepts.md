# Instructor concepts

Full source-owned concepts; runnable solutions remain separate.

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


#### Concept

The working tree contains editable files. A commit records a snapshot and its parent history. The index is the proposed next snapshot, not a synonym for every file in the directory. Staging one file selects its current content for the next commit; changing that file again can leave one version staged and another in the working tree. An untracked file has no committed baseline, so its presence in a folder does not imply version control protects it. This distinction matters when a contract edit and an unrelated note share a workspace.

For the first snapshot, the baseline contract should enter history while the scratch notes should not. Inspecting the staged diff and the committed file list gives stronger evidence than a commit command returning success. The repository root is also part of the boundary: operating from the course checkout instead of the disposable lab would select the wrong work. Confirm that root before reasoning about status.


#### Concept {#concept-1}

A useful commit makes one intention reviewable. A deadline clarification and an escalation rule can be related business work while still benefiting from separate snapshots: a reviewer can see the delivery promise and then the response to a missed promise. A commit message describes that intent; the actual diff proves what changed. Combining unrelated edits makes later diagnosis or reversal harder.

Staging also lets you choose when a change enters history. An accidental extra line in the working file need not be committed with the deadline, and unstaging differs from discarding content. Inspecting both ordinary and cached diffs reveals that boundary. The fixture remains ordinary contract text, so the review should preserve grain and currency while adding a clear time zone rather than silently replacing the original business assumptions.


#### Concept {#concept-2}

A branch names a position in commit history; it is not a separate copy of every file you must manage manually. Switching branches changes the checked-out snapshot, while merging combines ancestry and file changes. Compatible edits can be combined without conflict when they touch sufficiently separate content from a shared baseline. Adjacent edits in a tiny file can still conflict, so compatibility is a property to observe rather than assume from different branch names.

Use distinct contract facts for this demonstration, such as a nonadjacent delivery refinement and a newly separated producer note. The goal is to preserve both intentions and explain whether history advanced directly or recorded a merge. Fast-forward means the target simply reached a descendant commit; a merge commit records combined parents when histories diverged. Neither outcome alone tells whether the final text is correct.


#### Concept {#concept-3}

A conflict means Git cannot choose a combined text automatically. It does not mean either branch is necessarily wrong or that a valid business decision follows from accepting one side. The conflict markers show candidate content from two histories; the learner must understand the requirements and produce one coherent contract. For ownership, the resulting named owner and escalation responsibility must be compatible rather than two contradictory labels.

The merge remains unfinished until the resolved file is staged and committed. Removing markers without inspecting surrounding text can still lose the deadline or currency facts. A merge commit's parents record which histories were combined, while the resolution diff records the actual decision. That evidence is useful to a future reviewer who did not watch the editor. The exercise deliberately stops with a nonzero merge result so the expected failure can be distinguished from tool or identity setup problems.


#### Concept {#concept-4}

Restoring a working file replaces an uncommitted version with a known snapshot. That can safely remove an intentional teaching mistake after all useful work is committed, but it would discard wanted uncommitted edits if used without inspection. Reverting a committed change is different: it creates another historical decision rather than simply changing the current file. Choosing the operation depends on what state contains the mistake.

The final exercise adds accidental text after the completed ownership merge. Inspecting its diff establishes that only this new line is unwanted. Restoring that file should leave every committed deadline, escalation and ownership decision intact. A clean status then means working/index content agrees with history; it does not mean the contract is correct by itself. The committed file and complete prior evidence provide that additional check.


#### Concept

A remote URL identifies where commits can be fetched or pushed, while a tracking relationship tells Git which remote branch a local branch follows. Neither proves that the signed-in hosting identity has the intended rights. The clone's default branch can also differ from the proposal branch. Those boundaries matter before the first push: a correct contract edit sent to the wrong repository is still the wrong collaboration result.

The independent starter gives content and review context, not remote approval. Inspecting identity, remote URLs, local branch and proposed PR base makes the collaboration destination reviewable. Fetch updates remote-tracking information without automatically rewriting your branch. A private sandbox protects the teaching scope, and a local simulation must retain that label even if its history closely resembles a hosted workflow.


#### Concept {#concept-1}

A push makes branch commits available remotely; a pull request proposes how they should enter another branch. The PR description explains why the contract change matters and how its result was checked, while the diff shows the actual scope. A branch can exist without a PR, and a well-written local description can exist without either. The assessment therefore needs actual remote identity and head commit.

The deadline clarification should name time zone and expected consumer behavior without deleting grain or currency promises. A reviewer who did not attend the terminal session should understand the before/after requirement from the PR. Keeping the proposal on a feature branch preserves the sandbox main baseline and gives the later review response an identifiable place to land.


#### Concept {#concept-2}

Review supplies another participant's reasoning about the proposed behavior. A revision is useful when the new commit addresses a concrete comment and the response explains how. Merely adding any second commit can satisfy a numerical count while leaving the requirement unanswered. The supplied scenario concerns deadline time zone and late-feed responsibility, so the change should make those facts clearer without introducing unrelated policy.

A real peer review differs from a learner playing both sides of a local simulation. Both can teach revision mechanics, but only the former establishes the collaboration boundary required here. The reviewer/comment identity, revision hash and current hosted diff let another person trace that conversation. Approval is also separate from a comment or a pushed response; report it only when the actual review state supports it.


#### Concept {#concept-3}

An open proposal can become stale while another participant changes its base branch. Fetch updates your information about that upstream history; merge or rebase decides how it enters your proposal. Pull combines these operations according to configuration, which can conceal the decision if used without inspection. The final review should include both your clarification and the shared input-classification requirement.

The supplied concurrent edit adds internal input classification on main. A second clone can demonstrate the mechanics when that role is explicitly simulated, but the handoff should say who actually supplied the edit. A merge conflict requires the same requirement-preservation reasoning as foundation practice. An ancestor check proves history includes the upstream commit, while the final contract proves its content and your proposal both survived.


#### Concept {#concept-4}

A proposal's state reflects review, checks and branch policy, not just the last command exit. A green local workflow can coexist with an open PR awaiting review, and a review comment can coexist with no approval. The learner should identify the exact current state and its next authorized action. Some training sandboxes intentionally stop before merge so the review record remains inspectable.

Synchronizing local main after an authorized merge is another action, distinct from declaring that a proposal is ready. If a gate remains blocked, a useful handoff names it rather than manufacturing a merge hash. The actual head, review outcome, check state and retained contract facts let another participant assess completeness. This classroom evidence does not authorize merging production work or publishing the course repository.


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


#### Concept

A container's main process determines its lifetime. A short program that prints and exits can be a successful container execution; keeping it alive with an unrelated sleep would change the behavior being inspected. The image is a reusable package, while the container is one process execution with its own writable layer and recorded state. Removing that container does not automatically delete the image.

The hello command makes this distinction visible before app packaging. Inspecting all containers includes stopped executions that a default running-only list omits. Logs and exit status answer whether the process ran as expected, while the image identifier answers which package ran. A familiar tag can point to a different image later, so retain the actual identifier when comparing runs.


#### Concept {#concept-1}

A container writable layer belongs to that execution. Creating a temporary file inside one disposable container does not place it in the base image or the host application folder. A fresh execution of the same image starts from its packaged filesystem and a new writable layer. This is why an unmounted scratch file disappears after the first container is removed.

An interactive shell changes how you inspect the process, not whether it shares the host kernel. The terminal flags attach input and a pseudo-terminal; a noninteractive command can inspect the same filesystem facts when the classroom interface lacks a terminal. Keep the image's OS/runtime observations distinct from the author's host environment. A container is not automatically a virtual machine with a separate kernel.


#### Concept {#concept-2}

A bind mount exposes a selected host path at a container path. The target can replace what the image would otherwise show there, so both path and access mode matter. Read-only access lets the supplied summary read its fixture while protecting that copied input from container writes. Mounting an entire workspace would broaden the boundary beyond what this task needs.

The app reads its CSV relative to the working directory. A correct mount at one path with execution in another can still fail, even though the file exists somewhere inside the container. Comparing the host and mounted input plus the app output distinguishes this path error from a business-data defect. The deliberate write denial demonstrates the mount promise and should not be repaired by removing read-only protection.


#### Concept {#concept-3}

An image build records filesystem content and startup configuration. Copying the supplied app into an image and selecting its working directory makes runtime independent of a host bind mount. The build context limits which files are available to copy, and the startup command determines which process runs. A benign placeholder Dockerfile can build successfully while still lacking the assessed application.

WORKDIR sets the directory for subsequent relative paths, COPY adds build-context files, and CMD selects the default process. The app's path assumption means copied files and working directory must agree. Packaging the test alone or printing the expected text would bypass the application behavior. The independently supplied test and fixture output make that distinction reviewable. Build success establishes that instructions could be executed; only running the resulting image establishes its main process and actual app result.


#### Concept {#concept-4}

Repeatability means a known package and input produce the stated result across executions. A mutable tag alone is weaker identity than the image ID because the tag can be rebuilt between runs. Two disposable runs from the same image should both print the six-holding fixture result and exit normally. Their writable layers are separate even though their package is shared.

Cleanup is also an ownership decision. Removing every container or pruning all images would interfere with other learners and erase useful evidence. The exercise names its own containers/tags and retains logs and identities before removal. A build cache or shared base image need not be deleted to finish the core. Repeatability here concerns this supplied app and fixture, not every external dependency or production deployment scenario.


#### Concept

A multistage file defines a dependency graph of named build stages. Selecting one target chooses the output image and the stages it depends on; it does not automatically publish every intermediate stage as a separate tagged image. The test target and runtime target therefore need deliberate build/tag commands when both are review artifacts.

Named stages also communicate purpose. A runtime target should contain the executable app/input, while a test target can retain the independent test script and its command. The source file alone cannot show which target an actual build selected or whether a cached stage was reused. Record command, target and resulting image identity so a reviewer can connect intended architecture with observed output.


#### Concept {#concept-1}

A testing stage is useful when it validates the artifact that runtime receives. An unrelated test command in an unreachable stage can look reassuring while providing no gate. The stage graph should connect the tested app/input to the runtime copy path, and a build-time assertion or equivalent explicit workflow should reject an incorrect artifact before acceptance.

The supplied Python test computes the fixture expectation independently of a hard-coded echo. The tiny app's baseline result is fixed, so a controlled copied input or app-path defect should make that assertion fail. Keeping the test's purpose visible prevents a Dockerfile from satisfying advanced work merely by naming a stage test. The runtime output remains a separate observation after the test succeeds.


#### Concept {#concept-2}

A runtime user changes the process's permission boundary, not the meaning of the app. The image should provide readable app/input files and an appropriate working directory for the declared non-root identity. A USER line can name an identity that lacks the necessary file access, so inspect actual UID and execute the app rather than trusting the Dockerfile keyword.

The expected training runtime UID is 10001. Its app only needs read access to the packaged fixture; adding broad writable host mounts or privileged flags would change the exercise boundary. An image can build under root while its final process runs non-root, because build and runtime identities are separate. That distinction should be visible in the explanation and actual command output.


#### Concept {#concept-3}

A focused runtime image contains what the executable needs, not every file available during build. The independent test is useful for acceptance but not required by the summary process. Copying the whole test stage can retain unnecessary scripts or temporary files. Narrow COPY decisions make the runtime boundary easier to inspect and reduce accidental content exposure.

Smaller size alone is not correctness: deleting the input CSV can shrink the image while breaking the app. The appropriate evidence combines required content presence, test-script absence and expected runtime behavior. Build/cache files and runtime files serve different roles. The exercise does not claim a production security audit from this small content check, but it teaches deliberate artifact selection.


#### Concept {#concept-4}

Runtime path failures often come from an inconsistent relationship among build context, COPY destination and working directory. The summary opens its CSV by relative name. Moving its execution directory or copying that input elsewhere can cause a missing-file error even though the image built successfully. The diagnosis should identify that relationship rather than modify business data or install unrelated dependencies.

A controlled defective Dockerfile creates a useful before/after experiment after a known good baseline exists. The build can remain valid while the process fails, demonstrating the distinction between build-time and runtime checks. Repairing the minimal path assumption and rerunning the same fixture establishes recovery. Keep the defect out of the final image and retain evidence before cleaning owned tags.


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


#### Concept

A dbt project describes transformations and dependencies; it does not become a separate database simply because it lives in a container. The adapter compiles and submits SQL to Databricks, where the approved catalog, schema and warehouse determine the relations you read and write. Seeds load copied training inputs. Sources describe that input boundary, while models describe derived relations. Keeping those roles separate helps diagnose a missing table before changing a transformation.

In this fixture a holding is identified by fund, business date and instrument. The same fund appears on two dates, so fund alone cannot identify a row. A report with four rows after both dates are loaded has probably collapsed the date dimension. Inspecting the eight raw rows makes that mistake visible before SQL is written. Distinguish the position date from the extraction timestamp: one describes the observation being valued, the other describes ingestion freshness. An old business date can be the correct teaching input even when its original extraction timestamp is stale. Likewise, a successful connection says nothing about whether the six raw feeds have actually been loaded.


#### Concept {#concept-1}

The source function gives a model a logical dependency on data loaded outside that model. Its first name identifies the source group and its second identifies the table inside that group. Those logical names need not equal the physical warehouse relation: the source identifier can add the owned training prefix while the SQL remains stable. A reference to another model instead declares a derived dependency that dbt can order and document.

Consider the holdings model reading the custodian holdings source. Databricks ultimately executes a fully qualified relation in your approved namespace; the source declaration explains why that relation is an input rather than a generated mart. A raw seed can be present but wrongly mapped to another learner's table. Conversely, a perfectly written declaration can resolve to a table that was never seeded. Compilation and an actual query expose different halves of this boundary. The instrument-reference input is useful to inspect even though the prepared consumer graph does not depend on it. Do not invent a lineage edge merely to make every loaded feed appear in the final report.


#### Concept {#concept-2}

Staging gives raw data stable names and types while preserving its declared population. Renaming the custodian fund code and position date makes their purpose clearer, but it does not justify dropping a date, replacing a missing key or changing money units. Money stored as native market value must remain native market value until the dated FX join explicitly converts it. A fund's master base currency is a separate attribute, not permission to relabel a holding value.

For example, a holding observed on 20 May and the same instrument observed on 21 May represent different positions. The composite key preserves both; casting the date into a SQL date type makes later dated joins less ambiguous. Decimal conversion preserves exact cents within the stated precision, whereas an uncontrolled floating-point aggregation can introduce comparison noise. Quantity has its own precision and meaning. The supplied valuation is not necessarily quantity multiplied by the supplementary price, so reconstructing it that way would silently change the teaching contract. Filtering a zero or negative amount also changes population semantics unless the contract explicitly requires that rule.


#### Concept {#concept-3}

A mart combines modeled inputs into an output a consumer can interpret. Its grain must be declared before aggregation, because an apparently sensible total can conceal loss of dates or duplication from joins. Here the consumer result is one row per fund and position date, containing holding count, GBP exposure and teaching NAV per synthetic unit. The prepared enrichment provides native market value and the matching dated FX rate; the report sums converted holding values at that grain.

For the global-core fund on 20 May, the independent fixture calculation yields GBP exposure of 1,500,440,000 and teaching NAV of 15.004400 after division by one hundred million. The next date is a distinct report row, not an update to that same key. GBP reporting is fixed even when fund master says a fund has another base currency. Cash positions are deliberately excluded from this teaching numerator. Calling the result official custodian NAV would overstate its meaning. A three-column output with a correct grand total can still be wrong for each fund/date, so compare complete keys and values rather than relying on an aggregate smoke check.


#### Concept {#concept-4}

A test is useful when it protects a stated failure mode and its result can be interpreted. A uniqueness test checks row identity, a not-null test checks required presence, and a relationship test checks membership in another relation. None independently proves all joins preserve the intended population. A relationship assertion can ignore nulls, and a reconciliation can compare two outputs that already lost the same fund. Combining structural checks with independent business values closes different gaps.

The holding grain includes a date, while fund-master membership is checked by fund identifier. A date-free fund uniqueness test would therefore reject valid holdings. Conversely, a report sum could stay numerically unchanged if an unknown fund's zero-valued holding were silently filtered out; the population and relationship assertions should still catch that loss. For missing dated FX, the correct failure is incomplete conversion coverage, not a guessed one-to-one rate. The teaching drill deliberately changes a copied input so you can observe the failed assertion, repair its cause and prove the restored output. A red test is not automatically a successful drill unless it failed for the intended reason.


#### Concept

A join's correctness depends on the relationship between its keys and the grain of each input, not on whether SQL executes. Holdings are at fund/date/instrument grain; prices are at instrument/date grain. An instrument-only price join can attach both May prices to every holding and duplicate the holding's native value. The resulting consumer sum may look plausible because it contains familiar columns and positive amounts, but it measures a fan-out rather than the intended position population.

Count the holding keys before enrichment and the matching price rows per key afterward. With this supplied fixture the date-free price join yields sixteen matches from eight holdings; including the position/price date restores one dated price per holding. An unmatched price or FX observation has a different symptom: a left join retains the holding with null enrichment, while an inner join can hide it by dropping the row. A correct pipeline must detect both duplication and loss. The appropriate diagnosis names which input relationship violated its key contract before choosing a repair. Merely adding distinct to the final report can hide multiplicity without selecting the right dated observation.


#### Concept {#concept-1}

An intermediate model isolates business relationships that would otherwise be repeated in every consumer query. Its output contract is more important than its position in a folder: here it retains each typed holding and attaches a dated price, dated GBP conversion rate and converted value. Left joins make missing observations visible to a coverage assertion. They do not excuse incomplete data; they preserve evidence needed to reject it.

A reusable expression is valuable when it states an actual shared rule, such as converting a decimal native valuation by an explicitly matched rate with an agreed output precision. That macro should compile into understandable SQL and should not decide the join keys or manufacture a default rate. For example, a missing May 20 GBP rate must remain null and fail coverage even though GBP-to-GBP is normally one. The feed's declared observation is part of the readiness contract. Fund master may describe a USD base currency while this report remains explicitly GBP. Moving environment routing or relationship selection into an opaque macro would make the model harder to review and would not add useful abstraction.

The supplied `int_fund_attributes` and `int_positions_dated` retain v1's two smaller intermediate contracts. The first filters active funds and exposes their reporting attributes; the second adds cash balance and accrued interest once at fund/date/currency grain. All four raw fund-master entries are active here, and the positions helper retains eight dated rows. These are supplied supporting models to inspect rather than additional unfinished SQL assignments. Cash remains outside the declared teaching NAV, so an available cash field does not authorize silently adding it to that report.


#### Concept {#concept-2}

A business reconciliation compares a consumer result with an independently specified meaning. It should detect wrong units, key loss, joined duplication and changed values rather than simply compare two sums built from the same faulty model. The supplied custodian NAV fixture and Decimal CSV reference give concrete expected results for the unmodified teaching population. Key membership is as important as numeric closeness: a report missing one date should fail even when another row absorbs its value.

A negative case tests the assertion's sensitivity. Removing a copied FX observation should fail enrichment coverage; feeding that incomplete result into a holdings-only NAV report should not produce accepted output. Another controlled experiment intentionally changes a holding's value. That makes baseline NAV comparison fail for a legitimate reason until the variation's expected output is used. These cases require different interpretations. A test message without the input variant and failed node cannot tell a reviewer whether it detected a real defect, an intended correction or an unrelated connection issue. Keep the assertion's unit, tolerance, key set and applicable fixture state explicit.


#### Concept {#concept-3}

Incremental materialization changes how a relation is maintained; it does not automatically make a pipeline correct under late data. A merge needs a stable unique key that identifies the business observation being replaced. For holdings that key includes fund, date and instrument. Choosing only a fund would overwrite another date, while appending without key matching would duplicate an existing observation when the same input is replayed.

This exercise creates a correction to the first copied May holding by increasing its native market value by one thousand. The selected observation is GBP-denominated, so its independently expected GBP value changes by the same amount. The date remains the older fixture date. A filter that processes only dates greater than the current maximum would miss this legitimate correction. Replaying the corrected input twice should produce the same eight-key state after both merges, with one changed value and no duplicate. A second controlled input appends a new holding key: PEF-EM-GROWTH, May 20, GB00B3M9JJ78, with native and GBP value 500. Its price and FX already exist, so the result must grow to nine keys with total exposure another 500 higher. Replaying that combined input must retain nine, proving insertion as well as update. The experiment is bounded to your namespace and copied fixture; it does not prove a general production late-arrival policy, transaction isolation or concurrent writer behavior. Those limitations belong in the handoff.


#### Concept {#concept-4}

An end-to-end feature needs a consumer question, output grain, units, lineage and evidence that someone can review. Generating another SQL file is insufficient if its result cannot be interpreted. A small fund-level report can answer how the two supplied dates differ in holdings exposure; it must label that observation difference without pretending it is investment return. The fixture lacks the flows and complete unit history needed to establish that stronger measure.

Attribute history is a separate feature. A snapshot can retain successive fund-name versions using a stable fund key and validity intervals. A copied fund-master name change creates the exercise's second observed version; it is not a correction to the holding value and does not change the reporting date. One current interval and one closed interval for the changed key demonstrate the intended history. Documentation connects these decisions to the next consumer and to Astro's worker boundary: the terminal's successful build does not prove worker executable paths, mounted files or task-time credentials. A useful handoff states what was actually executed and what still needs connected or human review.


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


#### Concept

A profile selects connection and authentication context; it is not a business namespace or proof of table permissions. The CLI executable version determines available command groups and output options, while the active identity determines whose rights those commands use. A copied source configuration can describe an intended profile/version without establishing the environment currently loaded in the terminal.

Inspecting current user is a read-only identity probe. It should return a safe account identity in the prepared environment, but its success does not imply access to every catalog or warehouse. Keep tokens out of notes and screenshots. When cloud access is absent, the metadata fixture can teach response interpretation but cannot establish authenticated identity. This distinction prevents a local JSON parse from becoming a false readiness pass for later dbt work.


#### Concept {#concept-1}

Workspace objects organize notebooks, directories and other workspace content; Unity Catalog organizes governed data objects through catalog, schema and table names. A path containing training_dev does not mean it is the same object as a catalog named training_dev. The CLI uses different command groups and response fields for those boundaries.

The fixture's workspace directory under Shared and its qualified holdings table illustrate that naming similarity. A SQL warehouse supplies execution for queries, while listing a directory or table metadata does not run model SQL. Misidentifying these objects can send a learner to a filesystem command when they need governed table metadata, or lead them to infer data access from a visible notebook folder. State type, identifier and purpose together rather than retaining only a familiar name.


#### Concept {#concept-2}

Metadata discovery answers what objects exist or are visible and how they are described. It does not automatically return their data rows. Catalog/schema/table listings can be filtered by permissions, so a user may see less than an administrator. A table's qualified identity and type help connect a later dbt source declaration to its physical relation.

Use the instructor's approved namespace rather than assuming a training label is globally unique. The same table short name can exist in several schemas, and a source profile can resolve one while a manual CLI command inspects another. Retaining the full qualified name prevents that confusion. Read-only discovery must not become provisioning: creating schemas, changing grants or deleting a denied object would change the environment rather than explain the observed access boundary.


#### Concept {#concept-3}

JSON output preserves field names and nested structure, making a small selected projection more reliable than visually scanning a long terminal response. The learner should distinguish a response wrapper from its object list and handle an empty list without inventing an error. A filter selecting one qualified table can also return empty because the name or namespace was wrong.

Missing object, denied access and a permitted empty result have different meanings. The installed CLI's exit category and structured response help distinguish them; a blank-looking terminal alone does not. The supplied snapshot offers a stable local interpretation example, while actual cloud observations may differ. Avoid printing entire auth context as a diagnostic shortcut. A useful discovery note retains the selected safe fields and explains what the observation supports and what it cannot establish.


#### Concept {#concept-4}

A discovery handoff makes the inspected environment useful to another learner. It identifies the actual profile/identity, permitted object types and qualified names, relevant metadata and access limitations. A list of commands without interpretation leaves the next person to repeat every probe. Conversely, a claim that the environment is ready can overstate what metadata alone established.

The later dbt route needs a warehouse, approved namespace, loaded sources and usable credentials. CLI discovery contributes identity and object context but does not prove all those execution steps. State the next consumer question, such as which declared holdings relation the prepared pipeline should read, and which separate query/build check remains. This finite phase is read-only and has no advanced provisioning assignment.


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


#### Concept

A DAG definition describes tasks and dependencies; the scheduler decides when a run is due, and a worker executes its task code. The terminal that edits the file is another process boundary. Databricks is yet another boundary, executing dbt SQL remotely. A file visible to the terminal may not be mounted in the worker, and a dbt executable on the terminal path may not exist inside Astro. Diagnosing those differences before writing operators prevents a successful local command from becoming misleading run evidence.

The supplied project contains a complete Portfolio Analytics baseline and a partly authored orchestration file. Its root is discovered relative to the staged DAG, while ownership metadata binds the namespace and relation prefix. For example, the worker must find the staged project directory, its profiles and an artifact directory it can write, not a path copied from your laptop. The same approved warehouse and schema must be reached by terminal seeding and worker transformations. Source presence and a running scheduler do not prove either mount correctness or database permission. The inspection task records those prerequisites explicitly without pretending that setup alone demonstrates orchestration competence.


#### Concept {#concept-1}

An operator executes work; the task identifier is only the name Airflow uses to track that execution. A task called dbt_build that prints a message does not build a data product. The prepared PythonOperator route invokes the delivered dbt executable with explicit project, profile, target and artifact paths. Its exit status and artifacts then connect task state to actual Databricks model and test results. Airflow controls ordering while dbt controls the transformation graph.

The publication-evidence step has a narrower classroom meaning than production release. It checks the consumer output, selects the run's four fund/date rows and writes a receipt tied to run identity, input hashes and the shared contract. A successful no-op marker would be insufficient because it could exist without any correct warehouse result. A small partition identifier can be passed between tasks, but holdings data itself stays in Databricks rather than being copied through XCom. This boundary makes the DAG easier to reason about and prevents a green graph from becoming the only evidence of business correctness.


#### Concept {#concept-2}

Dependencies state which task must finish successfully before another becomes eligible. They do not themselves move business data or guarantee that the downstream task reads the right relation. The required chain is readiness, dbt build, quality and publication evidence. This protects the receipt from being created before inputs and results have been checked. Leaving a branch disconnected can make a green task appear even when its upstream product work failed.

A manual trigger and a scheduler-created run can execute the same graph, but they establish different things. The manual run can help diagnose code and logs; only the scheduled run proves the configured timetable, scheduler and worker boundary required here. The schedule's logical date/data interval is not automatically the May business partition. Catchup is disabled and the fixture date is explicit. A prior green UI run may belong to old code or another prefix, so record current DAG/run/task identities and the start of this rehearsal. Both the dependency graph and the actual task state transitions matter.


#### Concept {#concept-3}

A task failure is a state with a cause, not merely a red UI tile. A controlled business-quality fault should fail the quality task after dbt has built its input and prevent downstream evidence. A bad executable path or expired token is a different failure category and should not be counted as the intended quality drill. Reading the first useful log error distinguishes these cases and guides the repair.

The supplied fault marker belongs to your owned stage. While it exists, the quality branch raises its declared teaching failure and the evidence task becomes upstream-failed. The last accepted receipt should remain available, but this failed run must create no new accepted receipt. Removing the marker repairs the controlled cause; rerunning without removing it merely repeats the failure. Retries can repeat transient work, but they cannot turn a permanent business-quality violation into correct data. This small experiment teaches failure propagation and bounded recovery without requiring external alert transports or production deployment.


#### Concept {#concept-4}

Completion evidence connects an executed workflow to a business result a reader can assess. Airflow's run and task identities establish which orchestration instance ran; dbt artifacts identify transformations and tests; an independent warehouse query establishes the intended population and values. None can substitute for all the others. A correct report queried from an old prefix says little about whether your current scheduled worker produced it.

The receipt ties a current run to its selected fixture partition and input hashes, while checking the complete small report. It is useful because the May business date differs from the October timetable. The handoff must distinguish those clocks and explain the build's full-fixture scope. Authentication is another boundary: a terminal login does not automatically make a cached worker connection fresh, and a first successful run does not prove expiry/restart recovery. Describe these unexecuted checks honestly. The classroom evidence step also does not grant consumers access, publish a catalog product or authorize deployment. That narrow meaning avoids overclaiming a successful practice workflow.


#### Concept

Replay asks a workflow to repeat work for an identified business input, so correctness depends on more than the new run's timestamp. The scheduler interval describes when Airflow created work; the fixture partition describes which business-date result the receipt presents. The copied graph refreshes both supplied dates, and its output check must still select the declared partition explicitly. A current run can therefore describe historical holdings without claiming that old holdings were newly generated.

Readiness has two separate conditions: the declared raw population exists, and extraction timestamps meet the freshness promise for this rehearsal. A presence sensor alone cannot establish freshness, while a fresh timestamp alone cannot establish complete rows. The supplied May timestamps intentionally reveal that distinction. A documented timestamp-only refresh changes ingestion observation time but keeps fund/date keys and valuations unchanged. The run must reject an unsupported business date rather than silently attach an empty or latest result. Those explicit contracts prevent a green replay from referring to the wrong input or a receipt that only relabels yesterday's evidence.


#### Concept {#concept-1}

Retry policies express a belief about which failures might disappear without changing business inputs. A transient connection interruption can merit a bounded retry; a missing required FX observation or a deliberate quality marker requires repair. Retrying the latter only repeats the violated contract. The task log, attempt identity and delay reveal what happened; a final state alone cannot explain whether retry was useful.

The prepared classroom default uses a bounded retry and a short delay, with logging-only failure callbacks. Keep those controls within the rehearsal window rather than introducing unlimited waits. The callback observes a failure; it must not swallow the operator exception or write an accepted publication receipt. With one active run and a two-minute schedule, an unrepaired fault can affect a later scheduled run as well, so pause or bound the owned rehearsal while collecting evidence. Compare a readiness failure with a quality failure to show where the graph stops. Both should block downstream accepted evidence, but their causes and repair locations differ.


#### Concept {#concept-2}

Recovery is successful when the workflow's repaired result satisfies its business contract. A later green run could still read stale relations, duplicate a date or select another learner's output. Independent key/value checking establishes what the consumer actually receives. The shared contract and owned prefix bind the query to the staged attempt; the receipt binds it to a run and business partition.

Replaying identical copied input should preserve the complete eight-key report and the selected four-row partition result. Distinct runs may write distinct evidence files while producing identical business values; that is expected, not duplicate business data. Replaying the other May date should produce a different selected partition without erasing the first run's receipt. The supplied tiny graph rebuilds the fixture, so this exercise proves repeatable checked output rather than every possible incremental/backfill algorithm. The dbt advanced route demonstrates the separate Delta correction transition. Explain that limit instead of calling two green tasks a general exactly-once guarantee.


#### Concept {#concept-3}

An operational screen is useful when it helps answer a decision, not when it merely looks green. The graph shows dependencies, the grid shows run/task state over time, and a task log shows the causal error and attempt. These views need the exact owned DAG and fresh run identity. A bookmarked old run can look convincing while describing different code, inputs or namespace.

For the controlled marker, the decision is to remove the known fault and rerun a bounded owned scope, not clear every task or change warehouse grants. For expired credentials, the decision concerns delivered connection refresh and worker token resolution, not replacing business values. For missing mounted files, inspect the worker path. The API validates machine-readable identities and states; human review assesses whether the corresponding UI and logs are understandable and safe to present. Neither automatically establishes auth expiry/restart behavior. A short operational note should explain the chosen action and its evidence so another learner can distinguish diagnosis from trial-and-error clicking.


#### Concept {#concept-4}

An incident handoff explains impact, cause, action and evidence of recovery so someone else can decide what to do next. In this classroom pipeline the impact is blocked publication evidence for a named fixture partition, not a claimed production outage. The cause must be the observed marker, readiness, auth or path condition; vague statements such as Airflow was broken do not guide a successor.

The handoff also states ownership: which DAG, stage and prefixed warehouse relations belong to this attempt and how cleanup preserves others. A prepared Cosmos or hosted observability route can be useful optional depth, but does not become a missing mandatory deployment step. The finite core demonstrates an understandable data result, intended failure and recovery. Distinguish configured behavior from the recovery you actually observed. A good note names the remaining checks and their exact environment without replacing them with reassuring prose.


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


#### Concept

An event describes an occurrence and the input it refers to; it does not carry every row of that dataset. Identity supports tracing and replay decisions, version identifies the expected fixture semantics, and location is a controlled reference rather than permission to execute an arbitrary path. The arrival timestamp describes event context, not automatic proof of processing completion.

The bridge validates the small fixture contract before it triggers work. A valid record can therefore be accepted as input while its downstream run remains pending. Reusing an event identifier with a different payload changes its meaning and must be rejected under the declared policy. Kafka's retained log and consumer offsets track broker progress; they are separate from a receipt that says the data result was checked. Keeping those boundaries explicit prevents a syntactically valid JSON event from becoming a false end-to-end pass.


#### Concept {#concept-1}

A Kafka topic contains partition logs: ordered lanes of retained records. Each record has an offset, its position in that lane. A consumer group maintains its own progress. Two groups can consume retained records independently, but two learners accidentally using the same group can affect each other's observed offset progression. Topic/group ownership is therefore part of the classroom setup rather than an optional naming preference.

A broker metadata response establishes that the intended topic/partition is reachable. It does not mean an event was produced or a workflow completed. The prepared local runtime keeps infrastructure work outside this short clinic. A port collision or missing container engine is a setup condition; it should not be repaired by deleting unrelated services. The learner's task is to inspect the actual allocated boundary and explain its role.


#### Concept {#concept-2}

Producer acknowledgement means the broker accepted a record at a partition/offset. It does not mean a consumer processed it or a downstream data job succeeded. The supplied bridge reads the event, validates its input contract and triggers the prepared Airflow run with a deterministic identity. Its evidence records broker position and the corresponding run so those boundaries can be traced.

Consumer offset progress also has a policy: acknowledging or committing a consumed record can occur before downstream success, depending on the bridge contract. The learner must inspect that behavior rather than call every committed offset completed data. A uniquely identified event avoids confusing a current trace with a prior record already retained in the topic. Actual task states and receipts provide later execution evidence.


#### Concept {#concept-3}

An event-driven result must be associated with the input event that selected it. Correct-looking fund totals from a previous run or another fixture are not sufficient. The receipt should bind event payload and run identity, while independent dbt output checking confirms the controlled fixture's per-fund values and population. A shared grand total cannot reveal values shifted between funds.

This optional clinic deliberately uses the small A/B/C fixture and local prepared chain. Its evidence must not be presented as the assigned Databricks Portfolio product. The independent reference protects both fund membership and native fixture values. A zero-valued C holding still belongs to the expected population, so dropping it because it contributes nothing to a sum would change the output contract. Trace identity and business values together.


#### Concept {#concept-4}

Replay policy defines how retained records are interpreted when the same event is seen again. The supplied bridge can reuse an identical completed run when its receipt matches the event payload. A record with the same event identity but changed payload is a conflict, not a new legitimate input under that policy. The broker can assign a later offset while the bridge reuses the prior run.

This is a bounded teaching strategy based on a matching completed receipt, not a general exactly-once guarantee. An existing run without a matching completed receipt needs explicit recovery inspection, and concurrent events or a broader deduplication store introduce additional design questions. The learner should explain those limits rather than claiming that a successful replay solved all distributed failure modes. Business output stability and run reuse are separate checks.


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


#### Concept

A consumer report needs a population as well as a row grain. One row per portfolio describes the shape of output, but does not say whether every known portfolio or only those with qualifying activity should appear. Atlas's core report is driven by valid trades and their resulting positions. A conformed portfolio with no qualifying trade participation can legitimately be absent under that contract. It should not silently disappear if the consumer expected an all-portfolio inventory.

The supplied fixture makes this distinction measurable: 2,500 conformed portfolios, 1,028 with qualifying trade-derived output, and 1,472 without it. Keys remain important even for omitted populations because an anti-join must identify exactly which portfolios are absent and why. Source→domain→consumer alignment connects that business meaning to transformations. For example, cents become decimal price units before position valuation, and a portfolio's advisor key connects to the advisor dimension. A diagram without the correct keys or units cannot protect against a plausible but wrong join. State the intended question and relationship before deciding how many tables to build.


#### Concept {#concept-1}

A domain fact defines which raw observations represent valid business activity and how their values are expressed. Atlas keeps trades with positive quantity and price and a recognized buy/sell side. That rule excludes 120 of the ten thousand raw rows in this fixture. Retaining trade, portfolio and instrument identifiers allows the consumer and quality checks to trace that selection instead of relying on an unexplained reduction in count.

Price cents must be divided by one hundred to obtain decimal currency units. Fee basis points are divided by ten thousand when applied to traded value. For a simple worked example, two units at 12,500 cents create 250 currency units of traded value; a twenty-basis-point fee is 0.50 units. Multiplying by twenty as a percentage would be wrong by orders of magnitude. Buy and sell are directions used later for signed position quantity; a raw sell trade can have positive quantity and remain valid. A nonnegative test on derived signed net position would therefore enforce the wrong contract. Types, units and filters must be explained together.


#### Concept {#concept-2}

A portfolio summary aggregates positions at portfolio grain, then attaches the client and advisor context through the declared portfolio relationships. Positions are at portfolio/instrument grain, so several positions can contribute to one report row. Aggregating or joining at the wrong key can duplicate market value, attach another advisor or exclude a portfolio without an obvious SQL error. Retained identifiers make those defects inspectable.

The prepared position model sums signed quantity and fees across valid trades and uses a deterministic latest-price observation. The summary then reports nominal fixture market value, fees, trade count and position count. It does not convert currencies or establish realized investment performance. Those limitations matter when explaining a consumer metric. The supplied 3,717 positions yield 1,028 portfolio summaries, not one report row for every conformed portfolio. A correct grand total can still hide value shifted between portfolios, so compare full portfolio-key projections and relationship identities. Descriptive names enrich the result but cannot replace stable keys.


#### Concept {#concept-3}

An anti-join answers which declared keys are absent from another population. It is more informative than subtracting two row counts because it identifies the missing members and lets you inspect their cause. For Atlas, comparing all conformed portfolios with the trade-active summary reveals the expected 1,472 portfolios without qualifying activity. Comparing a correct relationship with a deliberately wrong join reveals a different, avoidable loss.

Portfolio client identifiers and advisor identifiers can both be integers without describing the same entity. Joining a portfolio's client key to the advisor dimension can accidentally match a subset and drop the rest. The output may still contain familiar advisor names and plausible amounts. That defect cannot be explained as inactive population merely because the row count is smaller. Keep the business membership rule separate from the SQL relationship predicate. The consumer may later choose an all-portfolio variant, but that is a contract change with explicit empty-status semantics, not permission to disguise an erroneous join.


#### Concept {#concept-4}

A data product is useful when its consumer can understand what the output represents, which quality promises were checked and what its limits are. SQL completion and a green test summary are technical evidence, but the consumer also needs population, units, timing and ownership. The Atlas minimum slice makes this concrete through valid trades, positions and an active-portfolio report with an independently accounted excluded population.

Quality assertions should protect keys, relationships, filter membership and business arithmetic. A relationship test alone may ignore nulls; a numeric reconciliation alone may share a lost population; an output sample alone cannot establish complete keys. The team therefore combines structural tests with independent per-key comparison and a controlled wrong-join diagnosis. The presentation describes the nominal-money limitation and supplied supporting baseline, avoiding claims of FX-normalized AUM or official performance. Roles help review the result: the producer explains source meaning, the creator explains transformations, and the consumer challenges whether the report answers its stated question.


#### Concept

A richer report adds measures with distinct business meanings rather than renaming the same total. Buy and sell value describe traded activity, net flow describes their difference, and current nominal AUM describes signed position quantity valued at the prepared latest price. These measures can differ substantially without being inconsistent. The portfolio performance report combines baseline summary fields with position-level bought/sold totals reaggregated to portfolio grain.

The realized fee rate is a weighted rate: aggregate fees divided by aggregate traded value, multiplied by ten thousand to express basis points. Averaging trade fee rates would weight a tiny trade the same as a large one and answer another question. For example, a fee of one on total traded value of one thousand corresponds to ten basis points, not one percent or a fraction mislabeled as basis points. A zero traded denominator needs an explicit null-safe rule. This fixture does not provide a flow-adjusted investment-return calculation or FX-normalized wealth measure, so the report title and consumer explanation must not claim either.


#### Concept {#concept-1}

A leaderboard defines both the participating population and the ranking rule. Here the prepared advisor book aggregates active portfolio reports, so participation follows the declared trade-active consumer population rather than every advisor record in the raw reference. Stable advisor identifiers and region attributes must remain available for reconciliation and the later regional rollup. A display name alone is not a safe grouping or relationship key.

Dense ranking gives equal book values the same rank and assigns the next distinct value the next integer. With values ten, ten and five, dense ranks are one, one and two. A row-number function instead forces a unique order, while ordinary rank can leave a gap; those alternatives support different consumer interpretations. A separate deterministic display ordering can use advisor identifier after rank without breaking the tie meaning. The supplied nominal book values inherit the fixture's absence of FX conversion, so a leaderboard comparison must state that limitation rather than turn the ranking into a real-world advice claim.


#### Concept {#concept-2}

A rollup changes grain through aggregation, so each measure must be interpreted at the new grain. The regional report groups the advisor leaderboard by region, counting participating advisor rows and summing their portfolio counts, nominal AUM and fees. Counting raw trades would produce another measure entirely. Rejoining lower-grain positions after the leaderboard could duplicate advisor totals and make the report look larger without adding new consumer meaning.

This dependency is explicit: the regional report requires the completed leaderboard and its region/totals, while the separate performance mart supports another question. The core does not need every legacy extension before a region can be built. Region membership must be inherited from the declared advisor mapping, not guessed from an advisor name or client segment. Summing region totals can match a shared upstream error, so the independent oracle should rebuild expected regions from copied source relationships and valid-trade values. Key membership and counts complement the numeric comparison.


#### Concept {#concept-3}

Reconciliation needs sensitivity to a realistic defect, not just a happy-path pass. A regional report that omits an advisor can still return familiar region names and plausible positive totals. The independent expected contribution must expose the lost advisor/portfolio membership and money. Comparing only two outputs that share the omission could miss it completely.

The controlled negative drill changes a copied report predicate to omit a participating advisor. Its failed assertion should identify the affected region/key/value contract. Restoring that predicate and rebuilding the model repairs the cause; changing the expected oracle or tolerance would merely hide it. Keep the baseline raw data unchanged so the difference comes from the deliberate model defect. Tie and zero-denominator examples protect separate semantics and should not be counted as this omission drill. A nonzero build exit alone could arise from credentials or an unfinished unrelated model, so inspect the actual failed node and diagnostic rows before declaring the negative case meaningful.


#### Concept {#concept-4}

An advanced capstone should have a finite completion standard so a team can demonstrate a coherent product rather than an arbitrary collection of files. Here the three consumer views support related but distinct questions: portfolio trading/fee detail, advisor book comparison and regional aggregation. Their grains and dependencies make that relationship understandable. The presentation must explain how independent checks and the omission drill protect the output, not merely display a long list of passed tests.

Optional depth can extend windows, freshness, exposures, macros, generic tests, incrementals, snapshots or orchestration, but each adds prerequisites and time. Selecting an extension does not erase unfinished core reports, and finishing every legacy extension is not mandatory. The team should choose based on a consumer question and available prepared runtime. Honest limits are part of the product: nominal native-unit money, active population, supplied baseline, unobserved warehouse/orchestration boundaries and unpiloted timing. A classroom artifact and reviewed source are valuable without implying production promotion or publication.

