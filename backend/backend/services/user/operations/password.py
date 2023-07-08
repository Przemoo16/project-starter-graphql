import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from gettext import gettext as _
from typing import Any, Protocol
from uuid import UUID

from backend.libs.db.crud import NoObjectFoundError
from backend.libs.email.message import HTMLMessage
from backend.libs.security.token import InvalidTokenError
from backend.services.user.crud import UserCRUDProtocol
from backend.services.user.exceptions import (
    InvalidResetPasswordTokenError,
)
from backend.services.user.models import User
from backend.services.user.schemas import (
    SetPasswordData,
    UserFilters,
    UserUpdateData,
)

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
    fingerprint: str


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
    url_template: str,
    token: str,
    template_loader: TemplateLoader,
    send_email_func: Callable[[HTMLMessage], None],
) -> None:
    link = url_template.format(token=token)
    subject = _("Reset password")
    html_message = template_loader("reset-password.html", link=link)
    plain_message = _("Click the link to reset your password: {link}").format(link=link)
    send_email_func(
        HTMLMessage(
            subject=subject, html_message=html_message, plain_message=plain_message
        )
    )


def read_reset_password_token(
    token: str, token_reader: TokenReader
) -> ResetPasswordTokenData:
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
    return ResetPasswordTokenData(
        user_id=UUID(data["sub"]), fingerprint=data["fingerprint"]
    )


async def set_password(
    data: SetPasswordData,
    token_reader: TokenReader,
    password_validator: PasswordValidator,
    crud: UserCRUDProtocol,
) -> User:
    token_data = read_reset_password_token(data.token, token_reader)
    try:
        user = await crud.read_one(UserFilters(id=token_data.user_id))
    except NoObjectFoundError as exc:
        logger.info("User with id %r not found", token_data.user_id)
        raise InvalidResetPasswordTokenError from exc
    is_valid, _ = password_validator(user.hashed_password, token_data.fingerprint)
    if not is_valid:
        logger.info("The token has invalid fingerprint")
        raise InvalidResetPasswordTokenError
    if not user.confirmed_email:
        logger.info("User %r not confirmed", user.email)
        raise InvalidResetPasswordTokenError
    return await crud.update_and_refresh(
        user, UserUpdateData(hashed_password=data.hashed_password)
    )
