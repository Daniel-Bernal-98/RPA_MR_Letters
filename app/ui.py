import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import csv
from datetime import datetime
from core.processor import process_folder


def main():
    root = tk.Tk()
    root.title("RPA PDF Organizer")
    root.geometry("700x500")
    root.resizable(False, False)

    style = ttk.Style()
    try:
        style.theme_use('vista')
    except:
        pass

    input_folder = tk.StringVar()
    csv_file = tk.StringVar()
    output_folder = tk.StringVar()

    # ---------- LOG UI ----------
    def log_message(msg):
        log_text.insert(tk.END, msg + "\n")
        log_text.see(tk.END)

    # ---------- FUNCIONES ----------
    def select_input():
        folder = filedialog.askdirectory()
        if folder:
            input_folder.set(folder)

    def select_csv():
        file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file:
            csv_file.set(file)

    def select_output():
        folder = filedialog.askdirectory()
        if folder:
            output_folder.set(folder)

    def run():
        if not input_folder.get() or not csv_file.get() or not output_folder.get():
            messagebox.showerror("Error", "Please complete all fields")
            return

        status_var.set("Processing...")
        progress.start()

        def task():
            try:
                results = process_folder(
                    input_folder.get(),
                    csv_file.get(),
                    output_folder.get(),
                    log_callback=log_message
                )

                generate_csv_log(results)

                status_var.set("Completed successfully ✔")
                log_message("✔ Proceso completado")

                messagebox.showinfo("Success", "Processing completed")

            except Exception as e:
                status_var.set("Error occurred ❌")
                log_message(f"ERROR: {str(e)}")
                messagebox.showerror("Error", str(e))

            finally:
                progress.stop()

        threading.Thread(target=task, daemon=True).start()

    # ---------- CSV LOG ----------
    def generate_csv_log(results):
        now = datetime.now()
        filename = f"asignaciones_{now.strftime('%Y-%m-%d_%H-%M-%S')}.csv"

        filepath = f"{output_folder.get()}/{filename}"

        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "archivo", "patient", "dos", "collector", "fecha"
            ])
            writer.writeheader()
            writer.writerows(results)

        log_message(f"Log CSV generado: {filename}")

    # ---------- UI ----------
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)

    ttk.Label(
        main_frame,
        text="RPA PDF Organizer",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(0, 10))

    def build_row(label_text, var, command):
        row = ttk.Frame(main_frame)
        row.pack(fill="x", pady=5)

        ttk.Label(row, text=label_text, width=15).pack(side="left")
        ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(row, text="Browse", command=command).pack(side="left")

    build_row("Input Folder:", input_folder, select_input)
    build_row("CSV File:", csv_file, select_csv)
    build_row("Output Folder:", output_folder, select_output)

    ttk.Button(main_frame, text="Run Process", command=run).pack(pady=10)

    progress = ttk.Progressbar(main_frame, mode='indeterminate')
    progress.pack(fill="x", pady=5)

    status_var = tk.StringVar(value="Ready")
    ttk.Label(main_frame, textvariable=status_var).pack()

    #LOG VISUAL
    ttk.Label(main_frame, text="Log:").pack(anchor="w", pady=(10, 0))

    log_text = tk.Text(main_frame, height=10, bg="#1e1e1e", fg="#00ff00")
    log_text.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()