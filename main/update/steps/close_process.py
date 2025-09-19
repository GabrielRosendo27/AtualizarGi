from dataclasses import asdict
from main.utils.kill_process1 import kill_process  
from typing import Callable
from main.utils.types_1 import StepResult, Context  

def step_one(ctx: Context, step: Callable[[int, str], None]) -> StepResult:
    step(1, "Fechando Gi2000")
    try:
        kill_process("Gi2000.exe")
    except Exception as exc:
        return StepResult(False, "error", f"Falha ao fechar Gi2000: {exc}")

    if ctx.cancel_event and ctx.cancel_event.is_set():
        step(-1, "Operação cancelada")
        return StepResult(False, "canceled", "Operação cancelada antes de iniciar")

    return StepResult(True)
