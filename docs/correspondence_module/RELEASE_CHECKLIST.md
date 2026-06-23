# Correspondence Processing Module

## Release Checklist

### Pre-Release

---

#### Funtionality

##### **Payer detection and Assignation**

- [ ] Payer correcly detected and assigned in the filename.
- [ ] Payer added to the payer_signatures.py (if needed).

---

#### Classification

- [ ] Single-Patient classification validated.
- [ ] Multi-Patient classification validated.
- [ ] Miscellaneous classification validated.
- [ ] Historical year detection validated.
- [ ] Duplicate patient filtering validated.
- [ ] False Multi-Patient detection validated.

---

#### Extraction

- [ ] Payer detection validated.
- [ ] Patient extraction validated.
- [ ] DOS extraction validated.
- [ ] State extraction validated.
- [ ] Unknown payer handling validated.
- [ ] Unknown state handling validated.

---

#### OCR

- [ ] Tesseract functioning.
- [ ] Poppler functioning.
- [ ] OCR fallback validated.
- [ ] OCR optimization validated.

---

#### File Naming

- [ ] Single-Patients filenames validated
- [ ] Multi-Patient filenames validated.
- [ ] Miscellaneous filenames validated.
- [ ] Historical year prefic validated.
- [ ] Duplicate filename precention validated.

---

#### UI

- [ ] Forest-Dark theme loads correctly.
- [ ] Icon loads correctly.
- [ ] Processing logs display correctly.
- [ ] Error messages display correctly.

---

#### Performance

- [ ] Large batch processing validated.
- [ ] OCR performance validated.
- [ ] Processing logs reviwed.