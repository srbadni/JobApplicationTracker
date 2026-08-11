"""ASGI entry point kept at the repository root for ``uvicorn main:app``."""

from app.main import app, create_app

__all__ = ["app", "create_app"]
