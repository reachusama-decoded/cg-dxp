# Day 1 run sheet — Product discovery and effective AI use

Instructor-only companion to the anchor notebook, in the notebook's order: the same numbered sections and labelled parts, each with its time, purpose, what is on screen, what to say, what to ask at the whiteboard (with the answers rooms give and what to add), the demo steps with their coaching, fallbacks, the transition and what to do if ahead or behind. Keep the notebook on the projector and this beside it. Times follow the instructor plan; adapt them to the room and keep the sequence.

## Sections

| # | Section | Time | What happens |
|---|---|---|---|
| 1 | Welcome, the room and the operating model | 09:00–10:30 | Welcome · Activity 1: introductions and pain points · Guest: the DXP operating model · Shareback: products and pain points · Whiteboard: what is a data product? · Break |
| 2 | Discovery, justification and Catalyst | 10:30–13:00 | Whiteboard: how do you design a data product? · Activity 2: justify a product · Debrief · Whiteboard: lifetime value and adoption · Demo: Catalyst · Activity 3: compare independent PRDs · Lunch |
| 3 | AI foundations and effective practice | 13:00–13:55 | Whiteboard: the seven ideas · Demo: the interface on the running example · Break |
| 4 | Interview, generate and the lifecycle | 13:55–15:00 | Demo: Voice Memos to transcript · Activity 4: interview and generate · Debrief: requirements discovery · Reflect: the planted-errors contract · Activity 5: explore the lifecycle · Before learners leave |

## Timeline

| § | Time | Block | Type | On screen |
|---|---|---|---|---|
| 1 | 09:00–09:15 | Welcome and introductions | Intro | Anchor › Welcome; the week map |
| 1 | 09:15–09:30 | Activity 1 — Introductions and pain points | Group activity | Anchor › Activity 1 card |
| 1 | 09:30–09:45 | Sponsor contribution | Talk | Anchor › The DXP operating model (personas diagram) |
| 1 | 09:45–10:05 | Table share-out | Debrief | Anchor › The room's products (type into the table live) |
| 1 | 10:05–10:15 | What makes a data product | Teach | Anchor › What is a data product (two diagrams) |
| 1 | 10:15–10:30 | Break | Break | Agenda |
| 2 | 10:30–10:40 | Discovery and product justification | Teach | Anchor › Discovery questions (triage diagram) |
| 2 | 10:40–11:00 | Activity 2 — Justify a product | Group activity | Anchor › Activity 2 card |
| 2 | 11:00–11:25 | Debrief | Debrief | Anchor › Debrief and lifetime value |
| 2 | 11:25–11:40 | Lifetime value and adoption | Teach | Anchor › Lifetime value and adoption (mindmap) |
| 2 | 11:40–11:50 | Catalyst demonstration | Demo | Catalyst skills repo, then Copilot Chat (or Claude Code) |
| 2 | 11:50–12:00 | Activity 3 — Compare independent PRDs | Pair activity | Anchor › Activity 3 card |
| 2 | 12:00–13:00 | Lunch | Break |  |
| 3 | 13:00–13:40 | AI foundations and effective practice | Teach + demo | Anchor › AI foundations (two diagrams), then the Copilot interface |
| 3 | 13:40–13:55 | Break | Break |  |
| 4 | 13:55–14:25 | Activity 4 — Interview and generate | Group activity (threes) | Anchor › Activity 4 card, Voice Memos |
| 4 | 14:25–14:45 | Debrief and requirements discovery | Debrief | Anchor › Debrief (discovery methods diagram), planted-errors contract |
| 4 | 14:45–15:00 | Activity 5 — Explore the lifecycle | Individual, then tables | Anchor › Activity 5 card |

## 1. Welcome, the room and the operating model

### Welcome — the week, and the people in the room · 09:00–09:15

**Purpose.** Logistics, the sponsor's welcome video if there is one, the facilitators, and the rule that every data product mentioned gets written down.

**On screen.** Anchor › Welcome; the week map

**Instructor notes.**

- Hours 09:00–15:00, lunch 12–13, breaks mid-morning and mid-afternoon; Friday finishes when presentations do.
- Paper and pens on every table; one visible list of the room's products starts now and is reused on Days 1 and 2.
- A guest may arrive to speak at 09:30; if so, keep Activity 1 to fifteen minutes and hold the share-out until after them.

**Say.**

- “Everything you write down about a data product this week, you will use again. Nobody keeps it in their head.”
- “The transcript of this week is yours at the end: if you want to listen rather than write, you can.”

**Say.**

- “Write every data product you mention this week on the paper in front of you. You will use that list on every day.”
- “Hands up: who has used dbt? Airflow? Docker? Harness? Bitemporal loading in production? You are the people I will ask to go first on Thursday.”

**Transition.** Introduce the first activity: five minutes on people, ten on products and their pain points.

**If ahead or behind.** Running late: cut the facilitator introductions to names and one line each.

### Activity 1 — introductions and pain points · 09:15–09:30

**Purpose.** Everyone speaks once, and the room produces the list of real products that every later activity draws on.

**On screen.** Anchor › Activity 1 card

**Instructor notes.**

- Walk the tables; insist on a note taker and the written list.
- Give groups a name as soon as something memorable happens; use the names all day.

**Say.**

- “Five minutes: team, role, a shared hobby. Ten minutes: the data products you work on, and gossip about what is wrong with them. Write them down.”

**Activity 1 — Introductions and pain points.** Tables, 15 min; the card is in `activities/`.

**Transition.** If the sponsor has arrived, hand over; otherwise go straight to the share-out.

**If ahead or behind.** If a guest is late, extend to twenty minutes and start the share-out.

### Guest — the DXP operating model: the sponsor, or the fallback below · 09:30–09:45

**Purpose.** Why the programme exists: trusted self-service data for people and AI, four personas, the creator at the intersection.

**On screen.** Anchor › The DXP operating model (personas diagram)

**Instructor notes.**

- If nobody comes, give the instructor-led version from the anchor (five minutes) and move on.
- Capture any promise made to the room (questions logged, access help) in the Q&A table.

**Say.**

- “Can you find the positions of one fund, with confidence it is the right table, in three seconds? Could a new joiner in five minutes? Could AI? That gap is the job.”

**If it breaks.** No sponsor today? Give the opening yourself in five minutes, then move on.

- The three-second test, the four personas and the publishing promise, from the anchor.
- Log every question about access or policy in the Q&A table for the platform team.

**Transition.** Back to the tables' lists: the share-out.

**If ahead or behind.** A long guest Q&A eats the share-out; move the share-out into the data-product block and shorten it.

### Shareback — products and pain points · 09:45–10:05

**Purpose.** Collect each table's products and pain points into one visible list; connect pain points to the week's themes.

**On screen.** Anchor › The room's products (type into the table live)

**Instructor notes.**

- One table at a time: name, products, the sharpest pain point. Type them into the anchor's table as they come.
- Probe once per table: who makes a decision with it? what makes it untrustworthy? Alignment and sourcing pain points come up every cohort.

**Say.**

- “I am going to say this back to you on Wednesday: most of what is wrong with these products is alignment, not technology.”

**Ask at the whiteboard — share-out probes.** Ask in order, write what the room says, add what is missing.

| Ask | Expect, then add |
|---|---|
| Who makes a decision with this product? | An API or a dashboard is not the end; follow it to the person. Sales planning, compliance, risk, a client-facing app. |
| What makes it untrustworthy? | Rooms say: sourcing the right table, duplicated profiles for one person, conflicting sources, data entry errors (an extra zero), vendor files that change shape, aligning the teams that own each domain. |
| Why does alignment cost so much here? | Firms exist to reduce transaction costs; past a certain size the costs come back. One change upstream means a dozen meetings downstream. The paved path exists to push those costs down again. |

**Transition.** Ask: so what is a data product, if the data alone is not one?

**If ahead or behind.** Skip tables that duplicate an earlier product; ask them only for a new pain point.

### Whiteboard — what is a data product? · 10:05–10:15

**Purpose.** Promises, assets and alignment as three views of one thing; what a data product is not; the capstone previewed.

**On screen.** Anchor › What is a data product (two diagrams)

**Instructor notes.**

- Elicit before showing: ask for properties, then whose properties, then how they are enforced.
- Say the capstone line once: on Friday you build one on the paved path and we watch you do it.

**Say.**

- “Alignment is about people, not code. There is no test you can run on a table that says consumer-aligned.”

**Ask at the whiteboard — what is a data product.** Ask in order, write what the room says, add what is missing.

| Ask | Expect, then add |
|---|---|
| What properties does a data product have? | Trusted, reusable, business-ready, accessible. Then ask: properties of what? A data set. |
| How are the promises enforced? | Contracts and design documents; data quality checks; code that runs on infrastructure. Three views of one thing: promises (creator), assets (platform), alignment (consumer). |
| Is Morningstar's file in a folder a data product? | Morningstar's, yes. Ours, no: it is source-aligned, built for their interests. Our product is the realignment to our consumer's decision. |
| What does 'aligned' mean? | Relative to people and their goals. No code or test tells you a table is consumer-aligned. |
| What is a data product not? | A bare source data set; a consumer-shaped extract with no processes behind it; code and infrastructure that do no realignment. |

**Say.**

- “On Friday you get CSV files about funds and trades, and the goal is a data product on Databricks that we have watched you build. Phase 1 is the certification bar. Monday to Thursday exist to get you there.”

**Transition.** Break. On return: how do you design one?

**If ahead or behind.** Over time: show the alignment diagram and skip the elicitation.

> ☕ Break · 15 min · back at 10:30

## 2. Discovery, justification and Catalyst

### Whiteboard — how do you design a data product? · 10:30–10:40

**Purpose.** The questions a creator asks before anything is built: who, what for, exists?, can we, worth it.

**On screen.** Anchor › Discovery questions (triage diagram)

**Instructor notes.**

- Write the room's questions, then regroup them under the four headings.
- Keep 'how do we build it' explicitly for later in the week.

**Say.**

- “If someone comes to you and says we need a data product, what is the first thing you ask?”

**Ask at the whiteboard — how do you design a data product.** Ask in order, write what the room says, add what is missing.

| Ask | Expect, then add |
|---|---|
| Someone says we need a data product. First questions? | Who needs it? What is it for (the business problem)? Does it already exist? What do people do now? Do we still need it? |
| Suppose yes to all. Now what? | Can we build it, and how: does the data exist, sources, transformations, platform, sensitivity and PII, delivery method, update frequency, grain, when it is needed by. |
| And then? | The decision: is it worth it, is it viable, what does it cost, does it deserve this priority now, what is its lifetime value. |

**Transition.** Introduce Activity 2.

### Activity 2 — justify a product · 10:40–11:00

**Purpose.** Each table justifies one product from the list with the non-technical questions and finds its hardest question.

**On screen.** Anchor › Activity 2 card

**Instructor notes.**

- Circulate and push past the API: who makes the decision at the end?
- Early finishers take a second product.

**Say.**

- “Prioritise the non-technical questions. We spend the rest of the week on how to build it.”

**Activity 2 — Justify a product.** Tables, 20 min; the card is in `activities/`.

**Transition.** Debrief table by table: product, then the hardest or most surprising question.

**If ahead or behind.** Twenty minutes is firm; the debrief absorbs overrun.

### Debrief · 11:00–11:25

**Purpose.** Follow each product to the person deciding; name the consumer and the business owner; surface the unresolved question.

**On screen.** Anchor › Debrief and lifetime value

**Instructor notes.**

- Advisor and client master data, global definitions and fragmented engagement data are the examples rooms bring.
- Press for a business owner by name or role; 'EDO' is not an owner.

**Say.**

- “What changes for the person using this?”

**Ask at the whiteboard — Activity 2 debrief.** Ask in order, write what the room says, add what is missing.

| Ask | Expect, then add |
|---|---|
| What was the data product, and what was the hardest question? | Adoption comes up first: many consumers with different lenses, rigid API contracts, who owns it. Press for the business owner by role. |
| What changes for the person using this? | Follow the product past the API to the decision: sales planning, compliance, a client app. If nobody can name the person, the product is not yet justified. |
| Globalisation, less mature regions, regulation: what kind of problem is that? | It cuts across: can we build it (standards differ), is it worth it (alignment costs), will it be adopted. |

**Transition.** Those costs and barriers you just described: let's price them.

### Whiteboard — lifetime value and adoption · 11:25–11:40

**Purpose.** Costs and payoffs of a product over its life; why products fail on adoption and what to do about it.

**On screen.** Anchor › Lifetime value and adoption (mindmap)

**Instructor notes.**

- Elicit costs, then payoffs, then barriers, then responses; the anchor lists what rooms say.
- The paved path itself is an adoption programme; this week is part of its cost.

**Say.**

- “Things get prioritised the closer they sit to the money, not because they are better products. Far from the money, you have to get creative about value.”

**Ask at the whiteboard — lifetime value and adoption.** Ask in order, write what the room says, add what is missing.

| Ask | Expect, then add |
|---|---|
| What does a data product cost over its life? | Maintenance and total cost of ownership (teams), opportunity cost, licences and data acquisition, development time, prioritisation, SME and alignment time, the cost of adoption itself (training, communication; this week is one). |
| What are the payoffs? | Consistency (fewer alignment meetings), consumer time saved, new business opportunities from data being in the right place, trust and less friction, operational scale, lower transaction costs, data that AI workflows can use, focus. |
| Why do data products fail? | Lack of adoption. Barriers: integration difficulty, low trust in quality or payoff, liability, no training, no awareness, competing priorities, the cost of relearning, it does not fit the real use case. |
| What do we do about it? | Leadership takes the liability and evangelises; show the value (a demo beats an abstract pitch; record it); training; communication campaigns; deadlines; documentation; reliability in your own commitments. |

**Transition.** To write any of this down formally we use Catalyst.

**If ahead or behind.** Cut the responses list to three if behind.

### Demo — Catalyst: a skill is a prompt · 11:40–11:50

**Purpose.** What a skill is, the data-contract template, lifecycle skills calling skills, scripts; one PRD generated from a transcript.

**On screen.** Catalyst skills repo, then Copilot Chat (or Claude Code)

**Instructor notes.**

- Open the skills README and the data-contract SKILL.md with its eight sections.
- Generate from the running-example transcript; if the plugin is not installed on the demo laptop, show Claude Code with the same skill and say why.
- Check learners see 'reading skill file' in their own Copilot; those who do not are on the lunchtime setup list.

**Say.**

- “A skill is a saved prompt that someone at CG has already tested. The concierge runs all of them and takes an age; use the specific one.”

**Demo — the data-contract skill, then a PRD from the transcript.** A Catalyst skill is a prompt file: watch one run on the transcript, then find the invented detail.

1. Open `.claude/skills/data-contract/SKILL.md` (installed by `common/catalyst/install-skills.sh`; the same file learners see in the Catalyst repo): the eight required sections and the quality checks.
2. Open `.claude/skills/data-contract/templates/data-contract.md`: identity, schema, SLAs, quality rules, access, change management, consumer registry, approvals, revision history.
3. Open `.claude/skills/dplc-design/SKILL.md`: it chains requirements-acceptance-criteria, feasibility-report, consumer-use-case-map and data-model.
4. Open `.claude/skills/dplc-concierge/SKILL.md` and say: start it Friday, maybe a product by Monday.
5. Learners' form: Copilot Chat, `/ai-catalyst product-requirements-document`, paste a description.
6. Instructor's form: Claude Code in `courseware/`, `/product-requirements-document`, paste `common/running-example/interview-transcript.md`.
7. Point at the moment the skill file is read: that is how you know Catalyst is on, not plain Copilot.
8. Read one section of the result aloud and find the invented detail before accepting anything.

**If it breaks.** Catalyst not installed or slow on the demo laptop: review the prepared PRD instead; the lesson survives without the generation.

- Open `common/running-example/prd.md`: the reviewed output, with the corrections in brackets.
- Walk the Key Product Information, Problem and Value, and Consumers sections.

**Transition.** Pairs: same product, hidden descriptions, compare.

### Activity 3 — compare independent PRDs · 11:50–12:00

**Purpose.** See how input detail changes the output, and that a tidy document can contain invented fields, owners and approvals.

**On screen.** Anchor › Activity 3 card

**Instructor notes.**

- Keep to one or two differences per pair.
- Have the planted-errors contract ready for the debrief if live outputs are clean.

**Say.**

- “Hide your description from your partner until both documents exist.”

**Activity 3 — Compare independent PRDs.** Pairs, 10 min; the card is in `activities/`.

**Transition.** Lunch. Anyone without Catalyst working: set it up now, help is here.

**If ahead or behind.** If Catalyst is broken for many, run it as a discussion of the planted-errors contract instead.

> 🍽️ Lunch · 60 min · back at 13:00

## 3. AI foundations and effective practice

### Whiteboard — the seven ideas, in order · 13:00–13:40

**Purpose.** Models, training, inference and reasoning, tool calls, harnesses, agents and skills; then settings, context and output review on a real task.

**On screen.** Anchor › AI foundations (two diagrams), then the Copilot interface

**Instructor notes.**

- Follow the seven-step order in the anchor; keep the theory to twenty minutes so the interface demo gets fifteen.
- Show model choice, thinking effort and the context window on the running example; say which models CG exposes this week.

**Say.**

- “It generates text. Whether that text is any good at your task is an empirical question: try it, measure it.”

**Ask at the whiteboard — the seven ideas, in order.** Ask in order, write what the room says, add what is missing.

| Ask | Expect, then add |
|---|---|
| 1. What is AI? What is intelligence? | A project to automate tasks that need intelligence in people; intelligence as what animals do when there is no known solution. Discriminative (label, predict) vs generative (produce something like what it has seen). An LLM works in text: words in, words out; it does not simulate. |
| 2. How is a model trained? | A corpus (the internet, books, now vendors' own chat logs), compressed by pre-training; instruction tuning with paid examples; preference tuning with experts. Code is checked by running it, so models are strong at code. 'It runs' is a weak signal. |
| 3. What is inference and reasoning? | Running the model. Reasoning is hidden intermediate tokens the vendor generates for you; it is where the running cost goes. Domains with written-out working (maths, security) do well. |
| 4. What is a tool call, a harness, an agent, a skill? | JSON the model emits; a program that executes it (VS Code/Copilot, Claude Code); the two together; a saved prompt that triggers tool calls. |
| 5. Which model? | Bigger models are less compressed; with lots of context the model matters less. Empirical: try it on your task. Vendors differ in how literal they are. |
| 6. Which settings? | Thinking effort is a hidden token budget; maximum can be worse on simple tasks. The context window fills with everything including hidden reasoning; performance degrades; compaction is automatic and random. Summarise to a file and start a new conversation. |
| 7. How do I know it worked? | Be sceptical where your task is novel or internal (your source systems, your definitions). Measure on your actual task; keep your own model of where it is reliable. |

### Demo — the interface on the running example · 13:00–13:40

**Demo — the interface on the running example.** Copilot Chat and Claude Code side by side: model, effort and context, on one real task.

1. Open Copilot Chat (what learners see) and Claude Code (this laptop) side by side.
2. Model picker: name this week's models; say which is least compressed and most expensive.
3. Thinking effort: ask the same question at low and at maximum; compare the time and the answer.
4. Context: show the conversation length, then `/clear` in Claude or a new chat in Copilot; say when to do it.
5. The task: "Add realistic SLAs to this contract" with `common/running-example/data-contract.md` attached.
6. Then: "List every number in the SLA section and where it came from."

**Transition.** Break, then the interview.

**If ahead or behind.** Over time: drop the training-data history, keep tool calls, harness, context.

> ☕ Break · 15 min · back at 13:55

## 4. Interview, generate and the lifecycle

### Demo — Voice Memos to transcript · 13:55–14:25

**Purpose.** Turn a producer-consumer interview into a transcript, a PRD and a data contract, then inspect them.

**On screen.** Anchor › Activity 4 card, Voice Memos

**Instructor notes.**

- Re-mix groups by counting off.
- Five minutes to choose product and roles, fifteen for questions, ten to generate and inspect.
- If generation is slow, keep the notes and review one shared output on screen.

**Say.**

- “Stay in role until it breaks down, then help each other. The creator asks; the other two answer from what they know.”

**Demo — Voice Memos to transcript.** A recording on the laptop becomes the transcript Catalyst reads: free and good enough.

1. Open Voice Memos on the Mac; record thirty seconds of a mock interview; pause; Done.
2. Click Transcript to show the text; click off and on again, then Copy transcript.
3. Say: on Teams or Zoom the meeting transcript does the same job.
4. Paste the transcript into the Catalyst prompt.

### Activity 4 — interview and generate · 13:55–14:25

**Activity 4 — Interview and generate.** Threes, 30 min; the card is in `activities/`.

**Transition.** Debrief: what did the documents get wrong?

**If ahead or behind.** Thirty minutes is firm; generation can finish during the debrief.

### Debrief — requirements discovery · 14:25–14:45

**Purpose.** Inspect outputs for wrong identifiers and generic knowledge; compare interviews, observation and surveys; walk the PRD and contract sections.

**On screen.** Anchor › Debrief (discovery methods diagram), planted-errors contract

**Instructor notes.**

- Ask each group for one invented detail.
- Use the planted-errors contract if live outputs give nothing clear.
- Include revision history among the things to check.

**Say.**

- “It always generates something. The question is what context it needed and did not have.”

**Ask at the whiteboard — Activity 4 debrief.** Ask in order, write what the room says, add what is missing.

| Ask | Expect, then add |
|---|---|
| What did the generated documents get wrong? | Wrong or missing identifiers and fields; generic internet knowledge where internal source knowledge was needed; scope left open; one wide table instead of a sensible structure; a revision history for a document that has none. |
| How else could we discover requirements? | Interview (dynamic follow-up), observe (revealed behaviour, workarounds), survey (scale), read their documents and code. Interview first; observe when people cannot say what they do; survey when there are hundreds. |
| What are the sections of a PRD? | Summary, problem and value, consumers and use cases, solution and what it is not, data requirements, technical design, governance, success criteria, catalog metadata, approval. |
| And of a data contract? Why is the glossary there and not in the PRD? | Identity, schema, SLAs, quality rules, access, change management, consumer registry, approvals, revision history. The glossary sits with the contract because upstream sources define their own terms; alignment of meaning happens there. |

**Transition.** Last ten minutes: ask Catalyst about itself.

### Activity 5 — explore the lifecycle · 14:45–15:00

**Purpose.** The nine DPLC phases, the build-phase prerequisites and the skills that support them, checked against guidance; artefacts saved.

**On screen.** Anchor › Activity 5 card

**Instructor notes.**

- 14:45–14:55 ask Catalyst; 14:55–15:00 one correction per table with evidence.
- Collect: product notes, transcript, PRD, contract, open questions.

**Say.**

- “You can ask Catalyst what it needs before you use a skill. Do that tomorrow before you ask it for code.”

**Activity 5 — Explore the lifecycle.** Individual, then tables, 15 min; the card is in `activities/`.

**Transition.** Tomorrow: mappings and service levels on today's contract, then the platform.

## Before learners leave

- [ ] Product notes, interview transcript, reviewed PRD, data contract and open questions saved together (one folder per group, named by group).
- [ ] Each learner can name one correction they made to a generated document and why.
- [ ] The list of the room's products is captured in the anchor's table for tomorrow.
- [ ] Anyone whose Catalyst plugin or dev container is not working is on a list with a named next action.
