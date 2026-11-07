# docker: Phase 1 — foundations

## Purpose and outcome

Package and run a tiny portfolio-summary application while learning image/container boundaries. The app is supplied so your authoring focuses on Docker rather than rewriting business logic. You inspect process lifecycle and filesystem isolation, use a controlled mount, write a simple Dockerfile and prove the packaged app's output.

## Dataset and pipeline

The fixture under app contains six holdings and a standard-library summary script. Its total market value is 12,011,626.50. This small Docker fixture is distinct from the eight-row supplied Databricks Portfolio Analytics case; do not present its output as that pipeline's completion. The app reads a file relative to its working directory, so runtime path and copied input matter. A supplied Python test independently checks the fixture/application result. A container can exit normally after printing the summary because its main process has finished.

## Prerequisites and workspace

Use the delivered Docker client with access to the prepared training engine, Python for the optional local app check, and a pulled base image. Prepare a copied attempt through the version-explicit mise task, then work from its root. Choose a unique container name and image tag so two learners do not collide. The engine and image-pull boundary should be ready before timed practice; source presence alone does not establish either.

```bash
mise run challenge:v2:prepare docker phase-one-certified
cd .local/challenges-v2/docker/phase-one-certified
export DC_DOCKER_NAME=dc_alex_docker01
export DC_DOCKER_TAG=dc-alex-docker01:practice
docker version
```

Keep commands inside this attempt and mount only its chosen app directory, using an absolute host path. Do not mount the host root, create privileged containers or remove shared images to repair a path mistake. If an interactive terminal is unavailable, use a documented noninteractive inspection command and label that variation. A new attempt gets a fresh workspace and name; reset does not delete existing work.

## Starter behavior

The supplied Dockerfile is a benign buildable placeholder that prints its unfinished status and exits successfully. That behavior proves a starter can launch, not that you packaged the app. The Python summary and test work outside Docker from the app directory. Replace the Dockerfile's placeholder with the named authoring outcome before expecting completion verification to pass. Read-only mount writes intentionally fail later; an unavailable engine or image download is a prerequisite failure, not that teaching drill. Keep those failure categories separate in evidence.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 60–90 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [docker-p1-01: Run an image and inspect the lifecycle](#docker-p1-01) | 12–18 | Hello output, actual image/container identity and exit status |
| [docker-p1-02: Explore an interactive shell](#docker-p1-02) | 12–18 | Inside file disappears in a fresh disposable execution; version/OS evidence |
| [docker-p1-03: Use a bounded bind mount](#docker-p1-03) | 12–18 | Actual fixture summary and expected write denial; host input unchanged |
| [docker-p1-04: Author and run a simple holdings image](#docker-p1-04) | 12–18 | Authored image emits independent six-holding result |
| [docker-p1-05: Prove repeatability and clean scoped resources](#docker-p1-05) | 12–18 | Two matching outputs from one image identity; only owned resources removed |

## Core challenges


<a id="docker-p1-01"></a>

### docker-p1-01: Run an image and inspect the lifecycle


<a id="docker-p1-01-concept"></a>

#### Concept


A container's main process determines its lifetime. A short program that prints and exits can be a successful container execution; keeping it alive with an unrelated sleep would change the behavior being inspected. The image is a reusable package, while the container is one process execution with its own writable layer and recorded state. Removing that container does not automatically delete the image.

The hello command makes this distinction visible before app packaging. Inspecting all containers includes stopped executions that a default running-only list omits. Logs and exit status answer whether the process ran as expected, while the image identifier answers which package ran. A familiar tag can point to a different image later, so retain the actual identifier when comparing runs.


#### Challenge


Run `docker version` and `docker info`, then launch the hello process using your unique container name:

```bash
docker run --name "$DC_DOCKER_NAME" python:3.11-slim python -c "print('hello holdings')"
```

Inspect its logs, state, exit code and actual image identifier. Explain why successful output leaves a stopped container. Retain those observations, then remove only this named execution. If the engine or base image is unavailable, resolve that preparation issue before interpreting program behavior. Do not keep the hello process alive with a sleep: its normal completion is the lifecycle observation.


#### Hint


<details>
<summary>A successful short process can leave a stopped container</summary>

Use docker ps -a to include stopped containers. Instructor preparation supplies Docker and a pulled base image.

Use the stopped-container view and inspect the named execution rather than searching for any green-looking process. The expected hello output comes from its main command, not an image build. Keep removal separate from image cleanup so you can explain which state disappears. A name already in use means choose or inspect your owned attempt, not delete an unknown container.

</details>

#### Check


Expect the named execution's logs to contain the declared hello output and its process exit status to be zero. Retain container and image identifiers and explain the stopped state. Removing the execution should leave the reusable image available; inspect that distinction rather than infer it from a command message.

A printed client version alone does not prove engine access or process execution. If a preexisting name prevents launch, use a unique owned name and record the collision instead of removing someone else's container. This lifecycle observation is separate from the final six-holding app result and cannot be counted as completed packaging.

```bash
docker ps -a
docker logs "$DC_DOCKER_NAME"
docker inspect "$DC_DOCKER_NAME"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p1-01-reasoning)


---


<a id="docker-p1-02"></a>

### docker-p1-02: Explore an interactive shell


<a id="docker-p1-02-concept"></a>

#### Concept


A container writable layer belongs to that execution. Creating a temporary file inside one disposable container does not place it in the base image or the host application folder. A fresh execution of the same image starts from its packaged filesystem and a new writable layer. This is why an unmounted scratch file disappears after the first container is removed.

An interactive shell changes how you inspect the process, not whether it shares the host kernel. The terminal flags attach input and a pseudo-terminal; a noninteractive command can inspect the same filesystem facts when the classroom interface lacks a terminal. Keep the image's OS/runtime observations distinct from the author's host environment. A container is not automatically a virtual machine with a separate kernel.


#### Challenge


Start a disposable shell with `docker run --rm -it python:3.11-slim bash`. Inspect `pwd`, Python's version and `/etc/os-release`. Create `/tmp/inside.txt`, exit, then launch a fresh container from the same image and test whether the file exists.

Record both execution identities and observations. If an interactive terminal is unavailable, use a noninteractive command for the same creation/removal experiment and explain that choice. Keep both executions unmounted and leave the shared base image unchanged. A volume or a committed replacement image would introduce persistence and change the question being tested.


#### Hint


<details>
<summary>Compare fresh executions without adding persistence</summary>

The terminal flags attach standard input and a TTY; `--rm` removes the exited container.

Compare the two executions' identities and filesystem observations. The first file was created after launch, so it belongs to that writable layer. Do not commit the container into another image or add a volume during this experiment; either would change the persistence contract. A missing interactive terminal should change the inspection method, not the expected filesystem result.

</details>

#### Check


The second fresh execution should not contain the temporary file from the first removed container. Retain the first successful creation and second absence check with Python/OS observations. Explain which filesystem content came from the image and which was created at runtime. An accidentally reused container would not test the same claim.

Record the interactive or noninteractive method and why it was used. Do not describe the outcome as a separate-kernel virtual machine demonstration. The observation establishes disposable writable-layer behavior, not every possible persistence mechanism; the next mount task deliberately changes that boundary.

```bash
docker run --rm python:3.11-slim python -c "from pathlib import Path; print(Path('/tmp/inside.txt').exists())"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p1-02-reasoning)


---


<a id="docker-p1-03"></a>

### docker-p1-03: Use a bounded bind mount


<a id="docker-p1-03-concept"></a>

#### Concept


A bind mount exposes a selected host path at a container path. The target can replace what the image would otherwise show there, so both path and access mode matter. Read-only access lets the supplied summary read its fixture while protecting that copied input from container writes. Mounting an entire workspace would broaden the boundary beyond what this task needs.

The app reads its CSV relative to the working directory. A correct mount at one path with execution in another can still fail, even though the file exists somewhere inside the container. Comparing the host and mounted input plus the app output distinguishes this path error from a business-data defect. The deliberate write denial demonstrates the mount promise and should not be repaired by removing read-only protection.


#### Challenge


From the copied starter, run the supplied summary with `app/` mounted read-only at `/app` and `/app` as the working directory. Use an absolute host path. Compare the copied input with what the container reads.

Attempt a container-side write to the mounted input directory, retain the expected denial and verify the host copy did not change. Explain the source path, target path and access mode separately. If the summary cannot find its CSV, inspect the working directory before changing permissions. Keep the mount limited to the app directory rather than broadening it to the whole workspace.


#### Hint


<details>
<summary>Align the mount target and app working directory</summary>

Use an absolute host path from pwd and the :ro mount suffix. Do not mount the entire host root.

Check source path, container target and working directory as three separate values. The read-only suffix belongs to the mount declaration; do not assume the app itself protects the input. If summary cannot find its CSV, inspect the current directory before weakening permissions or mounting more host content. The write should fail while the read remains successful.

</details>

#### Check


The mounted app run must produce six holdings with total market value 12,011,626.50, matching the local fixture oracle. The controlled container-side write must fail for the read-only mount reason, and the host input hash/content must remain unchanged. Retain command, exit categories and output rather than only an image of the mounted folder.

Explain which files come from the image and which from the host mount, and why the current directory affects this app's relative CSV path. An engine or image-pull failure does not count as the intended write-denial drill. Do not remove the protection to make the negative command green.

```bash
docker run --rm -v "$PWD/app:/app:ro" -w /app python:3.11-slim python summarize.py
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p1-03-reasoning)


---


<a id="docker-p1-04"></a>

### docker-p1-04: Author and run a simple holdings image


<a id="docker-p1-04-concept"></a>

#### Concept


An image build records filesystem content and startup configuration. Copying the supplied app into an image and selecting its working directory makes runtime independent of a host bind mount. The build context limits which files are available to copy, and the startup command determines which process runs. A benign placeholder Dockerfile can build successfully while still lacking the assessed application.

WORKDIR sets the directory for subsequent relative paths, COPY adds build-context files, and CMD selects the default process. The app's path assumption means copied files and working directory must agree. Packaging the test alone or printing the expected text would bypass the application behavior. The independently supplied test and fixture output make that distinction reviewable. Build success establishes that instructions could be executed; only running the resulting image establishes its main process and actual app result.


#### Challenge


Replace the placeholder Dockerfile with a `python:3.11-slim` image, working directory `/app`, copied app files and default `summarize.py` command. Use your attempt root as the build context and keep the supplied application logic unchanged.

Build with `$DC_DOCKER_TAG`, inspect the actual image identifier, then run without a host app mount. Retain the build log and summary output. Explain how FROM, WORKDIR, COPY and CMD contribute to the packaged workload. The resulting image must contain the script and its CSV at paths the default command can use; a successful build alone does not establish that result.


#### Hint


<details>
<summary>Run the packaged app without relying on a host mount</summary>

The build context is the copied starter directory; COPY cannot read an arbitrary parent directory.

Read the app's relative CSV path and arrange the copied filesystem accordingly. Use the copied attempt as build context, not an unrelated parent folder. If output still says valid starter, the placeholder command remains. Inspect the build/run logs and image identity before assuming the engine used your latest Dockerfile.

</details>

#### Check


The authored image must emit the actual summary: six holdings and total market value 12,011,626.50. It must do so without mounting the host app directory, and its main process should exit successfully. Run the supplied local test as the independent fixture/application oracle, then retain the build log, actual image identifier and runtime output.

Explain how working directory, copied files and startup command jointly satisfy the app's path contract. A successful placeholder build, hard-coded echo or local-only Python result does not satisfy image packaging. Keep unavailable engine checks pending; direct source inspection remains useful but cannot establish built-image contents.

```bash
docker build --progress=plain -t "$DC_DOCKER_TAG" .
docker run --rm "$DC_DOCKER_TAG"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p1-04-reasoning)


---


<a id="docker-p1-05"></a>

### docker-p1-05: Prove repeatability and clean scoped resources


<a id="docker-p1-05-concept"></a>

#### Concept


Repeatability means a known package and input produce the stated result across executions. A mutable tag alone is weaker identity than the image ID because the tag can be rebuilt between runs. Two disposable runs from the same image should both print the six-holding fixture result and exit normally. Their writable layers are separate even though their package is shared.

Cleanup is also an ownership decision. Removing every container or pruning all images would interfere with other learners and erase useful evidence. The exercise names its own containers/tags and retains logs and identities before removal. A build cache or shared base image need not be deleted to finish the core. Repeatability here concerns this supplied app and fixture, not every external dependency or production deployment scenario.


#### Challenge


Run the finished image twice with `--rm`, recording the actual image ID and both outputs. Inspect its configured command and working directory. Explain whether changing `holdings.csv` on the host would change an already-built image.

Compare both runs with the independent fixture expectation. List this attempt's leftover containers and tag, retain the needed logs, then remove only those named resources when instructed. Keep the authored Dockerfile and local app test for review. Explain how image, container, writable layer and mount differ, and why rebuilding copied input differs from mounting a changed host file.


#### Hint


<details>
<summary>Compare actual image identity before cleaning named resources</summary>

Use docker image inspect v2-holdings:p1. Rebuilding is necessary for a copied input change.

Capture image identity before both runs so a rebuilt tag cannot masquerade as one package. Disposable execution removal handles its container but does not necessarily remove the image tag. List owned resources explicitly before cleanup. If a name or tag was shared accidentally, resolve ownership rather than invoking a broad prune.

</details>

#### Check


Both finished runs must produce the same six-holding total and successful exit from the same actual image identity. Retain outputs and identity before cleanup, and show that only your named resources were removed. The final Dockerfile remains reviewable and its local test still establishes the fixture expectation.

Explain why matching tags are weaker evidence than matching image IDs and why container removal differs from image/tag removal. A broad prune or deletion of another learner's resource fails the safe completion contract. The local verifier can check supplied app arithmetic without an engine, but image runtime repeatability stays pending unless the real build/run boundary was exercised.

```bash
docker image inspect "$DC_DOCKER_TAG"
docker run --rm "$DC_DOCKER_TAG"
docker run --rm "$DC_DOCKER_TAG"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p1-05-reasoning)


## Phase completion


Submit the simple Dockerfile and evidence showing image identity, container lifecycle, isolated filesystem, a bounded read-only bind mount and the actual six-holding application output. The printed summary must be six holdings with total market value 12,011,626.50, matching the supplied app's independent fixture check. A valid starter message is deliberately not that result. Retain repeated runs from the same image and explain why an exiting application can be successful without becoming a long-lived service.

Clean only the named exercise containers and tags, preserving another learner's resources and any evidence needed for review. The local app test can run without Docker and gives supporting expected-output evidence; the build/run/user/filesystem boundaries require a real engine. Mark unavailable engine or image-pull checks pending instead of treating a source Dockerfile as a built image. Foundation work is independent of Databricks access and does not replace the later Portfolio Analytics pipeline. Optional multistage work belongs to the independently prepared advanced phase.

---


## Optional stretch


The core completion standard is independent of optional work. No additional stretch is required in this phase; the next phase has an independently prepared entry baseline.

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Run an image and inspect the lifecycle

<a id="docker-p1-01-reasoning"></a>

<details>
<summary>Reasoning for docker-p1-01: Lifecycle state follows the main process</summary>

A zero-exit hello process is successful even though the container is stopped. Logs, exit status and actual identifiers establish that execution. Container removal and image removal affect different resources. Client installation is only a prerequisite, and this hello result is not evidence that the supplied app was packaged.

[Return to docker-p1-01](#docker-p1-01)

</details>

### Reasoning: Explore an interactive shell

<a id="docker-p1-02-reasoning"></a>

<details>
<summary>Reasoning for docker-p1-02: A writable layer is different from image or mounted persistence</summary>

The temporary file belongs to the first execution's writable layer and is absent in a fresh container from the unchanged image. Reusing the same execution or adding a volume would change that experiment. Interactive flags affect inspection, not kernel isolation. Record actual runtime observations separately from the author's host.

[Return to docker-p1-02](#docker-p1-02)

</details>

### Reasoning: Use a bounded bind mount

<a id="docker-p1-03-reasoning"></a>

<details>
<summary>Reasoning for docker-p1-03: Mount permissions and runtime paths protect different obligations</summary>

The selected host app path is readable in the container but deliberately not writable. The working directory makes its relative CSV lookup correct. Expected summary and expected write denial are complementary observations; a failure before mounting proves neither. Keep the host input unchanged and avoid broad mounts that would obscure the intended boundary.

[Return to docker-p1-03](#docker-p1-03)

</details>

### Reasoning: Author and run a simple holdings image

<a id="docker-p1-04-reasoning"></a>

<details>
<summary>Reasoning for docker-p1-04: Build and runtime output establish different steps</summary>

The Dockerfile must package the supplied script and fixture at a working directory that satisfies its relative lookup. A real run without a host mount proves those files are in the image. The placeholder is intentionally buildable but incomplete. Independent app output, image identity and selected logs prevent build success or echoed text from substituting for the authored packaging result.

[Return to docker-p1-04](#docker-p1-04)

</details>

### Reasoning: Prove repeatability and clean scoped resources

<a id="docker-p1-05-reasoning"></a>

<details>
<summary>Reasoning for docker-p1-05: Repeatability needs package identity and bounded ownership</summary>

Distinct executions can share the same immutable image ID and independent writable layers. Matching expected output from that identity demonstrates this bounded app result. Cleanup preserves evidence and removes only named owned resources, leaving shared bases and other learners intact. Local fixture tests supplement rather than replace the actual image build/run observations.

[Return to docker-p1-05](#docker-p1-05)

</details>
