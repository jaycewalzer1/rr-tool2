"""AWS Cognito authentication helpers.

The boto3 client is created lazily so importing this module never requires
credentials — a prerequisite for running the test suite and for tooling such as
linters that import the package.
"""

from __future__ import annotations

import base64
import functools
import hashlib
import hmac
import logging
from typing import Any

import boto3
from botocore.exceptions import ClientError
from flask import current_app

from cre.config import Config

logger = logging.getLogger(__name__)

AuthTokens = dict[str, str]


def _config() -> Config:
    return current_app.config["APP_CONFIG"]


@functools.lru_cache(maxsize=4)
def _client(region: str) -> Any:
    return boto3.client("cognito-idp", region_name=region)


def cognito_client() -> Any:
    """Return a cached ``cognito-idp`` client for the configured region."""
    return _client(_config().cognito.region)


def secret_hash(username: str) -> str:
    """Compute the Cognito ``SECRET_HASH`` for an app client with a secret.

    Cognito requires ``Base64(HMAC-SHA256(client_secret, username + client_id))``
    on every call when the app client is configured with a secret.
    """
    cognito = _config().cognito
    digest = hmac.new(
        cognito.app_client_secret.encode("utf-8"),
        (username + cognito.app_client_id).encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode()


def client_id() -> str:
    """Return the configured Cognito app client id."""
    return _config().cognito.app_client_id


def authenticate(username: str, password: str) -> AuthTokens | None:
    """Exchange credentials for Cognito tokens.

    Args:
        username: The Cognito username (this app uses the user's email).
        password: The user's plaintext password, never persisted.

    Returns:
        A mapping with ``access_token``, ``id_token`` and ``refresh_token``, or
        ``None`` when the credentials are rejected.

    Raises:
        botocore.exceptions.ClientError: For any failure other than bad
            credentials (for example an unconfirmed account), so callers can
            react to the specific Cognito error code.
    """
    try:
        response = cognito_client().initiate_auth(
            ClientId=client_id(),
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
                "SECRET_HASH": secret_hash(username),
            },
        )
    except ClientError as error:
        if error.response["Error"]["Code"] == "NotAuthorizedException":
            logger.info("authentication rejected", extra={"username": username})
            return None
        raise

    return _tokens(response)


def refresh(username: str, refresh_token: str) -> AuthTokens | None:
    """Mint a new access token from a refresh token.

    Returns ``None`` when the refresh token has expired or been revoked.
    """
    try:
        response = cognito_client().initiate_auth(
            ClientId=client_id(),
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={
                "REFRESH_TOKEN": refresh_token,
                "SECRET_HASH": secret_hash(username),
            },
        )
    except ClientError as error:
        logger.info("token refresh failed", extra={"code": error.response["Error"]["Code"]})
        return None

    tokens = _tokens(response)
    # Cognito omits the refresh token on REFRESH_TOKEN_AUTH; keep the old one.
    tokens.setdefault("refresh_token", refresh_token)
    return tokens


def user_attributes(access_token: str) -> dict[str, str]:
    """Fetch the Cognito profile attributes for an access token."""
    response = cognito_client().get_user(AccessToken=access_token)
    return {attr["Name"]: attr["Value"] for attr in response["UserAttributes"]}


def sign_up(*, username: str, password: str, email: str, phone_number: str, name: str) -> str:
    """Register a new (unconfirmed) user and return their Cognito subject id."""
    response = cognito_client().sign_up(
        ClientId=client_id(),
        Username=username,
        Password=password,
        SecretHash=secret_hash(username),
        UserAttributes=[
            {"Name": "email", "Value": email},
            {"Name": "phone_number", "Value": phone_number},
            {"Name": "name", "Value": name},
            {"Name": "preferred_username", "Value": username},
        ],
    )
    return str(response["UserSub"])


def confirm_sign_up(username: str, confirmation_code: str) -> None:
    """Confirm a signup with the code Cognito emailed to the user."""
    cognito_client().confirm_sign_up(
        ClientId=client_id(),
        Username=username,
        ConfirmationCode=confirmation_code,
        SecretHash=secret_hash(username),
    )


def resend_confirmation_code(username: str) -> None:
    """Send a fresh signup confirmation code."""
    cognito_client().resend_confirmation_code(
        ClientId=client_id(), Username=username, SecretHash=secret_hash(username)
    )


def forgot_password(username: str) -> None:
    """Start the forgotten-password flow."""
    cognito_client().forgot_password(
        ClientId=client_id(), Username=username, SecretHash=secret_hash(username)
    )


def confirm_forgot_password(username: str, confirmation_code: str, password: str) -> None:
    """Complete the forgotten-password flow with a new password."""
    cognito_client().confirm_forgot_password(
        ClientId=client_id(),
        Username=username,
        ConfirmationCode=confirmation_code,
        Password=password,
        SecretHash=secret_hash(username),
    )


def error_code(error: ClientError) -> str:
    """Extract the Cognito error code from a botocore exception."""
    return str(error.response["Error"]["Code"])


def _tokens(response: dict[str, Any]) -> AuthTokens:
    result = response["AuthenticationResult"]
    tokens = {
        "access_token": result["AccessToken"],
        "id_token": result["IdToken"],
    }
    if "RefreshToken" in result:
        tokens["refresh_token"] = result["RefreshToken"]
    return tokens
