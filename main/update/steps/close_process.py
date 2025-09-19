# steps/close_process.py
from dataclasses import asdict
from main.utils import kill_process  # se kill_process estiver no root
from typing import Callable
from main.utils import StepResult, Context  # se types estiverem no updater, ajuste import

def step_one(ctx: Context, step: Callable[[int, str], None]) -> StepResult:
    step(1, "Fechando Gi2000")
    try:
        # kill_process deve ser uma função que recebe nome do executável
        kill_process("Gi2000.exe")
    except Exception as exc:
        # se quiser continuar mesmo com erro, ajuste comportamento
        return StepResult(False, "error", f"Falha ao fechar Gi2000: {exc}")

    if ctx.cancel_event and ctx.cancel_event.is_set():
        step(-1, "Operação cancelada")
        return StepResult(False, "canceled", "Operação cancelada antes de iniciar")

    return StepResult(True)
