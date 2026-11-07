# Branch Creation Prompt

Create feature branches in target repositories with generated artifacts.

## Dual Repository Setup

Keep **reference repos** pristine (always on main) and use **working repos** for branch creation:

| Purpose | Location | Usage |
|---------|----------|-------|
| Reference | `workspace/reference/repos/` | Pattern extraction, reading code, stays on main |
| Working | `workspace/working/repos/` | Branch creation, commits, pushes |

The script auto-clones working repos if they don't exist.

## Batch Mode

For processing many files (up to 300+), use a **single branch** for all configs:

```bash
# All ingestion configs in one branch
python prepare_branch.py \
  --artifact-dir workspace/generated/source-aligned/file1 \
  --artifact-dir workspace/generated/source-aligned/file2 \
  --artifact-dir workspace/generated/source-aligned/file3 \
  --repo pipelines \
  --process-domain blmbrg \
  --branch feature/blmbrg-batch-2025-01
```

Or use shell glob expansion:
```bash
python prepare_branch.py \
  --artifact-dir workspace/generated/source-aligned/govt_* \
  --repo pipelines \
  --process-domain blmbrg
# Auto-generates: feature/blmbrg-ingestion-20250120-143022
```

Branch names include full timestamp (`YYYYMMDD-HHMMSS`) to allow multiple runs per day.

## System of Record → dc_tag Mapping

The **System of Record** (`process_domain`) identifies the source system. The **dc_tag** determines the folder structure in casper-im-foundation.

| System of Record (`process_domain`) | dc_tag | Notes |
|-------------------------------------|--------|-------|
| `blmbrg` | `blmbrg` | Bloomberg — same for both |
| `rdm` | `ref` | Reference Data Management → reference data |
| `moodys` | `rat` | Moody's → ratings |
| `refinitiv` | `ref` | Refinitiv → reference data |
| `factset` | `fds` | FactSet |
| `msci` | `msci` | MSCI — same for both |
| `rapid` | `raem` | RAPID → RA Equity Models |
| `comet` | `mor` | COMET → Mortgage |

If the system of record is not in this table, ask the user for the appropriate dc_tag.

## Repository Destinations

### casper-pipelines (Ingestion)

**Branch name:** `feature/<process_name>-ingestion`

**Files to copy:**

| Source (generated) | Destination |
|--------------------|-------------|
| `ingestion/<process>.yml` | `dags/ingestion/<process_domain>/<process_name>/<process>.yml` |
| `ingestion/dq.yml` | `dags/ingestion/<process_domain>/<process_name>/<process>.dq.yml` |
| `ingestion/pipeline.py` | `dags/ingestion/<process_domain>/<process_name>/pipeline.py` |

**Example:**
- Process: `govt_agency_regl_asia_moody`
- Domain: `blmbrg`
- Destination: `dags/ingestion/blmbrg/govt_agency_regl_asia_moody/`

### casper-im-foundation (Curation EMR)

**Branch name:** `feature/<table_name>-curation`

**Files to copy:**

| Source (generated) | Destination |
|--------------------|-------------|
| `curation-emr/models/<table>.yml` | `models/<dc_tag>/<table>_f/<table>.yml` |
| `curation-emr/models/staging/*.sql` | `models/<dc_tag>/<table>_f/staging/*.sql` |
| `curation-emr/models/integration/*.sql` | `models/<dc_tag>/<table>_f/integration/*.sql` |
| `curation-emr/models/prepared/*.sql` | `models/<dc_tag>/<table>_f/prepared/*.sql` |
| `curation-emr/source.yml` | Merge into model yml OR keep separate |

**Example:**
- Table: `govt_agency_regl_asia_moody_v4`
- dc_tag: `blmbrg`
- Destination: `models/blmbrg/govt_agency_regl_asia_moody_v4_f/`

### casper-im-foundation (Curation Databricks) — TBD

> **Status:** Placeholder. Databricks curation target structure is not yet finalized.
>
> When ready:
> - Branch name: `feature/<table_name>-curation-dbx`
> - Files: `curation-databricks/models/*.sql`, `curation-databricks/dag.yml`
> - Destination: TBD

## Commit Message Template

```
feat(<domain>): add <process_name> ingestion/curation

- Generated via source-aligned skill
- Source: <original_filename>
- Schedule: <cron_expression or unscheduled>
```

## Workflow Steps

1. **Verify repos exist** at `workspace/reference/repos/`
2. **Create feature branch** from main/master
3. **Copy files** to correct destinations
4. **Commit** with descriptive message
5. **Push** to remote (`origin`)
6. **Output PR instructions** (manual PR creation)

## Safety Checks

Before pushing:
- Confirm branch name with user
- Show files that will be committed
- Verify no uncommitted changes in target repo
- Check remote exists

## Usage

```bash
# Single artifact - ingestion
python plugins/casper/skills/source-aligned/scripts/prepare_branch.py \
  --artifact-dir workspace/generated/source-aligned/govt_agency_regl_asia_moody \
  --repo pipelines \
  --process-domain blmbrg \
  --branch feature/blmbrg-govt-2025-01

# Batch mode - multiple artifacts (shell glob)
python plugins/casper/skills/source-aligned/scripts/prepare_branch.py \
  --artifact-dir workspace/generated/source-aligned/govt_* \
  --repo pipelines \
  --process-domain blmbrg \
  --branch feature/blmbrg-govt-batch-2025-01

# Curation batch
python plugins/casper/skills/source-aligned/scripts/prepare_branch.py \
  --artifact-dir workspace/generated/source-aligned/govt_* \
  --repo im-foundation \
  --dc-tag blmbrg \
  --branch feature/blmbrg-curation-batch-2025-01

# Dry run to preview
python plugins/casper/skills/source-aligned/scripts/prepare_branch.py \
  --artifact-dir workspace/generated/source-aligned/govt_* \
  --repo pipelines \
  --process-domain blmbrg \
  --branch feature/test \
  --dry-run
```
