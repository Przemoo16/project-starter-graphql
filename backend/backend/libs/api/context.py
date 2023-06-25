from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext
from strawberry.types import Info as BaseInfo


class Context(BaseContext):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session


Info = BaseInfo[Context, Any]
