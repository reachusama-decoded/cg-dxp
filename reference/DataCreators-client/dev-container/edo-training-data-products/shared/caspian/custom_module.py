from typing import Dict, Any
import os
import dbt.context.base as _dbt_base

def set_context_modules():
    os.environ["ABC"] = "1"
    _dbt_context_modules = _dbt_base.get_context_modules
    def _cspn_context_modules() -> Dict[str, Dict[str, Any]]:
        from caspian.dbt import dbt_extn
        return {"caspian": {"dbt_extn": dbt_extn}, **_dbt_context_modules()}
    _dbt_base.get_context_modules = _cspn_context_modules