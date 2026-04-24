import pytesseract
import os
import cv2


class OCRReader:
    def __init__(self):
        # Ruta absoluta basada en el archivo
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        tesseract_path = os.path.join(base_dir, "assets", "tesseract", "tesseract.exe")
        tessdata_path = os.path.join(base_dir, "assets", "tesseract", "tessdata")

        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        os.environ["TESSDATA_PREFIX"] = tessdata_path

    def preprocess(self, image):
        # Asegurar que la imagen esté en escala de grises
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Aumentar contraste
        gray = cv2.convertScaleAbs(gray, alpha=1.6, beta=10)

        # Reducir ruido
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # Binarización adaptativa (mejor para escaneos)
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            31,
            2
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
                output_type=pytesseract.Output.DICT
            )

            lines = []

            for i in range(len(data["text"])):
                text = data["text"][i].strip()

                if len(text) < 2:
                    continue

                lines.append({
                    "text": text,
                    "top": data["top"][i],
                    "left": data["left"][i]
                })

            return lines

        except Exception as e:
            print("OCR ERROR:", e)
            return []