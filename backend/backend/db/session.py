from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from backend.db.engine import get_engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, autoflush=False)


_session_factory = create_session_factory(get_engine())


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with _session_factory() as session:
        yield session
