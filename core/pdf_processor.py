from pdf2image import convert_from_path
import numpy as np
import os
import sys


def _app_base_dir():
    """
    Returns the base directory where bundled resources live.

    - In PyInstaller one-folder / one-file builds: sys._MEIPASS points to the
      extraction dir that contains bundled data files.
    - In normal Python execution: use repo root (one level above /core).
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_poppler_path():
    base_dir = _app_base_dir()

    poppler_path = os.path.join(
        base_dir,
        "assets",
        "poppler",
        "Library",
        "bin",
    )
    return poppler_path


def pdf_to_image(pdf_path):
    poppler_path = get_poppler_path()

    # Keep these prints if you need diagnostics; otherwise you can remove later
    print("POPPLER PATH:", poppler_path)
    print("EXISTS:", os.path.exists(poppler_path))

    if not os.path.exists(poppler_path):
        raise FileNotFoundError(f"Poppler not found at: {poppler_path}")

    pages = convert_from_path(
        pdf_path,
        first_page=1,
        last_page=1,
        dpi=200,  # optimized for OCR
        poppler_path=os.path.normpath(poppler_path),
    )

    return np.array(pages[0])