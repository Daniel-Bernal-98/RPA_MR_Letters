"""
Corresponcende Team specialized text extractor.

This extracts Payer, Patient & DOS from the OCR and process it using the correspondence_processor.py module
for the final data processing.

"""

import re
from core.payer_signatures import PAYER_SIGNATURES
from datetime import datetime

def extract_generic_payer(text):
        #Extract the payer from the OCR by comparing the signatures on file
        
        text_upper = text.upper()
        signatures = PAYER_SIGNATURES

        for signature, payer in signatures.items():
              if signature in text_upper:
                    return payer
        
        return "UNKOWN_PAYER"

def extract_all_patients(text):
    
    patterns = [
         
        r"PATIENT'S NAME[:\s]+([A-Z ,'-]+)",

        r"PATIENT NAME[:\s]+([A-Z ,'-]+)",

        r"PATIENT\s*:\s*(.*?)\s+PROV:",

        r"PATIENT\s*:\s*([A-Z]+(?:\s+[A-Z]+){1,3})",

        r"CONFIDENTIAL HEALTH PLAN INFORMATION FOR[:\s]+(?:DATE REQUEST RECEIVED\s+)?([A-Z]+(?:\s+[A-Z]+){1,3})",

        r"NAME\s*:\s*([A-Z\s]+?)(?:\s+ID|\s+SR|$)",
    ]

    invalid_patients = {
        "OPER",
        "PATIENT",
        "MEMBER",
        "NAME",
        "PROVIDER",
        "EEE TAXPAYER",
        "ARE CONDITION TORECEIVE NOTICE",
        "AN",
        "-",
        "TANVI",
    }

    text_upper = text.upper()

    cleanup_terms = [
        " MEMBER ID NUMBER",
        " MEMBER ID",
        " MEMBER",
        " HCID NUMBER",
        " HCID",
        " PATIENT DOB",
        " ACCOUNT NUMBER",
        " SERVICE DATE",
        " PATIENT ACCT",
        " PATIENT ACCT#",
        " PATIENT ACCOUNT",
        " RCID NUMBER",
        " DATE",
        " OPER",
        " PPO",
        " POS",
        " HSA",
        " MO",
        " WE",
    ]

    patients = []

    for pattern in patterns:
        matches = re.findall(pattern, text_upper)
        
        for patient in matches:
            patient = patient.strip()

            patient = re.sub(
                r"\bPATIENT\s+ACCT\w*\b",
                "",
                patient
            )

            patient = re.sub(
                r"\s+",
                " ",
                patient        
            ).strip()

            patient = re.sub(
                  r"^(PATIENT_NAME|PATIENT_|NAME_)", "", patient
            )
            for term in cleanup_terms:
                patient = patient.replace(term, "")
            
            patient = patient.strip()

            if patient in invalid_patients:
                 continue

            if len(patient.split()) > 4:
                 continue

            if patient:
                patients.append(patient)
        
    return list(set(patients))

def extract_generic_patient(text):
    #Extract the patient name using generic patterns

    patterns = [

        r"PATIENT'S NAME[:\s]+([A-Z ,'-]+)",

        r"PATIENT NAME[:\s]+([A-Z ,'-]+)",

        r"PATIENT\s*:\s*(.*?)\s+PROV:",

        r"PATIENT\s*:\s*([A-Z]+(?:\s+[A-Z]+){1,3})",

        r"CONFIDENTIAL HEALTH PLAN INFORMATION FOR[:\s]+(?:DATE REQUEST RECEIVED\s+)?([A-Z]+(?:\s+[A-Z]+){1,3})",

        #r"MEMBER ID[:\s]+([A-Z ,'-]+)",
        
        #r"MEMBER[:\s]+([A-Z ,'-]+)",

        r"NAME\s*:\s*([A-Z\s]+?)(?:\s+ID|\s+SR|$)",
    ]

    text_upper = text.upper()

    for pattern in patterns:
          match = re.search(pattern, text_upper)

          if match:
                patient = match.group(1).strip()

                patient = re.sub(r"^(PATIENT_NAME_|PATIENT_|NAME_)", "", patient)

                cleanup_terms = [
                    " MEMBER ID NUMBER",
                    " MEMBER ID",
                    " MEMBER",
                    " HCID NUMBER",
                    " HCID",
                    " PATIENT DOB",
                    " ACCOUNT NUMBER",
                    " SERVICE DATE",
                    " PATIENT ACCT",
                    " PATIENT ACCT#",
                    " PATIENT ACCOUNT",
                    " RCID NUMBER",
                    " DATE",
                    " OPER",
                    " PPO",
                    " POS",
                    " HSA",
                    " MO",
                    " WE",
                ]

                invalid_patients = {
                    "OPER",
                    "PATIENT",
                    "MEMBER",
                    "NAME",
                    "PROVIDER",
                    "EEE TAXPAYER",
                    "ARE CONDITION TORECEIVE NOTICE",
                    "AN",
                    "-",
                    "TANVI",
                }
                
                for term in cleanup_terms:
                    patient = patient.replace(term, "")

                if patient in invalid_patients:
                    continue

                print(f"PATTERN USED: {pattern}")
                print(f"MATCH VALUE : {patient}")

                return patient
    
    return "UNKNOWN_PATIENT"

def extract_generic_dos(text):
      # Extract the DOS using common heatlhcare patterns

    patterns = [
        r"DOS[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",

        r"DATE OF SERVICE[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",

        r"SERVICE DATE[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",

        r"DATES OF SERVICE[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",

        r"DATE\(S\)\s+OF\s+SERVICE[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",

        r"SERVICE\s+FROM\s+DATE\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
      ]

    text_upper = text.upper()

    for pattern in patterns:
        match = re.search(pattern, text_upper)

        if match:
            return match.group(1).replace("/", "-")
        
    fallback_patterns = [
         
        r"SERVICE\s+FROM\s+DATE.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",

        r"SERVICE\s+DATE.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",

        r"DATE(?:\(S\))?\s+OF\s+SERVICE.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",

        r"PROVIDER.*?SERVICE\s+FROM.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
    ]

    for pattern in fallback_patterns:
        match = re.search(
              pattern,
              text_upper,
              re.DOTALL
        )
            
    return "00-00-0000"

def extract_all_dos(text):
    text_upper = text.upper()

    date_pattern = r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"

    matches = re.findall(date_pattern, text_upper)

    valid_dates = []

    for date_str in matches:
        try:
            clean_date = date_str.replace("-", "/")
            parts = clean_date.split("/")
            
            if len(parts[2]) == 2:
                year = int("20" + parts[2])
            else:
                year = int(parts[2])

            month = int(parts[0])
            day = int(parts[1])

            dt = datetime(year, month, day)
            
            valid_dates.append(dt)

        except:
            continue

    return valid_dates

def get_oldest_claim_year(text):
    dates = extract_all_dos(text)

    if not dates:
        return None
    
    oldest_date = min(dates)

    today = datetime.today()

    age_days = (today - oldest_date).days

    if age_days >= 365 and age_days <= 1095:
        return str(oldest_date.year)
    
    return None

def extract_state(text):

    text_upper = text.upper()

    if "ABA CENTERS" in text_upper:

        start = text_upper.find("ABA CENTERS")

        print("\n===== ABA BLOCK =====")
        print(text_upper[start:start+400])
        print("=====================\n")

    state_map = {

        "ALABAMA": "AL",
        "ALASKA": "AK",
        "ARIZONA": "AZ",
        "ARKANSAS": "AR",
        "CALIFORNIA": "CA",
        "COLORADO": "CO",
        "CONNECTICUT": "CT",
        "DELAWARE": "DE",
        "FLORIDA": "FL",
        "GEORGIA": "GA",
        "HAWAII": "HI",
        "IDAHO": "ID",
        "ILLINOIS": "IL",
        "INDIANA": "IN",
        "IOWA": "IA",
        "KANSAS": "KS",
        "KENTUCKY": "KY",
        "LOUISIANA": "LA",
        "MAINE": "ME",
        "MARYLAND": "MD",
        "MASSACHUSETTS": "MA",
        "MICHIGAN": "MI",
        "MINNESOTA": "MN",
        "MISSISSIPPI": "MS",
        "MISSOURI": "MO",
        "MONTANA": "MT",
        "NEBRASKA": "NE",
        "NEVADA": "NV",
        "NEW HAMPSHIRE": "NH",
        "NEW JERSEY": "NJ",
        "NEW MEXICO": "NM",
        "NEW YORK": "NY",
        "NORTH CAROLINA": "NC",
        "NORTH DAKOTA": "ND",
        "OHIO": "OH",
        "OKLAHOMA": "OK",
        "OREGON": "OR",
        "PENNSYLVANIA": "PA",
        "RHODE ISLAND": "RI",
        "SOUTH CAROLINA": "SC",
        "SOUTH DAKOTA": "SD",
        "TENNESSEE": "TN",
        "TEXAS": "TX",
        "UTAH": "UT",
        "VERMONT": "VT",
        "VIRGINIA": "VA",
        "WASHINGTON": "WA",
        "WEST VIRGINIA": "WV",
        "WISCONSIN": "WI",
        "WYOMING": "WY",

        # Territorios
        "DISTRICT OF COLUMBIA": "DC",
        "PUERTO RICO": "PR",
        "GUAM": "GU",
        "VIRGIN ISLANDS": "VI",

        # Casos ABA
        "PA": "PA",
        "NJ": "NJ",
        "GA": "GA",
        "RI": "RI",

        # ABA Centers of America
        "AMERICA": "COA",
    }

    for state_name in state_map.keys():
        if f"ABA CENTERS OF {state_name}" in text_upper:
            print(f"STATE FOUND: {state_name}")
            return state_map[state_name]
        
    for state_name in state_map.keys():
        search_text = f"{state_name} ABA CENTERS"

        if search_text in text_upper:
            print(f"STATE FOUND: {state_name} ABA Centers")
            return state_map[state_name]
        
    adress_matches = re.findall(
        r"\b([A-Z]{2})\s+\d{5}(?:-\d{4}?)",
        text_upper
    )

    #Temporal debug
    print("\n===== ADRESS STATES =====")
    print(adress_matches)
    print("=========================\n")

    if adress_matches:
        state_code = adress_matches[-1]
        if state_code in state_map.values():
            print(f"STATE MATCH FROM ADRESS: {state_code}")
            return state_code
        
    if "ABA CENTERS OF" in text.upper():
        start = text_upper.find("ABA CENTERS OF")
        print("\n===== ABA DEBUG =====")
        print(text_upper[start:start+300])
        print("=====================\n")
    #temporal debug
    if state_name not in state_map:

        print("\n===== UNKNOWN STATE =====")
        print(state_name)
        print("=========================\n")

    return "UNK"