---
name: module-review
description: The independent reviews of CG Core material by someone who didn't write it — the peer review of a module by another developer or instructor (or this agent acting as reviewer), the pedagogical review of a handbook draft (the source stage) and the read-through of a whole session as a learner and an instructor. The peer review reads in development-flow order (handbook, lesson-plan block, overview, demo section, challenge section) for factual accuracy, learning value, challenge evidence, connection to the modules either side, running the demo anchor and every folded solution yourself — reported as must-fix vs should-improve with evidence before the fix into the module's research folder (reference/cg-core-research/dayNN/mN-<slug>/); and the closing loop where the author addresses the feedback (apply must-fixes, decide should-improves, rerun, reply, flag substantial revisions). Use whenever the user asks for a peer review, a pedagogical review, a session read-through, "read it through as a learner", SME pass, review, QA, "check this is right", "is this teachable", to verify quoted figures, or to address or close review feedback — for CG Core. These are Asana subtasks "Peer-review" and "Feedback addressed".
---

# Module review (peer review and feedback loop)

Stages 5 and 6 of the seven, plus the two independent reviews the source process and the session build need (below). Where `module-audit` asks "does it match the pattern?", this asks "is it true, runnable, teachable and safe for CG?". Allowance: about half a day per module for the reviewer, about one day per unit for the author's responses. Definition of done: `reference/subtask-descriptions.md` → **Peer-review** and **Feedback addressed**. The Decoded SME responsibilities are the master: [references/sme-peer-review-responsibilities.txt](references/sme-peer-review-responsibilities.txt).

## Before you start (reviewer)

1. Read `programme-profile` (SKILL.md, `references/layout.md`, `references/conventions.md`, `references/structure.md`) and this session's digest: the review checks against what the pair has already taught and decided; and `module-builder/references/session-checklist.md`.
2. Open the module in the session folder in development-flow order: `learner/moduleNN-<slug>/dayNN_mN_handbook.md`, its block in `instructor/module00-overview/dayNN_lesson_plan.md`, `learner/module00-overview/dayNN_overview.md`, its section of the module demo notebook (`instructor/moduleNN-<slug>/dayNN_mN_demo.ipynb`) with the files beside it, its section of the module challenge notebook (`learner/moduleNN-<slug>/dayNN_mN_challenge.ipynb`) with its starter files. Read once as a learner and once as an instructor.
3. Confirm `module-self-review` and `module-audit` are done (audit 0 errors, 0 warnings; the author's correction transcript summary says so). If not, send it back.
4. Read the brief's module section: the review judges against the key questions, not against taste.
5. Have the dev container ready (or a throwaway container from its image): every code block is executed, not read, in the environment learners use.

## Principle: evidence before the fix

Execute the demo anchor top to bottom and every file it opens, run each challenge cell and starter file as shipped (it fails where the task says), apply each folded solution's change to fresh starter files and run its check, quote the real numbers, then propose. Never verify a quoted figure by reading. Classic catches: a handbook worked example the code never produced; a lesson plan or demo quoting a number the handbook does not; a challenge whose "what to show" cannot be reached with the taught skills; a `::: catalyst` box that paraphrases. The handbook is the source of truth: a fix lands there first and flows down.

## Priorities (the brief's order)

1. **Factual accuracy** of explanations, code, figures and claims. Terminology consistent; examples reflect real practice; numbers in the handbook match a real run, and the lesson plan, demo and challenge quote the same ones.
2. **Learning value**: do the explanations, figures and activities support the outcomes? Missing foundations, overload, poor sequencing, unsuitability for adult learners. Each new concept gets an example before terminology; every rule says why. Is it the simplest version that works? Is every reference back specific (file, command, what it shows)? Is every term defined before its shorthand, in each file on its own? Does each module section open with an anchor that makes the case from the learner's own work?
3. **Challenge evidence**: does the challenge produce observable evidence of the outcomes in the module's challenge time (the demo's 🏆 CHALLENGE TIME box) with the pair's prerequisites? Is each outcome clause's core evidenced at Q1 or Q2? Are the challenge's faults its own, not the demo's? Does Put it together start from a state that Q1 and Q2 reach? Do paired tasks run in parallel, swapping only for the review? Walk it as a struggling learner from Q1: where do they stall, does the task box or a hint cover it? Does it follow the programme's way of working (`programme-profile/references/conventions.md` → "Learners direct AI and review what it wrote"): Copilot writes, fixes or changes the code, maths included, and the learner reviews, runs the check and keeps or undoes, never typing code; light maths; planted faults rather than gaps; Q3 not expected? Would each folded solution's model prompt plausibly get its change from Copilot, and does the recorded check prove it? Are the Copilot settings right for the job (`programme-profile/references/conventions.md` → "The Copilot box"): Ask for understanding code, Plan for a bigger change before anything changes, Agent for a job that creates or changes files; Fast for quick edits and questions, Reasoning for multi-step work; an ATTACH badge wherever the prompt needs a file, the selection or the codebase? Try one prompt with exactly those settings.
4. **Run the demo anchor and the solutions yourself**, on a fresh kernel in the dev container image, zero pre-adjustment; no output shows a warning; pins match `courseware/.devcontainer/requirements.txt`; the services' tests and `scripts/test-dev-container.sh` pass; starter files fail where they should and nowhere else; the challenge runs on a fresh kernel without the demo (self-contained: its own setup cell, data path and starter files); the challenge notebook ships without outputs and every solution is folded after a 💭 reflect box, in AIA's box set from `nbkit`, with the demo's 🏆 CHALLENGE TIME box matching its tiers.
5. **CG safety**: every "at CG" claim traced to Catalyst; tools, platforms and ways of working compared with their pros and cons and what each is good for, never framed by their limitations, in table headings and FAQs too (`programme-profile` CG rule 2; limitation-led wording is a must-fix), review and checks taught as good practice every change gets, a planted-fault file presented as a first draft to review, never as Copilot's mistakes, and no `<!-- sensitive: … -->` marker; nothing inferred from public Databricks docs; nothing identifiable; no real firm.
6. **Alignment and connection**: handbook ↔ lesson-plan rows ↔ overview ↔ demo section ↔ challenge section agree on names, numbers, durations and "what to show"; the lesson plan's section summary and transitions join the module to the ones either side, and each module section's 🧭 anchor and bridge say why it matters and what it builds on; the anchors in `dayNN_anchors.md` are specific and define their terms; the module's served outcomes match `dayNN_overview.md` and the programme document, and ladder to the programme demonstrations. The handbook stays self-contained (no demos, challenges, session, instructors or later modules). The demo and challenge mention the handbook only in each module section's closing Go deeper box, and the lesson plan and overview never cite a handbook section, because such references go stale.
7. **Readability**: every prompt learners or instructors are given sits in the standard 🤖 COPILOT box, in every file: `nbkit.copilot_prompt` in the anchors with the Copilot legend in "How to use this notebook", `nbkit.copilot_solution` in folded solutions, a `::: copilot` div in the handbook, lesson plan and overview; no prompt in a blockquote, a bare fenced block or a prose mode label; prompt lines short enough not to wrap in the PDF (under about 90 characters). UK English, sentence case, plain sentences, plain-English first use. Handbook and overview prose in connected paragraphs with transitions, no in-line references (sources only in further reading), no typed section or figure numbers; no "The proper words" line that repeats what a figure labels; the demo visual-first, each config file it opens explained in a line-by-line table, figures that pair two things lined up row by row, and each challenge section showing its recap visual after its anchor and bridge. Code formatted (`scripts/format_code.py --check`), its comments helpful rather than noisy and none of them splitting a line.

Do **not** rewrite presentation style; the delivering instructor adapts that.

## Report

`reference/cg-core-research/dayNN/mN-<slug>/peer-review.md` (user, 2026-10-27: every review lives in the research folder):

```markdown
# Peer review — S03 M2 <title>   (reviewer, date)

## Verdict
<ready for materials / ready after must-fixes / needs another source pass>

## Must-fix
| # | File | Location | Issue | Evidence | Suggested fix |

## Should-improve
| # | File | Location | Issue | Suggested fix |

## Verified by running
<commands run, figures confirmed>

## Author responses
(filled in stage 6)
```

## Closing the loop (author, stage 6)

- Apply every must-fix. Decide each should-improve and record the decision and reason in the Author responses section.
- Apply each fix at the earliest development-flow step it touches (handbook → lesson plan → overview → demo → challenges) and mirror it downstream in the same pass.
- Re-execute the demo anchor and rerun every folded solution after changes; refresh any quoted figure.
- Reply to the reviewer with what changed (the responses table is the reply).
- If revisions are substantial, say so in the session digest so the delivering instructor has time to understand them.
- Once the capstone schema is defined, revisit the challenge for alignment and treat it as a further review round.
- Done when every must-fix is resolved, every should-improve decided, and the module is ready for stage 7 and the 13 December submission.

## Pedagogical review of a handbook draft (source stage)

Commissioned by `module-source` (its source process, step 4) from someone who didn't write the draft; the author's self-check never stands in for it. Read the draft (`draft.md` or the handbook) with its figures, the brief's key questions and the outcomes it serves. Report missing foundations, overload, sequencing, suitability for adult learners, simplicity (is this the simplest version that works?), vagueness (references back that don't name the file, command and result) and define-first (terms used before they're defined), as must-fix, should-improve and a reduce-and-refine table (cut, simplify, merge or move to an appendix, with words saved), each item with its location and evidence, and a suggested final outline. Remember the ruling: the handbook is the source of truth for the topic, so topic knowledge stays in it or its appendix; only delivery detail moves to the lesson plan. Save it as `reference/cg-core-research/dayNN/mN-<slug>/pedagogical-review.md`. The user chooses what to apply.

## Session read-through

Commissioned by `module-builder` once the session's tooling is clean (session checklist part E), from someone who didn't build the session. Read it end to end twice: as a learner (overview, handbooks, demo, challenge, opening the files they point to) and as an instructor (lesson plan, demo and its folders, completed challenge). Check the thread and the transitions; timing (each demo row fits its minutes, slow steps pre-run in the breaks, Q1 fits the challenge time, paired work in parallel); simplicity; consistency of names, numbers, ports, branches, repositories and folders across files; outcome evidence (core clauses at Q1 or Q2, Put it together reachable); the content rules; vagueness; and define-first, in every opening, tagline, persona card and CHALLENGE TIME box. Report a verdict, must-fix and should-improve with file and location, and the timing risk per module, in `reference/cg-core-research/dayNN/session-read-through-<date>.md`.

Record any decision that constrains other modules in the session digest. MJB's programme review (14–17 December, printed and marked up) is separate and follows this.

**Action-first prose (user, 2026-11-02).** Summaries, purposes, section summaries, slide lines, cards and speaker notes say what learners do, in order, with a concrete object ("Write pytest tests for the report's code, fix it test-first…"), never a topic summary ("Make a change the way a team does", "An AI service that answers with evidence"). The rule and its banned words are in `courseware-conventions/references/writing-rules.md` → Learner-facing descriptions; reviews flag any line a reader couldn't picture doing at their laptop.

**Technical terms and completeness (user, 2026-11-02).** A summary names the techniques in the field's terms (FastAPI, RAG, agents, evals, dbt, Airflow), explained at first use or in the notes, and covers every module it summarises; check it against the module list ("Build a FastAPI service with model calls, RAG, agents and evals", not "Serve a JSON API whose AI summaries cite sources"). Rule: `courseware-conventions/references/writing-rules.md` → Learner-facing descriptions.
