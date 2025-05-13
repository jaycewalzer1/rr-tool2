from tenant_parser.constants import popular_tenants, anchor_tenants
import re
from tenant_parser.logger import logger
from tenant_parser.tenant_logic import *

def categorize_tenants_from_data_sheet(data_sheet, pdf_name, anchor_tenants, popular_tenants):
    """
    Scans an Excel data sheet for tenants associated with a specific PDF name.
    Categorizes them into anchor or popular tenants based on predefined lists and returns
    two lists of (tenant_name, rent_psf) tuples.
    """
    anchor_tenants_data = []
    popular_tenants_data = []
    tenant_dict = {}
    for row in data_sheet.iter_rows(min_row=2, values_only=True):  # Skip header row
        current_pdf_name = row[0]  # PDF Name column
        tenant_name = row[1]       # Tenant Name column
        rent_psf = row[5]          # Smallest Rent PSF column
        # Check if the row matches the specified PDF and has a tenant name and rent_psf
        if current_pdf_name == pdf_name and tenant_name and rent_psf:
            # Store the smallest Rent PSF for each unique tenant
            if tenant_name not in tenant_dict or (tenant_dict[tenant_name] > rent_psf):
                tenant_dict[tenant_name] = rent_psf
    # Categorize tenants based on predefined lists
    for tenant_name, rent_psf in tenant_dict.items():
        if tenant_name in anchor_tenants:
            anchor_tenants_data.append((tenant_name, rent_psf))
        elif tenant_name in popular_tenants:
            popular_tenants_data.append((tenant_name, rent_psf))
    return anchor_tenants_data, popular_tenants_data

def process_tenant_block(tenant_data_block, filename, addresses, sheet, row_counter, popular_tenants, anchor_tenants, months_map, tenant_data):
    """
    Processes a contiguous block of rent roll text representing one or more tenants.
    Splits the block into individual entries using known tenant lists, then parses and
    writes each valid entry to the provided Excel sheet.
    """
    tenant_text = " ".join(tenant_data_block)
    tenant_entries = detect_and_split_tenants(tenant_text, popular_tenants, anchor_tenants)
    for entry in tenant_entries:
        for address, city, state, zip_code in addresses or [("N/A", "UNKNOWN", "UNKNOWN", "N/A")]:
            structured_row = process_line_for_tenant(entry, filename, city, state, zip_code, address, months_map, tenant_data)
            if structured_row:
                print("Processed line:", structured_row)
                for col_idx, value in enumerate(structured_row, start=1):
                    sheet.cell(row=row_counter[0], column=col_idx, value=value)
                row_counter[0] += 1


def is_new_tenant_line(cleaned_line):
    """
    Determines whether a line likely represents the start of a new tenant entry based on
    whether it begins with a capital letter.
    """
    return bool(re.match(r'^[A-Za-z]', cleaned_line))
