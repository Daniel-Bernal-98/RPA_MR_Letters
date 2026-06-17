from core.ocr import OCRReader
from core.pdf_processor import pdf_to_image
from core.correspondence_extractor import extract_generic_dos, extract_generic_patient, extract_generic_payer

ocr = OCRReader()

def correspondence_processor(pdf_path):
    pages = pdf_to_image(pdf_path)

    payer_text = ""
    full_text = ""

    for img in pages:
        data = ocr.read_with_boxes(img)

        page_text = " ".join(
            item["text"]
            for item in data
            if item["text"].strip()
        )
    
        full_text += page_text + "\n"

    for img in pages[:2]:
        data = ocr.read_with_boxes(img)

        page_text = " ".join(
            item["text"]
            for item in data
            if item["text"].strip()
        )

        payer_text += page_text + "\n"
    
    payer = extract_generic_payer(payer_text)
    patient = extract_generic_patient(full_text)
    dos = extract_generic_dos(full_text)

    print("\n===== CORRESPONDENCE TEST =====")
    print(f"Payer: {payer}")
    print(f"Patient: {patient}")
    print(f"DOS: {dos}")
    print("===============================\n")

    return payer, patient, dos
