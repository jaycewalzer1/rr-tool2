"""Flask application factory for the CRE rent roll platform."""

from __future__ import annotations

import logging

import stripe
from dotenv import load_dotenv
from flask import Flask, g, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config, flask_settings, load_config
from flask_session import Session  # type: ignore[attr-defined]
from logging_config import configure_logging, new_request_id
from models import db
from routes import register_routes

logger = logging.getLogger(__name__)


def create_app(config: Config | None = None) -> Flask:
    """Build and configure the Flask application.

    Args:
        config: Pre-built configuration. When omitted it is loaded from the
            environment (after reading a local ``.env`` file if present).

    Returns:
        A fully wired Flask app with sessions, database, routes and logging.
    """
    load_dotenv()
    config = config or load_config()

    configure_logging(config.log_level, json_output=config.is_production)

    app = Flask(__name__)
    app.config.update(flask_settings(config))

    Session(app)
    db.init_app(app)
    stripe.api_key = config.stripe.secret_key

    # Terminating TLS at the load balancer means url_for(_external=True) needs
    # the forwarded scheme/host to build correct Stripe redirect URLs.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)  # type: ignore[method-assign]

    register_routes(app)
    _register_observability(app)
    _register_error_handlers(app)

    logger.info("application started", extra={"env": config.env})
    return app


def _register_observability(app: Flask) -> None:
    """Attach request correlation ids and access logging."""

    @app.before_request
    def _start_request() -> None:
        g.request_id = new_request_id()

    @app.after_request
    def _log_request(response):  # type: ignore[no-untyped-def]
        logger.info(
            "request completed",
            extra={
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
            },
        )
        response.headers["X-Request-ID"] = g.get("request_id", "-")
        return response


def _register_error_handlers(app: Flask) -> None:
    """Render friendly pages instead of leaking stack traces to users."""

    @app.errorhandler(404)
    def _not_found(_error):  # type: ignore[no-untyped-def]
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def _server_error(error):  # type: ignore[no-untyped-def]
        logger.exception("unhandled server error", exc_info=error)
        return render_template("404.html"), 500


if __name__ == "__main__":
    application = create_app()
    with application.app_context():
        db.create_all()
    application.run(
        host="127.0.0.1",
        port=5000,
        debug=application.config["APP_CONFIG"].env == "development",
    )
