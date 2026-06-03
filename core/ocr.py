# ============================================================================
# Automatic Letter Reader for workload Assignations
#
# Copyright (c) 2026 ABA Centers of America
# All Rights Reserved.
#
# Proprietary and Confidential.
# For internal use only.
#
# Unauthorized copying, distribution, modification, or disclosure
# of this software is strictly prohibited.
# ============================================================================

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
    """Multi-payer support OCR supporting different configurations for diferent payers"""

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

    def preprocess(self, image, alpha=1.6, beta=10, blur_kernel=3, threshold_block_size=31):

        """
        Preprocess image for OCR with configurable parameters.
        
        Args:
            image: Input image (BGR or grayscale)
            alpha: Scale factor for brightness adjustment
            beta: Offset for brightness adjustment
            blur_kernel: Kernel size for Gaussian blur (must be odd)
            threshold_block_size: Block size for adaptive threshold (must be odd)
        
        Returns:
            Processed binary image
        """

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        gray = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
        gray = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)

        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            threshold_block_size,
            2,
        )

        return thresh

    def read_with_boxes(self, image, payer_config=None):

        """
        Read text from image with bounding boxes using Tesseract.
        
        Args:
            image: Input image
            payer_config: Optional dict with payer-specific Tesseract config.
                         Supported keys:
                         - 'psm': Page Segmentation Mode (0-13, default 6)
                         - 'oem': OCR Engine Mode (0-3, default 3)
                         - 'lang': Language (default 'eng')
                         - 'alpha': Brightness scale (default 1.6)
                         - 'beta': Brightness offset (default 10)
                         - 'blur_kernel': Gaussian blur kernel (default 3)
                         - 'threshold_block_size': Adaptive threshold block size (default 31)
        
        Returns:
            List of dicts with keys: 'text', 'top', 'left', 'width', 'height', 'confidence'
        """

        try:
            # Set Defaults
            config_params = {
                'psm': 6,
                'oem': 3,
                'lang': 'eng',
                'alpha': 1.6,
                'beta': 10,
                'blur_kernel': 3,
                'threshold_block_size': 31
            }

            # Override with payer-specific config if provided
            if payer_config:
                config_params.update(payer_config)

            # Preprocess with payer Specific parameters
            processed = self.preprocess(
                image,
                alpha=config_params['alpha'],
                beta=config_params['beta'],
                blur_kernel=config_params['blur_kernel'],
                threshold_block_size=config_params['threshold_block_size']
            )

            # Build Tesseract config string
            config =(
                f"--oem {config_params['oem']} "
                f"--psm {config_params['psm']} "
                f"-l {config_params['lang']} "
            )

            data = pytesseract.image_to_data(
                processed,
                config=config,
                output_type=pytesseract.Output.DICT
            )

            lines =[]
            for i in range(len(data["text"])):
                text = data["text"][i].strip()
                if len(text) < 2:
                    continue

                lines.append(
                    {
                        "text": text,
                        "top": data["top"][i],
                        "left": data["left"][i],
                        "width": data["width"][i],
                        "height": data["height"][i],
                        "confidence": float(data["conf"][i]) if data["conf"][i] != '-1' else 0.0
                    }
                )

            return lines
        except Exception as e:
            return []