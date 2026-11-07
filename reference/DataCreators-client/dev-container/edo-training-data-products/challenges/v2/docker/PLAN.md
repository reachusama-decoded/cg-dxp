# Docker route: v2 plan (uplift of v1 Challenge 01)

## At a glance

| | |
|---|---|
| **v1 source** | [v1/01-docker-intro](../../v1/01-docker-intro/README.md), "Docker, hands-on: wrap a script in a container" |
| **Target folder** | `challenges/v2/01-docker-intro/` (rename of this `docker/` folder) |
| **App / data** | Same as v1: `starter/app/summarize.py` and `starter/app/holdings.csv`. Goal output `Portfolio summary` / `6 holdings, total market value 12,011,626.50` |
| **Phase 1 — Certified** | `phase-one-certified`, target **~1 h** (tool primer). v1's six sections **plus** a bind-mount section and a change-data/rebuild/clean-up section |
| **Phase 2 — Proficient** | `phase-two-proficient`, target **~45 min**. v1 has no Phase 2; add 2 challenges that connect the lab to the repo's real Astro image used in Challenge 03 |
| **mise** | `mise run challenge:verify 01 --phase 1\|2`, `mise run challenge:reset 01 --phase 1\|2`, plus a new `mise run challenge:docker-clean 01` |
| **Current v2 content dropped** | The "Valid starter" echo `CMD`, the generated task cards, `.local/challenges-v2` copies, and the five-task multistage/non-root Phase 2 |

---

## Ground rules (same in every route plan)

1. **v1 is the source of truth.** Use the same data products (`portfolio_analytics`, `atlas_elt`), the same seeds and CSVs, the same model and file names, and the same Atlas framing. v2 reorganises and improves v1; it does not add new datasets, toy projects or a separate harness.
2. **Databricks is the only dbt engine.** This applies to every route that runs dbt, including Airflow and the capstone.
   - Profiles are Databricks-only and follow [portfolio_analytics/dbt/profiles.yml](../../../data_products/portfolio_analytics/dbt/profiles.yml): `DATABRICKS_HOST`, `DATABRICKS_HTTP_PATH`, `DBT_CATALOG`, `DBT_SCHEMA`, and the `DBT_ACCESS_TOKEN` that `.mise/env.sh` mints from the OAuth session.
   - Everything builds in the learner's single pre-provisioned schema (`$DBT_SCHEMA` in `$DBT_CATALOG`).
   - No DuckDB, no `dbt-duckdb`, no offline dbt mode.
3. **mise for every command; work in place.** Run `mise run setup:databricks` once, then `mise run challenge:seed|dbt|verify|reset NN`, extended with `--phase 1|2`. Learners work in this repository, in the same files v1 uses. There are no sandbox repositories, no clones elsewhere, no copied `.local/challenges-v2/` workspaces, no `python3 scripts/challenge-v2.py` and no venv activation.
4. **No placeholders.** None in starter code (`select 1 as placeholder`, "Valid starter" echo commands), in config (`'unused'`, `'must_be_provisioned'`), in commands (`<instructor-schema>`, `OWNER/…`, `/path/to/…`), or as pages ("Phase 2 — not offered").
   - Every stub is real code that runs and does part of the job, with a `TODO` stating exactly what the learner adds. v1's Docker starter is the model: a real `FROM` line plus TODOs.
   - Every value in a command comes from the environment or from another command.
5. **Phase 1 — Certified; Phase 2 — Proficient.**
   - `phase-one-certified` certifies a learner to the baseline Data Creator standard. It is the core for everyone and ends with something that works end to end.
   - `phase-two-proficient` certifies a more advanced practitioner, through a small, fixed core of harder work.
   - **Time targets:** 2 h / 90 min for the main routes (dbt, Airflow, Atlas capstone); about 1 h / 45 min for the tool primers (Docker, environment and Databricks CLI, Git, optional Kafka).
   - Remaining v1 Phase 2 challenges go to a Stretch appendix, improved but unchanged in substance. Stretch counts toward neither certification.
6. **README layout (every route).** Use `#` for the title, `##` for top-level parts and `###` for each section. Put a `---` rule between every section. Follow this order:

   ```text
   # Route title: one-line outcome
   Two or three sentences: what you build and why it matters to the data product
   ## At A Glance        main task · files you edit · provided vs you write · start / verify / reset (mise) · time · finish line
   ## The two phases     opening discussion (§0 of the route plan)
   ## Learning outcomes  3–5 per phase, and what Certified vs Proficient means (§0b)
   ## What you will build   mermaid pipeline + the expected end result
   ## Before you start   where this route sits · entry check · one ordered mise block · which directory each command runs in
   ## Phase 1 — Certified
   ### Every section has the same shape
   ### Pacing guide     ranges, an environment-waits row, typical total = phase target
   ---
   ### 1. Section title … (recall prompt · Concept · Provided / You write · … · Common mistakes; each followed by ---)
   ### Certification task   a new problem, no scaffold, no solution shown
   ### Explain-back and check yourself   3–4 explain-back questions · 3–5 self-check questions · one reflection line
   ### Phase 1 summary
   ## Phase 2 — Proficient   (same pattern)
   ## Stretch
   ## Troubleshooting    symptom → cause → fix table
   ```

   - Use tables for budgets and comparisons, and `> **Note.**` callouts for warnings.
   - Put every command and every expected output in a fenced block.
   - Put level-2 hints and solutions in `<details>`.
7. **Content standard.** This defines "substantially improved":
   - **Concept:** plain English first, then why it matters for this data product, then one concrete example from the route's own data. Define every term on first use and give one docs link. Keep it to about 150 words.
   - **Provided / You write:** every section opens with these two lines, so scaffolding is announced rather than discovered.
   - **Challenge:** names the exact file and TODO, and states the outcome as something observable.
   - **Hint:** two levels. Level 1 says where to look; level 2 gives the shape (column list, command skeleton) but not the answer.
   - **How to check:** starts with **Predict:**, a one-line expectation the learner writes before running anything. Then the exact mise or tool command and the literal expected output. An intended failure shows its exact error text under a "this failure is the goal" callout.
   - **Try a variation:** a predict-then-run twist on the same data.
   - **Common mistakes:** the two or three mistakes seen in pilot runs, inline at the end of each section. Troubleshooting keeps only environment problems.
   - **Solution:** collapsible, behind a "try it first" prompt, with two or three lines on why it works. Certification tasks have no solution in the learner README; the reference answer lives in the facilitator guide.
8. **Learning design.** These rules make the two certifications mean something.
   - **Outcomes first.** Each phase states 3–5 outcomes ("By the end you can …"). Every section and every gate check maps to an outcome (§0b).
   - **What each level certifies.**
     - *Certified:* completes the guided build and explains why it works.
     - *Proficient:* solves an unfamiliar problem with little scaffolding, chooses between options and justifies the choice.
   - **Evidence = artefact + explanation.** The gate proves the files. Certification also needs:
     - a **certification task**: a new, unscaffolded problem on the same data, with no solution in the learner README;
     - **explain-back questions**, answered to a facilitator or partner and judged with the rubric in the facilitator guide.
   - **Fade the scaffolding.**
     - Phase 1 moves from worked example → completion problem (a stub with TODOs) → a file the learner creates from scratch.
     - Phase 2 starts at completion problems and ends at from-scratch work, framed as realistic requests: a bug report, a consumer request or a review comment.
   - **Debugging is core.** Each phase has at least one core section where something is broken on purpose and the learner reads the error, finds the cause and fixes it. Broken states come from a mise task (`mise run challenge:break NN --scenario …`), never from hand edits.
   - **Name the misconceptions.** Any Concept that touches a misconception listed in §0b states it and refutes it with evidence the learner sees in their own terminal.
   - **Recall before new material.** Key sections open with a one-question recall prompt that links to an earlier section or route.
   - **Fast feedback.** `mise run challenge:verify NN --section N` checks one section in under a minute and gives an actionable message. The phase gate runs all of them.
   - **Pacing guide, not a stopwatch.**
     - Budgets are ranges, with an explicit environment-waits row (warehouse start, Astro boot).
     - The typical total equals the phase target.
     - Re-baseline after pilot runs.
   - **Two tracks.**
     - *Fast track:* experienced learners skip reading-only sections once they answer that section's recall question.
     - *Support track:* a third hint level that gives the full shape, plus a suggested pairing point in each phase.
   - **Accessible visuals.** Put the diagram before the prose. Every mermaid diagram and screenshot has a one-sentence text alternative.
   - **Facilitator guide.** `FACILITATOR.md` sits beside each route README and contains timing checkpoints, likely sticking points, demo moments, the explain-back rubric and the certification-task reference answers.
   - **Course map.** Routes run 00 → Git → 01 → 02 → 03 → Kafka (optional) → 04. Each README states its prerequisites and opens with a two-question entry check.
9. **Plain language for first-time learners.** Write for a capable person meeting each idea for the first time, not for an expert.
   - **Reading level.** Concepts, Challenges and Hints aim for reading grade 9 or below (about age 14). Sentences average under 20 words. One idea per sentence, active voice, and address the reader as "you".
   - **Everyday words first, then the term.** For example: "what one row stands for, which dbt users call the **grain**". Bold a term once, where it is defined.
   - **Define every term at first use** in plain words, using the route's "Words to explain" list (§0c). Collect them in a glossary at the end of the README. Only these words need no definition: file, folder, command, terminal, table, row, column, query, CSV.
   - **Expand and explain acronyms** the first time they appear: SLA, DLQ, CTE, AUM, bps, NAV, FX, ISIN, JSON, CLI, PR, UC.
   - **Picture or example before the general rule.** Start with a two- or three-row example table, a diagram or an analogy. If you use an analogy, say where it stops being true.
   - **One new idea per section.** If a Concept runs past about 150 words or introduces more than two new terms, split the section.
   - **Why before how.** Each Concept opens with the problem the idea solves.
   - **Explain commands and errors.** The first time a command appears, a small table says what each part does. Every quoted error message is followed by one plain sentence: what it means and what to do.
   - **Rewrite dense v1 passages.** v1 is the base, but rewrite any passage that fails this rule. For example, v1 02 Phase 2 Ch1's Concept explains left joins, NULLs and `coalesce` in one 170-word paragraph; split it into three short steps with a two-row example.
   - **First-time-reader review.**
     - Before release, someone new to the tool reads the README and marks every word or sentence they had to reread or look up. Fix each mark by defining or replacing the word.
     - **(new)** `mise run challenge:lint-language NN` flags §0c terms used before their definition, unexpanded acronyms, and sentences over 30 words.

---

## 0. README opening: the two phases (draft text)

> Docker lets you package a program together with everything it needs to run, so it behaves the same on any computer. This company runs Airflow and dbt this way. Here you package a tiny program that summarises fund holdings. The program is deliberately simple, so you can focus on Docker.
>
> **Phase 1 — Certified (about 1 hour).** Everyone does this phase.
> - You run a ready-made package, look inside it, then write your own recipe for one, build it and run it.
> - You also give it data from your own folder, and see why changed data means building again.
>
> Passing `mise run challenge:verify 01 --phase 1` and explaining your work reaches the baseline standard.
>
> **Phase 2 — Proficient (about 45 minutes).** You read the real recipe this course uses to run Airflow, then make your own package safer.
>
> **How the help works:** the program and its data are finished. You write only the recipe, called a `Dockerfile`. Its first line is already written, with one `TODO` for each line you add.

---

## 0b. Learning design for this route

**Where it sits:** after 00 and Git; before 02.

**Entry check:**
1. Does `docker --version` print a version?
2. Can you run a Python script from a terminal?

**Outcomes**

| Phase | By the end you can… | Evidence |
|---|---|---|
| 1 | Explain the difference between an image and a container, using what you saw in your terminal | §1–§2; explain-back |
| 1 | Write, build and run a Dockerfile | §3–§5 |
| 1 | Give a container data from a folder, read-only, and explain the error when it tries to write | §6 |
| 1 | Explain why changed data needs a rebuild, and clean up only your own containers and images | §7; certification task |
| 2 | Read a real production Dockerfile and explain what each part does | Ch1 |
| 2 | Make an image safer (non-root user, smaller build context) and prove it | Ch2 certification task |

**Fading map**

| Stage | Sections |
|---|---|
| Worked example | §1–§2 |
| Completion problem | §3 (one TODO per line) |
| Partial command | §6 (the command is given with one flag missing) |
| From scratch | Phase 1 certification task |
| Phase 2 | Ch1 guided reading; Ch2 from a review comment only |

**Certification tasks (no solution in the learner README)**

- **Phase 1:** create `Dockerfile.mount` from scratch. It builds an image that contains Python and `summarize.py` but **not** the CSV. Run it with the CSV mounted read-only, and it must print the goal output. Check: `mise run challenge:verify 01 --section cert`.
- **Phase 2:** Ch2. A security-review comment says: "this image runs as root and sends the whole folder to the build". Fix both, starting from v1's solution Dockerfile, and prove the fix.

**Explain-back questions**

- **Phase 1:**
  - In your certification image, where does the CSV live, and why?
  - What is kept, and what is lost, when a container is removed?
  - Why did your old image still print the old total?
- **Phase 2:**
  - Why does the Astro Dockerfile switch to the root user and back?
  - What does `.dockerignore` change, and how did you prove it?

**Misconceptions to refute**

- A container is a small virtual machine. It shares your computer's operating system core; §2 shows this.
- Editing a file on your computer changes an image that is already built. §7 shows it doesn't.
- Stopping a container deletes its image.
- `docker system prune` is a normal way to tidy up.

**Recall prompt:** Phase 2 Ch1 → "Which program in this course runs inside this image?" (Airflow, Challenge 03).

**Tracks**

- *Fast track:* skip §1 after answering its recall question.
- *Support track:* pair at §3; the third hint level gives the four instruction keywords in order.

---

## 0c. Words to explain

Define each term in plain words where it first appears in the README (ground rule 9).

| Term | Plain definition to use | First used |
|---|---|---|
| image | A packaged, read-only copy of a program and everything it needs. Like a recipe that has already been cooked and frozen | §1 |
| container | One running copy of an image. You can run many containers from one image | §1 |
| base image | The ready-made image yours starts from, here `python:3.11-slim` | §3 |
| pull / registry | Downloading an image / the online store it comes from | §1 |
| Dockerfile | The recipe: a list of instructions Docker follows to make an image | §3 |
| instruction (`FROM`, `WORKDIR`, `COPY`, `CMD`, `USER`) | One line of the recipe. Define each where it first appears | §3 |
| layer | Each instruction saves a snapshot. Docker reuses unchanged snapshots to build faster | §4 |
| build / build context | Turning a Dockerfile into an image / the folder Docker is allowed to copy files from | §4 |
| tag | A readable name for an image, for example `v2-holdings:1` | §4 |
| `--rm`, `-it` | Remove the container when it stops / let you type into it | §2 |
| bind mount | Showing a folder from your computer inside a container, without copying it into the image | §6 |
| read-only (`:ro`) | The container can read the folder but cannot change it | §6 |
| Docker-in-Docker | In this devcontainer, Docker runs inside a container. Folder paths are those inside the devcontainer | Troubleshooting |
| root / non-root user, UID | Root is the all-powerful user. A non-root user has a number (UID) and fewer rights | P2 Ch2 |
| `.dockerignore` | A list of files Docker must not send to the build | P2 Ch2 |

---

## 1. What current v2 got wrong for this route

- It replaced v1's TODO-per-line Dockerfile with a placeholder `CMD ["python", "-c", "print('Valid starter: …')"]`.
- It hid the goal output until the last check.
- It removed v1's "What You'll Build", the section shape and the Troubleshooting section.
- It added a five-task Phase 2 (multistage, test gate, UID 10001, runtime contents, WORKDIR repair) that is larger than the whole v1 lab and unrelated to anything later in the course.

**Kept from v2:** the bind-mount idea and the "rebuild after a data change" insight. Both become Phase 1 sections.

---

## 2. Phase map: v1 → v2

| v1 | v2 | Change |
|---|---|---|
| What You'll Build | At A Glance + What You'll Build | Goal output shown first; image → container lifecycle diagram |
| §1 Run an image | P1 §1 | Add `docker ps -a` and exit-code check with expected output |
| §2 Look inside (isolation) | P1 §2 | Add a predict-then-run step: does `/tmp/inside.txt` survive a new container? |
| §3 Write the Dockerfile | P1 §3 | Keep v1's TODO stub; annotate which instruction makes which layer |
| §4 Build the image | P1 §4 | Expected build output trimmed to the step lines |
| §5 Run your image (portability) | P1 §5 | — |
| — | **P1 §6 (new): bind mount** | `docker run --rm -v "$PWD/app:/app:ro" -w /app python:3.11-slim python summarize.py`, plus the expected `Read-only file system` error on write |
| — | **P1 §7 (new): change data, rebuild, clean up** | Edit `holdings.csv`; old image still prints `12,011,626.50`; rebuild shows the new total; `mise run challenge:docker-clean 01` |
| §6 Try it yourself | Variations spread across §1–§7 | — |
| Troubleshooting | Troubleshooting | Add Docker-in-Docker bind-path behaviour in the devcontainer |
| — | **P2 Ch1: read a real image** | Walk the repo's [Dockerfile](../../../Dockerfile): `FROM astro-runtime`, `USER root` then back, the CA certificate, `os-packages.txt`, `requirements.txt`. Map each line to a §3 concept |
| — | **P2 Ch2: non-root + .dockerignore** | Add `USER` and the shipped `.dockerignore` to the holdings image; prove with `docker run … id` and a smaller build context |

---

## 3. Phase 1 — Certified (target ~1 h): improvements

| § | Section | Scaffold | Range (min) |
|---|---|---|---|
| 1 | Run an image (includes the first image download) | worked example | 5 |
| 2 | Look inside (predict: does the file survive a new container?) | worked example | 5–10 |
| 3 | Write the Dockerfile | completion | 10 |
| 4 | Build the image | run | 5 |
| 5 | Run your image | run | 5 |
| 6 | Bind mount: read the write error | debugging | 5–10 |
| 7 | Change data, rebuild, clean up (predict first) | run | 5–10 |
| Cert | `Dockerfile.mount` from scratch | none | 10 |
| — | Explain-back + check yourself | — | 5 |
| | **Typical total** | | **~60** |

- **At A Glance:** main task (complete `starter/Dockerfile`), goal output, `mise run challenge:verify 01 --phase 1`.
- **Time-budget table:** the one above.
- **Expected outputs** for every command, including the intended failures (§6 write denied).
- **Two-level hints.** Level 2 for §3 gives the four instruction keywords in order.
- **Collapsible solutions**, sourced from v1 `solution/`.

## 4. Phase 2 — Proficient (target ~45 min)

| Ch | Framed as | Content | Scaffold | Check | Range (min) |
|---|---|---|---|---|---|
| 1 | "What is the course actually running?" | Read the repo's Astro `Dockerfile` and answer five guided questions: the base image, why `USER root`, where the Python packages come from, what the CA certificate is for, and which image Challenge 03 runs | guided reading | Answers compared with a solution table | 15–20 |
| 2 (cert) | Security-review comment: "runs as root; the whole folder is sent to the build" | Non-root user + `.dockerignore`, starting from v1's solution Dockerfile | none | `id` shows a non-root UID; the build context is smaller; output unchanged; `mise run challenge:verify 01 --phase 2` → PASS | 20–25 |
| — | Explain-back + check yourself | | | | 5 |
| | **Typical total** | | | | **~45** |

## 5. Stretch appendix

- Multistage build with a test stage, kept from current v2 docker-p2-01/02 and rewritten in v1 style.
- Layer-cache experiment: reorder `COPY` and time the rebuild.

---

## 6. Starter code: no placeholders

- **Phase 1:** v1's `starter/Dockerfile` as-is (real `FROM python:3.11-slim` plus three TODOs). Remove the v2 echo `CMD`.
- **Phase 2:** starts from v1's `solution/Dockerfile` with no TODOs. The security-review comment is the brief, because Ch2 is the certification task.
- Name every exercise image and container with the `v2-holdings` prefix so cleanup is scoped.

## 7. mise

| Learner action | Command |
|---|---|
| Phase gate | `mise run challenge:verify 01 --phase 1` / `--phase 2` |
| Start a phase over | `mise run challenge:reset 01 --phase 1` |
| **(new)** Scoped cleanup | `mise run challenge:docker-clean 01`: removes `v2-holdings*` containers and images only, never `docker system prune` |

Docker commands themselves run from `challenges/v2/01-docker-intro/starter`, because `.` is the build context. Say this once in "Start Here", as v1 does.

## 8. Retire from current v2

- `challenges/v2/docker/phase-*/starter/**` and `challenges/v2-solutions/docker/**`.
- The Docker paths in `scripts/challenge-v2.py`.
- Update `tests/challenges/offline/test_v2_contracts.py`.

## 9. Done when

- [ ] Same app, data and goal output as v1 01.
- [ ] Phase 1 — Certified = 7 sections, piloted at about 1 h. Phase 2 — Proficient = 2 challenges tied to the course's real image, piloted at about 45 min. Stretch holds the multistage material.
- [ ] No placeholder `CMD` or values; every command is mise or a plain `docker` command run in the starter folder.
- [ ] Docker-in-Docker bind-mount behaviour verified in the devcontainer and documented.
- [ ] §0b is implemented: outcomes mapped to sections and checks; certification tasks with no learner-visible solution; explain-back questions with a rubric; the fading map; a core debugging section per phase; misconceptions addressed; recall prompts; check-yourself questions; `--section N` checks; and `FACILITATOR.md`.
- [ ] A trainee run is recorded via the `challenge-trainee-runs` skill, and the pacing ranges are re-baselined from it.
