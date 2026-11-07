# Diagrams and visuals

**Draw the analogy, not just the concept.** If a section says "think of it like X", X gets a picture. Stating an analogy in prose and then diagramming only the technical side is the most common miss. Where an analogy maps onto something technical, draw the *mapping* (architect → AI product manager), not one half of it.

**Stop the diagram at the picture.** The interpretation line belongs in the lesson plan's Say lines, so the room works it out before the instructor confirms it. A node that carries its own explanation has done the thinking for them.

**Every diagram is introduced from directly above.** The line before the image says what the learner is about to look at. Never a bare image under a heading.

## Mermaid, conservatively

Plain nodes, `-->` links, `<br>`, `style`. No `~~~` invisible links, no `direction` inside a subgraph, no `timeline` diagram type: those render differently across the mermaid versions a notebook will be opened in. Use real typographic characters inside labels (curly quotes “ ”) rather than escaping straight quotes; `&amp;` for ampersands.

**Direction carries meaning:**

| Shape | Direction | Why |
|---|---|---|
| A chain or progression | `LR` | The sequence *is* the left-to-right movement |
| Two things compared | `TB` | Disconnected trees sit side by side, so the eye reads across |
| A fan from one parent | `TB` | Parent on top, children in a row beneath |
| A decision | `TD` | It is a tree |
| Independent pairs (X becomes Y) | `LR` | Each row reads as "this maps to that" |

Highlight the focus node `fill:#F8DB59,color:#000`; where the nodes are peers, colour them the same, or the odd one out reads as emphasis nobody explained.

**Label shape.** One line when the label is one phrase. Otherwise: title, blank line (`<br><br>`), then the detail. Keep every line under roughly 35 characters: in a multi-column layout the longest line sets the column width, and one wide row reintroduces the horizontal scroll. Height is cheap, width is not. A blank line separates distinct thoughts only — never split a sentence that merely wraps.

**Vary the texture.** Three visuals inside one beat tire the eye before the concept lands. If the neighbouring cell already carries two diagrams, make this one a table.

## Matplotlib figures and concept cards

- Brand palette, Work Sans, one `images/` folder at the session root, referenced as `../images/…` from subfolder notebooks and `images/…` from the lesson plan. Never per-folder image copies. (Decoded default; CG Core's `programme-profile` overrides it: one figures folder per session, `courseware/common/figures/<session>/`, referenced as `../../../../common/figures/dayNN/…` from a handbook, the overview or a module notebook (all four folders below `courseware/`), and one more `../` from a completed challenge in `challenge-solution/`.)
- Eyeball every rendered diagram before shipping: label collisions, off-canvas boxes, ellipse-distorted circles (use `ax.scatter` markers, not patch circles). Column headers never overlap the first row. A layer stack reads in the same order as the file it was built from.
- Describe positions in rendering-stable language ("top row", "indexing side") — never left/right.
- **Concept cards are pictures only**: no heading, paragraph, caption sentence or "the proper words" line inside a PNG; those live in the notebook markdown around the image. Smallest type about 11 pt at 1800 px wide, labels 13–17 pt. A card is a drawn graphic (laptop, cloud, bucket, document page, person icons, a stack of layers), not a text table with boxes.
- **Charts in a demo**: the pandas one-liner (`series.plot(kind="barh", color="#F8DB59", title=...)`) rather than a `plt.subplots` grid — in an early session the matplotlib scaffolding is a wall of detail around a two-line idea. Check the chart has something to show: a bar chart of ten near-identical values reads as a ranking that is not there.

## Interactive HTML visualisers

A live pattern for concept layers: one standalone single-file HTML page in `resources/`, taught **first** with the notebook opened afterwards for the code, and **reusable across programmes** — no heading, pointer or line names a demo notebook, a session number or a notebook filename (hand off to "your notebook", unnamed). Wire it into the lesson plan with exactly one What-to-do checkbox; nothing in the demo notebook.

- Make the maths genuinely live (real in-browser computation, not scripted animation). Where a model cannot run in a browser, precompute with the real model, label it on the page, and never ship a recorded model answer.
- One section per screen with a sticky menu, Previous/Next and URL-hash routing; the pipeline map on its own page; a Start page with a "How to use this page" card that says Show answer submits or scores nothing. A single-page concise variant (no menu, scroll only) is fine for short topics.
- **Intro panel** on every teaching page is a four-row labelled grid, never a paragraph: **Context / Approach / Why / Try it**. Four markers, all introduced on the Start page before a learner meets them — ℹ️ Info, 🤔 Guess first, 💡 the revealed answer, 🧪 marks only fields the learner can change.
- **Card layout**: controls left in a narrow rail, results right. Never a control in a card header. The label sits directly on top of the control it names. A live value never lives in a card heading. A button that advances a sequence goes below the state it changes. Every card opens with a full-width ℹ️ Info band that gives the visual's own grammar (what a row, dot or colour means).
- **Spacing scale** 4 / 8 / 16 / 24 / 36: within-group 8px, between-group 24px, between major blocks 28–36px. Reading order made explicit with step badges: 1 on every control group, 2 on every result.
- **Register**: short declarative sentences (about 17 words), no em-dashes in prose, rhetorical questions only inside Guess-first strips, no aphoristic one-liners, headings as "Verb: what you do here". Show one rewritten section for sign-off before doing the rest.
- **The notebook is the code**: short per-section snippets that explain what is on screen, never a complete duplicate script.
- Verify headless (Chrome `--headless=new --screenshot`, minimum sensible width 500px) before shipping.
