from copy import copy

from backend.crud.base import CRUDProtocol
from backend.libs.db.crud import NoObjectFoundError
from backend.libs.security.password import hash_password
from backend.models.user import User
from backend.types.user import UserCreate, UserFilters, UserUpdate

UserCRUDProtocol = CRUDProtocol[User, UserCreate, UserUpdate, UserFilters]


class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InactiveUserError(Exception):
    pass


async def create_user(data: UserCreate, crud: UserCRUDProtocol) -> User:
    try:
        await get_user(UserFilters(email=data.email), crud)
    except UserNotFoundError:
        copied_data = copy(data)
        copied_data.password = hash_password(copied_data.password)
        return await crud.create_and_refresh(copied_data)
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


async def update_user(user: User, data: UserUpdate, crud: UserCRUDProtocol) -> User:
    copied_data = copy(data)
    if copied_data.email:
        try:
            await get_user(UserFilters(email=copied_data.email), crud)
        except UserNotFoundError:
            copied_data.confirmed_email = False
        else:
            raise UserAlreadyExistsError
    if copied_data.password:
        copied_data.password = hash_password(copied_data.password)
    return await crud.update_and_refresh(user, copied_data)


async def delete_user(user: User, crud: UserCRUDProtocol) -> None:
    await crud.delete(user)
