import re
from tenant_parser.logger import logger
import datetime
from tenant_parser.constants import anchor_tenants
from tenant_parser.tenant_utils import extract_tenant_name
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

def preprocess_rent_roll_section(ocr_lines, popular_tenants, anchor_tenants):
    """
    Cleans raw OCR lines by removing irrelevant content and reformatting common noise.
    Filters lines that are likely to represent valid tenant or lease data.
    Returns a list of cleaned text lines.
    """
    cleaned_lines = []
    rent_psf_pattern = r'\$\d+(\.\d{1,2})?'
    combined_patterns = [
        r'\[\d+\]\s?.*',
        r'^(NOTE:|Denominator:|Notes:|Note:|Per\s.*|Exclusive Use:|Percentage Rent:|Renewal History:|Recovery:|CAM:)\s+.*',
        r'^[A-Z][^\.]*[\.,;!?]*\s*\.$',
        r'^(?:Additionally|Moreover|Furthermore|Also|However|Tenant|Tenant\'s)\s+.*\.$',
        r'\b\d{1,3}-\d{1,3}\s+year\s+term\b',
        r'\b(?:e-commerce|retail|demographics|development|industry|threats)\b',
        r'^(?:Tenant|Suite|Feet|Property|Begin|End|Monthly|Annually|PSF|Rent|Improvements).*',
        r"^Tenant recovery denominator[^\.]*\.$",
        r'\b(?:averaging|over|their|size|pay|paid|summary|is|a|are|less|than|area|contributions|total|based|and|has|leased|agrees|of|agree)\b.*',
    ]
    combined_regex = re.compile(r'|'.join(combined_patterns), re.IGNORECASE)
    admin_fee_regex = re.compile(r'\b\w+\s+\+\s*\d{1,3}%\s+(?:Admin|Fee)\b', re.IGNORECASE)
    capped_plus_regex = re.compile(r'\b\w+\s+Capped\s+\+\s*\d{1,3}%\b', re.IGNORECASE)
    prs_or_cam_regex = re.compile(r'(PRS|Fixed CAM).*?(Option|Options)', re.IGNORECASE)
    rent_psf_regex = re.compile(rent_psf_pattern, re.IGNORECASE)

    for line in ocr_lines:
        line = re.sub(r'\s+', ' ', line).strip()
        if not rent_psf_regex.search(line) or combined_regex.search(line):
            continue

        prs_match = prs_or_cam_regex.search(line)
        if prs_match:
            start, end = prs_match.span()
            line = line[:start] + prs_match.group(2) + line[end:]

        if admin_fee_regex.search(line):
            start = line.rfind(' ', 0, admin_fee_regex.search(line).start())
            line = line[:start].strip()

        if capped_plus_regex.search(line):
            start = line.rfind(' ', 0, capped_plus_regex.search(line).start())
            line = line[:start].strip()

        if line:
            cleaned_lines.append(line)

    return cleaned_lines
