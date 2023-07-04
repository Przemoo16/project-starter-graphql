from collections.abc import Mapping
from typing import Any
from uuid import uuid4

from backend.libs.email.message import HTMLMessage
from backend.services.user.controllers.token import (
    create_access_token,
    create_email_confirmation_token,
    create_refresh_token,
    send_confirmation_email,
)


def test_create_access_token() -> None:
    user_id = uuid4()

    def create_token(payload: Mapping[str, Any]) -> str:
        return f"sub:{payload['sub']}-type:{payload['type']}"

    token = create_access_token(user_id, create_token)

    assert token == f"sub:{user_id}-type:access"


def test_create_refresh_token() -> None:
    user_id = uuid4()

    def create_token(payload: Mapping[str, Any]) -> str:
        return f"sub:{payload['sub']}-type:{payload['type']}"

    token = create_refresh_token(user_id, create_token)

    assert token == f"sub:{user_id}-type:refresh"


def test_create_email_confirmation_token() -> None:
    user_id = uuid4()
    user_email = "test@email.com"

    def create_token(payload: Mapping[str, Any]) -> str:
        return f"sub:{payload['sub']}-email:{payload['email']}-type:{payload['type']}"

    token = create_email_confirmation_token(user_id, user_email, create_token)

    assert token == f"sub:{user_id}-email:test@email.com-type:email-confirmation"


def test_send_confirmation_email() -> None:
    url_template = "http://test/{token}"
    token = "test-token"
    message_result = {}

    def load_template(name: str, **kwargs: Any) -> str:
        return f"{name} {kwargs}"

    def send_email(message: HTMLMessage) -> None:
        nonlocal message_result
        message_result = {
            "subject": message.subject,
            "html_message": message.html_message,
            "plain_message": message.plain_message,
        }

    send_confirmation_email(url_template, token, load_template, send_email)

    assert message_result["subject"]
    assert (
        message_result["html_message"]
        == "email-confirmation.html {'link': 'http://test/test-token'}"
    )
    assert "http://test/test-token" in message_result["plain_message"]
