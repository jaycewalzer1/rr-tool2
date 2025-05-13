from tenant_parser.logger import logger
from tenant_parser.optimized_ocr_processor import process_pdf_with_ocr
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
            # Add type checking to handle different data structures
            if isinstance(page, dict) and 'text' in page:
                text += page['text'] + "\n"
            elif isinstance(page, list) and len(page) > 0:
                # If page is a list, try to find text in its elements
                for item in page:
                    if isinstance(item, dict) and 'text' in item:
                        text += item['text'] + "\n"
                    elif isinstance(item, str):
                        text += item + "\n"
            elif isinstance(page, str):
                # If page is just a string, add it directly
                text += page + "\n"
            else:
                logger.warning(f"Unexpected page data type: {type(page)}")
                logger.warning(f"Page content: {page}")
                
        return text
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
        return ""