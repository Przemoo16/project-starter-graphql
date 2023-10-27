from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from backend.config.settings import get_settings
from backend.db import get_session
from backend.libs.db.engine import (
    AsyncEngine,
    create_async_engine,
    dispose_async_engine,
)
from backend.libs.db.session import (
    AsyncSession,
    AsyncSessionMaker,
    create_async_session_factory,
)
from backend.main import get_local_app
from backend.models import Base

__all__ = ["AsyncEngine", "AsyncSession", "Base"]

_settings = get_settings()
db_settings = _settings.db
user_settings = _settings.user


@pytest.fixture(name="engine", scope="session")
async def engine_fixture() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(db_settings.url)
    yield engine
    await dispose_async_engine(engine)


@pytest.fixture(name="session_factory", scope="session")
async def session_factory_fixture(engine: AsyncEngine) -> AsyncSessionMaker:
    return create_async_session_factory(engine)


@pytest.fixture(name="_create_tables")
async def _create_tables_fixture(engine: AsyncEngine) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(name="session")
async def session_fixture(
    session_factory: AsyncSessionMaker, _create_tables: None
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


@pytest.fixture(name="app_instance", scope="session")
def app_instance_fixture(engine: AsyncEngine) -> FastAPI:
    return get_local_app(engine)


@pytest.fixture(name="app")
def app_fixture(
    app_instance: FastAPI, session: AsyncSession
) -> Generator[FastAPI, None, None]:
    async def get_test_session() -> AsyncSession:
        return session

    app_instance.dependency_overrides[get_session] = get_test_session
    yield app_instance
    app_instance.dependency_overrides.clear()


@pytest.fixture(name="async_client")
async def async_client_fixture(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(name="auth_private_key", scope="session")
def auth_private_key_fixture() -> bytes:
    return user_settings.auth_private_key


@pytest.fixture(name="graphql_url", scope="session")
def graphql_url_fixture() -> str:
    return "/api/graphql"


@pytest.fixture(name="rest_url", scope="session")
def rest_url_fixture() -> str:
    return "/api/rest"
