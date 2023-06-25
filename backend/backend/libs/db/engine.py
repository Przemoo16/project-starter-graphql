import logging

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine as aio_create_async_engine

logger = logging.getLogger(__name__)


def create_async_engine(url: URL) -> AsyncEngine:
    logger.debug(
        "Creating an async database engine with the connection string %r",
        url.render_as_string(),
    )
    return aio_create_async_engine(url)


async def dispose_async_engine(engine: AsyncEngine) -> None:
    logger.debug("Disposing the async database engine")
    await engine.dispose()
