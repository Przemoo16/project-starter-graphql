import logging
from functools import partial
from uuid import UUID

from backend.config.settings import settings
from backend.libs.email.message import (
    EmailParticipants,
    SMTPServer,
    send_html_email,
)
from backend.services.user.context import (
    password_hasher,
    template_loader,
    token_creator,
)
from backend.services.user.operations.email import (
    ConfirmationEmailData,
    ConfirmationTokenData,
    send_confirmation_email,
)
from backend.services.user.operations.password import (
    ResetPasswordEmailData,
    ResetPasswordTokenData,
    send_reset_password_email,
)
from backend.worker import worker_app

_logger = logging.getLogger(__name__)

_email_settings = settings.email
_user_settings = settings.user

_smtp_server = partial(
    SMTPServer,
    host=_email_settings.smtp_host,
    port=_email_settings.smtp_port,
    user=_email_settings.smtp_user,
    password=_email_settings.smtp_password,
)


@worker_app.task  # type: ignore[misc]
def send_confirmation_email_task(user_id: UUID, user_email: str) -> None:
    token_data = ConfirmationTokenData(user_id=user_id, user_email=user_email)
    confirmation_email_token_creator = partial(
        token_creator,
        expiration=int(
            _user_settings.email_confirmation_token_lifetime.total_seconds()
        ),
    )
    email_data = ConfirmationEmailData(
        url_template=_user_settings.email_confirmation_url_template,
        template_loader=template_loader,
        email_sender=partial(
            send_html_email,
            participants=EmailParticipants(
                sender=_email_settings.sender, receiver=user_email
            ),
            smtp_server=_smtp_server(),
        ),
    )
    send_confirmation_email(token_data, confirmation_email_token_creator, email_data)
    _logger.info("Sent confirmation email to %r", user_email)


@worker_app.task  # type: ignore[misc]
def send_reset_password_email_task(
    user_id: UUID, user_email: str, user_password: str
) -> None:
    token_data = ResetPasswordTokenData(user_id=user_id, user_password=user_password)
    reset_password_token_creator = partial(
        token_creator,
        expiration=int(_user_settings.reset_password_token_lifetime.total_seconds()),
    )
    email_data = ResetPasswordEmailData(
        url_template=_user_settings.reset_password_url_template,
        template_loader=template_loader,
        email_sender=partial(
            send_html_email,
            participants=EmailParticipants(
                sender=_email_settings.sender, receiver=user_email
            ),
            smtp_server=_smtp_server(),
        ),
    )
    send_reset_password_email(
        token_data, reset_password_token_creator, password_hasher, email_data
    )
    _logger.info("Sent reset password email to %r", user_email)
