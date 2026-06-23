# Automatic Payer Detection Configuration Guide

## Overview

The Automatic Processing mode identifies the payer automatically before document extraction begins.

The detection engine analyzes text extracted from the PDF and compares it against a list of known payer signatures.

Once a payer is identified, the application automatically routes the document to the corresponding payer-specific extraction logic.

Processing Flow:

PDF
→ Text Extraction
→ Payer Signature Detection
→ Payer Selection
→ Existing Payer Extractor
→ Assignment & Renaming

---

## Scope Notice

This document applies exclusively to the Medical Records Letters module and its Automatic Processing Mode.

The configuration, workflows, payer detection rules, and processing logic described in this document are not used by the Correspondence Processing Module.

The Correspondence Processing Module maintains its own extraction logic, payer signature configuration, classification engine, and processing workflow, which are documented separately in the Correspondence module documentation.

---

## Detection Method

Each payer has a list of signatures.

Example:

```python
"Aetna": [
    "AETNA",
    "AETNA BETTER HEALTH",
    "PROVIDER DISPUTE"
]
```

Each signature found in the document contributes to the payer confidence score.

Example:

Document contains:

* AETNA
* AETNA BETTER HEALTH
* PROVIDER DISPUTE

Result:

Aetna score = 3

The payer with the highest score is selected.

---

## Current Supported Payers

* UMR
* Optum
* BCBS TX
* Florida Blue
* Aetna
* Cigna

---

## Adding a New Payer

### Step 1

Add payer-specific extraction logic to:

```text
core/extractor.py
```

### Step 2

Add OCR configuration to:

```text
config/payer_config.py
```

### Step 3

Add payer signatures to:

```text
core/payer_detector.py
```

Example:

```python
"Humana": [
    "HUMANA",
    "HUMANA HEALTH",
    "HUMANA INSURANCE"
]
```

### Step 4

Add payer-specific OCR zones and thresholds.

### Step 5

Test Automatic Processing mode with sample documents.

---

## Confidence Scores

Current scoring system:

1 point = one matching signature

Example:

```text
CIGNA
HEALTHSPRING
```

Result:

Cigna confidence = 2

The payer with the highest confidence score is selected.

---

## Future Enhancements

Planned improvements:

* OCR-based payer detection fallback
* Unknown payer classification
* Generic extraction engine
* Automatic learning of new signatures
* Confidence percentage reporting
* Multi-model detection strategy

---

## Troubleshooting

If a document is assigned to the wrong payer:

1. Review extracted text.
2. Identify unique payer phrases.
3. Add additional signatures.
4. Re-test Automatic Processing mode.

Always prefer highly unique signatures that only appear in documents from a single payer.
