import os
from werkzeug.utils import secure_filename
from tenant_parser import export_rent_roll_data_with_ocr

def run_pdf_processing(pdf_path):
    """
    Processes a PDF file and returns the path to the resulting Excel file.
    
    Args:
        pdf_path (str): Path to the PDF file.
        
    Returns:
        str: Path to the processed Excel file.
    """
    # Extract the user email (using a placeholder for MVP)
    user_email = "test@example.com"
    
    # Ensure output directory exists
    master_db_folder = "master_database"
    os.makedirs(master_db_folder, exist_ok=True)
    
    # Define output file path
    output_path = os.path.join(master_db_folder, f"{secure_filename(user_email)}_master_database.xlsx")
    
    # Process the PDF
    export_rent_roll_data_with_ocr(user_email, pdf_path)
    
    return output_path