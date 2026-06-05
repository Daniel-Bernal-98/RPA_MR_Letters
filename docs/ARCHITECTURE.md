# MR Letters Automation
## System Architecture

---

## High Level Flow

```text
User Interface
        │
        ▼
Processor
        │
        ▼
PDF Extraction
        │
        ▼
OCR Engine
        │
        ▼
Patient Matching
        │
        ▼
Collector Assignment
        │
        ▼
Output Generation
```

---

## Project Structure

### app/

Contains the graphical user interface.

```text
app/
└── ui.py
```

Responsibilities:

- User interaction
- Configuration selection
- Progress display
- Logging display

---

### core/

Contains all processing logic.

#### processor.py

Main orchestration layer.

Responsibilities:

- Batch processing
- Payer routing
- Workflow control

---

#### extractor.py

Document extraction engine.

Responsibilities:

- Patient extraction
- DOS extraction
- Issue date extraction
- OCR fallback

---

#### ocr.py

OCR engine.

Responsibilities:

- Image preprocessing
- Tesseract integration
- OCR data extraction

---

#### pdf_processor.py

PDF rendering.

Responsibilities:

- Convert PDF pages to images
- Poppler integration

---

#### payer_config.py

Payer configuration repository.

Responsibilities:

- OCR settings
- Search zones
- Thresholds
- Extraction parameters

---

#### payer_detector.py

Automatic payer identification.

Current Status:

Development in progress.

Responsibilities:

- Signature detection
- Automatic payer selection

---

#### file_manager.py

Output management.

Responsibilities:

- Folder creation
- File movement
- File renaming

---

### utils/

Support utilities.

#### logger.py

Application logging.

#### helpers.py

Shared utility functions.

---

### assets/

Contains runtime dependencies.

```text
assets/
├── icon.ico
├── forest-dark.tcl
├── poppler/
└── tesseract/
```

---

## OCR Architecture

```text
PDF
 ↓
Poppler
 ↓
Image
 ↓
Preprocessing
 ↓
Tesseract OCR
 ↓
Structured OCR Data
 ↓
Extraction Logic
```

---

## Supported Payers

Current Production Ready:

- UMR
- Optum
- BCBS TX
- Florida Blue
- Aetna
- Cigna

---

## Future Architecture

Planned:

- Automatic Processing
- Mixed Payer Processing
- Generic Extraction Engine
- Unknown Format Detection