import json

import cv2
import numpy as np
from mss import mss
from PIL import Image
from paddleocr import PaddleOCR


class OCRReader:
    def __init__(self):
        print("Loading PaddleOCR... (first launch may take a while)")
        self.reader = PaddleOCR(
            use_angle_cls=False,
            lang="en"
        )
        print("PaddleOCR loaded!")

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

        # Same upscale as your tests
        image = cv2.resize(
            image,
            None,
            fx=3,
            fy=3,
            interpolation=cv2.INTER_CUBIC
        )

        result = self.reader.ocr(image, cls=False)

        lines = []
        debug_lines = []

        if result and result[0]:
            for line in result[0]:
                text = line[1][0].strip()
                confidence = float(line[1][1])

                if confidence < 0.40:
                    continue

                if not text:
                    continue

                lines.append(text)
                debug_lines.append({
                    "text": text,
                    "confidence": confidence
                })

        return "\n".join(lines), debug_lines