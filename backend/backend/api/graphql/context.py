from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from strawberry.fastapi import BaseContext
from strawberry.types import Info as BaseInfo

from backend.db.session import get_session_factory


class Context(BaseContext):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__()
        self.session_factory = session_factory


Info = BaseInfo[Context, Any]


async def get_context(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_session_factory)
    ]
) -> Context:
    return Context(session_factory=session_factory)
