from tenant_parser.logger import logger
from tenant_parser.constants import popular_tenants, anchor_tenants
from tenant_parser.rent_roll_parser import *
import re
import datetime

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
            begin_date_obj = datetime.strptime(earliest_date, '%m/%d/%Y')  # Adjust date format if needed
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

def extract_tenant_name(parts):
    """
    Attempts to extract a tenant name by matching sequences of 1–4 adjacent tokens against
    known lists of popular and anchor tenants. Prioritizes popular tenant matches if both
    are found.
    Returns the matched tenant name or an empty string if none found.
    """
    detected_popular = None
    detected_anchor = None
    for i in range(len(parts)):
        # Extract combinations of 1 to 4 parts
        single_part = parts[i].strip() if parts[i] else ""
        two_parts = " ".join(filter(None, parts[i:i+2])).strip()
        three_parts = " ".join(filter(None, parts[i:i+3])).strip()
        four_parts = " ".join(filter(None, parts[i:i+4])).strip()
        # Check against popular tenants
        if any(name.lower() == single_part.lower() for name in popular_tenants):
            detected_popular = single_part
        elif any(name.lower() == two_parts.lower() for name in popular_tenants):
            detected_popular = two_parts
        elif any(name.lower() == three_parts.lower() for name in popular_tenants):
            detected_popular = three_parts
        elif any(name.lower() == four_parts.lower() for name in popular_tenants):
            detected_popular = four_parts
       
        # Check against anchor tenants if no popular tenant detected
        if not detected_popular:  # Only check for anchor if no popular tenant found
            if any(name.lower() == single_part.lower() for name in anchor_tenants):
                detected_anchor = single_part
            elif any(name.lower() == two_parts.lower() for name in anchor_tenants):
                detected_anchor = two_parts
            elif any(name.lower() == three_parts.lower() for name in anchor_tenants):
                detected_anchor = three_parts
            elif any(name.lower() == four_parts.lower() for name in anchor_tenants):
                detected_anchor = four_parts
    # Prioritize the detected popular tenant over the anchor tenant
    if detected_popular:
        return detected_popular
    elif detected_anchor:
        return detected_anchor
    # If no match is found, return an empty string
    return ""

def detect_and_split_tenants(cleaned_line, popular_tenants, anchor_tenants):
    """
    Uses regex to split a rent roll line into individual tenant entries based on matches
    to known tenant names. Also filters out 'VACANT' or 'AVAILABLE' segments where detected.
    Returns a list of tenant entry strings.
    """
    tenant_list = list(popular_tenants) + list(anchor_tenants)
    tenant_pattern = re.compile(r'\b(' + '|'.join(re.escape(t) for t in tenant_list) + r')\b', re.IGNORECASE)
    vacancy_pattern = re.compile(r'\b(VACANT|AVAILABLE)\b', re.IGNORECASE)
    tenant_segments = re.split(tenant_pattern, cleaned_line)
    tenants = []
    current_tenant = None

    for segment in tenant_segments:
        segment = segment.strip()
        if not segment:
            continue
        if tenant_pattern.match(segment):
            current_tenant = segment
            continue
        if current_tenant:
            if (match := vacancy_pattern.search(segment)):
                segment = segment[:match.start()].strip()
            if segment:
                tenants.append(f"{current_tenant} {segment}")
            current_tenant = None

    logger.info(f"Detected tenants: {tenants}")
    return tenants
