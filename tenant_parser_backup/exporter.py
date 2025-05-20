import sys
import os
from tenant_parser.pdf_handler import *
from tenant_parser.rent_roll_parser import * 
from tenant_parser.address_utils import *
from tenant_parser.excel_utils import *
from tenant_parser.tenant_utils import *
from tenant_parser.logger import logger
from tenant_parser.ocr_utils import *
from tenant_parser.tenant_logic import *
from werkzeug.utils import secure_filename
from openpyxl import load_workbook, Workbook
import pandas as pd
import fitz
import io
from tenant_parser.constants import months_map

def export_rent_roll_data_with_ocr(user_email, pdf_path, data_sheet_name="Retail Tenants"):
    """
    Processes a rent roll from a PDF file using OCR, extracts tenant and address information,
    and saves the structured output into a user-specific Excel workbook.

    Args:
        user_email (str): Identifier for the user's output Excel filename.
        pdf_path (str): Path to the PDF file containing the rent roll.
        data_sheet_name (str): Sheet name where the tenant data should be saved (default is 'Retail Tenants').

    Workflow:
        - Loads or creates the user's master Excel file.
        - Uses OCR to process rent roll pages identified in the PDF.
        - Extracts tenant entries and address metadata.
        - Cleans and structures the data, removing unusable or malformed entries.
        - Updates or appends to the Excel sheet accordingly.
    """
    filename = os.path.basename(pdf_path)
    safe_user_folder = secure_filename(user_email)
    os.makedirs("master_database", exist_ok=True)
    excel_path = os.path.join("master_database", f"{safe_user_folder}_master_database.xlsx")

    workbook = load_workbook(excel_path) if os.path.exists(excel_path) else Workbook()
    sheet = workbook[data_sheet_name] if data_sheet_name in workbook.sheetnames else workbook.create_sheet(data_sheet_name)

    if sheet.max_row == 1:
        sheet.append(["PDF Name", "Tenant Name", "Square Feet", "Lease Begin Date", "Lease End Date",
                      "Rent PSF", "Annual Rent", "City", "State", "Zip", "Address"])

    try:
        # Load CSV data for address validation
        csv_path = os.path.join(os.path.dirname(__file__), 'address_validation.csv')
        if not os.path.exists(csv_path):
            print("Warning: Address validation CSV not found. Using default empty data.")
            csv_data = []
        else:
            csv_data = pd.read_csv(csv_path).to_dict('records')
            
        text = extract_text_from_pdf(pdf_path)
        addresses = extract_addresses(text, filename, csv_data)
        rent_roll_pages = locate_rent_roll_sections(pdf_path)
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
        return
    if not rent_roll_pages:
        print(f"No rent roll pages found in {filename}")
        return

    row_counter = [sheet.max_row + 1]
    tenant_data_tracker = {}

    with fitz.open(pdf_path) as pdf_reader:
        for page_num in rent_roll_pages:
            page = pdf_reader[page_num]
            pix = page.get_pixmap(dpi=400)  # Higher DPI for better OCR accuracy
            img = Image.open(io.BytesIO(pix.tobytes()))
            ocr_text = apply_ocr_to_image(img)
            ocr_lines = ocr_text.splitlines()
            cleaned_lines = preprocess_rent_roll_section(ocr_lines, popular_tenants, anchor_tenants)
            tenant_data_block = []
            for line in cleaned_lines:
                if is_new_tenant_line(line):
                    if tenant_data_block:
                        process_tenant_block(tenant_data_block, filename, addresses, sheet, row_counter,
                                             popular_tenants, anchor_tenants, months_map, tenant_data_tracker)
                        tenant_data_block = []
                tenant_data_block.append(line)
            if tenant_data_block:
                process_tenant_block(tenant_data_block, filename, addresses, sheet, row_counter,
                                     popular_tenants, anchor_tenants, months_map, tenant_data_tracker)

    remove_rows_without_square_footage_or_dates(sheet)
    recalculate_tenant_options(sheet)
    workbook.save(excel_path)
    print(f"✅ Saved extracted rent roll from {filename} to {excel_path}")
    return excel_path
