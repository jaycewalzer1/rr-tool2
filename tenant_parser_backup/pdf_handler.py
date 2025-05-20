from tenant_parser.optimized_ocr_processor import process_pdf_with_ocr
from tenant_parser.logger import logger

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF using optimized OCR processing.
    """
    try:
        # Process PDF with optimized OCR
        processed_pages = process_pdf_with_ocr(pdf_path)
        
        # Combine text from all pages
        text = ""
        for page in processed_pages:
            text += page['text'] + "\n"
            
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
        return ""