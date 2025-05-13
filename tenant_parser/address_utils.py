import re
import pandas as pd

def extract_addresses(text, pdf_file, csv_data):
    """Extract addresses, fallback to city/state if no address is found, and validate using CSV."""

    """
    Extracts valid addresses from a block of OCR text, using pattern matching and CSV validation.

    Args:
        text (str): The full OCR-extracted text content of a PDF.
        pdf_file (str): The name of the PDF file (unused in logic but preserved for future tagging).
        csv_data (DataFrame): A DataFrame containing valid city/state/ZIP data for address validation.

    Returns:
        List[Tuple[str, str, str, str]]: A list containing one or more tuples of (address, city, state, zip).
    """

    addresses = []

    if isinstance(csv_data, list):
        if not csv_data:  # Empty list
            # Create an empty DataFrame with required columns
            csv_data = pd.DataFrame(columns=['Zip Code', 'City', 'State Name', 'State Abbreviation'])
        else:
            # Convert list of dictionaries to DataFrame
            csv_data = pd.DataFrame(csv_data)
    else:
        # Already a DataFrame or similar
        csv_data = csv_data
    
    # Ensure all required columns exist
    required_columns = ['State Abbreviation', 'City', 'State Name', 'Zip Code']
    for col in required_columns:
        if col not in csv_data.columns:
            csv_data[col] = ""


    # Ensure all values in 'State Abbreviation' are strings
    csv_data['State Abbreviation'] = csv_data['State Abbreviation'].fillna("").astype(str)
    patterns = [
        r'\d{3,5}\s[\w\s]+\s(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\s*,?\s*[\w\s]*,\s*[A-Za-z]{2}\s*\d{5}',
        r'\d{3,5}\s[\w\s]+\s(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\s+[\w\s]+,\s*[A-Za-z]{2}\s*\d{5}',
        r'\d{3,5},?\s*[\d,\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\s*,?\s*[\w\s]*,\s*[A-Za-z]{2}',
        r'\d{4,6}\s*-\s*\d{4,6}\s[\w\s]+\s*,?\s*[\w\s]*,\s*[A-Za-z]{2}\s*\d{5}',
        r'\d{3,5}\s[\w\s]+\s[\w\s]+,\s*[A-Za-z][a-z]+\s[A-Za-z]{2}\s*\d{5}',
        r'[\w\s]+,\s*[A-Za-z]{2}\s*\d{5}',
        r'\d+\s[\w\s]+,?\s*[\w\s]+\s\|\s*[\w\s]+,\s*[A-Za-z]{2}\s*\d{5}',
    ]
    phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
    newmark_pattern = re.compile(r'\bNewmark\b|@nmrk\.com', re.IGNORECASE)
    invalid_keywords = re.compile(r'\b(stores|summary|overview|market|job|students|kay|zale)\b', re.IGNORECASE)
    lines = text.splitlines()
    unique_addresses = {}
    # Extract addresses using patterns
    for i, line in enumerate(lines):
        # Skip lines with invalid keywords
        if invalid_keywords.search(line):
            continue
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                address = match.group(0).strip()
                zip_code = re.search(r'\b\d{5}\b$', address).group(0) if re.search(r'\b\d{5}\b$', address) else "N/A"
                state = re.search(r'\b[A-Za-z]{2}\b(?=\s*\d{5})', address).group(0).upper() if re.search(r'\b[A-Za-z]{2}\b(?=\s*\d{5})', address) else ""
                city_match = re.search(r'([\w\s]+)\s*,?\s*' + state, address, re.IGNORECASE) if state else None
                city = city_match.group(1).strip().title() if city_match else "UNKNOWN"
                # Skip if phone number is nearby
                if (i - 1 >= 0 and phone_pattern.search(lines[i - 1])) or (i + 1 < len(lines) and phone_pattern.search(lines[i + 1])):
                    continue
                # Skip if "Newmark" appears nearby
                nearby_lines = lines[max(0, i - 17):min(len(lines), i + 17)]
                if any(newmark_pattern.search(nearby_line) for nearby_line in nearby_lines):
                    continue
                # Validate the address components against the CSV
                if not is_real_address_with_csv(address, city, state, zip_code, csv_data):
                    continue
                # Add to unique addresses
                key = (city, state, zip_code)
                if key not in unique_addresses or len(address) > len(unique_addresses[key][0]):
                    unique_addresses[key] = (address, city, state, zip_code)
    # Fallback logic for when no address is found
    if not unique_addresses:
        state_pattern = re.compile(r'\b(?:' + '|'.join(csv_data['State Abbreviation'].unique()) + r')\b', re.IGNORECASE)
        state_match = state_pattern.search(text)
        state = state_match.group(0).upper() if state_match else "N/A"
        if state != "N/A":
            city_pattern = re.compile(r'((?:\b\w+\b\s*){1,3}),?\s*' + re.escape(state), re.IGNORECASE)
            city_match = city_pattern.search(text)
            city = city_match.group(1).strip().title() if city_match else "UNKNOWN"
        else:
            city = "UNKNOWN"
        # Validate fallback city/state with CSV
        if city != "UNKNOWN" and is_real_address_with_csv("N/A", city, state, "N/A", csv_data):
            fallback_address = ("N/A", city, state, "N/A")
        else:
            fallback_address = ("N/A", "N/A", "N/A", "N/A")
        unique_addresses[("UNKNOWN", state, "N/A")] = fallback_address
    # Finalize results
    addresses = list(unique_addresses.values())
    if addresses:
        most_complete_address = max(addresses, key=lambda x: len(x[0]))
        return [most_complete_address]
    return [("N/A", "N/A", "N/A", "N/A")]

def is_real_address_with_csv(address, city, state, zip_code, csv_data):
    """
    Validates an address by comparing its city, state, and ZIP code to entries in the CSV.

    Args:
        address (str): Full address string.
        city (str): Extracted city name.
        state (str): State abbreviation or full name.
        zip_code (str): 5-digit ZIP code.
        csv_data (DataFrame): A DataFrame containing verified location entries.

    Returns:
        bool: True if the address matches a valid city/state/ZIP in the CSV, False otherwise.
    """
    # Reject known invalid patterns
    invalid_patterns = [
        r'\bstores\b', r'\bsummary\b', r'\boverview\b', r'\bmarket\b', r'\bphase\b',
        r'\bjob\b', r'\bstudents\b', r'\bsuite\b', r'\b700\b', r'\b800\b', r'\bkay\b', r'\bzale\b'
    ]
    if any(re.search(pattern, address, re.IGNORECASE) for pattern in invalid_patterns):
        return False
    # Validate city and state with the CSV file
    city_valid = csv_data['City'].str.lower().eq(city.lower()).any()
    state_valid = (
        csv_data['State Name'].str.lower().eq(state.lower()).any() or
        csv_data['State Abbreviation'].str.upper().eq(state.upper()).any()
    )
    # Validate ZIP code if present
    if zip_code and zip_code.isdigit():
        zip_match = csv_data[csv_data['Zip Code'] == zip_code]
        if not zip_match.empty:
            valid_zip = (
                zip_match['City'].str.lower().eq(city.lower()).any() and
                (zip_match['State Name'].str.lower().eq(state.lower()).any() or
                 zip_match['State Abbreviation'].str.upper().eq(state.upper()).any())
            )
            if not valid_zip:
                return False
    # Final validation: Both city and state must match
    return city_valid and state_valid

def remove_duplicates_with_csv(addresses, csv_data):
    """
    Removes duplicates from a list of address entries by grouping and validating them using the CSV.

    Args:
        addresses (List[Tuple]): Each address entry is a tuple of (pdf_name, city, state, zip_code, address).
        csv_data (DataFrame): A DataFrame used to validate addresses.

    Returns:
        List[Tuple]: A list of the most valid address entries, one per PDF.
    """
    def get_most_complete_entry(entries):
        """Get the most complete entry based on the number of non-'N/A' or non-'UNKNOWN' fields."""
        return max(
            entries,
            key=lambda e: sum(1 for v in e if v not in ("UNKNOWN", "N/A", "")),
            default=None
        )
    # Filter out invalid addresses
    filtered_addresses = []
    for pdf_name, city, state, zip_code, address in addresses:
        if is_real_address_with_csv(address, city, state, zip_code, csv_data):
            filtered_addresses.append((pdf_name, city, state, zip_code, address))
        else:
            print(f"Removed invalid or mismatched address: {address}, {city}, {state}, {zip_code}")
    # Group by PDF name, city, and state
    grouped_addresses = {}
    for pdf_name, city, state, zip_code, address in filtered_addresses:
        key = (pdf_name, city, state)
        if key not in grouped_addresses:
            grouped_addresses[key] = []
        grouped_addresses[key].append((pdf_name, city, state, zip_code, address))
    # Select the best entry per group
    deduplicated_entries = []
    for key, entries in grouped_addresses.items():
        best_entry = get_most_complete_entry(entries)
        if best_entry:
            deduplicated_entries.append(best_entry)
    # Ensure at least one valid entry per PDF
    final_addresses = []
    pdf_seen = set()
    for entry in deduplicated_entries:
        pdf_name = entry[0]
        if pdf_name not in pdf_seen:
            pdf_seen.add(pdf_name)
            final_addresses.append(entry)
    # If no valid entries exist for a PDF, add a fallback
    all_pdfs = {entry[0] for entry in addresses}
    for pdf_name in all_pdfs - pdf_seen:
        fallback_entry = (pdf_name, "UNKNOWN", "UNKNOWN", "UNKNOWN", "N/A")
        final_addresses.append(fallback_entry)
    return final_addresses
