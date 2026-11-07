# CG teaching data: a frozen snapshot

The real-data files preserve values captured from public CG sources. A product ID identifies an ETF, mutual-fund class or SMA strategy within this snapshot. It is not a universal identifier for every fund worldwide. `source_area` records which part of the archive supplied a row.

CSV blanks mean unknown or absent values, not zero. Percentage fields use percentage points: a stored `0.39` means `0.39%`, or 39 basis points.

## Files and their purpose

| File | Contents and how to use them |
|---|---|
| `cg_products.csv` | Product records from catalogue and detail sources, plus extracted SMA strategy records (`web_extraction`). The same product can appear in several source layers. Apply the selection required by your contract. |
| `cg_fees.csv` | Fee observations with source layers and component labels. Select the required component. Gross and net expense ratios are alternative measures; do not add them together. |
| `cg_returns.csv` | Return observations with calculation basis, frequency and one-, three-, five- or ten-year periods. Benchmark series are excluded. Keep those contexts when selecting or comparing values. |
| `cg_source_receipts.csv` | Source URLs, capture times and file hashes. A hash identifies captured bytes; the URL identifies where they came from. |
| `DISCLOSURES.md` | Selected first-party explanations of costs and performance. Read it as documentation; you do not need to build another model from it. |
| `training_events.json` | Synthetic statements and corrections for the advanced history exercise. `training_fee_bps` is a training measure, not actual CG fee history. A real product ID connects the exercise to the catalogue. |
| `cg_training_enquiries.csv` | Synthetic historical questions specifying a business date and knowledge cutoff. Use both to query the training history. |
| `cg_smoke.csv` | Synthetic input for the environment check. It contains no assessed product logic. |
| `manifest.json` | Input file sizes and hashes used to check that the teaching inputs have not changed. |

## Classroom use

Use this snapshot for the course exercises and follow your instructor’s instructions for access and sharing. Keep the source records unchanged; use a separate labeled copy for controlled faults or synthetic practice. The SMA source is intended for registered investment advisers, and source availability alone does not establish unrestricted reuse.
