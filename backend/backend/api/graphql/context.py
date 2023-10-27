from collections.abc import Awaitable, Callable
from functools import partial
from typing import Annotated

from fastapi import Depends, Request, WebSocket

from backend.api.deps import get_confirmed_user
from backend.config.settings import get_settings
from backend.db import get_db
from backend.libs.api.context import Context
from backend.libs.db.session import AsyncSession
from backend.services.user.context import ASYNC_TOKEN_READER
from backend.services.user.crud import UserCRUD
from backend.services.user.models import User

UserFetcher = Callable[[Request | WebSocket | None], Awaitable[User]]

user_settings = get_settings().user


async def get_user(db: Annotated[AsyncSession, Depends(get_db)]) -> UserFetcher:
    return partial(
        get_confirmed_user,
        token_reader=ASYNC_TOKEN_READER,
        crud=UserCRUD(db=db),
    )


async def get_context(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_fetcher: Annotated[UserFetcher, Depends(get_user)],
) -> Context:
    return Context(db, user_fetcher)
