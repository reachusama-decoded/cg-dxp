"""One-off: demo, challenge, reflect and fallback boxes become one line + steps beneath (ran 7 Nov 2026)."""
import ast, pathlib, re
HERE = pathlib.Path(__file__).resolve().parent.parent

# ---------- 1. helpers ----------
dc = HERE / "dc.py"; s = dc.read_text()
old_challenge = '''def challenge(title_text: str, path: str, minutes: str, body: str) -> str:
    return _box(GREY, GREY, "#fff", "#f8f8f8", f"🏆 CHALLENGE TIME &nbsp;—&nbsp; {title_text} &nbsp;·&nbsp; {minutes}",
                f"In the training repository: <code>{path}</code>.<br><br>{body}")
'''
new_challenge = '''def _list(items: list[str], numbered: bool = True) -> str:
    return "\\n".join((f"{i}. {t}" if numbered else f"- {t}") for i, t in enumerate(items, 1))

def _after(box: str, parts: list[str]) -> str:
    """A one-line box, then plain Markdown beneath it (a blank line ends the HTML block)."""
    return box + "".join("\\n\\n" + p for p in parts if p)

def challenge(title_text: str, path: str, minutes: str, line: str, phases: list[tuple[str, list[str]]], gate: str,
              support: list[str] | None = None, stretch: str | None = None) -> str:
    """One line in the box; what learners do, phase by phase, one line per step; then the gate, support and stretch."""
    box = _box(GREY, GREY, "#fff", "#f8f8f8", f"🏆 CHALLENGE TIME &nbsp;—&nbsp; {title_text} &nbsp;·&nbsp; {minutes}",
               f"{line} &nbsp;·&nbsp; <code>{path}</code>")
    parts = [f"**{label}**\\n\\n{_list(steps)}" for label, steps in phases]
    parts.append(f"**Gate.** {gate}")
    if support:
        parts.append("**Support.**\\n\\n" + _list(support, numbered=False))
    if stretch:
        parts.append(f"**Finished early?** {stretch}")
    return _after(box, parts)
'''
old_demo = '''def demo(title_text: str, body: str) -> str:
    return _box("#434343", "#C9DAF8", TEXT, "#fff", f"🖥️ DEMO &nbsp;—&nbsp; {title_text}", body)

def reflect(title_text: str, body: str) -> str:
    return _box("#F8DB59", "#FFF2CC", "#000", "#fffef5", f"💭 {title_text}", body)
'''
new_demo = '''def demo(title_text: str, line: str, steps: list[str] | None = None) -> str:
    """One line in the box; the exact steps to show learners beneath it, one line each."""
    box = _box("#434343", "#C9DAF8", TEXT, "#fff", f"🖥️ DEMO &nbsp;—&nbsp; {title_text}", line)
    return _after(box, [_list(steps)] if steps else [])

def reflect(title_text: str, line: str, bullets: list[str] | None = None) -> str:
    box = _box("#F8DB59", "#FFF2CC", "#000", "#fffef5", f"💭 {title_text}", line)
    return _after(box, [_list(bullets, numbered=False)] if bullets else [])
'''
old_fallback = '''def fallback(body: str) -> str:
    return _box("#F4CCCC", "#F4CCCC", TEXT, "#fff", "🧯 IF IT BREAKS", body)
'''
new_fallback = '''def fallback(line: str, bullets: list[str] | None = None) -> str:
    box = _box("#F4CCCC", "#F4CCCC", TEXT, "#fff", "🧯 IF IT BREAKS", line)
    return _after(box, [_list(bullets, numbered=False)] if bullets else [])
'''
for old, new in [(old_challenge, new_challenge), (old_demo, new_demo), (old_fallback, new_fallback)]:
    assert s.count(old) == 1, old[:40]
    s = s.replace(old, new)
dc.write_text(s)

# ---------- 2. call sites ----------
NEW = {
("day1.py", 189): r'''dc.fallback("No sponsor today? Give the opening yourself in five minutes, then move on.", [
                     "The three-second test, the four personas and the publishing promise, from the anchor.",
                     "Log every question about access or policy in the Q&A table for the platform team."])''',
("day1.py", 255): r'''dc.demo("the data-contract skill, then a PRD from the transcript", "A Catalyst skill is a prompt file: watch one run on the transcript, then find the invented detail.", [
                  "Open `.claude/skills/data-contract/SKILL.md` (installed by `common/catalyst/install-skills.sh`; the same file learners see in the Catalyst repo): the eight required sections and the quality checks.",
                  "Open `.claude/skills/data-contract/templates/data-contract.md`: identity, schema, SLAs, quality rules, access, change management, consumer registry, approvals, revision history.",
                  "Open `.claude/skills/dplc-design/SKILL.md`: it chains requirements-acceptance-criteria, feasibility-report, consumer-use-case-map and data-model.",
                  "Open `.claude/skills/dplc-concierge/SKILL.md` and say: start it Friday, maybe a product by Monday.",
                  "Learners' form: Copilot Chat, `/ai-catalyst product-requirements-document`, paste a description.",
                  "Instructor's form: Claude Code in `courseware/`, `/product-requirements-document`, paste `common/running-example/interview-transcript.md`.",
                  "Point at the moment the skill file is read: that is how you know Catalyst is on, not plain Copilot.",
                  "Read one section of the result aloud and find the invented detail before accepting anything."])''',
("day1.py", 263): r'''dc.fallback("Catalyst not installed or slow on the demo laptop: review the prepared PRD instead; the lesson survives without the generation.", [
                     "Open `common/running-example/prd.md`: the reviewed output, with the corrections in brackets.",
                     "Walk the Key Product Information, Problem and Value, and Consumers sections."])''',
("day1.py", 288): r'''dc.demo("the interface on the running example", "Copilot Chat and Claude Code side by side: model, effort and context, on one real task.", [
                  "Open Copilot Chat (what learners see) and Claude Code (this laptop) side by side.",
                  "Model picker: name this week's models; say which is least compressed and most expensive.",
                  "Thinking effort: ask the same question at low and at maximum; compare the time and the answer.",
                  "Context: show the conversation length, then `/clear` in Claude or a new chat in Copilot; say when to do it.",
                  "The task: \"Add realistic SLAs to this contract\" with `common/running-example/data-contract.md` attached.",
                  "Then: \"List every number in the SLA section and where it came from.\""])''',
("day1.py", 304): r'''dc.demo("Voice Memos to transcript", "A recording on the laptop becomes the transcript Catalyst reads: free and good enough.", [
                  "Open Voice Memos on the Mac; record thirty seconds of a mock interview; pause; Done.",
                  "Click Transcript to show the text; click off and on again, then Copy transcript.",
                  "Say: on Teams or Zoom the meeting transcript does the same job.",
                  "Paste the transcript into the Catalyst prompt."])''',
("day1.py", 318): r'''dc.reflect("REFLECT — the planted-errors contract", "Five invented details are planted in this contract; the room gets three minutes to find them.", [
                     "Open `common/running-example/data-contract-planted-errors.md` on the projector; the answer key is at the end of the file.",
                     "Name the pattern afterwards: identifiers, dates, versions, approvals and confident numbers are where models fill gaps."])''',
("day2.py", 163): r'''dc.demo("Markdown editor, then a self-contained HTML page", "Read Markdown properly, then turn the contract into one HTML page on a small model and on a big one.", [
                  "Right-click a submitted contract, Open with…, Markdown editor (or Open Preview); edit one cell.",
                  "Say: this is how to read the long READMEs on Wednesday and Thursday.",
                  "In Claude Code (or Copilot) run the prompt below on a fast model at low effort.",
                  "Open the result in the browser: contents, overview, diagrams.",
                  "Start the same prompt on the biggest model at high effort; let it run while you teach; compare when it finishes.",
                  "Say why the reasoning is hidden now (vendors stopped showing traces after competitors trained on them) and why the big model is slow."])''',
("day2.py", 199): r'''dc.demo("Delta under the hood, on this laptop", "A Delta table is Parquet files plus a log: the cell writes one and reads every version back.", [
                  "Run the cell: it writes the vendor prices as a Delta table, appends a day, merges a correction, reads version 0, compacts, and reads the table from DuckDB.",
                  "Open the table folder the script names: the Parquet files and `_delta_log/*.json`.",
                  "Point at the merge output: the corrected row replaced, the old file kept, the log naming the files in each version.",
                  "Say: on Databricks the same table sits in S3 and Spark reads it; the format is open, which is why dbt, DuckDB, Spark and pandas all read it."])''',
("day2.py", 206): r'''dc.demo("the Spark engine, locally", "A local Spark shows the driver, executors, partitions and the shuffle that Databricks runs for you at scale.", [
                  "Run the cell (about thirty seconds): a local Spark with four executors loads the vendor prices multiplied up and runs a SQL aggregate.",
                  "Find *Exchange* in the printed physical plan: that is the shuffle between stages.",
                  "Run it again with `--hold 90` and open http://localhost:4040: Jobs, Stages, the SQL tab.",
                  "Say: Databricks is this on many machines, with Delta and Unity Catalog around it, and you never configure it."])''',
("day2.py", 229): r'''dc.reflect("SHAREBACK — one minute per table", "Each table answers in one minute.", [
                     "One thing Databricks does that a plain file store cannot.",
                     "One thing dbt relies on Databricks for.",
                     "One tool on the diagram you have used, and one you have not."])''',
("day2.py", 240): r'''dc.demo("the five steps of Challenge 7, in cells", "The challenge's own six-holding app (`demos/docker/portfolio-summary/`), run and built in cells before learners do it.", [
                  "Check Docker Desktop is running: the whale in the menu bar, or `docker info`.",
                  "Cell 1: run `python:3.11-slim` and print its Python; the container exits when the command does.",
                  "Cell 2: write a file inside one container and list it from another: its own filesystem, gone with the container.",
                  "Cell 3: read the app's Dockerfile: FROM, WORKDIR, COPY, CMD.",
                  "Cell 4: build twice; the second build is all CACHED.",
                  "Cell 5: run the app, then run it with a mounted holdings file: same image, different data.",
                  "Cell 6: tag the image: two names, one ID; that is how CG ships Airflow and dbt images.",
                  "After each cell, say what learners will see at the same step of `challenges/v1/01-docker-intro`."])''',
("day2.py", 247): r'''dc.demo("the dev container's Dockerfile", "The learners' dev container is a Dockerfile they can now read.", [
                  "Open `reference/DataCreators-client/dev-container/edo-training-data-products/.devcontainer/Dockerfile`, the file VS Code builds for learners (the cell below prints its head).",
                  "Point at the two `FROM` lines: a flyway stage, then CG's Python 3.13 image from the internal registry.",
                  "Point at the `RUN curl` lines: the Astro CLI, starship and mise; then `mise install databricks-cli`.",
                  "Point at `COPY` of the setup scripts and `ENV VIRTUAL_ENV=/opt/venv` with its `bin` on `PATH`.",
                  "Say: EDO maintains this; you never will; but now you can read it.",
                  "Open Docker Desktop: Images, then Settings and Resources, briefly."])''',
("day2.py", 250): r'''dc.challenge("Docker practical", "challenges/v1/01-docker-intro/README.md", "35 min",
                            "Sections 1 to 5: run an image, look inside, write the Dockerfile, build it, run it.",
                            [("What learners do", [
                                "`docker --version`; if the engine is not running, start Docker Desktop.",
                                "Section 1, run an image: a container from a public Python image.",
                                "Section 2, look inside: the container's own filesystem and processes.",
                                "Section 3, write the Dockerfile: `starter/Dockerfile` has one TODO per line.",
                                "Section 4, build the image.",
                                "Section 5, run the image: the app runs the same anywhere."])],
                            "`mise run challenge:verify 01` prints PASS.",
                            support=["Engine not running means Docker Desktop is not started on the laptop.",
                                     "CRLF line endings on Windows cause `exec format error`.",
                                     "The first pull is slow once."],
                            stretch="Section 6: tags, the variations, multi-stage builds, resource limits.")''',
("day2.py", 261): r'''dc.demo("where output lands: Databricks for learners, DuckDB here", "Learners' tables land in Databricks under their own schema; here the same tables land in a DuckDB file.", [
                  "Learners: `mise run setup:databricks` (browser OAuth; Enter through the prompts), then `dpc-check`.",
                  "Databricks UI: Catalog, `training_dev`, `training_<username>`; every dbt table appears there.",
                  "Say: on the paved path you rarely open this UI; you write dbt in files and commit.",
                  "Here: run the cell below; it lists the same schema in the DuckDB file once the prepared project is built."])''',
("day2.py", 268): r'''dc.demo("one minute of live generation", "Start the generation live, stop after a minute, then open the finished project.", [
                  "In Claude Code: `/setup-dbt-project` with `common/running-example/data-contract.md` and `sttm.md` attached.",
                  "Let it run for a minute and narrate what it reads first.",
                  "Stop it and open `demos/contract-to-code/eod_prices/models/`: every CTE comments the STTM rule it implements.",
                  "Open `tests/` and `schema.yml` there: the tests mirror the contract's quality rules.",
                  "Open `eod_prices_daily.py` in `../day4-airflow/demos/airflow_local/dags/eod_prices/dags/`: the schedule comes from the SLA."])''',
("day3.py", 89): r'''dc.challenge("dbt practical (challenge 02)", "challenges/v1/02-dbt-pipeline/README.md", "about 3 hours across the day",
                      "Build, test and document the Portfolio Analytics pipeline: eight staging sections, then ten challenges.",
                      [("Where to work", [
                          "`cd challenges/v1/02-dbt-pipeline/dbt`; every `dbt` command runs from here.",
                          "`dbt debug` (connection), `dbt seed` (eight CSVs into `training_dev.training_<you>`), `dbt ls --resource-type model` (ten stubs).",
                          "`mise run challenge:verify 02` and `challenge:reset 02` run from anywhere; never reset to \"start clean\": it deletes authored work."]),
                       ("Phase 1, about an hour", [
                          "S1 Inspect the raw data.", "S2 Read the dbt project.", "S3 Declare sources and freshness.", "S4 First staging model: `stg_holdings`.",
                          "S5 The remaining staging models.", "S6 Materialisations: view vs table.", "S7 Build the whole staging layer.", "S8 A staging test."]),
                       ("Phase 2", [
                          "C1 The enrichment join: `int_holdings_enriched`.", "C2 The two supporting intermediate models.", "C3 First curated mart: `agg_fund_exposure`.",
                          "C4 Second curated mart: `fct_portfolio_returns`.", "C5 Generic tests on the marts.", "C6 A singular reconciliation test: NAV within tolerance.",
                          "C7 The full build: `dbt build`.", "C8 Docs and the lineage graph.", "C9 The Databricks post-hook: `OPTIMIZE … ZORDER`.", "C10 Capstone: a new mart end to end."])],
                      "`mise run challenge:verify 02` runs seeds, models and tests; green means solved.",
                      support=["Keep a list of commands, configuration changes, questions and discoveries; the recap is built from it."])''',
("day3.py", 100): r'''dc.demo("the same project, on DuckDB, section by section", f"The learners' challenge 02 solution ported to DuckDB in <code>{PA}/</code>: one cell per README section, for \"what should I see?\".", [
                  "Same model names, layers, tags and tests; the Databricks-only post-hook is a no-op macro here.",
                  f"Use a cell when someone asks what they should see; `{PA}/README.md` maps each cell to its README section.",
                  "Say once: the SQL is the same; only the target differs."])''',
("day3.py", 132): r'''dc.reflect("CIRCULATION CHECKLIST — three questions per learner", "Ask: could this join pass its tests and still double the reported value? A successful build alone is insufficient.", [
                     "Sources and staging: can they say what one row means, name its key, and explain the types and units?",
                     "Joins and models: are the lookup keys unique on the right-hand side, do dates belong in the join, and what happens to unmatched rows?",
                     "Tests and output: can they show a value checked independently of the model that produced it?",
                     "Check the row grain, right-side uniqueness, unmatched rows and an independent total."])''',
("day4.py", 123): r'''dc.demo("three loads on DuckDB, then the four questions", "Three loads of a tiny associate feed, then the four questions, from one script.", [
                  "Run the cell: `demos/bitemporal/demo.sh` seeds, loads day 1, loads day 2, loads the correction, and prints the history and the as-is, as-of and as-was queries.",
                  "Read the history row by row: which load wrote each row, and which clock closed it.",
                  "Run the two `sql()` cells: the audit trail for one associate, then as-of 2 November.",
                  "Open `demos/bitemporal/macros/bitemporal_load.sql` (the cell prints it): three steps on one screen.",
                  "Say: the paved path's `bitemporal_load_v2` does the same job with more strategies."])''',
("day4.py", 136): r'''dc.reflect("GUEST OR VOLUNTEER BRIEF — ten minutes", "Show one real bitemporal table, then take two questions.", [
                     "The DL columns, and one row's history ordered by system start.",
                     "One change that created a version; one correction if you have one.",
                     "Which strategy the model uses: full, incremental or balance.",
                     "If a defect once created a version, show it: the table is an audit of what the code did."])''',
("day4.py", 137): r'''dc.reflect("SHAREBACK — which clock?", "Each table takes one question: say the clock, then the filter.", [
                     "What was the associate's title on 2 November?",
                     "What did the dashboard show on the morning of day 2?",
                     "When did we learn about the correction?",
                     "Which rows does an auditor need to see?"])''',
("day4.py", 159): r'''dc.demo("the stack, a run, the UI", "Trigger a run on the local Astro stack and read it in the UI the way learners will.", [
                  f"Before the day, in `{AL}/`: `bash run.sh start`.",
                  "Run the cells below: seed, trigger, wait, status.",
                  "Open http://localhost:8080: the DAGs list with owner, schedule and tags.",
                  "Graph view: five boxes and the dbt task group.",
                  "Grid view: one column per run.",
                  "Click `publish_to_catalog` and open its log: the published rows are in it.",
                  "Code tab: the DAG file as deployed.",
                  "Say: learners use the same commands: `astro dev run dags list`, `dags trigger`, `tasks states-for-dag-run`."])''',
("day4.py", 172): r'''dc.demo("a controlled failure, then the repair", "Break the freshness gate on purpose, read the log, repair, rerun.", [
                  "Run the stale cell: the custodian feed looks two days old; a run is triggered.",
                  "Watch the freshness gate fail and everything downstream go `upstream_failed`: no publish, no rows.",
                  "Open the failed task's log in the UI and read the first useful line aloud.",
                  "Run the fresh cell: the feed is stamped fresh, a run is triggered, green.",
                  "Say: this is the same drill as the challenge's Phase 2 and Friday's questions: late input, failed check, repeated run."])''',
("day4.py", 176): r'''dc.challenge("Airflow practical (challenge 03)", "challenges/v1/03-airflow-orchestration/README.md", "until 13:30, with lunch",
                      "Wire, schedule and run the Portfolio Analytics DAG with Cosmos; Phase 2 is production operations.",
                      [("Prerequisites, in this order", [
                          "`mise run setup:databricks` done, in a terminal where `echo $DBT_CATALOG` prints a value.",
                          "`(cd challenges/v1/02-dbt-pipeline/dbt && dbt seed)`: the DAG reads the same four feeds, refreshed.",
                          "From the repo root, `astro dev start`, only after setup finished; the UI address is the one astro prints, not a fixed localhost:8080."]),
                       ("Phase 1, about 1.5 hours", [
                          "1 Why orchestration.", "2 Anatomy of a DAG.", "3 Connect to Databricks: `dbt debug`.",
                          "4 The freshness gate: `astro dev run tasks test portfolio_analytics_daily source_freshness_check 2026-05-04`.",
                          "5 The Cosmos `DbtTaskGroup`.",
                          "6 Wire the chain, the one TODO: `start >> source_freshness_check >> dbt_pipeline >> publish_to_catalog >> end`.",
                          "7 Scheduling: a timezone-aware cron.", "8 Retries and exponential backoff.", "9 First full run.", "10 Reading logs and re-running."]),
                       ("Phase 2", [
                          "1 The vendor-neutral alert transport.", "2 Tiered failure alerting.", "3 The P2 and P3 tiers: SLA miss and retry.",
                          "4 Wire the callbacks and the SLA into the DAG.", "5 The freshness gate as a contract.", "6 The monitoring config.",
                          "7 The runbook and the consumer guide.", "8 Structural tests for the DAG.", "9 Stretch: the `DatabricksSubmitRunOperator` variant.", "10 Capstone: a production-ready DAG."])],
                      "`mise run challenge:verify 03` is a static check of the wiring; the live run is the evidence: graph, logs, states.",
                      stretch="What happens if the input is late? If the quality check fails? If the run is repeated? Show a log or output check for each answer.")''',
("day4.py", 210): r'''dc.demo("Harness, with screenshots or a guest", "Walk a deployment to SQA and then to production: live if someone has access, else from the pre-flight screenshots.", [
                  "Pick the environment and find the repository's pipeline.",
                  "SQA: Run, apply the SQA input set, choose the feature branch, run; a few minutes.",
                  "Check who deployed to SQA last and whether they finished testing: SQA is shared.",
                  "Production: the PRD pipeline, fixed values, the release branch, and a change record (CRQ) number before anything runs.",
                  "Open the logs of a failed execution.",
                  "Say: secrets live in AWS Secrets Manager, never in code or a chat; an API token that lets an AI assistant trigger deployments is a risk, not a shortcut."])''',
("day4.py", 235): r'''dc.reflect("FRIDAY CHECKLIST — every learner, before leaving", "Five checks; any failure goes on the list with a name and a time it will be fixed.", [
                     "☐ Open `challenges/v1/04-atlas-capstone/README.md` and read the plan of the day.",
                     "☐ From the repo root: `test -f .mise.toml && test -d data_products/atlas_elt && echo OK`.",
                     "☐ `mise exec -- databricks auth describe --profile DEFAULT`.",
                     "☐ From `data_products/atlas_elt`: `dbt debug` passes.",
                     "☐ `astro dev stop`, so tomorrow starts clean."])''',
("day5.py", 115): r'''dc.challenge("Atlas capstone, Phase 1", "challenges/v1/04-atlas-capstone/README.md", "two to three hours",
                      "Every team establishes the baseline: seeds, the three layers, the tests, and the orchestration understood.",
                      [("Readiness, from the repo root", [
                          "`test -f .mise.toml && test -d data_products/atlas_elt && echo OK`.",
                          "`mise exec -- databricks auth describe --profile DEFAULT`.",
                          "`cd data_products/atlas_elt && dbt debug`."]),
                       ("Sections", [
                          "1 Inspect the source data.", "2 Understand the dbt project: `dbt deps`, `dbt ls`.", "3 Set up the Databricks connection.", "4 `dbt seed`.",
                          "5 Build source-aligned: `dbt run --select tag:source-aligned`.", "6 Build domain-aligned.", "7 Build consumer-aligned and run the tests.", "8 Understand the orchestration."])],
                      "`mise run challenge:verify 04` (not a bare verify.sh: it needs mise's environment); compare numbers with the expected results below.",
                      support=["Edit only under `data_products/atlas_elt/`; the stubs under `challenges/` are reset templates; solutions live with the instructor."])''',
("day5.py", 172): r'''dc.reflect("CERTIFICATION EVIDENCE — what Phase 1 shows per team", "Observed during the day, not handed in.", [
                     "The worksheet: consumer, decision, sources, rules, assumptions.",
                     "The three layers built with the tag selectors.",
                     "The tests passing, including the reconciliations.",
                     "One value checked independently of the model that produced it.",
                     "An explanation of what the orchestration triggers and where dbt runs.",
                     "A presentation that states a finding and a caveat."])''',
}

found = set()
for fname in ["day1.py", "day2.py", "day3.py", "day4.py", "day5.py"]:
    p = HERE / fname; src = p.read_text(); tree = ast.parse(src)
    repl = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("demo", "challenge", "fallback", "reflect"):
            key = (fname, node.lineno); found.add(key)
            seg = ast.get_source_segment(src, node)
            assert key in NEW, f"no replacement for {key}"
            repl.append((seg, NEW[key]))
    for seg, new in repl:
        assert src.count(seg) == 1, (fname, seg[:60])
        src = src.replace(seg, new)
    p.write_text(src)
    ast.parse(src)  # still valid Python
missing = set(NEW) - found
assert not missing, f"replacements never applied: {missing}"
print(f"replaced {len(found)} boxes in 5 modules; helpers updated")
