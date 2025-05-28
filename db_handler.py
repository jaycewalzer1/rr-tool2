import boto3
import os
import tempfile
from tenant_parser.exporter import export_rent_roll_data_with_ocr

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
        s3_client.download_file(pdf_bucket, pdf_key, temp_pdf.name)

        # Check if master Excel exists and download it
        try:
            s3_client.download_file(excel_bucket, excel_key, temp_excel.name)
            excel_exists = True
        except s3_client.exceptions.NoSuchKey:
            excel_exists = False

        # Run OCR and export (append if file exists)
        export_rent_roll_data_with_ocr(
            pdf_path=temp_pdf.name,
            excel_path=temp_excel.name,
            generate_summary=True  # assuming it handles appending
        )

        # Upload the updated Excel file back to S3
        s3_client.upload_file(temp_excel.name, excel_bucket, excel_key)

    return {
        'message': 'PDF processed and data added to master Excel.',
        'excel_s3_key': excel_key
    }
