"""Public marketing pages and the health check."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, Response, jsonify, render_template, send_from_directory

marketing_bp = Blueprint("marketing", __name__)


@marketing_bp.route("/")
def home() -> str:
    return render_template("home/index.html")


@marketing_bp.route("/platform")
def platform() -> str:
    return render_template("home/platform.html")


@marketing_bp.route("/solutions")
def solutions() -> str:
    return render_template("home/solutions.html")


@marketing_bp.route("/contact")
def contact() -> str:
    return render_template("home/contact.html")


@marketing_bp.route("/privacy")
def privacy() -> str:
    return render_template("home/privacy.html")


@marketing_bp.route("/terms")
def terms() -> str:
    return render_template("home/terms.html")


@marketing_bp.route("/healthz")
def healthz() -> Response:
    """Liveness probe for the load balancer and container orchestrator."""
    return jsonify(status="ok")


@marketing_bp.route("/favicon.ico")
def favicon() -> Response:
    return send_from_directory(
        Path(marketing_bp.root_path).parent / "static",
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )
