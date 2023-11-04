import logging
from collections.abc import Callable
from dataclasses import dataclass
from gettext import gettext as _
from typing import Any
from uuid import UUID

from backend.libs.db.crud import NoObjectFoundError
from backend.libs.email.message import HTMLMessage
from backend.libs.security.token import InvalidTokenError
from backend.services.user.crud import UserFilters, UserUpdateData
from backend.services.user.exceptions import (
    InvalidEmailConfirmationTokenError,
    UserEmailAlreadyConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.operations.types import (
    AsyncTokenReader,
    TemplateLoader,
    TokenCreator,
    UserCRUDProtocol,
)

_logger = logging.getLogger(__name__)


_EMAIL_CONFIRMATION_TOKEN_TYPE = "email-confirmation"  # nosec


@dataclass
class ConfirmationTokenData:
    user_id: UUID
    user_email: str


@dataclass
class ConfirmationEmailData:
    url_template: str
    template_loader: TemplateLoader
    email_sender: Callable[[HTMLMessage], None]


@dataclass
class _ConfirmationTokenPayload:
    user_id: UUID
    user_email: str


def send_confirmation_email(
    token_data: ConfirmationTokenData,
    token_creator: TokenCreator,
    email_data: ConfirmationEmailData,
) -> None:
    token = _create_email_confirmation_token(token_data, token_creator)
    link = _construct_link(token, email_data.url_template)
    _send_confirmation_email(link, email_data.template_loader, email_data.email_sender)


def _create_email_confirmation_token(
    token_data: ConfirmationTokenData, token_creator: TokenCreator
) -> str:
    return token_creator(
        {
            "sub": str(token_data.user_id),
            "email": token_data.user_email,
            "type": _EMAIL_CONFIRMATION_TOKEN_TYPE,
        }
    )


def _construct_link(token: str, url_template: str) -> str:
    return url_template.format(token=token)


def _send_confirmation_email(
    link: str,
    template_loader: TemplateLoader,
    email_sender: Callable[[HTMLMessage], None],
) -> None:
    subject = _("Confirm email")
    html_message = template_loader("email-confirmation.html", link=link)
    plain_message = _("Click the link to confirm your email: {link}").format(link=link)
    message = HTMLMessage(
        subject=subject, html_message=html_message, plain_message=plain_message
    )
    email_sender(message)


async def confirm_email(
    token: str, token_reader: AsyncTokenReader, crud: UserCRUDProtocol
) -> None:
    payload = await _read_email_confirmation_token(token, token_reader)
    user = await _get_user_by_id_and_email(payload.user_id, payload.user_email, crud)
    _validate_user_email_is_not_already_confirmed(user)
    await _confirm_email(user, crud)


async def _read_email_confirmation_token(
    token: str, token_reader: AsyncTokenReader
) -> _ConfirmationTokenPayload:
    payload = await _read_token(token, token_reader)
    _validate_token_type(payload["type"])
    return _ConfirmationTokenPayload(
        user_id=UUID(payload["sub"]), user_email=payload["email"]
    )


async def _read_token(token: str, token_reader: AsyncTokenReader) -> dict[str, Any]:
    try:
        return await token_reader(token)
    except InvalidTokenError as exc:
        _logger.info("The token is invalid")
        raise InvalidEmailConfirmationTokenError from exc


def _validate_token_type(token_type: str) -> None:
    if token_type != _EMAIL_CONFIRMATION_TOKEN_TYPE:
        _logger.info(
            "The token is not an %r token, actual type: %r",
            _EMAIL_CONFIRMATION_TOKEN_TYPE,
            token_type,
        )
        raise InvalidEmailConfirmationTokenError


async def _get_user_by_id_and_email(
    user_id: UUID, user_email: str, crud: UserCRUDProtocol
) -> User:
    try:
        return await crud.read_one(UserFilters(id=user_id, email=user_email))
    except NoObjectFoundError as exc:
        _logger.info("User with id %r and email %r not found", user_id, user_email)
        raise UserNotFoundError from exc


def _validate_user_email_is_not_already_confirmed(user: User) -> None:
    if user.confirmed_email:
        _logger.info("User email %r already confirmed", user.email)
        raise UserEmailAlreadyConfirmedError


async def _confirm_email(user: User, crud: UserCRUDProtocol) -> None:
    await crud.update(user, UserUpdateData(confirmed_email=True))
