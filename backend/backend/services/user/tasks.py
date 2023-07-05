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
from backend.libs.security.token import (
    create_paseto_token_public_v4,
)
from backend.services.user.controllers import (
    create_email_confirmation_token,
    send_confirmation_email,
)
from backend.services.user.jinja import load_template

logger = logging.getLogger(__name__)

settings = get_settings()


@celery_app.task  # type: ignore[misc]
def send_confirmation_email_task(user_id: UUID, user_email: str) -> None:
    send_email_func = partial(
        send_html_email,
        participants=EmailParticipants(
            sender=settings.email.sender, receiver=user_email
        ),
        smtp_server=SMTPServer(
            host=settings.email.smtp_host,
            port=settings.email.smtp_port,
            user=settings.email.smtp_user,
            password=settings.email.smtp_password.get_secret_value(),
        ),
    )

    token = create_email_confirmation_token(
        user_id=user_id,
        user_email=user_email,
        token_creator=partial(
            create_paseto_token_public_v4,
            expiration=int(
                settings.user.email_confirmation_token_lifetime.total_seconds()
            ),
            key=settings.user.auth_private_key.get_secret_value(),
        ),
    )
    send_confirmation_email(
        url_template=settings.user.email_confirmation_url_template,
        token=token,
        template_loader=load_template,
        send_email_func=send_email_func,
    )
    logger.info("Sent confirmation email to %r", user_email)
