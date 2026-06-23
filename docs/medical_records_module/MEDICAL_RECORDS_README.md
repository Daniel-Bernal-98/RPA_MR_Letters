# Automatic Letter Reader for workload Assignations

## Overview

Automatic Letter Reader for workload Assignations is a Windows desktop application designed to automate the processing and assignment of Medical Records (MR) request letters received from multiple insurance payers.

The application:

* Reads PDF letters from a selected folder.
* Extracts patient information and dates from each document.
* Matches patients against an assignment spreadsheet.
* Assigns each letter to the correct collector.
* Renames and organizes files automatically.
* Flags old letters based on configurable age thresholds.
* Generates a processing log for auditing and troubleshooting.

The system supports both direct PDF text extraction and OCR fallback for scanned or image-based documents.

---

# Key Features

## Automatic Payer Detection

The application can automatically detect the payer from PDF content without requiring manual selection.

Supported payers:

* Florida Blue
* Aetna
* Cigna
* BCBS TX (Blue Cross Blue Shield of Texas)
* Optum / United Healthcare / UHC
* UMR

Falls back to default extraction rules if payer cannot be determined.

---

## Multi-Payer Support

Supports payer-specific extraction rules through configurable profiles.

Currently supported:

* UMR / Optum
* Aetna
* BCBS
* Cigna
* Default profile

Each payer can define:

* OCR settings
* Regex extraction patterns
* Search zones
* OCR thresholds
* Layout-specific logic

---

## Intelligent Extraction Pipeline

The application uses a layered extraction strategy:

### 1. Fast Text Extraction

Attempts direct text extraction from PDF pages.

Advantages:

* Extremely fast
* High accuracy
* Minimal resource usage

### 2. OCR Fallback

If required data is not found through text extraction:

* Converts PDF pages to images
* Applies payer-specific OCR preprocessing
* Extracts patient and date information from configured search zones

---

## Multi-Page Document Support

The system scans all pages of a PDF until required information is found.

Supported for:

* Patient extraction
* Date of Service (DOS) extraction
* Issue Date extraction
* OCR fallback processing

---

## Automatic Collector Assignment

Patients are matched against an assignment spreadsheet using:

* Exact matching
* Name normalization
* Fuzzy matching fallback

Example:

```text
MICHAEL COTONE
```

can match:

```text
COTONE_MICHAEL
```

without requiring manual intervention.

---

## Old Letter Detection

Letters can be automatically classified based on age.

Configurable threshold:

```text
365 days
```

Example:

```text
Issue Date: 2024-01-01
Today: 2025-06-01
```

Result:

```text
Old Letter = True
```

---

## Processing Logs

At the end of each run the application generates a CSV log including:

* File name
* Patient
* DOS
* Collector
* Payer
* Issue date
* Old letter status

This provides complete auditability of every processed document.

---

# Project Structure

```text
RPA_MR_Letters/
│
├── app/
│   └── ui.py
│
├── core/
│   ├── data_loader.py
│   ├── extractor.py
│   ├── file_manager.py
│   ├── ocr.py
│   ├── payer_config.py
│   ├── payer_detector.py
│   ├── pdf_processor.py
│   └── processor.py
│
├── utils/
│   ├── helpers.py
│   └── logger.py
│
├── assets/
│   ├── poppler/
│   └── icons/
│
├── main.py
│
└── README.md
```

---

# Spreadsheet Requirements

The assignment spreadsheet must contain:

| Column       | Required |
| ------------ | -------- |
| patient_name | Yes      |
| collector    | Yes      |

Example:

| patient_name         | collector     |
| -------------------- | ------------- |
| LastName1_FirstName1 | COLLECTOR_ONE |
| LastName2_FirstName2 | COLLECTOR_TWO |

---

# Output Structure

Example:

```text
Output/
│
├── COLLECTOR_ONE/
│   ├── LastName1_FirstName1_04-15-2025.pdf
│   └── LastName2_FirstName2_03-12-2025.pdf
│
├── COLLECTOR_TWO/
│   └── LastName3_FirstName3_05-08-2025.pdf
│
└── UNASSIGNED/
    └── UNKNOWN_00-00-0000.pdf
```

---

# Payer Configuration

Payer-specific settings are stored in:

```text
core/payer_config.py
```

Configuration categories:

## OCR Configuration

Defines:

* Tesseract PSM
* OCR Engine Mode
* Contrast
* Thresholding
* Blur settings

## Text Patterns

Regex patterns used for direct extraction:

* Patient name
* Date of Service
* Alternate layouts

## OCR Zones

Defines where the application searches for:

* Patient information
* Issue dates

Zones are expressed as percentages of page dimensions.

---

# Installation

## Requirements

* Python 3.10+
* Windows 10/11

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Application

```bash
python main.py
```

---

# Building the Executable

The project is designed to be packaged with PyInstaller.

Example:

```bash
pyinstaller --onefile --windowed main.py
```

The final build must include:

```text
assets/
```

particularly:

```text
assets/poppler/
```

which is required for PDF-to-image conversion.

---

# OCR Dependencies

The application relies on:

## Poppler

Used by:

```python
pdf2image
```

for PDF page rendering.

Location:

```text
assets/poppler/
```

---

## EasyOCR / Tesseract-Based Processing

Used when direct text extraction is insufficient.

Capabilities:

* Scanned documents
* Faxed documents
* Low-quality PDFs
* Multi-page records

---

# Processing Workflow

```text
PDF
 ↓
Fast Text Extraction
 ↓
Patient Found?
DOS Found?
 ↓
Yes
 ↓
Spreadsheet Matching
 ↓
Collector Assignment
 ↓
File Rename
 ↓
Output Folder
```

If extraction fails:

```text
PDF
 ↓
OCR Fallback
 ↓
Patient Extraction
 ↓
DOS Extraction
 ↓
Matching
 ↓
Output
```

---

# Generated Logs

Each execution produces:

```text
asignaciones_YYYY-MM-DD_HH-MM.csv
```

Including:

* Original file
* Extracted patient
* DOS
* Collector
* Payer
* Issue date
* Old letter status

---

# Troubleshooting

## OCR Not Working

Verify:

```text
assets/poppler/
```

exists and contains Poppler binaries.

---

## All Files Assigned to UNASSIGNED

Verify:

* Spreadsheet columns are correct.
* Patient names exist in the spreadsheet.
* Payer profile is correctly selected.
* OCR extraction is working.

---

## DOS Returns 00-00-0000

Possible causes:

* Incorrect payer regex.
* DOS not present on scanned page.
* OCR search zone requires adjustment.

Review:

```text
core/payer_config.py
```

---

# Future Enhancements

Potential future improvements:

* OCR confidence scoring
* Visual zone editor
* Batch profile management
* JSON/YAML payer configuration
* Dashboard reporting
* Processing statistics

---

# Author

Daniel Bernal

Medical Records Automation Project

Built to streamline payer letter assignment workflows and reduce manual processing time.

## License

This software is proprietary and confidential.

Copyright (c) 2026 ABA Centers of America.
All Rights Reserved.

This application is intended solely for internal use by authorized personnel of ABA Centers of America. Unauthorized distribution, modification, reproduction, or disclosure is prohibited.