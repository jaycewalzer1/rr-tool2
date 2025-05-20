"""
Script to directly process a PDF file using the tenant_parser module.
This helps troubleshoot issues with the PDF processing pipeline.
"""

import os
import sys
import traceback
import logging
from werkzeug.utils import secure_filename
from tenant_parser import export_rent_roll_data_with_ocr
import pandas as pd

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def process_pdf(user_email, pdf_path):
    """Process a PDF file directly using the tenant_parser module."""
    
    # Check if PDF file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file {pdf_path} does not exist.")
        return False
    
    # Check if it's a PDF
    if not pdf_path.lower().endswith('.pdf'):
        print(f"Error: {pdf_path} is not a PDF file.")
        return False
    
    # Setup folder paths
    MARKETING_FOLDER = "marketing_oms"
    MASTER_DB_FOLDER = "master_database"
    os.makedirs(MARKETING_FOLDER, exist_ok=True)
    os.makedirs(MASTER_DB_FOLDER, exist_ok=True)
    # Create user folder
    safe_email = secure_filename(user_email)
    user_folder = os.path.join(MARKETING_FOLDER, safe_email)
    os.makedirs(user_folder, exist_ok=True)
    
    # Copy PDF to user folder if it's not already there
    pdf_filename = os.path.basename(pdf_path)
    dest_path = os.path.join(user_folder, pdf_filename)
    # Copy the file only if it's not already in the user folder
    if pdf_path != dest_path:
        print(f"Copying {pdf_path} to {dest_path}")
        try:
            import shutil
            shutil.copy2(pdf_path, dest_path)
            print(f"Copied PDF to {dest_path}")
        except Exception as e:
            print(f"Error copying PDF: {str(e)}")
            return False
    
    # Process the PDF
    try:
        print(f"Processing {dest_path} for user {user_email}")
        export_rent_roll_data_with_ocr(user_email, dest_path)
        print("Processing completed successfully")
        
        # Check the Excel file
        excel_path = os.path.join(MASTER_DB_FOLDER, f"{safe_email}_master_database.xlsx")
        if os.path.exists(excel_path):
            print(f"Excel file created at {excel_path}")
            
            # Read the Excel file to check if data was extracted
            try:
                df = pd.read_excel(excel_path, sheet_name="Retail Tenants")
                rows = len(df)
                print(f"Found {rows} tenant entries in Excel file")
                
                if rows > 0:
                    print("\nSample data:")
                    print(df.head(3))
                    return True
                else:
                    print("No tenant entries were found in the Excel file")
                    return False
            except Exception as e:
                print(f"Error reading Excel file: {str(e)}")
                return False
        else:
            print(f"Error: Excel file was not created at {excel_path}")
            return False
    except Exception as e:
        error_message = f"Error processing PDF: {str(e)}"
        print(error_message)
        full_traceback = traceback.format_exc()
        
        # Log the error
        logger.error(error_message)
        logger.error(f"Full traceback:\n{full_traceback}")
        
        print(f"Full traceback:\n{full_traceback}")
        print("\nDetailed traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_pdf.py <email> <pdf_path>")
        sys.exit(1)
    
    user_email = sys.argv[1]
    pdf_path = sys.argv[2]
    if process_pdf(user_email, pdf_path):
        print("\nSuccess: PDF processed successfully and data extracted.")
    else:
        print("\nError: Failed to process PDF or extract data.")
        print("\nTroubleshooting steps:")
        print("1. Try running 'python add_test_data.py <email>' to add test data")
        print("2. Check if the tenant_parser module is properly installed")
        print("3. Make sure the PDF contains recognizable tenant information")
        print("4. Check if Tesseract OCR is installed and working")