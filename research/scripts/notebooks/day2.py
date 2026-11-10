"""Day 2 — Mappings, service levels, the platform and Docker (revised 10 Nov 2026 after Day 1 as delivered)."""
import dc
DAY, SLUG, TITLE = 2, "day2-platform", "Mappings, service levels, the platform and Docker"

BLOCKS = [
 dict(time="09:00–09:25", title="Day 1 recap and the map of the week", type="Shareback", on_screen="Anchor › Recap (alignment diagrams); the room's products list",
      purpose="Reclaim yesterday in the learners' words, place the contract in the source-, domain-, consumer-aligned picture, and show where today and the rest of the week fit.",
      notes=["Ask, write, add: what is a data product, what did discovery teach, what did the generated documents get wrong.", "The alignment whiteboard is new: keep it to the three one-liners and the running example.",
             "Say the two musts for today: the design documents before the break, Docker done by the end of the day."],
      say=["Yesterday you made the why and the what. Today the what becomes precise enough to implement, and you build the box it runs in.",
           "Source-aligned is their shape, consumer-aligned is your reader's shape, domain-aligned is the firm's shape agreed once."],
      transition="The core of the contract you did not write yesterday: the mapping.", flex="Running late: skip the discovery recap; keep the alignment picture."),
 dict(time="09:25–09:45", title="Mappings and service commitments", type="Demo", on_screen="Anchor › STTM and service levels (two diagrams, nines table)",
      purpose="Source-to-target mapping rule types; SLI, SLO and SLA as measure, ideal, tolerance; the indicators a product needs; availability in nines.",
      notes=["Elicit rule types on the whiteboard; Catalyst returns a CG-specific list, say so.", "The nines table is in the anchor; say the month, week, day, hour, minute mnemonic.",
             "Last five minutes: screen-share the running example (03-data-contract.md sections 2 to 4, 04-sttm.md, 05-service-levels.md) so they see a finished one before extending their own."],
      say=["An SLI is a number you can measure. An SLO is what you wish it were. An SLA is how far it may stray before you owe someone an explanation.",
           "This is what yours will look like in thirty minutes: one rule per column, row rules beneath, a number and a clock on every commitment."],
      transition="Activity 6: put both into yesterday's contract.", flex="Running late: skip how providers get nines; keep the table."),
 dict(time="09:45–10:15", title="Activity 6 — Extend the contract", type="Challenge", on_screen="Anchor › Activity 6 card",
      purpose="Ask Catalyst for the transformation types and service measures, then add realistic STTM rules and commitments to a Day 1 contract.",
      notes=["Transcribe the table's rule discussion and feed it in, as on Day 1.", "Collect one revised contract per table for the review block."],
      say=["Be specific enough that someone else could implement the rule without asking you what it means."],
      transition="Break; after it, one submitted contract on screen.", flex="Overrun flows into the break; the review block uses whatever was submitted."),
 dict(time="10:15–10:30", title="Break", type="Break", on_screen="", purpose="", notes=[], say=[], transition="", flex=""),
 dict(time="10:30–10:45", title="Review and present a contract", type="Shareback + demo", on_screen="VS Code Markdown editor, then Copilot/Claude, then the browser",
      purpose="Review a submitted contract in the Markdown editor, then generate a self-contained HTML version with an overview, contents and diagrams.",
      notes=["Open with 'Open with Markdown editor'; then the prompt in the anchor; use a fast model at low effort first and let the big model finish in the background.", "Open the HTML in the browser; show it is navigable and iterable."],
      say=["Same file, two renderings. The AI does not care; you and your reviewers do."],
      transition="Where the tables will live: the platform.", flex="If generation stalls, open common/running-example/03-data-contract.html."),
 dict(time="10:45–11:15", title="Platform architecture: warehouse, lake, lakehouse and Databricks under the hood", type="Demo + shareback", on_screen="Anchor › Platform architecture (five diagrams); the Delta and Spark demos",
      purpose="Warehouse vs lake vs lakehouse; where Databricks fits; Delta tables under the hood; what the Spark engine does; how the tools fit together.",
      notes=["Thirty minutes: elicit the three words, run the Delta demo, show the tools-together diagram; Spark only if ahead.", "Shareback: each table names one thing Databricks does that a plain file store cannot, and one thing dbt relies on Databricks for."],
      say=["A lakehouse is a relational database split in two: files on S3, compute on Databricks, and a transaction log in between to get the guarantees back."],
      transition="Straight into Docker: the box all of this runs in.", flex="Behind: the tools-together diagram and the Delta demo only; the timeline and Spark are optional."),
 dict(time="11:15–11:40", title="Docker demonstration", type="Demo", on_screen="Anchor › Docker; a terminal; the dev container's Dockerfile",
      purpose="Dependencies, reproducibility, isolation and resource limits; Dockerfile to image to container; the dev container and its terminal.",
      notes=["Mirror the challenge's six sections in order with the same commands: run an image, look inside, the Dockerfile (a commented sample on screen), build and the cache, run and the expected two lines, tag; then the gate and the four stalls.", "Show the training repo's Dockerfile: FROM, COPY, RUN, USER, ENV. Say EDO maintains it.", "Point at the glossary: every command by objective, and the secure example, for the afternoon."],
      say=["Your terminal in VS Code is inside a container. That is why dbt and astro are there and why your laptop's Python is not."],
      transition="Challenge 7 in the dev container; lunch when you reach a good stopping point, back at 13:00.", flex=""),
 dict(time="11:40–12:00", title="Challenge 7 — Docker practical", type="Challenge", on_screen="Anchor › Challenge box; learners in challenges/v1/01-docker-intro",
      purpose="Start the practical: run an image and look inside before lunch.",
      notes=["Sections 1 and 2 need no authoring; most learners reach section 3 before lunch.", "Anyone blocked on the engine (Docker Desktop, Windows container mode) is paired now, not after lunch."],
      say=["Why did the container stop, and what survives when you run a fresh one?"],
      transition="Lunch.", flex=""),
 dict(time="12:00–13:00", title="Lunch", type="Break", on_screen="", purpose="", notes=[], say=[], transition="", flex=""),
 dict(time="13:00–13:45", title="Challenge 7 continued, with the stretch", type="Challenge", on_screen="Anchor › Challenge box and the stretch list",
      purpose="Everyone reaches PASS on the gate; fast finishers take section 6, the variations, multi-stage builds, resource limits or the secure example.",
      notes=["Circulate with the glossary open; the stalls are the engine, CRLF line endings and the build context.", "Collect the PASS count by 13:40."],
      say=["PASS is the floor, not the ceiling: the stretch list is where the experienced people go."],
      transition="Shareback.", flex="If most of the room has PASS by 13:30, start the shareback early and give the skills block the time."),
 dict(time="13:45–14:00", title="Docker shareback", type="Shareback", on_screen="Anchor › Docker shareback box",
      purpose="Image versus container versus writable files; what travels with the image; one surprise per table.",
      notes=["Ask one table per question; show the PASS count.", "Close the loop to the platform: this is how CG ships Airflow and dbt images."],
      say=["What travels with the image, and what does not?"],
      transition="Break, then where Catalyst's skills fit.", flex=""),
 dict(time="14:00–14:15", title="Break", type="Break", on_screen="", purpose="", notes=[], say=[], transition="", flex=""),
 dict(time="14:15–14:45", title="Catalyst skills overview, and experimentation if time allows", type="Demo + challenge", on_screen="Anchor › Skills: tiers, phases, how to load; Activity 8 card",
      purpose="The map of Catalyst's skills by tier and lifecycle phase, which ones the week uses, and how to load them; then, if time allows, one design-phase skill run on a learner's own product. No dbt generation today.",
      notes=["Tiers diagram, the phase table, the five skills used so far, the ones Wednesday and Thursday use.", "Show the settings and /plugins once; the 'reading skill file' tell.",
             "Activity 8 is optional: a design skill on their own PRD and contract, never a build skill."],
      say=["Pick the skill for the phase you are in. A build skill on a design that is not agreed produces confident code for the wrong product."],
      transition="Set up Databricks before you leave.", flex="Short of time: the tiers and the phase table only; Activity 8 becomes homework."),
 dict(time="14:45–15:00", title="Databricks setup and close", type="Shareback", on_screen="Anchor › Before learners leave",
      purpose="Everyone runs the Databricks setup, because tomorrow's first command is dbt debug; questions recorded; tomorrow previewed.",
      notes=["mise run setup:databricks (browser OAuth, Enter through the prompts, minutes per person), then dpc-check green; the catalog training_dev and schema training_<user> in the UI.", "Keep access problems on a separate list from content questions; a platform-support contact for tonight."],
      say=["Tomorrow is self-paced: the README teaches dbt as you go, and I walk the room. The first command is dbt debug, so set up now."],
      transition="", flex=""),
]

LEAVE_WITH = ["Each table's contract extended with mapping rules and measurable service levels, shared for review.",
              "Challenge 7 at PASS for everyone (paired where an engine was blocked); the stretch noted for those who took it.",
              "Databricks setup done for everyone: dpc-check green, the training schema visible, because tomorrow's first command is dbt debug.",
              "Access problems recorded separately from content questions, with an owner for each; a platform-support contact for tonight."]

ACTIVITIES = [
 dict(number="6", title="Extend the contract", grouping="Individual, then pairs or tables", minutes=30,
      brief="On your own, ask Catalyst what source-to-target transformation types and what service-level indicators and objectives it knows. Then, in pairs or at your table, take one of yesterday's data contracts: name the incoming tables and the outgoing table, write the rules that get you from one to the other (lookups, derivations, filters, what nulls mean), and the commitments a consumer would hold you to. Transcribe the discussion, give it to Catalyst, extend the contract, then inspect and revise.",
      outputs=["At least one unambiguous mapping rule someone else could implement without asking you", "At least one measurable commitment with its indicator, target, tolerance and time zone", "The revised contract, shared for review"],
      early="Add the breach response: who is told, by when, what they are told.",
      debrief=["Could someone else implement this rule without asking you what it means?", "For 'available by 07:30': which time zone, which days, measured where, and what happens on failure?", "For a lookup: what is the join key, and what happens with zero or several matches?"],
      extra="""
      **Prompts.** "What types of source-to-target transformation do you distinguish?" · "What service-level indicators and objectives should a data contract state?" · then `/ai-catalyst data-contract` with the transcript of your discussion and the existing contract attached: "Extend the STTM and SLA sections; keep everything else."
      """),
 dict(number="7", title="Docker practical", grouping="Individual or pairs", minutes=65,
      brief="In the dev container, work through `challenges/v1/01-docker-intro/README.md` sections 1 to 5: run an image, look inside, write the Dockerfile, build the image, run your image. Start before lunch, finish after it. Section 6, the 'try a variation' steps and the stretch list are for anyone with time.",
      outputs=["`docker run --rm portfolio-summary` printing the six-holding summary", "`mise run challenge:verify 01` showing PASS", "An answer to: why did the container stop, and what survives when you run a fresh one?"],
      early="Section 6 (tags); multi-stage builds; resource limits (`--memory`, `--cpus`); read the training repository's own Dockerfile and explain three lines of it; or build and run the secure example in `common/glossaries/docker-secure-example/`.",
      debrief=["What is the difference between the image, the running process and its writable files?", "What travels with the image, and what does not?"]),
 dict(number="8", title="Try one design skill on your product (if time allows)", grouping="Pairs", minutes=20,
      brief="Pick one design-phase skill and run it on your own PRD and contract: `consumer-use-case-map` (who consumes it and how), `data-model` (the entities and their keys), `architecture-diagram` (the flow from sources to consumers), `data-quality-controls-plan` (the few checks that matter) or `nfr-specification` (performance, reliability, cost). Attach the PRD and the contract. Read the result for the invented detail before you keep anything. No build skills today: dbt comes tomorrow, with the design agreed.",
      outputs=["One generated design document, reviewed", "One line for the room: what it added that the PRD and contract did not say, and one thing it invented"],
      early="Run a second skill and check whether the two documents agree with each other.",
      debrief=["Which phase was the skill for, and did your product have what that phase needs?", "What did it invent, and which input would have prevented it?"],
      extra="""
      **Prompts.** `/ai-catalyst consumer-use-case-map` "Map the consumers, their use cases and access patterns for the product in #file:02-prd.md and #file:03-data-contract.md" · `/ai-catalyst data-model` "Design the conceptual and logical model for this product" · `/ai-catalyst architecture-diagram` "Draw the data flow from sources to consumers" · `/ai-catalyst data-quality-controls-plan` "Propose the controls for the target table in the contract".
      """),
]

SECTIONS = [
 dict(n=1, title="Day 1 recap and the map of the week", anchor="s1", start="09:00",
      parts=["Recap: what we made yesterday", "Whiteboard: source-, domain- and consumer-aligned", "Today, and the two musts"]),
 dict(n=2, title="Mappings and service commitments", anchor="s2", start="09:25",
      parts=["Demo: STTM and service levels", "Worked example: the running example's contract, mapping and service levels", "Activity 6: extend the contract", "Break", "Shareback: review and present a contract"]),
 dict(n=3, title="Platform architecture", anchor="s3", start="10:45",
      parts=["Demo: warehouse, lake, lakehouse; Databricks under the hood; Delta; the tools together", "Shareback"]),
 dict(n=4, title="Docker", anchor="s4", start="11:15",
      parts=["Demo: Docker in the six steps of the challenge, a sample Dockerfile, the gate", "Demo: the dev container's Dockerfile", "Challenge 7: Docker practical", "Lunch", "Challenge 7 continued, with the stretch", "Shareback: image, container, what survives", "Break"]),
 dict(n=5, title="Catalyst skills, and setting up for tomorrow", anchor="s5", start="14:15",
      parts=["Demo: the skills, their tiers and the lifecycle; how to load them", "Activity 8 (if time allows): one design skill on your product", "Databricks setup", "Close"]),
]

def cells():
    A = {a["number"]: a for a in ACTIVITIES}
    act = lambda n: dc.md(dc.activity(n, A[n]["title"], A[n]["grouping"], A[n]["minutes"], A[n]["brief"], A[n]["outputs"], A[n].get("debrief"), A[n].get("early")))

    C = [dc.title(2, TITLE, "anchor notebook"),
         *dc.how_to_use(2),
         dc.code(dc.setup_cell(2)),
         dc.agenda(SECTIONS, lead="Yesterday's contract is today's input. By the end of the day it has mapping rules and measurable commitments, you know what the platform does with your tables, and you have built and run a container. The code comes tomorrow."),
         # ---------------- 1. recap ----------------
         dc.section(1, "Day 1 recap and the map of the week", "s1"),
         dc.part("Recap", "what we made yesterday", time="09:00"),
         dc.anchor("What did we make yesterday, and where does it go today?",
                   "A list of the room's products and pain points; PRDs and data contracts generated from interviews and reviewed; the vocabulary of the lifecycle.",
                   "Today's design morning extends those contracts; the practicals from this afternoon on exist to check what the design produces.",
                   "Ask the room for each answer and write it up; add what is missing; then the alignment picture; then the agenda."),
         dc.md(dc.say(["Yesterday you made the why and the what. Today the what becomes precise enough to implement, and you build the box it runs in.",
                       "Open the contract you made yesterday. Everything before the first break happens to that document."])),
         dc.md(dc.whiteboard("Day 1 recap", [
             ("What is a data product?", "A data set with promises (trusted, reusable, business-ready, accessible), enforced by contracts, tests and infrastructure. Three views: data plus promises; data plus code plus infrastructure; a transformation from source-aligned to consumer-aligned."),
             ("What did we learn about finding out what to build?", "Interviews get you there fastest when the right people are in the room; the real questions are the follow-ups; surveys scale but anonymous answers are suspect; observation shows what people actually do; transcription can mangle terms, so review it."),
             ("What did the generated documents get wrong?", "They always generate something: identifiers, dates, versions, approvals and confident numbers are where the model fills gaps. Fix the input (the transcript, the brief), not the output."),
             ("Which documents exist now, and in what order?", "Transcript, then PRD (why and for whom), then data contract (what is promised). Today adds the source-to-target mapping and the service levels; then sign-off; then, from tomorrow, the code."),
             ("What is the week's thread?", "Design conversations, transcripts and reviewed contracts produce most of the code; the practicals exist so you can check what was generated."),
         ], open_=True)),
         dc.part("Whiteboard", "source-, domain- and consumer-aligned"),
         dc.anchor("Yesterday's contract describes a table. Whose shape is that table?",
                   "The consumer's. The sources keep the producer's shape; the mapping you write today is the path between; the firm's agreed definitions sit in the middle.",
                   "The three words are how CG names layers, catalogs and products; every model you build this week belongs to one of them.",
                   "Three one-liners, the running example, and the older names you will hear."),
         dc.figure("d1-alignment", "Source-aligned to consumer-aligned, with the domain layer between",
                   ["Source-aligned: the producer's shape, kept faithfully, as an audit path back to the extract.",
                    "Domain-aligned: the firm's one definition of each entity, agreed by the data owner, reused by every consumer.",
                    "Consumer-aligned: the shape of the decision, one row per business question."]),
         dc.md(dc.whiteboard("source-, domain- and consumer-aligned", [
             ("What is source-aligned data?", "Their shape: the vendor price file as it arrived, every delivery kept, native currency. The audit path."),
             ("What is consumer-aligned data?", "Your reader's shape: the US price sheet, one row per instrument per business day, in USD, by 07:30 Eastern. Yesterday's contract describes this table."),
             ("So what is domain-aligned?", "The firm's shape: the one agreed definition of an instrument, a close, a business date, owned by the domain's data owner, so every consumer gets the same answer. The running example borrows it from the instrument master; Friday's product builds it."),
             ("Where does today's mapping fit?", "It is the path from source-aligned to consumer-aligned, rule by rule; the domain definitions are the words the rules use."),
             ("What about staging, intermediate, marts, or bronze, silver, gold?", "dbt's folder names describe a project's structure; medallion names describe how clean the data is; alignment describes whose shape it is. They usually line up; alignment is the one you decide."),
         ], open_=True)),
         dc.figure("d5-alignment-naming", "The names, and the older names you will hear",
                   ["src_, dom_, and rpt_/agg_/ts_/api_ are the prefixes Friday's project uses.",
                    "Recognise raw, staging, intermediate, curated and bronze, silver, gold when you meet them; speak alignment."]),
         dc.part("Today", "and the two musts"),
         dc.md("""
         Two things must happen today, whatever else slips: the **design documents before the first break** (the mapping and the service levels into your contract), and **Docker done by the end of the day** (Challenge 7 at PASS). The platform block in between is there so the practical makes sense; the afternoon's skills overview is there so tomorrow's code comes from the right place. No dbt code is generated today; the design is agreed first.
         """),
         # ---------------- 2. mappings and service levels ----------------
         dc.section(2, "Mappings and service commitments", "s2"),
         dc.part("Demo", "STTM and service levels", time="09:25"),
         dc.anchor("What is the core of a source-to-target mapping?",
                   "The transformation rules: one per target column, plus the row rules, in English precise enough to implement.",
                   "The STTM is where the product's business logic lives; a vague rule becomes a wrong join nobody notices.",
                   "Name the rule type for every column, then the edge cases: nulls, zeros, duplicates, dates, time zones."),
         dc.figure("d2-sttm", "Sources, rules and target for the running example",
                   ["Direct, constant, lookup, aggregate, derive: the textbook five; Catalyst splits derive further.",
                    "Row rules matter as much as column rules: dedup, filter, reject, and what a null means in each column.",
                    "The running example's mapping is in common/running-example/04-sttm.md: eleven column rules and four row rules."]),
         dc.md("""
         #### How a rule is written

         One row per target column. The columns of the mapping, and what goes in each:

         | Column | What it holds |
         |---|---|
         | Target column | The name in the consumer-aligned table, from the contract's schema |
         | Type | The target data type, with precision for money and rates (`DECIMAL(18,6)`) |
         | Rule type | One of the five below: it tells a reviewer what kind of work the column needs before reading the rule |
         | Source | Which source table and column, by alias (V for the vendor feed, I for the instrument master, F for FX) |
         | Rule, in English | Precise enough to implement without asking: the operation, the join key, what null means, zero and negative, which value wins |

         Row rules sit beneath the column rules and say which rows exist at all: dedup (which delivery wins), filter (which rows are in scope), reject (what cannot be placed and is dropped), and what a null means per column.

         #### The five rule types

         | Rule type | What it means | Running example | What a reviewer checks |
         |---|---|---|---|
         | Direct | Copy the source value, perhaps renamed, trimmed or cast | `price_date` from `V.px_date`, cast to date: the business date of the close, not the delivery time | The type and the cast; what null or an unexpected value means |
         | Constant | A fixed value with no source column | `price_source = 'VENDOR'` (`'MANUAL'` reserved for an override that does not exist yet) | That the value list is closed and documented |
         | Lookup | A value fetched from another table by a key | `ticker` from the instrument master, joined on `upper(trim(isin))`; a missing master row leaves it null and fails the relationship test | That the key is unique on the lookup side; what happens with zero or several matches |
         | Aggregate | One value from several source rows | The latest delivery per instrument and date (row rule R1: the row with the latest `vendor_ts` wins) | The grain, and the tie-break |
         | Derive | Compute from one or more inputs with an operation | `price_usd = price_native * fx_rate_to_usd`, null when the rate is null so the build fails; `price_key = instrument_id || '|' || price_date` | The units, the null arithmetic, and the test that guards the result |

         Catalyst's `transformation-spec` returns a CG-specific list that splits derive further (conversions, concatenations, conditional logic); the five above are the textbook set and every CG type is one of them.
         """),
         dc.md(dc.whiteboard("STTM", [
             ("What is a source-to-target mapping? What is its core?", "An artefact showing where data comes from and goes to; the core is the transformation rules."),
             ("What kinds of rule can a column have?", "Direct (copy), constant, lookup (a third table), aggregate (a mean), derive or transform (an operation; concatenate is a subtype). Ask Catalyst for CG's list."),
             ("What is in the design documentation set?", "PRD, data contract, glossary or data dictionary, STTM, service levels."),
         ], open_=True)),
         dc.anchor("Delay is allowed to be an hour. Is that the indicator, the objective or the agreement?",
                   "SLI: the measure. SLO: its ideal value. SLA: the permissible departure, agreed, with a consequence.",
                   "Consumers hold you to commitments, not to good intentions; each commitment has a cost.",
                   "List the indicators a product needs, give each a target and a tolerance, and say how it is measured."),
         dc.figure("d2-service-levels", "Measure it, target it, promise it with a tolerance",
                   ["The indicator is a number you can measure every run; the objective is zero delay, 100% complete; the agreement is what you actually sign.",
                    "Delivery time needs a time zone, the eligible days, the measurement point and the action on failure.",
                    "Duty to explain: when a number looks wrong, somebody owes the consumer an answer within an agreed time."]),
         dc.md(dc.whiteboard("service levels", [
             ("What do SLI, SLO and SLA stand for, and what do they mean?", "Indicator: the measurable quantity. Objective: its ideal value. Agreement: the permissible departure and the consequences."),
             ("Give me indicators.", "Delay from delivery time (which time zone?), latency, throughput, recovery time (service, data or level), completeness, accuracy, freshness, availability, support turnaround, a duty to explain."),
             ("What is availability, and what does 99.9% mean?", "The share of time the service works, in nines. 90% is a month a year; 99% a working week; 99.9% a working day; 99.99% an hour; 99.999% five minutes."),
             ("How do providers get more nines?", "Cloned infrastructure, global and local load balancing, a disaster-recovery site that already takes some traffic. Nines tell you about spare capacity."),
         ])),
         dc.md("""
         | Availability | Downtime a year | Remember it as |
         |---|---|---|
         | 90% | about 36 days | a month |
         | 99% | about 3.65 days | a working week |
         | 99.9% | about 8.8 hours | a working day |
         | 99.99% | about 53 minutes | an hour |
         | 99.999% | about 5 minutes | a coffee |
         """),
         dc.part("Worked example", "the running example's contract, mapping and service levels"),
         dc.md(dc.demo("a finished set, before you extend your own", "Screen-share the running example: the contract, then its mapping and service levels as separate documents.", [
                  "Open `common/running-example/03-data-contract.md` in the Markdown preview: section 2 (the schema, the target), section 3 (the SLAs) and section 4 (the quality rules).",
                  "Open `04-sttm.md`: one rule per target column with its type, rule type, source and the rule in English; the four row rules beneath; the edge cases agreed in the interview.",
                  "Open `05-service-levels.md`: each commitment as an indicator, an objective and an agreement, with its clock and how it is measured.",
                  "Say: this is what yours will look like after the activity, in the same template Catalyst uses; the two cells below keep both documents on the projector."])),
         dc.code('from IPython.display import Markdown, display\ndisplay(Markdown((COMMON / "running-example" / "04-sttm.md").read_text()))'),
         dc.code('display(Markdown((COMMON / "running-example" / "05-service-levels.md").read_text()))'),
         dc.part("Activity 6", "extend the contract", time="09:45"),
         act("6"),
         dc.md(dc.prompt("Chat view", "What types of source-to-target transformation do you distinguish, and what service-level indicators and objectives should a data contract state?\n\n/ai-catalyst data-contract\nExtend the attached contract with an STTM section (one rule per target column, plus row rules) and measurable SLAs from this discussion transcript. Keep every other section as it is.",
                         "Same questions, then: /data-contract  Extend ... (attach common/running-example/03-data-contract.md and the discussion)")),
         dc.break_(15, "10:30"),
         dc.part("Shareback", "review and present a contract", time="10:30"),
         dc.md(dc.demo("Markdown editor, then a self-contained HTML page", "Read Markdown properly, then turn the contract into one HTML page on a small model and on a big one.", [
                  "Right-click a submitted contract, Open with…, Markdown editor (or Open Preview); edit one cell.",
                  "Say: this is how to read the long READMEs on Wednesday and Thursday.",
                  "In Claude Code (or Copilot) run the prompt below on a fast model at low effort.",
                  "Open the result in the browser: contents, overview, diagrams.",
                  "Start the same prompt on the biggest model at high effort; let it run while you teach; compare when it finishes.",
                  "Say why the reasoning is hidden now (vendors stopped showing traces after competitors trained on them) and why the big model is slow."])),
         dc.md(dc.prompt("Chat view, contract attached", "Create a well-structured, self-contained HTML document from this contract: an overview at the top, a table of contents, diagrams where they help (sources to target, the SLA timeline), and plain-English prose explaining any section a non-engineer would find hard. One file, no external dependencies.",
                         "Same prompt. Fallback already rendered: common/running-example/03-data-contract.html")),
         dc.code("""# Fallback: the contract already rendered as HTML (made with pandoc; the AI version adds prose and diagrams)
import webbrowser
webbrowser.open((COMMON / "running-example" / "03-data-contract.html").as_uri())
print("opened", COMMON / "running-example" / "03-data-contract.html")"""),
         dc.md("### Could someone else implement this rule without asking you what it means?\n\nTake two rules from the room's contracts and test them against this list.\n\n| Ambiguity | Ask | Running-example answer |\n|---|---|---|\n| Identifiers and keys | Which column joins, and is it unique on the lookup side? | ISIN, one primary row per instrument in the master |\n| Null | What does empty mean in this column? | A null FX rate means no same-day rate; the USD price is null and the build fails |\n| Zero, minimum, maximum | Is zero a value or a missing value? What is implausible? | A zero or negative price is a quality failure |\n| Duplicates | Can the source send the same row twice? Which wins? | Re-deliveries: latest vendor timestamp wins |\n| Dates and time zones | Business date or delivery time? Which zone? | Business date of the close; 07:30 America/New_York |\n| Scope words | 'US', 'active', 'price': whose definition? | Market and active flag from the master; price is the primary-listing close |"),
         # ---------------- 3. platform ----------------
         dc.section(3, "Platform architecture", "s3"),
         dc.part("Demo", "warehouse, lake and lakehouse; Databricks under the hood; Delta; the tools together", time="10:45"),
         dc.anchor("Why is Databricks on the paved path, and what does it actually do with your dbt SQL?",
                   "A lakehouse: Delta tables in S3 (files plus a transaction log), Spark compute run by Databricks, Unity Catalog on top.",
                   "Every dbt model you build runs here; knowing what happens under the hood explains the costs, the guarantees and the limits.",
                   "Three pictures (warehouse, lake, lakehouse; Databricks under the hood; the Delta format), the Delta demo on this laptop, then how all the tools fit together. Spark only if ahead."),
         dc.figure("d2-warehouse-lake-lakehouse", "Data warehouse, data lake, lakehouse",
                   ["A warehouse gives tables, SQL and ACID on its own storage: strong guarantees, expensive to scale, structured data only.",
                    "A lake is files in object storage: cheap and flexible, no guarantees; left alone it becomes a swamp.",
                    "A lakehouse keeps the cheap files and adds an open table format (Delta) for ACID and versions, an engine (Spark) for SQL, and governance (Unity Catalog)."]),
         dc.md(dc.whiteboard("warehouse, lake, lakehouse", [
             ("What does a warehouse give you, and what does it cost?", "Tables, SQL, transactions, strong consistency; proprietary storage you pay to scale; structured data only."),
             ("What is a data lake?", "A cloud file system (S3) with any format in it: CSV, Parquet, JSON, images. Cheap, scales, no structure guaranteed, so every program must know every file."),
             ("What goes wrong with lakes?", "No transactions: half-written files, duplicates on retry, no history, nobody knows what a file means. The data swamp."),
             ("What does a lakehouse add?", "An open table format on the files (Delta: Parquet plus a log) so you get ACID, versions and schema; an engine that speaks SQL (Spark); a catalog for names, permissions and lineage."),
         ], open_=True)),
         dc.figure("d2-databricks-under-the-hood", "Databricks under the hood: sources, ingestion, Delta storage, Spark compute, Unity Catalog, consumers",
                   ["Loading from different sources: files dropped in S3 (Auto Loader, COPY INTO), databases, streams and APIs (Kafka, Lakeflow), and in training dbt seed.",
                    "Storage is your S3 bucket in Delta format; Databricks does not keep your data inside itself.",
                    "Compute is Spark: clusters for notebooks and jobs, SQL warehouses (Photon) for dbt and BI. Serverless by default on the paved path.",
                    "Unity Catalog names everything catalog.schema.table, holds permissions and lineage, and is what the Marketplace and Catalyst search. CG's three catalog types (application, source-aligned, domain) are the alignment layers made physical."]),
         dc.figure("d2-delta-format", "A Delta table: Parquet files plus a transaction log",
                   ["The log is the trick: every write is a commit that lists which files make up the table now.",
                    "That gives ACID, versions and time travel, MERGE and DELETE on files, and schema enforcement.",
                    "OPTIMIZE compacts small files and ZORDER co-locates rows by the columns queries filter on; that is the post-hook in the learners' project."]),
         dc.md(dc.demo("Delta under the hood, on this laptop", "A Delta table is Parquet files plus a log: the cell writes one and reads every version back.", [
                  "Run the cell: it writes the vendor prices as a Delta table, appends a day, merges a correction, reads version 0, compacts, and reads the table from DuckDB.",
                  "Open the table folder the script names: the Parquet files and `_delta_log/*.json`.",
                  "Point at the merge output: the corrected row replaced, the old file kept, the log naming the files in each version.",
                  "Say: on Databricks the same table sits in S3 and Spark reads it; the format is open, which is why dbt, DuckDB, Spark and pandas all read it."])),
         dc.code("!python demos/delta-under-the-hood/demo.py"),
         dc.code('!ls -R demos/delta-under-the-hood/warehouse/prices_delta | head -20\n!python -c "import json,glob; [print(json.dumps(json.loads(l))[:120]) for l in open(sorted(glob.glob(\"demos/delta-under-the-hood/warehouse/prices_delta/_delta_log/*.json\"))[0]).read().splitlines()[:3]]"\n# The log is readable JSON: a commit lists the files it added or removed.'),
         dc.figure("d2-spark-engine", "The Spark engine: a driver plans, executors run the plan over partitions, results combine",
                   ["Spark splits data into partitions and runs the same work on each in parallel across machines; a shuffle (Exchange) regroups rows between stages.",
                    "You write SQL; the driver builds a plan; Databricks provides the machines, the scheduling and the Delta integration.",
                    "dbt never runs your data through its own process: it sends SQL to Databricks and Spark does the work next to the data."]),
         dc.md(dc.demo("the Spark engine, locally (only if ahead of time)", "A local Spark shows the driver, executors, partitions and the shuffle that Databricks runs for you at scale.", [
                  "Run the cell (about thirty seconds): a local Spark with four executors loads the vendor prices multiplied up and runs a SQL aggregate.",
                  "Find *Exchange* in the printed physical plan: that is the shuffle between stages.",
                  "Run it again with `--hold 90` and open http://localhost:4040: Jobs, Stages, the SQL tab.",
                  "Say: Databricks is this on many machines, with Delta and Unity Catalog around it, and you never configure it."])),
         dc.code("!python demos/spark-engine/demo.py 2>&1 | grep -vE 'WARN|^Setting|^To adjust'"),
         dc.anchor("How do all the tools fit together?",
                   "Catalyst generates; the dev container runs dbt and Airflow locally; GitHub holds the code; Harness deploys on merge; Airflow on Astro schedules; Cosmos turns the dbt project into tasks; dbt sends SQL to Databricks; Spark writes Delta on S3; Unity Catalog governs; the Marketplace publishes; Datadog watches.",
                   "Every day this week zooms into one or two boxes; the picture is what connects them.",
                   "Elicit the role of each tool, then the diagram, then one scheduled run as a sequence."),
         dc.figure("d2-tools-together", "How the tools fit together: generate, develop, ship, schedule, transform, store, govern, find, observe",
                   ["Left to right is the life of a change: generated with Catalyst, developed in the dev container, merged on GitHub, deployed by Harness.",
                    "Top to bottom at run time: Airflow decides when, Cosmos maps the dbt project to tasks, dbt sends SQL, Databricks runs Spark, Delta is written to S3.",
                    "Unity Catalog and the Marketplace are where consumers find the product; Datadog is where operations sees it run."]),
         dc.figure("d2-scheduled-run", "One scheduled run, as a sequence: scheduler, Cosmos, dbt, Databricks, Delta, Datadog",
                   ["At 06:00 the scheduler decides a run is due; each Cosmos task runs one dbt model; dbt sends compiled SQL; Spark reads inputs and commits a new Delta version.",
                    "Status flows back up; a failure is an event in Datadog; the publish step is what consumers see."]),
         dc.md(dc.whiteboard("the paved path, tool by tool", [
             ("Which technologies are on the paved path?", "Databricks, dbt, S3, Airflow with Astronomer, Cosmos, Docker, Git and GitHub, Harness, Unity Catalog, Marketplace, Catalyst, Datadog."),
             ("What does dbt provide? Databricks? S3?", "The transformation rules and the tests. The compute that runs the SQL as Spark. Storage, as Delta files."),
             ("Airflow? Astronomer? Cosmos?", "Timing and triggering. Managed Airflow, vended per team. The adapter that renders a dbt project as Airflow tasks."),
             ("Docker? Git? Harness? Datadog?", "The environment for development and deployment. Version control whose pull-request events trigger release. The CI/CD pipeline that deploys on merge. Monitors and alerts on the runs."),
             ("When may you leave the path?", "With a real reason (an API served from S3, a specialist engine); then you own every problem yourself."),
         ])),
         dc.part("Shareback", "one minute per table"),
         dc.md(dc.reflect("SHAREBACK — one minute per table", "Each table answers in one minute.", [
                     "One thing Databricks does that a plain file store cannot.",
                     "One thing dbt relies on Databricks for.",
                     "One tool on the diagram you have used, and one you have not."])),
         # ---------------- 4. docker ----------------
         dc.section(4, "Docker", "s4"),
         dc.part("Demo", "Docker in the six steps of the challenge", time="11:15"),
         dc.anchor("Why is your VS Code terminal not your laptop's terminal this week?",
                   "A container bundles an application with its dependencies down to the OS user space; an image is the frozen template; a Dockerfile is the recipe.",
                   "Repeatable environments, isolation (network, ports, resources), the same bytes on a laptop, a build server and the cloud.",
                   "Run an image, look inside, write a four-line Dockerfile, build, run, tag; then the dev container's Dockerfile."),
         dc.figure("d2-docker", "Dockerfile to image to container; the dev container is a container VS Code attaches to",
                   ["FROM extends a base image: almost every Dockerfile starts that way; the training container extends an EDO image.",
                    "An image is layered and cached: change the app and only COPY onwards rebuilds.",
                    "A container lives as long as its command; a fresh container starts clean from the image.",
                    "Isolation is the production point: one app per container, controlled ports, capped CPU and memory, a limited blast radius."]),
         dc.md(dc.demo("Docker in the six steps of the challenge", "The same six steps, commands and outputs as `challenges/v1/01-docker-intro`, run here on the challenge's own six-holding app; you type them yourselves in the practical.", [
                  "Check Docker Desktop is running: the whale in the menu bar, or `docker info`.",
                  "Step 1, run an image: `docker run --rm python:3.11-slim python --version`; the first run pulls the image, the container prints one line and is gone.",
                  "Step 2, look inside: `docker run --rm -it python:3.11-slim bash`, then `ls /` and `cat /etc/os-release` (Debian, not your laptop); a file written in `/tmp` is gone in the next container.",
                  "Step 3, the Dockerfile: four instructions in order, `FROM`, `WORKDIR`, `COPY`, `CMD`; the sample below is commented line by line; the starter leaves three of them as TODOs for you.",
                  "Step 4, build: `docker build -t portfolio-summary .` from the folder with the Dockerfile; the `.` is the build context; build twice and read `CACHED`; `docker images | grep portfolio-summary`.",
                  "Step 5, run: `docker run --rm portfolio-summary` prints exactly two lines; mount a different CSV with `-v` and the same image gives a different answer.",
                  "Step 6, tag: `docker tag portfolio-summary portfolio-summary:v1`; two names, one image ID; that is how CG ships Airflow and dbt images.",
                  "The gate: `mise run challenge:verify 01` from anywhere in the repository builds the starter image, runs it, checks the two lines and prints PASS.",
                  "Say: nothing in the practical is new after this; the glossary has every command by what it does."])),
         dc.md("""
         | Step | What you do | The command | What you should see |
         |---|---|---|---|
         | 1 Run an image | Run a public image's Python | `docker run --rm python:3.11-slim python --version` | One line, `Python 3.11.x`; the container has already exited |
         | 2 Look inside | Open a shell in a container | `docker run --rm -it python:3.11-slim bash`, then `ls /`, `cat /etc/os-release`, `exit` | A Linux root listing; `os-release` names Debian |
         | 3 Write the Dockerfile | Fill the three TODO lines in `starter/Dockerfile` | `grep -E '^(FROM\|WORKDIR\|COPY\|CMD)' Dockerfile` | Exactly four lines, in that order |
         | 4 Build | Bake the recipe into an image | `docker build -t portfolio-summary .` (twice) | Steps the first time; `CACHED` the second; `docker images` shows the row, about 130 MB |
         | 5 Run | Start a container from your image | `docker run --rm portfolio-summary` | `Portfolio summary` then `6 holdings, total market value 12,011,626.50` |
         | 6 Tag (optional) | Give the image a version | `docker tag portfolio-summary portfolio-summary:v1` | Two rows, `latest` and `v1`, one image ID |
         | Gate | Prove it | `mise run challenge:verify 01` | `PASS` |

         **If it stalls.** `Cannot connect to the Docker daemon`: the engine is not running, start Docker Desktop. `permission denied` on the socket: use the dev container. `exec format error` or script not found: CRLF line endings after editing on Windows; save as LF and rebuild. A slow first `run` or `build`: the base image is being pulled, once.
         """),
         dc.code("!docker run --rm python:3.11-slim python --version\n# Step 1. Python from inside a container built from an image, not from this laptop. The container exited when the command did."),
         dc.code('!docker run --rm python:3.11-slim bash -c "ls / && cat /etc/os-release | head -2"\n# Step 2, non-interactive form (the challenge uses -it for a real shell). A Linux root and a Debian os-release: the container\'s own filesystem.'),
         dc.code('!docker run --rm python:3.11-slim bash -c "touch /tmp/proof.txt && ls /tmp"\n!docker run --rm python:3.11-slim ls /tmp\n# Step 2, the variation: the file written in the first container is gone in the second. Each container starts clean from the image.'),
         dc.code('!cat demos/docker/portfolio-summary/Dockerfile\n!echo "--- the four instructions the check greps for:" && grep -E "^(FROM|WORKDIR|COPY|CMD)" demos/docker/portfolio-summary/Dockerfile\n# Step 3. A sample Dockerfile: base, then where, then what, then how to run. The starter gives FROM and leaves the other three as TODOs.'),
         dc.code("!cd demos/docker/portfolio-summary && docker build -t portfolio-summary . 2>&1 | tail -3\n!cd demos/docker/portfolio-summary && echo \"--- second build, CACHED lines:\" && docker build -t portfolio-summary . 2>&1 | grep -cE 'CACHED'\n!docker images | grep portfolio-summary\n# Step 4. Build twice: the second build is almost entirely cached. The image row is mostly the shared Python base layer."),
         dc.code('!docker run --rm portfolio-summary\n!echo "--- same image, a mounted CSV:" && docker run --rm -v "$PWD/demos/docker/portfolio-summary/app/holdings.csv:/app/holdings.csv:ro" portfolio-summary\n# Step 5. Exactly the two lines the gate checks. Mount a different CSV and the same image gives a different answer: image and data are separate.'),
         dc.code("!docker tag portfolio-summary portfolio-summary:v1 && docker images portfolio-summary\n# Step 6. Two names, one image ID. Tag, push to a registry, pull elsewhere: that is how CG ships Airflow and dbt images."),
         dc.part("Demo", "the dev container's Dockerfile"),
         dc.md(dc.demo("the dev container's Dockerfile", "The learners' dev container is a Dockerfile they can now read.", [
                  "Open `reference/DataCreators-client/dev-container/edo-training-data-products/.devcontainer/Dockerfile`, the file VS Code builds for learners (the cell below prints its head).",
                  "Point at the two `FROM` lines: a flyway stage, then CG's Python 3.13 image from the internal registry.",
                  "Point at the `RUN curl` lines: the Astro CLI, starship and mise; then `mise install databricks-cli`.",
                  "Point at `COPY` of the setup scripts and `ENV VIRTUAL_ENV=/opt/venv` with its `bin` on `PATH`.",
                  "Say: EDO maintains this; you never will; but now you can read it.",
                  "Open Docker Desktop: Images, then Settings and Resources, briefly."])),
         dc.code('!sed -n "1,12p" ../../reference/DataCreators-client/dev-container/edo-training-data-products/.devcontainer/Dockerfile'),
         dc.part("Challenge 7", "Docker practical", time="11:40"),
         act("7"),
         dc.md(dc.challenge("Docker practical", "challenges/v1/01-docker-intro/README.md", "before and after lunch, about 65 min",
                            "Sections 1 to 5: run an image, look inside, write the Dockerfile, build it, run it. Lunch when you reach a good stopping point; back at 13:00.",
                            [("What learners do", [
                                "`docker --version`; if the engine is not running, start Docker Desktop.",
                                "Section 1, run an image: a container from a public Python image.",
                                "Section 2, look inside: the container's own filesystem and processes.",
                                "Section 3, write the Dockerfile: `starter/Dockerfile` has one TODO per line.",
                                "Section 4, build the image.",
                                "Section 5, run the image: the app runs the same anywhere."])],
                            "`mise run challenge:verify 01` prints PASS.",
                            support=["Every Docker command by what it does, the Dockerfile instructions, and how to build and run containers securely: `common/glossaries/docker-commands.md`.",
                                     "Engine not running means Docker Desktop is not started on the laptop.",
                                     "CRLF line endings on Windows cause `exec format error`.",
                                     "The first pull is slow once."],
                            stretch="Section 6 (tags); the variations; multi-stage builds; resource limits; the secure example in `common/glossaries/docker-secure-example/`.")),
         dc.break_(60, "13:00", lunch=True),
         dc.part("Challenge 7 continued", "with the stretch", time="13:00"),
         dc.md("""
         **Everyone:** sections 3 to 5 to PASS. **Finished?** In this order, as far as time allows:

         1. Section 6, tags, and the "try a variation" steps.
         2. Resource limits: run your image with `--memory 128m --cpus 0.5` and read `docker stats`.
         3. A multi-stage build: a builder stage that installs, a final stage that only runs.
         4. The secure example in `common/glossaries/docker-secure-example/`: build it, run it read-only as a non-root user, then `docker compose up` with the database and call `/db`.
         5. Read the dev container's own Dockerfile and explain three lines to your neighbour.
         """),
         dc.part("Shareback", "image, container, what survives", time="13:45"),
         dc.md(dc.reflect("SHAREBACK — one table per question", "Show the PASS count, then one table each.", [
                     "What is the difference between the image, the running process and its writable files?",
                     "What travels with the image, and what does not?",
                     "Why did the container stop, and what survives when you run a fresh one?",
                     "One thing from the stretch list that surprised you."])),
         dc.break_(15, "14:15"),
         # ---------------- 5. catalyst skills, setup, close ----------------
         dc.section(5, "Catalyst skills, and setting up for tomorrow", "s5"),
         dc.part("Demo", "the skills, their tiers and the lifecycle; how to load them", time="14:15"),
         dc.anchor("Which skill do I reach for, and when?",
                   "About a hundred Catalyst skills in four tiers that compose downwards, each tagged with the lifecycle phase it serves; the five you have used sit in discovery and design.",
                   "Knowing the map means asking Catalyst for the right document at the right phase, instead of generating code before the design is agreed.",
                   "The tiers, the phase table, how the plugin loads, then (if time) one design skill on your own product. No build skills today."),
         dc.figure("d1-catalyst", "Catalyst: skills, tiers, the lifecycle",
                   ["Orchestrators run a phase; workflow skills run several steps; document skills make one artefact from a template; capability skills do one action.",
                    "A skill is a Markdown instruction file with a template and checks, sometimes with Python; Copilot shows it reading the file."]),
         dc.md("""
         | Tier | How many | What they are | Examples |
         |---|---|---|---|
         | Orchestrators | 11 | Run a lifecycle phase or stage end to end | `dplc-concierge`, `dplc-triage`, `dplc-design`, `dplc-build`, `dplc-publish` |
         | Workflow | 15 | Several steps, one job | `source-aligned`, `domain-aligned`, `consumer-aligned`, `setup-dbt-project`, `data-modeling` |
         | Document | 37 | One artefact from a template | `product-requirements-document`, `data-contract`, `transformation-spec`, `sla-dashboard-spec`, `runbook` |
         | Capability | 42 | One action, composable | `connect-databricks`, `query-table`, `profile-columns`, `write-dbt-model`, `generate-dag`, `validate-dag` |

         | Phase | The document skills you would ask for | This week |
         |---|---|---|
         | 1 Triage | `marketplace-search`, `consumer-use-case-map`, `demand-tracker-entry` | Day 1 (does it exist? who consumes it?) |
         | 2 Discovery | `product-requirements-document`, `feasibility-report`, `business-case`, `effort-estimate`, `requirements-acceptance-criteria` | Day 1 |
         | 3 Design | `data-contract`, `transformation-spec`, `data-model`, `architecture-diagram`, `data-quality-controls-plan`, `nfr-specification`, `security-design` | Day 1 and today |
         | 4 Build | `setup-dbt-project`, `write-dbt-source`, `write-dbt-model`, `validate-dbt`, `adding-dbt-unit-test`, `generate-dag`, `validate-dag` | Wednesday and Thursday |
         | 5 Validate | `data-quality-sign-off`, `uat-sign-off` | Friday's evidence |
         | 6 Publish | `release-notes`, `consumer-onboarding-guide`, `deployment-record` | Thursday's Phase 2 |
         | 7 Operate | `runbook`, `sla-dashboard-spec`, `incident-log` | Today (service levels) and Thursday |
         | 8 Evolve | `downstream-impact-assessment`, `deprecation-notice`, `usage-analytics-report` | Mentioned |
         """),
         dc.md(dc.demo("how the skills load, and how you know one ran", "The plugin is three settings and one click; a skill is a file you can read.", [
                  "VS Code settings: `chat.plugins.enabled`, `chat.useAgentSkills`, and `chat.plugins.marketplaces` pointing at the Catalyst repository (or a local copy of it).",
                  "Reload; in Copilot Chat run `/plugins` and enable AI Catalyst; `/ai-catalyst` then lists the skills.",
                  "Open one skill's `SKILL.md` and its template: the instructions, the sections, the checks.",
                  "Run `/ai-catalyst data-contract` on the running example and point at the moment Copilot reads the skill file; without that line it is plain Copilot.",
                  "Same skills in Claude Code on this laptop, as `/data-contract`, from `courseware/.claude/skills/`."])),
         dc.part("Activity 8", "one design skill on your product (if time allows)"),
         act("8"),
         dc.md(dc.prompt("Chat view, PRD and contract attached", "/ai-catalyst consumer-use-case-map\nMap the consumers, their use cases, access patterns and SLA needs for the product in the attached PRD and contract. Mark anything you could not find in them as an open question.",
                         "/consumer-use-case-map with @courseware/common/running-example/02-prd.md and @courseware/common/running-example/03-data-contract.md")),
         dc.part("Databricks setup", "before you leave", time="14:45"),
         dc.md(dc.demo("where tomorrow's tables will land", "Everyone sets up Databricks now, because tomorrow's first command is dbt debug.", [
                  "In the dev container: `mise run setup:databricks` (browser OAuth; press Enter through the prompts; it takes minutes per person).",
                  "Then `dpc-check`: every gate green.",
                  "Databricks UI: Catalog, `training_dev`, `training_‹username›`; tomorrow every dbt table appears there.",
                  "Say: on the paved path you rarely open this UI; you write dbt in files and commit.",
                  "Open `challenges/v1/02-dbt-pipeline/README.md` tonight if you want a head start; the first hour tomorrow is sources and staging."])),
         dc.part("Close"),
         dc.md(dc.say(["Two musts, both done: the contract has rules and commitments, and the container runs. Tomorrow the contract becomes code, and the README teaches dbt as you go.",
                       "Write down the questions you want answered tomorrow, and keep the access problems on a separate list from the content questions."])),
         dc.md(dc.leave_with(LEAVE_WITH)),
         *dc.qa_section(2)]
    return C
