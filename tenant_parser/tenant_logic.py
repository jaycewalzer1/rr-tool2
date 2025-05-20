from tenant_parser.logger import logger
from tenant_parser.constants import popular_tenants, anchor_tenants
import re
import datetime
from tenant_parser.shared_extractors import (
    extract_refined_square_feet,
    extract_psf_candidates,
    extract_date_objects,
    extract_tenant_name,
    determine_lease_begin_date,
    determine_lease_end_date,
    calculate_annual_rent,
    detect_and_split_tenants
)

def process_line_for_tenant(entry, pdf_name, city, state, zip_code, address, months_map, tenant_data=None):
    """
    Parses a single OCR text block to extract structured tenant information.
    Tracks tenant name and option numbers, calculates PSF, dates, and annual rent.
    Returns a list of structured data fields for Excel export.
    """
    if tenant_data is None:
        tenant_data = {}  # Track tenant names and their option counts


    # Split entry into parts
    parts = re.split(r'[,\s]+', entry.strip())
    tenant_name = extract_tenant_name(parts)
   
    # Skip if no tenant name detected and no "current_tenant" context
    if not tenant_name and "current_tenant" not in tenant_data:
        return None
   
    # Update or use the existing tenant name
    if tenant_name:
        if tenant_name not in tenant_data:
            tenant_data[tenant_name] = {"option_number": 0}  # Initialize option tracking
        tenant_data["current_tenant"] = tenant_name
   
    # Use the "current_tenant" context
    tenant_name = tenant_data["current_tenant"]
    option_number = tenant_data[tenant_name]["option_number"]


    # Increment the option number for each subsequent entry
    if option_number > 0:
        tenant_name_with_option = f"{tenant_name} Option {option_number}"
    else:
        tenant_name_with_option = tenant_name  # No "Option" for the first row
    tenant_data[tenant_name]["option_number"] += 1  # Increment option for future entries
    # Extract square footage and other data
    square_feet = extract_refined_square_feet(parts)
    date_candidates, found_current = extract_date_objects(parts, months_map)
    earliest_date = determine_lease_begin_date(date_candidates, found_current, parts)
    begin_date_obj = None
    if earliest_date and earliest_date != "Current":
        try:
            begin_date_obj = datetime.datetime.strptime(earliest_date, '%m/%d/%Y')  # Adjust date format if needed
        except ValueError:
            logger.warning(f"Failed to parse lease begin date: {earliest_date}")
    end_date = determine_lease_end_date(date_candidates, begin_date_obj, found_current)
    psf_candidates = extract_psf_candidates(parts, tenant_name)
    smallest_psf = f"${min(psf_candidates):.2f}" if psf_candidates else None
    annual_rent = calculate_annual_rent(parts, square_feet, psf_candidates)
    # Build structured row (remove raw data parts)
    structured_row = [
        pdf_name, tenant_name_with_option, square_feet, earliest_date, end_date,
        smallest_psf, annual_rent, city, state, zip_code, address
    ]
    return structured_row

