import logging

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from backend.config.db import DBSettings
from backend.config.settings import get_settings

logger = logging.getLogger(__name__)


def create_engine(settings: DBSettings) -> AsyncEngine:
    logger.debug(
        "Creating a database engine with the connection string %r",
        settings.url.render_as_string(),
    )
    return create_async_engine(settings.url)


async def dispose_engine(engine: AsyncEngine) -> None:
    logger.debug("Disposing the database engine")
    await engine.dispose()


_engine = create_engine(get_settings().db)


def get_engine() -> AsyncEngine:
    return _engine
