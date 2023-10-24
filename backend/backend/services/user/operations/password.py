import logging
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from gettext import gettext as _
from typing import Any, Protocol
from uuid import UUID

from pydantic import SecretStr

from backend.libs.db.crud import NoObjectFoundError
from backend.libs.email.message import HTMLMessage
from backend.libs.security.token import InvalidTokenError
from backend.services.user.crud import UserCRUDProtocol, UserFilters, UserUpdateData
from backend.services.user.exceptions import (
    InvalidPasswordError,
    InvalidResetPasswordTokenError,
    InvalidResetPasswordTokenFingerprintError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.schemas import PasswordChangeSchema, PasswordResetSchema

logger = logging.getLogger(__name__)

AsyncPasswordValidator = Callable[[str, str], Awaitable[tuple[bool, str | None]]]
PasswordHasher = Callable[[str], str]
AsyncPasswordHasher = Callable[[str], Awaitable[str]]
TokenCreator = Callable[[Mapping[str, Any]], str]
AsyncTokenReader = Callable[[str], Awaitable[dict[str, Any]]]


class TemplateLoader(Protocol):
    def __call__(self, name: str, **kwargs: Any) -> str:
        ...


RESET_PASSWORD_TOKEN_TYPE = "reset-password"  # nosec


@dataclass
class ResetPasswordTokenData:
    user_id: UUID
    user_password: str


@dataclass
class ResetPasswordEmailData:
    url_template: str
    template_loader: TemplateLoader
    email_sender: Callable[[HTMLMessage], None]


@dataclass
class PasswordManager:
    validator: AsyncPasswordValidator
    hasher: AsyncPasswordHasher


@dataclass
class ResetPasswordTokenPayload:
    user_id: UUID
    fingerprint: str


async def recover_password(
    email: str,
    crud: UserCRUDProtocol,
    success_callback: Callable[[User], None] = lambda _: None,
) -> None:
    try:
        user = await crud.read_one(UserFilters(email=email))
    except NoObjectFoundError:
        logger.info("User %r not found", email)
        return
    success_callback(user)


def send_reset_password_email(
    token_data: ResetPasswordTokenData,
    token_creator: TokenCreator,
    password_hasher: PasswordHasher,
    email_data: ResetPasswordEmailData,
) -> None:
    token = _create_reset_password_token(token_data, token_creator, password_hasher)
    link = _construct_link(token, email_data.url_template)
    _send_reset_password_email(
        link,
        email_data.template_loader,
        email_data.email_sender,
    )


def _create_reset_password_token(
    token_data: ResetPasswordTokenData,
    token_creator: TokenCreator,
    password_hasher: PasswordHasher,
) -> str:
    return token_creator(
        {
            "sub": str(token_data.user_id),
            "fingerprint": password_hasher(token_data.user_password),
            "type": RESET_PASSWORD_TOKEN_TYPE,
        }
    )


def _construct_link(token: str, url_template: str) -> str:
    return url_template.format(token=token)


def _send_reset_password_email(
    link: str,
    template_loader: TemplateLoader,
    email_sender: Callable[[HTMLMessage], None],
) -> None:
    subject = _("Reset password")
    html_message = template_loader("reset-password.html", link=link)
    plain_message = _("Click the link to reset your password: {link}").format(link=link)
    email_sender(
        HTMLMessage(
            subject=subject, html_message=html_message, plain_message=plain_message
        )
    )


async def reset_password(
    data: PasswordResetSchema,
    token_reader: AsyncTokenReader,
    password_manager: PasswordManager,
    crud: UserCRUDProtocol,
) -> None:
    payload = await _decode_reset_password_token(data.token, token_reader)
    user = await _get_user_by_id(payload.user_id, crud)
    await _validate_token_fingerprint(
        user.hashed_password, payload.fingerprint, password_manager.validator
    )
    await _set_password(user, data.password, password_manager.hasher, crud)


async def _decode_reset_password_token(
    token: str, token_reader: AsyncTokenReader
) -> ResetPasswordTokenPayload:
    try:
        data = await token_reader(token)
    except InvalidTokenError as exc:
        logger.info("The token is invalid")
        raise InvalidResetPasswordTokenError from exc
    if data["type"] != RESET_PASSWORD_TOKEN_TYPE:
        logger.info(
            "The token is not a reset password token, actual type: %r",
            data["type"],
        )
        raise InvalidResetPasswordTokenError
    return ResetPasswordTokenPayload(
        user_id=UUID(data["sub"]), fingerprint=data["fingerprint"]
    )


async def _get_user_by_id(user_id: UUID, crud: UserCRUDProtocol) -> User:
    try:
        return await crud.read_one(UserFilters(id=user_id))
    except NoObjectFoundError as exc:
        logger.info("User with id %r not found", user_id)
        raise UserNotFoundError from exc


async def _validate_token_fingerprint(
    hashed_password: str, fingerprint: str, password_validator: AsyncPasswordValidator
) -> None:
    is_valid, _ = await password_validator(hashed_password, fingerprint)
    if not is_valid:
        logger.info("The token has invalid fingerprint")
        raise InvalidResetPasswordTokenFingerprintError


async def _set_password(
    user: User,
    password: SecretStr,
    password_hasher: AsyncPasswordHasher,
    crud: UserCRUDProtocol,
) -> None:
    await crud.update(
        user,
        UserUpdateData(
            hashed_password=await password_hasher(password.get_secret_value())
        ),
    )


async def change_password(
    user: User,
    data: PasswordChangeSchema,
    password_manager: PasswordManager,
    crud: UserCRUDProtocol,
) -> None:
    await _validate_password(
        user,
        data.current_password,
        password_validator=password_manager.validator,
    )
    await _set_password(user, data.new_password, password_manager.hasher, crud)


async def _validate_password(
    user: User, password: SecretStr, password_validator: AsyncPasswordValidator
) -> None:
    is_valid, _ = await password_validator(
        password.get_secret_value(), user.hashed_password
    )
    if not is_valid:
        logger.info("Invalid password for the user %r", user.email)
        raise InvalidPasswordError
