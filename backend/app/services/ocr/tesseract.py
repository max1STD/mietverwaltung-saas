"""OCR-Wrapper um Tesseract + PyMuPDF für PDF-Belege."""
from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF
import pytesseract
from PIL import Image


def extract_text_from_pdf(file_path: str | Path) -> str:
    """Extrahiert Text aus einem PDF: erst eingebetteter Text, dann OCR als Fallback."""
    path = Path(file_path)
    text_parts: list[str] = []

    doc = fitz.open(str(path))
    try:
        for page in doc:
            embedded = page.get_text()
            if embedded.strip():
                text_parts.append(embedded.strip())
            else:
                pix = page.get_pixmap(dpi=200)
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                ocr_text = pytesseract.image_to_string(img, lang="deu")
                if ocr_text.strip():
                    text_parts.append(ocr_text.strip())
    finally:
        doc.close()

    return "\n\n".join(text_parts)


def extract_text_from_image(file_path: str | Path) -> str:
    """OCR auf einem Bild (PNG/JPG/...)."""
    img = Image.open(str(file_path))
    return pytesseract.image_to_string(img, lang="deu").strip()


def extract_text(file_path: str | Path, mime_type: str | None = None) -> str:
    """Wählt automatisch PDF oder Bild-OCR."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if mime_type and "pdf" in mime_type:
        return extract_text_from_pdf(path)
    if suffix in {".pdf"}:
        return extract_text_from_pdf(path)
    return extract_text_from_image(path)
