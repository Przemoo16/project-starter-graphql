from collections.abc import Generator

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.config.settings import get_settings
from backend.db.engine import create_engine


@pytest.fixture(name="engine", scope="session")
def engine_fixture() -> Generator[AsyncEngine, None, None]:
    yield create_engine(get_settings().db.url)
