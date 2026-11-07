"""
Caspian dbt runtime shim.

dbt Jinja macros expect:
  modules.get('caspian').dbt_extn.<function>(...)

Our implementation in caspian/dbt/dbt_extn.py is a module of functions, so we
expose an object `dbt_extn` that proxies attribute access to that module.
"""

from __future__ import annotations

from caspian.dbt import dbt_extn as _dbt_extn_module
from caspian.dbt import dbt_modules

__all__ = ["dbt_extn", "dbt_modules"]

class _DbtExtensionProxy:
    def __getattr__(self, name: str):
        return getattr(_dbt_extn_module, name)


# This is what dbt macros use: caspian.dbt_extn.<fn>(...)
dbt_extn = _DbtExtensionProxy()
