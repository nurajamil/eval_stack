# Import libraries
import ast

# Import files
from ..types import ContextPayload

def parse_context_fields(context_raw) -> ContextPayload:
    sp, ctx = "", ""

    try:
        if isinstance(context_raw, str):
            data = ast.literal_eval(context_raw)
        else:
            context_raw
        sp_raw = (data or {}).get("system_prompt", "")

        if isinstance(sp_raw, list):
            sp = " ".join([e.get("content", "") for e in sp_raw])
        elif isinstance(sp_raw, dict):
            sp = sp_raw.get("content", "")
        else:
            sp = str(sp_raw or "")
        
        clist = (data or {}).get("context", [])
        if isinstance(clist, list):
            ctx = " ".join([c.get("content", "") for c in clist])
        elif isinstance(clist, dict):
            ctx = clist.get("content", "")
        else:
            ctx = str(clist or "")
    except Exception as e:
        sp, ctx = "", ""

    return ContextPayload(system_prompt=sp, context=ctx)