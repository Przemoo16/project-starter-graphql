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
    InvalidEmailConfirmationTokenError,
    UserAlreadyConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.schemas import UserFilters, UserUpdateData

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
    token_creator: TokenCreator


@dataclass
class ConfirmationEmailData:
    url_template: str
    template_loader: TemplateLoader
    email_sender: Callable[[HTMLMessage], None]


@dataclass
class ConfirmationTokenPayload:
    user_id: UUID
    user_email: str


def send_email_confirmation_token(
    token_data: ConfirmationTokenData, email_data: ConfirmationEmailData
) -> None:
    token = create_email_confirmation_token(
        token_data.user_id, token_data.user_email, token_data.token_creator
    )
    send_confirmation_email(
        token,
        email_data.url_template,
        email_data.template_loader,
        email_data.email_sender,
    )


def create_email_confirmation_token(
    user_id: UUID, user_email: str, token_creator: TokenCreator
) -> str:
    return token_creator(
        {
            "sub": str(user_id),
            "email": user_email,
            "type": EMAIL_CONFIRMATION_TOKEN_TYPE,
        }
    )


def send_confirmation_email(
    token: str,
    url_template: str,
    template_loader: TemplateLoader,
    email_sender: Callable[[HTMLMessage], None],
) -> None:
    link = url_template.format(token=token)
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
) -> User:
    token_payload = read_email_confirmation_token(token, token_reader)
    return await confirm_user(token_payload.user_id, token_payload.user_email, crud)


def read_email_confirmation_token(
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


async def confirm_user(user_id: UUID, user_email: str, crud: UserCRUDProtocol) -> User:
    try:
        user = await crud.read_one(UserFilters(id=user_id, email=user_email))
    except NoObjectFoundError as exc:
        logger.info("User with id %r and email %r not found", user_id, user_email)
        raise UserNotFoundError from exc
    if user.confirmed_email:
        logger.info("User %r already confirmed", user.email)
        raise UserAlreadyConfirmedError
    return await crud.update_and_refresh(user, UserUpdateData(confirmed_email=True))
