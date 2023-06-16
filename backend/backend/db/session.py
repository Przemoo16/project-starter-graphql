from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.engine import get_engine
from backend.libs.db.session import create_session_factory

_session_factory = create_session_factory(get_engine())


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with _session_factory() as session:
        yield session
