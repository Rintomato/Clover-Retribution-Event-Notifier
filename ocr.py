import json

import cv2
import numpy as np
from mss import mss
from PIL import Image
from rapidocr import EngineType, LangDet, LangRec, ModelType, OCRVersion, RapidOCR


class OCRReader:
    def __init__(self):
        print("Loading RapidOCR... (first launch may take a while)")
        # RapidOCR 3.9.x configuration.
        # Lightweight ONNX Runtime + English PP-OCRv4 mobile models.
        self.reader = RapidOCR(
            params={
                "Det.engine_type": EngineType.ONNXRUNTIME,
                "Det.lang_type": LangDet.EN,
                "Det.model_type": ModelType.MOBILE,
                "Det.ocr_version": OCRVersion.PPOCRV4,
                "Rec.engine_type": EngineType.ONNXRUNTIME,
                "Rec.lang_type": LangRec.EN,
                "Rec.model_type": ModelType.MOBILE,
                "Rec.ocr_version": OCRVersion.PPOCRV4,
            }
        )
        print("RapidOCR loaded!")

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

        # cls (angle classification) stays disabled to match the old
        # use_angle_cls=False behavior -- chat text is never rotated.
        result = self.reader(image, use_cls=False)

        lines = []
        debug_lines = []

        if result and result.txts:
            for text, score in zip(result.txts, result.scores):
                text = text.strip()
                confidence = float(score)

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
