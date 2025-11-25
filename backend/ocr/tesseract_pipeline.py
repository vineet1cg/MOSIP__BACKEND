from PIL import Image
import pytesseract
import os
import cv2
import numpy as np

class TesseractPipeline:
    def __init__(self, lang='eng'):
        self.lang = lang

    def predict(self, pil_image):
        # image_to_data returns word-level info
        data = pytesseract.image_to_data(pil_image, lang=self.lang, output_type=pytesseract.Output.DICT)
        n = len(data['text'])
        words = []
        confs = []
        lines = {}
        for i in range(n):
            text = data['text'][i].strip()
            conf = float(data['conf'][i]) if data['conf'][i] != '-1' and data['conf'][i] != '' else 0.0
            if text:
                words.append(text)
                confs.append(conf/100.0)
                line_num = f"{data['page_num'][i]}_{data['block_num'][i]}_{data['par_num'][i]}_{data['line_num'][i]}"
                lines.setdefault(line_num, []).append((text, conf/100.0))
        text = " ".join(words)
        avg_conf = float(sum(confs)/len(confs)) if confs else 0.0
        # capture detailed lines
        line_texts = {"_".join(k.split("_")[1:]): {"words": [w for w,_ in v], "avg_conf": float(sum([c for _,c in v])/len(v)) if v else 0.0} for k,v in lines.items()}
        return {"text": text, "score": avg_conf, "words": words, "word_confidences": confs, "lines": line_texts}

    def image_to_boxes(self, path):
        img = Image.open(path).convert("RGB")
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        boxes = []
        n = len(data['level'])
        w, h = img.size
        for i in range(n):
            text = data['text'][i].strip()
            if not text:
                continue
            boxes.append({
                "left": int(data['left'][i]),
                "top": int(data['top'][i]),
                "width": int(data['width'][i]),
                "height": int(data['height'][i]),
                "text": text,
                "conf": float(data['conf'][i]) if data['conf'][i] != '-1' else 0.0
            })
        return {"boxes": boxes, "image_size": [w, h]}
