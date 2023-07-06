from collections.abc import Mapping
from contextlib import suppress
from typing import Any
from uuid import UUID

import pytest

from backend.libs.db.crud import NoObjectFoundError
from backend.libs.email.message import HTMLMessage
from backend.libs.security.token import InvalidTokenError
from backend.services.user.controllers import (
    TokenType,
    authenticate,
    confirm_email,
    create_access_token,
    create_email_confirmation_token,
    create_refresh_token,
    create_reset_password_token,
    create_user,
    delete_user,
    get_confirmed_user,
    get_user,
    login,
    read_email_confirmation_token,
    read_reset_password_token,
    send_confirmation_email,
    send_reset_password_email,
    set_password,
    update_user,
)
from backend.services.user.exceptions import (
    InvalidCredentialsError,
    InvalidEmailConfirmationTokenError,
    InvalidResetPasswordTokenError,
    UserAlreadyConfirmedError,
    UserAlreadyExistsError,
    UserNotConfirmedError,
    UserNotFoundError,
)
from backend.services.user.models import User
from backend.services.user.schemas import (
    Credentials,
    SetPasswordData,
    UserCreateData,
    UserFilters,
    UserUpdateData,
)
from tests.unit.helpers.user import (
    create_confirmed_user as create_confirmed_user_helper,
)
from tests.unit.helpers.user import create_user as create_user_helper
from tests.unit.stubs.crud.base import CRUDStub


class UserCRUD(  # pylint: disable=abstract-method
    CRUDStub[User, UserCreateData, UserUpdateData, UserFilters]
):
    def __init__(self, existing_user: User | None = None):
        self.existing_user = existing_user

    async def create_and_refresh(self, data: UserCreateData) -> User:
        return create_user_helper(**data.model_dump())

    async def read_one(self, filters: UserFilters) -> User:
        if not self.existing_user:
            raise NoObjectFoundError
        filters_dict = filters.model_dump(exclude_unset=True)
        if all(
            getattr(self.existing_user, field) == value
            for field, value in filters_dict.items()
        ):
            return self.existing_user
        raise NoObjectFoundError

    async def update_and_refresh(self, obj: User, data: UserUpdateData) -> User:
        return create_user_helper(**data.model_dump(exclude_unset=True))

    async def delete(self, obj: User) -> None:
        pass


def get_test_password(_: str) -> str:
    return "hashed_password"


@pytest.mark.anyio()
async def test_create_user() -> None:
    data = UserCreateData(
        email="test@email.com",
        password="plain_password",
        password_hasher=get_test_password,
    )
    crud = UserCRUD()

    user = await create_user(data, crud)

    assert user.email == "test@email.com"


@pytest.mark.anyio()
async def test_create_user_already_exists() -> None:
    data = UserCreateData(
        email="test@email.com",
        password="plain_password",
        password_hasher=get_test_password,
    )
    crud = UserCRUD(existing_user=create_user_helper(email="test@email.com"))

    with pytest.raises(UserAlreadyExistsError):
        await create_user(data, crud)


@pytest.mark.anyio()
async def test_get_user() -> None:
    filters = UserFilters(email="test@email.com")
    crud = UserCRUD(existing_user=create_user_helper(email="test@email.com"))

    user = await get_user(filters, crud)

    assert user


@pytest.mark.anyio()
async def test_get_user_not_found() -> None:
    filters = UserFilters(email="test@email.com")
    crud = UserCRUD()

    with pytest.raises(UserNotFoundError):
        await get_user(filters, crud)


@pytest.mark.anyio()
async def test_get_confirmed_user() -> None:
    filters = UserFilters(email="test@email.com")
    crud = UserCRUD(existing_user=create_confirmed_user_helper(email="test@email.com"))

    user = await get_confirmed_user(filters, crud)

    assert user


@pytest.mark.anyio()
async def test_get_not_confirmed_user_not_found() -> None:
    filters = UserFilters(email="test@email.com")
    crud = UserCRUD()

    with pytest.raises(UserNotFoundError):
        await get_confirmed_user(filters, crud)


@pytest.mark.anyio()
async def test_get_not_confirmed_user() -> None:
    filters = UserFilters(email="test@email.com")
    crud = UserCRUD(existing_user=create_user_helper(email="test@email.com"))

    with pytest.raises(UserNotConfirmedError):
        await get_confirmed_user(filters, crud)


@pytest.mark.anyio()
async def test_update_user() -> None:
    data = UserUpdateData(confirmed_email=True)
    user = create_user_helper(confirmed_email=False)
    crud = UserCRUD()

    updated_user = await update_user(user, data, crud)

    assert updated_user.confirmed_email is True


@pytest.mark.anyio()
async def test_update_user_email() -> None:
    data = UserUpdateData(email="updated@email.com")
    user = create_user_helper(email="test@email.com")
    crud = UserCRUD()

    updated_user = await update_user(user, data, crud)

    assert updated_user.email == "updated@email.com"
    assert updated_user.confirmed_email is False


@pytest.mark.anyio()
async def test_update_user_email_the_same_email_provided() -> None:
    data = UserUpdateData(email="test@email.com")
    user = create_user_helper(email="test@email.com")
    crud = UserCRUD()

    updated_user = await update_user(user, data, crud)

    assert updated_user.email == "test@email.com"
    assert updated_user.confirmed_email is not False


@pytest.mark.anyio()
async def test_update_user_email_already_exists() -> None:
    data = UserUpdateData(email="updated@email.com")
    user = create_user_helper(email="test@email.com")
    crud = UserCRUD(existing_user=create_user_helper(email="updated@email.com"))

    with pytest.raises(UserAlreadyExistsError):
        await update_user(user, data, crud)


@pytest.mark.anyio()
async def test_delete_user() -> None:
    user = create_user_helper()
    crud = UserCRUD()

    await delete_user(user, crud)


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


def test_read_email_confirmation_token() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "email": "test@email.com",
            "type": TokenType.EMAIL_CONFIRMATION.value,
        }

    data = read_email_confirmation_token(token, read_token)

    assert data.id == UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    assert data.email == "test@email.com"


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
async def test_confirm_email() -> None:
    token = "test-token"
    crud = UserCRUD(
        existing_user=create_user_helper(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"),
            email="test@email.com",
            confirmed_email=False,
        )
    )

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "email": "test@email.com",
            "type": TokenType.EMAIL_CONFIRMATION.value,
        }

    user = await confirm_email(token, read_token, crud)

    assert user.confirmed_email is True


@pytest.mark.anyio()
async def test_confirm_email_user_id_not_found() -> None:
    token = "test-token"
    crud = UserCRUD(
        existing_user=create_user_helper(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), email="test@email.com"
        )
    )

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "e85b027d-67be-48ea-a11a-40e34d57442b",
            "email": "test@email.com",
            "type": TokenType.EMAIL_CONFIRMATION.value,
        }

    with pytest.raises(InvalidEmailConfirmationTokenError):
        await confirm_email(token, read_token, crud)


@pytest.mark.anyio()
async def test_confirm_email_user_email_not_found() -> None:
    token = "test-token"
    crud = UserCRUD(
        existing_user=create_user_helper(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"),
            email="test@email.com",
        )
    )

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "email": "invalid@email.com",
            "type": TokenType.EMAIL_CONFIRMATION.value,
        }

    with pytest.raises(InvalidEmailConfirmationTokenError):
        await confirm_email(token, read_token, crud)


@pytest.mark.anyio()
async def test_confirm_email_user_already_confirmed() -> None:
    token = "test-token"
    crud = UserCRUD(
        existing_user=create_confirmed_user_helper(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941"), email="test@email.com"
        )
    )

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "email": "test@email.com",
            "type": TokenType.EMAIL_CONFIRMATION.value,
        }

    with pytest.raises(UserAlreadyConfirmedError) as exc_info:
        await confirm_email(token, read_token, crud)
    assert exc_info.value.email == "test@email.com"


def success_password_validator(*_: str) -> tuple[bool, None]:
    return True, None


@pytest.mark.anyio()
async def test_success_authentication_without_password_hash_update() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(
        existing_user=create_confirmed_user_helper(
            email="test@email.com", hashed_password="hashed_password"
        )
    )

    user = await authenticate(
        credentials, success_password_validator, get_test_password, crud
    )

    assert user.hashed_password == "hashed_password"


@pytest.mark.anyio()
async def test_success_authentication_with_password_hash_update() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(
        existing_user=create_confirmed_user_helper(
            email="test@email.com", hashed_password="hashed_password"
        )
    )

    def password_validator_update_hash(*_: str) -> tuple[bool, str]:
        return True, "new_hashed_password"

    user = await authenticate(
        credentials, password_validator_update_hash, get_test_password, crud
    )

    assert user.hashed_password == "new_hashed_password"


@pytest.mark.anyio()
async def test_failure_authentication_user_not_found() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD()

    with pytest.raises(InvalidCredentialsError):
        await authenticate(
            credentials, success_password_validator, get_test_password, crud
        )


@pytest.mark.anyio()
@pytest.mark.parametrize(
    ("user", "hasher_called"),
    [
        (
            create_confirmed_user_helper(email="test@email.com"),
            False,
        ),
        (None, True),
    ],
)
async def test_authentication_calling_password_hasher(
    user: User | None, hasher_called: bool
) -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(existing_user=user)

    hash_function_called = False

    def hash_password(_: str) -> str:
        nonlocal hash_function_called
        hash_function_called = True
        return "hashed_password"

    with suppress(InvalidCredentialsError):
        await authenticate(credentials, success_password_validator, hash_password, crud)

    assert hash_function_called == hasher_called


@pytest.mark.anyio()
async def test_failure_authentication_invalid_password() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(existing_user=create_confirmed_user_helper(email="test@email.com"))

    def failure_validator(*_: str) -> tuple[bool, None]:
        return False, None

    with pytest.raises(InvalidCredentialsError):
        await authenticate(credentials, failure_validator, get_test_password, crud)


@pytest.mark.anyio()
async def test_failure_authentication_user_not_confirmed() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(existing_user=create_user_helper(email="test@email.com"))

    with pytest.raises(UserNotConfirmedError):
        await authenticate(
            credentials, success_password_validator, get_test_password, crud
        )


@pytest.mark.anyio()
async def test_update_last_login_when_user_log_in() -> None:
    credentials = Credentials(email="test@email.com", password="plain_password")
    crud = UserCRUD(
        existing_user=create_confirmed_user_helper(
            email="test@email.com", last_login=None
        )
    )

    user = await login(credentials, success_password_validator, get_test_password, crud)

    assert user.last_login


def test_create_access_token() -> None:
    user_id = UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")

    def create_token(payload: Mapping[str, Any]) -> str:
        return f"sub:{payload['sub']}-type:{payload['type']}"

    token = create_access_token(user_id, create_token)

    assert token == "sub:6d9c79d6-9641-4746-92d9-2cc9ebdca941-type:access"


def test_create_refresh_token() -> None:
    user_id = UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")

    def create_token(payload: Mapping[str, Any]) -> str:
        return f"sub:{payload['sub']}-type:{payload['type']}"

    token = create_refresh_token(user_id, create_token)

    assert token == "sub:6d9c79d6-9641-4746-92d9-2cc9ebdca941-type:refresh"


def test_send_reset_password_email() -> None:
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

    send_reset_password_email(url_template, token, load_template, send_email)

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


def test_read_reset_password_token() -> None:
    token = "test-token"

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "fingerprint": "test-fingerprint",
            "type": TokenType.RESET_PASSWORD.value,
        }

    data = read_reset_password_token(token, read_token)

    assert data.id == UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
    assert data.fingerprint == "test-fingerprint"


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


@pytest.mark.anyio()
async def test_set_password() -> None:
    def hash_password(_: str) -> str:
        return "new_hashed_password"

    data = SetPasswordData(
        token="test-token",
        password="new_password",
        password_hasher=hash_password,
    )
    crud = UserCRUD(
        existing_user=create_confirmed_user_helper(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
        )
    )

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "fingerprint": "test-fingerprint",
            "type": TokenType.RESET_PASSWORD.value,
        }

    user = await set_password(data, read_token, success_password_validator, crud)

    assert user.hashed_password == "new_hashed_password"


@pytest.mark.anyio()
async def test_set_password_user_not_found() -> None:
    data = SetPasswordData(
        token="test-token",
        password="new_password",
        password_hasher=get_test_password,
    )
    crud = UserCRUD()

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "fingerprint": "test-fingerprint",
            "type": TokenType.RESET_PASSWORD.value,
        }

    with pytest.raises(InvalidResetPasswordTokenError):
        await set_password(data, read_token, success_password_validator, crud)


@pytest.mark.anyio()
async def test_set_password_user_not_confirmed() -> None:
    data = SetPasswordData(
        token="test-token",
        password="new_password",
        password_hasher=get_test_password,
    )
    crud = UserCRUD(
        existing_user=create_user_helper(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
        )
    )

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "fingerprint": "test-fingerprint",
            "type": TokenType.RESET_PASSWORD.value,
        }

    with pytest.raises(InvalidResetPasswordTokenError):
        await set_password(data, read_token, success_password_validator, crud)


@pytest.mark.anyio()
async def test_set_password_invalid_fingerprint() -> None:
    data = SetPasswordData(
        token="test-token",
        password="new_password",
        password_hasher=get_test_password,
    )
    crud = UserCRUD(
        existing_user=create_confirmed_user_helper(
            id=UUID("6d9c79d6-9641-4746-92d9-2cc9ebdca941")
        )
    )

    def read_token(_: str) -> dict[str, str]:
        return {
            "sub": "6d9c79d6-9641-4746-92d9-2cc9ebdca941",
            "fingerprint": "test-fingerprint",
            "type": TokenType.RESET_PASSWORD.value,
        }

    def failure_validator(*_: str) -> tuple[bool, None]:
        return False, None

    with pytest.raises(InvalidResetPasswordTokenError):
        await set_password(data, read_token, failure_validator, crud)
