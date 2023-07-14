import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from backend.libs.db.crud import NoObjectFoundError
from backend.libs.security.token import InvalidTokenError
from backend.services.user.crud import UserCRUDProtocol
from backend.services.user.exceptions import (
    InvalidAccessTokenError,
    InvalidPasswordError,
    InvalidRefreshTokenError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.schemas import Credentials, UserFilters, UserUpdateData

logger = logging.getLogger(__name__)

PasswordValidator = Callable[[str, str], tuple[bool, str | None]]
PasswordHasher = Callable[[str], str]
TokenCreator = Callable[[Mapping[str, Any]], str]
TokenReader = Callable[[str], dict[str, Any]]

ACCESS_TOKEN_TYPE = "access"  # nosec
REFRESH_TOKEN_TYPE = "refresh"  # nosec


@dataclass
class AuthData:
    credentials: Credentials
    password_validator: PasswordValidator
    password_hasher: PasswordHasher


@dataclass
class TokensCreationData:
    access_token_creator: TokenCreator
    refresh_token_creator: TokenCreator


@dataclass
class AccessTokenPayload:
    user_id: UUID


@dataclass
class RefreshTokenPayload:
    user_id: UUID


async def login(
    auth_data: AuthData, tokens_data: TokensCreationData, crud: UserCRUDProtocol
) -> tuple[str, str]:
    user = await authenticate(
        auth_data.credentials,
        auth_data.password_validator,
        auth_data.password_hasher,
        crud,
    )
    updated_user = await crud.update_and_refresh(
        user, UserUpdateData(last_login=datetime.utcnow())
    )
    return (
        create_access_token(updated_user.id, tokens_data.access_token_creator),
        create_refresh_token(updated_user.id, tokens_data.refresh_token_creator),
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
        raise UserNotFoundError from exc
    is_valid, updated_password_hash = password_validator(
        credentials.password, user.hashed_password
    )
    if not is_valid:
        logger.info("Invalid password for the user %r", user.email)
        raise InvalidPasswordError
    if not user.confirmed_email:
        logger.info("User %r not confirmed", user.email)
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


def read_access_token(token: str, token_reader: TokenReader) -> AccessTokenPayload:
    try:
        data = token_reader(token)
    except InvalidTokenError as exc:
        logger.info("The token is invalid")
        raise InvalidAccessTokenError from exc
    if data["type"] != ACCESS_TOKEN_TYPE:
        logger.info(
            "The token is not an access token, actual type: %r",
            data["type"],
        )
        raise InvalidAccessTokenError
    return AccessTokenPayload(user_id=UUID(data["sub"]))


def read_refresh_token(token: str, token_reader: TokenReader) -> RefreshTokenPayload:
    try:
        data = token_reader(token)
    except InvalidTokenError as exc:
        logger.info("The token is invalid")
        raise InvalidRefreshTokenError from exc
    if data["type"] != REFRESH_TOKEN_TYPE:
        logger.info(
            "The token is not a refresh token, actual type: %r",
            data["type"],
        )
        raise InvalidRefreshTokenError
    return RefreshTokenPayload(user_id=UUID(data["sub"]))
