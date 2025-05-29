import boto3
import os
import tempfile
import botocore.exceptions
from tenant_parser.exporter import export_rent_roll_data_with_ocr
from openpyxl import Workbook

s3_client = boto3.client('s3')
pdf_bucket = os.getenv('S3_BUCKET_NAME_PDF')
excel_bucket = os.getenv('S3_BUCKET_NAME_EXCEL')

def process_uploaded_pdf(user_id, filename):
    # Define S3 keys
    pdf_key = f"uploads/{user_id}/{filename}"
    excel_key = f"uploads/{user_id}_master.xlsx"

    # Create temporary local files
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf, \
         tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_excel:

        # Download the PDF from S3
        print(f"Downloading PDF from: bucket={pdf_bucket}, key={pdf_key}")
        s3_client.download_file(pdf_bucket, pdf_key, temp_pdf.name)

        # Check if master Excel exists and download it
        try:
            print(f"Attempting to download Excel file from: bucket={excel_bucket}, key={excel_key}")
            s3_client.download_file(excel_bucket, excel_key, temp_excel.name)
            excel_exists = True
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] in ['404', 'NoSuchKey']:
                print(f"Excel file not found in S3 at key: {excel_key}")
                excel_exists = False
                wb = Workbook()
                wb.save(temp_excel.name)
            else:
                raise

        # Run OCR and export (append if file exists)
        export_rent_roll_data_with_ocr(
            pdf_path=temp_pdf.name,
            excel_path=temp_excel.name,
            generate_summary=True  # assuming your function handles file creation/appending
        )

        # Upload the updated Excel file back to S3
        print(f"Uploading updated Excel to: bucket={excel_bucket}, key={excel_key}")
        s3_client.upload_file(temp_excel.name, excel_bucket, excel_key)

    return {
        'message': 'PDF processed and data added to master Excel.',
        'excel_s3_key': excel_key
    }
