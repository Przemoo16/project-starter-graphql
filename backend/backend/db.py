from collections.abc import AsyncGenerator

from backend.config.settings import settings
from backend.libs.db.engine import create_async_engine
from backend.libs.db.session import AsyncSession, create_async_session_factory

engine = create_async_engine(settings.db.url)

_session_factory = create_async_session_factory(engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _session_factory() as session:
        yield session
