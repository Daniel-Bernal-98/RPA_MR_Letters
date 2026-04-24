import re
import cv2
import numpy as np

from core.pdf_processor import pdf_to_image
from core.ocr import OCRReader
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
    try:
        reader = PdfReader(pdf_path)
        page = reader.pages[0]
        return (page.extract_text() or "").strip()
    except:
        return ""


def preprocess_image(img):
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


def extract_data(pdf_path):
    try:
        patient = "UNKNOWN"
        dos = "00-00-0000"

        texto = extract_text_fast(pdf_path)

        if texto:
            print("Using fast extraction (no OCR)")

            texto = texto.upper()

            match_patient = re.search(
                r"PATIENT[:\s]+([A-Z]+)\s+([A-Z]+)",
                texto
            )

            if match_patient:
                patient = normalizar_nombre(
                    f"{match_patient.group(2)}_{match_patient.group(1)}"
                )

            match_dos = re.search(
                r"SERV\s*DT[:\s]*([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})",
                texto
            )

            if match_dos:
                dos = match_dos.group(1).replace("/", "-")

        else:
            print("Using OCR fallback")

            img = pdf_to_image(pdf_path)
            img = preprocess_image(img)

            h, w = img.shape[:2]

            data = ocr.read_with_boxes(img)

            right_zone = [
                d for d in data if d["left"] > int(w * 0.55)
            ]

            for item in right_zone:
                text = item["text"].upper()
                top = item["top"]
                left = item["left"]

                if re.search(r"P[A-Z]*IENT[:;]", text):

                    same_line = [
                        d for d in right_zone
                        if abs(d["top"] - top) < 10 and d["left"] > left
                    ]

                    below_line = [
                        d for d in right_zone
                        if 10 < (d["top"] - top) < 25 and d["left"] > left
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

                if "SERV" in text:
                    same_line = [
                        d for d in right_zone
                        if abs(d["top"] - top) < 10
                    ]

                    for w_item in same_line:
                        match = re.search(
                            r"([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})",
                            w_item["text"]
                        )
                        if match:
                            dos = match.group(1).replace("/", "-")

        print("PATIENT:", patient)
        print("DOS:", dos)

        return patient, dos

    except Exception as e:
        print("ERROR:", e)
        return "ERROR", "00-00-0000"