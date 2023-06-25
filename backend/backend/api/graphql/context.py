from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db import get_session
from backend.libs.api.context import Context


async def get_context(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> Context:
    return Context(session=session)
