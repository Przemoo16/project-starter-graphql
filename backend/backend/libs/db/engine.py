from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine as aio_create_async_engine

__all__ = ["AsyncEngine"]


def create_async_engine(url: URL) -> AsyncEngine:
    return aio_create_async_engine(url)


async def dispose_async_engine(engine: AsyncEngine) -> None:
    await engine.dispose()
