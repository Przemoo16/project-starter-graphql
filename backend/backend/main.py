from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from backend.api.graphql.router import get_router as get_graphql_router
from backend.api.rest.router import get_router as get_rest_router
from backend.config.settings import settings
from backend.db import engine
from backend.libs.db.engine import AsyncEngine, dispose_async_engine
from backend.logs import setup_logging

_app_settings = settings.app


def get_local_app(db_engine: AsyncEngine, debug: bool = False) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
        _logging_listener = setup_logging(_app_settings.logging_level)
        _logging_listener.start()
        yield
        await dispose_async_engine(db_engine)
        _logging_listener.stop()

    local_app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)

    local_app.include_router(get_graphql_router(debug), prefix="/api/graphql")
    local_app.include_router(get_rest_router(), prefix="/api/rest")

    return local_app


def get_app() -> FastAPI:
    return get_local_app(engine, _app_settings.dev_mode)
