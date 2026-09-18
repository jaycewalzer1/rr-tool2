"""Blueprint registration for the application factory."""

from __future__ import annotations

from flask import Flask

from .auth_routes import auth_bp
from .billing_routes import billing_bp
from .dashboard_routes import dashboard_bp
from .marketing_routes import marketing_bp

__all__ = ["register_routes"]


def register_routes(app: Flask) -> None:
    """Attach every blueprint to ``app``."""
    app.register_blueprint(marketing_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(billing_bp)
