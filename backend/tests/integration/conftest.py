from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.config.settings import get_settings
from backend.db.engine import create_engine
from backend.main import get_local_app


@pytest.fixture(name="engine", scope="session")
def engine_fixture() -> Generator[AsyncEngine, None, None]:
    yield create_engine(get_settings().db.url)


@pytest.fixture(name="app_instance", scope="session")
def app_instance_fixture(engine: AsyncEngine) -> Generator[FastAPI, None, None]:
    yield get_local_app(engine)


@pytest.fixture(name="app")
def app_fixture(app_instance: FastAPI) -> Generator[FastAPI, None, None]:
    yield app_instance
    app_instance.dependency_overrides.clear()


@pytest.fixture(name="async_client")
async def async_client_fixture(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
