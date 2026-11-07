# dbt deps SSL / CA Cert Error — Full Fix

## Symptoms to grep for

```
ssl.SSLCertVerificationError
CERTIFICATE_VERIFY_FAILED
dbt deps failed
requests.exceptions.SSLError
```

## Root cause

The CG corporate network intercepts TLS connections through a transparent proxy
that presents its own CA certificate. Python's `requests` library (which dbt
deps uses) does not trust this CA by default.

## Diagnostic steps

1. In the failing task log, look for `ssl.SSLCertVerificationError` or
   `CERTIFICATE_VERIFY_FAILED`.
2. In `dbt_wrapper.py`, grep for `REQUESTS_CA_BUNDLE`:
   ```bash
   grep -n "REQUESTS_CA_BUNDLE" dbt_wrapper.py
   ```
3. If missing, the wrapper is not setting the CA bundle path.

## Fix

In `dbt_wrapper.py`, before invoking any dbt command, set:

```python
import os

# Point requests (and dbt deps) at the CG corporate CA bundle.
# The bundle is pre-installed on Databricks clusters provisioned via
# the CG cluster policy.
os.environ.setdefault(
    "REQUESTS_CA_BUNDLE",
    "/etc/ssl/certs/ca-certificates.crt",  # adjust path per cluster image
)
```

Also verify the CA bundle file is present on the cluster:

```bash
ls -la /etc/ssl/certs/ca-certificates.crt
```

If it is absent, the cluster policy or init script must be updated to
install the CG CA bundle. Raise with the platform team.

See `/write-dbt-wrapper` for the canonical location of this env-var
injection in the wrapper's bootstrap block.
