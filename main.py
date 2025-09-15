
import sys
from updater import run_update

from admin_helper import is_admin, relaunch_as_admin
if not is_admin():
    print("Executando sem privilégios de administrador — tentando relançar com UAC...")
    if relaunch_as_admin():
        sys.exit(0) 
    else:
        print("Não foi possível relançar com UAC. Execute este programa como Administrador.")


if __name__ == "__main__":
    print("🚀 Iniciando atualização do Gi2000...")
    try:
        run_update()
    except Exception as e:
        print(f"[ERRO] {e}")
