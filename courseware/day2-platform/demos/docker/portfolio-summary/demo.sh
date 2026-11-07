#!/usr/bin/env bash
# Day 2 Docker demo, in the same order as the learners' challenge 01 (run, look inside,
# Dockerfile, build, run, tag). Uses the `docker` CLI; Docker Desktop must be running.
set -euo pipefail
cd "$(dirname "$0")"
step() { printf '\n\033[1;34m== %s ==\033[0m\n' "$*"; }
step "1. Run an image: Python from inside a container, not from this laptop"
docker run --rm python:3.11-slim python --version
step "2. Look inside: its own Linux filesystem; a file written here is gone in the next container"
docker run --rm python:3.11-slim bash -c "cat /etc/os-release | head -1 && touch /tmp/proof.txt && ls /tmp"
docker run --rm python:3.11-slim ls /tmp
step "3. The Dockerfile: FROM, WORKDIR, COPY, CMD"
grep -E '^(FROM|WORKDIR|COPY|CMD)' Dockerfile
step "4. Build the image (run it twice to show the cache)"
docker build -t portfolio-summary .
docker build -t portfolio-summary . 2>&1 | grep -E 'CACHED|DONE' | head -5 || true
docker images portfolio-summary
step "5. Run your image: the app, Python and the OS libraries travel together"
docker run --rm portfolio-summary
step "5b. Same image, different data: mount a CSV over the one baked in"
docker run --rm -v "$PWD/app/holdings.csv:/app/holdings.csv:ro" portfolio-summary
step "6. Tag a version: two names, one image ID"
docker tag portfolio-summary portfolio-summary:v1
docker images portfolio-summary
step "Cleanup hint (not run): docker rmi portfolio-summary:v1 portfolio-summary"
