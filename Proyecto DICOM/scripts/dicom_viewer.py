"""Visor unificado: abre una ventana para elegir un archivo o carpeta
DICOM, detecta automaticamente si es una imagen simple, un archivo
multi-frame, o una serie completa, y abre el explorador interactivo
(scroll = navegar cortes, teclas a/c/s = cambiar de plano).

Uso
---
    python scripts/dicom_viewer.py
"""

import tkinter as tk
from tkinter import filedialog, messagebox

from dicom_tools import load_volume
from dicom_tools.viewer import explore_volume


def _pick_path() -> str:
    root = tk.Tk()
    root.title("DICOM Tools")
    root.attributes("-topmost", True)
    root.resizable(False, False)

    chosen = {"path": ""}

    def choose_file():
        path = filedialog.askopenfilename(
            parent=root,
            title="Selecciona un archivo DICOM",
            filetypes=[("DICOM", "*.dcm"), ("Todos los archivos", "*.*")],
        )
        if path:
            chosen["path"] = path
            root.quit()

    def choose_folder():
        path = filedialog.askdirectory(parent=root, title="Selecciona una carpeta con una serie DICOM")
        if path:
            chosen["path"] = path
            root.quit()

    tk.Label(root, text="Que quieres abrir?", padx=20, pady=10).pack()
    tk.Button(root, text="Archivo .dcm", width=28, command=choose_file).pack(padx=20, pady=5)
    tk.Button(root, text="Carpeta con una serie", width=28, command=choose_folder).pack(padx=20, pady=(0, 15))
    root.protocol("WM_DELETE_WINDOW", root.quit)

    root.mainloop()
    root.destroy()
    return chosen["path"]


def main() -> None:
    path = _pick_path()
    if not path:
        print("No se selecciono ninguna ruta.")
        return

    try:
        volume = load_volume(path)
    except ValueError as exc:
        messagebox.showerror("Error al cargar DICOM", str(exc))
        return

    print(f"Cargado: {path}")
    print(f"shape={volume.shape}  spacing(mm)={volume.spacing}  un_solo_corte={volume.is_single_slice}")

    explore_volume(volume)


if __name__ == "__main__":
    main()
