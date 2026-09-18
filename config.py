"""Centralised, validated application configuration.

All environment access happens here so the rest of the codebase never calls
``os.getenv`` directly. Configuration is resolved once at start-up and any
missing production secret fails fast with a clear error instead of silently
falling back to an insecure default.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Literal

Environment = Literal["development", "testing", "production"]


class ConfigError(RuntimeError):
    """Raised when the environment is missing configuration the app requires."""


def _require(name: str, _unused_default: str = "") -> str:
    """Return an environment variable, raising :class:`ConfigError` if unset."""
    value = os.getenv(name)
    if not value:
        raise ConfigError(
            f"Missing required environment variable: {name}. "
            "Copy .env.example to .env and fill it in, or set it in your deployment."
        )
    return value


def _optional(name: str, default: str = "") -> str:
    """Return an environment variable, falling back to ``default`` if unset."""
    return os.getenv(name) or default


@dataclass(frozen=True)
class CognitoConfig:
    """AWS Cognito user-pool credentials used for authentication."""

    region: str
    user_pool_id: str
    app_client_id: str
    app_client_secret: str


@dataclass(frozen=True)
class StorageConfig:
    """S3 buckets backing uploaded PDFs and generated workbooks."""

    pdf_bucket: str
    excel_bucket: str
    presigned_url_ttl_seconds: int = 3600


@dataclass(frozen=True)
class StripeConfig:
    """Stripe keys for checkout and webhook signature verification."""

    public_key: str
    secret_key: str
    webhook_secret: str
    price_id_basic: str


@dataclass(frozen=True)
class Config:
    """Fully-resolved application configuration."""

    env: Environment
    secret_key: str
    database_uri: str
    base_url: str
    google_maps_api_key: str
    cognito: CognitoConfig
    storage: StorageConfig
    stripe: StripeConfig
    log_level: str = "INFO"
    session_lifetime: timedelta = field(default=timedelta(days=7))
    max_upload_bytes: int = 50 * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def is_testing(self) -> bool:
        return self.env == "testing"


def load_config() -> Config:
    """Build a :class:`Config` from the process environment.

    In ``testing`` mode every secret falls back to an obvious dummy value so the
    test suite runs without credentials. In every other mode missing secrets
    raise :class:`ConfigError` at start-up rather than failing at request time.
    """
    env: Environment = _optional("FLASK_ENV", "production")  # type: ignore[assignment]
    if env not in ("development", "testing", "production"):
        raise ConfigError(f"FLASK_ENV must be development, testing or production (got {env!r})")

    getter = _optional if env == "testing" else _require
    placeholder = "test-value" if env == "testing" else ""

    return Config(
        env=env,
        secret_key=getter("SECRET_KEY", placeholder),
        database_uri=_optional("DATABASE_URL", "sqlite:///app.db"),
        base_url=_optional("APP_BASE_URL", "http://localhost:5000").rstrip("/"),
        google_maps_api_key=_optional("GOOGLE_MAPS_API_KEY"),
        cognito=CognitoConfig(
            region=getter("AWS_REGION", placeholder),
            user_pool_id=getter("COGNITO_USER_POOL_ID", placeholder),
            app_client_id=getter("COGNITO_APP_CLIENT_ID", placeholder),
            app_client_secret=getter("COGNITO_APP_CLIENT_SECRET", placeholder),
        ),
        storage=StorageConfig(
            pdf_bucket=getter("S3_BUCKET_NAME_PDF", placeholder),
            excel_bucket=getter("S3_BUCKET_NAME_EXCEL", placeholder),
        ),
        stripe=StripeConfig(
            public_key=getter("STRIPE_PUBLIC_KEY", placeholder),
            secret_key=getter("STRIPE_SECRET_KEY", placeholder),
            webhook_secret=getter("STRIPE_WEBHOOK_SECRET", placeholder),
            price_id_basic=_optional("STRIPE_PRICE_ID_BASIC"),
        ),
        log_level=_optional("LOG_LEVEL", "DEBUG" if env == "development" else "INFO"),
    )


def flask_settings(config: Config) -> dict[str, object]:
    """Translate a :class:`Config` into Flask's ``app.config`` mapping.

    Session cookies are ``Secure``/``SameSite=Lax`` in production and relaxed in
    development so the app is usable over plain HTTP on localhost.
    """
    return {
        "SECRET_KEY": config.secret_key,
        "SQLALCHEMY_DATABASE_URI": config.database_uri,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SESSION_TYPE": "filesystem",
        "SESSION_PERMANENT": True,
        "PERMANENT_SESSION_LIFETIME": config.session_lifetime,
        "SESSION_COOKIE_SECURE": config.is_production,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "MAX_CONTENT_LENGTH": config.max_upload_bytes,
        "WTF_CSRF_ENABLED": not config.is_testing,
        "TESTING": config.is_testing,
        "GOOGLE_MAPS_API_KEY": config.google_maps_api_key,
        "APP_CONFIG": config,
    }
