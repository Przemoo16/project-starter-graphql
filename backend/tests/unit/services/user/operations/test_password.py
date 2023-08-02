from collections.abc import Mapping
from typing import Any
from uuid import UUID

import pytest

from backend.libs.email.message import HTMLMessage
from backend.libs.security.token import InvalidTokenError
from backend.services.user.exceptions import (
    InvalidPasswordError,
    InvalidResetPasswordTokenError,
    InvalidResetPasswordTokenFingerprintError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.operations.password import (
    PasswordManager,
    change_password,
    create_reset_password_token,
    recover_password,
    reset_password,
    send_reset_password_email,
)
from backend.services.user.schemas import PasswordChangeSchema, PasswordResetSchema
from tests.unit.helpers.user import UserCRUD, create_user


@pytest.fixture(name="password_manager")
def password_manager_fixture() -> PasswordManager:
    def validate_password(*_: str) -> tuple[bool, None]:
        return True, None

    def hash_password(_: str) -> str:
        return "hashed_password"

    return PasswordManager(validator=validate_password, hasher=hash_password)


@pytest.mark.anyio()
async def test_recover_password() -> None:
    email = "test@email.com"
    crud = UserCRUD(existing_user=create_user(email="test@email.com"))
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


def test_create_reset_password_token() -> None:
    user_id = UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    user_password = "hashed_password"

    def hash_password(_: str) -> str:
        return "again_hashed_password"

    def create_token(payload: Mapping[str, Any]) -> str:
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


def test_send_reset_password_email() -> None:
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

    send_reset_password_email(token, url_template, load_template, send_email)

    assert message_result["subject"]
    assert (
        message_result["html_message"]
        == "reset-password.html {'link': 'http://test/test-token'}"
    )
    assert "http://test/test-token" in message_result["plain_message"]


@pytest.mark.anyio()
async def test_reset_password(password_manager: PasswordManager) -> None:
    data = PasswordResetSchema(token="test-token", password="plain_password")

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "fingerprint": "test-fingerprint",
            "type": "reset-password",
        }

    def hash_password(_: str) -> str:
        return "new_hashed_password"

    password_manager.hasher = hash_password

    crud = UserCRUD(
        existing_user=create_user(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"),
            hashed_password="hashed_password",
        )
    )

    user = await reset_password(data, read_token, password_manager, crud)

    assert user.hashed_password == "new_hashed_password"


@pytest.mark.anyio()
async def test_reset_password_invalid_token(password_manager: PasswordManager) -> None:
    data = PasswordResetSchema(token="test-token", password="plain_password")

    def read_token(_: str) -> dict[str, str]:
        raise InvalidTokenError

    crud = UserCRUD()

    with pytest.raises(InvalidResetPasswordTokenError):
        await reset_password(data, read_token, password_manager, crud)


@pytest.mark.anyio()
async def test_reset_password_invalid_token_type(
    password_manager: PasswordManager,
) -> None:
    data = PasswordResetSchema(token="test-token", password="plain_password")

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "fingerprint": "test-fingerprint",
            "type": "invalid-type",
        }

    crud = UserCRUD()

    with pytest.raises(InvalidResetPasswordTokenError):
        await reset_password(data, read_token, password_manager, crud)


@pytest.mark.anyio()
async def test_reset_password_user_not_found(password_manager: PasswordManager) -> None:
    data = PasswordResetSchema(token="test-token", password="plain_password")

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "fingerprint": "test-fingerprint",
            "type": "reset-password",
        }

    crud = UserCRUD()

    with pytest.raises(UserNotFoundError):
        await reset_password(data, read_token, password_manager, crud)


@pytest.mark.anyio()
async def test_reset_password_invalid_fingerprint(
    password_manager: PasswordManager,
) -> None:
    data = PasswordResetSchema(token="test-token", password="plain_password")

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "fingerprint": "test-fingerprint",
            "type": "reset-password",
        }

    def validate_password(*_: str) -> tuple[bool, None]:
        return False, None

    password_manager.validator = validate_password

    crud = UserCRUD(
        existing_user=create_user(id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"))
    )

    with pytest.raises(InvalidResetPasswordTokenFingerprintError):
        await reset_password(data, read_token, password_manager, crud)


@pytest.mark.anyio()
async def test_change_password(password_manager: PasswordManager) -> None:
    user = create_user(hashed_password="hashed_password")
    data = PasswordChangeSchema(
        current_password="plain_password", new_password="new_password"
    )

    def hash_password(_: str) -> str:
        return "new_hashed_password"

    password_manager.hasher = hash_password
    crud = UserCRUD()

    updated_user = await change_password(user, data, password_manager, crud)

    assert updated_user.hashed_password == "new_hashed_password"


@pytest.mark.anyio()
async def test_change_password_invalid_password(
    password_manager: PasswordManager,
) -> None:
    user = create_user(hashed_password="plain_password")
    data = PasswordChangeSchema(
        current_password="plain_password", new_password="new_password"
    )

    def validate_password(*_: str) -> tuple[bool, None]:
        return False, None

    password_manager.validator = validate_password
    crud = UserCRUD()

    with pytest.raises(InvalidPasswordError):
        await change_password(user, data, password_manager, crud)
