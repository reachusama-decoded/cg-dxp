# Skills Graph

An interactive map of every skill in [`skills/`](../../skills), laid out as one
column per DPLC lifecycle phase, left to right, and wired together by the
dependencies each skill declares in its own `SKILL.md` frontmatter.

| | |
|---|---|
| **Page** | [`index.html`](index.html) — zero dependencies, no build step, no CDN |
| **Data** | [`graph.json`](graph.json) — **generated, do not hand-edit** |
| **Generator** | [`scripts/build_skills_graph.py`](../../scripts/build_skills_graph.py) |
| **Guard** | [`tests/ci/test_skills_graph.py`](../../tests/ci/test_skills_graph.py) |

## Viewing it

**Locally** — browsers block `fetch` over `file://`, so serve the folder rather
than double-clicking the file. Serve **`docs/`**, not `docs/skills-graph/`, so
the local paths match what Pages actually publishes:

```bash
python3 -m http.server -d docs
# then open http://localhost:8000/skills-graph/
```

**Published** — via GitHub Pages, served straight from `docs/` on `main`
(**Settings → Pages → Source: Deploy from a branch, `main` / `docs`,
Visibility: Private**). This matches how the sibling skills repo
[`cg-edo/edo-ai-skills`](https://github.com/cg-edo/edo-ai-skills) publishes its
own skill graph, and needs no CI — repo-owned GitHub Actions are not enabled in
this org.

Because the branch itself is the source, **whatever is committed under `docs/`
is what is served**. There is no build step and no deploy to wait on: merging a
regenerated `graph.json` to `main` publishes it. That also means the staleness
guard below is the only thing standing between a skill change and a wrong
published graph — run it.

> Pages is not enabled on this repo yet; a repo admin has to set the three
> values above once. Until then, use the local preview command.

## Updating it — the harness

`graph.json` is derived entirely from frontmatter, so **any** skill change can
make it stale. Regenerate after adding, removing, renaming, or re-phasing a
skill:

```bash
python scripts/build_skills_graph.py
```

You do not have to remember. The offline suite contributors already run fails
if the committed graph drifts from what's on disk:

```bash
python -m pytest tests/ci tests/skills -q
```

A stale graph reports the specific drift, not just a diff:

```
Failed: docs/skills-graph/graph.json is stale — skills missing from the graph:
my-new-skill. Run: python scripts/build_skills_graph.py
```

`python scripts/build_skills_graph.py --check` is the same check as a standalone
exit code, matching the convention in `scripts/sync_plugin_version.py`.

## What the graph encodes

| Channel | Meaning |
|---|---|
| **Column (left to right)** | Lifecycle phase, in order 0 → 8, then cross-cutting and standalone |
| **Color** | Stage — Design, Build, Ship, Cross-cutting, Standalone |
| **Glyph** | Tier — `◆` orchestrator, `▲` workflow, `■` document, `●` capability, `?` undeclared |
| **Solid edge** | `metadata.dependencies` — this skill composes that one |
| **Dashed edge** | `metadata.consumes` — this skill reads that one's artifact |
| **Dashed outline** | Skill is not registered in `plugin.json` |
| **⚠ amber glyph** | Skill's frontmatter omits `tier` and/or `lifecycle-phase` |

Phase is *ordinal* — phase 3 genuinely follows phase 2 — so it is encoded by
position, where the order is visible. Color is spent on stage instead, which
keeps the palette to four hues plus a neutral. The four were validated for
colorblind separation and contrast against the page surface rather than picked
by eye; every node also carries a permanently visible text label, so identity
never rests on color alone.

## Notes on the data

- **Agents.** The generator reads `agents/*.md` if that directory exists. It
  does not today, so the graph renders zero agents; they will appear
  automatically if agents are ever added.
- **File inputs.** Nine `consumes` entries name files (`dbt_project.yml`,
  `.env`, `Dockerfile`) rather than skills. Those are not edges — they are
  listed under "File inputs" in a skill's detail panel.
- **Frontmatter gaps.** Two skills — `catalyst-feedback` and `dplc-validate` —
  predate the RFD 0006 metadata block and omit `tier` and/or `lifecycle-phase`.
  The graph does **not** guess a value for them: guessing would have drawn the
  `dplc-validate` orchestrator as a leaf capability. They are marked
  `unspecified` and surfaced by the **⚠ Incomplete frontmatter** filter.

  That filter is **load-bearing, not a transitional artifact.** Both skills are
  deliberate `xfail` entries in `tests/ci/test_skill_frontmatter_contract.py`
  (`_PRE_RFD0006_NO_METADATA_TIER`, `_PRE_RFD0006_NO_ALLOWED_TOOLS`), so the
  contract suite passes while the gaps remain. The graph is the place they stay
  visible. Closing them — and deleting the allowlists — is tracked in
  **AICAT-288**; until that lands, expect this filter to report 2.
