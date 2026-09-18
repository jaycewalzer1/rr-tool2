"""Authenticated views: file management, the parsed database and the map."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
from botocore.exceptions import ClientError
from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    jsonify,
    render_template,
    request,
    send_file,
    session,
)

import storage
from decorators import login_required, verify_account
from pipeline import ProcessingError, process_uploaded_pdf
from utils import safe_filename, user_prefix

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint("dashboard", __name__)

ADDRESS_COLUMN = "Address"
RENT_COLUMN = "Annual Rent"


@dashboard_bp.route("/dashboard")
@dashboard_bp.route("/files")
@login_required
@verify_account
def files() -> str:
    """Upload page listing the user's rent roll PDFs."""
    return render_template("dashboard/files.html")


@dashboard_bp.route("/database")
@login_required
@verify_account
def database() -> str:
    """Render the parsed tenant table extracted from the user's rent rolls."""
    prefix = user_prefix()
    frame = _load_master(prefix)

    return render_template(
        "dashboard/database.html",
        excel_file=storage.excel_filename(prefix) if frame is not None else None,
        pdf_list=[file.filename for file in _safe_list_pdfs()],
        table_html=None
        if frame is None
        else frame.to_html(classes="excel-table table table-striped table-bordered", index=False),
    )


@dashboard_bp.route("/gmaps")
@login_required
@verify_account
def gmaps() -> str:
    """Plot every parsed tenant on a map, coloured by annual rent."""
    frame = _load_master(user_prefix())

    return render_template(
        "dashboard/gmaps.html",
        GOOGLE_MAPS_API_KEY=current_app.config["GOOGLE_MAPS_API_KEY"],
        map_points=_map_points(frame),
    )


@dashboard_bp.route("/api/s3/upload-url", methods=["POST"])
@login_required
@verify_account
def generate_presigned_upload_url() -> tuple[Response, int] | Response:
    """Hand the browser a short-lived URL to upload a PDF directly to S3."""
    payload = request.get_json(silent=True) or {}
    filename = safe_filename(str(payload.get("filename", "")))
    if not filename:
        return jsonify(error="A filename is required."), 400
    if not filename.lower().endswith(".pdf"):
        return jsonify(error="Only PDF rent rolls can be uploaded."), 400

    key = storage.pdf_key(_user_id(), filename)
    return jsonify(upload_url=storage.presigned_upload_url(key), s3_key=key, filename=filename)


@dashboard_bp.route("/api/s3/files", methods=["GET"])
@login_required
@verify_account
def list_s3_files() -> Response:
    """List the current user's uploaded PDFs with presigned view URLs."""
    files = storage.list_pdfs(_user_id())
    return jsonify(
        files=[
            {
                "filename": file.filename,
                "s3_key": file.s3_key,
                "public_url": file.download_url,
                "size": file.size,
                "last_modified": file.last_modified.isoformat(),
            }
            for file in files
        ]
    )


@dashboard_bp.route("/api/s3/files", methods=["POST"])
@login_required
@verify_account
def handle_uploaded_file() -> tuple[Response, int] | Response:
    """Run the OCR pipeline over a freshly uploaded PDF."""
    payload = request.get_json(silent=True) or {}
    filename = safe_filename(str(payload.get("filename", "")))
    if not filename:
        return jsonify(error="A filename is required."), 400

    try:
        result = process_uploaded_pdf(
            user_id=_user_id(), user_prefix=user_prefix(), filename=filename
        )
    except ProcessingError as error:
        return jsonify(error=str(error)), 502

    return jsonify(
        message="File processed successfully.",
        excel_key=result.excel_s3_key,
        rows_added=result.rows_added,
    )


@dashboard_bp.route("/api/s3/files", methods=["DELETE"])
@login_required
@verify_account
def delete_s3_file() -> tuple[Response, int] | Response:
    """Delete one of the current user's PDFs."""
    payload = request.get_json(silent=True) or {}
    s3_key = str(payload.get("s3_key", ""))

    # Ownership check: the key must live under this user's own prefix.
    if not s3_key or not s3_key.startswith(storage.pdf_prefix(_user_id())):
        return jsonify(error="File not found."), 404

    storage.delete_pdf(s3_key)
    return jsonify(message="File deleted successfully.")


@dashboard_bp.route("/dashboard/download-excel/<path:filename>")
@login_required
@verify_account
def download_master_excel(filename: str) -> Response:
    """Stream the caller's master workbook back to the browser."""
    prefix = user_prefix()
    if filename != storage.excel_filename(prefix):
        abort(404)

    obj = storage.s3_client().get_object(
        Bucket=current_app.config["APP_CONFIG"].storage.excel_bucket,
        Key=storage.excel_key(prefix),
    )
    return send_file(
        obj["Body"],
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        download_name=filename,
        as_attachment=True,
    )


def _user_id() -> str:
    """Cognito subject for the logged-in user (guaranteed by ``login_required``)."""
    return str(session["user"]["user_id"])


def _safe_list_pdfs() -> list[storage.StoredFile]:
    try:
        return storage.list_pdfs(_user_id())
    except ClientError:
        logger.exception("could not list uploaded pdfs")
        return []


def _load_master(prefix: str) -> pd.DataFrame | None:
    """Read the user's master workbook, or ``None`` if they have not uploaded one."""
    try:
        return storage.read_master(prefix)
    except ClientError as error:
        if storage.is_missing_object(error):
            return None
        logger.exception("could not read master workbook")
        return None
    except ValueError:
        logger.exception("master workbook is not readable")
        return None


def _map_points(frame: pd.DataFrame | None) -> list[dict[str, Any]]:
    """Shape parsed rows into JSON the map can render without inline HTML.

    Popup markup used to be built server-side and injected with ``innerHTML``,
    which let arbitrary spreadsheet text execute as script. The client now
    builds the popup from these plain values instead.
    """
    if frame is None or ADDRESS_COLUMN not in frame.columns:
        return []

    points: list[dict[str, Any]] = []
    for _, row in frame.iterrows():
        address = str(row[ADDRESS_COLUMN]).strip()
        if not address or address.lower() in {"nan", "n/a"}:
            continue
        points.append(
            {
                "address": address,
                "rent": _numeric(row.get(RENT_COLUMN)),
                "fields": [
                    [str(column), str(value)]
                    for column, value in row.items()
                    if not pd.isna(value) and str(value).strip()
                ],
            }
        )
    return points


def _numeric(value: Any) -> float | None:
    """Best-effort conversion of a spreadsheet cell to a float."""
    if value is None or pd.isna(value):
        return None
    try:
        return float(str(value).replace("$", "").replace(",", ""))
    except ValueError:
        return None
