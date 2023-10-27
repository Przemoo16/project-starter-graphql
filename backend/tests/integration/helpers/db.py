from typing import TypeVar

from sqlalchemy.orm import DeclarativeBase

from tests.integration.conftest import AsyncSession

Obj = TypeVar("Obj", bound=DeclarativeBase)


async def save_to_db(db: AsyncSession, obj: Obj) -> Obj:
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj
