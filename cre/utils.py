"""Small helpers shared across request handlers."""

from __future__ import annotations

import re
from typing import Final

from flask import session

from cre.auth import AuthTokens

_UNSAFE_FILENAME = re.compile(r"[^A-Za-z0-9._-]+")
_MAX_FILENAME_LENGTH: Final = 120


def start_session(*, email: str, username: str, user_id: str, tokens: AuthTokens) -> None:
    """Replace the session with exactly the fields the app needs.

    Assigning whole dictionaries (rather than mutating them) guarantees no stale
    keys — notably plaintext passwords from the signup flow — survive login.
    """
    session.clear()
    session["auth"] = dict(tokens)
    session["user"] = {"email": email, "username": username, "user_id": user_id}
    session.permanent = True


def user_prefix() -> str:
    """Return the per-user S3 key prefix derived from the session username."""
    username = (session.get("user") or {}).get("username") or ""
    return safe_filename(username.split("@")[0]) or "default"


def safe_filename(name: str) -> str:
    """Reduce a user-supplied name to characters that are safe in an S3 key.

    Strips any directory components and disallowed characters so a value such as
    ``../../other-user/secret.pdf`` cannot escape the caller's own prefix.
    """
    stem = name.replace("\\", "/").split("/")[-1].strip()
    cleaned = _UNSAFE_FILENAME.sub("_", stem).lstrip(".")
    return cleaned[:_MAX_FILENAME_LENGTH]
