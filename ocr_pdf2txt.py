"""
ocr_pdf2txt.py — OCR module for scanned PDFs.

Usage:
    from ocr_pdf2txt import ocr_pdf
    text = ocr_pdf("path/to/scanned.pdf", dpi=300)

Description:
    - Uses PyMuPDF to render PDF pages
    - Detects page rotation using OpenCV
    - Preprocesses images for Tesseract OCR
    - Returns extracted text as a single string
    - Supports Slovak and English (lang="slk+eng")

Dependencies:
    pytesseract, PyMuPDF, opencv-python, numpy
Tesseract must be installed on the system.
"""

import fitz
import pytesseract
import cv2
import numpy as np

TESS_CONFIG = "--oem 3 --psm 6"
TESS_LANG = "slk+eng"


def _render_page(page, dpi=300):
    """Render page to numpy image, handle color channels safely."""
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)

    img = np.frombuffer(pix.samples, dtype=np.uint8)
    # Handle grayscale, RGB, or RGBA pages
    if pix.n == 1:
        img = img.reshape(pix.height, pix.width)
    else:
        img = img.reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:  # remove alpha channel if present
            img = img[:, :, :3]

    return img


def _detect_rotation(img):
    """Detect approximate rotation of text using OpenCV."""
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

    coords = np.column_stack(np.where(thresh > 0))
    angle = 0

    if coords.shape[0] > 0:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        if angle < -45:
            angle = 90 + angle

    return angle


def _preprocess(img):
    """Prepare image for OCR: grayscale + thresholding."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh


def _ocr_image(img):
    """Run Tesseract OCR on a preprocessed image."""
    return pytesseract.image_to_string(
        img,
        config=TESS_CONFIG,
        lang=TESS_LANG
    )


def ocr_pdf(pdf_path: str, dpi: int = 300) -> str:
    """
    Perform OCR on a scanned PDF and return extracted text.

    Parameters
    ----------
    pdf_path : str
        Path to the scanned PDF file.
    dpi : int, optional
        Resolution to render PDF pages (default is 300).

    Returns
    -------
    str
        OCR-extracted text from all pages concatenated.
    """
    pages_text = []

    with fitz.open(pdf_path) as doc:
        for page in doc:

            img = _render_page(page, dpi=dpi)

            angle = _detect_rotation(img)
            if abs(angle) > 2:
                h, w = img.shape[:2]
                M = cv2.getRotationMatrix2D((w // 2, h // 2), -angle, 1.0)
                img = cv2.warpAffine(img, M, (w, h))

            img = _preprocess(img)

            text = _ocr_image(img)
            pages_text.append(text)

    return "\n".join(pages_text)