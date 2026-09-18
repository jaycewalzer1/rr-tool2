"""Smoke tests for the HTTP layer: pages render and the file API behaves."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import pytest
from flask.testing import FlaskClient

from pipeline import ProcessingError, ProcessingResult
from storage import StoredFile


@pytest.mark.parametrize(
    "path", ["/", "/platform", "/solutions", "/contact", "/privacy", "/terms", "/subscription"]
)
def test_public_pages_render(client: FlaskClient, path: str):
    assert client.get(path).status_code == 200


@pytest.mark.parametrize("path", ["/login", "/signup", "/reset"])
def test_auth_pages_render(client: FlaskClient, path: str):
    assert client.get(path).status_code == 200


def test_health_check_reports_ok(client: FlaskClient):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_unknown_paths_render_the_404_page(client: FlaskClient):
    assert client.get("/no-such-page").status_code == 404


def test_every_response_carries_a_request_id(client: FlaskClient):
    assert client.get("/").headers["X-Request-ID"] != "-"


class TestFileApi:
    def stored_file(self) -> StoredFile:
        return StoredFile(
            filename="roll.pdf",
            s3_key="uploads/cognito-sub-123/roll.pdf",
            size=2048,
            last_modified=datetime(2025, 1, 1),
            download_url="https://s3.example/roll.pdf",
        )

    def test_lists_only_the_callers_files(
        self,
        logged_in_client: FlaskClient,
        verified_account: None,
        monkeypatch: pytest.MonkeyPatch,
    ):
        seen: list[str] = []

        def fake_list(user_id: str) -> list[StoredFile]:
            seen.append(user_id)
            return [self.stored_file()]

        monkeypatch.setattr("storage.list_pdfs", fake_list)

        response = logged_in_client.get("/api/s3/files")

        assert seen == ["cognito-sub-123"]
        assert response.json["files"][0]["filename"] == "roll.pdf"

    def test_processing_reports_the_rows_added(
        self,
        logged_in_client: FlaskClient,
        verified_account: None,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr(
            "routes.dashboard_routes.process_uploaded_pdf",
            lambda **_: ProcessingResult(excel_s3_key="uploads/tester_master.xlsx", rows_added=12),
        )

        response = logged_in_client.post("/api/s3/files", json={"filename": "roll.pdf"})

        assert response.status_code == 200
        assert response.json["rows_added"] == 12

    def test_a_processing_failure_is_a_bad_gateway(
        self,
        logged_in_client: FlaskClient,
        verified_account: None,
        monkeypatch: pytest.MonkeyPatch,
    ):
        def fail(**_: object) -> None:
            raise ProcessingError("Could not parse roll.pdf.")

        monkeypatch.setattr("routes.dashboard_routes.process_uploaded_pdf", fail)

        response = logged_in_client.post("/api/s3/files", json={"filename": "roll.pdf"})

        assert response.status_code == 502
        assert "roll.pdf" in response.json["error"]

    def test_a_missing_filename_is_rejected(
        self, logged_in_client: FlaskClient, verified_account: None
    ):
        assert logged_in_client.post("/api/s3/upload-url", json={}).status_code == 400


class TestMapPage:
    def test_parsed_rows_are_delivered_as_json_not_html(
        self,
        logged_in_client: FlaskClient,
        verified_account: None,
        monkeypatch: pytest.MonkeyPatch,
    ):
        """Spreadsheet text must never reach the page as markup.

        Popup content used to be built server-side and injected with innerHTML,
        so a tenant name could execute as script.
        """
        monkeypatch.setattr(
            "storage.read_master",
            lambda _prefix: pd.DataFrame(
                [{"Address": "1 Main St, Austin TX", "Tenant Name": "<img src=x onerror=alert(1)>"}]
            ),
        )

        body = logged_in_client.get("/gmaps").get_data(as_text=True)

        assert "<img src=x onerror=alert(1)>" not in body
        assert 'id="map-points"' in body


class TestDatabasePage:
    def test_renders_an_empty_state_without_a_workbook(
        self,
        logged_in_client: FlaskClient,
        verified_account: None,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr("routes.dashboard_routes._load_master", lambda _prefix: None)
        monkeypatch.setattr("storage.list_pdfs", lambda _user_id: [])

        assert logged_in_client.get("/database").status_code == 200
