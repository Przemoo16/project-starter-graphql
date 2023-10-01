import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.api.graphql.router import get_router as get_graphql_router
from backend.api.rest.router import get_router as get_rest_router
from backend.config.settings import get_settings
from backend.db import get_engine
from backend.libs.db.engine import dispose_async_engine

app_settings = get_settings().app

logging.basicConfig(
    format=(
        "%(threadName)s(%(thread)d): %(asctime)s - %(levelname)s - "
        "%(name)s:%(lineno)d - %(message)s"
    ),
    level=app_settings.logging_level,
)


def get_local_app(engine: AsyncEngine, debug: bool = False) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
        yield
        await dispose_async_engine(engine)

    local_app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)

    local_app.include_router(get_graphql_router(debug), prefix="/graphql")
    local_app.include_router(get_rest_router(), prefix="/rest")

    return local_app


def get_app() -> FastAPI:
    engine = get_engine()
    return get_local_app(engine, app_settings.dev_mode)
