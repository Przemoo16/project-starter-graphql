from collections.abc import Mapping
from typing import Any, Protocol

from backend.services.user.exceptions import (
    InvalidAccessTokenError,
    MissingAccessTokenError,
    UserEmailNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.operations.auth import get_confirmed_user_from_headers
from backend.services.user.operations.types import AsyncTokenReader, UserCRUDProtocol


class _Request(Protocol):
    @property
    def headers(self) -> Mapping[Any, str]:
        ...


class UnauthorizedError(Exception):
    pass


async def get_confirmed_user(
    request: _Request | None, token_reader: AsyncTokenReader, crud: UserCRUDProtocol
) -> User:
    if not request:
        msg = "Authentication token required"
        raise UnauthorizedError(msg)
    try:
        return await get_confirmed_user_from_headers(
            request.headers, token_reader, crud
        )
    except MissingAccessTokenError:
        msg = "Authentication token required"
    except (InvalidAccessTokenError, UserNotFoundError, UserEmailNotConfirmedError):
        msg = "Invalid token"
    raise UnauthorizedError(msg)
