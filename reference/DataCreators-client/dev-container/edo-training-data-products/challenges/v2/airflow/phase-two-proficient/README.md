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
