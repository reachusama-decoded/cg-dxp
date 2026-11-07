# Writing rules (house additions to the tone-of-voice master)

The tone-of-voice master is the authority. These are the rules Decoded courseware adds on top, confirmed across programmes. Each says why it exists so you can apply it to cases it does not list.

## Voice

- Short, punchy sentences. No fluff, but no missing core content either.
- **No lone paragraphs of three or more sentences.** Restructure into bullets or separate short paragraphs (blank line between — a single newline does not render as a break in Jupyter). Two short sentences may share a paragraph; deliberate staccato fragments ("Confident. Specific. Wrong.") are exempt. Where a paragraph explains a flow, comparison or mapping, a small brand mermaid replaces it: graphics over text.
- No dramatic wording ("dies in a notebook" was rejected). No hedging ("we believe", "it seems", "perhaps", "arguably"). No corporate jargon ("leverage", "seamless", "cutting-edge", "unlock", "empower", "synergy", "best-in-class", "utilize", "robustify"). Banned-flavour words beyond the master's list: "crucial(ly)", "journey", "impactful".
- Contractions wherever prose reads as spoken; not in tables, labels, prompt templates or deliberate emphasis.
- Technical terms get a plain-English introduction at first use; full forms first (Application Programming Interface; say "User Interface", not just "Interface").
- **Define every term before its shorthand** (Decoded-wide, 2026-10-27). Name and explain a method or term at its first use in each file, before any abbreviation, nickname or derived phrase for it: test-driven development (TDD) before "TDD" or "test-first"; "a fixture, a small table pytest hands to any test that names it" before "the fixture". Each file can be read on its own (a notebook, a handbook, an overview), so each defines its own terms.
- Real typographic characters, never HTML entities (`—` not `&mdash;`), except `&amp;` inside mermaid labels and `&nbsp;` inside HTML banners. Whether prose em-dashes are rewritten out (commas, colons, full stops) is a per-programme choice: check the profile and never cross-apply one session's dash convention to another without asking. Structural em-dashes always survive: banner `&nbsp;—&nbsp;`, version lines, quote attributions, `**Qn — label:**` prefixes, "Solution — attempt before opening", "Reflect — answer:".
- Sentence case everywhere, including headings and table columns. Named methods may be capitalised as a deliberate, session-wide exception (Decision Tree, Random Forest) — never lowercase them piecemeal.

## Learner-facing descriptions

- **Say what learners do, not a summary of the topic** (Decoded-wide, 2026-11-02). Every short piece of prose, the summaries most of all (a programme or unit intro, a day's purpose, a section summary, a slide line, a card, a speaker note, a goal), names the actions in the order learners take them: "Write pytest tests for the report's code, fix it test-first, take the change through a reviewed pull request" beats "Make a change the way a team does"; "Serve a JSON API whose AI summaries cite sources and pass evals" beats "An AI service that answers with evidence". Lead with a verb or "Learners …"/"you …" and a concrete object. Ban the vague promise words, "trust", "defend", "properly", "the right way", "the shape of", "make sense of", "a sense of", "is about", "explores", "the way an engineer does", unless the same sentence says exactly what that means; "trust" stays only in its exact technical senses (an SSH host key). A goal is an action too ("Build ETL/ELT pipelines on a data platform", not "Practical data engineering"). Test: could a reader picture what they will be doing at their laptop? If not, rewrite.
- **Invite; never lecture** (Decoded-wide, 2026-11-02). Say what learners can do and choose, warmly, never a curt or superior contrast: "Attend the units you want and leave the others as optional; your own experience counts towards the capstone too", not "The capstone asks for skills, not attendance" or "The capstone certifies the skills, not the attendance". Watch for "X, not Y" put-downs, "nothing else", "nobody minds" and rules aimed at the reader; turn each into what the reader may do.
- **Name the techniques, and cover the whole** (Decoded-wide, 2026-11-02). A summary uses the field's technical terms for what learners do (FastAPI, RAG, agents, evals, pytest, dbt, Airflow, leakage checks), each explained in plain words at its first use in the file or in the speaker notes, and it covers every module or part it summarises: a unit line names all six modules' techniques, a day line all three. "Serve a JSON API whose AI summaries cite sources and pass evals" fails twice: too narrow a detail, and no agents or model calls; "Build a FastAPI service with model calls, RAG, agents and evals" passes. Check a summary against the module list before you keep it.
- **Be specific: name the concrete thing** (Decoded-wide, 2026-10-27). When text refers back to earlier work or to a check, it names the file, the command and what it shows ("`python fund_report.py | diff report.txt -` prints nothing while the output still matches"), never "a check", "a saved copy" or "the earlier script". Section openings ("This builds on …"), taglines and summaries are where vagueness creeps in: read them for it.
- **Pass the day-one test.** Say what a tool *lets you do*, not what it is: "let other software ask your model a question and get an answer back" beats "build and serve production APIs". Never lean on a term the programme has not taught yet (API, frontend, deploy, orchestration), including in column headers and layer names. Collapse rows whose distinction is not meaningful yet.
- **Every checkable claim carries a source.** Dates, named incidents and industry statistics get a link to a primary source, verified to resolve before it is written in. If a statistic cannot be sourced, soften it or cut it. Never attach a shaky link to make a claim look sourced.
- **Numbers learners can check must be exact** — line counts, row counts, prices. The session invites counting; "about 150" when the folder holds 170 gets caught live.
- **Learner-facing timings use natural denominations**: 30/60/90 seconds, 1/2/3/5/10 minutes — never "4 mins" or "~28 minutes" in activity boxes or spoken prose. The lesson plan's schedule grid keeps its exact odd minutes; only the learner-facing phrasing rounds.
- **No time-of-day or section-number rhetoric in teaching prose**: no "this morning", "all morning", "in Section 3". The lesson plan's Say lines count as teaching prose. Use relative phrasing ("earlier", "coming up") or content-named references ("the MLP build", "the ice-breaker word cloud"). Exempt as navigation: headings, TOCs, block banners, break cells, "Open challenge_NN.ipynb, Section 2" pointers, instructor checklists.
- **Never mention a future session** in learner-facing text, even when it pins today's scope. No "when you'll use it: Session 9" columns either — give the trigger instead ("as soon as you start training models"). Instructor-only blocks may keep the numbers.
- **Analogies map back to the proper words.** Every teaching analogy (lunchbox, fridge, recipe card) is tied to its technical term on the page or section that uses it, as a one-line 📖 "the proper words" band, with a link to a glossary where one exists.

## Outcomes

Open with the stem, then about four outcomes (one per section is fine when sections map 1:1), each carrying all three elements:

- **Behaviour** — a measurable action verb (explain, build, call, choose, describe…). Never unobservable verbs: understand, know, appreciate, be aware of, be familiar with, grasp, recognise.
- **Standard** — the level of performance, quantifiable ("naming every layer", "on every call", "within 10% of the baseline"). Never unquantifiable fillers: basic, quickly, confidently, effectively, successfully.
- **Condition** — the circumstances/tools ("using the provided dataset", "for an app of your choice", "with the session's key file").

```markdown
## What learners will leave with

By the end of this session learners will be able to:

- **Outcome 1:** <Verb> <what> — <standard>, <condition>
```

The demo repeats the outcomes under `## What you will learn` with the second-person stem ("By the end of this session you will be able to:") and the leading verbs bolded — wording otherwise identical to the lesson plan. Each outcome must be assessable inside the session: its standard and condition happen somewhere concrete (a challenge, a poll, a your-turn beat).

**Outcomes must not spoil the session's reveals.** No standard that itemises an in-session answer or pre-answers a guess activity ("naming all four (user interface, API, model, data)" hands over the layer map). Keep standards measurable without the list: "naming every layer".

## Structure

- `---` only at genuine section transitions (before block banners, `## Section` headings, the footer) — never between activities in one section. In a long walkthrough, use it just to open and close the sequence.
- Drop section numbers when the order already carries them: numbered headings, a numbered contents table and numbered anchors drift apart the moment one section moves. If you number, number all three or none.
- Real-world analogy before terminology for every major concept; decision tables or mermaid flowcharts wherever learners must choose between approaches.
- "Why this matters" and "Apply it to your work" wording identical across lesson plan, demo and challenge.
- **The lesson plan is the source of truth, but sync runs both ways.** Adding or changing an activity in the demo or challenge is not done until the lesson-plan activity tells the instructor it exists — a box nobody is sent to is a box nobody opens. Same pass, not a follow-up.
- **A number that lives in two files goes stale in one of them.** Durations, counts and figures repeated across notebooks have exactly one correct value: change it in one, grep the others before moving on.
- **No word does two jobs in one notebook.** If the architecture section says "three services", do not call the tools "four services" a paragraph later.
- **One idea per markdown cell** in demo and resource notebooks. Split long teaching cells at natural boundaries (sub-headings, tables that follow prose, "**N. Topic**" numbered concepts, closing caveats), keeping each image in the same cell as the paragraph that introduces it; roughly one screen per cell. Never split: title cells, single HTML boxes, `<details>` blocks. The lesson plan is exempt (one cell per timed activity). Splitting is re-celling only — no rewording in the same pass.
- **Every diagram is introduced from directly above.** The line before the image says what the learner is about to look at. Never a bare image under a heading.
- **No guidance blurbs at the top of notebooks** ("yours to keep", "how today works"). Header cell is logo/title/version/© only, then straight into the content. Activity-box instructions mid-notebook and a challenge's "How to use this notebook" section are fine.

## Titles you invent

Session titles come from the profile's confirmed list; never type one from memory. For titles you *do* invent (resources, hackathons, activities):

- No colons; an em dash is fine ("Hackathon — Deploy and monitor a live system").
- Never "(cont.)". Tools appear only as a single "with <tool>" suffix, never tool lists.
- House shapes: "X & Y" pairs · "with <tool>" suffix · "From X to Y" journeys · verb-led imperatives ("Build and ship …").
- Brand-voice test: would a smart 16-year-old understand it?
