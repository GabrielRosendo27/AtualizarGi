# steps/open_browser.py
from typing import Callable
from updater import StepResult, Context
from main.browser import start_browser, accept_cookies_if_present  # seu util real

def step_two(ctx: Context, step: Callable[[int, str], None]) -> StepResult:
    step(2, "Abrindo navegador")
    try:
        driver = start_browser()
        driver.get("https://seu.portal.url")   # substitua por config.PORTAL_URL
        # pequenas esperas, etc.
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
