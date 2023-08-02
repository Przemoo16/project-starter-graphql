import logging
from functools import partial
from uuid import UUID

from backend.celery import celery_app
from backend.config.settings import get_settings
from backend.libs.email.message import (
    EmailParticipants,
    SMTPServer,
    send_html_email,
)
from backend.services.user.context import PASSWORD_HASHER, TOKEN_CREATOR
from backend.services.user.jinja import load_template
from backend.services.user.operations.email import (
    ConfirmationEmailData,
    ConfirmationUserData,
    send_confirmation_email,
)
from backend.services.user.operations.password import (
    ResetPasswordEmailData,
    ResetPasswordUserData,
    send_reset_password_email,
)

logger = logging.getLogger(__name__)

_settings = get_settings()
email_settings = _settings.email
user_settings = _settings.user

CONFIRMATION_TOKEN_CREATOR = partial(
    TOKEN_CREATOR,
    expiration=int(user_settings.email_confirmation_token_lifetime.total_seconds()),
)
RESET_PASSWORD_TOKEN_CREATOR = partial(
    TOKEN_CREATOR,
    expiration=int(user_settings.reset_password_token_lifetime.total_seconds()),
)
SMTP_SERVER = SMTPServer(
    host=email_settings.smtp_host,
    port=email_settings.smtp_port,
    user=email_settings.smtp_user,
    password=email_settings.smtp_password.get_secret_value(),
)


@celery_app.task  # type: ignore[misc]
def send_confirmation_email_task(user_id: UUID, user_email: str) -> None:
    token_data = ConfirmationUserData(user_id=user_id, user_email=user_email)
    email_data = ConfirmationEmailData(
        url_template=user_settings.email_confirmation_url_template,
        template_loader=load_template,
        email_sender=partial(
            send_html_email,
            participants=EmailParticipants(
                sender=email_settings.sender, receiver=user_email
            ),
            smtp_server=SMTP_SERVER,
        ),
    )
    send_confirmation_email(token_data, CONFIRMATION_TOKEN_CREATOR, email_data)
    logger.info("Sent confirmation email to %r", user_email)


@celery_app.task  # type: ignore[misc]
def send_reset_password_email_task(
    user_id: UUID, user_email: str, user_password: str
) -> None:
    token_data = ResetPasswordUserData(user_id=user_id, user_password=user_password)
    email_data = ResetPasswordEmailData(
        url_template=user_settings.reset_password_url_template,
        template_loader=load_template,
        email_sender=partial(
            send_html_email,
            participants=EmailParticipants(
                sender=email_settings.sender, receiver=user_email
            ),
            smtp_server=SMTP_SERVER,
        ),
    )
    send_reset_password_email(
        token_data, RESET_PASSWORD_TOKEN_CREATOR, PASSWORD_HASHER, email_data
    )
    logger.info("Sent reset password email to %r", user_email)
