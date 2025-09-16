# updater.py (corrigido)
import os
import time
import shutil
import zipfile
import requests
import traceback
import urllib.parse
import string
import socket
import platform
from datetime import datetime, timezone
from pathlib import Path
from selenium.webdriver.common.by import By
from utils import kill_process
from browser import accept_cookies_if_present, start_browser, wait_and_click

PORTAL_URL = "https://www.gi.com.br/"
DOWNLOAD_DIR = Path.home() / "Downloads"
TARGET_DIR = Path(r"C:\Program Files (x86)\Gi2000")
FILES_TO_COPY = ["Gi2000.exe", "GI_REMESSA.exe"]

USERNAME = "github"
PASSWORD = "github"

TOTAL_STEPS = 6

WEBHOOK_URL = "github"
SECRET = "github"


def sanitize_filename_from_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    raw_name = os.path.basename(urllib.parse.unquote(parsed.path)) or "downloaded_update.zip"
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleaned = "".join(c for c in raw_name if c in valid_chars)
    if not cleaned.lower().endswith(".zip"):
        cleaned += ".zip"
    return cleaned


def send_status(maquina: str, status: str, detalhe: str = "", versao: str = "") -> bool:
    """
    Envia o status para o webhook (com retries).
    Retorna True se o webhook respondeu ok, False caso contrário.
    """
    payload = {
        "token": SECRET,
        "maquina": maquina,
        "status": status,               # "ok", "error", "canceled"
        "data": datetime.now(timezone.utc).isoformat(),
        "versao": versao,
        "detalhe": detalhe
    }

    for attempt in range(3):
        try:
            r = requests.post(WEBHOOK_URL, json=payload, timeout=10)
            r.raise_for_status()
            try:
                j = r.json()
            except Exception:
                j = {}
            if j.get("ok") is True:
                return True
            else:
                # resposta não-ok (apps script pode devolver {ok:false, error:...})
                # não vamos levantar exceção aqui, tentamos novamente
                time.sleep(2 + attempt)
        except Exception:
            # espera incremental antes de nova tentativa
            time.sleep(2 + attempt)
            continue
    return False


def run_update(progress_callback=None, cancel_event=None):
    """
    Executa a atualização do GI2000 e notifica progresso via progress_callback(step_idx, total, message).
    Retorna True em sucesso, False em cancelamento/erro.
    """

    def step(n, msg):
        if progress_callback:
            try:
                progress_callback(n, TOTAL_STEPS, msg)
            except Exception:
                pass

    driver = None
    # variáveis para envio de status no finally
    status_to_send = None
    detail_msg = ""
    version_str = ""

    try:
        step(1, "Fechando Gi2000")
        kill_process("Gi2000.exe")
        if cancel_event and cancel_event.is_set():
            status_to_send = "canceled"
            detail_msg = "Operação cancelada antes de iniciar"
            step(-1, "Operação cancelada")
            return False

        step(2, "Abrindo navegador")
        driver = start_browser()
        driver.get(PORTAL_URL)
        time.sleep(1)
        try:
            accept_cookies_if_present(driver)
        except Exception:
            pass
        if cancel_event and cancel_event.is_set():
            status_to_send = "canceled"
            detail_msg = "Operação cancelada após abrir navegador"
            step(-1, "Operação cancelada")
            return False

        step(3, "Realizando login")
        wait_and_click(driver, By.LINK_TEXT, "Área do Cliente")
        time.sleep(1)
        try:
            driver.find_element(By.ID, "Login").send_keys(USERNAME)
            driver.find_element(By.ID, "Senha").send_keys(PASSWORD)
            wait_and_click(driver, By.CSS_SELECTOR, "button[type=submit]")
        except Exception:
            try:
                wait_and_click(driver, By.CSS_SELECTOR, "button.login-btn")
            except Exception:
                pass
        time.sleep(2)
        if cancel_event and cancel_event.is_set():
            status_to_send = "canceled"
            detail_msg = "Operação cancelada durante login"
            step(-1, "Operação cancelada")
            return False

        step(4, "Obtendo link de download")
        try:
            if not wait_and_click(driver, By.LINK_TEXT, "Abrir Downloads"):
                wait_and_click(driver, By.LINK_TEXT, "Downloads")
        except Exception:
            pass
        time.sleep(1)

        url = None
        try:
            url = driver.execute_script("return (document.getElementById('down_2')||{}).value || null;")
        except Exception:
            url = None

        if not url:
            inputs = driver.find_elements(By.CSS_SELECTOR, "input[id^='down_']")
            if inputs:
                url = inputs[0].get_attribute("value")

        if not url:
            els = driver.find_elements(By.CSS_SELECTOR, "a[onclick]")
            for el in els:
                onclick = el.get_attribute("onclick") or ""
                if "Download(2" in onclick:
                    try:
                        el.click()
                        time.sleep(0.8)
                        url = driver.execute_script("return (document.getElementById('down_2')||{}).value || null;")
                        if url:
                            break
                    except Exception:
                        pass

        if not url:
            status_to_send = "error"
            detail_msg = "Não conseguiu capturar URL do download"
            step(-2, "Erro: não conseguiu capturar URL do download")
            return False

        try:
            driver.quit()
        except Exception:
            pass
        driver = None

        if cancel_event and cancel_event.is_set():
            status_to_send = "canceled"
            detail_msg = "Operação cancelada após obter URL"
            step(-1, "Operação cancelada")
            return False

        step(5, "Baixando atualização")
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        zip_name = sanitize_filename_from_url(url)
        tmp_zip = DOWNLOAD_DIR / (zip_name + ".part")
        final_zip = DOWNLOAD_DIR / zip_name
        try:
            with requests.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(tmp_zip, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if cancel_event and cancel_event.is_set():
                            try:
                                tmp_zip.unlink(missing_ok=True)
                            except Exception:
                                pass
                            status_to_send = "canceled"
                            detail_msg = "Cancelado durante download"
                            step(-1, "Operação cancelada durante download")
                            return False
                        if chunk:
                            f.write(chunk)
            tmp_zip.replace(final_zip)
        except Exception as e:
            status_to_send = "error"
            detail_msg = f"Erro no download: {e}"
            step(-2, detail_msg)
            traceback.print_exc()
            try:
                if tmp_zip.exists():
                    tmp_zip.unlink()
            except Exception:
                pass
            return False

        try:
            extract_dir = Path(os.environ.get("TEMP", ".")) / f"Gi2000_Update_{int(time.time())}"
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            extract_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(final_zip, "r") as zf:
                zf.extractall(extract_dir)
        except Exception as e:
            status_to_send = "error"
            detail_msg = f"Erro ao extrair o ZIP: {e}"
            step(-2, detail_msg)
            traceback.print_exc()
            return False

        if cancel_event and cancel_event.is_set():
            status_to_send = "canceled"
            detail_msg = "Operação cancelada após extração"
            step(-1, "Operação cancelada")
            return False

        step(6, "Substituindo arquivos")
        if not Path(TARGET_DIR).exists():
            status_to_send = "error"
            detail_msg = f"Pasta destino não encontrada: {TARGET_DIR}"
            step(-2, detail_msg)
            return False

        try:
            for f in FILES_TO_COPY:
                if cancel_event and cancel_event.is_set():
                    status_to_send = "canceled"
                    detail_msg = "Cancelado antes da substituição de arquivos"
                    step(-1, "Operação cancelada")
                    return False
                src = extract_dir / f
                dest = Path(TARGET_DIR) / f
                if not src.exists():
                    status_to_send = "error"
                    detail_msg = f"Arquivo esperado não encontrado no ZIP: {src.name}"
                    step(-2, detail_msg)
                    return False
                try:
                    if dest.exists():
                        try:
                            dest.unlink()
                        except Exception:
                            pass
                    shutil.copy2(src, dest)
                except Exception as e:
                    status_to_send = "error"
                    detail_msg = f"Falha ao copiar {f}: {e}"
                    step(-2, detail_msg)
                    traceback.print_exc()
                    return False
        finally:
            try:
                shutil.rmtree(extract_dir)
            except Exception:
                pass

        # sucesso
        status_to_send = "ok"
        detail_msg = "Atualização concluída com sucesso"
        step(TOTAL_STEPS, detail_msg)
        return True

    except Exception as e:
        status_to_send = "error"
        detail_msg = f"Erro inesperado: {e}"
        step(-2, detail_msg)
        traceback.print_exc()
        return False

    finally:
        # cleanup final: garantir que driver foi fechado e informar o webhook (não retorna nada)
        try:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
        except Exception:
            pass

        # tenta enviar status (não altera o retorno da função)
        try:
            maquina = socket.gethostname()
            # versão tentamos obter do exe, se existir
            try:
                ver = ""
                exe_path = Path(TARGET_DIR) / "Gi2000.exe"
                if exe_path.exists():
                    try:
                        ver = str(exe_path.stat().st_mtime)  # como fallback simples; ajuste se quiser FileVersion
                    except Exception:
                        ver = ""
            except Exception:
                ver = ""
            # envia (fire-and-forget, com retries)
            try:
                ok_sent = send_status(maquina=maquina, status=status_to_send or "unknown", detalhe=detail_msg or "", versao=ver)
                if not ok_sent:
                    # opcional: logar em arquivo local se não conseguiu enviar
                    try:
                        log_dir = Path(r"C:\ProgramData\GIUpdater")
                        log_dir.mkdir(parents=True, exist_ok=True)
                        with open(log_dir / "last_status.txt", "a", encoding="utf-8") as fh:
                            fh.write(f"{datetime.now(timezone.utc).isoformat()} | {maquina} | {status_to_send} | {detail_msg}\n")
                    except Exception:
                        pass
            except Exception:
                pass
        except Exception:
            pass
