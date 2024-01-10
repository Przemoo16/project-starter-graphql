import logging
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from backend.libs.api.headers import BearerTokenNotFoundError, read_bearer_token
from backend.libs.db.crud import NoObjectFoundError
from backend.libs.security.token import InvalidTokenError
from backend.services.user.crud import UserFilters, UserUpdateData
from backend.services.user.exceptions import (
    InvalidAccessTokenError,
    InvalidPasswordError,
    InvalidRefreshTokenError,
    MissingAccessTokenError,
    UserEmailNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.operations.types import (
    AsyncPasswordHasher,
    AsyncPasswordValidator,
    AsyncTokenCreator,
    AsyncTokenReader,
    UserCRUDProtocol,
)
from backend.services.user.schemas import CredentialsSchema

_logger = logging.getLogger(__name__)


_ACCESS_TOKEN_TYPE = "access"  # nosec B105
_REFRESH_TOKEN_TYPE = "refresh"  # nosec B105


@dataclass
class PasswordManager:
    validator: AsyncPasswordValidator
    hasher: AsyncPasswordHasher


@dataclass
class AuthTokensManager:
    access_token_creator: AsyncTokenCreator
    refresh_token_creator: AsyncTokenCreator


@dataclass
class _AccessTokenPayload:
    user_id: UUID


@dataclass
class _RefreshTokenPayload:
    user_id: UUID


async def login(
    credentials: CredentialsSchema,
    password_manager: PasswordManager,
    tokens_manager: AuthTokensManager,
    crud: UserCRUDProtocol,
) -> tuple[str, str]:
    user = await _get_authenticated_user(credentials, password_manager, crud)
    _validate_user_email_is_confirmed(user)
    await _login_user(user, crud)
    return await _create_auth_tokens(user.id, tokens_manager)


async def _get_authenticated_user(
    credentials: CredentialsSchema,
    password_manager: PasswordManager,
    crud: UserCRUDProtocol,
) -> User:
    user = await _get_user_by_credentials(credentials, password_manager.hasher, crud)
    if updated_password_hash := await _validate_password(
        user, credentials.password, password_manager.validator
    ):
        await _update_password_hash(user, updated_password_hash, crud)
        _logger.info("Updated password hash for the user %r", user.email)
    return user


async def _get_user_by_credentials(
    credentials: CredentialsSchema,
    password_hasher: AsyncPasswordHasher,
    crud: UserCRUDProtocol,
) -> User:
    try:
        return await crud.read_one(UserFilters(email=credentials.email))
    except NoObjectFoundError as exc:
        # Run the password hasher to mitigate timing attack
        await password_hasher(credentials.password)
        _logger.info("User %r not found", credentials.email)
        raise UserNotFoundError from exc


async def _validate_password(
    user: User, password: str, password_validator: AsyncPasswordValidator
) -> str | None:
    is_valid, updated_password_hash = await password_validator(
        password, user.hashed_password
    )
    if not is_valid:
        _logger.info("Invalid password for the user %r", user.email)
        raise InvalidPasswordError
    return updated_password_hash


async def _update_password_hash(
    user: User, password_hash: str, crud: UserCRUDProtocol
) -> None:
    await crud.update_and_refresh(user, UserUpdateData(hashed_password=password_hash))


def _validate_user_email_is_confirmed(user: User) -> None:
    if not user.confirmed_email:
        _logger.info("User email %r not confirmed", user.email)
        raise UserEmailNotConfirmedError


async def _login_user(user: User, crud: UserCRUDProtocol) -> None:
    await crud.update_and_refresh(user, UserUpdateData(last_login=datetime.now(UTC)))


async def _create_auth_tokens(
    user_id: UUID, tokens_manager: AuthTokensManager
) -> tuple[str, str]:
    return (
        await _create_access_token(user_id, tokens_manager.access_token_creator),
        await _create_refresh_token(user_id, tokens_manager.refresh_token_creator),
    )


async def _create_access_token(user_id: UUID, token_creator: AsyncTokenCreator) -> str:
    return await token_creator({"sub": str(user_id), "type": _ACCESS_TOKEN_TYPE})


async def _create_refresh_token(user_id: UUID, token_creator: AsyncTokenCreator) -> str:
    return await token_creator({"sub": str(user_id), "type": _REFRESH_TOKEN_TYPE})


async def get_confirmed_user_from_headers(
    headers: Mapping[Any, str], token_reader: AsyncTokenReader, crud: UserCRUDProtocol
) -> User:
    token = _read_access_token_from_header(headers)
    payload = await _read_access_token(token, token_reader)
    user = await _get_user_by_id(payload.user_id, crud)
    _validate_user_email_is_confirmed(user)
    return user


def _read_access_token_from_header(headers: Mapping[Any, str]) -> str:
    try:
        return read_bearer_token(headers)
    except BearerTokenNotFoundError as exc:
        raise MissingAccessTokenError from exc


async def _read_access_token(
    token: str, token_reader: AsyncTokenReader
) -> _AccessTokenPayload:
    error = InvalidAccessTokenError
    payload = await _read_token(token, token_reader, error)
    _validate_token_type(payload["type"], _ACCESS_TOKEN_TYPE, error)
    return _AccessTokenPayload(user_id=UUID(payload["sub"]))


async def _read_token(
    token: str, token_reader: AsyncTokenReader, error: type[Exception]
) -> dict[str, Any]:
    try:
        return await token_reader(token)
    except InvalidTokenError as exc:
        _logger.info("The token is invalid")
        raise error from exc


def _validate_token_type(
    token_type: str, expected_type: str, error: type[Exception]
) -> None:
    if token_type != expected_type:
        _logger.info(
            "The token is not an %r token, actual type: %r", expected_type, token_type
        )
        raise error


async def _get_user_by_id(user_id: UUID, crud: UserCRUDProtocol) -> User:
    try:
        return await crud.read_one(UserFilters(id=user_id))
    except NoObjectFoundError as exc:
        _logger.info("User with id %r not found", user_id)
        raise UserNotFoundError from exc


async def refresh_token(
    token: str, token_reader: AsyncTokenReader, token_creator: AsyncTokenCreator
) -> str:
    payload = await _read_refresh_token(token, token_reader)
    return await _create_access_token(payload.user_id, token_creator)


async def _read_refresh_token(
    token: str, token_reader: AsyncTokenReader
) -> _RefreshTokenPayload:
    error = InvalidRefreshTokenError
    payload = await _read_token(token, token_reader, error)
    _validate_token_type(payload["type"], _REFRESH_TOKEN_TYPE, error)
    return _RefreshTokenPayload(user_id=UUID(payload["sub"]))
