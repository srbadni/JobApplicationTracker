from unittest.mock import AsyncMock

import pytest


@pytest.fixture(autouse=True)
def prevent_database_connections(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep API unit tests independent from a running PostgreSQL instance."""
    monkeypatch.setattr("main.create_db_and_tables", AsyncMock())
