# Word builds (from CG Core's scripts/docx)

`build_lesson_plan.js`, `preview_docx.py`, the logo and the fonts in `../fonts/` are copies of the CG Core repository's `scripts/docx/` and `scripts/fonts/` (sibling clone under `reference/ts-cg-core/`), taken on 7 Nov 2026. The builder reads a Markdown file through pandoc and writes an A4-landscape Word document in the Decoded house style (Work Sans and Fira Code embedded, the brand palette, the logo); its `## Timeline` section becomes one table with a dark band per H3 section and a coloured label per activity row (`#### H:MM · N min · <activity type> — <title>`). Anything it does not know stops the build, so nothing is dropped silently.

One change from the original: the header, title and description read the programme and document kind from `DOC_PROGRAMME` and `DOC_KIND` (defaults: "CG Core", "lesson plan"). `build_all.py` sets them to "Data Creators" and "run sheet" and writes each day's `run-sheet.md` in the builder's dialect, then `run-sheet.docx` beside it.

Install once: `cd research/scripts/docx && npm install` (node_modules is ignored). Needs `node` and `pandoc` on PATH (or `PANDOC` set).
