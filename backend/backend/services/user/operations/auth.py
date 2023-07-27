import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from backend.libs.api.headers import read_bearer_token
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
    return await login_with_tokens(
        user, tokens_data.access_token_creator, tokens_data.refresh_token_creator, crud
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
        password_hasher(credentials.password.get_secret_value())
        logger.info("User %r not found", credentials.email)
        raise UserNotFoundError from exc
    is_valid, updated_password_hash = password_validator(
        credentials.password.get_secret_value(), user.hashed_password
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


async def login_with_tokens(
    user: User,
    access_token_creator: TokenCreator,
    refresh_token_creator: TokenCreator,
    crud: UserCRUDProtocol,
) -> tuple[str, str]:
    updated_user = await crud.update_and_refresh(
        user, UserUpdateData(last_login=datetime.utcnow())
    )
    return (
        create_access_token(updated_user.id, access_token_creator),
        create_refresh_token(updated_user.id, refresh_token_creator),
    )


def create_access_token(user_id: UUID, token_creator: TokenCreator) -> str:
    return token_creator({"sub": str(user_id), "type": ACCESS_TOKEN_TYPE})


def create_refresh_token(user_id: UUID, token_creator: TokenCreator) -> str:
    return token_creator({"sub": str(user_id), "type": REFRESH_TOKEN_TYPE})


async def get_confirmed_user_from_headers(
    headers: Mapping[Any, str], token_reader: TokenReader, crud: UserCRUDProtocol
) -> User:
    token = read_bearer_token(headers)
    payload = read_access_token(token, token_reader)
    return await get_confirmed_user_by_id(payload.user_id, crud)


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


async def get_confirmed_user_by_id(user_id: UUID, crud: UserCRUDProtocol) -> User:
    try:
        user = await crud.read_one(UserFilters(id=user_id))
    except NoObjectFoundError as exc:
        logger.info("User with id %r not found", user_id)
        raise UserNotFoundError from exc
    if not user.confirmed_email:
        logger.info("User %r not confirmed", user.email)
        raise UserNotConfirmedError
    return user


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
