import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox

from app.theme import set_theme
from app.utils import resource_path, close_application
from core.correspondence_processor import process_correspondence_folder

import time
import threading


def main(launcher_root=None):

    def back_to_launcher():
        if launcher_root:
            launcher_root.deiconify()
        root.destroy()

    root = tk.Toplevel()
    set_theme(root)

    root.iconbitmap(resource_path("assets/icon.ico"))
    root.title("Correspondence Processing Module v1.0.0")
    root.geometry("850x700")
    root.resizable(True, True)

    input_folder = tk.StringVar()
    output_folder = tk.StringVar()

    # Future use if needed
    # assignation_csv = tk.StringVar()

    start_time = None

    ####################################################################
    # LOG
    ####################################################################

    def log_message(msg):
        root.after(
            0,
            lambda: (
                log_text.insert(tk.END, msg + "\n"),
                log_text.see(tk.END)
            )
        )

    ####################################################################
    # NAVIGATION
    ####################################################################

    ttk.Button(
        root,
        text="Back",
        command=back_to_launcher
    ).pack(anchor="w", padx=10, pady=5)

    ####################################################################
    # FOLDER SELECTION
    ####################################################################

    def select_input_folder():
        folder = filedialog.askdirectory()

        if folder:
            input_folder.set(folder)
            log_message(f"Input folder selected: {folder}")

    def select_output_folder():
        folder = filedialog.askdirectory()

        if folder:
            output_folder.set(folder)
            log_message(f"Output folder selected: {folder}")

    ####################################################################
    # PLACEHOLDER FUNCTIONS
    ####################################################################

    def update_progress(processed, total):

        def _update():

            percent = (
                processed / total * 100
                if total > 0
                else 0
            )

            progress["value"] = percent

            progress_var.set(
                f"Processed: {processed} / {total}"
            )

            if processed > 0 and start_time:

                elapsed = time.time() - start_time

                avg_time = elapsed / processed

                remaining = total - processed

                eta_seconds = int(
                    avg_time * remaining
                )

                mins, secs = divmod(
                    eta_seconds,
                    60
                )

                eta_var.set(
                    f"Time Remaining: {mins:02d}:{secs:02d}"
                )

        root.after(0, _update)

    def update_current_file(filename):

        root.after(
            0,
            lambda f=filename:
            current_file_var.set(
                f"Current File: {f}"
            )
        )

    ####################################################################
    # TEMPORARY RUN
    ####################################################################

    def run():

        nonlocal start_time

        if not input_folder.get():
            messagebox.showerror(
                "Error",
                "Please select an input folder"
            )
            return
        
        if not output_folder.get():
            messagebox.showerror(
                "Error",
                "Please select an output folder"
            )
            return
        
        start_time = time.time()

        status_var.set(("Processing..."))

        run_button.config(state=tk.DISABLED)

        threading.Thread(
            target = task,
            daemon = True
        ).start()

    def task():
        try:
            results = process_correspondence_folder(
                input_folder.get(),
                output_folder.get(),
                log_callback=log_message,
                progress_callback=update_progress,
                current_file_callback=update_current_file
            )

            root.after(
                0,
                lambda: status_var.set("Completed Sucessfully")
            )

            log_message("Correspondence Processing Completed.")

            root.after(
                0,
                lambda: messagebox.showinfo(
                    "Process Completed",
                    f"Processed Files: {len(results)}"
                )
            )
        except Exception as e:
            error_msg = str(e)

            root.after(
                0,
                lambda: status_var.set("Error")
            )

            log_message(
                f"Error {error_msg}"
            )

            root.after(
                0,
                lambda msg=error_msg:
                messagebox.showerror("Error", msg)
            )
        
        finally:

            root.after(
                0,
                lambda: run_button.config(
                    state=tk.NORMAL
                )
            )

            root.after(
                0,
                lambda: progress.configure(
                    value=100
                )
            )
    ####################################################################
    # UI
    ####################################################################

    main_frame = ttk.Frame(
        root,
        padding=20
    )

    main_frame.pack(
        fill=tk.BOTH,
        expand=True
    )

    ####################################################################
    # TITLE
    ####################################################################

    ttk.Label(
        main_frame,
        text="Correspondence Processing Module",
        font=("Helvetica", 16, "bold")
    ).pack(
        pady=(0, 20)
    )

    ####################################################################
    # INPUTS
    ####################################################################

    def build_row(label_text, var, command):

        row = ttk.Frame(main_frame)

        row.pack(
            fill="x",
            pady=5
        )

        ttk.Label(
            row,
            text=label_text,
            width=18
        ).pack(
            side=tk.LEFT
        )

        ttk.Entry(
            row,
            textvariable=var
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        ttk.Button(
            row,
            text="Browse",
            command=command
        ).pack(
            side="left"
        )

    build_row(
        "Input Folder:",
        input_folder,
        select_input_folder
    )

    build_row(
        "Output Folder:",
        output_folder,
        select_output_folder
    )

    """
    build_row(
        "Assignment CSV:",
        assignation_csv,
        select_assignation_csv
    )
    """

    ####################################################################
    # NAMING FORMAT
    ####################################################################

    ttk.Separator(
        main_frame,
        orient="horizontal"
    ).pack(
        fill="x",
        pady=15
    )

    ttk.Label(
        main_frame,
        text="Output Naming Format",
        font=("Segoe UI", 11, "bold")
    ).pack(
        anchor="w"
    )

    ttk.Label(
        main_frame,
        text="PAYER_PATIENT_MM-DD-YYYY.pdf"
    ).pack(
        anchor="w",
        pady=(5, 10)
    )

    ####################################################################
    # PROCESS BUTTON
    ####################################################################

    ttk.Separator(
        main_frame,
        orient="horizontal"
    ).pack(
        fill="x",
        pady=15
    )

    button_frame = ttk.Frame(
        main_frame
    )

    button_frame.pack(
        fill="x",
        pady=10
    )

    run_button = ttk.Button(
        button_frame,
        text="Start Processing",
        command=run,
        width=20,
        style="Accent.TButton"
    )

    run_button.pack(
        side="left",
        padx=5
    )

    ####################################################################
    # PROGRESS
    ####################################################################

    progress = ttk.Progressbar(
        button_frame,
        mode="determinate",
        maximum=100
    )

    progress.pack(
        fill="x",
        padx=5
    )

    status_var = tk.StringVar(
        value="Ready"
    )

    progress_var = tk.StringVar(
        value="Processed 0 / 0"
    )

    eta_var = tk.StringVar(
        value="Time Remaining: Calculating..."
    )

    current_file_var = tk.StringVar(
        value="Current File: Waiting"
    )

    ttk.Label(
        main_frame,
        textvariable=status_var
    ).pack()

    ttk.Label(
        main_frame,
        textvariable=progress_var
    ).pack()

    ttk.Label(
        main_frame,
        textvariable=eta_var
    ).pack()

    ttk.Label(
        main_frame,
        textvariable=current_file_var
    ).pack()

    ####################################################################
    # LOG
    ####################################################################

    ttk.Separator(
        main_frame,
        orient="horizontal"
    ).pack(
        fill="x",
        pady=10
    )

    ttk.Label(
        main_frame,
        text="Processing Log",
        font=("Segoe UI", 10, "bold")
    ).pack(
        anchor="w",
        pady=(10, 5)
    )

    log_text = tk.Text(
        main_frame,
        height=12,
        bg="#1e1e1e",
        fg="#00ff00",
        font=("Courier", 9)
    )

    log_text.pack(
        fill="both",
        expand=True,
        pady=(5, 0)
    )

    scrollbar = ttk.Scrollbar(
        log_text
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    log_text.config(
        yscrollcommand=scrollbar.set
    )

    scrollbar.config(
        command=log_text.yview
    )

    root.protocol(
        "WM_DELETE_WINDOW",
        lambda: close_application(root, launcher_root)
    )