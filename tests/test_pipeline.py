"""Tests for the upload -> parse -> upload orchestration.

S3 and the OCR parser are both stubbed; what is under test is the bookkeeping
around them, especially that temporary files never survive a failure.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from openpyxl import Workbook, load_workbook

import pipeline
from pipeline import ProcessingError, process_uploaded_pdf
from tenant_parser.workbook import DATA_HEADERS, append_row, ensure_headers


@pytest.fixture
def s3(monkeypatch: pytest.MonkeyPatch) -> dict:
    """Replace the storage layer with an in-memory double."""
    state: dict = {"uploaded": None, "master": None}

    monkeypatch.setattr(pipeline.storage, "download_pdf", lambda _key, dest: Path(dest).touch())

    def download_master(_prefix: str, destination: str) -> bool:
        if state["master"] is None:
            return False
        Path(destination).write_bytes(state["master"])
        return True

    def upload_master(prefix: str, source: str) -> str:
        state["uploaded"] = Path(source).read_bytes()
        return f"uploads/{prefix}_master.xlsx"

    monkeypatch.setattr(pipeline.storage, "download_master", download_master)
    monkeypatch.setattr(pipeline.storage, "upload_master", upload_master)
    return state


def workbook_bytes(tenant_count: int) -> bytes:
    book = Workbook()
    sheet = book.active
    sheet.title = "Retail Tenants"
    ensure_headers(sheet)
    for number in range(tenant_count):
        append_row(sheet, number + 2, ["roll.pdf", f"Tenant {number}"] + [None] * 9)
    with tempfile.NamedTemporaryFile(suffix=".xlsx") as handle:
        book.save(handle.name)
        return Path(handle.name).read_bytes()


def parser_adding(rows: int):
    """Stub parser that appends ``rows`` tenant rows to the workbook."""

    def parse(*, pdf_path: str, excel_path: str, generate_summary: bool) -> None:
        book = load_workbook(excel_path)
        sheet = book["Retail Tenants"] if "Retail Tenants" in book.sheetnames else book.active
        sheet.title = "Retail Tenants"
        ensure_headers(sheet)
        start = sheet.max_row + 1
        for offset in range(rows):
            append_row(sheet, start + offset, ["roll.pdf", f"New {offset}"] + [None] * 9)
        book.save(excel_path)

    return parse


def test_reports_the_rows_a_run_added(s3: dict, monkeypatch: pytest.MonkeyPatch):
    s3["master"] = workbook_bytes(tenant_count=3)
    monkeypatch.setattr(pipeline, "export_rent_roll_data_with_ocr", parser_adding(4))

    result = process_uploaded_pdf(user_id="sub-1", user_prefix="tester", filename="roll.pdf")

    assert result.rows_added == 4
    assert result.excel_s3_key == "uploads/tester_master.xlsx"


def test_creates_the_first_workbook_for_a_new_user(s3: dict, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(pipeline, "export_rent_roll_data_with_ocr", parser_adding(2))

    result = process_uploaded_pdf(user_id="sub-1", user_prefix="tester", filename="roll.pdf")

    assert result.rows_added == 2
    assert s3["uploaded"] is not None


def test_the_master_workbook_accumulates_across_uploads(s3: dict, monkeypatch: pytest.MonkeyPatch):
    s3["master"] = workbook_bytes(tenant_count=3)
    monkeypatch.setattr(pipeline, "export_rent_roll_data_with_ocr", parser_adding(2))

    process_uploaded_pdf(user_id="sub-1", user_prefix="tester", filename="roll.pdf")

    with tempfile.NamedTemporaryFile(suffix=".xlsx") as handle:
        Path(handle.name).write_bytes(s3["uploaded"])
        sheet = load_workbook(handle.name)["Retail Tenants"]

    assert sheet.max_row == 1 + 3 + 2  # headers plus both runs
    assert [cell.value for cell in sheet[1]] == list(DATA_HEADERS)


class TestFailureHandling:
    def test_a_download_failure_becomes_a_processing_error(
        self, s3: dict, monkeypatch: pytest.MonkeyPatch
    ):
        def fail(*_args: object) -> None:
            raise OSError("s3 unreachable")

        monkeypatch.setattr(pipeline.storage, "download_pdf", fail)

        with pytest.raises(ProcessingError, match="Could not download roll.pdf"):
            process_uploaded_pdf(user_id="sub-1", user_prefix="tester", filename="roll.pdf")

    def test_a_parser_failure_becomes_a_processing_error(
        self, s3: dict, monkeypatch: pytest.MonkeyPatch
    ):
        def fail(**_: object) -> None:
            raise RuntimeError("tesseract is not installed")

        monkeypatch.setattr(pipeline, "export_rent_roll_data_with_ocr", fail)

        with pytest.raises(ProcessingError, match="Could not parse roll.pdf"):
            process_uploaded_pdf(user_id="sub-1", user_prefix="tester", filename="roll.pdf")

    def test_a_failed_run_uploads_nothing(self, s3: dict, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(pipeline, "export_rent_roll_data_with_ocr", lambda **_: 1 / 0)

        with pytest.raises(ProcessingError):
            process_uploaded_pdf(user_id="sub-1", user_prefix="tester", filename="roll.pdf")

        assert s3["uploaded"] is None

    def test_temporary_files_are_cleaned_up_after_a_failure(
        self, s3: dict, monkeypatch: pytest.MonkeyPatch
    ):
        workdirs: list[Path] = []

        def capture_and_fail(*, pdf_path: str, excel_path: str, generate_summary: bool) -> None:
            workdirs.append(Path(pdf_path).parent)
            raise RuntimeError("boom")

        monkeypatch.setattr(pipeline, "export_rent_roll_data_with_ocr", capture_and_fail)

        with pytest.raises(ProcessingError):
            process_uploaded_pdf(user_id="sub-1", user_prefix="tester", filename="roll.pdf")

        assert workdirs and not workdirs[0].exists()
