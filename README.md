# MR Letters Generator

A portable Windows application that generates Medical Records (MR) request letters driven by a spreadsheet (CSV / XLSX).  
Each letter is saved as a `.docx` file named after the **patient name** and **Date of Service (DOS)**, inside a sub-folder named after the **assigned collector**.

---

## Features

| Feature | Description |
|---------|-------------|
| **Spreadsheet input** | Load assignments from `.csv`, `.xlsx`, or `.xls` |
| **Automatic letter generation** | Creates formatted `.docx` letters via `python-docx` |
| **Collector-based output folders** | `<output_dir>/<Collector_Name>/<PatientName_DOS>.docx` |
| **Windows UI** | Simple Tkinter interface – no command line needed |
| **Portable executable** | PyInstaller build bundles everything into one folder |

---

## Spreadsheet Schema

The input file must contain the following columns (header row required, case-insensitive):

| Column | Required | Description |
|--------|----------|-------------|
| `patient_name` | ✅ | Full name of the patient |
| `dos` | ✅ | Date of Service (e.g. `01/15/2024` or `2024-01-15`) |
| `collector` | ✅ | Name of the collector assigned to work on the letter |
| `claim_number` | ☐ | Insurance claim / reference number |
| `insurance_name` | ☐ | Insurance company name |
| `provider_name` | ☐ | Healthcare provider or facility name |
| `npi` | ☐ | National Provider Identifier |
| `address` | ☐ | Patient mailing address |

A ready-to-use sample file is provided: [`sample_input.csv`](sample_input.csv)

---

## Output Structure

```
<output_directory>/
├── Maria_Garcia/
│   ├── John_Smith_01-15-2024.docx
│   └── Jane_Doe_03-22-2024.docx
├── Carlos_Rivera/
│   ├── Robert_Johnson_02-10-2024.docx
│   └── Emily_Williams_04-05-2024.docx
└── Linda_Chen/
    └── Michael_Brown_12-01-2023.docx
```

---

## Running on Windows (portable build)

### Option 1 – Pre-built executable (recommended)

1. Download the latest `MR_Letters_Generator.zip` artifact from the [GitHub Actions Releases](../../actions).
2. Extract the zip to any folder.
3. Double-click **`MR_Letters_Generator.exe`** (inside the `dist/MR_Letters_Generator/` folder).
4. The UI will open — no Python installation required.

### Option 2 – Run from source

**Requirements:** Python 3.9+ on Windows

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the UI
python main.py
```

### Using the UI

1. Click **Browse…** next to *Input File* and select your `.csv` or `.xlsx` spreadsheet.
2. Click **Browse…** next to *Output Directory* and choose (or create) the folder where letters should be saved.
3. Click **▶ Generate Letters**.
4. Progress and any errors are shown in the log panel.
5. When complete a success dialog will confirm how many letters were generated.

---

## Building the portable executable (developers)

Install build dependencies:

```bash
pip install pyinstaller
pip install -r requirements.txt
```

Build:

```bash
pyinstaller build.spec
```

The portable folder will be created at `dist/MR_Letters_Generator/`.  
Zip it and distribute.

A GitHub Actions workflow (`.github/workflows/build.yml`) automates this on every push to `main`.

---

## Project Structure

```
.
├── main.py                  # Entry point – launches the UI
├── ui.py                    # Tkinter user interface
├── config.py                # (reserved for future configuration)
├── requirements.txt
├── sample_input.csv         # Example spreadsheet
├── build.spec               # PyInstaller spec
├── core/
│   ├── data_loader.py       # CSV/XLSX parsing & validation
│   ├── letter_generator.py  # .docx letter generation
│   ├── file_manager.py      # File saving helpers
│   ├── extractor.py         # Legacy OCR text extraction
│   ├── ocr.py               # EasyOCR wrapper
│   └── pdf_processor.py     # PDF-to-image helper
├── utils/
│   ├── helpers.py           # sanitize_filename()
│   └── logger.py            # Logging setup
└── assets/
    └── poppler/             # Bundled Poppler binaries (Windows)
```
