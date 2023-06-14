from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from backend.config.settings import get_settings
from backend.db.engine import create_engine, dispose_engine
from backend.db.session import create_session_factory
from backend.main import get_local_app
from backend.models.base import Base


@pytest.fixture(name="engine", scope="session")
async def engine_fixture() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_engine(get_settings().db.url)
    yield engine
    await dispose_engine(engine)


@pytest.fixture(name="session_factory", scope="session")
async def session_factory_fixture(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(engine)


@pytest.fixture(name="_create_tables")
async def _create_tables_fixture(engine: AsyncEngine) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(name="session")
async def session_fixture(
    session_factory: async_sessionmaker[AsyncSession], _create_tables: None
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


@pytest.fixture(name="app_instance", scope="session")
def app_instance_fixture(engine: AsyncEngine) -> FastAPI:
    return get_local_app(engine)


@pytest.fixture(name="app")
def app_fixture(app_instance: FastAPI) -> Generator[FastAPI, None, None]:
    yield app_instance
    app_instance.dependency_overrides.clear()


@pytest.fixture(name="async_client")
async def async_client_fixture(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
