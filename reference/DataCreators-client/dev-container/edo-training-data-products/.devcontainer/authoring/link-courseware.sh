#!/usr/bin/env sh
# Authoring only: expose the course (repository root) as challenges/courseware/ through
# per-item links. Linking the root itself would loop back into this directory.
set -eu
client="$(cd "$(dirname "$0")/../.." && pwd)"
dest="$client/challenges/courseware"
# In the authoring container the course is a separate mount; on the host it is four levels up.
if [ -f /workspaces/ts-cg-datacreators/builder.toml ]; then
  course=/workspaces/ts-cg-datacreators; prefix=$course
else
  course="$client/../../../.."; prefix=../../../../../..
fi
if [ ! -f "$course/builder.toml" ]; then
  echo "link-courseware: no course at $course (learner checkout?); nothing to link" >&2
  exit 0
fi
mkdir -p "$dest"
for item in learner facilitator designer scripts build builder.toml build-pdf Makefile mkdocs.yml README.md devc.md CLAUDE.md; do
  [ -e "$course/$item" ] || continue
  ln -sfn "$prefix/$item" "$dest/$item"
done
echo "link-courseware: $dest -> $(cd "$course" && pwd)"
