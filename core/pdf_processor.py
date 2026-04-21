from pdf2image import convert_from_path
import numpy as np
import os

def pdf_to_image(pdf_path):
    poppler_path = os.path.join("assets", "poppler", "bin")

    pages = convert_from_path(
        pdf_path,
        first_page=1,
        last_page=1,
        poppler_path=poppler_path
    )

    return np.array(pages[0])