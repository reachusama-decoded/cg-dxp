#!/usr/bin/env bash
# 03 — airflow orchestration.
#
# The trainee authors the wiring of the Cosmos DAG
# (data_products/portfolio_analytics/dags/portfolio_analytics_daily.py):
#   start -> source_freshness_check -> dbt_pipeline -> publish_to_catalog -> end
#
# A full Airflow DagBag load would render the Cosmos dbt graph (`dbt ls`), which
# only completes inside the fully-configured astro runtime (real OAuth
# connection + refresher). For a fast, offline self-check we instead statically
# verify the DAG file parses and wires the required task chain. Run the pipeline
# for real in astro via the guide's `astro dev start` / trigger steps.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DAG_FILE="${PORTFOLIO_ANALYTICS_DAG:-$REPO_ROOT/data_products/portfolio_analytics/dags/portfolio_analytics_daily.py}"

if [ ! -f "$DAG_FILE" ]; then
  echo "[FAIL] DAG file not found: $DAG_FILE" >&2
  exit 1
fi

if [ -x "/opt/venv/bin/python" ]; then
  PY="/opt/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
else
  PY="$(command -v python)"
fi

"$PY" - "$DAG_FILE" <<'PY'
import ast
import sys

path = sys.argv[1]
src = open(path, encoding="utf-8").read()

try:
    tree = ast.parse(src)
except SyntaxError as exc:
    print(f"[FAIL] DAG does not parse (fix the Python syntax first): {exc}")
    sys.exit(1)

edges = set()


def name(node):
    return node.id if isinstance(node, ast.Name) else None


def flatten(node):
    # a >> b >> c parses left-associatively as (((a>>b)>>c)); flatten to operands.
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.RShift):
        return flatten(node.left) + [node.right]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.LShift):
        return flatten(node.left) + [node.right]
    return [node]


class Wiring(ast.NodeVisitor):
    def visit_BinOp(self, node):
        if isinstance(node.op, (ast.RShift, ast.LShift)):
            seq = flatten(node)
            names = [name(n) for n in seq]
            if all(names):
                pairs = list(zip(names, names[1:]))
                if isinstance(node.op, ast.LShift):
                    pairs = [(d, u) for u, d in pairs]
                edges.update(pairs)
        self.generic_visit(node)

    def visit_Call(self, node):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr in ("set_downstream", "set_upstream"):
            anchor = name(func.value)
            for arg in node.args:
                other = name(arg)
                if anchor and other:
                    edges.add((anchor, other) if func.attr == "set_downstream" else (other, anchor))
        if isinstance(func, ast.Name) and func.id == "chain":
            names = [name(a) for a in node.args]
            if all(names):
                edges.update(zip(names, names[1:]))
        self.generic_visit(node)


Wiring().visit(tree)

expected = [
    ("start", "source_freshness_check"),
    ("source_freshness_check", "dbt_pipeline"),
    ("dbt_pipeline", "publish_to_catalog"),
    ("publish_to_catalog", "end"),
]
missing = [e for e in expected if e not in edges]
if missing:
    print("[FAIL] The DAG is not wired correctly. Missing dependencies:")
    for upstream, downstream in missing:
        print(f"        {upstream} >> {downstream}")
    print("Wire: start >> source_freshness_check >> dbt_pipeline >> publish_to_catalog >> end")
    sys.exit(1)

print("[pass] DAG parses and wires: start -> source_freshness_check -> dbt_pipeline -> publish_to_catalog -> end")
PY
