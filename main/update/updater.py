# updater.py
import time
from dataclasses import dataclass
from typing import Callable, Optional

from steps.close_process import step_one
from steps.open_browser import step_two
from steps.login import step_three
from steps.link_download import step_four
from steps.att_download import step_five
from steps.file_switch import step_six

TOTAL_STEPS = 6

@dataclass
class Context:
    cancel_event: Optional[object] = None
    driver: Optional[object] = None
    status_to_send: Optional[str] = None
    detail_msg: str = ""

@dataclass
class StepResult:
    ok: bool
    status_to_send: Optional[str] = None
    detail_msg: Optional[str] = None

def run_update(progress_callback: Optional[Callable[[int, int, str], None]] = None, cancel_event=None):
    def step(n: int, msg: str):
        if progress_callback:
            try:
                progress_callback(n, TOTAL_STEPS, msg)
            except Exception:
                pass

    ctx = Context(cancel_event=cancel_event)
    try:
        # STEP 1
        res = step_one(ctx, step)
        if not res.ok:
            ctx.status_to_send = res.status_to_send
            ctx.detail_msg = res.detail_msg or ""
            return False

        # STEP 2
        res = step_two(ctx, step)
        if not res.ok:
            ctx.status_to_send = res.status_to_send
            ctx.detail_msg = res.detail_msg or ""
            return False

        # STEP 3
        res = step_three(ctx, step)
        if not res.ok:
            ctx.status_to_send = res.status_to_send
            ctx.detail_msg = res.detail_msg or ""
            return False

        # STEP 4
        res = step_four(ctx, step)
        if not res.ok:
            ctx.status_to_send = res.status_to_send
            ctx.detail_msg = res.detail_msg or ""
            return False

        # STEP 5
        res = step_five(ctx, step)
        if not res.ok:
            ctx.status_to_send = res.status_to_send
            ctx.detail_msg = res.detail_msg or ""
            return False

        # STEP 6
        res = step_six(ctx, step)
        if not res.ok:
            ctx.status_to_send = res.status_to_send
            ctx.detail_msg = res.detail_msg or ""
            return False

        # ... restantes
        return True

    except Exception as exc:
        # capture unexpected exceptions, defina status se quiser
        ctx.status_to_send = "error"
        ctx.detail_msg = f"Exceção não tratada: {exc}"
        return False
    finally:
        # cleanup: fechar driver se houver
        try:
            if ctx.driver:
                ctx.driver.quit()
        except Exception:
            pass
