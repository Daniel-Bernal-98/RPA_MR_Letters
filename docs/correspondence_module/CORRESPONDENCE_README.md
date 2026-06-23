# Correspondence Processing Module

## Overview

The Correspondence Processing Module is designed to automate the classification, extraction, and organization of insurance payer correspondence received by ABA Centers.

Unlike the MR Letters module, which focuses on workload assignment and collector distribution, the Correspondence module focuses on identifying, classifying, and renaming payer correspondence using standardized business rules.

The module automatically:

* Detects the payer.
* Extracts patient information.
* Extracts Date of Service (DOS).
* Identifies facility state information.
* Detects multi-patient correspondence.
* Identifies miscellaneous/non-claim correspondence.
* Renames documents according to business naming conventions.
* Generates processing logs.

---

# Business Objective

The purpose of this module is to reduce the manual effort required to review, classify, and organize incoming payer correspondence.

The system standardizes document naming and classification while maintaining consistency across different payer formats.

---

# Supported Payers

Current payer signatures include:

* Anthem
* BCBS Texas
* Horizon / BCBS New Jersey
* AmeriHealth
* Highmark
* Molina
* Cigna
* UnitedHealthcare
* Optum
* UMR
* Regence BlueShield

Additional payers can be added through payer signature configuration.

---

# Classification Types

## Single Patient

Correspondence associated with a single patient and a valid DOS.

Example:

```text
Anthem_COA_PATIENT NAME_03-10-2025.pdf
```

---

## Multi Patient

Correspondence containing multiple patients and/or multiple claims.

Example:

```text
2024_Anthem_COA_MULTI_PATIENTS.pdf
```

Business Rules:

* Multiple unique patients detected.
* DOS removed from filename.
* Oldest valid claim year may be included when applicable.

---

## Miscellaneous

Documents not associated with a patient claim.

Examples:

* General communications
* Transportation notices
* Administrative correspondence
* Non-claim documents

Example:

```text
PAYER_STATE_MISCELLANEOUS.pdf
```

Business Rules:

* No valid DOS found.
* No patient claim identified.

---

# Extraction Strategy

The module uses a layered extraction approach.

## Fast Text Extraction

The application first attempts direct PDF text extraction.

Benefits:

* Fastest processing method.
* Highest accuracy when embedded text exists.
* Minimal resource consumption.

---

## OCR Fallback

When required information cannot be extracted directly:

* PDF pages are converted to images.
* OCR is applied.
* Extraction patterns are re-executed.

Supported for:

* Scanned correspondence.
* Faxed documents.
* Image-based PDFs.

---

# Patient Extraction

Patient names are extracted using multiple payer-independent patterns.

The system supports:

* Patient Name
* Patient:
* Name:
* Confidential Health Plan Information For:

Additional cleanup logic removes:

* Member ID references
* HCID references
* OCR artifacts
* Layout-specific noise

---

# DOS Extraction

The module searches for common healthcare date patterns, including:

* DOS
* Date of Service
* Date(s) of Service
* Service Date
* Service From Date

Fallback extraction is available for payer-specific layouts.

---

# Facility State Identification

The module attempts to identify the servicing ABA facility using:

1. ABA Centers of <State>
2. <State> ABA Centers LLC
3. Facility address extraction

Examples:

```text
ABA Centers of Pennsylvania
→ PA
```

```text
Texas ABA Centers LLC
→ TX
```

The extracted state is included in the generated filename whenever available.

---

# File Naming Convention

## Single Patient

```text
PAYER_STATE_PATIENT_DOS.pdf
```

Example:

```text
BCBS_TX_PATIENT NAME_01-25-2026.pdf
```

---

## Multi Patient

```text
YEAR_PAYER_STATE_MULTI_PATIENTS.pdf
```

Example:

```text
2024_Anthem_COA_MULTI_PATIENTS.pdf
```

---

## Miscellaneous

```text
PAYER_STATE_MISCELLANEOUS.pdf
```

Example:

```text
OPTUM_PA_MISCELLANEOUS.pdf
```

---

# OCR Optimization

The module avoids redundant OCR execution by reusing previously extracted text whenever possible.

Benefits:

* Faster processing.
* Reduced CPU usage.
* Improved batch performance.

---

# Processing Workflow

```text
PDF
 ↓
Payer Detection
 ↓
Patient Extraction
 ↓
DOS Extraction
 ↓
State Extraction
 ↓
Classification
 ↓
File Rename
 ↓
Output
```

If direct extraction fails:

```text
PDF
 ↓
OCR Fallback
 ↓
Reprocessing
 ↓
Classification
 ↓
Output
```

---

# Performance

Current benchmark:

Manual Processing

* 71 documents
* Approximately 90 minutes

Automated Processing

* 71 documents
* Approximately 9 minutes

Approximate improvement:

* 10x faster than manual processing

---

# Author

Daniel Bernal

Correspondence Automation Project

Built to reduce manual correspondence processing effort and improve classification consistency.

## License

This software is proprietary and confidential.

Copyright (c) 2026 ABA Centers of America.
All Rights Reserved.

This application is intended solely for internal use by authorized personnel of ABA Centers of America. Unauthorized distribution, modification, reproduction, or disclosure is prohibited.