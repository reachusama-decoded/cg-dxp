// build_lesson_plan.js: a CG Core lesson plan (dayNN_lesson_plan.md) to the instructors' Word document (user, 2026-10-16).
// The Markdown is the source (format: .claude/skills/lesson-plan/references/format.md). pandoc reads it; this script
// writes the .docx in build_overview.js's house style: Work Sans, the brand palette, A4 landscape, the Decoded logo.
//
//   node scripts/docx/build_lesson_plan.js <dayNN_lesson_plan.md> <out.docx>
//
// "## Timeline" becomes one table (Timing · Activity and notes · Assessment): each H3 a dark section band, each H4
// ("H:MM[:SS] · N min · <type> — <title>", e.g. "0:12:30 · 2.5 min · …") an activity row with its coloured label. Anything this script doesn't know
// stops the build, so nothing an instructor relies on is dropped silently. HTML comments are dropped on purpose.
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
        AlignmentType, LevelFormat, Header, Footer, PageNumber, ImageRun, VerticalAlign, ExternalHyperlink, PageOrientation,
        HeadingLevel } = require("docx");

const [MD, OUT] = process.argv.slice(2);
if (!MD || !OUT) {
  console.error("usage: node build_lesson_plan.js <dayNN_lesson_plan.md> <out.docx>");
  process.exit(2);
}
const LOGO = path.join(__dirname, "logo-decoded.png");
// cg-dxp: the header, title and description name the programme and the document kind (defaults are CG Core's)
const PROGRAMME = process.env.DOC_PROGRAMME || "CG Core", KIND = process.env.DOC_KIND || "lesson plan";
const ASSESS_HEADER = process.env.DOC_ASSESS_HEADER || "Assessment";

// house style, as build_overview.js
const FONT = "Work Sans", MONO = "Fira Code";
const FONTS = path.join(__dirname, "..", "fonts");
const BLACK = "000000", DARK = "434343", GREY = "666666", MID = "CCCCCC", LIGHT = "F3F3F3", YELLOW = "FEF800";
// A4 landscape, 2 cm margins (user, 2026-10-19: easier to read, less text-heavy). docx-js takes the portrait size plus
// the orientation and swaps them, so the page is given portrait; the text runs across the long side.
// cg-dxp: DOC_ORIENTATION=portrait gives an A4 portrait page (the prep guides); the default stays landscape (run sheets)
const PORTRAIT = (process.env.DOC_ORIENTATION || "landscape") === "portrait";
const A4_SHORT = 11906, A4_LONG = 16838, MARGIN = 1134, CONTENT_W = (PORTRAIT ? A4_SHORT : A4_LONG) - 2 * MARGIN;
const BODY = 20, CELL = 18, SMALL = 16, LABEL = 14, TITLE = 32, H1 = 28, H2 = 24, H3 = 21;  // half-points
const LINE = 300, CELL_LINE = 264;

// the seven activity types (format.md: Activity types) and their label colours
const TYPES = {
  "Intro/Outro": "D0E0E3", "Explain": "C9DAF8", "Instructor-led demo": "F8DB59", "Questioning": "FFF2CC",
  "Independent or pairs work": "D9EAD3", "Feedback and discussion": "F4CCCC", "Break": "F3F3F3",
};
// the Copilot box, as scripts/pdf-filters/copilot-box.lua and nbkit.copilot_prompt draw it
// (badges in the order WHERE, MODE, MODEL, ATTACH; MODE with Chat view only, where it is required; Chat view for
// questions, plans and jobs that change files, Inline chat for one change to the selected lines, Terminal chat for a
// shell command to read before it runs). mode="" counts as no mode; a mode that isn't Ask, Plan or Agent, or one given
// with Inline chat or Terminal chat, warns on stderr and is left out, never drawn as a badge (copilot-box.lua does the same)
const COPILOT = { frame: "434343", head: "C9DAF8", body: "F4F7FD", WHERE: "D0E0E3", MODE: "F8DB59", MODEL: "C9DAF8", ATTACH: "D9EAD3" };
const WHERES = ["Chat view", "Inline chat", "Terminal chat"], MODES = ["Ask", "Plan", "Agent"], MODELS = ["Fast", "Reasoning", "Auto"];
const THEN = {
  Ask: "**Then** check the answer against the code: the code is the final word.",
  Plan: "**Then** read the plan before anything changes: does it cover every requirement and name the check?",
  Agent: "**Then** read every line it wrote, choose **Keep** or **Undo**, and run the check.",
};
// the closing line for the surfaces without a mode
const THEN_WHERE = {
  "Inline chat": "**Then** read the change in the editor, choose **Keep** or **Undo**, and run the check.",
  "Terminal chat": "**Then** choose **Insert**, not Run: read the command, press Enter, and check what it printed.",
};
// a row's fields (format.md); key questions live in the Question bank, never in a row, except a Questioning row's
// Ask, Listen for and If stuck (user, 2026-10-27); an intro row's From the overview (the persona card or the day's
// outcomes, quoted word for word) and a module section's Module outcomes (user, 2026-10-27)
const FIELDS = ["Purpose", "On screen", "From the overview", "Instructor notes", "Ask", "Listen for", "If stuck", "Say", "Adapt", "Transition", "Assessment", "Module outcomes"];
// a row starts at H:MM, or H:MM:SS on a half minute (0:12:30), and runs in 2.5-minute steps (user, 2026-10-27)
const ROW = /^(\d+:[0-5]\d(?::[0-5]\d)?) · (\d+(?:\.\d+)?) min · (.+?) — (.+)$/;
// the Assessment column is narrow (user, 2026-10-19): its entries are two short parts, "Outcome N · <evidence>", or —
const TIMING_W = 1500, ASSESS_W = 1900, NOTES_W = CONTENT_W - TIMING_W - ASSESS_W;

function fail(msg) {
  console.error(`build_lesson_plan: ${msg}`);
  process.exit(1);
}

// ---------- read the Markdown with pandoc ----------
function pandocBin() {
  if (process.env.PANDOC) return process.env.PANDOC;
  const tools = path.join(process.env.HOME || "", ".cache/build-pdf/tools");
  if (fs.existsSync(tools)) {
    for (const d of fs.readdirSync(tools).filter(n => n.startsWith("pandoc-")).sort().reverse()) {
      for (const e of fs.readdirSync(path.join(tools, d))) {
        const bin = path.join(tools, d, e, "bin", "pandoc");
        if (fs.existsSync(bin)) return bin;
      }
    }
  }
  return "pandoc";
}
let ast;
try {
  ast = JSON.parse(execFileSync(pandocBin(), ["-f", "markdown", "-t", "json", MD], { maxBuffer: 64 << 20 }));
} catch (e) {
  fail(`pandoc could not read ${MD}: ${e.message} (set PANDOC, or run ./build-pdf setup once)`);
}

// ---------- inlines ----------
const plain = inl => inl.map(x => {
  switch (x.t) {
    case "Str": return x.c;
    case "Space": case "SoftBreak": return " ";
    case "LineBreak": return "\n";
    case "Code": return x.c[1];
    case "Quoted": return (x.c[0].t === "SingleQuote" ? "‘" : "“") + plain(x.c[1]) + (x.c[0].t === "SingleQuote" ? "’" : "”");
    case "Strong": case "Emph": case "Underline": case "SmallCaps": case "Strikeout": return plain(x.c);
    case "Span": return plain(x.c[1]);
    case "Link": return plain(x.c[1]);
    default: return "";
  }
}).join("");

function runs(inl, st = {}) {
  const size = st.size || BODY;
  const style = extra => ({ font: FONT, bold: !!st.bold, size, color: st.color || BLACK, italics: !!st.italic, ...extra });
  const out = [];
  const push = t => { if (t) out.push(new TextRun({ text: t, ...style() })); };
  for (const x of inl) {
    switch (x.t) {
      case "Str": push(x.c); break;
      case "Space": case "SoftBreak": push(" "); break;
      case "LineBreak": out.push(new TextRun({ break: 1, ...style() })); break;
      case "Strong": out.push(...runs(x.c, { ...st, bold: true })); break;
      case "Emph": out.push(...runs(x.c, { ...st, italic: true })); break;
      case "Underline": case "SmallCaps": case "Superscript": case "Subscript": out.push(...runs(x.c, st)); break;
      case "Code":
        out.push(new TextRun({ text: x.c[1], ...style({ font: MONO, size: size - 2,
          shading: { type: ShadingType.CLEAR, fill: st.codeFill || LIGHT, color: "auto" } }) }));
        break;
      case "Quoted": {
        const single = x.c[0].t === "SingleQuote";
        push(single ? "‘" : "“"); out.push(...runs(x.c[1], st)); push(single ? "’" : "”");
        break;
      }
      case "Link": {
        const [, inner, [url]] = x.c;
        if (/^https?:/.test(url)) out.push(new ExternalHyperlink({ link: url, children: runs(inner, { ...st, color: "1155CC" }) }));
        else out.push(...runs(inner, st));
        break;
      }
      case "Span": out.push(...runs(x.c[1], st)); break;
      case "Image": out.push(imageRun(x, ctxWidth(st))); break;
      case "RawInline":
        if (x.c[0] === "html" && /^<!--[\s\S]*-->$/.test(x.c[1].trim())) break;
        fail(`raw ${x.c[0]} in the text: ${x.c[1].slice(0, 60)} (write a placeholder as ‹…›, not <…>)`);
        break;
      default: fail(`unsupported inline: ${x.t}`);
    }
  }
  return out;
}

// ---------- images (cg-dxp) ----------
// A PNG in the Markdown becomes an inline picture scaled to the column; the diagrams were rendered at scale 2, so a
// picture is shown at half its pixel size unless the column is narrower. Only PNG is supported; anything else stops the build.
const ctxWidth = st => st.width || CONTENT_W;
function imageRun(x, widthDxa) {
  const [, , [src]] = x.c;
  const file = path.resolve(path.dirname(MD), decodeURI(src));
  if (!fs.existsSync(file)) fail(`image not found: ${src} (resolved to ${file})`);
  const png = fs.readFileSync(file);
  if (png.readUInt32BE(0) !== 0x89504e47) fail(`only PNG images are supported: ${src}`);
  const w = png.readUInt32BE(16), h = png.readUInt32BE(20);
  const maxPx = Math.floor(widthDxa / 20 * 96 / 72) - 8;
  const width = Math.min(maxPx, Math.round(w / 2));
  return new ImageRun({ type: "png", data: png, transformation: { width, height: Math.round(width * h / w) } });
}

// ---------- blocks ----------
let listInstance = 0;
const border = { style: BorderStyle.SINGLE, size: 4, color: MID };
const borders = { top: border, bottom: border, left: border, right: border, insideHorizontal: border, insideVertical: border };
const isComment = b => b.t === "RawBlock" && b.c[0] === "html" && /^<!--[\s\S]*-->$/.test(b.c[1].trim());

function para(inl, ctx, extra = {}) {
  return new Paragraph({ children: runs(inl, { size: ctx.size }), spacing: { after: ctx.cell ? 80 : 120, line: ctx.cell ? CELL_LINE : LINE }, ...extra });
}

function listItems(items, ctx, ordered) {
  const out = [];
  const level = ctx.level || 0;
  const instance = ordered ? ++listInstance : 0;
  const spacing = { after: ctx.cell ? 40 : 60, line: ctx.cell ? CELL_LINE : LINE };
  for (const item of items) {
    let first = true;
    for (const b of item) {
      if ((b.t === "Plain" || b.t === "Para") && first) {
        // a task-list item ("- [ ]") already starts with its box: no bullet as well. Its wrapped lines hang under its
        // text, and outside a table each item has room above it, so a checklist of short items, each with its
        // commands as sub-bullets, reads at a glance (user, 2026-10-19)
        const box = !ordered && b.c.length && b.c[0].t === "Str" && /^[☐☒]/.test(b.c[0].c);
        if (box) out.push(new Paragraph({ children: runs(b.c, { size: ctx.size }), indent: { left: 360 * level + 520, hanging: 340 },
          spacing: { ...spacing, before: ctx.cell ? 0 : 100 } }));
        else out.push(new Paragraph({ children: runs(b.c, { size: ctx.size }),
          numbering: ordered ? { reference: "numbers", level, instance } : { reference: "bullets", level }, spacing }));
        first = false;
      } else if (b.t === "BulletList" || b.t === "OrderedList") {
        out.push(...blocks([b], { ...ctx, level: Math.min(level + 1, 2), nested: true }));
      } else {
        out.push(...blocks([b], { ...ctx, indent: 360 * (level + 1) }));
        first = false;
      }
    }
  }
  // one spacer after a whole list, never inside one
  if (!ctx.cell && !ctx.nested) out.push(new Paragraph({ spacing: { after: 40 } }));
  return out;
}

function codeBlock(code, ctx) {
  const lines = code.replace(/\n$/, "").split("\n");
  return lines.map((l, i) => new Paragraph({
    children: [new TextRun({ text: l || " ", font: MONO, size: (ctx.size || BODY) - 3, color: BLACK })],
    shading: { type: ShadingType.CLEAR, fill: LIGHT, color: "auto" },
    indent: ctx.indent ? { left: ctx.indent } : undefined,
    spacing: { before: i === 0 ? 60 : 0, after: i === lines.length - 1 ? 120 : 0, line: 240 },
    keepLines: true, keepNext: i < lines.length - 1,
  }));
}

// Column widths follow the average text in each column, but never drop below what the column's longest word needs,
// so a short column ("Learning objective") doesn't break its words letter by letter.
function widths(header, body, total) {
  const longest = header.map((h, i) => Math.max(...[h, ...body.map(r => r[i] || "")].flatMap(t => t.split(/\s+/)).map(w => w.length)));
  const floor = longest.map(n => Math.min(Math.max(520, n * 105 + 220), Math.round(total * 0.4)));
  const weight = header.map((h, i) => {
    const cells = body.map(r => (r[i] || "").length);
    const mean = cells.length ? cells.reduce((a, b) => a + b, 0) / cells.length : 0;
    return Math.max(6, mean, h.length * 0.8);
  });
  const spare = total - floor.reduce((a, b) => a + b, 0);
  const sum = weight.reduce((a, b) => a + b, 0);
  const w = spare > 0 ? floor.map((f, i) => f + Math.round(spare * weight[i] / sum)) : floor.map(f => Math.round(f * total / floor.reduce((a, b) => a + b, 0)));
  w[w.indexOf(Math.max(...w))] += total - w.reduce((a, b) => a + b, 0);
  return w;
}

function houseTable(t, ctx) {
  const [, , , thead, tbodies] = t.c;
  const cellBlocks = c => c[4];
  const head = (thead[1][0] || [null, []])[1];
  const body = tbodies.flatMap(tb => [...tb[2], ...tb[3]]).map(r => r[1]);
  const total = ctx.width || CONTENT_W;
  // a table with no header row (a grid table, such as the persona card an intro row quotes) still has its columns
  const ncol = Math.max(head.length, ...body.map(r => r.length));
  const headText = Array.from({ length: ncol }, (_, i) => (head[i] ? blocksText(cellBlocks(head[i])) : ""));
  const w = widths(headText, body.map(r => r.map(c => blocksText(cellBlocks(c)))), total);
  const typed = head.length && blocksText(cellBlocks(head[0])).trim() === "Activity type";
  const cell = (c, i, isHead, row) => {
    const name = blocksText(cellBlocks(c)).trim();
    const fill = isHead ? LIGHT : (typed && i === 0 && TYPES[name]) ? TYPES[name] : undefined;
    return new TableCell({
      width: { size: w[i], type: WidthType.DXA },
      shading: fill ? { type: ShadingType.CLEAR, fill, color: "auto" } : undefined,
      margins: { top: 60, bottom: 60, left: 90, right: 90 },
      verticalAlign: VerticalAlign.TOP,
      children: cellChildren(isHead ? boldBlocks(cellBlocks(c)) : cellBlocks(c), { size: SMALL + 2, cell: true, width: w[i] - 180 }),
    });
  };
  const rows = [];
  if (head.length) rows.push(new TableRow({ tableHeader: true, children: head.map((c, i) => cell(c, i, true)) }));
  for (const r of body) rows.push(new TableRow({ children: r.map((c, i) => cell(c, i, false)) }));
  const out = [new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: w, borders, rows })];
  if (!ctx.cell) out.push(new Paragraph({ spacing: { after: 160 } }));
  return out;
}

const boldBlocks = bs => bs.map(b => (b.t === "Plain" || b.t === "Para") ? { t: b.t, c: [{ t: "Strong", c: b.c }] } : b);
function blocksText(bs) {
  return bs.map(b => {
    if (b.t === "Plain" || b.t === "Para") return plain(b.c);
    if (b.t === "BulletList" || b.t === "OrderedList") return (b.t === "OrderedList" ? b.c[1] : b.c).map(blocksText).join(" ");
    if (b.t === "CodeBlock") return b.c[1];
    return "";
  }).join(" ");
}
// a table cell must hold at least one paragraph
function cellChildren(bs, ctx) {
  const out = blocks(bs, ctx);
  return out.length ? out : [new Paragraph({ children: [] })];
}

function box(headRuns, headFill, bodyChildren, ctx, frame = COPILOT.frame, bodyFill) {
  const total = ctx.width || CONTENT_W;
  const line = { style: BorderStyle.SINGLE, size: 10, color: frame };
  const edge = { top: line, bottom: line, left: line, right: line, insideHorizontal: line, insideVertical: line };
  const cell = (children, fill) => new TableCell({
    width: { size: total, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 140, right: 140 },
    shading: fill ? { type: ShadingType.CLEAR, fill, color: "auto" } : undefined, children,
  });
  const out = [new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: [total], borders: edge, rows: [
    new TableRow({ cantSplit: true, children: [cell([new Paragraph({ children: headRuns, spacing: { after: 0 }, keepNext: true })], headFill)] }),
    new TableRow({ children: [cell(bodyChildren.length ? bodyChildren : [new Paragraph({ children: [] })], bodyFill)] }),
  ] })];
  out.push(new Paragraph({ spacing: { after: ctx.cell ? 60 : 160 } }));
  return out;
}

function badge(label, value, size) {
  const fill = COPILOT[label];
  return [
    new TextRun({ text: ` ${label} `, font: FONT, bold: true, size: size - 4, color: "1A1A1A", shading: { type: ShadingType.CLEAR, fill, color: "auto" } }),
    new TextRun({ text: ` ${value} `, font: FONT, size: size - 4, color: "1A1A1A", shading: { type: ShadingType.CLEAR, fill: "FFFFFF", color: "auto" },
      border: { style: BorderStyle.SINGLE, size: 4, color: COPILOT.frame, space: 0 } }),
    new TextRun({ text: "   ", size: size - 4 }),
  ];
}

function copilotBox(attr, content, ctx) {
  const a = Object.fromEntries(attr[2]);
  const size = ctx.size || BODY;
  // a div with no where draws as Chat view (the audit warns)
  let where = a.where || "Chat view";
  if (!WHERES.includes(where)) {
    console.error(`build_lesson_plan: warning: copilot where must be Chat view, Inline chat or Terminal chat, got '${where}'; drawn as Chat view`);
    where = "Chat view";
  }
  let mode = a.mode || undefined;  // an empty mode is no mode
  if (where === "Chat view") {
    if (!MODES.includes(mode)) {
      console.error(`build_lesson_plan: warning: copilot mode must be Ask, Plan or Agent in Chat view, got '${mode || ""}'; no MODE badge and no closing line ('${a.title || ""}')`);
      mode = undefined;
    }
  } else {
    if (mode) console.error(`build_lesson_plan: warning: ${where} has no mode: mode '${mode}' left out ('${a.title || ""}')`);
    mode = undefined;
  }
  if (!MODELS.includes(a.model)) console.error(`build_lesson_plan: warning: copilot model must be Fast, Reasoning or Auto, got '${a.model}'`);
  const head = [new TextRun({ text: "COPILOT", font: FONT, bold: true, size, color: BLACK }), new TextRun({ text: "  —  " + (a.title || ""), font: FONT, bold: true, size, color: BLACK })];
  const badges = [...badge("WHERE", where, size)];
  if (mode) badges.push(...badge("MODE", mode, size));
  badges.push(...badge("MODEL", a.model || "", size));
  if (a.attach) badges.push(...badge("ATTACH", a.attach, size));
  const inner = { ...ctx, cell: true, width: (ctx.width || CONTENT_W) - 280 };
  const children = [new Paragraph({ children: badges, spacing: { after: 100 } }), ...blocks(content, inner)];
  const then = a.then === undefined ? (where === "Chat view" ? THEN[mode] : THEN_WHERE[where]) : a.then;
  if (then && then !== "none") {
    const t = JSON.parse(execFileSync(pandocBin(), ["-f", "markdown", "-t", "json"], { input: then }));
    children.push(...blocks(t.blocks, inner));
  }
  return box(head, COPILOT.head, children, ctx, COPILOT.frame, COPILOT.body);
}

// the 🧭 module anchor, as scripts/pdf-filters/module-anchor.lua and nbkit.anchor_box_html draw it (user, 2026-10-27):
// a dark header with the title attribute ("WHAT, WHY AND HOW"; never the module title), the learner's question on a pale grey band, then WHAT, WHY and HOW side by side.
// The div is written by `nbkit.py anchors` from the session's dayNN_anchors.md, never by hand.
const ANCHOR = { frame: "434343", question: "F3F3F3", What: "D0E0E3", Why: "FFF2CC", How: "D9EAD3" };
function anchorBox(attr, content, ctx) {
  const a = Object.fromEntries(attr[2]);
  const size = ctx.size || BODY;
  let question = null;
  const parts = {};
  for (const b of content) {
    if ((b.t === "Para" || b.t === "Plain") && b.c.length && b.c[0].t === "Strong") {
      const label = plain(b.c[0].c).trim().replace(/\.$/, "");
      if (["What", "Why", "How"].includes(label)) {
        const rest = b.c.slice(1);
        while (rest.length && (rest[0].t === "Space" || rest[0].t === "SoftBreak")) rest.shift();
        parts[label] = rest;
        continue;
      }
    }
    if (!question && (b.t === "Para" || b.t === "Plain")) question = b.c.length === 1 && b.c[0].t === "Emph" ? b.c[0].c : b.c;
  }
  if (!question || !parts.What || !parts.Why || !parts.How) fail(`anchor '${a.key || "?"}' needs a question and What, Why and How paragraphs`);
  const total = (ctx.width || CONTENT_W) - (ctx.cell ? 80 : 0), third = Math.floor(total / 3), widths = [third, third, total - 2 * third];
  const line = { style: BorderStyle.SINGLE, size: 10, color: ANCHOR.frame };
  const white = { style: BorderStyle.SINGLE, size: 24, color: "FFFFFF" };
  const shade = fill => ({ type: ShadingType.CLEAR, fill, color: "auto" });
  const span = (children, fill) => new TableCell({ columnSpan: 3, width: { size: total, type: WidthType.DXA },
    margins: { top: 80, bottom: 80, left: 140, right: 140 }, shading: shade(fill), children });
  const tile = (label, k) => new TableCell({ width: { size: widths[k], type: WidthType.DXA }, margins: { top: 80, bottom: 100, left: 120, right: 120 },
    shading: shade(ANCHOR[label]), borders: { top: white, bottom: white, left: k === 0 ? line : white, right: k === 2 ? line : white },
    children: [
      new Paragraph({ children: [new TextRun({ text: label.toUpperCase(), font: FONT, bold: true, size: size - 4, color: "1A1A1A" })], spacing: { after: 40 } }),
      new Paragraph({ children: runs(parts[label], { size, codeFill: "FFFFFF" }), spacing: { after: 0, line: CELL_LINE } }),
    ] });
  const edge = { top: line, bottom: line, left: line, right: line, insideHorizontal: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
    insideVertical: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" } };
  return [new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, borders: edge, rows: [
    new TableRow({ cantSplit: true, children: [span([new Paragraph({ children: [new TextRun({ text: a.title || "", font: FONT, bold: true, size, color: "FFFFFF" })], spacing: { after: 0 }, keepNext: true })], ANCHOR.frame)] }),
    new TableRow({ cantSplit: true, children: [span([new Paragraph({ children: runs(question, { size, italic: true, codeFill: "FFFFFF" }), spacing: { after: 0 }, keepNext: true })], ANCHOR.question)] }),
    new TableRow({ cantSplit: true, children: ["What", "Why", "How"].map(tile) }),
  ] }), new Paragraph({ spacing: { after: ctx.cell ? 60 : 160 } })];
}

function blocks(bs, ctx = {}) {
  const out = [];
  for (const b of bs) {
    switch (b.t) {
      case "Para": case "Plain": {
        const inl = b.c.filter(x => !(x.t === "Space" || x.t === "SoftBreak"));
        if (inl.length === 1 && inl[0].t === "Image") {           // a picture on its own line: centred, its alt text as a caption
          const alt = plain(inl[0].c[1]);
          out.push(new Paragraph({ children: [imageRun(inl[0], ctx.width || CONTENT_W)], alignment: AlignmentType.CENTER, spacing: { before: 120, after: alt ? 40 : 160 }, keepNext: !!alt }));
          if (alt) out.push(new Paragraph({ children: [new TextRun({ text: alt, font: FONT, size: SMALL, color: GREY, italics: true })], alignment: AlignmentType.CENTER, spacing: { after: 200 } }));
          break;
        }
        out.push(para(b.c, ctx, ctx.indent ? { indent: { left: ctx.indent } } : {}));
        break;
      }
      case "Header":
        out.push(new Paragraph({ children: runs(b.c[2], { size: ctx.size, bold: true }), keepNext: true, spacing: { before: 120, after: 80 } }));
        break;
      case "BulletList": out.push(...listItems(b.c, ctx, false)); break;
      case "OrderedList":
        // Word restarts each list at 1: a list split by a comment would be renumbered, so stop instead
        if (b.c[0][0] !== 1) fail(`a numbered list starts at ${b.c[0][0]}: keep a numbered list in one piece (a comment or paragraph between items splits it)`);
        out.push(...listItems(b.c[1], ctx, true));
        break;
      case "CodeBlock": out.push(...codeBlock(b.c[1], ctx)); break;
      case "Table": out.push(...houseTable(b, ctx)); break;
      case "BlockQuote": out.push(...blocks(b.c, { ...ctx, indent: (ctx.indent || 0) + 360 })); break;
      case "Div": {
        const [attr, content] = b.c;
        if (attr[1].includes("copilot")) out.push(...copilotBox(attr, content, ctx));
        else if (attr[1].includes("anchor")) out.push(...anchorBox(attr, content, ctx));
        // CG-access notes are retired: CG Core content never carries one, and scripts/build_session.py stops on one
        else if (attr[1].includes("blocked")) fail("a ::: blocked callout: CG-access notes are retired, so remove it (the session build refuses one too)");
        else fail(`unsupported div class: .${attr[1].join(" .") || "(none)"}`);
        break;
      }
      case "RawBlock":
        if (isComment(b)) break;
        fail(`raw ${b.c[0]} block: ${b.c[1].slice(0, 60)} (write a placeholder as ‹…›, not <…>)`);
        break;
      case "HorizontalRule": break;
      default: fail(`unsupported block: ${b.t}`);
    }
  }
  return out;
}

// ---------- the timeline ----------
function fieldsOf(bs) {
  const out = [];
  let f = null;
  for (const b of bs) {
    if (isComment(b)) continue;
    if ((b.t === "Para" || b.t === "Plain") && b.c.length && b.c[0].t === "Strong") {
      const label = plain(b.c[0].c).trim().replace(/\.$/, "");
      if (FIELDS.includes(label)) {
        const rest = b.c.slice(1);
        while (rest.length && (rest[0].t === "Space" || rest[0].t === "SoftBreak")) rest.shift();
        f = { label, blocks: rest.length ? [{ t: "Para", c: rest }] : [] };
        out.push(f);
        continue;
      }
    }
    if (!f) { f = { label: null, blocks: [] }; out.push(f); }
    f.blocks.push(b);
  }
  return out;
}

function labelled(label, bs, ctx) {
  const lab = new TextRun({ text: `${label}. `, font: FONT, bold: true, size: ctx.size, color: BLACK });
  if (bs.length && (bs[0].t === "Para" || bs[0].t === "Plain")) {
    return [new Paragraph({ children: [lab, ...runs(bs[0].c, { size: ctx.size })], spacing: { after: 80, line: CELL_LINE } }), ...blocks(bs.slice(1), ctx)];
  }
  return [new Paragraph({ children: [lab], spacing: { after: 40, line: CELL_LINE }, keepNext: true }), ...blocks(bs, ctx)];
}

function timelineTable(sections) {
  const tcell = (children, w, extra = {}) => new TableCell({ width: { size: w, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 100, right: 100 },
    verticalAlign: VerticalAlign.TOP, children, ...extra });
  const headRun = t => new Paragraph({ children: [new TextRun({ text: t, font: FONT, bold: true, size: CELL, color: BLACK })], spacing: { after: 0 } });
  const shade = fill => ({ type: ShadingType.CLEAR, fill, color: "auto" });
  const rows = [new TableRow({ tableHeader: true, cantSplit: true, children: [
    tcell([headRun("Timing")], TIMING_W, { shading: shade(LIGHT) }),
    tcell([headRun("Activity and notes")], NOTES_W, { shading: shade(LIGHT) }),
    tcell([headRun(ASSESS_HEADER)], ASSESS_W, { shading: shade(LIGHT) }),
  ] })];
  for (const s of sections) {
    rows.push(new TableRow({ cantSplit: true, children: [tcell([new Paragraph({ children: runs(s.title, { size: H3, bold: true, color: "FFFFFF" }), spacing: { after: 0 } })],
      CONTENT_W, { columnSpan: 3, shading: shade(DARK) })] }));
    const summary = s.blocks.filter(b => !isComment(b));
    if (summary.length) {
      const ctx = { size: CELL, cell: true, width: CONTENT_W - 200 };
      const kids = fieldsOf(summary).flatMap(f => f.label ? labelled(f.label, f.blocks, ctx) : blocks(f.blocks, ctx));
      rows.push(new TableRow({ children: [tcell(kids, CONTENT_W, { columnSpan: 3, shading: shade(LIGHT) })] }));
    }
    for (const r of s.rows) {
      const ctx = { size: CELL, cell: true, width: NOTES_W - 200 };
      const fields = fieldsOf(r.blocks);
      const fill = TYPES[r.type];
      if (!fill) fail(`unknown activity type '${r.type}' in '${r.start} · ${r.min} min · ${r.type} — ${plain(r.title)}'`);
      const notes = [new Paragraph({ children: [
        new TextRun({ text: ` ${r.type.toUpperCase()} `, font: FONT, bold: true, size: LABEL, color: "1A1A1A", shading: shade(fill),
          border: { style: BorderStyle.SINGLE, size: 4, color: MID, space: 0 } }),
        new TextRun({ text: "  ", size: CELL }),
        ...runs(r.title, { size: CELL + 2, bold: true }),
      ], spacing: { after: 100 }, keepNext: true })];
      let assessment = [];
      for (const f of fields) {
        if (f.label === "Assessment") assessment = blocks(f.blocks, { size: CELL, cell: true, width: ASSESS_W - 200 });
        else if (f.label) notes.push(...labelled(f.label, f.blocks, ctx));
        else notes.push(...blocks(f.blocks, ctx));
      }
      if (!assessment.length) assessment = [new Paragraph({ children: [new TextRun({ text: "—", font: FONT, size: CELL })] })];
      rows.push(new TableRow({ children: [
        tcell([new Paragraph({ children: [new TextRun({ text: r.start, font: FONT, bold: true, size: 22, color: BLACK })], spacing: { after: 20 } }),
               new Paragraph({ children: [new TextRun({ text: `${r.min} min`, font: FONT, size: SMALL, color: GREY })], spacing: { after: 0 } })], TIMING_W),
        tcell(notes, NOTES_W),
        tcell(assessment, ASSESS_W),
      ] }));
    }
  }
  return [new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [TIMING_W, NOTES_W, ASSESS_W], borders, rows }),
          new Paragraph({ spacing: { after: 160 } })];
}

function timeline(bs) {
  const pre = [], sections = [];
  let sec = null, row = null;
  for (const b of bs) {
    if (b.t === "Header" && b.c[0] === 3) {
      sec = { title: b.c[2], blocks: [], rows: [] };
      sections.push(sec);
      row = null;
    } else if (b.t === "Header" && b.c[0] === 4) {
      if (!sec) fail(`timeline row before any section: ${plain(b.c[2])}`);
      const m = ROW.exec(plain(b.c[2]).trim());
      if (!m) fail(`timeline row heading must read 'H:MM[:SS] · N min · <type> — <title>': ${plain(b.c[2])}`);
      // the title keeps its formatting: everything after the first " — "
      const inl = b.c[2];
      let cut = inl.findIndex((x, i) => x.t === "Str" && x.c === "—" && i > 0);
      const title = cut >= 0 ? inl.slice(cut + 1).filter((x, i) => !(i === 0 && x.t === "Space")) : [{ t: "Str", c: m[4] }];
      row = { start: m[1], min: m[2], type: m[3], title, blocks: [] };
      sec.rows.push(row);
    } else {
      (row ? row.blocks : sec ? sec.blocks : pre).push(b);
    }
  }
  return [...blocks(pre, { size: BODY }), ...timelineTable(sections)];
}

// ---------- the document ----------
const all = ast.blocks;
const front = [], body = [];
let title = "Lesson plan", crumb = null;
const h2 = (inl, opts = {}) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: runs(inl, { size: H1, bold: true }),
  spacing: { before: 360, after: 160, line: 276 }, keepNext: true, ...opts });
const h3 = inl => new Paragraph({ heading: HeadingLevel.HEADING_2, children: runs(inl, { size: H2, bold: true }),
  spacing: { before: 280, after: 120, line: 276 }, keepNext: true });
const h4 = inl => new Paragraph({ heading: HeadingLevel.HEADING_3, children: runs(inl, { size: H3, bold: true }),
  spacing: { before: 200, after: 80, line: 276 }, keepNext: true });

let i = 0, afterTimeline = false;
while (i < all.length) {
  const b = all[i];
  if (b.t === "Header" && b.c[0] === 1) { title = plain(b.c[2]); i++; continue; }
  if ((b.t === "Para" || b.t === "Plain") && b.c.some(x => x.t === "Span" && x.c[0][1].includes("breadcrumb"))) {
    crumb = plain(b.c); i++; continue;
  }
  if (b.t === "Header" && b.c[0] === 2) {
    const name = plain(b.c[2]).trim();
    if (name === "Timeline") {
      body.push(h2(b.c[2], { pageBreakBefore: true }));
      const tl = [];
      i++;
      while (i < all.length && !(all[i].t === "Header" && all[i].c[0] <= 2)) tl.push(all[i++]);
      body.push(...timeline(tl));
      afterTimeline = true;
      continue;
    }
    body.push(h2(b.c[2], afterTimeline ? { pageBreakBefore: true } : {}));
    afterTimeline = false;
    i++;
    continue;
  }
  if (b.t === "Header" && b.c[0] === 3) { body.push(h3(b.c[2])); i++; continue; }
  if (b.t === "Header" && b.c[0] >= 4) { body.push(h4(b.c[2])); i++; continue; }
  body.push(...blocks([b], { size: BODY }));
  i++;
}

if (fs.existsSync(LOGO)) {
  const png = fs.readFileSync(LOGO);
  const w = png.readUInt32BE(16), h = png.readUInt32BE(20);
  front.push(new Paragraph({ children: [new ImageRun({ type: "png", data: png, transformation: { width: 110, height: Math.round(110 * h / w) } })], spacing: { after: 360 } }));
}
if (crumb) front.push(new Paragraph({ children: [new TextRun({ text: crumb, font: FONT, size: SMALL + 2, color: GREY })], spacing: { after: 120 } }));
front.push(new Paragraph({ children: [new TextRun({ text: title, font: FONT, bold: true, size: TITLE, color: BLACK })], spacing: { after: 200, line: 300 } }));
front.push(new Paragraph({ spacing: { after: 360 }, border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: YELLOW, space: 1 } } }));

const session = ((crumb || "").match(/(?:Day|Session) (\d+)/) || path.basename(MD).match(/^day(\d+)_/) || [null, "?"])[1];
const NONE = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: NONE, bottom: NONE, left: NONE, right: NONE, insideHorizontal: NONE, insideVertical: NONE };
function twoCell(left, right) {
  const half = Math.round(CONTENT_W / 2);
  const cell = (r, align) => new TableCell({ width: { size: half, type: WidthType.DXA }, margins: { top: 0, bottom: 0, left: 0, right: 0 },
    children: [new Paragraph({ alignment: align, children: r, spacing: { after: 0 } })] });
  return new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [half, CONTENT_W - half], borders: noBorders,
    rows: [new TableRow({ children: [cell(left, AlignmentType.LEFT), cell(right, AlignmentType.RIGHT)] })] });
}
const small = t => new TextRun({ text: t, font: FONT, size: SMALL, color: DARK });
const bullets = ["•", "–", "·"].map((text, level) => ({ level, format: LevelFormat.BULLET, text, alignment: AlignmentType.LEFT,
  style: { paragraph: { indent: { left: 360 * (level + 1) + 180, hanging: 260 } } } }));
const numbers = ["%1.", "%2.", "%3."].map((text, level) => ({ level, format: [LevelFormat.DECIMAL, LevelFormat.LOWER_LETTER, LevelFormat.LOWER_ROMAN][level], text,
  alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360 * (level + 1) + 180, hanging: 300 } } } }));

const embedded = [["Work Sans", "WorkSans/WorkSans-Regular.ttf"], ["Fira Code", "FiraCode/FiraCode-Regular.ttf"]]
  .filter(([, f]) => fs.existsSync(path.join(FONTS, f)))
  .map(([name, f]) => ({ name, data: fs.readFileSync(path.join(FONTS, f)) }));
const doc = new Document({
  fonts: embedded,
  creator: "Decoded", title: `${title}: ${KIND}`, description: `${PROGRAMME} ${KIND} for instructors`,
  styles: {
    default: { document: { run: { font: FONT, size: BODY, color: BLACK }, paragraph: { spacing: { line: LINE, after: 120 } } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, bold: true, size: H1, color: BLACK, bold: false }, paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, bold: true, size: H2, color: BLACK, bold: false }, paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, bold: true, size: H3, color: BLACK, bold: false }, paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [{ reference: "bullets", levels: bullets }, { reference: "numbers", levels: numbers }] },
  sections: [{
    properties: { page: { size: { width: A4_SHORT, height: A4_LONG, orientation: PORTRAIT ? PageOrientation.PORTRAIT : PageOrientation.LANDSCAPE }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } },
    headers: { default: new Header({ children: [twoCell([small(`${PROGRAMME} · Day ${session} ${KIND}`)], [small("For instructors")])] }) },
    footers: { default: new Footer({ children: [twoCell(
      [new TextRun({ children: ["Page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES], font: FONT, size: SMALL, color: DARK })],
      [small(`© ${new Date().getFullYear()} Decoded Limited · decoded.com`)])] }) },
    children: [...front, ...body],
  }],
});
// Word uses the embedded faces when settings say so; where a reader ignores them (Google Docs, Pages), the family
// and alternative name steer it to a sans-serif and a monospace font rather than a serif.
async function finish(buf) {
  const JSZip = require("jszip");
  const zip = await JSZip.loadAsync(buf);
  let settings = await zip.file("word/settings.xml").async("string");
  if (!settings.includes("w:embedTrueTypeFonts")) {
    settings = settings.replace("<w:displayBackgroundShape/>", "<w:displayBackgroundShape/><w:embedTrueTypeFonts/>");
  }
  zip.file("word/settings.xml", settings);
  let fonts = await zip.file("word/fontTable.xml").async("string");
  fonts = fonts
    .replace('<w:font w:name="Work Sans"><w:family w:val="auto"/>', '<w:font w:name="Work Sans"><w:altName w:val="Arial"/><w:family w:val="swiss"/>')
    .replace('<w:font w:name="Fira Code"><w:family w:val="auto"/>', '<w:font w:name="Fira Code"><w:altName w:val="Courier New"/><w:family w:val="modern"/>');
  zip.file("word/fontTable.xml", fonts);
  return zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
}
Packer.toBuffer(doc).then(finish).then(buf => { fs.writeFileSync(OUT, buf); console.log(`written ${OUT} (${buf.length} bytes)`); });
