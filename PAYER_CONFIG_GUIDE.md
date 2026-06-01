# PAYER_CONFIG_GUIDE.md

# Payer Configuration Guide

This document explains how payer-specific configurations work inside the MR Letters Generator project and how to add, tune, and troubleshoot new payer configurations.

---

# Overview

The application supports multiple insurance payers by using payer-specific extraction rules.

Each payer can define:

* OCR preprocessing parameters
* OCR engine settings
* Regex extraction patterns
* OCR search zones
* Text grouping thresholds

All payer configurations are stored in:

```python
core/payer_config.py
```

The system is designed so that new payers can be added without changing the extraction engine itself.

---

# Configuration Architecture

The configuration module is divided into 3 major sections:

| Section               | Purpose                                    |
| --------------------- | ------------------------------------------ |
| `PAYER_OCR_CONFIGS`   | OCR preprocessing and Tesseract parameters |
| `PAYER_TEXT_PATTERNS` | Regex patterns used for text extraction    |
| `PAYER_ZONE_CONFIGS`  | Document layout zones used during OCR      |

Helper functions are provided to safely retrieve configurations with automatic fallback to `default`.

---

# How Extraction Works

The extraction pipeline generally follows this process:

1. PDF text extraction is attempted first
2. Regex patterns are used to extract patient name and DOS
3. If extraction fails, OCR fallback is used
4. OCR preprocessing is applied using payer-specific settings
5. OCR zones are scanned for relevant text
6. Extracted values are normalized and matched against spreadsheet data

---

# Adding a New Payer

To add support for a new payer:

## Step 1 — Add OCR Configuration

Inside:

```python
PAYER_OCR_CONFIGS = {
```

Add a new entry:

```python
"NewPayer": {
    "psm": 6,
    "oem": 3,
    "lang": "eng",
    "alpha": 1.6,
    "beta": 10,
    "blur_kernel": 3,
    "threshold_block_size": 31,
},
```

---

## Step 2 — Add Text Extraction Patterns

Inside:

```python
PAYER_TEXT_PATTERNS = {
```

Add regex patterns:

```python
"NewPayer": {
    "patient_pattern": r"PATIENT[:\\s]+([A-Z\\s]+?)(?=\\n|$)",
    "dos_pattern": r"SERVICE DATE[:\\s]*([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})",
    "patient_pattern_alt": r"MEMBER[:\\s]+([A-Z\\s]+?)(?=\\n|$)",
},
```

---

## Step 3 — Add OCR Search Zones

Inside:

```python
PAYER_ZONE_CONFIGS = {
```

Add document search zones:

```python
"NewPayer": {
    "patient_search_zone": {
        "left_percent": 0.55,
        "right_percent": 1.0,
        "top_percent": 0.0,
        "bottom_percent": 0.6,
    },
    "date_search_zone": {
        "left_percent": 0.55,
        "right_percent": 1.0,
        "top_percent": 0.0,
        "bottom_percent": 0.35,
    },
    "same_line_threshold": 10,
    "below_line_threshold": 25,
},
```

---

## Step 4 — Add Payer to the UI

Add the payer name to:

```python
app/ui.py
```

Locate the default payer list and append the new payer.

Example:

```python
DEFAULT_PAYERS = [
    "UMR/Optum",
    "Aetna",
    "Cigna",
    "BCBS",
    "NewPayer"
]
```

---

## Step 5 — Test With Real Documents

Use multiple PDFs from the payer:

* clean PDFs
* scanned PDFs
* low-quality scans
* rotated scans
* multi-page documents

Validate:

* patient extraction
* DOS extraction
* collector assignment
* OCR fallback
* filename generation

---

# OCR Configuration Reference

## PSM (Page Segmentation Mode)

Controls how Tesseract interprets page layout.

| Value | Meaning                                     |
| ----- | ------------------------------------------- |
| 3     | Fully automatic page segmentation           |
| 4     | Single column                               |
| 6     | Uniform block of text (recommended default) |
| 7     | Single text line                            |
| 11    | Sparse text                                 |

Recommended:

* Structured letters → `6`
* Mixed layouts → `3`
* Single-line fields → `7`

---

## OEM (OCR Engine Mode)

| Value | Meaning             |
| ----- | ------------------- |
| 0     | Legacy engine       |
| 1     | LSTM neural engine  |
| 2     | Legacy + LSTM       |
| 3     | Automatic selection |

Recommended:

```python
"oem": 3
```

---

## Alpha

Controls image contrast scaling.

Higher values increase contrast.

Typical range:

```python
1.4 - 2.0
```

Example:

```python
"alpha": 1.8
```

Use higher values for:

* faded scans
* low contrast PDFs
* gray backgrounds

---

## Beta

Controls brightness offset.

Typical range:

```python
0 - 25
```

Example:

```python
"beta": 10
```

---

## Blur Kernel

Applies Gaussian blur before thresholding.

Must always be an odd number.

Examples:

```python
3
5
7
```

Larger blur values:

* reduce noise
* may remove fine text details

---

## Threshold Block Size

Used during adaptive thresholding.

Must always be odd.

Typical range:

```python
21 - 51
```

Smaller values:

* preserve detail
* more sensitive to noise

Larger values:

* smoother OCR
* may lose small characters

---

# Regex Pattern Guide

Regex patterns are used during direct text extraction.

This is usually faster and more accurate than OCR.

---

# Patient Name Patterns

Example:

```python
r"PATIENT[:\\s]+([A-Z\\s]+?)(?=\\n|$)"
```

Breakdown:

| Pattern        | Meaning               |                      |
| -------------- | --------------------- | -------------------- |
| `PATIENT`      | Matches literal label |                      |
| `[:\\s]+`      | Colon or spaces       |                      |
| `([A-Z\\s]+?)` | Captures patient name |                      |
| `(?=\n         | $)`                   | Stops at newline/end |

---

# DOS Patterns

Example:

```python
r"SERVICE DATE[:\\s]*([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})"
```

Matches:

* 01/15/2025
* 01-15-2025

---

# OCR Zone Configuration

OCR zones limit where the system searches for information.

This improves:

* OCR speed
* extraction accuracy
* false positive reduction

Zones are percentage-based.

Example:

```python
"left_percent": 0.55
```

Means:

* start scanning at 55% of page width

---

# Visual Example

```text
+------------------------------------------------+
|                                                |
|                     DATE ZONE                  |
|                +------------------+            |
|                |                  |            |
|                +------------------+            |
|                                                |
|                     PATIENT ZONE               |
|                +------------------+            |
|                |                  |            |
|                |                  |            |
|                +------------------+            |
|                                                |
+------------------------------------------------+
```

---

# Line Thresholds

## same_line_threshold

Defines how close OCR words must be vertically to be considered on the same line.

Example:

```python
"same_line_threshold": 10
```

Increase if:

* text rows are slightly misaligned

Decrease if:

* unrelated lines are merging

---

## below_line_threshold

Defines search distance below labels.

Example:

```python
"below_line_threshold": 25
```

Increase if:

* values appear farther below labels

Decrease if:

* unrelated text is being captured

---

# Debugging OCR Problems

## Problem: No Patient Name Found

Possible causes:

* wrong regex pattern
* OCR zone too small
* low OCR contrast
* unexpected label name

Recommended fixes:

* inspect raw OCR text
* expand search zone
* add alternate regex patterns
* increase alpha value

---

## Problem: Wrong DOS Extracted

Possible causes:

* multiple dates on document
* regex too generic
* OCR artifacts

Recommended fixes:

* make DOS regex more specific
* reduce OCR zone size
* use alternate label anchors

---

## Problem: OCR Returns Garbage Text

Possible causes:

* low resolution scans
* excessive compression
* skewed documents
* poor preprocessing

Recommended fixes:

* increase contrast
* adjust threshold size
* change PSM mode
* increase blur slightly

---

# Recommended Workflow for New Payers

1. Collect 5–10 real PDFs
2. Inspect where patient and DOS appear
3. Attempt direct text extraction first
4. Build regex patterns
5. Add OCR fallback config
6. Tune OCR preprocessing
7. Tune OCR zones
8. Validate output filenames
9. Validate spreadsheet matching
10. Test edge cases

---

# Best Practices

## Prefer Text Extraction Over OCR

Direct PDF text extraction is:

* faster
* more accurate
* less CPU intensive

OCR should only be fallback logic.

---

## Keep Regex Patterns Specific

Overly broad regex patterns increase false positives.

Prefer:

```python
r"SERVICE DATE[:\\s]*(...)"
```

Instead of:

```python
r"DATE[:\\s]*(...)"
```

---

## Use Multiple Fallback Patterns

Many payers use inconsistent wording.

Example:

```python
"patient_pattern_alt"
```

can significantly improve extraction reliability.

---

## Test Against Real Production PDFs

Synthetic or edited PDFs rarely reflect production OCR conditions.

Always test:

* low-quality scans
* rotated pages
* fax artifacts
* grayscale copies
* partially cropped pages

---

# Current Supported Payers

The project currently includes configurations for:

* UMR/Optum
* Aetna
* Cigna
* BCBS
* default

---

# Future Improvements

Potential future enhancements:

* payer auto-detection
* ML-based field detection
* visual OCR zone editor
* regex validation UI
* OCR confidence scoring
* extraction preview window
* JSON/YAML payer configs
* per-payer logging

---

# File Reference

| File                   | Purpose                            |
| ---------------------- | ---------------------------------- |
| `core/payer_config.py` | All payer configuration data       |
| `core/ocr.py`          | OCR processing logic               |
| `core/extractor.py`    | Extraction engine                  |
| `core/processor.py`    | Main processing pipeline           |
| `app/ui.py`            | User interface and payer selection |

---

# Summary

The payer configuration system allows the MR Letters Generator to adapt to multiple document formats without changing the extraction engine.

Most new payer integrations only require:

* OCR tuning
* regex adjustments
* OCR zone tuning

A well-tuned payer configuration dramatically improves:

* extraction accuracy
* assignment reliability
* OCR performance
* processing speed
* production stability
