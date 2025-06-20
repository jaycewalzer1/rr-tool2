import boto3
import os
import tempfile
import botocore.exceptions
from tenant_parser.exporter import export_rent_roll_data_with_ocr
from openpyxl import Workbook

s3_client = boto3.client('s3')
pdf_bucket = os.getenv('S3_BUCKET_NAME_PDF')
excel_bucket = os.getenv('S3_BUCKET_NAME_EXCEL')

def process_uploaded_pdf(user_id, user_prefix, filename):
    print(f"[PROCESS] user_id: {user_id}")
    print(f"[PROCESS] user_prefix: {user_prefix}")

    # Define S3 keys
    pdf_key = f"uploads/{user_id}/{filename}"
    excel_key = f"uploads/{user_prefix}_master.xlsx"

    # Construct real file paths using the original filename
    temp_dir = tempfile.gettempdir()
    local_pdf_path = os.path.join(temp_dir, filename)
    local_excel_path = os.path.join(temp_dir, f"{user_prefix}_master.xlsx")

    # Download the PDF from S3
    print(f"Downloading PDF from: bucket={pdf_bucket}, key={pdf_key}")
    s3_client.download_file(pdf_bucket, pdf_key, local_pdf_path)

    # Check if master Excel exists and download it
    try:
        print(f"Attempting to download Excel file from: bucket={excel_bucket}, key={excel_key}")
        s3_client.download_file(excel_bucket, excel_key, local_excel_path)
        excel_exists = True
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] in ['404', 'NoSuchKey']:
            print(f"Excel file not found in S3 at key: {excel_key}")
            excel_exists = False
            wb = Workbook()
            wb.save(local_excel_path)
        else:
            raise

    # Run OCR and export
    export_rent_roll_data_with_ocr(
        pdf_path=local_pdf_path,
        excel_path=local_excel_path,
        generate_summary=True
    )

    # Upload the updated Excel file back to S3
    print(f"Uploading updated Excel to: bucket={excel_bucket}, key={excel_key}")
    s3_client.upload_file(
        local_excel_path,
        excel_bucket,
        excel_key,
        ExtraArgs={'ACL': 'bucket-owner-full-control'}
    )
    return {
        'message': 'PDF processed and data added to master Excel.',
        'excel_s3_key': excel_key
    }
