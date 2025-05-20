import os
import pandas as pd

def save_addresses_to_excel(addresses, excel_path, sheet_name):
    df = pd.DataFrame(addresses, columns=['pdf name', 'city', 'state', 'zip', 'address']).drop_duplicates()
    """
    Save a list of address entries to an Excel sheet, avoiding duplicates and appending if the file exists.
    """
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

def auto_adjust_column_widths(sheet):
    """
    Resize each column in an Excel worksheet based on the maximum content width for readability.
    """

    for col in sheet.columns:
        max_length = 0
        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        sheet.column_dimensions[col[0].column_letter].width = max_length + 2

def remove_rows_without_square_footage_or_dates(sheet):
    """
    Remove rows from the worksheet that lack square footage or lease start date information.
    """
    rows_to_delete = [
        row[0].row for row in sheet.iter_rows(min_row=2, values_only=False)
        if not row[2].value or not row[3].value
    ]
    for row_num in reversed(rows_to_delete):
        sheet.delete_rows(row_num, 1)

def recalculate_tenant_options(sheet):
    """
    Recalculate and append '(Option N)' suffixes to repeated tenant entries from the same PDF.
    Ensures tenant names are uniquely identified across multiple lease terms.
    """
    pdf_tenant_tracker = {}
    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, values_only=False):
        pdf_name_cell = row[0]
        tenant_cell = row[1]
        if pdf_name_cell.value and tenant_cell.value:
            pdf_name = pdf_name_cell.value
            tenant_name = tenant_cell.value.split(" Option")[0]
            if pdf_name not in pdf_tenant_tracker:
                pdf_tenant_tracker[pdf_name] = {}
            if tenant_name not in pdf_tenant_tracker[pdf_name]:
                pdf_tenant_tracker[pdf_name][tenant_name] = 0
            else:
                pdf_tenant_tracker[pdf_name][tenant_name] += 1
            option_count = pdf_tenant_tracker[pdf_name][tenant_name]
            tenant_cell.value = tenant_name if option_count == 0 else f"{tenant_name} (Option {option_count})"
