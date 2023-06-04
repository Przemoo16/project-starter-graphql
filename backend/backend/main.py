from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.api.graphql.api import get_router
from backend.db.engine import dispose_engine, get_engine


def get_local_app(engine: AsyncEngine, debug: bool = False) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
        yield
        await dispose_engine(engine)

    local_app = FastAPI(lifespan=lifespan, openapi_url=None)

    local_app.include_router(get_router(debug), prefix="/graphql")

    return local_app


def get_app() -> FastAPI:
    engine = get_engine()
    return get_local_app(engine)
