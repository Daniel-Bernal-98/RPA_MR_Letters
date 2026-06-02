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

#Module Description (Expand)
"""
Multi-Payer Configuration Module

This module contains all payer-specific configurations including:
- OCR settings (Tesseract PSM, OEM, preprocessing parameters)
- Text extraction patterns (regex patterns for patient name, DOS, etc.)
- Zone configurations (document layout zones for OCR data extraction)
- Document characteristics (document type, expected fields, etc.)

Adding a new payer:
1. Add OCR config to PAYER_OCR_CONFIGS
2. Add text patterns to PAYER_TEXT_PATTERNS
3. Add zone config to PAYER_ZONE_CONFIGS
4. Add to DEFAULT_PAYERS list in app/ui.py
5. Test with sample documents and adjust parameters
"""

# Module OCR Parameters & config (Expand)
"""
OCR CONFIGURATIONS
============================================================================
These are Tesseract OCR parameters. Adjust based on document quality/format.

PSM (Page Segmentation Mode):
   0: OSD only, 1: Auto OSD, 2: Auto, 3: Fully auto, 4: Column, 5: Uniform block,
   6: Uniform block with text (default), 7: Vertical text, 8-13: various modes
OEM (OCR Engine Mode):
   0: Legacy only, 1: Neural nets only, 2: Legacy+Neural, 3: Auto (default)
Alpha/Beta: Image brightness adjustment
Blur kernel: Gaussian blur size (must be odd)
Threshold block size: Adaptive threshold block size (must be odd)
"""

PAYER_OCR_CONFIGS = {
    "UMR": {
        "psm": 6,          # Uniform block of text
        "oem": 3,          # Auto OCR engine
        "lang": "eng",     # English language
        "alpha": 1.6,      # Brightness scale
        "beta": 10,        # Brightness offset
        "blur_kernel": 3,  # Gaussian blur kernel (must be odd)
        "threshold_block_size": 31,  # Adaptive threshold block size (must be odd)
    },
    #Same as UMR,letter format is very similar to UMR, so we can use the same zones and thresholds for text grouping
    "Optum": {
        "psm": 6,          
        "oem": 3,          
        "lang": "eng",     
        "alpha": 1.6,      
        "beta": 10,        
        "blur_kernel": 3,  
        "threshold_block_size": 31,  
    },
    "Aetna": {
        "psm": 6,
        "oem": 3,
        "lang": "eng",
        "alpha": 1.8, #Slightly higher contrast
        "beta": 15,
        "blur_kernel": 5, #stronger blur
        "threshold_block_size": 25,
    },
    "Cigna": {
        "psm": 3, #Automatic segmentation
        "oem": 3,
        "lang": "eng",      
        "alpha": 1.6,
        "beta": 10,
        "blur_kernel": 3,
        "threshold_block_size": 31,
    },
    "BCBS TX": {
        "psm": 6,
        "oem": 3,
        "lang": "eng",
        "alpha": 2.0,
        "beta": 20,
        "blur_kernel": 3,
        "threshold_block_size": 31,
    },
    "Florida Blue": {
        "psm": 6,
        "oem": 3,
        "lang": "eng",
        "alpha": 1.7,
        "beta": 12,
        "blur_kernel": 3,
        "threshold_block_size": 31,
    },
    "default": {
        "psm": 6,
        "oem": 3,
        "lang": "eng",
        "alpha": 1.6,
        "beta": 10,
        "blur_kernel": 3,
        "threshold_block_size": 31,
    },
}


#TEXT EXTRACTION PATTERNS (Expand)
"""
Regex patterns for extracting patient name and DOS from text-based PDFs.
Each payer may have different label formats or field arrangements.
"""

PAYER_TEXT_PATTERNS = {
    "UMR": {
        # Pattern for patient name extraction from text
        "patient_pattern": r"PATIENT[:\s]+([A-Z\s]+?)(?=\n|$|\s{2,})",
        # Pattern for Date of Service extraction
        "dos_pattern": r"(?:SERV|SERVICE)\s*(?:DT|DATE|DATES)[:\s]*([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})",
        # Additional patterns can be added here for fallback
        "patient_pattern_alt": r"(?:MEMBER|INSURED)[:\s]+([A-Z\s]+?)(?=\n|$)",
    },
    #Same as UMR,letter format is very similar to UMR, so we can use the same zones and thresholds for text grouping
    "Optum": {
        # Pattern for patient name extraction from text
        "patient_pattern": r"PATIENT[:\s]+([A-Z\s]+?)(?=\n|$|\s{2,})",
        # Pattern for Date of Service extraction
        "dos_pattern": r"(?:DATE\s+OF\s+SERVICE|SERV|SERVICE)[:\s]*([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})",
        # Additional patterns can be added here for fallback
        "patient_pattern_alt": r"(?:PATIENT|PT)[:\s]+([A-Z\s]+?)(?=\n|$)",
    },
    "Aetna": {
        "patient_pattern": r"PATIENT[:\s]+([A-Z\s]+?)(?=\n|$|\s{2,})",
        "dos_pattern": r"(?:SERVICE|SERV)\s*(?:DATE|DT)[:\s]*([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})",
        "patient_pattern_alt": r"(?:MEMBER|CLAIMANT)[:\s]+([A-Z\s]+?)(?=\n|$)",
    },
    "Cigna": {
        "patient_pattern": r"(?:PATIENT|MEMBER)[:\s]+([A-Z\s]+?)(?=\n|$|\s{2,})",
        "dos_pattern": r"(?:SERVICE|DATE OF SERVICE|DOS)[:\s]*([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})",
        "patient_pattern_alt": r"NAME[:\s]+([A-Z\s]+?)(?=\n|$)",
    },
    "BCBS TX": {
        "patient_pattern": r"Patient\s+Name[:\s]+([A-Za-z\s]+?)(?=\n\n|Patient\s+Number|Service\s+Date|$)",
        "dos_pattern": r"Service\s+Date[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{4})",
        "patient_pattern_alt": r"PATIENT[:\s]+([A-Z\s]+?)(?=\n|$)",
    },
    "Florida Blue": {
        "patient_pattern": r"PATIENT NAME[:\s]+([A-Z\s]+?)(?=\n|PATIENT NUMBER|SERVICE DATE)",
        "dos_pattern": r"SERVICE DATE[:\s]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{4})",
        "patient_pattern_alt": r"PATIENT[:\s]+([A-Z\s]+?)(?=\n|$)",
    },
    "default": {
        "patient_pattern": r"PATIENT[:\s]+([A-Z]+)\s+([A-Z]+)",
        "dos_pattern": r"SERV\s*DT[:\s]*([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})",
        "patient_pattern_alt": None,
    },
}



#ZONE CONFIGURATIONS (Expand)
"""
Define document layout zones for OCR-based extraction.
Each zone is defined as percentage offsets from document edges.
Example: {"left": 0.55} means "right of 55% width"

Common zones:
  - right_zone: Right side of document (typically 55% to 100%)
  - top_zone: Top portion of document (0% to 35%)
  - center_zone: Center area
  - bottom_zone: Bottom area
"""

PAYER_ZONE_CONFIGS = {
    "UMR": {
        # Right side of document where patient info typically is
        "patient_search_zone": {
            "left_percent": 0.55,
            "right_percent": 1.0,
            "top_percent": 0.0,
            "bottom_percent": 0.6,
        },
        # Top right area where date typically is
        "date_search_zone": {
            "left_percent": 0.55,
            "right_percent": 1.0,
            "top_percent": 0.0,
            "bottom_percent": 0.35,
        },
        # Pixel tolerance for same-line text grouping
        "same_line_threshold": 10,
        # Pixel tolerance for below-line text grouping
        "below_line_threshold": 25,
    },
    #Same as UMR,letter format is very similar to UMR, so we can use the same zones and thresholds for text grouping
    "Optum": {
        # Right side of document where patient info typically is
        "patient_search_zone": {
            "left_percent": 0.55,
            "right_percent": 1.0,
            "top_percent": 0.0,
            "bottom_percent": 0.6,
        },
        # Top right area where date typically is
        "date_search_zone": {
            "left_percent": 0.55,
            "right_percent": 1.0,
            "top_percent": 0.0,
            "bottom_percent": 0.35,
        },
        # Pixel tolerance for same-line text grouping
        "same_line_threshold": 10,
        # Pixel tolerance for below-line text grouping
        "below_line_threshold": 25,
    },
    "Aetna": {
        "patient_search_zone": {
            "left_percent": 0.05,
            "right_percent": 0.95,
            "top_percent": 0.20,
            "bottom_percent": 0.70,
        },
        "date_search_zone": {
            "left_percent": 0.05,
            "right_percent": 0.95,
            "top_percent": 0.20,
            "bottom_percent": 0.70,
        },
        "same_line_threshold": 20,
        "below_line_threshold": 40,
    },
    "Cigna": {
        "patient_search_zone": {
            "left_percent": 0.05,
            "right_percent": 0.95,
            "top_percent": 0.05,
            "bottom_percent": 0.50,
        },
        "date_search_zone": {
            "left_percent": 0.05,
            "right_percent": 0.95,
            "top_percent": 0.05,
            "bottom_percent": 0.75,
        },
        "same_line_threshold": 25,
        "below_line_threshold": 30,
    },
    "BCBS TX": {
        "patient_search_zone": {
            "left_percent": 0.55,
            "right_percent": 1.0,
            "top_percent": 0.10,
            "bottom_percent": 0.55,
        },
        "date_search_zone": {
            "left_percent": 0.55,
            "right_percent": 1.0,
            "top_percent": 0.10,
            "bottom_percent": 0.55,
        },
        "same_line_threshold": 20,
        "below_line_threshold": 40,
    },
    "Florida Blue": {
        "patient_search_zone": {
            "left_percent": 0.0,
            "right_percent": 1.0,
            "top_percent": 0.10,
            "bottom_percent": 0.55,
        },
        "date_search_zone": {
            "left_percent": 0.55,
            "right_percent": 1.0,
            "top_percent": 0.10,
            "bottom_percent": 0.55,
        },
        "same_line_threshold": 15,
        "below_line_threshold": 20,
    },
    "default": {
        "patient_search_zone": {
            "left_percent": 0.55,
            "right_percent": 1.0,
            "top_percent": 0.0,
            "bottom_percent": 0.6,
        },
        "date_search_zone": {
            "left_percent": 0.55,
            "right_percent": 1.0,
            "top_percent": 0.0,
            "bottom_percent": 0.35,
        },
        "same_line_threshold": 10,
        "below_line_threshold": 25,
    },
}

### Helper Functions ###

def get_payer_ocr_config(payer: str) -> dict:
    """
    Retirve ths specific config for the selected payer

    Args: 
        payer: Payer identifier, must match a key in PAYER_OCR_CONFIGS.
    Returns:
        Dictionary with OCR Parameters, falls back to 'default' if payer not found
    """

    return PAYER_OCR_CONFIGS.get(payer, PAYER_OCR_CONFIGS["default"])

def get_payer_text_patterns(payer: str) -> dict:
    """
    Retrieve text extraction patterns for the selected payer.

    Args:
        payer: Payer identifier, must match a key in PAYER_TEXT_PATTERNS
    Returns:
        Dictionary with regex patterns, falls back to default if the payer is not found
    """
    return PAYER_TEXT_PATTERNS.get(payer, PAYER_TEXT_PATTERNS["default"])

def get_payer_zone_config(payer:str) -> dict:
    """
    Retrieves the zone configuration for the text extraction for the selected payer (this is made to avoid scaning the complete
    document and only scan a reduced zone where the necesary information is located and optimize time and resources)

    Args:
        payer: Payer Identifier, must match a key in PAYER_ZONE_CONFIGS
    Returns:
        Dictionary with the zone configs, falls back to default if no payer found
    """
    return PAYER_ZONE_CONFIGS.get(payer, PAYER_ZONE_CONFIGS["default"])

def list_available_payers() -> list:
    """
    Get the payer list excluding the 'default'

    Returns:
        List of payer identifiers.
    """
    return [p for p in PAYER_OCR_CONFIGS.keys() if p != "default"]