from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from backend.config.settings import get_settings
from backend.db import get_db
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

__all__ = ["AsyncClient", "AsyncEngine", "AsyncSession", "Base"]

_settings = get_settings()
db_settings = _settings.db
user_settings = _settings.user


@pytest.fixture(name="db_engine", scope="session")
async def db_engine_fixture() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(db_settings.url)
    yield engine
    await dispose_async_engine(engine)


@pytest.fixture(name="session_factory", scope="session")
async def session_factory_fixture(db_engine: AsyncEngine) -> AsyncSessionMaker:
    return create_async_session_factory(db_engine)


@pytest.fixture(name="_create_tables")
async def _create_tables_fixture(db_engine: AsyncEngine) -> AsyncGenerator[None, None]:
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(name="db")
async def db_fixture(
    session_factory: AsyncSessionMaker, _create_tables: None
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


@pytest.fixture(name="app_instance", scope="session")
def app_instance_fixture(db_engine: AsyncEngine) -> FastAPI:
    return get_local_app(db_engine)


@pytest.fixture(name="app")
def app_fixture(
    app_instance: FastAPI, db: AsyncSession
) -> Generator[FastAPI, None, None]:
    async def get_test_db() -> AsyncSession:
        return db

    app_instance.dependency_overrides[get_db] = get_test_db
    yield app_instance
    app_instance.dependency_overrides.clear()


@pytest.fixture(name="client")
async def client_fixture(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
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
