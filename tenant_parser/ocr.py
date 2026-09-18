"""PDF text extraction and OCR.

Rent rolls are usually a scanned or vector table that ``get_text()`` returns as
an unusable jumble, so each relevant page is rendered to a bitmap and read with
Tesseract instead. The embedded text layer is still used, but only to locate
which pages are worth rendering and to find the property address.
"""

from __future__ import annotations

import io
import logging
from collections.abc import Iterator

import pymupdf
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)

# 300 dpi is the lowest resolution at which Tesseract reliably separates the
# narrow rent columns; anything lower merges "$24.00" into the adjacent cell.
RENDER_DPI = 300

# PSM 6 treats the page as one uniform block of text, which keeps table rows on
# a single line. OEM 3 selects the default LSTM engine.
TESSERACT_CONFIG = "--psm 6 --oem 3"

CONTRAST_BOOST = 2

RENT_ROLL_MARKER = "rent roll"


def extract_text(pdf_path: str) -> str:
    """Concatenate the embedded text layer of every page."""
    with pymupdf.open(pdf_path) as pdf:
        return "".join(page.get_text() for page in pdf)


def locate_rent_roll_pages(pdf_path: str) -> list[int]:
    """Zero-based page numbers whose text mentions a rent roll."""
    with pymupdf.open(pdf_path) as pdf:
        pages = [
            number
            for number in range(pdf.page_count)
            if RENT_ROLL_MARKER in pdf[number].get_text().lower()
        ]
    logger.info("located %d rent roll page(s)", len(pages))
    return pages


def read_pages(pdf_path: str, page_numbers: list[int]) -> Iterator[list[str]]:
    """Yield the OCR'd lines of each requested page, one list per page."""
    with pymupdf.open(pdf_path) as pdf:
        for number in page_numbers:
            pixmap = pdf[number].get_pixmap(dpi=RENDER_DPI)
            with Image.open(io.BytesIO(pixmap.tobytes())) as image:
                yield read_image(image).splitlines()


def read_image(image: Image.Image) -> str:
    """OCR a page bitmap after grayscale, sharpen and contrast preprocessing."""
    prepared = image.convert("L").filter(ImageFilter.SHARPEN)
    prepared = ImageEnhance.Contrast(prepared).enhance(CONTRAST_BOOST)
    return pytesseract.image_to_string(prepared, config=TESSERACT_CONFIG)
