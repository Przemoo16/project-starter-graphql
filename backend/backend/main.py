from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from importlib.metadata import distribution

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.db.engine import dispose_engine, get_engine


def get_local_app(engine: AsyncEngine) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
        yield
        await dispose_engine(engine)

    package_distribution = distribution("backend")
    app = FastAPI(
        title=package_distribution.metadata["Name"],
        version=package_distribution.version,
        description=package_distribution.metadata["Summary"],
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
    )
    return app


def get_app() -> FastAPI:
    engine = get_engine()
    return get_local_app(engine)
