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
