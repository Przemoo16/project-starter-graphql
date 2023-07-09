import logging
from collections.abc import Callable
from copy import copy

from backend.libs.db.crud import NoObjectFoundError
from backend.services.user.crud import UserCRUDProtocol
from backend.services.user.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.schemas import UserCreateData, UserFilters, UserUpdateData

logger = logging.getLogger(__name__)


async def create_user(data: UserCreateData, crud: UserCRUDProtocol) -> User:
    try:
        await crud.read_one(UserFilters(email=data.email))
    except NoObjectFoundError:
        return await crud.create_and_refresh(data)
    logger.info("User %r already exists", data.email)
    raise UserAlreadyExistsError


async def get_user(filters: UserFilters, crud: UserCRUDProtocol) -> User:
    try:
        return await crud.read_one(filters)
    except NoObjectFoundError as exc:
        logger.info("User with filters %r not found", filters)
        raise UserNotFoundError from exc


async def update_user(
    user: User,
    data: UserUpdateData,
    crud: UserCRUDProtocol,
    email_update_callback: Callable[[User], None] = lambda _: None,
) -> User:
    email_updated = False
    if data.email and data.email != user.email:
        try:
            await crud.read_one(UserFilters(email=data.email))
        except NoObjectFoundError:
            data = copy(data)
            data.confirmed_email = False
            email_updated = True
            logger.info("Marked the user %r as unconfirmed", user.email)
        else:
            logger.info("User %r already exists", data.email)
            raise UserAlreadyExistsError
    updated_user = await crud.update_and_refresh(user, data)
    if email_updated:
        email_update_callback(updated_user)
        logger.info("Called the email update callback")
    return updated_user


async def delete_user(user: User, crud: UserCRUDProtocol) -> None:
    await crud.delete(user)
