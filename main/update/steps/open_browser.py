
from typing import Callable

from dotenv import load_dotenv
from main.utils.types_1 import StepResult, Context
from main.browser.browser_cookies import accept_cookies_if_present
from main.browser.browser import start_browser
from main.utils.config import PORTAL_URL
def step_two(ctx: Context, step: Callable[[int, str], None]) -> StepResult:
    step(2, "Abrindo navegador")
    try:
        driver = start_browser()
        driver.get(PORTAL_URL)   
        try:
            accept_cookies_if_present(driver)
        except Exception:
            pass
    except Exception as exc:
        return StepResult(False, "error", f"Falha ao abrir navegador: {exc}")

    ctx.driver = driver

    if ctx.cancel_event and ctx.cancel_event.is_set():
        step(-1, "Operação cancelada")
        return StepResult(False, "canceled", "Operação cancelada após abrir navegador")

    return StepResult(True)
