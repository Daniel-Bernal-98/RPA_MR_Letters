# Correspondence Processing Module

## Release Checklist

### Release V1.0.0

---

#### Funtionality

##### **Payer detection and Assignation**

- [Y] Payer correcly detected and assigned in the filename.
- [Y] Payer added to the payer_signatures.py (if needed).

---

#### Classification

- [Y] Single-Patient classification validated.
- [Y] Multi-Patient classification validated.
- [Y] Miscellaneous classification validated.
- [Y] Historical year detection validated.
- [Y] Duplicate patient filtering validated.
- [Y] False Multi-Patient detection validated.

---

#### Extraction

- [Y] Payer detection validated.
- [Y] Patient extraction validated.
- [Y] DOS extraction validated.
- [Y] State extraction validated.
- [Y] Unknown payer handling validated.
- [Y] Unknown state handling validated.

---

#### OCR

- [Y] Tesseract functioning.
- [Y] Poppler functioning.
- [Y] OCR fallback validated.
- [Y] OCR optimization validated.

---

#### File Naming

- [Y] Single-Patients filenames validated
- [Y] Multi-Patient filenames validated.
- [Y] Miscellaneous filenames validated.
- [Y] Historical year prefic validated.
- [Y] Duplicate filename precention validated.

---

#### UI

- [Y] Forest-Dark theme loads correctly.
- [ ] Icon loads correctly.
- [Y] Processing logs display correctly.
- [Y] Error messages display correctly.

---

#### Performance

- [Y] Large batch processing validated.
- [Y] OCR performance validated.
- [Y] Processing logs reviwed.