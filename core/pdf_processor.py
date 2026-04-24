from pdf2image import convert_from_path
import numpy as np
import os


def get_poppler_path():
    # Ruta absoluta basada en el archivo (NO cwd)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    poppler_path = os.path.join(
        base_dir,
        "assets",
        "poppler",
        "Library",
        "bin"
    )

    return poppler_path


def pdf_to_image(pdf_path):
    poppler_path = get_poppler_path()

    # Debug útil (puedes quitarlo luego)
    print("POPPLER PATH:", poppler_path)
    print("EXISTS:", os.path.exists(poppler_path))

    if not os.path.exists(poppler_path):
        raise Exception(f"Poppler not found at: {poppler_path}")

    pages = convert_from_path(
        pdf_path,
        first_page=1,
        last_page=1,
        dpi=200,  # optimizado para OCR
        poppler_path=os.path.normpath(poppler_path)
    )

    return np.array(pages[0])