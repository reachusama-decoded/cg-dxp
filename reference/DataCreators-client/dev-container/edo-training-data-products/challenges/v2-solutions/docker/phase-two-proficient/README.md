# Instructor: docker phase-two-proficient

The following reasoning is generated from the canonical learner phase. Runnable reference files are in `solution/`; learner setup and task prose remain authoritative in `challenges/v2/docker/phase-two-proficient/README.md`. Use the complete updated instructor training workspace for runtime commands. Current local checks do not establish fresh connected reconstruction or human acceptance.

## Reference and starter commands

From the updated training project root, use the version-explicit interface. Verification preserves source bytes and runs reference work in a temporary owned copy. Airflow needs fresh scheduled/API/warehouse evidence from the owned stage.

```bash
mise run challenge:v2:verify-starter docker phase-two-proficient --mode offline
mise run challenge:v2:verify-solution docker phase-two-proficient --mode offline
```

Supporting or blocked output is not connected completion. Actual learner explanations and intended negative drills need review alongside business behavior.

## Phase-owned reasoning



Read these explanations after attempting the checks.

### Reasoning: Separate named build targets

<a id="docker-p2-01-reasoning"></a>

<details>
<summary>Reasoning for docker-p2-01: Separate outputs require deliberate target builds</summary>

Named stages describe dependency and purpose. Selecting runtime does not automatically tag every stage, so retain explicit test/runtime builds and actual image IDs. Their commands produce different expected outputs. Source stage declarations are useful review evidence but cannot substitute for real target execution or an actual oracle run.

Learner task: `docker-p2-01` in `challenges/v2/docker/phase-two-proficient/README.md`.

</details>

### Reasoning: Gate the runtime on a tested artifact

<a id="docker-p2-02-reasoning"></a>

<details>
<summary>Reasoning for docker-p2-02: The test must validate the artifact runtime actually uses</summary>

The meaningful gate is the supplied oracle executed on the same app/input passed to runtime. A disconnected stage or unconditional success message does not establish it. The bounded defective artifact should fail for its intended reason, and restoration should recover the expected summary. Build-time gating and an explicit separate acceptance test need truthful distinction.

Learner task: `docker-p2-02` in `challenges/v2/docker/phase-two-proficient/README.md`.

</details>

### Reasoning: Run with a bounded runtime user

<a id="docker-p2-03-reasoning"></a>

<details>
<summary>Reasoning for docker-p2-03: Build identity and runtime identity are different boundaries</summary>

The finished process must actually run as UID 10001 while reading the correctly packaged app/input. Build steps may use another identity. Source USER text states intent, while identity plus successful output proves the runtime boundary. Minimal file access is the proper repair; root or privileged execution would bypass the assessed contract.

Learner task: `docker-p2-03` in `challenges/v2/docker/phase-two-proficient/README.md`.

</details>

### Reasoning: Keep runtime contents focused

<a id="docker-p2-04-reasoning"></a>

<details>
<summary>Reasoning for docker-p2-04: Focused content requires both absence and functioning presence</summary>

The runtime does not need the test script, but it does need the summary and input. Actual final-stage inspection plus expected output establishes both sides of that boundary. Size or source COPY text alone can conceal missing required content or accidental test material. Tie the observations to the same runtime identity.

Learner task: `docker-p2-04` in `challenges/v2/docker/phase-two-proficient/README.md`.

</details>

### Reasoning: Repair a path assumption and explain the result

<a id="docker-p2-05-reasoning"></a>

<details>
<summary>Reasoning for docker-p2-05: A minimal causal repair preserves the other runtime promises</summary>

The app's relative input lookup links COPY path and working directory. A valid build can still fail that runtime contract. The controlled defect and minimal repair must preserve test gating, non-root identity and focused contents. Actual failure/recovered output and image IDs establish the transition; host mounting or echoed output would bypass it.

Learner task: `docker-p2-05` in `challenges/v2/docker/phase-two-proficient/README.md`.

</details>
