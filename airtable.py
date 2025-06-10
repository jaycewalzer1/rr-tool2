import boto3
import pandas as pd
from io import BytesIO
import requests
import os

def read_excel_from_s3(user_id):
    s3 = boto3.client('s3')
    bucket = os.getenv('S3_BUCKET_NAME_EXCEL')
    key = f"uploads/{user_id}_master.xlsx"

    obj = s3.get_object(Bucket=bucket, Key=key)
    excel_data = obj['Body'].read()
    
    # Load the first sheet explicitly
    return pd.read_excel(BytesIO(excel_data), sheet_name=1)

def push_to_airtable(dataframe, user_id):
    # Example logic – adjust as needed
    s3 = boto3.client('s3')
    bucket = os.getenv('S3_BUCKET_NAME_EXCEL')
    key = f"uploads/{user_id}_master.xlsx"

    with BytesIO() as buffer:
        dataframe.to_excel(buffer, index=False)
        buffer.seek(0)
        s3.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())
