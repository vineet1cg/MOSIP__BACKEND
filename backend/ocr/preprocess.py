import cv2
import numpy as np
from PIL import Image
import io
import os
from typing import Dict, Any
from pathlib import Path

def read_image(path: str):
    # supports PDF via pdf2image if needed
    if path.lower().endswith(".pdf"):
        try:
            from pdf2image import convert_from_path
            pages = convert_from_path(path, dpi=300)
            pil = pages[0]
            return pil
        except Exception:
            raise
    else:
        pil = Image.open(path).convert("RGB")
        return pil

def pil_to_cv2(pil: Image.Image):
    arr = np.array(pil)
    # convert RGB to BGR
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

def cv2_to_pil(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img)

def deskew_image(gray):
    coords = np.column_stack(np.where(gray > 0))
    if coords.size == 0:
        return gray
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = gray.shape[:2]
    center = (w//2, h//2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()

def detect_blur(gray):
    return variance_of_laplacian(gray)

def adaptive_threshold(gray):
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 25, 15)

def denoise(gray):
    return cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)

def perspective_correction(img):
    # attempt to find largest contour rectangle and warp
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            pts = approx.reshape(4,2)
            rect = order_points(pts)
            (tl, tr, br, bl) = rect
            widthA = np.linalg.norm(br - bl)
            widthB = np.linalg.norm(tr - tl)
            maxWidth = max(int(widthA), int(widthB))
            heightA = np.linalg.norm(tr - br)
            heightB = np.linalg.norm(tl - bl)
            maxHeight = max(int(heightA), int(heightB))
            dst = np.array([
                [0,0],
                [maxWidth-1, 0],
                [maxWidth-1, maxHeight-1],
                [0, maxHeight-1]
            ], dtype="float32")
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(img, M, (maxWidth, maxHeight))
            return warped
    return img

def order_points(pts):
    rect = np.zeros((4,2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def preprocess_image_from_path(path: str) -> Dict[str, Any]:
    pil = read_image(path)
    bgr = pil_to_cv2(pil)
    # perspective
    corrected = perspective_correction(bgr)
    gray = cv2.cvtColor(corrected, cv2.COLOR_BGR2GRAY)
    # denoise
    den = denoise(gray)
    # deskew
    deskewed = deskew_image(den)
    # threshold
    binary = adaptive_threshold(deskewed)
    # blur detection
    blur_var = detect_blur(deskewed)
    # brightness
    mean_brightness = float(deskewed.mean())
    pil_rgb = cv2_to_pil(corrected)
    return {
        "bgr": corrected,
        "pil_rgb": pil_rgb,
        "binary": Image.fromarray(binary),
        "quality": {"blur_variance": float(blur_var), "brightness": mean_brightness}
    }
