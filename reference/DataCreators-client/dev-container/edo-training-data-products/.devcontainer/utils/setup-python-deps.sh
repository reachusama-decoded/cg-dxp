#!/bin/sh

set -eu

UV_INDEX_ARGS="--index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/ --extra-index-url https://cgrepo.capgroup.com/repository/cgpypi/simple/"

uv pip install --system --quiet $UV_INDEX_ARGS -r .devcontainer/requirements.txt

for py in .venv/bin/python /opt/venv/bin/python; do
if [ -f .devcontainer/sitecustomize.py ] && [ -x "$py" ]; then
  "$py" - <<'PY'
import os
import shutil
import site

src = ".devcontainer/sitecustomize.py"
for d in site.getsitepackages():
    if os.path.isdir(d):
        shutil.copy(src, os.path.join(d, "sitecustomize.py"))
PY
fi

if [ -f /cacert.pem ] && [ -x "$py" ]; then
  "$py" - <<'PY'
import shutil

try:
    import certifi
except Exception:
    certifi = None

if certifi:
    shutil.copy("/cacert.pem", certifi.where())
PY
fi
done
