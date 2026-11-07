# Public PyPI 404 on dbt deps — Full Fix

## Symptoms to grep for

```
Could not find a version that satisfies the requirement
pypi.org
files.pythonhosted.org
ERROR: No matching distribution found
404 Client Error: NOT FOUND for url: https://pypi.org
```

## Root cause

Capital Group's corporate network blocks public package repositories —
including `pypi.org` and `files.pythonhosted.org` — to mitigate supply-chain
attacks. The `dbt deps` command runs `pip install` for hub packages, and if
pip is not redirected to the internal Nexus mirror, it will hit a 404 or
connection timeout against the public host.

The fix is **not** to find a different package. It is to re-point pip at the
internal Nexus proxy.

## Diagnostic steps

1. Grep `dbt_wrapper.py` for `--index-url` or `cgrepo`:
   ```bash
   grep -n "index-url\|cgrepo" dbt_wrapper.py
   ```
2. Grep `requirements.txt` (if used) for the same:
   ```bash
   grep -n "index-url\|cgrepo" requirements.txt
   ```
3. If neither file references `cgrepo-aws.capgroup.com`, pip is pointing at
   public PyPI.

## Fix

In `dbt_wrapper.py`, any `pip install` or `pip install -r` call must include
the `--index-url` flag. (`uv pip install` accepts the same flag; if the team
uses uv, the diagnostic and fix are identical — only the binary name changes.)

```python
import subprocess

subprocess.check_call([
    "pip", "install",
    "--index-url", "https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/",
    "--quiet",
    "-r", "requirements.txt",
])
```

In `requirements.txt`, add the index-url as the first line:

```
--index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/
dbt-databricks==1.8.7
dbt-core==1.8.7
```

See `/write-dbt-wrapper` for the canonical pip invocation pattern used in the
wrapper's deps task.

The internal Nexus pip mirror URL is:
`https://cgrepo-aws.capgroup.com/repository/cgpypi/simple/`
(also reachable as `https://cgrepo.capgroup.com/repository/cgpypi/simple/`).
