#!/usr/bin/env bash
# Overlay the latest template scaffolding (Astro/IAC) onto an existing vended
# deployment repository. Source-of-truth for comparisons is the template repo
# on GitHub — by default the `main` branch of
#   https://github.com/cg-open-itg/template-copier-astro-infra-bundle
# cloned/fetched on demand into a local cache. Override with --template-ref
# (branch/tag/SHA), --template-repo (git URL), or --template-root (local path
# — skips the fetch entirely).
#
# The target's Airflow major version is detected from its Dockerfile so we
# pick templates/astro-2.x vs templates/astro-3.x.
#
# The script relies on git for safety: by default, divergent files are
# overwritten in the target working tree so `git diff` shows exactly what
# changed and `git checkout -- <file>` reverts. Opt in to `--strategy preserve`
# if you need the old `<file>.template-new` sibling behavior.
set -euo pipefail

DEFAULT_TEMPLATE_REPO="https://github.com/cg-open-itg/template-copier-astro-infra-bundle.git"
DEFAULT_TEMPLATE_REF="main"
DEFAULT_TEMPLATE_CACHE="${CATALYST_CACHE_DIR:-$HOME/.cache/catalyst}/astronomer-update-base-deployment"

usage() {
  cat <<EOF
Usage:
  ./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh \\
    [--target <path>] \\
    [--template-repo <url>] [--template-ref <ref>] [--template-cache <path>] \\
    [--template-root <path>] \\
    [--dry-run | --apply] \\
    [--to-version 2|3] \\
    [--strategy overwrite|merge|preserve|skip] \\
    [--baseline-ref <git-ref>] \\
    [--backup] [--yes]

Examples:
  # Preview the plan for the current directory against the tip of main
  # (default: overwrite divergent files).
  ./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh

  # Apply against a specific vended repo, comparing to main:
  ./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh \\
    --target ../my-vended-repo --apply

  # Pin to a release tag / SHA:
  ./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh \\
    --target ../my-vended-repo --template-ref v1.4.0 --apply

  # 3-way merge divergent files against a git ref that represents the previously
  # vended template baseline (e.g. the tag of the last successful vend).
  ./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh \\
    --target ../my-vended-repo --apply --strategy merge --baseline-ref last-vend

  # Old safe behavior: keep target files intact and drop <file>.template-new
  # siblings for manual review.
  ./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh \\
    --target ../my-vended-repo --apply --strategy preserve

  # Offline / local checkout (skip the git fetch):
  ./skills/astronomer-update-base-deployment/scripts/upgrade_deployment.sh \\
    --target ../my-vended-repo \\
    --template-root ../template-copier-astro-infra-bundle

Options:
  --target <path>          Path to the vended deployment repo. Default: current dir.
  --template-repo <url>    Git URL of the template repo.
                           Default: ${DEFAULT_TEMPLATE_REPO}
  --template-ref <ref>     Branch, tag, or SHA in the template repo.
                           Default: ${DEFAULT_TEMPLATE_REF}
  --template-cache <path>  Where to cache the shallow clone.
                           Default: \${CATALYST_CACHE_DIR:-\$HOME/.cache/catalyst}/astronomer-update-base-deployment
  --template-root <path>   Local checkout to use directly. When set, skips the
                           git fetch. Must contain templates/astro-2.x/ and
                           templates/astro-3.x/.
  --dry-run                Print the plan; do not modify the target. Default.
  --apply                  Actually write changes into the target.
  --to-version 2|3         Override auto-detection (e.g. to migrate 2 -> 3).
  --strategy STRATEGY      How to handle files that already exist and differ
                           from the template (default: overwrite):
                             overwrite replace target with template. Rely on
                                       git for review (\`git diff\`) and rollback
                                       (\`git checkout -- <file>\`).
                             merge     try \`git merge-file\` using --baseline-ref
                                       (or an auto-detected common ancestor).
                                       On conflict: keep target, drop
                                       .template-new alongside.
                             preserve  keep target, write <file>.template-new
                                       alongside for manual review. Use when
                                       the target is not a git working tree.
                             skip      leave target alone; do not write .template-new.
  --baseline-ref <ref>     Git ref inside the target repo whose content is the
                           common ancestor for \`--strategy merge\`. If omitted,
                           the merge tries to auto-detect (per-file: the commit
                           that first added the file).
  --backup                 With \`--apply --strategy overwrite\`, keep a
                           <file>.bak next to each overwritten file. Usually
                           unnecessary if the target is a git working tree.
  --yes                    Skip the interactive confirmation before --apply.
  -h, --help               Show this help.

Classification (dry-run + apply both use it):
  - MISSING    : file exists in template but not in target -> always added.
  - IDENTICAL  : file exists in both, byte-identical       -> no-op (safe).
  - DIVERGENT  : file exists in both and differs           -> follows --strategy.
  - PARAM      : \`.copier\` stencil                         -> skipped (needs vars).
  - USER-OWNED : path is user-owned (see below)            -> skipped.

Template scaffolding covered:
  - Root: Dockerfile, docker-compose.override.yml, justfile, packages.txt,
    requirements.txt, requirements-venv-cosmos.txt, pyproject.toml,
    pre-commit-config.yaml, .dockerignore, .gitignore, README.md, VERSION
  - astro-2.x-only extras: README.test.md
  - astro-3.x-only extras: os-packages.txt, requirements-pypi.txt
  - iac/*.tf, iac/lambda/**, iac/.gitignore, iac/README.md
    (astro-3.x also ships iam.tf, locals.tf, lookup.tf)
  - data_products/utils/autosys_scrape_calendar.dag.py
  - plugins/README.md
  - tests/data_products/**

Never touched (user-owned):
  - data_products/* except utils/  (user data products)
  - .astro/                        (deployment metadata; contains parameterized
                                    config.yaml.copier that needs copier vars)
  - iac/config/deployment/{dev1,sqa1,prd1,__ENV__}/  (rendered per-env configs)
  - .env, .env.copier              (deployment-scoped secrets/paths)
  - .copier-answers.yml, .git/     (state)
  - Anything not shipped by the selected template
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

TARGET=""
TEMPLATE_REPO="$DEFAULT_TEMPLATE_REPO"
TEMPLATE_REF="$DEFAULT_TEMPLATE_REF"
TEMPLATE_CACHE="$DEFAULT_TEMPLATE_CACHE"
TEMPLATE_ROOT=""
MODE="dry-run"
TO_VERSION=""
STRATEGY="overwrite"
BASELINE_REF=""
BACKUP=false
ASSUME_YES=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)         TARGET="$2"; shift 2 ;;
    --template-repo)  TEMPLATE_REPO="$2"; shift 2 ;;
    --template-ref)   TEMPLATE_REF="$2"; shift 2 ;;
    --template-cache) TEMPLATE_CACHE="$2"; shift 2 ;;
    --template-root)  TEMPLATE_ROOT="$2"; shift 2 ;;
    --dry-run)        MODE="dry-run"; shift ;;
    --apply)          MODE="apply"; shift ;;
    --to-version)     TO_VERSION="$2"; shift 2 ;;
    --strategy)       STRATEGY="$2"; shift 2 ;;
    --baseline-ref)   BASELINE_REF="$2"; shift 2 ;;
    --backup)         BACKUP=true; shift ;;
    --yes|-y)         ASSUME_YES=true; shift ;;
    -h|--help)        usage; exit 0 ;;
    *)                echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

case "$STRATEGY" in
  preserve|overwrite|merge|skip) ;;
  *) echo "ERROR: --strategy must be one of preserve|overwrite|merge|skip, got '$STRATEGY'" >&2; exit 1 ;;
esac

# --- Resolve template root: local override, or clone/fetch from GitHub -----
TEMPLATE_SOURCE_LABEL=""
TEMPLATE_COMMIT_SHA=""

if [[ -n "$TEMPLATE_ROOT" ]]; then
  TEMPLATE_ROOT="$(cd "$TEMPLATE_ROOT" && pwd)"
  TEMPLATE_SOURCE_LABEL="local: $TEMPLATE_ROOT"
  if command -v git >/dev/null 2>&1 && git -C "$TEMPLATE_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    TEMPLATE_COMMIT_SHA="$(git -C "$TEMPLATE_ROOT" rev-parse HEAD 2>/dev/null || true)"
  fi
else
  if ! command -v git >/dev/null 2>&1; then
    echo "ERROR: git is required to fetch the template from '$TEMPLATE_REPO'." >&2
    echo "       Install git, or pass --template-root <path> to a local checkout." >&2
    exit 1
  fi

  if [[ ! -d "$TEMPLATE_CACHE/.git" ]]; then
    if [[ -e "$TEMPLATE_CACHE" ]]; then
      if [[ ! -d "$TEMPLATE_CACHE" ]] ||
         find "$TEMPLATE_CACHE" -mindepth 1 -maxdepth 1 -print -quit | grep -q .; then
        echo "ERROR: template cache '$TEMPLATE_CACHE' exists and is not an empty git cache." >&2
        echo "       Refusing to remove caller-supplied contents; choose another --template-cache." >&2
        exit 1
      fi
    fi

    # Clone into a sibling so a failed attempt can never remove the requested
    # cache path or unrelated contents already stored there.
    mkdir -p "$(dirname "$TEMPLATE_CACHE")"
    clone_tmp="$(mktemp -d "${TEMPLATE_CACHE}.tmp.XXXXXX")"
    rmdir "$clone_tmp"
    if ! git clone --depth 1 --branch "$TEMPLATE_REF" \
           "$TEMPLATE_REPO" "$clone_tmp" >/dev/null 2>&1; then
      # Fallback: some refs (SHAs, non-branch refs) cannot be cloned with
      # --branch; do a full-ish clone then check out the ref.
      rm -rf "$clone_tmp"
      git clone "$TEMPLATE_REPO" "$clone_tmp" >/dev/null
      git -C "$clone_tmp" checkout "$TEMPLATE_REF" >/dev/null
    fi
    if [[ -e "$TEMPLATE_CACHE" ]]; then
      rmdir "$TEMPLATE_CACHE"
    fi
    mv "$clone_tmp" "$TEMPLATE_CACHE"
  else
    # Existing cache: verify origin matches, then fetch + checkout the ref.
    existing_origin="$(git -C "$TEMPLATE_CACHE" remote get-url origin 2>/dev/null || true)"
    if [[ -n "$existing_origin" && "$existing_origin" != "$TEMPLATE_REPO" ]]; then
      echo "ERROR: template cache '$TEMPLATE_CACHE' already points at" >&2
      echo "         $existing_origin" >&2
      echo "       which does not match --template-repo=$TEMPLATE_REPO." >&2
      echo "       Delete the cache directory or pass a different --template-cache." >&2
      exit 1
    fi
    git -C "$TEMPLATE_CACHE" fetch --depth 1 origin "$TEMPLATE_REF" >/dev/null 2>&1 || \
      git -C "$TEMPLATE_CACHE" fetch origin >/dev/null
    # Detach onto the requested ref; supports branches, tags, and SHAs.
    git -C "$TEMPLATE_CACHE" checkout --quiet --detach FETCH_HEAD 2>/dev/null || \
      git -C "$TEMPLATE_CACHE" checkout --quiet --detach "$TEMPLATE_REF"
  fi

  TEMPLATE_ROOT="$TEMPLATE_CACHE"
  TEMPLATE_COMMIT_SHA="$(git -C "$TEMPLATE_ROOT" rev-parse HEAD)"
  TEMPLATE_SOURCE_LABEL="$TEMPLATE_REPO @ $TEMPLATE_REF ($TEMPLATE_COMMIT_SHA)"
fi

if [[ ! -d "$TEMPLATE_ROOT/templates/astro-2.x" || ! -d "$TEMPLATE_ROOT/templates/astro-3.x" ]]; then
  echo "ERROR: resolved template root does not contain templates/astro-2.x and templates/astro-3.x:" >&2
  echo "         $TEMPLATE_ROOT" >&2
  exit 1
fi

if [[ -z "$TARGET" ]]; then
  TARGET="$(pwd)"
fi
TARGET="$(cd "$TARGET" && pwd)"
if [[ ! -d "$TARGET" ]]; then
  echo "ERROR: --target='$TARGET' is not a directory" >&2
  exit 1
fi

if [[ "$TARGET" == "$TEMPLATE_ROOT" ]]; then
  echo "ERROR: --target must be a vended deployment repo, not the template repo itself ($TEMPLATE_ROOT)" >&2
  exit 1
fi

# `git` is required for --strategy merge and for applying overwrite; probe once for a clearer error.
if [[ "$STRATEGY" == "merge" || ( "$MODE" == "apply" && "$STRATEGY" == "overwrite" ) ]]; then
  if ! command -v git >/dev/null 2>&1; then
    echo "ERROR: --strategy $STRATEGY needs git on PATH" >&2; exit 1
  fi
  if ! git -C "$TARGET" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "ERROR: --strategy $STRATEGY needs the target to be a git working tree" >&2; exit 1
  fi
fi

# --- Detect the target's Airflow major version ------------------------------
detect_airflow_major() {
  local target="$1"
  local dockerfile="$target/Dockerfile"

  if [[ -f "$target/requirements-pypi.txt" || -f "$target/os-packages.txt" ]]; then
    echo "3"; return
  fi

  if [[ ! -f "$dockerfile" ]]; then
    return 1
  fi

  local constraints_line
  constraints_line="$(grep -E '^[[:space:]]*ADD[[:space:]]+https://raw\.githubusercontent\.com/apache/airflow/constraints-' "$dockerfile" | head -1 || true)"
  if [[ "$constraints_line" =~ constraints-([23])\.[0-9]+\.[0-9]+ ]]; then
    echo "${BASH_REMATCH[1]}"; return
  fi

  local from_line
  from_line="$(grep -E '^[[:space:]]*FROM[[:space:]]' "$dockerfile" | head -1 || true)"
  if [[ "$from_line" =~ runtime:([0-9]+)([.-][0-9]+)? ]]; then
    local runtime_major="${BASH_REMATCH[1]}"
    if (( runtime_major <= 9 )); then echo "3"; return; fi
    if (( runtime_major >= 10 )); then echo "2"; return; fi
  fi

  return 1
}

DETECTED_VERSION="$(detect_airflow_major "$TARGET" || true)"

if [[ -n "$TO_VERSION" ]]; then
  case "$TO_VERSION" in
    2|3) ;;
    *) echo "ERROR: --to-version must be 2 or 3, got '$TO_VERSION'" >&2; exit 1 ;;
  esac
  SELECTED_VERSION="$TO_VERSION"
else
  if [[ -z "$DETECTED_VERSION" ]]; then
    echo "ERROR: could not detect the target's Airflow major version." >&2
    echo "       Inspect '$TARGET/Dockerfile' and re-run with --to-version 2 or 3." >&2
    exit 1
  fi
  SELECTED_VERSION="$DETECTED_VERSION"
fi

SRC="$TEMPLATE_ROOT/templates/astro-${SELECTED_VERSION}.x"
if [[ ! -d "$SRC" ]]; then
  echo "ERROR: expected template dir does not exist: $SRC" >&2
  exit 1
fi

# --- Classify each template file --------------------------------------------
# Paths (relative to the target) that the user owns; overlay never touches them.
is_user_owned_path() {
  local rel="$1"
  case "$rel" in
    .astro|.astro/*) return 0 ;;
    iac/config/deployment/dev1|iac/config/deployment/dev1/*) return 0 ;;
    iac/config/deployment/sqa1|iac/config/deployment/sqa1/*) return 0 ;;
    iac/config/deployment/prd1|iac/config/deployment/prd1/*) return 0 ;;
    iac/config/deployment/__ENV__|iac/config/deployment/__ENV__/*) return 0 ;;
    data_products/*)
      case "$rel" in
        data_products/utils/*) return 1 ;;
        *) return 0 ;;
      esac ;;
    .env|.copier-answers.yml|.git|.git/*) return 0 ;;
  esac
  return 1
}

relpath() {
  local path="$1" base="$2"
  python3 -c 'import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))' "$path" "$base"
}

validate_target_path() {
  local rel="$1"
  local path="$TARGET"
  local remainder="$rel"
  local component

  while [[ "$remainder" == */* ]]; do
    component="${remainder%%/*}"
    remainder="${remainder#*/}"
    path="$path/$component"
    if [[ -L "$path" || ( -e "$path" && ! -d "$path" ) ]]; then
      echo "ERROR: target path has an unsafe parent component: $path" >&2
      return 1
    fi
  done

  path="$path/$remainder"
  if [[ -L "$path" || ( -e "$path" && ! -f "$path" ) ]]; then
    echo "ERROR: target path is not a regular file: $path" >&2
    return 1
  fi
}

declare -a PLAN_ADD=()          # missing in target -> add unconditionally
declare -a PLAN_IDENTICAL=()    # already match template byte-for-byte
declare -a PLAN_DIVERGENT=()    # exist in target and differ from template
declare -a PLAN_PARAM=()        # .copier stencils
declare -a PLAN_SKIPPED_USER=() # user-owned paths shipped by the template

while IFS= read -r -d '' src_path; do
  rel="$(relpath "$src_path" "$SRC")"
  [[ "$rel" == "." ]] && continue

  if is_user_owned_path "$rel"; then
    PLAN_SKIPPED_USER+=("$rel")
    continue
  fi

  if [[ "$rel" == *.copier ]]; then
    PLAN_PARAM+=("$rel")
    continue
  fi

  validate_target_path "$rel" || exit 1
  target_path="$TARGET/$rel"
  if [[ ! -e "$target_path" ]]; then
    PLAN_ADD+=("$rel")
  elif cmp -s "$src_path" "$target_path"; then
    PLAN_IDENTICAL+=("$rel")
  else
    PLAN_DIVERGENT+=("$rel")
  fi
done < <(find "$SRC" -type f -print0)

# --- Report -----------------------------------------------------------------
printf '=======================================================================\n'
printf 'astronomer-update-base-deployment\n'
printf '=======================================================================\n'
printf 'Template src  : %s\n' "$TEMPLATE_SOURCE_LABEL"
if [[ -n "$TEMPLATE_COMMIT_SHA" ]]; then
  printf 'Template SHA  : %s\n' "$TEMPLATE_COMMIT_SHA"
fi
printf 'Template root : %s\n' "$TEMPLATE_ROOT"
printf 'Target repo   : %s\n' "$TARGET"
printf 'Detected      : Airflow %s\n' "${DETECTED_VERSION:-unknown}"
printf 'Selected      : Airflow %s  (source: %s)\n' "$SELECTED_VERSION" "${SRC#$TEMPLATE_ROOT/}"
printf 'Mode          : %s\n' "$MODE"
printf 'Strategy      : %s (applies to DIVERGENT files)\n' "$STRATEGY"
if [[ "$STRATEGY" == "merge" ]]; then
  printf 'Baseline ref  : %s\n' "${BASELINE_REF:-<auto-detect first-add commit per file>}"
fi
printf 'Backup (.bak) : %s (only used with --strategy overwrite)\n' "$BACKUP"
printf '\n'

if [[ -n "$DETECTED_VERSION" && "$DETECTED_VERSION" != "$SELECTED_VERSION" ]]; then
  printf 'WARNING: cross-version upgrade requested (%s -> %s).\n' "$DETECTED_VERSION" "$SELECTED_VERSION"
  printf '         Review the resulting Dockerfile/requirements diffs carefully.\n'
  printf '         Notable moves between v2 and v3: packages.txt (v2 has real\n'
  printf '         packages; v3 is empty and OS packages live in os-packages.txt),\n'
  printf '         requirements.txt vs requirements-pypi.txt, new iac/{iam,locals,lookup}.tf.\n\n'
fi

# Section headers start with `---`, which macOS bash's `printf` builtin can
# treat as end-of-options. Passing the header as a %s argument sidesteps that.
printf '%s\n' "--- Files to ADD (missing in target) (${#PLAN_ADD[@]}) ---"
if (( ${#PLAN_ADD[@]} )); then
  printf '  %s\n' "${PLAN_ADD[@]}"
fi

printf '%s\n' "" "--- Files IDENTICAL to template (no action) (${#PLAN_IDENTICAL[@]}) ---"
if (( ${#PLAN_IDENTICAL[@]} )); then
  printf '  %s\n' "${PLAN_IDENTICAL[@]}"
fi

case "$STRATEGY" in
  preserve)  divergent_hdr="--- DIVERGENT files (target modified) -> keep target, write <file>.template-new (${#PLAN_DIVERGENT[@]}) ---" ;;
  overwrite) divergent_hdr="--- DIVERGENT files (target modified) -> OVERWRITE with template (${#PLAN_DIVERGENT[@]}) ---" ;;
  merge)     divergent_hdr="--- DIVERGENT files (target modified) -> git merge-file 3-way (${#PLAN_DIVERGENT[@]}) ---" ;;
  skip)      divergent_hdr="--- DIVERGENT files (target modified) -> SKIP entirely (${#PLAN_DIVERGENT[@]}) ---" ;;
esac
printf '%s\n' "" "$divergent_hdr"
if (( ${#PLAN_DIVERGENT[@]} )); then
  printf '  %s\n' "${PLAN_DIVERGENT[@]}"
fi

printf '%s\n' "" "--- Parameterized stencils skipped (${#PLAN_PARAM[@]}) ---" \
  '  (End in .copier and need copier variables to render. Run' \
  '   `copier update --trust` in the target repo, or edit by hand.)'
if (( ${#PLAN_PARAM[@]} )); then
  printf '  %s\n' "${PLAN_PARAM[@]}"
fi

printf '%s\n' "" "--- User-owned paths skipped (${#PLAN_SKIPPED_USER[@]}) ---"
if (( ${#PLAN_SKIPPED_USER[@]} )); then
  printf '  %s\n' "${PLAN_SKIPPED_USER[@]}"
fi
printf '\n'

if [[ -f "$TARGET/.copier-answers.yml" ]]; then
  printf 'NOTE: %s/.copier-answers.yml exists.\n' "$TARGET"
  printf '      For a semantically correct upgrade (including .copier stencils),\n'
  printf '      the preferred command is:\n'
  printf '        cd %s && copier update --trust\n' "$TARGET"
  printf '      Use this script when you want a targeted file-level overlay.\n\n'
fi

if [[ "$MODE" == "dry-run" ]]; then
  printf 'Dry-run complete. Re-run with --apply to write these changes.\n'
  exit 0
fi

# --- Apply ------------------------------------------------------------------
if ! $ASSUME_YES; then
  case "$STRATEGY" in
    overwrite)
      printf 'About to ADD %d file(s), leave %d identical file(s) alone, and\n' \
        "${#PLAN_ADD[@]}" "${#PLAN_IDENTICAL[@]}"
      printf 'overwrite %d divergent (user-modified) file(s) under %s.\n' \
        "${#PLAN_DIVERGENT[@]}" "$TARGET"
      printf 'Review with `git diff`; revert individual files with `git checkout -- <file>`.\n' ;;
    merge)
      printf 'About to ADD %d file(s) and 3-way-merge %d divergent file(s) under %s.\n' \
        "${#PLAN_ADD[@]}" "${#PLAN_DIVERGENT[@]}" "$TARGET"
      printf 'On conflict the target file is left intact and <file>.template-new is written.\n' ;;
    preserve)
      printf 'About to ADD %d file(s), leave %d identical file(s) alone, and\n' \
        "${#PLAN_ADD[@]}" "${#PLAN_IDENTICAL[@]}"
      printf 'write <file>.template-new alongside %d divergent file(s) under %s.\n' \
        "${#PLAN_DIVERGENT[@]}" "$TARGET" ;;
    skip)
      printf 'About to ADD %d file(s) and skip %d divergent file(s) entirely under %s.\n' \
        "${#PLAN_ADD[@]}" "${#PLAN_DIVERGENT[@]}" "$TARGET" ;;
  esac
  read -r -p 'Continue? [y/N]: ' reply
  case "$reply" in
    y|Y|yes|YES) ;;
    *) echo 'Aborted.'; exit 1 ;;
  esac
fi

add_one() {
  local rel="$1"
  local src_path="$SRC/$rel"
  local dst_path="$TARGET/$rel"
  validate_target_path "$rel" || exit 1
  mkdir -p "$(dirname "$dst_path")"
  # `cp -p` preserves mode/mtime; important for executable scripts (justfile).
  cp -p "$src_path" "$dst_path"
}

overwrite_one() {
  local rel="$1"
  local src_path="$SRC/$rel"
  local dst_path="$TARGET/$rel"
  validate_target_path "$rel" || exit 1
  if $BACKUP; then
    validate_target_path "$rel.bak" || exit 1
  fi
  mkdir -p "$(dirname "$dst_path")"
  if $BACKUP && [[ -e "$dst_path" ]]; then
    cp -p "$dst_path" "$dst_path.bak"
  fi
  cp -p "$src_path" "$dst_path"
}

write_template_new() {
  local rel="$1"
  local src_path="$SRC/$rel"
  local dst_path="$TARGET/$rel.template-new"
  validate_target_path "$rel.template-new" || exit 1
  mkdir -p "$(dirname "$dst_path")"
  cp -p "$src_path" "$dst_path"
}

# Try to get the common-ancestor blob for a given file into $1 (out path).
# Returns 0 on success, non-zero if no ancestor could be determined.
get_ancestor_blob() {
  local out_file="$1" rel="$2"
  local ref="$BASELINE_REF"

  if [[ -z "$ref" ]]; then
    # Auto-detect: the first commit that added this file is our best guess at
    # the vended baseline. --diff-filter=A limits to add commits, --follow tracks
    # renames, and `tail -1` picks the OLDEST (chronologically first) add.
    ref="$(git -C "$TARGET" log --follow --diff-filter=A --format=%H -- "$rel" 2>/dev/null | tail -1 || true)"
    [[ -z "$ref" ]] && return 1
  fi

  git -C "$TARGET" show "$ref:$rel" > "$out_file" 2>/dev/null || return 1
  return 0
}

MERGE_CLEAN=0
MERGE_CONFLICT=0
MERGE_NO_ANCESTOR=0

merge_one() {
  local rel="$1"
  local template_new="$SRC/$rel"
  local target_current="$TARGET/$rel"
  local ancestor merged
  validate_target_path "$rel" || exit 1
  ancestor="$(mktemp)"
  merged="$(mktemp)"

  if ! get_ancestor_blob "$ancestor" "$rel"; then
    rm -f "$ancestor" "$merged"
    MERGE_NO_ANCESTOR=$((MERGE_NO_ANCESTOR + 1))
    write_template_new "$rel"
    return
  fi

  # `git merge-file -p` writes merged output to stdout; exit 0 = clean, >0 =
  # conflict markers. We do NOT touch the target file until we know the outcome.
  if git merge-file -p "$target_current" "$ancestor" "$template_new" > "$merged" 2>/dev/null; then
    cat "$merged" > "$target_current"
    MERGE_CLEAN=$((MERGE_CLEAN + 1))
  else
    rm -f "$merged"
    write_template_new "$rel"
    MERGE_CONFLICT=$((MERGE_CONFLICT + 1))
  fi
  rm -f "$ancestor"
}

# --- Do the writes ---------------------------------------------------------
if (( ${#PLAN_ADD[@]} )); then
  for rel in "${PLAN_ADD[@]}"; do add_one "$rel"; done
fi

case "$STRATEGY" in
  preserve)
    if (( ${#PLAN_DIVERGENT[@]} )); then
      for rel in "${PLAN_DIVERGENT[@]}"; do write_template_new "$rel"; done
    fi ;;
  overwrite)
    if (( ${#PLAN_DIVERGENT[@]} )); then
      for rel in "${PLAN_DIVERGENT[@]}"; do overwrite_one "$rel"; done
    fi ;;
  merge)
    if (( ${#PLAN_DIVERGENT[@]} )); then
      for rel in "${PLAN_DIVERGENT[@]}"; do merge_one "$rel"; done
    fi ;;
  skip) ;;
esac

# --- Summary ----------------------------------------------------------------
printf '\nDone.\n'
printf '  Added         : %d\n' "${#PLAN_ADD[@]}"
printf '  Identical     : %d (no action)\n' "${#PLAN_IDENTICAL[@]}"
case "$STRATEGY" in
  preserve)
    printf '  Divergent     : %d (target preserved; .template-new written alongside)\n' \
      "${#PLAN_DIVERGENT[@]}" ;;
  overwrite)
    printf '  Divergent     : %d (overwritten)\n' "${#PLAN_DIVERGENT[@]}"
    if $BACKUP; then printf '                 (.bak siblings saved)\n'; fi ;;
  merge)
    printf '  Divergent     : %d total\n' "${#PLAN_DIVERGENT[@]}"
    printf '    clean-merge : %d\n' "$MERGE_CLEAN"
    printf '    conflict    : %d (target kept; .template-new written)\n' "$MERGE_CONFLICT"
    printf '    no-ancestor : %d (fell back to preserve)\n' "$MERGE_NO_ANCESTOR" ;;
  skip)
    printf '  Divergent     : %d (skipped)\n' "${#PLAN_DIVERGENT[@]}" ;;
esac

if (( ${#PLAN_PARAM[@]} )); then
  printf '  Stencils      : %d (.copier — not applied)\n' "${#PLAN_PARAM[@]}"
fi

printf '\nRecommended follow-ups:\n'
printf '  - cd %s && git status  # review the changes\n' "$TARGET"
if [[ "$STRATEGY" == "overwrite" ]] && (( ${#PLAN_DIVERGENT[@]} )); then
  printf '  - git diff <file>            # inspect incoming template deltas\n'
  printf '  - git checkout -- <file>     # revert any single file to its previous state\n'
fi
if [[ "$STRATEGY" == "preserve" || "$STRATEGY" == "merge" ]] && (( ${#PLAN_DIVERGENT[@]} )); then
  printf '  - find %s -name "*.template-new"  # inspect what the template ships\n' "$TARGET"
  printf '  - diff <file> <file>.template-new  # per-file review; merge by hand or with meld/vimdiff\n'
  printf '  - find %s -name "*.template-new" -delete  # after merging, clean up\n' "$TARGET"
fi
printf '  - astro dev parse       # validate the Airflow project still parses\n'
printf '  - cd iac && terraform validate  # sanity-check TF\n'
