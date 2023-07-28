from typing import Any
from uuid import uuid4

from backend.libs.db.crud import NoObjectFoundError
from backend.services.user.crud import UserCreateData, UserFilters, UserUpdateData
from backend.services.user.models import User
from tests.unit.stubs.crud.base import CRUDStub


def create_user(**kwargs: Any) -> User:
    if "email" not in kwargs:
        kwargs["email"] = f"{uuid4()}@email.com"
    if "hashed_password" not in kwargs:
        kwargs["hashed_password"] = "hashed_password"
    return User(**kwargs)


def create_confirmed_user(**kwargs: Any) -> User:
    kwargs["confirmed_email"] = True
    return create_user(**kwargs)


class UserCRUD(  # pylint: disable=abstract-method
    CRUDStub[User, UserCreateData, UserUpdateData, UserFilters]
):
    def __init__(self, existing_user: User | None = None):
        self.existing_user = existing_user

    async def create_and_refresh(self, data: UserCreateData) -> User:
        return create_user(**data.model_dump())

    async def read_one(self, filters: UserFilters) -> User:
        if not self.existing_user:
            raise NoObjectFoundError
        filters_dict = filters.model_dump(exclude_unset=True)
        if all(
            getattr(self.existing_user, field) == value
            for field, value in filters_dict.items()
        ):
            return self.existing_user
        raise NoObjectFoundError

    async def update_and_refresh(self, obj: User, data: UserUpdateData) -> User:
        data_dict = data.model_dump(exclude_unset=True)
        for field, value in data_dict.items():
            setattr(obj, field, value)
        return obj

    async def delete(self, obj: User) -> None:
        pass
