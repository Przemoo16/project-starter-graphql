from collections.abc import Mapping
from typing import Any
from uuid import UUID

import pytest

from backend.libs.email.message import HTMLMessage
from backend.libs.security.token import InvalidTokenError
from backend.services.user.exceptions import (
    InvalidEmailConfirmationTokenError,
    UserAlreadyConfirmedError,
    UserNotFoundError,
)
from backend.services.user.operations.email import (
    confirm_user,
    create_email_confirmation_token,
    read_email_confirmation_token,
    send_confirmation_email,
)
from tests.unit.helpers.user import UserCRUD, create_confirmed_user, create_user


def test_create_email_confirmation_token() -> None:
    user_id = UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    user_email = "test@email.com"

    def create_token(payload: Mapping[str, Any]) -> str:
        return f"sub:{payload['sub']}-email:{payload['email']}-type:{payload['type']}"

    token = create_email_confirmation_token(user_id, user_email, create_token)

    assert token == (
        "sub:6d9c79d6-9641-4746-92d9-2cc9ebdca941-email:test@email.com-"
        "type:email-confirmation"
    )


def test_send_confirmation_email() -> None:
    token = "test-token"
    url_template = "http://test/{token}"
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

    send_confirmation_email(token, url_template, load_template, send_email)

    assert message_result["subject"]
    assert (
        message_result["html_message"]
        == "email-confirmation.html {'link': 'http://test/test-token'}"
    )
    assert "http://test/test-token" in message_result["plain_message"]


def test_read_email_confirmation_token() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "email": "test@email.com",
            "type": "email-confirmation",
        }

    payload = read_email_confirmation_token(token, read_token)

    assert payload.user_id == UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    assert payload.user_email == "test@email.com"


def test_read_email_confirmation_token_invalid_token() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        raise InvalidTokenError

    with pytest.raises(InvalidEmailConfirmationTokenError):
        read_email_confirmation_token(token, read_token)


def test_read_email_confirmation_token_invalid_token_type() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "email": "test@email.com",
            "type": "invalid-type",
        }

    with pytest.raises(InvalidEmailConfirmationTokenError):
        read_email_confirmation_token(token, read_token)


@pytest.mark.anyio()
async def test_confirm_user() -> None:
    user_id = UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    user_email = "test@email.com"
    crud = UserCRUD(
        existing_user=create_user(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"),
            email="test@email.com",
            confirmed_email=False,
        )
    )

    user = await confirm_user(user_id, user_email, crud)

    assert user.confirmed_email is True


@pytest.mark.anyio()
async def test_confirm_user_id_not_found() -> None:
    user_id = UUID("e85b027d-67be-48ea-a11a-40e34d57442b")
    user_email = "test@email.com"
    crud = UserCRUD(
        existing_user=create_user(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), email="test@email.com"
        )
    )

    with pytest.raises(UserNotFoundError):
        await confirm_user(user_id, user_email, crud)


@pytest.mark.anyio()
async def test_confirm_user_email_not_found() -> None:
    user_id = UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    user_email = "invalid@email.com"
    crud = UserCRUD(
        existing_user=create_user(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), email="test@email.com"
        )
    )

    with pytest.raises(UserNotFoundError):
        await confirm_user(user_id, user_email, crud)


@pytest.mark.anyio()
async def test_confirm_user_already_confirmed() -> None:
    user_id = UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    user_email = "test@email.com"
    crud = UserCRUD(
        existing_user=create_confirmed_user(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), email="test@email.com"
        )
    )

    with pytest.raises(UserAlreadyConfirmedError):
        await confirm_user(user_id, user_email, crud)
