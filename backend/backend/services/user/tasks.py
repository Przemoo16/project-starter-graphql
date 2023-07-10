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
from backend.libs.security.password import hash_password
from backend.libs.security.token import (
    create_paseto_token_public_v4,
)
from backend.services.user.jinja import load_template
from backend.services.user.operations.email import (
    ConfirmationEmailData,
    ConfirmationTokenData,
    send_email_confirmation_token,
)
from backend.services.user.operations.password import (
    ResetPasswordEmailData,
    ResetPasswordTokenData,
    send_reset_password_token,
)

logger = logging.getLogger(__name__)

_settings = get_settings()
email_settings = _settings.email
user_settings = _settings.user


@celery_app.task  # type: ignore[misc]
def send_confirmation_email_task(user_id: UUID, user_email: str) -> None:
    token_data = ConfirmationTokenData(
        user_id=user_id,
        user_email=user_email,
        token_creator=partial(
            create_paseto_token_public_v4,
            expiration=int(
                user_settings.email_confirmation_token_lifetime.total_seconds()
            ),
            key=user_settings.auth_private_key.get_secret_value(),
        ),
    )
    email_data = ConfirmationEmailData(
        url_template=user_settings.email_confirmation_url_template,
        template_loader=load_template,
        email_sender=partial(
            send_html_email,
            participants=EmailParticipants(
                sender=email_settings.sender, receiver=user_email
            ),
            smtp_server=SMTPServer(
                host=email_settings.smtp_host,
                port=email_settings.smtp_port,
                user=email_settings.smtp_user,
                password=email_settings.smtp_password.get_secret_value(),
            ),
        ),
    )
    send_email_confirmation_token(token_data, email_data)
    logger.info("Sent confirmation email to %r", user_email)


@celery_app.task  # type: ignore[misc]
def send_reset_password_email_task(
    user_id: UUID, user_email: str, user_password: str
) -> None:
    token_data = ResetPasswordTokenData(
        user_id=user_id,
        user_password=user_password,
        password_hasher=hash_password,
        token_creator=partial(
            create_paseto_token_public_v4,
            expiration=int(
                user_settings.email_confirmation_token_lifetime.total_seconds()
            ),
            key=user_settings.auth_private_key.get_secret_value(),
        ),
    )
    email_data = ResetPasswordEmailData(
        url_template=user_settings.reset_password_url_template,
        template_loader=load_template,
        email_sender=partial(
            send_html_email,
            participants=EmailParticipants(
                sender=email_settings.sender, receiver=user_email
            ),
            smtp_server=SMTPServer(
                host=email_settings.smtp_host,
                port=email_settings.smtp_port,
                user=email_settings.smtp_user,
                password=email_settings.smtp_password.get_secret_value(),
            ),
        ),
    )
    send_reset_password_token(token_data, email_data)
    logger.info("Sent reset password email to %r", user_email)
