## Module 1 — Software engineering, your first programs and Copilot {#day01-m1}

**0:10 to 1:10.** Serves outcomes 1, 2 and 3. Learners place a reporting script in the lifecycle, write it in a notebook, turn it into a script with Copilot, review every generated line and record one check. Module 1 also sets Copilot up for the whole programme, so protect the four moves and the agent-mode demo above everything else.

The module answers seven questions, and the Module 1 handbook covers each one in depth:

1. What is software engineering, and what are the stages of the software development lifecycle?
2. How do notebooks and scripts differ, and when is each useful?
3. How does Python execute code in Jupyter and VS Code?
4. Which Python syntax and control structures are needed for the exemplar task?
5. How do I debug, organise and document code so it can be reused?
6. Where do integration, release and deployment fit into the lifecycle?
7. How do I use CG's VS Code and Copilot workflow for engineering tasks: context, prompts, planning a change, reviewing generated code, validating with deterministic checks, retaining responsibility for correctness?

**Bridge in.** Learners have the setup and nothing else yet; this module starts from Jordan's finished table and ends with their own version of the script that prints it.

### Teach and demo · 20 minutes

**0:10 to 0:30.** Twenty minutes covers the core of each idea, in the order the Module 1 handbook takes them, not every block. Teach every beat from its visual in the demo anchor's Module 1 section, which opens on the module map and the demo data's card, and say once, at minute 0, that the handbook carries the rest. The section closes on a short bridge out, *Where the report goes next*, then a Challenge time box that names the three challenge tiers, then a Go deeper box pointing to the Module 1 handbook, and the Module 1 section of the challenge ends on the same Go deeper box, so learners know where the depth lives after the session.

**Left to the Module 1 handbook, not taught live:** the Python building blocks, the notebook-or-script table, CI/CD and the three places code lives, the quiet wrong answer and the debugger, context and slash commands, and the mode and model tables. The four reuse habits come back inside the demo's review step, with the Catalyst rules.

| Min | Beat | What to say | What to do |
|---|---|---|---|
| 0 | Jordan's report | "This is what Jordan sends every week. Read it before the code." | The module map, `figures/m1-map.png`, at the top of the anchor's Module 1 section, then the demo data's card under it: "Harbourline's HLF funds, 46 share classes, prices to 30 September 2026. Your challenges use a different family, the challenge data." Don't read the Files row. Then *The finished output*: run `python m1_fund_report_reviewed.py` from the anchor. Hands up: notebook? terminal? Copilot? Then the category chart, `figures/m1-one-year-return-by-category.png`, in the same section |
| 2 | The loop | "Programming is making it work once. Engineering is making it keep working." | The lifecycle card, `figures/m1-lifecycle.png`, in *The loop round your code*. Ask where a notebook stops; let them answer: at Build |
| 4 | Bench and card | "A notebook remembers. A script forgets. Both are features." | The bench-and-card figure, `figures/m1-notebook-vs-script.png`, then the kernel diagram (Mermaid), in *Bench and card*. Predict aloud, then run the `x = 1` and `x + 1` cells, delete the first and rerun the second; then the two `python -c` cells, the second raising `NameError` |
| 7 | One error on purpose | "Here's the error you'll meet first. Read three things, ignore the rest." | The traceback card, `figures/m1-read-a-traceback.png`, in *One error on purpose*. Open a terminal in `demo/` and run `python m1_break_it.py`; read the last line, then find the first line in our file. Back to the anchor for the one-line fix, which prints `11684` |
| 9 | A script you can reuse | "Same table, organised so someone else can run it." | The reusable-script card, `figures/m1-reusable-script.png`, in *What makes a script reusable*. Open `m1_fund_report_reviewed.py` beside the anchor and point at the four habits. Select `build_report` and send the prompt in the COPILOT box there (Ask, a fast model, the selection). Tick three facts against the code, then come back |
| 11 | The four moves | "Plan, generate, review, validate. Plan's the one people skip." | The four-moves diagram (Mermaid) in *The four moves* |
| 12 | Notebook to script with Copilot | "Same output, no notebook state, from the terminal." | The five-part brief card, `figures/m1-five-part-brief.png`, in *From notebook to script with Copilot*, then the agent-mode run split below |
| 20 | Into the challenge | "Your report, the challenge data, 25 minutes. Copilot fixes it; you review it." | Read *Where the report goes next* aloud, then the Challenge time box under it: Q1 to Q3 in a line each. Point at the Go deeper box under it: the Module 1 handbook, for after the session. Then open `challenge/day01_challenge.ipynb` at the Module 1 section |

#### The points on each visual

Three to five points per visual, each one a sentence you say while it's on screen. None of the visuals needs a "proper words" line, because each one already labels its analogy against the technical terms.

**The module map.**

- Seven stops, one report: from Jordan's table to a script Copilot helped write and a check you ran.
- Each stop names what it leaves behind, so you can tick it off as we go.
- Every stop leaves something you could show someone.

**The category chart.**

- Read the axis before you believe a bar chart: this one starts at zero, so the lengths are honest.
- UK Gilts at 3.05 against Emerging Markets Equity at 55.59: a real spread, not a trick of the axis.
- The UK Equity bar, 26.83, is the mean of the eight rows we just printed.
- Every I class beats its A sibling: same portfolio, lower charge.

**The lifecycle card.**

- Seven stages, round in a loop: what you learn while operating becomes the next design.
- Each stage leaves an artefact someone else can see; a stage with no artefact didn't really happen.
- A notebook stops at Build. Everything after Build is what engineering adds.
- The three yellow stages, integrate, release and deploy, are where the report stops being something only Jordan can produce.

**The bench-and-card figure and the kernel diagram.**

- Both make the same table; the difference is whether anyone but you can make it again.
- The kernel is a separate process that holds variables, not cells, until you restart it.
- A script gets a fresh interpreter every run and forgets everything at exit, which is what a weekly report needs.
- Restart and Run All is the notebook's test; two identical terminal runs are the script's.

**The traceback card.**

- The last line says what happened: a `TypeError`.
- The names say which values: the `Timestamp` we typed against the `datetime.date` in the column.
- Your own line says where: the first frame in a file you wrote. The pandas frames show how it got there.
- Fix the cause: convert the column once, straight after loading. Never a bare `except:`.

**The reusable-script card.**

- One job per function: `load_data`, `one_year_return`, `build_report`.
- A docstring on each, one imperative sentence.
- The `__main__` guard: run the file and it prints; import it and it doesn't.
- Paths from the file, not the terminal, so it runs from any folder.

**The four-moves diagram.**

- Plan, generate, review, validate, in that order, every time.
- Plan names the check before you prompt; without it, the other moves can't tell a good result from a plausible one.
- A failed check sends you back to the plan, not to another quick prompt.

**The five-part brief card.**

- Intent, context, format, constraints, check: each part removes a guess the model would otherwise make.
- The context names the date quirk, because the model can't see the data.
- The check, 8 rows summing to 214.63, tells the model what done means and commits you to running it.

<!-- sensitive: clear -->
**At the `/explain` beat,** don't show a canned answer, because the wording changes from run to run and model to model. Read whatever the room's Copilot produces and tick the three facts together: it keeps one category's rows, adds the latest NAV and the one-year return as columns, and sorts best first. If the answer is wrong, say so, because that's the best possible moment in the module. If Ask mode isn't available, the same prompt works in inline chat on the selected function.

#### The agent-mode demo, minutes 12 to 20

Eight minutes, run from *From notebook to script with Copilot* in the anchor. The prompt sits in the COPILOT box in that section of the anchor, ready to paste, and the script appears beside it.

| Min | Step | Do |
|---|---|---|
| 12 | Plan (1) | In the Chat view, set Copilot up as the COPILOT box in *From notebook to script with Copilot* says: **Agent**, and a fast model for a small, known change. Paste its five-part prompt. It attaches the notebook with `#` and names the check: 8 rows, the return column sums to 214.63 |
| 13 | Generate (2) | Talk through the five parts on the brief card while the agent works. Say why this mode and this model |
| 15 | Review (2) | Open the new `fund_report.py` and walk each edit against the four review questions in the anchor's Review cell, then its Catalyst line as CG's own version of the same habits. **Keep** or **Undo** each edit |
| 17 | Run twice (2) | In the terminal: `python fund_report.py > report.txt`, `python fund_report.py > report_run2.txt`, then `diff report.txt report_run2.txt && echo "identical"` |
| 19 | Validate (1) | In the room, the evidence is for Copilot's file. In the check cell at the end of the section, change `m1_fund_report_reviewed` to `fund_report` in the import and run it: it must print `check passed: 8 rows, sum 214.63, same table as the notebook`. Skip the run-twice cell above it, because the terminal run at minute 17 has already done it. If the import fails because Copilot named `DATA` or `CATEGORY` differently, use its names and say why: that's a review finding. Undo the import change afterwards, so the anchor still runs for learners. Then open `m1_checks.md` to show the recorded check, and come back |

<!-- sensitive: clear -->
- "Copilot said it's done. That's a claim. This is the evidence." Say it at the diff.
- If the room's Copilot turns `>=` into `>`, don't fix it silently. Run the check, watch it fail on 222.78, and fix it in front of them: if it happens, it's the module's best moment.
- Check that `DATA` resolves from `__file__`, not from the terminal's folder. Proof if asked: `cd .. && python demo/fund_report.py | head -1` still prints the title line.
- Changed the script after the anchor imported it? Restart and Run All before the check, because the kernel keeps the version it imported first.

**Fallback.** If Copilot hasn't finished after 2 minutes, or isn't signed in, run `cp m1_fund_report_reviewed.py fund_report.py` in `demo/`, say that's what you're doing, open it as if Copilot had just written it, and do the review and validate steps on it.

#### Facts to have ready

- **The exemplar.** UK Equity, demo data, one-year return to 2026-09-30: 8 rows, best HLF002-I-ACC at 29.34, category mean 26.83%. Every I class beats its A sibling (29.34 against 28.72, 27.71 against 27.13, 24.10 against 23.66). `INC` classes carry the same price path as their `ACC` sibling in this data.
- **The chart.** Category means across the 46 share classes: UK Gilts 3.05, Money Market 4.61, Global Bonds 10.00, Multi-Asset 14.68, Global Equity 22.84, UK Equity 26.83, Emerging Markets Equity 55.59.
- **Why `>=`.** A one-year return compares the latest price with the price a year earlier, so the base date belongs in the window. With `>` the window loses the base-date close: the UK Equity column sums to 222.78 and the mean is 27.85%. If someone raises the convention, that's the right instinct: say which one you use and pin it with a check.
- **The check rounds on purpose.** It asserts on the 2-dp column because that's what the reader sees. Unrounded, the returns sum to 214.6227, which rounds to 214.62. A check that fails by 0.01 is the rounding conversation, not a bug.
- **The error.** `m1_break_it.py` filters before converting the date column and stops with `TypeError: Cannot compare Timestamp with datetime.date`. With `pd.to_datetime` straight after loading, the same filter keeps 11684 rows.
- **`print` stays.** Catalyst's RFD 0008 rules out `print()` in production code (PY-IDIOM-016) but makes an exception for command-line tools that write to standard output on purpose, and the report script is one. If someone wants logging, the trigger is "as soon as the script runs where nobody watches it".
- **CI/CD.** Keep it to the yellow stages on the lifecycle card. Harness is CG's CI/CD platform, as confirmed by CG's programme contact on 2026-10-13: name it if asked, don't demo it. Session 02 builds the pipeline.

<!-- sensitive: clear -->
- **Modes, if asked.** Ask answers questions about code without changing files; Plan produces a step-by-step plan before anything changes; Agent takes a task, edits files, runs commands and tries again when something fails. Agent isn't the advanced mode; it's the mode for jobs that create or change files. If the room's VS Code still shows Edit, it does the same job for a known change in named files, and the demo works either way. A fast model suits quick edits and questions, a reasoning model multi-step work, and which models learners see is set by their administrator.
- **Three names to keep apart.** Catalyst supplies the skills, Copilot is the chat and agent in VS Code that uses them, and the model, chosen in the picker, writes the reply. Catalyst's own Copilot instructions ask reviewers to cite a rule ID per comment: present that as Catalyst's instruction for its own reviews, not as CG-wide practice.

#### Questions to expect

- **"Is a notebook not software?"** It is, at the Build stage, and it stops there unless you carry it round the loop. VS Code can export a notebook as a `.py` file, but that's the cells in page order with the scratch work left in: a file, not yet a script.
- **"Why Operate and not Maintain?"** Both are in use, and writers split the loop into six or seven phases. The loop is the point, not the label.
- **"When does a pipeline run?"** As soon as your change has tests a machine can run for you. That's Session 02.

**If there's a spare minute.** A script that exits cleanly can still be wrong. Change the category to `"UK equity"`, with a small e, and the report runs without an error, prints an empty table and a mean of `nan%`. A loud crash beats a quiet wrong answer, which is why the check counts the rows.

### Challenge · 25 minutes

**0:30 to 0:55.** Start on time, even if the demo ran short: learners have `day01_demo.ipynb` for anything you skipped, and the challenge stands alone, so nobody needs a demo cell to have run. The Module 1 section of `challenge/day01_challenge.ipynb`, "Fix, then review Copilot", opens on the module map as its recap visual, then sets three tiers on the challenge data. Learners direct Copilot to make every fix and review what it wrote; they never type the code. Each task that prompts Copilot has a COPILOT box with a starting prompt to copy and adapt, and its badges say which mode and model to pick.

| Tier | Minutes | The task | Outcome it evidences |
|---|---|---|---|
| Setup | 1 | Run the setup cell under the challenge data's card: `✅ Challenge data found: 49 share classes` | None on its own |
| Q1 · CORE · Fix the report cell | 8 | Jordan's report cell stops with a `KeyError`. Note the three things to read, `/explain` it in Ask mode, check the answer against the traceback, have Copilot fix the cause, review the one-word change, **Keep** it and rerun | 2: a notebook cell that runs; 3: explain, review, Keep |
| Q2 · STRETCH · Review the script Copilot wrote | 12 | `m1_fund_report_copilot.py`, presented as what Copilot wrote from that cell, runs but hides three problems. Run it from `challenge/` and from the folder above, compare with Q1, review each function, list the problems, have Copilot fix each one and write the check, review every changed line, run it, record it in My checks | 2: the script prints the notebook's table; 3: a review note and a recorded check |
| Your turn · Name the stage | 2 | The lifecycle stage of each thing they made | 1 |
| Q3 · BONUS · Make the category an argument | Not expected | A five-part brief, Agent mode, a line-by-line review and a run on two categories | 3 |

#### What to say

<!-- sensitive: clear -->
- "Same columns as the demo, different funds: the challenge data. Its card is at the top of the notebook."
- "Copilot does the typing. You read the traceback, you review every line it changes, and you run the check."
- "Q1: Jordan's cell stops. Read three things before you ask Copilot anything."
- "Q2: Copilot wrote a script from that cell. It runs, and it's still wrong in three places. Find them before you ask for fixes."
- "Keep or Undo is your decision, not Copilot's: write down why."
- "Start at Q1. Q3 is there if you finish; nobody's expected to reach it."

#### What to do

- [ ] Open `challenge/day01_challenge.ipynb` at the Module 1 section on screen
- [ ] Pair anyone who answered no to the first self-check question with someone who answered yes, with the newcomer as reviewer
- [ ] Walk the room at 0:38 and 0:50: anyone still on Q1 at 0:38 gets the first hint below, anyone with fewer than three problems in My review at 0:50 gets the second
- [ ] Give a two-minute warning at 0:53, and send anyone who hasn't done it to the Your turn box

#### What a finished challenge looks like

Q1 and Q2 end on the same table: Global Equity, challenge data, one-year return to 2026-09-30, as the fixed script prints it.

```text
share_class_id share_class  ongoing_charge_pct     nav  one_year_return_pct
  HLP007-I-ACC       I Acc                0.51 1636.74                52.68
  HLP007-A-ACC       A Acc                0.98  157.95                51.96
  HLP005-I-ACC       I Acc                0.44 3164.79                40.22
  HLP008-A-ACC       A Acc                0.87  132.70                40.13
  HLP005-A-ACC       A Acc                0.93  286.83                39.53
  HLP006-I-ACC       I Acc                0.43 1829.40                34.13
  HLP006-A-ACC       A Acc                0.86  171.88                33.55
  HLP006-A-INC       A Inc                0.86  171.88                33.55
Category mean: 40.72%
```

- **Q1.** The three things: the last line is `KeyError: "['ongoing_charge'] not in index"`; the name is `ongoing_charge`, a column the data doesn't have (it's `ongoing_charge_pct`); their own line is line 12 of the cell, the `cols = ...` line the arrow points at. Copilot's fix changes that one name and nothing else; the rerun prints the 8 rows. My reading is filled in, including whether Copilot's explanation agreed with the traceback.
- **Q2, before the fixes.** From `challenge/` the script prints 7 rows, HLP006-A-INC missing, and `Category mean: 41.74%`. From the folder above it prints `No data this week: nothing to report.` and `exit code: 0`.
- **Q2, the three problems.** `DATA = Path("../../../../common/data/challenge")` resolves from the terminal's folder, not the script's; `chosen[chosen["share_class"].str.endswith("Acc")]` drops the Inc class, which nobody asked for; `except Exception:` in `main()` turns any error, a missing file included, into a friendly line and exit code 0.
- **Q2, after the fixes.** Both run cells print the 8 rows above. The check cell prints `check passed: 8 rows, sum 325.75, same table as Q1`; it asserts on the 2-dp column, because unrounded the returns sum to 325.74. My checks holds the prompt, the mode and model and why, one quoted review note and the result.
- **Your turn.** Build, Build, Test, Test. Integrate, Release, Deploy and Operate have nothing yet.
- **Q3.** `"UK Equity"` prints 9 rows and `Category mean: 27.95%`; `"UK equity"` stops with `error: unknown category 'UK equity'; choose from: …` and exit code 2; Global Equity and the Q2 check are unchanged.

#### The two likeliest stalls

| Stall | What you'll see | Hint |
|---|---|---|
| Asking Copilot before reading the traceback | The whole error pasted into chat, the first fix accepted, and My reading empty | "Last line, the name, your own line: write those three down first, then check Copilot's explanation against them. If they disagree, the traceback wins." |
| Q2 finds one problem, not three | The folder problem shows itself from the folder above; the dropped row and the hidden error don't, because both runs exit with 0 | "Count the rows against your Q1 table, and ask what the script does when the data isn't there. Then read `build_report` and `main()` line by line: which line would you not have written?" |

### Debrief · 5 minutes

**0:55 to 1:00.** One count, one question and the takeaways; don't let it eat the break.

#### What to say

- "Who got 8 rows from the script? Who saw 7 first?" The missing Inc class is the quiet wrong answer: no error, just a table one row short, and only the comparison with Q1 caught it.
- "Who found all three problems? Which one would a scheduler never have told you about?" The hidden error: it exited with 0.

<!-- sensitive: clear -->
- "Copilot wrote some of your code. You wrote the check. Which of the two are you sure about?"
- "What did your review check, and what did it find?"
- The three takeaways, one per outcome served:
  - Software engineering is the loop round your code, design to operate, with each stage leaving an artefact someone else can see.
  - A notebook keeps state and a script starts clean: Restart and Run All proves the notebook, two identical terminal runs prove the script.
  - With Copilot, plan the change and its check, pick the mode and model, read every line, and run a check that gives the same answer every time.

#### What to do

- [ ] Harvest one or two stage tables aloud. Look for reasoning, not the Module 1 handbook's wording: who sees each artefact, and why Release means a pinned environment plus a README rather than "I ran it". If someone writes "Deploy: I ran it", that's Build; say so kindly
- [ ] Ask: "Which of the three would you not have believed an hour ago?"

### Break · 10 minutes

**1:00 to 1:10.**

- [ ] Keep VS Code and the terminal open for Module 2
- [ ] Check anyone whose remote wasn't running at the welcome: `bash service.sh status` in `services/remote-machine/`
- [ ] Skim questions from the challenge and answer them after the break

**Bridge out.** "Your script runs from your terminal now. As soon as it has to run somewhere else, you need to find your way round a terminal on a machine you can't click on." Module 2 copies the learner's fixed `m1_fund_report_copilot.py` onto the Harbourline remote over SSH, moves round its filesystem and captures what the script prints and logs.

### If they already know this

Ask the key questions first: "Who can say what a kernel is?" and "Who's used Copilot's agent mode?" If most of the room writes Python daily, take the bench and the card in a minute and spend the saved time on the review move: what did Copilot change that nobody asked for?

### If prerequisites are missing

Nobody needs notebook experience. A learner who has never opened one runs the Module 1 cells of `day01_demo.ipynb` one at a time with **Shift+Enter** and watches the outputs appear. If the room is new to Python, take the building blocks from the Module 1 handbook at the error beat with one prediction: "What will `charge_band(0.93), charge_band(0.38), charge_band(1.20)` print?" The answer is `Mid Low High`. Add one line at the function, "I'm wrapping this in a function because we're about to call it eight times, then forty-six", and take those minutes from the four moves, which the demo shows in use anyway.

If the room is new to notebooks and you have a spare minute after the bench and card, run the hidden-state walk-through from the Module 1 handbook in a copy of the anchor: move the `to_datetime` and `as_of` lines into a new last cell, run it, rerun the window cell (it prints 11684), then Restart and Run All, and the window cell stops with `NameError: name 'as_of' is not defined`. It's the most convincing minute in the module for anyone new to notebooks.

Pair newcomers with someone confident for the challenge, with the newcomer as reviewer, because reading every generated line is the skill that matters most here.

### Fallbacks

| Problem | Do this |
|---|---|
| Copilot isn't signed in, or is slow | `cp m1_fund_report_reviewed.py fund_report.py` in `demo/`, open it as if Copilot had just written it, and do the review and validate moves on it. Learners without Copilot pair with a neighbour and review |
| The notebook kernel won't start | Run every block as a script from the terminal; nothing in the module needs Jupyter to make its point |
| No network | Everything in Module 1 runs offline except Copilot. Use the first fallback |
| A learner's remote won't build | It isn't needed until Module 2. Point them at the troubleshooting table in `services/remote-machine/README.md` during the break |
| Learners ask for the Copilot quick reference or the programme's Copilot appendix | Neither is published yet. Until they are, point at the five-part brief and the four review questions in the Module 1 handbook |

