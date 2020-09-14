from typing import Any
from typing import Dict
from dataclasses import dataclass, field
from contextvars import ContextVar


@dataclass
class Registry:
    app: Dict[str, Any] = field(default_factory=dict)
    service: Dict[str, Any] = field(default_factory=dict)
    storage: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)


REGISTRY: ContextVar[Registry] = ContextVar("REGISTRY", default=Registry())
