import logging
from copy import copy

from backend.libs.db.crud import NoObjectFoundError
from backend.services.user.crud import UserCRUDProtocol
from backend.services.user.exceptions import (
    UserAlreadyExistsError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.schemas import (
    UserCreateData,
    UserFilters,
    UserUpdateData,
)

logger = logging.getLogger(__name__)


async def create_user(data: UserCreateData, crud: UserCRUDProtocol) -> User:
    try:
        await crud.read_one(UserFilters(email=data.email))
    except NoObjectFoundError:
        return await crud.create_and_refresh(data)
        # TODO: Send email to confirm email here
    raise UserAlreadyExistsError


async def get_user(filters: UserFilters, crud: UserCRUDProtocol) -> User:
    try:
        return await crud.read_one(filters)
    except NoObjectFoundError as exc:
        raise UserNotFoundError from exc


async def get_confirmed_user(filters: UserFilters, crud: UserCRUDProtocol) -> User:
    try:
        user = await crud.read_one(filters)
    except NoObjectFoundError as exc:
        raise UserNotFoundError from exc
    if not user.confirmed_email:
        raise UserNotConfirmedError
    return user


async def update_user(user: User, data: UserUpdateData, crud: UserCRUDProtocol) -> User:
    if data.email and data.email != user.email:
        try:
            await crud.read_one(UserFilters(email=data.email))
        except NoObjectFoundError:
            data = copy(data)
            data.confirmed_email = False
            logger.info("Marked the user %r as unconfirmed", user.email)
            # TODO: Send email to confirm new email
        else:
            raise UserAlreadyExistsError
    return await crud.update_and_refresh(user, data)


async def delete_user(user: User, crud: UserCRUDProtocol) -> None:
    await crud.delete(user)
