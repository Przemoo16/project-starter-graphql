import logging
from functools import partial

from backend.celery import celery_app
from backend.config.settings import get_settings
from backend.libs.email.message import (
    EmailParticipants,
    SMTPServer,
    send_html_email,
)
from backend.services.user.controllers import send_confirmation_email
from backend.services.user.jinja import load_template

logger = logging.getLogger(__name__)

settings = get_settings()


@celery_app.task  # type: ignore[misc]
def send_confirmation_email_task(receiver: str) -> None:
    send_email_func = partial(
        send_html_email,
        participants=EmailParticipants(sender=settings.email.sender, receiver=receiver),
        smtp_server=SMTPServer(
            host=settings.email.smtp_host,
            port=settings.email.smtp_port,
            user=settings.email.smtp_user,
            password=settings.email.smtp_password.get_secret_value(),
        ),
    )
    send_confirmation_email(
        url_template=str(settings.user.email_confirmation_url),
        token_encoder=lambda token: token,
        template_loader=load_template,
        send_email_func=send_email_func,
    )
    logger.info("Sent confirmation email to %r", receiver)
