from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.db.engine import get_engine

_session_factory = async_sessionmaker(bind=get_engine(), expire_on_commit=False)


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return _session_factory
