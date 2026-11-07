# Cohort 7 — Day 1 (Monday): designing data products, Catalyst, effective AI

Source: `extracts/cohort7/d1-transcript.txt`, `d1-ai-notes.txt`, `d1-agenda.txt`. Times are reconstructed from the transcript and the agenda.

## As delivered

| Time | What happened |
|---|---|
| 09:00 | Nicole: lunch voucher code (also in the Teams chat), step out quietly if you must, tell us if you'll be gone long. Leadership welcome video (Data Excellence; "trusted reusable data products"; hands-on; "the programme is still evolving, your feedback matters"). |
| 09:05 | Michael and Sophie introduce themselves (Michael: head of technical consulting at Decoded, software engineering and defence background, designs first iterations of programmes; Sophie: nine years in data roles, maths/statistics, MSc data science, AI engineering programmes). |
| 09:10 | Table challenge, part 1 (5 min): team, role, shared hobbies. Part 2 (10 min): brainstorm on paper the data products you work on and what is annoying about them. Groups told to write things down because later challenges reuse the list. |
| 09:30 | Hero (sponsor): the DXP operating model. See "Hero's talk" below. |
| 09:50 | Table share-out. Michael walks the room, names groups by "the first thing that happens" (Table of extreme agreement, Three Musketeers, Disagreeables, Team Monterey, Team Mumble, Point left…). Products and pain points listed below. |
| 10:05 | Course map and the Friday capstone. "What is a data product?" on the whiteboard. |
| 10:15 | Break to 10:30. |
| 10:30 | "How do you design a data product?" elicited on the whiteboard (the triage questions). |
| 10:40 | Group challenge: pick a product from the morning list (or propose a new CG product) and answer the non-technical questions; note the most interesting, surprising or difficult question. 20 minutes. Paper and a note taker. |
| 11:00 | Debrief by table, then lifetime value (costs and payoffs) and adoption (barriers and responses) elicited on the whiteboard. |
| 11:40 | Catalyst: what skills are, the GitHub repo, the data-contract skill template, lifecycle skills calling skills, skills with Python scripts. Live attempt at `/ai-catalyst product-requirements-document` with a pasted transcript. |
| 11:50 | Pair challenge: same product, independent PRDs, compare before lunch. Several learners could not see the Catalyst repo (access request raised; set up over lunch). |
| 12:00 | Lunch. |
| 13:00 | AI and effective AI practice lecture (about 40 minutes), then the Copilot interface walk-through (model picker, thinking effort, context window, compaction). |
| 13:45 | Break 15 minutes. |
| 14:00 | Interview challenge in threes (producer, consumer, creator) recorded with Apple Voice Memos; transcript into Catalyst for a PRD then a data contract. Groups re-mixed by counting off. |
| 14:35 | Debrief: what the generated documents got wrong; interviews vs observation vs surveys; PRD and contract sections; why the glossary lives in the contract; hallucinated revision history. |
| 14:50 | "Interview Catalyst": phases of the DPLC, requirements of the build phase, which have skills. End about 15:00. |

## Hero's talk (sponsor, ~20 minutes) — reusable framing

- Everyone is busy, AI raises expectations, and "AI without solid data is not good". Technologists have always made the data calls (which table, which key, which join) without the business context or the policy knowledge, which makes them accountable for decisions that are not theirs.
- Test: "Can you find the portfolio positions of fund BFA, with confidence it is the right table, in three seconds? Could a new associate do it in five minutes? Could AI?" Today the answer is no. The target: self-service on trusted data across the firm, governed (entitlements, aggregation policies, PII protected), usable by people and AI.
- Four personas: consumers (everyone, including the people in the room); platform providers (the EDO platform team; until 18 months ago the platform choice was Laser, Caspian, EMR, Databricks or Dremio; now one paved path with policies, standards, tooling, catalogs, metadata); business data owners (senior business people accountable per domain: client, results, positions, attribution, trades, research; the DXP site lists owners and stewards); data product creators ("the most important job": the intersection of platform, owner priorities and consumer needs; build for reuse, scale and resilience).
- Publishing to the right catalog with metadata and access controls replaces "ask a person for the data". Entry and intermediate level course, everyone must pass, apply it to real use cases straight after; questions the instructors cannot answer get logged for Hero's team.

## Products and pain points the room brought (reuse as examples)

- Client data platform: aligning the teams that own different client domains (retirement plan accounts vs investor accounts), discrepancies between sources.
- Positions and transactions from the accounting book of record: sourcing the right data per product type.
- Website behaviour / customer data platform: raw data exists but curated extracts depend on EDO bandwidth.
- Marketing engagement data (email, search): one person has multiple profiles; reconciling identities ("golden nominal" in policing).
- Enterprise search data: siloed on the vendor's platform.
- Attribution (equity, multi-asset; monthly and quarterly publishes): de-duplicating datasets ahead of the target state.
- Product reference data, Morningstar, indexes, the multi-portfolio system: "all the data all the time"; the social networking needed to align owners; many lineages and versions supported at once.
- Client sales flows; mastered client profiles (dedup, quality; "is 50 billion right or is it 50 million?"; correlation across products to judge correctness).
- Advisor data / CDM: one trusted current record per advisor office; consumers are sales, wholesalers, client services, marketing, compliance, sales finance; APIs and files; rigid contracts frustrate consumers with different lenses (contact details vs affiliations vs trading identities).
- Globalisation: North-America-centric data standards; less mature regions, regulatory differences.
- Michael's aside: firms exist to reduce transaction (alignment) costs; past a certain size the costs return, hence bureaucracy; alignment is the dominant cost as the business scales.

## Whiteboard scripts (questions, then the answers the room gave)

**What is a data product?** Promises: trusted, reusable, business-ready, accessible. Promises of what? A data set. Enforced how? Contracts and design documents, data quality checks, code running on infrastructure. Three views: (1) data set plus promises (creator/product-manager view); (2) data plus code plus infrastructure (platform/engineering view); (3) a transformation from source-aligned to consumer-aligned data, where alignment is relative to people's goals, not a technical property ("the other people over there built it for their interests, we realign it for ours"). What it is not: a bare source data set (Morningstar in a folder is Morningstar's product, not CG's), a consumer-aligned data set stranded without processes, code and infrastructure without realignment.

**How do you design a data product (triage questions)?** Who needs it? What is the business purpose? Does it already exist? What do people do now (workarounds)? Do we still need it? Then: can we build it, how (data exists? sources, transformations, platform, sensitivity/PII, delivery, update frequency, grain, when by)? Then the decision: is it worth it, viable, cost, does it deserve this priority now, lifetime value.

**Lifetime value — costs:** total cost of ownership and maintenance (teams), opportunity cost, licensing/data acquisition, development time, prioritisation, alignment/SME time ("an auction market for people's time would price it exactly"), adoption cost ("you being here is part of the cost of adopting the paved path"). **Payoffs:** consistency (price it by the alignment meetings it removes), consumer time saved (easy to price near revenue; "finance makes money because it sits where the value is observable"), new business opportunities ("good things in the right place"), trust/reduced churn, less friction, operational scale, lower transaction costs (that is what the paved path is), AI workflows and process efficiency, focus ("one way, let's go"). Leadership must make judgement calls on value that cannot be priced.

**Adoption — barriers:** integration difficulty, low trust (quality, payoff), liability ("blame me" as the leadership fix), lack of training, awareness, competing priorities, resistance and the cost of relearning, safety, doesn't support the use case / missold, planning overhead. **Responses:** leadership that absorbs liability and evangelises, show the value (a demo beats an abstract pitch; record the walkthrough), training, comms campaigns and announcements, deadlines (force prioritisation), documentation, reliable follow-through.

**Catalyst:** a repo of AI skills (saved prompts in Markdown) aligned to CG policy; the data-contract skill's template (identity, schema, SLAs, data quality, access, change management, consumer registry, approvals, revision history); lifecycle skills (design) call requirements-acceptance-criteria, feasibility-report, consumer-use-case-map, data-modeling; some skills ship Python (search Databricks, run jobs); DPLC concierge "takes a long time to run, start it Friday and you may have a product Monday" so prefer specific skills. In Copilot chat type `/` and pick `ai-catalyst ...`; when it is really Catalyst you see "reading skill file".

**AI lecture outline (13:00):** definitions (AI as a project to automate tasks that need intelligence; intelligence as the strategy animals use when there is no known solution; computer scientists define it by the solved problem; generative AI is a proxy model operating in the text domain, it cannot simulate the future, only describe it); discriminative vs generative; LLM training (the internet and e-books as corpus; vendors now harvest their own chat traffic as human signal; training on model output collapses quality, compression analogy; instruction fine-tuning with paid annotators; RLHF with experts; code is the one domain where preference can be automated, hence LLMs are good at code; "it runs" is a weak quality signal); costs (order of $50M to train a frontier model, hundreds of millions a month to run; inference is the moat now); inference and reasoning (hidden intermediate tokens; domains with written-out reasoning like cybersecurity and maths do well); tool calls (JSON) interpreted by a harness (VS Code/Copilot; "Claude is the harness, Opus is the model"); agent = harness + LLM; skills = prompts that trigger tool calls. Interface: model picker (Opus least compressed, Haiku most; GPT Sol/Terra/Lunar likewise; more context in the prompt means model quality matters less; choice is empirical; OpenAI tends literal, Anthropic tends preference-driven), thinking effort (hidden token budget; maximum can be worse on simple questions; medium/high is the sensible default), context window (about 800k characters ≈ 100k words including hidden reasoning and tool calls; non-trivial tasks take about a million tokens; performance degrades as it fills; compaction is random, so summarise to a file and start a new conversation yourself).

**Interview challenge (14:00):** Apple Voice Memos demo (record, pause, done, transcript tab, copy transcript; "free and good enough"; Teams/Zoom transcripts also fine). Roles: producer (knows the upstream source), consumer (knows the decision and desired result), creator (interviews both). The seven questions: what decision do you make with the data; how do you make it today; who uses the result directly; how is the source generated; what do these terms mean in your work; how do you recognise a usable result; when do you read the result. Add your own. Stay in role until it breaks down, then help each other. Transcript → Catalyst PRD → data contract.

**Debrief lines:** "It always generates something; it can't not generate." Fixed-income analytics group: SME said the fees were wrong, generic internet knowledge; pointing Catalyst at the internal source (Nexus) fixed it; PRDs look better because they are vaguer. Products catalogue group: asked for universal attributes, got CUSIP/ticker/ISIN but incomplete. Another: scope too broad, one wide table instead of normalised. Requirements discovery: interview (dynamic follow-up; people lie or are confused), observe (revealed behaviour; "design from purgatory, not technical heaven"), survey (scale), read their documents and code. PRD sections: executive summary, use case, problem/value, consumers, solution overview, what this is not, requirements, roles, success criteria, technical design, version. Contract sections: schema, data quality, dependencies, glossary (because upstream vendors define their own terms), change management (version 0 already had hallucinated breaking changes). Interview Catalyst: DPLC phases (prereq, triage, discovery, design, build, validate, publish, operate, evolve — nine), build-phase requirements (PRD, data contract, data model, transformation spec) and their skills; "you can ask Catalyst what it needs before you use a skill".

## Issues seen

- Catalyst plugin not working for some; GitHub repo `cg-open-itg/catalyst` "not found" for several learners (needs the GitHub team membership; Access Central → Manage user access → copy another user's entitlements). Expect a lunchtime setup scramble.
- Michael's own second laptop did not have Catalyst; the first demo ran plain Copilot (no "reading skill file" line).
- Transcript/recording discipline: the course transcript is taken on a laptop with Voice Memos; closing the lid stops it.
