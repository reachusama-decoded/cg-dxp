# Source-content workflow (MJB's reference-led method, from transcript Part 2 §9)

MJB's original method. Where `module-source` Stage B differs (the user's source process of 2026-10-26), Stage B wins: research sweep, wide draft, visuals, independent pedagogical review, reduce and refine, in that order.

## The seven steps

1. **Collect references** into the module's references folder: articles, vendor documentation, internal material (Fundamentals modules, AI Accelerator sessions, existing platform/dbt/orchestration content, the Deloitte GenAI reference under `reference/Deloitte/GenAI`, DataCreators v4 under `reference/DataCreators-v4`, Catalyst resources). Reuse existing material rather than redeveloping it. Run the sweep with a research agent with web search and write it up as `deep-research-<date>.md`. Keep a `references.md` with every link: its URL, the date checked, what it is and what you took (and a licence or sensitivity note for anything copied).
2. **Generate a Markdown lesson** from those references, supplemented by web research where needed. Structure it by the brief's key questions; add subsections where a question needs more than one idea.
3. **Produce enough substantive material to select from**: more than will ship (the handbook ships 3,000 to 12,000 words, aiming for about 7,000), organised by the key questions and the session outcomes, in the research folder's `draft.md`. A drafting target, not a script.
4. **Check the session outcomes** in `internal-programme-overview.md` §6: which ones this module serves, and that the key questions are covered by them. Outcomes are owned at session level (about five per session, each mapped to modules in §6's Modules column, never as a tag on the outcome text); propose an edit there rather than inventing module outcomes. Each outcome is an observable demonstration. Preferred verbs: describe, explain, list, compare and contrast, write, design, annotate, create, discuss, analyse; request and refine where they describe the task clearly. Never: understand, know, appreciate, be aware of, be familiar with, grasp.
5. **Add diagrams, screenshots, images and assets** where they improve understanding; inspect each for accuracy and learning value. Python-generated figures preferred; Mermaid is fine for flows. A figure whose rows explain something lines them up with the thing it explains.
6. **Independent pedagogical review** of the draft and its assets, by a separate reviewer (a developer or a reviewer agent, never the author): missing foundations, overload, sequencing, suitability for adult learners, simplicity, vagueness and define-first, saved as `pedagogical-review.md`. A self-check never stands in for it.
7. **Reduce and refine**: topic knowledge stays in the handbook, in its main text or, if truly optional, its appendix after the Summary; only delivery detail (click paths, logistics, what to run when) moves to the lesson plan; record what moved where in `notes.md`; remove material with little learning value; fix unclear explanations and figures.

## Outcome format (session level; the example below is illustrative)

```
By the end of this session you will be able to:

- **Write** a Python script from a working notebook — same output, no notebook state, using the module's starter notebook
- **Compare and contrast** a notebook and a script for a daily report — naming two advantages of each, from the demo
- **Explain** what a virtual environment isolates — in two sentences a new joiner could follow, without notes
- **Create** a `requirements.txt` that reproduces the demo's environment — `uv pip install` succeeds in a fresh container
- **Describe** how Jordan's team at Harbourline would ship this script — naming the repository, the review step and the runner
```

Behaviour (verb) + standard (measurable, no "basic", "effectively", "confidently") + condition (tools, data, circumstances). Each outcome happens somewhere concrete: the challenge, the demo, a discussion box.

## CG rules checklist for the source stage

- [ ] Every key question from the brief appears in the `::: session` list and is answered.
- [ ] The module names the session outcomes it serves. Each clause's core is evidenced at Q1 or Q2 of its challenge; a clause evidenced only in the demo or debrief is said so in the lesson plan's Objectives table.
- [ ] `deep-research-<date>.md` and an independent `pedagogical-review.md` are in the research folder, and every link in the handbook is in `references.md`.
- [ ] Every design choice is the simplest version that works; every reference back is specific; every term is defined before its shorthand.
- [ ] CG context present: Harbourline, Jordan, the synthetic pack, reporting and historical performance; app/API examples too.
- [ ] "At CG" answers come from Catalyst with `source=`; unresolved ones recorded as a Slack question in the digest.
- [ ] Tools and alternatives written to `programme-profile` CG rule 2 (pros and cons, no limitation-led wording, review as good practice); no `<!-- sensitive: … -->` marker.
- [ ] Everything runs on the dev container and the local services, with no CG-access note or `::: blocked` box (`programme-profile` rule 3); nothing inferred from a public Databricks configuration.
- [ ] Nothing essential depends on `::: extra` or appendices.
- [ ] Figures introduced from above, captioned by their description (or a Mermaid caption comment), never numbered by hand; analogies drawn, with a "The proper words" line only where the figure does not label the mapping.
- [ ] Conventions match `lesson-build/references/markdown-conventions.md`.
- [ ] The lesson-plan block carries everything the learner should not read (no inline speaker notes).
