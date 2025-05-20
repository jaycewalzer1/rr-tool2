import re
from tenant_parser.logger import logger
import datetime
from tenant_parser.constants import anchor_tenants
from tenant_parser.tenant_utils import extract_tenant_name

def extract_date_objects(parts, months_map):
    """
    Parses date-related fragments from a list of text parts using regex patterns.
    Supports standard dates, month-year formats, and 'Years #' fallbacks.
    Returns a list of valid datetime objects and a boolean indicating if 'Current' was found.
    """
    date_pattern_standard = re.compile(r'\d{1,2}/\d{1,2}/\d{2,4}')
    date_pattern_month_year = re.compile(r'([A-Za-z]{3,9})[-\s]*(\d{2,4})')
    date_candidates = []
    found_current = False
    for part in parts:
        part = part.strip()
        # Match standard date formats like MM/DD/YYYY or MM/DD/YY
        if match := date_pattern_standard.match(part):
            date_str = match.group()
            try:
                date_obj = datetime.strptime(date_str, '%m/%d/%Y')
                date_candidates.append(date_obj)
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_str, '%m/%d/%y')
                    date_candidates.append(date_obj)
                except ValueError:
                    logger.warning(f"Invalid standard date string skipped: {date_str}")
                    continue
        # Match month-year formats like 'Jan 2009' or 'July - 2025'
        elif match := date_pattern_month_year.match(part):
            month_name, year = match.groups()
            month = months_map.get(month_name.lower())
            if month and year.isdigit():
                try:
                    year = int(year)
                    if len(str(year)) == 2:
                        year += 2000 if year < 70 else 1900
                    date_candidates.append(datetime(year, month, 1))
                except ValueError:
                    logger.warning(f"Invalid month-year date skipped: {part}")
                    continue
        # Match "Years #" patterns like '10 Years', even if split
        elif "years" in part.lower():
            for i, word in enumerate(parts):
                if word.lower() == "years" and i > 0 and parts[i-1].isdigit():
                    try:
                        year_num = int(parts[i-1])
                        fallback_date = datetime(year=2000 + year_num, month=1, day=1)
                        date_candidates.append(fallback_date)
                        print(f"Matched 'Years #' pattern: {parts[i-1]} Years, interpreted as year {2000 + year_num}")
                    except ValueError:
                        continue
        # Detect "Current" if found in the text
        elif part.lower() == "current":
            found_current = True
    return date_candidates, found_current


def extract_psf_candidates(parts, tenant_name):
    """
    Scans the text parts for dollar-format rent PSF values.
    Filters results by thresholds depending on whether the tenant is an anchor.
    Returns a list of numeric PSF candidates.
    """
    psf_pattern = re.compile(r'^\$\d+\.\d{2}$')
    is_anchor_tenant = tenant_name.lower() in (name.lower() for name in anchor_tenants)
    psf_candidates = []
    for part in parts:
        if psf_pattern.match(part):
            psf_value = float(part.replace('$', ''))
            if (is_anchor_tenant and psf_value >= 4.20) or (not is_anchor_tenant and psf_value >= 4.60):
                psf_candidates.append(psf_value)
    return psf_candidates

def calculate_annual_rent(parts, square_feet, psf_candidates):
    """
    Attempts to infer annual rent from text parts using dollar patterns.
    Falls back to calculating rent from square footage and PSF when necessary.
    Returns a string-formatted dollar amount or None.
    """
    dollar_pattern = re.compile(r'^\$\d+$')
    potential_rents = []
    for i, part in enumerate(parts):
        if dollar_pattern.match(part) and i + 1 < len(parts):
            rent_part1 = part.replace("$", "")
            rent_part2 = parts[i + 1]
            try:
                if "." in rent_part2:
                    combined_rent_value = float(f"{rent_part1}{rent_part2}")
                    if combined_rent_value > 10000:
                        potential_rents.append(int(combined_rent_value))
                elif rent_part2.isdigit():
                    combined_rent = f"{rent_part1}{rent_part2}"
                    if int(combined_rent) > 10000:
                        potential_rents.append(int(combined_rent))
            except ValueError:
                continue
    # Calculate rent based on square footage and PSF
    if len(potential_rents) > 1 and square_feet and psf_candidates:
        calculated_rent = square_feet * min(psf_candidates)
        return f"${min(potential_rents, key=lambda x: abs(x - calculated_rent)):,}"
    elif len(potential_rents) == 1:
        return f"${potential_rents[0]:,}"
    elif square_feet and psf_candidates:
        try:
            calculated_rent = square_feet * min(psf_candidates)
            if calculated_rent > 10000:
                return f"${int(calculated_rent):,}"
        except ValueError:
            return None
    return None

def extract_refined_square_feet(parts):
    """
    Attempts to parse square footage from a fragmented OCR line.
    Reconstructs values split across adjacent tokens and filters invalid values.
    Returns an integer square footage or None.
    """
    # Combine split values and filter out invalid square feet values
    for i in range(len(parts) - 1):
        # Check if the current part and the next part are numbers
        if re.match(r'^\d+$', parts[i]) and re.match(r'^\d+$', parts[i + 1]):        
            # Handle formats like "1" "400" to make 1400
            if len(parts[i]) == 1 and len(parts[i + 1]) == 3:
                combined_sqft = parts[i] + parts[i + 1]
                sqft_value = int(combined_sqft)
                if 800 <= sqft_value <= 250000:
                    return sqft_value
            # Handle formats like "4" "000" to make 4000
            if len(parts[i]) == 1 and len(parts[i + 1]) == 3 and parts[i] != "0":
                combined_sqft = parts[i] + parts[i + 1]
                sqft_value = int(combined_sqft)
                if 800 <= sqft_value <= 250000:
                    return sqft_value
            # Handle formats like "29" "000" to make 29000, skipping if the first part starts with "0"
            if len(parts[i]) == 2 and len(parts[i + 1]) == 3 and not parts[i].startswith("0"):
                combined_sqft = parts[i] + parts[i + 1]
                sqft_value = int(combined_sqft)
                if 800 <= sqft_value <= 250000:
                    return sqft_value          
            # Handle formats like "101" "035" to make 101035
            if len(parts[i]) == 3 and len(parts[i + 1]) == 3:
                combined_sqft = parts[i] + parts[i + 1]
                sqft_value = int(combined_sqft)
                if 800 <= sqft_value <= 250000:
                    return sqft_value
            # Skip if first part is like "05" and only use the second part if it’s valid
            if len(parts[i]) == 2 and parts[i].startswith("0"):
                if 800 <= int(parts[i + 1]) <= 250000:
                    return int(parts[i + 1])
            # Only consider the first part if it has three digits and the next part is a single digit
            if len(parts[i]) == 3 and len(parts[i + 1]) == 1:
                sqft_value = int(parts[i])
                if 800 <= sqft_value <= 250000:
                    return sqft_value
    # If no valid combined values are found, look for individual values
    for i in range(len(parts)):
        if re.match(r'^\d+$', parts[i]):
            possible_sqft = parts[i].replace(",", "")
            if possible_sqft.isdigit() and len(possible_sqft) <= 4:
                sqft_value = int(possible_sqft)
                if 800 <= sqft_value <= 250000:
                    return sqft_value
    # If no valid square footage is found, return None
    return None

def determine_lease_begin_date(date_candidates, found_current, parts):
    """
    Chooses the most plausible lease begin date from date candidates.
    Falls back to 'Current' or parsed 'Years #' patterns if no date is found.
    Returns a formatted date string or None.
    """
    if date_candidates:
        # Sort dates to find the earliest one
        earliest_date_obj = min(date_candidates, key=lambda d: (d.year, d.month, d.day))
        return earliest_date_obj.strftime('%m/%d/%Y')
    elif found_current:
        return "Current"
    else:
        # Final fallback: Search for "Years #" pattern in the parts
        year_pattern = re.compile(r"Years?\s+(\d+)", re.IGNORECASE)  # Match "Years #" pattern
        for part in parts:
            match = year_pattern.search(part)
            if match:
                try:
                    # Extract the number and calculate the year
                    year_num = int(match.group(1))
                    fallback_date = datetime(year=2000 + year_num, month=1, day=1)  # Default to January 1st
                    return fallback_date.strftime('%m/%d/%Y')
                except ValueError:
                    continue
        # If no match for "Years #", return None
        return None

def determine_lease_end_date(date_candidates, begin_date_obj, found_current):
    """
    Determines the lease end date by prioritizing:
    1. A date 3 years from the begin date.
    2. A date 5 years from the begin date.
    3. A date 10 years from the begin date.
    4. The second lowest date.
    5. 'Current' as a fallback.
    """
    if not begin_date_obj:
        return "Current" if found_current else None
    # Pre-sort dates to improve efficiency for subsequent checks
    date_candidates = sorted(date_candidates, key=lambda d: (d.year, d.month, d.day))
    # Define the target years based on the begin date
    three_years_later = begin_date_obj.year + 3
    five_years_later = begin_date_obj.year + 5
    ten_years_later = begin_date_obj.year + 10
    # Group dates by target years
    three_year_candidates = [date for date in date_candidates if date.year == three_years_later]
    five_year_candidates = [date for date in date_candidates if date.year == five_years_later]
    ten_year_candidates = [date for date in date_candidates if date.year == ten_years_later]
    # Priority: Check for dates that match the target years
    if three_year_candidates:
        return min(three_year_candidates, key=lambda d: (d.month, d.day)).strftime('%m/%d/%Y')
    elif five_year_candidates:
        return min(five_year_candidates, key=lambda d: (d.month, d.day)).strftime('%m/%d/%Y')
    elif ten_year_candidates:
        return min(ten_year_candidates, key=lambda d: (d.month, d.day)).strftime('%m/%d/%Y')
    # If no matching year is found, select the second lowest date if available
    if len(date_candidates) > 1:
        second_lowest_date = date_candidates[1]
        return second_lowest_date.strftime('%m/%d/%Y')
    # If all else fails and 'Current' is found, use 'Current'
    return "Current" if found_current else None

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
