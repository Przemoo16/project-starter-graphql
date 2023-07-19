from collections.abc import Awaitable, Callable
from functools import partial
from typing import Annotated

from fastapi import Depends, Request, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_confirmed_user
from backend.config.settings import get_settings
from backend.db import get_session
from backend.libs.api.context import Context
from backend.libs.security.token import read_paseto_token_public_v4
from backend.services.user.crud import UserCRUD
from backend.services.user.models import User

UserFetcher = Callable[[Request | WebSocket | None], Awaitable[User]]

user_settings = get_settings().user


def get_user(session: Annotated[AsyncSession, Depends(get_session)]) -> UserFetcher:
    return partial(
        get_confirmed_user,
        token_reader=partial(
            read_paseto_token_public_v4, key=user_settings.auth_public_key
        ),
        crud=UserCRUD(model=User, session=session),
    )


async def get_context(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_fetcher: Annotated[UserFetcher, Depends(get_user)],
) -> Context:
    return Context(session, user_fetcher)
