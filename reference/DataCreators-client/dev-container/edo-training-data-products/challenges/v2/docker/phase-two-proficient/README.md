# docker: Phase 2 — advanced practice

## Purpose and outcome

Design a bounded multistage image for the supplied summary app. Advanced work separates test and execution concerns, selects named targets deliberately, runs with a suitable user and diagnoses a real path assumption. You author Docker configuration and evidence; the app and expected fixture result remain supplied so the focus stays on runtime boundaries.

## Dataset and pipeline

The advanced copy contains the same six-holding app fixture and independent test as foundation practice. Its expected total is 12,011,626.50. This app dataset is distinct from the assigned Databricks Portfolio Analytics and CG product sources. A build stage supplies files, a named test target executes the oracle, and a runtime target includes only the app/input needed for execution. The exact stage graph determines whether runtime receives a tested artifact and what a target build actually executes.

The app resolves its CSV from the current working directory. A deliberately wrong copy destination or directory can therefore make a perfectly built image fail at runtime. The named targets and actual filesystem/user inspections provide evidence that cannot be replaced by reading FROM, USER or COPY text alone.

## Prerequisites and workspace

Prepare an independent advanced attempt through mise from the training project root. Use the delivered engine and prepared base image, then choose distinct test/runtime tags for your attempt. The advanced starter includes app/test inputs without requiring your completed foundation Dockerfile. Work from the copied root so build context and relative source paths are unambiguous.

```bash
mise run challenge:v2:prepare docker phase-two-proficient
cd .local/challenges-v2/docker/phase-two-proficient
export DC_DOCKER_TEST_TAG=dc-alex-docker02:test
export DC_DOCKER_RUNTIME_TAG=dc-alex-docker02:runtime
```

Record actual engine/base identities before comparing builds. Non-root identity and file permissions should be tested in a real container; source configuration only states intent. Avoid privileged options, broad host mounts and global image pruning. Engine access and image pulls belong to preparation outside the unpiloted task estimate. If unavailable, continue Dockerfile review and the local app oracle while leaving actual target/user/filesystem checks pending.

## Starter behavior

The copied Dockerfile still prints a benign placeholder and has no completed multistage outcome. A successful starter build is deliberate but cannot pass the finished target checks. Both app and Python oracle work from their supplied directory. You must author named test/runtime targets, meaningful test execution, required non-root user and focused runtime contents. The path defect is introduced later in a disposable version after a working baseline, so an initial missing engine or image is not its intended failure. Preserve a known working Dockerfile before the drill.

## Timeline and completion standard

Core reading, authoring, checking and explanation: 75–110 minutes. Allow additional time for setup and optional stretch.

| Task | Minutes | Evidence |
| --- | --- | --- |
| [docker-p2-01: Separate named build targets](#docker-p2-01) | 15–22 | Actual target image IDs and expected target outputs |
| [docker-p2-02: Gate the runtime on a tested artifact](#docker-p2-02) | 15–22 | Test failure blocks accepted runtime artifact path; repaired test/app succeeds |
| [docker-p2-03: Run with a bounded runtime user](#docker-p2-03) | 15–22 | Runtime UID 10001; app reads intended files and still prints expected summary |
| [docker-p2-04: Keep runtime contents focused](#docker-p2-04) | 15–22 | Required app/input present; test script absent; expected output preserved |
| [docker-p2-05: Repair a path assumption and explain the result](#docker-p2-05) | 15–22 | Predicted missing-file failure followed by repaired expected output and explanation |

## Core challenges


<a id="docker-p2-01"></a>

### docker-p2-01: Separate named build targets


<a id="docker-p2-01-concept"></a>

#### Concept


A multistage file defines a dependency graph of named build stages. Selecting one target chooses the output image and the stages it depends on; it does not automatically publish every intermediate stage as a separate tagged image. The test target and runtime target therefore need deliberate build/tag commands when both are review artifacts.

Named stages also communicate purpose. A runtime target should contain the executable app/input, while a test target can retain the independent test script and its command. The source file alone cannot show which target an actual build selected or whether a cached stage was reused. Record command, target and resulting image identity so a reviewer can connect intended architecture with observed output.


#### Challenge


Create named `base`, `test` and `runtime` stages in the Dockerfile. The test target runs `test_summary.py`; runtime runs `summarize.py`. State their dependency relationship and how tested app/input reaches runtime.

Build test with `$DC_DOCKER_TEST_TAG` and runtime with `$DC_DOCKER_RUNTIME_TAG`. Inspect both resulting image IDs and run the targets separately. Keep the selected target explicit in each command so a default final-stage build cannot stand in for two outputs. Retain the commands and explain which prerequisite stages each target used. Check that the named stages match the verifier's expected interface.


#### Hint


<details>
<summary>Target selection follows the stage graph, not every FROM line</summary>

Use FROM ... AS name and COPY `--from`=test for the selected runtime artifacts.

Draw the small stage dependency graph before writing COPY references. A target flag chooses an output, while a tag names the resulting image. Inspect the actual selected stage command and runtime output to distinguish a test image from an app image. If a stage is unreachable from the selected target, its existence in source is not proof it ran.

</details>

#### Check


The test and runtime target builds must produce identifiable separately tagged images. Running test must emit the supplied oracle success, and running runtime must emit the six-holding summary. Retain both target commands, image IDs and outputs, explaining which stages each depended on.

A default final-stage build alone does not prove the separate test image exists or executed. An echoed success string also does not replace the supplied test behavior. If the engine cannot run here, leave build/target observations pending while preserving a source graph that can be inspected. The finished verifier builds the named targets, not arbitrary intermediate indexes.

```bash
docker build --target test -t "$DC_DOCKER_TEST_TAG" .
docker build --target runtime -t "$DC_DOCKER_RUNTIME_TAG" .
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p2-01-reasoning)


---


<a id="docker-p2-02"></a>

### docker-p2-02: Gate the runtime on a tested artifact


<a id="docker-p2-02-concept"></a>

#### Concept


A testing stage is useful when it validates the artifact that runtime receives. An unrelated test command in an unreachable stage can look reassuring while providing no gate. The stage graph should connect the tested app/input to the runtime copy path, and a build-time assertion or equivalent explicit workflow should reject an incorrect artifact before acceptance.

The supplied Python test computes the fixture expectation independently of a hard-coded echo. The tiny app's baseline result is fixed, so a controlled copied input or app-path defect should make that assertion fail. Keeping the test's purpose visible prevents a Dockerfile from satisfying advanced work merely by naming a stage test. The runtime output remains a separate observation after the test succeeds.


#### Challenge


Add `RUN python test_summary.py` to the test stage. Wire runtime's COPY or inheritance path to the same app/input that the test validates. Build the valid target and retain its success.

In a separate copied build context, change one holding amount by a known value and predict the oracle failure. Rebuild, inspect the failed assertion, then restore the fixture and rebuild both targets. Keep the working Dockerfile available throughout. Do not suppress the nonzero test result or alter the expected baseline total. Explain why the tested artifact is the one the runtime receives.


#### Hint


<details>
<summary>Trace runtime content back to the actual oracle boundary</summary>

Keep the original workspace intact; make the controlled defect in a second copied build context.

Trace the exact file source of the runtime COPY back to the tested stage. If the test runs only as an optional container command, describe how acceptance enforces it rather than pretending the build itself is gated. Avoid appending an unconditional success echo after a failed assertion. Use the supplied test's expected result to diagnose the copied artifact cause.

</details>

#### Check


The valid test target must execute the real supplied summary test, and the finished runtime must use the corresponding tested app/input. The controlled incorrect artifact must be rejected for the predicted oracle or path reason; restore it and retain a successful test/runtime sequence. Record stage graph, command exit categories and actual identities.

Explain the difference between a stage named test and an enforced test boundary. A compiler/source inspection cannot establish the rejection transition. Keep source fixtures unchanged outside the disposable copy, and do not loosen the expected total merely to accept a broken artifact. Any unavailable engine execution remains pending rather than a source-only pass.

```bash
docker run --rm "$DC_DOCKER_TEST_TAG"
docker run --rm "$DC_DOCKER_RUNTIME_TAG"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p2-02-reasoning)


---


<a id="docker-p2-03"></a>

### docker-p2-03: Run with a bounded runtime user


<a id="docker-p2-03-concept"></a>

#### Concept


A runtime user changes the process's permission boundary, not the meaning of the app. The image should provide readable app/input files and an appropriate working directory for the declared non-root identity. A USER line can name an identity that lacks the necessary file access, so inspect actual UID and execute the app rather than trusting the Dockerfile keyword.

The expected training runtime UID is 10001. Its app only needs read access to the packaged fixture; adding broad writable host mounts or privileged flags would change the exercise boundary. An image can build under root while its final process runs non-root, because build and runtime identities are separate. That distinction should be visible in the explanation and actual command output.


#### Challenge


Create runtime UID 10001, give it the required read access to the packaged script/input, and set `USER 10001`. Use explicit ownership when copying from the test stage. Build runtime, inspect `id -u` inside it and run the default summary.

Retain both observations from the same image ID. If execution fails, distinguish a missing path from a file-permission error and repair only that cause. Confirm the process can read the app and fixture without privileged flags or a writable host mount. Explain which build steps used another identity and why runtime does not need root.


#### Hint


<details>
<summary>Prove actual runtime identity together with useful app access</summary>

COPY `--chown` can set ownership while copying from a named stage.

Inspect identity and file permissions as separate observations. The build's default user does not prove the final process's user. Read-only app access is sufficient for this fixture. If a file exists but cannot be read, diagnose its path and mode before changing the whole container security boundary.

</details>

#### Check


The finished runtime must report UID 10001 and still emit six holdings with total market value 12,011,626.50. Retain the identity probe and application run from the same image ID. Explain which build steps ran under another identity and how packaged file access supports the final process.

A USER declaration without successful execution is insufficient, and a successful app run forced back to root fails the stated runtime contract. Do not add broad write permissions or host mounts to conceal a packaging defect. The source may be reviewed locally, but actual UID and access observations require a real container engine.

```bash
docker run --rm "$DC_DOCKER_RUNTIME_TAG" id -u
docker run --rm "$DC_DOCKER_RUNTIME_TAG"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p2-03-reasoning)


---


<a id="docker-p2-04"></a>

### docker-p2-04: Keep runtime contents focused


<a id="docker-p2-04-concept"></a>

#### Concept


A focused runtime image contains what the executable needs, not every file available during build. The independent test is useful for acceptance but not required by the summary process. Copying the whole test stage can retain unnecessary scripts or temporary files. Narrow COPY decisions make the runtime boundary easier to inspect and reduce accidental content exposure.

Smaller size alone is not correctness: deleting the input CSV can shrink the image while breaking the app. The appropriate evidence combines required content presence, test-script absence and expected runtime behavior. Build/cache files and runtime files serve different roles. The exercise does not claim a production security audit from this small content check, but it teaches deliberate artifact selection.


#### Challenge


Copy only `summarize.py` and `holdings.csv` into runtime. Inspect `/app` in both targets and confirm `test_summary.py` is absent from the final runtime image. Compare their configured users, commands and sizes.

Run the summary after any COPY-path change and tie the filesystem inspection to that same image ID. Explain why each retained file is needed and why image size is only supporting information. A smaller image that lacks its CSV has not met the app contract. Inspect the final stage rather than assuming a narrow COPY statement produced the image your tag currently names.


#### Hint


<details>
<summary>Inspect the final filesystem and keep required behavior intact</summary>

Override the runtime command with ls or python -c when inspecting.

Inspect the final stage rather than a test-stage shell. Copying an entire directory may carry the test script even when no command executes it. Pair absence checks with app output so a missing required file cannot pass as a lean runtime. Use explicit source/destination paths rather than an unexplained broad directory copy.

</details>

#### Check


The runtime filesystem must exclude the supplied test script while retaining the app and holdings input at the expected paths. Its non-root process must still print the independent six-holding summary. Retain filesystem inspection and output tied to the actual runtime image ID.

Explain why an image-size comparison alone cannot establish focused contents or useful behavior. A source COPY statement is insufficient if actual execution uses another image/tag. Keep build/test stage evidence separate from runtime inspection. If an engine is unavailable, record the intended file inventory and leave its actual absence/presence assertions pending.

```bash
docker run --rm "$DC_DOCKER_RUNTIME_TAG" python -c "from pathlib import Path; assert not Path('/app/test_summary.py').exists()"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p2-04-reasoning)


---


<a id="docker-p2-05"></a>

### docker-p2-05: Repair a path assumption and explain the result


<a id="docker-p2-05-concept"></a>

#### Concept


Runtime path failures often come from an inconsistent relationship among build context, COPY destination and working directory. The summary opens its CSV by relative name. Moving its execution directory or copying that input elsewhere can cause a missing-file error even though the image built successfully. The diagnosis should identify that relationship rather than modify business data or install unrelated dependencies.

A controlled defective Dockerfile creates a useful before/after experiment after a known good baseline exists. The build can remain valid while the process fails, demonstrating the distinction between build-time and runtime checks. Repairing the minimal path assumption and rerunning the same fixture establishes recovery. Keep the defect out of the final image and retain evidence before cleaning owned tags.


#### Challenge


Save the working multistage Dockerfile. In a disposable copy, change runtime's WORKDIR to `/wrong` and predict how the default command will fail. Build and run the defective target, then inspect its configured directory and packaged paths.

Repair the path and repeat both target checks. Retain the failure, minimal Dockerfile diff and repaired summary from identifiable images. Confirm the fix preserves test gating, UID 10001 and the absence of `test_summary.py` from runtime. Write a short handoff explaining why the image built successfully but failed when its default process ran. Keep optional cache analysis separate.


#### Hint


<details>
<summary>Repair the path contract instead of bypassing the application</summary>

Inspect the image configured working directory and run a listing before editing Python code.

Follow the CSV path from the app source to final COPY destination and process working directory. A missing-file error differs from a read-permission failure. Change one assumption at a time and keep the known-good version available. Do not add a broad host mount or hard-code the expected output to make the defective container appear recovered.

</details>

#### Check


The controlled runtime failure must match the predicted path/entrypoint cause, and the repaired image must again emit the six-holding total with UID 10001 and no packaged test script. Retain failing and repaired command/category, bounded Dockerfile diff and actual image IDs. Explain why build success did not catch this runtime assumption.

Recheck both named targets after repair so a path fix cannot bypass the test boundary. Clean only owned tags/executions after preserving evidence. A missing engine or base-image download is not the intended defect, and local Python success does not prove repaired image behavior. Leave those actual runtime observations pending if they cannot run here.

```bash
docker build --target runtime -t "$DC_DOCKER_RUNTIME_TAG" .
docker run --rm "$DC_DOCKER_RUNTIME_TAG"
```


<!-- variation: none; use the separately scoped phase stretch after core completion. -->

[Phase contents](#core-challenges) · [Reasoning key](#docker-p2-05-reasoning)


## Phase completion


Finish a reviewable multistage Dockerfile with separately buildable test and runtime targets. The test target must run the supplied independent summary test, while the runtime target must emit six holdings and total market value 12,011,626.50. Inspect actual runtime user and filesystem to prove the declared non-root identity and absence of the test script. Retain a controlled working-directory/copy-path defect and its repaired output rather than relying on Dockerfile keyword inspection.

Explain the selected target dependency graph, why a tested artifact reaches runtime, and which files belong to build/test versus execution. Use owned tags/names and clean only this attempt's resources after retaining image identities and logs. A local Python test establishes fixture arithmetic but does not prove image stage, user or filesystem behavior. Mark engine/image-build evidence pending when unavailable. Optional cache/size analysis can follow the fixed core with its own estimate, but it cannot replace the test, runtime, identity and repair outcomes.

---


## Optional stretch


The core completion standard is independent of optional work. Choose a separately timed route from [the stretch guide](stretch/README.md).

---


## Reasoning keys


Read these explanations after attempting the checks.

### Reasoning: Separate named build targets

<a id="docker-p2-01-reasoning"></a>

<details>
<summary>Reasoning for docker-p2-01: Separate outputs require deliberate target builds</summary>

Named stages describe dependency and purpose. Selecting runtime does not automatically tag every stage, so retain explicit test/runtime builds and actual image IDs. Their commands produce different expected outputs. Source stage declarations are useful review evidence but cannot substitute for real target execution or an actual oracle run.

[Return to docker-p2-01](#docker-p2-01)

</details>

### Reasoning: Gate the runtime on a tested artifact

<a id="docker-p2-02-reasoning"></a>

<details>
<summary>Reasoning for docker-p2-02: The test must validate the artifact runtime actually uses</summary>

The meaningful gate is the supplied oracle executed on the same app/input passed to runtime. A disconnected stage or unconditional success message does not establish it. The bounded defective artifact should fail for its intended reason, and restoration should recover the expected summary. Build-time gating and an explicit separate acceptance test need truthful distinction.

[Return to docker-p2-02](#docker-p2-02)

</details>

### Reasoning: Run with a bounded runtime user

<a id="docker-p2-03-reasoning"></a>

<details>
<summary>Reasoning for docker-p2-03: Build identity and runtime identity are different boundaries</summary>

The finished process must actually run as UID 10001 while reading the correctly packaged app/input. Build steps may use another identity. Source USER text states intent, while identity plus successful output proves the runtime boundary. Minimal file access is the proper repair; root or privileged execution would bypass the assessed contract.

[Return to docker-p2-03](#docker-p2-03)

</details>

### Reasoning: Keep runtime contents focused

<a id="docker-p2-04-reasoning"></a>

<details>
<summary>Reasoning for docker-p2-04: Focused content requires both absence and functioning presence</summary>

The runtime does not need the test script, but it does need the summary and input. Actual final-stage inspection plus expected output establishes both sides of that boundary. Size or source COPY text alone can conceal missing required content or accidental test material. Tie the observations to the same runtime identity.

[Return to docker-p2-04](#docker-p2-04)

</details>

### Reasoning: Repair a path assumption and explain the result

<a id="docker-p2-05-reasoning"></a>

<details>
<summary>Reasoning for docker-p2-05: A minimal causal repair preserves the other runtime promises</summary>

The app's relative input lookup links COPY path and working directory. A valid build can still fail that runtime contract. The controlled defect and minimal repair must preserve test gating, non-root identity and focused contents. Actual failure/recovered output and image IDs establish the transition; host mounting or echoed output would bypass it.

[Return to docker-p2-05](#docker-p2-05)

</details>
