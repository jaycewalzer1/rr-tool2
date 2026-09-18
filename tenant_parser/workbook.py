"""Building the output workbook: the tenant data sheet and the comps summary."""

from __future__ import annotations

import logging
from typing import Any

from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet

logger = logging.getLogger(__name__)

DATA_SHEET_NAME = "Retail Tenants"
SUMMARY_SHEET_NAME = "Summary 1"

DATA_HEADERS = (
    "PDF Name",
    "Tenant Name",
    "Square Feet",
    "Lease Begin Date",
    "Lease End Date",
    "Rent PSF",
    "Annual Rent",
    "City",
    "State",
    "Zip",
    "Address",
)

# Column offsets within a data-sheet row, matching DATA_HEADERS.
PDF_NAME_INDEX = 0
TENANT_INDEX = 1
SQUARE_FEET_INDEX = 2
BEGIN_DATE_INDEX = 3
RENT_PSF_INDEX = 5
CITY_INDEX = 7
STATE_INDEX = 8

_HEADER_FILL = PatternFill(start_color="000000", end_color="000000", fill_type="solid")
_HEADER_FONT = Font(color="FFFFFF", bold=True)


def ensure_headers(sheet: Worksheet) -> None:
    """Write the column headers to a freshly created data sheet.

    Headers are written by cell rather than with ``append``: reading a sheet to
    decide whether it is empty materialises cells, which advances the cursor
    ``append`` uses and would silently push the headers down to row 2.
    """
    is_empty = sheet.max_row == 1 and sheet.max_column == 1 and sheet["A1"].value is None
    if is_empty:
        append_row(sheet, 1, list(DATA_HEADERS))


def append_row(sheet: Worksheet, row_number: int, values: list[Any]) -> None:
    for column, value in enumerate(values, start=1):
        sheet.cell(row=row_number, column=column, value=value)


def drop_incomplete_rows(sheet: Worksheet) -> None:
    """Remove rows with no unit size or no lease start - they are OCR noise."""
    incomplete = [
        row[0].row
        for row in sheet.iter_rows(min_row=2)
        if not row[SQUARE_FEET_INDEX].value or not row[BEGIN_DATE_INDEX].value
    ]
    # Delete bottom-up so earlier deletions do not shift later row numbers.
    for row_number in reversed(incomplete):
        sheet.delete_rows(row_number, 1)
    logger.debug("dropped %d incomplete row(s)", len(incomplete))


def relabel_tenant_options(sheet: Worksheet) -> None:
    """Number repeat appearances of a tenant within one PDF as options.

    The provisional labels applied during parsing go stale once incomplete rows
    are dropped, so the numbering is recomputed from the surviving rows.
    """
    counts: dict[str, dict[str, int]] = {}

    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row):
        pdf_cell = row[PDF_NAME_INDEX]
        tenant_cell = row[TENANT_INDEX]
        if not pdf_cell.value or not tenant_cell.value:
            continue

        base_name = str(tenant_cell.value).split(" Option")[0]
        seen = counts.setdefault(str(pdf_cell.value), {})
        occurrence = seen.get(base_name, -1) + 1
        seen[base_name] = occurrence

        tenant_cell.value = base_name if occurrence == 0 else f"{base_name} (Option {occurrence})"


def write_summary(
    summary_sheet: Worksheet,
    data_sheet: Worksheet,
    *,
    pdf_name: str,
    address: tuple[str, str, str, str],
    anchor_tenants: set[str],
    popular_tenants: set[str],
) -> None:
    """Write the comparables summary for one rent roll.

    Four blocks: the property's location, its anchor tenants, its inline
    tenants, and - per tenant - how its rent compares with every other
    occurrence of that same tenant already in the workbook.
    """
    street, city, state, zip_code = address
    anchors, inline = categorise_tenants(data_sheet, pdf_name, anchor_tenants, popular_tenants)

    _table_header(summary_sheet, f"Table 1 - General Information Table on {pdf_name}", width=4)
    summary_sheet.append(["PDF Name", "State", "City", "Zip Code", "Address"])
    summary_sheet.append([pdf_name, state, city, zip_code, street])
    summary_sheet.append([""])

    for title, tenants in (
        (f"Table 2 - Anchor Tenants in {pdf_name}", anchors),
        (f"Table 3 - Popular Tenants in {pdf_name}", inline),
    ):
        _table_header(summary_sheet, title, width=2)
        summary_sheet.append(["Tenant Name", "Rent PSF"])
        for name, rent_psf in tenants:
            summary_sheet.append([name, rent_psf])
        summary_sheet.append([""])

    for tenant_name in _tenants_in_pdf(data_sheet, pdf_name):
        _write_tenant_comparison(summary_sheet, data_sheet, pdf_name, tenant_name)

    logger.info("summary written for %s", pdf_name)


def categorise_tenants(
    data_sheet: Worksheet,
    pdf_name: str,
    anchor_tenants: set[str],
    popular_tenants: set[str],
) -> tuple[list[tuple[str, Any]], list[tuple[str, Any]]]:
    """Split one PDF's tenants into anchors and inline tenants, cheapest rent first.

    A tenant can appear on several rows (options, renewals); the lowest rent PSF
    is kept because that is the in-place base rent.
    """
    lowest_rent: dict[str, Any] = {}

    for row in data_sheet.iter_rows(min_row=2, values_only=True):
        if row[PDF_NAME_INDEX] != pdf_name:
            continue
        tenant_name, rent_psf = row[TENANT_INDEX], row[RENT_PSF_INDEX]
        if not tenant_name or not rent_psf:
            continue
        if tenant_name not in lowest_rent or lowest_rent[tenant_name] > rent_psf:
            lowest_rent[tenant_name] = rent_psf

    anchors = [(name, rent) for name, rent in lowest_rent.items() if name in anchor_tenants]
    inline = [(name, rent) for name, rent in lowest_rent.items() if name in popular_tenants]
    return anchors, inline


def tenant_entries(data_sheet: Worksheet, tenant_name: str) -> list[tuple[Any, ...]]:
    """Every row for ``tenant_name`` across all PDFs - the comparable set."""
    return [
        (tenant_name, row[RENT_PSF_INDEX], row[CITY_INDEX], row[STATE_INDEX])
        for row in data_sheet.iter_rows(min_row=2, values_only=True)
        if row[TENANT_INDEX] == tenant_name
    ]


def _tenants_in_pdf(data_sheet: Worksheet, pdf_name: str) -> set[str]:
    return {
        row[TENANT_INDEX]
        for row in data_sheet.iter_rows(min_row=2, values_only=True)
        if row[PDF_NAME_INDEX] == pdf_name and row[TENANT_INDEX]
    }


def _write_tenant_comparison(
    summary_sheet: Worksheet, data_sheet: Worksheet, pdf_name: str, tenant_name: str
) -> None:
    entries = tenant_entries(data_sheet, tenant_name)
    if not entries:
        return

    _table_header(summary_sheet, f"Details for Tenant: {tenant_name}", width=4)
    summary_sheet.append(["Tenant Name", "Smallest Rent PSF", "City", "State"])

    rents = []
    for entry in entries:
        summary_sheet.append(list(entry))
        rent = _as_float(entry[1])
        if rent is not None:
            rents.append(rent)

    if not rents:
        summary_sheet.append(["Average Rent PSF", "N/A"])
        summary_sheet.append([""])
        return

    average = sum(rents) / len(rents)
    summary_sheet.append(["Average Rent PSF", f"${average:.2f}"])

    difference = (rents[0] / average - 1) * 100
    direction = "above" if difference > 0 else "below"
    summary_sheet.append(
        [
            f"The {tenant_name} for {pdf_name} is {abs(difference):.2f}% "
            f"{direction} market from our existing comp set."
        ]
    )
    summary_sheet.append([""])


def _table_header(sheet: Worksheet, title: str, *, width: int) -> None:
    sheet.append([title])
    row = sheet.max_row
    sheet.merge_cells(start_row=row, start_column=1, end_row=row, end_column=width)
    header = sheet.cell(row=row, column=1)
    header.fill = _HEADER_FILL
    header.font = _HEADER_FONT


def _as_float(value: Any) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("$", "").replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None
