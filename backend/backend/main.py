import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.api.graphql.router import get_router
from backend.config.settings import get_settings
from backend.db import get_engine
from backend.libs.db.engine import dispose_async_engine

settings = get_settings()

logging.basicConfig(
    format=(
        "%(threadName)s(%(thread)d): %(asctime)s - %(levelname)s - "
        "%(name)s:%(lineno)d - %(message)s"
    ),
    level=settings.app.logging_level,
)


def get_local_app(engine: AsyncEngine, debug: bool = False) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
        yield
        await dispose_async_engine(engine)

    local_app = FastAPI(lifespan=lifespan, openapi_url=None)

    local_app.include_router(get_router(debug), prefix="/graphql")

    return local_app


def get_app() -> FastAPI:
    engine = get_engine()
    return get_local_app(engine, settings.app.dev_mode)
