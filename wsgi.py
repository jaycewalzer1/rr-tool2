"""WSGI entrypoint used by gunicorn (``gunicorn wsgi:app``)."""

from cre.app import create_app

app = create_app()
