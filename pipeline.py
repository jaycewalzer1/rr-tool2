"""Orchestrates the upload -> OCR -> workbook pipeline.

The parser writes to a local ``.xlsx``, so each run round-trips the user's
master workbook through a temporary directory that is always cleaned up, even
when parsing fails part-way through a document.
"""

from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path

from openpyxl import Workbook, load_workbook

import storage
from tenant_parser import export_rent_roll_data_with_ocr

logger = logging.getLogger(__name__)


class ProcessingError(RuntimeError):
    """Raised when a rent roll could not be parsed into the master workbook."""


@dataclass(frozen=True)
class ProcessingResult:
    """Outcome of processing one uploaded rent roll."""

    excel_s3_key: str
    rows_added: int


def process_uploaded_pdf(*, user_id: str, user_prefix: str, filename: str) -> ProcessingResult:
    """Parse an uploaded rent roll and merge the results into the master workbook.

    Args:
        user_id: Cognito subject id; namespaces the PDF in S3.
        user_prefix: Slug used for the per-user master workbook key.
        filename: Name of the already-uploaded PDF within the user's prefix.

    Returns:
        The S3 key of the updated workbook and how many rows the run added.

    Raises:
        ProcessingError: If the PDF could not be downloaded or parsed.
    """
    with tempfile.TemporaryDirectory(prefix="rentroll-") as workdir:
        local_pdf = Path(workdir) / filename
        local_excel = Path(workdir) / storage.excel_filename(user_prefix)

        try:
            storage.download_pdf(storage.pdf_key(user_id, filename), str(local_pdf))
        except Exception as error:  # boto3 raises a wide range of client errors
            raise ProcessingError(f"Could not download {filename} from storage.") from error

        if not storage.download_master(user_prefix, str(local_excel)):
            logger.info("creating first master workbook", extra={"user_prefix": user_prefix})
            Workbook().save(local_excel)

        rows_before = _row_count(local_excel)

        try:
            export_rent_roll_data_with_ocr(
                pdf_path=str(local_pdf),
                excel_path=str(local_excel),
                generate_summary=True,
            )
        except Exception as error:  # OCR and parsing fail in many unrelated ways
            # "filename" is a reserved LogRecord attribute; using it here would
            # raise KeyError from inside the handler and mask the real failure.
            logger.exception("rent roll parsing failed", extra={"pdf_name": filename})
            raise ProcessingError(f"Could not parse {filename}.") from error

        rows_added = max(_row_count(local_excel) - rows_before, 0)
        excel_s3_key = storage.upload_master(user_prefix, str(local_excel))

    logger.info(
        "rent roll processed",
        extra={"pdf_name": filename, "user_prefix": user_prefix, "rows_added": rows_added},
    )
    return ProcessingResult(excel_s3_key=excel_s3_key, rows_added=rows_added)


def _row_count(excel_path: Path) -> int:
    """Number of tenant rows currently in the workbook's data sheet."""
    workbook = load_workbook(excel_path, read_only=True)
    try:
        if storage.DATA_SHEET_NAME not in workbook.sheetnames:
            return 0
        # Subtract the header row.
        return max(workbook[storage.DATA_SHEET_NAME].max_row - 1, 0)
    finally:
        workbook.close()
