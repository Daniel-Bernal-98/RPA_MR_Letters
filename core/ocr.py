import os
import sys

import cv2
import pytesseract


def _app_base_dir():
    """
    Returns the base directory where bundled resources live.

    - In PyInstaller builds: sys._MEIPASS points to the extracted bundle dir.
    - In normal execution: use repo root (one level above /core).
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class OCRReader:
    def __init__(self):
        base_dir = _app_base_dir()

        tesseract_path = os.path.join(base_dir, "assets", "tesseract", "tesseract.exe")
        tessdata_path = os.path.join(base_dir, "assets", "tesseract", "tessdata")

        # Validate existence to fail fast with a clear error
        if not os.path.exists(tesseract_path):
            raise FileNotFoundError(f"Tesseract not found at: {tesseract_path}")
        if not os.path.exists(tessdata_path):
            raise FileNotFoundError(f"Tesseract tessdata not found at: {tessdata_path}")

        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        os.environ["TESSDATA_PREFIX"] = tessdata_path

    def preprocess(self, image):
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        gray = cv2.convertScaleAbs(gray, alpha=1.6, beta=10)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            31,
            2,
        )

        return thresh

    def read_with_boxes(self, image):
        try:
            processed = self.preprocess(image)

            config = (
                "--oem 3 "
                "--psm 6 "
                "-l eng "
            )

            data = pytesseract.image_to_data(
                processed,
                config=config,
                output_type=pytesseract.Output.DICT,
            )

            lines = []
            for i in range(len(data["text"])):
                text = data["text"][i].strip()
                if len(text) < 2:
                    continue

                lines.append(
                    {
                        "text": text,
                        "top": data["top"][i],
                        "left": data["left"][i],
                    }
                )

            return lines

        except Exception as e:
            print("OCR ERROR:", e)
            return []