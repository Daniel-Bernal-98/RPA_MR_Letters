import re
import numpy as np


def extract_text_from_pdf(pdf_path):

    #Step 1: Convert PDF to images

    pages = convert_from_path(pdf_path) #Convert PDF to images
    img= np.array(pages[0]) #Convert first page to numpy array

    #Step 2: Initialize EasyOCR reader
    reader =easyocr.Reader(['en']) #Initialize EasyOCR reader for English language
    results = reader.readtext(img) #Extract text from image
    complete_text = " ".join(results) #Join extracted text into a single string
    
    #Step 3: Extract data using regular expressions

    match_name = re.search(r"(?:Paciente|Patient|Nombre|Name)[:\s]+([A-Z\s]{5,30})", # Detect posible combinations of keywords for the patient name
                           complete_text, re.I)  #Extract name using regex
    
    match_dos = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", complete_text) #Extract date of service using regex

    match_claim_number = re.search(r"(?:Claim|Reclamo|ID|Number)[:\s#]+([A-Z0-9]{5,15})",
        complete_text,
        re.I
    )

    # Data cleaning

    patient = match_name.group(1).strip().replace(" ", "_") if match_name else "Patient Not Found" #Clean patient name
    date_of_service = match_dos.group(1).replace("/","-") if match_dos else "00-00-0000" #Clean date of service
    claim_number = match_claim_number.group(1).strip() if match_claim_number else "Claim Number Not Found" #Clean claim number

    return patient, date_of_service, claim_number