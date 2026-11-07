# Activity 7 — Docker practical

*Day 2 · Individual or pairs · 35 minutes*

In the dev container, work through `challenges/v1/01-docker-intro/README.md` sections 1 to 5: run an image, look inside, write the Dockerfile, build the image, run your image. Section 6 and the 'try a variation' steps are for anyone with time.

**Produce**

- `docker run --rm portfolio-summary` printing the six-holding summary
- `mise run challenge:verify 01` showing PASS
- An answer to: why did the container stop, and what survives when you run a fresh one?

**Finished early?** Multi-stage builds, resource limits (`--memory`, `--cpus`), or read the training repository's own Dockerfile and explain three lines of it.

**Debrief questions**

- What is the difference between the image, the running process and its writable files?
- What travels with the image, and what does not?
