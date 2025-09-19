
import sys, os
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def relaunch_as_admin():
    
    if is_admin():
        return False
    params = " ".join([f'"{p}"' for p in sys.argv[1:]])
    python_exe = sys.executable
    
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", python_exe, f'"{sys.argv[0]}" {params}', None, 1)
        return True
    except Exception:
        return False
