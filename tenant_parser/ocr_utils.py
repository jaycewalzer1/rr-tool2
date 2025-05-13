from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from tenant_parser.optimized_ocr_processor import process_pdf_with_ocr
from tenant_parser.logger import logger
import os

def apply_ocr_to_image(image):
    """
    Use OCR to extract text from an image of a PDF page with horizontal alignment.
    """
    # Preprocess image: Convert to grayscale, enhance contrast
    image = image.convert('L')  # Grayscale
    image = image.filter(ImageFilter.SHARPEN)  # Sharpen the image
    image = ImageEnhance.Contrast(image).enhance(2)  # Increase contrast
    # OCR configuration
    config = "--psm 6 --oem 3"  # PSM 6 assumes a single uniform block of text; OEM 3 is the best model
    return pytesseract.image_to_string(image, config=config)

def locate_rent_roll_sections(pdf_path):
    """
    Scans each page in the PDF to identify rent roll sections using optimized OCR.
    """
    try:
        rent_roll_pages = set()
        processed_pages = process_pdf_with_ocr(pdf_path)

        # Expanded keyword list to catch more variations
        keywords = [
            "rent roll", "tenant list", "lease summary", "space occupancy",
            "retail tenants", "anchor tenants", "tenant roster", "lease matrix",
            "lease schedule", "tenancy schedule", "occupancy chart"
        ]

        for page in processed_pages:
            page_text = page.get('text', '').lower()
            page_num = page.get('page_num')

            # Line-by-line match increases robustness
            for line in page_text.splitlines():
                if any(keyword in line for keyword in keywords):
                    rent_roll_pages.add(page_num)
                    logger.info(
                        f"Rent Roll-like section detected on page {page_num} in {os.path.basename(pdf_path)}"
                    )
                    break  # Avoid double-logging the same page

        if not rent_roll_pages:
            logger.info(f"No rent roll-like sections found in {os.path.basename(pdf_path)}")

        return sorted(rent_roll_pages)

    except Exception as e:
        logger.error(f"Error locating rent roll sections in {pdf_path}: {str(e)}")
        return []



### Is this function used anywhere?
def split_line_into_columns(line, max_columns=58):
    """
    Splits a line of rent roll data into separate columns by spaces,
    up to a specified maximum number of columns.
    """
    # Split the line by spaces
    columns = line.split()
    # Ensure we have exactly `max_columns` columns, padding with empty strings if necessary
    return columns[:max_columns] + [''] * (max_columns - len(columns))