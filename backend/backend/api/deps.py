from collections.abc import Callable, Mapping
from typing import Any, Protocol

from backend.libs.api.headers import BearerTokenNotFoundError
from backend.services.user.crud import UserCRUDProtocol
from backend.services.user.exceptions import (
    InvalidAccessTokenError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.operations.auth import get_confirmed_user_from_headers


class Request(Protocol):
    @property
    def headers(self) -> Mapping[str, str]:
        ...


class UnauthorizedError(Exception):
    pass


async def get_confirmed_user(
    request: Request | None,
    token_reader: Callable[[str], dict[str, Any]],
    crud: UserCRUDProtocol,
) -> User:
    if not request:
        msg = "Authentication token required"
        raise UnauthorizedError(msg)
    try:
        return await get_confirmed_user_from_headers(
            request.headers, token_reader, crud
        )
    except BearerTokenNotFoundError:
        msg = "Authentication token required"
    except (InvalidAccessTokenError, UserNotFoundError, UserNotConfirmedError):
        msg = "Invalid token"
    raise UnauthorizedError(msg)
