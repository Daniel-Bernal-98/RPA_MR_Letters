# ============================================================================
# Automatic Letter Reader for workload Assignations 
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

"""
Payer Auto-Detection

Detects the payer from the PDF before processing.
Used by Automatic Processing Mode.
"""

from core.extractor import pdf_to_image
from core.ocr import OCRReader
import re
from utils.logger import setup_logger

PAYER_SIGNATURES = {
    "UMR":[
        "UMR"
    ],
    "Optum":[
        "UNITED HEALTHCARE",
        "OPTUM HEALTH",
        "OPTUM"
    ],
    "BCBS TX":[
        "BLUE CROSS BLUE SHIELD OF TEXAS",
        "OF TEXAS",
        "BLUE CROSS AND BLUE SHIELD OF TEXAS"
    ],
    "Florida Blue":[
        "FLORIDA BLUE"
    ],
    "Aetna":[
        "AETNA",
        "AETNA BETTER HEALTH",
        "AETNA PROVIDER",
        "AETNA INC."
    ],
    "Cigna":[
        "CIGNA",
        "EVERNORTH"
    ]
}

MINIMUM_CONFIDENCE = 1

ocr = OCRReader()
logger = setup_logger

def calculate_payer_scores(text):
    """
    Calculates the payer score for better payer detection using by comparing
    the extracted text with each payer signature and assing an score, the payer
    with the higher score will be the selected format for the text extraction and 
    further clasification.
    """
    scores = {}

    for payer, signatures in PAYER_SIGNATURES.items():
        score = 0
        for signature in signatures:
            if signature.upper() in text:
                score += 1
        scores[payer] = score
    
    return scores

def detect_payer(pdf_path):
    """
    Detect payer from PDF contents

    Returns: Payer Name or None.
    """

    try:
        full_text = extract_text_for_payer_detection(pdf_path)
        
        full_text = re.sub(r"\s+", " ", full_text).upper()

        scores = calculate_payer_scores(full_text)
        
        best_payer = None
        best_score = 0

        for payer, score in scores.items():
            if score > best_score:
                best_score = score
                best_payer = payer

        if best_score >= MINIMUM_CONFIDENCE:
            print(f"[AUTO] Detected: {best_payer}, Score: {best_score}")
        
        return best_payer

    except Exception as e:
        print(f"[AUTO] Detection error: {e}")
        return None    
    
def is_known_payer(pdf_path):
    return detect_payer(pdf_path) is not None

def extract_text_for_payer_detection(pdf_path):
    text = ""

    try:
        images = pdf_to_image(pdf_path)

        for page_num, img in enumerate(images[:10]):
            data = ocr.read_with_boxes(img)

            page_text = " ".join(
                item["text"]
                for item in data
            )

            text += " " + page_text
        return text.upper()
    except Exception as e:
        print(f"[AUTO] OCR Detection Error")
        import traceback
        traceback.print_exc()

        return ""