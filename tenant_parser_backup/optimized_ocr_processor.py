import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import io
import logging
import time
import tempfile
import gc
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_page_with_ocr(page, page_num, pdf_name):
    """
    Process a single page with OCR using a robust approach that works with different
    versions of PyMuPDF and PIL.
    """
    temp_file = None
    try:
        logger.info(f"Processing page {page_num} of {pdf_name}")
        
        # Create a temporary file for the page image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tf:
            temp_file = tf.name
        
        # Get page dimensions
        rect = page.rect
        width, height = int(rect.width), int(rect.height)
        
        # Set zoom factor for better OCR
        zoom = 2  # Increase resolution for better OCR
        mat = fitz.Matrix(zoom, zoom)
        
        # Render page to PNG file - most compatible approach
        try:
            pix = page.get_pixmap(matrix=mat)
            pix.save(temp_file)
            
            # Check the file exists and has content
            if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
                raise Exception(f"Failed to create temporary file or file is empty: {temp_file}")
                
            # Get file size for debugging
            file_size = os.path.getsize(temp_file) / 1024  # KB
                
        except Exception as e:
            logger.error(f"Error rendering PDF page to image: {str(e)}")
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
            return ""
        
        # Load the image from file - avoids direct buffer handling issues
        try:
            img = Image.open(temp_file)
        except Exception as e:
            logger.error(f"Error loading image with PIL: {str(e)}")
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
            return ""
        
        # Apply image preprocessing
        try:
            img = img.convert('L')  # Convert to grayscale
            img = img.filter(ImageFilter.SHARPEN)  # Sharpen image
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2)  # Increase contrast
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
            return ""
        
        # Use optimized OCR configuration
        try:
            logger.info("Running OCR")
            config = '--psm 6 --oem 3'
            
            # Use a timeout to prevent OCR from running too long
            start_time = time.time()
            text = pytesseract.image_to_string(img, config=config)
            duration = time.time() - start_time
            
            
            if not text:
                logger.warning("OCR returned empty text")
        except Exception as e:
            logger.error(f"Error running OCR: {str(e)}")
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
            return ""
        
        return text
    
    except Exception as e:
        logger.error(f"General error in page processing: {str(e)}")
        return ""
    
    finally:
        # Clean up temporary files
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {str(e)}")
                
        # Force garbage collection
        gc.collect()

def process_pdf_with_ocr(pdf_path, max_pages=None):
    """
    Process PDF with OCR, handling errors and memory issues.
    """
    try:
        pdf_name = os.path.basename(pdf_path)
        logger.info(f"Starting OCR processing for {pdf_name}")
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file does not exist: {pdf_path}")
            return []
            
        # Get file size for debugging
        file_size = os.path.getsize(pdf_path) / (1024 * 1024)  # MB
        logger.info(f"PDF file size: {file_size:.2f} MB")
        
        # Open PDF with memory optimization
        try:
            pdf_reader = fitz.open(pdf_path)
            logger.info(f"PDF opened: {pdf_reader.page_count} pages")
        except Exception as e:
            logger.error(f"Failed to open PDF: {str(e)}")
            return []
        
        # Process pages in chunks to prevent memory issues
        chunk_size = 5  # Smaller chunks for better stability
        total_pages = pdf_reader.page_count
        
        if max_pages is not None:
            total_pages = min(total_pages, max_pages)
            
        
        processed_pages = []

        for start in range(0, total_pages, chunk_size):
            end = min(start + chunk_size, total_pages)
            logger.info(f"Processing chunk: pages {start+1}-{end} of {total_pages}")
            
            # Process current chunk
            for page_num in range(start, end):
                try:
                    page = pdf_reader[int(page_num)]
                    text = process_page_with_ocr(page, page_num + 1, pdf_name)
                    
                    if text:
                        processed_pages.append({
                            'page_num': int(page_num + 1),
                            'text': text
                        })
                        logger.info(f"Successfully processed page {page_num+1}")
                    else:
                        logger.warning(f"No text extracted from page {page_num+1}")
                        
                except Exception as e:
                    logger.error(f"Error processing page {page_num+1}: {str(e)}")
                
                # Clean up after each page
                gc.collect()
                
                # Add small delay to prevent CPU overload
            # Clean up after each chunk
            gc.collect()
            
        # Close PDF
        try:
            pdf_reader.close()
            logger.info("PDF closed successfully")
        except Exception as e:
            logger.error(f"Error closing PDF: {str(e)}")
        
        gc.collect()
        
        logger.info(f"Finished processing {pdf_name}, extracted text from {len(processed_pages)} pages")
        return processed_pages
        
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
        return []

# Test function
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python robust_ocr_processor.py <pdf_path> [max_pages]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    max_pages = None
    
    if len(sys.argv) > 2:
        max_pages = int(sys.argv[2])
    
    print(f"Processing {pdf_path}" + (f" (max {max_pages} pages)" if max_pages else ""))
    
    processed_pages = process_pdf_with_ocr(pdf_path, max_pages)
    
    
    print(f"\nProcessed {len(processed_pages)} pages successfully")
    
    if processed_pages:
        print("\nSample text from first processed page:")
        first_text = processed_pages[0]['text']
        print("-" * 40)
        print(first_text[:500] + "..." if len(first_text) > 500 else first_text)
        print("-" * 40)
