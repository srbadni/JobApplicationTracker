import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from db import database
from db.base import Base


def test_create_db_and_tables_uses_registered_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection = MagicMock()
    connection.run_sync = AsyncMock()
    transaction = AsyncMock()
    transaction.__aenter__.return_value = connection
    engine = MagicMock()
    engine.begin.return_value = transaction
    monkeypatch.setattr(database, "engine", engine)

    asyncio.run(database.create_db_and_tables())

    connection.run_sync.assert_awaited_once_with(Base.metadata.create_all)
    assert "companies" in Base.metadata.tables
