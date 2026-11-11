#!/usr/bin/env python
"""Smoke-run an anchor notebook's code cells outside Jupyter, skipping the long demos.

Each code cell runs from its day folder: Python lines are exec'd in one shared namespace,
`!` lines run through the shell, `%` magics are ignored, except `%cd`, which changes folder, and `%%writefile`, which writes its file (full runs only). Cells that start a long demo
(run.sh, demo.sh, build.sh, docker, Spark, dbt builds, claude, npx) are skipped.
Usage: smoke.py [--full] day1 day2 ... | all   (--full runs the demos too; needs Docker Desktop and, for Day 4, the Airflow stack started)
"""
import os, re, subprocess, sys, traceback
from pathlib import Path
import nbformat

ROOT = Path(__file__).resolve().parents[3]
SLUGS = {1: "day1-design", 2: "day2-platform", 3: "day3-dbt", 4: "day4-airflow", 5: "day5-capstone"}
SKIP_QUICK = re.compile(r"%%writefile|reset\.sh|run\.sh|demo\.sh|build\.sh|docker |curl |spark-engine|delta-under-the-hood|\bdbt (build|run|seed|test|snapshot|source|deps|docs|compile)\b|\bclaude\b|npx|quick_diagram\(|\bastro |mmdc")
SKIP_FULL = re.compile(r"\bclaude\b|npx|quick_diagram\(|mmdc|docs serve|--hold")
SKIP = SKIP_QUICK

def skip(src: str) -> bool:
    if src.lstrip().startswith("# Setup"):      # the setup cell defines sql() and PATH; never skip it
        return False
    return bool(SKIP.search(src))

def shell(cmd, cwd):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=900, env=os.environ)
    return r.returncode, (r.stdout + r.stderr)

def run_cell(src, ns, cwd):
    """Returns (ok, output)."""
    py, out = [], []
    if src.startswith("%%writefile "):          # the cell is a file: write it, as Jupyter would
        first, _, body = src.partition("\n")
        target = Path(os.getcwd()) / first.split(None, 1)[1].strip()
        if not target.parent.is_dir():           # Jupyter's %%writefile does not create folders either
            return False, f"%%writefile: no such folder {target.parent}"
        target.write_text(body + "\n")
        return True, f"wrote {target}"
    def flush():
        if py:
            exec(compile("\n".join(py), "<cell>", "exec"), ns)
            py.clear()
    for line in src.splitlines():
        s = line.lstrip()
        if s.startswith("!"):
            flush()
            rc, o = shell(s[1:], os.getcwd())
            out.append(o[-600:])
            if rc != 0 and "on purpose" not in s:      # a demo step that is meant to fail says so
                return False, f"shell rc={rc}: {s[1:80]}\n" + o[-800:]
        elif s.startswith("%cd "):                      # the notebook sets its working folder once per part
            flush()
            os.chdir(s[4:].strip().format(**{k: v for k, v in ns.items() if isinstance(v, (str, Path))}))
        elif s.startswith("%"):
            continue
        else:
            py.append(line)
    flush()
    return True, "\n".join(out)

def main(days):
    total_fail = 0
    for d in days:
        folder = ROOT / "courseware" / SLUGS[d]
        nb = nbformat.read(folder / f"day{d}_anchor.ipynb", as_version=4)
        os.chdir(folder)
        ns = {"__name__": "__main__"}
        ran = skipped = failed = 0
        import io, contextlib
        for i, cell in enumerate(nb.cells):
            if cell.cell_type != "code":
                continue
            src = cell.source
            if skip(src):
                skipped += 1
                continue
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    ok, out = run_cell(src, ns, folder)
            except Exception:
                ok, out = False, traceback.format_exc().strip().splitlines()[-1][:400]
            if ok:
                ran += 1
            else:
                failed += 1
                print(f"\n[day {d}] cell {i} FAILED\n  {src.splitlines()[0][:110]}\n  {out.strip()[-700:]}")
        print(f"day {d}: ran {ran}, skipped {skipped}, failed {failed}")
        total_fail += failed
    return total_fail

if __name__ == "__main__":
    args = sys.argv[1:] or ["all"]
    if "--full" in args:
        SKIP = SKIP_FULL; args.remove("--full")
    days = [1, 2, 3, 4, 5] if "all" in args else [int(a.replace("day", "")) for a in args]
    sys.exit(1 if main(days) else 0)
