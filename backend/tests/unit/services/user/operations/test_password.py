from collections.abc import Mapping
from typing import Any
from uuid import UUID

import pytest

from backend.libs.email.message import HTMLMessage
from backend.libs.security.token import InvalidTokenError
from backend.services.user.exceptions import (
    InvalidResetPasswordTokenError,
    InvalidResetPasswordTokenFingerprintError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.operations.password import (
    ResetPasswordEmailData,
    ResetPasswordTokenData,
    create_reset_password_token,
    read_reset_password_token,
    recover_password,
    reset_password,
    send_reset_password_token,
)
from backend.services.user.schemas import ResetPasswordData
from tests.unit.helpers.user import UserCRUD, create_confirmed_user, create_user


def success_password_validator(*_: str) -> tuple[bool, None]:
    return True, None


def get_test_password(_: str) -> str:
    return "hashed_password"


@pytest.mark.anyio()
async def test_recover_password() -> None:
    email = "test@email.com"
    crud = UserCRUD(existing_user=create_confirmed_user(email="test@email.com"))
    callback_called = False

    def callback(_: User) -> None:
        nonlocal callback_called
        callback_called = True

    await recover_password(email, crud, callback)

    assert callback_called


@pytest.mark.anyio()
async def test_recover_password_user_not_found() -> None:
    email = "test@email.com"
    crud = UserCRUD()
    callback_called = False

    def callback(_: User) -> None:
        nonlocal callback_called
        callback_called = True

    await recover_password(email, crud, callback)

    assert not callback_called


@pytest.mark.anyio()
async def test_recover_password_user_not_confirmed() -> None:
    email = "test@email.com"
    crud = UserCRUD(existing_user=create_user(email="test@email.com"))
    callback_called = False

    def callback(_: User) -> None:
        nonlocal callback_called
        callback_called = True

    await recover_password(email, crud, callback)

    assert not callback_called


def test_send_reset_password_token() -> None:
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

    token_data = ResetPasswordTokenData(
        user_id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"),
        user_password="hashed_password",
        password_hasher=get_test_password,
        token_creator=lambda _: "test-token",
    )
    email_data = ResetPasswordEmailData(
        url_template="http://test/{token}",
        template_loader=load_template,
        email_sender=send_email,
    )

    send_reset_password_token(token_data, email_data)

    assert message_result["subject"]
    assert (
        message_result["html_message"]
        == "reset-password.html {'link': 'http://test/test-token'}"
    )
    assert "http://test/test-token" in message_result["plain_message"]


def test_create_reset_password_token() -> None:
    user_id = UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    user_password = "hashed_password"

    def hash_password(_: str) -> str:
        return "again_hashed_password"

    def create_token(payload: Mapping[str, str]) -> str:
        return (
            f"sub:{payload['sub']}-fingerprint:{payload['fingerprint']}-"
            f"type:{payload['type']}"
        )

    token = create_reset_password_token(
        user_id, user_password, hash_password, create_token
    )

    assert token == (
        "sub:6d9c79d6-9641-4746-92d9-2cc9ebdca941-"
        "fingerprint:again_hashed_password-type:reset-password"
    )


@pytest.mark.anyio()
async def test_reset_password() -> None:
    def hash_password(_: str) -> str:
        return "new_hashed_password"

    data = ResetPasswordData(
        token="test-token",
        password="new_password",
        password_hasher=hash_password,
    )
    crud = UserCRUD(
        existing_user=create_confirmed_user(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
        )
    )

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "fingerprint": "test-fingerprint",
            "type": "reset-password",
        }

    user = await reset_password(data, read_token, success_password_validator, crud)

    assert user.hashed_password == "new_hashed_password"


@pytest.mark.anyio()
async def test_reset_password_user_not_found() -> None:
    data = ResetPasswordData(
        token="test-token",
        password="new_password",
        password_hasher=get_test_password,
    )
    crud = UserCRUD()

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "fingerprint": "test-fingerprint",
            "type": "reset-password",
        }

    with pytest.raises(UserNotFoundError):
        await reset_password(data, read_token, success_password_validator, crud)


@pytest.mark.anyio()
async def test_reset_password_invalid_fingerprint() -> None:
    data = ResetPasswordData(
        token="test-token",
        password="new_password",
        password_hasher=get_test_password,
    )
    crud = UserCRUD(
        existing_user=create_confirmed_user(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
        )
    )

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "fingerprint": "test-fingerprint",
            "type": "reset-password",
        }

    def failure_validator(*_: str) -> tuple[bool, None]:
        return False, None

    with pytest.raises(InvalidResetPasswordTokenFingerprintError):
        await reset_password(data, read_token, failure_validator, crud)


@pytest.mark.anyio()
async def test_reset_password_user_not_confirmed() -> None:
    data = ResetPasswordData(
        token="test-token",
        password="new_password",
        password_hasher=get_test_password,
    )
    crud = UserCRUD(
        existing_user=create_user(id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"))
    )

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "fingerprint": "test-fingerprint",
            "type": "reset-password",
        }

    with pytest.raises(UserNotConfirmedError):
        await reset_password(data, read_token, success_password_validator, crud)


def test_read_reset_password_token() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "fingerprint": "test-fingerprint",
            "type": "reset-password",
        }

    payload = read_reset_password_token(token, read_token)

    assert payload.user_id == UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    assert payload.fingerprint == "test-fingerprint"


def test_read_reset_password_token_invalid_token() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        raise InvalidTokenError

    with pytest.raises(InvalidResetPasswordTokenError):
        read_reset_password_token(token, read_token)


def test_read_reset_password_token_invalid_token_type() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "fingerprint": "test-fingerprint",
            "type": "invalid-type",
        }

    with pytest.raises(InvalidResetPasswordTokenError):
        read_reset_password_token(token, read_token)
