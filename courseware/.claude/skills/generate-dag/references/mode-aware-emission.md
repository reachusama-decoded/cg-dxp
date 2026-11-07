# Mode-Aware Emission

`/generate-dag` operates in three modes. The mode is set by the caller
(or read from `.catalyst-build.yml#mode` if present in the target repo).

## Mode matrix

| Mode | Schedule | MDS tags | Asset triggers | DQ checks | Validation | Output location |
|---|---|---|---|---|---|---|
| `prototype` | cron OK | optional (emit TODOs for missing) | optional (cron fallback OK) | minimal | lite (no hard refusal) | runtime location (`data_products/.../airflow/`) |
| `production` | Asset-driven required; cron with advisory only | ALL required (refuse if missing) | required (cron requires explicit override) | full | full RFD 0011 | runtime location |
| `lift-and-shift` | preserve existing | warn-and-add (annotate `# ADDED by /generate-dag`) | preserve existing trigger; add Asset trigger as `# TODO: migrate to Asset-driven` comment | preserve + add | full RFD 0011 (warn instead of block on existing deviations) | **`workspace/dag-proposals/`** (NOT runtime) |

## Mode selection

The skill picks the mode from (in order):
1. Explicit `--mode` flag in skill arguments
2. `.catalyst-build.yml#mode` in the target repo
3. Ask the user if still ambiguous

## Prototype mode

When the team is iterating on a new dataset:
- No deployed bundle yet → emit with placeholder job_name (see `compose-with-bundle.md`).
- MDS tags can be partial → emit `# TODO` for missing fields.
- Schedule via cron OK → no advisory required if user explicitly chose schedule.
- DQ checks are minimal — just row count > 0 — but the file is emitted.

Goal: enable quick iteration without forcing the team to gather all DPLC
artifacts upfront.

## Production mode

When the team is ready to deploy:
- Bundle MUST exist; refuse if absent.
- All MDS tags required.
- Asset-driven trigger required (cron requires explicit override with advisory).
- Full DQ checks per data contract.
- Structural pytest emitted to `tests/dags/test_<dataset>_dag.py`.

Goal: production DAGs meet every RFD 0011 directive.

## Lift-and-shift mode

When retrofitting an existing DAG (e.g., the prototype's `instrument_ext_curr.dag.yaml`):
- Read the existing DAG file.
- Map existing fields to RFD 0011 equivalents.
- Emit the proposed DAG to **non-runtime location**:

```
workspace/dag-proposals/data_products/<product>/datasets/<dataset>/airflow/<dataset>.dag-factory.yml
```

- Print a diff-like summary of what changed and what was preserved.
- The user diffs against the original at the runtime location and moves
  files manually when ready. No version/RFD numbers in runtime artifact paths.

See `lift-and-shift.md` for the full flow.

## Promote-mode transition

When transitioning from prototype to production:
1. Re-run `/generate-dag` with `--mode production`.
2. Skill regenerates the DAG file, filling in placeholders with real values
   from the now-deployed bundle.
3. All MDS tags must now be present (user supplies if not in DPLC artifacts).
4. Advisory comments are removed when their underlying issue is resolved.
