from collections.abc import Awaitable, Callable
from functools import cached_property
from typing import Any

from fastapi import Request, WebSocket
from strawberry.fastapi import BaseContext
from strawberry.types import Info as BaseInfo

from backend.libs.db.session import AsyncSession
from backend.services.user.models import User


class Context(BaseContext):
    def __init__(
        self,
        session: AsyncSession,
        user_fetcher: Callable[[Request | WebSocket | None], Awaitable[User]],
    ):
        super().__init__()
        self.session = session
        self._user_fetcher = user_fetcher

    @cached_property
    async def user(self) -> User:
        return await self._user_fetcher(self.request)


Info = BaseInfo[Context, Any]
