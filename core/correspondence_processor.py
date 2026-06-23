from core.ocr import OCRReader
from core.pdf_processor import pdf_to_image
from core.correspondence_extractor import (
    extract_generic_dos,
    extract_generic_patient,
    extract_generic_payer,
    extract_all_patients,
    extract_state,
    get_oldest_claim_year
)

import os
import shutil

ocr = OCRReader()

def correspondence_processor(pdf_path):

    pages = pdf_to_image(pdf_path)

    full_text = ""
    payer_text = ""

    for page_number, img in enumerate(pages):

        data = ocr.read_with_boxes(img)

        page_text = " ".join(
            item["text"]
            for item in data
            if item["text"].strip()
        )
        full_text += page_text + "\n"

        if page_number < 2:
            payer_text += page_text +"\n"

    payer = extract_generic_payer(payer_text)
    state = extract_state(full_text)
    print("\n===== STATE =====")
    print(state)
    print("========================\n")
    all_patients = extract_all_patients(full_text)
    print("\n===== ALL PATIENTS =====")
    print(all_patients)
    print("========================\n")
    if len(all_patients) > 1:
        patient = "MULTI_PATIENTS"
        dos = " "
        oldest_year = get_oldest_claim_year(full_text)
    else:
        patient = extract_generic_patient(full_text)
        dos = extract_generic_dos(full_text)
        oldest_year = None

        if dos == "00-00-0000":
            patient = "MISCELANEOUS"

    print("\n===== EXTRACTED VALUES =====")
    print(f"PAYER   : {payer}")
    print(f"STATE   : {state}")
    print(f"PATIENT : {patient}")
    print(f"DOS     : {dos}")
    print("============================\n")

    return payer, state, patient, dos, oldest_year


def sanitize_filename(value):

    if not value:
        return "UNKNOWN"

    invalid_chars = r'<>:"/\|?*'

    for char in invalid_chars:
        value = value.replace(char, "-")

    return value.strip()


def process_correspondence_folder(
    input_folder,
    output_folder,
    log_callback=None,
    progress_callback=None,
    current_file_callback=None
):

    files = [
        f for f in os.listdir(input_folder)
        if f.lower().endswith(".pdf")
    ]

    if not files:
        raise ValueError("No PDF files found.")

    results = []

    total = len(files)

    for index, file in enumerate(files, start=1):

        path = os.path.join(
            input_folder,
            file
        )

        try:

            if current_file_callback:
                current_file_callback(file)

            payer, state, patient, dos, oldest_year = correspondence_processor(path)

            safe_payer = sanitize_filename(payer)
            safe_state = sanitize_filename(state)
            safe_patient = sanitize_filename(patient)
            safe_dos = sanitize_filename(dos)

            if safe_patient == "MULTI_PATIENTS" and oldest_year:

                new_filename = (
                    f"{oldest_year}_"
                    f"{safe_payer}_"
                    f"{safe_state}_"
                    f"{safe_patient}_"
                    f"{safe_dos}.pdf"
                )

            else:

                new_filename = (
                    f"{safe_payer}_"
                    f"{safe_state}_"
                    f"{safe_patient}_"
                    f"{safe_dos}.pdf"
                )

            payer_folder = os.path.join(
                output_folder,
                safe_payer
            )

            os.makedirs(
                payer_folder,
                exist_ok= True
            )

            destination = os.path.join(
                payer_folder,
                new_filename
            )

            # Prevend overwriting existing files that could have the same name.

            base_name = os.path.splitext(new_filename)[0]
            extension = os.path.splitext(new_filename)[1]

            counter = 1

            while os.path.exists(destination):
                destination = os.path.join(
                    payer_folder,
                    f"{base_name}_{counter}{extension}"
                )

                counter += 1

            shutil.copy2(
                path,
                destination
            )

            result = {
                "archivo": file,
                "payer": payer,
                "patient": patient,
                "dos": dos,
                "output": new_filename,
                "status": "SUCCESS"
            }

            results.append(result)

            if log_callback:
                log_callback(
                    f"{file} -> {new_filename}"
                )

        except Exception as e:

            result = {
                "archivo": file,
                "payer": "ERROR",
                "patient": "ERROR",
                "dos": "ERROR",
                "output": "",
                "status": "ERROR",
                "error": str(e)
            }

            results.append(result)

            if log_callback:
                log_callback(
                    f"[ERROR] {file} -> {str(e)}"
                )

        finally:

            if progress_callback:
                progress_callback(
                    index,
                    total
                )

    if log_callback:

        success_count = len(
            [
                r for r in results
                if r["status"] == "SUCCESS"
            ]
        )

        error_count = len(
            [
                r for r in results
                if r["status"] == "ERROR"
            ]
        )

        log_callback("")
        log_callback("==============================")
        log_callback("CORRESPONDENCE SUMMARY")
        log_callback("==============================")
        log_callback(f"Processed: {total}")
        log_callback(f"Successful: {success_count}")
        log_callback(f"Errors: {error_count}")
        log_callback("==============================")

    return results