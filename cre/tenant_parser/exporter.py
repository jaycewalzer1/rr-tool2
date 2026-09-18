"""Orchestrates the rent roll pipeline: PDF in, Excel workbook out.

The stages are deliberately thin wrappers over the specialised modules so the
flow reads top to bottom: find the pages, OCR them, clean the lines, split them
per tenant, parse each tenant's lease terms, then write and summarise.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from cre.tenant_parser import addresses, lines, ocr, workbook
from cre.tenant_parser.constants import anchor_tenants, popular_tenants
from cre.tenant_parser.fields import build_tenant_row

logger = logging.getLogger(__name__)


def export_rent_roll_data_with_ocr(
    pdf_path: str,
    excel_path: str,
    generate_summary: bool = True,
    data_sheet_name: str = workbook.DATA_SHEET_NAME,
    summary_sheet_name: str = workbook.SUMMARY_SHEET_NAME,
) -> int:
    """Append every tenant found in ``pdf_path`` to the workbook at ``excel_path``.

    The workbook accumulates across uploads: rows from previous rent rolls are
    what the summary sheet compares a new property against. Returns the number
    of rows written.
    """
    filename = Path(pdf_path).name

    rent_roll_pages = ocr.locate_rent_roll_pages(pdf_path)
    if not rent_roll_pages:
        logger.info("no rent roll pages found in %s", filename)
        return 0

    book = load_workbook(excel_path) if Path(excel_path).exists() else Workbook()
    sheet = _sheet(book, data_sheet_name)
    workbook.ensure_headers(sheet)

    property_address = addresses.extract_addresses(ocr.extract_text(pdf_path))
    rows_written = _write_tenant_rows(sheet, pdf_path, filename, rent_roll_pages, property_address)

    workbook.drop_incomplete_rows(sheet)
    workbook.relabel_tenant_options(sheet)

    if generate_summary:
        workbook.write_summary(
            _sheet(book, summary_sheet_name),
            sheet,
            pdf_name=filename,
            address=property_address[0],
            anchor_tenants=anchor_tenants,
            popular_tenants=popular_tenants,
        )

    book.save(excel_path)
    logger.info("wrote %d tenant row(s) from %s", rows_written, filename)
    return rows_written


def _write_tenant_rows(
    sheet: Worksheet,
    pdf_path: str,
    filename: str,
    page_numbers: list[int],
    property_addresses: list[addresses.Address],
) -> int:
    next_row = sheet.max_row + 1
    seen_tenants: dict[str, Any] = {}
    written = 0

    for ocr_lines in ocr.read_pages(pdf_path, page_numbers):
        for block in _tenant_blocks(lines.clean_lines(ocr_lines)):
            for segment in lines.split_tenants(" ".join(block)):
                for address, city, state, zip_code in property_addresses:
                    row = build_tenant_row(
                        segment,
                        pdf_name=filename,
                        address=address,
                        city=city,
                        state=state,
                        zip_code=zip_code,
                        seen_tenants=seen_tenants,
                    )
                    if row is None:
                        continue
                    workbook.append_row(sheet, next_row, row)
                    next_row += 1
                    written += 1

    return written


def _tenant_blocks(cleaned_lines: list[str]) -> list[list[str]]:
    """Group cleaned lines into blocks, one per tenant.

    A line starting with a letter begins a new tenant; lines starting with a
    figure are wrapped continuations of the row above.
    """
    blocks: list[list[str]] = []
    current: list[str] = []

    for line in cleaned_lines:
        if lines.starts_new_tenant(line) and current:
            blocks.append(current)
            current = []
        current.append(line)

    if current:
        blocks.append(current)

    return blocks


def _sheet(book: Workbook, name: str) -> Worksheet:
    return book[name] if name in book.sheetnames else book.create_sheet(name)
