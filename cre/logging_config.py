"""Application-wide logging configuration.

Logs are emitted as JSON to stdout so they can be shipped straight to
CloudWatch/Datadog from the container, and a ``request_id`` is attached to every
record so a single user action can be traced across modules.
"""

from __future__ import annotations

import json
import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Any

_request_id: ContextVar[str] = ContextVar("request_id", default="-")

_RESERVED = frozenset(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {
    "asctime",
    "message",
    "taskName",
}


def new_request_id() -> str:
    """Generate and bind a fresh request id for the current context."""
    request_id = uuid.uuid4().hex[:12]
    _request_id.set(request_id)
    return request_id


def current_request_id() -> str:
    """Return the request id bound to the current context, or ``-``."""
    return _request_id.get()


class JsonFormatter(logging.Formatter):
    """Render log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": current_request_id(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        # Surface anything passed via logger.info("...", extra={...}).
        payload.update(
            {key: value for key, value in record.__dict__.items() if key not in _RESERVED}
        )
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO", *, json_output: bool = True) -> None:
    """Install a single stdout handler on the root logger.

    Args:
        level: Minimum level to emit, e.g. ``"DEBUG"``.
        json_output: Emit JSON when ``True``, human-readable text otherwise.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        JsonFormatter()
        if json_output
        else logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s")
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())

    # botocore/urllib3 are extremely chatty at DEBUG and leak request metadata.
    for noisy in ("botocore", "boto3", "urllib3", "s3transfer"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
