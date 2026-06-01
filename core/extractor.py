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
        print(f"Fast Extraction Error: {e}")
    
        return []

# def extract_text_fast(pdf_path):
#     """Fast text extraction without OCR."""
#     try:
#         reader = PdfReader(pdf_path)
#         page = reader.pages[0]
#         return (page.extract_text() or "").strip()
#     except:
#         return ""


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
            
            print(f"[{payer}] Scanning text page {page_num +1}")

            patient, dos = _extract_from_text(texto, payer)

            valid_patient = patient != "UNKNOWN"
            valid_dos = dos != "00-00-0000"

            if valid_patient and valid_dos:
                print(f"[{payer}] Fast extraction success on page {page_num +1}")
                used_fast = True
                break

        # if texto:

        #     patient, dos = _extract_from_text(texto, payer)

        #     valid_patient = patient != "UNKNOWN"
        #     valid_dos = dos != "00-00-0000"

        #     if valid_patient and valid_dos:
        #         print(f"[{payer}] Using fast extraction (No OCR)")
        #         used_fast = True
        
        if not used_fast:
            print(f"[{payer}] Fast extraction incomplete, Using OCR")

            images = pdf_to_image(pdf_path)
            payer_config = get_payer_ocr_config(payer)

            for page_num, img in enumerate(images):
                print(f"[{payer}] OCR Scanning page {page_num + 1}")

                data = ocr.read_with_boxes(img, payer_config=payer_config)
                ocr_patient, ocr_dos = _extract_from_ocr_data(data, img, payer)

                valid_patient = ocr_patient != "UNKNOWN"
                valid_dos = ocr_dos != "00-00-0000"

                if patient == "UNKNOWN" and valid_patient:
                    patient = ocr_patient

                if dos == "00-00-0000" and valid_dos:
                    dos = ocr_dos

                if patient != "UNKNOWN" and dos != "00-00-0000":
                    print(f"[{payer}] OCR extraction success on page {page_num + 1}")

                break
                    

            # img = pdf_to_image(pdf_path)
            # payer_config = get_payer_ocr_config(payer)
            # data = ocr.read_with_boxes(img, payer_config=payer_config)
            # ocr_patient, ocr_dos = _extract_from_ocr_data(data, img, payer)

            # if patient == "UNKNOWN":
            #     patient = ocr_patient
            # if dos == "00-00-0000":
            #     dos = ocr_dos

        # else:
        #     # Step 2: Fall back to OCR with payer-specific config
        #     print(f"[{payer}] Using OCR fallback")

        #     img = pdf_to_image(pdf_path)

        #     # Get payer-specific OCR config
        #     payer_config = get_payer_ocr_config(payer)

        #     data = ocr.read_with_boxes(img, payer_config=payer_config)

        #     patient, dos = _extract_from_ocr_data(data, img, payer)

        # print(f"[{payer}] PATIENT: {patient}, DOS: {dos}")

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
        texto = extract_text_fast(pdf_path)
        text_pages = extract_text_fast(pdf_path)
        for page_num, texto in text_pages:
            d = _parse_issue_date_from_text(texto.upper())

            if d:
                print(f"Issue date found on page {page_num +1}")
                return d

        # OCR fallback
        images = pdf_to_image(pdf_path)
        
        # Get payer-specific OCR config
        payer_config = get_payer_ocr_config(payer)

        # Get payer-specific zone config
        zone_config = get_payer_zone_config(payer)
        date_zone = zone_config["date_search_zone"]

        for page_num, img in enumerate(images):
            print(f"Issue date OCR Scanning page {page_num + 1}")
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
        print(f"ERROR extracting issue date: {e}")
        return None