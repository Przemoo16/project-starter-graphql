import logging

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from backend.config.settings import get_settings

logger = logging.getLogger(__name__)


def create_engine(url: URL) -> AsyncEngine:
    logger.debug(
        "Creating a database engine with the connection string %r",
        url.render_as_string(),
    )
    return create_async_engine(url)


async def dispose_engine(engine: AsyncEngine) -> None:
    logger.debug("Disposing the database engine")
    await engine.dispose()


_engine = create_engine(get_settings().db.url)


def get_engine() -> AsyncEngine:
    return _engine
