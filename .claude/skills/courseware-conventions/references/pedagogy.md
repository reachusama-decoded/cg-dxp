# Pedagogy and session design

How Decoded sessions are designed to teach. All of it is embodied in the material and none of it is named in learner-facing text.

## The frameworks underneath

**DEAR**: Discover (the hook — why and what the topic matters) → Explore (connections, how it works) → Reinforce (memory fades fast, so practice, drills and hackathons in a safe-to-fail environment) → Apply (take it to your work, feedback on people's own work). Every block of a session maps to one of these stages.

**Super learning principles**: meta-learning (map the concepts, facts and procedures up front — the map-of-the-day diagram), directness (teach the core idea via one strong diagram in 15 minutes or less), the drill (attack the real bottleneck), active retrieval (pulse checks and quizzes at the seams, recall-first revision), high-intensity feedback (where did it fail and why — gold-set numbers, peer teach-back).

Less lecturing, more learners-figure-it-out: gamified drills, tiered challenges, hackathons.

## How it shows up in content

- **Core-first sequencing**: the simplest working thing first, elaboration after. A showcase product opens the day as *aspiration, not assignment* — say plainly that nobody is expected to rebuild it, and use it to show how an application comes apart into things on the syllabus. Never "you'll build this".
- **Why-explanations**: every rule states why it exists.
- **Attribute comparisons** for competing tools (a short table), decision tables or flowcharts wherever learners must choose.
- **Emotional hook first** (a working product, a guess, a story beat), logic after.
- **Failure-first**: in a first coding session, break something on purpose and read the error together. Catch the exception so Run All still completes for someone working alone.
- **Predict before run**: an opening guess activity (a number in the chat) that is self-marked in the outro. Keep guesses simple and real-world — technical prediction chains and contrived role-play were both rejected.
- **Leave the instructor something to fill in**: a table with its last columns deliberately empty is a live teaching moment; pre-filled, it is a handout the room reads ahead on.
- **Explain from basics before specifics**: a comparison of options starts with what each one *is* and when it fits, then the factors, then the numbers. Never open on the price.
- **Explain on the visual first, then return to the notebook for the code.** Not side by side. A visual's own teaching order may differ from the notebook's.

## Interaction beats

- The taught day is a demo-along with a 🎯 beat every 10–15 minutes; "cut script, never the your-turn moments".
- Every 🎯 Your turn is scripted in four beats: **Task** (exact instruction + where) → **Time** (limit + halfway call) → **Share** (chat/reactions/partner) → **Harvest** (read two or three back by name, credit, bridge).
- **A prediction elicit must come before its answer is visible.** In a demo-along notebook everything on screen counts as visible — never ask learners to predict what a diagram or paragraph right there answers. Diagram-dependent questions (locate your work ON the diagram) and retrieval checks straight after exposure ("from memory") are fine.
- **Vote options must map to the ask** (✅/❌ or A/B — never "1 or 2" for a good-or-bad question), and a written resolution after the box is labelled (**Resolved — …**).
- **Activity names must be honest for the delivery mode** — no "Pairs verdict" for a two-minute chat moment with no pairing mechanism.
- **Never invent delivery logistics.** No "use the instructor's link", "the instructor posts X in the chat", or fallback mechanisms the user has not specified — learners run their own copy of every app. Neutral fallback only: "Stuck? Ask in the chat." (online) or "Stuck? Ask." (in-person).
- **Poll questions live only in the lesson plan's bank and the poll tool.** Demo and challenge notebooks show the activity name, the join instruction and a notes space — never the questions (protects retrieval practice).
- **Every section gets an activity box, and it goes after the content.** If a section has anything for learners to do, think or write, it carries a full box rather than an italic pointer, and the demo and challenge carry the same box: identical header, title and question wording, with the demo adding the your-turn footer and the challenge adding the answer cells. A box asking "which of these seven matters most" above the seven asks about something unread.
- **After a product showcase, "Apply it to your work" is a business case, not a preference**: who does it help (a person or a team, never "the organisation") · what would you point it at first (something specific) · what is it worth (how often, how long now, how long with it) · what would stop you (sensitive data, sign-off, cost, trust). A question that can be answered without deciding anything is the wrong question.

## Challenges and gapped tasks

- **Every coding challenge is tiered (Q1 easy / Q2 medium / Q3 hard), and every tier gets session time.** One Q1/Q2/Q3 block per section, one shared timed window, everyone starts at Q1, nobody is expected to reach Q3, and whatever they do not reach stays in their notebook. Say that out loud at the start: the window exists so learners can get unstuck with an instructor present, which is the part they cannot do at home. No standalone non-tiered coding task above the tiers, and no tier labelled "post-session" with zero minutes. Discussion notes (case study, breakout) are not challenges and stay untiered. The profile may switch tiering off for a programme that does not run challenges.
- **Gapped tasks ramp, and the function comes last.** Never open a coding task with `def name(___, ___): return ___`: that asks a learner to invent a signature and the arithmetic at once. Split the task across several small cells that each print something, one or two gaps each, easiest first: look a value up → do the calculation once → loop it → *then* wrap it in a function whose parameters are already written. Say why the wrapper earns its place, and point out that the refactor changes nothing in the output.
- **Gaps are `___`** (three underscores), placed so the stub parses — a missed gap fails with a NameError pointing at the line. One `# HINT:` comment per decision point (not per gap); mark provided lines `(given)` when mixing.
- **A 💭 REFLECT question sits before every solution**, visible before the solution opens; the answer waits inside the block.
- **Demo ≠ challenge**: the challenge applies the day's skills to a *different* scenario, dataset or theme so the skill transfers.
- **Required setup lives in the learner notebook, not only the instructor's checklist.** If an app needs a key, a file or a running service before anything works, the notebook says so at the point of use, and says where to find it.

## Session shape defaults (the profile sets the specifics)

- Intro (icebreaker poll + welcome + a guess revisited in the outro) · teaching sections · Outro. Breaks between sections; a 10-minute break every hour.
- Every activity lasts 5, 10, 15, 20 or 30 minutes. Demos about 20 minutes, split when complex; every coding challenge a full 30-minute window.
- **Each block is balanced on its own.** Time for a new or lengthened activity is found inside the same block, never borrowed from another, which silently overruns the meal break.
- **The outro blocks are one text, used three times.** Key takeaways is a `| Takeaway | Outcome |` table, byte-identical in the lesson plan and the demo, one row per outcome, each row about 25 words. Apply it to your work is always the same three questions in the same order and the same words: `Q1 — your familiar problem`, `Q2 — your hidden cost`, `Q3 — your outcome`, echoing the three **Why this matters** bullets. It appears as spoken lines in the lesson plan, as the 💡 box in the demo (plus the your-turn footer), and as the same box in the challenge followed by three answer cells headed with the same `**Qn — label:**`. Keep questions under about 25 words.
- Depth goes to `resources/`; a full guided project goes to `stretch/`. Resources and stretch only for the most important bits: two or three resources at most, never one per topic; a stretch only when the session has no other stretch outlet.

## Delivery modes

**Online** (remote, everyone on their own laptop):
- Chat votes ("1 or 2 in the chat"), ✅ reaction checks every few cells, solo-write + mic/chat share for micro-moments.
- Breakout rooms only for blocks of 10 minutes or more (teach-backs, hackathons). Groups of up to three or solo, each in its own room; instructors move between rooms; wrap-up on screenshare with a fixed running order.
- NEVER: sketching, show of hands, "person next to you", whiteboards, "circulate the room". Activities must be doable alone at a laptop (write a number in chat, list three things, search something).
- Polls through the programme's poll tool; questions in the lesson plan bank only.

**In person first, virtual-safe** (CG Core's mode): write for the room (discussion boxes, pairs, show of hands, whiteboard) but give every activity a solo route a learner can do alone on a laptop, and never depend on chat, polls or breakouts.

**In-person** (instructor-led in a room):
- No chat mechanics, no reaction syncs, no breakout rooms. Discussion beats are `💬 DISCUSSION` boxes with the answer folded into a `<details>` block underneath.
- Show of hands and "turn to the person next to you" are fine. Whiteboard moments are fine when the lesson plan names them.
- If only the instructor has the content (demo-only programmes), there are no 🎯 YOUR TURN boxes and no "open your challenge notebook"; follow-along code is marked `⌨️ LIVE CODE` and watch-only code `💻 DEMO`.

**Constraint to check in the profile**: some client environments cannot upload or download files or fetch arbitrary URLs. Where that applies, ship corpora pasted inside notebooks and never depend on a download at run time.
