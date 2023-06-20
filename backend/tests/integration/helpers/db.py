from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

Obj = TypeVar("Obj", bound=DeclarativeBase)


async def save_to_db(session: AsyncSession, obj: Obj) -> Obj:
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj
