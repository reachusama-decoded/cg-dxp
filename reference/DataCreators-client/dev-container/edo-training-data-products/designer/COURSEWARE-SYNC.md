# Single-source challenge, course and instructor views

Planning specification, 5 October 2026. The implementation belongs to a future course candidate. The current v4 PDF and promoted release are unchanged by this plan.

## Content authority and the three views

The learner READMEs in `challenges/v2/` are the authority for concepts, explanations, tasks, checks and intentional-defect notices. The manifest controls order, optionality, timing and course destinations. Do not independently rewrite a parallel instructor task list and then rely on memory to synchronize it.

| View | Content | Destination |
|---|---|---|
| Session summary | Tool/phase, minimum or advanced outcome, core/stretch and optional status, task IDs/titles, concept titles, timeline, prerequisites, completion evidence and appendix links. | Inline in the relevant day/session, immediately where practical teaching is introduced. |
| Instructor companion | Tool-root README reused verbatim; ordered concept titles and explanations from the phase READMEs; demonstration prompts/prerequisites referenced by task ID. | Facilitator notes and concept index; selected concept blocks may appear adjacent to inline summary. |
| Complete learner appendix | Full version/root/tool/phase and nested learner README text, including hints, checks, code, tables, expected outcomes and optional stretch. | Main course PDF appendix, plus offline HTML with equivalent content. |

Tool-root README source text is included verbatim, with only presentation-layer heading/anchor/link changes recorded. In the instructor view, concept explanations are extracted in full, not automatically summarized by an agent. The inline view is deliberately shorter and is derived from structured titles/metadata; concise instructor demonstration notes should be authored alongside each concept and tagged as instructor-only so the generator can include them without copying solutions into the learner appendix.

Possible tagged instructor metadata lives in Markdown comments or a clearly specified frontmatter field. Validate its schema, keep the concept/task ID link and never hide learner-required context there. Learner explanations must remain readable in an ordinary Markdown viewer with no generator.

## Deterministic inventory and extraction

Proposed order:

1. Version/root overview and course route.
2. Git root, Phase 1, Phase 2, nested stretch READMEs in explicit manifest order.
3. Docker in the same root/phase/stretch order.
4. dbt in the same order.
5. Databricks CLI root, offered Phase 1, explicit non-offered Phase 2 page.
6. Airflow in the same order.
7. Kafka root, optional Phase 1, explicit non-offered Phase 2 page.
8. Capstone root, Phase 1, Phase 2 core and every stretch README.

Recursively inventory **all learner-facing README.md files under v2**, including those in starters or nested task folders. Each must have a manifest position or be declared a non-learner generated/runtime file with a reason. Do not accidentally omit a README because it is below the phase root. Fail on duplicate, missing or unclassified learner files. Within a phase, starter guidance should follow the phase page before stretch; freeze that order in the manifest.

Parse Markdown structurally rather than truncating on a heading string or using a character/word limit. Resolve headings, fenced code, tables, lists, callouts and referenced local assets. Generate a stable task anchor from the task ID; maintain old published anchors if a title changes. A concept block has an explicit title and ID, an explanation, and an associated task/check. Reject ambiguous boundaries instead of quietly extracting the wrong text.

Produce a source coverage manifest containing each README path/hash, inventory position, extracted task/concept IDs, full appendix destination and inline/instructor destinations. Hash the manifest and generator version with the candidate. Include concise source/version provenance in the printed appendix so a reviewer knows which challenge pack it describes.

## Print, links and code

Resolve relative links against the original README directory before relocation. Internal README links become PDF/HTML anchors; asset links point to packaged copies; reference solution links remain instructor-pack pointers without embedding the solution. Record the solution pointer's deliberate omission from learner content. External links retain meaningful titles and an understandable printed description. Do not silently replace a broken link with its label.

Embed referenced learner images at readable size with captions/alt text. Ship code/starter assets in the companion pack and include enough explanation/code in the appendix to make the printed learner notes understandable. The requirement is complete README text, not necessarily a printout of every source file; if a README's essential check depends on an external file, include a labelled excerpt or rendered asset description and inventory the packaged file. Preserve code indentation and commands; handle wide tables/code deliberately so nothing is clipped.

Generate appropriate page breaks, appendix navigation and task cross-references without adding filler. Render intentional starter failures and core/stretch distinction consistently. Inactive Phase 2 pages stay explicit in the complete appendix but are excluded from active task/time totals. Instructor-only comments and solution bodies never enter the learner appendix.

## Drift and coverage checks

| Check | Acceptance condition |
|---|---|
| Inventory | Every learner README included exactly once in full appendix order, with a matching source hash. |
| Root reuse | Tool-root text is preserved without semantic edits; presentation transformations are recorded. |
| Task/concept parity | Manifest, phase headings, tool tables, inline summaries and instructor concept index contain the same IDs/status. |
| Complete text | Parsed text/code blocks are retained; compare normalized block coverage, not just keywords or page counts. |
| Links/assets | Internal targets resolve; assets exist/package correctly; any external-only dependency is declared. |
| Solutions | No solution text/assets leak into the learner extraction; instructor links still resolve in its pack. |
| Regeneration | A concept/title/timing/check edit triggers regeneration of all affected views; stale output fails the build check. |
| Render review | Review dense appendix pages, code/table wrapping, task navigation and optionality in PDF and offline HTML. |

Provide a deterministic generation command and a non-mutating check mode that reports stale outputs. Version generated files as derived content only where current packaging expects committed sources; always retain their provenance manifest. One source edit should update session summary, concept notes and appendix in one build, without manual editing of three documents.

## Fit with the existing course

Current v4 includes lengthy client guides in teaching sessions and has adapters with edition-specific scope changes, including removing the original Airflow operations phase from its learner route. A future v2 challenge integration must use the new manifest and include requested active advanced content; carrying forward a heading-based truncation would recreate the regression concern.

Reduce duplicated challenge instructions inline by providing the new short summaries, while retaining the full tool-root table and complete learner text in the appendix. Preserve the substantive course teaching that explains those tools; do not treat moving a challenge guide as permission to remove surrounding exposition. Maintain a source-retention ledger against the accepted v4/v2 restoration baseline and the FiveDay reference where relevant.

Retain the existing 100,000 substantive learner-word and 237 readable-page floors for a future main-book candidate, along with the richer content/visual/reference gates. The current release's actual totals are historical evidence; no new totals are claimed here. Additions should increase usable coverage, not replace detailed chapters with a handful of challenge titles. Course scheduling must separately account for new Git/CLI instruction and optional Kafka/Phase 2 clinics; preserve protected teaching time or flag a timetable finding.

Future outputs: learner appendix, inline session fragments, facilitator concept index, challenge source/coverage manifest, packaged learner starter assets, separately packaged instructor solutions and a sync/readability review. Building or promoting these outputs is outside the present planning-only delivery.


## 8 October 2026 supersession — structure and container alignment

The new plan replaces the full-Appendix-H delivery with named project chapters, owned phases/tasks and reference destinations. The manifest remains source authority; course adapters label small dbt/Airflow fixtures as optional and bind the assigned Portfolio Analytics guide/runtime contract. Every recursive README retains a coverage disposition. Inactive phases stay in route/source records and delivered READMEs rather than competing project chapters. Generator freshness, normalized full-block parity, separate instructor solutions and the 100,000-word/237-page floors remain required. Historical editions and evidence are unchanged. Connected execution and human acceptance remain pending; no promotion is authorized.
