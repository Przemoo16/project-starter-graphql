from dataclasses import asdict
from typing import Any

from backend.libs.db.crud import NoObjectFoundError, is_unset
from backend.services.user.crud import (
    UserCreateData,
    UserFilters,
    UserUpdateData,
)
from backend.services.user.models import User
from tests.unit.stubs.crud.base import CRUDStub


def create_confirmed_user(**kwargs: Any) -> User:
    kwargs["confirmed_email"] = True
    return create_user(**kwargs)


def create_user(**kwargs: Any) -> User:
    if "email" not in kwargs:
        kwargs["email"] = "test_helper_user@email.com"
    if "hashed_password" not in kwargs:
        kwargs["hashed_password"] = "test_helper_hashed_password"
    if "full_name" not in kwargs:
        kwargs["full_name"] = "Test Helper User"
    return User(**kwargs)


class UserCRUD(CRUDStub[User, UserCreateData, UserUpdateData, UserFilters]):
    def __init__(self, existing_user: User | None = None):
        self._existing_user = existing_user

    async def create_and_refresh(self, data: UserCreateData) -> User:
        return create_user(**asdict(data))

    async def read_one(self, filters: UserFilters) -> User:
        filters_dict = asdict(filters)
        if self._existing_user and all(
            getattr(self._existing_user, field) == value
            for field, value in filters_dict.items()
            if not is_unset(value)
        ):
            return self._existing_user
        raise NoObjectFoundError

    async def update(self, obj: User, data: UserUpdateData) -> None:
        self._update(obj, data)

    async def update_and_refresh(self, obj: User, data: UserUpdateData) -> None:
        self._update(obj, data)

    def _update(self, obj: User, data: UserUpdateData) -> User:
        data_dict = asdict(data)
        for field, value in data_dict.items():
            if is_unset(value):
                continue
            setattr(obj, field, value)
        return obj

    async def delete(self, obj: User) -> None:
        pass
