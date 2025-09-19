# updater.py (ou types.py)
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class Context:
    cancel_event: Optional[Any] = None
    driver: Optional[Any] = None
    status_to_send: Optional[str] = None
    detail_msg: str = ""
    # adicione mais campos compartilhados conforme necessário


@dataclass
class StepResult:
    ok: bool
    status_to_send: Optional[str] = None
    detail_msg: Optional[str] = None
    # opcional: campo extra (e.g. driver) se necessário
