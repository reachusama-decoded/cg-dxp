# docker optional stretch


Choose an optional exercise after the advanced core. Allow 20–40 minutes for each and use a fresh copy of your completed baseline. Keep the assessed attempt unchanged.


## Optional exercises


<a id="docker-stretch-01"></a>

### docker-stretch-01: Explain cache reuse and a controlled input rebuild


<a id="docker-stretch-01-concept"></a>

#### Concept

Build cache can reuse a stage whose relevant inputs and instructions have not changed. The observed rebuild log, selected target and actual resulting image determine what was reused; merely running the same command twice does not prove every stage executed again. A mutable tag can hide that distinction because it can point to a new image after a rebuild.

The supplied six-holding input provides a bounded invalidation experiment. Changing one copied CSV value can affect the application layer and expected summary without requiring an unrelated service stack. Keep that variation separate from the fixed core baseline and calculate its expected total independently. Image size alone cannot establish correctness or cache behavior. The useful explanation identifies the input boundary, affected build stage and actual output.

#### Challenge

Preserve a working completed Dockerfile and perform two builds with unchanged input, retaining plain build logs and image identifiers. In a separate copied variation, change one holding value by a known amount, predict the new total through an independent CSV calculation, and rebuild the selected runtime target. Inspect which stages reused cache and which consumed the changed input. The fixed baseline assertion should now fail. In this optional copy only, replace its expected total with your independently calculated variation total, label that test as variation-specific, and rebuild. Run the resulting image and compare its actual summary with the predicted variation. Restore the copied baseline afterward without loosening the fixed core oracle.

Record the copied input delta before rebuilding and name the specific layer whose changed content should invalidate reuse.

#### Hint

<details>
<summary>Trace the changed input to its COPY boundary</summary>

Compare the stage logs rather than only elapsed time. A fast network or already pulled base can make a build faster without the specific layer reuse you intend to explain. Trace the changed CSV to its COPY boundary. Preserve the original input hash and total so the variation cannot be mistaken for the assessed baseline. A changed tag name alone does not invalidate the relevant content.

</details>

#### Check

Retain unchanged and changed build logs, actual image IDs, input hashes and runtime summaries. The changed result must differ by the independently predicted amount while still containing six holdings; restoration must recover the baseline 12,011,626.50 result. Explain which input/stage boundary produced the observed reuse or invalidation.

Retain the original core test's rejection of the changed fixture and the separate variation-specific test result. Keep the assessed baseline test unchanged. Source inspection or duration alone cannot prove cache reuse. Use the actual engine when available and mark those observations pending otherwise. Clean only the optional experiment tags after preserving evidence, leaving the completed core image and another learner's resources intact.

<!-- variation: none; this entire exercise is optional and separately timed. -->

[Optional contents](#optional-exercises) · [Reasoning key](#docker-stretch-01-reasoning)

---


<a id="docker-stretch-02"></a>

### docker-stretch-02: Run the prepared app through bounded Compose configuration


<a id="docker-stretch-02-concept"></a>

#### Concept

Compose describes a local multi-container application configuration, but a single supplied app can also demonstrate its project/name and command boundaries. The optional experiment should not introduce a database, broker and web service merely to look more advanced. The same packaged summary and its read-only input can establish a useful configuration comparison.

Project identity scopes names and cleanup. A Compose file in source does not prove the selected service image, runtime user or working directory actually ran. The core Dockerfile remains the artifact under test, while Compose selects and starts its local execution. A service that finishes a batch summary can exit successfully; forcing it to stay alive would change the behavior. Retain the expected app result and owned project boundary.

#### Challenge

Author a small Compose configuration for the completed summary image, with an explicit owned project name and the required runtime path/input contract. Inspect the resolved configuration, execute only that supplied batch service and retain its logs/exit result. Compare it with the direct docker run outcome. If you explore a read-only mount, keep it limited to the copied app directory and explain how it changes packaging assumptions. Remove only this optional Compose project after collecting evidence.

Keep the resolved configuration and its project name beside the actual service result so the observed runtime can be reproduced.

#### Hint

<details>
<summary>Inspect the resolved service before starting it</summary>

Inspect the installed Compose help and resolved service definition before startup. Compare selected image, working directory, user and mount with the direct runtime contract. A completed batch service need not remain running. Keep project cleanup bounded; a global prune is unrelated to this optional configuration exercise. Do not require an extension-specific renderer to understand the Compose YAML.

</details>

#### Check

The resolved configuration and actual service execution must preserve the expected six-holding total, intended user and bounded filesystem access. Retain project/service identity, selected image ID, exit category and logs. Explain what Compose changed about orchestration/configuration and what remained the same application behavior.

A parsed YAML file alone is supporting evidence. Actual startup and cleanup need the prepared engine, and unavailable runtime stays pending. Do not introduce external infrastructure or another mandatory course dependency. After owned project removal, the completed core Dockerfile and evidence remain intact. The optional route has its own estimate and cannot replace the core multistage/test/user/path checks.

<!-- variation: none; this entire exercise is optional and separately timed. -->

[Optional contents](#optional-exercises) · [Reasoning key](#docker-stretch-02-reasoning)

---


## Reasoning keys


<a id="docker-stretch-01-reasoning"></a>

<details>
<summary>Reasoning for docker-stretch-01: Cache observations need logs and checked output</summary>

The build log identifies cached stages; runtime output checks the result of the changed input. A data-only COPY change should invalidate stages that depend on it while earlier unchanged work can be reused. The fixed core oracle may reject the changed fixture intentionally. Restore the baseline and its expected total before final cleanup.

[Return to docker-stretch-01](#docker-stretch-01)

</details>

<a id="docker-stretch-02-reasoning"></a>

<details>
<summary>Reasoning for docker-stretch-02: Configuration selects an execution of the same app</summary>

Compose selects the image and execution configuration for the same batch app. Its project name scopes resources, while the resolved service shows user, command, path and mounts. A successful summary can exit normally. Compare actual logs and image identity with the direct run to establish that the configuration preserved the app contract.

[Return to docker-stretch-02](#docker-stretch-02)

</details>
