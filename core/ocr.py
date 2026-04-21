import easyocr

class OCRReader:
    def __init__(self):
        self.reader =easyocr.Reader(['en']) #Initialize EasyOCR reader for English language

    def read(self, image):
        return self.reader.readtext(image, detail=0) #Extract text from image without details