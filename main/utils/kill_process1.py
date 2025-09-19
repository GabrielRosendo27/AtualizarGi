
import subprocess

def kill_process(process_name: str):
    try:
        subprocess.run(["taskkill", "/f", "/im", process_name], check=True, capture_output=True)
        print(f"[OK] Processo {process_name} encerrado.")
    except subprocess.CalledProcessError:
        print(f"[INFO] Processo {process_name} não encontrado ou já fechado.")
