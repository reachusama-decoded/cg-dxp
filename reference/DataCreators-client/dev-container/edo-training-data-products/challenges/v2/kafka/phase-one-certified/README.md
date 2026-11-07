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

Explain producer acknowledgement, consumer offset and downstream completion as separate observations. The supplied bridge is bounded and its completed-receipt policy does not establish distributed exactly-once behavior or arbitrary concurrent event deduplication. Use the instructor-provided topic/group/runtime and clean only the owned clinic resources after preserving evidence. Offline JSON validation is supporting input evidence; the broker, actual Airflow and dbt chain remain pending without their prepared runtime. Kafka is optional everywhere and phase two is not offered. Mandatory dbt/Airflow/CG capstone completion never depends on this clinic.

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
