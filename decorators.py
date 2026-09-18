"""View decorators enforcing authentication and account verification."""

from __future__ import annotations

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from botocore.exceptions import ClientError
from flask import flash, redirect, session, url_for

import auth

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

REQUIRED_TOKENS = ("access_token", "refresh_token", "id_token")
REQUIRED_USER_FIELDS = ("email", "username", "user_id")


def login_required(view: F) -> F:
    """Redirect to the login page unless a complete session is present."""

    @wraps(view)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not _session_is_complete():
            flash("Please log in to access this page.", "danger")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return cast(F, wrapper)


def verify_account(view: F) -> F:
    """Ensure the caller's Cognito email is verified, refreshing tokens if needed.

    Must be applied *below* :func:`login_required` so the session is known to be
    populated before Cognito is called.
    """

    @wraps(view)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        attributes = _attributes_with_refresh()
        if attributes is None:
            flash("Your session has expired. Please log in again.", "warning")
            return redirect(url_for("auth.login"))

        if attributes.get("email_verified") != "true":
            flash("Please verify your email address before proceeding.", "warning")
            return redirect(url_for("auth.confirm_signup"))

        return view(*args, **kwargs)

    return cast(F, wrapper)


def _session_is_complete() -> bool:
    tokens = session.get("auth") or {}
    user = session.get("user") or {}
    return all(key in tokens for key in REQUIRED_TOKENS) and all(
        user.get(field) for field in REQUIRED_USER_FIELDS
    )


def _attributes_with_refresh() -> dict[str, str] | None:
    """Read Cognito attributes, transparently refreshing an expired token."""
    try:
        return auth.user_attributes(session["auth"]["access_token"])
    except ClientError as error:
        if error.response["Error"]["Code"] != "NotAuthorizedException":
            logger.exception("cognito lookup failed")
            return None

    tokens = auth.refresh(session["user"]["username"], session["auth"]["refresh_token"])
    if tokens is None:
        return None

    session["auth"] = tokens
    try:
        return auth.user_attributes(tokens["access_token"])
    except ClientError:
        logger.exception("cognito lookup failed after refresh")
        return None
