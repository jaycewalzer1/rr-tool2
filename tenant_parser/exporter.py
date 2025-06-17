import os
import fitz  # PyMuPDF for PDF handling
import pandas as pd
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Alignment, Font
import pytesseract
from PIL import Image
import io
import re
from openpyxl import load_workbook
from collections import Counter
import PyPDF2
from datetime import datetime
from openpyxl.utils import get_column_letter
from tenant_parser.constants import popular_tenants, anchor_tenants, states_map, months_map
# Load the list of US cities and states from a CSV file
city_list_path = os.path.join(os.path.dirname(__file__), 'data', 'US.txt')
csv_data = pd.read_csv(city_list_path, header=None, sep='\t', usecols=[1, 2, 3, 4])
csv_data.columns = ['Zip Code', 'City', 'State Name', 'State Abbreviation']
csv_data['Zip Code'] = csv_data['Zip Code'].astype(str).str.strip()
csv_data['City'] = csv_data['City'].str.strip().str.lower()
csv_data['State Name'] = csv_data['State Name'].str.strip().str.lower()
csv_data['State Abbreviation'] = csv_data['State Abbreviation'].str.strip().str.upper()
city_list_path = os.path.join(os.path.dirname(__file__), 'city_list.tsv')
from openpyxl.styles import PatternFill, Font
from openpyxl.utils import get_column_letter
def generate_summary_sheet(pdf_path, summary_sheet, data_sheet, pdf_name, anchor_tenants, popular_tenants):
    # Define cell styles for table headers
    black_fill = PatternFill(start_color="000000", end_color="000000", fill_type="solid")
    white_font_bold = Font(color="FFFFFF", bold=True)
    # Extract general information
    text = extract_text_from_pdf(pdf_path)
    addresses = extract_addresses(text, pdf_name, csv_data)
    address_info = addresses[0] if addresses else ("N/A", "N/A", "N/A", "N/A")
    address, city, state, zip_code = address_info[:4]
    # Categorize tenants from the Data Sheet for the specific PDF
    anchor_tenants_data, popular_tenants_data = categorize_tenants_from_data_sheet(
        data_sheet, pdf_name, anchor_tenants, popular_tenants
    )
    # Table 1: General Information
    summary_sheet.append(["Table 1 - General Information Table on " + pdf_name])
    summary_sheet.merge_cells("A1:D1")
    summary_sheet["A1"].fill = black_fill
    summary_sheet["A1"].font = white_font_bold
    summary_sheet.append(["PDF Name", "State", "City", "Zip Code", "Address"])
    summary_sheet.append([pdf_name, state, city, zip_code, address])
    summary_sheet.append([""])  # Blank row for spacing
    # Table 2: Anchor Tenants with Rent PSF
    start_row = summary_sheet.max_row + 1
    summary_sheet.append([f"Table 2 - Anchor Tenants in {pdf_name}"])
    summary_sheet.merge_cells(start_row=start_row, start_column=1, end_row=start_row, end_column=2)
    summary_sheet.cell(row=start_row, column=1).fill = black_fill
    summary_sheet.cell(row=start_row, column=1).font = white_font_bold
    summary_sheet.append(["Tenant Name", "Rent PSF"])
    for tenant_name, rent_psf in anchor_tenants_data:
        summary_sheet.append([tenant_name, rent_psf])
    summary_sheet.append([""])  # Blank row for spacing
    # Table 3: Popular Tenants with Rent PSF
    start_row = summary_sheet.max_row + 1
    summary_sheet.append([f"Table 3 - Popular Tenants in {pdf_name}"])
    summary_sheet.merge_cells(start_row=start_row, start_column=1, end_row=start_row, end_column=2)
    summary_sheet.cell(row=start_row, column=1).fill = black_fill
    summary_sheet.cell(row=start_row, column=1).font = white_font_bold
    summary_sheet.append(["Tenant Name", "Rent PSF"])
    for tenant_name, rent_psf in popular_tenants_data:
        summary_sheet.append([tenant_name, rent_psf])
    summary_sheet.append([""])  # Blank row for spacing
    # Table 4: Tenant-Specific Summary for the PDF
    tenant_names = set(row[1] for row in data_sheet.iter_rows(min_row=2, values_only=True) if row[0] == pdf_name)
    for tenant_name in tenant_names:
        tenant_entries = get_tenant_data_by_name(data_sheet, tenant_name)
        if tenant_entries:
            start_row = summary_sheet.max_row + 1
            summary_sheet.append([f"Details for Tenant: {tenant_name}"])
            summary_sheet.merge_cells(start_row=start_row, start_column=1, end_row=start_row, end_column=4)
            summary_sheet.cell(row=start_row, column=1).fill = black_fill
            summary_sheet.cell(row=start_row, column=1).font = white_font_bold
            summary_sheet.append(["Tenant Name", "Smallest Rent PSF", "City", "State"])
            rent_psf_values = []
            for entry in tenant_entries:
                summary_sheet.append(entry)
                rent_psf = entry[1]
                if isinstance(rent_psf, str):
                    rent_psf = rent_psf.replace('$', '').replace(',', '').strip()
                if isinstance(rent_psf, (int, float)) or (isinstance(rent_psf, str) and rent_psf.replace('.', '', 1).isdigit()):
                    rent_psf_values.append(float(rent_psf))
            if rent_psf_values:
                average_rent_psf = sum(rent_psf_values) / len(rent_psf_values)
                summary_sheet.append(["Average Rent PSF", f"${average_rent_psf:.2f}"])
                tenant_rent_psf = rent_psf_values[0]
                difference = (tenant_rent_psf / average_rent_psf - 1) * 100
                above_below = "above" if difference > 0 else "below"
                formatted_difference = f"{abs(difference):.2f}% {above_below} market"
                summary_sheet.append([f"The {tenant_name} for {pdf_name} is {formatted_difference} from our existing comp set."])
            else:
                summary_sheet.append(["Average Rent PSF", "N/A"])
            summary_sheet.append([""])  # Blank row for spacing between tenant tables
    print(f"Summary generated for {pdf_name} with General Info, Anchor Tenants, Popular Tenants, and Individual Tenant Tables.")
def categorize_tenants_from_data_sheet(data_sheet, pdf_name, anchor_tenants, popular_tenants):
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
def get_tenant_data_by_name(data_sheet, tenant_name):
    tenant_entries = []
    for row in data_sheet.iter_rows(min_row=2, values_only=True):  # Skip header row
        current_tenant_name = row[1]  # Tenant Name column
        rent_psf = row[5]             # Smallest Rent PSF column
        city = row[7]                 # City column
        state = row[8]                # State column
        # Only process rows that match the specified tenant name
        if current_tenant_name == tenant_name:
            tenant_entry = (tenant_name, rent_psf, city, state)
            tenant_entries.append(tenant_entry)
    return tenant_entries
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text
def extract_addresses(text, pdf_file, csv_data):
    """Extract addresses, fallback to city/state if no address is found, and validate using CSV."""
    addresses = []
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
def process_pdfs_with_fallback(pdf_folder, csv_data, excel_path, sheet_name):
    """Process PDFs and apply improved fallback logic."""
    all_addresses = []
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.lower().endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder, pdf_file)
            text = extract_text_from_pdf(pdf_path)
            addresses = extract_addresses(text, pdf_file, csv_data)
            formatted_addresses = [(pdf_file, city, state, zip_code, address) for address, city, state, zip_code in addresses]
            all_addresses.extend(formatted_addresses)
    # Deduplicate and save to Excel
    cleaned_addresses = remove_duplicates_with_csv(all_addresses, csv_data)
    save_addresses_to_excel(cleaned_addresses, excel_path, sheet_name)
def save_addresses_to_excel(addresses, excel_path, sheet_name):
    df = pd.DataFrame(addresses, columns=['pdf name', 'city', 'state', 'zip', 'address']).drop_duplicates()
    # Check if the Excel file exists
    if os.path.exists(excel_path):
        with pd.ExcelWriter(excel_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            if sheet_name in writer.book.sheetnames:
                existing_data = pd.read_excel(excel_path, sheet_name=sheet_name)
                existing_data.columns = ['pdf name', 'city', 'state', 'zip', 'address']
                df = df[~df[['pdf name', 'city', 'state', 'zip', 'address']].apply(tuple, axis=1).isin(
                    existing_data[['pdf name', 'city', 'state', 'zip', 'address']].apply(tuple, axis=1)
                )]
            if not df.empty:
                start_row = writer.book[sheet_name].max_row if sheet_name in writer.book.sheetnames else 0
                df.to_excel(writer, sheet_name=sheet_name, index=False, header=(start_row == 0), startrow=start_row)
    else:
        df.to_excel(excel_path, sheet_name=sheet_name, index=False)
def process_pdfs(pdf_folder, excel_path, sheet_name):
    all_addresses = []
    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.lower().endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder, pdf_file)
            print(f"Processing PDF: {pdf_file}")
            text = extract_text_from_pdf(pdf_path)
            addresses = extract_addresses(text, pdf_file, csv_data)  # Ensure extract_addresses returns full tuples
            # Ensure each address includes all necessary components
            formatted_addresses = [(pdf_file, city, state, zip_code, address) for address, city, state, zip_code in addresses]
            all_addresses.extend(formatted_addresses)
    # Remove duplicates from the collected addresses
    cleaned_addresses = remove_duplicates_with_csv(all_addresses)
    save_addresses_to_excel(cleaned_addresses, excel_path, sheet_name)
from collections import Counter
def is_real_address_with_csv(address, city, state, zip_code, csv_data):
    """Check if an address is real by validating city, state, and ZIP code against the CSV."""
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
    """Remove duplicates and validate entries with the CSV."""
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
def deduplicate_data_sheet(data_sheet):
    """
    Retains only the most complete entry per tenant name for each PDF in the data sheet,
    and removes any entries with no data in critical columns: Square Feet, Begin Date,
    End Date, Smallest Rent PSF, and Annual Rent.
    """
    rows = list(data_sheet.iter_rows(min_row=2, values_only=False))  # Get all rows except the header
    data = {}  # Dictionary to store the most complete entry per tenant for each PDF
    for row in rows:
        pdf_name = row[0].value
        tenant_name = row[1].value
        if pdf_name and tenant_name:
            # Extract critical columns for completeness check
            square_feet = row[2].value
            begin_date = row[3].value
            end_date = row[4].value
            smallest_rent_psf = row[5].value
            annual_rent = row[6].value
            # Skip rows missing data in all critical columns
            if not (square_feet or begin_date or end_date or smallest_rent_psf or annual_rent):
                print(f"Removing incomplete entry for {pdf_name} - {tenant_name} with all critical columns empty.")
                continue
            # Calculate completeness score based on filled columns
            current_row_data = [square_feet, begin_date, end_date, smallest_rent_psf, annual_rent]
            completeness_score = sum(1 for value in current_row_data if value)
            key = (pdf_name, tenant_name)
            if key not in data or completeness_score > data[key][1]:
                # Store the row and completeness score if this is more complete
                data[key] = (row, completeness_score)
    # Clear the data sheet except for the headers
    data_sheet.delete_rows(2, data_sheet.max_row - 1)
    # Append only the most complete rows
    for row, _ in data.values():
        data_sheet.append([cell.value for cell in row])
    print("Deduplication completed: Only the most complete entries for each tenant retained.")
def determine_lease_begin_date(date_candidates, found_current, parts):
    """
    Determines the lease begin date by selecting the earliest date.
    If no dates are found but 'Current' is detected, use 'Current' as the fallback.
    If neither dates nor 'Current' are found, check for "Years #" as a final fallback.
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
def extract_date_objects(parts, months_map):
    """
    Extracts date objects from parts of a line using multiple patterns, including formats like 'Jan 2009', 'July - 2025',
    and fallbacks like '10 Years'.
    Handles both two-digit (%y) and four-digit (%Y) years. Skips invalid date strings gracefully.
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
def process_line_for_tenant(entry, pdf_name, city, state, zip_code, address, months_map, tenant_data=None):
    """
    Processes a single tenant entry to extract relevant details and structure it.
    Includes proper handling of "Option #" rows for every subsequent entry.
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
def extract_psf_candidates(parts, tenant_name):
    """
    Extracts Price Per Square Foot (PSF) candidates from parts.
    Prioritizes PSF values based on tenant type.
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
    Calculates the annual rent based on the extracted PSF and square footage.
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
def remove_empty_tenant_rows(sheet):
    rows_to_delete = [
        row[0].row for row in sheet.iter_rows(min_row=2, max_col=2, values_only=False)
        if not row[1].value or not row[1].value.strip() or
        (row[1].value.strip().lower() not in (name.lower() for name in popular_tenants | anchor_tenants))
    ]
    for row_num in reversed(rows_to_delete):
        sheet.delete_rows(row_num, 1)
def remove_rows_without_begin_date(sheet):
    rows_to_delete = [
        row[0].row for row in sheet.iter_rows(min_row=2, max_col=4, values_only=False)
        if not row[3].value or not row[3].value.strip()
    ]
    for row_num in reversed(rows_to_delete):
        sheet.delete_rows(row_num, 1)
def apply_header_style(sheet):
    for cell in sheet["1:1"]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
def auto_adjust_column_widths(sheet):
    for col in sheet.columns:
        max_length = 0
        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        sheet.column_dimensions[col[0].column_letter].width = max_length + 2
def extract_tenant_name(parts):
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
# Example Usage
def apply_ocr_to_image(image):
    """
    Use OCR to extract text from an image of a PDF page with horizontal alignment.
    """
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    # Preprocess image: Convert to grayscale, enhance contrast
    image = image.convert('L')  # Grayscale
    image = image.filter(ImageFilter.SHARPEN)  # Sharpen the image
    image = ImageEnhance.Contrast(image).enhance(2)  # Increase contrast
    # OCR configuration
    config = "--psm 6 --oem 3"  # PSM 6 assumes a single uniform block of text; OEM 3 is the best model
    return pytesseract.image_to_string(image, config=config)
def locate_rent_roll_sections(pdf_path):
    """
    Scans each page in the PDF to identify rent roll sections by searching for
    keywords like 'Rent Roll' or similar indicators.
    """
    rent_roll_pages = []
    with fitz.open(pdf_path) as pdf_reader:
        for page_num in range(pdf_reader.page_count):
            page_text = pdf_reader[page_num].get_text()
            # Detect "Rent Roll" sections dynamically
            if "rent roll" in page_text.lower():
                rent_roll_pages.append(page_num)
                print(f"Rent Roll detected on page {page_num + 1} in {os.path.basename(pdf_path)}")
    return rent_roll_pages
def split_line_into_columns(line, max_columns=58):
    """
    Splits a line of rent roll data into separate columns by spaces,
    up to a specified maximum number of columns.
    """
    # Split the line by spaces
    columns = line.split()
    # Ensure we have exactly `max_columns` columns, padding with empty strings if necessary
    return columns[:max_columns] + [''] * (max_columns - len(columns))
def remove_empty_tenant_rows(sheet):
    rows_to_delete = [
        row[0].row for row in sheet.iter_rows(min_row=2, max_col=2, values_only=False)
        if not row[1].value or not row[1].value.strip() or
        (row[1].value.strip().lower() not in (name.lower() for name in popular_tenants | anchor_tenants))
    ]
    for row_num in reversed(rows_to_delete):
        sheet.delete_rows(row_num, 1)
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
class PDFHandler(FileSystemEventHandler):
    def __init__(self, folder_path, excel_path, process_function):
        self.folder_path = folder_path
        self.excel_path = excel_path
        self.process_function = process_function
        self.final_pdf = None  # Tracks the last detected PDF
    def on_created(self, event):
        if event.src_path.endswith(".pdf"):
            pdf_path = event.src_path
            print(f"New PDF detected: {os.path.basename(pdf_path)}")
            self.final_pdf = pdf_path
            self.process_all_existing_pdfs()  # Process other PDFs in the folder
            # Process the detected PDF last with summary generation
            if self.final_pdf:
                print(f"Processing detected PDF last with summary: {self.final_pdf}")
                self.process_function(self.final_pdf, self.excel_path, generate_summary=True)
    def process_all_existing_pdfs(self):
        for pdf_file in os.listdir(self.folder_path):
            pdf_path = os.path.join(self.folder_path, pdf_file)
            if pdf_file.endswith(".pdf") and pdf_path != self.final_pdf:
                print(f"Processing existing PDF: {pdf_file}")
                self.process_function(pdf_path, self.excel_path, generate_summary=False)
def start_pdf_monitor(folder_path, excel_path, process_function):
    event_handler = PDFHandler(folder_path, excel_path, process_function)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    print("Monitoring folder for new PDFs...")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
import logging
import re
import os
from openpyxl import Workbook, load_workbook
from PIL import Image
import io
logging.basicConfig(filename="database1.log", level=logging.INFO, format="%(message)s")
logger = logging.getLogger()
import re
def preprocess_rent_roll_section(ocr_lines, popular_tenants, anchor_tenants):
    """
    Preprocesses normalized rent roll data by removing irrelevant sentences, footers, and rows
    without a valid Rent PSF format.
    """
    cleaned_lines = []
   
    # Patterns for filtering
    rent_psf_pattern = r'\$\d+(\.\d{1,2})?'  # Matches "$24.00" or "$9.05"
    bracket_analysis_pattern = r'\[\d+\]\s?.*'  # Matches "[1]" or "[2] Analysis..."
    note_or_denominator_pattern = r'^(NOTE:|Denominator:|Notes:|Note:|Per\s.*|Exclusive Use:|Percentage Rent:|Renewal History:|Recovery:|CAM:)\s+.*'
    alphabetic_sentence_pattern = r'^[A-Z][^\.]*[\.,;!?]*\s*\.$'  # Matches sentences starting with a capital letter
    full_sentence_structure = r'^(?:Additionally|Moreover|Furthermore|Also|However|Tenant|Tenant\'s)\s+.*\.$'
    time_related_pattern = r'\b\d{1,3}-\d{1,3}\s+year\s+term\b'  # Matches "1-5 year term"
    industry_related_pattern = r'\b(?:e-commerce|retail|demographics|development|industry|threats)\b'
    table_header_pattern = r'^(?:Tenant|Suite|Feet|Property|Begin|End|Monthly|Annually|PSF|Rent|Improvements).*'
    tenant_recovery_pattern = r"^Tenant recovery denominator[^\.]*\.$"
    keyword_based_sentence_pattern = r'\b(?:averaging|over|their|size|pay|paid|summary|is|a|are|less|than|area|contributions|total|based|and|has|leased|agrees|of|agree)\b.*'
    # Compile all patterns into a combined regex
    combined_patterns = [
        bracket_analysis_pattern,
        note_or_denominator_pattern,
        alphabetic_sentence_pattern,
        full_sentence_structure,
        time_related_pattern,
        industry_related_pattern,
        table_header_pattern,
        tenant_recovery_pattern,
        keyword_based_sentence_pattern,
    ]
    combined_regex = re.compile(r'|'.join(combined_patterns), re.IGNORECASE)
   
    # Additional processing patterns
    admin_fee_pattern = r'\b\w+\s+\+\s*\d{1,3}%\s+(?:Admin|Fee)\b'  # Matches "+ 15% Admin" or "+ 15% Fee"
    capped_plus_pattern = r'\b\w+\s+Capped\s+\+\s*\d{1,3}%\b'  # Matches "Capped + 15%"
    prs_or_cam_pattern = r'(PRS|Fixed CAM).*?(Option|Options)'  # Matches PRS/Fixed CAM until Option/Options
    rent_psf_regex = re.compile(rent_psf_pattern, re.IGNORECASE)
    admin_fee_regex = re.compile(admin_fee_pattern, re.IGNORECASE)
    capped_plus_regex = re.compile(capped_plus_pattern, re.IGNORECASE)
    prs_or_cam_regex = re.compile(prs_or_cam_pattern, re.IGNORECASE)
    for line in ocr_lines:
        # Normalize whitespace
        line = re.sub(r'\s+', ' ', line).strip()
        # Filter out rows without a valid Rent PSF format early
        if not rent_psf_regex.search(line):
            continue  # Skip rows without a Rent PSF
        # Apply pattern-based filtering (e.g., remove brackets, notes, and irrelevant lines)
        if re.search(bracket_analysis_pattern, line) or re.search(note_or_denominator_pattern, line):
            continue
        # Process PRS or Fixed CAM pattern
        prs_match = prs_or_cam_regex.search(line)
        if prs_match:
            start, end = prs_match.span()
            line = line[:start] + prs_match.group(2) + line[end:]  # Remove PRS/Fixed CAM but keep "Option"
        # Process "+ Admin Fee" or "+ 15%"
        admin_fee_match = admin_fee_regex.search(line)
        if admin_fee_match:
            start = line.rfind(' ', 0, admin_fee_match.start())  # Find the space before "+ Admin Fee"
            line = line[:start].strip()
        # Process "Capped + 15%"
        capped_match = capped_plus_regex.search(line)
        if capped_match:
            start = line.rfind(' ', 0, capped_match.start())  # Find the space before "Capped +"
            line = line[:start].strip()
        # Apply combined cleaning patterns (e.g., remove notes, headers, etc.)
        while True:
            match = combined_regex.search(line)
            if not match:
                break
            match_start = match.start()
            match_end = match.end()
            line = line[:match_start] + line[match_end:].strip()
        # Add the cleaned line to the results if it is not empty
        if line:
            cleaned_lines.append(line)
    return cleaned_lines
def detect_and_split_tenants(cleaned_line, popular_tenants, anchor_tenants):
    """
    Splits the cleaned tenant data into individual entries based on known tenants.
    Handles multiline entries by associating lines with the same tenant.
    Removes content starting from "VACANT" or "AVAILABLE" in a tenant line.
    """
    # Combine tenants into a single list and compile a regex pattern
    tenant_list = list(popular_tenants) + list(anchor_tenants)
    tenant_pattern = re.compile(r'\b(' + '|'.join(re.escape(tenant) for tenant in tenant_list) + r')\b', re.IGNORECASE)
    # Regex to detect "VACANT", "Available" and similar terms (case-insensitive)
    vacancy_pattern = re.compile(r'\b(VACANT|AVAILABLE)\b', re.IGNORECASE)
    # Split the line by tenant names
    tenant_segments = re.split(tenant_pattern, cleaned_line)
    tenants = []
    current_tenant = None
    for segment in tenant_segments:
        segment = segment.strip()
        if not segment:
            continue
        # If the segment matches a tenant name, set it as the current tenant
        if tenant_pattern.match(segment):
            current_tenant = segment.strip()
            continue
        # If it's a continuation of the current tenant, check for "VACANT" or "AVAILABLE"
        if current_tenant:
            vacancy_match = vacancy_pattern.search(segment)
            if vacancy_match:
                # Truncate the segment at the vacancy keyword
                segment = segment[:vacancy_match.start()].strip()
            # Only add non-empty segments
            if segment:
                tenants.append(f"{current_tenant} {segment}")
            current_tenant = None  # Reset to ensure proper grouping of tenants
    # Log the detected tenants
    logger.info(f"Detected tenants: {tenants}")
    return tenants
def is_new_tenant_line(cleaned_line):
    """Determine if a cleaned line starts a new tenant entry."""
    return bool(re.match(r'^[A-Za-z]', cleaned_line))
def remove_rows_without_square_footage_or_dates(sheet):
    """Removes rows missing square footage or lease begin dates."""
    rows_to_delete = [
        row[0].row for row in sheet.iter_rows(min_row=2, values_only=False)
        if not row[2].value or not row[3].value
    ]
    # Delete rows in reverse order to avoid shifting
    for row_num in reversed(rows_to_delete):
        sheet.delete_rows(row_num, 1)
def process_tenant_block(tenant_data_block, filename, addresses, sheet, row_counter, popular_tenants, anchor_tenants, months_map, tenant_data):
    """
    Processes each tenant block by structuring the data and exporting rows directly to Excel.
    Handles tenant option numbering dynamically.
    """
    tenant_text = " ".join(tenant_data_block)  # Combine tenant data block into a single text block
    tenant_entries = detect_and_split_tenants(tenant_text, popular_tenants, anchor_tenants)  # Detect tenant entries
    for entry in tenant_entries:
        for address, city, state, zip_code in addresses or [("N/A", "UNKNOWN", "UNKNOWN", "N/A")]:
            structured_row = process_line_for_tenant(entry, filename, city, state, zip_code, address, months_map, tenant_data)
            if structured_row:
                print("Processed line:", structured_row)  # Debugging output for processed rows
                # Write structured_row directly to the Excel sheet
                for col_idx, value in enumerate(structured_row, start=1):
                    sheet.cell(row=row_counter[0], column=col_idx, value=value)
                row_counter[0] += 1  # Increment the row counter
import os
from openpyxl import load_workbook, Workbook
from openpyxl.utils.exceptions import InvalidFileException
import fitz  # PyMuPDF
from PIL import Image
import io
def export_rent_roll_data_with_ocr(pdf_path, excel_path, generate_summary, data_sheet_name="Retail Tenants", summary_sheet_name="Summary 1"):
    months_map = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    filename = os.path.basename(pdf_path)
    workbook = load_workbook(excel_path) if os.path.exists(excel_path) else Workbook()
    sheet = workbook[data_sheet_name] if data_sheet_name in workbook.sheetnames else workbook.create_sheet(data_sheet_name)
    if sheet.max_row == 1:
        data_headers = [
            "PDF Name", "Tenant Name", "Square Feet", "Lease Begin Date", "Lease End Date",
            "Rent PSF", "Annual Rent", "City", "State", "Zip", "Address"
        ]
        sheet.append(data_headers)
    text = extract_text_from_pdf(pdf_path)
    addresses = extract_addresses(text, filename, csv_data)
    rent_roll_pages = locate_rent_roll_sections(pdf_path)
    if not rent_roll_pages:
        return
    row_counter = [sheet.max_row + 1]
    finalized_tenants = {}  # Initialize tenant data tracking
    with fitz.open(pdf_path) as pdf_reader:
        for page_num in rent_roll_pages:
            page = pdf_reader[page_num]
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes()))
            ocr_text = apply_ocr_to_image(img)
            ocr_lines = ocr_text.splitlines()
            cleaned_lines = preprocess_rent_roll_section(ocr_lines, popular_tenants, anchor_tenants)
            tenant_data_block = []
            for line in cleaned_lines:
                if is_new_tenant_line(line):
                    if tenant_data_block:
                        process_tenant_block(tenant_data_block, filename, addresses, sheet, row_counter, popular_tenants, anchor_tenants, months_map, finalized_tenants)
                        tenant_data_block = []
                tenant_data_block.append(line)
            if tenant_data_block:
                process_tenant_block(tenant_data_block, filename, addresses, sheet, row_counter, popular_tenants, anchor_tenants, months_map, finalized_tenants)
    # Remove rows without square footage or dates
    remove_rows_without_square_footage_or_dates(sheet)
    # Recalculate tenant options after rows are finalized
    recalculate_tenant_options(sheet)
    # Generate a summary sheet if required
    if generate_summary:
        summary_sheet = workbook[summary_sheet_name] if summary_sheet_name in workbook.sheetnames else workbook.create_sheet(summary_sheet_name)
        generate_summary_sheet(pdf_path, summary_sheet, sheet, filename, anchor_tenants, popular_tenants)
    workbook.save(excel_path)
def recalculate_tenant_options(sheet):
    """
    Recalculates the tenant names with proper "Option #" counts based on rows grouped by the same PDF.
    The first occurrence of a tenant name in the same PDF remains as-is,
    and subsequent occurrences are labeled as 'Option 1', 'Option 2', etc.
    """
    # Create a dictionary to track tenant counts for each PDF
    pdf_tenant_tracker = {}
    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, values_only=False):  # Skip header row
        pdf_name_cell = row[0]  # PDF Name column (assumed to be column 0)
        tenant_cell = row[1]    # Tenant Name column (assumed to be column 1)
        if pdf_name_cell.value and tenant_cell.value:
            pdf_name = pdf_name_cell.value
            tenant_name = tenant_cell.value.split(" Option")[0]  # Extract base tenant name
            # Initialize a tracker for this PDF if not already done
            if pdf_name not in pdf_tenant_tracker:
                pdf_tenant_tracker[pdf_name] = {}
            # Initialize the option count for this tenant within the PDF
            if tenant_name not in pdf_tenant_tracker[pdf_name]:
                pdf_tenant_tracker[pdf_name][tenant_name] = 0  # Start counting from 0
            else:
                pdf_tenant_tracker[pdf_name][tenant_name] += 1  # Increment for additional rows
            # Update tenant name with the correct Option #
            option_count = pdf_tenant_tracker[pdf_name][tenant_name]
            if option_count == 0:
                tenant_cell.value = tenant_name  # Keep the base name for the first occurrence
            else:
                tenant_cell.value = f"{tenant_name} (Option {option_count})"