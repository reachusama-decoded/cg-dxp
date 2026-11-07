---
name: courseware-conventions
description: The Decoded house rules for any training courseware — voice and tone, brand colours and components, learning-outcome format, pedagogy (super learning embodied, never named), delivery-mode rules, the Decoded default tech stack (which the CG Core profile overrides) and how to find the programme profile that personalises them. Read this before writing or revising ANY learner- or instructor-facing content — lessons, session openings, speaker notes, demos, challenges, READMEs, figures — even when the user only asks to "tidy the wording", "fix the outcomes" or "make this sound like Decoded". Every other courseware skill (module-source, module-demo, module-challenge, module-self-review, module-review, module-materials, module-audit, lesson-build) depends on it.
---

# Courseware conventions

The Decoded-wide foundation that every courseware skill reads first. It carries what is true for *every* Decoded programme. Anything that varies by programme (audience, persona, session shape, timings, stack overrides, per-session decisions) lives in that programme's **profile** — see below.

## 1. Find the programme profile first

Every programme repo carries its own profile skill at `<repo root>/.claude/skills/programme-profile/`. Locate it by walking up from the folder you are working in until you find `.claude/skills/programme-profile/SKILL.md`. In this repo the profile is **CG Core**.

- **Found** → read its SKILL.md in full before anything else. It states the programme name, audience, delivery mode, module anatomy, timing, persona, stack overrides, CG rules, and where its per-session decision digest lives. Profile rulings override the defaults in this skill wherever they conflict.
- **Not found** → stop and say so. Offer to create one by copying this repo's `programme-profile` layout (SKILL.md · references/structure, conventions, stack, layout · digest/). If the user wants to proceed without one, use the Decoded defaults here and label every programme-level assumption you make in your brief, so the user can correct it before you build.

Never invent programme facts (persona, session titles, unit names, timings, client names). If the profile does not say, ask.

## 2. Non-negotiables for every programme

- **Voice**: short, punchy, no fluff, no hedging, no jargon. The master is [references/tone-of-voice-guidelines.txt](references/tone-of-voice-guidelines.txt); the house additions (banned words, paragraph length, first-use rule and define-before-shorthand, be specific, say what learners do rather than summarise the topic, day-one test, sourced claims) are in [references/writing-rules.md](references/writing-rules.md).
- **Learning outcomes**: about four, opened with "By the end of this session … will be able to:", each a full three-element objective — measurable **behaviour** (action verb, never "understand"/"know") + **standard** (quantifiable) + **condition** (circumstances/tools). Master: [references/learning-outcomes-guidelines.txt](references/learning-outcomes-guidelines.txt); house format in writing-rules.md §Outcomes.
- **Pedagogy embodied, never named**: core-first sequencing, why-explanations, attribute comparisons, emotional hook before logic, failure-first demos, predict-before-run, retrieval checks at the seams. No "retrieval practice" or "Feynman" in learner text. Detail: [references/pedagogy.md](references/pedagogy.md).
- **Delivery mode honesty**: the profile says online, in-person, or in person first and virtual-safe. Online: chat votes, ✅ reaction syncs, breakout rooms only for blocks of 10+ minutes, never sketching, show-of-hands or "person next to you". In-person: discussion boxes with folded answers, no chat mechanics. Rules for all: pedagogy.md §Delivery modes.
- **Brand furniture**: on notebooks, the Decoded title cell and footer cell (catalogue: [references/brand-components.md](references/brand-components.md)); on Markdown-to-PDF material, the programme's build theme and callout vocabulary (`lesson-build`). Brand colours and the diagram palette apply everywhere.
- **Code is self-explanatory**: inline comments on every code cell, files simple enough to read in full, every rule in prose says why it exists.
- **Link to the exact file**: the challenge README, the demo README, the appendix section. Never "see the practice folder".
- **Never promise the future**: no "later in the programme covers this", no naming the session or module where a skill is taught, in learner-facing text. The session stands on its own (a session opening may list what its pair covers, because learners choose pairs on that).
- **Nothing identifiable**: synthetic data only, invented organisations, invented people. Invented characters default to they/them pronouns unless the profile records a deliberate exception.

## 3. Default tech stack (Decoded-wide; the profile overrides)

**CG Core overrides parts of this** — see `programme-profile/references/stack.md` (LangChain as here, but configured from `.env` rather than `secrets.txt`, the Decoded proxy's base URL and OpenRouter model ids, keys not guaranteed so fixtures required, local Docker ports). The defaults below describe other Decoded programmes and apply here only where the profile is silent.

- **LLM calls through LangChain** (`ChatOpenAI`, `.invoke().content`), never a direct provider SDK. Default model `gpt-5-nano`, no `temperature` (gpt-5 models reject it), `timeout` of 20s or more.
- **Keys from `secrets.txt`** at the session root, loaded with `python-dotenv`; never pasted into cells. Keys are guaranteed in the learner environment, so: no keyless fallbacks, no `HAS_KEY` branches, no local models standing in for an API call. A missing key is an error surfaced at setup ("tell the instructor"), not a silently degraded session.
- **Setup cells are minimal**: package check + key load + file checks + `MODEL_NAME`. Other plumbing sits beside the code it serves.
- **Served apps follow the Decoded lab pattern**: bind `0.0.0.0`, port 2000–9000 (never 80, 22, 8001–8003, 8005), public URL `https://<port>-lab<N>.labs.decoded.com/`. Exact commands per framework, the server lifecycle helper and the key-loading snippet: [references/tech-stack.md](references/tech-stack.md). The profile keeps the programme's port registry.

## 4. Where each reference goes

| Read | When |
|---|---|
| [tone-of-voice-guidelines.txt](references/tone-of-voice-guidelines.txt) | Every content pass. The authority on voice; never edit it. |
| [writing-rules.md](references/writing-rules.md) | Writing or revising any prose, outcomes, headings, tables, activity names. |
| [brand-components.md](references/brand-components.md) | Producing a demo notebook's title or footer cell; the colour and diagram palette for figures. (AIA activity boxes and tiers are not used in CG Core.) |
| [pedagogy.md](references/pedagogy.md) | Designing a session flow, an activity, a challenge ramp, an interactive beat, or choosing delivery mechanics. |
| [learning-outcomes-guidelines.txt](references/learning-outcomes-guidelines.txt) | Writing or checking outcomes. |
| [tech-stack.md](references/tech-stack.md) | Any LLM call, key handling, served app, or background server — after reading the profile's `stack.md`, which overrides it for CG Core. |
| [diagrams.md](references/diagrams.md) | Any mermaid, matplotlib figure, chart or concept card. |

## 5. Keeping this skill honest

This skill holds only what is true across programmes. When a user ruling applies to one programme, record it in that programme's profile (its `references/conventions.md` or the session's digest), not here. When a ruling is clearly Decoded-wide ("never show-of-hands online", "footer on every notebook"), it belongs here — add it with the date it was confirmed.
