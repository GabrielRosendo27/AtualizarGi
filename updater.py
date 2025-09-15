
import os
import time
import shutil
import zipfile
import requests
import traceback
import urllib.parse
import string

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


def sanitize_filename_from_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    raw_name = os.path.basename(urllib.parse.unquote(parsed.path)) or "downloaded_update.zip"
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleaned = "".join(c for c in raw_name if c in valid_chars)
    if not cleaned.lower().endswith(".zip"):
        cleaned += ".zip"
    return cleaned


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
    try:
        
        step(1, "Fechando Gi2000")
        kill_process("Gi2000.exe")
        if cancel_event and cancel_event.is_set():
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
            step(-2, "Erro: não conseguiu capturar URL do download")
            return False

        
        try:
            driver.quit()
        except Exception:
            pass
        driver = None

        if cancel_event and cancel_event.is_set():
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
                            tmp_zip.unlink(missing_ok=True)
                            step(-1, "Operação cancelada durante download")
                            return False
                        if chunk:
                            f.write(chunk)
            tmp_zip.replace(final_zip)
        except Exception as e:
            step(-2, f"Erro no download: {e}")
            traceback.print_exc()
            if tmp_zip.exists():
                try:
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
            step(-2, f"Erro ao extrair o ZIP: {e}")
            traceback.print_exc()
            return False

        if cancel_event and cancel_event.is_set():
            step(-1, "Operação cancelada")
            return False

        
        step(6, "Substituindo arquivos")
        if not Path(TARGET_DIR).exists():
            step(-2, f"Pasta destino não encontrada: {TARGET_DIR}")
            return False

        try:
            for f in FILES_TO_COPY:
                if cancel_event and cancel_event.is_set():
                    step(-1, "Operação cancelada")
                    return False
                src = extract_dir / f
                dest = Path(TARGET_DIR) / f
                if not src.exists():
                    step(-2, f"Arquivo esperado não encontrado no ZIP: {src.name}")
                    return False
                
                try:
                    if dest.exists():
                        try:
                            dest.unlink()
                        except Exception:
                            pass
                    shutil.copy2(src, dest)
                except Exception as e:
                    step(-2, f"Falha ao copiar {f}: {e}")
                    traceback.print_exc()
                    return False
        finally:
            
            try:
                shutil.rmtree(extract_dir)
            except Exception:
                pass

        
        step(TOTAL_STEPS, "Atualização concluída com sucesso")
        return True

    except Exception as e:
        step(-2, f"Erro inesperado: {e}")
        traceback.print_exc()
        return False

    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass
