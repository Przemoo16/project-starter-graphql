from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext
from strawberry.types import Info as BaseInfo

from backend.db.session import get_session


class Context(BaseContext):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session


Info = BaseInfo[Context, Any]


async def get_context(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> Context:
    return Context(session=session)
