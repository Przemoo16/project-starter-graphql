from sqlalchemy.ext.asyncio import AsyncEngine

from backend.config.settings import get_settings
from backend.libs.db.engine import create_engine

_engine = create_engine(get_settings().db.url)


def get_engine() -> AsyncEngine:
    return _engine
