# MR Letters Generator

A portable Windows application that assigns PDF letters to collectors based on a spreadsheet (CSV / XLSX) and information extracted from each PDF.  
Each PDF is copied into a sub-folder named after the **assigned collector** and renamed using the **patient name** and **Date of Service (DOS)**.

> Note: The app uses **Poppler** (via `pdf2image`) and optionally **Tesseract OCR** for fallback extraction when text cannot be read directly from the PDF.

---

## Features

| Feature | Description |
|---------|-------------|
| **Spreadsheet input** | Load assignments from `.csv`, `.xlsx`, or `.xls` |
| **PDF parsing** | Extract patient name and DOS from the PDF (fast text extraction first; OCR fallback if needed) |
| **Collector-based output folders** | `<output_dir>/<Collector_Name>/<PatientName_DOS>.pdf` |
| **Windows UI** | Simple Tkinter interface – no command line needed |
| **Portable executable** | PyInstaller build bundles the app and required assets into one folder |

---

## Spreadsheet Schema

The input file must contain the following columns (header row required, case-insensitive).  
Minimum required by the current code in `core/data_loader.py`:

| Column | Required | Description |
|--------|----------|-------------|
| `patient_name` | ✅ | Patient name used for matching (the app normalizes it internally) |
| `collector` | ✅ | Collector name for output folder assignment |

A ready-to-use sample file is provided: [`sample_input.csv`](sample_input.csv)

> Tip: Keep patient names consistent. The app uses fuzzy matching (RapidFuzz) to match extracted names to the spreadsheet.

---

## Output Structure

```
<output_directory>/
├── Maria_Garcia/
│   ├── John_Smith_01-15-2024.pdf
│   └── Jane_Doe_03-22-2024.pdf
├── Carlos_Rivera/
│   ├── Robert_Johnson_02-10-2024.pdf
│   └── Emily_Williams_04-05-2024.pdf
└── UNASSIGNED/
    └── Unknown_00-00-0000.pdf
```

---

## Running on Windows (portable build)

### Option 1 – Pre-built executable (recommended)

1. Download the latest `MR_Letters_Generator.zip` artifact from the [GitHub Actions page](../../actions).
2. Extract the zip to any folder.
3. Run **`MR_Letters_Generator.exe`** (inside the extracted folder).
4. The UI will open — no Python installation required.

> Important: Distribute/run the **entire folder**, not just the `.exe`. The build includes an `assets/` folder required at runtime.

### Option 2 – Run from source

**Requirements:** Python 3.9+ on Windows

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the UI
python main.py
```

---

## Using the UI

1. Click **Browse** next to **Input Folder** and select the folder containing your PDFs.
2. Click **Browse** next to **CSV File** and select your assignment `.csv`.
3. Click **Browse** next to **Output Folder** and select where results should be saved.
4. Click **Run Process**.
5. Progress and any errors are shown in the log panel.

A CSV log will also be generated in the output folder.

---

## Assets (Poppler / Tesseract)

The app expects these paths (relative to the application base directory):

- Poppler:
  - `assets/poppler/Library/bin`
- Tesseract (OCR fallback):
  - `assets/tesseract/tesseract.exe`
  - `assets/tesseract/tessdata/`

When running as a PyInstaller `.exe`, the code should resolve assets using `sys._MEIPASS` (frozen mode) so it can find bundled assets correctly.

---

## Building the portable executable (developers)

### 1) Install build dependencies

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 2) Clean previous builds (recommended)

**Command Prompt (Windows):**
```bat
rmdir /S /Q build
rmdir /S /Q dist
```

### 3) Build

```bash
pyinstaller build.spec
```

The portable folder will be created at:

- `dist/MR_Letters_Generator/`

Zip that folder and distribute it.

> Important: If users see errors like “A process in the process pool was terminated abruptly…”, it is commonly caused by missing bundled assets (Poppler/Tesseract) or Windows multiprocessing in frozen apps. Ensure your entrypoint calls `multiprocessing.freeze_support()` and that `assets/` is included in the final `dist/` folder.

---

## Project Structure

```
.
├── main.py                  # Entry point – launches the UI
├── config.py                # (reserved for future configuration)
├── requirements.txt
├── sample_input.csv         # Example spreadsheet
├── build.spec               # PyInstaller spec
├── app/
│   └── ui.py                # Tkinter user interface
├── core/
│   ├── data_loader.py       # CSV/XLSX parsing & validation
│   ├── processor.py         # Batch processing (ProcessPoolExecutor)
│   ├── file_manager.py      # File saving helpers
│   ├── extractor.py         # PDF text extraction + OCR fallback
│   ├── ocr.py               # Tesseract OCR wrapper
│   └── pdf_processor.py     # PDF-to-image helper (Poppler)
├── utils/
│   ├── helpers.py           # sanitize_filename()
│   └── logger.py            # Logging setup (if used)
└── assets/
    ├── poppler/             # Bundled Poppler binaries (Windows)
    └── tesseract/           # Bundled Tesseract + tessdata (if used)
```