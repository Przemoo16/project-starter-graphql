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
    InvalidEmailConfirmationTokenError,
    UserEmailAlreadyConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User

logger = logging.getLogger(__name__)

TokenCreator = Callable[[Mapping[str, Any]], str]
TokenReader = Callable[[str], dict[str, Any]]


class TemplateLoader(Protocol):
    def __call__(self, name: str, **kwargs: Any) -> str:
        ...


EMAIL_CONFIRMATION_TOKEN_TYPE = "email-confirmation"  # nosec


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
class ConfirmationTokenPayload:
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
            "type": EMAIL_CONFIRMATION_TOKEN_TYPE,
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
    email_sender(
        HTMLMessage(
            subject=subject, html_message=html_message, plain_message=plain_message
        )
    )


async def confirm_email(
    token: str, token_reader: TokenReader, crud: UserCRUDProtocol
) -> None:
    payload = _decode_email_confirmation_token(token, token_reader)
    user = await _get_user_by_id_and_email(payload.user_id, payload.user_email, crud)
    _validate_user_email_is_not_already_confirmed(user)
    await _confirm_email(user, crud)


def _decode_email_confirmation_token(
    token: str, token_reader: TokenReader
) -> ConfirmationTokenPayload:
    try:
        data = token_reader(token)
    except InvalidTokenError as exc:
        logger.info("The token is invalid")
        raise InvalidEmailConfirmationTokenError from exc
    if data["type"] != EMAIL_CONFIRMATION_TOKEN_TYPE:
        logger.info(
            "The token is not an email confirmation token, actual type: %r",
            data["type"],
        )
        raise InvalidEmailConfirmationTokenError
    return ConfirmationTokenPayload(user_id=UUID(data["sub"]), user_email=data["email"])


async def _get_user_by_id_and_email(
    user_id: UUID, user_email: str, crud: UserCRUDProtocol
) -> User:
    try:
        return await crud.read_one(UserFilters(id=user_id, email=user_email))
    except NoObjectFoundError as exc:
        logger.info("User with id %r and email %r not found", user_id, user_email)
        raise UserNotFoundError from exc


def _validate_user_email_is_not_already_confirmed(user: User) -> None:
    if user.confirmed_email:
        logger.info("User email %r already confirmed", user.email)
        raise UserEmailAlreadyConfirmedError


async def _confirm_email(user: User, crud: UserCRUDProtocol) -> None:
    await crud.update(user, UserUpdateData(confirmed_email=True))
