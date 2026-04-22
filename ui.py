"""ui.py – Windows-friendly Tkinter front-end for the MR Letters Generator."""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from core.data_loader import load_assignments
from core.letter_generator import generate_letter
from utils.logger import setup_logger

logger = setup_logger()

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
BG = "#F0F4F8"
ACCENT = "#1F497D"
BTN_RUN = "#2E7D32"
BTN_RUN_FG = "#FFFFFF"
BTN_BROWSE = "#1565C0"
BTN_BROWSE_FG = "#FFFFFF"
LOG_BG = "#1E1E1E"
LOG_FG = "#D4D4D4"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MR Letters Generator")
        self.geometry("780x560")
        self.minsize(680, 480)
        self.configure(bg=BG)
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        # ---- Title bar ----
        title_frame = tk.Frame(self, bg=ACCENT)
        title_frame.pack(fill="x")
        tk.Label(
            title_frame,
            text="  MR Letters Generator",
            font=("Segoe UI", 14, "bold"),
            bg=ACCENT,
            fg="#FFFFFF",
            pady=8,
        ).pack(side="left")

        # ---- Main content frame ----
        content = tk.Frame(self, bg=BG, padx=20, pady=15)
        content.pack(fill="both", expand=True)

        # Input file row
        self._make_file_row(
            content,
            row=0,
            label="Input File (CSV / XLSX):",
            var_name="_input_var",
            browse_cmd=self._browse_input,
        )

        # Output directory row
        self._make_file_row(
            content,
            row=1,
            label="Output Directory:",
            var_name="_output_var",
            browse_cmd=self._browse_output,
            is_dir=True,
        )

        # Run button + progress bar
        run_frame = tk.Frame(content, bg=BG)
        run_frame.grid(row=2, column=0, columnspan=3, pady=12, sticky="ew")

        self._run_btn = tk.Button(
            run_frame,
            text="▶  Generate Letters",
            font=("Segoe UI", 11, "bold"),
            bg=BTN_RUN,
            fg=BTN_RUN_FG,
            relief="flat",
            padx=18,
            pady=6,
            cursor="hand2",
            command=self._on_run,
        )
        self._run_btn.pack(side="left")

        self._progress = ttk.Progressbar(
            run_frame, mode="indeterminate", length=420
        )
        self._progress.pack(side="left", padx=(20, 0))

        # Status label
        self._status_var = tk.StringVar(value="Ready.")
        tk.Label(
            content,
            textvariable=self._status_var,
            font=("Segoe UI", 9, "italic"),
            bg=BG,
            fg="#555555",
        ).grid(row=3, column=0, columnspan=3, sticky="w")

        # Log output
        tk.Label(
            content,
            text="Log output:",
            font=("Segoe UI", 9, "bold"),
            bg=BG,
            fg=ACCENT,
        ).grid(row=4, column=0, columnspan=3, sticky="w", pady=(8, 2))

        self._log_box = scrolledtext.ScrolledText(
            content,
            height=14,
            font=("Consolas", 9),
            bg=LOG_BG,
            fg=LOG_FG,
            insertbackground=LOG_FG,
            state="disabled",
            relief="flat",
            borderwidth=1,
        )
        self._log_box.grid(
            row=5, column=0, columnspan=3, sticky="nsew", pady=(0, 6)
        )
        content.rowconfigure(5, weight=1)
        content.columnconfigure(1, weight=1)

    def _make_file_row(self, parent, row, label, var_name, browse_cmd, is_dir=False):
        tk.Label(
            parent,
            text=label,
            font=("Segoe UI", 10),
            bg=BG,
            fg="#333333",
            anchor="w",
        ).grid(row=row, column=0, sticky="w", pady=6)

        var = tk.StringVar()
        setattr(self, var_name, var)

        entry = tk.Entry(
            parent,
            textvariable=var,
            font=("Segoe UI", 10),
            width=52,
            relief="solid",
            borderwidth=1,
        )
        entry.grid(row=row, column=1, sticky="ew", padx=(8, 8), pady=6)

        tk.Button(
            parent,
            text="Browse…",
            font=("Segoe UI", 9),
            bg=BTN_BROWSE,
            fg=BTN_BROWSE_FG,
            relief="flat",
            padx=6,
            pady=3,
            cursor="hand2",
            command=browse_cmd,
        ).grid(row=row, column=2, sticky="w", pady=6)

    # ------------------------------------------------------------------
    # Button callbacks
    # ------------------------------------------------------------------
    def _browse_input(self):
        path = filedialog.askopenfilename(
            title="Select input spreadsheet",
            filetypes=[
                ("Spreadsheet files", "*.csv *.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self._input_var.set(path)

    def _browse_output(self):
        path = filedialog.askdirectory(title="Select output directory")
        if path:
            self._output_var.set(path)

    def _on_run(self):
        input_file = self._input_var.get().strip()
        output_dir = self._output_var.get().strip()

        if not input_file:
            messagebox.showerror("Missing input", "Please select an input CSV/XLSX file.")
            return
        if not output_dir:
            messagebox.showerror(
                "Missing output", "Please select an output directory."
            )
            return

        self._clear_log()
        self._run_btn.config(state="disabled")
        self._progress.start(10)
        self._status_var.set("Processing…")

        thread = threading.Thread(
            target=self._process_thread,
            args=(input_file, output_dir),
            daemon=True,
        )
        thread.start()

    # ------------------------------------------------------------------
    # Background processing
    # ------------------------------------------------------------------
    def _process_thread(self, input_file, output_dir):
        """Run in a background thread so the UI stays responsive."""
        try:
            self._log(f"Loading assignments from: {input_file}")
            assignments, skipped = load_assignments(input_file)
            self._log(
                f"Loaded {len(assignments)} assignment(s)."
                + (f" ({skipped} row(s) skipped – missing required fields)" if skipped else "")
            )

            success = 0
            errors = 0
            total = len(assignments)
            for i, assignment in enumerate(assignments, 1):
                patient = assignment.get("patient_name", "?")
                collector = assignment.get("collector", "?")
                dos = assignment.get("dos", "?")
                try:
                    out_path = generate_letter(assignment, output_dir)
                    self._log(
                        f"[{i}/{total}] ✓  {patient} | DOS: {dos} | Collector: {collector}\n"
                        f"        → {out_path}"
                    )
                    success += 1
                except Exception as exc:
                    self._log(f"[{i}/{total}] ✗  {patient}: {exc}")
                    logger.error("Error generating letter for %s: %s", patient, exc)
                    errors += 1

            summary = f"Finished – {success} letter(s) generated"
            if errors:
                summary += f", {errors} error(s)"
            summary += f". Output: {output_dir}"
            self._log(summary)
            self.after(0, self._on_done, success, errors, summary)

        except Exception as exc:
            msg = str(exc)
            self._log(f"ERROR: {msg}")
            logger.exception("Unexpected error")
            self.after(0, lambda: messagebox.showerror("Error", msg))
            self.after(0, self._on_reset)

    def _on_done(self, success, errors, summary):
        self._progress.stop()
        self._run_btn.config(state="normal")
        self._status_var.set(summary)
        if errors == 0:
            messagebox.showinfo(
                "Success",
                f"All {success} letter(s) generated successfully!\n\nOutput folder:\n{self._output_var.get()}",
            )
        else:
            messagebox.showwarning(
                "Done with errors",
                f"{success} letter(s) generated, {errors} error(s).\nCheck the log for details.",
            )

    def _on_reset(self):
        self._progress.stop()
        self._run_btn.config(state="normal")
        self._status_var.set("Ready.")

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------
    def _log(self, message):
        """Append *message* to the log box (thread-safe via after())."""
        self.after(0, self._append_log, message)

    def _append_log(self, message):
        self._log_box.config(state="normal")
        self._log_box.insert(tk.END, message + "\n")
        self._log_box.see(tk.END)
        self._log_box.config(state="disabled")

    def _clear_log(self):
        self._log_box.config(state="normal")
        self._log_box.delete("1.0", tk.END)
        self._log_box.config(state="disabled")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
