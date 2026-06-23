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

This deployment package includes:

- Medical Records Letters Module
- Correspondence Processing Module

Both module share the same OCR engine, runtime assets and application interface.

---

## Build Requirements

Development Environment:

- Python 3.14
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

***Complete the respective checklist for each module.***

## Release Packaging

Package contents:

```text
RPA_Letters/
README
User Manual
License
 Medical Records Documentation
 Correspondence Documentation
```

---

## Build Optimization

Before generating a production build:

- Remove temporary debug code
- Exclude test files
- Exclude development documentation not required by end users
- Include only runtime dependencies
- Verify bundled assets

---

## Rollback Procedure

If issues are found:

1. Remove deployed version
2. Restore previous validated build
3. Re-test critical workflows
4. Document issue before next deployment