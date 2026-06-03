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

from core.extractor import extract_text_fast

PAYER_SIGNATURES = {
    "UMR":[
        "UMR"
    ],
    "Optum":[
        "UNITED HEALTHCARE",
        "OPTUM HEALTH"
    ],
    "BCBS TX":[
        "BLUE CROSS BLUE SHIELD OF TEXAS",
        "OF TEXAS"
    ],
    "Florida Blue":[
        "FLORIDA BLUE"
    ],
    "Aetna":[
        "AETNA",
        "AETNA BETTER HEALTH"
    ],
    "Cigna":[
        "CIGNA",
        "EVERNORTH"
    ]
}

MINIMUM_CONFIDENCE = 1

def calculate_payer_scores(text):
    """
    Calculates the payer score for better payer detection using by comparing
    the extracted text with each payer signature and assing an score, the payer
    with the higher score will be the selected format for the text extraction and 
    further clasification.
    """
    scores = {}

    for payer, signatures in PAYER_SIGNATURES.items:
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
        text_pages = extract_text_fast(pdf_path)

        full_text = " ".join(
            text
            for _, text in text_pages
        ).upper()

        scores = calculate_payer_scores(full_text)

        best_payer = None
        best_score = 0

        for payer, score in scores.items():
            if score > best_score:

                best_score = score
                best_payer = payer
        if best_score >= MINIMUM_CONFIDENCE:
            return best_payer
        return None
    
    except Exception as e:
        return(f"[AUTO] Detection error: {e}")
    
def is_known_payer(pdf_path):
    return detect_payer(pdf_path) is not None