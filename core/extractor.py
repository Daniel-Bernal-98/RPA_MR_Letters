# ============================================================================
# MR Letters Generator
#
# Copyright (c) 2026 ABA Centers of America
# All Rights Reserved.
#
# Proprietary and Confidential.
# For internal use only.
#
# Unauthorized copying, distribution, modification, or disclosure
# of this software is strictly prohibited.
# ============================================================================

import re
import cv2
import numpy as np

from datetime import datetime, date
from core.pdf_processor import pdf_to_image
from core.ocr import OCRReader
from core.payer_config import (
    get_payer_ocr_config,
    get_payer_text_patterns,
    get_payer_zone_config
)
from utils.helpers import sanitize_filename

from PyPDF2 import PdfReader

ocr = OCRReader()


def normalizar_nombre(nombre):
    return sanitize_filename(nombre.upper())


def split_name(text):
    text = re.sub(r"[^A-Z]", "", text)

    if len(text) < 6:
        return None

    mid = len(text) // 2
    return text[mid:], text[:mid]

def extract_text_fast(pdf_path):
    results =[]

    try:
        reader = PdfReader(pdf_path)

        for i, page in enumerate(reader.pages):
            text = (page.extract_text() or "").strip()

            if text:
                results.append((i, text))
        return results
    
    except Exception as e:
        print(f"ERROR: {e}")
        return []


def preprocess_image(img):
    """Generic image preprocessing for OCR, can be further customized per payer if needed."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.convertScaleAbs(gray, alpha=1.8, beta=15)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    return cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        31,
        2
    )


def extract_data_with_payer(pdf_path, payer='default'):
    """
    Extract patient name and DOS from PDF with payer-specific configuration.
    
    Args:
        pdf_path: Path to PDF file
        payer: Payer identifier (e.g., 'aetna', 'cigna', 'uhc', 'bcbs')
               Used to retrieve payer-specific OCR and extraction config
               from payer_config.py
    Returns:
        Tuple of (patient_name, date_of_service)
    """
    try:
        patient = "UNKNOWN"
        dos = "00-00-0000"

        # Step 1: Try fast extraction first
        text_pages = extract_text_fast(pdf_path)
        used_fast = False

        for page_num, texto in text_pages:
            patient, dos = _extract_from_text(texto, payer)

            valid_patient = patient != "UNKNOWN"
            valid_dos = dos != "00-00-0000"

            if valid_patient and valid_dos:
                used_fast = True
                break
        
        if not used_fast:
            images = pdf_to_image(pdf_path)
            payer_config = get_payer_ocr_config(payer)

            for page_num, img in enumerate(images):
                data = ocr.read_with_boxes(img, payer_config=payer_config)
                if payer == "BCBS TX":
                    ocr_patient, ocr_dos = _extract_from_ocr_data_bsbc_tx(data, img, payer)
                elif payer == "Florida Blue":
                    ocr_patient, ocr_dos = _extract_from_ocr_data_florida_blue(data, img, payer)
                elif payer == "Aetna":
                    ocr_patient, ocr_dos = _extract_from_ocr_data_aetna(data, img, payer)
                elif payer == "Cigna":
                    ocr_patient, ocr_dos = _extract_from_ocr_data_cigna(data, img, payer)
                else:
                    ocr_patient, ocr_dos = _extract_from_ocr_data(data, img, payer)

                valid_patient = ocr_patient != "UNKNOWN"
                valid_dos = ocr_dos != "00-00-0000"

                if patient == "UNKNOWN" and valid_patient:
                    patient = ocr_patient

                if dos == "00-00-0000" and valid_dos:
                    dos = ocr_dos

                if patient != "UNKNOWN" and dos != "00-00-0000":
                    break
                    
        return patient, dos

    except Exception as e:
        print(f"[{payer}] ERROR: {e}")
        patient, dos = "ERROR", "00-00-0000"
        return patient, dos


def extract_data(pdf_path):
    """Backward-compatible wrapper using default payer config."""
    return extract_data_with_payer(pdf_path, payer='default')


def _extract_from_text(text, payer):
    """
    Extract patient name and DOS from fast text extraction.
    
    Args:
        text: Extracted text from PDF
        payer: Payer identifier (for payer-specific regex patterns)
    
    Returns:
        Tuple of (patient_name, date_of_service)
    """
    patient = "UNKNOWN"
    dos = "00-00-0000"

    # Get payer-specific patterns
    patterns = get_payer_text_patterns(payer)

    text_upper = text.upper()

    # Try primary patient pattern
    match_patient = re.search(patterns["patient_pattern"], text_upper)

    if match_patient:
        # Handle groups based on number of capture groups
        groups = match_patient.groups()
        if len(groups) >= 2:
            patient = normalizar_nombre(f"{groups[1]}_{groups[0]}")
        elif len(groups) == 1:
            patient = normalizar_nombre(groups[0])

    # Try alternative patient pattern if primary failed
    if patient == "UNKNOWN" and patterns.get("patient_pattern_alt"):
        match_patient = re.search(patterns["patient_pattern_alt"], text_upper)
        if match_patient:
            groups = match_patient.groups()
            if len(groups) >= 2:
                patient = normalizar_nombre(f"{groups[1]}_{groups[0]}")
            elif len(groups) == 1:
                patient = normalizar_nombre(groups[0])

    # Extract DOS
    match_dos = re.search(patterns["dos_pattern"], text_upper)

    if match_dos:
        dos = match_dos.group(1).replace("/", "-")

    return patient, dos

def _extract_from_ocr_data_bsbc_tx(data, img, payer):
    """
    BCBS TX specific OCR extraction.
    
    These payers have "Patient" and "Name:" on separate OCR items,
    followed by first and last names on the same or nearby lines.
    
    Args:
        data: List of OCR results with bounding boxes
        img: Original image (for zone calculations)
        payer: Payer identifier
    
    Returns:
        Tuple of (patient_name, date_of_service)
    """
    patient = "UNKNOWN"
    dos = "00-00-0000"

    h, w = img.shape[:2]

    # Get payer specific zone config
    zone_config = get_payer_zone_config(payer)
    patient_zone = zone_config["patient_search_zone"]

    #Calculate boundaries in pixels
    zone_left = int(w * patient_zone["left_percent"])
    zone_right = int(w * patient_zone["right_percent"])
    zone_top = int(h * patient_zone["top_percent"])
    zone_bottom = int(h * patient_zone["bottom_percent"])

    # Filter OCR data to patient search zone
    zone_data = [
        d for d in data
        if zone_left <= d["left"] <= zone_right
        and zone_top <= d["top"] <= zone_bottom
    ]

    same_line_threshold = zone_config["same_line_threshold"]
    below_line_threshold = zone_config["below_line_threshold"]

    # BCBS TX specific logic: Look for "Patient" and "Name:" then find nearby words
    for i, item in enumerate(zone_data):
        text =item["text"].upper()
        top = item["top"]
        left = item["left"]

        # Look for "PATIENT" label
        if "PATIENT" in text:
            # Find "NAME" label that follows
            name_label_idx = None
            for j in range(i + 1, min (i+ 5, len(zone_data))):
                if "NAME" in zone_data[j]["text"].upper():
                    name_label_idx = j
                    break

            #if "NAME" label found, use its position
            if name_label_idx is not None:
                top = zone_data[name_label_idx]["top"]
                left = zone_data[name_label_idx]["left"]

            # get items below or same line as "NAME" label
            same_line = [
                d for d in zone_data
                if abs(d["top"] - top) < same_line_threshold and d["left"] > left
            ]
            below_line = [
                d for d in zone_data
                if same_line_threshold < (d["top"] - top) < below_line_threshold and d["left"] > left
            ]

            candidates = same_line + below_line
            candidates = sorted(candidates, key=lambda x: (x["top"], x["left"]))

            words = []

            for w_item in candidates:
                # Allow lowercase letters from OCR
                word = re.sub(r"[^A-Za-z]", "", w_item["text"])
                if word.upper() in ["ABOVE", "LISTED", "THE", "PATIENT", "NAME"]:
                    continue
                if len(word) >= 2:
                    words.append(word)
                if len(words) == 2:
                    break

            if len(words) == 2:
                # Format as LASTNAME_FIRSTNAME
                patient = normalizar_nombre(f"{words[1]}_{words[0]}")

        #Look for DOS label (Service date for BCBS TX)
        if "SERVICE" in text:
            date_label_idx = None

            for j in range(i+1, min(i+5, len(zone_data))):
                if "DATE" in zone_data[j]["text"].upper():
                    date_label_idx = j
                    break
            
            if date_label_idx is not None:

                date_top = zone_data[date_label_idx]["top"]
                date_left = zone_data[date_label_idx]["left"]

                same_line = [
                    d for d in zone_data
                    if abs(d["top"] - date_top) < same_line_threshold and d["left"] > date_left
                ]

                for w_item in same_line:
                    match = re.search(r"([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{4})", w_item["text"])
                    if match:
                        dos = match.group(1).replace("/", "-")
                        break
    """
     BCBS TX DOS FALLBACK
     OCR sometimes reads:
    
     04/19/2025 -> 4190025
     04/21/2025 -> 4212025
    
     If normal extraction failed, look below the patient block
     for a 7-8 digit number and reconstruct the date.
    """
    if patient != "UNKNOWN" and dos == "00-00-0000":
        
        patient_top = None
        
        for item in zone_data:
            if "PATIENT" in item["text"].upper():
                patient_top = item["top"]
                break
        if patient_top is not None:
            for item in zone_data:
                text = item["text"].strip()

                #Search only below patient area
                if patient_top < item["top"] < patient_top + 80:
                    match = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})", text)
                    if match:
                        dos = match.group(1).replace("/", "-")
                        break

                    # OCR Artifact: 4190025 -> 04/19/2025
                    if re.fullmatch(r"\d{7,8}", text):
                        raw = text
                        try:
                            if len(raw) == 7:
                                month = raw[0]
                                day = raw[1:3]
                                year = raw[3:]
                            elif len(raw) == 8:
                                month = raw[:2]
                                day = raw[2:4]
                                year = raw[4:]
                                if len(year) == 4 and year.startswith("00"):
                                    year = "20" + year[2:]
                            else:
                                continue

                            dos = (
                                f"{month.zfill(2)}-"
                                f"{day.zfill(2)}-"
                                f"{year}"
                            )

                            break
                        except Exception:
                            pass

    return patient, dos

def _extract_from_ocr_data_florida_blue(data, img, payer):
    # Florida Blue specific OCR extraction

    patient = "UNKNOWN"
    dos = "00-00-0000"

    h, w = img.shape[:2]

    zone_config = get_payer_zone_config(payer)

    patient_zone = zone_config["patient_search_zone"]

    zone_left = int(w * patient_zone["left_percent"])
    zone_right = int(w * patient_zone["right_percent"])
    zone_top = int(h * patient_zone["top_percent"])
    zone_bottom = int(h * patient_zone["bottom_percent"])

    zone_data = [
        d for d in data
        if zone_left <= d["left"] <= zone_right
        and zone_top <= d["top"] <= zone_bottom
    ]
    
    same_line_threshold = zone_config["same_line_threshold"]

    for i, item in enumerate(zone_data):

        text = item["text"].upper()

        #Patient extraction
        if text.strip() == "PATIENT:":

            top = item["top"]
            left = item["left"]

            same_line = [d for d in zone_data if abs(d["top"] - top) < same_line_threshold and d["left"] > left]
            same_line = sorted(same_line, key=lambda x:x["left"])

            words = []

            for w in same_line:

                word = re.sub(r"[^A-Z]", "", w["text"].upper())

                if len(word) >= 2:
                    words.append(word)

            if len(words) >= 2:
                
                first_name = words[0]
                last_name = words[1]

                patient = normalizar_nombre(f"{last_name}_{first_name}")
        
        # Service Date Extraction
        if text.strip() == "SERVICE":
            top = item["top"]

            nearby = [
                d for d in zone_data
                if abs(d["top"] - top) < same_line_threshold
            ]

            for d in nearby:
                match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", d["text"])
                if match:
                    dos = match.group(1).replace("/", "-")
                    break
    
    return patient, dos

def _extract_from_ocr_data_aetna(data, img, payer):
    # Aetna specific OCR Extraction logic

    patient = "UNKNOWN"
    dos = "00-00-0000"

    h, w = img.shape[:2]

    zone_config = get_payer_zone_config(payer)

    patient_zone = zone_config["patient_search_zone"]

    zone_left = int(w * patient_zone["left_percent"])
    zone_right = int(w * patient_zone["right_percent"])
    zone_top = int(h * patient_zone["top_percent"])
    zone_bottom = int(h * patient_zone["bottom_percent"])

    zone_data = [
        d for d in data
        if zone_left <= d["left"] <= zone_right
        and zone_top <= d["top"] <= zone_bottom
    ]

    for i, item in enumerate(zone_data):
        text = item["text"].upper().strip()

        # Member Name Extraction Logic for Aetna:
        if text == "MEMBER":
            if(i+1 < len(zone_data) and zone_data[i+1]["text"].upper().startswith("NAME")):
                patient_words = []

                for j in range(i+2, min(i+8, len(zone_data))):
                    candidate = zone_data[j]["text"].strip()
                    upper = candidate.upper()

                    if upper.startswith("MEMBER"):
                        break
                    if upper.startswith("ID"):
                        break
                    if upper.startswith("CASE"):
                        break     
                    
                    clean = re.sub(r"[^A-Z]", "", upper)

                    if len(clean) >= 2:
                        patient_words.append(clean)

                if len(patient_words) >= 2:
                    first_name = patient_words[0]
                    last_name = patient_words[-1]

                    patient = normalizar_nombre(f"{last_name}_{first_name}")

        # Date of Service Extraction Logic for Aetna
        if "DATE" in text:

            service_text = " ".join(
                zone_data[j]["text"]
                for j in range(i, min(i +12, len(zone_data)))
            ).upper()

            month_match = re.search(r"(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+(\d{1,2}),\s+(\d{4})",
                                     service_text
                                    )
            if month_match:

                months = {
                    "JANUARY": "01",
                    "FEBRUARY": "02",
                    "MARCH": "03",
                    "APRIL": "04",
                    "MAY": "05",
                    "JUNE": "06",
                    "JULY": "07",
                    "AUGUST": "08",
                    "SEPTEMBER": "09",
                    "OCTOBER": "10",
                    "NOVEMBER": "11",
                    "DECEMBER": "12"
                }

                month = months[month_match.group(1)]
                day = month_match.group(2).zfill(2)
                year = month_match.group(3)

                dos = f"{month}-{day}-{year}"

    return patient, dos

def _extract_from_ocr_data_cigna(data, img, payer):
    """
    Cigna specific OCR extraction.

    Supports:
        Format 1:
            Patient:
            Date of Service:
        
        Format 2:
            Name:
            Date of Service:
    
    The information may appear on different pages, and since there iare at least 2
    different formats it is necesary to implement different extraction methods for
    each format.
    """
    patient = "UNKNOWN"
    dos = "00-00-0000"

    h, w = img.shape[:2]

    zone_config = get_payer_zone_config(payer)

    patient_zone = zone_config["patient_search_zone"]

    zone_left = int(w * patient_zone["left_percent"])
    zone_right = int(w * patient_zone["right_percent"])
    zone_top = int(h * patient_zone["top_percent"])
    zone_bottom = int(h * patient_zone["bottom_percent"])

    zone_data = [
        d for d in data
        if zone_left <= d["left"] <= zone_right
        and zone_top <= d["top"] <= zone_bottom
    ]

    same_line_threshold = zone_config["same_line_threshold"]

    # Patient Name Extraction

    for i, item in enumerate(zone_data):
        
        text = item["text"].upper().strip()

        # Format 1
        # Patient
        if text.startswith("PATIENT"):
            
            patient_words = []

            for j in range(i+1, min(i+10, len(zone_data))):

                candidate = zone_data[j]["text"].strip()
                upper = candidate.upper()

                if upper.startswith("RELATIONSHIP"):
                    break
                if upper.startswith("PROVIDER"):
                    break
                if upper.startswith("DATE"):
                    break

                clean = re.sub(r"[^A-Z]","", upper)

                if len(clean) >= 2:
                    patient_words.append(clean)

            if len(patient_words) >= 2:

                first_name = patient_words[0]
                last_name = patient_words[1]

                patient = normalizar_nombre(f"{last_name}_{first_name}")

                break
        
        # Format 2
        # Name:

        elif text.startswith("NAME"):
            patient_words = []

            for j in range(i + 1, min(i + 6, len(zone_data))):

                candidate = zone_data[j]["text"].strip()
                upper = candidate.upper()

                if upper.startswith("ID"):
                    break
                if upper.startswith("SR"):
                    break
                if upper.startswith("DATE"):
                    break

                clean = re.sub(r"[^A-Z]", "", upper)

                if len(clean) >= 2:
                    patient_words.append(clean)

            if len(patient_words) >= 2:

                first_name = patient_words[0]
                last_name = patient_words[-1]

                patient = normalizar_nombre(f"{last_name}_{first_name}")

                break

    # DOS Extraction

    for i, item in enumerate(zone_data):

        text = item["text"].upper().strip()

        if "DATE" in text:
            search_text = " ".join(
                zone_data[j]["text"]
                for j in range (i, min(i + 25, len(zone_data)))
            ).upper()

            # Format MM/DD/YYYY

            match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", search_text)

            if match:
                dos = (match.group(1).replace("/","-"))
                break

            # For date ranges

            range_match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})\s*-\s*(\d{1,2}/\d{1,2}/\d{4})", search_text)

            if range_match:
                dos = (range_match.group(1).replace("/","-"))
                break
    print(f"Tesseract captured text: {text}")
    print("\n====== CIGNA OCR ======")

    for item in zone_data:
        print(repr(item["text"]))

    print("=========================\n")
    return patient, dos

# Default OCR extraction logic for other payers
def _extract_from_ocr_data(data, img, payer):
    """
    Extract patient name and DOS from OCR bounding box data.
    
    Args:
        data: List of OCR results with bounding boxes
        img: Original image (for zone calculations)
        payer: Payer identifier (for payer-specific extraction logic)
    
    Returns:
        Tuple of (patient_name, date_of_service)
    """
    patient = "UNKNOWN"
    dos = "00-00-0000"

    h, w = img.shape[:2]

    # Get payer-specific zone config
    zone_config = get_payer_zone_config(payer)
    patient_zone = zone_config["patient_search_zone"]

    # Calculate zone boundaries in pixels
    zone_left = int(w * patient_zone["left_percent"])
    zone_right = int(w * patient_zone["right_percent"])
    zone_top = int(h * patient_zone["top_percent"])
    zone_bottom = int(h * patient_zone["bottom_percent"])

    # Filter OCR data to patient search zone
    zone_data = [
        d for d in data
        if zone_left <= d["left"] <= zone_right
        and zone_top <= d["top"] <= zone_bottom
    ]

    same_line_threshold = zone_config["same_line_threshold"]
    below_line_threshold = zone_config["below_line_threshold"]

    for item in zone_data:
        text = item["text"].upper()
        top = item["top"]
        left = item["left"]

        # Look for patient label
        if re.search(r"P[A-Z]*IENT[:;]", text):

            same_line = [
                d for d in zone_data
                if abs(d["top"] - top) < same_line_threshold and d["left"] > left
            ]

            below_line = [
                d for d in zone_data
                if same_line_threshold < (d["top"] - top) < below_line_threshold and d["left"] > left
            ]

            candidates = same_line + below_line
            candidates = sorted(candidates, key=lambda x: (x["top"], x["left"]))

            words = []

            for w_item in candidates:
                word = re.sub(r"[^A-Z]", "", w_item["text"].upper())

                if word in ["ABOVE", "LISTED", "THE", "PATIENT"]:
                    continue

                if len(word) >= 2:
                    words.append(word)

                if len(words) == 2:
                    break

            if len(words) == 2:
                patient = normalizar_nombre(f"{words[1]}_{words[0]}")

            elif len(words) == 1:
                split = split_name(words[0])
                if split:
                    last, first = split
                    patient = normalizar_nombre(f"{last}_{first}")

            if "ABOVE" in patient or "LISTED" in patient:
                patient = "UNKNOWN"

        # Look for DOS label
        if "SERV" in text or "DATE" in text:
            same_line = [
                d for d in zone_data
                if abs(d["top"] - top) < same_line_threshold
            ]

            for w_item in same_line:
                match = re.search(
                    r"([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})",
                    w_item["text"]
                )
                if match:
                    dos = match.group(1).replace("/", "-")
                    break

    return patient, dos


# ============================================================================
# ISSUE DATE EXTRACTION (BONUS FEATURE)
# ============================================================================

ISSUE_DATE_REGEX = re.compile(
    r"\b("
    r"JAN(?:UARY)?|FEB(?:RUARY)?|MAR(?:CH)?|APR(?:IL)?|MAY|JUN(?:E)?|"
    r"JUL(?:Y)?|AUG(?:UST)?|SEP(?:TEMBER)?|OCT(?:OBER)?|NOV(?:EMBER)?|DEC(?:EMBER)?"
    r")\s+(\d{1,2}),?\s+(\d{4})\b",
    re.IGNORECASE
)

_MONTH_MAP = {
    "JAN": 1, "JANUARY": 1,
    "FEB": 2, "FEBRUARY": 2,
    "MAR": 3, "MARCH": 3,
    "APR": 4, "APRIL": 4,
    "MAY": 5,
    "JUN": 6, "JUNE": 6,
    "JUL": 7, "JULY": 7,
    "AUG": 8, "AUGUST": 8,
    "SEP": 9, "SEPT": 9, "SEPTEMBER": 9,
    "OCT": 10, "OCTOBER": 10,
    "NOV": 11, "NOVEMBER": 11,
    "DEC": 12, "DECEMBER": 12,
}


def _parse_issue_date_from_text(text: str):
    """Parse issue date from text in format 'MONTH DD, YYYY'."""
    if not text:
        return None

    t = str(text).strip()
    m = ISSUE_DATE_REGEX.search(t)

    if not m:
        return None

    mon_raw = m.group(1).upper()
    day = int(m.group(2))
    year = int(m.group(3))

    # Normalize month name
    mon_key = mon_raw[:3] if len(mon_raw) > 3 else mon_raw
    month = _MONTH_MAP.get(mon_raw, _MONTH_MAP.get(mon_key, None))

    if not month:
        return None

    try:
        return date(year, month, day)
    except ValueError:
        return None


def extract_issue_date(pdf_path, payer='default'):
    """Extract the letter issue date from the PDF using Tesseract OCR."""
    try:
        text_pages = extract_text_fast(pdf_path)
        for page_num, texto in text_pages:
            d = _parse_issue_date_from_text(texto.upper())

            if d:
                return d

        # OCR fallback
        images = pdf_to_image(pdf_path)
        
        # Get payer-specific OCR config
        payer_config = get_payer_ocr_config(payer)

        # Get payer-specific zone config
        zone_config = get_payer_zone_config(payer)
        date_zone = zone_config["date_search_zone"]

        for page_num, img in enumerate(images):
            data = ocr.read_with_boxes(img, payer_config=payer_config)

            h, w = img.shape[:2]

            # Top right area where the date is typically located
            zone_left = int(w * date_zone["left_percent"])
            zone_right = int(w * date_zone["right_percent"])
            zone_top = int(h * date_zone["top_percent"])
            zone_bottom = int(h * date_zone["bottom_percent"])

            zone = [
                d for d in data
                if zone_left <= d["left"] <= zone_right
                and zone_top <= d["top"] <= zone_bottom
            ]

            zone_sorted = sorted(zone, key=lambda x: (x["top"], x["left"]))
            joined = " ".join([d["text"] for d in zone_sorted])

            return _parse_issue_date_from_text(joined)

    except Exception as e:
        return None