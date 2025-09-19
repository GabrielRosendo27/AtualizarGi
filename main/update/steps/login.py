# steps/login.py
from typing import Callable
from main.utils import StepResult, Context

def step_three(ctx: Context, step: Callable[[int, str], None]) -> StepResult:
    step(3, "Realizando login")
    driver = ctx.driver
    if driver is None:
        return StepResult(False, "error", "Driver não inicializado")
    try:
        # seu fluxo de login, por exemplo:
        # fill form, submit, wait, validar login
        pass
    except Exception as exc:
        return StepResult(False, "error", f"Erro no login: {exc}")

    if ctx.cancel_event and ctx.cancel_event.is_set():
        step(-1, "Operação cancelada")
        return StepResult(False, "canceled", "Operação cancelada durante login")

    return StepResult(True)
