import logging
from collections.abc import Callable, Mapping
from datetime import datetime
from typing import Any
from uuid import UUID

from backend.libs.db.crud import NoObjectFoundError
from backend.services.user.crud import UserCRUDProtocol
from backend.services.user.exceptions import (
    InvalidCredentialsError,
    UserNotConfirmedError,
)
from backend.services.user.models import User
from backend.services.user.schemas import Credentials, UserFilters, UserUpdateData

logger = logging.getLogger(__name__)

PasswordValidator = Callable[[str, str], tuple[bool, str | None]]
PasswordHasher = Callable[[str], str]
TokenCreator = Callable[[Mapping[str, Any]], str]

ACCESS_TOKEN_TYPE = "access"  # nosec
REFRESH_TOKEN_TYPE = "refresh"  # nosec


async def login(
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


def create_access_token(user_id: UUID, token_creator: TokenCreator) -> str:
    return token_creator({"sub": str(user_id), "type": ACCESS_TOKEN_TYPE})


def create_refresh_token(user_id: UUID, token_creator: TokenCreator) -> str:
    return token_creator({"sub": str(user_id), "type": REFRESH_TOKEN_TYPE})
