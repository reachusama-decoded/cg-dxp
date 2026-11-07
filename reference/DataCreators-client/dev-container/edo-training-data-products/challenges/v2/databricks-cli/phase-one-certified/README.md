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
