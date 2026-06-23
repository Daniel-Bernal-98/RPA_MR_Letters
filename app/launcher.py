import tkinter as tk
from tkinter import ttk

from app.mr_ui import main as mr_main
from app.utils import resource_path, close_application
from app.correspondence_ui import main as correspondence_main
from app.theme import set_theme

root = tk.Tk()

def open_mr_ui():
    set_theme(root)
    root.withdraw()
    mr_main(root)

def open_correspondence_ui():
    set_theme(root)
    root.withdraw()
    correspondence_main(root)

def main():
    set_theme(root)
    root.title("ABATECH Letters Automation Tool")
    root.geometry("600x400")
    root.resizable(True, True)

    ttk.Label(
        root,
        text= "ABATECH Letters Automation Tool",
        font= ("Segoe UI", 16, "bold")
    ).pack(pady=10)

    ttk.Label(
        root,
        text= "Select the module you want to use"
    ).pack(pady=10)

    ttk.Button(
        root,
        text= "Medical Records Letters",
        command=lambda: open_mr_ui(),
        width=30
    ).pack(pady=20)

    ttk.Button(
        root,
        text= "Correspondence Team",
        command=lambda: open_correspondence_ui(),
        width=30
    ).pack(pady=20)

    root.protocol(
        "WM_DELETE_WINDOW",
        lambda: close_application(root)
    )

    root.mainloop()

if __name__ == "__main__":
    main()