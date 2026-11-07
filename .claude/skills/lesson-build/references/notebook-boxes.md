# Notebook boxes (demo and challenge anchors)

The styled boxes CG Core's demo and challenge anchors use, copied from AIA's Session 12 and 16 notebooks so every session looks the same (user, 2026-10-15). Build them with the `nbkit` helpers (`scripts/nbkit.py` in the repo) rather than by hand; the HTML below is what the helpers must produce, and `scripts/nbkit.py selftest` renders every helper with the placeholder text shown here and compares it with these blocks byte for byte. `module-audit` checks every box in an anchor against the same spelling. Each box is its own markdown cell unless noted. Text inside a box is plain HTML: `<strong>`, `<code>`, `<br>`, `&amp;`, never Markdown.

What goes in the boxes follows the programme's way of working (`programme-profile/references/conventions.md` → "Learners direct AI and review what it wrote"): task boxes ask learners to prompt Copilot to write, fix or change the code, review what it wrote and run a check; folded solutions show a model prompt, the change and the check.

## Difficulty legend (challenge, "How to use this notebook")

`nbkit.difficulty_legend()`; append `nbkit.difficulty_legend_html()` to the how-to-use cell's text.

````html
| Badge | Who it's for | What to expect |
|-------|-------------|----------------|
| <span style="background:#2ecc71;color:#fff;padding:2px 8px;border-radius:3px;font-size:0.85em;font-weight:700;">Q1 · CORE</span> | Everyone | Start here, then go as far as you can |
| <span style="background:#f39c12;color:#fff;padding:2px 8px;border-radius:3px;font-size:0.85em;font-weight:700;">Q2 · STRETCH</span> | Anyone who finishes Core | More of the decisions left to you |
| <span style="background:#e74c3c;color:#fff;padding:2px 8px;border-radius:3px;font-size:0.85em;font-weight:700;">Q3 · BONUS</span> | Anyone with time left | Not expected: extra practice, if you want it |
````

## Task box (challenge): one per tier

`nbkit.task_box(tier, title, mode, goal, tasks, note=None)`, tier 1, 2 or 3.

| Tier | Colour (border and header) | Body background |
|---|---|---|
| ⚡ Q1 · CORE | `#2ecc71` | `#f5fff8` |
| ⚡ Q2 · STRETCH | `#f39c12` | `#fffdf0` |
| ⚡ Q3 · BONUS | `#e74c3c` | `#fff5f5` |

````html
<div style="border:2px solid #2ecc71;border-radius:6px;overflow:hidden;margin:24px 0;"><div style="background:#2ecc71;padding:8px 16px;font-family:sans-serif;font-weight:700;font-size:0.78em;letter-spacing:0.08em;color:#fff;">⚡ Q1 · CORE &nbsp;—&nbsp; Title &nbsp;·&nbsp; Individual</div><div style="padding:18px 22px;background:#f5fff8;font-size:0.95em;line-height:1.7;color:#1a1a1a;"><strong>One bold line: what this tier makes.</strong><br><br><strong>Task 1.1 —</strong> First step.<br><strong>Task 1.2 —</strong> Second step.</div></div>
````

The header names the tier, the title, and Individual or Pairs. No times anywhere in a challenge notebook: the demo's 🏆 CHALLENGE TIME box gives the one fixed time for all three tiers, and the lesson plan holds the instructor's timings (user, 2026-10-16). Tasks are numbered by tier (Q1's are Task 1.1, 1.2 …; Q2's Task 2.1 …). Q3's body says it is not expected (the helper adds `Q3_NOTE`, "Not expected: extra practice if you have time.", when the text does not). Learners start at Q1 and go as far as they can; no tier is compulsory. Task lines read "Ask Copilot to …", "Review …", "Run the check …": learners direct Copilot and review what it wrote; they never type the code or do the maths by hand.

## Reflect box and folded solution (challenge): before every solution

`nbkit.reflect_solution(question, solution, answer)`, with `solution` usually built by `nbkit.copilot_solution(prompt, change, check, mode=…, model=…, attach=…, where=…)` (its badges are the 🤖 COPILOT box's; `where` defaults to Chat view, and `mode` defaults to `None`, which means Ask in Chat view and no mode in Inline chat or Terminal chat). The box and the `<details>` share one cell.

````html
<div style="border:2px solid #F8DB59; border-radius:8px; margin:10px 0;">
<div style="background:#FFF2CC; color:#000; padding:8px 14px; font-weight:bold;">💭 REFLECT &nbsp;—&nbsp; before you open the solution</div>
<div style="background:#fffef5; padding:12px 14px; color:#1a1a1a;">One question that makes the learner think about why, not what.</div></div>

<details>
<summary><strong>Solution — attempt before opening</strong></summary>

**A prompt that works:** <span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#D0E0E3;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">WHERE</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Chat view</span></span><span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#F8DB59;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">MODE</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Ask</span></span><span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#C9DAF8;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">MODEL</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Fast</span></span>

```text
The prompt, in words a learner could type.
```

**The change a good answer makes:**

```python
# the fixed code, with helpful in-line comments
```

**The check that proves it:** what to run, and what it shows.

**Reflect — answer:** Two or three sentences.

</details>
````

## Terminal box (demo and challenge): before a terminal step

`nbkit.terminal_box(title, body, commands=None)`; `commands` adds the fenced `bash` block under the box in the same cell. When a step crosses machines, pass `commands` as a list of `(label, commands)` pairs, such as `[("On your laptop", …), ("Now on the remote (the prompt shows jordan@harbourline-remote)", …)]`: each label becomes a bold line over its own block, so the remote's lines are never in the same block as the `ssh` that logs in.

````html
<div style="border:2px solid #434343; border-radius:8px; margin:10px 0;">
<div style="background:#434343; color:#fff; padding:8px 14px; font-weight:bold;">⌨️ TERMINAL &nbsp;—&nbsp; What to do in the terminal</div>
<div style="background:#f8f8f8; padding:12px 14px; color:#1a1a1a;">Where to open the terminal and which folder to start in.</div></div>
````

## Your-turn box (challenge): a short task with no code

`nbkit.your_turn_box(title, body)`. No minutes.

````html
<div style="border:2px solid #F8DB59; border-radius:8px; margin:10px 0;">
<div style="background:#F8DB59; color:#000; padding:8px 14px; font-weight:bold;">🎯 YOUR TURN &nbsp;—&nbsp; Title</div>
<div style="background:#fffef5; padding:12px 14px; color:#1a1a1a;"><strong>The question.</strong> Where the answer goes.</div></div>
````

## Challenge-time box (demo): at the end of each module section, just before the Go deeper box

`nbkit.challenge_time_box(module, minutes, anchor, section, line, q1, q2, q3)`. Q1, Q2 and Q3 each start their own line (user, 2026-10-16). With module folders (user, 2026-10-27) the link runs from the demo's module folder, `instructor/moduleNN-<slug>/`, to the module's own challenge notebook, `../../learner/moduleNN-<slug>/dayNN_mN_challenge.ipynb` (pass that path as `anchor`; a bare file name keeps the older `../../learner/challenge/` link); the block below is regenerated from nbkit's self-test fixtures whenever the helper changes, so it shows whatever link the helper currently writes. The last line is `nbkit.CHALLENGE_TIME_LAST`: start at Q1 and go as far as you can.

````html
<div style="border:2px solid #434343; border-radius:8px; margin:10px 0;">
<div style="background:#434343; color:#fff; padding:8px 14px; font-weight:bold;">🏆 CHALLENGE TIME &nbsp;—&nbsp; Module 1 — 25 mins</div>
<div style="background:#f8f8f8; padding:12px 14px; color:#1a1a1a;">Open <a href="../../learner/module01-first-programs-copilot/day01_m1_challenge.ipynb"><code>day01_m1_challenge.ipynb</code></a> → <strong>Module 1 challenge</strong>. One line on the task.<br><br><strong>Q1:</strong> one line<br><strong>Q2:</strong> one line<br><strong>Q3:</strong> one line<br><br>Start at Q1 and go as far as you can. Q3 is a bonus, not expected.</div></div>
````

## Go deeper box (demo and challenge): last in each module section, the anchors' only mention of the handbook

`nbkit.go_deeper(module, body)`; a Markdown anchor pastes `nbkit.go_deeper_html(module, body)`.

````html
<div style="border:2px solid #F8DB59; border-radius:8px; margin:10px 0;">
<div style="background:#F8DB59; color:#000; padding:8px 14px; font-weight:bold;">📚 GO DEEPER &nbsp;—&nbsp; the Module 1 handbook</div>
<div style="background:#fffef5; padding:12px 14px; color:#1a1a1a;">One or two sentences: what the handbook adds. No path, no link, no section.</div></div>
````

## Module anchor (demo and challenge): its own cell, straight after each module section's heading cell

The 🧭 anchor (user, 2026-10-27) opens every module (the day has none): a dark header that names its job, always "🧭 WHAT, WHY AND HOW" (the heading above already names the module, so the header never repeats it), one question from the learner's own
work, then WHAT, WHY and HOW side by side, each one short phrase of 12 words or fewer (user, 2026-10-27): the same
words as the slides' three tiles, so slides, notebooks and handbooks read the same; the audit fails a longer one. Never typed by hand: its words live once per session in `dayNN_anchors.md`, and
`.venv/bin/python scripts/nbkit.py anchors --session <session folder>` writes every copy (the notebooks' anchor cells,
id `anchor-<key>` between `<!-- module-anchor: <key> -->` markers, and the `::: {.anchor}` div in the handbooks and
the lesson plan, drawn by `scripts/pdf-filters/module-anchor.lua` and the Word builder). `--check` and the
audit fail on a copy that differs. Each module section then runs: heading cell · anchor cell · a bridge cell ("This
builds on …" plus one sentence leading into the map) · the module map cell with its bullets. The helper is
`nbkit.anchor_box_html(nbkit.anchor_header(key), question, what, why, how)`.

````html
<div style="border:2px solid #434343; border-radius:8px; margin:18px 0 12px; overflow:hidden;">
<div style="background:#434343; color:#fff; padding:8px 14px; font-weight:bold;">🧭 WHAT, WHY AND HOW</div>
<div style="background:#F3F3F3; padding:10px 14px; color:#1a1a1a; font-style:italic;">A question from the learner's own work?</div>
<div style="display:flex; gap:8px; padding:10px; background:#fff;"><div style="flex:1; min-width:0; background:#D0E0E3; border-radius:6px; padding:10px 12px; color:#1a1a1a;"><div style="font-weight:bold; font-size:0.78em; letter-spacing:0.08em; margin-bottom:4px;">WHAT</div>What it is.</div><div style="flex:1; min-width:0; background:#FFF2CC; border-radius:6px; padding:10px 12px; color:#1a1a1a;"><div style="font-weight:bold; font-size:0.78em; letter-spacing:0.08em; margin-bottom:4px;">WHY</div>Why it matters.</div><div style="flex:1; min-width:0; background:#D9EAD3; border-radius:6px; padding:10px 12px; color:#1a1a1a;"><div style="font-weight:bold; font-size:0.78em; letter-spacing:0.08em; margin-bottom:4px;">HOW</div>How you'll do it.</div></div></div>
````

## Data card (overview, demo and challenge): wherever a dataset is introduced to learners

AIA's format (user, 2026-10-15), drawn like the persona card in blue (user, 2026-10-19). Never describe a dataset in a paragraph; give its card. Two rules (user, 2026-10-16):

- **Once, at the top.** In a demo or challenge anchor the card sits in a `## Setup` section after "How to use this notebook" and before the first module section. It serves every module; no module section repeats it, and a module that reads data the card doesn't cover adds that data to this card. In an overview the cards sit under "The data".
- **One file per line.** The Files row lists each file and what it holds on its own line: pass the value as a list.

One design, two palettes (user, 2026-10-19): the data card is the persona card's box (a header bar, a pale label column beside white values, rows ruled, a thin `#434343` frame, never split across pages) in blue: the header bar in the Copilot box's MODEL badge blue `#C9DAF8`, the labels in its pale tint `#E4EDFC`, where the persona card has brand yellow `#FEF800` and `#FFFDCC`. Never style a card by hand.

Notebooks: `nbkit.data_card(name, rows)` (`data_card_html` for the string): the header bar reads "🗂️ DATA — <name>", list values become one "•" line per item, and values are HTML (`<code>…</code>`, not backticks). It shares `_card_html` with `persona_card_html`, so the two can't drift; the 🗺️ table of contents lists it as "🗂️ Data card — <name>". Overviews and other Markdown that becomes a PDF: `nbkit.data_card_pdf_md(name, rows)`, a "#### Data card — <name>" heading and a pandoc grid table (no 🗂️, because the PDF fonts have no glyph for it; a grid table, the only table form whose cells hold a real bullet list), which `scripts/pdf-filters/persona-card.lua` draws as the box titled "DATA — <name>", with the same drawing function as the persona card.

````html
<div style="border:1px solid #434343; border-radius:4px; margin:10px 0; overflow:hidden;">
<div style="background:#C9DAF8; color:#1a1a1a; padding:6px 10px; border-bottom:1px solid #434343;">🗂️ DATA &nbsp;—&nbsp; the challenge data</div>
<table style="width:100%; border-collapse:collapse; margin:0; color:#1a1a1a;"><tr><td style="border-right:1px solid #434343;background:#E4EDFC;width:24%;padding:6px 10px;vertical-align:top;text-align:left;font-weight:bold;">Name</td><td style="background:#fff;padding:6px 10px;vertical-align:top;text-align:left;">The challenge data, in <code>common/data/challenge/</code> (from this notebook: <code>../../../../common/data/challenge</code>)</td></tr><tr><td style="border-top:1px solid #434343;border-right:1px solid #434343;background:#E4EDFC;width:24%;padding:6px 10px;vertical-align:top;text-align:left;font-weight:bold;">Used in</td><td style="border-top:1px solid #434343;background:#fff;padding:6px 10px;vertical-align:top;text-align:left;">Your challenges</td></tr><tr><td style="border-top:1px solid #434343;border-right:1px solid #434343;background:#E4EDFC;width:24%;padding:6px 10px;vertical-align:top;text-align:left;font-weight:bold;">Files</td><td style="border-top:1px solid #434343;background:#fff;padding:6px 10px;vertical-align:top;text-align:left;">• <code>funds.csv</code>: one row per share class<br>• <code>fund_nav_daily.parquet</code>: one price per share class per business day</td></tr><tr><td style="border-top:1px solid #434343;border-right:1px solid #434343;background:#E4EDFC;width:24%;padding:6px 10px;vertical-align:top;text-align:left;font-weight:bold;">Note</td><td style="border-top:1px solid #434343;background:#fff;padding:6px 10px;vertical-align:top;text-align:left;">Different funds and numbers from the demo data</td></tr></table></div>
````

## Copilot box (demo and challenge): wherever a learner or the instructor prompts Copilot

**One box per cell** (user, 2026-10-16): each 🤖 COPILOT box, with its prompt block and closing line, is its own markdown cell with nothing else in it; a task that needs two prompts gets two cells, and the task box or any explanation sits in the cell before.

`nbkit.copilot_prompt(title, prompt, mode, model, attach=None, purpose=None, then=None, where="Chat view")` (user, 2026-10-16). The header names the job; colour-coded badges say where to open Copilot and how to set it up, in this order, each label on its colour and each value on white:

- **WHERE** (aqua), the surface: **Chat view**, the Chat panel, opened with Ctrl+Alt+I (Ctrl+Cmd+I on a Mac), for questions, plans and jobs that change files; **Inline chat**, in the editor on the selected lines, opened with Ctrl+I (Cmd+I on a Mac), for one change you read in place as a diff, then Keep or Undo (in a notebook cell, **Accept and Run**); or **Terminal chat**, in the terminal, opened with Ctrl+I (Cmd+I on a Mac), for a shell command to read before it runs, so Insert, not Run. Ctrl+I opens Inline chat or Terminal chat, whichever has focus, so select the lines or click in the terminal first; in a file with Chat view edits not yet kept or undone, Ctrl+I opens the prompt in the Chat view instead (Ask in Chat), so Keep or Undo those edits first. Chat view is the default. Mac shortcuts are spelled out, never as key symbols: the PDF fonts can't print them.
- **MODE** (yellow): Ask, Plan or Agent, the handbook's three modes. Chat view only, where it is required; pass `mode=None` with Inline chat or Terminal chat (`""` counts as no mode too).
- **MODEL** (blue): Fast, Reasoning or Auto, on every box.
- **ATTACH** (green), only when the prompt needs context: `#<file>`, `selection`, `#codebase`, `#terminalLastCommand` (the last command and what it printed) or `#terminalSelection` (the lines selected in the terminal); several go in one badge, separated by spaces.

The helpers raise `ValueError` on an unknown WHERE, a mode given with Inline chat or Terminal chat, and a missing mode (`None` or `""`) with Chat view. The prompt follows in a plain text block learners copy; keep its lines short so they don't wrap in a PDF. The closing line follows the surface: Chat view's comes from the mode (Ask: check the answer against the code; Plan: read the plan first; Agent: read every line, Keep or Undo, run the check); Inline chat's is read the change in the editor, Keep or Undo, run the check (Inline chat in a notebook cell sets its own, below); Terminal chat's is Insert, not Run, then read the command, press Enter and check what it printed. `then="…"` replaces the line and `then="none"` (or `""`) leaves it out. Folded solutions show their model prompt the same way (`copilot_solution`, with the same `where`). In Markdown that becomes a PDF, write `::: {.copilot title="…" where="Chat view" mode="Agent" model="Fast" attach="#file"}` (or `where="Terminal chat" model="Fast"`, with no mode) around the ```` ```text ```` block; `scripts/pdf-filters/copilot-box.lua` and the Word lesson plan's `scripts/docx/build_lesson_plan.js` draw the same badges and closing lines. They warn on stderr rather than stop: a div with no `where` draws as Chat view (and the audit warns), and an empty or unknown `mode` is left out, never drawn as a badge.

````html
<div style="border:2px solid #434343; border-radius:8px; margin:10px 0;">
<div style="background:#C9DAF8; color:#1a1a1a; padding:8px 14px; font-weight:bold;">🤖 COPILOT &nbsp;—&nbsp; What Copilot should do</div>
<div style="background:#f4f7fd; padding:12px 14px; color:#1a1a1a;"><span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#D0E0E3;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">WHERE</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Chat view</span></span><span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#F8DB59;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">MODE</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Agent</span></span><span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#C9DAF8;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">MODEL</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Fast</span></span><span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#D9EAD3;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">ATTACH</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">#file</span></span><br>One line on what the prompt is for.</div></div>

```text
The prompt, in words a learner could type.
```

**Then** read every line it wrote, choose **Keep** or **Undo**, and run the check.
````

## Copilot box in Inline chat (demo and challenge): one change to the selected code

`nbkit.copilot_prompt(title, prompt, None, model, purpose=…, where="Inline chat")`: no MODE badge, and the closing line says to read the change in the editor, then Keep or Undo. VS Code shows the change as a diff in place, with **Keep** and **Undo**. The purpose line says which lines to select before Ctrl+I. No ATTACH `selection`: Inline chat works on the selected lines already, so the selection is where the learner opens it, not context to add; ATTACH is for anything else the prompt needs, such as `#<file>`.

**Inline chat in a notebook cell** (2026-10-16): the template below is for a `.py` file in the editor. In a notebook cell VS Code shows the change as a diff in the cell and offers **Accept and Run**, which applies it and reruns the cell, so the check runs in the same step (code.visualstudio.com/docs/agents/guides/notebooks-with-ai, "Make focused cell changes with inline chat"); it does not show Keep and Undo. The box keeps WHERE Inline chat and sets its own closing line: `then=nbkit.COPILOT_THEN_NOTEBOOK_CELL` ("read the diff in the cell: if it makes only the change you asked for, choose **Accept and Run**, which applies it and reruns the cell; if not, discard it and ask again"), or a line fitted to the task in the same shape. Name no reject button: the docs name none. The audit accepts Accept and Run on Inline chat and still warns on a bare Accept or Discard.

````html
<div style="border:2px solid #434343; border-radius:8px; margin:10px 0;">
<div style="background:#C9DAF8; color:#1a1a1a; padding:8px 14px; font-weight:bold;">🤖 COPILOT &nbsp;—&nbsp; What Copilot should change</div>
<div style="background:#f4f7fd; padding:12px 14px; color:#1a1a1a;"><span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#D0E0E3;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">WHERE</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Inline chat</span></span><span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#C9DAF8;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">MODEL</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Fast</span></span><br>Select the lines first.</div></div>

```text
The prompt, in words a learner could type.
```

**Then** read the change in the editor, choose **Keep** or **Undo**, and run the check.
````

## Copilot box in Terminal chat (demo and challenge): a shell command to read before it runs

`nbkit.copilot_prompt(title, prompt, None, model, where="Terminal chat")`: no MODE badge, and the closing line says Insert, not Run. Terminal chat offers **Run** (Ctrl+Enter, Cmd+Enter on a Mac), which runs the command at once, and **Insert** (Alt+Enter, Option+Enter on a Mac), which puts it at the prompt for the learner to read and then run with Enter.

````html
<div style="border:2px solid #434343; border-radius:8px; margin:10px 0;">
<div style="background:#C9DAF8; color:#1a1a1a; padding:8px 14px; font-weight:bold;">🤖 COPILOT &nbsp;—&nbsp; The command Copilot should suggest</div>
<div style="background:#f4f7fd; padding:12px 14px; color:#1a1a1a;"><span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#D0E0E3;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">WHERE</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Terminal chat</span></span><span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#C9DAF8;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">MODEL</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Fast</span></span></div></div>

```text
The prompt, in words a learner could type.
```

**Then** choose **Insert**, not Run: read the command, press Enter, and check what it printed.
````

## Table of contents (demo and challenge): its own cell, straight before "How to use this notebook"

AIA's 🗺️ table of contents in CG Core's form (user, 2026-10-16). Never type it: run `.venv/bin/python scripts/nbkit.py toc --nb <anchor>` after `write()`, on the demo, the challenge and, after its overlays, the completed copy (`nbkit.apply_toc(nb, kind)` from a script). The helper builds the cell, id `toc`, from the notebook's own headings and boxes, and `module-audit` rebuilds it and compares. Run it again whenever a `## ` or `### ` heading, a task box or a your-turn box changes; `--check` writes nothing and exits 1 when the table is out of date.

- **Where:** its own markdown cell straight before "How to use this notebook", so it sits at the top of page 1 under the title. In the completed copy that is after its twin-only first cell.
- **Columns:** Section and What happens. AIA's Block and Duration are left out: a session is one half-day, and the table names no minutes in either notebook.
- **Rows:** every `## ` section from How to use on, in order, each linked to its anchor. How to use lists Start here, then Difficulty guide and Copilot settings. A demo section lists its `### ` headings, then Challenge time when it holds the 🏆 box. A challenge section lists each task box as "Q1 Core: <title>", each your-turn box as "Your turn: <title>", and its `### ` headings except the answer boxes (My checks …). In a challenge row each task item after the first starts a new line of the cell (`<br>`), so Q1, Q2 and Q3 each start their own line, and so does the item after a Q3 item (What to show, say); every other item follows with " · ". The Go deeper box is never listed, nor are reflect, Copilot and terminal boxes or anything inside a folded solution.
- **Anchors:** every `## ` heading opens its own cell, and the cell's first line is its anchor, then a blank line, then the heading. The id is the heading text before " — ", in lower case with hyphens: `how-to-use-this-notebook`, `setup`, `module-1`, `module-1-challenge`, `put-it-together`. Rewording a title after the dash keeps the id; two sections with one id stop the helper.
- **The lead:** one line, and it never spells a box label in capitals, which the audit would read as a misspelt box. It says learners go as far as they can, and, in a challenge with a Put it together section, that Put it together is an optional stretch. Its words are nbkit's `TOC_LEAD_KIND` and `TOC_LEAD_TOGETHER`, in the tier-wording block.

Demo:

````markdown
## 🗺️ Table of contents

> **Every module runs the same way: a short demo, then its challenge, then a debrief.** Each module section ends by sending you to its challenge, where you go as far as you can.

| Section | What happens |
|:---|:---|
| [How to use this notebook](#how-to-use-this-notebook) | Start here · Copilot settings |
| [Setup](#setup) | 🗂️ Data card — the demo data |
| [Module 1 — The module's title](#module-1) | The first beat · The second beat · Challenge time |
| [Module 2 — The next module's title](#module-2) | Its one beat · Challenge time |
````

Challenge and completed copy (the last sentence of the lead only when there is a Put it together section):

````markdown
## 🗺️ Table of contents

> **Every module runs the same way: a short demo, then its challenge, then a debrief.** Start at Q1 and go as far as you can. Put it together is an optional stretch if you finish early.

| Section | What happens |
|:---|:---|
| [How to use this notebook](#how-to-use-this-notebook) | Start here · Difficulty guide · Copilot settings |
| [Setup](#setup) | 🗂️ Data card — the challenge data |
| [Module 1 challenge — The task's title](#module-1-challenge) | Q1 Core: Core title<br>Q2 Stretch: Stretch title · Your turn: Your-turn title<br>Q3 Bonus: Bonus title |
| [Put it together — The task's title](#put-it-together) | Q1 Core: Core title · What to show |
````

A section's heading cell:

````markdown
<a id="module-1-challenge"></a>

## Module 1 challenge — The task's title

One line on what the section's tasks build.
````

## Copilot settings legend (demo and challenge, "How to use this notebook")

`nbkit.copilot_legend()`: every badge, once, with what it means, so each box's settings read at a glance: the three WHERE surfaces first, with their shortcuts and what each is best for, then MODE (Chat view only), MODEL and ATTACH.

````html
**Copilot settings** (each 🤖 COPILOT box shows the ones its prompt needs):

WHERE comes first: for a shell command, use Terminal chat; for one change to lines you can see, use Inline chat; for a question, a plan or a job across files, use Chat view, the only one with a MODE.

| Setting | What it means |
|---|---|
| <span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#D0E0E3;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">WHERE</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Chat view</span></span> | Open the Chat panel with Ctrl+Alt+I (Ctrl+Cmd+I on a Mac): questions, plans and jobs that change files |
| <span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#D0E0E3;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">WHERE</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Inline chat</span></span> | Select the lines in the editor or a notebook cell, then Ctrl+I (Cmd+I on a Mac): one change you read in place, then Keep or Undo (Accept and Run in a notebook cell) |
| <span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#D0E0E3;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">WHERE</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Terminal chat</span></span> | Click in the terminal, then Ctrl+I (Cmd+I on a Mac): a shell command to read before it runs, so choose Insert, not Run |
| <span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#F8DB59;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">MODE</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Ask</span></span> | Answers about your code or an idea; nothing changes (Chat view only) |
| <span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#F8DB59;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">MODE</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Plan</span></span> | A step-by-step plan for a bigger change, before anything changes (Chat view only) |
| <span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#F8DB59;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">MODE</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Agent</span></span> | Copilot does the job: it edits files and runs commands, and you choose Keep or Undo (Chat view only) |
| <span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#C9DAF8;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">MODEL</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Fast</span></span> | Quick edits and questions |
| <span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#C9DAF8;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">MODEL</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Reasoning</span></span> | Multi-step work: it thinks a problem through before answering |
| <span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#C9DAF8;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">MODEL</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">Auto</span></span> | Copilot picks the model, where your organisation allows it |
| <span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#D9EAD3;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">ATTACH</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">#file</span></span> | A file Copilot should read: type # and its name |
| <span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#D9EAD3;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">ATTACH</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">selection</span></span> | The lines you selected in the editor |
| <span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#D9EAD3;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">ATTACH</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">#codebase</span></span> | Copilot searches the whole workspace |
| <span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#D9EAD3;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">ATTACH</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">#terminalLastCommand</span></span> | The last command you ran in the terminal, and what it printed |
| <span style="display:inline-block;margin:0 6px 4px 0;border:1px solid #434343;border-radius:4px;overflow:hidden;font-size:0.85em;line-height:1.7;white-space:nowrap;"><span style="background:#D9EAD3;color:#1a1a1a;padding:2px 7px;font-weight:700;letter-spacing:0.05em;">ATTACH</span><span style="background:#fff;color:#1a1a1a;padding:2px 7px;">#terminalSelection</span></span> | The lines you selected in the terminal |
````
