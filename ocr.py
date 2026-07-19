import json

import easyocr
import numpy as np
from mss import mss
from PIL import Image


class OCRReader:
    def __init__(self):
        print("Loading EasyOCR... (first launch may take a while)")
        self.reader = easyocr.Reader(["en"], gpu=False)
        print("EasyOCR loaded!")

    def read_chat(self):
        with open("config.json", "r") as f:
            region = json.load(f)

        with mss() as sct:
            screenshot = sct.grab(region)

        image = Image.frombytes(
            "RGB",
            screenshot.size,
            screenshot.rgb
        )

        image = np.array(image)

        results = self.reader.readtext(
            image,
            detail=1,
            paragraph=False,
            allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789[]:.,!'?-()/ "
        )

        lines = []

        for _, text, confidence in results:
            # Ignore garbage with very low confidence
            if confidence < 0.40:
                continue

            text = text.strip()

            if not text:
                continue

            lines.append(text)

        return "\n".join(lines)