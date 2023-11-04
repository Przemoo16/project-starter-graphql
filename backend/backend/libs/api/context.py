from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import cached_property
from typing import Any

from fastapi import Request, WebSocket
from strawberry.fastapi import BaseContext
from strawberry.types import Info as BaseInfo

from backend.libs.db.session import AsyncSession
from backend.services.user.models import User


@dataclass
class Context(BaseContext):
    db: AsyncSession
    _user_fetcher: Callable[[Request | WebSocket | None], Awaitable[User]]

    @cached_property
    async def user(self) -> User:
        return await self._user_fetcher(self.request)


Info = BaseInfo[Context, Any]
