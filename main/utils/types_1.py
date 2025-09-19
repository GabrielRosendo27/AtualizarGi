
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class Context:
    cancel_event: Optional[Any] = None
    driver: Optional[Any] = None
    status_to_send: Optional[str] = None
    detail_msg: str = ""
   


@dataclass
class StepResult:
    ok: bool
    status_to_send: Optional[str] = None
    detail_msg: Optional[str] = None
    
