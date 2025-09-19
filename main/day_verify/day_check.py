from weekday_check import should_run_today
import sys
import os
from pathlib import Path


def daycheck():
    ALLOWED_SPEC = os.environ.get("ALLOWED_UPDAYS", "mon,tue,thu")
    FORCE = "--force" in sys.argv or os.environ.get("FORCE_UPDATER", "") == "1"

    if not (FORCE or should_run_today(ALLOWED_SPEC)):
        msg = f"Hoje não é dia permitido ({ALLOWED_SPEC}). Saindo imediatamente."
        print(msg)
        try:
            p = Path(r"C:\ProgramData\GIUpdater")
            p.mkdir(parents=True, exist_ok=True)
            with open(p / "launcher.log", "a", encoding="utf-8") as fh:
                from datetime import datetime
                fh.write(f"{datetime.now().isoformat()} - {msg}\n")
        except Exception:
            pass
        sys.exit(0)

