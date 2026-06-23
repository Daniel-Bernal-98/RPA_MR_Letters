# ============================================================================
# Automatic Letter Reader for workload Assignations
#
# Copyright (c) 2026 ABA Centers of America
# All Rights Reserved.
#
# Proprietary and Confidential.
# For internal use only.
#
# Unauthorized copying, distribution, modification, or disclosure
# of this software is strictly prohibited.
# ============================================================================

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from app.theme import set_theme
import threading
import csv
from datetime import datetime
from core.processor import process_folder
import locale
from app.utils import resource_path, close_application
import time

#default list of payers, can be extended if needed
DEFAULT_PAYERS = ["UMR","Optum", "Aetna", "Cigna", "BCBS TX", "Florida Blue", "Auto"]

def main(launcher_root = None):

    def back_to_launcher():
        if launcher_root:
            launcher_root.deiconify()
        root.destroy()

    root =tk.Toplevel()

    #set_theme(root)

    root.iconbitmap(resource_path("assets/icon.ico"))#Custom Icon
    root.title("RPA Letter Mass Processor - Multi-Payer Support v1.0.0")
    ttk.Button(root, text="Back", command=back_to_launcher).pack(anchor="w", padx=10, pady=5)
    root.geometry("850x700")
    root.resizable(True, True)   
    
    input_folder = tk.StringVar()
    csv_file = tk.StringVar()
    output_folder = tk.StringVar()
    selected_payer = tk.StringVar(value=DEFAULT_PAYERS[0])
    start_time = None

    # ----------------- UI Build -----------------
    
    ### LOG UI ###

    def log_message(msg):
        root.after(
            0,lambda: (
                log_text.insert(tk.END, msg + "\n"),
                log_text.see(tk.END)
            )
        )

    ### FUNCTIONS ###

    def select_input_folder():
        folder = filedialog.askdirectory()
        if folder:
            input_folder.set(folder)

    def select_csv_file(): # Assignations CSV
        file = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file:
            csv_file.set(file)

    def select_output_folder():
        folder = filedialog.askdirectory()
        if folder:
            output_folder.set(folder)

    def update_progress(processed, total):
        def _update():
            percent = (processed / total *100 if total > 0  else 0)
            progress["value"] = percent
            progress_var.set(f"{processed} / {total}")

            if processed >0 and start_time:
                elapsed = time.time() - start_time
                avg_time = elapsed / processed
                remaining = total - processed
                eta_seconds = int(avg_time * remaining)
                mins, secs = divmod(eta_seconds, 60)
                eta_var.set(f"Time remaining: {mins:02d}:{secs:02d}")

        root.after(0, _update)

    def update_current_file(filename):
        root.after(0, lambda f=filename: current_file_var.set(f"Current File: {f}"))

    def run():
        nonlocal start_time
        if not input_folder.get() or not csv_file.get() or not output_folder.get():
            messagebox.showerror("Error", "Please select input folder, CSV file, and output folder.")
            return
        
        payer = selected_payer.get()
        if not payer:
            messagebox.showerror("Error", "Please select a payer.")
            return
        
        start_time = time.time()

        status_var.set("Processing...")

        run_button.config(state=tk.DISABLED)

        def task():
            try:

                results = process_folder(
                    input_folder.get(),
                    csv_file.get(),
                    output_folder.get(),
                    payer = payer,
                    log_callback=log_message,
                    progress_callback=update_progress,
                    current_file_callback=update_current_file
                )

                generate_csv_log(results)

                root.after(0, lambda: status_var.set("Completed Successfully"))
            
                log_message("Processing completed successfully.")

                root.after(
                    0, lambda: messagebox.showinfo(
                        "Process Completed",
                        f"Processing completed successfully for payer: {payer}.\n\n"
                        f"CSV Log has been generated in the output folder. \n\n"
                        f"Processed files: {len(results)}\n"
                    )
                )
                
            except Exception as e:
                import traceback #Temporary
                root.after(0, lambda: status_var.set("Error During processing"))
                traceback.print_exc() # Temporary
                error_msg = traceback.format_exc() # Temporary
                print(error_msg) # Temporary
                log_message(error_msg)
                root.after(0, lambda msg = error_msg: messagebox.showerror("Error", msg))
            finally:

                root.after(0, lambda:run_button.config(state=tk.NORMAL))
                root.after(0, lambda: progress.configure(value = 100))
            
        threading.Thread(target=task, daemon= True).start()

    ### CSV LOG ###

    def generate_csv_log(results):
        now =datetime.now()
        filename = f"asignaciones_{now.strftime('%Y-%m-%d_%H-%M')}.csv"
        filepath = f"{output_folder.get()}/{filename}"

        with open(filepath, mode= "w", newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames =[
                "archivo", "patient", "dos", "collector", "fecha", "payer"
            ], delimiter=';' if locale.localeconv()["decimal_point"] == ',' else ',', extrasaction= "ignore")
            writer.writeheader()
            writer.writerows(results)
        log_message(f"CSV log generated: {filename}")

    ### UI Layout ###

    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    #title
    ttk.Label(
        main_frame,
        text="RPA Letter Mass Processor - Multi-Payer Support",
        font=("Helvetica", 16, "bold")
    ).pack(pady= (0, 20))

    # Input/Output Controls
    def build_row(label_text, var, command):
        row =ttk.Frame(main_frame)
        row.pack(fill= "x", pady=5)

        ttk.Label(row, text = label_text, width=18).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=var, width=40).pack(side="left", fill ="x", expand=True, padx=5)
        ttk.Button(row, text="Browse", command=command, width=10).pack(side="left")

    build_row("Assignations CSV:", csv_file, select_csv_file)
    build_row("Input Folder:", input_folder, select_input_folder)
    build_row("Output Folder:", output_folder, select_output_folder)

    # Payer Selection
    ttk.Separator(main_frame, orient = "horizontal").pack(fill="x", pady=15)

    ttk.Label(
        main_frame,
        text = "Select Payer:",
        font = ("Segoe UI", 12, "bold")
    ).pack(anchor="w", pady= (10, 5))

    # Frame for payer buttons
    payer_frame = ttk.Frame(main_frame)
    payer_frame.pack(fill="x", pady=10)

    # Notebook style for payer selection
    notebook = ttk.Notebook(payer_frame)
    notebook.pack(fill="both", expand=True)

    # Create a tab for each payer
    for payer in DEFAULT_PAYERS:
        tab = ttk.Frame(notebook, padding = 15)
        notebook.add(tab, text=payer)

        if payer == "Auto":
            description = (
                "Letters will be analyzed automatically."
                "This mode supports mixed payers but may be less accurate"
            )
        else:
            description = (
                f"PDF's will be processed using {payer} specific letter format."
            )

        ttk.Label(
            tab,
            text =f"Processing: {payer}",
            font= ("Segoe UI", 11)
        ).pack(pady=10)

        ttk.Label(
            tab,
            text = description,
            foreground="white"
        ).pack(pady=5)

    # Update the selected payer when the tab is changed
    def on_tab_change(event):
        selected_idx = notebook.index(notebook.select())
        selected_payer.set(DEFAULT_PAYERS[selected_idx])
        log_message(f"Selected Payer: {selected_payer.get()}")
        
        payer = selected_payer.get()

        if payer == "Auto":
            log_message("WARNING: Automatic mode is experimental")
            log_message("and may produce assignment or extraction errors than payer-specific processing")

    notebook.bind("<<NotebookTabChanged>>", on_tab_change)
    selected_payer.set(DEFAULT_PAYERS[0])  # Set default payer

    # Run button
    ttk.Separator(main_frame, orient= "horizontal").pack(fill="x", pady=15)

    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=10)

    run_button = ttk.Button(button_frame, text= "Start Processing", command=run, width=20, style="Accent.TButton")
    run_button.pack(side="left", padx=5)

    # Progress Bar
    progress = ttk.Progressbar(button_frame, mode="determinate", maximum=100)
    progress.pack(fill="x", padx=5)

    # Status Label
    status_var = tk.StringVar(value="Ready")
    progress_var = tk.StringVar(value ="Processed 0 / 0")
    eta_var = tk.StringVar(value="Time Remaining: Calculating...")
    ttk.Label(main_frame, textvariable=status_var, foreground="gray").pack()
    ttk.Label(main_frame, textvariable=progress_var).pack()
    ttk.Label(main_frame, textvariable=eta_var).pack()
    current_file_var = tk.StringVar(value="Current File: None")
    ttk.Label(main_frame, textvariable=current_file_var).pack()

    # Log Section
    ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)

    ttk.Label(
        main_frame,
        text = "Processing Log:",
        font = ("Segoe UI", 10, "bold")
    ).pack(anchor="w", pady=(10, 5))

    log_text = tk.Text(main_frame, height=12, bg="#1e1e1e", fg="#00ff00", font=("Courier", 9))
    log_text.pack(fill="both", expand=True, pady=(5, 0))

    # Scrollbar for log
    scrollbar = ttk.Scrollbar(log_text)
    scrollbar.pack(side="right", fill="y")
    log_text.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=log_text.yview)

    root.protocol(
        "WM_DELETE_WINDOW",
        lambda: close_application(root, launcher_root)
    )

    #root.mainloop()

if __name__ == "__main__":
    main()