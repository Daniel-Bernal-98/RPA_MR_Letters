"""
Corresponcende Team specialized text extractor.

This extracts Payer, Patient & DOS from the OCR and process it using the correspondence_processor.py module
for the final data processing.

"""

import re
from core.payer_signatures import PAYER_SIGNATURES

def extract_generic_payer(text):
        #Extract the payer from the OCR by comparing the signatures on file
        
        text_upper = text.upper()
        signatures = PAYER_SIGNATURES

        for signature, payer in signatures.items():
              if signature in text_upper:
                    return payer
        
        return "UNKOWN_PAYER"

def extract_generic_patient(text):
    #Extract the patient name using generic patterns

    patterns = [
        r"PATIENT[:\s]+([A-Z ,'-]+)",

        r"MEMBER[:\s]+([A-Z ,'-]+)",

        r"PATIENT NAME[:\s]+([A-Z ,'-]+)",

        r"RE:\s*([A-Z ,'-]+)",
    ]

    text_upper = text.upper()

    for pattern in patterns:
          match = re.search(pattern, text_upper)

          if match:
                patient = match.group(1).strip()

                patient = re.sub(r"s+", "_", patient)

                return patient
    
    return "UNKOWN_PATIENT"

def extract_generic_dos(text):
      # Extract the DOS using common heatlhcare patterns

    patterns = [
        r"DOS[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",

        r"DATE OF SERVICE[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",

        r"SERVICE DATE[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",

        r"DATES OF SERVICE[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", 
      ]

    text_upper = text.upper()

    for pattern in patterns:
        match = re.search(pattern, text_upper)

        if match:
            return match.group(1).replace("/", "-")
            
    return "00-00-0000"