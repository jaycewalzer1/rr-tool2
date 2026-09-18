"""S3 access layer.

Every S3 key in the product is derived here, which keeps the tenant-isolation
rule (``uploads/<user_id>/...``) in one auditable place instead of being
re-implemented in each view.
"""

from __future__ import annotations

import functools
import logging
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Any

import pandas as pd
from botocore.exceptions import ClientError
from flask import current_app

from cre.config import Config
from cre.tenant_parser.workbook import DATA_SHEET_NAME

logger = logging.getLogger(__name__)

_MISSING_OBJECT_CODES = frozenset({"404", "NoSuchKey", "NoSuchBucket"})


@dataclass(frozen=True)
class StoredFile:
    """Metadata for one PDF a user has uploaded."""

    filename: str
    s3_key: str
    size: int
    last_modified: datetime
    download_url: str


def _config() -> Config:
    return current_app.config["APP_CONFIG"]


@functools.lru_cache(maxsize=4)
def _client(region: str) -> Any:
    import boto3

    return boto3.client("s3", region_name=region)


def s3_client() -> Any:
    """Return a cached boto3 S3 client for the configured region."""
    return _client(_config().cognito.region)


def is_missing_object(error: ClientError) -> bool:
    """True when a ``ClientError`` simply means the key does not exist."""
    return error.response["Error"]["Code"] in _MISSING_OBJECT_CODES


def pdf_key(user_id: str, filename: str) -> str:
    """Key for a user's uploaded rent roll PDF."""
    return f"uploads/{user_id}/{filename}"


def pdf_prefix(user_id: str) -> str:
    """Prefix containing every PDF owned by ``user_id``."""
    return f"uploads/{user_id}/"


def excel_key(user_prefix: str) -> str:
    """Key for a user's cumulative master workbook."""
    return f"uploads/{user_prefix}_master.xlsx"


def excel_filename(user_prefix: str) -> str:
    """Filename presented to the user when downloading the master workbook."""
    return f"{user_prefix}_master.xlsx"


def presigned_upload_url(key: str) -> str:
    """Presigned ``PUT`` URL so the browser uploads straight to S3.

    Keeping large PDFs off the application server avoids tying up a gunicorn
    worker for the duration of an upload.
    """
    return s3_client().generate_presigned_url(
        "put_object",
        Params={"Bucket": _config().storage.pdf_bucket, "Key": key},
        ExpiresIn=_config().storage.presigned_url_ttl_seconds,
    )


def presigned_download_url(key: str) -> str:
    """Presigned ``GET`` URL, so the PDF bucket can stay fully private."""
    return s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": _config().storage.pdf_bucket, "Key": key},
        ExpiresIn=_config().storage.presigned_url_ttl_seconds,
    )


def list_pdfs(user_id: str) -> list[StoredFile]:
    """List the PDFs a user has uploaded, newest first."""
    response = s3_client().list_objects_v2(
        Bucket=_config().storage.pdf_bucket, Prefix=pdf_prefix(user_id)
    )
    files = [
        StoredFile(
            filename=obj["Key"].rsplit("/", 1)[-1],
            s3_key=obj["Key"],
            size=obj["Size"],
            last_modified=obj["LastModified"],
            download_url=presigned_download_url(obj["Key"]),
        )
        for obj in response.get("Contents", [])
        if obj["Key"].lower().endswith(".pdf")
    ]
    return sorted(files, key=lambda file: file.last_modified, reverse=True)


def delete_pdf(key: str) -> None:
    """Delete a single PDF. Callers must verify ownership of ``key`` first."""
    s3_client().delete_object(Bucket=_config().storage.pdf_bucket, Key=key)


def download_pdf(key: str, destination: str) -> None:
    """Download a PDF to a local path."""
    s3_client().download_file(_config().storage.pdf_bucket, key, destination)


def master_exists(user_prefix: str) -> bool:
    """True when the user already has a master workbook in S3."""
    try:
        s3_client().head_object(Bucket=_config().storage.excel_bucket, Key=excel_key(user_prefix))
    except ClientError as error:
        if is_missing_object(error):
            return False
        raise
    return True


def download_master(user_prefix: str, destination: str) -> bool:
    """Download the master workbook, returning ``False`` if it does not exist."""
    try:
        s3_client().download_file(
            _config().storage.excel_bucket, excel_key(user_prefix), destination
        )
    except ClientError as error:
        if is_missing_object(error):
            return False
        raise
    return True


def upload_master(user_prefix: str, source: str) -> str:
    """Upload the master workbook and return its S3 key."""
    key = excel_key(user_prefix)
    s3_client().upload_file(source, _config().storage.excel_bucket, key)
    return key


def read_master(user_prefix: str) -> pd.DataFrame:
    """Load the parsed tenant rows from the user's master workbook.

    Raises:
        ClientError: If the workbook does not exist in S3.
    """
    obj = s3_client().get_object(Bucket=_config().storage.excel_bucket, Key=excel_key(user_prefix))
    buffer = BytesIO(obj["Body"].read())

    try:
        frame = pd.read_excel(buffer, sheet_name=DATA_SHEET_NAME)
    except ValueError:
        # Older workbooks predate the named data sheet; fall back to position.
        buffer.seek(0)
        frame = pd.read_excel(buffer, sheet_name=1)

    return frame.dropna(how="all")
