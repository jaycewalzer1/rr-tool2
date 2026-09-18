"""Shared fixtures.

The suite runs entirely offline: ``FLASK_ENV=testing`` makes ``load_config``
substitute dummy secrets, and any test that needs AWS or Stripe patches the
relevant module rather than reaching the network.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Any

import pytest

os.environ["FLASK_ENV"] = "testing"

from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from models import db


@pytest.fixture
def app(tmp_path: Any) -> Iterator[Flask]:
    application = create_app()
    application.config.update(
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{tmp_path / 'test.db'}",
        SESSION_TYPE="cachelib",
    )
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def logged_in_client(client: FlaskClient) -> FlaskClient:
    """A client whose session passes ``login_required``.

    ``verify_account`` still calls Cognito, so views behind it must additionally
    patch ``decorators.auth``.
    """
    with client.session_transaction() as session:
        session["auth"] = {
            "access_token": "access",
            "refresh_token": "refresh",
            "id_token": "id",
        }
        session["user"] = {
            "email": "tester@example.com",
            "username": "tester@example.com",
            "user_id": "cognito-sub-123",
        }
    return client


@pytest.fixture
def verified_account(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make ``verify_account`` succeed without contacting Cognito."""
    monkeypatch.setattr(
        "decorators.auth.user_attributes",
        lambda _token: {"sub": "cognito-sub-123", "email_verified": "true"},
    )
