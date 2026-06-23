# Correspondence Automation

This file contains ONLY the files that are unique for the module, this module uses the same OCR system, assets that the Medical Records Module uses.

This module is not meant to assign documents to a collector, instead, this module only scans documents and classifies them by payer, location, patient and other requests not related to claims.

---

## System Architecture

```text
User Interface
        │
        ▼
Correspondence Processor
        │
        ▼
Payer Detection
        │
        ▼
Text Extraction
        │
        ▼
OCR Fallback (if required)
        │
        ▼
Patient Extraction
        │
        ▼
DOS Extraction
        │
        ▼
State Extraction
        │
        ▼
Classification Engine
        │
        ▼
File Naming Engine
        │
        ▼
Output Generation
```

---

## Business Workflow

```text
PDF
 ↓
Detect Payer
 ↓
Extract Text
 ↓
Extract Patient(s)
 ↓
Extract DOS
 ↓
Extract Facility State
 ↓
Determine Classification

 ├─ Single Patient
 ├─ Multi Patient
 └─ Miscellaneous

 ↓
Generate Standardized Filename
 ↓
Save Output File
```

---

## Module Structure

### app/

Contains the graphical user interface.

```text
app/
└── ui.py
```

Responsibilities:

- Folder Selection
- Processing controls 
- Progress Tracking
- Processing logs
- User Feedback

---

### core/

Contains all correspondence processing logic.

#### correspondence_processor.py

Main orchestration layer.

Responsibilities:

- Batch processing
- Payer routing
- Extraction workflow control
- Classification decisions
- Filename generation
- Output creation

---

#### correspondence_extractor.py

Document extraction engine.

Responsibilities:

- Payer extraction using signatures
- Patient extraction
- DOS extraction
- State extraction
- Multi-patient detection
- Generic fallback extraction

---

#### payer_signatures.py

Payer signatures list.

Responsibilities:

- Simplify payer supporting using a dictionary with payer signatures that allows to improve the payer recognition/addition.

---

## Extraction Architecture

This module uses a layered extraction strategy.

---

### Layer 1 - Direct Text Extraction

Primary extraction method.

PDF
 ↓
Embedded Text
 ↓
Regex Extraction

Advantages:

- Fastest method
- Highest accuracy
- Minimal resource usage

---

### Layer 2 - OCR Fallback

Used only when required data cannot be extracted using direct extraction.

PDF
 ↓
Image Conversion
 ↓
OCR
 ↓
Regex Extraction

Supported for:

- Scanned documents
- Faxed Correspondence
- Image only PDFs

---

### OCR Optimization

To improve performance, OCR is executed only when necessary.

The module:

- Attempts text extraction first.
- Reuses extracted text whenever possible.
- Avoids duplicate OCR execution.

Benefits:

- Faster processing
- Lower CPU usage
- Improved batch performance

---

## Payer Detection Architecture

```text
Document Text
 ↓
Signature Scan
 ↓
Known Payer Match?
      │
      ├─ Yes → Route to Payer Logic
      │
      └─ No → UNKNOWN_PAYER
```

Detection is based on configurable Payer signatures on *payer_signatures.py*

---

## Patient Extraction Architecture

The module searches for common healthcare patterns using RegEx.

Examples:

```text
- Patient Name:
- Patient:
- Name:
- Confidential health plan information for:
```

This extraction engine performs:

- Cleanup
- OCR Correction
- Invalid patient filtering
- Duplicate patient elimination

---

## DOS Extraction Architecture

The module searches for healthcare-specific date patterns

Examples:

```
- DOS
- Date of Service
- Date(s) of Service
- Service Date
- Service from Date
```

Fall back extraction supports payer-specific layouts.

---

## State Extraction Architecture

The module attempts facility identification using:

### Method 1

````
ABA Centers of Pennsylvania -> PA
````
### Method 2

````
Texas ABA Centers LLC -> TX
````

### Method 3

Facility address extraction, this method is only used when the facility names are not available. The extraction engine evaluates multiple strategies sequentially until a state is identified.

---

## Classification Engine

Documents are classified into three categories.

### Single Patient

Conditions:
- One patient detected
- Valid DOS Found

Output:

````
PAYER_STATE_PATIENT_DOS.pdf
````

### Multi Patient

Conditions:

- More than one unique patient detected

Output:

````
YEAR_PAYER_STATE_MULTI_PATIENTS.pdf
````

Rules:

- DOS Omitted from filename.
- Oldest valid claim year may be included.
- Only claim dates between 1 and 3 years old are eligible for historical year classification.
- Older dates are ignored to avoid OCR-related false positives and inactive claims.

---

### Miscellaneous

Conditions:

- No valid DOS found or no identifiable patient claim.

Output:

````
PAYER_STATE_MISCELLANEOUS.pdf
````

---

## File Naming Engine

Standard naming convention:

### Single Patient

``PAYER_STATE_PATIENT_DOS.pdf``

### Multi Patient

``YEAR_PAYER_STATE_MULTI_PATIENTS.pdf``

### Miscellaneous

``PAYER_STATE_MISCELLANEOUS.pdf``

---

## Error Handling

The module gracefully handles_

- Missing Patients
- Missing DOS
- Unknown Payers
- OCR Failures
- Corrupted PDFs
- Duplicate filenames
- Missing facility information

Fallback values:

````
UNKOWN_PAYER
UNKOWN_PATIENT
UNK -> State could not be identified.
00-00-0000 -> No valid DOS found
````

---

## Duplicate Filename Handling

When a generated filename already exists, the module automatically appends a numeric suffix.

Example:

Anthem_COA_PATIENT_1_03-10-2025.pdf

Anthem_COA_PATIENT_1_03-10-2025_1.pdf

Anthem_COA_PATIENT_1_03-10-2025_2.pdf

## Current Production Features

- Automatic payer detection based on payer signature-based detection
- Multi-payer processing
- Generic extraction engine
- OCR fallback
- State extraction
- Multi-patient detection
- Miscellaneous classification
- Historical claim year detection
- Duplicate filename prevention
- OCR optimization

---

## Performance

This module's objective is to reduce the manual work while separating different correspondence received, in order to have a base point the benchmark is the current time to process the documents manually.

### Manual Processing

``71`` Documents ~ ``90`` Minutes

### Automated Processing

``71`` Documents ~ ``9`` Minutes

Resulting in an approximate improvement of ``10x`` faster processing by using the module.

## Author

Daniel Bernal

Correspondence Automation Project

Built to standardize correspondence processing, improve classification accuracy, and reduce manual document handling.