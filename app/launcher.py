import tkinter as tk
from tkinter import ttk

from app.mr_ui import main as mr_main, resource_path
from app.correspondence_ui import main as correspondence_main

root = tk.Tk()

def set_theme(root):
    style = ttk.Style()
    try:
        root.tk.call("source", resource_path("assets/forest-dark.tcl"))# Forest dark theme call
        style.theme_use("forest-dark")
    except Exception as e:
        print(f"Theme loading error: {e}")

def open_mr_ui():
    set_theme(root)
    root.withdraw()
    mr_main()

def open_correspondence_ui():
    set_theme(root)
    root.withdraw()
    correspondence_main()

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
        command=lambda: open_mr_ui(root),
        width=30
    ).pack(pady=20)

    ttk.Button(
        root,
        text= "Correspondence Team",
        command=lambda: open_correspondence_ui(root),
        width=30
    ).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()