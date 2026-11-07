# Git route: v2 plan (new tool primer, built on this repo and v1's files)

## At a glance

| | |
|---|---|
| **v1 source** | None. v1 has no Git challenge, so this route is a short primer that uses **this repository and the v1 Challenge 02 files** instead of the current toy `contract.md` |
| **Target folder** | `challenges/v2/git/` (an optional primer taken before Challenge 02) |
| **Where learners work** | **In place, in their clone of this repository**, on their own branch. No sandbox repository, no second clone, no lab folder outside the repo |
| **Files touched** | [challenges/v1/02-dbt-pipeline/dbt/models/sources.yml](../../v1/02-dbt-pipeline/dbt/models/sources.yml) (the `custodian.holdings_raw` freshness block: `warn_after` 4 h, `error_after` 6 h) and the Challenge 02 `stg_holdings.sql` stub |
| **Phase 1 — Certified** | `phase-one-certified`, target **~1 h**. Local Git on the training repo: status, staging, commits, branches, a merge conflict, restoring a mistake. Ends back on the learner's starting branch with a clean tree |
| **Phase 2 — Proficient** | `phase-two-proficient`, target **~45 min**. Push the branch to this repo's `origin`, open a **draft** PR, respond to a review, integrate `origin/main`, then close the PR without merging |
| **mise** | `mise run setup:gh-auth`, `mise run challenge:verify git --phase 1\|2` |
| **Current v2 content dropped** | `contract.md`, `review-scenario.json`, the instruction to create a personal `dc-git-training` repository, the second `../colleague` clone, and the hardcoded example username |

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

> **Git** keeps a full history of every change to the files in this project, and lets several people work on them safely. Every change to a data product here goes through Git, and someone else checks it first. You practise on a real setting from Challenge 02: how old the custodian data may get before dbt warns you.
>
> **Phase 1 — Certified (about 1 hour).** Everyone does this phase.
> - You save changes in small, clear steps.
> - You work on your own line of history (a **branch**), combine two branches, and settle a clash between two edits.
> - You undo a mistake safely, and finish with everything back as it was.
>
> Passing `mise run challenge:verify git --phase 1` and explaining your work reaches the baseline standard.
>
> **Phase 2 — Proficient (about 45 minutes).** You share your branch on GitHub and ask a colleague to review it. You answer their comment, bring in other people's changes, then close the request without merging it.
>
> **How the help works:** nothing to install, and no new project. You edit one settings file (written in YAML, a simple text format) that you will meet again in Challenge 02.

---

## 0b. Learning design for this route

**Where it sits:** after 00; before 01 and 02.

**Entry check:**
1. Does `git --version` print a version?
2. Have you seen a **diff** before, a before-and-after comparison of a file? If not, §2 shows one first.

**Outcomes**

| Phase | By the end you can… | Evidence |
|---|---|---|
| 1 | Explain the working folder, the staging area and the history, using `git status` output | §2 |
| 1 | Make small commits that each record a business reason | §3 |
| 1 | Branch and merge, predicting whether Git can combine the changes by itself | §4 |
| 1 | Settle a conflict by making the business decision, not by picking a side at random | §5 |
| 1 | Undo safely, and explain restore vs revert vs reset | §6; certification task |
| 2 | Open a pull request a reviewer can follow, and answer a review in the history | Ch1–Ch2 |
| 2 | Bring in other people's changes and explain fetch vs merge | Ch3 certification task |

**Fading map**

| Stage | Sections |
|---|---|
| Worked examples | §1–§2 |
| Completion problems | §3–§4 |
| Debugging | §5 |
| From scratch | Phase 1 certification task |
| Phase 2 | Ch1 completion; Ch2 guided review; Ch3 none |

**Certification tasks (no solution in the learner README)**

- **Phase 1:** on `training/$ME/revert-drill`, change `error_after` for `bloomberg.prices_raw` and commit it. Then undo that commit with `git revert`, and explain in two lines why revert, not reset, is the right choice on a branch others might see.
- **Phase 2:** Ch3, below.

**Explain-back questions**

- **Phase 1:**
  - What is the difference between `git diff` and `git diff --cached`?
  - In the conflict, who decides the 3-hour value, and why?
  - Why did `git restore` not change your history?
- **Phase 2:**
  - What does fetch do that merge doesn't?
  - Why close the training pull request instead of merging it?

**Misconceptions to refute**

- A branch is a copy of all the files. It is only a pointer; §4 shows the files switching.
- `git restore` deletes commits. §6 shows `git log` unchanged.
- A conflict means something is broken.
- `git pull` only downloads.

**Recall prompt:** 02 §3 opens with "You changed this freshness setting in the Git route. What did the two thresholds mean?"

**Tracks**

- *Fast track:* skip §1 after its recall question.
- *Support track:* pair at §5; the third hint level shows the resolved file.

---

## 0c. Words to explain

Define each term in plain words where it first appears in the README (ground rule 9).

| Term | Plain definition to use | First used |
|---|---|---|
| Git / repository (repo) | A tool that records every change to a set of files / the project folder plus its history | §0 |
| commit | A saved snapshot of your changes, with a message saying why | §1 |
| working folder, staging area | The files as they are now / the changes you have picked for the next commit (`git add` picks them) | §2 |
| diff | A before-and-after comparison: `-` lines removed, `+` lines added | §2 |
| branch / `main` | Your own line of history / the shared main line | §2 |
| YAML | A simple text format for settings, using indentation and `key: value` pairs | §2 |
| merge / fast-forward | Combining two lines of history / when Git just moves forward because nothing clashes | §4 |
| conflict, conflict markers | Two edits to the same line. Git marks them with `<<<<<<<`, `=======`, `>>>>>>>` and asks you to choose | §4 |
| restore / revert / reset | Undo an uncommitted change / add a new commit that undoes an old one / move a branch back (it rewrites history, so avoid it on shared branches) | §6 |
| stash | Put unfinished changes aside, and get them back later | §6 |
| remote, `origin` / push / fetch / pull | The shared copy on GitHub / send your commits there / download others' commits / fetch and then merge in one step | P2 Ch1 |
| pull request (PR), draft, review | A request to merge your branch, shown on GitHub / not ready to merge yet / a colleague's comments on it | P2 Ch1 |

---

## 1. What current v2 got wrong for this route

- It taught Git on an invented `contract.md` with no link to the course's data products.
- It sent learners outside the repo: a new lab directory, a personal `dc-git-training` repository created with `gh repo create`, and a second clone to impersonate a colleague.
- It used generated task cards with prose-only commands, no expected output and no solutions.

---

## 2. Branch naming (no placeholders)

Every branch name is computed, never typed from a template:

```bash
ME="$(gh api user --jq .login)"
git switch -c "training/$ME/freshness"
```

The At A Glance block shows this once. Later sections reuse `$ME`, and Troubleshooting covers re-setting it in a new terminal.

---

## 3. Phase 1 — Certified (target ~1 h)

**Before you start:**

- Run `mise run setup:gh-auth`, because `gh api user` sets `$ME`.
- If you already have Challenge work in progress, save it with `git stash push -u -m "before git route"`. Section 6 restores it.

| § | Section | What the learner does in this repo | Expected evidence | Scaffold | Range (min) |
|---|---|---|---|---|---|
| 1 | Where am I? | `git status`, `git branch --show-current`, `git log --oneline -5`, `git remote -v` | Starting branch name recorded; clean working folder | worked example | 5 |
| 2 | The three states (predict the `git status --short` output first) | Create `training/$ME/freshness`; change `custodian.holdings_raw` `warn_after` from 4 to 3 hours; compare `git diff` with `git diff --cached` before and after `git add` | ` M` vs `M ` in `git status --short`, explained | worked example | 10 |
| 3 | A good commit | Commit with a message that states the business reason ("Tighten custodian freshness warning to 3h"); then a second commit lowering `error_after` from 6 to 5 hours | `git log --oneline -2` shows two scoped commits | completion | 5–10 |
| 4 | Branch and merge (predict: will Git combine these by itself?) | From the starting branch create `training/$ME/freshness-alt` that sets `warn_after` to 5 hours; merge it into `training/$ME/freshness` | Expected `CONFLICT (content): Merge conflict in …/sources.yml` | completion | 10 |
| 5 | Resolve the conflict | Read the markers, keep 3 hours (the agreed value), stage and commit | `git log --graph --oneline` shows a merge commit with two parents; no markers left | debugging | 10–15 |
| 6 | Restore a mistake, then tidy up | Make an accidental edit to `stg_holdings.sql`; run `git log --oneline -3`, then `git restore`, then `git log --oneline -3` again; switch back to the starting branch and `git stash pop` if used | Both logs identical (restore does not touch history); clean working folder on the starting branch | worked example | 5–10 |
| Cert | Revert drill | See §0b | `git log` shows the change and its revert; two-line explanation | none | 10 |
| — | Explain-back + check yourself | | | — | 5 |
| | **Typical total** | | | | **~60** |

Each section has a mermaid `gitGraph` of the state so far, two-level hints, the literal expected terminal output, a variation (for example `git merge --abort` in §4, `git commit --amend` in §3) and a collapsible solution.

## 4. Phase 2 — Proficient (target ~45 min)

| Ch | What the learner does | Expected evidence | Scaffold | Range (min) |
|---|---|---|---|---|
| 1 | Push `training/$ME/freshness` to `origin` with `-u`; `gh pr create --draft --base main --fill` | Draft PR URL; `gh pr diff` shows only `sources.yml` | completion | 10–15 |
| 2 | **Structured peer review.** A partner (or the facilitator) answers three questions on the PR: (a) Is the change about one thing? (b) Is the business reason written down, in the commit message or a YAML comment? (c) What could it break later (the 02 freshness check, the 03 DAG)? The learner answers each point in a new commit and pushes | Review comments visible; new commit in `gh pr view --comments` | guided | 10–15 |
| 3 (cert) | `git fetch origin`; compare with `git log --left-right --oneline HEAD...origin/main`; merge `origin/main` into the branch and push. Write a closing comment explaining fetch vs merge and what reached `origin`, then `gh pr close --delete-branch` and return to the starting branch | `git merge-base --is-ancestor origin/main HEAD` exits 0 before closing; PR shows **Closed**, not merged; closing comment present | none | 15–20 |
| — | Explain-back + check yourself | | — | 5 |
| | **Typical total** | | | **~45** |

**Repository rules this phase needs**, agreed with the repository owners before the course:

- Learners can push `training/*` branches to `origin`.
- `main` is protected.
- Training PRs are always closed, never merged.

The README states this in the Phase 2 At A Glance. If push access is missing, `git push` fails with the permission error shown in Troubleshooting, and the learner asks the facilitator.

## 5. Stretch

- `git rebase origin/main` on a copy of the training branch (`training/$ME/freshness-rebase`), compared with the merge from Ch3.
- `git bisect` across the last ten commits of `challenges/v1/02-dbt-pipeline/dbt/models/sources.yml`.

## 6. mise

| Learner action | Command |
|---|---|
| GitHub auth | `mise run setup:gh-auth`, then `gh auth status` |
| **(new)** Phase gates | `mise run challenge:verify git --phase 1` checks for a `training/$ME/freshness` branch with two scoped commits and a two-parent merge, and a clean tree on the starting branch. `--phase 2` checks the closed PR via `gh pr list --state closed --head training/$ME/freshness` |

## 7. Retire from current v2

- `challenges/v2/git/phase-*/starter/**` (`contract.md`, `review-scenario.json`, `pr` templates).
- `challenges/v2-solutions/git/**`, including `workflow.sh`, and the Git paths in `scripts/challenge-v2.py`.
- Update `tests/challenges/offline/test_v2_contracts.py` (it currently copies the Git solution into a temporary directory).

## 8. Done when

- [ ] All work happens on `training/$ME/*` branches in this repository, on the v1 Challenge 02 files; nothing is created outside the repo.
- [ ] Phase 1 — Certified = 6 sections, piloted at about 1 h. Phase 2 — Proficient = 3 challenges, piloted at about 45 min.
- [ ] No placeholder names; the branch name comes from `gh api user`.
- [ ] Training PRs are closed and branches deleted at the end of Phase 2; the learner's tree is clean on the starting branch at the end of Phase 1.
- [ ] §0b is implemented: outcomes mapped to sections and checks; certification tasks with no learner-visible solution; explain-back questions with a rubric; the fading map; a core debugging section per phase; misconceptions addressed; recall prompts; check-yourself questions; `--section N` checks; and `FACILITATOR.md`.
- [ ] A trainee run is recorded via the `challenge-trainee-runs` skill, and the pacing ranges are re-baselined from it.
