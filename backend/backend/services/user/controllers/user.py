import logging
from collections.abc import Callable
from copy import copy
from datetime import datetime

from backend.libs.db.crud import CRUDProtocol, NoObjectFoundError
from backend.services.user.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.schemas import (
    Credentials,
    UserCreateData,
    UserFilters,
    UserUpdateData,
)

logger = logging.getLogger(__name__)

UserCRUDProtocol = CRUDProtocol[User, UserCreateData, UserUpdateData, UserFilters]
PasswordValidator = Callable[[str, str], tuple[bool, str | None]]
PasswordHasher = Callable[[str], str]


async def create_user(data: UserCreateData, crud: UserCRUDProtocol) -> User:
    try:
        await crud.read_one(UserFilters(email=data.email))
    except NoObjectFoundError:
        return await crud.create_and_refresh(data)
    raise UserAlreadyExistsError


async def get_user(filters: UserFilters, crud: UserCRUDProtocol) -> User:
    try:
        return await crud.read_one(filters)
    except NoObjectFoundError as exc:
        raise UserNotFoundError from exc


async def update_user(user: User, data: UserUpdateData, crud: UserCRUDProtocol) -> User:
    if data.email and data.email != user.email:
        try:
            await crud.read_one(UserFilters(email=data.email))
        except NoObjectFoundError:
            data = copy(data)
            data.confirmed_email = False
            logger.info("Mark the user %r as unconfirmed email", user.email)
        else:
            raise UserAlreadyExistsError
    return await crud.update_and_refresh(user, data)


async def delete_user(user: User, crud: UserCRUDProtocol) -> None:
    await crud.delete(user)


async def login_user(
    credentials: Credentials,
    password_validator: PasswordValidator,
    password_hasher: PasswordHasher,
    crud: UserCRUDProtocol,
) -> User:
    user = await authenticate(credentials, password_validator, password_hasher, crud)
    return await crud.update_and_refresh(
        user, UserUpdateData(last_login=datetime.utcnow())
    )


async def authenticate(
    credentials: Credentials,
    password_validator: PasswordValidator,
    password_hasher: PasswordHasher,
    crud: UserCRUDProtocol,
) -> User:
    try:
        user = await crud.read_one(UserFilters(email=credentials.email))
    except NoObjectFoundError as exc:
        # Run the password hasher to mitigate timing attack
        password_hasher(credentials.password)
        logger.info("User %r not found", credentials.email)
        raise InvalidCredentialsError from exc
    is_valid, updated_password_hash = password_validator(
        credentials.password, user.hashed_password
    )
    if not is_valid:
        logger.info("Invalid password for the user %r", user.email)
        raise InvalidCredentialsError
    if not user.confirmed_email:
        raise UserNotConfirmedError
    if updated_password_hash:
        user = await crud.update_and_refresh(
            user, UserUpdateData(hashed_password=updated_password_hash)
        )
        logger.info("Updated password hash for the user %r", user.email)
    return user
