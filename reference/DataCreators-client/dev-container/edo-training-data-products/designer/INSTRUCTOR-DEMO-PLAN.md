# Instructor-demo capture implementation plan

Status: partially implemented. The reusable system and four real local DuckDB stories were exercised on the authoring host on 7 October UTC / 8 October London; Docker and Astro UI pilots, connected routes and full acceptance remain pending. See ../instructor-demos/README.md and the root devc.md evidence index.
Created 5 October 2026. The main resume prompt is root devc.md in the authoring
repository. This plan also works when this runnable project is mounted alone.

## Objective and authority

Build a repeatable system that executes a short instructor teaching story,
verifies its intermediate outcomes and captures frames and recordings. Publish
the same observed sequence as a printed story and captioned video. Begin with
three real pilots, then the twelve stories in
[INSTRUCTOR-DEMO-CATALOGUE.md](INSTRUCTOR-DEMO-CATALOGUE.md).

Current challenges/v2 learner READMEs, manifests, starters and solutions are the
authority for task concepts and expected outputs. Existing instructor-demo
comments already associate demonstration prompts with task IDs. Reuse those
relationships. Do not author an unrelated parallel Docker/dbt/Airflow curriculum.
Inspect v1 only for an explicitly needed reference. Legacy numeric challenge
commands are not substitutes for version-explicit v2 commands.

Keep route identity explicit: a real DuckDB build inside the dev container is
valid DuckDB evidence; it does not prove a Databricks adapter run. A real
dag.test() is execution evidence; it does not prove Astro scheduler/UI integration.
Capture the actual supported classroom route and label it accurately.

## Repository and output layout to implement

Paths below are relative to the runnable project root. These are planned new
interfaces, not files or commands already implemented.

```text
instructor-demos/
  README.md
  schema/story.schema.json
  stories/<story-id>/story.yaml
  stories/<story-id>/actions.py        # only where an adapter action is needed
  stories/<story-id>/fixtures/         # small synthetic or source-bound fixtures
  theme/                             # shared type, color and spacing tokens
scripts/instructor-demos.py           # portable CLI entry point
scripts/instructor_demos/             # schema, runner, PTY/browser, export modules
tests/instructor_demos/               # behavior/assertion/export tests
.local/instructor-demos/<run-id>/     # ignored workspaces, raw output and sessions
designer/reviews/instructor-demos/<run-id>/
  environment.json
  capture-manifest.json
  results.json
  resource-ledger.json
  review.md
```

Reviewed distribution assets should be exported into a candidate bundle, not
mixed with credentials, browser storage, generated databases or raw logs. Large
video files belong in ignored capture/candidate output; maintained stories,
fixtures, locks and sanitized review manifests belong in source control.

The current course checkout builds with `./build-pdf` (`./build-pdf doctor` checks it); no separate CwBuilder checkout is required. Older CwBuilder references below describe design history, not a current prerequisite.

## P0 — Discover and prepare the live environment

1. Discover CLIENT_ROOT from .mise.toml and scripts/challenge-v2.py. Record the
   current source revision/dirty state, task inventory and source hashes. Locate
   COURSE_ROOT and CWBUILDER_ROOT if mounted; all three roots are independent.
2. Inspect .devcontainer/README.md, devcontainer.json, GETTING_STARTED.md,
   .mise.toml, actual runtime configuration and the challenge's prerequisites.
   The supplied container uses a workspace under /workspaces/, an internal Docker
   daemon and persistent Docker data. Probe actual behavior rather than assuming
   a forwarded desktop port or authoring-host path.
3. Check actual Docker client/server/context and Compose, dbt/adapters, Astro,
   Airflow, Databricks CLI/profile and browser availability. Existing source pins
   differ between the main client runtime and v2's isolated teaching environments.
   Record versions in each execution boundary, including worker containers.
4. Inspect current commands before running them. Existing discovery entry points
   include `python3 scripts/challenge-v2.py --help` and
   `python3 scripts/challenge-v2.py list`. Prepare/verify the relevant v2 phases
   using their documented interface and fresh explicit workspaces.
5. Resolve named training resources from the environment/instructor assignment.
   Build an owned-resource ledger and keep every intentional failure in a
   disposable copy. Capture dependencies use a separate project-local environment
   and pinned browser installation. Preserve the managed interpreter and locks.
6. Identify actual addresses visible to the capture browser and actual mount paths
   visible to dbt/Astro workers. Validate them with a real lightweight probe.
   Do not assume localhost inside a worker points to the dev-container service.

Readiness emits per-capability statuses, not one all-or-nothing flag. Missing
Databricks access can block connected stories while Docker capture continues.
No live execution is asserted by the creation of this plan.

## P1 — Define the story and capture contracts

A story has an ID/title, objective, tool/task/concept links, audience/prerequisites,
route/runtime requirements, source inputs, ordered actions and checkpoints,
caption text, closing question, main-book selection and suggested teaching anchor.
Use explicit schema versions and reject unknown fields or duplicate IDs.

Illustrative contract; implement and validate the final schema before treating
this example as executable:

```yaml
schema_version: 1
id: docker-image-to-shell
title: From an image to a shell inside a container
objective: Distinguish the downloaded image from the container executing commands.
tool: docker
task_ids: [docker-p1-01, docker-p1-02]
route: devcontainer-docker
requires: [docker-client, docker-server, image-registry]
main_book:
  include: true
  teaching_key: docker-images-and-containers
steps:
  - id: pull
    action:
      adapter: terminal
      session: developer
      command: docker pull python:3.11-slim
    expect:
      exit_code: 0
      assertion: local-image-resolves-to-recorded-digest
    capture:
      context: DEV CONTAINER TERMINAL
      focus: command-and-image-result
    caption:
      action: Download the Python image.
      notice: The image is local; this command has not started a container.
closing_question: What changes when you start two containers from the same image?
```

The complete schema must also support terminal input/control keys, browser
navigation/clicks, application/API assertions, file/database checks, intentional
failures, focus locators, detailed crops, caption hold time and cleanup. Assertions
have documented registered handlers; do not evaluate arbitrary strings from YAML.
Terminal session names are explicit so a container shell is not accidentally
replaced by a fresh host process at the next step.

Each checkpoint record contains story/step IDs, action and observation times,
actual exit/state result, assertion evidence, runtime/route, source/config hashes,
full raw capture hash, selected-frame hash, crop/locator, dimensions, caption and
video time range. Record image tags AND observed immutable digests. Subsequent
captures of a mutable tag must not silently reuse old evidence.

## P2 — Execute, assert and capture

### Terminal adapter

Use a real PTY so interactive Docker shells, prompts, ANSI output and terminal
state work. Bridge it to a local browser terminal surface, such as xterm.js, for
consistent screenshots and recording. Preserve actual ordered output and input
events as a replayable transcript. Command completion should be established by
exit status/session markers and assertions, not matching any visible dollar sign.

Send actual input to the PTY. Optional typing animation may delay real keystrokes
or replay the recorded input; it must not invent outputs or hide failed actions.
Keep raw execution and edited playback distinguishable. Publish a plain-text
transcript and exact copyable commands alongside visual assets.

The existing CwBuilder terminal renderer executes scripts that may print a faux
session and emits one image. Reuse its styling/caching ideas where useful; it is
not an interactive capture adapter. Its single-image output and authoring layout
also do not directly implement this runnable project's story contract.

### Browser adapter

Use Playwright against the actual dbt docs/Airflow UI. Authenticate outside the
recording and keep browser storage private. Prefer accessible locators and real
application state/API checks to fragile screen coordinates and fixed sleeps.
Capture the graph, relevant table, dialog or log region, with enough surrounding
context to identify the view. Preserve the original capture and the selected crop.

Do not replace real application state with edited DOM success labels or mock
responses. Presentation overlays are separate annotations, clearly instructor
authored, and must not cover the evidence being explained.

### Stable capture and recording

- Start in a fresh story workspace. Declare intentional cache state; do not
  clear the learner's shared Docker cache merely to show a download animation.
- Wait for verified state and a settled screen; use separate configurable pacing
  for video. State waits and learner reading pauses have different purposes.
- Use logical viewport/font sizes that remain readable when printed. A terminal
  around 1000 logical pixels wide with approximately 20 px text is a useful
  pilot; 2x capture sharpens it. Device pixel ratio alone does not enlarge type.
- Keep an unedited recording where practical. Produce the teaching edit using
  checkpoint timings; label compressed download/wait sections. Compose terminal
  and UI segments in story order rather than pretending they share one browser.
- Export WebM initially; add MP4 through a pinned available encoder where needed.
  Generate WebVTT subtitles and chapter timings from the same caption data.
  Native Playwright video recording does not supply instructor voice narration;
  audio is an optional separate future input.
- Keep login/token screens and sensitive values out of published frames. If a
  frame requires sanitization, preserve its raw/private original and a recorded
  redaction transform; do not modify pedagogical outcomes.

Always distinguish DEV CONTAINER TERMINAL, DEMO CONTAINER and ASTRO WORKER/UI.
Calling the developer terminal HOST is misleading when it is itself a container.

## P3 — Pilots, reuse and verification

Complete Docker image-to-shell, dbt build/output and Airflow run/log pilots. Then
complete a controlled failure/repair pilot and review print/video output before
scaling to the catalogue. Reuse real v2 fixtures and independent output oracles;
bind instructor solution use explicitly to the instructor route.

Extend missing connected verifier routes when required. A new screenshot runner
must not simply trust a central verifier that currently returns blocked or only
establishes a local execution boundary. Record actual run/task IDs and fresh
outputs; pre-existing green tasks are not proof of this capture run.

Test the consequential contracts: persistent interactive shell state, stale
evidence rejection after a source change, expected-failure reason, downstream
publication blocked, wrong-workspace output rejected, failed prerequisite status,
and cleanup after interruption. Use small deterministic fixtures for runner tests,
then actual tool acceptance runs. Do not mirror implementation line-by-line.

Plan a CLI supporting `doctor`, `list`, `validate`, `capture`, `review`, `export`
and `check`, with explicit root/story/run/output options and help. A dry run must
show planned actions/resources without executing them. Document commands only
after implementing and exercising them. Ordinary publishing consumes reviewed
assets; it must not start live jobs or re-run every capture automatically.

Cache rendering by capture hashes, caption/theme/schema versions and render
configuration. Capture reuse additionally binds source inputs, environment/route
and observed external identities. Environment changes require an explicit
revalidation decision; a story YAML hash alone cannot prove freshness.

## P4 — Export and hand off

Export a portable reviewed bundle containing relative asset paths, final story
data, selected frames, transcripts, videos/subtitles, checksums and sanitized
execution evidence. Exclude raw client data, browser storage, credentials,
databases, unrelated logs and stale frames. Include task/source hashes and route.

The course publisher consumes this bundle using the separate
[publishing plan](../../../../../designer/INSTRUCTOR-DEMO-PUBLISHING-PLAN.md)
when the full authoring checkout is mounted. If it is absent, retain the bundle
and source patch plus course-handoff.md; capture success is not course-build success.

Acceptance requires real pilots, the available catalogue, reusable documented
code, accurate route/blocked status, readable reviewed frames, captioned playback,
detected drift and owned-resource cleanup. Report every missing story/route.
No capture or publication is completed merely by authoring these plans.
