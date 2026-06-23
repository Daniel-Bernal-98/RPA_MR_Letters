from tkinter import ttk
from app.utils import resource_path

_theme_loaded = False

def set_theme(root):
    global _theme_loaded

    style = ttk.Style()

    try:
        if not _theme_loaded:
            root.tk.call(
                "source",
                resource_path("assets/forest-dark.tcl")
            )
            _theme_loaded = True

        style.theme_use("forest-dark")
    except Exception:
        style.theme_use("forest-dark")