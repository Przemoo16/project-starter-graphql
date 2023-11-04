from collections.abc import Awaitable, Callable
from functools import partial
from typing import Annotated

from fastapi import Depends, Request, WebSocket

from backend.api.deps import get_confirmed_user
from backend.db import get_db
from backend.libs.api.context import Context
from backend.libs.db.session import AsyncSession
from backend.services.user.context import async_token_reader
from backend.services.user.crud import UserCRUD
from backend.services.user.models import User

_UserFetcher = Callable[[Request | WebSocket | None], Awaitable[User]]


async def _get_user(db: Annotated[AsyncSession, Depends(get_db)]) -> _UserFetcher:
    return partial(
        get_confirmed_user,
        token_reader=async_token_reader,
        crud=UserCRUD(db=db),
    )


async def get_context(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_fetcher: Annotated[_UserFetcher, Depends(_get_user)],
) -> Context:
    return Context(db, user_fetcher)
