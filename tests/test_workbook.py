"""Tests for the generated workbook: the data sheet and the comps summary."""

from __future__ import annotations

from openpyxl import Workbook

from cre.tenant_parser.workbook import (
    DATA_HEADERS,
    append_row,
    categorise_tenants,
    drop_incomplete_rows,
    ensure_headers,
    relabel_tenant_options,
    tenant_entries,
    write_summary,
)


def data_sheet(rows: list[list] | None = None):
    sheet = Workbook().active
    ensure_headers(sheet)
    for number, row in enumerate(rows or [], start=2):
        append_row(sheet, number, row)
    return sheet


def tenant_row(tenant: str, *, pdf="centre.pdf", sqft=1800, begin="03/01/2019", psf="$32.50"):
    return [
        pdf,
        tenant,
        sqft,
        begin,
        "02/28/2024",
        psf,
        "$58,500",
        "Austin",
        "TX",
        "78701",
        "1 Main",
    ]


class TestEnsureHeaders:
    def test_writes_headers_to_an_empty_sheet(self):
        sheet = Workbook().active
        ensure_headers(sheet)
        assert [cell.value for cell in sheet[1]] == list(DATA_HEADERS)

    def test_does_not_duplicate_headers_on_an_existing_sheet(self):
        sheet = data_sheet([tenant_row("Subway")])
        ensure_headers(sheet)
        assert sheet.max_row == 2


class TestDropIncompleteRows:
    def test_removes_rows_missing_a_size_or_start_date(self):
        sheet = data_sheet(
            [
                tenant_row("Subway"),
                tenant_row("Starbucks", sqft=None),
                tenant_row("Panda Express", begin=None),
            ]
        )

        drop_incomplete_rows(sheet)

        assert [row[1].value for row in sheet.iter_rows(min_row=2)] == ["Subway"]

    def test_deletes_from_the_bottom_so_row_numbers_stay_valid(self):
        sheet = data_sheet(
            [tenant_row("Subway", sqft=None), tenant_row("Starbucks"), tenant_row("KFC", sqft=None)]
        )

        drop_incomplete_rows(sheet)

        assert [row[1].value for row in sheet.iter_rows(min_row=2)] == ["Starbucks"]


class TestRelabelTenantOptions:
    def test_numbers_repeat_appearances_within_one_pdf(self):
        sheet = data_sheet([tenant_row("Subway"), tenant_row("Subway"), tenant_row("Subway")])

        relabel_tenant_options(sheet)

        assert [row[1].value for row in sheet.iter_rows(min_row=2)] == [
            "Subway",
            "Subway (Option 1)",
            "Subway (Option 2)",
        ]

    def test_numbering_restarts_for_each_pdf(self):
        sheet = data_sheet([tenant_row("Subway"), tenant_row("Subway", pdf="other.pdf")])

        relabel_tenant_options(sheet)

        assert [row[1].value for row in sheet.iter_rows(min_row=2)] == ["Subway", "Subway"]

    def test_stale_labels_are_recomputed_after_rows_are_dropped(self):
        sheet = data_sheet([tenant_row("Subway Option 3")])

        relabel_tenant_options(sheet)

        assert sheet.cell(row=2, column=2).value == "Subway"


class TestCategoriseTenants:
    def test_splits_anchors_from_inline_tenants(self):
        sheet = data_sheet([tenant_row("Subway"), tenant_row("Target", psf="$8.00")])

        anchors, inline = categorise_tenants(sheet, "centre.pdf", {"Target"}, {"Subway"})

        assert anchors == [("Target", "$8.00")]
        assert inline == [("Subway", "$32.50")]

    def test_keeps_the_lowest_rent_for_a_repeated_tenant(self):
        sheet = data_sheet([tenant_row("Subway", psf="$32.50"), tenant_row("Subway", psf="$24.00")])

        _, inline = categorise_tenants(sheet, "centre.pdf", set(), {"Subway"})

        assert inline == [("Subway", "$24.00")]

    def test_ignores_tenants_from_other_pdfs(self):
        sheet = data_sheet([tenant_row("Subway", pdf="other.pdf")])

        anchors, inline = categorise_tenants(sheet, "centre.pdf", set(), {"Subway"})

        assert (anchors, inline) == ([], [])


class TestTenantEntries:
    def test_collects_comparables_across_every_pdf(self):
        sheet = data_sheet([tenant_row("Subway"), tenant_row("Subway", pdf="other.pdf")])

        assert len(tenant_entries(sheet, "Subway")) == 2


class TestWriteSummary:
    def test_reports_how_a_rent_compares_with_the_comp_set(self):
        book = Workbook()
        sheet = book.active
        ensure_headers(sheet)
        append_row(sheet, 2, tenant_row("Subway", psf="$30.00"))
        append_row(sheet, 3, tenant_row("Subway", pdf="other.pdf", psf="$20.00"))

        write_summary(
            book.create_sheet("Summary 1"),
            sheet,
            pdf_name="centre.pdf",
            address=("1 Main", "Austin", "TX", "78701"),
            anchor_tenants=set(),
            popular_tenants={"Subway"},
        )

        text = "\n".join(
            str(cell.value) for row in book["Summary 1"].iter_rows() for cell in row if cell.value
        )
        assert "$25.00" in text  # average of $30 and $20
        assert "20.00% above market" in text  # $30 against a $25 average
