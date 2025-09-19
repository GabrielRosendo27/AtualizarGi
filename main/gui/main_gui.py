import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import time

from main.update.updater import run_update 


AUTO_START = True             
AUTO_START_DELAY_MS = 500
AUTO_CLOSE_ON_COMPLETE = True  
AUTO_CLOSE_DELAY_MS = 1800
AUTO_SHOW_MESSAGE = False     

class UpdaterGUI:
    def __init__(self, root):
        self.root = root
        root.title("Atualizador Gi2000")
        root.geometry("420x160")

        self.label_status = tk.Label(root, text="Pronto", anchor="w")
        self.label_status.pack(fill="x", padx=12, pady=(12,4))

        self.progress = ttk.Progressbar(root, length=380, mode="determinate")
        self.progress.pack(padx=12, pady=6)
        self.progress["maximum"] = 6

        frame = tk.Frame(root)
        frame.pack(fill="x", padx=12, pady=6)
        self.btn_start = tk.Button(frame, text="Iniciar", command=self.start_update)
        self.btn_start.pack(side="left")
        self.btn_cancel = tk.Button(frame, text="Cancelar", command=self.cancel_update, state="disabled")
        self.btn_cancel.pack(side="right")

        self.q = queue.Queue()
        self.cancel_event = threading.Event()
        self.worker_thread = None

        
        self.root.after(150, self._poll_queue)

       
        if AUTO_START:
            self.root.after(AUTO_START_DELAY_MS, self._auto_start_if_not_running)

    def _auto_start_if_not_running(self):
        if not self.worker_thread or (self.worker_thread and not self.worker_thread.is_alive()):
            self.start_update()

    def start_update(self):
        
        if self.worker_thread and self.worker_thread.is_alive():
            return

        self.btn_start.config(state="disabled")
        self.btn_cancel.config(state="normal")
        self.progress["value"] = 0
        self.label_status.config(text="Iniciando...")
        self.cancel_event.clear()

        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def cancel_update(self):
        if messagebox.askyesno("Cancelar", "Deseja realmente cancelar a atualização?"):
            self.cancel_event.set()
            self.label_status.config(text="Pedido de cancelamento enviado...")

    def _worker(self):
        def progress_callback(step_idx, total, message):
            
            self.q.put((step_idx, total, message))

        ok = run_update(cancel_event=self.cancel_event, progress_callback=progress_callback)

        if ok:
            self.q.put(("done", None, "Atualização finalizada com sucesso"))
        else:
            if self.cancel_event.is_set():
                self.q.put(("canceled", None, "Atualização cancelada pelo usuário"))
            else:
                self.q.put(("error", None, "Atualização finalizada com erros"))

    def _close_and_exit(self):
        try:
            self.root.destroy()
        except Exception:
            pass
        
        try:
            time.sleep(0.2)
        except Exception:
            pass
        
        os._exit(0)

    def _poll_queue(self):
        try:
            while True:
                item = self.q.get_nowait()
                step_idx, total, message = item

                
                if step_idx == "done":
                    self.progress["value"] = self.progress["maximum"]
                    self.label_status.config(text=message)
                    
                    if AUTO_SHOW_MESSAGE:
                        try:
                            messagebox.showinfo("Concluído", message)
                        except Exception:
                            pass
                    
                    self.btn_start.config(state="disabled")
                    self.btn_cancel.config(state="disabled")
                    if AUTO_CLOSE_ON_COMPLETE:
                        
                        
                        self.root.after(AUTO_CLOSE_DELAY_MS, self._close_and_exit)
                    continue

                
                if step_idx == "canceled":
                    self.label_status.config(text=message)
                    if AUTO_SHOW_MESSAGE:
                        try:
                            messagebox.showinfo("Cancelado", message)
                        except Exception:
                            pass
                    self.btn_start.config(state="disabled")
                    self.btn_cancel.config(state="disabled")
                    if AUTO_CLOSE_ON_COMPLETE:
                        self.root.after(AUTO_CLOSE_DELAY_MS, self._close_and_exit)
                    continue

                
                if step_idx == "error":
                    self.label_status.config(text=message)
                    
                    if AUTO_SHOW_MESSAGE:
                        try:
                            messagebox.showerror("Erro", message)
                        except Exception:
                            pass
                    self.btn_start.config(state="normal")
                    self.btn_cancel.config(state="disabled")
                    continue

                
                try:
                    sidx = int(step_idx)
                except Exception:
                    sidx = 0
                if sidx > 0 and total:
                    try:
                        frac = (sidx / total) * self.progress["maximum"]
                        self.progress["value"] = frac
                    except Exception:
                        pass

                self.label_status.config(text=message)

                
                if "cancel" in str(message).lower() or "erro" in str(message).lower():
                    self.btn_start.config(state="normal")
                    self.btn_cancel.config(state="disabled")

        except queue.Empty:
            pass

        self.root.after(150, self._poll_queue)


if __name__ == "__main__":
    root = tk.Tk()
    app = UpdaterGUI(root)
    root.mainloop()
