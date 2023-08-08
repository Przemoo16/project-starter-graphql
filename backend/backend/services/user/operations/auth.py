import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import SecretStr

from backend.libs.api.headers import BearerTokenNotFoundError, read_bearer_token
from backend.libs.db.crud import NoObjectFoundError
from backend.libs.security.token import InvalidTokenError
from backend.services.user.crud import UserCRUDProtocol, UserFilters, UserUpdateData
from backend.services.user.exceptions import (
    InvalidAccessTokenError,
    InvalidPasswordError,
    InvalidRefreshTokenError,
    MissingAccessTokenError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.schemas import CredentialsSchema

logger = logging.getLogger(__name__)

PasswordValidator = Callable[[str, str], tuple[bool, str | None]]
PasswordHasher = Callable[[str], str]
TokenCreator = Callable[[Mapping[str, Any]], str]
TokenReader = Callable[[str], dict[str, Any]]

ACCESS_TOKEN_TYPE = "access"  # nosec
REFRESH_TOKEN_TYPE = "refresh"  # nosec


@dataclass
class PasswordManager:
    validator: PasswordValidator
    hasher: PasswordHasher


@dataclass
class AuthTokensManager:
    access_token_creator: TokenCreator
    refresh_token_creator: TokenCreator


@dataclass
class AccessTokenPayload:
    user_id: UUID


@dataclass
class RefreshTokenPayload:
    user_id: UUID


async def login(
    credentials: CredentialsSchema,
    password_manager: PasswordManager,
    tokens_manager: AuthTokensManager,
    crud: UserCRUDProtocol,
) -> tuple[str, str]:
    user = await _authenticate_user(credentials, password_manager, crud)
    _validate_user_is_confirmed(user)
    logged_user = await _login_user(user, crud)
    return _create_auth_tokens(logged_user.id, tokens_manager)


async def _authenticate_user(
    credentials: CredentialsSchema,
    password_manager: PasswordManager,
    crud: UserCRUDProtocol,
) -> User:
    user = await _get_user_by_credentials(credentials, password_manager.hasher, crud)
    if updated_password_hash := _validate_password(
        user, credentials.password, password_manager.validator
    ):
        user = await _update_password_hash(user, updated_password_hash, crud)
        logger.info("Updated password hash for the user %r", user.email)
    return user


async def _get_user_by_credentials(
    credentials: CredentialsSchema,
    password_hasher: PasswordHasher,
    crud: UserCRUDProtocol,
) -> User:
    try:
        return await crud.read_one(UserFilters(email=credentials.email))
    except NoObjectFoundError as exc:
        # Run the password hasher to mitigate timing attack
        password_hasher(credentials.password.get_secret_value())
        logger.info("User %r not found", credentials.email)
        raise UserNotFoundError from exc


def _validate_password(
    user: User, password: SecretStr, password_validator: PasswordValidator
) -> str | None:
    is_valid, updated_password_hash = password_validator(
        password.get_secret_value(), user.hashed_password
    )
    if not is_valid:
        logger.info("Invalid password for the user %r", user.email)
        raise InvalidPasswordError
    return updated_password_hash


async def _update_password_hash(
    user: User, password_hash: str, crud: UserCRUDProtocol
) -> User:
    return await crud.update_and_refresh(
        user, UserUpdateData(hashed_password=password_hash)
    )


def _validate_user_is_confirmed(user: User) -> None:
    if not user.confirmed_email:
        logger.info("User %r not confirmed", user.email)
        raise UserNotConfirmedError


async def _login_user(user: User, crud: UserCRUDProtocol) -> User:
    return await crud.update_and_refresh(
        user, UserUpdateData(last_login=datetime.utcnow())
    )


def _create_auth_tokens(
    user_id: UUID, tokens_manager: AuthTokensManager
) -> tuple[str, str]:
    return (
        _create_access_token(user_id, tokens_manager.access_token_creator),
        _create_refresh_token(user_id, tokens_manager.refresh_token_creator),
    )


def _create_access_token(user_id: UUID, token_creator: TokenCreator) -> str:
    return token_creator({"sub": str(user_id), "type": ACCESS_TOKEN_TYPE})


def _create_refresh_token(user_id: UUID, token_creator: TokenCreator) -> str:
    return token_creator({"sub": str(user_id), "type": REFRESH_TOKEN_TYPE})


async def get_confirmed_user_from_headers(
    headers: Mapping[Any, str], token_reader: TokenReader, crud: UserCRUDProtocol
) -> User:
    token = _read_access_token_from_header(headers)
    payload = _decode_access_token(token, token_reader)
    user = await _get_user_by_id(payload.user_id, crud)
    _validate_user_is_confirmed(user)
    return user


def _read_access_token_from_header(headers: Mapping[Any, str]) -> str:
    try:
        return read_bearer_token(headers)
    except BearerTokenNotFoundError as exc:
        raise MissingAccessTokenError from exc


def _decode_access_token(token: str, token_reader: TokenReader) -> AccessTokenPayload:
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


async def _get_user_by_id(user_id: UUID, crud: UserCRUDProtocol) -> User:
    try:
        return await crud.read_one(UserFilters(id=user_id))
    except NoObjectFoundError as exc:
        logger.info("User with id %r not found", user_id)
        raise UserNotFoundError from exc


def refresh_token(
    token: str, token_reader: TokenReader, token_creator: TokenCreator
) -> str:
    payload = _decode_refresh_token(token, token_reader)
    return _create_access_token(payload.user_id, token_creator)


def _decode_refresh_token(token: str, token_reader: TokenReader) -> RefreshTokenPayload:
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
