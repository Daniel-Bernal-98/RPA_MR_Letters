import os
import re
import easyocr #Highly accurate OCR library
import numpy as np
from pdf2image import convert_from_path #Converts PDF to images

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

def organize_file(pdf_path):
    try:
        patient, date_of_service_, claim_number = extract_text_from_pdf(pdf_path) #Extract data from PDF

        output_dir = "./Processed_Claims" #Directory to save organized files
        patient_dir = os.path.join(output_dir, patient) #Create patient directory
        
        if not os.path.exists(patient_dir):
            os.makedirs(patient_dir) #Create directory if it doesn't exist

        new_file_name = f"{patient}_{date_of_service_}_{claim_number}.pdf" #Create new file name
        final_dir = os.path.join(patient_dir, new_file_name) #Create final directory for the file

        os.rename(pdf_path, final_dir) #Move and rename the file

        return f"File organized successfully: {new_file_name}" #Return success message
    
    except Exception as e:
        #return an error message if something goes wrong
        return f"Error processing file: {os.path.basename(pdf_path)} - {str(e)}"



