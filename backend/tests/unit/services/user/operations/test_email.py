from collections.abc import Mapping
from typing import Any
from uuid import UUID

import pytest

from backend.libs.email.message import HTMLMessage
from backend.libs.security.token import InvalidTokenError
from backend.services.user.exceptions import (
    InvalidEmailConfirmationTokenError,
    UserEmailAlreadyConfirmedError,
    UserNotFoundError,
)
from backend.services.user.operations.email import (
    ConfirmationEmailData,
    ConfirmationTokenData,
    confirm_email,
    send_confirmation_email,
)
from tests.unit.helpers.user import UserCRUD, create_confirmed_user, create_user


def test_send_confirmation_email_sends_message() -> None:
    message_result = {}

    token_data = ConfirmationTokenData(
        user_id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"),
        user_email="test@email.com",
    )

    def create_token(payload: Mapping[str, Any]) -> str:
        return "-".join(f"{key}:{value}" for key, value in payload.items())

    def load_template(name: str, **kwargs: Any) -> str:
        return f"{name} {kwargs}"

    def send_email(message: HTMLMessage) -> None:
        nonlocal message_result
        message_result = {
            "html_message": message.html_message,
            "plain_message": message.plain_message,
        }

    email_data = ConfirmationEmailData(
        url_template="http://test/{token}",
        template_loader=load_template,
        email_sender=send_email,
    )

    send_confirmation_email(token_data, create_token, email_data)

    assert message_result["html_message"] == (
        "email-confirmation.html {'link': 'http://test/sub:6d9c79d6-9641-4746-92d9-"
        "2cc9ebdca941-email:test@email.com-type:email-confirmation'}"
    )
    assert (
        "http://test/sub:6d9c79d6-9641-4746-92d9-2cc9ebdca941-"
        "email:test@email.com-type:email-confirmation"
    ) in message_result["plain_message"]


@pytest.mark.anyio()
async def test_confirm_email_confirms_user_email() -> None:
    token = "test-token"
    user = create_user(
        id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"),
        email="test@email.com",
        confirmed_email=False,
    )

    async def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "email": "test@email.com",
            "type": "email-confirmation",
        }

    crud = UserCRUD(existing_user=user)

    await confirm_email(token, read_token, crud)

    assert user.confirmed_email is True


@pytest.mark.anyio()
async def test_confirm_email_raises_exception_if_token_is_invalid() -> None:
    token = "test-token"

    async def read_token(_: str) -> dict[str, str]:
        raise InvalidTokenError

    crud = UserCRUD()

    with pytest.raises(InvalidEmailConfirmationTokenError):
        await confirm_email(token, read_token, crud)


@pytest.mark.anyio()
async def test_confirm_email_raises_exception_if_token_has_invalid_type() -> None:
    token = "test-token"

    async def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "email": "test@email.com",
            "type": "invalid-type",
        }

    crud = UserCRUD()

    with pytest.raises(InvalidEmailConfirmationTokenError):
        await confirm_email(token, read_token, crud)


@pytest.mark.anyio()
async def test_confirm_email_raises_exception_if_user_with_encoded_id_is_not_found() -> None:
    token = "test-token"

    async def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "e85b027d-67be-48ea-a11a-40e34d57442b",
            "email": "test@email.com",
            "type": "email-confirmation",
        }

    crud = UserCRUD(
        existing_user=create_user(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), email="test@email.com"
        )
    )

    with pytest.raises(UserNotFoundError):
        await confirm_email(token, read_token, crud)


@pytest.mark.anyio()
async def test_confirm_email_raises_exception_if_user_with_encoded_email_is_not_found() -> None:
    token = "test-token"

    async def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "email": "invalid@email.com",
            "type": "email-confirmation",
        }

    crud = UserCRUD(
        existing_user=create_user(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), email="test@email.com"
        )
    )

    with pytest.raises(UserNotFoundError):
        await confirm_email(token, read_token, crud)


@pytest.mark.anyio()
async def test_confirm_email_raises_exception_if_user_email_is_already_confirmed() -> None:
    token = "test-token"

    async def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "email": "test@email.com",
            "type": "email-confirmation",
        }

    crud = UserCRUD(
        existing_user=create_confirmed_user(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), email="test@email.com"
        )
    )

    with pytest.raises(UserEmailAlreadyConfirmedError):
        await confirm_email(token, read_token, crud)
