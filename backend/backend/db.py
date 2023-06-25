from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from backend.config.settings import get_settings
from backend.libs.db.engine import create_async_engine
from backend.libs.db.session import create_async_session_factory

_engine = create_async_engine(get_settings().db.url)


def get_engine() -> AsyncEngine:
    return _engine


_session_factory = create_async_session_factory(get_engine())


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with _session_factory() as session:
        yield session
