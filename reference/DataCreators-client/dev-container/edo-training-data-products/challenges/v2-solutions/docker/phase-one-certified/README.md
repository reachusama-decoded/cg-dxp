# Instructor: docker phase-one-certified

The following reasoning is generated from the canonical learner phase. Runnable reference files are in `solution/`; learner setup and task prose remain authoritative in `challenges/v2/docker/phase-one-certified/README.md`. Use the complete updated instructor training workspace for runtime commands. Current local checks do not establish fresh connected reconstruction or human acceptance.

## Reference and starter commands

From the updated training project root, use the version-explicit interface. Verification preserves source bytes and runs reference work in a temporary owned copy. Airflow needs fresh scheduled/API/warehouse evidence from the owned stage.

```bash
mise run challenge:v2:verify-starter docker phase-one-certified --mode offline
mise run challenge:v2:verify-solution docker phase-one-certified --mode offline
```

Supporting or blocked output is not connected completion. Actual learner explanations and intended negative drills need review alongside business behavior.

## Phase-owned reasoning



Read these explanations after attempting the checks.

### Reasoning: Run an image and inspect the lifecycle

<a id="docker-p1-01-reasoning"></a>

<details>
<summary>Reasoning for docker-p1-01: Lifecycle state follows the main process</summary>

A zero-exit hello process is successful even though the container is stopped. Logs, exit status and actual identifiers establish that execution. Container removal and image removal affect different resources. Client installation is only a prerequisite, and this hello result is not evidence that the supplied app was packaged.

Learner task: `docker-p1-01` in `challenges/v2/docker/phase-one-certified/README.md`.

</details>

### Reasoning: Explore an interactive shell

<a id="docker-p1-02-reasoning"></a>

<details>
<summary>Reasoning for docker-p1-02: A writable layer is different from image or mounted persistence</summary>

The temporary file belongs to the first execution's writable layer and is absent in a fresh container from the unchanged image. Reusing the same execution or adding a volume would change that experiment. Interactive flags affect inspection, not kernel isolation. Record actual runtime observations separately from the author's host.

Learner task: `docker-p1-02` in `challenges/v2/docker/phase-one-certified/README.md`.

</details>

### Reasoning: Use a bounded bind mount

<a id="docker-p1-03-reasoning"></a>

<details>
<summary>Reasoning for docker-p1-03: Mount permissions and runtime paths protect different obligations</summary>

The selected host app path is readable in the container but deliberately not writable. The working directory makes its relative CSV lookup correct. Expected summary and expected write denial are complementary observations; a failure before mounting proves neither. Keep the host input unchanged and avoid broad mounts that would obscure the intended boundary.

Learner task: `docker-p1-03` in `challenges/v2/docker/phase-one-certified/README.md`.

</details>

### Reasoning: Author and run a simple holdings image

<a id="docker-p1-04-reasoning"></a>

<details>
<summary>Reasoning for docker-p1-04: Build and runtime output establish different steps</summary>

The Dockerfile must package the supplied script and fixture at a working directory that satisfies its relative lookup. A real run without a host mount proves those files are in the image. The placeholder is intentionally buildable but incomplete. Independent app output, image identity and selected logs prevent build success or echoed text from substituting for the authored packaging result.

Learner task: `docker-p1-04` in `challenges/v2/docker/phase-one-certified/README.md`.

</details>

### Reasoning: Prove repeatability and clean scoped resources

<a id="docker-p1-05-reasoning"></a>

<details>
<summary>Reasoning for docker-p1-05: Repeatability needs package identity and bounded ownership</summary>

Distinct executions can share the same immutable image ID and independent writable layers. Matching expected output from that identity demonstrates this bounded app result. Cleanup preserves evidence and removes only named owned resources, leaving shared bases and other learners intact. Local fixture tests supplement rather than replace the actual image build/run observations.

Learner task: `docker-p1-05` in `challenges/v2/docker/phase-one-certified/README.md`.

</details>
