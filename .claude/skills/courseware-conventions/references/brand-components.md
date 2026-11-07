# Brand components

Every HTML block Decoded courseware uses, in its one canonical spelling. `scripts/nbkit.py` (CG Core's repo) emits the title and footer cells, the only ones CG Core demo notebooks use; the rest are catalogued for other Decoded programmes.

## Colours

| Token | Hex | Use |
|---|---|---|
| Yellow | `#F8DB59` | Activity box borders/headers, highlighted mermaid nodes, black-banner text |
| Black | `#000000` | Block banners, dividers |
| Cream | `#fffef5` | Activity box body |
| Grey body | `#f5f5f5` | LIVE CODE box body |
| Hand-off grey | `#434343` header / `#f8f8f8` body | Grey boxes: 🏆 CHALLENGE TIME, ⌨️ TERMINAL, 👀 look at the interface |
| Tier green | `#2ecc71` | EASY border/header (body tint `#f5fff8`) |
| Tier orange | `#f39c12` | MEDIUM border/header (body tint `#fffdf0`) |
| Tier red | `#e74c3c` | HARD border/header (body tint `#fff5f5`) |
| Dark text | `#1a1a1a` | Box body text (always set explicitly — dark-theme Jupyter otherwise inverts it) |
| Muted | `#666` / `#555` | "Your turn" footers, quote attribution |

Diagram palette (matplotlib, Work Sans): `#C9DAF8` blue · `#FFF2CC` yellow-light · `#D9EAD3` green · `#D0E0E3` aqua · `#F4CCCC` red-light · greys `#F3F3F3`/`#CCCCCC`/`#434343` · `#FEF800` sparingly. Visualiser chrome: Work Sans, `#FCDF44` accent.

Yellow is for learner action (🎯 YOUR TURN, 💡 APPLY, 📚 GO DEEPER, 🗳️ poll). Grey is for hand-offs and "look over there" (🏆 CHALLENGE TIME, ⌨️ TERMINAL, 👀). Black is for structure (block banners, breaks). Tier colours only ever mean tiers.

## Shared cells (every notebook)

**Title cell** (first cell; logo 100px, no `<br clear>`):

```markdown
<img src="https://courseware.decoded.com/images/decoded/logo-decoded.png" align="left" width="100px"/>

# Session NN: <session title>

<small>v1.0 — <Month Year> &nbsp;</small>

---
<small>&copy; <year> Decoded Limited. All rights reserved. [decoded.com](https://decoded.com)</small>
```

The profile sets the title shape for each notebook type (a lesson plan usually appends ` — Instructor guide`; a challenge reads `# Session NN: challenge notebook: <title>`). Keep the version string identical across all notebooks of a session.

**Programme timeline** (optional second cell): if the profile carries a timeline mermaid (`programme-profile/assets/timeline.md`), it is the second cell of every learner notebook and the lesson plan, current unit and session styled `fill:#F8DB59,color:#000,stroke:#F8DB59`, closed by a `<small>Session N &nbsp;&rsaquo;&nbsp; **<unit>: <title>**</small>` breadcrumb. Programmes without one go straight from title to content.

**Footer** (last cell, standalone — never merged into a content cell):

```markdown
---

<img src="https://courseware.decoded.com/images/decoded/logo-decoded.png" align="left" width="80px"/>

<br clear="left"/>

<small>© <year> Decoded Limited. All rights reserved. [decoded.com](https://decoded.com)</small>
```

**Anchors:** every section and activity that a TOC links to gets an explicit `<a id="kebab-slug"></a>` on its own line before the heading. Never rely on Jupyter auto-anchors (`#Section-1:-The-AI-landscape`) — they break on renames and punctuation.

## Activity boxes (spaced style — demo notebooks)

```html
<div style="border:2px solid #F8DB59; border-radius:8px; margin:10px 0;">
<div style="background:#F8DB59; color:#000; padding:8px 14px; font-weight:bold;">🎯 YOUR TURN &nbsp;—&nbsp; <name> — <N> mins</div>
<div style="background:#fffef5; padding:12px 14px; color:#1a1a1a;">Instructions.</div></div>
```

Same wrapper with a different header for `🗳️ MENTI` (or the programme's poll tool), `💡 APPLY IT TO YOUR WORK`, `📚 GO DEEPER`, `💻 DEMO NOTES` (watch-and-listen sections still get a box — it is the signal that there is something to do).

**Break box** is black-framed: `border:2px solid #000`, header `background:#000; color:#F8DB59;` reading `☕ BREAK 1 — 10 mins — back for <topic>`, body "Keep this notebook open." Lunch is a plain `# 🍽️ LUNCH BREAK — <times>` heading.

**Grey hand-off box** (challenge hand-off, terminal step, look-at-the-interface): same wrapper, header `background:#434343; color:#fff;`, body `background:#f8f8f8; color:#1a1a1a;`. A `🏆 CHALLENGE TIME` box lists tiers one per `<br>` line: `Q1 · … <br> Q2 · … <br> Q3 · …`.

**Gated instructions** learners should not run yet: commands in `<pre>` blocks inside a labelled box under an explicit "wait for the instructor" heading.

## In-person discussion box (profile delivery = in-person)

Where there is no chat to harvest from, discussion beats are `💬 DISCUSSION` boxes with the answer folded underneath:

```html
<div style="border:2px solid #F8DB59;border-radius:6px;overflow:hidden;margin:24px 0;"><div style="background:#F8DB59;padding:8px 16px;font-family:sans-serif;font-weight:700;font-size:0.78em;letter-spacing:0.08em;color:#000;">💬 DISCUSSION &nbsp;—&nbsp; <question in six words></div><div style="padding:18px 22px;background:#fffef5;font-size:0.95em;line-height:1.7;color:#1a1a1a;"><the question, one or two lines></div></div>

<details><summary><strong>Answer</strong></summary>

<the answer, two or three short lines>

</details>
```

`⌨️ LIVE CODE` (grey body `#f5f5f5`) marks follow-along code in the same minified style.

## Challenge furniture (minified single-line style)

**Difficulty guide badge table** (exact):

```markdown
### Challenge difficulty guide

| Badge | Who it's for | What to expect |
|-------|-------------|----------------|
| <span style="background:#2ecc71;color:#fff;padding:2px 8px;border-radius:3px;font-size:0.85em;font-weight:700;">Q1 EASY</span> | Everyone | Guided tasks — every gap has a hint |
| <span style="background:#f39c12;color:#fff;padding:2px 8px;border-radius:3px;font-size:0.85em;font-weight:700;">Q2 MEDIUM</span> | Comfortable with Python | Partial guidance — some structure given, decisions left to you |
| <span style="background:#e74c3c;color:#fff;padding:2px 8px;border-radius:3px;font-size:0.85em;font-weight:700;">Q3 HARD</span> | Confident coders | HINT comments only — build it from scratch |

Solutions are hidden in `<details>` blocks — attempt before revealing.
```

**Tier banner** (header text white; grammar `⚡ Q<n> <TIER> &nbsp;—&nbsp; <topic> &nbsp;·&nbsp; <Individual|Group> &nbsp;·&nbsp; <N> mins`):

```html
<div style="border:2px solid #2ecc71;border-radius:6px;overflow:hidden;margin:24px 0;"><div style="background:#2ecc71;padding:8px 16px;font-family:sans-serif;font-weight:700;font-size:0.78em;letter-spacing:0.08em;color:#fff;">⚡ Q1 EASY &nbsp;—&nbsp; <topic> &nbsp;·&nbsp; Individual &nbsp;·&nbsp; 15 mins</div><div style="padding:18px 22px;background:#f5fff8;font-size:0.95em;line-height:1.7;color:#1a1a1a;">Task text. <strong>Task 1.1 —</strong> …</div></div>
```

MEDIUM: swap `#2ecc71`→`#f39c12`, body `#f5fff8`→`#fffdf0`. HARD: `#e74c3c` / `#fff5f5`. The matching yellow box uses the same minified wrapper with `#F8DB59` header (black text) and `#fffef5` body — poll notes, `🚀 STRETCH` pointers, case-study briefs.

**Block dividers**: black banner `background:#000;color:#F8DB59;padding:18px 24px;border-radius:6px;margin:28px 0;` with `<strong style="font-size:1.15em;">☀️ MORNING BLOCK</strong>` + muted white subtitle listing the block's challenges. Block names and emoji come from the profile's block structure.

**Hackathon track banners**: `border:2px solid <tier>; border-radius:8px; margin:14px 0;`, header `🟢 EASY TRACK &nbsp;—&nbsp; ~50 mins` white-on-tier, body `#fffef5`.

**Reflect strip + solution block** — one spelling only:

````markdown
<div style="border:2px solid #F8DB59; border-radius:8px; margin:10px 0;">
<div style="background:#FFF2CC; color:#000; padding:8px 14px; font-weight:bold;">💭 REFLECT &nbsp;—&nbsp; before you open the solution</div>
<div style="background:#fffef5; padding:12px 14px; color:#1a1a1a;"><one question that makes the learner reason about the output></div></div>

<details>
<summary><strong>Solution — attempt before opening</strong></summary>

```python
# complete solution
```

**Reflect — answer:** <the answer, two sentences max>

</details>
````

**Writing cells**: `**Q1 — <label>**` then `*Your answer — double-click this cell to edit and type here.*`

## Legacy spellings to normalise when you meet them

- Tier colours `#4CAF50/#FF9800/#F44336` and `CHALLENGE EASY` labels → the Q1/Q2/Q3 system above.
- `Solutions` / bare `Solution` summaries → `Solution — attempt before opening`.
- Five-underscore gap masking → `___`.
- Jupyter auto-anchor TOC links → explicit `<a id>` anchors.
- A `📓 CHALLENGE` grey bar (`#333`) mid-demo → the grey `🏆 CHALLENGE TIME` box.
