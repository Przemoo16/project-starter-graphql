import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from gettext import gettext as _
from typing import Any, Protocol
from uuid import UUID

from backend.libs.db.crud import NoObjectFoundError
from backend.libs.email.message import HTMLMessage
from backend.libs.security.token import InvalidTokenError
from backend.services.user.crud import UserCRUDProtocol, UserFilters, UserUpdateData
from backend.services.user.exceptions import (
    InvalidPasswordError,
    InvalidResetPasswordTokenError,
    InvalidResetPasswordTokenFingerprintError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.schemas import ChangePasswordData, ResetPasswordData

logger = logging.getLogger(__name__)

PasswordValidator = Callable[[str, str], tuple[bool, str | None]]
PasswordHasher = Callable[[str], str]
TokenCreator = Callable[[Mapping[str, Any]], str]
TokenReader = Callable[[str], dict[str, Any]]


class TemplateLoader(Protocol):
    def __call__(self, name: str, **kwargs: Any) -> str:
        ...


RESET_PASSWORD_TOKEN_TYPE = "reset-password"  # nosec


@dataclass
class ResetPasswordTokenData:
    user_id: UUID
    user_password: str
    password_hasher: PasswordHasher
    token_creator: TokenCreator


@dataclass
class ResetPasswordEmailData:
    url_template: str
    template_loader: TemplateLoader
    email_sender: Callable[[HTMLMessage], None]


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
    if not user.confirmed_email:
        logger.info("User %r not confirmed", user.email)
        return
    success_callback(user)


def send_reset_password_token(
    token_data: ResetPasswordTokenData, email_data: ResetPasswordEmailData
) -> None:
    token = create_reset_password_token(
        token_data.user_id,
        token_data.user_password,
        token_data.password_hasher,
        token_data.token_creator,
    )
    send_reset_password_email(
        token,
        email_data.url_template,
        email_data.template_loader,
        email_data.email_sender,
    )


def create_reset_password_token(
    user_id: UUID,
    user_password: str,
    password_hasher: PasswordHasher,
    token_creator: TokenCreator,
) -> str:
    return token_creator(
        {
            "sub": str(user_id),
            "fingerprint": password_hasher(user_password),
            "type": RESET_PASSWORD_TOKEN_TYPE,
        }
    )


def send_reset_password_email(
    token: str,
    url_template: str,
    template_loader: TemplateLoader,
    email_sender: Callable[[HTMLMessage], None],
) -> None:
    link = url_template.format(token=token)
    subject = _("Reset password")
    html_message = template_loader("reset-password.html", link=link)
    plain_message = _("Click the link to reset your password: {link}").format(link=link)
    email_sender(
        HTMLMessage(
            subject=subject, html_message=html_message, plain_message=plain_message
        )
    )


async def reset_password(
    data: ResetPasswordData,
    token_reader: TokenReader,
    password_validator: PasswordValidator,
    crud: UserCRUDProtocol,
) -> User:
    token_payload = read_reset_password_token(data.token, token_reader)
    return await set_password(
        token_payload.user_id,
        token_payload.fingerprint,
        data.hashed_password,
        password_validator,
        crud,
    )


def read_reset_password_token(
    token: str, token_reader: TokenReader
) -> ResetPasswordTokenPayload:
    try:
        data = token_reader(token)
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


async def set_password(
    user_id: UUID,
    fingerprint: str,
    hashed_password: str,
    password_validator: PasswordValidator,
    crud: UserCRUDProtocol,
) -> User:
    try:
        user = await crud.read_one(UserFilters(id=user_id))
    except NoObjectFoundError as exc:
        logger.info("User with id %r not found", user_id)
        raise UserNotFoundError from exc
    is_valid, _ = password_validator(user.hashed_password, fingerprint)
    if not is_valid:
        logger.info("The token has invalid fingerprint")
        raise InvalidResetPasswordTokenFingerprintError
    if not user.confirmed_email:
        logger.info("User %r not confirmed", user.email)
        raise UserNotConfirmedError
    return await crud.update_and_refresh(
        user, UserUpdateData(hashed_password=hashed_password)
    )


async def change_password(
    user: User,
    data: ChangePasswordData,
    password_validator: PasswordValidator,
    crud: UserCRUDProtocol,
) -> User:
    is_valid, _ = password_validator(
        data.current_password.get_secret_value(), user.hashed_password
    )
    if not is_valid:
        logger.info("Invalid password for the user %r", user.email)
        raise InvalidPasswordError()
    return await crud.update_and_refresh(
        user, UserUpdateData(hashed_password=data.hashed_password)
    )
