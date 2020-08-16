from typing import Dict
from contextvars import ContextVar
from sowba.core.application import SServiceRouter


sowba_services_var: ContextVar[Dict[str, SServiceRouter]] = ContextVar(
    "sowba_services_var", default={}
)
