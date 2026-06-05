# MR Letters Automation
## Deployment Guide

### Overview

This document describes the process for building, validating, and deploying the MR Letters Automation application.

---

## Deployment Type

The application is distributed as a portable Windows executable.

Characteristics:

- No installation required
- No administrator privileges required
- All dependencies bundled
- OCR resources included
- Poppler included
- Tesseract included

---

## Build Requirements

Development Environment:

- Python 3.11+
- Windows 10/11
- Virtual Environment (.venv)

Required Packages:

```bash
pip install -r requirements.txt
```

---

## Project Structure

Required deployment resources:

```text
assets/
├── icon.ico
├── forest-dark.tcl
├── poppler/
└── tesseract/
```

---

## Build Process

Generate executable:

```bash
pyinstaller --clean build.spec
```

Output:

```text
dist/
└── MR_Letters_Generator/
```

---

## Pre-Release Validation

Validate:

- UMR
- Optum
- BCBS TX
- Florida Blue
- Aetna
- Cigna
- Any other added payer
- Auto

Verify:

- OCR
- PDF Processing
- Assignment Logic
- File Renaming
- Logging
- UI Functionality

---

## User Acceptance Testing

Before release:

- Validate collector assignment
- Validate OCR extraction
- Validate output folders
- Validate CSV log generation

---

## Release Packaging

Package contents:

```text
MR_Letters_Generator/
README
User Manual
License
```

---

## Rollback Procedure

If issues are found:

1. Remove deployed version
2. Restore previous validated build
3. Re-test critical workflows
4. Document issue before next deployment