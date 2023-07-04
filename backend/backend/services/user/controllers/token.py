from collections.abc import Callable, Mapping
from enum import Enum, unique
from gettext import gettext as _
from typing import Any, Protocol
from uuid import UUID

from backend.libs.email.message import HTMLMessage


class TokenCreator(Protocol):
    def __call__(self, payload: Mapping[str, Any]) -> str:
        ...


@unique
class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_CONFIRMATION = "email-confirmation"


def create_access_token(user_id: UUID, token_creator: TokenCreator) -> str:
    return token_creator(payload={"sub": str(user_id), "type": TokenType.ACCESS})


def create_refresh_token(user_id: UUID, token_creator: TokenCreator) -> str:
    return token_creator(payload={"sub": str(user_id), "type": TokenType.REFRESH})


def create_email_confirmation_token(
    user_id: UUID, user_email: str, token_creator: TokenCreator
) -> str:
    return token_creator(
        payload={
            "sub": str(user_id),
            "email": user_email,
            "type": TokenType.EMAIL_CONFIRMATION,
        }
    )


class TemplateLoader(Protocol):
    def __call__(self, name: str, **kwargs: Any) -> str:
        ...


def send_confirmation_email(
    url_template: str,
    token: str,
    template_loader: TemplateLoader,
    send_email_func: Callable[[HTMLMessage], None],
) -> None:
    link = url_template.format(token=token)
    subject = _("Confirm email")
    html_message = template_loader("email-confirmation.html", link=link)
    plain_message = _("Click the link to confirm your email: {link}").format(link=link)
    send_email_func(
        HTMLMessage(
            subject=subject, html_message=html_message, plain_message=plain_message
        )
    )
