"""Regression tests for the security fixes this codebase depends on.

Each test here pins a specific vulnerability closed: forged Stripe webhooks,
S3 path traversal, cross-tenant file access, credentials leaking into the
session, and unauthenticated access to billing endpoints.
"""

from __future__ import annotations

import json
import time
from typing import Any

import pytest
import stripe
from flask import Flask
from flask.testing import FlaskClient
from wtforms import ValidationError

from cre.forms import validate_cognito_password
from cre.utils import safe_filename


class TestSafeFilename:
    @pytest.mark.parametrize(
        "attack",
        [
            "../../other-user/secret.pdf",
            "..\\..\\other-user\\secret.pdf",
            "/etc/passwd",
        ],
    )
    def test_strips_directory_traversal(self, attack: str):
        cleaned = safe_filename(attack)
        assert "/" not in cleaned
        assert "\\" not in cleaned
        assert not cleaned.startswith(".")

    def test_keeps_an_ordinary_filename_intact(self):
        assert safe_filename("Q3 Rent Roll.pdf") == "Q3_Rent_Roll.pdf"

    def test_caps_the_length(self):
        assert len(safe_filename("a" * 500)) <= 120


class TestPasswordValidation:
    @pytest.mark.parametrize(
        "password",
        ["Ab1!", "nouppercase1!", "NOLOWERCASE1!", "NoDigitsHere!", "NoSpecial123"],
    )
    def test_rejects_passwords_cognito_would_refuse(self, password: str):
        with pytest.raises(ValidationError):
            validate_cognito_password(None, _Field(password))

    def test_accepts_a_compliant_password(self):
        validate_cognito_password(None, _Field("Str0ng!Passw0rd"))


class TestStripeWebhook:
    """Without signature verification anyone could grant themselves a plan."""

    def test_rejects_an_unsigned_event(self, client: FlaskClient):
        response = client.post(
            "/webhook",
            data=json.dumps({"type": "customer.subscription.created", "data": {"object": {}}}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_rejects_a_forged_signature(self, client: FlaskClient):
        response = client.post(
            "/webhook",
            data=json.dumps({"type": "customer.subscription.created", "data": {"object": {}}}),
            content_type="application/json",
            headers={"Stripe-Signature": "t=1,v1=deadbeef"},
        )
        assert response.status_code == 400

    def test_accepts_a_correctly_signed_event(self, app: Flask, client: FlaskClient):
        secret = app.config["APP_CONFIG"].stripe.webhook_secret
        payload = json.dumps({"type": "ping", "data": {"object": {}}})
        timestamp = int(time.time())
        signature = stripe.WebhookSignature._compute_signature(f"{timestamp}.{payload}", secret)

        response = client.post(
            "/webhook",
            data=payload,
            content_type="application/json",
            headers={"Stripe-Signature": f"t={timestamp},v1={signature}"},
        )
        assert response.status_code == 200


class TestEndpointAuthentication:
    @pytest.mark.parametrize(
        ("method", "path"),
        [
            ("GET", "/dashboard"),
            ("GET", "/database"),
            ("GET", "/gmaps"),
            ("GET", "/api/s3/files"),
            ("POST", "/api/s3/upload-url"),
            ("DELETE", "/api/s3/files"),
            ("GET", "/subscription/status"),
            ("GET", "/subscription/payment-history"),
            ("GET", "/manage-membership"),
        ],
    )
    def test_anonymous_callers_are_redirected_to_login(
        self, client: FlaskClient, method: str, path: str
    ):
        response = client.open(path, method=method)
        assert response.status_code in (302, 401)
        assert "/login" in response.headers.get("Location", "")

    def test_checkout_requires_a_signup_in_progress(self, client: FlaskClient):
        # Checkout runs before the Cognito account exists, so it cannot require a
        # login; it must still refuse callers with no pending signup.
        response = client.post("/create-checkout-session")
        assert response.status_code == 400

    def test_no_debug_endpoint_exposes_the_session(self, app: Flask):
        paths = {str(rule) for rule in app.url_map.iter_rules()}
        assert not [path for path in paths if "debug" in path.lower()]


class TestTenantIsolation:
    def test_deleting_another_users_file_is_a_404(
        self,
        logged_in_client: FlaskClient,
        verified_account: None,
        monkeypatch: pytest.MonkeyPatch,
    ):
        deleted: list[str] = []
        monkeypatch.setattr("cre.storage.delete_pdf", deleted.append)

        response = logged_in_client.delete(
            "/api/s3/files", json={"s3_key": "uploads/someone-else/secret.pdf"}
        )

        assert response.status_code == 404
        assert deleted == []

    def test_upload_urls_are_scoped_to_the_callers_prefix(
        self,
        logged_in_client: FlaskClient,
        verified_account: None,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.setattr("cre.storage.presigned_upload_url", lambda key: f"https://s3/{key}")

        response = logged_in_client.post(
            "/api/s3/upload-url", json={"filename": "../../victim/roll.pdf"}
        )

        assert response.status_code == 200
        assert response.json["s3_key"].startswith("uploads/cognito-sub-123/")

    def test_non_pdf_uploads_are_rejected(
        self, logged_in_client: FlaskClient, verified_account: None
    ):
        response = logged_in_client.post("/api/s3/upload-url", json={"filename": "payload.exe"})
        assert response.status_code == 400


class TestSessionHygiene:
    def test_login_never_stores_the_password(
        self, client: FlaskClient, monkeypatch: pytest.MonkeyPatch
    ):
        tokens = {"access_token": "a", "refresh_token": "r", "id_token": "i"}
        monkeypatch.setattr("cre.auth.authenticate", lambda *_: tokens)
        monkeypatch.setattr(
            "cre.auth.user_attributes", lambda _: {"sub": "sub-1", "email_verified": "true"}
        )

        client.post("/login", data={"email": "tester@example.com", "password": "Str0ng!Passw0rd"})

        with client.session_transaction() as session:
            assert "Str0ng!Passw0rd" not in json.dumps(dict(session), default=str)
            assert "password" not in session.get("user", {})


class _Field:
    """Minimal stand-in for a WTForms field."""

    def __init__(self, data: Any) -> None:
        self.data = data
