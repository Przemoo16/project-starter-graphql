from collections.abc import Awaitable, Callable, Mapping
from typing import Any, Protocol

from backend.libs.db.crud import CRUDProtocol
from backend.services.user.crud import UserCreateData, UserFilters, UserUpdateData
from backend.services.user.models import User

UserCRUDProtocol = CRUDProtocol[User, UserCreateData, UserUpdateData, UserFilters]

TokenCreator = Callable[[Mapping[str, Any]], str]
AsyncTokenCreator = Callable[[Mapping[str, Any]], Awaitable[str]]
AsyncTokenReader = Callable[[str], Awaitable[dict[str, Any]]]

AsyncPasswordValidator = Callable[[str, str], Awaitable[tuple[bool, str | None]]]
PasswordHasher = Callable[[str], str]
AsyncPasswordHasher = Callable[[str], Awaitable[str]]


class TemplateLoader(Protocol):
    def __call__(self, name: str, **kwargs: Any) -> str:
        ...
