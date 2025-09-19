

from datetime import datetime, timezone
import time

import requests
import config


def send_status(maquina: str, status: str, detalhe: str = "", versao: str = "") -> bool:
    payload = {
        "token": config.SECRET,
        "maquina": maquina,
        "status": status,
        "data": datetime.now(timezone.utc).isoformat(),
        "versao": versao,
        "detalhe": detalhe
    }
    for attempt in range(3):
        try:
            r = requests.post(config.WEBHOOK_URL, json=payload, timeout=10)
            r.raise_for_status()
            try:
                j = r.json()
            except Exception:
                j = {}
            if j.get("ok") is True:
                return True
            else:
                time.sleep(2 + attempt)
        except Exception:
            time.sleep(2 + attempt)
            continue
    return False