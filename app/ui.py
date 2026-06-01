# ============================================================================
# MR Letters Generator
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
import threading
import csv
from datetime import datetime
from core.processor import process_folder
import locale

#default list of payers, can be extended if needed
DEFAULT_PAYERS = ["UMR","Optum", "Aetna", "Cigna", "BCBS TX", "Florida Blue"]

def main():
    root =tk.Tk()
    root.title("RPA Letter Mass Processor - Multi-Payer Support")
    root.geometry("850x700")
    root.resizable(True, True)
    
    style = ttk.Style()
    try:
        root.tk.call("source", "forest-dark.tcl")
        style.theme_use("forest-dark")
    except:
        pass

    input_folder = tk.StringVar()
    csv_file = tk.StringVar()
    output_folder = tk.StringVar()
    selected_payer = tk.StringVar(value=DEFAULT_PAYERS[0])

    # ----------------- UI Build -----------------
    
    ### LOG UI ###

    def log_message(msg):
        log_text.insert(tk.END, msg + "\n")
        log_text.see(tk.END)

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

    def run():
        if not input_folder.get() or not csv_file.get() or not output_folder.get():
            messagebox.showerror("Error", "Please select input folder, CSV file, and output folder.")
            return
        
        payer = selected_payer.get()
        if not payer:
            messagebox.showerror("Error", "Please select a payer.")
            return
        
        status_var.set("Processing...")
        progress.start()
        run_button.config(state=tk.DISABLED)

        def task():
            try:
                results = process_folder(
                    input_folder.get(),
                    csv_file.get(),
                    output_folder.get(),
                    payer = payer,
                    log_callback=log_message
                )

                generate_csv_log(results)

                status_var.set("Completed Successfully")
                log_message("Processing completed successfully.")

                messagebox.showinfo(
                    "Process Completed",
                    f"Processing completed successfully for payer: {payer}.\n\n"
                    f"CSV log has been generated in the output folder.\n\n"
                    f"Processed files: {len(results)}\n"
                )

            except Exception as e:
                status_var.set("Error during processing")
                log_message(f"Error occurred: {str(e)}")
                root.after(0, lambda: messagebox.showerror("Error", f"An error occurred during processing:\n\n {str(e)}"))
            finally:
                progress.stop()
                run_button.config(state=tk.NORMAL)
            
        threading.Thread(target=task).start()

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

        ttk.Label(
            tab,
            text =f"Processing: {payer}",
            font= ("Segoe UI", 11)
        ).pack(pady=10)

        ttk.Label(
            tab,
            text =f"PDF's will be processed using {payer} specific Letter format.",
            foreground="gray"
        ).pack(pady=5)

    # Update the selected payer when the tab is changed
    def on_tab_change(event):
        selected_idx = notebook.index(notebook.select())
        selected_payer.set(DEFAULT_PAYERS[selected_idx])
        log_message(f"Selected Payer: {selected_payer.get()}")

    notebook.bind("<<NotebookTabChanged>>", on_tab_change)
    selected_payer.set(DEFAULT_PAYERS[0])  # Set default payer

    # Run button
    ttk.Separator(main_frame, orient= "horizontal").pack(fill="x", pady=15)

    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=10)

    run_button = ttk.Button(button_frame, text= "Start Processing", command=run, width=20, style="Accent.TButton")
    run_button.pack(side="left", padx=5)

    # Progress Bar
    progress = ttk.Progressbar(button_frame, mode="indeterminate")
    progress.pack(fill="x", padx=5)

    # Status Label
    status_var = tk.StringVar(value="Ready")
    ttk.Label(main_frame, textvariable=status_var, foreground="gray").pack()

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

    root.mainloop()

if __name__ == "__main__":
    main()