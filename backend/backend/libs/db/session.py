from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from backend.libs.db.engine import AsyncEngine

__all__ = ["AsyncSession"]

AsyncSessionMaker = async_sessionmaker[AsyncSession]


def create_async_session_factory(engine: AsyncEngine) -> AsyncSessionMaker:
    return async_sessionmaker(bind=engine, autoflush=False)
