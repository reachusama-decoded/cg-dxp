# Activity 7 — Docker practical

*Day 2 · Individual or pairs · 65 minutes*

In the dev container, work through `challenges/v1/01-docker-intro/README.md` sections 1 to 5: run an image, look inside, write the Dockerfile, build the image, run your image. Start before lunch, finish after it. Section 6, the 'try a variation' steps and the stretch list are for anyone with time.

**Produce**

- `docker run --rm portfolio-summary` printing the six-holding summary
- `mise run challenge:verify 01` showing PASS
- An answer to: why did the container stop, and what survives when you run a fresh one?

**Finished early?** Section 6 (tags); multi-stage builds; resource limits (`--memory`, `--cpus`); read the training repository's own Dockerfile and explain three lines of it; run the Compose demo in `demos/docker/compose/` and add a third, one-shot service that queries `db` by name and exits; or build and run the secure example in `common/glossaries/docker-secure-example/`.

**Debrief questions**

- What is the difference between the image, the running process and its writable files?
- What travels with the image, and what does not?
