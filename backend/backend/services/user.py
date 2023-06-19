from collections.abc import Callable
from copy import copy
from dataclasses import InitVar, dataclass, field
from typing import Union

from backend.crud.base import CRUDProtocol
from backend.libs.db.crud import NoObjectFoundError
from backend.libs.security.password import hash_password
from backend.libs.types.scalars import UNSET, is_value_set
from backend.models.user import User


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InactiveUserError(Exception):
    pass


@dataclass
class UserCreateData:
    email: str
    password: InitVar[str]
    hash_password_algorithm: InitVar[Callable[[str], str]] = hash_password
    hashed_password: str = field(init=False, repr=False)

    def __post_init__(
        self, password: str, hash_password_algorithm: Callable[[str], str]
    ) -> None:
        self.hashed_password = hash_password_algorithm(password)


@dataclass
class UserUpdateData:
    email: Union[str, "UNSET"] = UNSET
    password: InitVar[Union[str, "UNSET"]] = UNSET
    hash_password_algorithm: InitVar[Callable[[str], str]] = hash_password
    hashed_password: Union[str, "UNSET"] = field(default=UNSET, init=False, repr=False)
    confirmed_email: Union[bool, "UNSET"] = UNSET

    def __post_init__(
        self,
        password: Union[str, "UNSET"],
        hash_password_algorithm: Callable[[str], str],
    ) -> None:
        if is_value_set(password):
            self.hashed_password = hash_password_algorithm(password)


@dataclass
class UserFilters:
    email: Union[str, "UNSET"] = UNSET


UserCRUDProtocol = CRUDProtocol[User, UserCreateData, UserUpdateData, UserFilters]


async def create_user(data: UserCreateData, crud: UserCRUDProtocol) -> User:
    try:
        await get_user(UserFilters(email=data.email), crud)
    except UserNotFoundError:
        return await crud.create_and_refresh(data)
    raise UserAlreadyExistsError


async def get_user(filters: UserFilters, crud: UserCRUDProtocol) -> User:
    try:
        return await crud.read_one(filters)
    except NoObjectFoundError as exc:
        raise UserNotFoundError from exc


async def get_active_user(filters: UserFilters, crud: UserCRUDProtocol) -> User:
    user = await get_user(filters, crud)
    if not user.is_active:
        raise InactiveUserError
    return user


async def update_user(user: User, data: UserUpdateData, crud: UserCRUDProtocol) -> User:
    if is_value_set(data.email) and data.email != user.email:
        try:
            await get_user(UserFilters(email=data.email), crud)
        except UserNotFoundError:
            data = copy(data)
            data.confirmed_email = False
        else:
            raise UserAlreadyExistsError
    return await crud.update_and_refresh(user, data)


async def delete_user(user: User, crud: UserCRUDProtocol) -> None:
    await crud.delete(user)
